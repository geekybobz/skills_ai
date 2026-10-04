#!/usr/bin/env python3

from __future__ import annotations

import datetime as dt
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from create_change_request import ChangeRequestError, create_change_request  # noqa: E402


class ChangeRequestTests(unittest.TestCase):
    def payload(self) -> dict:
        return {
            "title": "Qualify a router trigger",
            "original_request": "Please fix the ambiguous trigger.",
            "problem": "An ordinary sentence selects the wrong skill.",
            "desired_behavior": "Qualified technical prompts match; ordinary prose falls back.",
            "targets": ["registry/theory.md", "tests/model_orchestration_cases.json"],
            "evidence": ["A negative routing fixture reproduces the mismatch."],
            "risks": ["Over-qualification may reduce recall."],
            "rollback": ["Revert the focused registry commit."],
            "tests": ["Run the benchmark fixture."],
            "acceptance": ["Both positive and negative cases pass."],
            "client": "codex",
            "approval_ref": "user-turn-7",
        }

    def test_creates_one_detailed_pending_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = create_change_request(
                self.payload(),
                root=root,
                now=dt.datetime(2026, 7, 31, 12, 0, tzinfo=dt.timezone.utc),
                token="abcd1234",
            )
            path = Path(result["request_path"])
            self.assertTrue(path.is_file())
            self.assertEqual((root / "requests" / "pending").resolve(), path.parent)
            self.assertEqual(1, len(list(path.parent.glob("*.md"))))
            content = path.read_text(encoding="utf-8")
            self.assertIn('id: "SCR-20260731-120000-abcd1234"', content)
            self.assertIn("## Original user request", content)
            self.assertIn("`registry/theory.md`", content)
            self.assertIn("## Maintenance handoff", content)
            self.assertIn("Commit: pending", content)
            self.assertIn(str(root), result["handoff_prompt"])

    def test_refuses_target_outside_repository(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            payload = self.payload()
            payload["targets"] = ["../outside.md"]
            with self.assertRaises(ChangeRequestError):
                create_change_request(payload, root=Path(directory), token="abcd1234")

    def test_refuses_git_internal_target(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            payload = self.payload()
            payload["targets"] = [".git/config"]
            with self.assertRaises(ChangeRequestError):
                create_change_request(payload, root=Path(directory), token="abcd1234")

    def test_refuses_multiline_title(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            payload = self.payload()
            payload["title"] = "unsafe\nheading"
            with self.assertRaises(ChangeRequestError):
                create_change_request(payload, root=Path(directory), token="abcd1234")

    def test_refuses_oversized_request_packet(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            payload = self.payload()
            payload["original_request"] = "x" * 70_000
            with self.assertRaises(ChangeRequestError):
                create_change_request(payload, root=Path(directory), token="abcd1234")

    def test_stdin_json_cli_writes_only_to_configured_repository(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = (
                "import json,sys;"
                f"sys.path.insert(0,{str(ROOT / 'scripts')!r});"
                "from create_change_request import create_change_request;"
                f"print(json.dumps(create_change_request(json.load(sys.stdin),root=__import__('pathlib').Path({directory!r}),token='abcd1234')))"
            )
            completed = subprocess.run(
                [sys.executable, "-c", source],
                input=json.dumps(self.payload()),
                text=True,
                capture_output=True,
                timeout=2,
                check=False,
            )
            self.assertEqual(0, completed.returncode, completed.stderr)
            result = json.loads(completed.stdout)
            expected_root = (Path(directory) / "requests" / "pending").resolve()
            self.assertTrue(Path(result["request_path"]).is_relative_to(expected_root))


if __name__ == "__main__":
    unittest.main()
