#!/usr/bin/env python3
"""List the live Skills AI registry without loading any skill body."""

from __future__ import annotations

import argparse
import json

from registry_runtime import RegistryRuntimeError, load_manifest, registry_summary


def render_human(summary: dict, state: str, *, routes: bool = False) -> str:
    noun = "Internal capability routes" if routes else "Public skills"
    groups = summary["routes"] if routes else summary["skills"]
    counts_key = "route_counts" if routes else "skill_counts"
    lines = [f"Skills AI local registry (source {summary['source_hash'][:12]})", noun]
    if not routes:
        orchestrator = summary["orchestrator"]
        lines.append(
            f"Orchestrator: {orchestrator['id']} ({orchestrator['mode']}; not counted as a skill)"
        )
    states = ("active", "manual", "off") if state == "all" else (state,)
    for name in states:
        values = groups.get(name, [])
        lines.append(f"{name.title()} ({len(values)}): {', '.join(values) if values else 'none'}")
    counts = summary[counts_key]
    hidden_count = counts["hidden"] + counts["deprecated"]
    lines.append(
        f"Hidden/deprecated {'routes' if routes else 'skills'}: {hidden_count} "
        "(identifiers omitted outside maintenance)"
    )
    if not routes and summary.get("skill_records"):
        lines.append("Skill catalog")
        for skill in summary["skill_records"]:
            families = ", ".join(skill["families"]) or "none"
            triggers = ", ".join(skill["triggers"]) or "none"
            if skill["triggers_truncated"]:
                triggers += f" (+{skill['trigger_count'] - len(skill['triggers'])} more)"
            lines.append(
                f"- {skill['id']} [{skill['state']}/{skill['role']}]: {skill['purpose']} "
                f"Families: {families}. Triggers: {triggers}."
            )
    if routes:
        for key, label in (
            ("family_gates", "Family gates"),
            ("component_gates", "Component gates"),
        ):
            values = summary.get(key, {})
            lines.append(
                f"{label}: "
                + "; ".join(
                    f"{name}={','.join(values.get(name, [])) or 'none'}"
                    for name in states
                )
            )
        aliases = summary.get("command_aliases", [])
        lines.append(
            "Command aliases: "
            + ", ".join(item["command"] for item in aliases)
            if aliases
            else "Command aliases: none"
        )
        compatibility = summary.get("compatibility_aliases", [])
        if compatibility:
            lines.append(
                "Compatibility aliases: "
                + ", ".join(
                    f"{item['alias']} -> {item['canonical']}" for item in compatibility
                )
            )
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
    view_group = parser.add_mutually_exclusive_group()
    view_group.add_argument("--routes", action="store_true", help="list internal capability diagnostics instead of skills")
    view_group.add_argument("--catalog", action="store_true", help="include skill-level purpose, family, and trigger metadata")
    parser.add_argument("--json", action="store_true", help="emit stable JSON")
    args = parser.parse_args()
    try:
        include_hidden = args.include_hidden or args.state in {"hidden", "deprecated"}
        view = "diagnostic" if args.routes else "catalog" if args.catalog else "inventory"
        summary = registry_summary(load_manifest(), include_hidden=include_hidden, view=view)
        if args.json:
            print(json.dumps(summary, indent=2, sort_keys=True))
        else:
            print(render_human(summary, args.state, routes=args.routes))
        return 0
    except (OSError, RegistryRuntimeError, ValueError) as exc:
        print(f"error: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
