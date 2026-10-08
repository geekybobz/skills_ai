#!/usr/bin/env python3
"""Build or verify the portable macOS VS Code profile."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets" / "vscode"
OUTPUT = ASSETS / "markdown-protocol-macos.code-profile"


def rendered_profile() -> str:
    settings = json.loads((ASSETS / "profile-settings.json").read_text(encoding="utf-8"))
    keybindings = json.loads((ASSETS / "keybindings.json").read_text(encoding="utf-8"))
    extension_ids = json.loads((ASSETS / "extensions.json").read_text(encoding="utf-8"))
    extensions = [{"identifier": {"id": extension_id}} for extension_id in extension_ids]
    profile = {
        "name": "Markdown Protocol macOS",
        "settings": json.dumps(settings, separators=(",", ":")),
        "keybindings": json.dumps(keybindings, separators=(",", ":")),
        "extensions": json.dumps(extensions, separators=(",", ":")),
    }
    return json.dumps(profile, indent=2, ensure_ascii=False) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--write", action="store_true")
    action.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    expected = rendered_profile()
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != expected:
            print(f"ERROR: stale or missing profile: {OUTPUT}", file=sys.stderr)
            return 1
        print(f"PASS: VS Code profile is current: {OUTPUT}")
        return 0
    temporary = OUTPUT.with_suffix(OUTPUT.suffix + ".tmp")
    temporary.write_text(expected, encoding="utf-8")
    temporary.replace(OUTPUT)
    print(f"WROTE: {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
