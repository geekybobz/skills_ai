#!/usr/bin/env python3

from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from human_docs_guard import (  # noqa: E402
    _mermaid_errors,
    coverage_errors,
    guide_paths,
    load_source_map,
    required_guides,
    validate_human_docs,
)


class HumanDocsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = load_source_map(ROOT)

    def test_live_human_guide_is_consistent(self) -> None:
        self.assertEqual([], validate_human_docs(ROOT))

    def test_runtime_change_maps_to_routing_guide(self) -> None:
        required = required_guides(["runtime/PROTOCOL.md"], self.config)
        self.assertIn("README.md", required)
        self.assertIn("docs/human/00_START_HERE.md", required)
        self.assertIn("docs/human/01_FOLLOW_A_REQUEST.md", required)

    def test_dot_prefixed_graph_path_keeps_its_source_mapping(self) -> None:
        required = required_guides([".obsidian/graph.json"], self.config)
        self.assertIn("docs/human/06_GRAPH_AND_COLORS.md", required)
        self.assertIn("docs/human/07_MAINTAINING_SKILLS.md", required)

    def test_missing_mapped_page_blocks_coverage(self) -> None:
        errors = coverage_errors(["registry/activation.md"], self.config)
        self.assertTrue(any("03_SKILLS_AND_CONTROLS.md" in error for error in errors))

    def test_changed_mapped_page_satisfies_coverage(self) -> None:
        changed = [
            "registry/activation.md",
            "docs/human/03_SKILLS_AND_CONTROLS.md",
            "docs/human/09_SKILL_ANATOMY.md",
            "docs/human/_LIVE_SKILL_CATALOG.md",
        ]
        self.assertEqual([], coverage_errors(changed, self.config))

    def test_every_guide_is_human_marked(self) -> None:
        for relative in guide_paths(self.config):
            with self.subTest(path=relative):
                text = (ROOT / relative).read_text(encoding="utf-8")
                self.assertIn("audience: human", text[:500])
                self.assertIn("authority:", text[:500])

    def test_human_guide_is_not_a_runtime_route(self) -> None:
        manifest = (ROOT / "runtime" / "router-manifest.json").read_text(encoding="utf-8")
        self.assertNotIn("docs/human/", manifest)
        self.assertNotIn('"path": "README.md"', manifest)

    def test_oversized_mermaid_is_rejected(self) -> None:
        nodes = "\n".join(f'N{i}["Node {i}"] --> N{i + 1}["Node {i + 1}"]' for i in range(13))
        text = f"```mermaid\nflowchart LR\n{nodes}\n```\n"
        errors = _mermaid_errors(text, "guide.md", self.config["mermaid_limits"])
        self.assertTrue(any("split it into focused diagrams" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
