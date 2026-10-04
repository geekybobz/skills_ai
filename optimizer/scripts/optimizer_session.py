#!/usr/bin/env python3
"""Maintain a small semantic optimizer-session ledger without numerical calls."""

from __future__ import annotations

import argparse
import json
import math
import os
import tempfile
from pathlib import Path
from typing import Any


SCHEMA = "optimizer.session.v1"


class SessionError(ValueError):
    """Raised for invalid or unsafe session mutations."""


def _finite_number(value: Any, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise SessionError(f"{name} must be a finite number")
    result = float(value)
    if not math.isfinite(result):
        raise SessionError(f"{name} must be a finite number")
    return result


def _json_object(raw: str, option: str) -> dict[str, Any]:
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SessionError(f"{option} must be valid JSON") from exc
    if not isinstance(value, dict):
        raise SessionError(f"{option} must be a JSON object")
    return value


def _read(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise SessionError(f"cannot read session: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SessionError(f"session is not valid JSON: {path}") from exc
    if not isinstance(payload, dict) or payload.get("schema") != SCHEMA:
        raise SessionError(f"session does not use {SCHEMA}: {path}")
    if not isinstance(payload.get("stages"), list):
        raise SessionError("session stages must be a list")
    if not isinstance(payload.get("objective"), dict):
        raise SessionError("session objective must be an object")
    return payload


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent, text=True)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, indent=2, sort_keys=True) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except Exception:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise


def _emit(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


def _best_result(session: dict[str, Any], event: dict[str, Any]) -> None:
    objective = session["objective"]
    metric = objective.get("metric")
    metrics = event.get("metrics", {})
    if not isinstance(metric, str) or metric not in metrics:
        return
    try:
        value = _finite_number(metrics[metric], f"metrics.{metric}")
    except SessionError:
        return
    current = session.get("best_result")
    is_better = current is None
    if isinstance(current, dict):
        current_value = _finite_number(current.get("value"), "best_result.value")
        is_better = value < current_value if objective["mode"] == "min" else value > current_value
    if is_better:
        session["best_result"] = {
            "metric": metric,
            "value": value,
            "stage": event["stage"],
            "method": event["method"],
            "run_path": event.get("run_path"),
        }


def command_init(args: argparse.Namespace) -> dict[str, Any]:
    path = Path(args.session)
    if path.exists():
        raise SessionError(f"refusing to overwrite existing session: {path}")
    if args.mode not in {"min", "max"}:
        raise SessionError("mode must be min or max")
    if args.chunks < 1 or args.iterations < 1:
        raise SessionError("chunks and iterations must be positive")
    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "revision": 0,
        "optimizer": {"version": args.optimizer_version, "root": args.optimizer_root},
        "system_target": args.system_target,
        "objective": {"metric": args.metric, "mode": args.mode, "target": args.target},
        "budget": {"chunks": args.chunks, "iterations_per_chunk": args.iterations},
        "stages": [],
        "best_result": None,
        "next_action": {"code": "preflight", "reason": "session initialized"},
    }
    _write(path, payload)
    return payload


def command_record(args: argparse.Namespace) -> dict[str, Any]:
    path = Path(args.session)
    payload = _read(path)
    metrics = _json_object(args.metrics_json, "--metrics-json")
    event: dict[str, Any] = {"stage": args.stage, "method": args.method, "metrics": metrics}
    if args.run_path:
        event["run_path"] = args.run_path
    if args.diagnosis:
        event["diagnosis"] = args.diagnosis
    payload["stages"].append(event)
    _best_result(payload, event)
    payload["revision"] = int(payload.get("revision", 0)) + 1
    _write(path, payload)
    return payload


def command_next(args: argparse.Namespace) -> dict[str, Any]:
    path = Path(args.session)
    payload = _read(path)
    payload["next_action"] = {"code": args.code, "reason": args.reason}
    payload["revision"] = int(payload.get("revision", 0)) + 1
    _write(path, payload)
    return payload


def command_show(args: argparse.Namespace) -> dict[str, Any]:
    return _read(Path(args.session))


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    commands = root.add_subparsers(dest="command", required=True)

    init = commands.add_parser("init", help="create a new session without overwriting")
    init.add_argument("session")
    init.add_argument("--optimizer-version", required=True)
    init.add_argument("--optimizer-root", required=True)
    init.add_argument("--system-target", required=True)
    init.add_argument("--metric", default="J")
    init.add_argument("--mode", default="min")
    init.add_argument("--target", type=float)
    init.add_argument("--chunks", type=int, required=True)
    init.add_argument("--iterations", type=int, required=True)
    init.set_defaults(handler=command_init)

    record = commands.add_parser("record", help="append one observed bounded stage")
    record.add_argument("session")
    record.add_argument("--stage", required=True)
    record.add_argument("--method", required=True)
    record.add_argument("--metrics-json", required=True)
    record.add_argument("--run-path")
    record.add_argument("--diagnosis")
    record.set_defaults(handler=command_record)

    next_action = commands.add_parser("next", help="record the next explainable action")
    next_action.add_argument("session")
    next_action.add_argument("--code", required=True)
    next_action.add_argument("--reason", required=True)
    next_action.set_defaults(handler=command_next)

    show = commands.add_parser("show", help="print a session as JSON")
    show.add_argument("session")
    show.set_defaults(handler=command_show)
    return root


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        _emit(args.handler(args))
    except (OSError, SessionError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, sort_keys=True))
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
