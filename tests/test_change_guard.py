#!/usr/bin/env python3

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from change_guard import GuardError, assess_change  # noqa: E402


class ChangeGuardTests(unittest.TestCase):
    def test_operation_cards_exist(self) -> None:
        cards = {
            "ADD.md",
            "EDIT.md",
            "UPDATE_MIGRATE.md",
            "MOVE_RENAME.md",
            "DEPRECATE_DELETE.md",
            "INSTALL_UNINSTALL.md",
            "SCOPE_EXPANSION.md",
            "PROTOCOL_AMENDMENT.md",
        }
        actual = {path.name for path in (ROOT / "protocols" / "repository").glob("*.md")}
        self.assertEqual(cards, actual)

    def test_scoped_repository_edit_is_allowed(self) -> None:
        report = assess_change("edit", ["docs/06_CHANGE_CONTROL.md"])
        self.assertEqual("allowed", report["status"])

    def test_protected_collection_requires_approval(self) -> None:
        report = assess_change("edit", ["caveman/skills/caveman/SKILL.md"])
        self.assertEqual("approval-required", report["status"])
        self.assertTrue(report["protected_paths"])

    def test_delete_requires_approval(self) -> None:
        report = assess_change("delete", ["runtime/README.md"])
        self.assertEqual("approval-required", report["status"])

    def test_explicit_approval_reference_is_recorded(self) -> None:
        report = assess_change("delete", ["runtime/README.md"], approval_ref="review-42")
        self.assertEqual("allowed-with-recorded-approval", report["status"])
        self.assertEqual("review-42", report["approval_reference"])

    def test_external_install_requires_approval(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            report = assess_change("install", [directory])
        self.assertEqual("approval-required", report["status"])
        self.assertTrue(report["external_paths"])

    def test_git_internal_target_is_blocked(self) -> None:
        report = assess_change("edit", [".git/config"])
        self.assertEqual("blocked-by-invariant", report["status"])

    def test_staged_file_outside_scope_is_blocked(self) -> None:
        report = assess_change(
            "update",
            ["scripts/route_skill.py"],
            staged_paths=["scripts/route_skill.py", "README.md"],
        )
        self.assertEqual("blocked-by-invariant", report["status"])
        self.assertEqual(["README.md"], report["staged_outside_scope"])

    def test_empty_scope_is_rejected(self) -> None:
        with self.assertRaises(GuardError):
            assess_change("edit", [])


if __name__ == "__main__":
    unittest.main()
