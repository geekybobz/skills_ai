"""CLI contracts and real repair/installer flows in private synthetic repositories.

The fixture scanner deliberately reports synthetic PASS. Repository acceptance
runs separately against the actual changed candidate, not this fixture result.
"""
import contextlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "orchestrator" / "runtime"))
from maintenance import adapters, checks, cli, operations, workspace
from maintenance.common import AREA, SCHEMA, MaintenanceError, fingerprint, read_state, write_state


class MaintenanceTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        for folder in ('runtime', 'tools'):
            shutil.copytree(
                ROOT / 'orchestrator' / folder,
                self.root / 'orchestrator' / folder,
                ignore=shutil.ignore_patterns('__pycache__', '*.pyc'),
            )
        (self.root / 'orchestrator/adapters/claude').mkdir(parents=True)
        shutil.copy(ROOT / 'orchestrator/adapters/claude/skills-ai-context.js', self.root / 'orchestrator/adapters/claude/skills-ai-context.js')
        (self.root / 'orchestrator/governance').mkdir(parents=True)
        (self.root / 'orchestrator/governance/CONTRACT.json').write_text('{"allowed_external_symlinks": []}')
        (self.root / 'orchestrator/tools/scan_consistency.py').write_text(
            'import json\nprint(json.dumps({"status":"PASS","check_results":[{"id":"synthetic-fixture","status":"pass"}]}))\n')
        (self.root / '.gitignore').write_text('.runtime/\n.env*\n')
        (self.root / 'owned.txt').write_text('original')
        (self.root / 'untouched.txt').write_text('preserve')
        for args in (('init', '-q'), ('config', 'user.name', 'test'),
                     ('config', 'user.email', 'test@invalid'), ('add', '--all'),
                     ('-c', 'core.hooksPath=/dev/null', 'commit', '-qm', 'fixture')):
            subprocess.run(['git', '-C', str(self.root), *args], check=True, capture_output=True)
        self.session = 'fixture-session'
        self.binding = {'host': 'codex', 'config_dir': str(self.root / '.runtime/test-config')}

    def start(self):
        out = workspace.repair(self.root, self.session, True)
        self.candidate = Path(out['working_root'])
        return out

    def preview(self, hosts=()):
        return operations.make_preview(self.root, self.session, 'update', list(hosts), 'fixture-scope')

    def apply(self, preview, kind='update'):
        return operations.apply_preview(self.root, preview['preview_id'], 'fixture-human-agreement', expected_kind=kind)

    def invoke(self, arguments, implementation=None):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = cli.main(arguments, implementation_root=implementation or self.root)
        return code, output.getvalue()

    def test_repair_repeat_pause_resume_preserves_work(self):
        first = self.start()
        (self.candidate / 'owned.txt').write_text('pending')
        self.assertEqual(first['workspace'], workspace.repair(self.root, self.session, True)['workspace'])
        self.assertEqual('off', workspace.repair(self.root, self.session, False)['repair'])
        self.assertEqual('pending', (self.candidate / 'owned.txt').read_text())
        self.assertEqual(first['workspace'], workspace.repair(self.root, self.session, True)['workspace'])

    def test_fresh_terminal_identity_is_saved_only_on_repair_on(self):
        self.assertFalse((self.root / AREA).exists())
        out = workspace.repair(self.root, None, True)
        self.assertEqual(out['session'], read_state(self.root / AREA / 'terminal-session.json')['session'])

    def test_json_preview_never_applies_without_approval(self):
        self.start()
        (self.candidate / 'owned.txt').write_text('pending')
        code, output = self.invoke(['update', '--json', '--session', self.session])
        self.assertEqual(3, code)
        self.assertEqual('awaiting-approval', json.loads(output)['result']['status'])
        self.assertEqual('original', (self.root / 'owned.txt').read_text())

    def interactive(self, answer):
        class TerminalOutput(io.StringIO):
            def isatty(self):
                return True
        self.start()
        (self.candidate / 'owned.txt').write_text('reviewed edit')
        output = TerminalOutput()
        def agree(prompt):
            self.assertIn('owned.txt', output.getvalue())
            self.assertIn(self.binding['config_dir'], output.getvalue())
            self.assertEqual('original', (self.root / 'owned.txt').read_text())
            return answer
        with contextlib.redirect_stdout(output), patch.object(sys.stdin, 'isatty', return_value=True), patch('builtins.input', side_effect=agree):
            code = cli.main(['update', '--session', self.session, '--host', 'codex',
                             '--config-dir', self.binding['config_dir']], implementation_root=self.root)
        return code, output.getvalue()

    def test_interactive_approval_follows_visible_exact_review(self):
        code, output = self.interactive('yes')
        self.assertEqual(0, code)
        self.assertEqual('reviewed edit', (self.root / 'owned.txt').read_text())
        self.assertIn('Installation verified: codex', output)

    def test_interactive_cancellation_retains_candidate(self):
        code, output = self.interactive('no')
        self.assertEqual(0, code)
        self.assertEqual('original', (self.root / 'owned.txt').read_text())
        self.assertEqual('reviewed edit', (self.candidate / 'owned.txt').read_text())
        self.assertIn('cancelled', output)

    def test_dirty_work_index_preservation_and_combined_update_refresh(self):
        (self.root / 'untouched.txt').write_text('user dirty content')
        before_index = (self.root / '.git/index').read_bytes()
        self.start()
        (self.candidate / 'owned.txt').write_text('deployed')
        reviewed = self.preview([self.binding])
        out = self.apply(reviewed)
        self.assertEqual('complete', out['status'])
        self.assertEqual('deployed', (self.root / 'owned.txt').read_text())
        self.assertEqual('user dirty content', (self.root / 'untouched.txt').read_text())
        self.assertEqual(before_index, (self.root / '.git/index').read_bytes())
        self.assertEqual('current', adapters.check(self.root, self.binding)['status'])
        self.assertTrue(Path(out['source']['rollback']).is_file())
        self.assertEqual([self.binding], adapters.bindings(self.root))
        self.assertEqual(0o600, Path(out['receipt']).stat().st_mode & 0o777)

    def test_candidate_change_invalidates_review(self):
        self.start()
        (self.candidate / 'owned.txt').write_text('first')
        reviewed = self.preview()
        (self.candidate / 'owned.txt').write_text('second')
        out = self.apply(reviewed)
        self.assertEqual('failed', out['status'])
        self.assertIn('PREVIEW_CHANGED', out['error'])
        self.assertEqual('original', (self.root / 'owned.txt').read_text())

    def test_source_template_change_invalidates_review(self):
        reviewed = operations.make_preview(self.root, self.session, 'refresh', [self.binding])
        (self.root / 'orchestrator/runtime/skills-orchestrator/SKILL.md').write_text('changed')
        with self.assertRaisesRegex(MaintenanceError, 'SOURCE_CHANGED'):
            self.apply(reviewed, 'refresh')
        self.assertFalse(Path(self.binding['config_dir']).exists())

    def test_host_change_invalidates_review_before_source_deploy(self):
        self.start()
        (self.candidate / 'owned.txt').write_text('candidate')
        reviewed = self.preview([self.binding])
        target = adapters.targets(self.binding)[0]
        target.parent.mkdir(parents=True)
        target.write_text('foreign content')
        with self.assertRaises(MaintenanceError):
            self.apply(reviewed)
        self.assertEqual('original', (self.root / 'owned.txt').read_text())
        self.assertEqual('foreign content', target.read_text())

    def test_missing_actual_agreement_refuses_apply(self):
        reviewed = operations.make_preview(self.root, None, 'refresh', [self.binding])
        with self.assertRaisesRegex(MaintenanceError, 'ACTUAL_APPROVAL'):
            operations.apply_preview(self.root, reviewed['preview_id'], None, expected_kind='refresh')

    def test_unready_checks_cannot_deploy(self):
        self.start()
        (self.candidate / 'owned.txt').write_text('candidate')
        (self.candidate / 'orchestrator/tools/scan_consistency.py').write_text('import json\nprint(json.dumps({"status":"BLOCK"}))\n')
        reviewed = self.preview()
        self.assertEqual('blocked', reviewed['status'])
        with self.assertRaisesRegex(MaintenanceError, 'UNREADY'):
            self.apply(reviewed)
        self.assertEqual('original', (self.root / 'owned.txt').read_text())

    def test_failed_live_checks_restore_source(self):
        self.start()
        (self.candidate / 'owned.txt').write_text('candidate')
        reviewed = self.preview()
        # The live scan script itself must not drift: simulate the process result.
        original = workspace.run_tool
        def failing(root, script, args):
            if 'apply' in args:
                from importlib.util import spec_from_file_location, module_from_spec
                sys.path.insert(0, str(self.root / 'orchestrator/tools'))
                spec = spec_from_file_location('fixture_repair_failure', self.root / 'orchestrator/runtime/repair_workspace.py')
                repair = module_from_spec(spec); spec.loader.exec_module(repair)
                try:
                    repair.apply_update(root, self.session, reviewed['repair']['preview_id'], write=True,
                        approval_ref='fixture-agreement', checker=lambda *a: {'status':'BLOCK'})
                except ValueError as exc:
                    return {'tool_returncode':2, 'reason':str(exc)}
            return original(root, script, args)
        with patch.object(workspace, 'run_tool', side_effect=failing):
            out = self.apply(reviewed)
        self.assertEqual('failed', out['status'])
        self.assertEqual('original', (self.root / 'owned.txt').read_text())

    def test_host_failure_after_source_deploy_reports_partial(self):
        self.start()
        (self.candidate / 'owned.txt').write_text('deployed')
        reviewed = self.preview([self.binding])
        with patch.object(adapters, 'refresh', side_effect=MaintenanceError('HOST_INSTALL_FAILED')):
            out = self.apply(reviewed)
        self.assertEqual('partial', out['status'])
        self.assertEqual('deployed', (self.root / 'owned.txt').read_text())
        self.assertIn('retry refresh only', out['next'])
        self.assertEqual(1, len(out['attempted_hosts']))

    def test_install_refresh_and_repeated_entry_is_unchanged(self):
        reviewed = operations.make_preview(self.root, None, 'refresh', [self.binding])
        first = self.apply(reviewed, 'refresh')
        self.assertEqual('complete', first['status'])
        target = adapters.targets(self.binding)[0]
        before = (fingerprint(target), target.stat().st_mtime_ns)
        reviewed = operations.make_preview(self.root, None, 'refresh', adapters.bindings(self.root))
        self.assertEqual('unchanged', reviewed['status'])
        self.assertEqual(before, (fingerprint(target), target.stat().st_mtime_ns))
        self.assertEqual('current', adapters.check(self.root, self.binding)['status'])

    def test_shared_lock_blocks_concurrent_operations(self):
        from maintenance.common import operation_lock
        with operation_lock(self.root):
            with self.assertRaisesRegex(MaintenanceError, 'BUSY'):
                operations.make_preview(self.root, None, 'refresh', [self.binding])

    def test_two_host_refresh_preserves_foreign_settings(self):
        claude = {'host': 'claude', 'config_dir': str(self.root / '.runtime/test-claude')}
        settings = Path(claude['config_dir']) / 'settings.json'
        settings.parent.mkdir(parents=True)
        settings.write_text(json.dumps({'env':{'KEEP':'original'}, 'hooks':{'SessionStart':[
            {'hooks':[{'type':'command','command':'foreign-command'}]}]}}))
        reviewed = operations.make_preview(self.root, None, 'refresh', [self.binding, claude])
        out = self.apply(reviewed, 'refresh')
        self.assertEqual('complete', out['status'])
        self.assertEqual(2, len(out['hosts']))
        saved = json.loads(settings.read_text())
        self.assertEqual('original', saved['env']['KEEP'])
        self.assertIn('foreign-command', json.dumps(saved))
        self.assertEqual('current', adapters.check(self.root, claude)['status'])
        repeated = operations.make_preview(self.root, None, 'refresh', [claude, self.binding])
        self.assertEqual('unchanged', repeated['status'])

    def test_interrupt_keeps_receipt_and_actual_source_effects(self):
        self.start()
        (self.candidate / 'owned.txt').write_text('deployed')
        reviewed = self.preview([self.binding])
        with patch.object(adapters, 'refresh', side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt):
                self.apply(reviewed)
        receipts = list((self.root / AREA / 'receipts').glob('*.json'))
        self.assertEqual(1, len(receipts))
        saved = read_state(receipts[0])
        self.assertEqual('running', saved['status'])
        self.assertEqual('refresh', saved['phase'])
        self.assertEqual('updated', saved['source']['action'])
        self.assertEqual('deployed', (self.root / 'owned.txt').read_text())

    def test_invalid_host_value_has_structured_error(self):
        with self.assertRaisesRegex(MaintenanceError, 'INVALID_HOST'):
            adapters.validate({'host':[], 'config_dir':str(self.root)})

    def test_empty_explicit_session_never_uses_environment_default(self):
        from maintenance.common import session_id
        with patch.dict(os.environ, {'CODEX_THREAD_ID':'other-session'}):
            with self.assertRaisesRegex(MaintenanceError, 'INVALID_SESSION'):
                session_id(self.root, '')

    def test_claude_backup_targets_are_reviewed_and_symlinks_refused(self):
        binding = {'host':'claude', 'config_dir':str(self.root / '.runtime/claude')}
        targets = adapters.targets(binding)
        self.assertEqual(4, len(targets))
        targets[1].parent.mkdir(parents=True)
        targets[1].write_text('{}')
        reviewed = adapters.preview(self.root, binding)
        self.assertIn(str(targets[2]), reviewed['before'])
        self.assertIn('settings_backup', reviewed['changes'])
        outside = self.root / 'outside'; outside.write_text('foreign')
        targets[2].symlink_to(outside)
        with self.assertRaisesRegex(MaintenanceError, 'SYMLINK'):
            adapters.preview(self.root, binding)

    def test_installer_change_requires_separate_refresh_review(self):
        self.start()
        with (self.candidate / 'orchestrator/tools/install_runtime_adapter.py').open('a') as handle:
            handle.write('\n# fixture installer revision\n')
        with self.assertRaisesRegex(MaintenanceError, 'INSTALLER_CHANGED'):
            self.preview([self.binding])

    def test_new_cli_paths_have_roles_and_support_layer(self):
        sys.path.insert(0, str(ROOT / "orchestrator" / "tools"))
        from change_guard import load_contract, matching_roles
        from graph_layers import classify_path
        contract = load_contract(ROOT)
        for path in ('orchestrator/tools/skills_ai', 'orchestrator/tools/skills_ai.py', 'orchestrator/runtime/maintenance/cli.py',
                     'orchestrator/governance/TERMINAL_MAINTENANCE.md'):
            self.assertTrue(matching_roles(path, contract))
            self.assertEqual('L5', classify_path(path))

    def test_foreign_entry_is_preserved(self):
        target = adapters.targets(self.binding)[0]
        target.parent.mkdir(parents=True)
        target.write_text('unrelated user instructions')
        with self.assertRaisesRegex(MaintenanceError, 'FOREIGN'):
            operations.make_preview(self.root, None, 'refresh', [self.binding])
        self.assertEqual('unrelated user instructions', target.read_text())

    def test_symlink_file_and_ancestor_are_refused(self):
        outside = self.root / 'outside'
        outside.write_text('foreign')
        target = adapters.targets(self.binding)[0]
        target.parent.mkdir(parents=True)
        target.symlink_to(outside)
        with self.assertRaisesRegex(MaintenanceError, 'SYMLINK'):
            adapters.preview(self.root, self.binding)
        target.unlink()
        directory = self.root / 'link'
        directory.symlink_to(target.parent, target_is_directory=True)
        with self.assertRaisesRegex(MaintenanceError, 'SYMLINK'):
            fingerprint(directory / 'missing')

    def test_corrupt_profile_unknown_fields_and_duplicate_json_refused(self):
        profile = self.root / AREA / 'hosts.json'
        write_state(profile, {'schema': SCHEMA, 'hosts': [], 'command':'untrusted'})
        with self.assertRaisesRegex(MaintenanceError, 'INVALID_HOST_PROFILE'):
            adapters.bindings(self.root)
        profile.write_text('{"schema":"one","schema":"two"}')
        with self.assertRaisesRegex(MaintenanceError, 'DUPLICATE'):
            adapters.bindings(self.root)

    def test_no_association_does_not_find_old_workspaces(self):
        self.start()
        with self.assertRaises(MaintenanceError):
            operations.make_preview(self.root, 'other-exact-session', 'update', [])
        self.assertEqual('original', (self.root / 'owned.txt').read_text())

    def test_json_argument_works_before_and_after_command(self):
        fake = {'source': {'revision':'a'*40, 'clean':True}, 'runtime': {'repair':{}, 'catalog':{}},
                'installations':[], 'context':'host-owned'}
        with patch.object(cli.inspection, 'status', return_value=fake):
            for args in (['--json', 'status'], ['status', '--json']):
                code, output = self.invoke(args)
                self.assertEqual(0, code)
                self.assertEqual(SCHEMA, json.loads(output)['schema'])
        self.assertFalse((self.root / AREA).exists())

    def test_invalid_arguments_return_machine_error(self):
        code, output = self.invoke(['--json', 'unknown'])
        self.assertEqual(2, code)
        self.assertEqual('error', json.loads(output)['status'])

    def test_approval_cannot_substitute_targets(self):
        code, output = self.invoke(['refresh', '--json', '--approve', 'a'*64, '--host', 'claude',
                                    '--approval-ref', 'fixture'])
        self.assertEqual(2, code)
        self.assertIn('APPROVAL_CANNOT_CHANGE', json.loads(output)['reason'])

    def test_candidate_cannot_deploy_or_install_globally(self):
        self.start()
        with self.assertRaisesRegex(MaintenanceError, 'CANDIDATE'):
            workspace.repair(self.candidate, 'nested', True)
        with self.assertRaisesRegex(MaintenanceError, 'CANDIDATE'):
            adapters.preview(self.candidate, self.binding)
        code, output = self.invoke(['repair', 'on', '--root', str(self.root), '--json'],
                                    implementation=self.candidate)
        self.assertEqual(2, code)
        self.assertIn('CANDIDATE', json.loads(output)['reason'])

    def test_checks_follow_known_containment(self):
        self.start()
        out = checks.check(self.root, self.session, ['owned.txt'])
        self.assertEqual(str(self.candidate), out['working_root'])
        self.assertEqual('PASS', out['status'])

    def test_saved_preview_kind_and_corruption_refused(self):
        reviewed = operations.make_preview(self.root, None, 'refresh', [self.binding])
        with self.assertRaisesRegex(MaintenanceError, 'INVALID'):
            self.apply(reviewed, 'update')
        path = self.root / AREA / 'previews' / (reviewed['preview_id'] + '.json')
        value = read_state(path); value['root'] = '/arbitrary'; write_state(path, value)
        with self.assertRaisesRegex(MaintenanceError, 'INVALID'):
            self.apply(reviewed, 'refresh')

    def test_stale_source_is_reported_by_adapter_check(self):
        self.apply(operations.make_preview(self.root, None, 'refresh', [self.binding]), 'refresh')
        (self.root / 'orchestrator/runtime/skills-orchestrator/SKILL.md').write_text('new source')
        self.assertEqual('stale', adapters.check(self.root, self.binding)['status'])

    def test_real_executable_from_another_working_directory(self):
        result = subprocess.run([str(self.root / 'orchestrator/tools/skills_ai'), '--help'], cwd=self.root.parent,
                                capture_output=True, text=True)
        self.assertEqual(0, result.returncode)
        self.assertIn('repair', result.stdout)


if __name__ == '__main__':
    unittest.main()
