"""Bounded state, identities and fixed-tool execution."""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from contextlib import contextmanager
import fcntl

SCHEMA = 'skills-ai/maintenance/1'
MAX_BYTES = 16 * 1024 * 1024
AREA = '.runtime/maintenance'

@contextmanager
def operation_lock(root):
    path = safe_path(root / AREA / 'operation.lock')
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    with open(path, 'a+b') as handle:
        os.fchmod(handle.fileno(), 0o600)
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise MaintenanceError('MAINTENANCE_OPERATION_BUSY') from exc
        try:
            yield
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)

class MaintenanceError(RuntimeError):
    pass

def identity(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()

def safe_path(path):
    path = Path(path)
    if not path.is_absolute() or '..' in path.parts:
        raise MaintenanceError('ABSOLUTE_SAFE_PATH_REQUIRED')
    for part in (path, *path.parents):
        if part.is_symlink():
            raise MaintenanceError('SYMLINK_PATH_REFUSED')
    return path

def fingerprint(path):
    path = safe_path(path)
    if not path.exists():
        return None
    if not path.is_file() or path.stat().st_size > MAX_BYTES:
        raise MaintenanceError('INVALID_MANAGED_FILE')
    return {'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'mode': path.stat().st_mode & 0o777}

def unique_object(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise MaintenanceError('DUPLICATE_STATE_FIELD')
        value[key] = item
    return value

def read_state(path):
    path = safe_path(path)
    if not path.exists():
        return None
    if not path.is_file() or path.stat().st_size > MAX_BYTES:
        raise MaintenanceError('INVALID_STATE_FILE')
    try:
        value = json.loads(path.read_bytes(), object_pairs_hook=unique_object)
    except (ValueError, UnicodeError) as exc:
        raise MaintenanceError('INVALID_STATE_JSON') from exc
    if not isinstance(value, dict):
        raise MaintenanceError('INVALID_STATE_OBJECT')
    return value

def write_state(path, value):
    path = safe_path(path)
    raw = (json.dumps(value, indent=2, sort_keys=True) + '\n').encode()
    if len(raw) > MAX_BYTES:
        raise MaintenanceError('STATE_TOO_LARGE')
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd, temporary = tempfile.mkstemp(prefix='.' + path.name, dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as handle:
            os.fchmod(handle.fileno(), 0o600)
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)

def run_tool(root, script, arguments=(), *, timeout=180, parse=True):
    result = subprocess.run([sys.executable, '-B', str(root / 'orchestrator' / 'tools' / script), *arguments],
                            cwd=root, env=os.environ | {'PYTHONDONTWRITEBYTECODE': '1', 'GIT_OPTIONAL_LOCKS': '0'},
                            capture_output=True, timeout=timeout)
    if len(result.stdout) > MAX_BYTES or len(result.stderr) > MAX_BYTES:
        raise MaintenanceError('TOOL_OUTPUT_TOO_LARGE')
    if not parse:
        return {'returncode': result.returncode, 'output': result.stdout.decode(errors='replace').strip()}
    try:
        value = json.loads(result.stdout, object_pairs_hook=unique_object)
    except (ValueError, UnicodeError) as exc:
        raise MaintenanceError('INVALID_TOOL_RESPONSE:' + script) from exc
    if not isinstance(value, dict):
        raise MaintenanceError('INVALID_TOOL_RESPONSE:' + script)
    return value | {'tool_returncode': result.returncode}

def source_identity(root):
    return {p: fingerprint(root / p) for p in ('orchestrator/runtime/SKILL.md', 'orchestrator/runtime/skills-orchestrator/SKILL.md',
            'orchestrator/tools/install_runtime_adapter.py', 'orchestrator/adapters/claude/skills-ai-context.js')}

def candidate_source(root):
    marker = root.parent / 'workspace.json'
    if root.name == 'repo' and root.parent.parent.name == 'workspaces':
        value = read_state(marker)
        if value and value.get('schema') == 'skills-ai/repair-workspace/1':
            return value.get('source')
    return None

def session_id(root, explicit=None):
    value = explicit if explicit is not None else os.environ.get('CODEX_THREAD_ID')
    if value is None:
        stored = read_state(root / AREA / 'terminal-session.json')
        if stored is not None:
            if set(stored) != {'schema', 'session'} or stored['schema'] != SCHEMA:
                raise MaintenanceError('INVALID_TERMINAL_SESSION')
            value = stored['session']
    if value is not None and (not isinstance(value, str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,128}', value)):
        raise MaintenanceError('INVALID_SESSION')
    return value
