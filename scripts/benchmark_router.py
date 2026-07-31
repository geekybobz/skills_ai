#!/usr/bin/env python3
"""Benchmark deterministic route accuracy, latency, and context size."""

from __future__ import annotations

import argparse
import json
import math
import statistics
import subprocess
import sys
import time
from pathlib import Path

from registry_runtime import ROOT, compact_context, load_manifest, route_request


DEFAULT_CASES = ROOT / "tests" / "router_cases.json"


def percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    index = min(len(ordered) - 1, math.ceil(len(ordered) * fraction) - 1)
    return ordered[index]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES)
    parser.add_argument("--repeat", type=int, default=200)
    parser.add_argument("--process-repeat", type=int, default=5)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    manifest = load_manifest()
    cases = json.loads(args.cases.read_text(encoding="utf-8"))
    failures: list[str] = []
    route_times: list[float] = []
    receipt_tokens: list[int] = []
    selected_skill_tokens: list[int] = []
    process_times: list[float] = []

    for case in cases:
        decision = route_request(case["query"], manifest)
        actual_skill = decision.get("skill", {}).get("id")
        if decision["result"] != case["result"] or actual_skill != case.get("skill"):
            failures.append(
                f"{case['name']}: expected {case['result']}/{case.get('skill')}, "
                f"got {decision['result']}/{actual_skill} ({decision['reason_code']})"
            )
        receipt_tokens.append(math.ceil(len(compact_context(decision).encode("utf-8")) / 4))
        if decision.get("skill"):
            skill_path = ROOT / decision["skill"]["path"]
            selected_skill_tokens.append(math.ceil(skill_path.stat().st_size / 4))

    for _ in range(args.repeat):
        for case in cases:
            started = time.perf_counter_ns()
            route_request(case["query"], manifest)
            route_times.append((time.perf_counter_ns() - started) / 1_000_000)

    process_query = cases[0]["query"]
    for _ in range(args.process_repeat):
        started = time.perf_counter_ns()
        completed = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "route_skill.py")],
            input=json.dumps({"protocol": "skills-ai/1", "client": "benchmark", "query": process_query}) + "\n",
            text=True,
            capture_output=True,
            timeout=3,
            check=False,
        )
        process_times.append((time.perf_counter_ns() - started) / 1_000_000)
        if completed.returncode or not completed.stdout:
            failures.append(f"process API failed: {completed.stderr.strip() or completed.returncode}")

    report = {
        "cases": len(cases),
        "failures": failures,
        "accuracy": (len(cases) - len(failures)) / len(cases),
        "latency_ms": {
            "median": round(statistics.median(route_times), 4),
            "p95": round(percentile(route_times, 0.95), 4),
        },
        "process_latency_ms": {
            "median": round(statistics.median(process_times), 4),
            "p95": round(percentile(process_times, 0.95), 4),
        },
        "compact_receipt_tokens": {
            "median": round(statistics.median(receipt_tokens)),
            "maximum": max(receipt_tokens),
        },
        "shared_entry_tokens": math.ceil((ROOT / "runtime" / "SKILL.md").stat().st_size / 4),
        "selected_skill_tokens": {
            "median": round(statistics.median(selected_skill_tokens)),
            "maximum": max(selected_skill_tokens),
        },
        "repeat": args.repeat,
        "process_repeat": args.process_repeat,
    }
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(
            f"router: {len(cases) - len(failures)}/{len(cases)} cases; "
            f"median {report['latency_ms']['median']:.4f} ms; "
            f"p95 {report['latency_ms']['p95']:.4f} ms; "
            f"process p95 {report['process_latency_ms']['p95']:.4f} ms; "
            f"receipt <= {report['compact_receipt_tokens']['maximum']} estimated tokens; "
            f"selected skill median {report['selected_skill_tokens']['median']} estimated tokens"
        )
        for failure in failures:
            print(f"FAIL: {failure}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
