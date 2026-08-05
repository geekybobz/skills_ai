#!/usr/bin/env python3

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from registry_runtime import build_manifest, route_request  # noqa: E402


class SudoControlTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = build_manifest(ROOT)

    def test_leading_sudo_bypasses_only_local_protocol(self) -> None:
        decision = route_request("/sudo update exactly docs/example.md", self.manifest)
        self.assertEqual("NORMAL", decision["result"])
        self.assertEqual("USER_SUDO", decision["reason_code"])
        override = decision["context"]["local_protocol_override"]
        self.assertTrue(override["active"])
        self.assertEqual("current-request-only", override["scope"])
        self.assertIn("local-repository-procedure", override["bypasses"])
        self.assertIn("host-permissions-and-sandbox", override["preserves"])

    def test_sudo_response_never_echoes_instruction(self) -> None:
        secret_marker = "private-marker-123"
        decision = route_request(f"/sudo edit {secret_marker}", self.manifest)
        self.assertNotIn(secret_marker, json.dumps(decision))

    def test_bare_or_embedded_sudo_does_not_trigger(self) -> None:
        for query in (
            "/sudo",
            "please use /sudo to edit this",
            "`/sudo edit this`",
            "```text\n/sudo edit this\n```",
            "sudo edit this",
        ):
            with self.subTest(query=query):
                decision = route_request(query, self.manifest)
                self.assertNotEqual("USER_SUDO", decision["reason_code"])


if __name__ == "__main__":
    unittest.main()
