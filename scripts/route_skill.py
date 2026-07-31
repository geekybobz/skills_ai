#!/usr/bin/env python3
"""Select one active skill or return NORMAL without blocking the task."""

from __future__ import annotations

import argparse
import json
import os
import select
import sys
import time
from pathlib import Path
from typing import Any, BinaryIO

from registry_runtime import RegistryRuntimeError, compact_context, load_manifest, route_request


PROTOCOL_VERSION = "skills-ai/1"
DEFAULT_STDIN_TIMEOUT_MS = 10_000
DEFAULT_MAX_REQUEST_BYTES = 1024 * 1024
FALLBACK_RESPONSE_CONTRACT = [
    "Answer the request first.",
    "Use polished, complete sentences without filler or canned praise.",
    "Preserve technical terms, symbols, code, paths, URLs, and quoted errors.",
    "State assumptions, evidence boundaries, and uncertainty only when relevant.",
    "Use the smallest structure that keeps the result clear and verifiable.",
]


class RequestError(RegistryRuntimeError):
    """Expected request-boundary failure with a stable fail-open reason code."""

    def __init__(self, reason_code: str, message: str) -> None:
        super().__init__(message)
        self.reason_code = reason_code


def fallback_decision(reason_code: str, *, request_id: str | None = None) -> dict[str, Any]:
    decision: dict[str, Any] = {
        "protocol": PROTOCOL_VERSION,
        "result": "NORMAL",
        "reason_code": reason_code,
        "context": {
            "operation": "discuss",
            "domain": "general",
            "requested_access": "read-only",
            "output": {
                "voice": "compact-professional",
                "depth": "standard",
                "shape": "answer -> reason -> implication",
            },
            "response_contract": FALLBACK_RESPONSE_CONTRACT,
        },
    }
    if request_id is not None:
        decision["request_id"] = request_id
    return decision


def read_request_line(
    stream: BinaryIO,
    *,
    timeout_ms: int,
    max_request_bytes: int,
) -> bytes:
    """Read one framed request without requiring EOF from the caller."""
    if timeout_ms <= 0:
        raise RequestError("INVALID_INPUT", "stdin timeout must be positive")
    if max_request_bytes <= 0:
        raise RequestError("INVALID_INPUT", "maximum request size must be positive")
    deadline = time.monotonic() + timeout_ms / 1_000
    payload = bytearray()
    try:
        descriptor = stream.fileno()
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise RequestError("INPUT_TIMEOUT", f"request line was not completed within {timeout_ms} ms")
            ready, _, _ = select.select([descriptor], [], [], remaining)
            if not ready:
                raise RequestError("INPUT_TIMEOUT", f"request line was not completed within {timeout_ms} ms")
            chunk = os.read(descriptor, min(65_536, max_request_bytes + 1 - len(payload)))
            if not chunk:
                if not payload:
                    raise RequestError("INVALID_INPUT", "query is required via --query or stdin")
                break
            newline = chunk.find(b"\n")
            payload.extend(chunk if newline < 0 else chunk[:newline])
            if len(payload) > max_request_bytes:
                raise RequestError("REQUEST_TOO_LARGE", f"request exceeds {max_request_bytes} bytes")
            if newline >= 0:
                break
    except RequestError:
        raise
    except (OSError, TypeError, ValueError) as exc:
        raise RequestError("INVALID_INPUT", f"cannot read stdin: {type(exc).__name__}") from exc
    return bytes(payload).rstrip(b"\r")


def parse_request(payload: bytes) -> tuple[str, str | None]:
    try:
        text = payload.decode("utf-8").strip()
    except UnicodeDecodeError as exc:
        raise RequestError("INVALID_INPUT", "request must be UTF-8") from exc
    if not text:
        raise RequestError("INVALID_INPUT", "query must be a non-empty string")
    request_id: str | None = None
    if text.startswith("{"):
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            raise RequestError("INVALID_INPUT", f"invalid JSON request: {exc.msg}") from exc
        if not isinstance(data, dict):
            raise RequestError("INVALID_INPUT", "JSON request must be an object")
        protocol = data.get("protocol")
        if protocol is not None and protocol != PROTOCOL_VERSION:
            raise RequestError("UNSUPPORTED_PROTOCOL", "unsupported protocol version")
        request_id = data.get("request_id")
        if request_id is not None and (not isinstance(request_id, str) or len(request_id) > 128):
            raise RequestError("INVALID_INPUT", "request_id must be a string of at most 128 characters")
        query = data.get("query", "")
    else:
        # Backward-compatible raw one-line input. Structured callers should use JSON.
        query = text
    if not isinstance(query, str) or not query.strip():
        raise RequestError("INVALID_INPUT", "query must be a non-empty string")
    return query, request_id


def read_query(
    argument: str | None,
    *,
    timeout_ms: int,
    max_request_bytes: int,
) -> tuple[str, str | None]:
    if argument is not None:
        encoded = argument.encode("utf-8")
        if len(encoded) > max_request_bytes:
            raise RequestError("REQUEST_TOO_LARGE", f"query exceeds {max_request_bytes} bytes")
        if not argument.strip():
            raise RequestError("INVALID_INPUT", "query must be a non-empty string")
        return argument, None
    return parse_request(
        read_request_line(
            sys.stdin.buffer,
            timeout_ms=timeout_ms,
            max_request_bytes=max_request_bytes,
        )
    )


def emit(decision: dict[str, Any], *, compact: bool) -> None:
    if compact:
        print(compact_context(decision))
    else:
        print(json.dumps(decision, indent=2, sort_keys=True))


def selected_skill_is_available(decision: dict[str, Any]) -> bool:
    if not decision.get("skill"):
        return True
    root = Path(__file__).resolve().parents[1]
    skill_path = (root / decision["skill"]["path"]).resolve()
    try:
        skill_path.relative_to(root)
    except ValueError:
        return False
    return skill_path.is_file()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query", help="request text; one JSON line on stdin is used when omitted")
    parser.add_argument("--compact", action="store_true", help="emit a compact context receipt")
    parser.add_argument("--strict", action="store_true", help="return nonzero for operational router errors")
    parser.add_argument("--manifest", type=Path, help="override the compiled manifest path")
    parser.add_argument("--stdin-timeout-ms", type=int, default=DEFAULT_STDIN_TIMEOUT_MS)
    parser.add_argument("--max-request-bytes", type=int, default=DEFAULT_MAX_REQUEST_BYTES)
    args = parser.parse_args(argv)
    started = time.perf_counter_ns()
    request_id: str | None = None
    try:
        query, request_id = read_query(
            args.query,
            timeout_ms=args.stdin_timeout_ms,
            max_request_bytes=args.max_request_bytes,
        )
        try:
            manifest = load_manifest(args.manifest) if args.manifest else load_manifest()
        except RegistryRuntimeError as exc:
            raise RequestError("MANIFEST_UNAVAILABLE", str(exc)) from exc
        decision = route_request(query, manifest)
        decision["protocol"] = PROTOCOL_VERSION
        if request_id is not None:
            decision["request_id"] = request_id
        if not selected_skill_is_available(decision):
            decision = fallback_decision("SELECTED_SKILL_UNAVAILABLE", request_id=request_id)
        decision["router_ms"] = round((time.perf_counter_ns() - started) / 1_000_000, 3)
        emit(decision, compact=args.compact)
        return 0
    except RequestError as exc:
        decision = fallback_decision(exc.reason_code, request_id=request_id)
        decision["router_ms"] = round((time.perf_counter_ns() - started) / 1_000_000, 3)
        emit(decision, compact=args.compact)
        print(f"skills-ai router fail-open: reason={exc.reason_code} detail={exc}", file=sys.stderr)
        return 2 if args.strict else 0
    except (OSError, RegistryRuntimeError, ValueError) as exc:
        decision = fallback_decision("ROUTER_INTERNAL_ERROR", request_id=request_id)
        decision["router_ms"] = round((time.perf_counter_ns() - started) / 1_000_000, 3)
        emit(decision, compact=args.compact)
        print(f"skills-ai router fail-open: reason=ROUTER_INTERNAL_ERROR detail={type(exc).__name__}", file=sys.stderr)
        return 2 if args.strict else 0


if __name__ == "__main__":
    raise SystemExit(main())
