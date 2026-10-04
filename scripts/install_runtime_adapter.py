#!/usr/bin/env python3
"""Install thin Codex or Claude adapters for the shared Skills AI runtime."""

from __future__ import annotations

import argparse
import hashlib
import re
import json
import os
import shlex
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SHARED_ENTRY = ROOT / "runtime" / "SKILL.md"
CLAUDE_HOOK = ROOT / "adapters" / "claude" / "skills-ai-context.js"
CLAUDE_MANAGED_MARKERS = (
    b"// skills-ai-managed: claude-context",
    b"// skills-ai-managed: claude-router",
    b"// Claude UserPromptSubmit adapter for the shared Skills AI runtime.",
)
CODEX_MANAGED_MARKERS = (
    b"name: skills-ai-registry",
    b"# Skills AI Shared Runtime Entry",
)


class InstallError(RuntimeError):
    pass


def atomic_write(path: Path, content: bytes, *, mode: int = 0o600) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            os.fchmod(handle.fileno(), mode)
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


def installed_content(source: Path) -> bytes:
    content = source.read_bytes()
    if source == SHARED_ENTRY:
        core_path=ROOT / 'runtime/skills-orchestrator/SKILL.md'
        raw=core_path.read_bytes()
        core=re.sub(rb'^---[\s\S]*?---\s*',b'',raw)
        content = content.replace(b'{{SKILLS_AI_ROOT}}', str(ROOT).encode()).replace(b'{{CORE_SHA256}}',hashlib.sha256(raw).hexdigest().encode())
        content += b'\n' + core
    return content


def install_file(
    source: Path,
    target: Path,
    *,
    managed_markers: tuple[bytes, ...],
    dry_run: bool = False,
) -> str:
    if not source.is_file():
        raise InstallError(f"source is missing: {source}")
    if target.is_symlink():
        raise InstallError(f"refusing to replace symlink target: {target}")
    content = installed_content(source)
    target_content = target.read_bytes() if target.exists() else None
    if target_content == content:
        return "unchanged"
    if target_content is not None and not any(marker in target_content for marker in managed_markers):
        return "preserved-foreign"
    if dry_run:
        return "would-update"
    atomic_write(target, content)
    return "updated"


def backup_settings(config_dir: Path, original_settings: bytes) -> None:
    """Keep the first pre-install state and the state before the latest update."""
    first_backup = config_dir / "settings.json.skills-ai.bak"
    if not first_backup.exists():
        atomic_write(first_backup, original_settings)
        return
    atomic_write(config_dir / "settings.json.skills-ai.previous", original_settings)


def remove_managed_file(source: Path, target: Path, *, dry_run: bool = False) -> str:
    """Remove only an installer-managed byte-for-byte copy."""
    if not target.exists() and not target.is_symlink():
        return "absent"
    if target.is_symlink() or not target.is_file():
        return "preserved-foreign"
    if target.read_bytes() not in (source.read_bytes(), installed_content(source)):
        return "preserved-foreign"
    if dry_run:
        return "would-remove"
    target.unlink()
    return "removed"


def claude_hook_command(hook_path: Path) -> str:
    return f"node {shlex.quote(str(hook_path))} --root {shlex.quote(str(ROOT))}"


def merged_claude_settings(settings: dict[str, Any], hook_path: Path) -> dict[str, Any]:
    hooks = settings.setdefault("hooks", {})
    if not isinstance(hooks, dict): raise InstallError("Claude hooks must be an object")
    command = claude_hook_command(hook_path)
    previous_path=hook_path.with_name('skills-ai-router.js')
    previous_owned=previous_path.is_file() and not previous_path.is_symlink() and any(marker in previous_path.read_bytes() for marker in CLAUDE_MANAGED_MARKERS)
    def owned_command(value):
        if value==command:return True
        if not previous_owned or not isinstance(value,str):return False
        try:parts=shlex.split(value)
        except ValueError:return False
        return len(parts)==4 and parts[0]=='node' and parts[1]==str(previous_path) and parts[2]=='--root' and Path(parts[3]).is_absolute()
    for event in ("SessionStart", "UserPromptSubmit"):
        entries = hooks.setdefault(event, [])
        if not isinstance(entries, list): raise InstallError(f"Claude hooks.{event} must be a list")
        retained = []
        for entry in entries:
            if not isinstance(entry, dict) or not isinstance(entry.get("hooks"), list):
                retained.append(entry); continue
            # Only exact commands owned by this installer are migrated.
            foreign = [hook for hook in entry["hooks"] if not isinstance(hook, dict) or not owned_command(hook.get("command"))]
            if foreign: retained.append(entry | {"hooks": foreign})
        retained.append({"hooks": [{"type": "command", "command": command, "timeout": 3,
                                    "statusMessage": "Refreshing Skills AI context..."}]})
        hooks[event] = retained
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
        return {
            "entry": install_file(
                SHARED_ENTRY,
                target,
                managed_markers=CODEX_MANAGED_MARKERS,
                dry_run=dry_run,
            )
        }
    if adapter != "claude":
        raise InstallError(f"unsupported adapter: {adapter}")

    settings_path = config_dir / "settings.json"
    settings, original_settings = _load_settings(settings_path)
    skill_target = config_dir / "skills" / "skills-ai-registry" / "SKILL.md"
    hook_target = config_dir / "hooks" / "skills-ai-context.js"
    hook_result = install_file(
        CLAUDE_HOOK,
        hook_target,
        managed_markers=CLAUDE_MANAGED_MARKERS,
        dry_run=dry_run,
    )
    if hook_result == "preserved-foreign":
        return {
            "entry": "not-attempted",
            "hook": hook_result,
            "settings": "preserved",
        }
    updated_settings = merged_claude_settings(settings, hook_target)
    settings_content = (json.dumps(updated_settings, indent=2, sort_keys=True) + "\n").encode()
    settings_result = "unchanged" if original_settings == settings_content else "would-update" if dry_run else "updated"
    results = {
        # The hook performs routing and context injection. Keeping the shared
        # bootstrap in Claude's skill memory would duplicate that authority.
        "entry": remove_managed_file(SHARED_ENTRY, skill_target, dry_run=dry_run),
        "hook": hook_result,
        "settings": settings_result,
    }
    if not dry_run and settings_result == "updated":
        if original_settings is not None:
            backup_settings(config_dir, original_settings)
        atomic_write(settings_path, settings_content)
    return results


def check_adapter(adapter: str, config_dir: Path) -> bool:
    if adapter == "codex":
        target = config_dir / "skills" / "skills-ai-registry" / "SKILL.md"
        return target.is_file() and not target.is_symlink() and target.read_bytes() == installed_content(SHARED_ENTRY)
    skill_target = config_dir / "skills" / "skills-ai-registry" / "SKILL.md"
    hook_target = config_dir / "hooks" / "skills-ai-context.js"
    if skill_target.is_file() and not skill_target.is_symlink() and skill_target.read_bytes() == installed_content(SHARED_ENTRY):
        return False
    if not hook_target.is_file() or hook_target.read_bytes() != CLAUDE_HOOK.read_bytes():
        return False
    settings, _ = _load_settings(config_dir / "settings.json")
    expected = claude_hook_command(hook_target)
    return all(sum(hook.get("command") == expected
                   for entry in settings.get("hooks", {}).get(event, []) if isinstance(entry, dict)
                   for hook in entry.get("hooks", []) if isinstance(hook, dict)) == 1
               for event in ("SessionStart", "UserPromptSubmit"))


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
