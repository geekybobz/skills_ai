#!/usr/bin/env python3

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from analyze_ambiguities import load_events, summarize  # noqa: E402


class AmbiguityLogTests(unittest.TestCase):
    def test_summary_uses_only_bounded_metadata(self) -> None:
        events = [
            {
                "client": "codex",
                "candidates": ["debug-helper", "code-explainer"],
                "operation": "explain",
            },
            {
                "client": "claude",
                "candidates": ["code-explainer", "debug-helper"],
                "operation": "explain",
            },
        ]
        result = summarize(events)
        self.assertEqual(2, result["events"])
        self.assertEqual(2, result["candidate_pairs"]["code-explainer <-> debug-helper"])
        self.assertIn("prompt text", result["privacy"])

    def test_loader_ignores_invalid_lines_and_honors_limit(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "events.jsonl"
            path.write_text(
                '{"candidates":["old"]}\nnot-json\n{"candidates":["new"]}\n',
                encoding="utf-8",
            )
            events, invalid = load_events(path, limit=2)
            self.assertEqual([["new"]], [event["candidates"] for event in events])
            self.assertEqual(1, invalid)


if __name__ == "__main__":
    unittest.main()
