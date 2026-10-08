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

    def test_human_index_maps_the_package_without_default_loading(self) -> None:
        entry = self.read("SKILL.md")
        index = self.read("INDEX.md")
        compact_entry = " ".join(entry.split())
        self.assertIn("[INDEX.md](INDEX.md)", entry)
        self.assertIn("Do not load the index during ordinary task execution", compact_entry)
        for heading in ("Choose a route", "Package map", "Core references", "Add-ons"):
            self.assertIn(f"## {heading}", index)
        self.assertIn("compact machine entry", index)

    def test_skill_package_addon_has_adaptive_profiles_and_clear_owners(self) -> None:
        entry = self.read("SKILL.md")
        addon = self.read("references/addons/skill-package.md")
        self.assertIn("[skill-package.md](references/addons/skill-package.md)", entry)
        for profile in ("Minimal", "Routed", "Navigable", "Tool-bearing"):
            self.assertIn(profile, addon)
        self.assertIn("Target skill", addon)
        self.assertIn("Native skill-creation guidance", addon)
        self.assertIn("Markdown Protocol", addon)
        self.assertIn("Skills Orchestrator", addon)
        self.assertIn("does not authorize a repository-wide migration", addon)

    def test_orchestrator_requires_markdown_protocol_for_future_skill_packages(self) -> None:
        build = (ROOT / "runtime" / "skills-orchestrator" / "BUILD.md").read_text(encoding="utf-8")
        management = (ROOT / "runtime" / "skills-orchestrator" / "MANAGEMENT.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("For every future skill creation", build)
        self.assertIn("skill-package add-on", build)
        self.assertIn("smallest justified package profile", build)
        self.assertIn("Existing packages migrate one at a time", build)
        self.assertIn("For every future `add`, `edit`, `migrate`, or `document` operation", management)
        self.assertIn("Do not retrofit unnamed packages", management)

    def test_navigation_footer_is_a_required_portable_structure(self) -> None:
        entry = self.read("SKILL.md")
        core = self.read("references/core-protocol.md")
        layouts = self.read("references/layouts.md")
        validation = self.read("references/validation.md")
        self.assertIn("End every authored Markdown page", entry)
        self.assertIn("Home is mandatory", core)
        self.assertIn(
            "[← Previous](previous.md) · [⌂ Home](../README.md) · [Next →](next.md)",
            core,
        )
        self.assertIn("curated sequence", layouts)
        self.assertIn("Every authored page ends with a resolving Home footer link", validation)

    def test_every_package_markdown_file_ends_with_a_home_footer(self) -> None:
        for path in PACKAGE.rglob("*.md"):
            with self.subTest(path=path.relative_to(PACKAGE)):
                lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
                self.assertRegex(lines[-1], r"\[⌂ Home\]\([^)]+\)")
                self.assertEqual(1, lines[-1].count("[⌂ Home]"))
                self.assertEqual("---", lines[-2])

    def test_package_footer_file_links_resolve(self) -> None:
        footer_link = re.compile(r"\[[^]]+\]\(([^)#]+\.md)(?:#[^)]+)?\)")
        for path in PACKAGE.rglob("*.md"):
            lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
            for target in footer_link.findall(lines[-1]):
                with self.subTest(path=path.relative_to(PACKAGE), target=target):
                    self.assertTrue((path.parent / target).resolve().is_file())

    def test_package_footer_local_anchors_resolve(self) -> None:
        local_anchor = re.compile(r"\[[^]]+\]\(#([^)]+)\)")
        for path in PACKAGE.rglob("*.md"):
            text = path.read_text(encoding="utf-8")
            footer = [line for line in text.splitlines() if line.strip()][-1]
            headings = {
                re.sub(r"[^a-z0-9 -]", "", heading.lower()).strip().replace(" ", "-")
                for heading in re.findall(r"^#{1,6}\s+(.+)$", text, flags=re.MULTILINE)
            }
            for anchor in local_anchor.findall(footer):
                with self.subTest(path=path.relative_to(PACKAGE), anchor=anchor):
                    self.assertIn(anchor, headings)

    def test_package_previous_and_next_footer_links_are_reciprocal(self) -> None:
        relation = re.compile(r"\[(← Previous|Next →)\]\(([^)#]+\.md)(?:#[^)]+)?\)")
        inverse = {"← Previous": "Next →", "Next →": "← Previous"}
        for path in PACKAGE.rglob("*.md"):
            footer = [
                line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
            ][-1]
            for label, target in relation.findall(footer):
                target_path = (path.parent / target).resolve()
                target_footer = [
                    line
                    for line in target_path.read_text(encoding="utf-8").splitlines()
                    if line.strip()
                ][-1]
                expected = path.relative_to(target_path.parent).as_posix()
                with self.subTest(path=path.relative_to(PACKAGE), target=target):
                    self.assertIn(f"[{inverse[label]}]({expected})", target_footer)

    def test_entry_reference_links_resolve(self) -> None:
        entry = PACKAGE / "SKILL.md"
        for target in re.findall(r"\[[^]]+\]\(([^)]+\.md)\)", entry.read_text(encoding="utf-8")):
            self.assertTrue((entry.parent / target).resolve().is_file(), target)

    def test_human_index_reference_links_resolve(self) -> None:
        index = PACKAGE / "INDEX.md"
        for target in re.findall(r"\[[^]]+\]\(([^)#]+\.md)(?:#[^)]+)?\)", index.read_text(encoding="utf-8")):
            self.assertTrue((index.parent / target).resolve().is_file(), target)

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
