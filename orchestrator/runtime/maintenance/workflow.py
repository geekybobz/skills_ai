"""Compact package work and finish reports over the contained repair workflow."""
from pathlib import Path
import shlex

from . import checks, operations, updater, workspace
from .common import MaintenanceError


def _package(root: Path, name: str) -> tuple[dict, Path, bool]:
    manifest = updater._manifest(root)
    packages = manifest.get("packages", {})
    if name not in packages:
        raise MaintenanceError("UNKNOWN_PUBLIC_SKILL: " + name)
    entry = packages[name]
    relative = Path(entry["path"]).parent
    if relative.is_absolute() or ".." in relative.parts:
        raise MaintenanceError("INVALID_PACKAGE_PATH: " + name)
    return entry, relative, name in manifest.get("distributions", {})


def _report(package: str, outcome: str, detail: str, *, checks_status: str | None = None,
            changed_paths: list[str] | None = None, next_command: str | None = None) -> dict:
    return {
        "package": package,
        "outcome": outcome,
        "detail": detail,
        "checks": checks_status,
        "changed_paths": changed_paths or [],
        "next_command": next_command,
    }


def work(root: Path, session: str | None, package: str) -> dict:
    _, relative, _ = _package(root, package)
    state = workspace.repair(root, session, True)
    working_root = Path(state["working_root"])
    package_root = working_root / relative
    command = "cd " + shlex.quote(str(package_root))
    return state | {
        "status": "ready",
        "kind": "package-work",
        "package": package,
        "package_root": str(package_root),
        "report": _report(
            package,
            "Work area ready",
            "Contained edits stay separate from the live repository until finish is approved.",
            next_command=command,
        ),
    }


def finish_preview(root: Path, session: str | None, package: str,
                   approval_ref: str | None = None) -> dict:
    _, relative, distributed = _package(root, package)
    checked = checks.check(root, session, [str(relative)], False, approval_ref)
    if checked.get("status") != "PASS":
        return {
            "status": "blocked",
            "kind": "package-finish",
            "package": package,
            "checks": checked,
            "report": _report(
                package,
                "Finish blocked",
                "The package checks must pass before an apply review can be approved.",
                checks_status=checked.get("status"),
                next_command="skills_ai check --path " + shlex.quote(str(relative)),
            ),
        }
    reviewed = operations.make_preview(
        root, session, "repair-apply", [], approval_ref or "terminal-request"
    )
    repair = reviewed.get("repair") or {}
    paths = list(repair.get("paths") or [])
    if reviewed["status"] == "awaiting-approval":
        command = "skills_ai finish " + shlex.quote(package)
        exact_command = (command + " --approve " + reviewed["preview_id"] +
                         " --approval-ref approved")
        outcome = "Ready for approval"
        detail = (str(len(paths)) + " changed path" + ("" if len(paths) == 1 else "s") +
                  " passed the required checks.")
    elif reviewed["status"] == "unchanged":
        command = "skills_ai update " + shlex.quote(package) if distributed else "skills_ai status"
        exact_command = None
        outcome = "No contained changes"
        detail = "The work area has nothing new to apply."
    else:
        command = None
        exact_command = None
        outcome = "Finish blocked"
        detail = reviewed.get("next", "Inspect the reported finish condition.")
    return reviewed | {
        "kind": "package-finish",
        "package": package,
        "checks": checked,
        "approval_command": command if reviewed["status"] == "awaiting-approval" else None,
        "approval_reply": ("approve " + package + " finish"
                           if reviewed["status"] == "awaiting-approval" else None),
        "exact_approval_command": exact_command,
        "report": _report(package, outcome, detail, checks_status="PASS",
                          changed_paths=paths, next_command=command),
    }


def finish_apply(root: Path, package: str, preview_id: str,
                 approval_ref: str | None) -> dict:
    _, _, distributed = _package(root, package)
    result = operations.apply_preview(
        root, preview_id, approval_ref, expected_kind="repair-apply"
    )
    next_command = ("skills_ai update " + shlex.quote(package)
                    if result.get("status") == "complete" and distributed else
                    "skills_ai status" if result.get("status") == "complete" else None)
    outcome = "Work applied" if result.get("status") == "complete" else "Apply incomplete"
    detail = ("The reviewed contained changes were applied to the live source."
              if result.get("status") == "complete" else result.get("next", "Inspect the receipt."))
    return result | {
        "kind": "package-finish",
        "package": package,
        "next_command": next_command,
        "report": _report(package, outcome, detail, next_command=next_command),
    }
