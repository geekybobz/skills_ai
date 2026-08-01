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

from change_guard import GuardError, load_contract


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


def _target_path(root: Path, target: str) -> Path:
    path = root / target
    if path.suffix == "":
        path = path.with_suffix(".md")
    return path


def _has_wikilink(text: str, target: str) -> bool:
    return bool(re.search(rf"\[\[{re.escape(target)}(?:\\?\||#|\]\])", text))


def graph_link_errors(
    root: Path = ROOT,
    *,
    contract_id: str | None = None,
) -> list[str]:
    errors: list[str] = []
    try:
        contract = load_contract(root)
    except GuardError as exc:
        return [str(exc)]
    graph_contracts = contract.get("graph_contracts", [])
    for graph_contract in graph_contracts:
        graph_id = graph_contract.get("id", "unnamed")
        if contract_id is not None and graph_id != contract_id:
            continue

        entry = graph_contract.get("entry")
        if not isinstance(entry, str) or not (root / entry).is_file():
            errors.append(f"missing {graph_id} graph entry: {entry}")
        for canonical in graph_contract.get("canonical_sources", []):
            if not (root / canonical).is_file():
                errors.append(f"missing {graph_id} canonical source: {canonical}")

        for source, targets in graph_contract.get("required_links", {}).items():
            source_path = root / source
            if not source_path.is_file():
                errors.append(f"missing {graph_id} graph source: {source}")
                continue
            text = source_path.read_text(encoding="utf-8")
            for target in targets:
                if not _target_path(root, target).is_file():
                    errors.append(f"missing {graph_id} graph target: {source} -> {target}")
                    continue
                if not _has_wikilink(text, target):
                    errors.append(f"missing {graph_id} graph link: {source} -> {target}")
    return errors


def wikilink_errors(root: Path = ROOT) -> list[str]:
    """Reject dangling repository wikilinks without loading external submodule notes."""
    markdown = list(_markdown_paths(root))
    searchable = [
        path
        for path in markdown
        if not path.startswith("theory-reference/")
        or path in {
            "theory-reference/SKILL.md",
            "theory-reference/shared/SKILL.md",
        }
    ]
    exact: dict[str, str] = {}
    by_stem: dict[str, list[str]] = {}
    for relative in searchable:
        without_suffix = relative[:-3] if relative.endswith(".md") else relative
        exact[without_suffix] = relative
        exact[relative] = relative
        by_stem.setdefault(Path(relative).stem, []).append(relative)

    try:
        contract = load_contract(root)
    except GuardError:
        contract = {}
    allowed_external = tuple(contract.get("allowed_external_symlinks", []))
    errors: list[str] = []
    for source in searchable:
        text = (root / source).read_text(encoding="utf-8")
        for raw_target in re.findall(r"\[\[([^\]]+)\]\]", text):
            target = raw_target.replace("\\|", "|").split("|", 1)[0].split("#", 1)[0].strip()
            if not target or re.match(r"^[a-z]+://", target):
                continue
            normalized = target[:-3] if target.endswith(".md") else target
            resolved = normalized in exact
            candidate = root / normalized
            if candidate.suffix == "":
                candidate = candidate.with_suffix(".md")
            if not resolved and candidate.is_file() and any(
                normalized == prefix or normalized.startswith(prefix + "/")
                for prefix in allowed_external
            ):
                resolved = True
            if not resolved and "/" not in normalized:
                resolved = len(by_stem.get(normalized, [])) >= 1
            if not resolved:
                relative_candidate = (
                    Path(source).parent / normalized
                ).as_posix()
                resolved = relative_candidate in exact
            if not resolved:
                errors.append(f"broken wikilink: {source} -> {target}")
    return errors


def interaction_link_errors(root: Path = ROOT) -> list[str]:
    """Compatibility wrapper for the interaction-specific test/API."""
    return graph_link_errors(root, contract_id="interaction-protocol")


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
    if check_policy:
        errors.extend(graph_link_errors(root))
        errors.extend(wikilink_errors(root))
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
