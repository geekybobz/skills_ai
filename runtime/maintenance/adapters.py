"""Host adapter interface backed by the existing platform installers."""
from pathlib import Path
from .common import (AREA, SCHEMA, MaintenanceError, candidate_source, fingerprint,
                     read_state, run_tool, safe_path, write_state)

HOSTS = {'codex': ('skills/skills-ai-registry/SKILL.md',),
         'claude': ('hooks/skills-ai-context.js', 'settings.json',
                    'settings.json.skills-ai.bak', 'settings.json.skills-ai.previous')}

def validate(binding):
    if (not isinstance(binding, dict) or set(binding) != {'host', 'config_dir'}
            or not isinstance(binding['host'], str) or binding['host'] not in HOSTS
            or not isinstance(binding['config_dir'], str)):
        raise MaintenanceError('INVALID_HOST_BINDING')
    safe_path(Path(binding['config_dir']))
    return binding

def bindings(root):
    value = read_state(root / AREA / 'hosts.json')
    if value is None:
        return []
    if set(value) != {'schema', 'hosts'} or value['schema'] != SCHEMA or not isinstance(value['hosts'], list) or len(value['hosts']) > len(HOSTS):
        raise MaintenanceError('INVALID_HOST_PROFILE')
    result = [validate(item) for item in value['hosts']]
    if len({b['host'] for b in result}) != len(result):
        raise MaintenanceError('DUPLICATE_HOST_BINDING')
    return result

def select(root, names, config_dir=None):
    if config_dir and len(names) != 1:
        raise MaintenanceError('CONFIG_DIR_REQUIRES_ONE_HOST')
    if len(names) != len(set(names)):
        raise MaintenanceError('DUPLICATE_HOST_BINDING')
    if not names:
        return bindings(root)
    return [validate({'host': name, 'config_dir': str(config_dir or Path.home() / ('.' + name))}) for name in names]

def arguments(binding):
    return ['--adapter', binding['host'], '--config-dir', binding['config_dir']]

def targets(binding):
    return [safe_path(Path(binding['config_dir']) / p) for p in HOSTS[binding['host']]]

def check(root, binding):
    validate(binding)
    for target in targets(binding):
        fingerprint(target)
    result = run_tool(root, 'install_runtime_adapter.py', arguments(binding) + ['--check'], parse=False)
    return binding | {'status': 'current' if result['returncode'] == 0 else 'stale', 'detail': result['output']}

def preview(root, binding):
    validate(binding)
    if candidate_source(root):
        try:
            Path(binding['config_dir']).relative_to(root)
        except ValueError as exc:
            raise MaintenanceError('CANDIDATE_REFRESH_REQUIRES_CONTAINED_TEST_CONFIG') from exc
    before = {str(p): fingerprint(p) for p in targets(binding)}
    out = run_tool(root, 'install_runtime_adapter.py', arguments(binding) + ['--dry-run'])
    if out['tool_returncode']:
        raise MaintenanceError('ADAPTER_PREVIEW_FAILED')
    if 'preserved-foreign' in out.get('files', {}).values():
        raise MaintenanceError('FOREIGN_HOST_ENTRY_PRESERVED')
    if binding['host'] == 'claude' and out['files'].get('settings') == 'would-update':
        config = Path(binding['config_dir'])
        if (config / 'settings.json').exists():
            name = 'settings.json.skills-ai.previous' if (config / 'settings.json.skills-ai.bak').exists() else 'settings.json.skills-ai.bak'
            out['files']['settings_backup'] = 'would-update ' + name
    return {'binding': binding, 'before': before, 'changes': out['files']}

def refresh(root, plan, backup_dir):
    binding = validate(plan['binding'])
    if {str(p): fingerprint(p) for p in targets(binding)} != plan['before']:
        raise MaintenanceError('HOST_CHANGED_AFTER_REVIEW')
    backup_dir.mkdir(parents=True, exist_ok=False, mode=0o700)
    for index, target in enumerate(targets(binding)):
        if target.exists():
            destination = backup_dir / str(index)
            destination.write_bytes(target.read_bytes())
            destination.chmod(0o600)
    write_state(backup_dir / 'manifest.json', plan)
    result = run_tool(root, 'install_runtime_adapter.py', arguments(binding))
    if result['tool_returncode']:
        raise MaintenanceError('HOST_INSTALL_FAILED')
    verified = check(root, binding)
    if verified['status'] != 'current':
        raise MaintenanceError('HOST_VERIFICATION_FAILED')
    previous = bindings(root)
    write_state(root / AREA / 'hosts.json', {'schema': SCHEMA, 'hosts':
                [p for p in previous if p['host'] != binding['host']] + [binding]})
    return result | {'verification': verified, 'backup': str(backup_dir)}
