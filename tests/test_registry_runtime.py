#!/usr/bin/env python3

from __future__ import annotations

import json
import copy
import os
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from registry_runtime import (  # noqa: E402
    REGISTRY_VIEW_MAX_BYTES,
    RegistryRuntimeError,
    build_manifest,
    load_manifest,
    registry_summary,
)
from install_runtime_adapter import check_adapter, install_adapter  # noqa: E402
from compile_registry import atomic_write as atomic_write_manifest  # noqa: E402
from toggle_registry import toggle  # noqa: E402


class RegistryRuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = load_manifest()

    def test_compiled_manifest_matches_sources(self) -> None:
        self.assertEqual(build_manifest(), self.manifest)




    def test_registry_views_have_hard_serialized_size_budgets(self) -> None:
        for view, maximum in REGISTRY_VIEW_MAX_BYTES.items():
            with self.subTest(view=view):
                summary = registry_summary(self.manifest, view=view)
                encoded = json.dumps(
                    summary,
                    sort_keys=True,
                    separators=(",", ":"),
                ).encode()
                self.assertLessEqual(len(encoded), maximum)

        oversized = copy.deepcopy(self.manifest)
        for index in range(500):
            oversized["packages"][f"oversized-skill-{index:04d}"] = {
                "state": "active",
                "role": "task",
                "path": "unused",
                "boundary": "bounded failure fixture",
            }
        with self.assertRaisesRegex(RegistryRuntimeError, "inventory view exceeds"):
            registry_summary(oversized, view="inventory")

    def test_manifest_separates_six_skills_from_one_orchestrator(self) -> None:
        self.assertEqual(
            {
                "interaction-protocol",
                "markdown-protocol",
                "theory-reference",
                "research-context-scout",
                "optimizer",
                "quantum-job-collector",
            },
            set(self.manifest["packages"]),
        )
        self.assertEqual("skills-orchestrator", self.manifest["orchestrator"]["id"])
        self.assertEqual("model-led", self.manifest["orchestrator"]["mode"])
        self.assertTrue(all(route.get("package") for route in self.manifest["routes"]))























































    def test_toggle_dry_run_does_not_write(self) -> None:
        source = ROOT / "registry" / "activation.md"
        with tempfile.TemporaryDirectory() as directory:
            register = Path(directory) / "activation.md"
            register.write_bytes(source.read_bytes())
            before = register.read_bytes()
            changed = toggle(register, "interaction.math", "manual", write=False)
            self.assertTrue(changed)
            self.assertEqual(before, register.read_bytes())

    def test_codex_adapter_installer_is_atomic_and_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            config_dir = Path(directory)
            dry_run = install_adapter("codex", config_dir, dry_run=True)
            self.assertEqual("would-update", dry_run["entry"])
            self.assertFalse((config_dir / "skills").exists())
            self.assertEqual("updated", install_adapter("codex", config_dir)["entry"])
            self.assertTrue(check_adapter("codex", config_dir))
            self.assertEqual("unchanged", install_adapter("codex", config_dir)["entry"])

    def test_claude_adapter_installs_without_replacing_foreign_settings(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            config_dir = Path(directory)
            settings = {"model": "custom", "hooks": {"SessionStart": [{"hooks": []}]}}
            (config_dir / "settings.json").write_text(json.dumps(settings), encoding="utf-8")
            results = install_adapter("claude", config_dir)
            self.assertEqual("updated", results["hook"])
            self.assertEqual("updated", results["settings"])
            installed = json.loads((config_dir / "settings.json").read_text(encoding="utf-8"))
            self.assertEqual("custom", installed["model"])
            self.assertTrue(installed["hooks"]["SessionStart"])
            self.assertTrue(check_adapter("claude", config_dir))
            self.assertTrue((config_dir / "settings.json.skills-ai.bak").exists())

    def test_claude_adapter_preserves_foreign_hook_and_settings(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            config_dir = Path(directory)
            hook = config_dir / "hooks" / "skills-ai-context.js"
            hook.parent.mkdir(parents=True)
            hook.write_text("// user-owned hook\n", encoding="utf-8")
            settings = config_dir / "settings.json"
            original_settings = b'{"model":"custom"}\n'
            settings.write_bytes(original_settings)
            results = install_adapter("claude", config_dir)
            self.assertEqual("preserved-foreign", results["hook"])
            self.assertEqual("preserved", results["settings"])
            self.assertEqual("// user-owned hook\n", hook.read_text(encoding="utf-8"))
            self.assertEqual(original_settings, settings.read_bytes())
            self.assertFalse((config_dir / "settings.json.skills-ai.bak").exists())

    def test_claude_settings_backups_preserve_first_and_latest_states(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            config_dir = Path(directory)
            settings = config_dir / "settings.json"
            original = b'{"model":"first"}\n'
            settings.write_bytes(original)
            install_adapter("claude", config_dir)
            first_backup = config_dir / "settings.json.skills-ai.bak"
            self.assertEqual(original, first_backup.read_bytes())
            changed = json.loads(settings.read_text(encoding="utf-8"))
            changed["manual_after_install"] = True
            changed_bytes = (json.dumps(changed) + "\n").encode()
            settings.write_bytes(changed_bytes)
            install_adapter("claude", config_dir)
            self.assertEqual(original, first_backup.read_bytes())
            self.assertEqual(
                changed_bytes,
                (config_dir / "settings.json.skills-ai.previous").read_bytes(),
            )

    @unittest.skipIf(os.name == "nt", "POSIX mode bits are not portable")
    def test_compiled_manifest_write_is_world_readable(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "manifest.json"
            atomic_write_manifest(target, "{}\n")
            self.assertEqual(0o644, stat.S_IMODE(target.stat().st_mode))








if __name__ == "__main__":
    unittest.main()


class ContextInstallerTests(unittest.TestCase):
    def test_lifecycle_hooks_preserve_foreign_entries_and_are_idempotent(self):
        from install_runtime_adapter import merged_claude_settings, claude_hook_command
        hook=Path('/synthetic/hooks/skills-ai-context.js')
        owned={'type':'command','command':claude_hook_command(hook)}
        foreign={'type':'command','command':'echo unrelated-skills-ai-context.js'}
        settings={'other':True,'hooks':{'UserPromptSubmit':[{'hooks':[owned,foreign]}]}}
        first=merged_claude_settings(settings,hook)
        self.assertTrue(first['other']);self.assertIn(foreign,first['hooks']['UserPromptSubmit'][0]['hooks'])
        self.assertEqual(first,merged_claude_settings(json.loads(json.dumps(first)),hook))
        for event in ('SessionStart','UserPromptSubmit'):
            self.assertEqual(1,sum(h['command']==owned['command'] for e in first['hooks'][event] for h in e['hooks']))

class ClaudeAdapterHygieneTests(unittest.TestCase):
    """Claude-owned install hygiene: native skills must not shadow Skills AI packages."""

    def test_native_skill_named_like_a_package_makes_check_stale(self) -> None:
        from install_runtime_adapter import claude_check_problems, registry_packages
        self.assertIn("theory-reference", registry_packages())
        with tempfile.TemporaryDirectory() as directory:
            config_dir = Path(directory)
            install_adapter("claude", config_dir)
            self.assertTrue(check_adapter("claude", config_dir))
            shadow = config_dir / "skills" / "theory-reference"
            shadow.mkdir(parents=True)
            (shadow / "SKILL.md").write_text("---\nname: theory-reference\n---\n", encoding="utf-8")
            self.assertFalse(check_adapter("claude", config_dir))
            self.assertEqual("theory-reference", install_adapter("claude", config_dir)["native_shadow_skills"])
            self.assertTrue(any("theory-reference" in problem for problem in claude_check_problems(config_dir)))
            self.assertTrue(shadow.exists())  # user content is reported, never removed by the installer
            (config_dir / "skills" / "unrelated-skill").mkdir()
            (shadow / "SKILL.md").unlink(); shadow.rmdir()
            self.assertTrue(check_adapter("claude", config_dir))
            synced = config_dir / "skills" / "synced" / "account-bucket" / "research-context-scout"
            synced.mkdir(parents=True)
            self.assertFalse(check_adapter("claude", config_dir))
            synced.rmdir()
            self.assertTrue(check_adapter("claude", config_dir))
