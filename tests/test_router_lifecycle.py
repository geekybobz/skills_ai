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


ROOT = Path(__file__).resolve().parents[1]
ROUTER = ROOT / "scripts" / "route_skill.py"
CLAUDE_ADAPTER = ROOT / "adapters" / "claude" / "skills-ai-router.js"


class RouterLifecycleTests(unittest.TestCase):
    def router_process(self, *args: str) -> subprocess.Popen[str]:
        return subprocess.Popen(
            [sys.executable, str(ROUTER), *args],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

    def read_completed(self, process: subprocess.Popen[str]) -> tuple[dict, str]:
        process.wait(timeout=2)
        stdout = process.stdout.read() if process.stdout else ""
        stderr = process.stderr.read() if process.stderr else ""
        if process.stdin:
            try:
                process.stdin.close()
            except BrokenPipeError:
                pass
        if process.stdout:
            process.stdout.close()
        if process.stderr:
            process.stderr.close()
        return json.loads(stdout), stderr

    def test_json_line_exits_while_stdin_remains_open(self) -> None:
        process = self.router_process("--stdin-timeout-ms", "500")
        self.assertIsNotNone(process.stdin)
        process.stdin.write(json.dumps({"protocol": "skills-ai/1", "query": "What is the capital of France?"}) + "\n")
        process.stdin.flush()
        decision, _ = self.read_completed(process)
        self.assertEqual(0, process.returncode)
        self.assertEqual("NORMAL", decision["result"])
        self.assertEqual("NO_SKILL_MATCH", decision["reason_code"])

    @unittest.skipIf(os.name == "nt", "PTY behavior is POSIX-specific")
    def test_json_line_exits_in_pty_without_eof(self) -> None:
        import pty

        master, slave = pty.openpty()
        process = subprocess.Popen(
            [sys.executable, str(ROUTER), "--stdin-timeout-ms", "500"],
            stdin=slave,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=False,
            close_fds=True,
        )
        os.close(slave)
        try:
            os.write(master, json.dumps({"protocol": "skills-ai/1", "query": "What time is it?"}).encode() + b"\n")
            process.wait(timeout=1)
            stdout = process.stdout.read() if process.stdout else b""
            self.assertEqual(0, process.returncode)
            self.assertEqual("NORMAL", json.loads(stdout)["result"])
        finally:
            os.close(master)
            for handle in (process.stdout, process.stderr):
                if handle:
                    handle.close()
            if process.poll() is None:
                process.terminate()
                process.wait(timeout=1)

    def test_missing_input_self_times_out_fail_open(self) -> None:
        process = self.router_process("--stdin-timeout-ms", "50")
        decision, stderr = self.read_completed(process)
        self.assertEqual(0, process.returncode)
        self.assertEqual("INPUT_TIMEOUT", decision["reason_code"])
        self.assertIn("reason=INPUT_TIMEOUT", stderr)

    def test_partial_line_without_newline_self_times_out(self) -> None:
        process = self.router_process("--stdin-timeout-ms", "50")
        self.assertIsNotNone(process.stdin)
        process.stdin.write('{"query":"partial"}')
        process.stdin.flush()
        decision, stderr = self.read_completed(process)
        self.assertEqual(0, process.returncode)
        self.assertEqual("INPUT_TIMEOUT", decision["reason_code"])
        self.assertIn("reason=INPUT_TIMEOUT", stderr)

    def test_malformed_json_is_structured_fail_open(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(ROUTER)],
            input="{bad json}\n",
            text=True,
            capture_output=True,
            timeout=2,
            check=False,
        )
        self.assertEqual(0, completed.returncode)
        decision = json.loads(completed.stdout)
        self.assertEqual("NORMAL", decision["result"])
        self.assertEqual("INVALID_INPUT", decision["reason_code"])
        self.assertNotIn("bad json", completed.stderr)

    def test_json_array_is_not_routed_as_raw_text(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(ROUTER)],
            input='["secret"]\n',
            text=True,
            capture_output=True,
            timeout=2,
            check=False,
        )
        decision = json.loads(completed.stdout)
        self.assertEqual(0, completed.returncode)
        self.assertEqual("NORMAL", decision["result"])
        self.assertEqual("INVALID_INPUT", decision["reason_code"])
        self.assertNotIn("secret", completed.stderr)

    def test_strict_mode_returns_nonzero_after_receipt(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(ROUTER), "--strict"],
            input="{}\n",
            text=True,
            capture_output=True,
            timeout=2,
            check=False,
        )
        self.assertEqual(2, completed.returncode)
        self.assertEqual("INVALID_INPUT", json.loads(completed.stdout)["reason_code"])

    def test_request_size_is_bounded(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(ROUTER), "--max-request-bytes", "32"],
            input=json.dumps({"query": "x" * 100}) + "\n",
            text=True,
            capture_output=True,
            timeout=2,
            check=False,
        )
        self.assertEqual("REQUEST_TOO_LARGE", json.loads(completed.stdout)["reason_code"])

    def test_missing_manifest_is_structured_fail_open(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(ROUTER), "--manifest", "/tmp/skills-ai-missing-manifest.json"],
            input=json.dumps({"request_id": "test-1", "query": "Explain this"}) + "\n",
            text=True,
            capture_output=True,
            timeout=2,
            check=False,
        )
        decision = json.loads(completed.stdout)
        self.assertEqual("MANIFEST_UNAVAILABLE", decision["reason_code"])
        self.assertEqual("test-1", decision["request_id"])

    def test_selected_skill_cannot_escape_repository(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            manifest_path = Path(directory) / "manifest.json"
            manifest = json.loads((ROOT / "runtime" / "router-manifest.json").read_text(encoding="utf-8"))
            selected = next(route for route in manifest["routes"] if route["state"] == "active")
            selected["id"] = "escape-probe"
            selected["path"] = "/etc/hosts"
            selected["triggers"] = ["escape probe"]
            selected["family_triggers"] = []
            manifest["routes"] = [selected]
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, str(ROUTER), "--manifest", str(manifest_path)],
                input=json.dumps({"query": "escape probe"}) + "\n",
                text=True,
                capture_output=True,
                timeout=2,
                check=False,
            )
            decision = json.loads(completed.stdout)
            self.assertEqual("NORMAL", decision["result"])
            self.assertEqual("SELECTED_SKILL_UNAVAILABLE", decision["reason_code"])

    @unittest.skipIf(os.name == "nt", "POSIX signal behavior")
    def test_sigterm_ends_waiting_router(self) -> None:
        process = self.router_process("--stdin-timeout-ms", "5000")
        started = time.monotonic()
        process.send_signal(signal.SIGTERM)
        process.wait(timeout=1)
        self.assertLess(time.monotonic() - started, 0.75)
        self.assertIsNotNone(process.returncode)
        for handle in (process.stdin, process.stdout, process.stderr):
            if handle:
                handle.close()

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
    def test_claude_adapter_context_header_uses_one_line_per_key(self) -> None:
        completed = subprocess.run(
            ["node", str(CLAUDE_ADAPTER), "--root", str(ROOT)],
            input=json.dumps({"prompt": "Design a dark mode theme switch"}),
            text=True,
            capture_output=True,
            timeout=5,
            check=False,
        )
        self.assertEqual(0, completed.returncode)
        context = json.loads(completed.stdout)["hookSpecificOutput"]["additionalContext"]
        header, _, remainder = context.partition("\nSelected local skill: ")
        self.assertTrue(remainder, "a MATCH must inject exactly one selected skill")
        self.assertEqual([], [line for line in header.splitlines() if not line.strip()])
        self.assertTrue(header.startswith("Skills AI shared response context:\noperation="))
        self.assertTrue(remainder.startswith("dark-mode-specialist\n\n"))

    @unittest.skipUnless(shutil.which("node"), "Node.js is required")
    @unittest.skipIf(os.name == "nt", "symlink fixture requires POSIX semantics")
    def test_claude_adapter_realpath_guard_blocks_symlink_escape(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            root = base / "root"
            skill_dir = root / "skills"
            outside = base / "outside.md"
            skill_dir.mkdir(parents=True)
            outside.write_text("SAFE_SENTINEL", encoding="utf-8")
            (skill_dir / "linked.md").symlink_to(outside)
            decision = {
                "result": "MATCH",
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


if __name__ == "__main__":
    unittest.main()
