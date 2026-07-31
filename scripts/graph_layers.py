#!/usr/bin/env python3
"""Validate or synchronize Obsidian graph colours from the layer policy."""

from __future__ import annotations

import argparse
import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
GRAPH_PATH = Path(".obsidian/graph.json")
POLICY_PATH = Path("docs/05_COLOR_LAYERS.md")

LAYERS = (
    {
        "id": "L0",
        "query": "path:README.md OR path:AGENTS.md OR path:CLAUDE.md OR path:docs/SKILLS.md",
        "color": "#5B5BD6",
    },
    {
        "id": "L1",
        "query": (
            "path:docs/00_SKILLS_HUB.md OR path:docs/03_COMBO_MAP.md OR "
            "path:docs/04_RISK_MAP.md OR path:docs/05_COLOR_LAYERS.md OR "
            "path:docs/06_CHANGE_CONTROL.md"
        ),
        "color": "#00897B",
    },
    {"id": "L2", "query": "path:registry/", "color": "#2E7D32"},
    {"id": "L3", "query": "path:cards/", "color": "#EF6C00"},
    {
        "id": "L4",
        "query": (
            "path:design-with-claude/ OR path:interaction-protocol/ OR "
            "path:theory-reference/SKILL.md OR "
            "path:theory-reference/shared/SKILL.md OR "
            "path:theory-reference/shared/phases/ OR path:external-skills/"
        ),
        "color": "#6A1B9A",
    },
    {
        "id": "L5",
        "query": (
            "path:docs/ OR path:protocols/ OR path:runtime/ OR path:adapters/ OR "
            "path:scripts/ OR path:tests/ OR path:requests/ OR "
            "path:theory-reference/"
        ),
        "color": "#546E7A",
    },
)

INTERACTION_GRAPH_EDGES = {
    "docs/00_SKILLS_HUB.md": ("registry/interaction", "interaction-protocol/README"),
    "registry/interaction.md": (
        "docs/00_SKILLS_HUB",
        "registry/activation",
        "interaction-protocol/README",
        "runtime/PROTOCOL",
    ),
    "interaction-protocol/README.md": (
        "docs/00_SKILLS_HUB",
        "registry/activation",
        "registry/interaction",
        "runtime/PROTOCOL",
        "runtime/API_CONTRACT",
        "docs/INTERACTION_PROTOCOL_MIGRATION",
    ),
    "docs/INTERACTION_PROTOCOL_MIGRATION.md": ("interaction-protocol/README",),
    "runtime/README.md": ("interaction-protocol/README",),
    "runtime/PROTOCOL.md": ("interaction-protocol/README",),
    "runtime/API_CONTRACT.md": ("interaction-protocol/README",),
}


def expected_color_groups() -> list[dict[str, Any]]:
    return [
        {
            "query": layer["query"],
            "color": {"a": 1, "rgb": int(layer["color"].lstrip("#"), 16)},
        }
        for layer in LAYERS
    ]


def _query_matches(path: str, query: str) -> bool:
    for clause in query.split(" OR "):
        if not clause.startswith("path:"):
            continue
        target = clause.removeprefix("path:")
        if target.endswith("/") and path.startswith(target):
            return True
        if path == target:
            return True
    return False


def classify_path(path: str) -> str | None:
    normalized = Path(path).as_posix().lstrip("./")
    for layer in LAYERS:
        if _query_matches(normalized, layer["query"]):
            return layer["id"]
    return None


def _markdown_paths(root: Path) -> Iterable[str]:
    for path in sorted(root.rglob("*.md")):
        relative = path.relative_to(root)
        if any(part.startswith(".") for part in relative.parts):
            continue
        if relative.parts and relative.parts[0] == "sample_resources":
            continue
        yield relative.as_posix()


def interaction_link_errors(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    for source, targets in INTERACTION_GRAPH_EDGES.items():
        source_path = root / source
        if not source_path.is_file():
            errors.append(f"missing interaction graph source: {source}")
            continue
        text = source_path.read_text(encoding="utf-8")
        for target in targets:
            target_path = root / target
            if target_path.suffix == "":
                target_path = target_path.with_suffix(".md")
            if not target_path.is_file():
                errors.append(f"missing interaction graph target: {source} -> {target}")
                continue
            if not re.search(rf"\[\[{re.escape(target)}(?:\\?\||#|\]\])", text):
                errors.append(f"missing interaction graph link: {source} -> {target}")
    return errors


def check_graph(root: Path = ROOT, *, check_policy: bool = True) -> list[str]:
    errors: list[str] = []
    graph_path = root / GRAPH_PATH
    try:
        graph = json.loads(graph_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"cannot read {GRAPH_PATH}: {type(exc).__name__}"]
    if graph.get("colorGroups") != expected_color_groups():
        errors.append("Obsidian colorGroups do not match docs/05_COLOR_LAYERS.md")
    if check_policy:
        try:
            policy = (root / POLICY_PATH).read_text(encoding="utf-8")
        except OSError as exc:
            errors.append(f"cannot read {POLICY_PATH}: {type(exc).__name__}")
        else:
            for layer in LAYERS:
                if layer["query"] not in policy or layer["color"] not in policy:
                    errors.append(f"{POLICY_PATH} is missing the canonical {layer['id']} query or colour")
    unclassified = [path for path in _markdown_paths(root) if classify_path(path) is None]
    if unclassified:
        errors.append("unclassified Markdown: " + ", ".join(unclassified))
    if (root / "interaction-protocol" / "README.md").exists():
        errors.extend(interaction_link_errors(root))
    return errors


def sync_graph(root: Path = ROOT) -> None:
    graph_path = root / GRAPH_PATH
    graph_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        graph = json.loads(graph_path.read_text(encoding="utf-8"))
        mode = graph_path.stat().st_mode
    except FileNotFoundError:
        graph = {}
        mode = 0o644
    graph["colorGroups"] = expected_color_groups()
    payload = json.dumps(graph, indent=2) + "\n"
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{graph_path.name}.", dir=graph_path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temporary, mode & 0o777)
        os.replace(temporary, graph_path)
    finally:
        temporary.unlink(missing_ok=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--check", action="store_true", help="validate graph groups and Markdown coverage")
    action.add_argument("--sync", action="store_true", help="replace only colorGroups, preserving other graph settings")
    args = parser.parse_args(argv)
    if args.sync:
        sync_graph()
    errors = check_graph()
    if errors:
        for error in errors:
            print(f"error: {error}")
        return 1
    print("ok: Obsidian graph colors and Markdown layer coverage")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
