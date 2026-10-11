"""Human and machine clients share the same maintenance operations."""
import argparse
import json
from pathlib import Path
import sys
import subprocess
from . import adapters, checks, inspection, operations, updater, workflow, workspace
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
    sub.add_parser('help', parents=[common], help='Compact everyday command walkthrough')
    s = sub.add_parser('status', parents=[common], help='Compact package, version, source and global freshness summary')
    d = sub.add_parser('skills', parents=[common], help='Declared package/capability metadata only')
    d.add_argument('name', nargs='?')
    d.add_argument('detail', nargs='?', choices=('help',))
    d.add_argument('--offset', type=int, default=0)
    d.add_argument('--limit', type=int, default=8)
    l = sub.add_parser('lifecycle', parents=[common], help='Publication, release, global CLI and host freshness')
    l.add_argument('name', nargs='?', help='Exact declared distribution owner')
    l.add_argument('--detail', action='store_true', help='Show evidence beyond the compact receipt')
    l.add_argument('--check-remotes', action='store_true', help='Explicitly fetch origin before publication checks')
    c = sub.add_parser('check', parents=[common], help='Required local artifact checks')
    c.add_argument('--path', action='append', default=[])
    c.add_argument('--full', action='store_true')
    c.add_argument('--approval-ref')
    sub.add_parser('doctor', parents=[common], help='Full verification plus detailed status diagnosis')
    r = sub.add_parser('repair', parents=[common], help='Create, pause, or apply the selected contained workspace')
    r.add_argument('state', choices=('on', 'off', 'apply'))
    r.add_argument('--preview', action='store_true', help='Prepare contained apply review without applying')
    r.add_argument('--approve', metavar='PREVIEW_ID', help='Apply an exact reviewed contained-workspace preview')
    r.add_argument('--approval-ref', help='Reference to actual user agreement for contained apply')
    r.add_argument('--host', choices=sorted(adapters.HOSTS), action='append', default=[])
    r.add_argument('--config-dir', type=Path)
    w = sub.add_parser('work', parents=[common], help='Start or resume contained work for one public skill')
    w.add_argument('name', help='Exact public skill ID')
    f = sub.add_parser('finish', parents=[common], help='Check one skill and prepare or apply its exact work review')
    f.add_argument('name', help='Exact public skill ID')
    f.add_argument('--preview', action='store_true', help='Prepare the finish review without applying')
    f.add_argument('--approve', metavar='PREVIEW_ID', help='Apply the exact reviewed finish preview')
    f.add_argument('--approval-ref', help='Reference to actual user agreement for this finish review')
    u = sub.add_parser('update', parents=[common], help='Verify remotes and review all declared global updates')
    u.add_argument('name', nargs='?', help='Optional declared package to update without blocking on unrelated dirty work')
    u.add_argument('--preview', action='store_true', help='Prepare update review without applying')
    u.add_argument('--approve', metavar='PREVIEW_ID', help='Apply an exact reviewed global-update preview')
    u.add_argument('--approval-ref', help='Reference to actual user agreement for global update')
    for name in ('refresh',):
        a = sub.add_parser(name, parents=[common], help='Review and approve managed installation refresh')
        a.add_argument('--preview', action='store_true', help='Prepare review without applying')
        a.add_argument('--approve', metavar='PREVIEW_ID', help='Host attests actual agreement to this saved exact review')
        a.add_argument('--approval-ref', help='Reference to actual user agreement when applying a saved preview')
    for a in (s, sub.choices['refresh']):
        a.add_argument('--host', choices=sorted(adapters.HOSTS), action='append', default=[])
        a.add_argument('--config-dir', type=Path, help='Explicit configuration root for one host; also used for contained tests')
    return p

def render(value):
    command = value.get('command')
    data = value.get('result', {})
    if value.get('status') == 'error':
        return 'Blocked: ' + value['reason']
    lines = []
    if command == 'help':
        lines += ['Skills AI commands:',
                  '  status             versions, source, commands and hosts',
                  '  help               this compact walkthrough',
                  '  check              verify current changed scope',
                  '  work NAME          start or resume contained work for one skill',
                  '  finish NAME        check work and print the exact approval/update command',
                  '  update [NAME]      fetch, verify and review declared updates',
                  '  skills [NAME]      list skills or inspect one',
                  '  skills NAME help   show controls, commands and boundaries',
                  '  doctor             full verification and detailed diagnosis',
                  '',
                  'Advanced: lifecycle [PACKAGE] | repair on/off/apply | refresh --host HOST',
                  'Writes, installations and updates show an exact preview and require approval.',
                  '',
                  'Skills:']
        for skill in data.get('skills', []):
            purpose = skill['purpose'].split(';', 1)[0].rstrip()
            lines += ['  ' + skill['id'] + ' [' + skill['state'] + '/' + skill['role'] +
                      '] — ' + purpose]
        lines += ['', 'For one skill: #> <skill-name> help  |  skills_ai skills <NAME> help',
                  data.get('limits', 'Help is read-only metadata and grants no authority.')]
    elif command == 'status':
        source = data['source']
        lines += ['Source: ' + source['revision'][:12], 'Git: ' + ('clean' if source['clean'] else 'has local changes')]
        if data.get('candidate_of'):
            lines += ['Contained candidate of: ' + data['candidate_of'], 'Repair below describes this root only, not its source association.']
        repair = data['runtime'].get('repair', {})
        lines += ['Repair: ' + repair.get('repair', 'unknown')]
        if repair.get('working_root'):
            lines += ['Working folder: ' + repair['working_root']]
        catalog = data['runtime'].get('catalog', {})
        packages = data.get('packages', {})
        counts = packages.get('counts', {})
        if packages:
            lines += ['Skills: ' + str(packages.get('total', 'unknown')) +
                      ' — active ' + str(counts.get('active', 0)) +
                      ', manual ' + str(counts.get('manual', 0)) +
                      ', off ' + str(counts.get('off', 0))]
            for item in packages.get('items', []):
                version = item.get('version') or item['status']
                lines += ['  ' + item['package'] + ' ' + version + ' [' + str(item['state']) + ']']
        else:
            lines += ['Capabilities: ' + str(catalog.get('total', 'unknown')) + ' (declared packages are skills)']
        empty = sorted({item.get('package') or item['capability'] for item in catalog.get('capabilities', [])
                        if item.get('unavailable_reason') == 'PACKAGE_NOT_INITIALIZED'})
        if empty:
            lines += ['Unavailable, empty package folders: ' + ', '.join(empty),
                      'Fix: git submodule update --init --recursive']
        for host in data['installations']:
            lines += [host['host'] + ': ' + host['status'] + ' — ' + host['config_dir']]
        if not data['installations']:
            lines += ['No host bindings saved. Inspect with status --host codex; configure through refresh --host codex.']
        distribution = data.get('lifecycle', {})
        commands = [command_item for item in distribution.get('items', []) for command_item in item.get('commands', [])]
        if commands:
            lines += ['Global commands: ' + ', '.join(
                command_item['name'] + ' ' +
                (str(command_item.get('installed_version')) + ' ' if command_item.get('installed_version') else '') +
                command_item['status'] for command_item in commands)]
        lines += ['Overall: ' + data.get('status', 'unknown')]
        if data.get('next'):
            lines += ['Next: ' + data['next']]
        lines += [data['context']]
    elif command == 'skills':
        if data.get('schema') == 'skills-ai/skill-help/1':
            skill = data['skill']
            lines += [
                'Skill help — ' + skill['id'],
                'State: ' + skill['state'] + ' · Role: ' + skill['role'],
                'Purpose: ' + skill['purpose'],
            ]
            for key, label in (('use_when', 'Use when'), ('not_for', 'Do not use for')):
                if data.get(key):
                    lines += ['', label] + ['- ' + item for item in data[key]]
            for key, label in (
                ('chat', 'Chat controls'),
                ('terminal', 'Terminal commands'),
                ('keywords', 'Workflow keywords'),
            ):
                if data.get(key):
                    lines += ['', label]
                    for item in data[key]:
                        lines += ['- ' + item['syntax'] + ' — ' + item['does'],
                                  '  Boundary: ' + item['boundary']]
            lines += ['', 'More detail'] + ['- ' + entry for entry in data.get('entries', [])]
            lines += ['', data['limits']]
        else:
            for item in data.get('items', []):
                name = item['package'] + ' / ' + item['capability'] if 'capability' in item else item['id']
                lines += [name + ' [' + item['state'] + ']', '  ' + item['purpose']]
            if data.get('next_offset') is not None:
                lines += ['More: skills --offset ' + str(data['next_offset'])]
    elif command == 'lifecycle':
        labels = {'current': 'current', 'pending': 'pending', 'unknown': 'unknown', 'not-applicable': 'n/a'}
        for item in data.get('items', []):
            axes = item['axes']
            summary = ' | '.join(name + ' ' + labels.get(axes[name], axes[name])
                                 for name in ('source', 'child', 'parent', 'release', 'cli', 'hosts'))
            lines += ['Lifecycle ' + item['package'] + ': ' + summary,
                      'Status: ' + ('globally current' if item['globally_current'] else item['status'])]
            if not item['globally_current']:
                lines += ['Next: ' + item['next'][0]]
            if data.get('detail'):
                lines += ['  source ' + item['source']['revision'][:12] +
                          ' (' + item['source']['remote_evidence'] + ')']
                if item.get('child_pin'):
                    lines += ['  parent pin ' + item['child_pin'][:12]]
                for command_item in item['commands']:
                    version = command_item.get('installed_version')
                    lines += ['  command ' + command_item['name'] + ': ' + command_item['status'] +
                              ((' ' + str(version)) if version else '')]
                for host in item['hosts']:
                    lines += ['  host ' + host['host'] + ': ' + host['status']]
                lines += ['  limit: ' + item['limits']]
    elif command == 'check':
        lines += ['Checks: ' + data['status'], 'Working folder: ' + data['working_root']]
        for check in data['checks'].get('check_results', []):
            lines += [check['id'] + ': ' + check['status']]
        for finding in data['checks'].get('findings', []):
            lines += [finding['code'] + ': ' + finding['message']]
        lines += [data['limits']]
    elif command == 'doctor':
        verification = data.get('verification', {})
        lines += ['Doctor: ' + data.get('status', 'unknown'),
                  'Verification: ' + str(verification.get('passed', 0)) + ' passed, ' +
                  str(verification.get('failed', 'unknown')) + ' failed']
        current = data.get('current', {})
        lines += ['Current status: ' + current.get('status', 'unknown')]
        if current.get('next'):
            lines += ['Next: ' + current['next']]
        lines += [data['limits']]
    elif command in ('work', 'finish'):
        report = data.get('report', {})
        lines += [report.get('outcome', command.title()) + ' — ' +
                  report.get('package', data.get('package', 'unknown'))]
        if report.get('detail'):
            lines += [report['detail']]
        if report.get('checks'):
            lines += ['Checks: ' + report['checks']]
        if report.get('changed_paths'):
            lines += ['Changed paths: ' + str(len(report['changed_paths']))]
            lines += ['  ' + path for path in report['changed_paths'][:8]]
            if len(report['changed_paths']) > 8:
                lines += ['  … ' + str(len(report['changed_paths']) - 8) + ' more']
        if data.get('working_root'):
            lines += ['Work area: ' + data['working_root']]
        if report.get('next_command'):
            label = 'Approve with:' if data.get('status') == 'awaiting-approval' else 'Next command:'
            lines += [label, '  ' + report['next_command']]
            if data.get('approval_reply'):
                lines += ['Or reply in chat: ' + data['approval_reply']]
        elif data.get('next'):
            lines += ['Next: ' + data['next']]
    elif command == 'update':
        package = data.get('package')
        lines += [('Update report' + ((' — ' + package) if package else '')) +
                  ': ' + data.get('status', 'unknown')]
        completed = bool(data.get('operation_id'))
        sources = data.get('sources', {})
        parent = sources.get('parent', {})
        if parent:
            lines += ['  parent: ' + parent.get('relation', 'unknown')]
        for child in sources.get('children', []):
            relation = child.get('relation', child.get('status', 'unknown'))
            lines += ['  ' + child['name'] + ': ' + relation]
        for command_item in data.get('commands', []):
            name = command_item.get('distribution', command_item.get('name', 'unknown'))
            lines += ['  command: ' + name + (' ' + command_item.get('status', 'updated')
                                            if completed else ' would update')]
        for host in data.get('installations', []):
            lines += ['  host: ' + host['binding']['host'] + ' would update']
        for host in data.get('hosts', []):
            verification = host.get('verification', {})
            lines += ['  host: ' + verification.get('host', 'unknown') + ' updated']
        verification = data.get('verification', {})
        if verification:
            lines += ['Checks: ' + str(verification.get('passed', 0)) + ' passed, ' +
                      str(verification.get('failed', 0)) + ' failed']
        if sources.get('preserved_parent_changes'):
            lines += ['Preserved unrelated parent changes.']
        if data.get('receipt'):
            lines += ['Receipt: ' + data['receipt']]
        if data.get('error'):
            lines += ['Error: ' + data['error']]
        if data.get('approval_command'):
            lines += ['Approve with:', '  ' + data['approval_command']]
            if data.get('approval_reply'):
                lines += ['Or reply in chat: ' + data['approval_reply']]
        elif data.get('next_command'):
            lines += ['Next command:', '  ' + data['next_command']]
        elif data.get('next'):
            lines += ['Next: ' + data['next']]
    elif command == 'repair' and data.get('kind') != 'repair-apply':
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
        if data.get('status') == 'awaiting-approval':
            if command == 'refresh':
                names = [item['binding']['host'] for item in data.get('installations', [])]
                approval_command = 'skills_ai refresh' + ''.join(' --host ' + name for name in names)
                approval_reply = 'approve ' + (' and '.join(names) if names else 'host') + ' refresh'
            else:
                approval_command = 'skills_ai repair apply'
                approval_reply = 'approve contained work apply'
            lines += ['Approve with:', '  ' + approval_command,
                      'Or reply in chat: ' + approval_reply]
        for key in ('receipt', 'error', 'next'):
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
        if candidate_source(implementation_root) and root != implementation_root and command not in ('help', 'status', 'skills', 'lifecycle', 'check', 'doctor'):
            raise MaintenanceError('CANDIDATE_CANNOT_CONTROL_SOURCE')
        if command == 'help':
            out = inspection.help_overview(root)
        elif command == 'status':
            selected = adapters.select(root, getattr(args, 'host', []), getattr(args, 'config_dir', None))
            out = inspection.status(root, session, adapters, selected)
        elif command == 'skills':
            out = (inspection.help_metadata(root, args.name)
                   if args.detail == 'help'
                   else inspection.metadata(root, args.name, args.offset, args.limit))
        elif command == 'lifecycle':
            out = inspection.lifecycle_status(root, adapters, args.name, args.check_remotes)
            out['detail'] = args.detail
        elif command == 'check':
            out = checks.check(root, session, args.path, args.full, args.approval_ref)
        elif command == 'doctor':
            selected = adapters.select(root, getattr(args, 'host', []), getattr(args, 'config_dir', None))
            out = inspection.doctor(root, session, adapters, selected)
        elif command == 'repair':
            if args.state in ('on', 'off'):
                if args.preview or args.approve or args.approval_ref or args.host or args.config_dir:
                    raise MaintenanceError('REPAIR_STATE_REJECTS_APPLY_OPTIONS')
                out = workspace.repair(root, session, args.state == 'on')
            elif args.approve:
                if args.preview or args.host or args.config_dir:
                    raise MaintenanceError('APPROVAL_CANNOT_CHANGE_REVIEWED_TARGETS')
                out = operations.apply_preview(root, args.approve, args.approval_ref, expected_kind='repair-apply')
            else:
                hosts = adapters.select(root, args.host, args.config_dir)
                out = operations.make_preview(root, session, 'repair-apply', hosts,
                                              args.approval_ref or 'terminal-request')
                interactive = not as_json and not args.preview and sys.stdin.isatty() and sys.stdout.isatty()
                if interactive and out['status'] == 'awaiting-approval':
                    print(render(envelope(command, out)))
                    agreed = input('Apply this exact contained-workspace review? [y/N]: ').strip().lower()
                    if agreed in ('y', 'yes'):
                        out = operations.apply_preview(
                            root, out['preview_id'], 'interactive-terminal-agreement',
                            expected_kind='repair-apply')
                    else:
                        out = out | {'status': 'cancelled',
                                     'next': 'Contained work retained; nothing applied.'}
        elif command == 'work':
            out = workflow.work(root, session, args.name)
        elif command == 'finish':
            if args.approve:
                if args.preview:
                    raise MaintenanceError('APPROVAL_CANNOT_CHANGE_REVIEWED_TARGETS')
                out = workflow.finish_apply(root, args.name, args.approve, args.approval_ref)
            else:
                out = workflow.finish_preview(root, session, args.name,
                                              args.approval_ref or 'terminal-request')
                interactive = not as_json and not args.preview and sys.stdin.isatty() and sys.stdout.isatty()
                if interactive and out['status'] == 'awaiting-approval':
                    print(render(envelope(command, out)))
                    agreed = input('Apply the reviewed skill work? [y/N]: ').strip().lower()
                    if agreed in ('y', 'yes'):
                        out = workflow.finish_apply(
                            root, args.name, out['preview_id'], 'interactive-terminal-agreement')
                    else:
                        out = out | {'status': 'cancelled',
                                     'next': 'Contained work retained; nothing applied.'}
        elif command == 'update':
            if args.approve:
                if args.preview:
                    raise MaintenanceError('APPROVAL_CANNOT_CHANGE_REVIEWED_TARGETS')
                out = updater.apply(root, args.approve, args.approval_ref, package=args.name)
            else:
                out = updater.preview(root, package=args.name,
                                      approval_ref=args.approval_ref or 'terminal-request')
                interactive = not as_json and not args.preview and sys.stdin.isatty() and sys.stdout.isatty()
                if interactive and out['status'] == 'awaiting-approval':
                    print(render(envelope(command, out)))
                    agreed = input('Apply this exact global update review? [y/N]: ').strip().lower()
                    if agreed in ('y', 'yes'):
                        out = updater.apply(root, out['preview_id'], 'interactive-terminal-agreement',
                                            package=args.name)
                    else:
                        out = out | {'status': 'cancelled', 'next': 'Nothing updated.'}
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
            print('\nCommands: status | help | work NAME | finish NAME | update [NAME] | skills [NAME] | doctor')
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
