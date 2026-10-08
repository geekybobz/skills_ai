from __future__ import annotations

import re
import subprocess
import sys
import tempfile
import textwrap
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

    def test_explicit_alias_forces_guided_mode(self) -> None:
        manifest = build_manifest(ROOT)
        alias = next(item for item in manifest["command_aliases"] if item["command"] == "#> md_protocol")
        self.assertEqual("markdown-protocol", alias["skill_id"])
        self.assertEqual("guided", alias["mode"])

    def test_activation_includes_markdown_inside_another_task(self) -> None:
        entry = self.read("SKILL.md")
        registry = (ROOT / "registry" / "markdown.md").read_text(encoding="utf-8")
        self.assertIn("including Markdown changed inside another task", entry)
        self.assertIn("including Markdown changed inside another task", " ".join(registry.split()))
        self.assertIn("Reading Markdown\n  as input alone is not activation", entry)

    def test_entry_routes_writes_through_proportional_review(self) -> None:
        entry = self.read("SKILL.md")
        workflow = self.read("references/review-workflow.md")
        self.assertIn("[review-workflow.md]", entry)
        self.assertIn("Before writing", entry)
        self.assertIn("wait for agreement", entry)
        self.assertIn("Local edit", workflow)
        self.assertIn("Collection change", workflow)
        self.assertIn("Implement only the agreed design", workflow)
        self.assertIn("user's direct edit is new source state", workflow)

    def test_compact_local_edit_loading_path_has_a_measured_budget(self) -> None:
        parts = [self.read("SKILL.md")]
        for relative in (
            "references/core-protocol.md",
            "references/review-workflow.md",
            "references/validation.md",
        ):
            parts.append(self.read(relative).split("\n## Details", 1)[0])
        compact = "".join(parts)
        self.assertLessEqual(len(compact.encode("utf-8")), 8_500)
        self.assertLessEqual(len(compact.splitlines()), 180)

    def test_details_boundary_keeps_authority_in_the_compact_layer(self) -> None:
        core = self.read("references/core-protocol.md")
        layouts = self.read("references/layouts.md")
        validation = self.read("references/validation.md")
        self.assertIn("Everything a reader must obey or rely on appears above", core)
        self.assertIn("they never add,\n   weaken, or replace a rule", core)
        self.assertIn("No new rule begins here", layouts)
        self.assertIn("appear above\n  the first `## Details`", validation)

    def test_compactness_thresholds_are_review_warnings(self) -> None:
        layouts = self.read("references/layouts.md")
        self.assertIn("roughly 30 non-empty", layouts)
        self.assertIn("roughly 60", layouts)
        self.assertIn("warnings, not failures", layouts)

    def test_orientation_view_and_teaching_hook_remain_proportional(self) -> None:
        layouts = self.read("references/layouts.md")
        workflow = self.read("references/review-workflow.md")
        compact_layouts = " ".join(layouts.split())
        self.assertIn("A diagram is not mandatory", layouts)
        self.assertIn("nontrivial Compact profile", compact_layouts)
        self.assertIn("Patterns used", workflow)
        self.assertIn("Omit the line for\nordinary headings", workflow)

    def test_structured_inventory_tool_builds_checks_and_detects_errors(self) -> None:
        tool = PACKAGE / "scripts" / "markdown_protocol.py"
        with tempfile.TemporaryDirectory() as temporary:
            collection = Path(temporary)
            (collection / "topics").mkdir()
            readme = textwrap.dedent(
                """\
                ---
                role: front-door
                summary: Fixture collection.
                read_when: Start here.
                ---
                # Collection

                [Index](INDEX.md) · [Inventory](INVENTORY.md)

                ---

                [⌂ Home](#collection)
                """
            )
            index = textwrap.dedent(
                """\
                ---
                role: index
                parent: README.md
                summary: Human topic map.
                read_when: Browse the fixture.
                ---
                # Index

                - [Topic](topics/topic.md)

                ---

                [⌂ Home](README.md)
                """
            )
            topic = textwrap.dedent(
                """\
                ---
                role: topic
                parent: ../INDEX.md
                summary: One fixture topic.
                read_when: Test the checker.
                tags:
                  - domain/testing
                  - use/validation
                ---
                # Topic

                ## In brief

                Compact fixture.

                ## Core

                Authoritative fixture content.

                ---

                [⌂ Home](../README.md)
                """
            )
            (collection / "README.md").write_text(readme, encoding="utf-8")
            (collection / "INDEX.md").write_text(index, encoding="utf-8")
            topic_path = collection / "topics" / "topic.md"
            topic_path.write_text(topic, encoding="utf-8")

            before_index = (collection / "INDEX.md").read_text(encoding="utf-8")
            built = subprocess.run(
                [sys.executable, str(tool), "inventory", str(collection), "--write"],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(0, built.returncode, built.stderr)
            self.assertEqual(before_index, (collection / "INDEX.md").read_text(encoding="utf-8"))
            inventory = (collection / "INVENTORY.md").read_text(encoding="utf-8")
            self.assertIn("Generated file. Do not edit directly.", inventory)
            self.assertIn("## Optional", inventory)

            checked = subprocess.run(
                [sys.executable, str(tool), "check", str(collection), "--require-properties"],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(0, checked.returncode, checked.stdout + checked.stderr)
            self.assertIn("PASS", checked.stdout)

            long_core = "\n".join(f"Line {number}." for number in range(31))
            topic_path.write_text(
                topic.replace("Authoritative fixture content.", long_core),
                encoding="utf-8",
            )
            warned = subprocess.run(
                [sys.executable, str(tool), "check", str(collection), "--require-properties"],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(0, warned.returncode, warned.stdout + warned.stderr)
            self.assertIn("WARNING", warned.stdout)
            self.assertIn("review threshold is 30", warned.stdout)

            topic_path.write_text(
                topic.replace("Authoritative fixture content.", "[Broken](missing.md)"),
                encoding="utf-8",
            )
            broken = subprocess.run(
                [sys.executable, str(tool), "check", str(collection), "--require-properties"],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(1, broken.returncode)
            self.assertIn("broken link", broken.stdout)

            topic_path.write_text(topic.replace("summary:", "note:"), encoding="utf-8")
            missing = subprocess.run(
                [sys.executable, str(tool), "inventory", str(collection), "--check"],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(1, missing.returncode)
            self.assertIn("missing summary", missing.stderr)

    def test_typed_connections_learning_order_and_cycle_detection(self) -> None:
        tool = PACKAGE / "scripts" / "markdown_protocol.py"
        with tempfile.TemporaryDirectory() as temporary:
            collection = Path(temporary)
            readme = """# Collection\n\n- [A](a.md)\n- [B](b.md)\n- [C](c.md)\n\n---\n\n[⌂ Home](#collection)\n"""
            a = """# A\n\n## Connections\n\n- Next: [B](b.md)\n- Deeper: [B](b.md)\n\n---\n\n[⌂ Home](README.md) · [Next →](b.md)\n"""
            b = """# B\n\n## Connections\n\n- Parent: [A](a.md)\n- Prerequisite: [C](c.md)\n\n---\n\n[← Previous](a.md) · [⌂ Home](README.md)\n"""
            c = """# C\n\n## Connections\n\n- Related: [A](a.md)\n\n---\n\n[⌂ Home](README.md)\n"""
            for name, content in (("README.md", readme), ("a.md", a), ("b.md", b), ("c.md", c)):
                (collection / name).write_text(content, encoding="utf-8")

            checked = subprocess.run(
                [sys.executable, str(tool), "check", str(collection)],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(0, checked.returncode, checked.stdout + checked.stderr)

            graphed = subprocess.run(
                [sys.executable, str(tool), "graph", str(collection), "--topic", "b.md"],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(0, graphed.returncode, graphed.stdout + graphed.stderr)
            self.assertIn("Required before b.md:\n- c.md", graphed.stdout)
            self.assertIn("Orphans:\n- None.", graphed.stdout)
            order = graphed.stdout.split("Required before", 1)[0]
            self.assertLess(order.index("c.md"), order.index("b.md"))

            (collection / "a.md").write_text(a.replace("- Deeper: [B](b.md)\n", ""), encoding="utf-8")
            unpaired = subprocess.run(
                [sys.executable, str(tool), "check", str(collection)],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(1, unpaired.returncode)
            self.assertIn("not reciprocated by Deeper", unpaired.stdout)
            (collection / "a.md").write_text(a, encoding="utf-8")

            (collection / "c.md").write_text(
                c.replace("- Related: [A](a.md)", "- Prerequisite: [B](b.md)"),
                encoding="utf-8",
            )
            cycled = subprocess.run(
                [sys.executable, str(tool), "check", str(collection)],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(1, cycled.returncode)
            self.assertIn("prerequisite cycle", cycled.stdout)

    def test_tag_vocabulary_validation_and_and_filtering(self) -> None:
        tool = PACKAGE / "scripts" / "markdown_protocol.py"
        with tempfile.TemporaryDirectory() as temporary:
            collection = Path(temporary)
            (collection / "README.md").write_text(
                "# Collection\n\n- [A](a.md)\n- [B](b.md)\n\n---\n\n[⌂ Home](#collection)\n",
                encoding="utf-8",
            )
            a = """---
role: topic
parent: README.md
summary: Control learning topic.
read_when: Learn control.
tags:
  - domain/control
  - use/learning
---
# A

---

[⌂ Home](README.md)
"""
            b = a.replace("Control learning topic.", "Control reference topic.").replace(
                "use/learning", "use/reference"
            ).replace("# A", "# B")
            (collection / "a.md").write_text(a, encoding="utf-8")
            (collection / "b.md").write_text(b, encoding="utf-8")

            checked = subprocess.run(
                [sys.executable, str(tool), "check", str(collection)],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(0, checked.returncode, checked.stdout + checked.stderr)

            vocabulary = subprocess.run(
                [sys.executable, str(tool), "tags", str(collection)],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(0, vocabulary.returncode)
            self.assertIn("domain/control: 2 file(s)", vocabulary.stdout)

            filtered = subprocess.run(
                [
                    sys.executable,
                    str(tool),
                    "tags",
                    str(collection),
                    "--tag",
                    "domain/control",
                    "--tag",
                    "use/learning",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(0, filtered.returncode)
            self.assertIn("a.md", filtered.stdout)
            self.assertNotIn("b.md", filtered.stdout)

            (collection / "a.md").write_text(
                a.replace("use/learning", "audience/learner"), encoding="utf-8"
            )
            invalid = subprocess.run(
                [sys.executable, str(tool), "check", str(collection)],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(1, invalid.returncode)
            self.assertIn("invalid tag", invalid.stdout)

    def test_education_addon_is_selective_and_model_led(self) -> None:
        routes = self.read("references/addons/routes.md")
        education = self.read("references/addons/education.md")
        self.assertIn("[education.md](education.md)", routes)
        self.assertIn("the user does not have to choose", education)
        self.assertIn("Choose the minimum useful combination", education)
        self.assertIn("not a required file layout", education)
        self.assertNotIn("Add every", education)

    def test_addon_contract_keeps_extensions_optional_and_bounded(self) -> None:
        entry = self.read("SKILL.md")
        routes = self.read("references/addons/routes.md")
        contract = self.read("references/addons/add-on-contract.md")
        self.assertIn("[add-on routes](references/addons/routes.md)", entry)
        self.assertIn("[add-on-contract.md](add-on-contract.md)", routes)
        for field in (
            "Trigger",
            "Blocks",
            "Layout variants",
            "Generated views",
            "Checks",
            "Composition",
            "Boundaries",
        ):
            self.assertIn(field, contract)
        compact = " ".join(contract.split())
        self.assertIn("may not weaken the core invariants", compact)
        self.assertIn("minimum useful combination", compact)
        self.assertIn("Selection grants no network", compact)
        for name in (
            "education.md",
            "codebase.md",
            "research-notes.md",
            "decision-records.md",
            "runbooks.md",
            "skill-package.md",
        ):
            addon = self.read(f"references/addons/{name}")
            self.assertIn("## Add-on declaration", addon)
            self.assertIn("| Trigger |", addon)
            self.assertIn("| Generated views |", addon)
            self.assertIn("| Boundaries |", addon)

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

    def test_education_addon_designs_optional_recall_deck_path_and_glossary(self) -> None:
        education = self.read("references/addons/education.md")
        compact = " ".join(education.split())
        self.assertIn("## Optional recall card", education)
        self.assertIn("**Question:**", education)
        self.assertIn("<details>", education)
        self.assertIn("Prefer the\nQuick Review / Fact Card", education)
        self.assertIn("## Glossary block", education)
        self.assertIn("typed `Prerequisite` connections", education)
        self.assertIn("## Optional generated review deck", education)
        self.assertIn("links every card back to its owning topic", education)
        self.assertIn("does not itself authorize or provide a generator", compact)
        self.assertIn("hide no prerequisite", education)

    def test_codebase_addon_is_selective_and_routes_real_code_questions(self) -> None:
        routes = self.read("references/addons/routes.md")
        codebase = self.read("references/addons/codebase.md")
        compact = " ".join(codebase.split())
        self.assertIn("[codebase.md](codebase.md)", routes)
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

    def test_codebase_addon_designs_bounded_generated_navigation(self) -> None:
        codebase = self.read("references/addons/codebase.md")
        compact = " ".join(codebase.split())
        self.assertIn("## Optional generated Python import map", codebase)
        self.assertIn("standard library `ast` module", compact)
        self.assertIn("never present the result as a complete runtime call graph", compact)
        self.assertIn("one small package diagram", compact)
        self.assertIn("sortable text table", compact)
        self.assertIn("## Entry points and where-used views", codebase)
        self.assertIn("bounded reverse lookup", codebase)
        self.assertIn("Source code and tests decide behavior", compact)

    def test_research_notes_addon_separates_evidence_and_interpretation(self) -> None:
        routes = self.read("references/addons/routes.md")
        index = self.read("INDEX.md")
        addon = self.read("references/addons/research-notes.md")
        compact = " ".join(addon.split())
        self.assertIn("[research-notes.md](research-notes.md)", routes)
        self.assertIn("Research Notes Add-on", index)
        self.assertIn("citation_key", addon)
        for status in ("exact", "empirical", "numerical", "proposed", "uncertain"):
            self.assertIn(f"| {status} |", addon)
        self.assertIn("`research-context-scout`", addon)
        self.assertIn("does not establish influence, priority, or consensus", compact)
        self.assertIn("No citation, quotation, result, or access status is invented", addon)

    def test_decision_records_preserve_rationale_and_supersession(self) -> None:
        routes = self.read("references/addons/routes.md")
        addon = self.read("references/addons/decision-records.md")
        compact = " ".join(addon.split())
        self.assertIn("[decision-records.md](decision-records.md)", routes)
        for heading in ("Context", "Decision", "Consequences", "Alternatives considered"):
            self.assertIn(f"## {heading}", addon)
        self.assertIn("proposed | accepted | deprecated | superseded", addon)
        self.assertIn("link both directions", compact)
        self.assertIn("copying a meeting transcript", addon)

    def test_runbooks_pair_actions_with_verification_and_recovery(self) -> None:
        routes = self.read("references/addons/routes.md")
        addon = self.read("references/addons/runbooks.md")
        compact = " ".join(addon.split())
        self.assertIn("[runbooks.md](runbooks.md)", routes)
        self.assertIn("\\text{Action} + \\text{Expected result} + \\text{Verification}", addon)
        for label in ("**Action:**", "**Expected:**", "**Verify:**", "**Stop if:**"):
            self.assertIn(label, addon)
        self.assertIn("## Rollback or recovery", addon)
        self.assertIn("does not grant permission to execute itself", compact)
        self.assertIn("Sample output is visibly illustrative", addon)

    def test_human_index_maps_the_package_without_default_loading(self) -> None:
        entry = self.read("SKILL.md")
        index = self.read("INDEX.md")
        compact_entry = " ".join(entry.split())
        self.assertIn("[INDEX.md](INDEX.md)", entry)
        self.assertIn("ordinary model work does not", compact_entry)
        for heading in ("Choose a route", "Package map", "Core references", "Add-ons"):
            self.assertIn(f"## {heading}", index)
        self.assertIn("compact machine entry", index)

    def test_skill_package_addon_has_adaptive_profiles_and_clear_owners(self) -> None:
        routes = self.read("references/addons/routes.md")
        addon = self.read("references/addons/skill-package.md")
        self.assertIn("[skill-package.md](skill-package.md)", routes)
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
        self.assertIn("Every authored page ends with the", entry)
        self.assertIn("Home points to the nearest Front Door", core)
        self.assertIn(
            "[← Previous](previous.md) · [⌂ Home](../README.md) · [Next →](next.md)",
            core,
        )
        self.assertIn("curated sequence", layouts)
        self.assertIn("Home footers", validation)

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

    def test_phase_two_gallery_and_renderer_matrix_are_explicit(self) -> None:
        gallery = self.read("references/markdown-patterns.md")
        visual = self.read("references/visual-patterns.md")
        for name in (
            "17-editor-folding.md",
            "18-markmap-view.md",
            "19-editable-svg-diagrams.md",
            "20-renderer-verification-fixture.md",
        ):
            self.assertIn(name, gallery)
            self.assertTrue((PACKAGE / "references" / "formatting-examples" / name).is_file())
        self.assertIn("### Renderer matrix", gallery)
        self.assertIn("visual pass pending", gallery)
        self.assertIn("P = max(N / 12, E / 12, L / 8)", visual)
        self.assertIn("A = width / height", visual)

    def test_renderer_fixture_covers_visual_and_math_risks(self) -> None:
        fixture = self.read(
            "references/formatting-examples/20-renderer-verification-fixture.md"
        )
        self.assertGreaterEqual(fixture.count("```mermaid"), 3)
        self.assertIn("$E = mc^2$", fixture)
        self.assertIn("\\begin{aligned}", fixture)
        self.assertIn("<details>", fixture)
        self.assertIn("> [!WARNING]", fixture)
        self.assertIn("Text fallback", fixture)

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

    def test_math_guidance_has_a_bounded_verified_house_style(self) -> None:
        math_example = self.read("references/formatting-examples/13-mathematical-expressions.md")
        self.assertIn("## Provisional house style", math_example)
        self.assertIn("VS Code uses KaTeX", math_example)
        self.assertIn("GitHub uses MathJax", math_example)
        self.assertIn("Do not depend on `\\label`, `\\ref`", math_example)


if __name__ == "__main__":
    unittest.main()
