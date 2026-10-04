"""Artifact-bound checkpoint inspection. Evidence records never certify claims.

The host decides workflow, approval, validation and recovery. This module only
checks checkpoint shape and whether referenced bytes match recorded identities.
"""
from __future__ import annotations
import hashlib
import json
import os
import re
import secrets
import stat
from pathlib import Path
from model_context import ContextError, read_relative
from project_context import SECRET_VALUE_PATTERN, PERSONAL_PATH_PATTERN

MAX_STATE_BYTES=32*1024
HASH=re.compile(r'^[a-f0-9]{64}$')


def validate_state(value: dict) -> None:
    required={'schema','objective','phase','bindings','artifacts','evidence','completed_effects','unresolved','next_step'}
    if not isinstance(value,dict) or set(value)!=required or value.get('schema')!='skills-ai/checkpoint/1':
        raise ContextError('INVALID_CHECKPOINT_FIELDS')
    if len(json.dumps(value,separators=(',',':')).encode())>MAX_STATE_BYTES:
        raise ContextError('CHECKPOINT_TOO_LARGE')
    def text(v):
        if not isinstance(v,str) or len(v)>700 or SECRET_VALUE_PATTERN.search(v) or PERSONAL_PATH_PATTERN.search(v):
            raise ContextError('INVALID_CHECKPOINT_TEXT')
    def binding(v):
        if not isinstance(v,dict) or set(v)!={'path','sha256'}:
            raise ContextError('INVALID_BINDING')
        path=v['path'];digest=v['sha256'];text(path)
        if not path or path.startswith('/') or '\x00' in path or any(p in {'','.','..'} for p in path.split('/')):
            raise ContextError('INVALID_PATH')
        if not isinstance(digest,str) or not HASH.fullmatch(digest):raise ContextError('INVALID_CONTENT_IDENTITY')
    for name in ('objective','phase','next_step'):text(value[name])
    if not value['objective'] or not value['phase']:raise ContextError('OBJECTIVE_AND_PHASE_REQUIRED')
    for section in ('bindings','artifacts'):
        if not isinstance(value[section],list) or len(value[section])>64:raise ContextError('INVALID_BINDINGS')
        seen=set()
        for v in value[section]:
            binding(v)
            if v['path'] in seen:raise ContextError('DUPLICATE_BINDING')
            seen.add(v['path'])
    if not isinstance(value['evidence'],list) or len(value['evidence'])>64:raise ContextError('INVALID_EVIDENCE')
    for ev in value['evidence']:
        if not isinstance(ev,dict) or set(ev)!={'check','artifact','record','outcome'}:raise ContextError('INVALID_EVIDENCE')
        text(ev['check']);binding(ev['artifact']);binding(ev['record'])
        if ev['outcome'] not in ('passed','failed','unknown'):raise ContextError('INVALID_OUTCOME')
        if ev['artifact'] not in value['artifacts']:raise ContextError('UNBOUND_EVIDENCE_ARTIFACT')
    if not isinstance(value['completed_effects'],list) or len(value['completed_effects'])>32:raise ContextError('INVALID_EFFECTS')
    seen=set()
    for effect in value['completed_effects']:
        if not isinstance(effect,dict) or set(effect)!={'id','receipt'}:raise ContextError('INVALID_EFFECTS')
        text(effect['id']);binding(effect['receipt'])
        if not effect['id'] or effect['id'] in seen:raise ContextError('DUPLICATE_EFFECT')
        seen.add(effect['id'])
    if not isinstance(value['unresolved'],list):raise ContextError('INVALID_UNRESOLVED')
    for item in value['unresolved']:text(item)


def inspect_state(repository: Path, project: Path, value: dict) -> dict:
    validate_state(value)
    observations=[]
    sections=[('bindings',repository,value['bindings']),('artifacts',project,value['artifacts']),
              ('evidence',project,[x['record'] for x in value['evidence']]),
              ('effects',project,[x['receipt'] for x in value['completed_effects']])]
    for section,base,items in sections:
        for binding in items:
            try:
                current=hashlib.sha256(read_relative(base,binding['path'])).hexdigest()
                status='matches' if current==binding['sha256'] else 'changed'
            except ContextError:status='unavailable'
            observations.append({'section':section,'path':binding['path'],'status':status})
    return {'schema':'skills-ai/checkpoint-inspection/1','trust':'untrusted-data-only',
            'content_matches':all(x['status']=='matches' for x in observations),
            'observations':observations,'authority':'none','verification':'not-assessed',
            'resume':'host-must-recheck-scope-instructions-effects-and-evidence'}


def save_state(project: Path, relative: str, value: dict, *, write: bool=False) -> dict:
    """Explicit atomic persistence, with no approval or prompt storage fields."""
    validate_state(value)
    if not re.fullmatch(r'\.skills-ai/[a-z0-9][a-z0-9-]{0,63}\.json',relative):raise ContextError('INVALID_STATE_TARGET')
    if not write:return {'action':'preview','path':relative,'authority':'none'}
    base=os.open(project,os.O_RDONLY|os.O_DIRECTORY)
    directory=None
    temporary='.'+secrets.token_hex(16)+'.tmp'
    created=False
    try:
        try:os.mkdir('.skills-ai',mode=0o700,dir_fd=base)
        except FileExistsError:pass
        directory=os.open('.skills-ai',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=base)
        target=relative.split('/')[1]
        try:
            info=os.stat(target,dir_fd=directory,follow_symlinks=False)
            if not stat.S_ISREG(info.st_mode):raise ContextError('INVALID_STATE_TARGET')
        except FileNotFoundError:pass
        fd=os.open(temporary,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600,dir_fd=directory)
        created=True
        with os.fdopen(fd,'wb') as f:
            f.write((json.dumps(value,sort_keys=True,indent=2)+'\n').encode());f.flush();os.fsync(f.fileno())
        os.replace(temporary,target,src_dir_fd=directory,dst_dir_fd=directory)
        created=False
        os.fsync(directory)
        return {'action':'saved','path':relative,'authority':'none'}
    except OSError as exc:raise ContextError('STATE_WRITE_UNAVAILABLE') from exc
    finally:
        if created and directory is not None:os.unlink(temporary,dir_fd=directory)
        if directory is not None:os.close(directory)
        os.close(base)
