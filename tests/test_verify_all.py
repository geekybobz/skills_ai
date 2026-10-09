"""verify_all orders each package's own checks before the parent gates; these tests never run the real gates."""

from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import verify_all  # noqa: E402

GITMODULES = "".join(
    f'[submodule "{name}"]\n\tpath = {name}\n\turl = https://example.invalid/{name}.git\n'
    for name in ("pkg-verify", "pkg-tests", "pkg-bare")
)
TRIVIAL_GATES = (("ok gate", ("-c", "print('fine')")), ("bad gate", ("-c", "print('boom'); raise SystemExit(4)")))


def run_main(arguments: list[str], root: Path) -> tuple[int, str]:
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        code = verify_all.main(arguments, root=root)
    return code, output.getvalue()


class VerifyAllTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        (self.root / ".gitmodules").write_text(GITMODULES, encoding="utf-8")
        verify = self.root / "pkg-verify" / "scripts"
        verify.mkdir(parents=True)
        (verify / "verify_package.py").write_text("print('package verified')\n", encoding="utf-8")
        tests = self.root / "pkg-tests" / "tests"
        tests.mkdir(parents=True)
        (tests / "test_ok.py").write_text(
            "import unittest\n\n\nclass T(unittest.TestCase):\n    def test_ok(self):\n        self.assertTrue(True)\n",
            encoding="utf-8",
        )
        (self.root / "pkg-bare").mkdir()
        (self.root / "pkg-bare" / "README.md").write_text("no checks here\n", encoding="utf-8")

    def test_packages_follow_gitmodules_order_and_the_bare_one_is_noted(self) -> None:
        self.assertEqual(["pkg-verify", "pkg-tests", "pkg-bare"], verify_all.declared_packages(self.root))
        steps, unchecked = verify_all.build_steps(self.root)
        names = [step.name for step in steps]
        self.assertEqual(["package pkg-verify", "package pkg-tests"], names[:2])
        self.assertEqual(["pkg-bare"], unchecked)
        self.assertEqual("scripts/verify_package.py", steps[0].argv[-1])
        self.assertEqual(("-m", "unittest", "discover", "-s", "tests"), steps[1].argv[-5:])
        self.assertEqual(self.root / "pkg-tests", steps[1].cwd)

    def test_parent_gates_are_the_documented_set_and_all_exist(self) -> None:
        self.assertEqual(
            [
                "full consistency scan",
                "generated registry",
                "generated views",
                "graph layers",
                "human guide",
                "registry validation",
                "activation register",
                "delivery budgets",
            ],
            [name for name, _ in verify_all.PARENT_GATES],
        )
        for name, args in verify_all.PARENT_GATES:
            with self.subTest(gate=name):
                self.assertTrue((ROOT / args[0]).is_file(), args[0])

    def test_run_step_reports_pass_fail_and_timeout(self) -> None:
        python = sys.executable
        ok = verify_all.run_step(verify_all.Step("ok", self.root, (python, "-c", "print(1)")))
        self.assertEqual(("pass", 0, []), (ok["status"], ok["exit_code"], ok["tail"]))
        bad = verify_all.run_step(verify_all.Step("bad", self.root, (python, "-c", "print('boom'); raise SystemExit(3)")))
        self.assertEqual(("fail", 3), (bad["status"], bad["exit_code"]))
        self.assertIn("boom", bad["tail"])
        slow = verify_all.run_step(verify_all.Step("slow", self.root, (python, "-c", "import time; time.sleep(5)")), timeout=1)
        self.assertEqual(("fail", 124), (slow["status"], slow["exit_code"]))

    def test_list_shows_the_steps_without_running_any(self) -> None:
        with patch.object(verify_all, "run_step", side_effect=AssertionError("must not run")):
            code, text = run_main(["--list"], self.root)
        self.assertEqual(0, code)
        self.assertIn("package pkg-verify", text)
        self.assertIn("full consistency scan", text)
        self.assertIn("package pkg-bare: no verification script or tests", text)

    def test_a_failing_step_fails_the_run_and_fail_fast_stops_at_it(self) -> None:
        with patch.object(verify_all, "PARENT_GATES", TRIVIAL_GATES):
            code, text = run_main([], self.root)
            self.assertEqual(1, code)
            self.assertIn("PASS  package pkg-verify", text)
            self.assertIn("FAIL  bad gate", text)
            self.assertIn("boom", text)
            self.assertIn("verify-all: 3 passed, 1 failed", text)
            code, text = run_main(["--fail-fast", "--only", "gate"], self.root)
            self.assertEqual(1, code)
            self.assertNotIn("package pkg-verify", text)
            self.assertIn("verify-all: 1 passed, 1 failed", text)

    def test_json_report_has_a_schema_and_the_unchecked_packages(self) -> None:
        with patch.object(verify_all, "PARENT_GATES", TRIVIAL_GATES[:1]):
            code, text = run_main(["--json"], self.root)
        report = json.loads(text)
        self.assertEqual(0, code)
        self.assertEqual("skills-ai/verify-all/1", report["schema"])
        self.assertEqual(["pkg-bare"], report["no_checks"])
        self.assertEqual([("pass",)] * 3, [(r["status"],) for r in report["results"]])

    def test_empty_package_folder_stops_before_any_step_with_the_fix(self) -> None:
        for child in (self.root / "pkg-tests").rglob("*"):
            if child.is_file():
                child.unlink()
        for folder in sorted((self.root / "pkg-tests").rglob("*"), reverse=True):
            folder.rmdir()
        with patch.object(verify_all, "run_step", side_effect=AssertionError("must not run")):
            code, text = run_main([], self.root)
        self.assertEqual(2, code)
        self.assertIn("pkg-tests", text)
        self.assertIn("git submodule update --init --recursive", text)

    def test_old_python_is_refused_before_anything_runs(self) -> None:
        with patch.object(verify_all.sys, "version_info", (3, 10, 0)):
            with patch.object(verify_all, "run_step", side_effect=AssertionError("must not run")):
                code, text = run_main([], self.root)
        self.assertEqual(2, code)
        self.assertIn("Python 3.11", text)


class RepositoryWiringTests(unittest.TestCase):
    def test_ci_runs_verify_all_on_the_pythons_the_parent_supports(self) -> None:
        workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
        self.assertIn("scripts/verify_all.py", workflow)
        self.assertIn("submodules: recursive", workflow)
        self.assertIn('["3.11", "3.13"]', workflow)

    def test_workspace_file_lists_the_parent_and_every_declared_package(self) -> None:
        workspace = json.loads((ROOT / "skills_ai.code-workspace").read_text(encoding="utf-8"))
        folders = [folder["path"] for folder in workspace["folders"]]
        self.assertEqual(["."], folders[:1])
        self.assertEqual(sorted(verify_all.declared_packages(ROOT)), sorted(folders[1:]))
        self.assertFalse(workspace["settings"]["git.detectSubmodules"])


if __name__ == "__main__":
    unittest.main()
