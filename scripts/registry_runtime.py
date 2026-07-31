#!/usr/bin/env python3
"""Compile and route the Skills AI registry without loading it into model context."""

from __future__ import annotations

import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "runtime" / "router-manifest.json"
PROFILE_PATH = ROOT / "runtime" / "profile.json"
HUB_PATH = ROOT / "docs" / "00_SKILLS_HUB.md"
ACTIVATION_PATH = ROOT / "registry" / "activation.md"

ACTIVE_STATES = {"active", "manual"}
INACTIVE_STATES = {"off", "hidden", "deprecated"}
VALID_STATES = ACTIVE_STATES | INACTIVE_STATES

FAMILY_DOMAINS = {
    "design": "visual-design",
    "ui-patterns": "product-ux",
    "build-ops": "software",
    "compression": "communication",
    "theory": "theory",
    "career": "career",
}

OUTPUT_SHAPES = {
    "discuss": "answer -> reason -> implication",
    "explain": "answer -> mechanism -> example or consequence",
    "derive": "result -> setup -> equations -> derivation -> boundary",
    "investigate": "scope -> evidence -> findings -> unknowns",
    "design": "aim -> requirements -> architecture -> validation",
    "implement": "preflight -> change -> verification -> result",
    "review": "findings -> evidence -> fix -> test gaps",
    "write": "audience -> facts -> draft -> factual check",
}


class RegistryRuntimeError(RuntimeError):
    pass


def split_row(line: str) -> list[str] | None:
    """Split a Markdown table row while preserving escaped wikilink pipes."""
    if not line.startswith("|"):
        return None
    body = line.strip().strip("|")
    cells = [cell.strip().replace("\\|", "|") for cell in re.split(r"(?<!\\)\|", body)]
    if not cells or all(set(cell) <= {"-", ":", " "} for cell in cells):
        return None
    return cells


def extract_route(cell: str) -> tuple[str, str]:
    """Return a normalized Markdown target path and its display label."""
    text = cell.replace("\\|", "|").strip()
    link = re.search(r"\[\[([^|\]]+)(?:\|([^\]]+))?\]\]", text)
    if link:
        target = link.group(1)
        label = link.group(2) or Path(target).name
    else:
        code = re.search(r"`([^`]+)`", text)
        if not code:
            raise RegistryRuntimeError(f"route is neither wikilink nor code path: {cell}")
        target = code.group(1)
        label = Path(target).name
    path = target if target.endswith(".md") else target + ".md"
    if path.endswith("/SKILL.md"):
        label = Path(path).parent.name
    elif label.endswith(".md"):
        label = label[:-3]
    return path, label


def normalize(text: str) -> str:
    text = text.lower().replace("-", " ").replace("_", " ")
    text = re.sub(r"[`*_#]", "", text)
    return " ".join(re.findall(r"[a-z0-9.+/]+", text))


def split_triggers(text: str) -> list[str]:
    return [item.strip(" `") for item in re.split(r"\s*,\s*", text) if item.strip(" `")]


def _read_sections(path: Path) -> Iterable[tuple[str, list[str]]]:
    section = ""
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            section = line[3:].strip()
            continue
        cells = split_row(line)
        if cells:
            yield section, cells


def parse_activation(path: Path = ACTIVATION_PATH) -> dict[str, dict[str, dict[str, str]]]:
    result: dict[str, dict[str, dict[str, str]]] = {
        "families": {},
        "skills": {},
        "components": {},
    }
    section_kinds = {
        "Family Gates": "families",
        "Skill Gates": "skills",
        "Caveman Components": "components",
        "Quantum Job Collector Components": "components",
    }
    for section, cells in _read_sections(path):
        kind = section_kinds.get(section)
        if not kind or cells[0] == "id" or len(cells) < 4:
            continue
        row_id, state, route, boundary = cells[:4]
        state = state.strip("`")
        if state not in VALID_STATES:
            raise RegistryRuntimeError(f"invalid state {state} for {row_id}")
        route_path, _ = extract_route(route)
        if row_id in result[kind]:
            raise RegistryRuntimeError(f"duplicate activation id: {row_id}")
        result[kind][row_id] = {
            "state": state,
            "path": route_path,
            "boundary": boundary,
        }
    return result


def parse_hub(path: Path = HUB_PATH) -> dict[str, list[str]]:
    routes: dict[str, list[str]] = {}
    for section, cells in _read_sections(path):
        if section != "Route" or cells[0] == "task looks like" or len(cells) < 2:
            continue
        route_path, _ = extract_route(cells[1])
        routes[route_path] = split_triggers(cells[0])
    return routes


def parse_family_registry(path: Path) -> list[dict[str, Any]]:
    routes: list[dict[str, Any]] = []
    for section, cells in _read_sections(path):
        if section != "Skills" or cells[0] in {"skill", "route"} or len(cells) < 4:
            continue
        skill_path, skill_id = extract_route(cells[0])
        routes.append(
            {
                "id": skill_id,
                "path": skill_path,
                "description": cells[1],
                "triggers": split_triggers(cells[2]),
                "not_for": cells[3],
            }
        )
    if not routes:
        path_match = re.search(
            r"^- Path:\s+`([^`]+)`",
            path.read_text(encoding="utf-8"),
            flags=re.MULTILINE,
        )
        if path_match:
            skill_path = path_match.group(1)
            skill_id = Path(skill_path).parent.name if skill_path.endswith("/SKILL.md") else Path(skill_path).stem
            routes.append(
                {
                    "id": skill_id,
                    "path": skill_path,
                    "description": f"entry route declared by {path.name}",
                    "triggers": [],
                    "not_for": "",
                }
            )
    return routes


def _source_fingerprint(paths: Iterable[Path]) -> tuple[str, list[dict[str, str]]]:
    records: list[dict[str, str]] = []
    for path in sorted(set(paths)):
        data = path.read_bytes()
        records.append(
            {
                "path": str(path.relative_to(ROOT)),
                "sha256": hashlib.sha256(data).hexdigest(),
            }
        )
    payload = json.dumps(records, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest(), records


def _estimated_tokens(path: Path) -> int:
    return math.ceil(path.stat().st_size / 4)


def build_manifest(root: Path = ROOT) -> dict[str, Any]:
    profile_path = root / PROFILE_PATH.relative_to(ROOT)
    hub_path = root / HUB_PATH.relative_to(ROOT)
    activation_path = root / ACTIVATION_PATH.relative_to(ROOT)
    profile = json.loads(profile_path.read_text(encoding="utf-8"))
    activation = parse_activation(activation_path)
    hub_routes = parse_hub(hub_path)
    errors: list[str] = []
    warnings: list[str] = []
    routes: list[dict[str, Any]] = []
    source_paths = [profile_path, hub_path, activation_path]

    for family_id, family in activation["families"].items():
        family_path = root / family["path"]
        source_paths.append(family_path)
        if not family_path.exists():
            errors.append(f"missing family registry: {family['path']}")
            continue
        family_triggers = hub_routes.get(family["path"], [])
        if family["state"] in ACTIVE_STATES and not family_triggers:
            errors.append(f"active family has no hub route: {family_id}")
        for skill in parse_family_registry(family_path):
            if not skill["triggers"]:
                skill["triggers"] = family_triggers
            skill_gate = activation["skills"].get(skill["id"])
            declared_state = skill_gate["state"] if skill_gate else family["state"]
            effective_state = declared_state
            if family["state"] in INACTIVE_STATES:
                if declared_state in ACTIVE_STATES:
                    errors.append(
                        f"{skill['id']} is {declared_state} while family {family_id} is {family['state']}"
                    )
                effective_state = family["state"]
            skill_file = root / skill["path"]
            if not skill_file.exists():
                errors.append(f"missing skill target: {skill['path']}")
            routes.append(
                {
                    **skill,
                    "family": family_id,
                    "family_state": family["state"],
                    "state": effective_state,
                    "family_triggers": family_triggers,
                }
            )

    known_hub_paths = set(hub_routes)
    known_family_paths = {item["path"] for item in activation["families"].values()}
    for path in sorted(known_hub_paths - known_family_paths):
        errors.append(f"hub route missing activation family: {path}")
    for family_id, family in activation["families"].items():
        if family["state"] in ACTIVE_STATES and family["path"] not in known_hub_paths:
            errors.append(f"activation family missing hub route: {family_id}")

    route_ids = {route["id"] for route in routes}
    for skill_id, gate in activation["skills"].items():
        if skill_id not in route_ids and gate["state"] in ACTIVE_STATES:
            errors.append(f"active/manual skill is absent from family registries: {skill_id}")

    if errors:
        raise RegistryRuntimeError("\n".join(errors))
    fingerprint, source_records = _source_fingerprint(source_paths)
    return {
        "schema_version": 1,
        "source_hash": fingerprint,
        "profile": profile,
        "routes": sorted(routes, key=lambda route: (route["family"], route["id"])),
        "components": activation["components"],
        "sources": source_records,
        "stats": {
            "families": len(activation["families"]),
            "routes": len(routes),
            "active_routes": sum(route["state"] == "active" for route in routes),
            "manual_routes": sum(route["state"] == "manual" for route in routes),
            "inactive_routes": sum(route["state"] in INACTIVE_STATES for route in routes),
        },
        "warnings": warnings,
    }


def load_manifest(path: Path = DEFAULT_MANIFEST) -> dict[str, Any]:
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RegistryRuntimeError(f"cannot load router manifest: {exc}") from exc
    if manifest.get("schema_version") != 1:
        raise RegistryRuntimeError("unsupported router manifest schema")
    return manifest


def _phrase_score(query: str, phrase: str) -> int:
    normalized_phrase = normalize(phrase)
    if not normalized_phrase:
        return 0
    words = normalized_phrase.split()
    if len(words) == 1:
        token = re.escape(words[0])
        return 7 if re.search(rf"(?<![a-z0-9]){token}(?![a-z0-9])", query) else 0
    if normalized_phrase in query:
        return 20 + 3 * len(words)
    query_words = query.split()
    positions: list[int] = []
    cursor = 0
    for word in words:
        try:
            position = query_words.index(word, cursor)
        except ValueError:
            return 0
        positions.append(position)
        cursor = position + 1
    if positions[-1] - positions[0] <= len(words) + 2:
        return 12 + 2 * len(words)
    return 0


def _operation(query: str) -> str:
    rules = [
        ("derive", r"\b(derive|derivation|prove|proof|calculate|equation|formula)\b"),
        ("review", r"\b(review|audit|critique|inspect|evaluate)\b"),
        ("investigate", r"\b(investigate|research|search|find|verify|diagnose)\b"),
        ("implement", r"\b(implement|edit|modify|patch|fix|install|deploy|stage|commit)\b"),
        ("design", r"\b(design|layout|prototype|mockup|architecture)\b"),
        ("write", r"\b(write|draft|rewrite|reply|email|message)\b"),
        ("explain", r"\b(explain|what|why|how|teach|summarize)\b"),
    ]
    for operation, pattern in rules:
        if re.search(pattern, query):
            return operation
    return "discuss"


def _requested_access(query: str) -> str:
    file_write = r"\b(edit|modify|patch|delete|remove|install|deploy|stage|commit)\b"
    build_write = r"\b(implement|create|add|build|generate)\b.*\b(file|code|project|app|site|script|test)\b"
    return "write-requested" if re.search(file_write, query) or re.search(build_write, query) else "read-only"


def _route_allowed_by_intent(route: dict[str, Any], query: str) -> bool:
    if route["family"] == "design":
        consuming = re.search(r"\b(read|summarize|extract|inspect|analyze)\b.*\b(pdf|document|file)\b", query)
        creating = re.search(r"\b(design|create|layout|export|print|poster|visual)\b", query)
        if consuming and not creating:
            return False
    negative_boundary = re.split(r"→|->", route.get("not_for", ""), maxsplit=1)[0]
    for phrase in split_triggers(negative_boundary):
        normalized_phrase = normalize(phrase)
        if len(normalized_phrase.split()) >= 2 and normalized_phrase in query:
            return False
    return True


def _context_packet(manifest: dict[str, Any], operation: str, domain: str, access: str) -> dict[str, Any]:
    profile = manifest["profile"]
    return {
        "operation": operation,
        "domain": domain,
        "requested_access": access,
        "output": {
            "voice": profile["voice"],
            "depth": profile["default_depth"],
            "shape": OUTPUT_SHAPES[operation],
        },
        "response_contract": profile["response_contract"],
    }


def route_request(query: str, manifest: dict[str, Any]) -> dict[str, Any]:
    """Return MATCH or fail-open NORMAL without exposing the original prompt."""
    normalized_query = normalize(query)
    operation = _operation(normalized_query)
    access = _requested_access(normalized_query)
    if re.search(r"\bskillhub\s+normal\b", normalized_query):
        return {
            "result": "NORMAL",
            "reason_code": "USER_NORMAL",
            "context": _context_packet(manifest, operation, "general", access),
        }

    active_matches: list[tuple[int, dict[str, Any], list[str]]] = []
    inactive_matches: list[tuple[int, dict[str, Any]]] = []
    for route in manifest["routes"]:
        if not _route_allowed_by_intent(route, normalized_query):
            continue
        matched = []
        skill_score = 0
        normalized_id = normalize(route["id"])
        if normalized_id and normalized_id in normalized_query:
            skill_score += 100
            matched.append(route["id"])
        for phrase in route["triggers"]:
            score = _phrase_score(normalized_query, phrase)
            if score:
                skill_score += score
                matched.append(phrase)
        if not skill_score:
            continue
        family_score = max(
            (_phrase_score(normalized_query, phrase) for phrase in route["family_triggers"]),
            default=0,
        )
        score = skill_score + min(family_score, 15)
        if route["state"] in ACTIVE_STATES:
            active_matches.append((score, route, matched))
        else:
            inactive_matches.append((score, route))

    if not active_matches:
        reason = "DISABLED_SKILL" if inactive_matches else "NO_SKILL_MATCH"
        return {
            "result": "NORMAL",
            "reason_code": reason,
            "context": _context_packet(manifest, operation, "general", access),
        }

    active_matches.sort(key=lambda item: (-item[0], item[1]["id"]))
    top_score, selected, matched = active_matches[0]
    tied = [item for item in active_matches if item[0] == top_score and item[1]["id"] != selected["id"]]
    if tied:
        return {
            "result": "NORMAL",
            "reason_code": "AMBIGUOUS_SKILL_MATCH",
            "context": _context_packet(manifest, operation, "general", access),
        }

    domain = "mathematics" if selected["id"] == "caveman-math" else FAMILY_DOMAINS.get(selected["family"], "general")
    skill_file = ROOT / selected["path"]
    estimated_tokens = _estimated_tokens(skill_file) if skill_file.exists() else 0
    return {
        "result": "MATCH",
        "reason_code": "ACTIVE_SKILL_MATCH",
        "skill": {
            "id": selected["id"],
            "family": selected["family"],
            "path": selected["path"],
            "state": selected["state"],
            "matched_triggers": matched,
            "estimated_tokens": estimated_tokens,
        },
        "context": _context_packet(manifest, operation, domain, access),
    }


def compact_context(decision: dict[str, Any]) -> str:
    context = decision["context"]
    parts = [
        f"route={decision['result'].lower()}",
        f"reason={decision['reason_code'].lower()}",
        f"operation={context['operation']}",
        f"domain={context['domain']}",
        f"access={context['requested_access']}",
        f"voice={context['output']['voice']}",
        f"shape={context['output']['shape']}",
        "contract=answer first; polished complete sentences; no filler; preserve technical terms; state boundaries when relevant",
    ]
    if decision.get("skill"):
        parts.insert(2, f"skill={decision['skill']['id']}")
        parts.insert(3, f"path={decision['skill']['path']}")
    return "\n".join(parts)
