"""Read-only publication, release and installation facts for declared distributions."""
from __future__ import annotations

from email.parser import BytesParser
import os
from pathlib import Path
import re
import shutil
import subprocess

from .common import MAX_BYTES, MaintenanceError

PROBLEM = {"pending", "stale", "absent", "not-configured"}
SEMVER = re.compile(r"[0-9]+\.[0-9]+\.[0-9]+(?:[-+][A-Za-z0-9.-]+)?")


def _git(repo: Path, *args: str, timeout: int = 30) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        timeout=timeout,
        env=os.environ | {"GIT_OPTIONAL_LOCKS": "0"},
    )


def _text(result: subprocess.CompletedProcess) -> str:
    if len(result.stdout) > MAX_BYTES or len(result.stderr) > MAX_BYTES:
        raise MaintenanceError("GIT_OUTPUT_TOO_LARGE")
    return result.stdout.decode(errors="replace").strip()


def _refresh(repo: Path) -> str | None:
    result = _git(repo, "fetch", "--quiet", "origin", timeout=60)
    return None if result.returncode == 0 else "REMOTE_CHECK_FAILED"


def _repository(repo: Path, *, check_remotes: bool) -> dict:
    error = _refresh(repo) if check_remotes else None
    head_result = _git(repo, "rev-parse", "HEAD")
    status_result = _git(repo, "status", "--porcelain=v1", "--ignore-submodules=none")
    if head_result.returncode or status_result.returncode:
        raise MaintenanceError("GIT_INSPECTION_FAILED")
    head = _text(head_result)
    remote_result = _git(repo, "rev-parse", "--verify", "origin/main")
    remote = _text(remote_result) if remote_result.returncode == 0 else None
    published = None
    if remote and error is None:
        published = _git(repo, "merge-base", "--is-ancestor", head, "origin/main").returncode == 0
    remote_tags = None
    if check_remotes and error is None:
        remote_tag_result = _git(repo, "ls-remote", "--tags", "--refs", "origin", timeout=60)
        if remote_tag_result.returncode:
            error = "REMOTE_TAG_CHECK_FAILED"
            published = None
        else:
            remote_tags = sorted(
                match.group(1)
                for line in _text(remote_tag_result).splitlines()
                if (match := re.fullmatch(r"[0-9a-f]{40}\trefs/tags/(.+)", line))
            )
    tags_result = _git(repo, "tag", "--points-at", "HEAD")
    if tags_result.returncode:
        raise MaintenanceError("GIT_INSPECTION_FAILED")
    return {
        "revision": head,
        "clean": not bool(_text(status_result)),
        "remote_revision": remote,
        "published": published,
        "remote_evidence": "fresh-remote-check" if check_remotes and error is None else "local-tracking-ref",
        "remote_error": error,
        "remote_tags": remote_tags,
        "tags": sorted(line for line in _text(tags_result).splitlines() if line),
    }


def _gitlink(root: Path, relative: str) -> str | None:
    result = _git(root, "ls-tree", "HEAD", "--", relative)
    if result.returncode:
        raise MaintenanceError("GITLINK_INSPECTION_FAILED")
    match = re.fullmatch(r"160000 commit ([0-9a-f]{40})\t.+", _text(result))
    return match.group(1) if match else None


def _normalized_distribution(value: str) -> str:
    return re.sub(r"[-_.]+", "-", value).lower()


def _version_file(path: Path) -> str | None:
    if not path.is_file() or path.is_symlink() or path.stat().st_size > 65536:
        return None
    value = path.read_text(encoding="utf-8", errors="strict").strip()
    return value if SEMVER.fullmatch(value) else None


def _pyproject_version(path: Path) -> str | None:
    if not path.is_file() or path.is_symlink() or path.stat().st_size > 65536:
        return None
    section = ""
    for line in path.read_text(encoding="utf-8", errors="strict").splitlines():
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            section = stripped
            continue
        if section == "[project]":
            match = re.fullmatch(r'version\s*=\s*["\']([^"\']+)["\']', stripped)
            if match and SEMVER.fullmatch(match.group(1)):
                return match.group(1)
    return None


def package_versions(root: Path, manifest: dict) -> dict:
    """Return bounded package version facts without loading package instructions."""
    packages = manifest.get("packages")
    if not isinstance(packages, dict) or len(packages) > 64:
        raise MaintenanceError("PACKAGE_METADATA_UNAVAILABLE")
    records = []
    for package, metadata in sorted(packages.items()):
        entry = metadata.get("path") if isinstance(metadata, dict) else None
        if not isinstance(entry, str):
            raise MaintenanceError("PACKAGE_METADATA_UNAVAILABLE")
        relative = Path(entry).parent
        if relative.is_absolute() or ".." in relative.parts:
            raise MaintenanceError("PACKAGE_PATH_INVALID")
        package_root = root / relative
        available = package_root.is_dir() and not package_root.is_symlink()
        sources = []
        if available:
            for candidate, reader in ((package_root / "pyproject.toml", _pyproject_version),
                                      (package_root / "VERSION", _version_file)):
                version = reader(candidate)
                if version is not None:
                    sources.append({"path": str(candidate.relative_to(root)), "version": version})
        versions = sorted({item["version"] for item in sources})
        if not available:
            status, version = "unavailable", None
        elif len(versions) > 1:
            status, version = "ambiguous", None
        elif versions:
            status, version = "versioned", versions[0]
        else:
            status, version = "unversioned", None
        records.append({"package": package, "state": metadata.get("state"),
                        "status": status, "version": version, "sources": sources})
    counts = {state: sum(item["state"] == state for item in records)
              for state in ("active", "manual", "off", "hidden", "deprecated")}
    return {"total": len(records), "counts": counts, "items": records}


def _python_distribution_version(executable: Path, distribution: str) -> str | None:
    resolved = executable.resolve()
    if not resolved.is_file():
        return None
    environment = resolved.parent.parent
    library = environment / "lib"
    if not library.is_dir():
        return None
    candidates = sorted(library.glob("python*/site-packages/*.dist-info/METADATA"))
    if len(candidates) > 512:
        raise MaintenanceError("INSTALLATION_METADATA_TOO_LARGE")
    wanted = _normalized_distribution(distribution)
    for metadata in candidates:
        if not metadata.is_file() or metadata.stat().st_size > 1024 * 1024:
            continue
        message = BytesParser().parsebytes(metadata.read_bytes(), headersonly=True)
        if _normalized_distribution(message.get("Name", "")) == wanted:
            version = message.get("Version")
            return version.strip() if isinstance(version, str) else None
    return None


def _command(root: Path, command: dict, expected_version: str | None) -> dict:
    name = command["name"]
    found = shutil.which(name)
    if found is None:
        return {"name": name, "status": "absent", "required": command["required"], "path": None}
    path = Path(found)
    if command["kind"] == "python-distribution":
        installed = _python_distribution_version(path, command["distribution"])
        status = "current" if installed == expected_version else "stale"
        return {"name": name, "status": status, "required": command["required"],
                "path": str(path), "installed_version": installed, "expected_version": expected_version}
    if not path.is_file() or path.stat().st_size > 8192:
        return {"name": name, "status": "stale", "required": command["required"], "path": str(path)}
    expected = str((root / command["target"]).resolve())
    text = path.read_text(encoding="utf-8", errors="replace")
    current = "# Managed Skills AI terminal launcher." in text and f'exec "{expected}" "$@"' in text
    return {"name": name, "status": "current" if current else "stale",
            "required": command["required"], "path": str(path), "expected_target": expected}


def _axis(items: list[dict]) -> str:
    if not items:
        return "not-applicable"
    statuses = {item["status"] for item in items if item.get("required", True)}
    if statuses & PROBLEM:
        return "pending"
    if "unknown" in statuses:
        return "unknown"
    return "current"


def _release(repository: dict, contract: dict, version: str | None) -> dict:
    if contract["kind"] == "semver-tag":
        expected = "v" + str(version)
        local = expected in repository["tags"]
        status = ("pending" if not local else "unknown" if repository.get("remote_tags") is None
                  else "current" if expected in repository["remote_tags"] else "pending")
        return {"status": status, "expected": expected,
                "tags": repository["tags"], "required": contract["required"]}
    matches = [tag for tag in repository["tags"] if re.fullmatch(r"release/[0-9]{4}\.[0-9]{2}\.[0-9]{2}(?:\.[0-9]+)?", tag)]
    remote = repository.get("remote_tags")
    status = ("pending" if not matches else "unknown" if remote is None
              else "current" if any(tag in remote for tag in matches) else "pending")
    return {"status": status, "expected": "release/YYYY.MM.DD[.n]",
            "tags": matches, "required": contract["required"]}


def inspect_one(root: Path, owner: str, contract: dict, adapter_api, *, check_remotes: bool,
                repository_cache: dict[Path, dict] | None = None) -> dict:
    cache = {} if repository_cache is None else repository_cache
    def facts(path: Path) -> dict:
        key = path.resolve()
        if key not in cache:
            cache[key] = _repository(path, check_remotes=check_remotes)
        return cache[key]
    repository_contract = contract["repository"]
    source_root = root if repository_contract["kind"] == "parent" else root / repository_contract["path"]
    source = facts(source_root)
    parent = source if repository_contract["kind"] == "parent" else facts(root)
    if repository_contract["kind"] == "submodule":
        pin = _gitlink(root, repository_contract["path"])
        child_status = "current" if source["published"] is True else "pending" if source["published"] is False else "unknown"
        if pin != source["revision"]:
            parent_status = "pending"
        else:
            parent_status = ("current" if parent["published"] is True else
                             "pending" if parent["published"] is False else "unknown")
    else:
        pin = None
        child_status = "not-applicable"
        parent_status = "current" if parent["published"] is True else "pending" if parent["published"] is False else "unknown"
    release = _release(source, contract["release"], contract.get("expected_version"))
    commands = [_command(root, command, contract.get("expected_version")) for command in contract["commands"]]
    saved = {binding["host"]: binding for binding in adapter_api.bindings(root)}
    hosts = []
    for host in contract["host_adapters"]:
        binding = saved.get(host)
        if binding is None:
            hosts.append({"host": host, "status": "not-configured", "required": True})
        else:
            checked = adapter_api.check(root, binding)
            hosts.append({"host": host, "status": checked["status"], "required": True,
                          "config_dir": binding["config_dir"], "detail": checked["detail"]})
    axes = {
        "source": "current" if source["clean"] else "pending",
        "child": child_status,
        "parent": parent_status,
        "release": release["status"] if release["required"] else "not-applicable",
        "cli": _axis(commands),
        "hosts": _axis(hosts),
    }
    values = set(axes.values())
    status = "partial" if values & PROBLEM else "unknown" if "unknown" in values else "current"
    next_steps = []
    if source.get("remote_error") or parent.get("remote_error"):
        next_steps.append("The explicit remote check failed; inspect connectivity and retry before claiming publication.")
    if not source["clean"]:
        next_steps.append("Review and explicitly authorize a coherent source commit when ready.")
    if child_status == "pending":
        next_steps.append("Publish the child commit before moving or publishing the parent pointer.")
    elif child_status == "unknown":
        next_steps.append("Run an explicit remote check before claiming the child is published.")
    if parent_status == "pending":
        next_steps.append("Integrate and publish the parent only after the child is published.")
    elif parent_status == "unknown":
        next_steps.append("Run an explicit remote check before claiming the parent is published.")
    if release["status"] == "pending" and release["required"]:
        next_steps.append("Review the required release tag; tagging and pushing need explicit instruction.")
    elif release["status"] == "unknown" and release["required"]:
        next_steps.append("Run an explicit remote check before claiming the release tag is published.")
    for command in commands:
        if command["status"] in {"absent", "stale"} and command["required"]:
            next_steps.append(f"Review the global {command['name']} installation before refreshing it.")
    for host in hosts:
        if host["status"] in {"stale", "not-configured"}:
            next_steps.append(f"Review the {host['host']} adapter refresh before applying it.")
    return {
        "package": owner,
        "status": status,
        "globally_current": status == "current",
        "axes": axes,
        "source": source,
        "child_pin": pin,
        "parent": parent,
        "release": release,
        "commands": commands,
        "hosts": hosts,
        "next": next_steps or ["No pending declared lifecycle step."],
        "limits": "Publication uses origin/main tracking refs unless --check-remotes was explicitly requested; installation freshness does not certify native model behavior.",
    }


def inspect(root: Path, manifest: dict, adapter_api, package: str | None = None, *, check_remotes: bool = False) -> dict:
    distributions = manifest.get("distributions")
    if not isinstance(distributions, dict):
        raise MaintenanceError("DISTRIBUTION_CONTRACT_UNAVAILABLE")
    if package is not None and package not in distributions:
        raise MaintenanceError("DISTRIBUTION_NOT_DECLARED: " + package)
    selected = [package] if package else sorted(distributions)
    repository_cache: dict[Path, dict] = {}
    items = [inspect_one(root, owner, distributions[owner], adapter_api, check_remotes=check_remotes,
                         repository_cache=repository_cache)
             for owner in selected]
    statuses = {item["status"] for item in items}
    status = "partial" if "partial" in statuses else "unknown" if "unknown" in statuses else "current"
    return {"schema": "skills-ai/lifecycle/1", "status": status, "items": items,
            "remote_check": "explicit" if check_remotes else "local-only", "authority": "none"}
