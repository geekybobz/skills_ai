#!/usr/bin/env python3
"""On-demand checks and generated inventory for Markdown Protocol collections."""

from __future__ import annotations

import argparse
import re
import sys
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote


ROLES = {"front-door", "map", "index", "topic", "deep", "generated"}
REQUIRED_PROPERTIES = ("role", "summary", "read_when")
CONNECTION_LABELS = ("parent", "prerequisite", "related", "next", "deeper")
LINK_RE = re.compile(r"(?<!!)\[[^]]*\]\(([^)]+)\)")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.MULTILINE)
CONNECTION_LINE_RE = re.compile(r"^-\s+([^:]+):\s*(.*?)\s*$")
NEXT_FOOTER_RE = re.compile(r"\[Next →\]\(([^)]+)\)")
PREVIOUS_FOOTER_RE = re.compile(r"\[← Previous\]\(([^)]+)\)")


@dataclass(frozen=True)
class Finding:
    level: str
    path: str
    message: str


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


def split_frontmatter(text: str) -> tuple[list[str], str]:
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


def without_fenced_code(text: str) -> str:
    lines: list[str] = []
    fence: str | None = None
    for line in text.splitlines():
        marker = line.lstrip()
        if fence:
            if marker.startswith(fence):
                fence = None
            continue
        if marker.startswith("```"):
            fence = "```"
            continue
        if marker.startswith("~~~"):
            fence = "~~~"
            continue
        lines.append(line)
    return "\n".join(lines)


def slugged_headings(text: str) -> set[str]:
    text = without_fenced_code(text)
    seen: dict[str, int] = {}
    anchors: set[str] = set()
    for _, heading in HEADING_RE.findall(text):
        heading = re.sub(r"\[([^]]+)\]\([^)]+\)", r"\1", heading)
        heading = re.sub(r"[`*_~]", "", heading).lower()
        base = re.sub(r"[^\w\- ]", "", heading, flags=re.UNICODE).strip()
        base = re.sub(r"\s+", "-", base)
        count = seen.get(base, 0)
        seen[base] = count + 1
        anchors.add(base if count == 0 else f"{base}-{count}")
    return anchors


def local_links(path: Path, root: Path, text: str) -> list[tuple[str, str | None, Path]]:
    links: list[tuple[str, str | None, Path]] = []
    for raw_target in LINK_RE.findall(without_fenced_code(text)):
        target = raw_target.strip().strip("<>")
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
    target = raw_target.strip().strip("<>")
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
    output_path = (root / output).resolve()
    rows: list[tuple[str, str, str, str]] = []
    errors: list[str] = []
    for path in markdown_files(root):
        if path.resolve() == output_path:
            continue
        data = properties(path.read_text(encoding="utf-8"))
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
        result = ["| path | role | summary | read when |", "|---|---|---|---|"]
        for path, role, summary, read_when in sorted(items):
            result.append(f"| [{path}]({path}) | {role} | {summary} | {read_when} |")
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
) -> list[Finding]:
    findings: list[Finding] = []
    files = markdown_files(root)
    file_set = {path.resolve() for path in files}
    adjacency: dict[Path, set[Path]] = {path.resolve(): set() for path in files}
    typed: dict[Path, dict[str, set[Path]]] = {
        path.resolve(): {label: set() for label in CONNECTION_LABELS} for path in files
    }
    texts: dict[Path, str] = {}

    for path in files:
        relative = path.relative_to(root).as_posix()
        text = path.read_text(encoding="utf-8")
        texts[path.resolve()] = text
        data = properties(text)
        role = str(data.get("role", ""))
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

        compact = compact_line_count(text, role)
        threshold = 60 if role == "front-door" else 30 if role == "topic" else 0
        if threshold and compact > threshold:
            findings.append(
                Finding("warning", relative, f"compact section has {compact} lines; review threshold is {threshold}")
            )

        nonempty = [line for line in text.splitlines() if line.strip()]
        if len(nonempty) < 2 or nonempty[-2] != "---" or "[⌂ Home]" not in nonempty[-1]:
            findings.append(Finding("error", relative, "missing final portable Home footer"))

        anchors = slugged_headings(text)
        for raw, anchor, resolved in local_links(path, root, text):
            if not resolved.exists():
                findings.append(Finding("error", relative, f"broken link: {raw}"))
                continue
            if resolved in file_set:
                adjacency[path.resolve()].add(resolved)
                if anchor:
                    target_text = resolved.read_text(encoding="utf-8")
                    if anchor not in slugged_headings(target_text):
                        findings.append(Finding("error", relative, f"missing anchor: {raw}"))

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
            typed[path.resolve()][connection.label].add(connection.resolved)

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

    entry_path = choose_entry(root, entry)
    if not entry_path:
        findings.append(Finding("error", ".", "no entry found; use README.md, SKILL.md, INDEX.md, or --entry"))
    else:
        reachable = reachable_files(entry_path, adjacency)
        for orphan in sorted(file_set - reachable):
            findings.append(Finding("error", orphan.relative_to(root).as_posix(), "orphan Markdown file"))

    inventory_path = (root / inventory).resolve()
    if inventory_path.is_file():
        try:
            expected = render_inventory(root, inventory, entry)
        except ValueError as exc:
            findings.append(Finding("error", inventory, f"cannot verify inventory: {exc}"))
        else:
            if inventory_path.read_text(encoding="utf-8") != expected:
                findings.append(Finding("error", inventory, "generated inventory is stale"))
    return findings


def render_graph_report(root: Path, *, entry: str | None = None, topic: str | None = None) -> str:
    files = markdown_files(root)
    file_set = {path.resolve() for path in files}
    adjacency: dict[Path, set[Path]] = {path.resolve(): set() for path in files}
    typed: dict[Path, dict[str, set[Path]]] = {
        path.resolve(): {label: set() for label in CONNECTION_LABELS} for path in files
    }
    for path in files:
        text = path.read_text(encoding="utf-8")
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


def print_findings(findings: list[Finding]) -> None:
    if not findings:
        print("PASS: Markdown Protocol check")
        return
    for finding in findings:
        print(f"{finding.level.upper()}: {finding.path}: {finding.message}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    check = subparsers.add_parser("check", help="check one bounded Markdown collection")
    check.add_argument("root", type=Path)
    check.add_argument("--entry")
    check.add_argument("--require-properties", action="store_true")
    check.add_argument("--inventory", default="INVENTORY.md")

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

    args = parser.parse_args(argv)
    root = args.root.resolve()
    if not root.is_dir():
        print(f"ERROR: not a directory: {root}", file=sys.stderr)
        return 2

    if args.command == "check":
        findings = check_collection(
            root,
            entry=args.entry,
            require_properties=args.require_properties,
            inventory=args.inventory,
        )
        print_findings(findings)
        return 1 if any(item.level == "error" for item in findings) else 0

    if args.command == "graph":
        findings = check_collection(root, entry=args.entry)
        errors = [finding for finding in findings if finding.level == "error"]
        if errors:
            print_findings(errors)
            return 1
        try:
            print(render_graph_report(root, entry=args.entry, topic=args.topic), end="")
        except ValueError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 1
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
        if not output.is_file() or output.read_text(encoding="utf-8") != rendered:
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
