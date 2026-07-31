#!/usr/bin/env python3
"""Select one active skill or return NORMAL without blocking the task."""

from __future__ import annotations

import argparse
import json
import sys
import time

from registry_runtime import RegistryRuntimeError, compact_context, load_manifest, route_request


def read_query(argument: str | None) -> str:
    if argument is not None:
        return argument
    payload = sys.stdin.read().strip()
    if not payload:
        raise RegistryRuntimeError("query is required via --query or stdin")
    if payload.startswith("{"):
        data = json.loads(payload)
        payload = data.get("query", "")
    if not isinstance(payload, str) or not payload.strip():
        raise RegistryRuntimeError("query must be a non-empty string")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query", help="request text; stdin is used when omitted")
    parser.add_argument("--compact", action="store_true", help="emit a compact context receipt")
    args = parser.parse_args()
    try:
        query = read_query(args.query)
        manifest = load_manifest()
        started = time.perf_counter_ns()
        decision = route_request(query, manifest)
        decision["router_ms"] = round((time.perf_counter_ns() - started) / 1_000_000, 3)
        if args.compact:
            print(compact_context(decision))
        else:
            print(json.dumps(decision, indent=2, sort_keys=True))
        return 0
    except (json.JSONDecodeError, RegistryRuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
