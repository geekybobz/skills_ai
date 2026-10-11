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
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'orchestrator'/'runtime'))
DEFAULT_MANIFEST=ROOT/'orchestrator/runtime/manifest.json'
HUB_PATH=ROOT/'docs/00_SKILLS_HUB.md'
ACTIVATION_PATH=ROOT/'orchestrator/registry/activation.md'
DISTRIBUTION_PATH=ROOT/'orchestrator/registry/distribution.json'
ACTIVE_STATES={'active','manual'}
INACTIVE_STATES={'off','hidden','deprecated'}
VALID_STATES=ACTIVE_STATES|INACTIVE_STATES
VALID_PACKAGE_ROLES={'interaction','supporting','task'}
ORCHESTRATOR_ID='skills-orchestrator'
INTERACTION_PACKAGE_ID='interaction-protocol'
VALID_HELP_KINDS={'chat','terminal','keyword'}
HELP_MAX_BYTES=16384
VALID_REGISTRY_VIEWS={'auto','inventory','catalog','diagnostic'}
REGISTRY_VIEW_MAX_BYTES={'inventory':2048,'catalog':8192,'diagnostic':32768}
class RegistryRuntimeError(RuntimeError):
    pass


def _unique_object(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise RegistryRuntimeError(f"duplicate JSON field: {key}")
        value[key] = item
    return value


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
        if not re.fullmatch(r"#>\s+[a-z0-9][a-z0-9_-]{0,79}", command):
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

def parse_help_operations(path: Path) -> list[dict[str, str]]:
    """Read bounded, user-facing quick-help operations from one family registry."""
    operations: list[dict[str, str]] = []
    for section, cells in _read_sections(path):
        if section != "Help operations" or cells[0] == "kind" or len(cells) < 4:
            continue
        kind = cells[0].strip("`").lower()
        syntax = cells[1].strip("`").strip()
        does = cells[2].strip()
        boundary = cells[3].strip()
        if kind not in VALID_HELP_KINDS:
            raise RegistryRuntimeError(f"invalid help operation kind {kind} in {path.name}")
        for field, value, maximum in (
            ("syntax", syntax, 160),
            ("does", does, 240),
            ("boundary", boundary, 240),
        ):
            if not value or len(value) > maximum or re.search(r"[\x00-\x1f\x7f]", value):
                raise RegistryRuntimeError(f"invalid help operation {field} in {path.name}")
        operations.append(
            {"kind": kind, "syntax": syntax, "does": does, "boundary": boundary}
        )
    return operations

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


def _relative_path(value: str, *, field: str) -> Path:
    path = Path(value)
    if not value or path.is_absolute() or ".." in path.parts:
        raise RegistryRuntimeError(f"invalid {field}: {value}")
    return path


def _project_version(path: Path) -> str:
    if not path.is_file() or path.stat().st_size > 65536:
        raise RegistryRuntimeError(f"invalid version source: {path}")
    section = ""
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            section = stripped
            continue
        if section == "[project]":
            match = re.fullmatch(r'version\s*=\s*["\']([^"\']+)["\']', stripped)
            if match:
                version = match.group(1)
                if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+(?:[-+][A-Za-z0-9.-]+)?", version):
                    raise RegistryRuntimeError(f"invalid project version: {version}")
                return version
    raise RegistryRuntimeError(f"project version missing: {path}")


def parse_distribution(path: Path, packages: dict[str, dict[str, str]], *, root: Path = ROOT) -> dict[str, Any]:
    if not path.is_file() or path.stat().st_size > 65536:
        raise RegistryRuntimeError("distribution registry missing or too large")
    try:
        value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_unique_object)
    except (ValueError, UnicodeError) as exc:
        raise RegistryRuntimeError("invalid distribution registry") from exc
    if not isinstance(value, dict) or set(value) != {"schema", "records"} or value["schema"] != "skills-ai/distribution/1":
        raise RegistryRuntimeError("invalid distribution registry schema")
    records = value["records"]
    if not isinstance(records, dict) or not 1 <= len(records) <= 64 or ORCHESTRATOR_ID not in records:
        raise RegistryRuntimeError("invalid distribution records")
    known = set(packages) | {ORCHESTRATOR_ID}
    command_owners: dict[str, str] = {}
    compiled: dict[str, Any] = {}
    for record_id, record in records.items():
        if record_id not in known or not isinstance(record, dict):
            raise RegistryRuntimeError(f"unknown distribution owner: {record_id}")
        allowed = {"repository", "version_source", "release", "commands", "host_adapters"}
        if set(record) - allowed or not {"repository", "release", "commands", "host_adapters"} <= set(record):
            raise RegistryRuntimeError(f"invalid distribution fields: {record_id}")
        repository = record["repository"]
        if not isinstance(repository, dict) or set(repository) != {"kind", "path"} or repository.get("kind") not in {"parent", "submodule"}:
            raise RegistryRuntimeError(f"invalid repository distribution: {record_id}")
        repository_path = _relative_path(repository.get("path", ""), field="repository path")
        if repository["kind"] == "parent":
            if record_id != ORCHESTRATOR_ID or repository_path != Path("."):
                raise RegistryRuntimeError(f"invalid parent distribution: {record_id}")
        else:
            expected = Path(packages[record_id]["path"]).parent
            if record_id == ORCHESTRATOR_ID or repository_path != expected or not (root / repository_path).is_dir():
                raise RegistryRuntimeError(f"invalid submodule distribution: {record_id}")
        version = None
        source = record.get("version_source")
        if source is not None:
            if not isinstance(source, dict) or set(source) != {"kind", "path"} or source.get("kind") != "pyproject":
                raise RegistryRuntimeError(f"invalid version source: {record_id}")
            source_path = _relative_path(source.get("path", ""), field="version source")
            if repository["kind"] == "submodule" and repository_path not in (source_path, *source_path.parents):
                raise RegistryRuntimeError(f"version source escapes package: {record_id}")
            version = _project_version(root / source_path)
        release = record["release"]
        if (not isinstance(release, dict) or set(release) != {"kind", "required"}
                or release.get("kind") not in {"date-tag", "semver-tag"} or not isinstance(release.get("required"), bool)):
            raise RegistryRuntimeError(f"invalid release contract: {record_id}")
        if release["kind"] == "semver-tag" and version is None:
            raise RegistryRuntimeError(f"semver release needs a version source: {record_id}")
        commands = record["commands"]
        if not isinstance(commands, list) or len(commands) > 16:
            raise RegistryRuntimeError(f"invalid command distribution: {record_id}")
        checked_commands = []
        for command in commands:
            if not isinstance(command, dict) or not isinstance(command.get("required"), bool):
                raise RegistryRuntimeError(f"invalid command distribution: {record_id}")
            kind = command.get("kind")
            expected_fields = ({"name", "kind", "distribution", "required"} if kind == "python-distribution"
                               else {"name", "kind", "target", "required"} if kind == "source-launcher" else set())
            if not expected_fields or set(command) != expected_fields:
                raise RegistryRuntimeError(f"invalid command check: {record_id}")
            name = command.get("name")
            if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", name):
                raise RegistryRuntimeError(f"invalid command name: {record_id}")
            if name in command_owners:
                raise RegistryRuntimeError(f"duplicate command distribution: {name}")
            command_owners[name] = record_id
            if kind == "python-distribution":
                distribution = command.get("distribution")
                if (version is None or not isinstance(distribution, str)
                        or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}", distribution)):
                    raise RegistryRuntimeError(f"invalid Python distribution check: {record_id}")
            else:
                target = _relative_path(command.get("target", ""), field="launcher target")
                if not (root / target).is_file():
                    raise RegistryRuntimeError(f"launcher target missing: {record_id}")
            checked_commands.append(command)
        hosts = record["host_adapters"]
        if (not isinstance(hosts, list) or len(hosts) != len(set(hosts))
                or any(host not in {"codex", "claude"} for host in hosts)):
            raise RegistryRuntimeError(f"invalid host adapters: {record_id}")
        compiled[record_id] = {
            "repository": repository,
            "release": release,
            "commands": checked_commands,
            "host_adapters": hosts,
            **({"expected_version": version, "version_source": source} if version is not None else {}),
        }
    return compiled

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
    help_operations: list[dict[str, str]] = []
    distribution_path = root / DISTRIBUTION_PATH.relative_to(ROOT)
    source_paths = [hub_path, activation_path, distribution_path]

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
    distributions = parse_distribution(distribution_path, packages, root=root)

    for family_id, family in activation["families"].items():
        package_id = family.get("package", "")
        package = packages.get(package_id)
        if package is None:
            errors.append(f"family {family_id} references unknown package: {package_id or '(missing)'}")
        elif package["role"] not in {"task", "interaction", "supporting"}:
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
        for operation in parse_help_operations(family_path):
            help_operations.append(
                {**operation, "package": package_id, "family": family_id}
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

    help_seen: set[tuple[str, str, str]] = set()
    for operation in help_operations:
        key = (operation["package"], operation["kind"], operation["syntax"].lower())
        if key in help_seen:
            errors.append(
                f"duplicate help operation: {operation['package']} / {operation['syntax']}"
            )
        help_seen.add(key)
    missing_help = sorted(set(packages) - {item["package"] for item in help_operations})
    if missing_help:
        errors.append("public packages missing help operations: " + ", ".join(missing_help))

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
        "help_operations": sorted(
            help_operations,
            key=lambda item: (item["package"], item["kind"], item["syntax"].lower()),
        ),
        "components": activation["components"],
        "distributions": distributions,
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
            "help_operations": len(help_operations),
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
        root=path.parents[2] if path.parent.name=='runtime' and path.parent.parent.name=='orchestrator' else path.parent
        seen=set();total=0
        for source in sources:
            if not isinstance(source,dict) or set(source)!={'path','sha256'} or not isinstance(source['path'],str) or not isinstance(source['sha256'],str):
                raise RegistryRuntimeError('INVALID_MANIFEST_BINDINGS')
            name=source['path']
            if name in seen or (name!='docs/00_SKILLS_HUB.md' and not re.fullmatch(r'orchestrator/registry/(?:[a-z][a-z0-9_-]*\.md|distribution\.json)',name)) or not re.fullmatch(r'[a-f0-9]{64}',source['sha256']):
                raise RegistryRuntimeError('INVALID_MANIFEST_BINDINGS')
            seen.add(name)
            raw=read_relative(root,name,maximum=65536);total+=len(raw)
            if total>1024*1024:raise RegistryRuntimeError('MANIFEST_SOURCES_TOO_LARGE')
            if hashlib.sha256(raw).hexdigest()!=source['sha256']:raise RegistryRuntimeError('STALE_MANIFEST')
        if not {'docs/00_SKILLS_HUB.md','orchestrator/registry/activation.md','orchestrator/registry/distribution.json'}<=seen or hashlib.sha256(json.dumps(sources,sort_keys=True,separators=(',',':')).encode()).hexdigest()!=manifest['source_hash']:
            raise RegistryRuntimeError('INVALID_MANIFEST_BINDINGS')
        packages=manifest.get('packages')
        if not isinstance(packages,dict) or len(packages)>512:
            raise RegistryRuntimeError('invalid package metadata')
        for name, package in packages.items():
            if not isinstance(package,dict) or package.get('state') not in VALID_STATES or not isinstance(package.get('path'),str):
                raise RegistryRuntimeError('invalid package metadata')
        routes=manifest.get('routes');aliases=manifest.get('command_aliases')
        help_operations=manifest.get('help_operations')
        if not isinstance(routes,list) or not isinstance(aliases,list) or not isinstance(help_operations,list):
            raise RegistryRuntimeError('invalid capability metadata')
        for route in routes:
            if not isinstance(route,dict) or route.get('package') not in packages or route.get('state') not in VALID_STATES or any(not isinstance(route.get(k),str) for k in ('id','path','description')):
                raise RegistryRuntimeError('invalid capability metadata')
        for alias in aliases:
            if not isinstance(alias,dict) or alias.get('skill_id') not in packages or any(not isinstance(alias.get(k),str) for k in ('command','mode')):
                raise RegistryRuntimeError('invalid alias metadata')
        help_seen=set()
        for operation in help_operations:
            if (not isinstance(operation,dict)
                    or operation.get('package') not in packages
                    or operation.get('kind') not in VALID_HELP_KINDS
                    or any(not isinstance(operation.get(k),str) for k in ('syntax','does','boundary','family'))):
                raise RegistryRuntimeError('invalid help metadata')
            key=(operation['package'],operation['kind'],operation['syntax'].lower())
            if key in help_seen:
                raise RegistryRuntimeError('duplicate help metadata')
            help_seen.add(key)
        if set(packages)-{item['package'] for item in help_operations}:
            raise RegistryRuntimeError('incomplete help metadata')
        distributions=manifest.get('distributions')
        if not isinstance(distributions,dict) or ORCHESTRATOR_ID not in distributions or len(distributions)>64:
            raise RegistryRuntimeError('invalid distribution metadata')
        for owner, distribution in distributions.items():
            if owner not in set(packages)|{ORCHESTRATOR_ID} or not isinstance(distribution,dict):
                raise RegistryRuntimeError('invalid distribution metadata')
            if (not isinstance(distribution.get('repository'),dict)
                    or not isinstance(distribution.get('commands'),list)
                    or not isinstance(distribution.get('host_adapters'),list)
                    or not isinstance(distribution.get('release'),dict)):
                raise RegistryRuntimeError('invalid distribution metadata')
        return manifest
    except (ContextError, OSError, ValueError, TypeError, RecursionError) as exc:
        raise RegistryRuntimeError('cannot load bounded manifest') from exc

def _public_purpose(value: str, maximum: int = 160) -> str:
    """Return one bounded display label, never executable or multiline content."""
    return re.sub(r"[\x00-\x1f\x7f{}]", " ", value).strip()[:maximum]

def skill_help(manifest: dict[str, Any], raw_name: str) -> dict[str, Any]:
    """Return one bounded quick-reference card without loading a skill body."""
    if not isinstance(raw_name, str) or not raw_name.strip() or len(raw_name) > 160:
        raise RegistryRuntimeError("invalid skill help target")
    skill_id = re.sub(r"[-_\s]+", "-", raw_name.strip().lower())
    package = manifest.get("packages", {}).get(skill_id)
    if package is None or package.get("state") in {"hidden", "deprecated"}:
        raise RegistryRuntimeError(f"unknown public skill: {skill_id}")

    routes = [route for route in manifest.get("routes", []) if route.get("package") == skill_id]
    trigger_items = []
    for route in routes:
        for trigger in route.get("family_triggers", route.get("triggers", [])):
            cleaned = _public_purpose(trigger, 240)
            if cleaned and cleaned not in trigger_items:
                trigger_items.append(cleaned)
    use_when = [", ".join(trigger_items)] if trigger_items else []
    not_for = sorted(
        {_public_purpose(route.get("not_for", ""), 480) for route in routes if _public_purpose(route.get("not_for", ""), 480)}
    )
    route_purposes = [
        _public_purpose(route.get("description", ""), 320)
        for route in routes
        if _public_purpose(route.get("description", ""), 320)
    ]
    purpose = (route_purposes[0] if len(route_purposes) == 1
               else _public_purpose(package.get("boundary", ""), 320))

    sections: dict[str, list[dict[str, str]]] = {"chat": [], "terminal": [], "keyword": []}
    seen: dict[str, set[str]] = {kind: set() for kind in sections}
    for alias in manifest.get("command_aliases", []):
        if alias.get("skill_id") != skill_id:
            continue
        syntax = alias["command"]
        sections["chat"].append(
            {
                "syntax": syntax,
                "does": f"Selects the {alias['mode']} operation for this skill.",
                "boundary": alias.get("boundary", "Selection grants no additional authority."),
            }
        )
        seen["chat"].add(syntax.lower())
    for operation in manifest.get("help_operations", []):
        if operation.get("package") != skill_id:
            continue
        kind = operation["kind"]
        key = operation["syntax"].lower()
        if key in seen[kind]:
            continue
        sections[kind].append(
            {key: operation[key] for key in ("syntax", "does", "boundary")}
        )
        seen[kind].add(key)

    packet = {
        "schema": "skills-ai/skill-help/1",
        "authority": "none",
        "source_hash": manifest["source_hash"],
        "skill": {
            "id": skill_id,
            "state": package["state"],
            "role": package["role"],
            "purpose": purpose,
            "available": package["state"] in ACTIVE_STATES,
        },
        "use_when": use_when[:16],
        "not_for": not_for[:8],
        "chat": sections["chat"],
        "terminal": sections["terminal"],
        "keywords": sections["keyword"],
        "entries": sorted({route["path"] for route in routes}),
        "limits": "Help is read-only metadata. It does not select, load, activate, or authorize the skill or any operation it describes.",
    }
    if len(json.dumps(packet, sort_keys=True, separators=(",", ":")).encode()) > HELP_MAX_BYTES:
        raise RegistryRuntimeError("skill help exceeds bounded output size")
    return packet

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
