#!/usr/bin/env python3
"""Parent integration of the optimizer package: manual route and declared aliases.

The package's own wording, workflow and helper tests live in its repository.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "orchestrator" / "tools"))

from registry_runtime import build_manifest  # noqa: E402


class OptimizerSkillTests(unittest.TestCase):
    def test_package_is_manual_and_its_three_aliases_are_declared(self) -> None:
        manifest = build_manifest(ROOT)
        route = next(item for item in manifest["routes"] if item["id"] == "optimizer")
        self.assertEqual("manual", route["state"])
        self.assertEqual("skills/optimizer/SKILL.md", route["path"])
        self.assertEqual(
            [
                ("#> build-system", "build-system"),
                ("#> optimize", "optimize"),
                ("#> optimizer", "route"),
            ],
            sorted(
                (item["command"], item["mode"])
                for item in manifest["command_aliases"]
                if item["skill_id"] == "optimizer"
            ),
        )


if __name__ == "__main__":
    unittest.main()
