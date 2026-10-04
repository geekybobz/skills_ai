"""Deterministic, local feedback-ticket collection for the Skills Orchestrator.

Project reports remain read-only sources.  The hub copies selected reports and
root-relative evidence into one ignored local workspace, where a human-led
``resolve`` session can be reviewed before any project edit is considered.
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import tempfile
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from typing import Any


SCHEMA_VERSION = 1
TICKET_FILE_PATTERN = "FB-*.md"
TICKET_ID_PATTERN = re.compile(r"FB-[A-Za-z0-9][A-Za-z0-9-]{0,119}$")
PROJECT_ID_PATTERN = re.compile(r"[a-z0-9][a-z0-9_-]{0,79}$")
REQUIRED_SECTIONS = (
    "prompt that caused the issue",
    "answer given",
    "your correction / direction",
)
ROOT_REFERENCE_PATTERN = re.compile(r"^\s*-\s+@root/(.+?)\s*$")
SKILL_PATTERN = re.compile(
    r"^\s*(?:skill|skill used)\s*:\s*([A-Za-z0-9_-]+)\s*$",
    re.IGNORECASE | re.MULTILINE,
)


class TicketHubError(RuntimeError):
    """Raised for malformed ticket data or unsafe local paths."""


def _utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _normalize_heading(value: str) -> str:
    return " ".join(value.strip().lower().split())


def _sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _validate_project_id(project_id: str) -> str:
    if not PROJECT_ID_PATTERN.fullmatch(project_id):
        raise TicketHubError("project id must use lowercase letters, digits, hyphens, or underscores")
    return project_id


def _validate_ticket_id(ticket_id: str) -> str:
    if not TICKET_ID_PATTERN.fullmatch(ticket_id):
        raise TicketHubError("ticket filename must be FB-<identifier>.md")
    return ticket_id


def _safe_relative_reference(reference: str) -> str:
    value = reference.strip().strip("`")
    if not value or value.startswith("/") or "\\" in value:
        raise TicketHubError(f"invalid @root reference: {reference!r}")
    path = PurePosixPath(value)
    if any(part in {"", ".", ".."} for part in path.parts):
        raise TicketHubError(f"@root reference escapes its project: {reference!r}")
    return path.as_posix()


def _parse_sections(report: str) -> dict[str, str]:
    headings = list(re.finditer(r"(?m)^##\s+(.+?)\s*$", report))
    sections: dict[str, str] = {}
    for index, heading in enumerate(headings):
        start = heading.end()
        end = headings[index + 1].start() if index + 1 < len(headings) else len(report)
        sections[_normalize_heading(heading.group(1))] = report[start:end].strip()
    missing = [name for name in REQUIRED_SECTIONS if not sections.get(name)]
    if missing:
        raise TicketHubError("ticket report is missing required section(s): " + ", ".join(missing))
    return sections


def _extract_skill(report: str) -> str:
    match = SKILL_PATTERN.search(report)
    return match.group(1).lower() if match else "unclassified"


def _extract_root_references(report: str) -> list[str]:
    sections = _parse_sections(report)
    references: list[str] = []
    seen: set[str] = set()
    for line in sections.get("relevant project files", "").splitlines():
        match = ROOT_REFERENCE_PATTERN.match(line)
        if match is None:
            continue
        reference = _safe_relative_reference(match.group(1))
        if reference not in seen:
            seen.add(reference)
            references.append(reference)
    return references


def _atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        dir=path.parent,
        prefix=f".{path.name}.",
        delete=False,
    ) as handle:
        handle.write(text)
        temporary = Path(handle.name)
    temporary.replace(path)


def _atomic_write_json(path: Path, value: Any) -> None:
    _atomic_write_text(path, json.dumps(value, indent=2, sort_keys=True) + "\n")


def _load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    if path.is_symlink() or not path.is_file():
        raise TicketHubError(f"unsafe local state file: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise TicketHubError(f"invalid JSON state: {path}") from exc


class TicketHub:
    """A local, one-project-at-a-time ticket workspace."""

    def __init__(self, root: Path) -> None:
        self.root = Path(root).expanduser().resolve(strict=False)
        self.sources_path = self.root / "sources.local.json"
        self.index_path = self.root / "index.jsonl"
        self.resolved_path = self.root / "resolved.jsonl"

    def _ensure_root(self) -> None:
        if self.root.exists() and self.root.is_symlink():
            raise TicketHubError("ticket-hub root must not be a symlink")
        self.root.mkdir(parents=True, exist_ok=True)

    def _load_sources(self) -> dict[str, Any]:
        self._ensure_root()
        value = _load_json(self.sources_path, {"schema_version": SCHEMA_VERSION, "projects": []})
        if not isinstance(value, dict) or value.get("schema_version") != SCHEMA_VERSION:
            raise TicketHubError("unsupported source registry schema")
        projects = value.get("projects")
        if not isinstance(projects, list):
            raise TicketHubError("source registry projects must be a list")
        for project in projects:
            if not isinstance(project, dict):
                raise TicketHubError("source registry project entries must be objects")
            if not isinstance(project.get("id"), str) or not isinstance(project.get("root"), str):
                raise TicketHubError("source registry project entries require id and root")
            _validate_project_id(project["id"])
        return value

    def register(self, project_id: str, project_root: Path) -> dict[str, str]:
        """Register one exact project root for later read-only scanning."""
        project_id = _validate_project_id(project_id)
        root = Path(project_root).expanduser().resolve(strict=False)
        if not root.is_dir():
            raise TicketHubError(f"project root is not a directory: {root}")
        sources = self._load_sources()
        projects = [item for item in sources["projects"] if item["id"] != project_id]
        projects.append({"id": project_id, "root": str(root), "enabled": True})
        sources["projects"] = sorted(projects, key=lambda item: item["id"])
        _atomic_write_json(self.sources_path, sources)
        return {"project_id": project_id, "root": str(root)}

    @staticmethod
    def _record_id(project_id: str, ticket_id: str) -> str:
        return f"{project_id}--{ticket_id}"

    def _ticket_path(self, record_id: str) -> Path:
        if "/" in record_id or "\\" in record_id or record_id in {"", ".", ".."}:
            raise TicketHubError("unsafe ticket identifier")
        path = self.root / record_id
        if path.parent != self.root:
            raise TicketHubError("ticket path escapes hub root")
        return path

    def _load_context(self, ticket_path: Path) -> dict[str, Any]:
        value = _load_json(ticket_path / "context.json", None)
        if not isinstance(value, dict) or value.get("schema_version") != SCHEMA_VERSION:
            raise TicketHubError(f"invalid ticket context: {ticket_path.name}")
        return value

    def _ticket_records(self) -> list[dict[str, Any]]:
        if not self.root.exists():
            return []
        records: list[dict[str, Any]] = []
        for child in sorted(self.root.iterdir(), key=lambda item: item.name):
            if not child.is_dir() or child.is_symlink():
                continue
            context_path = child / "context.json"
            if not context_path.exists():
                continue
            context = self._load_context(child)
            records.append(
                {
                    "record_id": context["record_id"],
                    "ticket_id": context["ticket_id"],
                    "project_id": context["project_id"],
                    "skill": context["skill"],
                    "status": context["status"],
                    "updated_at": context["updated_at"],
                }
            )
        return records

    def _registered_project_root(self, project_id: str) -> Path:
        for project in self._load_sources()["projects"]:
            if project["id"] == project_id and project.get("enabled") is not False:
                root = Path(project["root"]).expanduser().resolve(strict=False)
                if not root.is_dir():
                    raise TicketHubError("ticket project root is unavailable")
                return root
        raise TicketHubError("ticket project is no longer registered")

    def _write_index(self) -> None:
        rows = self._ticket_records()
        _atomic_write_text(
            self.index_path,
            "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        )

    def scan(self) -> dict[str, Any]:
        """Copy valid new or updated reports from registered projects into the hub."""
        sources = self._load_sources()
        result: dict[str, Any] = {"new": [], "updated": [], "unchanged": [], "errors": []}
        for project in sources["projects"]:
            if project.get("enabled") is False:
                continue
            project_id = project["id"]
            project_root = Path(project["root"]).expanduser().resolve(strict=False)
            if not project_root.is_dir():
                result["errors"].append({"project_id": project_id, "error": "project root is unavailable"})
                continue
            report_root = project_root / ".skills-ai"
            if not report_root.exists():
                continue
            if report_root.is_symlink() or not report_root.is_dir():
                result["errors"].append({"project_id": project_id, "error": ".skills-ai must be a directory, not a symlink"})
                continue
            for report_path in sorted(report_root.glob(TICKET_FILE_PATTERN), key=lambda item: item.name):
                try:
                    if report_path.is_symlink() or not report_path.is_file():
                        raise TicketHubError("ticket report must be a regular file, not a symlink")
                    ticket_id = _validate_ticket_id(report_path.stem)
                    report = report_path.read_text(encoding="utf-8")
                    _parse_sections(report)
                    skill = _extract_skill(report)
                    record_id = self._record_id(project_id, ticket_id)
                    ticket_path = self._ticket_path(record_id)
                    if ticket_path.exists() and ticket_path.is_symlink():
                        raise TicketHubError("central ticket directory must not be a symlink")
                    source_hash = _sha256_path(report_path)
                    state = "new"
                    previous: dict[str, Any] | None = None
                    if ticket_path.exists():
                        previous = self._load_context(ticket_path)
                        if previous.get("source_hash") == source_hash:
                            state = "unchanged"
                    if state != "unchanged":
                        ticket_path.mkdir(parents=True, exist_ok=True)
                        _atomic_write_text(ticket_path / "report.md", report)
                        now = _utc_now()
                        context = {
                            "schema_version": SCHEMA_VERSION,
                            "record_id": record_id,
                            "ticket_id": ticket_id,
                            "project_id": project_id,
                            "project_root": str(project_root),
                            "source_path": ".skills-ai/" + report_path.name,
                            "source_hash": source_hash,
                            "skill": skill,
                            "status": previous.get("status", "pending") if previous else "pending",
                            "created_at": previous.get("created_at", now) if previous else now,
                            "updated_at": now,
                            "directions": previous.get("directions", []) if previous else [],
                        }
                        _atomic_write_json(ticket_path / "context.json", context)
                        if not (ticket_path / "analysis.md").exists():
                            _atomic_write_text(
                                ticket_path / "analysis.md",
                                f"# Analysis — {record_id}\n\nOpen this ticket with `resolve` and wait for the user's direction before writing analysis.\n",
                            )
                        if not (ticket_path / "proposal.md").exists():
                            _atomic_write_text(
                                ticket_path / "proposal.md",
                                f"# Proposal — {record_id}\n\nNo project edit is authorized until the user explicitly directs it during resolve mode.\n",
                            )
                    result[state].append({"record_id": record_id, "skill": skill})
                except (OSError, UnicodeDecodeError, TicketHubError) as exc:
                    result["errors"].append(
                        {"project_id": project_id, "source": report_path.name, "error": str(exc)}
                    )
        self._write_index()
        return result

    def list(self, *, skill: str | None = None, group_by_skill: bool = False) -> dict[str, Any]:
        records = self._ticket_records()
        if skill is not None:
            normalized_skill = skill.lower()
            records = [record for record in records if record["skill"] == normalized_skill]
        if not group_by_skill:
            return {"tickets": records}
        groups: dict[str, list[dict[str, Any]]] = {}
        for record in records:
            groups.setdefault(record["skill"], []).append(record)
        return {"groups": {name: groups[name] for name in sorted(groups)}}

    def _resolve_record_id(self, value: str) -> str:
        direct = self._ticket_path(value)
        if not direct.is_symlink() and direct.is_dir() and (direct / "context.json").is_file():
            return value
        matches = [record["record_id"] for record in self._ticket_records() if record["ticket_id"] == value]
        if len(matches) == 1:
            return matches[0]
        if len(matches) > 1:
            raise TicketHubError("ticket id is ambiguous; use the displayed record_id")
        raise TicketHubError(f"unknown active ticket: {value}")

    @staticmethod
    def _source_file(project_root: Path, reference: str) -> Path:
        relative = _safe_relative_reference(reference)
        candidate = project_root.joinpath(*PurePosixPath(relative).parts)
        cursor = project_root
        for part in PurePosixPath(relative).parts:
            cursor = cursor / part
            if cursor.is_symlink():
                raise TicketHubError(f"@root reference uses a symlink: {reference}")
        try:
            resolved_root = project_root.resolve(strict=True)
            resolved_candidate = candidate.resolve(strict=True)
        except FileNotFoundError as exc:
            raise TicketHubError(f"@root reference is unavailable: {reference}") from exc
        if not resolved_candidate.is_relative_to(resolved_root) or not resolved_candidate.is_file():
            raise TicketHubError(f"@root reference is not a regular project file: {reference}")
        return resolved_candidate

    def _snapshot_evidence(self, ticket_path: Path, context: dict[str, Any], report: str) -> dict[str, Any]:
        project_root = Path(context["project_root"]).expanduser().resolve(strict=False)
        if not project_root.is_dir():
            return {"copied": [], "unavailable": ["project root is unavailable"]}
        references = _extract_root_references(report)
        copied: list[dict[str, str]] = []
        unavailable: list[str] = []
        temporary = Path(tempfile.mkdtemp(prefix=".ticket-files-", dir=ticket_path))
        try:
            for reference in references:
                try:
                    source = self._source_file(project_root, reference)
                    destination = temporary.joinpath(*PurePosixPath(reference).parts)
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(source, destination)
                    copied.append({"reference": "@root/" + reference, "sha256": _sha256_path(destination)})
                except TicketHubError as exc:
                    unavailable.append(str(exc))
            evidence_path = ticket_path / "files"
            if evidence_path.exists():
                if evidence_path.is_symlink() or not evidence_path.is_dir():
                    raise TicketHubError("central evidence path must be a directory, not a symlink")
                shutil.rmtree(evidence_path)
            temporary.replace(evidence_path)
        except Exception:
            shutil.rmtree(temporary, ignore_errors=True)
            raise
        return {"copied": copied, "unavailable": unavailable}

    def resolve(
        self,
        ticket: str,
        *,
        note: str | None = None,
        close: bool = False,
        summary: str | None = None,
    ) -> dict[str, Any]:
        """Open one ticket for review, or explicitly close its central workspace."""
        record_id = self._resolve_record_id(ticket)
        ticket_path = self._ticket_path(record_id)
        if ticket_path.is_symlink() or not ticket_path.is_dir():
            raise TicketHubError("central ticket directory must be a directory, not a symlink")
        context = self._load_context(ticket_path)
        if close:
            if not summary or not summary.strip():
                raise TicketHubError("closing a ticket requires a short --summary after user confirmation")
            resolved = {
                "record_id": context["record_id"],
                "ticket_id": context["ticket_id"],
                "project_id": context["project_id"],
                "skill": context["skill"],
                "resolved_at": _utc_now(),
                "summary": summary.strip()[:1000],
            }
            if self.resolved_path.exists() and (
                self.resolved_path.is_symlink() or not self.resolved_path.is_file()
            ):
                raise TicketHubError("resolved ticket log must be a regular file, not a symlink")
            existing = self.resolved_path.read_text(encoding="utf-8") if self.resolved_path.exists() else ""
            _atomic_write_text(self.resolved_path, existing + json.dumps(resolved, sort_keys=True) + "\n")
            if ticket_path.parent != self.root or ticket_path == self.root:
                raise TicketHubError("refusing to delete outside the exact central ticket directory")
            shutil.rmtree(ticket_path)
            self._write_index()
            return {"closed": resolved, "deleted_ticket_folder": record_id}

        report_path = ticket_path / "report.md"
        if report_path.is_symlink() or not report_path.is_file():
            raise TicketHubError("central ticket report is unavailable")
        report = report_path.read_text(encoding="utf-8")
        _parse_sections(report)
        registered_root = self._registered_project_root(context["project_id"])
        remembered_root = Path(context["project_root"]).expanduser().resolve(strict=False)
        if remembered_root != registered_root:
            raise TicketHubError("ticket project root changed; run scan before resolve")
        if note is not None:
            cleaned_note = note.strip()
            if not cleaned_note:
                raise TicketHubError("resolve note must not be empty")
            if len(cleaned_note) > 4000:
                raise TicketHubError("resolve note exceeds 4000 characters")
            directions = list(context.get("directions", []))
            directions.append({"at": _utc_now(), "text": cleaned_note})
            context["directions"] = directions[-20:]
        evidence = self._snapshot_evidence(ticket_path, context, report)
        context["status"] = "review"
        context["opened_at"] = context.get("opened_at", _utc_now())
        context["updated_at"] = _utc_now()
        context["evidence"] = evidence
        _atomic_write_json(ticket_path / "context.json", context)
        self._write_index()
        return {
            "record_id": record_id,
            "ticket_id": context["ticket_id"],
            "project_id": context["project_id"],
            "project_root": context["project_root"],
            "skill": context["skill"],
            "status": context["status"],
            "report": report,
            "evidence": evidence,
            "directions": context.get("directions", []),
            "analysis_path": str(ticket_path / "analysis.md"),
            "proposal_path": str(ticket_path / "proposal.md"),
            "next": "Review the ticket with the user and wait for explicit direction before editing the project.",
        }
