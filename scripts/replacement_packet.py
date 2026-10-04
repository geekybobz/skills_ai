#!/usr/bin/env python3
"""Export/rehearse an exact replacement; never reset Git or grant deployment authority."""
from __future__ import annotations
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'runtime'))
from model_context import ContextError, read_relative
MAX_PACKET_BYTES=16*1024*1024

def digest(raw):return hashlib.sha256(raw).hexdigest()
def safe_path(path):
 if not isinstance(path,str) or not path or path.startswith('/') or '\x00' in path or '\\' in path or any(p in ('','.','..','.git','.agents','.codex') for p in path.split('/')):
  raise ContextError('INVALID_REPLACEMENT_PATH')
 if path.startswith('theory-reference/'):raise ContextError('SUBMODULE_REPLACEMENT_FORBIDDEN')
 return path

def git(root,*args):
 p=subprocess.run(['git','-C',str(root),*args],capture_output=True,check=True)
 return p.stdout

def blob(root,revision,path):
 p=subprocess.run(['git','-C',str(root),'ls-tree',revision,'--',path],capture_output=True,check=True)
 if not p.stdout:return None
 mode,kind,oid=p.stdout.split(None,3)[:3]
 if kind!=b'blob' or mode not in (b'100644',b'100755'):raise ContextError('UNSUPPORTED_REPLACEMENT_ENTRY')
 raw=git(root,'cat-file','blob',oid.decode())
 return {'sha256':digest(raw),'mode':int(mode,8)&0o777,'data':base64.b64encode(raw).decode()}

def export(root,baseline,revision):
 before=git(root,'rev-parse',baseline).decode().strip();after=git(root,'rev-parse',revision).decode().strip()
 names=git(root,'diff','--no-renames','--name-only','-z',before,after).decode().split('\x00')
 entries=[]
 for name in filter(None,names):
  safe_path(name);entries.append({'path':name,'before':blob(root,before,name),'after':blob(root,after,name)})
 packet={'schema':'skills-ai/replacement/1','baseline':before,'revision':after,'entries':entries}
 validate(packet);return packet

def validate(packet):
 if not isinstance(packet,dict) or set(packet)!={'schema','baseline','revision','entries'} or packet['schema']!='skills-ai/replacement/1':raise ContextError('INVALID_REPLACEMENT_PACKET')
 if len(json.dumps(packet).encode())>MAX_PACKET_BYTES:raise ContextError('REPLACEMENT_TOO_LARGE')
 if not isinstance(packet['entries'],list) or len(packet['entries'])>512:raise ContextError('INVALID_REPLACEMENT_ENTRIES')
 seen=set()
 for entry in packet['entries']:
  if not isinstance(entry,dict) or set(entry)!={'path','before','after'}:raise ContextError('INVALID_REPLACEMENT_ENTRY')
  name=safe_path(entry['path'])
  if name in seen:raise ContextError('DUPLICATE_REPLACEMENT_PATH')
  seen.add(name)
  for side in ('before','after'):
   b=entry[side]
   if b is None:continue
   if not isinstance(b,dict) or set(b)!={'sha256','mode','data'} or type(b['mode']) is not int or b['mode'] not in (0o644,0o755):raise ContextError('INVALID_REPLACEMENT_BLOB')
   try:raw=base64.b64decode(b['data'],validate=True)
   except (ValueError,TypeError) as exc:raise ContextError('INVALID_REPLACEMENT_DATA') from exc
   if digest(raw)!=b['sha256']:raise ContextError('REPLACEMENT_DIGEST_MISMATCH')


def current(root,path):
 safe_path(path)
 # Every existing parent is checked before even recognizing a missing leaf.
 parent=root
 for part in path.split('/')[:-1]:
  parent=parent/part
  if parent.is_symlink() or (parent.exists() and not parent.is_dir()):raise ContextError('UNSAFE_REPLACEMENT_PARENT')
 target=root/path
 if not target.exists() and not target.is_symlink():return None
 raw=read_relative(root,path,maximum=MAX_PACKET_BYTES)
 return {'sha256':digest(raw),'mode':stat.S_IMODE(target.stat().st_mode)}

def preflight(root,packet,*,rollback=False):
 validate(packet);side='after' if rollback else 'before';conflicts=[]
 for entry in packet['entries']:
  got=current(root,entry['path']);want=entry[side]
  if (got is None)!=(want is None) or (got and (got['sha256']!=want['sha256'] or got['mode']!=want['mode'])):conflicts.append(entry['path'])
 if conflicts:raise ContextError('REPLACEMENT_CONTENT_CONFLICT:'+','.join(conflicts))
 return {'action':'rollback-preview' if rollback else 'replacement-preview','files':len(packet['entries']),'authority':'none','git_index':'untouched'}


def atomic_file(path,raw,mode):
 path.parent.mkdir(parents=True,exist_ok=True)
 fd,temp=tempfile.mkstemp(prefix='.'+path.name+'.',dir=path.parent)
 try:
  with os.fdopen(fd,'wb') as f:os.fchmod(f.fileno(),mode);f.write(raw);f.flush();os.fsync(f.fileno())
  os.replace(temp,path)
 finally:
  if os.path.exists(temp):os.unlink(temp)


def apply(root,packet,*,write=False,rollback=False,backup=None):
 preview=preflight(root,packet,rollback=rollback)
 if not write:return preview
 # The caller must independently establish host authorization and acceptance.
 if not rollback:
  if backup is None or backup.exists() or backup.is_symlink():raise ContextError('NEW_ROLLBACK_FILE_REQUIRED')
  atomic_file(backup,(json.dumps(packet,sort_keys=True)+'\n').encode(),0o600)
 source='after' if rollback else 'before';target='before' if rollback else 'after';completed=[]
 try:
  for entry in packet['entries']:
   # Recheck immediately before replacing; concurrent host writes remain unsupported.
   preflight(root,packet|{'entries':[entry]},rollback=rollback)
   path=root/entry['path'];value=entry[target]
   if value is None:path.unlink()
   else:atomic_file(path,base64.b64decode(value['data']),value['mode'])
   completed.append(entry)
 except Exception:
  # Restore only our completed writes, and only if nobody subsequently changed them.
  for entry in reversed(completed):
   got=current(root,entry['path']);value=entry[target]
   if (got is None)!=(value is None) or (got and got['sha256']!=value['sha256']):raise ContextError('INTERRUPTED_REPLACEMENT_REQUIRES_RECOVERY')
   original=entry[source];path=root/entry['path']
   if original is None:path.unlink()
   else:atomic_file(path,base64.b64decode(original['data']),original['mode'])
  raise
 return preview|{'action':'rolled-back' if rollback else 'replaced','rollback_packet':str(backup) if backup else None}


def recover(root,packet,*,write=False):
    """Recover a process-killed partial apply; preserve any third-party edits."""
    validate(packet);remaining=[]
    for entry in packet['entries']:
        got=current(root,entry['path'])
        def matches(value):
            return (got is None and value is None) or (got is not None and value is not None and got['sha256']==value['sha256'] and got['mode']==value['mode'])
        if matches(entry['before']):continue
        if matches(entry['after']):remaining.append(entry)
        else:raise ContextError('RECOVERY_CONTENT_CONFLICT:'+entry['path'])
    if not write:return {'action':'recovery-preview','files':len(remaining),'authority':'none'}
    if not remaining:return {'action':'already-restored','files':0,'authority':'none'}
    return apply(root,packet|{'entries':remaining},rollback=True,write=True)


def main():
 p=argparse.ArgumentParser(description=__doc__);s=p.add_subparsers(dest='action',required=True)
 e=s.add_parser('export');e.add_argument('--root',type=Path,required=True);e.add_argument('--baseline',required=True);e.add_argument('--revision',default='HEAD');e.add_argument('--output',type=Path,required=True)
 for action in ('apply','rollback','recover'):
  a=s.add_parser(action);a.add_argument('--root',type=Path,required=True);a.add_argument('--packet',type=Path,required=True);a.add_argument('--write',action='store_true');a.add_argument('--backup',type=Path)
 args=p.parse_args()
 try:
  if not args.root.is_absolute():raise ContextError('ABSOLUTE_ROOT_REQUIRED')
  if args.action=='export':
   if args.output.exists() or args.output.is_symlink():raise ContextError('NEW_PACKET_FILE_REQUIRED')
   packet=export(args.root,args.baseline,args.revision);atomic_file(args.output,(json.dumps(packet,sort_keys=True)+'\n').encode(),0o600);out={'action':'exported','files':len(packet['entries']),'authority':'none'}
  else:
   if args.packet.stat().st_size>MAX_PACKET_BYTES:raise ContextError('REPLACEMENT_TOO_LARGE')
   packet=json.loads(args.packet.read_bytes())
   out=recover(args.root,packet,write=args.write) if args.action=='recover' else apply(args.root,packet,write=args.write,rollback=args.action=='rollback',backup=args.backup)
  print(json.dumps(out));return 0
 except (ContextError,OSError,ValueError,subprocess.CalledProcessError) as exc:
  print(json.dumps({'action':'blocked','reason':str(exc),'authority':'none'}));return 2
if __name__=='__main__':raise SystemExit(main())
