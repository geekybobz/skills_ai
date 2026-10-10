"""Read-only skill metadata and Git facts."""
import os
import subprocess
from .common import MaintenanceError, candidate_source, run_tool

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

def status(root, session, adapters, hosts=None):
    out = run_tool(root, 'orchestrate.py', ['status'] + (['--session', session] if session else []))
    if out['tool_returncode']:
        raise MaintenanceError(out.get('reason', 'STATUS_FAILED'))
    return {'source': git_status(root), 'runtime': out,
            'candidate_of': candidate_source(root),
            'installations': [adapters.check(root, host) for host in (adapters.bindings(root) if hosts is None else hosts)],
            'context': 'Controls and retained instructions are host-supplied; disk checks cannot establish them.'}
