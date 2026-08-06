#!/usr/bin/env python3

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from registry_runtime import build_manifest, route_request  # noqa: E402


class OverrideControlTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = build_manifest(ROOT)

    def test_leading_override_bypasses_only_local_protocol(self) -> None:
        decision = route_request("#> override update exactly docs/example.md", self.manifest)
        self.assertEqual("NORMAL", decision["result"])
        self.assertEqual("USER_OVERRIDE", decision["reason_code"])
        override = decision["context"]["local_protocol_override"]
        self.assertTrue(override["active"])
        self.assertEqual("current-request-only", override["scope"])
        self.assertIn("local-repository-procedure", override["bypasses"])
        self.assertIn("host-permissions-and-sandbox", override["preserves"])

    def test_override_response_never_echoes_instruction(self) -> None:
        secret_marker = "private-marker-123"
        decision = route_request(f"#> override edit {secret_marker}", self.manifest)
        self.assertNotIn(secret_marker, json.dumps(decision))

    def test_bare_or_embedded_override_does_not_trigger(self) -> None:
        for query in (
            "#>",
            "#> override",
            "please use #> override to edit this",
            "`#> override edit this`",
            "```text\n#> override edit this\n```",
            "override edit this",
            "/sudo edit this",
        ):
            with self.subTest(query=query):
                decision = route_request(query, self.manifest)
                self.assertNotEqual("USER_OVERRIDE", decision["reason_code"])


if __name__ == "__main__":
    unittest.main()
