"""Read-only skill metadata and Git facts."""
import os
import subprocess
from . import lifecycle
from .common import MaintenanceError, candidate_source, read_state, run_tool

def git_status(root):
    env = os.environ | {'GIT_OPTIONAL_LOCKS': '0'}
    result = subprocess.run(['git', '-C', str(root), 'status', '--porcelain=v1', '-z'],
                            capture_output=True, timeout=30, env=env)
    revision = subprocess.run(['git', '-C', str(root), 'rev-parse', 'HEAD'],
                              capture_output=True, timeout=30, env=env)
    if result.returncode or revision.returncode:
        raise MaintenanceError('GIT_INSPECTION_FAILED')
    return {'revision': revision.stdout.decode().strip(), 'clean': not result.stdout,
            'records': result.stdout.decode(errors='replace').split('\0')[:-1]}

def metadata(root, package=None, offset=0, limit=8):
    if offset < 0 or not 1 <= limit <= 32:
        raise MaintenanceError('INVALID_PAGE')
    if package is None:
        catalog = run_tool(root, 'list_registry.py', ['--catalog', '--json'])
        if catalog['tool_returncode']:
            raise MaintenanceError('INVENTORY_FAILED')
        records = catalog['skill_records']
        if offset > len(records):
            raise MaintenanceError('INVALID_PAGE')
        end = min(offset + limit, len(records))
        return {'schema': 'skills-ai/maintenance-inventory/1', 'source_hash': catalog['source_hash'],
                'skill_counts': catalog['skill_counts'], 'offset': offset, 'total': len(records),
                'items': records[offset:end], 'next_offset': end if end < len(records) else None}
    args = ['discover', '--offset', str(offset), '--limit', str(limit)]
    if package:
        args += ['--package', package]
    result = run_tool(root, 'orchestrate.py', args)
    if result['tool_returncode']:
        raise MaintenanceError(result.get('reason', 'DISCOVERY_FAILED'))
    return result

def help_metadata(root, package):
    if not isinstance(package, str) or not package.strip():
        raise MaintenanceError('SKILL_HELP_REQUIRES_NAME')
    result = run_tool(root, 'list_registry.py', ['--help-skill', package, '--json'])
    if result['tool_returncode']:
        raise MaintenanceError(result.get('reason', 'SKILL_HELP_FAILED'))
    return result


def help_overview(root):
    inventory = metadata(root, None, 0, 32)
    if inventory.get('next_offset') is not None:
        raise MaintenanceError('HELP_INVENTORY_EXCEEDS_BOUND')
    return {
        'schema': 'skills-ai/help-overview/1',
        'status': 'current',
        'authority': 'none',
        'source_hash': inventory['source_hash'],
        'skill_counts': inventory['skill_counts'],
        'skills': inventory['items'],
        'limits': ('Help is read-only metadata. It does not select, load, activate, '
                   'or authorize a skill or maintenance operation.'),
    }

def status(root, session, adapters, hosts=None):
    out = run_tool(root, 'orchestrate.py', ['status'] + (['--session', session] if session else []))
    if out['tool_returncode']:
        raise MaintenanceError(out.get('reason', 'STATUS_FAILED'))
    compiled = run_tool(root, 'compile_registry.py', ['--check'], parse=False)
    if compiled['returncode']:
        raise MaintenanceError('STALE_REGISTRY: run orchestrator/tools/compile_registry.py')
    manifest = read_state(root / 'orchestrator/runtime/manifest.json')
    if manifest is None:
        raise MaintenanceError('MANIFEST_UNAVAILABLE')
    distribution = lifecycle.inspect(root, manifest, adapters)
    packages = lifecycle.package_versions(root, manifest)
    source = git_status(root)
    configured = [adapters.check(root, host) for host in (adapters.bindings(root) if hosts is None else hosts)]
    version_problems = [item for item in packages['items']
                        if item['state'] in ('active', 'manual') and item['status'] in ('ambiguous', 'unavailable')]
    health = ('partial' if not source['clean'] or distribution['status'] == 'partial' or version_problems
              else 'unknown' if distribution['status'] == 'unknown' else 'current')
    next_action = None
    if not source['clean']:
        next_action = 'Review and explicitly authorize one coherent source commit when ready.'
    elif version_problems:
        next_action = 'Resolve the first unavailable or ambiguous package version source.'
    else:
        for item in distribution['items']:
            if not item['globally_current']:
                next_action = item['next'][0]
                break
    return {'status': health, 'source': source, 'runtime': out,
            'packages': packages, 'lifecycle': distribution,
            'candidate_of': candidate_source(root),
            'installations': configured,
            'next': next_action or 'No pending declared status action.',
            'context': 'Controls and retained instructions are host-supplied; disk checks cannot establish them.'}


def lifecycle_status(root, adapters, package=None, check_remotes=False):
    compiled = run_tool(root, 'compile_registry.py', ['--check'], parse=False)
    if compiled['returncode']:
        raise MaintenanceError('STALE_REGISTRY: run orchestrator/tools/compile_registry.py')
    manifest = read_state(root / 'orchestrator/runtime/manifest.json')
    if manifest is None:
        raise MaintenanceError('MANIFEST_UNAVAILABLE')
    return lifecycle.inspect(root, manifest, adapters, package, check_remotes=check_remotes)


def doctor(root, session, adapters, hosts=None):
    verification = run_tool(root, 'verify_all.py', ['--json'], timeout=600)
    current = status(root, session, adapters, hosts)
    failed = verification.get('failed', 1) or verification['tool_returncode']
    return {'status': 'partial' if failed or current['status'] != 'current' else 'current',
            'verification': verification, 'current': current,
            'limits': 'Local checks and managed-file freshness; native host behavior remains host-owned.'}
