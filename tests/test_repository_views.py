from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch
import tempfile


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from compile_repository_views import (  # noqa: E402
    GENERATED_NOTICE,
    _strip_frontmatter,
    _token_estimate,
    load_model,
    render_outputs,
    repository_paths,
    render_agent_entries,
    stale_outputs,
)


class RepositoryViewTests(unittest.TestCase):
    def test_agent_regeneration_replaces_unsupported_external_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "common.md").write_text("Shared rules\n", encoding="utf-8")
            (root / "overlay.md").write_text("Host rules\n", encoding="utf-8")
            block = "<!-- external-tool:start -->\nUnsupported instructions\n<!-- external-tool:end -->"
            (root / "AGENTS.md").write_text("Old generated text\n\n" + block + "\n", encoding="utf-8")
            model = {"agent_entries": {"common": "common.md", "outputs": {"AGENTS.md": "overlay.md"}}}
            output = render_agent_entries(root, model)["AGENTS.md"]
            self.assertNotIn(block, output)
            self.assertNotIn("Old generated text", output)
            (root / "AGENTS.md").write_text(output, encoding="utf-8")
            self.assertEqual(output, render_agent_entries(root, model)["AGENTS.md"])

    def test_expected_outputs_are_generated(self) -> None:
        outputs = render_outputs(ROOT)
        self.assertEqual(
            set(outputs),
            {
                "AGENTS.md",
                "CLAUDE.md",
                "docs/human/_LIVE_REPOSITORY_INDEX.md",
                "docs/human/_LIVE_SKILL_CATALOG.md",
                "graph/orchestration/skills-orchestrator.md",
                "graph/skills/interaction-protocol.md",
                "graph/skills/optimizer.md",
                "graph/skills/quantum-job-collector.md",
                "graph/skills/research-context-scout.md",
                "graph/skills/theory-reference.md",
            },
        )
        self.assertTrue(all(text.endswith("\n") for text in outputs.values()))

    def test_agent_entries_share_one_canonical_body(self) -> None:
        model = load_model(ROOT)
        common = _strip_frontmatter(
            (ROOT / model["agent_entries"]["common"]).read_text(encoding="utf-8")
        )
        outputs = render_outputs(ROOT)
        self.assertIn(common, outputs["AGENTS.md"])
        self.assertIn(common, outputs["CLAUDE.md"])
        self.assertIn("Codex-specific access", outputs["AGENTS.md"])
        self.assertNotIn("Claude-specific access", outputs["AGENTS.md"])
        self.assertIn("Claude-specific access", outputs["CLAUDE.md"])
        self.assertNotIn("Codex-specific access", outputs["CLAUDE.md"])

    def test_human_outputs_are_marked_and_exhaustive(self) -> None:
        model = load_model(ROOT)
        outputs = render_outputs(ROOT)
        repository_index = outputs[model["human_outputs"]["repository_index"]]
        skill_catalog = outputs[model["human_outputs"]["skill_catalog"]]
        for text in (repository_index, skill_catalog):
            self.assertIn("audience: human", text[:500])
            self.assertIn(GENERATED_NOTICE, text[:500])
        self.assertNotIn("classDef", repository_index)
        for path in repository_paths(ROOT, model):
            marker = (
                f"`{path}`"
                if path.startswith("external-skills/quantum-job-collector")
                else f"[{path}]"
            )
            self.assertIn(marker, repository_index)

    def test_skill_catalog_separates_orchestrator_from_five_skills(self) -> None:
        catalog = render_outputs(ROOT)["docs/human/_LIVE_SKILL_CATALOG.md"]
        orchestrator_section = catalog.split("# Skills Orchestrator", 1)[1].split(
            "# Public Skills", 1
        )[0]
        public_section = catalog.split("# Public Skills", 1)[1].split(
            "# Internal Capabilities", 1
        )[0]
        internal_section = catalog.split("# Internal Capabilities", 1)[1].split(
            "# Orchestrator Contents", 1
        )[0]
        self.assertIn("| skills-orchestrator |", orchestrator_section)
        for package_id in (
            "interaction-protocol",
            "theory-reference",
            "research-context-scout",
            "optimizer",
            "quantum-job-collector",
        ):
            self.assertIn(f"| {package_id} |", public_section)
        public_rows = [
            line
            for line in public_section.splitlines()
            if line.startswith("| ") and not line.startswith("| Public skill |")
        ]
        self.assertEqual(5, len(public_rows))
        self.assertNotIn("skills-orchestrator", public_section)
        self.assertNotIn("| code-explainer |", public_section)
        self.assertIn("| theory-reference | theory-reference |", internal_section)
        self.assertIn("never additional skills", catalog)

    def test_orchestrator_and_every_live_skill_have_declared_contents_boundary(self) -> None:
        catalog = render_outputs(ROOT)["docs/human/_LIVE_SKILL_CATALOG.md"]
        orchestrator_contents = catalog.split("# Orchestrator Contents", 1)[1].split(
            "# Skill Contents", 1
        )[0]
        self.assertIn("runtime/skills-orchestrator/SKILL.md", orchestrator_contents)
        package_contents = catalog.split("# Skill Contents", 1)[1]
        for package_id in (
            "interaction-protocol",
            "theory-reference",
            "research-context-scout",
            "optimizer",
            "quantum-job-collector",
        ):
            self.assertIn(f"## {package_id}", package_contents)

    def test_external_skill_is_not_traversed_for_tokens_or_contents(self) -> None:
        external_file = ROOT / "external-skills/quantum-job-collector/SKILL.md"
        self.assertEqual(
            _token_estimate(external_file, "external-skills/quantum-job-collector/SKILL.md"),
            "—",
        )
        catalog = render_outputs(ROOT)["docs/human/_LIVE_SKILL_CATALOG.md"]
        external_section = catalog.split("# Skill Contents", 1)[1].split(
            "## quantum-job-collector", 1
        )[1]
        self.assertIn("does not traverse or copy its files", external_section)
        self.assertNotIn("| [external-skills/quantum-job-collector/SKILL.md]", external_section)

    def test_repository_owned_external_skill_package_is_linked_and_traversed(self) -> None:
        internal_file = ROOT / "research-context-scout" / "SKILL.md"
        self.assertNotEqual(
            "—",
            _token_estimate(internal_file, "research-context-scout/SKILL.md"),
        )
        catalog = render_outputs(ROOT)["docs/human/_LIVE_SKILL_CATALOG.md"]
        internal_section = catalog.split("# Skill Contents", 1)[1].split(
            "## research-context-scout", 1
        )[1]
        self.assertIn(
            "| [research-context-scout/shared/SKILL.md]",
            internal_section,
        )
        repository_index = render_outputs(ROOT)["docs/human/_LIVE_REPOSITORY_INDEX.md"]
        self.assertIn(
            "[research-context-scout/README.md]"
            "(../../research-context-scout/README.md)",
            repository_index,
        )
        self.assertIn("codex/SKILL.md]", repository_index)
        self.assertIn("| Codex |", repository_index)
        self.assertIn("claude/CLAUDE.md]", repository_index)
        self.assertIn("| Claude |", repository_index)

    def test_generated_graph_nodes_are_uniquely_named_inventory_entries(self) -> None:
        outputs = render_outputs(ROOT)
        orchestrator = outputs["graph/orchestration/skills-orchestrator.md"]
        self.assertIn("# Skills Orchestrator", orchestrator)
        self.assertIn("graph_kind: orchestrator", orchestrator)
        for skill_id in (
            "interaction-protocol",
            "theory-reference",
            "research-context-scout",
            "optimizer",
            "quantum-job-collector",
        ):
            node = outputs[f"graph/skills/{skill_id}.md"]
            self.assertIn("graph_kind: skill-package", node)
            self.assertIn("[[graph/orchestration/skills-orchestrator|Skills Orchestrator]]", node)

    def test_checked_in_views_are_fresh(self) -> None:
        self.assertEqual(stale_outputs(ROOT), [])

    def test_untracked_scratch_files_do_not_enter_generated_views(self) -> None:
        model = load_model(ROOT)
        with patch(
            "compile_repository_views._git_paths",
            side_effect=[["README.md"], ["NOTES_SCRATCH.md", "scripts/measure_context.py"]],
        ):
            paths = repository_paths(ROOT, model)
        self.assertIn("README.md", paths)
        self.assertIn("scripts/measure_context.py", paths)
        self.assertNotIn("NOTES_SCRATCH.md", paths)

    def test_deleted_tracked_files_do_not_enter_generated_views(self) -> None:
        model = load_model(ROOT)
        with patch(
            "compile_repository_views._git_paths",
            side_effect=[["README.md", "tests/deleted-file.py"], []],
        ):
            paths = repository_paths(ROOT, model)
        self.assertIn("README.md", paths)
        self.assertNotIn("tests/deleted-file.py", paths)

    def test_plan_only_ideas_are_excluded_from_generated_views(self) -> None:
        model = load_model(ROOT)
        with patch(
            "compile_repository_views._git_paths",
            side_effect=[
                ["README.md", "skill-plans/future-scout/plan.md"],
                [],
            ],
        ):
            paths = repository_paths(ROOT, model)
        self.assertIn("README.md", paths)
        self.assertNotIn("skill-plans/future-scout/plan.md", paths)


if __name__ == "__main__":
    unittest.main()
