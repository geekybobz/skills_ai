#!/usr/bin/env python3
"""Parent integration of research-context-scout: route, aliases and registry text.

The package's own wording and structure tests live in its repository.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from registry_runtime import build_manifest  # noqa: E402


class ResearchContextScoutTests(unittest.TestCase):
    def test_package_entry_is_manual_and_alias_modes_are_declared(self) -> None:
        manifest = build_manifest(ROOT)
        route = next(item for item in manifest["routes"] if item["id"] == "research-context-scout")
        self.assertEqual("manual", route["state"])
        self.assertEqual("research-context-scout/SKILL.md", route["path"])
        self.assertEqual(
            [
                ("#> scout", "initial"),
                ("#> scout-again", "deepen"),
            ],
            [
                (item["command"], item["mode"])
                for item in manifest["command_aliases"]
                if item["skill_id"] == "research-context-scout"
            ],
        )

    def test_registry_description_matches_the_current_workflow(self) -> None:
        registry = (ROOT / "registry" / "research.md").read_text(encoding="utf-8")
        for term in (
            "physics objective",
            "user-aligned",
            "extracted-corpus synthesis",
            "project-notation translation",
        ):
            with self.subTest(term=term):
                self.assertIn(term, registry)


if __name__ == "__main__":
    unittest.main()
