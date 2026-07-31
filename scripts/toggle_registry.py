#!/usr/bin/env python3
"""Toggle rows in registry/activation.md between active/manual/off states."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTER = ROOT / "registry" / "activation.md"
ACTIVE_STATES = {"active", "manual"}
INACTIVE_STATES = {"off", "hidden", "deprecated"}
VALID_STATES = ACTIVE_STATES | INACTIVE_STATES
STATE_ALIASES = {
    "enable": "active",
    "enabled": "active",
    "on": "active",
    "activate": "active",
    "disable": "off",
    "disabled": "off",
    "deactivate": "off",
}


class RegistryError(RuntimeError):
    pass


def atomic_write(path: Path, content: str) -> None:
    """Replace a registry file without exposing a partial write."""
    descriptor, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent, text=True)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    except Exception:
        try:
            os.unlink(temp_name)
        except OSError:
            pass
        raise


def normalize_state(raw: str) -> str:
    value = raw.strip().lower()
    value = STATE_ALIASES.get(value, value)
    if value not in VALID_STATES:
        raise RegistryError(f"unknown state: {raw}")
    return value


def split_row(line: str) -> list[str] | None:
    if not line.startswith("|") or "---" in line:
        return None
    body = line.strip().strip("|")
    cells = [cell.strip().replace("\\|", "|") for cell in re.split(r"(?<!\\)\|", body)]
    if len(cells) < 4:
        return None
    return cells


def make_row(cells: list[str]) -> str:
    escaped = [cell.replace("|", "\\|") for cell in cells]
    return "| " + " | ".join(escaped) + " |"


def route_to_path(route: str) -> str:
    route = route.strip().replace("\\|", "|")
    link = re.fullmatch(r"\[\[([^|\]]+)(?:\|[^\]]+)?\]\]", route)
    if link:
        target = link.group(1).replace("\\|", "|")
        return target if target.endswith(".md") else target + ".md"
    code = re.fullmatch(r"`([^`]+)`", route)
    if code:
        return code.group(1)
    raise RegistryError(f"route is neither wikilink nor code path: {route}")


def path_to_link(path_text: str, row_id: str) -> str:
    path = route_to_path(path_text)
    if not (ROOT / path).exists():
        raise RegistryError(f"route target does not exist for {row_id}: {path}")
    target = path[:-3] if path.endswith(".md") else path
    label = row_id.split(".")[-1]
    if target.endswith("/SKILL"):
        label = Path(target).parent.name
    return f"[[{target}\\|{label}]]"


def path_to_code(route: str, row_id: str) -> str:
    path = route_to_path(route)
    if not (ROOT / path).exists():
        raise RegistryError(f"route target does not exist for {row_id}: {path}")
    return f"`{path}`"


def validate(lines: list[str]) -> dict[str, str]:
    states: dict[str, str] = {}
    errors: list[str] = []
    for lineno, line in enumerate(lines, start=1):
        cells = split_row(line)
        if not cells or cells[0] == "id":
            continue
        row_id, state, route = cells[0], cells[1].strip("`"), cells[2]
        if row_id in states:
            errors.append(f"line {lineno}: duplicate id {row_id}")
            continue
        if state not in VALID_STATES:
            errors.append(f"line {lineno}: invalid state {state} for {row_id}")
            continue
        states[row_id] = state
        try:
            path = route_to_path(route)
        except RegistryError as exc:
            errors.append(f"line {lineno}: {exc}")
            continue
        if not (ROOT / path).exists():
            errors.append(f"line {lineno}: route target missing for {row_id}: {path}")
        if state in ACTIVE_STATES and not route.startswith("[["):
            errors.append(f"line {lineno}: active/manual {row_id} must use wikilink route")
        if state in INACTIVE_STATES and not route.startswith("`"):
            errors.append(f"line {lineno}: inactive {row_id} must use plain code path")

    for row_id, state in states.items():
        if "." not in row_id or state not in ACTIVE_STATES:
            continue
        parent = row_id.split(".", 1)[0]
        parent_state = states.get(parent)
        if parent_state not in ACTIVE_STATES:
            errors.append(f"{row_id}: parent {parent} is not active/manual")

    if errors:
        raise RegistryError("\n".join(errors))
    return states


def toggle(register: Path, row_id: str, state: str, *, write: bool = True) -> bool:
    original = register.read_text(encoding="utf-8")
    lines = original.splitlines()
    found = False
    changed = False
    next_lines: list[str] = []
    for line in lines:
        cells = split_row(line)
        if not cells or cells[0] != row_id:
            next_lines.append(line)
            continue
        found = True
        old_state = cells[1].strip("`")
        cells[1] = state
        cells[2] = path_to_link(cells[2], row_id) if state in ACTIVE_STATES else path_to_code(cells[2], row_id)
        new_line = make_row(cells)
        changed = changed or old_state != state or new_line != line
        next_lines.append(new_line)
    if not found:
        raise RegistryError(f"id not found: {row_id}")
    validate(next_lines)
    if changed and write:
        updated = "\n".join(next_lines) + "\n"
        atomic_write(register, updated)
        if register.resolve() == DEFAULT_REGISTER.resolve():
            try:
                from compile_registry import serialized_manifest
                from registry_runtime import DEFAULT_MANIFEST

                atomic_write(DEFAULT_MANIFEST, serialized_manifest())
            except Exception as exc:
                atomic_write(register, original)
                raise RegistryError(f"runtime compile failed; activation restored: {exc}") from exc
    return changed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Toggle registry activation rows")
    parser.add_argument("state", nargs="?", help="active/manual/off/hidden/deprecated or enable/disable")
    parser.add_argument("id", nargs="?", help="row id, for example caveman.no-ai-traces")
    parser.add_argument("--file", default=str(DEFAULT_REGISTER), help="activation register path")
    parser.add_argument("--check", action="store_true", help="validate without editing")
    parser.add_argument("--dry-run", action="store_true", help="validate and report without writing")
    parser.add_argument("--json", action="store_true", help="emit machine-readable output")
    args = parser.parse_args(argv)

    register = Path(args.file)
    if not register.is_absolute():
        register = ROOT / register

    try:
        if args.check:
            validate(register.read_text(encoding="utf-8").splitlines())
            if register.resolve() == DEFAULT_REGISTER.resolve():
                from compile_registry import serialized_manifest
                from registry_runtime import DEFAULT_MANIFEST

                expected = serialized_manifest()
                if not DEFAULT_MANIFEST.exists() or DEFAULT_MANIFEST.read_text(encoding="utf-8") != expected:
                    raise RegistryError("runtime/router-manifest.json is missing or stale")
            try:
                display = str(register.relative_to(ROOT))
            except ValueError:
                display = str(register)
            output = {"result": "ok", "register": display}
            print(json.dumps(output, sort_keys=True) if args.json else f"ok: {display}")
            return 0
        if not args.state or not args.id:
            raise RegistryError("state and id are required unless --check is used")
        state = normalize_state(args.state)
        changed = toggle(register, args.id, state, write=not args.dry_run)
        result = "would-update" if args.dry_run and changed else "updated" if changed else "unchanged"
        output = {"result": result, "id": args.id, "state": state}
        print(json.dumps(output, sort_keys=True) if args.json else f"{result}: {args.id} -> {state}")
        return 0
    except RegistryError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
