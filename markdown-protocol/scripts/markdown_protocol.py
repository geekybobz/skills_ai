#!/usr/bin/env python3
"""On-demand checks and generated inventory for Markdown Protocol collections."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import unicodedata
from collections import deque
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from urllib.parse import unquote
from urllib.error import URLError
from urllib.request import urlopen


ROLES = {"front-door", "map", "index", "topic", "deep", "generated"}
STATUSES = {"draft", "active", "stable", "deprecated", "archived"}
REQUIRED_PROPERTIES = ("role", "summary", "read_when")
CONNECTION_LABELS = ("parent", "prerequisite", "related", "next", "deeper")
LINK_RE = re.compile(r"!?\[[^]]*\]\(([^)\n]+)\)")
REFERENCE_USE_RE = re.compile(r"(?<!!)\[([^]\n]+)\]\[([^]\n]*)\]")
REFERENCE_DEFINITION_RE = re.compile(
    r"^ {0,3}\[([^]\n]+)\]:[ \t]*(?:<([^>\n]+)>|(\S+))(?:[ \t]+.*)?$",
    re.MULTILINE,
)
ATX_HEADING_RE = re.compile(r"^ {0,3}(#{1,6})[ \t]+(.+?)[ \t]*$")
SETEXT_UNDERLINE_RE = re.compile(r"^ {0,3}(?:=+|-+)[ \t]*$")
FENCE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
CONNECTION_LINE_RE = re.compile(r"^[-*+]\s+([^:]+):\s*(.*?)\s*$")
NEXT_FOOTER_RE = re.compile(r"\[Next →\]\(([^)]+)\)")
PREVIOUS_FOOTER_RE = re.compile(r"\[← Previous\]\(([^)]+)\)")
TAG_RE = re.compile(r"^(domain|use)/[a-z0-9][a-z0-9-]*(?:/[a-z0-9][a-z0-9-]*)*$")
VERSION = "0.1.0"
DEFAULT_VERSION_URL = (
    "https://raw.githubusercontent.com/geekybobz/markdown-protocol/main/pyproject.toml"
)


@dataclass(frozen=True)
class Finding:
    level: str
    path: str
    message: str
    code: str = "MDP000"


@dataclass(frozen=True)
class Connection:
    label: str
    raw_target: str
    resolved: Path


def markdown_files(root: Path) -> list[Path]:
    return sorted(
        path
        for path in root.rglob("*.md")
        if not any(part.startswith(".") for part in path.relative_to(root).parts)
    )


def read_utf8(path: Path) -> str:
    """Read portable Markdown and consume an optional leading UTF-8 BOM."""
    try:
        return path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValueError("not valid UTF-8") from exc
    except OSError as exc:
        raise ValueError(f"cannot read file: {exc}") from exc


def split_frontmatter(text: str) -> tuple[list[str], str]:
    text = text.removeprefix("\ufeff")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return [], text
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            return lines[1:index], "\n".join(lines[index + 1 :])
    return [], text


def properties(text: str) -> dict[str, object]:
    frontmatter, _ = split_frontmatter(text)
    result: dict[str, object] = {}
    current_list: str | None = None
    for raw in frontmatter:
        if raw.startswith("  - ") and current_list:
            values = result.setdefault(current_list, [])
            assert isinstance(values, list)
            values.append(raw[4:].strip().strip('"\''))
            continue
        current_list = None
        if not raw.strip() or raw.lstrip().startswith("#") or ":" not in raw:
            continue
        key, value = raw.split(":", 1)
        key = key.strip()
        value = value.strip().strip('"\'')
        if value:
            result[key] = value
        else:
            result[key] = []
            current_list = key
    return result


def validated_tags(data: dict[str, object]) -> tuple[list[str], list[str]]:
    value = data.get("tags", [])
    if value in (None, ""):
        return [], []
    if not isinstance(value, list):
        return [], ["tags property must be an indented list"]
    tags = [str(item) for item in value]
    problems: list[str] = []
    if len(tags) != len(set(tags)):
        problems.append("duplicate tag")
    for tag in tags:
        if not TAG_RE.fullmatch(tag):
            problems.append(f"invalid tag: {tag}; use domain/... or use/...")
    return tags, problems


def validated_freshness(data: dict[str, object]) -> tuple[str, date | None, list[str]]:
    status = str(data.get("status", ""))
    problems: list[str] = []
    if status and status not in STATUSES:
        problems.append(f"invalid status: {status}; use {', '.join(sorted(STATUSES))}")

    raw_reviewed = str(data.get("reviewed", ""))
    reviewed: date | None = None
    if raw_reviewed:
        try:
            reviewed = date.fromisoformat(raw_reviewed)
        except ValueError:
            problems.append("reviewed property must use YYYY-MM-DD")
    return status, reviewed, problems


def iso_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("expected YYYY-MM-DD") from exc


def without_fenced_code(text: str) -> str:
    lines: list[str] = []
    fence_character: str | None = None
    fence_length = 0
    for line in text.splitlines():
        if fence_character:
            closing = re.match(
                rf"^ {{0,3}}{re.escape(fence_character)}{{{fence_length},}}[ \t]*$",
                line,
            )
            if closing:
                fence_character = None
                fence_length = 0
            continue
        opening = FENCE_RE.match(line)
        if opening:
            marker = opening.group(1)
            fence_character = marker[0]
            fence_length = len(marker)
            continue
        lines.append(line)
    return "\n".join(lines)


def without_inline_code(text: str) -> str:
    """Remove code spans while retaining surrounding Markdown for link scans."""
    return re.sub(r"(`+)(.*?)\1", lambda match: " " * len(match.group(0)), text, flags=re.DOTALL)


def visible_heading_text(heading: str) -> str:
    heading = re.sub(r"\s+#+\s*$", "", heading)
    heading = re.sub(r"!\[([^]]*)\]\([^)]+\)", r"\1", heading)
    heading = re.sub(r"\[([^]]+)\]\([^)]+\)", r"\1", heading)
    heading = re.sub(r"`+([^`]*)`+", r"\1", heading)
    return re.sub(r"[*~]", "", heading)


def github_slug(heading: str) -> str:
    visible = visible_heading_text(heading).lower()
    kept = []
    for character in visible:
        category = unicodedata.category(character)
        if character in {"_", "-", " "} or category[0] in {"L", "M", "N"}:
            kept.append(character)
    return "".join(kept).replace(" ", "-")


def slugged_headings(text: str) -> set[str]:
    lines = without_fenced_code(text).splitlines()
    seen: dict[str, int] = {}
    anchors: set[str] = set()
    headings: list[str] = []
    for index, line in enumerate(lines):
        match = ATX_HEADING_RE.match(line)
        if match:
            headings.append(match.group(2))
            continue
        if index and SETEXT_UNDERLINE_RE.match(line) and lines[index - 1].strip():
            headings.append(lines[index - 1].strip())
    for heading in headings:
        base = github_slug(heading)
        count = seen.get(base, 0)
        seen[base] = count + 1
        anchors.add(base if count == 0 else f"{base}-{count}")
    return anchors


def link_destination(raw_target: str) -> str:
    target = raw_target.strip()
    if target.startswith("<"):
        end = target.find(">")
        return target[1:end] if end >= 0 else target.strip("<>")
    return target.split(maxsplit=1)[0] if target else ""


def local_links(path: Path, root: Path, text: str) -> list[tuple[str, str | None, Path]]:
    links: list[tuple[str, str | None, Path]] = []
    cleaned = without_inline_code(without_fenced_code(text))
    raw_targets = list(LINK_RE.findall(cleaned))
    definitions: dict[str, str] = {}
    for label, angled, plain in REFERENCE_DEFINITION_RE.findall(cleaned):
        definitions[label.strip().casefold()] = angled or plain
    for label, reference in REFERENCE_USE_RE.findall(cleaned):
        key = (reference or label).strip().casefold()
        if key in definitions:
            raw_targets.append(definitions[key])
    for raw_target in raw_targets:
        target = link_destination(raw_target)
        if target.startswith(("http://", "https://", "mailto:", "codex://")):
            continue
        file_part, separator, anchor = target.partition("#")
        if not file_part:
            resolved = path
        else:
            resolved = (path.parent / unquote(file_part)).resolve()
        links.append((target, unquote(anchor) if separator else None, resolved))
    return links


def resolve_local_target(path: Path, raw_target: str) -> Path | None:
    target = link_destination(raw_target)
    if target.startswith(("http://", "https://", "mailto:", "codex://")):
        return None
    file_part = target.partition("#")[0]
    if not file_part:
        return path.resolve()
    return (path.parent / unquote(file_part)).resolve()


def connection_section(text: str) -> list[str]:
    cleaned = without_fenced_code(text)
    match = re.search(r"^## Connections\s*$", cleaned, flags=re.MULTILINE)
    if not match:
        return []
    remainder = cleaned[match.end() :]
    next_heading = re.search(r"^##\s+", remainder, flags=re.MULTILINE)
    section = remainder[: next_heading.start()] if next_heading else remainder
    return section.splitlines()


def parse_connections(path: Path, text: str) -> tuple[list[Connection], list[str]]:
    connections: list[Connection] = []
    problems: list[str] = []
    counts: dict[str, int] = {}
    for line in connection_section(text):
        match = CONNECTION_LINE_RE.match(line.strip())
        if not match:
            continue
        label = match.group(1).strip().lower()
        value = match.group(2).strip()
        if label not in CONNECTION_LABELS:
            problems.append(f"unknown connection label: {match.group(1).strip()}")
            continue
        raw_targets = LINK_RE.findall(value)
        if not raw_targets:
            if value not in {"", "—", "-", "none", "None"}:
                problems.append(f"{label} connection needs a local Markdown link")
            continue
        counts[label] = counts.get(label, 0) + len(raw_targets)
        for raw_target in raw_targets:
            resolved = resolve_local_target(path, raw_target)
            if resolved is None:
                problems.append(f"{label} connection must be local: {raw_target}")
                continue
            connections.append(Connection(label, raw_target, resolved))
    for label in ("parent", "next"):
        if counts.get(label, 0) > 1:
            problems.append(f"{label} connection allows at most one target")
    return connections, problems


def prerequisite_cycle(typed: dict[Path, dict[str, set[Path]]]) -> list[Path]:
    state: dict[Path, int] = {}
    stack: list[Path] = []

    def visit(node: Path) -> list[Path]:
        state[node] = 1
        stack.append(node)
        for dependency in sorted(typed.get(node, {}).get("prerequisite", set())):
            if state.get(dependency, 0) == 0:
                cycle = visit(dependency)
                if cycle:
                    return cycle
            elif state.get(dependency) == 1:
                start = stack.index(dependency)
                return stack[start:] + [dependency]
        stack.pop()
        state[node] = 2
        return []

    nodes = set(typed)
    for by_label in typed.values():
        nodes.update(by_label.get("prerequisite", set()))
    for node in sorted(nodes):
        if state.get(node, 0) == 0:
            cycle = visit(node)
            if cycle:
                return cycle
    return []


def learning_order(typed: dict[Path, dict[str, set[Path]]]) -> list[Path]:
    nodes: set[Path] = set()
    for source, by_label in typed.items():
        if any(by_label.values()):
            nodes.add(source)
        for targets in by_label.values():
            nodes.update(targets)
    outgoing: dict[Path, set[Path]] = {node: set() for node in nodes}
    indegree: dict[Path, int] = {node: 0 for node in nodes}
    for topic, by_label in typed.items():
        for prerequisite in by_label.get("prerequisite", set()):
            outgoing.setdefault(prerequisite, set()).add(topic)
            indegree[topic] = indegree.get(topic, 0) + 1
    ready = sorted(node for node, degree in indegree.items() if degree == 0)
    order: list[Path] = []
    while ready:
        node = ready.pop(0)
        order.append(node)
        for dependent in sorted(outgoing.get(node, set())):
            indegree[dependent] -= 1
            if indegree[dependent] == 0:
                ready.append(dependent)
                ready.sort()
    return order if len(order) == len(nodes) else []


def transitive_prerequisites(topic: Path, typed: dict[Path, dict[str, set[Path]]]) -> set[Path]:
    required: set[Path] = set()
    queue: deque[Path] = deque(typed.get(topic, {}).get("prerequisite", set()))
    while queue:
        current = queue.popleft()
        if current in required:
            continue
        required.add(current)
        queue.extend(typed.get(current, {}).get("prerequisite", set()))
    return required


def reachable_files(entry: Path, adjacency: dict[Path, set[Path]]) -> set[Path]:
    reachable: set[Path] = set()
    queue: deque[Path] = deque([entry.resolve()])
    while queue:
        current = queue.popleft()
        if current in reachable:
            continue
        reachable.add(current)
        queue.extend(adjacency.get(current, ()))
    return reachable


def compact_line_count(text: str, role: str) -> int:
    _, body = split_frontmatter(text)
    before_details = body.split("\n## Details", 1)[0]
    if role == "front-door":
        return sum(1 for line in before_details.splitlines() if line.strip())
    if role != "topic":
        return 0
    lines = before_details.splitlines()
    active = False
    count = 0
    for line in lines:
        if line.startswith("## "):
            active = line.strip() in {"## In brief", "## Core"}
            continue
        if active and line.strip():
            count += 1
    return count


def choose_entry(root: Path, entry: str | None) -> Path | None:
    if entry:
        candidate = (root / entry).resolve()
        return candidate if candidate.is_file() else None
    for name in ("README.md", "SKILL.md", "INDEX.md"):
        candidate = (root / name).resolve()
        if candidate.is_file():
            return candidate
    return None


def render_inventory(root: Path, output: str = "INVENTORY.md", entry: str | None = None) -> str:
    root = root.resolve()
    output_path = (root / output).resolve()
    rows: list[tuple[str, str, str, str]] = []
    errors: list[str] = []
    for path in markdown_files(root):
        if path.resolve() == output_path:
            continue
        try:
            text = read_utf8(path)
        except ValueError as exc:
            errors.append(f"{path.relative_to(root)}: {exc}")
            continue
        data = properties(text)
        missing = [key for key in REQUIRED_PROPERTIES if not data.get(key)]
        role = str(data.get("role", ""))
        if role not in ROLES:
            missing.append("valid role")
        if role != "front-door" and not data.get("parent"):
            missing.append("parent")
        if missing:
            errors.append(f"{path.relative_to(root)}: missing {', '.join(dict.fromkeys(missing))}")
            continue
        parent = data.get("parent")
        if parent:
            parent_path = (path.parent / str(parent)).resolve()
            if root.resolve() not in parent_path.parents and parent_path != root.resolve():
                errors.append(f"{path.relative_to(root)}: parent escapes collection root")
                continue
            if not parent_path.is_file():
                errors.append(f"{path.relative_to(root)}: parent does not exist: {parent}")
                continue
        rows.append(
            (
                path.relative_to(root).as_posix(),
                role,
                str(data["summary"]),
                str(data["read_when"]),
            )
        )
    if errors:
        raise ValueError("\n".join(errors))

    entry_path = choose_entry(root, entry)
    home = entry_path.relative_to(root).as_posix() if entry_path else "README.md"
    core = [row for row in rows if row[1] not in {"deep", "generated"}]
    optional = [row for row in rows if row[1] in {"deep", "generated"}]

    def table(items: list[tuple[str, str, str, str]]) -> list[str]:
        def cell(value: str) -> str:
            return value.replace("|", "\\|").replace("\n", " ")

        result = ["| path | role | summary | read when |", "|---|---|---|---|"]
        for path, role, summary, read_when in sorted(items):
            result.append(
                f"| [{path}]({path}) | {cell(role)} | {cell(summary)} | {cell(read_when)} |"
            )
        if not items:
            result.append("| — | — | No files in this group. | — |")
        return result

    lines = [
        "---",
        "role: generated",
        f"parent: {home}",
        "summary: Generated inventory of protocol-managed Markdown files.",
        "read_when: Read when an exhaustive file listing is needed.",
        "---",
        "<!-- Generated file. Do not edit directly.",
        "Source: Markdown properties in this collection.",
        "Regenerate with: markdown_protocol.py inventory <root> --write",
        "-->",
        "",
        "# Markdown Inventory",
        "",
        "Generated from the structured properties of this collection. The authored",
        "Front Door or `INDEX.md` remains the semantic route map.",
        "",
        "## Core files",
        "",
        *table(core),
        "",
        "## Optional",
        "",
        *table(optional),
        "",
        "---",
        "",
        f"[⌂ Home]({home})",
        "",
    ]
    return "\n".join(lines)


def check_collection(
    root: Path,
    *,
    entry: str | None = None,
    require_properties: bool = False,
    inventory: str = "INVENTORY.md",
    reviewed_since: date | None = None,
    adoption: bool = False,
) -> list[Finding]:
    root = root.resolve()
    findings: list[Finding] = []
    files = markdown_files(root)
    file_set = {path.resolve() for path in files}
    adjacency: dict[Path, set[Path]] = {path.resolve(): set() for path in files}
    typed: dict[Path, dict[str, set[Path]]] = {
        path.resolve(): {label: set() for label in CONNECTION_LABELS} for path in files
    }
    texts: dict[Path, str] = {}
    headings: dict[Path, set[str]] = {}

    for path in files:
        relative = path.relative_to(root).as_posix()
        try:
            text = read_utf8(path)
        except ValueError as exc:
            findings.append(Finding("error", relative, str(exc), "MDP101"))
            continue
        resolved = path.resolve()
        texts[resolved] = text
        headings[resolved] = slugged_headings(text)

    entry_path = choose_entry(root, entry)

    for path in files:
        relative = path.relative_to(root).as_posix()
        resolved_path = path.resolve()
        if resolved_path not in texts:
            continue
        text = texts[resolved_path]
        data = properties(text)
        role = str(data.get("role", ""))
        managed = bool(role) or require_properties
        if managed:
            _, tag_problems = validated_tags(data)
            for problem in tag_problems:
                findings.append(Finding("error", relative, problem, "MDP201"))
            status, reviewed, freshness_problems = validated_freshness(data)
            for problem in freshness_problems:
                findings.append(Finding("error", relative, problem, "MDP202"))
            if reviewed_since and role in {"topic", "deep"} and status not in {"deprecated", "archived"}:
                if reviewed is None and not freshness_problems:
                    findings.append(
                        Finding(
                            "warning",
                            relative,
                            f"not reviewed since {reviewed_since}: missing reviewed property",
                            "MDP203",
                        )
                    )
                elif reviewed and reviewed < reviewed_since:
                    findings.append(
                        Finding(
                            "warning",
                            relative,
                            f"not reviewed since {reviewed_since}: last reviewed {reviewed}",
                            "MDP203",
                        )
                    )
        if require_properties:
            for key in REQUIRED_PROPERTIES:
                if not data.get(key):
                    findings.append(Finding("error", relative, f"missing property: {key}"))
            if role not in ROLES:
                findings.append(Finding("error", relative, "missing or invalid property: role"))
            if role != "front-door" and not data.get("parent"):
                findings.append(Finding("error", relative, "missing property: parent"))
            parent = data.get("parent")
            if parent:
                parent_path = (path.parent / str(parent)).resolve()
                if root.resolve() not in parent_path.parents and parent_path != root.resolve():
                    findings.append(Finding("error", relative, "parent escapes collection root"))
                elif not parent_path.is_file():
                    findings.append(Finding("error", relative, f"parent does not exist: {parent}"))

        if role == "generated":
            head = "\n".join(text.splitlines()[:20])
            for marker in ("Generated file. Do not edit directly.", "Source:", "Regenerate with:"):
                if marker not in head:
                    findings.append(Finding("error", relative, f"generated banner missing: {marker}"))

        effective_role = role
        if not effective_role and entry_path and resolved_path == entry_path:
            effective_role = "front-door"
        elif not effective_role and re.search(r"^## (?:In brief|Core)\s*$", without_fenced_code(text), re.MULTILINE):
            effective_role = "topic"
        compact = compact_line_count(text, effective_role)
        threshold = 60 if effective_role == "front-door" else 30 if effective_role == "topic" else 0
        if threshold and compact > threshold:
            findings.append(
                Finding("warning", relative, f"compact section has {compact} lines; review threshold is {threshold}")
            )

        nonempty = [line for line in text.splitlines() if line.strip()]
        if len(nonempty) < 2 or nonempty[-2].strip() != "---" or "[⌂ Home]" not in nonempty[-1]:
            findings.append(
                Finding(
                    "warning" if adoption else "error",
                    relative,
                    "missing final portable Home footer",
                    "MDP301",
                )
            )

        for raw, anchor, resolved in local_links(path, root, text):
            if not resolved.exists():
                findings.append(Finding("error", relative, f"broken link: {link_destination(raw)}", "MDP401"))
                continue
            if resolved in file_set:
                adjacency[resolved_path].add(resolved)
                if anchor and resolved in headings and anchor not in headings[resolved]:
                    findings.append(Finding("error", relative, f"missing anchor: {raw}", "MDP402"))

        connections, problems = parse_connections(path, text)
        for problem in problems:
            findings.append(Finding("error", relative, problem))
        for connection in connections:
            if connection.resolved not in file_set:
                findings.append(
                    Finding(
                        "error",
                        relative,
                        f"broken {connection.label} connection: {connection.raw_target}",
                    )
                )
                continue
            if connection.resolved == path.resolve():
                findings.append(Finding("error", relative, f"self {connection.label} connection"))
                continue
            typed[resolved_path][connection.label].add(connection.resolved)

    for source, by_label in typed.items():
        relative = source.relative_to(root).as_posix()
        for child in by_label["deeper"]:
            if source not in typed.get(child, {}).get("parent", set()):
                findings.append(
                    Finding(
                        "error",
                        relative,
                        f"deeper connection is not reciprocated by Parent: {child.relative_to(root)}",
                    )
                )
        for parent in by_label["parent"]:
            if source not in typed.get(parent, {}).get("deeper", set()):
                findings.append(
                    Finding(
                        "error",
                        relative,
                        f"parent connection is not reciprocated by Deeper: {parent.relative_to(root)}",
                    )
                )
        for next_path in by_label["next"]:
            if source not in texts or next_path not in texts:
                continue
            footer = [line for line in texts[source].splitlines() if line.strip()][-1]
            next_match = NEXT_FOOTER_RE.search(footer)
            next_resolved = resolve_local_target(source, next_match.group(1)) if next_match else None
            if next_resolved != next_path:
                findings.append(Finding("error", relative, "typed Next does not match the footer"))
            target_footer = [line for line in texts[next_path].splitlines() if line.strip()][-1]
            previous_match = PREVIOUS_FOOTER_RE.search(target_footer)
            previous_resolved = (
                resolve_local_target(next_path, previous_match.group(1)) if previous_match else None
            )
            if previous_resolved != source:
                findings.append(
                    Finding(
                        "error",
                        next_path.relative_to(root).as_posix(),
                        f"Previous footer does not reciprocate Next from {relative}",
                    )
                )

    cycle = prerequisite_cycle(typed)
    if cycle:
        route = " -> ".join(path.relative_to(root).as_posix() for path in cycle)
        findings.append(Finding("error", ".", f"prerequisite cycle: {route}"))

    if not entry_path:
        findings.append(Finding("error", ".", "no entry found; use README.md, SKILL.md, INDEX.md, or --entry"))
    else:
        reachable = reachable_files(entry_path, adjacency)
        for orphan in sorted(file_set - reachable):
            findings.append(
                Finding(
                    "warning" if adoption else "error",
                    orphan.relative_to(root).as_posix(),
                    "orphan Markdown file",
                    "MDP501",
                )
            )

    inventory_path = (root / inventory).resolve()
    if inventory_path.is_file():
        try:
            expected = render_inventory(root, inventory, entry)
        except ValueError as exc:
            findings.append(Finding("error", inventory, f"cannot verify inventory: {exc}"))
        else:
            try:
                current_inventory = read_utf8(inventory_path)
            except ValueError as exc:
                findings.append(Finding("error", inventory, str(exc), "MDP101"))
                current_inventory = None
            if current_inventory is not None and current_inventory != expected:
                findings.append(Finding("error", inventory, "generated inventory is stale"))
    return findings


def render_graph_report(root: Path, *, entry: str | None = None, topic: str | None = None) -> str:
    root = root.resolve()
    files = markdown_files(root)
    file_set = {path.resolve() for path in files}
    adjacency: dict[Path, set[Path]] = {path.resolve(): set() for path in files}
    typed: dict[Path, dict[str, set[Path]]] = {
        path.resolve(): {label: set() for label in CONNECTION_LABELS} for path in files
    }
    for path in files:
        try:
            text = read_utf8(path)
        except ValueError as exc:
            raise ValueError(f"{path.relative_to(root)}: {exc}") from exc
        for _, _, resolved in local_links(path, root, text):
            if resolved in file_set:
                adjacency[path.resolve()].add(resolved)
        connections, _ = parse_connections(path, text)
        for connection in connections:
            if connection.resolved in file_set and connection.resolved != path.resolve():
                typed[path.resolve()][connection.label].add(connection.resolved)

    cycle = prerequisite_cycle(typed)
    if cycle:
        route = " -> ".join(path.relative_to(root).as_posix() for path in cycle)
        raise ValueError(f"prerequisite cycle: {route}")

    lines = ["Markdown connection graph", "", "Learning order:"]
    order = learning_order(typed)
    if order:
        lines.extend(
            f"{number}. {path.relative_to(root).as_posix()}" for number, path in enumerate(order, 1)
        )
    else:
        lines.append("- No typed connections.")

    if topic:
        topic_path = (root / topic).resolve()
        if topic_path not in file_set:
            raise ValueError(f"unknown topic: {topic}")
        required = transitive_prerequisites(topic_path, typed)
        lines.extend(["", f"Required before {topic}:"])
        ordered_required = [path for path in order if path in required]
        if ordered_required:
            lines.extend(f"- {path.relative_to(root).as_posix()}" for path in ordered_required)
        else:
            lines.append("- None.")

    entry_path = choose_entry(root, entry)
    if not entry_path:
        raise ValueError("no entry found; use README.md, SKILL.md, INDEX.md, or --entry")
    orphans = sorted(file_set - reachable_files(entry_path, adjacency))
    lines.extend(["", "Orphans:"])
    if orphans:
        lines.extend(f"- {path.relative_to(root).as_posix()}" for path in orphans)
    else:
        lines.append("- None.")
    return "\n".join(lines) + "\n"


def render_tag_report(root: Path, requested: list[str]) -> str:
    root = root.resolve()
    for tag in requested:
        if not TAG_RE.fullmatch(tag):
            raise ValueError(f"invalid tag: {tag}; use domain/... or use/...")

    records: list[tuple[str, str, str, list[str]]] = []
    vocabulary: dict[str, list[str]] = {}
    for path in markdown_files(root):
        try:
            text = read_utf8(path)
        except ValueError as exc:
            raise ValueError(f"{path.relative_to(root)}: {exc}") from exc
        data = properties(text)
        tags, problems = validated_tags(data)
        if problems:
            continue
        relative = path.relative_to(root).as_posix()
        for tag in tags:
            vocabulary.setdefault(tag, []).append(relative)
        if requested and not all(tag in tags for tag in requested):
            continue
        records.append(
            (
                relative,
                str(data.get("role", "")),
                str(data.get("summary", "")),
                tags,
            )
        )

    if not requested:
        lines = ["Markdown tag vocabulary", ""]
        if vocabulary:
            for tag in sorted(vocabulary):
                lines.append(f"- {tag}: {len(vocabulary[tag])} file(s)")
        else:
            lines.append("- No tags.")
        return "\n".join(lines) + "\n"

    lines = [f"Files matching: {' AND '.join(requested)}", ""]
    if records:
        for path, role, summary, tags in sorted(records):
            detail = f" — {summary}" if summary else ""
            role_text = f" [{role}]" if role else ""
            lines.append(f"- {path}{role_text}{detail} ({', '.join(tags)})")
    else:
        lines.append("- No matching files.")
    return "\n".join(lines) + "\n"


def findings_payload(findings: list[Finding], *, schema: str = "markdown-protocol.verify.v1") -> dict[str, object]:
    return {
        "schema": schema,
        "summary": {
            "errors": sum(item.level == "error" for item in findings),
            "warnings": sum(item.level == "warning" for item in findings),
        },
        "findings": [asdict(item) for item in findings],
    }


def collection_status(root: Path, entry: str | None = None) -> dict[str, object]:
    root = root.resolve()
    files = markdown_files(root)
    managed = 0
    footers = 0
    unreadable = 0
    for path in files:
        try:
            text = read_utf8(path)
        except ValueError:
            unreadable += 1
            continue
        if properties(text).get("role"):
            managed += 1
        nonempty = [line for line in text.splitlines() if line.strip()]
        if len(nonempty) >= 2 and nonempty[-2].strip() == "---" and "[⌂ Home]" in nonempty[-1]:
            footers += 1
    entry_path = choose_entry(root, entry)
    return {
        "schema": "markdown-protocol.status.v1",
        "root": str(root),
        "entry": entry_path.relative_to(root).as_posix() if entry_path else None,
        "files": len(files),
        "managed_files": managed,
        "portable_footers": footers,
        "unreadable_files": unreadable,
    }


def graph_payload(root: Path) -> dict[str, object]:
    root = root.resolve()
    files = markdown_files(root)
    file_set = {path.resolve() for path in files}
    nodes = [
        {"id": f"n{index}", "path": path.relative_to(root).as_posix()}
        for index, path in enumerate(files)
    ]
    identifiers = {path.resolve(): f"n{index}" for index, path in enumerate(files)}
    edges: set[tuple[str, str, str]] = set()
    for path in files:
        try:
            text = read_utf8(path)
        except ValueError as exc:
            raise ValueError(f"{path.relative_to(root)}: {exc}") from exc
        typed_targets = {
            (connection.resolved, connection.label) for connection in parse_connections(path, text)[0]
        }
        for _, _, target in local_links(path, root, text):
            if target in file_set and target != path.resolve():
                labels = [label for resolved, label in typed_targets if resolved == target]
                edges.add((identifiers[path.resolve()], identifiers[target], labels[0] if labels else "link"))
    return {
        "schema": "markdown-protocol.graph.v1",
        "nodes": nodes,
        "edges": [
            {"source": source, "target": target, "kind": kind}
            for source, target, kind in sorted(edges)
        ],
    }


def render_mermaid_graph(root: Path) -> str:
    payload = graph_payload(root)
    lines = ["flowchart TD"]
    for node in payload["nodes"]:
        assert isinstance(node, dict)
        label = str(node["path"]).replace('"', "&quot;")
        lines.append(f'  {node["id"]}["{label}"]')
    for edge in payload["edges"]:
        assert isinstance(edge, dict)
        label = str(edge["kind"])
        lines.append(f'  {edge["source"]} -->|{label}| {edge["target"]}')
    for node in payload["nodes"]:
        assert isinstance(node, dict)
        path = str(node["path"]).replace('"', "%22")
        lines.append(f'  click {node["id"]} "{path}" "Open {path}"')
    return "\n".join(lines) + "\n"


def initialize_collection(root: Path, title: str) -> list[Path]:
    root = root.resolve()
    targets = (root / "README.md", root / "INDEX.md")
    existing = [path for path in targets if path.exists()]
    if existing:
        raise ValueError("refusing to overwrite: " + ", ".join(path.name for path in existing))
    root.mkdir(parents=True, exist_ok=True)
    readme = (
        "---\nrole: front-door\n"
        f"summary: Entry point for {title}.\n"
        "read_when: Start here.\n---\n"
        f"# {title}\n\n## In brief\n\nState the purpose in a few lines.\n\n"
        "## Routes\n\n- [Topic index](INDEX.md)\n\n---\n\n[⌂ Home](README.md)\n"
    )
    index = (
        "---\nrole: index\nparent: README.md\n"
        f"summary: Topic map for {title}.\n"
        "read_when: Browse the available topics.\n---\n"
        "# Topic index\n\nAdd topic links here.\n\n---\n\n[⌂ Home](README.md)\n"
    )
    targets[0].write_text(readme, encoding="utf-8")
    targets[1].write_text(index, encoding="utf-8")
    return list(targets)


def footer_fixes(root: Path, *, apply: bool = False, entry: str | None = None) -> list[Path]:
    root = root.resolve()
    entry_path = choose_entry(root, entry)
    if not entry_path:
        raise ValueError("no entry found; use README.md, SKILL.md, INDEX.md, or --entry")
    changed: list[Path] = []
    for path in markdown_files(root):
        try:
            text = read_utf8(path)
        except ValueError:
            continue
        nonempty = [line for line in text.splitlines() if line.strip()]
        if len(nonempty) >= 2 and nonempty[-2].strip() == "---" and "[⌂ Home]" in nonempty[-1]:
            continue
        changed.append(path)
        if apply:
            relative_home = Path(os.path.relpath(entry_path, path.parent)).as_posix()
            updated = text.rstrip() + f"\n\n---\n\n[⌂ Home]({relative_home})\n"
            temporary = path.with_suffix(path.suffix + ".tmp")
            temporary.write_text(updated, encoding="utf-8")
            temporary.replace(path)
    return changed


def remote_version(url: str) -> str:
    try:
        with urlopen(url, timeout=5) as response:  # noqa: S310 - explicit user command and declared URL
            content = response.read().decode("utf-8")
    except (OSError, UnicodeDecodeError, URLError) as exc:
        raise ValueError(f"cannot check remote version: {exc}") from exc
    match = re.search(r'^version\s*=\s*"([^"]+)"\s*$', content, re.MULTILINE)
    if not match:
        raise ValueError("remote metadata has no project version")
    return match.group(1)


def version_key(value: str) -> tuple[int, ...]:
    match = re.fullmatch(r"(\d+(?:\.\d+)*)", value)
    if not match:
        raise ValueError(f"unsupported version format: {value}")
    return tuple(int(part) for part in value.split("."))


def print_findings(findings: list[Finding]) -> None:
    if not findings:
        print("PASS: Markdown Protocol check")
        return
    for finding in findings:
        print(f"{finding.level.upper()}: {finding.path}: {finding.message}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    def add_check_arguments(command: argparse.ArgumentParser) -> None:
        command.add_argument("root", type=Path)
        command.add_argument("--entry")
        command.add_argument("--require-properties", action="store_true")
        command.add_argument("--inventory", default="INVENTORY.md")
        command.add_argument("--format", choices=("text", "json"), default="text")
        command.add_argument(
            "--reviewed-since",
            type=iso_date,
            help="list topic and deep notes not reviewed since YYYY-MM-DD",
        )

    verify = subparsers.add_parser("verify", help="verify one bounded Markdown collection")
    add_check_arguments(verify)
    check = subparsers.add_parser("check", help="compatibility alias for verify")
    add_check_arguments(check)
    adopt = subparsers.add_parser("adopt", help="audit a collection before protocol adoption")
    add_check_arguments(adopt)

    status = subparsers.add_parser("status", help="show collection coverage and entry point")
    status.add_argument("root", type=Path)
    status.add_argument("--entry")
    status.add_argument("--format", choices=("text", "json"), default="text")

    doctor = subparsers.add_parser("doctor", help="check whether mdp can operate on a collection")
    doctor.add_argument("root", type=Path)
    doctor.add_argument("--format", choices=("text", "json"), default="text")

    initialize = subparsers.add_parser("init", help="create a minimal protocol collection")
    initialize.add_argument("root", type=Path)
    initialize.add_argument("--title", default="Markdown Collection")

    fix = subparsers.add_parser("fix", help="preview or apply deterministic footer repairs")
    fix.add_argument("root", type=Path)
    fix.add_argument("--entry")
    fix.add_argument("--apply", action="store_true")

    subparsers.add_parser("version", help="print the installed mdp version")

    update = subparsers.add_parser("update", help="explicitly check for a newer GitHub version")
    update.add_argument("action", choices=("check",))
    update.add_argument("--url", default=DEFAULT_VERSION_URL)
    update.add_argument("--format", choices=("text", "json"), default="text")

    inventory = subparsers.add_parser("inventory", help="render or verify INVENTORY.md")
    inventory.add_argument("root", type=Path)
    inventory.add_argument("--entry")
    inventory.add_argument("--output", default="INVENTORY.md")
    action = inventory.add_mutually_exclusive_group()
    action.add_argument("--write", action="store_true")
    action.add_argument("--check", action="store_true")

    graph = subparsers.add_parser("graph", help="show typed connections and learning order")
    graph.add_argument("root", type=Path)
    graph.add_argument("--entry")
    graph.add_argument("--topic")
    graph.add_argument("--format", choices=("text", "json", "mermaid"), default="text")

    tags = subparsers.add_parser("tags", help="show tag vocabulary or filter files")
    tags.add_argument("root", type=Path)
    tags.add_argument("--tag", action="append", default=[])

    args = parser.parse_args(argv)
    if args.command == "version":
        print(f"mdp {VERSION}")
        return 0

    if args.command == "update":
        try:
            available = remote_version(args.url)
        except ValueError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 2
        payload = {
            "schema": "markdown-protocol.update.v1",
            "current": VERSION,
            "available": available,
            "update_available": version_key(available) > version_key(VERSION),
            "source": args.url,
        }
        if args.format == "json":
            print(json.dumps(payload, indent=2, sort_keys=True))
        elif payload["update_available"]:
            print(f"UPDATE AVAILABLE: {VERSION} -> {available}")
        else:
            print(f"PASS: mdp {VERSION} is current")
        return 1 if payload["update_available"] else 0

    root = args.root.resolve()
    if args.command == "init":
        try:
            created = initialize_collection(root, args.title)
        except (OSError, ValueError) as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 1
        for path in created:
            print(f"CREATED: {path}")
        return 0

    if not root.is_dir():
        print(f"ERROR: not a directory: {root}", file=sys.stderr)
        return 2

    if args.command in {"verify", "check", "adopt"}:
        findings = check_collection(
            root,
            entry=args.entry,
            require_properties=args.require_properties,
            inventory=args.inventory,
            reviewed_since=args.reviewed_since,
            adoption=args.command == "adopt",
        )
        if args.format == "json":
            print(json.dumps(findings_payload(findings), indent=2, sort_keys=True))
        else:
            print_findings(findings)
        return 1 if any(item.level == "error" for item in findings) else 0

    if args.command == "status":
        payload = collection_status(root, args.entry)
        if args.format == "json":
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print(f"Markdown Protocol status: {payload['root']}")
            print(f"Entry: {payload['entry'] or 'not found'}")
            print(f"Files: {payload['files']}")
            print(f"Managed: {payload['managed_files']}")
            print(f"Portable footers: {payload['portable_footers']}")
            print(f"Unreadable: {payload['unreadable_files']}")
        return 0

    if args.command == "doctor":
        status_payload = collection_status(root)
        payload = {
            "schema": "markdown-protocol.doctor.v1",
            "version": VERSION,
            "python": ".".join(str(part) for part in sys.version_info[:3]),
            "python_ok": sys.version_info >= (3, 10),
            "root_ok": root.is_dir(),
            "entry_ok": status_payload["entry"] is not None,
            "unreadable_files": status_payload["unreadable_files"],
        }
        if args.format == "json":
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            for key, value in payload.items():
                print(f"{key}: {value}")
        return 0 if payload["python_ok"] and payload["root_ok"] else 1

    if args.command == "fix":
        try:
            changed = footer_fixes(root, apply=args.apply, entry=args.entry)
        except ValueError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 1
        action = "FIXED" if args.apply else "WOULD FIX"
        for path in changed:
            print(f"{action}: {path.relative_to(root)}: add portable footer")
        if not changed:
            print("PASS: no deterministic footer repairs needed")
        elif not args.apply:
            print("DRY RUN: use --apply to write these repairs")
        return 0

    if args.command == "graph":
        findings = check_collection(root, entry=args.entry)
        errors = [finding for finding in findings if finding.level == "error"]
        if errors:
            print_findings(errors)
            return 1
        try:
            if args.format == "json":
                print(json.dumps(graph_payload(root), indent=2, sort_keys=True))
            elif args.format == "mermaid":
                print(render_mermaid_graph(root), end="")
            else:
                print(render_graph_report(root, entry=args.entry, topic=args.topic), end="")
        except ValueError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 1
        return 0

    if args.command == "tags":
        try:
            print(render_tag_report(root, args.tag), end="")
        except ValueError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 2
        return 0

    try:
        rendered = render_inventory(root, args.output, args.entry)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    output = (root / args.output).resolve()
    if output.parent != root and root not in output.parents:
        print("ERROR: inventory output escapes the collection root", file=sys.stderr)
        return 2
    if args.check:
        try:
            current = read_utf8(output) if output.is_file() else None
        except ValueError:
            current = None
        if current != rendered:
            print(f"ERROR: stale or missing generated inventory: {args.output}")
            return 1
        print(f"PASS: generated inventory is current: {args.output}")
        return 0
    if args.write:
        output.parent.mkdir(parents=True, exist_ok=True)
        temporary = output.with_suffix(output.suffix + ".tmp")
        temporary.write_text(rendered, encoding="utf-8")
        temporary.replace(output)
        print(f"WROTE: {output}")
        return 0
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
