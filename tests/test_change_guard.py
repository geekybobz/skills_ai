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
            "EXTERNAL_CHANGE_REQUEST.md",
            "REPAIR_WORKSPACE.md",
        }
        actual = {path.name for path in (ROOT / "protocols" / "repository").glob("*.md")}
        self.assertEqual(cards, actual)

    def test_machine_contract_exists(self) -> None:
        self.assertTrue((ROOT / "protocols" / "repository" / "CONTRACT.json").is_file())
        self.assertTrue((ROOT / "protocols" / "repository" / "DOCUMENTATION.json").is_file())

    def test_scoped_repository_edit_is_allowed(self) -> None:
        report = assess_change("edit", ["docs/06_CHANGE_CONTROL.md"])
        self.assertEqual("allowed", report["status"])

    def test_protected_collection_requires_approval(self) -> None:
        report = assess_change("edit", ["interaction-protocol/protocol.json"])
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
            ["scripts/orchestrate.py"],
            staged_paths=["scripts/orchestrate.py", "README.md"],
        )
        self.assertEqual("blocked-by-invariant", report["status"])
        self.assertEqual(["README.md"], report["staged_outside_scope"])

    def test_empty_scope_is_rejected(self) -> None:
        with self.assertRaises(GuardError):
            assess_change("edit", [])

    def test_external_request_operation_is_limited_to_pending_inbox(self) -> None:
        allowed = assess_change("request", ["requests/pending/request.md"])
        blocked = assess_change("request", ["registry/theory.md"])
        self.assertEqual("allowed", allowed["status"])
        self.assertEqual("blocked-by-invariant", blocked["status"])

    def test_markdown_changes_require_graph_layer_validation(self) -> None:
        report = assess_change("add", ["docs/new-governance-note.md"])
        self.assertIn("python3 scripts/graph_layers.py --check", report["required_checks"])

    def test_skill_change_derives_registry_and_unit_checks(self) -> None:
        report = assess_change(
            "add",
            ["external-skills/fixture-skill/SKILL.md"],
            approval_ref="approved-skill-add",
        )
        self.assertIn("skill-source", report["roles"]["external-skills/fixture-skill/SKILL.md"])
        self.assertIn("registry", report["required_check_ids"])
        self.assertIn("unit", report["required_check_ids"])

    def test_registry_source_reports_affected_generated_manifest(self) -> None:
        report = assess_change("edit", ["registry/optimizer.md"])
        self.assertEqual(
            [
                "docs/human/_LIVE_REPOSITORY_INDEX.md",
                "docs/human/_LIVE_SKILL_CATALOG.md",
                "runtime/manifest.json",
            ],
            report["affected_generated_outputs"],
        )
        self.assertIn("views", report["required_check_ids"])

    def test_unmapped_new_path_is_blocked(self) -> None:
        report = assess_change("add", ["unknown-concept/source.bin"])
        self.assertEqual("blocked-by-invariant", report["status"])
        self.assertEqual(["unknown-concept/source.bin"], report["unmapped_paths"])

    def test_plan_only_idea_has_no_repository_checks(self) -> None:
        report = assess_change("add", ["skill-plans/future-scout/plan.md"])
        self.assertEqual("allowed", report["status"])
        self.assertEqual(["skill-plan-draft"], report["roles"]["skill-plans/future-scout/plan.md"])
        self.assertEqual([], report["required_check_ids"])

    def test_extra_plan_files_do_not_inherit_the_fast_path(self) -> None:
        report = assess_change("add", ["skill-plans/future-scout/SKILL.md"])
        self.assertEqual("blocked-by-invariant", report["status"])
        self.assertEqual(["skill-plans/future-scout/SKILL.md"], report["unmapped_paths"])


if __name__ == "__main__":
    unittest.main()
