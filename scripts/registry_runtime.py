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
PROFILE_PATH = ROOT / "interaction-protocol" / "protocol.json"
HUB_PATH = ROOT / "docs" / "00_SKILLS_HUB.md"
ACTIVATION_PATH = ROOT / "registry" / "activation.md"

ACTIVE_STATES = {"active", "manual"}
INACTIVE_STATES = {"off", "hidden", "deprecated"}
VALID_STATES = ACTIVE_STATES | INACTIVE_STATES

FAMILY_DOMAINS = {
    "design": "visual-design",
    "ui-patterns": "product-ux",
    "build-ops": "software",
    "interaction": "communication",
    "theory": "theory",
    "research": "research",
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

REGISTRY_DISCOVERY_PATTERNS = (
    r"\b(list|show|display)\b.*\b(local\s+)?skills?\b",
    r"\bskills?\b.*\b(available|saved|memory|registry|active|activated|manual|disabled|off)\b",
    r"\bskills?\s+ai\s+(status|registry|skills?)\b",
)

SKILLS_AI_CHANGE_PATTERNS = (
    r"\bskills?\s+ai\b",
    r"\bskills ai\b",
    r"\blocal skill (file|registry|router|hub)\b",
    r"\b(interaction protocol|design with claude|theory reference) skill\b",
    r"\b(route skill|registry activation)\b",
)
SKILLS_AI_MAINTENANCE_ACTION_PATTERN = (
    r"\b(add|edit|update|change|modify|move|rename|delete|remove|deprecate|toggle|"
    r"install|uninstall|implement|maintain|maintenance|audit|review|inspect|scan|"
    r"validate|fix|protocol|consistency|graph)\b"
)
NEGATED_ACTION_CLAUSE_PATTERN = (
    r"\b(?:do\s+not|don't|should\s+not|shouldn't|must\s+not|mustn't|never|without|avoid)\b"
    r"[^.;\n]{0,80}|"
    r"\b(?:rather\s+than|instead\s+of)\b[^.;\n]{0,80}|"
    r"\bno\s+(?:external\s+|live\s+|automatic\s+)?"
    r"(?:install|installation|edit|change|delete|removal|commit|stage)\b[^.;\n]{0,50}"
)

SKILL_NORMAL_PATTERN = (
    r"(?:^|\s)#>\s+skill\s+normal(?:\s|$)|"
    r"\bskillhub\s+normal\b|"
    r"\b(?:do\s+not|don't)\s+use\s+(?:any\s+)?(?:local\s+)?skills?\b|"
    r"\banswer\s+normally\s+without\s+(?:skills?\s+ai|(?:a\s+)?local\s+skill)\b|"
    r"\bno\s+(?:local\s+)?skill\s+for\s+this\s+(?:request|task)\b"
)
SKILL_CONTROL_PATTERN = r"(?:^|\s)#>\s+skill\s+([a-z0-9][a-z0-9_-]{0,79})(?:\s|$)"
RECEIPT_CONTROL_PATTERN = r"(?:^|\s)#>\s+receipt\s+(auto|on|off)(?:\s|$)"
DEPTH_CONTROL_PATTERN = r"(?:^|\s)#>\s+depth\s+(brief|standard|detailed)(?:\s|$)"
FORMAT_CONTROL_PATTERN = r"(?:^|\s)#>\s+format\s+([a-z0-9+_-]{1,80})(?:\s|$)"
LOCAL_OVERRIDE_PATTERN = r"^\s*#>\s+override\s+(\S[\s\S]*)$"
LEADING_COMMAND_PATTERN = r"^\s*#>\s+([a-z0-9][a-z0-9-]{0,79})(?=\s|$)"
LEADING_PRESENTATION_CONTROL_PATTERN = (
    r"^\s*#>\s+(?:"
    r"receipt\s+(?:auto|on|off)|"
    r"depth\s+(?:brief|standard|detailed)|"
    r"format\s+[a-z0-9+_-]{1,80}|"
    r"interaction\s+(?:general|math)"
    r")(?=\s|$)"
)
RESEARCH_SCOUT_CANONICAL_PATTERN = (
    r"(?:^|\s)#>\s+skill\s+research[-_]context[-_]scout(?=\s|$)"
)
KNOWN_FORMATS = {"auto", "brief", "code", "equations", "mermaid", "steps", "summary", "table"}

RESEARCH_SCOUT_SKILL_ID = "research-context-scout"
RESEARCH_SCOUT_ACCESS = "write-scoped:research-orientation.md"
RESEARCH_SCOUT_SHAPE = (
    "supervisor result -> evidence or formulation -> decision boundary -> "
    "questions or next investigation -> record path"
)

DESIGN_ROUTED_FAMILIES = {"design", "ui-patterns"}
DESIGN_REQUEST_PATTERN = (
    r"(?:^|\b(?:please|kindly)\s+)(?:design|redesign)\b|"
    r"\b(?:can|could|would|will)\s+you\s+(?:please\s+)?(?:design|redesign)\b|"
    r"\bhelp(?:\s+(?:me|us))?\s+(?:design|redesign)\b|"
    r"\bi\s+(?:want|need)\s+you\s+to\s+(?:design|redesign)\b|"
    r"\b(?:create|make|produce|prepare|build|develop|need|want)\s+"
    r"(?:a|an|the|my|our|this)?\s*design\b|"
    r"\b(?:i\s+am|we\s+are)\s+designing\b"
)
DESIGN_DOMAIN_PATTERN = (
    r"\b(?:visual|layout|ui|ux|interface|user experience|design system|poster|dashboard|"
    r"chart|graph|plot|figure|table|form|navigation|sidebar|menu|mobile|responsive|"
    r"accessibility|a11y|wcag|color|colour|palette|dark mode|theme|typography|font|"
    r"brand|animation|motion|ecommerce|checkout|landing page|healthcare|screen|component|"
    r"wireframe|prototype|print|pdf|content hierarchy|spacing|visual hierarchy|auth ux|"
    r"login flow)\b"
)
NON_VISUAL_DESIGN_TARGET_PATTERN = (
    r"(?:(?:a|an|the|this|my|our|new|better|for)\s+){0,3}"
    r"(?:api|algorithm|code|database|schema|equation|derivation|experiment|study|"
    r"protocol|router|skill|software architecture|data architecture)\b"
)

MATH_EXPLICIT_PATTERN = (
    r"(?:^|\s)#>\s+interaction\s+math(?:\s|$)|"
    r"\b(?:math|mathematics|equation|formula)\s+first\b|"
    r"\buse\s+(?:the\s+)?(?:math|mathematical)\s+(?:interaction\s+)?(?:protocol|style)\b|"
    r"\b(?:derive|show|explain)\s+(?:it\s+)?mathematically\b"
)
MATH_GENERAL_PATTERN = (
    r"(?:^|\s)#>\s+interaction\s+general(?:\s|$)|"
    r"\b(?:use\s+)?normal\s+prose\b|"
    r"\bwithout\s+(?:the\s+)?(?:math|mathematical)\s+(?:interaction\s+)?(?:protocol|style)\b"
)
MATH_ACTION_PATTERN = (
    r"\b(?:solve|derive|prove|calculate|compute|simplify|integrate|differentiate|"
    r"optimize|evaluate|factor|expand)\b"
)
MATH_EXPLAIN_PATTERN = r"\b(?:explain|show|why|how|what)\b"
MATH_OBJECT_PATTERN = (
    r"\b(?:math|mathematical|equation|formula|derivation|proof|theorem|lemma|integral|"
    r"derivative|gradient|matrix|eigenvalue|eigenvector|hamiltonian|lagrangian|ode|pde|"
    r"differential equation|constraint|objective function|probability distribution|"
    r"sequence|series|convergence|stationary point|optimality condition|pontryagin|pmp|"
    r"kkt|jacobian|hessian|tensor|vector|operator)\b"
)
MATH_RESEARCH_PATTERN = (
    r"\b(?:research|paper|article|model|method|result|control problem)\b.*"
    r"\b(?:math|mathematical|analytic|analytical|equation|derivation|proof|hamiltonian|pmp|kkt)\b|"
    r"\b(?:math|mathematical|analytic|analytical|equation|derivation|proof|hamiltonian|pmp|kkt)\b.*"
    r"\b(?:research|paper|article|model|method|result|control problem)\b"
)
NON_MATH_ARTIFACT_PATTERN = (
    r"\b(?:file|filename|path|repository|code|parser|renderer|rendering|field|setting|"
    r"config|configuration|variable name|function name|class name|search|grep|rename)\b"
)


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


def _strip_negated_action_clauses(text: str) -> str:
    """Keep prohibited actions from becoming positive access or route signals."""
    return re.sub(NEGATED_ACTION_CLAUSE_PATTERN, " ", text, flags=re.IGNORECASE)


def _control_routing_prose(text: str) -> str:
    """Remove untrusted artifacts that cannot establish an explicit control."""
    prose = re.sub(r"```[\s\S]*?```", " ", text)
    prose = re.sub(r"`[^`\n]*`", " ", prose)
    prose = re.sub(r"https?://\S+", " ", prose, flags=re.IGNORECASE)
    return prose


def _explicit_skill_id(query: str, manifest: dict[str, Any]) -> str | None:
    """Return one explicitly named route id without guessing a family or alias."""
    slash = re.search(SKILL_CONTROL_PATTERN, query, flags=re.IGNORECASE)
    if slash and slash.group(1).lower() not in {"auto", "normal"}:
        requested = normalize(slash.group(1))
        for route in manifest["routes"]:
            if normalize(route["id"]) == requested:
                return route["id"]
        return ""
    for route in manifest["routes"]:
        identifier = re.escape(route["id"]).replace(r"\-", r"[-_\s]")
        if re.search(
            rf"\buse\s+(?:the\s+)?{identifier}\s+skill\b",
            query,
            flags=re.IGNORECASE,
        ):
            return route["id"]
    return None


def _request_controls(query: str, profile: dict[str, Any]) -> dict[str, Any]:
    """Parse small per-request presentation controls; the prompt remains authoritative."""
    receipt_match = re.search(RECEIPT_CONTROL_PATTERN, query, flags=re.IGNORECASE)
    depth_match = re.search(DEPTH_CONTROL_PATTERN, query, flags=re.IGNORECASE)
    format_match = re.search(FORMAT_CONTROL_PATTERN, query, flags=re.IGNORECASE)
    formats = ["auto"]
    if format_match:
        requested = [item for item in re.split(r"[+_-]", format_match.group(1).lower()) if item]
        accepted = [item for item in requested if item in KNOWN_FORMATS and item != "auto"]
        formats = accepted or ["auto"]
    return {
        "receipt": receipt_match.group(1).lower() if receipt_match else profile.get("receipt", "auto"),
        "depth": depth_match.group(1).lower() if depth_match else profile["default_depth"],
        "format": formats,
        "project_context": "bounded-host-context",
    }


def _local_override(query: str) -> bool:
    """Recognize only a leading current-request command with an instruction."""
    return re.match(LOCAL_OVERRIDE_PATTERN, query, flags=re.IGNORECASE) is not None


def _local_override_context(query: str) -> dict[str, Any]:
    """Return a prompt-free local-protocol override receipt."""
    match = re.match(LOCAL_OVERRIDE_PATTERN, query, flags=re.IGNORECASE)
    instruction = match.group(1) if match else ""
    normalized_instruction = normalize(_strip_negated_action_clauses(instruction))
    return {
        "operation": _operation(normalized_instruction),
        "domain": "general",
        "requested_access": _requested_access(normalized_instruction),
        "interaction": {"mode": "normal", "reason": "user-override"},
        "output": {
            "voice": "host-default",
            "depth": "host-default",
            "shape": "follow-explicit-instruction",
            "format": ["auto"],
        },
        "receipt": "on",
        "project_context": "explicit-targets-only",
        "local_protocol_override": {
            "active": True,
            "scope": "current-request-only",
            "bypasses": [
                "local-skill-routing",
                "local-interaction-formatting",
                "local-repository-procedure",
            ],
            "preserves": [
                "system-and-developer-instructions",
                "host-permissions-and-sandbox",
                "credential-and-external-action-boundaries",
                "destructive-action-safety",
            ],
        },
        "response_contract": ["Follow the explicit instruction within its exact targets and higher-level boundaries."],
    }


def _design_routing_query(text: str) -> str:
    """Return prose that may safely establish explicit design intent."""
    prose = re.sub(r"```[\s\S]*?```", " ", text)
    prose = re.sub(r"`[^`\n]*`", " ", prose)
    prose = re.sub(r"https?://\S+", " ", prose, flags=re.IGNORECASE)
    prose = re.sub(r"\bui\s*/\s*ux\b", " ui ux ", prose, flags=re.IGNORECASE)
    prose = re.sub(r"\S*[/\\_]\S*", " ", prose)
    prose = re.sub(r"\b[\w.-]+\.[a-z0-9]{1,10}\b", " ", prose, flags=re.IGNORECASE)
    return normalize(prose)


def _interaction_routing_prose(text: str) -> str:
    """Remove quoted artifacts that must not establish mathematical intent."""
    prose = re.sub(r"```[\s\S]*?```", " ", text)
    prose = re.sub(r"`[^`\n]*`", " ", prose)
    prose = re.sub(r"https?://\S+", " ", prose, flags=re.IGNORECASE)
    prose = re.sub(r"\S*[/\\_]\S*", " ", prose)
    prose = re.sub(r"\b[\w.-]+\.[a-z0-9]{1,10}\b", " ", prose, flags=re.IGNORECASE)
    return prose.lower()


def _has_math_reasoning_intent(text: str) -> bool:
    prose = _interaction_routing_prose(text)
    normalized = normalize(prose)
    if re.search(MATH_RESEARCH_PATTERN, normalized):
        return True
    has_action = bool(re.search(MATH_ACTION_PATTERN, normalized))
    has_explanation = bool(re.search(MATH_EXPLAIN_PATTERN, normalized))
    has_object = bool(re.search(MATH_OBJECT_PATTERN, normalized))
    has_notation = bool(
        re.search(r"[a-z0-9)\]]\s*(?:=|<=|>=|<|>|\^|\+|-)\s*[-+a-z0-9([]", prose)
    )
    artifact_only = bool(re.search(NON_MATH_ARTIFACT_PATTERN, normalized)) and not has_action
    if artifact_only:
        return False
    return (has_action and (has_object or has_notation)) or (has_explanation and has_object)


def _interaction_mode(query: str, manifest: dict[str, Any]) -> tuple[str, str]:
    normalized = normalize(query)
    control_query = _control_routing_prose(query)
    family_state = manifest.get("families", {}).get("interaction", {}).get("state", "off")
    general_state = manifest.get("components", {}).get("interaction.general", {}).get("state", "off")
    math_state = manifest.get("components", {}).get("interaction.math", {}).get("state", "off")
    if family_state in INACTIVE_STATES:
        return "normal", "family-disabled"
    if re.search(MATH_GENERAL_PATTERN, control_query, flags=re.IGNORECASE):
        return ("general", "explicit-general") if general_state in ACTIVE_STATES else ("normal", "general-disabled")
    explicit_math = bool(re.search(MATH_EXPLICIT_PATTERN, control_query, flags=re.IGNORECASE))
    if math_state == "active" and (explicit_math or _has_math_reasoning_intent(query)):
        return "math", "explicit-math" if explicit_math else "automatic-math"
    if math_state == "manual" and explicit_math:
        return "math", "explicit-math"
    if general_state in ACTIVE_STATES:
        return "general", "default-general"
    return "normal", "general-disabled"


def _has_explicit_design_intent(query: str) -> bool:
    request = re.search(DESIGN_REQUEST_PATTERN, query)
    if request is None:
        return False
    following = query[request.end() :].lstrip()
    if re.match(NON_VISUAL_DESIGN_TARGET_PATTERN, following):
        return False
    nearby = query[max(0, request.start() - 120) : request.end() + 180]
    return bool(re.search(DESIGN_DOMAIN_PATTERN, nearby))


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
        "Interaction Protocol Components": "components",
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


def parse_command_aliases(path: Path) -> list[dict[str, str]]:
    """Read exact leading command aliases declared by one family registry."""
    aliases: list[dict[str, str]] = []
    for section, cells in _read_sections(path):
        if section != "Command aliases" or cells[0] == "command" or len(cells) < 4:
            continue
        command = cells[0].strip("`").lower()
        skill_id = cells[1].strip("`")
        mode = cells[2].strip("`").lower()
        boundary = cells[3]
        if not re.fullmatch(r"#>\s+[a-z0-9][a-z0-9-]{0,79}", command):
            raise RegistryRuntimeError(f"invalid command alias {command} in {path.name}")
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,79}", skill_id):
            raise RegistryRuntimeError(f"invalid command alias target {skill_id} in {path.name}")
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,39}", mode):
            raise RegistryRuntimeError(f"invalid command alias mode {mode} in {path.name}")
        aliases.append(
            {
                "command": command,
                "skill_id": skill_id,
                "mode": mode,
                "boundary": boundary,
            }
        )
    return aliases


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
    command_aliases: list[dict[str, str]] = []
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
        for alias in parse_command_aliases(family_path):
            command_aliases.append({**alias, "family": family_id})

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

    aliases_seen: set[str] = set()
    route_by_id = {route["id"]: route for route in routes}
    for alias in command_aliases:
        command = alias["command"]
        if command in aliases_seen:
            errors.append(f"duplicate command alias: {command}")
        aliases_seen.add(command)
        target = route_by_id.get(alias["skill_id"])
        if target is None:
            errors.append(f"command alias target is absent: {command} -> {alias['skill_id']}")
        elif target["state"] not in ACTIVE_STATES:
            errors.append(f"command alias target is disabled: {command} -> {alias['skill_id']}")

    if errors:
        raise RegistryRuntimeError("\n".join(errors))
    fingerprint, source_records = _source_fingerprint(source_paths)
    return {
        "schema_version": 1,
        "source_hash": fingerprint,
        "profile": profile,
        "families": activation["families"],
        "routes": sorted(routes, key=lambda route: (route["family"], route["id"])),
        "command_aliases": sorted(command_aliases, key=lambda alias: alias["command"]),
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


def _strip_leading_presentation_controls(query: str) -> str:
    """Allow presentation controls before the first task directive."""
    remainder = query
    while True:
        match = re.match(LEADING_PRESENTATION_CONTROL_PATTERN, remainder, flags=re.IGNORECASE)
        if match is None:
            return remainder
        remainder = remainder[match.end():]


def _leading_command_alias(query: str, manifest: dict[str, Any]) -> dict[str, Any] | None:
    """Resolve one registry alias after optional leading presentation controls."""
    candidate = _strip_leading_presentation_controls(query)
    match = re.match(LEADING_COMMAND_PATTERN, candidate, flags=re.IGNORECASE)
    if match is None:
        return None
    command = f"#> {match.group(1).lower()}"
    for alias in manifest.get("command_aliases", []):
        if alias["command"] == command:
            resolved = dict(alias)
            first_argument = candidate[match.end():].lstrip()
            if first_argument.startswith("-"):
                resolved["malformed"] = "option-like-first-argument"
            return resolved
    return None


def _canonical_research_mode(query: str, explicit_skill_id: str | None) -> tuple[str | None, bool]:
    """Return a validated canonical Scout mode and whether its directive is malformed."""
    if explicit_skill_id != RESEARCH_SCOUT_SKILL_ID:
        return None, False
    match = re.search(RESEARCH_SCOUT_CANONICAL_PATTERN, query, flags=re.IGNORECASE)
    if match is None:
        return None, False
    remainder = query[match.end():].lstrip()
    token = re.match(r"([^\s]+)", remainder)
    if token is None:
        return None, True
    mode = token.group(1).lower()
    return (mode, False) if mode in {"initial", "deepen"} else (None, True)


def _operation(query: str) -> str:
    if re.search(r"\b(?:write|draft|rewrite)\b.*\bcommit message\b", query):
        return "write"
    if re.search(
        r"^(?:please\s+)?(?:implement|build|create|add|edit|modify|patch|fix|install|deploy|stage|commit)\b",
        query,
    ):
        return "implement"
    rules = [
        ("review", r"\b(review|audit|critique|inspect|evaluate)\b"),
        ("investigate", r"\b(investigate|research|search|find|verify|diagnose)\b"),
        ("implement", r"\b(implement|build|create|add|edit|modify|patch|fix|install|deploy|stage|commit)\b"),
        ("design", r"\b(design|layout|prototype|mockup|architecture)\b"),
        ("derive", r"\b(derive|derivation|prove|proof|calculate|compute|solve|equation|formula)\b"),
        ("write", r"\b(write|draft|rewrite|reply|email|message)\b"),
        ("explain", r"\b(explain|what|why|how|teach|summarize)\b"),
    ]
    for operation, pattern in rules:
        if re.search(pattern, query):
            return operation
    return "discuss"


def _requested_access(query: str) -> str:
    query = normalize(_strip_negated_action_clauses(query))
    file_write = r"\b(edit|modify|patch|fix|delete|remove|install|deploy|stage|commit(?!\s+message))\b"
    build_write = r"\b(implement|create|add|build|generate)\b.*\b(file|code|project|app|site|script|test)\b"
    maintenance_write = (
        r"\b(implement|add|update|modify|move|rename|delete|remove|deprecate|toggle)\b.*"
        r"\b(skills? ai|skill|registry|router|protocol|graph|scanner)\b"
    )
    return "write-requested" if any(
        re.search(pattern, query) for pattern in (file_write, build_write, maintenance_write)
    ) else "read-only"


def _route_allowed_by_intent(route: dict[str, Any], query: str) -> bool:
    if route["family"] == "design":
        consuming = re.search(r"\b(read|summarize|extract|inspect|analyze)\b.*\b(pdf|document|file)\b", query)
        creating = re.search(r"\b(design|create|layout|export|print|poster|visual)\b", query)
        if consuming and not creating:
            return False
    if route["family"] == "theory":
        implementation_artifact = re.search(
            r"\b(?:fix|debug|implement|code|parser|renderer|rendering|component|field|setting|config)\b",
            query,
        )
        theory_request = re.search(
            r"\b(?:theory|theorem|proof|derive|derivation|chapter|outline|notes|reference|refresher)\b",
            query,
        )
        if implementation_artifact and not theory_request:
            return False
    negative_boundary = re.split(r"→|->", route.get("not_for", ""), maxsplit=1)[0]
    for phrase in split_triggers(negative_boundary):
        normalized_phrase = normalize(phrase)
        if len(normalized_phrase.split()) >= 2 and normalized_phrase in query:
            return False
    return True


def _context_packet(
    manifest: dict[str, Any],
    operation: str,
    domain: str,
    access: str,
    interaction_mode: str,
    interaction_reason: str,
    controls: dict[str, Any] | None = None,
) -> dict[str, Any]:
    profile = manifest["profile"]
    contracts: list[str] = []
    if interaction_mode in {"general", "math"}:
        contracts.extend(profile["response_contract"])
    if interaction_mode == "math":
        contracts.extend(profile["math"]["response_contract"])
        shape = profile["math"]["shape"]
    else:
        shape = OUTPUT_SHAPES[operation]
    return {
        "operation": operation,
        "domain": domain,
        "requested_access": access,
        "interaction": {
            "mode": interaction_mode,
            "reason": interaction_reason,
        },
        "output": {
            "voice": profile["voice"] if interaction_mode != "normal" else "host-default",
            "depth": (controls or {}).get("depth", profile["default_depth"]),
            "shape": shape,
            "format": (controls or {}).get("format", ["auto"]),
        },
        "receipt": (controls or {}).get("receipt", profile.get("receipt", "auto")),
        "project_context": (controls or {}).get("project_context", "bounded-host-context"),
        "response_contract": contracts,
    }


def _routing(fit: int, fit_reason: str, *, candidates: list[dict[str, str]] | None = None) -> dict[str, Any]:
    packet: dict[str, Any] = {"fit": fit, "fit_reason": fit_reason}
    if candidates:
        packet["candidates"] = candidates
        packet["clarification"] = {
            "required": True,
            "choices": [candidate["id"] for candidate in candidates] + ["normal"],
            "message": "Two local skills fit materially differently. Ask the user to choose one option or normal, then continue the original task.",
        }
    return packet


def _public_purpose(value: str) -> str:
    """Return one bounded display label, never executable or multiline content."""
    return re.sub(r"[\x00-\x1f\x7f`{}]", " ", value).strip()[:160]


def registry_summary(manifest: dict[str, Any], *, include_hidden: bool = False) -> dict[str, Any]:
    """Return live registry metadata without loading or exposing skill bodies."""
    route_groups = {state: [] for state in sorted(VALID_STATES)}
    for route in manifest["routes"]:
        route_groups[route["state"]].append(route["id"])
    family_groups = {state: [] for state in sorted(VALID_STATES)}
    for family_id, family in manifest.get("families", {}).items():
        family_groups[family["state"]].append(family_id)
    component_groups = {state: [] for state in sorted(VALID_STATES)}
    for component_id, component in manifest.get("components", {}).items():
        component_groups[component["state"]].append(component_id)
    for groups in (route_groups, family_groups, component_groups):
        for values in groups.values():
            values.sort()

    visible_states = ("active", "manual", "off")
    routes = {state: route_groups[state] for state in visible_states}
    families = {state: family_groups[state] for state in visible_states}
    components = {state: component_groups[state] for state in visible_states}
    if include_hidden:
        for state in ("hidden", "deprecated"):
            routes[state] = route_groups[state]
            families[state] = family_groups[state]
            components[state] = component_groups[state]
    return {
        "source_hash": manifest["source_hash"],
        "route_counts": {state: len(values) for state, values in route_groups.items()},
        "routes": routes,
        "family_gates": families,
        "component_gates": components,
        "command_aliases": [
            {
                "command": alias["command"],
                "skill_id": alias["skill_id"],
                "mode": alias["mode"],
            }
            for alias in manifest.get("command_aliases", [])
        ],
        "hidden_policy": "hidden and deprecated identifiers are omitted unless maintenance explicitly requests them",
    }


def _is_registry_discovery(query: str) -> bool:
    if _requested_access(query) == "write-requested":
        return False
    return any(re.search(pattern, query) for pattern in REGISTRY_DISCOVERY_PATTERNS)


def _targets_skills_ai_change(query: str, access: str) -> bool:
    return access == "write-requested" and any(
        re.search(pattern, query) for pattern in SKILLS_AI_CHANGE_PATTERNS
    )


def _is_skills_ai_maintenance(query: str) -> bool:
    return any(re.search(pattern, query) for pattern in SKILLS_AI_CHANGE_PATTERNS) and bool(
        re.search(SKILLS_AI_MAINTENANCE_ACTION_PATTERN, query)
    )


def _apply_change_boundary(context: dict[str, Any], query: str, access: str) -> None:
    if not _targets_skills_ai_change(query, access):
        return
    context["skills_ai_change_boundary"] = {
        "mode": "request-only-outside-maintenance-workspace",
        "request_command": "python3 /Users/billabobz/skills_ai/scripts/create_change_request.py --stdin-json",
        "maintenance_workspace": "/Users/billabobz/skills_ai",
        "rule": "An external task may create one pending Markdown request but must not edit canonical Skills AI files.",
    }


def _apply_selected_skill_context(context: dict[str, Any], skill_id: str) -> None:
    """Apply a skill's narrow public context without changing global defaults."""
    if skill_id != RESEARCH_SCOUT_SKILL_ID:
        return
    context["requested_access"] = RESEARCH_SCOUT_ACCESS
    context["output"]["shape"] = RESEARCH_SCOUT_SHAPE


def route_request(query: str, manifest: dict[str, Any]) -> dict[str, Any]:
    """Return MATCH or fail-open NORMAL without exposing the original prompt."""
    if _local_override(query):
        return {
            "result": "NORMAL",
            "reason_code": "USER_OVERRIDE",
            "routing": _routing(0, "user-local-protocol-override"),
            "context": _local_override_context(query),
        }
    normalized_query = normalize(_strip_negated_action_clauses(query))
    design_query = _design_routing_query(query)
    design_intent = _has_explicit_design_intent(design_query)
    operation = _operation(normalized_query)
    access = _requested_access(normalized_query)
    interaction_mode, interaction_reason = _interaction_mode(query, manifest)
    control_query = _control_routing_prose(query)
    controls = _request_controls(control_query, manifest["profile"])
    explicit_skill_id = _explicit_skill_id(control_query, manifest)
    command_alias = None
    if explicit_skill_id is None:
        command_alias = _leading_command_alias(query, manifest)
        if command_alias is not None:
            explicit_skill_id = command_alias["skill_id"]
    canonical_research_mode, invalid_research_mode = _canonical_research_mode(
        control_query,
        explicit_skill_id,
    )
    maintenance = _is_skills_ai_maintenance(normalized_query)
    if _is_registry_discovery(normalized_query) and not maintenance:
        context = _context_packet(
            manifest, "explain", "skills-registry", "read-only", interaction_mode, interaction_reason, controls
        )
        return {
            "result": "NORMAL",
            "reason_code": "REGISTRY_STATUS",
            "registry": registry_summary(manifest),
            "routing": _routing(0, "registry-discovery"),
            "context": context,
        }
    if re.search(SKILL_NORMAL_PATTERN, control_query, flags=re.IGNORECASE) and not maintenance:
        context = _context_packet(
            manifest, operation, "general", access, interaction_mode, interaction_reason, controls
        )
        _apply_change_boundary(context, normalized_query, access)
        return {
            "result": "NORMAL",
            "reason_code": "USER_NORMAL",
            "routing": _routing(0, "user-opt-out"),
            "context": context,
        }
    if maintenance:
        context = _context_packet(
            manifest, operation, "skills-registry", access, interaction_mode, interaction_reason, controls
        )
        _apply_change_boundary(context, normalized_query, access)
        return {
            "result": "NORMAL",
            "reason_code": "SKILLS_AI_MAINTENANCE",
            "routing": _routing(0, "maintenance-bypass"),
            "context": context,
        }
    if explicit_skill_id == "":
        context = _context_packet(
            manifest, operation, "general", access, interaction_mode, interaction_reason, controls
        )
        return {
            "result": "NORMAL",
            "reason_code": "UNKNOWN_SKILL_REQUEST",
            "routing": _routing(0, "unknown-explicit-skill"),
            "context": context,
        }

    if command_alias is not None and command_alias.get("malformed"):
        context = _context_packet(
            manifest, operation, "general", access, interaction_mode, interaction_reason, controls
        )
        context["response_contract"].append(
            "Tell the user the Scout directive was rejected; use #> scout-again <path> for deepening."
        )
        return {
            "result": "NORMAL",
            "reason_code": "MALFORMED_COMMAND_ALIAS",
            "routing": _routing(0, "malformed-command-alias"),
            "context": context,
        }

    if invalid_research_mode:
        context = _context_packet(
            manifest, operation, "research", access, interaction_mode, interaction_reason, controls
        )
        context["response_contract"].append(
            "Tell the user that canonical Research Context Scout requires mode initial or deepen."
        )
        return {
            "result": "NORMAL",
            "reason_code": "INVALID_SKILL_MODE",
            "routing": _routing(0, "invalid-skill-mode"),
            "context": context,
        }

    active_matches: list[tuple[int, dict[str, Any], list[str]]] = []
    inactive_matches: list[tuple[int, dict[str, Any]]] = []
    for route in manifest["routes"]:
        explicitly_selected = explicit_skill_id == route["id"]
        if explicit_skill_id is not None and not explicitly_selected:
            continue
        if route["state"] == "manual" and not explicitly_selected:
            continue
        route_query = normalized_query
        if route["family"] in DESIGN_ROUTED_FAMILIES:
            if not design_intent and not explicitly_selected:
                continue
            route_query = design_query
        if not explicitly_selected and not _route_allowed_by_intent(route, route_query):
            continue
        matched = []
        skill_score = 0
        if explicitly_selected:
            skill_score += 100
            matched.append(command_alias["command"] if command_alias else route["id"])
        for phrase in route["triggers"]:
            score = _phrase_score(route_query, phrase)
            if score:
                skill_score += score
                matched.append(phrase)
        if not skill_score:
            continue
        family_score = max(
            (_phrase_score(route_query, phrase) for phrase in route["family_triggers"]),
            default=0,
        )
        score = skill_score + min(family_score, 15)
        if route["state"] in ACTIVE_STATES:
            active_matches.append((score, route, matched))
        else:
            inactive_matches.append((score, route))

    if not active_matches:
        reason = "DISABLED_SKILL" if inactive_matches else "NO_SKILL_MATCH"
        fallback_domain = "mathematics" if interaction_mode == "math" else "general"
        context = _context_packet(
            manifest, operation, fallback_domain, access, interaction_mode, interaction_reason, controls
        )
        _apply_change_boundary(context, normalized_query, access)
        return {
            "result": "NORMAL",
            "reason_code": reason,
            "routing": _routing(0, "disabled-match" if inactive_matches else "no-match"),
            "context": context,
        }

    active_matches.sort(key=lambda item: (-item[0], item[1]["id"]))
    top_score, selected, matched = active_matches[0]
    tied = [item for item in active_matches if item[0] == top_score and item[1]["id"] != selected["id"]]
    if tied:
        fallback_domain = "mathematics" if interaction_mode == "math" else "general"
        context = _context_packet(
            manifest, operation, fallback_domain, access, interaction_mode, interaction_reason, controls
        )
        _apply_change_boundary(context, normalized_query, access)
        candidates = [selected, *(item[1] for item in tied)]
        return {
            "result": "NORMAL",
            "reason_code": "AMBIGUOUS_SKILL_MATCH",
            "routing": _routing(
                1,
                "equal-top-score",
                candidates=[
                    {
                        "id": candidate["id"],
                        "family": candidate["family"],
                        "purpose": _public_purpose(candidate["description"]),
                    }
                    for candidate in candidates
                ],
            ),
            "context": context,
        }

    domain = FAMILY_DOMAINS.get(selected["family"], "general")
    if interaction_mode == "math" and domain in {"general", "communication"}:
        domain = "mathematics"
    skill_file = ROOT / selected["path"]
    estimated_tokens = _estimated_tokens(skill_file) if skill_file.exists() else 0
    context = _context_packet(
        manifest, operation, domain, access, interaction_mode, interaction_reason, controls
    )
    _apply_selected_skill_context(context, selected["id"])
    _apply_change_boundary(context, normalized_query, access)
    if command_alias is not None:
        context["skill_invocation"] = {
            "command": command_alias["command"],
            "mode": command_alias["mode"],
            "scope": "current-request-only",
        }
    elif canonical_research_mode is not None:
        context["skill_invocation"] = {
            "command": "#> skill research-context-scout",
            "mode": canonical_research_mode,
            "scope": "current-request-only",
        }
    return {
        "result": "MATCH",
        "reason_code": "ACTIVE_SKILL_MATCH",
        "routing": _routing(
            3 if explicit_skill_id else 2,
            "explicit-command-alias"
            if command_alias
            else "explicit-skill"
            if explicit_skill_id
            else "unique-context-match",
        ),
        "skill": {
            "id": selected["id"],
            "family": selected["family"],
            "path": selected["path"],
            "state": selected["state"],
            "matched_triggers": matched,
            "estimated_tokens": estimated_tokens,
        },
        "context": context,
    }


def compact_context(decision: dict[str, Any]) -> str:
    context = decision["context"]
    routing = decision.get("routing", {})
    parts = [
        f"route={decision['result'].lower()}",
        f"reason={decision['reason_code'].lower()}",
    ]
    if decision.get("skill"):
        parts.extend(
            (
                f"skill={decision['skill']['id']}",
                f"path={decision['skill']['path']}",
            )
        )
    invocation = context.get("skill_invocation")
    if invocation:
        parts.extend(
            (
                f"command={invocation['command']}",
                f"mode={invocation['mode']}",
            )
        )
    parts.extend(
        (
            f"fit={routing.get('fit', 0)}/3",
            f"fit_reason={routing.get('fit_reason', 'legacy-or-fail-open')}",
            f"operation={context['operation']}",
            f"domain={context['domain']}",
            f"access={context['requested_access']}",
            f"interaction={context['interaction']['mode']}",
            f"interaction_reason={context['interaction']['reason']}",
            f"voice={context['output']['voice']}",
            f"shape={context['output']['shape']}",
            f"depth={context['output'].get('depth', 'standard')}",
            f"format={'+'.join(context['output'].get('format', ['auto']))}",
            f"receipt={context.get('receipt', 'auto')}",
            f"project_context={context.get('project_context', 'bounded-host-context')}",
            f"contract={' '.join(context.get('response_contract', []))}",
        )
    )
    if decision.get("registry"):
        counts = decision["registry"]["route_counts"]
        parts.insert(2, f"registry_source={decision['registry']['source_hash'][:12]}")
        parts.insert(
            3,
            f"registry_routes=active:{counts['active']},manual:{counts['manual']},off:{counts['off']}",
        )
    return "\n".join(parts)
