#!/usr/bin/env python3
"""List the live Skills AI registry without loading any skill body."""

from __future__ import annotations

import argparse
import json

from registry_runtime import RegistryRuntimeError, load_manifest, registry_summary


def render_human(summary: dict, state: str) -> str:
    lines = [f"Skills AI local registry (source {summary['source_hash'][:12]})"]
    states = ("active", "manual", "off") if state == "all" else (state,)
    for name in states:
        values = summary["routes"].get(name, [])
        lines.append(f"{name.title()} ({len(values)}): {', '.join(values) if values else 'none'}")
    counts = summary["route_counts"]
    hidden_count = counts["hidden"] + counts["deprecated"]
    lines.append(f"Hidden/deprecated routes: {hidden_count} (identifiers omitted outside maintenance)")
    lines.append("This is live registry metadata; no skill body was loaded.")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--state",
        choices=("all", "active", "manual", "off", "hidden", "deprecated"),
        default="all",
    )
    parser.add_argument("--include-hidden", action="store_true", help="maintenance-only identifier listing")
    parser.add_argument("--json", action="store_true", help="emit stable JSON")
    args = parser.parse_args()
    try:
        include_hidden = args.include_hidden or args.state in {"hidden", "deprecated"}
        summary = registry_summary(load_manifest(), include_hidden=include_hidden)
        if args.json:
            print(json.dumps(summary, indent=2, sort_keys=True))
        else:
            print(render_human(summary, args.state))
        return 0
    except (OSError, RegistryRuntimeError, ValueError) as exc:
        print(f"error: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
