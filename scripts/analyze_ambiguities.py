#!/usr/bin/env python3
"""Summarize prompt-free Skills AI ambiguity events without loading user text."""

from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LOG = ROOT / ".runtime" / "ambiguity-events.jsonl"


def load_events(path: Path, *, limit: int) -> tuple[list[dict[str, Any]], int]:
    if limit < 1:
        raise ValueError("limit must be positive")
    try:
        lines = path.read_text(encoding="utf-8").splitlines()[-limit:]
    except FileNotFoundError:
        return [], 0
    events: list[dict[str, Any]] = []
    invalid = 0
    for line in lines:
        try:
            event = json.loads(line)
        except (json.JSONDecodeError, TypeError):
            invalid += 1
            continue
        if not isinstance(event, dict) or not isinstance(event.get("candidates"), list):
            invalid += 1
            continue
        events.append(event)
    return events, invalid


def summarize(events: list[dict[str, Any]], *, invalid: int = 0) -> dict[str, Any]:
    pairs: collections.Counter[str] = collections.Counter()
    clients: collections.Counter[str] = collections.Counter()
    operations: collections.Counter[str] = collections.Counter()
    for event in events:
        candidates = sorted(str(value) for value in event.get("candidates", []) if value)
        if candidates:
            pairs[" <-> ".join(candidates)] += 1
        clients[str(event.get("client", "other"))] += 1
        operations[str(event.get("operation", "unknown"))] += 1
    return {
        "events": len(events),
        "invalid_lines": invalid,
        "candidate_pairs": dict(pairs.most_common()),
        "clients": dict(clients.most_common()),
        "operations": dict(operations.most_common()),
        "privacy": "prompt text, file contents, paths, skill bodies, and answers are not logged",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--log", type=Path, default=DEFAULT_LOG)
    parser.add_argument("--limit", type=int, default=500)
    args = parser.parse_args(argv)
    try:
        events, invalid = load_events(args.log, limit=args.limit)
        print(json.dumps(summarize(events, invalid=invalid), indent=2, sort_keys=True))
        return 0
    except (OSError, ValueError) as exc:
        print(json.dumps({"error": type(exc).__name__}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
