"""Workspace transitions remain source-controller operations."""
import secrets
from .common import AREA, SCHEMA, MaintenanceError, candidate_source, run_tool, write_state

def transition(root, session, action, *, approval_ref=None, approved_preview=None, checks=False):
    if candidate_source(root):
        raise MaintenanceError('CANDIDATE_CANNOT_CONTROL_SOURCE')
    if not session:
        raise MaintenanceError('SESSION_REQUIRED: use repair on or --session NAME')
    args = [action, '--session', session]
    if action in ('start', 'pause', 'apply'):
        args += ['--write']
    if checks:
        args += ['--run-checks']
    if approval_ref:
        args += ['--approval-ref', approval_ref]
    if approved_preview:
        args += ['--approved-preview', approved_preview]
    result = run_tool(root, 'repair_workspace.py', args)
    if result['tool_returncode']:
        raise MaintenanceError(result.get('reason', 'REPAIR_FAILED'))
    return result

def repair(root, session, on):
    if on and not session:
        session = 'terminal-' + secrets.token_hex(12)
        result = transition(root, session, 'start')
        write_state(root / AREA / 'terminal-session.json', {'schema': SCHEMA, 'session': session})
    elif not on and not session:
        return {'repair': 'off', 'workspace': None, 'session': None}
    else:
        result = transition(root, session, 'start' if on else 'pause')
    return result | {'session': session}
