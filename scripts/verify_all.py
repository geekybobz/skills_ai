#!/usr/bin/env python3
"""Run every package's own checks, then the parent gates, once and on demand.

Nothing here runs in the background or changes a file; each step is an existing
check that can also be run alone. The parent needs Python 3.11 or newer.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STEP_TIMEOUT_SECONDS = 900
MINIMUM_PYTHON = (3, 11)
FIX = "git submodule update --init --recursive"
PARENT_GATES = (
    ("full consistency scan", ("scripts/scan_consistency.py", "full")),
    ("generated registry", ("scripts/compile_registry.py", "--check")),
    ("generated views", ("scripts/compile_repository_views.py", "--check")),
    ("graph layers", ("scripts/graph_layers.py", "--check")),
    ("human guide", ("scripts/human_docs_guard.py", "--check")),
    ("registry validation", ("scripts/validate_registry.py",)),
    ("activation register", ("scripts/toggle_registry.py", "--check")),
    ("delivery budgets", ("scripts/measure_context.py",)),
)


@dataclass(frozen=True)
class Step:
    name: str
    cwd: Path
    argv: tuple[str, ...]


def declared_packages(root: Path) -> list[str]:
    """Package paths from .gitmodules, in declaration order."""
    try:
        text = (root / ".gitmodules").read_text(encoding="utf-8")
    except OSError:
        return []
    return re.findall(r"^\s*path\s*=\s*(\S+)\s*$", text, re.MULTILINE)


def empty_packages(root: Path) -> list[str]:
    """Declared package folders that hold nothing but an optional .git link."""
    found = []
    for package in declared_packages(root):
        folder = root / package
        try:
            names = [name for name in folder.iterdir() if name.name != ".git"]
        except OSError:
            names = []
        if not names:
            found.append(package)
    return found


def package_step(root: Path, package: str) -> Step | None:
    """The package's own verification: verify_package.py when it has one, else its unittest suite."""
    folder = root / package
    if (folder / "scripts" / "verify_package.py").is_file():
        return Step(f"package {package}", folder, (sys.executable, "-B", "scripts/verify_package.py"))
    if (folder / "tests").is_dir():
        return Step(f"package {package}", folder, (sys.executable, "-B", "-m", "unittest", "discover", "-s", "tests"))
    return None


def build_steps(root: Path) -> tuple[list[Step], list[str]]:
    """Runnable steps in order, plus the packages that offer no checks of their own."""
    steps, unchecked = [], []
    for package in declared_packages(root):
        step = package_step(root, package)
        if step is None:
            unchecked.append(package)
        else:
            steps.append(step)
    steps.extend(Step(name, root, (sys.executable, "-B", *args)) for name, args in PARENT_GATES)
    return steps, unchecked


def run_step(step: Step, timeout: int = STEP_TIMEOUT_SECONDS) -> dict:
    started = time.monotonic()
    try:
        done = subprocess.run(step.argv, cwd=step.cwd, capture_output=True, text=True, timeout=timeout, stdin=subprocess.DEVNULL)
        code, output = done.returncode, (done.stdout + done.stderr)
    except subprocess.TimeoutExpired:
        code, output = 124, f"timed out after {timeout} seconds"
    except OSError as exc:
        code, output = 127, str(exc)
    return {
        "name": step.name,
        "status": "pass" if code == 0 else "fail",
        "exit_code": code,
        "seconds": round(time.monotonic() - started, 1),
        "tail": [] if code == 0 else output.strip().splitlines()[-12:],
    }


def main(argv: list[str] | None = None, root: Path = ROOT) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--list", action="store_true", help="show the steps without running them")
    parser.add_argument("--only", action="append", default=[], metavar="TEXT", help="run only steps whose name contains TEXT")
    parser.add_argument("--fail-fast", action="store_true", help="stop at the first failing step")
    parser.add_argument("--json", action="store_true", help="print one JSON report instead of text")
    args = parser.parse_args(argv)

    if sys.version_info < MINIMUM_PYTHON:
        print(f"error: the parent needs Python {MINIMUM_PYTHON[0]}.{MINIMUM_PYTHON[1]} or newer; "
              "the packages alone support 3.10")
        return 2
    empty = empty_packages(root)
    if empty:
        print(f"error: these package folders are empty: {', '.join(empty)}; run {FIX}")
        return 2

    steps, unchecked = build_steps(root)
    if args.only:
        steps = [step for step in steps if any(text in step.name for text in args.only)]
    if args.list:
        for step in steps:
            print(f"{step.name}: {' '.join(step.argv[1:])} (in {step.cwd.relative_to(root) if step.cwd != root else '.'})")
        for package in unchecked:
            print(f"package {package}: no verification script or tests")
        return 0

    results = []
    for step in steps:
        result = run_step(step)
        results.append(result)
        if not args.json:
            print(f"{result['status'].upper():5s} {result['name']:32s} ({result['seconds']} s)", flush=True)
            for line in result["tail"]:
                print(f"      {line}")
        if args.fail_fast and result["status"] == "fail":
            break
    failed = [r for r in results if r["status"] == "fail"]
    summary = {"passed": len(results) - len(failed), "failed": len(failed), "no_checks": unchecked}
    if args.json:
        print(json.dumps({"schema": "skills-ai/verify-all/1", "results": results, **summary}, indent=2))
    else:
        for package in unchecked:
            print(f"NOTE  package {package} has no verification script or tests")
        print(f"verify-all: {summary['passed']} passed, {summary['failed']} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
