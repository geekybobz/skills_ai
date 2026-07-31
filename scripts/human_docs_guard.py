#!/usr/bin/env python3
"""Validate the derivative human guide and its staged update coverage."""

from __future__ import annotations

import argparse
import fnmatch
import json
import re
import subprocess
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
SOURCE_MAP_PATH = Path("docs/human/_SOURCE_MAP.json")
AGENT_ENTRY_PATHS = (Path("AGENTS.md"), Path("CLAUDE.md"))
MANIFEST_PATH = Path("runtime/router-manifest.json")
HUMAN_BOUNDARY_TEXT = "`README.md` and `docs/human/` are human-facing explanations."


class HumanDocsError(RuntimeError):
    pass


def load_source_map(root: Path = ROOT) -> dict[str, Any]:
    path = root / SOURCE_MAP_PATH
    try:
        config = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise HumanDocsError(f"cannot read {SOURCE_MAP_PATH}: {type(exc).__name__}") from exc
    if config.get("version") != 1:
        raise HumanDocsError("unsupported human-doc source-map version")
    if not isinstance(config.get("human_entry"), str):
        raise HumanDocsError("human_entry must be a path string")
    if not isinstance(config.get("required_marker"), str):
        raise HumanDocsError("required_marker must be a string")
    if not isinstance(config.get("rules"), list) or not config["rules"]:
        raise HumanDocsError("rules must be a non-empty list")
    return config


def _matches(path: str, pattern: str) -> bool:
    return fnmatch.fnmatchcase(path, pattern)


def guide_paths(config: dict[str, Any]) -> list[str]:
    paths = {config["human_entry"]}
    for rule in config["rules"]:
        paths.update(rule.get("guides", []))
    return sorted(paths)


def required_guides(changed_paths: Iterable[str], config: dict[str, Any]) -> dict[str, list[str]]:
    required: dict[str, set[str]] = {}
    for raw_path in changed_paths:
        path = Path(raw_path).as_posix().lstrip("./")
        for rule in config["rules"]:
            if any(_matches(path, pattern) for pattern in rule.get("sources", [])):
                for guide in rule.get("guides", []):
                    required.setdefault(guide, set()).add(rule["name"])
    return {guide: sorted(names) for guide, names in sorted(required.items())}


def coverage_errors(changed_paths: Iterable[str], config: dict[str, Any]) -> list[str]:
    changed = {Path(path).as_posix().lstrip("./") for path in changed_paths}
    errors: list[str] = []
    for guide, rule_names in required_guides(changed, config).items():
        if guide not in changed:
            errors.append(
                f"mapped human page not changed: {guide} "
                f"(required by {', '.join(rule_names)})"
            )
    return errors


def _validate_markdown(path: Path, root: Path, marker: str) -> list[str]:
    relative = path.relative_to(root).as_posix()
    errors: list[str] = []
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return [f"cannot read human page {relative}: {type(exc).__name__}"]
    if marker not in text[:500]:
        errors.append(f"human page missing marker {marker!r}: {relative}")

    fence: tuple[int, str] | None = None
    for line_number, line in enumerate(text.splitlines(), start=1):
        if not line.startswith("```"):
            continue
        if fence is None:
            fence = (line_number, line[3:].strip())
        else:
            fence = None
    if fence is not None:
        errors.append(f"unclosed {fence[1] or 'code'} fence in {relative}:{fence[0]}")

    for target in re.findall(r"(?<!!)\[[^\]]+\]\(([^)]+)\)", text):
        destination = target.strip().strip("<>").split("#", 1)[0]
        if not destination or re.match(r"^[a-z]+://", destination) or destination.startswith("mailto:"):
            continue
        resolved = (path.parent / destination).resolve(strict=False)
        try:
            resolved.relative_to(root.resolve())
        except ValueError:
            errors.append(f"human link escapes repository in {relative}: {target}")
            continue
        if not resolved.exists():
            errors.append(f"broken human link in {relative}: {target}")
    return errors


def validate_human_docs(root: Path = ROOT) -> list[str]:
    try:
        config = load_source_map(root)
    except HumanDocsError as exc:
        return [str(exc)]
    errors: list[str] = []
    marker = config["required_marker"]
    names: set[str] = set()
    for index, rule in enumerate(config["rules"]):
        name = rule.get("name")
        if not isinstance(name, str) or not name:
            errors.append(f"rule {index} has no name")
        elif name in names:
            errors.append(f"duplicate source-map rule: {name}")
        else:
            names.add(name)
        if not rule.get("sources") or not rule.get("guides"):
            errors.append(f"source-map rule has empty sources or guides: {name or index}")
        for pattern in rule.get("sources", []):
            if not list(root.glob(pattern)):
                errors.append(f"source-map pattern matches nothing: {pattern}")

    for relative in guide_paths(config):
        path = root / relative
        if not path.is_file():
            errors.append(f"human page does not exist: {relative}")
            continue
        errors.extend(_validate_markdown(path, root, marker))

    for entry_path in AGENT_ENTRY_PATHS:
        try:
            entry = (root / entry_path).read_text(encoding="utf-8")
        except OSError as exc:
            errors.append(f"cannot read {entry_path}: {type(exc).__name__}")
            continue
        if HUMAN_BOUNDARY_TEXT not in entry:
            errors.append(f"agent entry is missing the human-guide boundary: {entry_path}")

    try:
        manifest = (root / MANIFEST_PATH).read_text(encoding="utf-8")
    except OSError as exc:
        errors.append(f"cannot read {MANIFEST_PATH}: {type(exc).__name__}")
    else:
        if "docs/human/" in manifest or '"path": "README.md"' in manifest:
            errors.append("human guide leaked into the runtime manifest")
    return errors


def git_changed_paths(root: Path = ROOT, *, staged: bool) -> list[str]:
    command = ["git", "diff"]
    if staged:
        command.append("--cached")
    command.extend(["--name-only", "--diff-filter=ACMRD"])
    completed = subprocess.run(command, cwd=root, text=True, capture_output=True, check=False)
    if completed.returncode:
        raise HumanDocsError(completed.stderr.strip() or "cannot inspect Git changes")
    paths = set(completed.stdout.splitlines())
    if not staged:
        untracked = subprocess.run(
            ["git", "ls-files", "--others", "--exclude-standard"],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )
        if untracked.returncode:
            raise HumanDocsError(untracked.stderr.strip() or "cannot inspect untracked files")
        paths.update(untracked.stdout.splitlines())
    return sorted(path for path in paths if path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--check", action="store_true", help="validate structure and boundaries")
    action.add_argument("--check-staged", action="store_true", help="also require staged source-to-guide coverage")
    action.add_argument("--check-changed", action="store_true", help="also require working-tree source-to-guide coverage")
    args = parser.parse_args(argv)

    errors = validate_human_docs()
    changed: list[str] = []
    try:
        if args.check_staged:
            changed = git_changed_paths(staged=True)
        elif args.check_changed:
            changed = git_changed_paths(staged=False)
        if changed:
            errors.extend(coverage_errors(changed, load_source_map()))
    except HumanDocsError as exc:
        errors.append(str(exc))

    if errors:
        for error in errors:
            print(f"error: {error}")
        return 1
    print(
        f"ok: human guide structure and boundaries"
        + (f"; {len(changed)} changed paths covered" if changed else "")
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
