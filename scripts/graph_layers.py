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
DOCUMENTATION_MODEL_PATH = Path("protocols/repository/DOCUMENTATION.json")

LAYERS = (
    {
        "id": "L0",
        "query": "path:README.md OR path:AGENTS.md OR path:CLAUDE.md OR path:docs/SKILLS.md",
        "color": "#5B5BD6",
    },
    {
        "id": "L1",
        "query": (
            "path:docs/00_SKILLS_HUB.md OR path:registry/activation.md OR "
            "path:graph/orchestration/skills-orchestrator.md OR "
            "path:interaction-protocol/README.md OR "
            "path:docs/SHARED_DOCUMENTATION_MODEL.md OR "
            "path:docs/03_COMBO_MAP.md OR "
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
            "path:markdown-protocol/ OR path:optimizer/ OR path:project-manager/ OR "
            "path:theory-reference/SKILL.md OR "
            "path:graph/skills/ OR "
            "path:theory-reference/shared/SKILL.md OR "
            "path:theory-reference/shared/phases/ OR path:external-skills/ OR "
            "path:research-context-scout/"
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
        if relative.parts and relative.parts[0] in {"sample_resources", "skill-plans"}:
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


def graph_role_errors(root: Path = ROOT) -> list[str]:
    """Enforce architectural node roles independently of query ordering."""
    try:
        contract = load_contract(root)
    except GuardError as exc:
        return [str(exc)]
    policy = contract.get("graph_role_policy")
    if not isinstance(policy, dict):
        return ["repository contract is missing graph_role_policy"]

    errors: list[str] = []
    entry_layer = policy.get("graph_contract_entry_layer")
    if not isinstance(entry_layer, str):
        errors.append("graph_role_policy.graph_contract_entry_layer must be a layer id")
    else:
        for graph_contract in contract.get("graph_contracts", []):
            entry = graph_contract.get("entry")
            if not isinstance(entry, str):
                continue
            actual = classify_path(entry)
            if actual != entry_layer:
                errors.append(
                    f"graph hub has wrong layer: {entry} is {actual or 'unclassified'}, "
                    f"expected {entry_layer}"
                )

    required = policy.get("required_paths")
    if not isinstance(required, dict):
        errors.append("graph_role_policy.required_paths must be an object")
    else:
        for path, expected in required.items():
            if not isinstance(path, str) or not isinstance(expected, str):
                errors.append("graph_role_policy.required_paths must map paths to layer ids")
                continue
            actual = classify_path(path)
            if actual != expected:
                errors.append(
                    f"graph role has wrong layer: {path} is {actual or 'unclassified'}, "
                    f"expected {expected}"
                )
    return errors


def _path_is_excluded(path: str, search: str) -> bool:
    for target in re.findall(r"(?:^|\s)-path:([^\s]+)", search):
        normalized = target.strip('"\'').rstrip("/")
        if path == normalized or path.startswith(normalized + "/"):
            return True
    return False


def graph_inventory_errors(root: Path = ROOT) -> list[str]:
    """Require one visible, descriptive graph node per orchestrator/skill record."""
    try:
        contract = load_contract(root)
        model = json.loads((root / DOCUMENTATION_MODEL_PATH).read_text(encoding="utf-8"))
        graph = json.loads((root / GRAPH_PATH).read_text(encoding="utf-8"))
    except (GuardError, OSError, json.JSONDecodeError) as exc:
        return [f"cannot validate graph inventory: {type(exc).__name__}"]

    policy = contract.get("graph_inventory_policy")
    if not isinstance(policy, dict):
        return ["repository contract is missing graph_inventory_policy"]
    orchestrator = model.get("orchestrator")
    packages = model.get("packages")
    if not isinstance(orchestrator, dict) or not isinstance(packages, list):
        return ["documentation model must declare one orchestrator and a package list"]

    reserved = set(policy.get("reserved_entry_names", []))
    entries = [(orchestrator, policy.get("orchestrator_layer"), "orchestrator")]
    entries.extend((package, policy.get("skill_layer"), "skill-package") for package in packages)
    errors: list[str] = []
    seen_paths: set[str] = set()
    seen_names: set[str] = set()
    search = graph.get("search", "")
    require_visibility = policy.get("require_default_visibility") is True
    orchestrator_entry = orchestrator.get("graph_entry")

    for record, expected_layer, kind in entries:
        record_id = record.get("id")
        display_name = record.get("display_name")
        entry = record.get("graph_entry")
        if not all(isinstance(value, str) and value for value in (record_id, display_name, entry)):
            errors.append(f"invalid {kind} graph declaration: {record_id or '(missing id)'}")
            continue
        name = Path(entry).name
        if entry in seen_paths:
            errors.append(f"duplicate graph inventory path: {entry}")
        seen_paths.add(entry)
        if name in seen_names:
            errors.append(f"duplicate graph inventory filename: {name}")
        seen_names.add(name)
        if name in reserved:
            errors.append(f"generic graph inventory filename is forbidden: {entry}")
        if Path(entry).stem != record_id:
            errors.append(f"graph inventory filename must match id: {entry} != {record_id}.md")
        actual_layer = classify_path(entry)
        if actual_layer != expected_layer:
            errors.append(
                f"graph inventory node has wrong layer: {entry} is {actual_layer or 'unclassified'}, "
                f"expected {expected_layer}"
            )
        path = root / entry
        if not path.is_file():
            errors.append(f"missing graph inventory node: {entry}")
            continue
        text = path.read_text(encoding="utf-8")
        if not re.search(rf"^#\s+{re.escape(display_name)}\s*$", text, flags=re.MULTILINE):
            errors.append(f"graph inventory label mismatch: {entry} must use '# {display_name}'")
        if f"graph_kind: {kind}" not in text:
            errors.append(f"graph inventory kind mismatch: {entry} must be {kind}")
        if not _has_wikilink(text, "registry/activation"):
            errors.append(f"graph inventory node must link Activation: {entry}")
        if kind == "skill-package" and isinstance(orchestrator_entry, str):
            if not _has_wikilink(text, orchestrator_entry.removesuffix(".md")):
                errors.append(f"skill graph node must link the orchestrator: {entry}")
        if require_visibility and _path_is_excluded(entry, search):
            errors.append(f"graph inventory node is hidden by the default filter: {entry}")
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
    """Graph-link errors for the interaction-protocol contract."""
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
        errors.extend(graph_role_errors(root))
        errors.extend(graph_inventory_errors(root))
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
