#!/usr/bin/env python3
"""One-shot repair controller. The host interprets controls and obtains approval."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "orchestrator" / "runtime"))
sys.path.insert(0, str(ROOT / "orchestrator" / "tools"))
from model_context import ContextError
# Import by a unique module name: this CLI and its runtime share a basename.
import importlib.util
spec = importlib.util.spec_from_file_location('skills_ai_repair', ROOT / 'orchestrator/runtime/repair_workspace.py')
repair = importlib.util.module_from_spec(spec)
spec.loader.exec_module(repair)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('start', 'inspect', 'pause', 'preview', 'apply', 'recover'))
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--session', default=os.environ.get('CODEX_THREAD_ID'))
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--run-checks', action='store_true')
    parser.add_argument('--approved-preview')
    parser.add_argument('--approval-ref')
    args = parser.parse_args()
    try:
        if not args.root.is_absolute() or args.root.is_symlink():
            raise ContextError('REPAIR_ABSOLUTE_ROOT_REQUIRED')
        root = args.root.resolve()
        repair.session_key(args.session)
        if args.action == 'inspect': result = repair.inspect(root, args.session)
        elif args.action == 'start': result = repair.start(root, args.session, write=args.write)
        elif args.action == 'pause': result = repair.pause(root, args.session, write=args.write)
        elif args.action == 'preview': result = repair.preview(root, args.session, run_checks=args.run_checks, approval_ref=args.approval_ref)
        elif args.action == 'apply': result = repair.apply_update(root, args.session, args.approved_preview, write=args.write, approval_ref=args.approval_ref)
        else: result = repair.recover_update(root, args.session, write=args.write)
        print(json.dumps(result)); return 0
    except (ContextError, OSError, ValueError, subprocess.TimeoutExpired) as exc:
        print(json.dumps({'action': 'blocked', 'reason': str(exc), 'authority': 'none'})); return 2


if __name__ == '__main__':
    raise SystemExit(main())
