"""A declared package whose submodule folder is empty is unavailable, with a specific reason and fix."""

from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "orchestrator" / "runtime"))
sys.path.insert(0, str(ROOT / "orchestrator" / "tools"))

import install_runtime_adapter as installer  # noqa: E402
import orchestrate  # noqa: E402
from maintenance import cli as maintenance_cli  # noqa: E402
from model_context import (  # noqa: E402
    ContextError,
    capability_records,
    compact_catalog,
    discover,
    load_capabilities,
    load_capability,
    status_packet,
)
from registry_runtime import build_manifest  # noqa: E402

GITMODULES = (
    '[submodule "pkg-empty"]\n\tpath = pkg-empty\n\turl = https://example.invalid/pkg-empty.git\n'
    '[submodule "pkg-full"]\n\tpath = pkg-full\n\turl = https://example.invalid/pkg-full.git\n'
)


def route(package: str) -> dict:
    return {"package": package, "id": package, "path": f"{package}/SKILL.md", "description": "purpose", "state": "active"}


class PackageAvailabilityTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        (self.root / ".gitmodules").write_text(GITMODULES, encoding="utf-8")
        (self.root / "pkg-empty").mkdir()
        (self.root / "pkg-full").mkdir()
        (self.root / "pkg-full" / "SKILL.md").write_text("A complete entry", encoding="utf-8")
        (self.root / "loose").mkdir()  # declared nowhere and its entry is absent
        self.manifest = {
            "source_hash": "a" * 64,
            "packages": {name: {"state": "active"} for name in ("pkg-empty", "pkg-full", "loose")},
            "routes": [route("pkg-empty"), route("pkg-full"), route("loose")],
            "command_aliases": [],
        }

    def records(self) -> dict:
        return {r["capability"]: r for r in capability_records(self.root, self.manifest)}

    def test_empty_declared_submodule_is_unavailable_with_a_specific_reason(self) -> None:
        records = self.records()
        self.assertEqual("unavailable", records["pkg-empty"]["state"])
        self.assertEqual("PACKAGE_NOT_INITIALIZED", records["pkg-empty"]["unavailable_reason"])
        self.assertEqual("active", records["pkg-full"]["state"])
        self.assertNotIn("unavailable_reason", records["pkg-full"])

    def test_undeclared_missing_entry_keeps_the_generic_behavior(self) -> None:
        self.assertEqual("active", self.records()["loose"]["state"])
        with self.assertRaisesRegex(ContextError, "FILE_UNAVAILABLE"):
            load_capability(self.root, self.manifest, "loose")

    def test_a_git_link_alone_still_counts_as_empty_and_files_make_it_available(self) -> None:
        (self.root / "pkg-empty" / ".git").write_text("gitdir: ../.git/modules/pkg-empty\n", encoding="utf-8")
        self.assertEqual("unavailable", self.records()["pkg-empty"]["state"])
        (self.root / "pkg-empty" / "SKILL.md").write_text("Now populated", encoding="utf-8")
        self.assertEqual("active", self.records()["pkg-empty"]["state"])
        self.assertEqual("Now populated", load_capability(self.root, self.manifest, "pkg-empty")["body"])

    def test_missing_declared_folder_is_unavailable_too(self) -> None:
        (self.root / "pkg-empty").rmdir()
        self.assertEqual("PACKAGE_NOT_INITIALIZED", self.records()["pkg-empty"]["unavailable_reason"])

    def test_loading_names_the_reason_and_never_substitutes_another_package(self) -> None:
        with self.assertRaisesRegex(ContextError, "PACKAGE_NOT_INITIALIZED"):
            load_capability(self.root, self.manifest, "pkg-empty", explicit=True)
        with self.assertRaisesRegex(ContextError, "PACKAGE_NOT_INITIALIZED"):
            load_capabilities(self.root, self.manifest, ["pkg-full", "pkg-empty"])
        self.assertEqual("A complete entry", load_capability(self.root, self.manifest, "pkg-full")["body"])

    def test_discovery_catalog_and_status_show_the_state_and_the_fix(self) -> None:
        page = discover(self.root, self.manifest)
        states = {item["capability"]: item["state"] for item in page["items"]}
        self.assertEqual("unavailable", states["pkg-empty"])
        catalog = compact_catalog(page)
        self.assertIn('"state":"unavailable"', catalog)
        self.assertIn("PACKAGE_NOT_INITIALIZED", catalog)
        self.assertIn("git submodule update --init --recursive", catalog)
        self.assertEqual(1, catalog.count("PACKAGE_NOT_INITIALIZED"))
        listed = {c["capability"]: c for c in status_packet(self.root, self.manifest)["catalog"]["capabilities"]}
        self.assertEqual("PACKAGE_NOT_INITIALIZED", listed["pkg-empty"]["unavailable_reason"])
        self.assertNotIn("unavailable_reason", listed["pkg-full"])

    def test_terminal_status_names_empty_package_folders_and_the_fix(self) -> None:
        def rendered() -> str:
            runtime = {"repair": {}, "catalog": status_packet(self.root, self.manifest)["catalog"]}
            result = {"source": {"revision": "0" * 40, "clean": True}, "runtime": runtime,
                      "installations": [], "context": "host-supplied"}
            return maintenance_cli.render({"command": "status", "result": result})

        text = rendered()
        self.assertIn("Unavailable, empty package folders: pkg-empty\n", text)
        self.assertIn("Fix: git submodule update --init --recursive", text)
        (self.root / "pkg-empty" / "SKILL.md").write_text("populated", encoding="utf-8")
        self.assertNotIn("empty package folders", rendered())
        self.assertNotIn("submodule update", rendered())

    def test_catalog_without_unavailable_packages_has_no_extra_text(self) -> None:
        (self.root / "pkg-empty" / "SKILL.md").write_text("populated", encoding="utf-8")
        catalog = compact_catalog(discover(self.root, self.manifest))
        self.assertNotIn("unavailable", catalog)
        self.assertNotIn("submodule update", catalog)

    def test_error_packet_adds_only_a_fixed_fix_for_this_reason(self) -> None:
        self.assertEqual(
            {
                "schema": "skills-ai/error/1",
                "reason": "PACKAGE_NOT_INITIALIZED",
                "fix": "git submodule update --init --recursive",
                "authority": "none",
            },
            orchestrate.error_packet("PACKAGE_NOT_INITIALIZED"),
        )
        self.assertEqual(
            ["schema", "reason", "authority"], list(orchestrate.error_packet("UNKNOWN_CAPABILITY"))
        )

    def test_adapter_check_prints_a_warning_but_keeps_its_exit_code(self) -> None:
        arguments = ["install_runtime_adapter.py", "--adapter", "codex", "--check", "--config-dir", str(self.root)]
        for healthy, code in ((True, 0), (False, 1)):
            with self.subTest(healthy=healthy):
                output = io.StringIO()
                with patch.object(sys, "argv", arguments), patch.object(
                    installer, "check_adapter", return_value=healthy
                ), patch.object(installer, "uninitialized_packages", return_value=["markdown-protocol"]):
                    with contextlib.redirect_stdout(output):
                        self.assertEqual(code, installer.main())
                text = output.getvalue()
                self.assertIn("warning: these package folders are empty", text)
                self.assertIn("markdown-protocol", text)
                self.assertIn("git submodule update --init --recursive", text)

    def test_this_repository_has_every_declared_package_populated(self) -> None:
        records = capability_records(ROOT, build_manifest(ROOT))
        empty = sorted(r["capability"] for r in records if r["state"] == "unavailable")
        self.assertEqual([], empty, "initialize the package submodules: git submodule update --init --recursive")
        self.assertEqual([], installer.uninitialized_packages())


if __name__ == "__main__":
    unittest.main()
