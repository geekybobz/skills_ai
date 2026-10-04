#!/usr/bin/env python3
"""Focused route, adaptive workflow, and discovery checks for Optimizer."""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "optimizer"
sys.path.insert(0, str(ROOT / "scripts"))

from registry_runtime import build_manifest  # noqa: E402


def load_discovery_helper():
    path = PACKAGE / "scripts" / "optimizer_api.py"
    spec = importlib.util.spec_from_file_location("optimizer_api_under_test", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class OptimizerSkillTests(unittest.TestCase):
    def setUp(self) -> None:
        self.manifest = build_manifest(ROOT)

    def read(self, relative: str) -> str:
        return (PACKAGE / relative).read_text(encoding="utf-8")



    def test_claude_wrapper_states_tool_and_lifecycle_boundaries(self) -> None:
        entry = self.read("SKILL.md")
        wrapper = " ".join(self.read("claude/CLAUDE.md").split())
        self.assertIn("claude/CLAUDE.md", entry)
        self.assertIn("injected `command=` and `mode=` lines", wrapper)
        self.assertIn("no injected line is present", wrapper)
        self.assertIn("optimizer_api.py", wrapper)
        self.assertIn("wait for approval", wrapper)
        self.assertIn("never touch the optimizer library itself", wrapper)
        self.assertIn("untrusted data", wrapper)
        self.assertIn("subagent", wrapper)
        self.assertIn("not certified", wrapper)

    def test_codex_wrapper_states_tool_and_lifecycle_boundaries(self) -> None:
        entry = self.read("SKILL.md")
        wrapper = " ".join(self.read("codex/CODEX.md").split())
        self.assertIn("codex/CODEX.md", entry)
        self.assertIn("context.skill_invocation.command", wrapper)
        self.assertIn("optimizer_api.py", wrapper)
        self.assertIn("apply_patch", wrapper)
        self.assertIn("never a project system or numerical run", wrapper)
        self.assertIn("optimizer library itself", wrapper)
        self.assertIn("untrusted data", wrapper)
        self.assertIn("Claude acceptance", wrapper)

    def test_wrapper_adds_platform_facts_without_restating_shared_rules(self) -> None:
        wrapper = " ".join(self.read("claude/CLAUDE.md").split())
        for owned_elsewhere in (
            "parameter continuation",
            "Fourier",
            "fingerprint",
            "analytical gradient",
            "global optimum",
        ):
            with self.subTest(rule=owned_elsewhere):
                self.assertNotIn(owned_elsewhere, wrapper)

    def test_entry_stays_compact_and_resolves_through_one_helper(self) -> None:
        entry = self.read("SKILL.md")
        # The Claude hook injects this body verbatim on every optimizer request.
        self.assertLess((PACKAGE / "SKILL.md").stat().st_size, 3500)
        self.assertLess((PACKAGE / "claude" / "CLAUDE.md").stat().st_size, 2500)
        # The resolver path has one home, in the discovery helper.
        self.assertNotIn("optimizer_registry.py", entry)
        self.assertIn("optimizer_registry.py", self.read("scripts/optimizer_api.py"))
        for operation in ("status", "catalog", "explore", "intervene", "continue", "branch"):
            with self.subTest(operation=operation):
                self.assertIn(f"#> optimizer {operation}", entry)

    def test_workflows_are_adaptive_and_keep_problem_boundaries(self) -> None:
        entry = (PACKAGE / "SKILL.md").read_text(encoding="utf-8")
        build = (PACKAGE / "build-system.md").read_text(encoding="utf-8")
        optimize = (PACKAGE / "optimize.md").read_text(encoding="utf-8")
        situation = (PACKAGE / "situation-analysis.md").read_text(encoding="utf-8")
        self.assertIn("never hard-code a stable version or environment", entry)
        self.assertIn("#> optimizer explore", entry)
        self.assertIn("#> optimizer intervene", entry)
        self.assertIn("#> optimizer continue", entry)
        self.assertIn("#> optimizer branch", entry)
        self.assertIn("Stop for review", build)
        self.assertIn("adaptive loop", optimize)
        self.assertIn("not a fixed recipe or a default method tournament", optimize)
        self.assertIn("new problem", optimize)
        self.assertIn("never called continuation", optimize)
        self.assertIn("Fourier family", optimize)
        self.assertIn("never become a competing numerical history", optimize)
        self.assertIn("Do not trigger numerical work\nwhile reading reports", situation)
        self.assertIn("new-problem branch", situation)
        self.assertIn("self-modifying", situation)
        # The identity contract has one home; situation analysis points at it.
        self.assertIn("problem-identity table in `optimize.md`", situation)
        self.assertNotIn("with_secondary", situation)

    def test_execution_integrity_gate_precedes_strategy_changes(self) -> None:
        optimize = self.read("optimize.md")
        situation = self.read("situation-analysis.md")
        build = self.read("build-system.md")

        # The gate is an ordered recovery contract: preserve evidence, reduce
        # to a deterministic reproduction, distinguish likely causes, and do
        # not silently alter the scientific problem to make an error disappear.
        for required in (
            "Freeze the current problem identity",
            "Reproduce the smallest deterministic case",
            "route/import, static\n   contract, finite/shape, exact replay, directional gradient",
            "environment/setup, API/shape, numerical\n   implementation, derivative, modelling/assumption, or unresolved anomaly",
            "Do not change physics, controls, objective, or optimizer settings as a\n\"fix\" before classification",
            "Require approval for a code edit",
            "new validation boundary",
        ):
            with self.subTest(required=required):
                self.assertIn(required, optimize)
        self.assertIn("execution-integrity gate before", optimize)
        self.assertIn("execution failure or suspicious result", situation)
        self.assertIn("instead of an optimizer intervention", situation)
        self.assertIn("before presenting the system as optimization-ready", build)

    def test_discovery_helper_uses_the_resolved_environment_and_exposes_contract(self) -> None:
        helper = load_discovery_helper()
        route = {"environment": "optimizer_v4"}
        completed = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout=json.dumps({"required_hooks": ["system_spec"]}),
        )
        with patch.object(helper.subprocess, "run", return_value=completed) as run:
            payload = helper.live_payload(route, "contract", None)
        self.assertEqual(["system_spec"], payload["payload"]["required_hooks"])
        args = run.call_args.args[0]
        self.assertEqual(["conda", "run", "--no-capture-output", "-n", "optimizer_v4", "python", "-c"], args[:7])
        self.assertEqual("contract", args[-1])
        self.assertIn("opt.contract_info()", args[7])

    @unittest.skipUnless(os.environ.get("OPTIMIZER_SKILL_LIVE") == "1", "set OPTIMIZER_SKILL_LIVE=1 for live optimizer acceptance")
    def test_live_discovery_acceptance(self) -> None:
        script = PACKAGE / "scripts" / "optimizer_api.py"
        for command in ("status", "contract", "campaigns", "tracker", "methods"):
            with self.subTest(command=command):
                completed = subprocess.run(
                    [sys.executable, str(script), command],
                    text=True,
                    capture_output=True,
                    check=True,
                )
                payload = json.loads(completed.stdout)
                self.assertTrue(payload["route"]["environment"])
                self.assertIsInstance(payload["payload"], dict)

    def test_retained_session_helper_records_decisions_without_numerical_dependencies(self) -> None:
        script = PACKAGE / "scripts" / "optimizer_session.py"
        with tempfile.TemporaryDirectory() as directory:
            session = Path(directory) / "optimization-session.json"
            initial = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "init",
                    str(session),
                    "--optimizer-version",
                    "v4.0.1",
                    "--optimizer-root",
                    "/tmp/optimizer-v4",
                    "--system-target",
                    "system.py",
                    "--chunks",
                    "3",
                    "--iterations",
                    "5",
                ],
                text=True,
                capture_output=True,
                check=True,
            )
            self.assertEqual("optimizer.session.v1", json.loads(initial.stdout)["schema"])
            subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "record",
                    str(session),
                    "--stage",
                    "scout",
                    "--method",
                    "adam",
                    "--metrics-json",
                    '{"J": 0.2}',
                ],
                text=True,
                capture_output=True,
                check=True,
            )
            updated = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "next",
                    str(session),
                    "--code",
                    "switch-to-lbfgs",
                    "--reason",
                    "stable plateau",
                ],
                text=True,
                capture_output=True,
                check=True,
            )
        payload = json.loads(updated.stdout)
        self.assertEqual(2, payload["revision"])
        self.assertEqual(0.2, payload["best_result"]["value"])
        self.assertEqual("switch-to-lbfgs", payload["next_action"]["code"])

    def test_package_stays_manual(self) -> None:
        config = (PACKAGE / "agents" / "openai.yaml").read_text(encoding="utf-8")
        self.assertIn("allow_implicit_invocation: false", config)


if __name__ == "__main__":
    unittest.main()
