#!/usr/bin/env python3

from __future__ import annotations

import json
import os
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from registry_runtime import build_manifest, compact_context, load_manifest, route_request  # noqa: E402
from install_runtime_adapter import check_adapter, install_adapter  # noqa: E402
from compile_registry import atomic_write as atomic_write_manifest  # noqa: E402
from toggle_registry import toggle  # noqa: E402


class RegistryRuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = load_manifest()

    def test_compiled_manifest_matches_sources(self) -> None:
        self.assertEqual(build_manifest(), self.manifest)

    def test_ordinary_question_uses_normal_fallback(self) -> None:
        decision = route_request("What is the capital of France?", self.manifest)
        self.assertEqual("NORMAL", decision["result"])
        self.assertEqual("NO_SKILL_MATCH", decision["reason_code"])

    def test_math_loads_only_math_skill(self) -> None:
        decision = route_request("Derive the equation formula first with less story", self.manifest)
        self.assertEqual("MATCH", decision["result"])
        self.assertEqual("caveman-math", decision["skill"]["id"])
        self.assertNotIn("caveman/skills/caveman/SKILL.md", compact_context(decision))

    def test_manual_commit_skill_requires_matching_request(self) -> None:
        matched = route_request("Write a commit message for the staged change", self.manifest)
        unrelated = route_request("Explain why commits are useful", self.manifest)
        self.assertEqual("caveman-commit", matched["skill"]["id"])
        self.assertNotEqual("caveman-commit", unrelated.get("skill", {}).get("id"))

    def test_disabled_skill_falls_back(self) -> None:
        decision = route_request("Run the exhaustive quantum job collector", self.manifest)
        self.assertEqual("NORMAL", decision["result"])
        self.assertEqual("DISABLED_SKILL", decision["reason_code"])

    def test_pdf_reading_does_not_route_to_design(self) -> None:
        decision = route_request("Summarize this PDF document", self.manifest)
        self.assertEqual("NORMAL", decision["result"])

    def test_context_has_polished_response_contract(self) -> None:
        decision = route_request("Explain this code", self.manifest)
        context = decision["context"]
        self.assertEqual("compact-professional", context["output"]["voice"])
        self.assertTrue(context["response_contract"])
        self.assertIn("polished complete sentences", compact_context(decision))

    def test_toggle_dry_run_does_not_write(self) -> None:
        source = ROOT / "registry" / "activation.md"
        with tempfile.TemporaryDirectory() as directory:
            register = Path(directory) / "activation.md"
            register.write_bytes(source.read_bytes())
            before = register.read_bytes()
            changed = toggle(register, "caveman.no-ai-traces", "manual", write=False)
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
            self.assertEqual("absent", results["entry"])
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
            hook = config_dir / "hooks" / "skills-ai-router.js"
            hook.parent.mkdir(parents=True)
            hook.write_text("// user-owned hook\n", encoding="utf-8")
            settings = config_dir / "settings.json"
            original_settings = b'{"model":"custom"}\n'
            settings.write_bytes(original_settings)
            results = install_adapter("claude", config_dir)
            self.assertEqual("preserved-foreign", results["hook"])
            self.assertEqual("not-attempted", results["entry"])
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

    def test_claude_adapter_removes_only_managed_bootstrap(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            config_dir = Path(directory)
            skill_target = config_dir / "skills" / "skills-ai-registry" / "SKILL.md"
            skill_target.parent.mkdir(parents=True)
            skill_target.write_bytes((ROOT / "runtime" / "SKILL.md").read_bytes())
            self.assertEqual("would-remove", install_adapter("claude", config_dir, dry_run=True)["entry"])
            self.assertTrue(skill_target.exists())
            self.assertEqual("removed", install_adapter("claude", config_dir)["entry"])
            self.assertFalse(skill_target.exists())
            self.assertTrue(check_adapter("claude", config_dir))

    def test_claude_adapter_preserves_foreign_bootstrap(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            config_dir = Path(directory)
            skill_target = config_dir / "skills" / "skills-ai-registry" / "SKILL.md"
            skill_target.parent.mkdir(parents=True)
            skill_target.write_text("user-authored\n", encoding="utf-8")
            self.assertEqual("preserved-foreign", install_adapter("claude", config_dir)["entry"])
            self.assertEqual("user-authored\n", skill_target.read_text(encoding="utf-8"))
            self.assertTrue(check_adapter("claude", config_dir))

    def test_claude_hook_uses_shared_router(self) -> None:
        completed = subprocess.run(
            ["node", str(ROOT / "adapters" / "claude" / "skills-ai-router.js"), "--root", str(ROOT)],
            input=json.dumps({"prompt": "Explain this code without jargon"}),
            text=True,
            capture_output=True,
            check=True,
        )
        payload = json.loads(completed.stdout)
        context = payload["hookSpecificOutput"]["additionalContext"]
        self.assertIn("Selected local skill: code-explainer", context)
        self.assertIn("voice=compact-professional", context)

    def test_benchmark_fixture_expectations(self) -> None:
        cases = json.loads((ROOT / "tests" / "router_cases.json").read_text(encoding="utf-8"))
        for case in cases:
            with self.subTest(case=case["name"]):
                decision = route_request(case["query"], self.manifest)
                self.assertEqual(case["result"], decision["result"])
                self.assertEqual(case.get("skill"), decision.get("skill", {}).get("id"))


if __name__ == "__main__":
    unittest.main()
