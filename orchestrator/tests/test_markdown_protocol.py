from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "skills" / "markdown-protocol"
sys.path.insert(0, str(ROOT / "orchestrator" / "tools"))

from registry_runtime import build_manifest  # noqa: E402


class MarkdownProtocolTests(unittest.TestCase):
    """Parent integration: route, aliases and activation. The package's own contract tests live in its repository."""

    def read(self, relative: str) -> str:
        return (PACKAGE / relative).read_text(encoding="utf-8")

    def test_package_and_route_are_active_for_markdown_artifacts(self) -> None:
        manifest = build_manifest(ROOT)
        package = manifest["packages"]["markdown-protocol"]
        route = next(item for item in manifest["routes"] if item["id"] == "markdown-protocol")
        self.assertEqual("active", package["state"])
        self.assertEqual("task", package["role"])
        self.assertEqual("skills/markdown-protocol/SKILL.md", package["path"])
        self.assertEqual("active", route["state"])
        self.assertEqual("markdown", route["family"])
        self.assertEqual("skills/markdown-protocol/SKILL.md", route["path"])
        triggers = " ".join(route["triggers"]).lower()
        self.assertIn("markdown", triggers)
        self.assertIn("readme", triggers)
        self.assertIn("notes", triggers)
        self.assertIn("merely reading markdown instructions", route["not_for"].lower())

    def test_explicit_alias_forces_guided_mode(self) -> None:
        manifest = build_manifest(ROOT)
        alias = next(item for item in manifest["command_aliases"] if item["command"] == "#> md_protocol")
        self.assertEqual("markdown-protocol", alias["skill_id"])
        self.assertEqual("guided", alias["mode"])

    def test_named_commands_select_bounded_deepen_and_check_modes(self) -> None:
        manifest = build_manifest(ROOT)
        aliases = {
            item["command"]: item
            for item in manifest["command_aliases"]
            if item["skill_id"] == "markdown-protocol"
        }
        self.assertEqual("deepen", aliases["#> md_deepen"]["mode"])
        self.assertEqual("check", aliases["#> md_check"]["mode"])
        commands = self.read("references/named-commands.md")
        compact = " ".join(commands.split())
        self.assertIn("typed `Deeper` relative link", commands)
        self.assertIn("typed\n   `Parent` relative link", commands)
        self.assertIn("read-only structural check", compact)
        self.assertIn("do not bypass the review gate", compact)

    def test_activation_includes_markdown_inside_another_task(self) -> None:
        entry = self.read("SKILL.md")
        registry = (ROOT / "orchestrator" / "registry" / "markdown.md").read_text(encoding="utf-8")
        self.assertIn("including Markdown changed inside another task", entry)
        self.assertIn("including Markdown changed inside another task", " ".join(registry.split()))
        self.assertIn("Reading Markdown as input alone is not activation", " ".join(entry.split()))

    def test_orchestrator_requires_markdown_protocol_for_future_skill_packages(self) -> None:
        build = (ROOT / "orchestrator" / "runtime" / "skills-orchestrator" / "BUILD.md").read_text(encoding="utf-8")
        management = (ROOT / "orchestrator" / "runtime" / "skills-orchestrator" / "MANAGEMENT.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("For every future skill creation", build)
        self.assertIn("skill-package add-on", build)
        self.assertIn("smallest justified package profile", build)
        self.assertIn("Existing packages migrate one at a time", build)
        self.assertIn("For every future `add`, `edit`, `migrate`, or `document` operation", management)
        self.assertIn("Do not retrofit unnamed packages", management)


if __name__ == "__main__":
    unittest.main()
