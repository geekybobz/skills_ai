"""Contained repair workspaces. Mechanical snapshots and transactions, never authority.

The host interprets repair controls and obtains approval. This controller stays in
the source checkout; edited candidate code cannot authorize its own deployment.
"""
from __future__ import annotations

import base64
from contextlib import contextmanager
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import stat
import subprocess
import sys

from model_context import ContextError, read_json, read_relative

AREA = '.runtime/repair'
MAX_FILES = 5000
MAX_BYTES = 128 * 1024 * 1024
MAX_FILE = 8 * 1024 * 1024
MAX_RECORD = 16 * 1024 * 1024
EXCLUDED = {'.git', '.runtime', 'feedback-tickets', 'sample_resources',
            '__pycache__', 'node_modules', '.venv', 'venv', '.ssh', '.aws'}


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def identity(value):
    return digest(json.dumps(value, sort_keys=True, separators=(',', ':')).encode())


def fingerprints(records):
    return {p: {k: b[k] for k in ('sha256', 'mode')} for p, b in records.items()}


def session_key(session):
    if not isinstance(session, str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,128}', session):
        raise ContextError('REPAIR_SESSION_REQUIRED')
    return digest(session.encode())[:32]


def permitted(path):
    parts = path.split('/')
    return (not path.startswith('/') and all(p and p not in {'.', '..'} for p in parts)
            and not any(p in EXCLUDED or p == '.DS_Store' or p == '.env'
                        or p.startswith('.env.') or p.endswith(('.pyc', '.pem', '.key')) or p in {'id_rsa', 'id_ed25519', 'credentials.json', 'secrets.json'} for p in parts)
            and parts[0] not in {'.codex', '.claude'}
            and not any(p in {'.codex', '.claude'} and (i + 1 >= len(parts) or parts[i + 1] != 'skills') for i, p in enumerate(parts))
            and not path.startswith('.obsidian/workspace'))


def git(root, *args):
    env = os.environ | {'GIT_OPTIONAL_LOCKS': '0', 'GIT_CONFIG_NOSYSTEM': '1'}
    result = subprocess.run(['git', '-c', 'core.hooksPath=/dev/null', '-c', 'commit.gpgsign=false',
                             '-C', str(root), *args], capture_output=True, env=env, timeout=30)
    if result.returncode:
        raise ContextError('REPAIR_GIT_FAILED')
    return result.stdout


def safe_target(root, relative, *, parents=False):
    if relative.startswith('/') or any(p in ('', '.', '..') for p in relative.split('/')):
        raise ContextError('REPAIR_INVALID_PATH')
    target = root
    for part in relative.split('/')[:-1]:
        target = target / part
        if target.is_symlink() or (target.exists() and not target.is_dir()):
            raise ContextError('REPAIR_UNSAFE_PARENT')
        if parents:
            target.mkdir(mode=0o700, exist_ok=True)
    target = root / relative
    if target.is_symlink():
        raise ContextError('REPAIR_UNSAFE_TARGET')
    return target


def write_json(root, relative, value):
    from replacement_packet import atomic_file
    target = safe_target(root, relative, parents=True)
    raw = (json.dumps(value, indent=2, sort_keys=True) + '\n').encode()
    if len(raw) > MAX_RECORD:
        raise ContextError('REPAIR_RECORD_TOO_LARGE')
    atomic_file(target, raw, 0o600)


@contextmanager
def lock(root):
    target = safe_target(root, AREA + '/controller.lock', parents=True)
    fd = os.open(target, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    try:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise ContextError('REPAIR_BUSY') from exc
        yield
    finally:
        os.close(fd)


def blob(root, path):
    raw = read_relative(root, path, maximum=MAX_FILE)
    mode = stat.S_IMODE((root / path).stat().st_mode)
    return {'sha256': digest(raw), 'mode': 0o755 if mode & 0o111 else 0o644,
            'data': base64.b64encode(raw).decode()}


def files(root):
    """Git-bounded source inventory; no recursive search through ignored state."""
    names = git(root, 'ls-files', '--cached', '--others', '--exclude-standard', '-z').decode().split('\0')
    out = {}
    for path in sorted(set(filter(None, names))):
        if not permitted(path):
            continue
        target = root / path
        if target.is_symlink():
            declared = read_json(root, 'orchestrator/governance/CONTRACT.json').get('allowed_external_symlinks', [])
            if path not in declared:
                raise ContextError('REPAIR_UNSAFE_SOURCE_LINK')
            continue  # Declared foreign trees are copied separately, never linked.
        if target.is_dir():
            continue  # Git submodule roots are handled separately.
        if target.exists():
            out[path] = blob(root, path)
        if len(out) > MAX_FILES:
            raise ContextError('REPAIR_SNAPSHOT_TOO_LARGE')
    if sum(len(base64.b64decode(b['data'])) for b in out.values()) > MAX_BYTES:
        raise ContextError('REPAIR_SNAPSHOT_TOO_LARGE')
    return out


def references(root):
    """Bound declared foreign trees, without retaining live symlinks or .git pointers."""
    contract = read_json(root, 'orchestrator/governance/CONTRACT.json')
    names = list(contract.get('allowed_external_symlinks', []))
    stages = git(root, 'ls-files', '--stage', '-z').decode().split('\0')
    names += [s.split('\t', 1)[1] for s in stages if s.startswith('160000 ')]
    out = {}
    for prefix in sorted(set(names)):
        if not permitted(prefix):
            raise ContextError('REPAIR_INVALID_REFERENCE')
        source = (root / prefix).resolve()
        if not source.is_dir():
            continue
        # Only explicitly declared references are walked; generated state is pruned.
        for directory, dirs, leaves in os.walk(source, followlinks=False):
            dirs[:] = [d for d in sorted(dirs) if d not in EXCLUDED and not (Path(directory) / d).is_symlink()]
            for name in sorted(leaves):
                relative = (Path(directory) / name).relative_to(source).as_posix()
                if not permitted(relative) or (source / relative).is_symlink():
                    continue
                path = prefix + '/' + relative
                out[path] = blob(source, relative)
                if len(out) > MAX_FILES:
                    raise ContextError('REPAIR_REFERENCE_TOO_LARGE')
    if sum(len(base64.b64decode(b['data'])) for b in out.values()) > MAX_BYTES:
        raise ContextError('REPAIR_REFERENCE_TOO_LARGE')
    return out


def association(root, session):
    relative = AREA + '/sessions/' + session_key(session) + '.json'
    safe_target(root, relative)
    try:
        value = read_json(root, relative, maximum=4096)
    except ContextError:
        if not (root / relative).exists():
            return relative, None
        raise
    if set(value) != {'schema', 'workspace', 'on'} or value['schema'] != 'skills-ai/repair-session/1' or type(value['on']) is not bool:
        raise ContextError('REPAIR_INVALID_SESSION')
    if not re.fullmatch(r'repair-[a-f0-9]{16}', str(value['workspace'])):
        raise ContextError('REPAIR_INVALID_WORKSPACE')
    return relative, value


def workspace(root, session):
    relative, session_record = association(root, session)
    if session_record is None:
        raise ContextError('REPAIR_WORKSPACE_REQUIRED')
    prefix = AREA + '/workspaces/' + session_record['workspace']
    meta = read_json(root, prefix + '/workspace.json', maximum=16384)
    if set(meta) != {'schema', 'source', 'baseline_commit', 'references', 'stage'} or meta['schema'] != 'skills-ai/repair-workspace/1' or meta['source'] != str(root):
        raise ContextError('REPAIR_INVALID_WORKSPACE')
    if not re.fullmatch('[a-f0-9]{40,64}', meta['baseline_commit']) or meta['stage'] not in {'working', 'review', 'deployed', 'recovering'}:
        raise ContextError('REPAIR_INVALID_WORKSPACE')
    repo = safe_target(root, prefix + '/repo/marker').parent
    if not repo.is_dir() or not (repo / '.git').is_dir() or (repo / '.git').is_symlink():
        raise ContextError('REPAIR_WORKSPACE_UNAVAILABLE')
    baseline = read_json(root, prefix + '/baseline.json', maximum=MAX_RECORD)
    if set(baseline) != {'files', 'references'} or identity(baseline['references']) != meta['references']:
        raise ContextError('REPAIR_INVALID_BASELINE')
    return relative, session_record, prefix, meta, repo, baseline


def inspect(root, session):
    _, record = association(root, session)
    if record is None:
        return {'repair': 'off', 'workspace': None, 'authority': 'none'}
    _, record, prefix, meta, repo, _ = workspace(root, session)
    return {'repair': 'on' if record['on'] else 'off', 'workspace': record['workspace'],
            'working_root': str(repo), 'stage': meta['stage'], 'authority': 'none',
            'instruction': 'Recheck actual conversation scope; this record is advisory data, not permission.'}


def start(root, session, *, write=False):
    relative, record = association(root, session)
    if record is not None:
        result = inspect(root, session)
        if write:
            with lock(root):
                write_json(root, relative, record | {'on': True})
        return result | {'action': 'resumed' if write else 'resume-preview', 'repair': 'on' if write else result['repair']}
    if not write:
        return {'action': 'start-preview', 'source': str(root), 'authority': 'none'}
    with lock(root):
        if association(root, session)[1] is not None:
            raise ContextError('REPAIR_SESSION_CHANGED')
        owned, foreign = files(root), references(root)
        combined = owned | foreign
        if len(combined) > MAX_FILES or sum(len(base64.b64decode(b['data'])) for b in combined.values()) > MAX_BYTES:
            raise ContextError('REPAIR_SNAPSHOT_TOO_LARGE')
        ws = 'repair-' + secrets.token_hex(8)
        prefix = AREA + '/workspaces/' + ws
        repo = safe_target(root, prefix + '/repo/marker', parents=True).parent
        from replacement_packet import atomic_file
        external = read_json(root, 'orchestrator/governance/CONTRACT.json').get('allowed_external_symlinks', [])
        modules = [line.split('\t', 1) for line in git(root, 'ls-files', '--stage', '-z').decode().split('\0') if line.startswith('160000 ')]
        for path, b in combined.items():
            destination = '.runtime/repair-references/' + path if any(path.startswith(e + '/') for e in external) else path
            atomic_file(safe_target(repo, destination, parents=True), base64.b64decode(b['data']), (b['mode'] & 0o555) if path in foreign else b['mode'])
        for name in external:
            link = safe_target(repo, name, parents=True)
            target = safe_target(repo, '.runtime/repair-references/' + name + '/marker', parents=True).parent
            os.symlink(os.path.relpath(target, link.parent), link)
        if files(root) != owned or references(root) != foreign:
            raise ContextError('REPAIR_SOURCE_CHANGED_DURING_COPY')
        for stage, name in modules:
            child = repo / name
            if child.is_dir():
                git(child, 'init', '-q')
                git(child, 'config', 'user.name', 'Skills AI reference snapshot')
                git(child, 'config', 'user.email', 'reference@skills-ai.invalid')
                copied = [p[len(name)+1:] for p in foreign if p.startswith(name + '/')]
                if (root / name / '.git').exists():
                    tracked = set(git(root / name, 'ls-files', '-z').decode().split('\0'))
                    copied = [p for p in copied if p in tracked]
                if copied:git(child, 'add', '--force', '--', *copied)
                git(child, 'commit', '--allow-empty', '-qm', 'Independent read-only reference snapshot')
        git(repo, 'init', '-q')
        git(repo, 'config', 'user.name', 'Skills AI repair')
        git(repo, 'config', 'user.email', 'repair@skills-ai.invalid')
        git(repo, 'add', '--all')
        for stage, name in modules:
            oid = stage.split()[1]
            git(repo, 'rm', '--cached', '-r', '-f', '--ignore-unmatch', '--', name)
            git(repo, 'update-index', '--add', '--cacheinfo', '160000,' + oid + ',' + name)
        git(repo, 'commit', '--allow-empty', '-qm', 'Snapshot current source for contained repair')
        baseline_commit = git(repo, 'rev-parse', 'HEAD').decode().strip()
        write_json(root, prefix + '/baseline.json', {'files': fingerprints(owned), 'references': fingerprints(foreign)})
        write_json(root, prefix + '/workspace.json', {'schema': 'skills-ai/repair-workspace/1',
                   'source': str(root), 'baseline_commit': baseline_commit, 'references': identity(fingerprints(foreign)), 'stage': 'working'})
        write_json(root, relative, {'schema': 'skills-ai/repair-session/1', 'workspace': ws, 'on': True})
        return inspect(root, session) | {'action': 'created', 'files': len(combined)}


def pause(root, session, *, write=False):
    relative, record = association(root, session)
    if record is None:
        return inspect(root, session)
    if write:
        with lock(root):
            write_json(root, relative, record | {'on': False})
    return inspect(root, session) | {'action': 'paused' if write else 'pause-preview'}


def packet_for(root, session):
    _, _, prefix, meta, repo, baseline = workspace(root, session)
    current = files(repo)
    current_ids = fingerprints(current)
    if fingerprints(references(repo)) != baseline['references']:
        raise ContextError('REPAIR_FOREIGN_REFERENCE_CHANGED')
    current = {p: b for p, b in current.items() if p not in baseline['references']}
    from replacement_packet import blob as committed_blob
    entries = [{'path': p, 'before': committed_blob(repo, meta['baseline_commit'], p) if p in baseline['files'] else None, 'after': current.get(p)}
               for p in sorted(set(current) | set(baseline['files']))
               if current_ids.get(p) != baseline['files'].get(p)]
    from replacement_packet import validate
    packet = {'schema': 'skills-ai/replacement/1', 'baseline': meta['baseline_commit'],
              'revision': git(repo, 'rev-parse', 'HEAD').decode().strip(), 'entries': entries}
    validate(packet)
    return prefix, meta, repo, baseline, packet


def check(root, repo, paths, approval_ref):
    """Invoke candidate checks through a fixed source-owned command, with candidate cwd.

Candidate tests are deliberately executed. They are not a sandbox: the host
must supply filesystem/network restrictions for untrusted code where required.
"""
    command = [sys.executable, '-B', str(repo / 'orchestrator/tools/scan_consistency.py'),
               'plan', '--operation', 'protocol', '--json',
               '--baseline-out', '.runtime/repair-check.json']
    if approval_ref:
        command += ['--approval-ref', approval_ref]
    for path in paths:
        command += ['--path', path]
    # The selected scanner/tests are deliberate test execution, not the controller.
    result = subprocess.run(command, cwd=repo, capture_output=True, timeout=60,
                            env=os.environ | {'PYTHONDONTWRITEBYTECODE': '1', 'GIT_OPTIONAL_LOCKS': '0'})
    if len(result.stdout) > MAX_RECORD:
        raise ContextError('REPAIR_CHECK_OUTPUT_TOO_LARGE')
    try:
        report = json.loads(result.stdout)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ContextError('REPAIR_CHECK_INVALID_OUTPUT') from exc
    if not isinstance(report, dict) or (result.returncode != 0 and report.get('status') == 'PASS'):
        raise ContextError('REPAIR_CHECK_INVALID_OUTPUT')
    return report


def preview(root, session, *, run_checks=False, approval_ref=None, checker=check):
    with lock(root):
        prefix, meta, repo, baseline, packet = packet_for(root, session)
        paths = [e['path'] for e in packet['entries']]
        if not paths:
            return {'action': 'no-changes', 'files': 0, 'authority': 'none'}
        from replacement_packet import preflight
        conflicts = []
        try:
            preflight(root, packet)
        except ContextError as exc:
            conflicts.append(str(exc))
        # Check all snapshotted inputs, not just files being replaced.
        now = fingerprints(files(root))
        dependency_drift = sorted(p for p in set(now) | set(baseline['files'])
                                  if now.get(p) != baseline['files'].get(p) and p not in paths)
        reference_drift = fingerprints(references(root)) != baseline['references']
        report = checker(root, repo, paths, approval_ref) if run_checks else {'status': 'NOT_RUN'}
        # Checks may generate outputs: never bind evidence to the pre-check version.
        _, _, _, _, after_checks = packet_for(root, session)
        if after_checks['entries'] != packet['entries']:
            raise ContextError('REPAIR_CHANGED_DURING_CHECKS')
        ready = report.get('status') == 'PASS' and not conflicts and not dependency_drift and not reference_drift
        if ready:
            # Phase commits may already have removed paths from the index.
            # Stage only existing files or deletions still tracked by Git;
            # committed deletions remain in the baseline-bound packet.
            tracked = set(git(repo, 'ls-files', '-z').decode().split('\0'))
            stage_paths = [p for p in paths if p in tracked or (repo / p).exists() or (repo / p).is_symlink()]
            if stage_paths:
                git(repo, 'add', '--', *stage_paths)
            git(repo, 'commit', '--allow-empty', '-qm', 'Record contained repair update for review')
            packet['revision'] = git(repo, 'rev-parse', 'HEAD').decode().strip()
        record = {'schema': 'skills-ai/repair-preview/1', 'packet': packet,
                  'checks_sha256': identity(report), 'ready': ready,
                  'source_files': identity(now), 'source_references': identity(fingerprints(references(root)))}
        preview_id = identity(record)
        write_json(root, prefix + '/evidence/' + preview_id + '.json', report)
        write_json(root, prefix + '/preview/current.json', record)
        write_json(root, prefix + '/workspace.json', meta | {'stage': 'review'})
        return {'action': 'update-preview', 'preview_id': preview_id, 'ready': ready,
                'paths': paths, 'conflicts': conflicts, 'dependency_drift': dependency_drift,
                'reference_drift': reference_drift, 'checks': report.get('status'),
                'diff': git(repo, 'diff', meta['baseline_commit'], '--', *paths).decode(errors='replace'),
                'authority': 'none', 'next': 'Host explains changes and waits for actual user agreement.'}


def approved(root, session, preview_id):
    prefix, meta, repo, baseline, packet = packet_for(root, session)
    record = read_json(root, prefix + '/preview/current.json', maximum=MAX_RECORD)
    if identity(record) != preview_id or not record.get('ready'):
        raise ContextError('REPAIR_REVIEW_REQUIRED')
    if record['packet'] != packet:
        raise ContextError('REPAIR_PREVIEW_CHANGED')
    evidence = read_json(root, prefix + '/evidence/' + preview_id + '.json', maximum=MAX_RECORD)
    if identity(evidence) != record['checks_sha256'] or evidence.get('status') != 'PASS':
        raise ContextError('REPAIR_EVIDENCE_CHANGED')
    if identity(fingerprints(files(root))) != record['source_files'] or identity(fingerprints(references(root))) != record['source_references']:
        raise ContextError('REPAIR_LIVE_CHANGED')
    return prefix, meta, repo, baseline, packet


def apply_update(root, session, preview_id, *, write=False, approval_ref=None, checker=check):
    # --approved-preview is an attestation by the host, never a permission grant.
    if not re.fullmatch('[a-f0-9]{64}', preview_id or ''):
        raise ContextError('REPAIR_REVIEW_REQUIRED')
    if not write:
        _, _, _, _, packet = approved(root, session, preview_id)
        return {'action': 'apply-preview', 'files': len(packet['entries']), 'authority': 'none'}
    if not approval_ref:
        raise ContextError('REPAIR_ACTUAL_APPROVAL_REQUIRED')
    with lock(root):
        prefix, meta, repo, baseline, packet = approved(root, session, preview_id)
        from replacement_packet import apply
        backup = safe_target(root, prefix + '/rollback/' + preview_id + '.json', parents=True)
        journal = {'schema': 'skills-ai/repair-transaction/1', 'preview_id': preview_id,
                   'backup': prefix + '/rollback/' + preview_id + '.json', 'stage': 'applying'}
        write_json(root, prefix + '/transaction.json', journal)
        write_json(root, prefix + '/workspace.json', meta | {'stage': 'recovering'})
        try:
            apply(root, packet, write=True, backup=backup)
            report = checker(root, root, [e['path'] for e in packet['entries']], approval_ref)
            write_json(root, prefix + '/evidence/live-' + preview_id + '.json', report)
            if report.get('status') != 'PASS':
                raise ContextError('REPAIR_LIVE_CHECK_FAILED')
        except Exception:
            if backup.exists():
                from replacement_packet import recover
                recover(root, packet, write=True)
            write_json(root, prefix + '/transaction.json', journal | {'stage': 'restored'})
            write_json(root, prefix + '/workspace.json', meta)
            raise
        # The isolated commit is the durable record; do not stage inherited live work.
        git(repo, 'bundle', 'create', str(safe_target(root, prefix + '/rollback/history-' + preview_id + '.bundle')), '--all')
        write_json(root, prefix + '/transaction.json', journal | {'stage': 'deployed', 'commit': packet['revision']})
        updated = baseline['files'].copy()
        for entry in packet['entries']:
            if entry['after'] is None:
                updated.pop(entry['path'], None)
            else:
                updated[entry['path']] = {k: entry['after'][k] for k in ('sha256', 'mode')}
        write_json(root, prefix + '/baseline.json', {'files': updated, 'references': baseline['references']})
        write_json(root, prefix + '/workspace.json', meta | {'baseline_commit': packet['revision'], 'stage': 'deployed'})
        return {'action': 'updated', 'files': len(packet['entries']), 'commit': packet['revision'],
                'repair': inspect(root, session)['repair'], 'git_index': 'untouched',
                'git_record': 'contained commit and retained bundle; live commit requires separately bounded staging',
                'rollback': str(backup), 'authority': 'none'}


def recover_update(root, session, *, write=False):
    with lock(root):
        _, _, prefix, meta, repo, _ = workspace(root, session)
        journal = read_json(root, prefix + '/transaction.json', maximum=4096)
        preview_id = journal.get('preview_id')
        expected = prefix + '/rollback/' + str(preview_id) + '.json'
        if not re.fullmatch('[a-f0-9]{64}', preview_id or '') or journal.get('backup') != expected:
            raise ContextError('REPAIR_INVALID_TRANSACTION')
        packet = read_json(root, expected, maximum=MAX_RECORD)
        from replacement_packet import recover
        result = recover(root, packet, write=write)
        if write:
            write_json(root, prefix + '/transaction.json', journal | {'stage': 'restored'})
            # Preserve both histories and recover the pre-apply source baseline.
            baseline = read_json(root, prefix + '/baseline.json', maximum=MAX_RECORD)
            for entry in packet['entries']:
                if entry['before'] is None:
                    baseline['files'].pop(entry['path'], None)
                else:
                    baseline['files'][entry['path']] = {k: entry['before'][k] for k in ('sha256', 'mode')}
            write_json(root, prefix + '/baseline.json', baseline)
            write_json(root, prefix + '/workspace.json', meta | {'baseline_commit': packet['baseline'], 'stage': 'working'})
        return result
