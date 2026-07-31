#!/usr/bin/env python3
"""Install thin Codex or Claude adapters for the shared Skills AI runtime."""

from __future__ import annotations

import argparse
import json
import os
import shlex
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SHARED_ENTRY = ROOT / "runtime" / "SKILL.md"
CLAUDE_HOOK = ROOT / "adapters" / "claude" / "skills-ai-router.js"


class InstallError(RuntimeError):
    pass


def atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as handle:
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


def install_file(source: Path, target: Path, *, dry_run: bool = False) -> str:
    if not source.is_file():
        raise InstallError(f"source is missing: {source}")
    if target.is_symlink():
        raise InstallError(f"refusing to replace symlink target: {target}")
    content = source.read_bytes()
    if target.exists() and target.read_bytes() == content:
        return "unchanged"
    if dry_run:
        return "would-update"
    atomic_write(target, content)
    return "updated"


def remove_managed_file(source: Path, target: Path, *, dry_run: bool = False) -> str:
    """Remove only an installer-managed byte-for-byte copy."""
    if not target.exists() and not target.is_symlink():
        return "absent"
    if target.is_symlink() or not target.is_file():
        return "preserved-foreign"
    if target.read_bytes() != source.read_bytes():
        return "preserved-foreign"
    if dry_run:
        return "would-remove"
    target.unlink()
    return "removed"


def claude_hook_command(hook_path: Path) -> str:
    return f"node {shlex.quote(str(hook_path))} --root {shlex.quote(str(ROOT))}"


def merged_claude_settings(settings: dict[str, Any], hook_path: Path) -> dict[str, Any]:
    hooks = settings.setdefault("hooks", {})
    entries = hooks.setdefault("UserPromptSubmit", [])
    if not isinstance(entries, list):
        raise InstallError("Claude settings hooks.UserPromptSubmit must be a list")
    command = claude_hook_command(hook_path)
    for entry in entries:
        for hook in entry.get("hooks", []) if isinstance(entry, dict) else []:
            if "skills-ai-router.js" in str(hook.get("command", "")):
                hook.update(
                    {
                        "type": "command",
                        "command": command,
                        "timeout": 3,
                        "statusMessage": "Selecting local skill...",
                    }
                )
                return settings
    entries.append(
        {
            "hooks": [
                {
                    "type": "command",
                    "command": command,
                    "timeout": 3,
                    "statusMessage": "Selecting local skill...",
                }
            ]
        }
    )
    return settings


def _load_settings(path: Path) -> tuple[dict[str, Any], bytes | None]:
    if not path.exists():
        return {}, None
    try:
        raw = path.read_bytes()
        value = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise InstallError(f"cannot parse Claude settings: {exc}") from exc
    if not isinstance(value, dict):
        raise InstallError("Claude settings root must be an object")
    return value, raw


def install_adapter(adapter: str, config_dir: Path, *, dry_run: bool = False) -> dict[str, str]:
    if adapter == "codex":
        target = config_dir / "skills" / "skills-ai-registry" / "SKILL.md"
        return {"entry": install_file(SHARED_ENTRY, target, dry_run=dry_run)}
    if adapter != "claude":
        raise InstallError(f"unsupported adapter: {adapter}")

    settings_path = config_dir / "settings.json"
    settings, original_settings = _load_settings(settings_path)
    skill_target = config_dir / "skills" / "skills-ai-registry" / "SKILL.md"
    hook_target = config_dir / "hooks" / "skills-ai-router.js"
    updated_settings = merged_claude_settings(settings, hook_target)
    settings_content = (json.dumps(updated_settings, indent=2, sort_keys=True) + "\n").encode()
    settings_result = "unchanged" if original_settings == settings_content else "would-update" if dry_run else "updated"
    results = {
        # The hook performs routing and context injection. Keeping the shared
        # bootstrap in Claude's skill memory would duplicate that authority.
        "entry": remove_managed_file(SHARED_ENTRY, skill_target, dry_run=dry_run),
        "hook": install_file(CLAUDE_HOOK, hook_target, dry_run=dry_run),
        "settings": settings_result,
    }
    if not dry_run and settings_result == "updated":
        if original_settings is not None:
            atomic_write(config_dir / "settings.json.skills-ai.bak", original_settings)
        atomic_write(settings_path, settings_content)
    return results


def check_adapter(adapter: str, config_dir: Path) -> bool:
    if adapter == "codex":
        target = config_dir / "skills" / "skills-ai-registry" / "SKILL.md"
        return target.is_file() and not target.is_symlink() and target.read_bytes() == SHARED_ENTRY.read_bytes()
    skill_target = config_dir / "skills" / "skills-ai-registry" / "SKILL.md"
    hook_target = config_dir / "hooks" / "skills-ai-router.js"
    if skill_target.is_file() and not skill_target.is_symlink() and skill_target.read_bytes() == SHARED_ENTRY.read_bytes():
        return False
    if not hook_target.is_file() or hook_target.read_bytes() != CLAUDE_HOOK.read_bytes():
        return False
    settings, _ = _load_settings(config_dir / "settings.json")
    entries = settings.get("hooks", {}).get("UserPromptSubmit", [])
    return any(
        "skills-ai-router.js" in str(hook.get("command", ""))
        for entry in entries if isinstance(entry, dict)
        for hook in entry.get("hooks", []) if isinstance(hook, dict)
    )


def default_config_dir(adapter: str) -> Path:
    if adapter == "claude":
        configured = os.environ.get("CLAUDE_CONFIG_DIR")
        return Path(configured) if configured else Path.home() / ".claude"
    return Path.home() / ".codex"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--adapter", choices=("codex", "claude"), required=True)
    parser.add_argument("--config-dir", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    config_dir = args.config_dir or default_config_dir(args.adapter)
    try:
        if args.check:
            if not check_adapter(args.adapter, config_dir):
                print(f"stale: {args.adapter} adapter in {config_dir}")
                return 1
            print(f"ok: {args.adapter} adapter in {config_dir}")
            return 0
        results = install_adapter(args.adapter, config_dir, dry_run=args.dry_run)
        print(json.dumps({"adapter": args.adapter, "config_dir": str(config_dir), "files": results}, sort_keys=True))
        return 0
    except (OSError, InstallError) as exc:
        print(f"error: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
