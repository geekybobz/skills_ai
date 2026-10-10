#!/usr/bin/env python3
"""Thin entry for the shared maintenance interface."""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / "orchestrator" / "runtime"))
from maintenance.cli import main as cli_main

def main(argv=None):
    return cli_main(argv, implementation_root=ROOT)

if __name__ == '__main__':
    raise SystemExit(main())
