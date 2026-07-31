#!/usr/bin/env python3
"""Classify Skills AI repository changes without granting write authority."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
OPERATIONS = {
    "add",
    "edit",
    "update",
    "move",
    "deprecate",
    "delete",
    "install",
    "scope",
    "protocol",
    "request",
}
APPROVAL_OPERATIONS = {"move", "deprecate", "delete", "install", "scope", "protocol"}
PROTECTED_PREFIXES = ("design-with-claude/", "caveman/", "theory-reference/")
GENERATED_PATHS = {"runtime/router-manifest.json"}
REQUEST_INBOX = "requests/pending"


class GuardError(RuntimeError):
    pass


def _relative_path(raw: str, root: Path) -> tuple[str, bool]:
    candidate = Path(raw)
    absolute = candidate.resolve(strict=False) if candidate.is_absolute() else (root / candidate).resolve(strict=False)
    try:
        relative = absolute.relative_to(root.resolve()).as_posix()
        return relative or ".", False
    except ValueError:
        return str(absolute), True


def _covered(path: str, allowed: Iterable[str]) -> bool:
    for item in allowed:
        prefix = item.rstrip("/")
        if path == prefix or path.startswith(prefix + "/"):
            return True
    return False


def required_checks(paths: Iterable[str]) -> list[str]:
    checks = {
        "git diff --check",
        "focused tests for changed behavior",
        "python3 scripts/human_docs_guard.py --check",
    }
    for path in paths:
        if path.endswith(".md") or path in {".obsidian/graph.json", "scripts/graph_layers.py"}:
            checks.add("python3 scripts/graph_layers.py --check")
        if path == "registry/activation.md" or path.startswith("registry/") or path in {
            "docs/00_SKILLS_HUB.md",
            "runtime/profile.json",
        }:
            checks.update(
                {
                    "python3 scripts/compile_registry.py --check",
                    "python3 scripts/validate_registry.py",
                    "python3 scripts/toggle_registry.py --check",
                    "python3 -m unittest discover -s tests",
                }
            )
        if path.startswith("runtime/") or path.startswith("scripts/route_skill.py"):
            checks.add("python3 -m unittest discover -s tests -p test_router_lifecycle.py")
        if path.startswith("adapters/claude/") or path == "scripts/install_runtime_adapter.py":
            checks.update(
                {
                    "node --check adapters/claude/skills-ai-router.js",
                    "temporary Claude adapter install and check",
                }
            )
        if path.startswith("requests/") or path == "scripts/create_change_request.py":
            checks.add("python3 -m unittest tests.test_change_request")
    return sorted(checks)


def assess_change(
    operation: str,
    paths: Iterable[str],
    *,
    root: Path = ROOT,
    staged_paths: Iterable[str] = (),
    approval_ref: str | None = None,
) -> dict[str, Any]:
    if operation not in OPERATIONS:
        raise GuardError(f"unsupported operation: {operation}")
    normalized: list[str] = []
    external: list[str] = []
    protected: list[str] = []
    blocked: list[str] = []
    generated: list[str] = []
    for raw in paths:
        path, is_external = _relative_path(raw, root)
        if path not in normalized:
            normalized.append(path)
        if is_external:
            external.append(path)
            continue
        if path == ".git" or path.startswith(".git/"):
            blocked.append(path)
        if any(path == prefix.rstrip("/") or path.startswith(prefix) for prefix in PROTECTED_PREFIXES):
            protected.append(path)
        if path in GENERATED_PATHS:
            generated.append(path)
    if not normalized:
        raise GuardError("at least one --path is required")

    staged = sorted(set(staged_paths))
    staged_outside_scope = [path for path in staged if not _covered(path, normalized)]
    reasons: list[str] = []
    status = "allowed"
    if blocked:
        status = "blocked-by-invariant"
        reasons.append("Git internals are never a change target")
    elif operation in APPROVAL_OPERATIONS or external or protected:
        status = "approval-required"
        if operation in APPROVAL_OPERATIONS:
            reasons.append(f"{operation} requires an explicit scope or destructive-action approval")
        if external:
            reasons.append("one or more targets are outside the repository")
        if protected:
            reasons.append("one or more targets are protected canonical or vendored collections")
    if operation == "request":
        outside_inbox = [
            path for path in normalized
            if path != REQUEST_INBOX and not path.startswith(REQUEST_INBOX + "/")
        ]
        if external or outside_inbox:
            status = "blocked-by-invariant"
            reasons.append("external request creation may write only under requests/pending")
    if staged_outside_scope:
        status = "blocked-by-invariant"
        reasons.append("staged files exist outside the declared scope")
    if status == "approval-required" and approval_ref:
        status = "allowed-with-recorded-approval"
    if generated:
        reasons.append("generated files must be rebuilt from their canonical sources")

    return {
        "operation": operation,
        "status": status,
        "paths": normalized,
        "external_paths": external,
        "protected_paths": protected,
        "generated_paths": generated,
        "staged_outside_scope": staged_outside_scope,
        "reasons": reasons,
        "required_checks": required_checks(normalized),
        "approval_reference": approval_ref,
        "authority_note": "This report classifies risk; it does not grant permission.",
        "next_action": (
            "stop and show the exact scope-expansion or destructive-action report"
            if status == "approval-required"
            else "resolve the invariant violation before continuing"
            if status == "blocked-by-invariant"
            else "perform only the declared scope and required checks"
        ),
    }


def staged_files(root: Path = ROOT) -> list[str]:
    completed = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMRD"],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode:
        raise GuardError(completed.stderr.strip() or "cannot inspect staged files")
    return [line for line in completed.stdout.splitlines() if line]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("plan", "check", "check-staged"))
    parser.add_argument("--operation", choices=sorted(OPERATIONS), required=True)
    parser.add_argument("--path", action="append", default=[], dest="paths")
    parser.add_argument("--approval-ref", help="non-sensitive reference to explicit user approval")
    parser.add_argument("--json", action="store_true", help="emit JSON; currently the default stable format")
    args = parser.parse_args(argv)
    try:
        staged = staged_files() if args.command == "check-staged" else []
        report = assess_change(args.operation, args.paths, staged_paths=staged, approval_ref=args.approval_ref)
        print(json.dumps(report, indent=2, sort_keys=True))
        if report["status"] in {"allowed", "allowed-with-recorded-approval"}:
            return 0
        if report["status"] == "approval-required":
            return 2
        return 1
    except (GuardError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
