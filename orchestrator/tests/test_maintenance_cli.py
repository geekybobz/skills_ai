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
from unittest.mock import ANY, patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "orchestrator" / "runtime"))
from maintenance import adapters, checks, cli, lifecycle, operations, updater, workflow, workspace
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
        return operations.make_preview(self.root, self.session, 'repair-apply', list(hosts), 'fixture-scope')

    def apply(self, preview, kind='repair-apply'):
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
        code, output = self.invoke(['repair', 'apply', '--json', '--session', self.session])
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
            code = cli.main(['repair', 'apply', '--session', self.session, '--host', 'codex',
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
                     'orchestrator/runtime/maintenance/lifecycle.py',
                     'orchestrator/runtime/maintenance/updater.py',
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
            operations.make_preview(self.root, 'other-exact-session', 'repair-apply', [])
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

    def test_help_lists_small_everyday_and_advanced_command_sets(self):
        overview = {
            'schema':'skills-ai/help-overview/1', 'status':'current', 'authority':'none',
            'skills':[{'id':'project-manager', 'state':'active', 'role':'supporting',
                       'purpose':'Portable project memory.'}],
            'limits':'Help is read-only metadata and does not select or load a skill.',
        }
        with patch.object(cli.inspection, 'help_overview', return_value=overview) as helped:
            code, output = self.invoke(['help'])
        self.assertEqual(0, code)
        helped.assert_called_once_with(self.root)
        for name in ('status', 'help', 'check', 'work NAME', 'finish NAME',
                     'update [NAME]', 'skills [NAME]', 'doctor'):
            self.assertIn(name, output)
        self.assertIn('repair on/off/apply', output)
        self.assertIn('project-manager [active/supporting]', output)
        self.assertIn('#> <skill-name> help', output)
        self.assertIn('does not select or load', output)

    def test_skill_help_renders_without_loading_or_selecting_package(self):
        card = {
            'schema':'skills-ai/skill-help/1', 'authority':'none',
            'skill':{'id':'project-manager', 'state':'active', 'role':'supporting',
                     'purpose':'Portable project memory.', 'available':True},
            'use_when':['project work'], 'not_for':['action approval'],
            'chat':[{'syntax':'#> memory init', 'does':'Preview initialization.',
                     'boundary':'No write without approval.'}],
            'terminal':[{'syntax':'project-manager check .', 'does':'Validate memory.',
                         'boundary':'Read-only.'}],
            'keywords':[], 'entries':['skills/project-manager/SKILL.md'],
            'limits':'Help is read-only metadata and does not select or load the skill.',
        }
        with patch.object(cli.inspection, 'help_metadata', return_value=card) as helped:
            code, output = self.invoke(['skills', 'project-manager', 'help'])
        self.assertEqual(0, code)
        helped.assert_called_once_with(self.root, 'project-manager')
        self.assertIn('Skill help — project-manager', output)
        self.assertIn('#> memory init', output)
        self.assertIn('project-manager check .', output)
        self.assertIn('does not select or load', output)

    def test_doctor_forwards_full_diagnosis(self):
        fake = {'status':'current', 'verification':{'passed':11, 'failed':0},
                'current':{'status':'current', 'next':'No pending declared status action.'},
                'limits':'bounded fixture'}
        with patch.object(cli.inspection, 'doctor', return_value=fake) as diagnosed:
            code, output = self.invoke(['doctor'])
        self.assertEqual(0, code)
        diagnosed.assert_called_once_with(self.root, ANY, adapters, [])
        self.assertIn('Verification: 11 passed, 0 failed', output)

    def test_update_previews_global_sync_without_applying(self):
        fake = {'status':'awaiting-approval', 'preview_id':'a'*64,
                'sources':{'parent':{'relation':'current'}, 'children':[]},
                'commands':[], 'installations':[], 'next':'Review this exact update.'}
        with patch.object(cli.updater, 'preview', return_value=fake) as previewed, \
             patch.object(cli.updater, 'apply') as applied:
            code, output = self.invoke(['update', '--json'])
        self.assertEqual(3, code)
        previewed.assert_called_once_with(self.root, package=None, approval_ref='terminal-request')
        applied.assert_not_called()
        self.assertEqual('awaiting-approval', json.loads(output)['result']['status'])

    def test_update_approval_forwards_exact_preview_and_agreement(self):
        fake = {'status':'complete', 'operation_id':'op', 'commands':[], 'hosts':[],
                'next':'complete'}
        with patch.object(cli.updater, 'apply', return_value=fake) as applied:
            code, _ = self.invoke(['update', '--approve', 'a'*64,
                                   '--approval-ref', 'fixture-agreement'])
        self.assertEqual(0, code)
        applied.assert_called_once_with(self.root, 'a'*64, 'fixture-agreement', package=None)

    def test_package_scoped_update_forwards_target_and_prints_copyable_approval(self):
        approval = 'skills_ai update project-manager'
        fake = {'status':'awaiting-approval', 'preview_id':'b'*64, 'package':'project-manager',
                'sources':{'parent':{'relation':'current'}, 'children':[],
                           'preserved_parent_changes':True},
                'verification':{'passed':11, 'failed':0}, 'commands':[], 'installations':[],
                'approval_command':approval, 'approval_reply':'approve project-manager update',
                'next':'Review this exact update.'}
        with patch.object(cli.updater, 'preview', return_value=fake) as previewed:
            code, output = self.invoke(['update', 'project-manager'])
        self.assertEqual(3, code)
        previewed.assert_called_once_with(
            self.root, package='project-manager', approval_ref='terminal-request')
        self.assertIn('Update report — project-manager: awaiting-approval', output)
        self.assertIn('Checks: 11 passed, 0 failed', output)
        self.assertIn('Preserved unrelated parent changes.', output)
        self.assertIn('Approve with:\n  ' + approval, output)
        self.assertIn('Or reply in chat: approve project-manager update', output)
        self.assertNotIn('Preview:', output)

    def test_work_and_finish_render_compact_task_reports(self):
        work_result = {'status':'ready', 'working_root':'/tmp/work', 'package':'project-manager',
                       'report':{'package':'project-manager', 'outcome':'Work area ready',
                                 'detail':'contained', 'checks':None, 'changed_paths':[],
                                 'next_command':'cd /tmp/work/skills/project-manager'}}
        finish_result = {'status':'awaiting-approval', 'package':'project-manager',
                         'preview_id':'c'*64,
                         'report':{'package':'project-manager', 'outcome':'Ready for approval',
                                   'detail':'2 changed paths passed.', 'checks':'PASS',
                                   'changed_paths':['one','two'],
                                   'next_command':'skills_ai finish project-manager'}}
        finish_result['approval_reply'] = 'approve project-manager finish'
        with patch.object(cli.workflow, 'work', return_value=work_result) as started:
            code, output = self.invoke(['work', 'project-manager'])
        self.assertEqual(0, code)
        started.assert_called_once_with(self.root, ANY, 'project-manager')
        self.assertIn('Work area ready — project-manager', output)
        self.assertIn('Next command:', output)
        with patch.object(cli.workflow, 'finish_preview', return_value=finish_result) as finished:
            code, output = self.invoke(['finish', 'project-manager', '--preview'])
        self.assertEqual(3, code)
        finished.assert_called_once_with(self.root, ANY, 'project-manager', 'terminal-request')
        self.assertIn('Ready for approval — project-manager', output)
        self.assertIn('Changed paths: 2', output)
        self.assertIn('Approve with:', output)

    def test_package_scoped_source_plan_preserves_unrelated_parent_changes(self):
        parent = {'head':'a'*40, 'origin_main':'a'*40, 'ahead':0, 'behind':0,
                  'relation':'current', 'clean':False}
        manifest = {'distributions':{'project-manager':{
            'repository':{'kind':'submodule', 'path':'skills/project-manager'}}}}
        with patch.object(updater, '_relation', return_value=parent), \
             patch.object(updater, '_submodules', return_value=[]), \
             patch.object(updater, '_path_dirty', return_value=False):
            result = updater._source_plan(
                self.root, package='project-manager', manifest=manifest)
        self.assertEqual([], result['blocked'])
        self.assertTrue(result['preserved_parent_changes'])

    def test_package_scoped_source_plan_blocks_selected_pointer_drift(self):
        parent = {'head':'a'*40, 'origin_main':'a'*40, 'ahead':0, 'behind':0,
                  'relation':'current', 'clean':False}
        manifest = {'distributions':{'project-manager':{
            'repository':{'kind':'submodule', 'path':'skills/project-manager'}}}}
        with patch.object(updater, '_relation', return_value=parent), \
             patch.object(updater, '_submodules', return_value=[]), \
             patch.object(updater, '_path_dirty', return_value=True):
            result = updater._source_plan(
                self.root, package='project-manager', manifest=manifest)
        self.assertIn('SELECTED_PACKAGE_POINTER_DIRTY: skills/project-manager', result['blocked'])

    def test_finish_report_supplies_exact_approval_and_followup_commands(self):
        checked = {'status':'PASS'}
        reviewed = {'status':'awaiting-approval', 'preview_id':'d'*64,
                    'repair':{'paths':['skills/example/SKILL.md']}, 'next':'review'}
        with patch.object(workflow, '_package', return_value=({}, Path('skills/example'), True)), \
             patch.object(workflow.checks, 'check', return_value=checked), \
             patch.object(workflow.operations, 'make_preview', return_value=reviewed):
            result = workflow.finish_preview(self.root, self.session, 'example')
        self.assertEqual('Ready for approval', result['report']['outcome'])
        self.assertEqual('skills_ai finish example', result['report']['next_command'])
        self.assertEqual('approve example finish', result['approval_reply'])
        self.assertEqual(
            'skills_ai finish example --approve ' + 'd'*64 + ' --approval-ref approved',
            result['exact_approval_command'])
        applied = {'status':'complete', 'next':'done'}
        with patch.object(workflow, '_package', return_value=({}, Path('skills/example'), True)), \
             patch.object(workflow.operations, 'apply_preview', return_value=applied):
            result = workflow.finish_apply(self.root, 'example', 'd'*64, 'approved')
        self.assertEqual('skills_ai update example', result['report']['next_command'])

    def test_refresh_human_report_hides_digest_and_suggests_normal_command(self):
        result = {'status':'awaiting-approval', 'preview_id':'e'*64,
                  'installations':[{'binding':{'host':'codex', 'config_dir':'/tmp/codex'},
                                    'before':[], 'changes':{}}],
                  'next':'Review actual targets.'}
        output = cli.render(cli.envelope('refresh', result))
        self.assertIn('Approve with:\n  skills_ai refresh --host codex', output)
        self.assertIn('Or reply in chat: approve codex refresh', output)
        self.assertNotIn('e'*64, output)

    def test_global_update_preview_suppresses_installation_when_source_blocked(self):
        sources = {'parent':{'relation':'current'}, 'children':[], 'actions':[],
                   'blocked':['PARENT_DIRTY']}
        with patch.object(updater, '_manifest', return_value={'distributions':{}}), \
             patch.object(updater, '_source_plan', return_value=sources), \
             patch.object(updater, '_verification', return_value={'passed':1, 'failed':0}), \
             patch.object(updater.lifecycle, 'inspect', return_value={'items':[]}), \
             patch.object(updater, '_command_plans') as commands, \
             patch.object(updater.adapters, 'bindings', return_value=[]):
            result = updater.preview(self.root, approval_ref='fixture')
        self.assertEqual('blocked', result['status'])
        self.assertEqual([], result['commands'])
        commands.assert_not_called()
        self.assertTrue((self.root / AREA / 'previews' / (result['preview_id'] + '.json')).is_file())

    def test_global_update_apply_requires_exact_actual_approval(self):
        with self.assertRaisesRegex(MaintenanceError, 'EXACT_PREVIEW'):
            updater.apply(self.root, 'a'*64, None)

    def test_global_update_binds_exact_installer_bytes(self):
        installer = self.root / 'installer'
        installer.write_bytes(b'first')
        before = updater._executable_identity(installer)
        installer.write_bytes(b'second')
        self.assertNotEqual(before, updater._executable_identity(installer))

    def test_status_renders_versions_global_commands_and_first_action(self):
        fake = {
            'status':'partial', 'source':{'revision':'a'*40, 'clean':False},
            'runtime':{'repair':{}, 'catalog':{}}, 'candidate_of':None,
            'packages':{'total':2, 'counts':{'active':1, 'manual':1, 'off':0}, 'items':[
                {'package':'alpha', 'state':'active', 'status':'versioned', 'version':'1.2.3'},
                {'package':'beta', 'state':'manual', 'status':'unversioned', 'version':None},
            ]},
            'lifecycle':{'items':[{'commands':[{'name':'alpha', 'status':'stale',
                                                'installed_version':'1.2.2'}]}]},
            'installations':[{'host':'codex', 'status':'stale', 'config_dir':'/tmp/codex'}],
            'next':'Review one coherent commit.', 'context':'host-owned',
        }
        with patch.object(cli.inspection, 'status', return_value=fake):
            code, output = self.invoke(['status'])
        self.assertEqual(2, code)
        self.assertIn('Skills: 2 — active 1, manual 1, off 0', output)
        self.assertIn('alpha 1.2.3 [active]', output)
        self.assertIn('beta unversioned [manual]', output)
        self.assertIn('Global commands: alpha 1.2.2 stale', output)
        self.assertIn('Next: Review one coherent commit.', output)

    def test_package_versions_detects_versioned_unversioned_and_ambiguous(self):
        for package in ('alpha', 'beta', 'gamma'):
            folder = self.root / 'skills' / package
            folder.mkdir(parents=True)
            (folder / 'SKILL.md').write_text('# Skill')
        (self.root / 'skills/alpha/VERSION').write_text('1.2.3\n')
        (self.root / 'skills/gamma/VERSION').write_text('2.0.0\n')
        (self.root / 'skills/gamma/pyproject.toml').write_text('[project]\nversion = "2.1.0"\n')
        manifest = {'packages':{
            'alpha':{'state':'active', 'path':'skills/alpha/SKILL.md'},
            'beta':{'state':'manual', 'path':'skills/beta/SKILL.md'},
            'gamma':{'state':'active', 'path':'skills/gamma/SKILL.md'},
        }}
        result = lifecycle.package_versions(self.root, manifest)
        items = {item['package']:item for item in result['items']}
        self.assertEqual(('versioned', '1.2.3'), (items['alpha']['status'], items['alpha']['version']))
        self.assertEqual('unversioned', items['beta']['status'])
        self.assertEqual('ambiguous', items['gamma']['status'])

    def test_lifecycle_command_renders_compact_receipt(self):
        fake_item = {
            'package': 'project-manager', 'status': 'partial', 'globally_current': False,
            'axes': {'source':'current', 'child':'current', 'parent':'current',
                     'release':'current', 'cli':'pending', 'hosts':'not-applicable'},
            'source': {'revision':'a'*40, 'remote_evidence':'local-tracking-ref'},
            'child_pin': 'a'*40, 'commands': [], 'hosts': [],
            'next': ['Review the global project-manager installation before refreshing it.'],
            'limits': 'bounded fixture',
        }
        fake = {'schema':'skills-ai/lifecycle/1', 'status':'partial', 'items':[fake_item],
                'remote_check':'local-only', 'authority':'none'}
        with patch.object(cli.inspection, 'lifecycle_status', return_value=fake):
            code, output = self.invoke(['lifecycle', 'project-manager'])
        self.assertEqual(2, code)
        self.assertIn('Lifecycle project-manager:', output)
        self.assertIn('cli pending', output)
        self.assertIn('Next: Review the global project-manager installation', output)
        self.assertNotIn('bounded fixture', output)

    def test_lifecycle_detail_is_explicit_and_forwarded(self):
        fake = {'schema':'skills-ai/lifecycle/1', 'status':'current', 'items':[],
                'remote_check':'explicit', 'authority':'none'}
        with patch.object(cli.inspection, 'lifecycle_status', return_value=fake) as inspected:
            code, output = self.invoke(['lifecycle', 'project-manager', '--detail', '--check-remotes', '--json'])
        self.assertEqual(0, code)
        inspected.assert_called_once_with(self.root, adapters, 'project-manager', True)
        self.assertTrue(json.loads(output)['result']['detail'])

    def test_lifecycle_state_distinguishes_release_and_installation(self):
        revision = 'a' * 40
        published = {'revision':revision, 'clean':True, 'remote_revision':revision,
                     'published':True, 'remote_evidence':'fresh-remote-check',
                     'remote_error':None, 'remote_tags':['v1.2.3'], 'tags':['v1.2.3']}
        contract = {
            'repository': {'kind':'submodule', 'path':'skills/example'},
            'expected_version':'1.2.3',
            'release': {'kind':'semver-tag', 'required':True},
            'commands': [{'name':'example', 'kind':'python-distribution',
                          'distribution':'example', 'required':True}],
            'host_adapters': [],
        }
        class NoAdapters:
            @staticmethod
            def bindings(root):
                return []
        with patch.object(lifecycle, '_repository', side_effect=[published, published]), \
             patch.object(lifecycle, '_gitlink', return_value=revision), \
             patch.object(lifecycle, '_command', return_value={
                 'name':'example', 'status':'stale', 'required':True}):
            result = lifecycle.inspect_one(self.root, 'example', contract, NoAdapters,
                                           check_remotes=False)
        self.assertEqual('current', result['axes']['release'])
        self.assertEqual('pending', result['axes']['cli'])
        self.assertEqual('partial', result['status'])
        self.assertIn('global example installation', result['next'][-1])

    def test_local_release_tag_is_not_claimed_published_without_remote_check(self):
        repository = {'tags':['v1.2.3'], 'remote_tags':None}
        release = lifecycle._release(repository, {'kind':'semver-tag', 'required':True}, '1.2.3')
        self.assertEqual('unknown', release['status'])

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
            self.apply(reviewed, 'repair-apply')
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
