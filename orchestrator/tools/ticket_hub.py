#!/usr/bin/env python3
"""Manage local Skills Orchestrator feedback tickets without project-wide scans."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "orchestrator" / "runtime"))

from ticket_hub import TicketHub, TicketHubError  # noqa: E402


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--hub-root",
        type=Path,
        default=ROOT / "feedback-tickets",
        help="local central ticket directory (default: %(default)s)",
    )
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    commands = parser.add_subparsers(dest="command", required=True)

    register = commands.add_parser("register", help="register one project root for scan")
    register.add_argument("--id", required=True, help="stable local project id")
    register.add_argument("--project", required=True, type=Path, help="absolute project root")

    commands.add_parser("scan", help="collect valid new or updated project reports")

    listing = commands.add_parser("list", help="show central active tickets")
    listing.add_argument("--skill", help="filter by recorded skill")
    listing.add_argument("--group-by", choices=("skill",), help="group result rows")

    resolve = commands.add_parser("resolve", help="open one ticket for human-led review")
    resolve.add_argument("--ticket", required=True, help="central record_id or unique source ticket id")
    resolve.add_argument("--note", help="user's additional direction; no project edit")
    resolve.add_argument("--close", action="store_true", help="delete central ticket folder after confirmation")
    resolve.add_argument("--summary", help="required one-line outcome when closing")
    return parser


def _render(command: str, result: dict[str, object]) -> str:
    if command == "scan":
        lines = [
            f"New: {len(result['new'])}",
            f"Updated: {len(result['updated'])}",
            f"Unchanged: {len(result['unchanged'])}",
            f"Errors: {len(result['errors'])}",
        ]
        for item in result["new"]:  # type: ignore[index]
            lines.append(f"+ {item['record_id']} ({item['skill']})")  # type: ignore[index]
        for item in result["errors"]:  # type: ignore[index]
            lines.append(f"! {item}")
        return "\n".join(lines)
    if command == "list":
        if "groups" in result:
            lines: list[str] = []
            for skill, rows in result["groups"].items():  # type: ignore[index]
                lines.append(str(skill))
                lines.extend(f"  - {row['record_id']} [{row['status']}]" for row in rows)  # type: ignore[index]
            return "\n".join(lines) or "No active tickets."
        rows = result["tickets"]  # type: ignore[index]
        return "\n".join(f"- {row['record_id']} | {row['skill']} | {row['status']}" for row in rows) or "No active tickets."
    if command == "resolve" and "closed" in result:
        return f"Closed {result['deleted_ticket_folder']}."
    if command == "resolve":
        return "\n\n".join(
            [
                f"Ticket: {result['record_id']}\nProject: {result['project_id']}\nSkill: {result['skill']}",
                str(result["report"]),
                "Review mode only. Explain more or give an explicit direction before any project edit.",
            ]
        )
    return json.dumps(result, indent=2, sort_keys=True)


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    hub = TicketHub(args.hub_root)
    try:
        if args.command == "register":
            result = hub.register(args.id, args.project)
        elif args.command == "scan":
            result = hub.scan()
        elif args.command == "list":
            result = hub.list(skill=args.skill, group_by_skill=args.group_by == "skill")
        else:
            result = hub.resolve(
                args.ticket,
                note=args.note,
                close=args.close,
                summary=args.summary,
            )
    except TicketHubError as exc:
        print(f"ticket-hub: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, sort_keys=True) if args.json else _render(args.command, result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
