#!/usr/bin/env python3

from __future__ import annotations

import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
CLAUDE_ADAPTER = ROOT / "orchestrator" / "adapters" / "claude" / "skills-ai-context.js"
sys.path.insert(0, str(ROOT / "orchestrator" / "tools"))



class ClaudeAdapterTests(unittest.TestCase):



















    @unittest.skipUnless(shutil.which("node"), "Node.js is required")
    def test_claude_adapter_input_wait_is_bounded(self) -> None:
        env = {**os.environ, "SKILLS_AI_ADAPTER_TIMEOUT_MS": "50"}
        process = subprocess.Popen(
            ["node", str(CLAUDE_ADAPTER), "--root", str(ROOT)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
        )
        process.wait(timeout=1)
        stdout = process.stdout.read() if process.stdout else ""
        stderr = process.stderr.read() if process.stderr else ""
        if process.stdin:
            process.stdin.close()
        if process.stdout:
            process.stdout.close()
        if process.stderr:
            process.stderr.close()
        self.assertEqual(0, process.returncode)
        self.assertEqual("", stdout)
        self.assertIn("reason=ADAPTER_INPUT_TIMEOUT", stderr)

    @unittest.skipUnless(shutil.which("node"), "Node.js is required")
    def test_claude_adapter_suppresses_python_child_stderr(self) -> None:
        missing_root = "/tmp/skills-ai-intentionally-missing-root"
        completed = subprocess.run(
            ["node", str(CLAUDE_ADAPTER), "--root", missing_root],
            input=json.dumps({"prompt": "private prompt must not appear"}),
            text=True,
            capture_output=True,
            timeout=2,
            check=False,
        )
        self.assertEqual(0, completed.returncode)
        self.assertEqual("", completed.stdout)
        self.assertIn("reason=ADAPTER_ERROR", completed.stderr)
        self.assertNotIn("can't open file", completed.stderr)
        self.assertNotIn(missing_root, completed.stderr)
        self.assertNotIn("private prompt", completed.stderr)

    @unittest.skipUnless(shutil.which("node"), "Node.js is required")
    def test_claude_adapter_reports_invalid_hook_payload_distinctly(self) -> None:
        completed = subprocess.run(
            ["node", str(CLAUDE_ADAPTER), "--root", str(ROOT)],
            input='{"prompt": "private prompt must not appear"',
            text=True,
            capture_output=True,
            timeout=5,
            check=False,
        )
        self.assertEqual(0, completed.returncode)
        self.assertEqual("", completed.stdout)
        self.assertIn("reason=ADAPTER_INVALID_INPUT", completed.stderr)
        self.assertNotIn("ROUTER_INVALID_OUTPUT", completed.stderr)
        self.assertNotIn("private prompt", completed.stderr)




    @unittest.skipUnless(shutil.which("node"), "Node.js is required")
    def test_claude_adapter_child_budget_shrinks_with_the_run_budget(self) -> None:
        """A small whole-run budget must bound the child, not just host input."""
        env = {
            **os.environ,
            "SKILLS_AI_ADAPTER_TIMEOUT_MS": "400",
            "SKILLS_AI_ROUTER_TIMEOUT_MS": "60000",
        }
        started = time.monotonic()
        completed = subprocess.run(
            ["node", str(CLAUDE_ADAPTER), "--root", str(ROOT)],
            input=json.dumps({"prompt": "What is the capital of France?"}),
            text=True,
            capture_output=True,
            env=env,
            timeout=10,
            check=False,
        )
        elapsed = time.monotonic() - started
        self.assertEqual(0, completed.returncode)
        self.assertLess(elapsed, 2.0)
        if completed.stdout:
            self.assertIn("additionalContext", completed.stdout)
        else:
            self.assertRegex(completed.stderr, r"reason=ADAPTER_(TIMEOUT|DEADLINE_EXCEEDED)")

    @unittest.skipUnless(shutil.which("node"), "Node.js is required")
    def test_claude_adapter_refuses_a_run_with_no_budget_left(self) -> None:
        env = {**os.environ, "SKILLS_AI_ADAPTER_TIMEOUT_MS": "1"}
        completed = subprocess.run(
            ["node", str(CLAUDE_ADAPTER), "--root", str(ROOT)],
            input=json.dumps({"prompt": "Design a dark mode theme switch"}),
            text=True,
            capture_output=True,
            env=env,
            timeout=10,
            check=False,
        )
        self.assertEqual(0, completed.returncode)
        self.assertEqual("", completed.stdout)
        self.assertRegex(completed.stderr, r"reason=ADAPTER_(INPUT_TIMEOUT|DEADLINE_EXCEEDED)")

    @unittest.skipUnless(shutil.which("node"), "Node.js is required")
    @unittest.skipIf(os.name == "nt", "symlink fixture requires POSIX semantics")
    def test_claude_adapter_realpath_guard_blocks_symlink_escape(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            root = base / "root"
            skill_dir = root / "runtime" / "skills-orchestrator"
            outside = base / "outside.md"
            skill_dir.mkdir(parents=True)
            outside.write_text("SAFE_SENTINEL", encoding="utf-8")
            (skill_dir / "SKILL.md").symlink_to(outside)
            decision = {
                "protocol": "skills-ai/2",
                "result": "NORMAL",
                "context": {
                    "operation": "review",
                    "domain": "general",
                    "requested_access": "read-only",
                    "interaction": {"mode": "general", "reason": "test"},
                    "output": {"voice": "compact", "shape": "answer"},
                    "response_contract": [],
                },
                "skill": {"id": "probe", "path": "skills/linked.md"},
            }
            source = (
                "const a=require(process.argv[1]);"
                "const d=JSON.parse(process.argv[2]);"
                "try{a.contextText(d,process.argv[3]);process.stdout.write('read-outside')}"
                "catch(e){process.stdout.write('blocked')}"
            )
            completed = subprocess.run(
                ["node", "-e", source, str(CLAUDE_ADAPTER), json.dumps(decision), str(root)],
                text=True,
                capture_output=True,
                timeout=2,
                check=False,
            )
            self.assertEqual(0, completed.returncode)
            self.assertEqual("blocked", completed.stdout)

    @unittest.skipUnless(shutil.which("node"), "Node.js is required")
    @unittest.skipIf(os.name == "nt", "executable fixture and process probe are POSIX-specific")
    def test_claude_child_timeout_reaps_process(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            fake_python = temp / "slow-python"
            pid_path = temp / "child.pid"
            fake_python.write_text(
                "#!/usr/bin/env python3\n"
                "import os, time\n"
                "open(os.environ['SKILLS_AI_TEST_CHILD_PID'], 'w').write(str(os.getpid()))\n"
                "time.sleep(5)\n",
                encoding="utf-8",
            )
            fake_python.chmod(0o755)
            env = {
                **os.environ,
                "SKILLS_AI_PYTHON": str(fake_python),
                "SKILLS_AI_TEST_CHILD_PID": str(pid_path),
                "SKILLS_AI_ROUTER_TIMEOUT_MS": "500",
                "SKILLS_AI_ADAPTER_TIMEOUT_MS": "1500",
            }
            started = time.monotonic()
            completed = subprocess.run(
                ["node", str(CLAUDE_ADAPTER), "--root", str(ROOT)],
                input=json.dumps({"prompt": "private prompt must not appear"}),
                text=True,
                capture_output=True,
                env=env,
                timeout=2,
                check=False,
            )
            elapsed = time.monotonic() - started
            self.assertEqual(0, completed.returncode)
            self.assertEqual("", completed.stdout)
            self.assertIn("reason=ADAPTER_TIMEOUT", completed.stderr)
            self.assertNotIn("private prompt", completed.stderr)
            self.assertLess(elapsed, 1.5)
            child_pid = int(pid_path.read_text(encoding="utf-8"))
            with self.assertRaises(ProcessLookupError):
                os.kill(child_pid, 0)

    @unittest.skipUnless(shutil.which("node"), "Node.js is required")
    @unittest.skipIf(os.name == "nt", "process groups are POSIX-specific")
    def test_claude_child_timeout_reaps_a_shim_grandchild(self) -> None:
        """An interpreter shim must not leave its real process behind."""
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            shim = temp / "shim-python"
            pid_path = temp / "grandchild.pid"
            inner = temp / "inner.py"
            inner.write_text(
                "import os, sys, time\n"
                "open(sys.argv[1], 'w').write(str(os.getpid()))\n"
                "time.sleep(10)\n",
                encoding="utf-8",
            )
            shim.write_text(
                f'#!/bin/sh\nexec_target="{sys.executable}"\n'
                f'"$exec_target" "{inner}" "{pid_path}" &\nwait\n',
                encoding="utf-8",
            )
            shim.chmod(0o755)
            env = {
                **os.environ,
                "SKILLS_AI_PYTHON": str(shim),
                "SKILLS_AI_ROUTER_TIMEOUT_MS": "700",
                "SKILLS_AI_ADAPTER_TIMEOUT_MS": "2500",
            }
            completed = subprocess.run(
                ["node", str(CLAUDE_ADAPTER), "--root", str(ROOT)],
                input=json.dumps({"prompt": "private prompt must not appear"}),
                text=True,
                capture_output=True,
                env=env,
                timeout=10,
                check=False,
            )
            self.assertEqual(0, completed.returncode)
            self.assertIn("reason=ADAPTER_TIMEOUT", completed.stderr)
            self.assertNotIn("private prompt", completed.stderr)
            grandchild = int(pid_path.read_text(encoding="utf-8"))
            deadline = time.monotonic() + 3
            while time.monotonic() < deadline:
                try:
                    os.kill(grandchild, 0)
                except ProcessLookupError:
                    break
                time.sleep(0.05)
            with self.assertRaises(ProcessLookupError):
                os.kill(grandchild, 0)

    @unittest.skipUnless(shutil.which("node"), "Node.js is required")
    @unittest.skipIf(os.name == "nt", "POSIX signal behavior")
    def test_claude_adapter_reports_host_cancellation(self) -> None:
        env = {**os.environ, "SKILLS_AI_ADAPTER_TIMEOUT_MS": "30000"}
        process = subprocess.Popen(
            ["node", str(CLAUDE_ADAPTER), "--root", str(ROOT)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
        )
        time.sleep(0.3)
        started = time.monotonic()
        process.send_signal(signal.SIGTERM)
        process.wait(timeout=3)
        elapsed = time.monotonic() - started
        stdout = process.stdout.read() if process.stdout else ""
        stderr = process.stderr.read() if process.stderr else ""
        for handle in (process.stdin, process.stdout, process.stderr):
            if handle:
                handle.close()
        self.assertEqual(0, process.returncode)
        self.assertEqual("", stdout)
        self.assertIn("reason=ADAPTER_CANCELLED", stderr)
        self.assertLess(elapsed, 1.0)


if __name__ == "__main__":
    unittest.main()
