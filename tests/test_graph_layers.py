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
    _markdown_paths,
    check_graph,
    classify_path,
    graph_inventory_errors,
    graph_link_errors,
    graph_role_errors,
    interaction_link_errors,
    sync_graph,
    wikilink_errors,
)


class GraphLayerTests(unittest.TestCase):
    def test_governance_and_support_paths_have_expected_layers(self) -> None:
        cases = {
            "docs/06_CHANGE_CONTROL.md": "L1",
            "registry/activation.md": "L1",
            "graph/orchestration/skills-orchestrator.md": "L1",
            "interaction-protocol/README.md": "L1",
            "docs/SHARED_DOCUMENTATION_MODEL.md": "L1",
            "registry/theory.md": "L2",
            "theory-reference/SKILL.md": "L4",
            "optimizer/SKILL.md": "L4",
            "research-context-scout/SKILL.md": "L4",
            "graph/skills/theory-reference.md": "L4",
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

    def test_declared_graph_roles_are_layered_by_node_type(self) -> None:
        self.assertEqual([], graph_role_errors(ROOT))

    def test_orchestrator_and_skill_inventory_nodes_are_visible_and_descriptive(self) -> None:
        self.assertEqual([], graph_inventory_errors(ROOT))

    def test_generic_or_hidden_inventory_nodes_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            contract_path = root / "protocols" / "repository" / "CONTRACT.json"
            model_path = root / "protocols" / "repository" / "DOCUMENTATION.json"
            graph_path = root / ".obsidian" / "graph.json"
            node_path = root / "graph" / "orchestration" / "SKILL.md"
            for path in (contract_path, model_path, graph_path, node_path):
                path.parent.mkdir(parents=True, exist_ok=True)
            contract_path.write_text(
                json.dumps(
                    {
                        "version": 1,
                        "roles": [{"id": "fixture", "patterns": ["**"]}],
                        "graph_inventory_policy": {
                            "orchestrator_layer": "L1",
                            "skill_layer": "L4",
                            "reserved_entry_names": ["SKILL.md", "README.md"],
                            "require_default_visibility": True,
                        },
                    }
                ),
                encoding="utf-8",
            )
            model_path.write_text(
                json.dumps(
                    {
                        "orchestrator": {
                            "id": "skills-orchestrator",
                            "display_name": "Skills Orchestrator",
                            "graph_entry": "graph/orchestration/SKILL.md",
                        },
                        "packages": [],
                    }
                ),
                encoding="utf-8",
            )
            graph_path.write_text(
                json.dumps({"search": "-path:graph/orchestration/"}),
                encoding="utf-8",
            )
            node_path.write_text(
                "# Skills Orchestrator\n\ngraph_kind: orchestrator\n\n[[registry/activation]]\n",
                encoding="utf-8",
            )
            errors = graph_inventory_errors(root)
        self.assertTrue(any("generic graph inventory filename" in error for error in errors))
        self.assertTrue(any("hidden by the default filter" in error for error in errors))

    def test_future_declared_hub_cannot_inherit_support_layer(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            contract_path = root / "protocols" / "repository" / "CONTRACT.json"
            contract_path.parent.mkdir(parents=True)
            contract_path.write_text(
                json.dumps(
                    {
                        "version": 1,
                        "roles": [{"id": "fixture", "patterns": ["**"]}],
                        "graph_role_policy": {
                            "graph_contract_entry_layer": "L1",
                            "required_paths": {},
                        },
                        "graph_contracts": [{"id": "future", "entry": "runtime/PROTOCOL.md"}],
                    }
                ),
                encoding="utf-8",
            )
            errors = graph_role_errors(root)
        self.assertTrue(any("graph hub has wrong layer" in error for error in errors))

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
                        "search": "-path:tests/",
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
            self.assertEqual("-path:tests/", updated["search"])
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

    def test_plan_only_ideas_are_not_graph_nodes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            plan = root / "skill-plans" / "future-scout" / "plan.md"
            plan.parent.mkdir(parents=True)
            plan.write_text("# Future scout\n", encoding="utf-8")
            self.assertEqual([], list(_markdown_paths(root)))


if __name__ == "__main__":
    unittest.main()
