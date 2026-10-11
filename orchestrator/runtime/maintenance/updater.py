"""Reviewed, foreground synchronization of declared Skills AI surfaces."""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
import re
import secrets
import shutil
import subprocess
import tempfile

from . import adapters, lifecycle
from .common import (AREA, SCHEMA, MAX_BYTES, MaintenanceError, candidate_source,
                     fingerprint, identity, operation_lock, read_state, run_tool,
                     safe_path, source_identity, write_state)


def _git(repo: Path, *args: str, timeout: int = 120) -> subprocess.CompletedProcess:
    result = subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, timeout=timeout,
        env=os.environ | {"GIT_OPTIONAL_LOCKS": "0"},
    )
    if len(result.stdout) > MAX_BYTES or len(result.stderr) > MAX_BYTES:
        raise MaintenanceError("GIT_OUTPUT_TOO_LARGE")
    return result


def _git_text(repo: Path, *args: str, timeout: int = 120) -> str:
    result = _git(repo, *args, timeout=timeout)
    if result.returncode:
        raise MaintenanceError("GIT_UPDATE_INSPECTION_FAILED")
    return result.stdout.decode(errors="replace").strip()


def _executable_identity(path: Path) -> dict:
    path = safe_path(path)
    if not path.is_file() or path.stat().st_size > 128 * 1024 * 1024:
        raise MaintenanceError("INVALID_TOOL_INSTALLER")
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return {"sha256": digest.hexdigest(), "size": path.stat().st_size,
            "mode": path.stat().st_mode & 0o777}


def _manifest(root: Path) -> dict:
    compiled = run_tool(root, "compile_registry.py", ["--check"], parse=False)
    if compiled["returncode"]:
        raise MaintenanceError("STALE_REGISTRY")
    manifest = read_state(root / "orchestrator/runtime/manifest.json")
    if manifest is None:
        raise MaintenanceError("MANIFEST_UNAVAILABLE")
    return manifest


def _submodules(root: Path) -> list[tuple[str, Path]]:
    path = root / ".gitmodules"
    if not path.is_file() or path.is_symlink() or path.stat().st_size > 65536:
        raise MaintenanceError("GITMODULES_UNAVAILABLE")
    result = subprocess.run(
        ["git", "config", "-f", str(path), "--get-regexp", r"^submodule\..*\.path$"],
        capture_output=True, timeout=30,
    )
    if result.returncode not in (0, 1) or len(result.stdout) > 65536:
        raise MaintenanceError("GITMODULES_INVALID")
    records = []
    for line in result.stdout.decode(errors="replace").splitlines():
        match = re.fullmatch(r"submodule\.([^\s]+)\.path\s+([^\s]+)", line)
        if not match:
            raise MaintenanceError("GITMODULES_INVALID")
        relative = Path(match.group(2))
        if relative.is_absolute() or ".." in relative.parts:
            raise MaintenanceError("GITMODULES_INVALID")
        records.append((match.group(1), relative))
    if len(records) > 64 or len({str(path) for _, path in records}) != len(records):
        raise MaintenanceError("GITMODULES_INVALID")
    return sorted(records, key=lambda item: item[0])


def _relation(repo: Path) -> dict:
    fetch = _git(repo, "fetch", "--quiet", "--tags", "origin")
    if fetch.returncode:
        raise MaintenanceError("REMOTE_FETCH_FAILED: " + str(repo))
    head = _git_text(repo, "rev-parse", "HEAD")
    remote = _git_text(repo, "rev-parse", "origin/main")
    counts = _git_text(repo, "rev-list", "--left-right", "--count", "HEAD...origin/main").split()
    if len(counts) != 2 or any(not item.isdigit() for item in counts):
        raise MaintenanceError("GIT_UPDATE_INSPECTION_FAILED")
    ahead, behind = map(int, counts)
    relation = "current" if not ahead and not behind else "behind" if not ahead else "ahead" if not behind else "diverged"
    dirty = bool(_git_text(repo, "status", "--porcelain=v1", "--ignore-submodules=none"))
    return {"head": head, "origin_main": remote, "ahead": ahead, "behind": behind,
            "relation": relation, "clean": not dirty}


def _tree_pin(root: Path, revision: str, relative: Path) -> str:
    value = _git_text(root, "ls-tree", revision, "--", str(relative))
    match = re.fullmatch(r"160000 commit ([0-9a-f]{40})\t.+", value)
    if not match:
        raise MaintenanceError("GITLINK_INSPECTION_FAILED")
    return match.group(1)


def _selected_repository(manifest: dict, package: str | None) -> dict | None:
    if package is None:
        return None
    distributions = manifest.get("distributions", {})
    if package not in distributions:
        raise MaintenanceError("DISTRIBUTION_NOT_DECLARED: " + package)
    return distributions[package]["repository"]


def _path_dirty(root: Path, relative: Path) -> bool:
    result = _git(root, "status", "--porcelain=v1", "--ignore-submodules=none", "--", str(relative))
    if result.returncode:
        raise MaintenanceError("GIT_UPDATE_INSPECTION_FAILED")
    return bool(result.stdout.strip())


def _source_plan(root: Path, *, package: str | None = None,
                 manifest: dict | None = None) -> dict:
    parent = _relation(root)
    repository = _selected_repository(manifest or _manifest(root), package)
    selected_path = (Path(repository["path"])
                     if repository and repository["kind"] == "submodule" else None)
    children = []
    for name, relative in _submodules(root):
        if selected_path is not None and relative != selected_path:
            continue
        repo = root / relative
        probe = _git(repo, "rev-parse", "--is-inside-work-tree") if repo.is_dir() else None
        if probe is None or probe.returncode or probe.stdout.strip() != b"true":
            children.append({"name": name, "path": str(relative), "status": "unavailable"})
            continue
        facts = _relation(repo)
        pin = _tree_pin(root, "HEAD", relative)
        target_pin = _tree_pin(root, "origin/main", relative)
        children.append({"name": name, "path": str(relative), "status": "available",
                         "parent_pin": pin, "target_parent_pin": target_pin, **facts})
    blocked = []
    actions = []
    # A package-scoped global refresh may safely preserve unrelated parent work
    # when the published parent revision and selected child pin are current.
    selected_dirty = selected_path is not None and _path_dirty(root, selected_path)
    if not parent["clean"] and (package is None or repository["kind"] == "parent"):
        blocked.append("PARENT_DIRTY")
    elif selected_dirty:
        blocked.append("SELECTED_PACKAGE_POINTER_DIRTY: " + str(selected_path))
    if parent["relation"] == "behind":
        if parent["clean"]:
            actions.append({"kind": "parent-fast-forward", "from": parent["head"],
                            "to": parent["origin_main"]})
        else:
            blocked.append("PARENT_DIRTY_AND_BEHIND")
    elif parent["relation"] != "current":
        blocked.append("PARENT_" + parent["relation"].upper())
    for child in children:
        if child["status"] == "unavailable":
            actions.append({"kind": "initialize-submodule", "path": child["path"]})
            continue
        if not child["clean"]:
            blocked.append("DIRTY_CHILD: " + child["path"])
            continue
        desired = child["target_parent_pin"] if parent["relation"] == "behind" else child["parent_pin"]
        if child["origin_main"] != desired:
            blocked.append("CHILD_NOT_INTEGRATED: " + child["path"])
            continue
        if child["head"] != desired:
            actions.append({"kind": "restore-parent-pin", "path": child["path"],
                            "from": child["head"], "to": desired})
    return {"parent": parent, "children": children, "actions": actions, "blocked": blocked,
            "package": package, "preserved_parent_changes": bool(package and not parent["clean"]
                                                                  and not selected_dirty)}


def _command_plans(root: Path, manifest: dict, lifecycle_result: dict,
                   package: str | None = None) -> list[dict]:
    by_owner = {item["package"]: item for item in lifecycle_result["items"]}
    plans = []
    seen_distributions = set()
    owners = [package] if package else sorted(manifest["distributions"])
    for owner in owners:
        contract = manifest["distributions"][owner]
        actual = {item["name"]: item for item in by_owner[owner]["commands"]}
        for command in contract["commands"]:
            observed = actual[command["name"]]
            if observed["status"] == "current":
                continue
            if command["kind"] == "python-distribution":
                distribution = command["distribution"]
                if distribution in seen_distributions:
                    continue
                seen_distributions.add(distribution)
                repository = contract["repository"]
                installer_name = shutil.which("uv")
                if repository["kind"] != "submodule" or installer_name is None:
                    raise MaintenanceError("PYTHON_TOOL_UPDATE_UNAVAILABLE: " + distribution)
                installer = safe_path(Path(installer_name).resolve())
                source = safe_path(root / repository["path"])
                if _git_text(source, "status", "--porcelain=v1"):
                    raise MaintenanceError("DIRTY_TOOL_SOURCE: " + str(source))
                plans.append({"kind": "python-tool", "owner": owner,
                              "distribution": distribution, "source": str(source),
                              "source_revision": _git_text(source, "rev-parse", "HEAD"),
                              "installer": str(installer),
                              "installer_before": _executable_identity(installer),
                              "expected_version": contract.get("expected_version"),
                              "commands": sorted(c["name"] for c in contract["commands"]
                                                 if c["kind"] == "python-distribution" and c["distribution"] == distribution)})
            elif command["kind"] == "source-launcher":
                path = Path(observed["path"]) if observed.get("path") else Path.home() / ".local/bin" / command["name"]
                safe_path(path)
                plans.append({"kind": "source-launcher", "owner": owner,
                              "name": command["name"], "path": str(path),
                              "before": fingerprint(path), "target": command["target"]})
    return plans


def _verification(root: Path) -> dict:
    result = run_tool(root, "verify_all.py", ["--json"], timeout=600)
    if result["tool_returncode"] or result.get("failed"):
        raise MaintenanceError("FULL_VERIFICATION_FAILED")
    return {"passed": result.get("passed"), "failed": result.get("failed")}


def _distribution_blocks(manifest: dict, current: dict, commands: list[dict],
                         installations: list[dict]) -> list[str]:
    owners = {item["owner"] for item in commands}
    requested_hosts = {item["binding"]["host"] for item in installations}
    for owner, contract in manifest["distributions"].items():
        if requested_hosts.intersection(contract["host_adapters"]):
            owners.add(owner)
    by_owner = {item["package"]: item for item in current["items"]}
    blocked = []
    for owner in sorted(owners):
        axes = by_owner[owner]["axes"]
        pending = [name for name in ("source", "child", "parent", "release")
                   if axes[name] not in ("current", "not-applicable")]
        if pending:
            blocked.append("DISTRIBUTION_NOT_READY: " + owner + " (" + ",".join(pending) + ")")
    return blocked


def preview(root: Path, *, package: str | None = None,
            approval_ref: str | None = None) -> dict:
    if candidate_source(root):
        raise MaintenanceError("CANDIDATE_CANNOT_UPDATE_GLOBALS")
    with operation_lock(root):
        manifest = _manifest(root)
        _selected_repository(manifest, package)
        sources = _source_plan(root, package=package, manifest=manifest)
        verification = _verification(root)
        current = lifecycle.inspect(root, manifest, adapters, package, check_remotes=True)
        command_plans = [] if sources["actions"] or sources["blocked"] else _command_plans(
            root, manifest, current, package)
        selected_hosts = (set(manifest["distributions"][package]["host_adapters"])
                          if package else None)
        host_plans = [] if sources["actions"] or sources["blocked"] else [adapters.preview(root, binding)
                     for binding in adapters.bindings(root)
                     if selected_hosts is None or binding["host"] in selected_hosts
                     if adapters.check(root, binding)["status"] != "current"]
        blocked = list(sources["blocked"])
        blocked += _distribution_blocks(manifest, current, command_plans, host_plans)
        sources["blocked"] = blocked
        plan = {"schema": SCHEMA, "kind": "global-update", "root": str(root),
                "package": package,
                "approval_ref": approval_ref, "source_identity": source_identity(root),
                "sources": sources, "verification": verification,
                "commands": command_plans, "installations": host_plans,
                "ready": not blocked}
        preview_id = identity(plan)
        write_state(root / AREA / "previews" / (preview_id + ".json"), plan)
        if blocked:
            status = "blocked"
        elif not sources["actions"] and not command_plans and not host_plans:
            status = "unchanged"
        else:
            status = "awaiting-approval"
        approval_command = "skills_ai update" + ((" " + package) if package else "")
        exact_approval_command = (approval_command + " --approve " + preview_id +
                                  " --approval-ref approved")
        return {"status": status, "preview_id": preview_id, "kind": "global-update",
                "package": package,
                "sources": sources, "verification": verification,
                "commands": command_plans, "installations": host_plans,
                "approval_command": approval_command if status == "awaiting-approval" else None,
                "approval_reply": (("approve " + package + " update")
                                   if status == "awaiting-approval" and package else
                                   "approve Skills AI update" if status == "awaiting-approval" else None),
                "exact_approval_command": exact_approval_command if status == "awaiting-approval" else None,
                "authority": "none",
                "next": ("Resolve the reported source block and rerun update." if blocked else
                         "Everything declared is already current." if status == "unchanged" else
                         "Review this exact update and approve its preview ID.")}


def _install_python_tool(plan: dict) -> dict:
    source = safe_path(Path(plan["source"]))
    installer = safe_path(Path(plan["installer"]))
    if _git_text(source, "rev-parse", "HEAD") != plan["source_revision"] or _git_text(source, "status", "--porcelain=v1"):
        raise MaintenanceError("TOOL_SOURCE_CHANGED_AFTER_REVIEW")
    if _executable_identity(installer) != plan["installer_before"]:
        raise MaintenanceError("TOOL_INSTALLER_CHANGED_AFTER_REVIEW")
    result = subprocess.run([str(installer), "tool", "install", "--force", str(source)],
                            capture_output=True, timeout=300)
    if len(result.stdout) > MAX_BYTES or len(result.stderr) > MAX_BYTES or result.returncode:
        raise MaintenanceError("PYTHON_TOOL_INSTALL_FAILED: " + plan["distribution"])
    return {"kind": "python-tool", "distribution": plan["distribution"],
            "expected_version": plan["expected_version"], "status": "updated"}


def _install_launcher(root: Path, plan: dict, backup: Path) -> dict:
    path = safe_path(Path(plan["path"]))
    if fingerprint(path) != plan["before"]:
        raise MaintenanceError("LAUNCHER_CHANGED_AFTER_REVIEW")
    backup.mkdir(parents=True, exist_ok=False, mode=0o700)
    if path.exists():
        (backup / "launcher").write_bytes(path.read_bytes())
        (backup / "launcher").chmod(0o600)
    target = str((root / plan["target"]).resolve())
    raw = ("#!/bin/sh\n# Managed Skills AI terminal launcher.\nexec \"" + target + "\" \"$@\"\n").encode()
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(prefix="." + path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            os.fchmod(handle.fileno(), 0o755)
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, path)
    finally:
        if os.path.exists(temporary_name):
            os.unlink(temporary_name)
    return {"kind": "source-launcher", "name": plan["name"], "status": "updated",
            "backup": str(backup)}


def _verify_effects(root: Path, manifest: dict, plan: dict) -> dict:
    current = lifecycle.inspect(root, manifest, adapters)
    by_owner = {item["package"]: item for item in current["items"]}
    command_results = []
    for requested in plan["commands"]:
        actual = {item["name"]: item for item in by_owner[requested["owner"]]["commands"]}
        names = requested.get("commands", [requested.get("name")])
        for name in names:
            observed = actual.get(name)
            if observed is None or observed["status"] != "current":
                raise MaintenanceError("GLOBAL_COMMAND_VERIFICATION_FAILED: " + str(name))
            command_results.append({"name": name, "status": "current"})
    host_results = []
    for requested in plan["installations"]:
        observed = adapters.check(root, requested["binding"])
        if observed["status"] != "current":
            raise MaintenanceError("HOST_VERIFICATION_FAILED: " + requested["binding"]["host"])
        host_results.append({"host": requested["binding"]["host"], "status": "current"})
    return {"commands": command_results, "hosts": host_results}


def apply(root: Path, preview_id: str, approval_ref: str | None,
          *, package: str | None = None) -> dict:
    if not re.fullmatch(r"[a-f0-9]{64}", preview_id or "") or not approval_ref or len(approval_ref) > 256:
        raise MaintenanceError("EXACT_PREVIEW_AND_ACTUAL_APPROVAL_REQUIRED")
    with operation_lock(root):
        plan = read_state(root / AREA / "previews" / (preview_id + ".json"))
        old_fields = {"schema", "kind", "root", "approval_ref", "source_identity", "sources",
                      "verification", "commands", "installations", "ready"}
        fields = old_fields | {"package"}
        if (plan is None or set(plan) not in (old_fields, fields) or plan["schema"] != SCHEMA
                or plan["kind"] != "global-update" or plan["root"] != str(root)
                or identity(plan) != preview_id or plan["ready"] is not True):
            raise MaintenanceError("INVALID_OR_UNREADY_PREVIEW")
        reviewed_package = plan.get("package")
        if package is not None and package != reviewed_package:
            raise MaintenanceError("APPROVAL_CANNOT_CHANGE_REVIEWED_TARGETS")
        if source_identity(root) != plan["source_identity"]:
            raise MaintenanceError("SOURCE_CHANGED_AFTER_REVIEW")
        operation_id = secrets.token_hex(16)
        receipt_path = root / AREA / "receipts" / (operation_id + ".json")
        receipt = {"schema": SCHEMA, "operation_id": operation_id, "preview_id": preview_id,
                   "kind": "global-update", "status": "running", "source": [], "commands": [],
                   "hosts": [], "phase": "source", "authority": "none"}
        write_state(receipt_path, receipt)
        try:
            actions = plan["sources"]["actions"]
            if actions:
                current = _source_plan(root, package=reviewed_package,
                                       manifest=_manifest(root))
                if current != plan["sources"]:
                    raise MaintenanceError("SOURCE_UPDATE_CHANGED_AFTER_REVIEW")
                if any(item["kind"] == "parent-fast-forward" for item in actions):
                    action = next(item for item in actions if item["kind"] == "parent-fast-forward")
                    result = _git(root, "merge", "--ff-only", "origin/main")
                    if result.returncode:
                        raise MaintenanceError("PARENT_FAST_FORWARD_FAILED")
                    receipt["source"].append(action | {"status": "updated"})
                result = _git(root, "submodule", "update", "--init", "--recursive")
                if result.returncode:
                    raise MaintenanceError("SUBMODULE_UPDATE_FAILED")
                receipt["source"].append({"kind": "submodules", "status": "updated",
                                          "actions": [item for item in actions
                                                      if item["kind"] != "parent-fast-forward"]})
                receipt["phase"] = "verify-source"
                write_state(receipt_path, receipt)
                receipt["verification"] = _verification(root)
                receipt["status"] = "complete"
                receipt["phase"] = "complete"
                receipt["next"] = "Source updated and verified; rerun skills_ai update to review global installations from the new source."
            else:
                receipt["phase"] = "commands"
                write_state(receipt_path, receipt)
                for index, command in enumerate(plan["commands"]):
                    if command["kind"] == "python-tool":
                        receipt["commands"].append(_install_python_tool(command))
                    else:
                        receipt["commands"].append(_install_launcher(
                            root, command, root / AREA / "backups" / operation_id / ("command-" + str(index))))
                    write_state(receipt_path, receipt)
                receipt["phase"] = "hosts"
                for installation in plan["installations"]:
                    backup = root / AREA / "backups" / operation_id / installation["binding"]["host"]
                    receipt["hosts"].append(adapters.refresh(root, installation, backup))
                    write_state(receipt_path, receipt)
                receipt["effects"] = _verify_effects(root, _manifest(root), plan)
                receipt["verification"] = _verification(root)
                receipt["status"] = "complete"
                receipt["phase"] = "complete"
                receipt["next"] = "Declared global surfaces updated and verified; host context remains host-owned."
        except Exception as exc:
            receipt["status"] = "partial" if receipt["source"] or receipt["commands"] or receipt["hosts"] else "failed"
            receipt["error"] = str(exc) if isinstance(exc, MaintenanceError) else type(exc).__name__
            receipt["next"] = "Inspect the receipt and actual effects before retrying."
        write_state(receipt_path, receipt)
        next_command = None if receipt["status"] != "complete" else (
            "skills_ai lifecycle " + reviewed_package if reviewed_package else "skills_ai status")
        return receipt | {"receipt": str(receipt_path), "package": reviewed_package,
                          "next_command": next_command}
