from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime"))

from ticket_hub import TicketHub, TicketHubError  # noqa: E402


def report(*, ticket_id: str = "FB-20260808-001", references: list[str] | None = None) -> str:
    file_lines = "\n".join(f"- @root/{reference}" for reference in references or [])
    return f"""# {ticket_id}

Skill: theory-reference

## Prompt that caused the issue

Please repair the reference.

## Answer given

The answer changed the wrong command.

## Your correction / direction

First explain the problem, then wait for my direction.

## Relevant project files

{file_lines}
"""


class TicketHubTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.base = Path(self.temporary.name)
        self.hub = TicketHub(self.base / "feedback-tickets")
        self.project = self.base / "project-a"
        (self.project / ".skills-ai").mkdir(parents=True)
        self.source = self.project / ".skills-ai" / "FB-20260808-001.md"

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _register_and_scan(self, *, content: str | None = None) -> str:
        self.source.write_text(content or report(), encoding="utf-8")
        self.hub.register("project-a", self.project)
        scanned = self.hub.scan()
        self.assertEqual([], scanned["errors"])
        self.assertEqual([{"record_id": "project-a--FB-20260808-001", "skill": "theory-reference"}], scanned["new"])
        return "project-a--FB-20260808-001"

    def test_scan_collects_a_report_and_lists_it_by_skill(self) -> None:
        record_id = self._register_and_scan()

        listed = self.hub.list(group_by_skill=True)
        self.assertEqual([record_id], [item["record_id"] for item in listed["groups"]["theory-reference"]])
        central = self.hub.root / record_id
        self.assertEqual(self.source.read_text(encoding="utf-8"), (central / "report.md").read_text(encoding="utf-8"))
        context = json.loads((central / "context.json").read_text(encoding="utf-8"))
        self.assertEqual("pending", context["status"])
        self.assertEqual("project-a", context["project_id"])

    def test_scan_is_read_only_for_the_registered_project(self) -> None:
        source_bytes = report().encode("utf-8")
        self.source.write_bytes(source_bytes)
        self.hub.register("project-a", self.project)

        self.hub.scan()

        self.assertEqual(source_bytes, self.source.read_bytes())
        self.assertEqual([self.source], list((self.project / ".skills-ai").iterdir()))

    def test_resolve_snapshots_only_root_relative_evidence_and_records_direction(self) -> None:
        target = self.project / "sections" / "full_theory.tex"
        target.parent.mkdir()
        target.write_text("\\section{Theory}\n", encoding="utf-8")
        record_id = self._register_and_scan(content=report(references=["sections/full_theory.tex"]))
        before = target.read_bytes()

        opened = self.hub.resolve(record_id, note="Check the notation before editing.")

        self.assertEqual("review", opened["status"])
        self.assertEqual(before, target.read_bytes())
        snapshot = self.hub.root / record_id / "files" / "sections" / "full_theory.tex"
        self.assertEqual(before, snapshot.read_bytes())
        self.assertEqual("Check the notation before editing.", opened["directions"][0]["text"])
        self.assertTrue((self.hub.root / record_id / "analysis.md").is_file())
        self.assertTrue((self.hub.root / record_id / "proposal.md").is_file())

    def test_resolve_rejects_a_reference_that_escapes_the_project_root(self) -> None:
        record_id = self._register_and_scan(content=report(references=["../outside.txt"]))

        with self.assertRaisesRegex(TicketHubError, "escapes its project"):
            self.hub.resolve(record_id)

    def test_close_deletes_only_central_ticket_folder_and_keeps_a_minimal_record(self) -> None:
        record_id = self._register_and_scan()

        closed = self.hub.resolve(record_id, close=True, summary="Corrected after review.")

        self.assertEqual(record_id, closed["deleted_ticket_folder"])
        self.assertFalse((self.hub.root / record_id).exists())
        self.assertTrue(self.source.exists())
        resolved = (self.hub.root / "resolved.jsonl").read_text(encoding="utf-8")
        self.assertIn(record_id, resolved)
        self.assertIn("Corrected after review.", resolved)
        self.assertNotIn("Please repair the reference.", resolved)

    def test_source_ticket_id_must_be_unique_across_registered_projects_when_resolving_short_id(self) -> None:
        record_id = self._register_and_scan()
        project_b = self.base / "project-b"
        (project_b / ".skills-ai").mkdir(parents=True)
        (project_b / ".skills-ai" / "FB-20260808-001.md").write_text(report(), encoding="utf-8")
        self.hub.register("project-b", project_b)
        self.hub.scan()

        with self.assertRaisesRegex(TicketHubError, "ambiguous"):
            self.hub.resolve("FB-20260808-001")
        self.assertEqual("review", self.hub.resolve(record_id)["status"])

    def test_resolve_rejects_a_ticket_when_its_registered_project_root_changes(self) -> None:
        record_id = self._register_and_scan()
        moved_project = self.base / "moved-project"
        moved_project.mkdir()
        self.hub.register("project-a", moved_project)

        with self.assertRaisesRegex(TicketHubError, "root changed"):
            self.hub.resolve(record_id)

    def test_cli_can_register_scan_and_list_without_writing_the_source_project(self) -> None:
        self.source.write_text(report(), encoding="utf-8")
        command = [sys.executable, str(ROOT / "scripts" / "ticket_hub.py"), "--hub-root", str(self.hub.root)]
        source_before = self.source.read_bytes()

        subprocess.run(
            command + ["register", "--id", "project-a", "--project", str(self.project)],
            text=True,
            capture_output=True,
            check=True,
        )
        scanned = subprocess.run(command + ["--json", "scan"], text=True, capture_output=True, check=True)
        listed = subprocess.run(command + ["--json", "list", "--skill", "theory-reference"], text=True, capture_output=True, check=True)

        self.assertEqual(source_before, self.source.read_bytes())
        self.assertEqual("project-a--FB-20260808-001", json.loads(scanned.stdout)["new"][0]["record_id"])
        self.assertEqual("project-a--FB-20260808-001", json.loads(listed.stdout)["tickets"][0]["record_id"])


if __name__ == "__main__":
    unittest.main()
