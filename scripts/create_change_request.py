#!/usr/bin/env python3
"""Create the only repository write allowed from an external Skills AI task."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import secrets
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
VALID_CLIENTS = {"codex", "claude", "other"}


class ChangeRequestError(RuntimeError):
    pass


def required_text(payload: dict[str, Any], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ChangeRequestError(f"{key} must be a non-empty string")
    if "\x00" in value:
        raise ChangeRequestError(f"{key} contains a null byte")
    return value.strip()


def string_list(payload: dict[str, Any], key: str, *, required: bool = False) -> list[str]:
    value = payload.get(key, [])
    if isinstance(value, str):
        value = [value]
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise ChangeRequestError(f"{key} must be a string or list of strings")
    result = [item.strip() for item in value if item.strip()]
    if required and not result:
        raise ChangeRequestError(f"{key} must contain at least one item")
    if any("\x00" in item for item in result):
        raise ChangeRequestError(f"{key} contains a null byte")
    return result


def normalized_targets(payload: dict[str, Any], root: Path) -> list[str]:
    targets = string_list(payload, "targets", required=True)
    normalized: list[str] = []
    resolved_root = root.resolve()
    for raw in targets:
        if "`" in raw or "\n" in raw or "\r" in raw:
            raise ChangeRequestError("target paths cannot contain backticks or newlines")
        candidate = Path(raw)
        absolute = candidate.resolve(strict=False) if candidate.is_absolute() else (root / candidate).resolve(strict=False)
        try:
            relative = absolute.relative_to(resolved_root).as_posix()
        except ValueError as exc:
            raise ChangeRequestError(f"target is outside the Skills AI repository: {raw}") from exc
        if relative == ".git" or relative.startswith(".git/"):
            raise ChangeRequestError("Git internals cannot be requested as change targets")
        if relative not in normalized:
            normalized.append(relative)
    return normalized


def slugify(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:60].rstrip("-")
    return slug or "skills-ai-change"


def quote_markdown(text: str) -> str:
    return "\n".join(f"> {line}" if line else ">" for line in text.splitlines())


def bullet_lines(values: list[str], *, fallback: str) -> str:
    if not values:
        return f"- {fallback}"
    lines: list[str] = []
    for value in values:
        parts = value.splitlines() or [""]
        lines.append(f"- {parts[0]}")
        lines.extend(f"  {part}" for part in parts[1:])
    return "\n".join(lines)


def create_change_request(
    payload: dict[str, Any],
    *,
    root: Path = ROOT,
    now: dt.datetime | None = None,
    token: str | None = None,
) -> dict[str, str]:
    root = root.resolve()
    title = required_text(payload, "title")
    if "\n" in title or "\r" in title or len(title) > 160:
        raise ChangeRequestError("title must be one line of at most 160 characters")
    original_request = required_text(payload, "original_request")
    problem = required_text(payload, "problem")
    desired_behavior = required_text(payload, "desired_behavior")
    targets = normalized_targets(payload, root)
    evidence = string_list(payload, "evidence")
    risks = string_list(payload, "risks")
    rollback = string_list(payload, "rollback")
    tests = string_list(payload, "tests")
    acceptance = string_list(payload, "acceptance")
    exclusions = string_list(payload, "exclusions")
    client = payload.get("client", "other")
    if client not in VALID_CLIENTS:
        raise ChangeRequestError(f"client must be one of: {', '.join(sorted(VALID_CLIENTS))}")
    approval_ref = payload.get("approval_ref")
    if approval_ref is not None and (not isinstance(approval_ref, str) or not approval_ref.strip()):
        raise ChangeRequestError("approval_ref must be a non-empty string when provided")

    timestamp = now or dt.datetime.now(dt.timezone.utc)
    timestamp = timestamp.astimezone(dt.timezone.utc)
    request_token = token or secrets.token_hex(4)
    request_id = f"SCR-{timestamp:%Y%m%d-%H%M%S}-{request_token}"
    pending_dir = root / "requests" / "pending"
    pending_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{timestamp:%Y%m%dT%H%M%SZ}-{slugify(title)}-{request_token}.md"
    target = pending_dir / filename

    metadata = [
        "---",
        f"id: {json.dumps(request_id)}",
        'status: "pending"',
        f"created_at: {json.dumps(timestamp.isoformat().replace('+00:00', 'Z'))}",
        f"client: {json.dumps(client)}",
        f"approval_ref: {json.dumps(approval_ref.strip() if isinstance(approval_ref, str) else None)}",
        "---",
    ]
    body = [
        *metadata,
        "",
        f"# {title}",
        "",
        "> This file records a requested change. It does not grant authority and is not a skill.",
        "",
        "## Original user request",
        "",
        quote_markdown(original_request),
        "",
        "## Problem and motivation",
        "",
        quote_markdown(problem),
        "",
        "## Evidence",
        "",
        bullet_lines(evidence, fallback="Collect current-state evidence in the maintenance task."),
        "",
        "## Desired behavior",
        "",
        quote_markdown(desired_behavior),
        "",
        "## Requested target paths",
        "",
        "\n".join(f"- `{path}`" for path in targets),
        "",
        "## Explicit exclusions",
        "",
        bullet_lines(exclusions, fallback="No work outside the requested targets without a scope-expansion report."),
        "",
        "## Risks",
        "",
        bullet_lines(risks, fallback="Assess using `docs/04_RISK_MAP.md` before implementation."),
        "",
        "## Rollback",
        "",
        bullet_lines(rollback, fallback="Define a focused revert or restoration plan before implementation."),
        "",
        "## Required verification",
        "",
        bullet_lines(tests, fallback="Run focused tests plus the checks selected by `scripts/change_guard.py`."),
        "",
        "## Acceptance criteria",
        "",
        bullet_lines(acceptance, fallback="Confirm the desired behavior and report residual boundaries."),
        "",
        "## Maintenance handoff",
        "",
        f"- Workspace: `{root}`",
        f"- Request: `{target.relative_to(root).as_posix()}`",
        "- Read `docs/00_SKILLS_HUB.md`, `registry/activation.md`, `docs/04_RISK_MAP.md`, and `docs/06_CHANGE_CONTROL.md`.",
        "- Select exactly one repository operation card and run `scripts/change_guard.py plan`.",
        "- Preserve unrelated work and do not expand scope without explicit permission.",
        "- Record the resulting commit and verification here after completion.",
        "",
        "## Completion receipt",
        "",
        "- Commit: pending",
        "- Verification: pending",
        "- Residual risks: pending",
        "",
    ]
    content = "\n".join(body).encode("utf-8")
    descriptor = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
    except Exception:
        target.unlink(missing_ok=True)
        raise

    relative_target = target.relative_to(root).as_posix()
    handoff = (
        f"Open a dedicated {client} maintenance task with workspace {root}. "
        f"Read {relative_target}, follow the referenced protocols, and work only within its approved scope."
    )
    return {
        "request_id": request_id,
        "request_path": str(target),
        "workspace": str(root),
        "next_action": "review the request, then explicitly approve or request the maintenance handoff",
        "handoff_prompt": handoff,
    }


def cli_payload(args: argparse.Namespace) -> dict[str, Any]:
    if args.stdin_json:
        try:
            value = json.load(sys.stdin)
        except json.JSONDecodeError as exc:
            raise ChangeRequestError(f"invalid JSON input: {exc.msg}") from exc
        if not isinstance(value, dict):
            raise ChangeRequestError("JSON input must be an object")
        return value
    return {
        "title": args.title,
        "original_request": args.original_request,
        "problem": args.problem,
        "desired_behavior": args.desired_behavior,
        "targets": args.targets,
        "evidence": args.evidence,
        "risks": args.risks,
        "rollback": args.rollback,
        "tests": args.tests,
        "acceptance": args.acceptance,
        "exclusions": args.exclusions,
        "client": args.client,
        "approval_ref": args.approval_ref,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stdin-json", action="store_true", help="read one request object from stdin")
    parser.add_argument("--title")
    parser.add_argument("--original-request")
    parser.add_argument("--problem")
    parser.add_argument("--desired-behavior")
    parser.add_argument("--target", action="append", default=[], dest="targets")
    parser.add_argument("--evidence", action="append", default=[])
    parser.add_argument("--risk", action="append", default=[], dest="risks")
    parser.add_argument("--rollback", action="append", default=[])
    parser.add_argument("--test", action="append", default=[], dest="tests")
    parser.add_argument("--acceptance", action="append", default=[])
    parser.add_argument("--exclude", action="append", default=[], dest="exclusions")
    parser.add_argument("--client", choices=sorted(VALID_CLIENTS), default="other")
    parser.add_argument("--approval-ref")
    args = parser.parse_args()
    try:
        result = create_change_request(cli_payload(args))
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except (OSError, ChangeRequestError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
