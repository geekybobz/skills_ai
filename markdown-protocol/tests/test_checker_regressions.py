from __future__ import annotations

import importlib.util
import re
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock


TOOL = Path(__file__).resolve().parents[1] / "scripts" / "markdown_protocol.py"
SPEC = importlib.util.spec_from_file_location("markdown_protocol_checker", TOOL)
assert SPEC and SPEC.loader
checker = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = checker
SPEC.loader.exec_module(checker)


def page(body: str, *, frontmatter: str = "", home: str = "README.md", rule: str = "---") -> str:
    prefix = f"---\n{frontmatter.strip()}\n---\n" if frontmatter else ""
    return f"{prefix}{textwrap.dedent(body).strip()}\n\n{rule}\n\n[⌂ Home]({home})\n"


class CheckerRegressionTests(unittest.TestCase):
    def collection(self) -> tempfile.TemporaryDirectory[str]:
        return tempfile.TemporaryDirectory()

    def write(self, root: Path, name: str, content: str | bytes) -> Path:
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            target.write_bytes(content)
        else:
            target.write_text(content, encoding="utf-8")
        return target

    def messages(self, root: Path, **options: object) -> list[str]:
        return [item.message for item in checker.check_collection(root, **options)]

    def assert_clean(self, root: Path, **options: object) -> None:
        findings = checker.check_collection(root, **options)
        self.assertEqual([], findings, "\n".join(f"{x.level}: {x.path}: {x.message}" for x in findings))

    def test_A1_A2_A4_A7_github_heading_anchors(self) -> None:
        with self.collection() as temporary:
            root = Path(temporary).resolve()
            self.write(
                root,
                "README.md",
                page(
                    """
                    # Collection

                    [A1](#inputs--outputs) · [A2](#read_when-field) ·
                    [A4](#setext-title) · [A7](#launch--plan)

                    ## Inputs — outputs
                    ## read_when field
                    Setext title
                    ============
                    ## Launch 🚀 plan
                    """
                ),
            )
            self.assert_clean(root)

    def test_heading_table_matches_github_slugger_rules(self) -> None:
        headings = {
            "Inputs — outputs": "inputs--outputs",
            "Recall card — optional": "recall-card--optional",
            "read_when field": "read_when-field",
            "Under_score_name": "under_score_name",
            "C++ & Rust": "c--rust",
            "x = y + z": "x--y--z",
            "Launch 🚀 plan": "launch--plan",
            "A  double  space": "a--double--space",
            "Step 1: Setup": "step-1-setup",
            "What's new?": "whats-new",
            "`code` heading": "code-heading",
            "**Bold** text": "bold-text",
            "[Link](x.md) text": "link-text",
            "Ünïcödé Überschrift": "ünïcödé-überschrift",
            "Version 2.0.1": "version-201",
            "foo/bar": "foobar",
            "Q&A": "qa",
            "50% done": "50-done",
            "Why? Because!": "why-because",
            "Trailing hashes ##": "trailing-hashes",
        }
        source = "\n".join(f"## {heading}" for heading in headings)
        self.assertEqual(set(headings.values()), checker.slugged_headings(source))

    def test_F3_nested_short_fence_does_not_expose_example_link(self) -> None:
        with self.collection() as temporary:
            root = Path(temporary).resolve()
            self.write(
                root,
                "README.md",
                page("""
                # Collection

                ````markdown
                ```text
                [x](gone.md)
                ```
                ````
                """),
            )
            self.assert_clean(root)

    def test_F4_only_matching_fence_length_closes_block(self) -> None:
        with self.collection() as temporary:
            root = Path(temporary).resolve()
            self.write(
                root,
                "README.md",
                page("""
                # Collection

                ````markdown
                ```text
                ````

                [real](gone.md)
                """),
            )
            self.assertIn("broken link: gone.md", self.messages(root))

    def test_E2_utf8_bom_does_not_hide_frontmatter(self) -> None:
        with self.collection() as temporary:
            root = Path(temporary).resolve()
            content = page(
                "# Collection",
                frontmatter="role: front-door\nsummary: Fixture.\nread_when: Start here.",
                home="#collection",
            )
            self.write(root, "README.md", "\ufeff" + content)
            self.assert_clean(root, require_properties=True)

    def test_E3_non_utf8_file_is_reported_without_stopping_run(self) -> None:
        with self.collection() as temporary:
            root = Path(temporary).resolve()
            self.write(root, "README.md", page("# Collection\n\n[Bad](bad.md)", home="#collection"))
            self.write(root, "bad.md", b"# Caf\xe9\n\n---\n\n[\xe2\x8c\x82 Home](README.md)\n")
            findings = checker.check_collection(root)
            self.assertTrue(any(x.path == "bad.md" and "not valid UTF-8" in x.message for x in findings))

    def test_E5_footer_rule_accepts_trailing_space(self) -> None:
        with self.collection() as temporary:
            root = Path(temporary).resolve()
            self.write(root, "README.md", page("# Collection", home="#collection", rule="--- "))
            self.assert_clean(root)

    def test_L6_link_title_is_not_part_of_path(self) -> None:
        with self.collection() as temporary:
            root = Path(temporary).resolve()
            self.write(root, "README.md", page('# Collection\n\n[A](a.md "Title")', home="#collection"))
            self.write(root, "a.md", page("# A"))
            self.assert_clean(root)

    def test_L7_reference_style_link_definition_is_checked(self) -> None:
        with self.collection() as temporary:
            root = Path(temporary).resolve()
            self.write(root, "README.md", page("# Collection\n\nSee [A][r].\n\n[r]: gone.md", home="#collection"))
            self.assertIn("broken link: gone.md", self.messages(root))

    def test_L8_inline_code_link_syntax_is_ignored(self) -> None:
        with self.collection() as temporary:
            root = Path(temporary).resolve()
            self.write(root, "README.md", page("# Collection\n\nWrite `[x](gone.md)` to link.", home="#collection"))
            self.assert_clean(root)

    def test_L9_image_target_is_checked(self) -> None:
        with self.collection() as temporary:
            root = Path(temporary).resolve()
            self.write(root, "README.md", page("# Collection\n\n![Diagram](gone.png)", home="#collection"))
            self.assertIn("broken link: gone.png", self.messages(root))

    def test_I4_inventory_escapes_pipe_characters(self) -> None:
        with self.collection() as temporary:
            root = Path(temporary).resolve()
            self.write(
                root,
                "README.md",
                page(
                    "# Collection",
                    frontmatter="role: front-door\nsummary: Inputs | outputs\nread_when: Start here.",
                    home="#collection",
                ),
            )
            rendered = checker.render_inventory(root)
            row = next(line for line in rendered.splitlines() if "[README.md]" in line)
            self.assertIn("Inputs \\| outputs", row)
            self.assertEqual(5, len(re.findall(r"(?<!\\)\|", row)))

    def test_K3_compactness_is_inferred_without_properties(self) -> None:
        with self.collection() as temporary:
            root = Path(temporary).resolve()
            self.write(root, "README.md", page("# Collection\n\n[Topic](topic.md)", home="#collection"))
            core = "\n".join(f"- Line {number}" for number in range(31))
            self.write(root, "topic.md", page(f"# Topic\n\n## Core\n\n{core}"))
            findings = checker.check_collection(root)
            self.assertTrue(any(x.path == "topic.md" and x.level == "warning" and "threshold is 30" in x.message for x in findings))

    def test_P1_P2_unmanaged_properties_use_local_conventions(self) -> None:
        with self.collection() as temporary:
            root = Path(temporary).resolve()
            self.write(root, "README.md", page("# Collection\n\n[One](one.md) · [Two](two.md)", home="#collection"))
            self.write(root, "one.md", page("# One", frontmatter="status: draft-for-review"))
            self.write(root, "two.md", page("# Two", frontmatter="tags:\n  - interaction"))
            self.assert_clean(root)

    def test_P3_managed_tags_are_validated(self) -> None:
        with self.collection() as temporary:
            root = Path(temporary).resolve()
            self.write(root, "README.md", page("# Collection\n\n[Topic](topic.md)", home="#collection"))
            self.write(
                root,
                "topic.md",
                page(
                    "# Topic",
                    frontmatter=(
                        "role: topic\nparent: README.md\nsummary: Topic.\n"
                        "read_when: Read it.\ntags:\n  - interaction"
                    ),
                ),
            )
            self.assertTrue(any("invalid tag: interaction" in message for message in self.messages(root)))

    def test_C10_connections_accept_star_and_plus_bullets(self) -> None:
        for bullet in ("*", "+"):
            with self.subTest(bullet=bullet), self.collection() as temporary:
                root = Path(temporary).resolve()
                self.write(root, "README.md", page("# Collection\n\n[A](a.md) · [D](d.md)", home="#collection"))
                self.write(root, "a.md", page(f"# A\n\n## Connections\n\n{bullet} Deeper: [D](d.md)"))
                self.write(root, "d.md", page("# D"))
                self.assertTrue(any("not reciprocated by Parent" in message for message in self.messages(root)))

    def test_X3_target_headings_are_cached_once_per_file(self) -> None:
        with self.collection() as temporary:
            root = Path(temporary).resolve()
            links = "\n".join(f"[S{number}](big.md#section-{number})" for number in range(100))
            headings = "\n".join(f"## Section {number}" for number in range(100))
            self.write(root, "README.md", page(f"# Collection\n\n[Big](big.md)\n\n{links}", home="#collection"))
            self.write(root, "big.md", page(f"# Big\n\n{headings}"))
            original = checker.slugged_headings
            with mock.patch.object(checker, "slugged_headings", wraps=original) as wrapped:
                findings = checker.check_collection(root)
                self.assertFalse([item for item in findings if item.level == "error"])
            self.assertLessEqual(wrapped.call_count, 2)


if __name__ == "__main__":
    unittest.main()
