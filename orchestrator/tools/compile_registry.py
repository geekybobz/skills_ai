#!/usr/bin/env python3
"""Compile the Markdown skill registry into a compact runtime manifest."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path

from registry_runtime import DEFAULT_MANIFEST, RegistryRuntimeError, build_manifest


def serialized_manifest() -> str:
    return json.dumps(build_manifest(), indent=2, sort_keys=True) + "\n"


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent, text=True)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            os.fchmod(handle.fileno(), 0o644)
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--check", action="store_true", help="fail when the compiled manifest is stale")
    parser.add_argument("--stdout", action="store_true", help="print the manifest without writing it")
    args = parser.parse_args()
    try:
        content = serialized_manifest()
        manifest = json.loads(content)
        if args.stdout:
            print(content, end="")
            return 0
        if args.check:
            if not args.output.exists() or args.output.read_text(encoding="utf-8") != content:
                print(f"stale: {args.output}")
                return 1
            print(f"ok: {args.output.relative_to(DEFAULT_MANIFEST.parents[2])}")
            return 0
        atomic_write(args.output, content)
        stats = manifest["stats"]
        print(
            f"compiled: {args.output.relative_to(DEFAULT_MANIFEST.parents[2])} "
            f"({stats['routes']} routes, {stats['active_routes']} active, "
            f"source {manifest['source_hash'][:12]})"
        )
        return 0
    except (OSError, RegistryRuntimeError, ValueError) as exc:
        print(f"error: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
