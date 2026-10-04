#!/usr/bin/env python3

from __future__ import annotations

import copy
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from change_guard import load_contract  # noqa: E402
from scan_consistency import (  # noqa: E402
    ScanError,
    _ai_review_packet,
    _is_registered_package_support,
    apply_baseline,
    apply_generated_outputs,
    classify_maintenance,
    compact_baseline,
    collect_changes,
    infer_operation,
    scan,
    split_scope,
    validate_contract,
)


class ConsistencyScanTests(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = load_contract(ROOT)

    def test_plan_derives_skill_roles_and_checks(self) -> None:
        report = scan(
            "plan",
            operation="add",
            paths=["external-skills/fixture-skill/SKILL.md"],
            approval_ref="approved-plan",
            run=False,
        )
        self.assertEqual("PASS", report["status"])
        self.assertIn("skill-source", report["roles"]["external-skills/fixture-skill/SKILL.md"])
        self.assertIn("registry", report["required_check_ids"])
        self.assertIn("unit", report["required_check_ids"])

    def test_only_conventional_nested_package_wrappers_skip_route_registration(self) -> None:
        routes = {"research-context-scout/SKILL.md"}
        self.assertTrue(
            _is_registered_package_support(
                "research-context-scout/shared/SKILL.md",
                routes,
            )
        )
        self.assertTrue(
            _is_registered_package_support(
                "research-context-scout/codex/SKILL.md",
                routes,
            )
        )
        self.assertFalse(
            _is_registered_package_support(
                "research-context-scout/experimental/SKILL.md",
                routes,
            )
        )
        self.assertFalse(
            _is_registered_package_support(
                "external-skills/unregistered/shared/SKILL.md",
                routes,
            )
        )

    def test_unknown_contract_check_is_blocking(self) -> None:
        contract = copy.deepcopy(self.contract)
        contract["roles"][0]["checks"].append("run-text-from-repository")
        findings = validate_contract(contract)
        self.assertTrue(any(item["code"] == "CONTRACT_UNKNOWN_CHECK" for item in findings))

    def test_contract_protocol_version_must_match_change_control(self) -> None:
        contract = copy.deepcopy(self.contract)
        contract["protocol_version"] = 999
        findings = validate_contract(contract)
        self.assertTrue(any(item["code"] == "CONTRACT_PROTOCOL_VERSION" for item in findings))

    def test_scope_preserves_unrelated_and_ignores_samples(self) -> None:
        changes = [
            {"status": "M", "path": "scripts/change_guard.py", "source": "unstaged"},
            {"status": "M", "path": ".obsidian/graph.json", "source": "unstaged"},
            {"status": "?", "path": "sample_resources/course.ipynb", "source": "untracked"},
        ]
        scoped, preserved, ignored = split_scope(
            changes,
            ["scripts/change_guard.py"],
            self.contract,
        )
        self.assertEqual(["scripts/change_guard.py"], [item["path"] for item in scoped])
        self.assertEqual([".obsidian/graph.json"], [item["path"] for item in preserved])
        self.assertEqual(["sample_resources/course.ipynb"], [item["path"] for item in ignored])

    def test_user_owned_graph_state_is_preserved_without_explicit_scope(self) -> None:
        changes = [
            {"status": "M", "path": ".obsidian/graph.json", "source": "unstaged"},
        ]
        scoped, preserved, ignored = split_scope(changes, [], self.contract)
        self.assertEqual([], scoped)
        self.assertEqual([".obsidian/graph.json"], [item["path"] for item in preserved])
        self.assertEqual([], ignored)

    def test_git_collector_retains_add_delete_and_rename(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.email", "scan@example.invalid"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "Consistency Scan"], cwd=root, check=True)
            (root / "keep.md").write_text("keep\n", encoding="utf-8")
            (root / "delete.md").write_text("delete\n", encoding="utf-8")
            (root / "rename.md").write_text("rename\n", encoding="utf-8")
            subprocess.run(["git", "add", "."], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "fixture"], cwd=root, check=True)
            (root / "delete.md").unlink()
            (root / "rename.md").rename(root / "renamed.md")
            subprocess.run(["git", "add", "-A"], cwd=root, check=True)
            (root / "new.md").write_text("new\n", encoding="utf-8")
            changes = collect_changes("changed", root=root)
        statuses = {(item["status"], item["path"]) for item in changes}
        self.assertIn(("D", "delete.md"), statuses)
        self.assertIn(("R", "renamed.md"), statuses)
        self.assertIn(("?", "new.md"), statuses)
        self.assertEqual("move", infer_operation(changes))

    def test_ai_packet_is_bounded_and_cannot_override_blocks(self) -> None:
        packet = _ai_review_packet(
            [{"status": "M", "path": "registry/theory.md", "source": "unstaged"}],
            {"registry/theory.md": ["registry-source"]},
            [{"severity": "block", "code": "STALE_GENERATED_MANIFEST", "message": "stale", "paths": []}],
        )
        self.assertIn("untrusted data", packet["trust_boundary"])
        self.assertIn("cannot override", packet["trust_boundary"])
        self.assertEqual(["STALE_GENERATED_MANIFEST"], packet["deterministic_block_codes"])

    def test_generated_writes_require_explicit_approval_reference(self) -> None:
        with self.assertRaises(ScanError):
            apply_generated_outputs(["registry/theory.md"], approval_ref=None)

    def test_classifier_returns_plan_only_without_a_card(self) -> None:
        report = classify_maintenance(["skill-plans/future-scout/plan.md"])
        self.assertEqual("PLAN_ONLY", report["classification"])
        self.assertIsNone(report["protocol_card"])
        self.assertEqual([], report["required_check_ids"])

    def test_classifier_selects_protocol_amendment_for_contract(self) -> None:
        report = classify_maintenance(["protocols/repository/CONTRACT.json"])
        self.assertEqual("GOVERNED_CHANGE", report["classification"])
        self.assertEqual("protocol", report["operation"])
        self.assertEqual(
            "protocols/repository/PROTOCOL_AMENDMENT.md",
            report["protocol_card"],
        )

    def test_baseline_preserves_only_an_identical_existing_failure(self) -> None:
        old = {
            "severity": "block",
            "code": "GRAPH_INVALID",
            "message": "old graph issue",
            "paths": ["old.md"],
        }
        new = {
            "severity": "block",
            "code": "GRAPH_INVALID",
            "message": "new graph issue",
            "paths": ["new.md"],
        }
        classified = apply_baseline(
            [old, new],
            {"findings": [{key: old[key] for key in ("code", "message", "paths")}]},
        )
        self.assertEqual("info", classified[0]["severity"])
        self.assertEqual("block", classified[1]["severity"])

    def test_baseline_cannot_cross_operation_or_scope(self) -> None:
        baseline = {
            "version": 1,
            "protocol_version": self.contract["protocol_version"],
            "operation": "edit",
            "scope": ["registry/theory.md"],
            "findings": [],
            "failed_checks": [],
        }
        with self.assertRaises(ScanError):
            scan(
                "changed",
                operation="update",
                paths=["registry/theory.md"],
                baseline=baseline,
                run=False,
            )

    def test_compact_baseline_keeps_check_failures_only_as_output_hashes(self) -> None:
        report = {
            "protocol_version": self.contract["protocol_version"],
            "operation": "update",
            "scope": ["registry/theory.md"],
            "findings": [
                {
                    "severity": "block",
                    "code": "CHECK_FAILED",
                    "message": "unit failed with exit code 1.",
                    "paths": [],
                }
            ],
            "check_results": [
                {"id": "unit", "status": "fail", "exit_code": 1, "output": "failure A"}
            ],
        }
        baseline = compact_baseline(report)
        self.assertEqual([], baseline["findings"])
        self.assertEqual("unit", baseline["failed_checks"][0]["id"])


if __name__ == "__main__":
    unittest.main()
