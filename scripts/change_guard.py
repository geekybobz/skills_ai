#!/usr/bin/env python3
"""Classify Skills AI repository changes without granting write authority."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from pathlib import PurePosixPath
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = Path("protocols/repository/CONTRACT.json")
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

CHECK_COMMANDS = {
    "adapter": (
        "node --check adapters/claude/skills-ai-router.js",
        "temporary Codex and Claude adapter install and check",
    ),
    "change-request": ("python3 -m unittest tests.test_change_request",),
    "benchmark": ("python3 scripts/benchmark_router.py --json",),
    "consistency": ("python3 scripts/scan_consistency.py changed --path <declared-path>",),
    "graph": ("python3 scripts/graph_layers.py --check",),
    "human-docs": ("python3 scripts/human_docs_guard.py --check",),
    "lifecycle": ("python3 -m unittest discover -s tests -p test_router_lifecycle.py",),
    "registry": (
        "python3 scripts/compile_registry.py --check",
        "python3 scripts/validate_registry.py",
        "python3 scripts/toggle_registry.py --check",
    ),
    "unit": ("python3 -m unittest discover -s tests",),
    "views": ("python3 scripts/compile_repository_views.py --check",),
}


class GuardError(RuntimeError):
    pass


def load_contract(root: Path = ROOT) -> dict[str, Any]:
    path = root / CONTRACT_PATH
    try:
        contract = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise GuardError(f"cannot read {CONTRACT_PATH}: {type(exc).__name__}") from exc
    if contract.get("version") != 1:
        raise GuardError("unsupported repository contract version")
    if not isinstance(contract.get("roles"), list) or not contract["roles"]:
        raise GuardError("repository contract roles must be a non-empty list")
    return contract


def _matches_pattern(path: str, pattern: str) -> bool:
    normalized = PurePosixPath(path).as_posix()
    if normalized.startswith("./"):
        normalized = normalized[2:]
    if pattern.endswith("/**"):
        prefix = pattern[:-3].rstrip("/")
        return normalized == prefix or normalized.startswith(prefix + "/")
    if not any(character in pattern for character in "*?["):
        return normalized == pattern
    return PurePosixPath(normalized).match(pattern)


def matching_roles(path: str, contract: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        role
        for role in contract["roles"]
        if any(_matches_pattern(path, pattern) for pattern in role.get("patterns", []))
    ]


def required_check_ids(paths: Iterable[str], contract: dict[str, Any]) -> list[str]:
    check_ids: set[str] = set()
    for path in paths:
        for role in matching_roles(path, contract):
            check_ids.update(role.get("checks", []))
    unknown = check_ids - set(CHECK_COMMANDS)
    if unknown:
        raise GuardError("unknown repository check ids: " + ", ".join(sorted(unknown)))
    return sorted(check_ids)


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


def required_checks(
    paths: Iterable[str],
    *,
    contract: dict[str, Any] | None = None,
) -> list[str]:
    contract = contract or load_contract()
    checks = {
        "git diff --check",
        "focused tests for changed behavior",
    }
    for check_id in required_check_ids(paths, contract):
        checks.update(CHECK_COMMANDS[check_id])
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
    contract = load_contract(root)
    approval_operations = set(contract["approval_operations"])
    protected_prefixes = tuple(contract["protected_prefixes"])
    generated_paths = set(contract["generated_outputs"])
    request_inbox = contract["request_inbox"]
    normalized: list[str] = []
    external: list[str] = []
    protected: list[str] = []
    blocked: list[str] = []
    generated: list[str] = []
    unmapped: list[str] = []
    roles: dict[str, list[str]] = {}
    for raw in paths:
        path, is_external = _relative_path(raw, root)
        if path not in normalized:
            normalized.append(path)
        if is_external:
            external.append(path)
            continue
        if path == ".git" or path.startswith(".git/"):
            blocked.append(path)
        if any(path == prefix.rstrip("/") or path.startswith(prefix) for prefix in protected_prefixes):
            protected.append(path)
        if path in generated_paths:
            generated.append(path)
        matched = matching_roles(path, contract)
        roles[path] = [role["id"] for role in matched]
        if not matched:
            unmapped.append(path)
    if not normalized:
        raise GuardError("at least one --path is required")

    staged = sorted(set(staged_paths))
    staged_outside_scope = [path for path in staged if not _covered(path, normalized)]
    reasons: list[str] = []
    status = "allowed"
    if blocked:
        status = "blocked-by-invariant"
        reasons.append("Git internals are never a change target")
    elif operation in approval_operations or external or protected:
        status = "approval-required"
        if operation in approval_operations:
            reasons.append(f"{operation} requires an explicit scope or destructive-action approval")
        if external:
            reasons.append("one or more targets are outside the repository")
        if protected:
            reasons.append("one or more targets are protected canonical or vendored collections")
    if operation == "request":
        outside_inbox = [
            path for path in normalized
            if path != request_inbox and not path.startswith(request_inbox + "/")
        ]
        if external or outside_inbox:
            status = "blocked-by-invariant"
            reasons.append("external request creation may write only under requests/pending")
    if staged_outside_scope:
        status = "blocked-by-invariant"
        reasons.append("staged files exist outside the declared scope")
    if unmapped and not external:
        status = "blocked-by-invariant"
        reasons.append("one or more repository paths have no declared maintenance role")
    if status == "approval-required" and approval_ref:
        status = "allowed-with-recorded-approval"
    if generated:
        reasons.append("generated files must be rebuilt from their canonical sources")

    affected_generated = []
    for output, rule in contract["generated_outputs"].items():
        if any(
            _matches_pattern(path, pattern)
            for path in normalized
            for pattern in rule.get("source_patterns", [])
        ):
            affected_generated.append(output)

    check_ids = required_check_ids(normalized, contract)

    return {
        "operation": operation,
        "status": status,
        "paths": normalized,
        "external_paths": external,
        "protected_paths": protected,
        "generated_paths": generated,
        "affected_generated_outputs": sorted(affected_generated),
        "roles": roles,
        "unmapped_paths": unmapped,
        "staged_outside_scope": staged_outside_scope,
        "reasons": reasons,
        "required_check_ids": check_ids,
        "required_checks": required_checks(normalized, contract=contract),
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
