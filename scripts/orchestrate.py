#!/usr/bin/env python3
"""Read-only metadata discovery and explicit loading; host owns all decisions."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'runtime'))
from registry_runtime import load_manifest, RegistryRuntimeError
from model_context import ContextError, discover, load_capability, load_capabilities, load_reference, context_packet, compact_catalog, acknowledge_context, status_packet

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='action',required=True)
    sub.add_parser('measure')
    s=sub.add_parser('status');s.add_argument('--project-root',type=Path);s.add_argument('--session')
    c=sub.add_parser('context');c.add_argument('--project-root',type=Path);c.add_argument('--session');c.add_argument('--delivery',choices=('bootstrap','continuation'),default='bootstrap');c.add_argument('--format',choices=('text','json'),default='text')
    c.add_argument('--defer-marker',action='store_true')
    a=sub.add_parser('ack-context');a.add_argument('--session',required=True);a.add_argument('--revision',required=True)
    d=sub.add_parser('discover');d.add_argument('--offset',type=int,default=0);d.add_argument('--limit',type=int,default=8)
    d.add_argument('--package');d.add_argument('--source-hash');d.add_argument('--metadata-hash');d.add_argument('--format',choices=('text','json'),default='json')
    l=sub.add_parser('load');l.add_argument('--capability',required=True,action='append');l.add_argument('--explicit',action='store_true');l.add_argument('--explicit-capability',action='append',default=[]);l.add_argument('--expected-sha256');l.add_argument('--if-changed')
    l.add_argument('--deduplicate',action='store_true',help='Batch v2: deliver shared entry bodies once; preserve per-capability metadata')
    r=sub.add_parser('read-reference');r.add_argument('--capability',required=True);r.add_argument('--reference',required=True);r.add_argument('--explicit',action='store_true')
    i=sub.add_parser('inspect-checkpoint');i.add_argument('--project',type=Path,required=True);i.add_argument('--state',required=True)
    w=sub.add_parser('save-checkpoint');w.add_argument('--project',type=Path,required=True);w.add_argument('--state',required=True);w.add_argument('--write',action='store_true')
    args=parser.parse_args(argv)
    try:
        if args.action=='measure':
            sys.path.insert(0,str(ROOT/'scripts'))
            from measure_context import main as measure_main
            return measure_main([])
        if args.action=='ack-context':
            if len(args.revision)>1024:raise ContextError('INVALID_DELIVERY_REVISION')
            from model_context import _unique_object
            out=acknowledge_context(ROOT,args.session,json.loads(args.revision,object_pairs_hook=_unique_object))
            print(json.dumps(out,separators=(',',':')));return 0
        if args.action in ('inspect-checkpoint','save-checkpoint'):
            from model_context import read_json
            from orchestration_state import inspect_state, save_state, MAX_STATE_BYTES
            if not args.project.is_absolute():raise ContextError('ABSOLUTE_PROJECT_REQUIRED')
            if args.action=='inspect-checkpoint':out=inspect_state(ROOT,args.project,read_json(args.project,args.state,maximum=MAX_STATE_BYTES))
            else:
                raw=sys.stdin.buffer.read(MAX_STATE_BYTES+1)
                if len(raw)>MAX_STATE_BYTES:raise ContextError('CHECKPOINT_TOO_LARGE')
                from model_context import _unique_object
                out=save_state(args.project,args.state,json.loads(raw,object_pairs_hook=_unique_object),write=args.write)
            print(json.dumps(out,separators=(',',':')));return 0
        manifest=load_manifest()
        if args.action=='status':
            print(json.dumps(status_packet(ROOT,manifest,project_root=args.project_root,session=args.session),ensure_ascii=False,separators=(',',':')));return 0
        if args.action=='context':
            out=context_packet(ROOT,manifest,project_root=args.project_root,session=args.session,delivery=args.delivery,defer_marker=args.defer_marker)
            print(out['additional_context'] if args.format=='text' else json.dumps(out,ensure_ascii=False,separators=(',',':')));return 0
        if args.action=='discover':out=discover(ROOT,manifest,offset=args.offset,limit=args.limit,package=args.package,source_hash=args.source_hash,metadata_hash=args.metadata_hash)
        elif args.action=='read-reference':out=load_reference(ROOT,manifest,args.capability,args.reference,explicit=args.explicit)
        else:
            explicit=set(args.capability if args.explicit else args.explicit_capability)
            if explicit-set(args.capability):raise ContextError('INVALID_EXPLICIT_SET')
            if len(args.capability)==1:
                if args.deduplicate:raise ContextError('BATCH_REQUIRED_FOR_DEDUPLICATION')
                out=load_capability(ROOT,manifest,args.capability[0],explicit=args.capability[0] in explicit,expected_sha256=args.expected_sha256,if_changed=args.if_changed)
            else:
                if args.expected_sha256 or args.if_changed:raise ContextError('SINGLE_CAPABILITY_REQUIRED')
                out=load_capabilities(ROOT,manifest,args.capability,explicit_capabilities=explicit,deduplicate=args.deduplicate)
        if args.action=='discover' and args.format=='text':print(compact_catalog(out),end='')
        else:print(json.dumps(out,ensure_ascii=False,separators=(',',':')))
        return 0
    except (ContextError,RegistryRuntimeError,OSError,ValueError) as exc:
        reason=str(exc) if isinstance(exc,(ContextError,RegistryRuntimeError)) else type(exc).__name__
        print(json.dumps({'schema':'skills-ai/error/1','reason':reason,'authority':'none'}))
        return 2
if __name__=='__main__':raise SystemExit(main())
