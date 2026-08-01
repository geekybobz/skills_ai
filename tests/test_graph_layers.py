#!/usr/bin/env python3

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from graph_layers import (  # noqa: E402
    check_graph,
    classify_path,
    graph_link_errors,
    interaction_link_errors,
    sync_graph,
    wikilink_errors,
)


class GraphLayerTests(unittest.TestCase):
    def test_governance_and_support_paths_have_expected_layers(self) -> None:
        cases = {
            "docs/06_CHANGE_CONTROL.md": "L1",
            "registry/design.md": "L2",
            "design-with-claude/poster-lead.md": "L4",
            "interaction-protocol/README.md": "L4",
            "protocols/repository/ADD.md": "L5",
            "docs/07_BUILD_AND_RELEASE.md": "L5",
            "runtime/PROTOCOL.md": "L5",
        }
        for path, expected in cases.items():
            with self.subTest(path=path):
                self.assertEqual(expected, classify_path(path))

    def test_live_graph_groups_and_markdown_coverage_are_current(self) -> None:
        self.assertEqual([], check_graph(ROOT))

    def test_interaction_protocol_graph_is_connected(self) -> None:
        self.assertEqual([], interaction_link_errors(ROOT))

    def test_all_declared_graph_concepts_are_connected(self) -> None:
        self.assertEqual([], graph_link_errors(ROOT))

    def test_broken_wikilink_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "source.md").write_text("# Source\n\n[[missing-target]]\n", encoding="utf-8")
            self.assertTrue(any("missing-target" in error for error in wikilink_errors(root)))

    def test_sync_preserves_unrelated_graph_preferences(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            graph_path = root / ".obsidian" / "graph.json"
            graph_path.parent.mkdir(parents=True)
            graph_path.write_text(
                json.dumps(
                    {
                        "showOrphans": False,
                        "scale": 0.75,
                        "colorGroups": [],
                    }
                ),
                encoding="utf-8",
            )
            (root / "README.md").write_text("# Entry\n", encoding="utf-8")
            sync_graph(root)
            updated = json.loads(graph_path.read_text(encoding="utf-8"))
            self.assertFalse(updated["showOrphans"])
            self.assertEqual(0.75, updated["scale"])
            self.assertTrue(updated["colorGroups"])
            self.assertEqual([], check_graph(root, check_policy=False))

    def test_unclassified_markdown_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            graph_path = root / ".obsidian" / "graph.json"
            graph_path.parent.mkdir(parents=True)
            graph_path.write_text(json.dumps({"colorGroups": []}), encoding="utf-8")
            (root / "unclassified.md").write_text("# Missing layer\n", encoding="utf-8")
            sync_graph(root)
            errors = check_graph(root, check_policy=False)
            self.assertTrue(any("unclassified Markdown" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
