#!/usr/bin/env python3

from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "research-context-scout"
sys.path.insert(0, str(ROOT / "scripts"))

from registry_runtime import build_manifest  # noqa: E402


class ResearchContextScoutTests(unittest.TestCase):
    def read(self, relative: str) -> str:
        return (PACKAGE / relative).read_text(encoding="utf-8")

    def test_package_entry_is_manual_and_alias_modes_are_declared(self) -> None:
        manifest = build_manifest(ROOT)
        route = next(item for item in manifest["routes"] if item["id"] == "research-context-scout")
        self.assertEqual("manual", route["state"])
        self.assertEqual("research-context-scout/SKILL.md", route["path"])
        self.assertEqual(
            [
                ("/scout", "initial"),
                ("/scout-again", "deepen"),
            ],
            [(item["command"], item["mode"]) for item in manifest["command_aliases"]],
        )

    def test_runtime_entry_excludes_the_long_human_guide(self) -> None:
        entry = self.read("SKILL.md")
        self.assertIn("Do not read `README.md` during task", entry)
        self.assertIn("shared/SKILL.md", entry)
        self.assertIn("codex/SKILL.md", entry)
        self.assertIn("claude/CLAUDE.md", entry)

    def test_initial_phase_questions_and_pauses_before_deep_research(self) -> None:
        phase = self.read("shared/phases/initial-scout.md")
        self.assertLess(phase.index("## Cycle A"), phase.index("## Cycle B"))
        self.assertIn("Ask one to three questions", phase)
        self.assertIn("tell the user where to", self.read("shared/SKILL.md"))
        self.assertIn("stop", phase.lower())
        self.assertIn("Do not conduct the deep", phase)

    def test_record_template_protects_user_answers(self) -> None:
        template = self.read("shared/templates/research-orientation.md")
        self.assertEqual(1, template.count("USER RESPONSES START"))
        self.assertEqual(1, template.count("USER RESPONSES END"))
        self.assertIn("### Agent interpretation", template)
        self.assertIn("never overwrite", self.read("codex/CODEX.md").lower())

    def test_recommendations_have_formal_evidence_and_application_contracts(self) -> None:
        rule = self.read("shared/rules/evidence-gate.md")
        self.assertIn("\\mathcal D=(C,M,A,E,T,F,U,P)", rule)
        self.assertIn("\\mathcal A=", rule)
        self.assertIn("\\mathcal P=(Q,C,N,E,G,A,F)", rule)
        for level in ("E0", "E1", "E2", "E3", "E4"):
            self.assertIn(level, rule)
        self.assertIn("Mathematical claim", rule)
        self.assertIn("Numerical claim", rule)
        self.assertIn("Physical claim", rule)

    def test_deepen_phase_is_delta_based(self) -> None:
        phase = self.read("shared/phases/deepen-scout.md")
        self.assertIn("S_{k+1}=\\operatorname{revise}(S_k,\\Delta_k)", phase)
        self.assertIn("Do not rerun the complete initial scan", phase)
        self.assertIn("counterevidence", phase)

    def test_runtime_files_remain_bounded(self) -> None:
        limits = {
            "SKILL.md": 5000,
            "shared/SKILL.md": 7000,
            "shared/phases/initial-scout.md": 8000,
            "shared/phases/deepen-scout.md": 8000,
            "shared/rules/evidence-gate.md": 8000,
            "codex/SKILL.md": 4000,
            "codex/CODEX.md": 4000,
            "claude/CLAUDE.md": 4000,
        }
        for relative, limit in limits.items():
            with self.subTest(relative=relative):
                self.assertLess((PACKAGE / relative).stat().st_size, limit)

    def test_human_guide_links_to_live_skill_files_and_hub(self) -> None:
        guide = self.read("README.md")
        required = (
            "docs/00_SKILLS_HUB",
            "research-context-scout/SKILL",
            "research-context-scout/shared/SKILL",
            "research-context-scout/codex/SKILL",
            "research-context-scout/claude/CLAUDE",
        )
        for target in required:
            self.assertIn(target, guide)


if __name__ == "__main__":
    unittest.main()
