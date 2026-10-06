"""Human and machine clients share the same maintenance operations."""
import argparse
import json
from pathlib import Path
import sys
import subprocess
from . import adapters, checks, inspection, operations, workspace
from .common import SCHEMA, MaintenanceError, candidate_source, safe_path, session_id

class Parser(argparse.ArgumentParser):
    def error(self, message):
        raise MaintenanceError('INVALID_ARGUMENTS: ' + message)

def parser():
    common = argparse.ArgumentParser(add_help=False, argument_default=argparse.SUPPRESS)
    common.add_argument('--root', type=Path, help='Exact repository root; default is this installed command source')
    common.add_argument('--session', help='Exact host or separate terminal session ID')
    common.add_argument('--json', action='store_true', help='Versioned machine output; never auto-approve')
    p = Parser(prog='skills_ai', parents=[common], description='Inspect, contain, verify, deploy and refresh Skills AI.')
    sub = p.add_subparsers(dest='command', parser_class=Parser)
    s = sub.add_parser('status', parents=[common], help='Source, workspace and configured installation facts')
    d = sub.add_parser('skills', parents=[common], help='Declared package/capability metadata only')
    d.add_argument('name', nargs='?')
    d.add_argument('--offset', type=int, default=0)
    d.add_argument('--limit', type=int, default=8)
    c = sub.add_parser('check', parents=[common], help='Required local artifact checks')
    c.add_argument('--path', action='append', default=[])
    c.add_argument('--full', action='store_true')
    c.add_argument('--approval-ref')
    r = sub.add_parser('repair', parents=[common], help='Create/resume or pause the selected contained workspace')
    r.add_argument('state', choices=('on', 'off'))
    for name in ('update', 'refresh'):
        a = sub.add_parser(name, parents=[common], help='Review and approve ' + ('contained source changes' if name == 'update' else 'managed installation refresh'))
        a.add_argument('--preview', action='store_true', help='Prepare review without applying')
        a.add_argument('--approve', metavar='PREVIEW_ID', help='Host attests actual agreement to this saved exact review')
        a.add_argument('--approval-ref', help='Reference to actual user agreement when applying a saved preview')
    for a in (s, sub.choices['update'], sub.choices['refresh']):
        a.add_argument('--host', choices=sorted(adapters.HOSTS), action='append', default=[])
        a.add_argument('--config-dir', type=Path, help='Explicit configuration root for one host; also used for contained tests')
    return p

def render(value):
    command = value.get('command')
    data = value.get('result', {})
    if value.get('status') == 'error':
        return 'Blocked: ' + value['reason']
    lines = []
    if command == 'status':
        source = data['source']
        lines += ['Source: ' + source['revision'][:12], 'Git: ' + ('clean' if source['clean'] else 'has local changes')]
        if data.get('candidate_of'):
            lines += ['Contained candidate of: ' + data['candidate_of'], 'Repair below describes this root only, not its source association.']
        repair = data['runtime'].get('repair', {})
        lines += ['Repair: ' + repair.get('repair', 'unknown')]
        if repair.get('working_root'):
            lines += ['Working folder: ' + repair['working_root']]
        catalog = data['runtime'].get('catalog', {})
        lines += ['Capabilities: ' + str(catalog.get('total', 'unknown')) + ' (declared packages are skills)']
        for host in data['installations']:
            lines += [host['host'] + ': ' + host['status'] + ' — ' + host['config_dir']]
        if not data['installations']:
            lines += ['No host bindings saved. Inspect with status --host codex; configure through refresh --host codex.']
        lines += [data['context']]
    elif command == 'skills':
        for item in data.get('items', []):
            name = item['package'] + ' / ' + item['capability'] if 'capability' in item else item['id']
            lines += [name + ' [' + item['state'] + ']', '  ' + item['purpose']]
        if data.get('next_offset') is not None:
            lines += ['More: skills --offset ' + str(data['next_offset'])]
    elif command == 'check':
        lines += ['Checks: ' + data['status'], 'Working folder: ' + data['working_root']]
        for check in data['checks'].get('check_results', []):
            lines += [check['id'] + ': ' + check['status']]
        for finding in data['checks'].get('findings', []):
            lines += [finding['code'] + ': ' + finding['message']]
        lines += [data['limits']]
    elif command == 'repair':
        lines += ['Repair: ' + data['repair'], 'Session: ' + str(data.get('session'))]
        if data.get('working_root'):
            lines += ['Working folder: ' + data['working_root'], 'Run edits, tests and Git there; this process cannot change your shell directory.']
    else:
        lines += ['Result: ' + data.get('status', 'unknown')]
        if data.get('installation_note'):
            lines += [data['installation_note']]
        repair = data.get('repair')
        if repair:
            lines += ['Source review: ' + repair.get('action', 'unknown')]
            for field in ('checks', 'conflicts', 'dependency_drift', 'reference_drift'):
                if field in repair:
                    lines += [field + ': ' + str(repair[field])]
            if repair.get('paths'):
                lines += ['Paths:'] + ['  ' + path for path in repair['paths']]
            if repair.get('diff'):
                lines += [repair['diff']]
        for host in data.get('installations', []):
            binding = host['binding']
            lines += ['Installation: ' + binding['host'] + ' at ' + binding['config_dir'],
                      'Managed targets:'] + ['  ' + target for target in host['before']]
            lines += ['Installer comparison before source deployment: ' + json.dumps(host['changes'], sort_keys=True)]
        if data.get('source'):
            lines += ['Source: ' + data['source']['action'], 'Live Git index: ' + data['source'].get('git_index', 'unknown')]
            for key in ('commit', 'rollback'):
                if data['source'].get(key):
                    lines += [key + ': ' + data['source'][key]]
        if data.get('status') in ('partial', 'failed'):
            for attempted in data.get('attempted_hosts', []):
                lines += ['Attempted host: ' + attempted['binding']['host'], 'Backup location: ' + attempted['backup']]
        for host in data.get('hosts', []):
            lines += ['Installation verified: ' + host['verification']['host']]
        for key in ('preview_id', 'receipt', 'error', 'next'):
            if data.get(key):
                lines += [key + ': ' + str(data[key])]
    return '\n'.join(lines)

def envelope(command, result):
    return {'schema': SCHEMA, 'command': command, 'authority': 'none', 'result': result}

def main(argv=None, *, implementation_root):
    raw = list(sys.argv[1:] if argv is None else argv)
    as_json = '--json' in raw
    try:
        args = parser().parse_args(raw)
        as_json = getattr(args, 'json', False)
        root = safe_path(getattr(args, 'root', implementation_root))
        if not root.is_dir():
            raise MaintenanceError('REPOSITORY_ROOT_MISSING')
        command = args.command or 'status'
        session = session_id(root, getattr(args, 'session', None))
        # An edited candidate facade cannot use --root to manage its original source.
        if candidate_source(implementation_root) and root != implementation_root and command not in ('status', 'skills', 'check'):
            raise MaintenanceError('CANDIDATE_CANNOT_CONTROL_SOURCE')
        if command == 'status':
            selected = adapters.select(root, getattr(args, 'host', []), getattr(args, 'config_dir', None))
            out = inspection.status(root, session, adapters, selected)
        elif command == 'skills':
            out = inspection.metadata(root, args.name, args.offset, args.limit)
        elif command == 'check':
            out = checks.check(root, session, args.path, args.full, args.approval_ref)
        elif command == 'repair':
            out = workspace.repair(root, session, args.state == 'on')
        else:
            if args.approve:
                if args.preview or args.host or args.config_dir:
                    raise MaintenanceError('APPROVAL_CANNOT_CHANGE_REVIEWED_TARGETS')
                out = operations.apply_preview(root, args.approve, args.approval_ref, expected_kind=command)
            else:
                hosts = adapters.select(root, args.host, args.config_dir)
                interactive = not as_json and not args.preview and sys.stdin.isatty() and sys.stdout.isatty()
                if command == 'refresh' and not hosts:
                    if interactive:
                        name = input('Configure which host? [codex/claude/cancel]: ').strip().lower()
                        if name not in adapters.HOSTS:
                            raise MaintenanceError('NO_HOST_SELECTED')
                        hosts = adapters.select(root, [name])
                    else:
                        raise MaintenanceError('NO_HOST_CONFIGURED: use --host codex or --host claude')
                out = operations.make_preview(root, session, command, hosts, args.approval_ref or 'terminal-request')
                if interactive and out['status'] == 'awaiting-approval':
                    print(render(envelope(command, out)))
                    agreed = input('Apply this exact review, including the listed installation targets? [y/N]: ').strip().lower()
                    if agreed in ('y', 'yes'):
                        out = operations.apply_preview(root, out['preview_id'], 'interactive-terminal-agreement', expected_kind=command)
                    else:
                        out = out | {'status': 'cancelled', 'next': 'Contained work retained; nothing applied.'}
        value = envelope(command, out)
        print(json.dumps(value, ensure_ascii=False, separators=(',', ':')) if as_json else render(value))
        if args.command is None and not as_json:
            print('\nCommands: status | skills [NAME] | check | repair on/off | update | refresh')
        status = out.get('status')
        if status in ('blocked', 'partial', 'failed', 'BLOCK'):
            return 2
        if status == 'awaiting-approval':
            return 3
        if status == 'REVIEW':
            return 1
        return 0
    except (MaintenanceError, OSError, ValueError, subprocess.TimeoutExpired) as exc:
        reason = str(exc) if isinstance(exc, MaintenanceError) else type(exc).__name__
        value = {'schema': SCHEMA, 'status': 'error', 'reason': reason, 'authority': 'none'}
        print(json.dumps(value, separators=(',', ':')) if as_json else render(value))
        return 2
