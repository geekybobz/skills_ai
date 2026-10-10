"""Bind actual update review to source and installation targets."""
import re
import secrets
from pathlib import Path
from . import adapters, workspace
from .common import (AREA, SCHEMA, MaintenanceError, candidate_source, identity,
                     operation_lock, read_state, source_identity, write_state)

def locked(function):
    def run(root, *args, **kwargs):
        with operation_lock(root):
            return function(root, *args, **kwargs)
    return run

@locked
def make_preview(root, session, kind, hosts, approval_ref=None):
    repair = workspace.transition(root, session, 'preview', checks=True, approval_ref=approval_ref) if kind == 'update' else None
    installations = [adapters.preview(root, host) for host in hosts]
    candidate_identity = None
    if repair and repair.get('action') != 'no-changes':
        associated = workspace.transition(root, session, 'inspect')
        candidate_identity = source_identity(Path(associated['working_root']))
        if hosts and candidate_identity['orchestrator/tools/install_runtime_adapter.py'] != source_identity(root)['orchestrator/tools/install_runtime_adapter.py']:
            raise MaintenanceError('INSTALLER_CHANGED: deploy reviewed source first, then review refresh separately')
    if ((not repair or repair.get('action') == 'no-changes')
            and sorted(hosts, key=lambda h: h['host']) == sorted(adapters.bindings(root), key=lambda h: h['host'])
            and all(adapters.check(root, host)['status'] == 'current' for host in hosts)):
        return {'status': 'unchanged', 'kind': kind, 'repair': repair, 'authority': 'none',
                'next': 'No source or configured installation changes; no approval needed.'}
    ready = not repair or repair.get('action') == 'no-changes' or repair.get('ready') is True
    plan = {'schema': SCHEMA, 'kind': kind, 'root': str(root), 'session': session,
            'source_identity': source_identity(root), 'candidate_identity': candidate_identity,
            'repair_preview_id': repair.get('preview_id') if repair else None,
            'ready': ready, 'installations': installations}
    preview_id = identity(plan)
    write_state(root / AREA / 'previews' / (preview_id + '.json'), plan)
    return {'status': 'awaiting-approval' if ready else 'blocked', 'preview_id': preview_id,
            'kind': kind, 'repair': repair, 'installations': installations, 'authority': 'none',
            'installation_source': candidate_identity or plan['source_identity'],
            'installation_note': 'Targets will be refreshed from the reviewed candidate after source verification.' if candidate_identity else 'Targets use the current source.',
            'next': 'Review actual changes and targets; approve this exact preview.'}

@locked
def apply_preview(root, preview_id, approval_ref, *, expected_kind):
    if not re.fullmatch('[a-f0-9]{64}', preview_id or '') or not approval_ref or len(approval_ref) > 256:
        raise MaintenanceError('EXACT_PREVIEW_AND_ACTUAL_APPROVAL_REQUIRED')
    plan = read_state(root / AREA / 'previews' / (preview_id + '.json'))
    fields = {'schema', 'kind', 'root', 'session', 'source_identity', 'candidate_identity',
              'repair_preview_id', 'ready', 'installations'}
    if (plan is None or set(plan) != fields or plan['schema'] != SCHEMA or identity(plan) != preview_id
            or plan['root'] != str(root) or plan['kind'] != expected_kind or plan['ready'] is not True):
        raise MaintenanceError('INVALID_OR_UNREADY_PREVIEW')
    if source_identity(root) != plan['source_identity']:
        raise MaintenanceError('SOURCE_CHANGED_AFTER_REVIEW')
    adapters.bindings(root)  # Corrupt known host state must fail before effects.
    if not isinstance(plan['installations'], list) or len(plan['installations']) > len(adapters.HOSTS):
        raise MaintenanceError('INVALID_INSTALLATION_PLAN')
    if candidate_source(root) and plan['kind'] == 'update':
        raise MaintenanceError('CANDIDATE_CANNOT_CONTROL_SOURCE')
    for installation in plan['installations']:
        if not isinstance(installation, dict) or set(installation) != {'binding', 'before', 'changes'}:
            raise MaintenanceError('INVALID_INSTALLATION_PLAN')
        if adapters.preview(root, installation['binding']) != installation:
            raise MaintenanceError('HOST_CHANGED_AFTER_REVIEW')
    operation_id = secrets.token_hex(16)
    receipt_path = root / AREA / 'receipts' / (operation_id + '.json')
    receipt = {'schema': SCHEMA, 'operation_id': operation_id, 'preview_id': preview_id,
               'kind': plan['kind'], 'status': 'running', 'source': None,
               'hosts': [], 'attempted_hosts': [], 'phase': 'source', 'authority': 'none'}
    write_state(receipt_path, receipt)
    try:
        if plan['repair_preview_id']:
            receipt['source'] = workspace.transition(root, plan['session'], 'apply',
                        approved_preview=plan['repair_preview_id'], approval_ref=approval_ref)
            if source_identity(root) != plan['candidate_identity']:
                raise MaintenanceError('DEPLOYED_SOURCE_IDENTITY_MISMATCH')
        receipt['phase'] = 'refresh'
        write_state(receipt_path, receipt)
        for installation in plan['installations']:
            backup = root / AREA / 'backups' / operation_id / installation['binding']['host']
            receipt['attempted_hosts'].append({'binding': installation['binding'], 'backup': str(backup)})
            write_state(receipt_path, receipt)
            receipt['hosts'].append(adapters.refresh(root, installation, backup))
            write_state(receipt_path, receipt)
        receipt['phase'] = 'complete'
        receipt['status'] = 'complete'
        receipt['next'] = ('No pending steps; host context remains host-owned.' if plan['installations']
                           else 'Source step complete. No hosts configured; use refresh --host codex or --host claude.')
    except Exception as exc:
        receipt['status'] = 'partial' if receipt['source'] or receipt['attempted_hosts'] else 'failed'
        receipt['error'] = str(exc) if isinstance(exc, MaintenanceError) else type(exc).__name__
        receipt['next'] = ('Inspect source and receipt; retry refresh only if source was deployed.'
                           if receipt['source'] else 'Inspect actual effects, repair transaction and backups before retry or recovery.')
    write_state(receipt_path, receipt)
    return receipt | {'receipt': str(receipt_path)}
