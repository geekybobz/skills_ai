from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "markdown-protocol"
sys.path.insert(0, str(ROOT / "scripts"))

from registry_runtime import build_manifest  # noqa: E402


class MarkdownProtocolTests(unittest.TestCase):
    def read(self, relative: str) -> str:
        return (PACKAGE / relative).read_text(encoding="utf-8")

    def test_package_and_route_are_active_for_markdown_artifacts(self) -> None:
        manifest = build_manifest(ROOT)
        package = manifest["packages"]["markdown-protocol"]
        route = next(item for item in manifest["routes"] if item["id"] == "markdown-protocol")
        self.assertEqual("active", package["state"])
        self.assertEqual("task", package["role"])
        self.assertEqual("markdown-protocol/SKILL.md", package["path"])
        self.assertEqual("active", route["state"])
        self.assertEqual("markdown", route["family"])
        self.assertEqual("markdown-protocol/SKILL.md", route["path"])
        triggers = " ".join(route["triggers"]).lower()
        self.assertIn("markdown", triggers)
        self.assertIn("readme", triggers)
        self.assertIn("notes", triggers)
        self.assertIn("merely reading markdown instructions", route["not_for"].lower())

    def test_implicit_native_invocation_is_enabled(self) -> None:
        metadata = self.read("agents/openai.yaml")
        self.assertIn("allow_implicit_invocation: true", metadata)

    def test_explicit_alias_forces_review_mode(self) -> None:
        manifest = build_manifest(ROOT)
        alias = next(item for item in manifest["command_aliases"] if item["command"] == "#> md_protocol")
        self.assertEqual("markdown-protocol", alias["skill_id"])
        self.assertEqual("review", alias["mode"])

    def test_entry_routes_writes_through_proportional_review(self) -> None:
        entry = self.read("SKILL.md")
        workflow = self.read("references/review-workflow.md")
        self.assertIn("[review-workflow.md]", entry)
        self.assertIn("Before any Markdown write", entry)
        self.assertIn("wait for the user's agreement", entry)
        self.assertIn("Local edit", workflow)
        self.assertIn("Collection change", workflow)
        self.assertIn("Continue without another pause", workflow)
        self.assertIn("user's direct edits are new source state", workflow)

    def test_education_addon_is_selective_and_model_led(self) -> None:
        entry = self.read("SKILL.md")
        education = self.read("references/addons/education.md")
        self.assertIn("[education.md](references/addons/education.md)", entry)
        self.assertIn("the user does not have to choose", education)
        self.assertIn("Choose the minimum useful combination", education)
        self.assertIn("not a required file layout", education)
        self.assertNotIn("Add every", education)

    def test_education_addon_has_restrained_visual_and_tone_rules(self) -> None:
        education = self.read("references/addons/education.md")
        self.assertIn("Use headings and whitespace before decorative devices", education)
        self.assertIn("Avoid decorative icons", education)
        self.assertIn("Write short, compact, straightforward sentences", education)
        self.assertIn("preserve the reader's established tone", education)
        self.assertIn("later manual edits", education)

    def test_education_reading_suggestions_require_verified_sources(self) -> None:
        education = self.read("references/addons/education.md")
        compact = " ".join(education.split())
        for field in ("title", "authorship", "year", "source type", "link target", "relevance"):
            self.assertIn(field, education)
        self.assertIn("Prefer a DOI, publisher page, arXiv record", education)
        self.assertIn("Do not invent a citation", education)
        self.assertIn("grants no network or acquisition authority", compact)

    def test_codebase_addon_is_selective_and_routes_real_code_questions(self) -> None:
        entry = self.read("SKILL.md")
        codebase = self.read("references/addons/codebase.md")
        compact = " ".join(codebase.split())
        self.assertIn("[codebase.md](references/addons/codebase.md)", entry)
        self.assertIn("select the smallest useful combination of views", compact)
        self.assertIn("Do not require every zoom level", codebase)
        self.assertIn("Small", codebase)
        self.assertIn("Medium", codebase)
        self.assertIn("Complex", codebase)

    def test_codebase_addon_connects_visuals_to_files_and_verification(self) -> None:
        codebase = self.read("references/addons/codebase.md")
        self.assertIn("Numbered workflow journey", codebase)
        self.assertIn("File responsibility map", codebase)
        self.assertIn("Change-impact guide", codebase)
        self.assertIn("file or symbol", codebase)
        self.assertIn("verified by", codebase)
        self.assertIn("same names and numbers across diagrams and text", codebase)

    def test_codebase_addon_preserves_portability_and_avoids_graph_sprawl(self) -> None:
        codebase = self.read("references/addons/codebase.md")
        compact = " ".join(codebase.split())
        self.assertIn("portable baseline", compact)
        self.assertIn("Preserve a text fallback", codebase)
        self.assertIn("Do not hand-maintain a complete import graph", codebase)
        self.assertIn("Graphviz", codebase)
        self.assertIn("No mandatory tool", codebase)

    def test_entry_reference_links_resolve(self) -> None:
        entry = PACKAGE / "SKILL.md"
        for target in re.findall(r"\[[^]]+\]\(([^)]+\.md)\)", entry.read_text(encoding="utf-8")):
            self.assertTrue((entry.parent / target).resolve().is_file(), target)

    def test_pattern_gallery_links_to_small_examples(self) -> None:
        gallery = PACKAGE / "references" / "markdown-patterns.md"
        targets = re.findall(r"\[[^]]+\]\((formatting-examples/[^)]+\.md)\)", gallery.read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(targets), 15)
        self.assertEqual(len(targets), len(set(targets)))
        for target in targets:
            path = gallery.parent / target
            self.assertTrue(path.is_file(), target)
            self.assertLess(path.stat().st_size, 8_000, target)

    def test_core_documents_use_portable_links(self) -> None:
        for name in (
            "core-protocol.md",
            "layouts.md",
            "markdown-patterns.md",
            "review-workflow.md",
            "visual-patterns.md",
            "validation.md",
        ):
            with self.subTest(name=name):
                self.assertNotIn("[[", self.read(f"references/{name}"))

    def test_math_guidance_is_explicitly_unverified(self) -> None:
        math_example = self.read("references/formatting-examples/13-mathematical-expressions.md")
        self.assertIn("**Verification status:** Pending", math_example)
        self.assertIn("Do not select a house style", math_example)


if __name__ == "__main__":
    unittest.main()
