#!/usr/bin/env python3
"""Validate and explicitly manage bounded project-local Skills AI context."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import stat
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = ROOT / "orchestrator" / "runtime" / "manifest.json"
SCHEMA_PATH = ROOT / "orchestrator" / "runtime" / "project-context.schema.json"
CAPSULE_RELATIVE_PATH = Path(".skills-ai/project.json")
MAX_CAPSULE_BYTES = 32 * 1024
MAX_STDIN_BYTES = 32 * 1024
MAX_RECEIPT_BYTES = 4 * 1024
MAX_ITEMS = 32
MAX_COMMANDS = 16

TOP_LEVEL_FIELDS = {
    "schema_version",
    "project",
    "routing",
    "constraints",
    "documentation",
    "checkpoint",
    "freshness",
}
SECTION_FIELDS = {
    "project": {"name", "kind", "languages", "frameworks", "entrypoints", "commands"},
    "routing": {"preferred_packages", "excluded_packages", "manual_only", "capability_hints"},
    "constraints": {"write_scope", "protected_paths", "network", "credentials"},
    "documentation": {"canonical_sources", "generated_outputs", "validation_commands"},
    "checkpoint": {"objective", "phase", "approved_scope", "next_condition"},
    "freshness": {"verified_at", "manifest_source_hash"},
}
PATH_LIST_FIELDS = {
    ("project", "entrypoints"),
    ("constraints", "write_scope"),
    ("constraints", "protected_paths"),
    ("documentation", "canonical_sources"),
    ("documentation", "generated_outputs"),
    ("checkpoint", "approved_scope"),
}
STRING_LIST_FIELDS = {
    ("project", "languages"),
    ("project", "frameworks"),
    ("documentation", "validation_commands"),
}
IDENTIFIER_LIST_FIELDS = {
    ("routing", "preferred_packages"),
    ("routing", "excluded_packages"),
    ("routing", "manual_only"),
}
IDENTIFIER_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")
COMMAND_NAME_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_.-]{0,63}$")
HASH_PATTERN = re.compile(r"^[a-f0-9]{64}$")
SECRET_KEY_PATTERN = re.compile(
    r"(?:^|[-_.])(api[-_]?key|credential|password|private[-_]?key|secret|token)(?:$|[-_.])",
    flags=re.IGNORECASE,
)
SECRET_VALUE_PATTERN = re.compile(
    r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----|"
    r"\b(?:sk|ghp|github_pat|xox[baprs])[-_][a-zA-Z0-9_-]{16,}|"
    r"\b(?:api[-_]?key|password|secret|token)\s*=\s*[^\s]+",
    flags=re.IGNORECASE,
)
PERSONAL_PATH_PATTERN = re.compile(
    r"(?:^|[\s\"'])(?:/Users/[^/\s]+|/home/[^/\s]+|[a-zA-Z]:[\\/]Users[\\/][^\\/\s]+)"
)
RECEIPT_ROLE_HEADER_PATTERN = re.compile(r"\b(system|assistant|user)\s*:", re.IGNORECASE)
RECEIPT_ALL_CAPS_RUN_PATTERN = re.compile(
    r"\b(?:[A-Z][A-Z0-9_-]{1,}\s+){3,}[A-Z][A-Z0-9_-]{1,}\b"
)
RECEIPT_INSTRUCTION_PATTERN = re.compile(
    r"\b(?:ignore|disregard|override)\b.{0,96}\b(?:instruction|policy|rule)s?\b|"
    r"\bgrant\b.{0,96}\b(?:permission|access|authority)\b|"
    r"\b(?:act as|pretend to be|you are now)\b",
    re.IGNORECASE,
)


class ProjectContextError(ValueError):
    """Expected capsule failure with a stable reason code."""

    def __init__(self, reason_code: str, message: str) -> None:
        super().__init__(message)
        self.reason_code = reason_code


@dataclass(frozen=True)
class ProjectContext:
    """Validated capsule data plus a bounded response-safe receipt."""

    status: str
    data: dict[str, Any]
    reason_code: str | None = None
    fingerprint: str | None = None

    @property
    def routing(self) -> Mapping[str, Any]:
        return self.data.get("routing", {}) if self.status == "valid" else {}

    def receipt(self, *, include_operational: bool = False) -> dict[str, Any]:
        receipt: dict[str, Any] = {
            "status": self.status,
            "source": CAPSULE_RELATIVE_PATH.as_posix(),
        }
        if self.reason_code:
            receipt["reason"] = self.reason_code
        if self.status != "valid":
            return receipt

        receipt.update(
            {
                "schema_version": self.data["schema_version"],
                "fingerprint": (self.fingerprint or "")[:12],
                "trust": "untrusted-data-only",
                "project": _receipt_section(
                    self.data["project"],
                    omit=set() if include_operational else {"commands"},
                ),
                "routing": _receipt_section(self.data["routing"]),
                "constraints": _receipt_section(self.data["constraints"]),
                "documentation": _receipt_section(
                    self.data["documentation"],
                    omit=set() if include_operational else {"validation_commands"},
                ),
                "checkpoint": _receipt_section(self.data["checkpoint"]),
                "freshness": _receipt_section(self.data["freshness"]),
            }
        )
        if include_operational:
            receipt["operational_fields"] = "explicit-inspection"
        receipt = {key: value for key, value in receipt.items() if value not in ({}, [], "")}
        encoded = json.dumps(receipt, sort_keys=True, separators=(",", ":")).encode("utf-8")
        if len(encoded) > MAX_RECEIPT_BYTES:
            receipt = {
                "status": "valid",
                "source": CAPSULE_RELATIVE_PATH.as_posix(),
                "schema_version": self.data["schema_version"],
                "fingerprint": (self.fingerprint or "")[:12],
                "trust": "untrusted-data-only",
                "routing": _receipt_section(self.data["routing"], item_limit=4, string_limit=96),
                "constraints": _receipt_section(self.data["constraints"], item_limit=4, string_limit=96),
                "checkpoint": _receipt_section(self.data["checkpoint"], item_limit=2, string_limit=96),
                "truncated": True,
            }
        return receipt


def _receipt_section(
    value: Mapping[str, Any],
    *,
    item_limit: int = MAX_ITEMS,
    string_limit: int = 160,
    omit: set[str] | None = None,
) -> dict[str, Any]:
    result: dict[str, Any] = {}
    truncated = False
    for key, item in value.items():
        if key in (omit or set()):
            continue
        if item in ({}, [], "", None):
            continue
        if isinstance(item, str):
            sanitized = _neutralize_receipt_text(item)
            result[key] = sanitized[:string_limit]
            truncated = truncated or len(sanitized) > string_limit
        elif isinstance(item, list):
            sanitized_entries = [_neutralize_receipt_text(entry) for entry in item[:item_limit]]
            result[key] = [entry[:string_limit] for entry in sanitized_entries]
            truncated = truncated or len(item) > item_limit or any(
                len(entry) > string_limit for entry in sanitized_entries
            )
        elif isinstance(item, dict):
            result[key] = {
                _neutralize_receipt_text(str(name))[:64]: _neutralize_receipt_text(str(entry))[:string_limit]
                for name, entry in list(item.items())[:item_limit]
            }
            truncated = truncated or len(item) > item_limit or any(
                len(_neutralize_receipt_text(str(name))) > 64
                or len(_neutralize_receipt_text(str(entry))) > string_limit
                for name, entry in list(item.items())[:item_limit]
            )
        else:
            result[key] = item
    if truncated:
        result["_truncated"] = True
    return result


def _neutralize_receipt_text(value: str) -> str:
    """Render capsule free text as data without directive or role markers."""
    if RECEIPT_INSTRUCTION_PATTERN.search(value):
        return "[instruction-like capsule text neutralized]"
    neutralized = value.replace("#>", "# >")
    neutralized = RECEIPT_ROLE_HEADER_PATTERN.sub(
        lambda match: f"{match.group(1).lower()} (data):",
        neutralized,
    )
    return RECEIPT_ALL_CAPS_RUN_PATTERN.sub(
        lambda match: match.group(0).lower(),
        neutralized,
    )


def _text(value: Any, label: str, *, maximum: int, allow_empty: bool = True) -> str:
    if not isinstance(value, str):
        raise ProjectContextError("INVALID_SCHEMA", f"{label} must be a string")
    if not allow_empty and not value:
        raise ProjectContextError("INVALID_SCHEMA", f"{label} must not be empty")
    if len(value) > maximum:
        raise ProjectContextError("INVALID_SCHEMA", f"{label} exceeds {maximum} characters")
    if any(ord(character) < 32 for character in value):
        raise ProjectContextError("INVALID_SCHEMA", f"{label} contains control characters")
    return value


def _identifier(value: Any, label: str) -> str:
    identifier = _text(value, label, maximum=64, allow_empty=False).lower()
    if not IDENTIFIER_PATTERN.fullmatch(identifier):
        raise ProjectContextError("INVALID_SCHEMA", f"{label} is not a valid identifier")
    return identifier


def _relative_path(value: Any, label: str) -> str:
    path = _text(value, label, maximum=240, allow_empty=False).replace("\\", "/")
    if path.startswith("/") or re.match(r"^[a-zA-Z]:/", path):
        raise ProjectContextError("ABSOLUTE_PATH_REJECTED", f"{label} must be project-relative")
    pure = PurePosixPath(path)
    if path in {".", ".."} or any(part in {"", ".", ".."} for part in pure.parts):
        raise ProjectContextError("PATH_ESCAPE_REJECTED", f"{label} must not escape the project")
    return pure.as_posix()


def _list(
    value: Any,
    label: str,
    validator: Any,
    *,
    maximum: int = MAX_ITEMS,
) -> list[str]:
    if not isinstance(value, list) or len(value) > maximum:
        raise ProjectContextError("INVALID_SCHEMA", f"{label} must be a list of at most {maximum} items")
    result = [validator(item, f"{label}[{index}]") for index, item in enumerate(value)]
    if len(set(result)) != len(result):
        raise ProjectContextError("INVALID_SCHEMA", f"{label} contains duplicate values")
    return result


def _mapping(value: Any, label: str, allowed: set[str]) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ProjectContextError("INVALID_SCHEMA", f"{label} must be an object")
    unknown = sorted(set(value) - allowed)
    if unknown:
        raise ProjectContextError("UNKNOWN_FIELD", f"{label} has unknown fields: {', '.join(unknown)}")
    for key in value:
        if SECRET_KEY_PATTERN.search(key):
            raise ProjectContextError("SECRET_FIELD_REJECTED", f"{label} contains a prohibited secret field")
    return dict(value)


def manifest_catalog(
    manifest: Mapping[str, Any] | None,
) -> tuple[dict[str, str], dict[str, str], set[str]]:
    if not manifest:
        return {}, {}, set()
    packages = {
        package_id: package.get("role", "task")
        for package_id, package in manifest.get("packages", {}).items()
        if isinstance(package_id, str) and isinstance(package, dict)
    }
    package_states = {
        package_id: package.get("state", "off")
        for package_id, package in manifest.get("packages", {}).items()
        if isinstance(package_id, str) and isinstance(package, dict)
    }
    capabilities = {
        route["id"]
        for route in manifest.get("routes", [])
        if isinstance(route, dict) and isinstance(route.get("id"), str)
    }
    return packages, package_states, capabilities


def _reject_sensitive_values(value: Any, label: str = "capsule") -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            _reject_sensitive_values(item, f"{label}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _reject_sensitive_values(item, f"{label}[{index}]")
    elif isinstance(value, str):
        if SECRET_VALUE_PATTERN.search(value):
            raise ProjectContextError("SECRET_VALUE_REJECTED", f"{label} resembles a credential")
        if PERSONAL_PATH_PATTERN.search(value):
            raise ProjectContextError("ABSOLUTE_PATH_REJECTED", f"{label} contains a personal absolute path")


def validate_capsule(
    value: Any,
    *,
    manifest: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Validate and normalize a capsule without executing stored commands."""
    capsule = _mapping(value, "capsule", TOP_LEVEL_FIELDS)
    missing = sorted(TOP_LEVEL_FIELDS - set(capsule))
    if missing:
        raise ProjectContextError("INVALID_SCHEMA", f"capsule is missing: {', '.join(missing)}")
    if capsule.get("schema_version") != 1:
        raise ProjectContextError("UNSUPPORTED_SCHEMA", "schema_version must be 1")

    normalized: dict[str, Any] = {"schema_version": 1}
    for section, allowed in SECTION_FIELDS.items():
        normalized[section] = _mapping(capsule[section], section, allowed)

    project = normalized["project"]
    for field in ("name", "kind"):
        if field in project:
            project[field] = _text(project[field], f"project.{field}", maximum=160)
    for section, field in STRING_LIST_FIELDS:
        target = normalized[section]
        if field in target:
            limit = 512 if field == "validation_commands" else 160
            target[field] = _list(
                target[field],
                f"{section}.{field}",
                lambda item, label, limit=limit: _text(item, label, maximum=limit, allow_empty=False),
                maximum=16 if field == "validation_commands" else MAX_ITEMS,
            )
    for section, field in PATH_LIST_FIELDS:
        target = normalized[section]
        if field in target:
            target[field] = _list(target[field], f"{section}.{field}", _relative_path)

    commands = project.get("commands", {})
    if not isinstance(commands, dict) or len(commands) > MAX_COMMANDS:
        raise ProjectContextError("INVALID_SCHEMA", "project.commands must be an object of at most 16 commands")
    normalized_commands: dict[str, str] = {}
    for raw_name, raw_command in commands.items():
        name = _text(raw_name, "project.commands key", maximum=64, allow_empty=False).lower()
        if not COMMAND_NAME_PATTERN.fullmatch(name):
            raise ProjectContextError("INVALID_SCHEMA", "project.commands has an invalid command name")
        if SECRET_KEY_PATTERN.search(name):
            raise ProjectContextError("SECRET_FIELD_REJECTED", "project.commands has a prohibited secret name")
        normalized_commands[name] = _text(
            raw_command,
            f"project.commands.{name}",
            maximum=512,
            allow_empty=False,
        )
    project["commands"] = normalized_commands

    routing = normalized["routing"]
    for section, field in IDENTIFIER_LIST_FIELDS:
        target = normalized[section]
        if field in target:
            target[field] = _list(target[field], f"{section}.{field}", _identifier)
    hints = routing.get("capability_hints", {})
    if not isinstance(hints, dict) or len(hints) > MAX_ITEMS:
        raise ProjectContextError("INVALID_SCHEMA", "routing.capability_hints must have at most 32 entries")
    normalized_hints: dict[str, str] = {}
    for phrase, capability in hints.items():
        normalized_phrase = _text(
            phrase,
            "routing.capability_hints key",
            maximum=80,
            allow_empty=False,
        ).lower()
        normalized_hints[normalized_phrase] = _identifier(
            capability,
            f"routing.capability_hints.{normalized_phrase}",
        )
    routing["capability_hints"] = normalized_hints

    package_roles, package_states, capabilities = manifest_catalog(manifest)
    if package_roles:
        task_packages = {package_id for package_id, role in package_roles.items() if role == "task"}
        for field in ("preferred_packages", "excluded_packages", "manual_only"):
            unknown = sorted(set(routing.get(field, [])) - task_packages)
            if unknown:
                raise ProjectContextError(
                    "UNKNOWN_PACKAGE",
                    f"routing.{field} contains unknown task packages: {', '.join(unknown)}",
                )
        for field in ("preferred_packages", "manual_only"):
            inactive = sorted(
                package_id
                for package_id in routing.get(field, [])
                if package_states.get(package_id) != "active"
            )
            if inactive:
                raise ProjectContextError(
                    "INACTIVE_PACKAGE_POLICY",
                    f"routing.{field} may contain active task packages only: {', '.join(inactive)}",
                )
    if capabilities:
        unknown_hints = sorted(set(normalized_hints.values()) - capabilities)
        if unknown_hints:
            raise ProjectContextError(
                "UNKNOWN_CAPABILITY",
                f"routing.capability_hints contains unknown capabilities: {', '.join(unknown_hints)}",
            )
    preferred = set(routing.get("preferred_packages", []))
    incompatible = preferred & (
        set(routing.get("excluded_packages", [])) | set(routing.get("manual_only", []))
    )
    if incompatible:
        raise ProjectContextError(
            "CONFLICTING_ROUTING_POLICY",
            f"preferred packages cannot also be excluded or manual-only: {', '.join(sorted(incompatible))}",
        )

    constraints = normalized["constraints"]
    network = constraints.get("network", "ask")
    if network not in {"ask", "deny"}:
        raise ProjectContextError("PERMISSION_GRANT_REJECTED", "constraints.network may only be ask or deny")
    constraints["network"] = network
    credentials = constraints.get("credentials", "never-store")
    if credentials != "never-store":
        raise ProjectContextError("PERMISSION_GRANT_REJECTED", "constraints.credentials must be never-store")
    constraints["credentials"] = credentials

    checkpoint = normalized["checkpoint"]
    for field in ("objective", "next_condition"):
        if field in checkpoint:
            checkpoint[field] = _text(checkpoint[field], f"checkpoint.{field}", maximum=512)
    if "phase" in checkpoint:
        checkpoint["phase"] = _text(checkpoint["phase"], "checkpoint.phase", maximum=160)

    freshness = normalized["freshness"]
    if "verified_at" in freshness:
        freshness["verified_at"] = _text(freshness["verified_at"], "freshness.verified_at", maximum=64)
    if "manifest_source_hash" in freshness:
        source_hash = _text(
            freshness["manifest_source_hash"],
            "freshness.manifest_source_hash",
            maximum=64,
            allow_empty=False,
        ).lower()
        if not HASH_PATTERN.fullmatch(source_hash):
            raise ProjectContextError("INVALID_SCHEMA", "freshness.manifest_source_hash must be SHA-256")
        freshness["manifest_source_hash"] = source_hash

    _reject_sensitive_values(normalized)
    encoded = json.dumps(normalized, sort_keys=True, separators=(",", ":")).encode("utf-8")
    if len(encoded) > MAX_CAPSULE_BYTES:
        raise ProjectContextError("CAPSULE_TOO_LARGE", f"capsule exceeds {MAX_CAPSULE_BYTES} bytes")
    return normalized


def _safe_capsule_path(project_root: Path) -> Path:
    root = project_root.expanduser().resolve()
    if not root.is_dir():
        raise ProjectContextError("PROJECT_NOT_FOUND", "project root must be an existing directory")
    directory = root / CAPSULE_RELATIVE_PATH.parent
    path = root / CAPSULE_RELATIVE_PATH
    if directory.is_symlink() or path.is_symlink():
        raise ProjectContextError("SYMLINK_REJECTED", "project context path must not be a symlink")
    return path


def _read_raw(path: Path) -> bytes:
    try:
        mode = path.stat(follow_symlinks=False).st_mode
    except FileNotFoundError as exc:
        raise ProjectContextError("CAPSULE_MISSING", "project context capsule does not exist") from exc
    if not stat.S_ISREG(mode):
        raise ProjectContextError("INVALID_FILE_TYPE", "project context capsule must be a regular file")
    if path.stat(follow_symlinks=False).st_size > MAX_CAPSULE_BYTES:
        raise ProjectContextError("CAPSULE_TOO_LARGE", f"capsule exceeds {MAX_CAPSULE_BYTES} bytes")
    return path.read_bytes()


def load_project_context(
    project_root: Path,
    *,
    manifest: Mapping[str, Any] | None = None,
) -> ProjectContext:
    """Load one capsule; all expected failures return a fail-open status."""
    try:
        path = _safe_capsule_path(project_root)
        raw = _read_raw(path)
        try:
            payload = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ProjectContextError("INVALID_JSON", "project context capsule is not valid UTF-8 JSON") from exc
        data = validate_capsule(payload, manifest=manifest)
        expected_hash = manifest.get("source_hash") if manifest else None
        capsule_hash = data["freshness"].get("manifest_source_hash")
        if capsule_hash and expected_hash and capsule_hash != expected_hash:
            return ProjectContext(status="stale", data={}, reason_code="MANIFEST_HASH_MISMATCH")
        return ProjectContext(
            status="valid",
            data=data,
            fingerprint=hashlib.sha256(raw).hexdigest(),
        )
    except ProjectContextError as exc:
        status = "missing" if exc.reason_code == "CAPSULE_MISSING" else "invalid"
        return ProjectContext(status=status, data={}, reason_code=exc.reason_code)
    except OSError:
        return ProjectContext(status="invalid", data={}, reason_code="CAPSULE_UNAVAILABLE")


def default_capsule(project_root: Path, manifest: Mapping[str, Any] | None) -> dict[str, Any]:
    freshness: dict[str, str] = {
        "verified_at": dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")
    }
    if manifest and isinstance(manifest.get("source_hash"), str):
        freshness["manifest_source_hash"] = manifest["source_hash"]
    return {
        "schema_version": 1,
        "project": {"name": project_root.resolve().name, "commands": {}},
        "routing": {
            "preferred_packages": [],
            "excluded_packages": [],
            "manual_only": [],
            "capability_hints": {},
        },
        "constraints": {
            "write_scope": [],
            "protected_paths": [],
            "network": "ask",
            "credentials": "never-store",
        },
        "documentation": {
            "canonical_sources": [],
            "generated_outputs": [],
            "validation_commands": [],
        },
        "checkpoint": {},
        "freshness": freshness,
    }


def _load_manifest() -> dict[str, Any] | None:
    try:
        value = json.loads(DEFAULT_MANIFEST.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def _read_stdin_json() -> Any:
    raw = sys.stdin.buffer.read(MAX_STDIN_BYTES + 1)
    if len(raw) > MAX_STDIN_BYTES:
        raise ProjectContextError("CAPSULE_TOO_LARGE", f"stdin exceeds {MAX_STDIN_BYTES} bytes")
    try:
        return json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ProjectContextError("INVALID_JSON", "stdin must contain one UTF-8 JSON object") from exc


def atomic_write_capsule(path: Path, capsule: Mapping[str, Any]) -> None:
    if path.parent.is_symlink() or path.is_symlink():
        raise ProjectContextError("SYMLINK_REJECTED", "project context path must not be a symlink")
    path.parent.mkdir(mode=0o755, parents=True, exist_ok=True)
    content = json.dumps(capsule, indent=2, sort_keys=True) + "\n"
    descriptor, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent, text=True)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            os.fchmod(handle.fileno(), 0o644)
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


def _emit(value: Mapping[str, Any], *, stream: Any = sys.stdout) -> None:
    print(json.dumps(value, indent=2, sort_keys=True), file=stream)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name in ("inspect", "show", "check", "refresh", "delete"):
        subparser = subparsers.add_parser(name)
        subparser.add_argument("--project", required=True, type=Path)
        if name == "delete":
            subparser.add_argument("--confirm-delete", action="store_true")
    init_parser = subparsers.add_parser("init")
    init_parser.add_argument("--project", required=True, type=Path)
    init_parser.add_argument("--stdin-json", action="store_true")
    init_parser.add_argument("--force", action="store_true")
    replace_parser = subparsers.add_parser("replace")
    replace_parser.add_argument("--project", required=True, type=Path)
    replace_parser.add_argument("--stdin-json", action="store_true", required=True)
    args = parser.parse_args(argv)

    manifest = _load_manifest()
    try:
        path = _safe_capsule_path(args.project)
        if args.command == "inspect":
            context = load_project_context(args.project, manifest=manifest)
            _emit(context.receipt())
            return 0
        if args.command == "show":
            raw = _read_raw(path)
            capsule = validate_capsule(json.loads(raw.decode("utf-8")), manifest=manifest)
            _emit(capsule)
            return 0
        if args.command == "check":
            context = load_project_context(args.project, manifest=manifest)
            _emit(context.receipt())
            return 0 if context.status == "valid" else 1
        if args.command == "delete":
            if not args.confirm_delete:
                raise ProjectContextError("CONFIRMATION_REQUIRED", "delete requires --confirm-delete")
            _read_raw(path)
            path.unlink()
            try:
                path.parent.rmdir()
            except OSError:
                pass
            _emit({"result": "deleted", "source": CAPSULE_RELATIVE_PATH.as_posix()})
            return 0

        if args.command == "init":
            if path.exists() and not args.force:
                raise ProjectContextError("CAPSULE_EXISTS", "project context capsule already exists")
            payload = _read_stdin_json() if args.stdin_json else default_capsule(args.project, manifest)
        elif args.command == "replace":
            _read_raw(path)
            payload = _read_stdin_json()
        elif args.command == "refresh":
            payload = validate_capsule(json.loads(_read_raw(path).decode("utf-8")), manifest=None)
            payload["freshness"]["verified_at"] = (
                dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")
            )
            if manifest and isinstance(manifest.get("source_hash"), str):
                payload["freshness"]["manifest_source_hash"] = manifest["source_hash"]
        else:
            raise ProjectContextError("INVALID_COMMAND", "unsupported project context command")

        capsule = validate_capsule(payload, manifest=manifest)
        atomic_write_capsule(path, capsule)
        context = load_project_context(args.project, manifest=manifest)
        _emit({"result": "written", **context.receipt()})
        return 0
    except (ProjectContextError, OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        reason = exc.reason_code if isinstance(exc, ProjectContextError) else "CAPSULE_UNAVAILABLE"
        _emit({"result": "error", "reason": reason}, stream=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
