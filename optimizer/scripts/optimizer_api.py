#!/usr/bin/env python3
"""Return a compact, read-only discovery payload for the live Optimizer route."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


RESOLVER = Path("/Users/billabobz/OPTIMIZER/registry/optimizer_registry.py")


def resolve(route: str) -> dict[str, Any]:
    completed = subprocess.run(
        [sys.executable, str(RESOLVER), "resolve", route, "--json"],
        check=True,
        text=True,
        capture_output=True,
    )
    return json.loads(completed.stdout)


def live_payload(route: dict[str, Any], command: str, topic: str | None) -> dict[str, Any]:
    source = """
import json
import optimizer as opt
mode = __import__('sys').argv[1]
topic = __import__('sys').argv[2] if len(__import__('sys').argv) > 2 else None
if mode == 'status':
    out = {'version': opt.__version__, 'groups': sorted(opt.info()['groups']), 'paths': sorted(opt.info()['paths'])}
elif mode == 'discover':
    out = opt.search(topic)
elif mode == 'campaigns':
    out = opt.campaigns.list()
elif mode == 'tracker':
    out = opt.tracker.info()
elif mode == 'methods':
    out = opt.optimizers.list()
elif mode == 'contract':
    out = opt.contract_info()
else:
    raise ValueError('unsupported mode')
print(json.dumps(out, sort_keys=True, default=str))
"""
    args = ["conda", "run", "--no-capture-output", "-n", str(route["environment"]), "python", "-c", source, command]
    if topic is not None:
        args.append(topic)
    completed = subprocess.run(args, check=True, text=True, capture_output=True)
    return {"route": route, "payload": json.loads(completed.stdout)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("status", "discover", "campaigns", "tracker", "methods", "contract"))
    parser.add_argument("topic", nargs="?")
    parser.add_argument("--route", default="default")
    args = parser.parse_args()
    if args.command == "discover" and not args.topic:
        parser.error("discover requires a narrow query topic")
    print(json.dumps(live_payload(resolve(args.route), args.command, args.topic), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
