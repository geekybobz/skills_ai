#!/usr/bin/env python3
"""Compile skill discovery metadata. Semantic coordination belongs to the host."""
from __future__ import annotations
import hashlib
import json
import math
import re
import sys
from pathlib import Path
from typing import Any, Iterable
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'runtime'))
DEFAULT_MANIFEST=ROOT/'runtime/manifest.json'
HUB_PATH=ROOT/'docs/00_SKILLS_HUB.md'
ACTIVATION_PATH=ROOT/'registry/activation.md'
ACTIVE_STATES={'active','manual'}
INACTIVE_STATES={'off','hidden','deprecated'}
VALID_STATES=ACTIVE_STATES|INACTIVE_STATES
VALID_PACKAGE_ROLES={'interaction','task'}
ORCHESTRATOR_ID='skills-orchestrator'
INTERACTION_PACKAGE_ID='interaction-protocol'
VALID_REGISTRY_VIEWS={'auto','inventory','catalog','diagnostic'}
REGISTRY_VIEW_MAX_BYTES={'inventory':2048,'catalog':8192,'diagnostic':32768}
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
        "orchestrator": {},
        "packages": {},
        "families": {},
        "skills": {},
        "components": {},
    }
    section_kinds = {
        "Skills Orchestrator": "orchestrator",
        "Skill Packages": "packages",
        "Family Gates": "families",
        "Skill Gates": "skills",
        "Interaction Protocol Components": "components",
        "Quantum Job Collector Components": "components",
    }
    for section, cells in _read_sections(path):
        kind = section_kinds.get(section)
        if not kind or cells[0] == "id" or len(cells) < 4:
            continue
        row_id, state, route, fourth = cells[:4]
        state = state.strip("`")
        if state not in VALID_STATES:
            raise RegistryRuntimeError(f"invalid state {state} for {row_id}")
        route_path, _ = extract_route(route)
        if row_id in result[kind]:
            raise RegistryRuntimeError(f"duplicate activation id: {row_id}")
        if kind == "orchestrator":
            result[kind][row_id] = {
                "state": state,
                "path": route_path,
                "boundary": fourth,
            }
        elif kind == "packages":
            role = fourth.strip("`")
            if role not in VALID_PACKAGE_ROLES:
                raise RegistryRuntimeError(f"invalid package role {role} for {row_id}")
            boundary = cells[4] if len(cells) > 4 else ""
            result[kind][row_id] = {
                "state": state,
                "path": route_path,
                "role": role,
                "boundary": boundary,
            }
        elif kind == "families":
            package = cells[4].strip("`") if len(cells) > 4 else ""
            result[kind][row_id] = {
                "state": state,
                "path": route_path,
                "boundary": fourth,
                "package": package,
            }
        else:
            result[kind][row_id] = {
                "state": state,
                "path": route_path,
                "boundary": fourth,
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
        if (
            section not in {"Skills", "Internal Capabilities", "Package Capability"}
            or cells[0] in {"skill", "route", "capability"}
            or len(cells) < 4
        ):
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

def _source_fingerprint(paths: Iterable[Path], *, root: Path = ROOT) -> tuple[str, list[dict[str, str]]]:
    records: list[dict[str, str]] = []
    for path in sorted(set(paths)):
        data = path.read_bytes()
        records.append(
            {
                "path": str(path.relative_to(root)),
                "sha256": hashlib.sha256(data).hexdigest(),
            }
        )
    payload = json.dumps(records, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest(), records

def _estimated_tokens(path: Path) -> int:
    return math.ceil(path.stat().st_size / 4)

def build_manifest(root: Path = ROOT) -> dict[str, Any]:
    hub_path = root / HUB_PATH.relative_to(ROOT)
    activation_path = root / ACTIVATION_PATH.relative_to(ROOT)
    activation = parse_activation(activation_path)
    hub_routes = parse_hub(hub_path)
    errors: list[str] = []
    warnings: list[str] = []
    routes: list[dict[str, Any]] = []
    command_aliases: list[dict[str, str]] = []
    source_paths = [hub_path, activation_path]

    orchestrators = activation["orchestrator"]
    if set(orchestrators) != {ORCHESTRATOR_ID}:
        errors.append("exactly one skills-orchestrator control plane is required")
    orchestrator = orchestrators.get(ORCHESTRATOR_ID, {})
    if orchestrator.get("state") != "active":
        errors.append("skills-orchestrator must be active")
    orchestrator_path = orchestrator.get("path")
    if not isinstance(orchestrator_path, str) or not (root / orchestrator_path).exists():
        errors.append(f"missing orchestrator target: {ORCHESTRATOR_ID} -> {orchestrator_path or '(missing)'}")

    packages = activation["packages"]
    for package_id, package in packages.items():
        if not (root / package["path"]).exists():
            errors.append(f"missing package target: {package_id} -> {package['path']}")

    for family_id, family in activation["families"].items():
        package_id = family.get("package", "")
        package = packages.get(package_id)
        if package is None:
            errors.append(f"family {family_id} references unknown package: {package_id or '(missing)'}")
        elif package["role"] not in {"task", "interaction"}:
            errors.append(f"family {family_id} references non-routable package: {package_id}")
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
            package_state = package["state"] if package else family["state"]
            declared_state = skill_gate["state"] if skill_gate else package_state
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
                    "package": package_id,
                    "family": family_id,
                    "family_state": family["state"],
                    "state": effective_state,
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
    fingerprint, source_records = _source_fingerprint(source_paths, root=root)
    return {
        "schema_version": 1,
        "source_hash": fingerprint,
        "packages": packages,
        "orchestrator": {
            "id": ORCHESTRATOR_ID,
            **orchestrator,
            "mode": "model-led",
        },
        "families": activation["families"],
        "routes": sorted(routes, key=lambda route: (route["family"], route["id"])),
        "command_aliases": sorted(command_aliases, key=lambda alias: alias["command"]),
        "components": activation["components"],
        "sources": source_records,
        "stats": {
            "packages": len(packages),
            "active_packages": sum(package["state"] == "active" for package in packages.values()),
            "manual_packages": sum(package["state"] == "manual" for package in packages.values()),
            "inactive_packages": sum(package["state"] in INACTIVE_STATES for package in packages.values()),
            "families": len(activation["families"]),
            "routes": len(routes),
            "active_routes": sum(route["state"] == "active" for route in routes),
            "manual_routes": sum(route["state"] == "manual" for route in routes),
            "inactive_routes": sum(route["state"] in INACTIVE_STATES for route in routes),
        },
        "warnings": warnings,
    }

def load_manifest(path: Path = DEFAULT_MANIFEST) -> dict[str, Any]:
    from model_context import read_json, read_relative, ContextError
    try:
        manifest = read_json(path.parent, path.name, maximum=1024*1024)
        if manifest.get('schema_version') != 1:
            raise RegistryRuntimeError('unsupported manifest schema')
        if not isinstance(manifest.get('source_hash'), str) or not re.fullmatch(r'[a-f0-9]{64}',manifest['source_hash']):
            raise RegistryRuntimeError('invalid manifest content identity')
        sources=manifest.get('sources')
        if not isinstance(sources,list) or not 2<=len(sources)<=514:
            raise RegistryRuntimeError('INVALID_MANIFEST_BINDINGS')
        root=path.parent.parent if path.parent.name=='runtime' else path.parent
        seen=set();total=0
        for source in sources:
            if not isinstance(source,dict) or set(source)!={'path','sha256'} or not isinstance(source['path'],str) or not isinstance(source['sha256'],str):
                raise RegistryRuntimeError('INVALID_MANIFEST_BINDINGS')
            name=source['path']
            if name in seen or (name!='docs/00_SKILLS_HUB.md' and not re.fullmatch(r'registry/[a-z][a-z0-9_-]*\.md',name)) or not re.fullmatch(r'[a-f0-9]{64}',source['sha256']):
                raise RegistryRuntimeError('INVALID_MANIFEST_BINDINGS')
            seen.add(name)
            raw=read_relative(root,name,maximum=65536);total+=len(raw)
            if total>1024*1024:raise RegistryRuntimeError('MANIFEST_SOURCES_TOO_LARGE')
            if hashlib.sha256(raw).hexdigest()!=source['sha256']:raise RegistryRuntimeError('STALE_MANIFEST')
        if not {'docs/00_SKILLS_HUB.md','registry/activation.md'}<=seen or hashlib.sha256(json.dumps(sources,sort_keys=True,separators=(',',':')).encode()).hexdigest()!=manifest['source_hash']:
            raise RegistryRuntimeError('INVALID_MANIFEST_BINDINGS')
        packages=manifest.get('packages')
        if not isinstance(packages,dict) or len(packages)>512:
            raise RegistryRuntimeError('invalid package metadata')
        for name, package in packages.items():
            if not isinstance(package,dict) or package.get('state') not in VALID_STATES or not isinstance(package.get('path'),str):
                raise RegistryRuntimeError('invalid package metadata')
        routes=manifest.get('routes');aliases=manifest.get('command_aliases')
        if not isinstance(routes,list) or not isinstance(aliases,list):
            raise RegistryRuntimeError('invalid capability metadata')
        for route in routes:
            if not isinstance(route,dict) or route.get('package') not in packages or route.get('state') not in VALID_STATES or any(not isinstance(route.get(k),str) for k in ('id','path','description')):
                raise RegistryRuntimeError('invalid capability metadata')
        for alias in aliases:
            if not isinstance(alias,dict) or alias.get('skill_id') not in packages or any(not isinstance(alias.get(k),str) for k in ('command','mode')):
                raise RegistryRuntimeError('invalid alias metadata')
        return manifest
    except (ContextError, OSError, ValueError, TypeError, RecursionError) as exc:
        raise RegistryRuntimeError('cannot load bounded manifest') from exc

def _public_purpose(value: str) -> str:
    """Return one bounded display label, never executable or multiline content."""
    return re.sub(r"[\x00-\x1f\x7f`{}]", " ", value).strip()[:160]

def registry_summary(
    manifest: dict[str, Any],
    *,
    include_hidden: bool = False,
    view: str = "inventory",
) -> dict[str, Any]:
    """Return one bounded live metadata view without loading skill bodies."""
    if view not in VALID_REGISTRY_VIEWS - {"auto"}:
        raise RegistryRuntimeError(f"invalid registry view: {view}")

    skill_groups = {state: [] for state in sorted(VALID_STATES)}
    skill_roles: dict[str, str] = {}
    for skill_id, package in manifest.get("packages", {}).items():
        skill_groups[package["state"]].append(skill_id)
        skill_roles[skill_id] = package["role"]
    for values in skill_groups.values():
        values.sort()

    visible_states = ["active", "manual", "off"]
    if include_hidden:
        visible_states.extend(("hidden", "deprecated"))
    skills = {state: skill_groups[state] for state in visible_states}
    orchestrator = manifest.get("orchestrator", {})
    result: dict[str, Any] = {
        "view": view,
        "source_hash": manifest["source_hash"],
        "orchestrator": {
            "id": orchestrator.get("id", ORCHESTRATOR_ID),
            "mode": orchestrator.get("mode", "model-led"),
            "state": orchestrator.get("state", "active"),
            "command": "#> orchestrator",
        },
        "skill_counts": {state: len(values) for state, values in skill_groups.items()},
        "skills": skills,
        "skill_roles": skill_roles,
        "hidden_policy": "hidden and deprecated identifiers are omitted unless maintenance explicitly requests them",
    }

    if view in {"catalog", "diagnostic"}:
        records: list[dict[str, Any]] = []
        for skill_id in sorted(manifest.get("packages", {})):
            package = manifest["packages"][skill_id]
            if package["state"] not in visible_states:
                continue
            families = sorted(
                family_id
                for family_id, family in manifest.get("families", {}).items()
                if family.get("package") == skill_id
            )
            all_triggers = sorted(
                {
                    trigger
                    for route in manifest.get("routes", [])
                    if route.get("package") == skill_id
                    for trigger in route.get("family_triggers", route.get("triggers", []))
                }
            )
            records.append(
                {
                    "id": skill_id,
                    "state": package["state"],
                    "role": package["role"],
                    "purpose": _public_purpose(package.get("boundary", "")),
                    "families": families,
                    "triggers": all_triggers[:16],
                    "trigger_count": len(all_triggers),
                    "triggers_truncated": len(all_triggers) > 16,
                }
            )
        result["skill_records"] = records

    if view == "diagnostic":
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
        result.update(
            {
                "route_counts": {state: len(values) for state, values in route_groups.items()},
                "routes": {state: route_groups[state] for state in visible_states},
                "family_gates": {state: family_groups[state] for state in visible_states},
                "component_gates": {state: component_groups[state] for state in visible_states},
                "command_aliases": [
                    {
                        "command": alias["command"],
                        "skill_id": alias["skill_id"],
                        "mode": alias["mode"],
                    }
                    for alias in manifest.get("command_aliases", [])
                ],
            }
        )
    encoded_size = len(json.dumps(result, sort_keys=True, separators=(",", ":")).encode())
    if encoded_size > REGISTRY_VIEW_MAX_BYTES[view]:
        raise RegistryRuntimeError(
            f"registry {view} view exceeds {REGISTRY_VIEW_MAX_BYTES[view]} bytes"
        )
    return result
