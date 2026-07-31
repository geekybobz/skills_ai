#!/usr/bin/env python3
"""Validate registry sources and confirm the runtime manifest is current."""

from __future__ import annotations

import json

from registry_runtime import DEFAULT_MANIFEST, RegistryRuntimeError, build_manifest


def main() -> int:
    try:
        expected = json.dumps(build_manifest(), indent=2, sort_keys=True) + "\n"
        if not DEFAULT_MANIFEST.exists():
            print("error: runtime/router-manifest.json is missing")
            return 1
        if DEFAULT_MANIFEST.read_text(encoding="utf-8") != expected:
            print("error: runtime/router-manifest.json is stale; run scripts/compile_registry.py")
            return 1
        manifest = json.loads(expected)
        stats = manifest["stats"]
        print(
            "ok: registry sources and runtime manifest "
            f"({stats['families']} families, {stats['routes']} routes, "
            f"{stats['active_routes']} active, {stats['manual_routes']} manual)"
        )
        return 0
    except (OSError, RegistryRuntimeError, ValueError) as exc:
        print(f"error: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
