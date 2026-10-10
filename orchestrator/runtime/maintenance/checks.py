"""Local verification separate from host semantics and certification."""
from pathlib import Path
from .common import MaintenanceError, run_tool

def check(root, session, paths=(), full=False, approval_ref=None):
    target = root
    if session:
        association = run_tool(root, 'repair_workspace.py', ['inspect', '--session', session])
        if association['tool_returncode']:
            raise MaintenanceError(association.get('reason', 'REPAIR_INSPECTION_FAILED'))
        if association.get('repair') == 'on' and association.get('working_root'):
            target = Path(association['working_root'])
    args = ['full' if full else 'changed', '--operation', 'update', '--json']
    for path in paths:
        args += ['--path', path]
    if approval_ref:
        args += ['--approval-ref', approval_ref]
    out = run_tool(target, 'scan_consistency.py', args)
    return {'working_root': str(target), 'checks': out, 'status': out.get('status', 'BLOCK'),
            'limits': 'Local artifact checks; host acceptance and domain certification are separate.'}
