#!/usr/bin/env python3
"""Measure context delivery in a disposable fixture; never judge model decisions."""
import argparse
import json
import math
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from registry_runtime import ROOT, load_manifest
from model_context import context_packet, compact_catalog, core_text, discover, STARTUP_CATALOG_BYTES

# Delivery regression budgets, distinct from transport/security hard bounds.
CORE_BUDGET = 5632
BOOTSTRAP_BUDGET = 8192


def budgeted_bootstrap_bytes(context, root):
    """Bootstrap bytes without the checkout path, which differs per clone and repair workspace."""
    return len(context.encode())-len(json.dumps(str(Path(root).resolve())).encode())


def measure(*, repeat=3):
    manifest=load_manifest();raw=(ROOT/'runtime/skills-orchestrator/SKILL.md').read_bytes()
    initial=context_packet(ROOT,manifest)
    catalog=compact_catalog(discover(ROOT,manifest,limit=32),maximum=STARTUP_CATALOG_BYTES)
    latencies=[]
    for _ in range(repeat):
        started=time.perf_counter()
        run=subprocess.run([sys.executable,'-B',str(ROOT/'scripts/orchestrate.py'),'context','--format','json'],capture_output=True,text=True,timeout=4)
        latencies.append((time.perf_counter()-started)*1000)
        if run.returncode:raise ValueError('context process failed')
        if json.loads(run.stdout)['additional_context']!=initial['additional_context']:raise ValueError('context process differed')
    with tempfile.TemporaryDirectory(prefix='skills-ai-measure-') as directory:
        root=Path(directory);(root/'runtime/skills-orchestrator').mkdir(parents=True)
        (root/'runtime/skills-orchestrator/SKILL.md').write_bytes(raw)
        shutil.copy(ROOT/'runtime/repair_workspace.py',root/'runtime/repair_workspace.py')
        if (ROOT/'registry/contracts').exists():shutil.copytree(ROOT/'registry/contracts',root/'registry/contracts')
        context_packet(root,manifest,session='measure-fixture')
        unchanged=context_packet(root,manifest,session='measure-fixture',delivery='continuation')
        (root/'runtime/skills-orchestrator/SKILL.md').write_bytes(raw+b'\nChanged measurement fixture.\n')
        changed=context_packet(root,manifest,session='measure-fixture',delivery='continuation')
    sizes={'core':len(core_text(raw.decode()).encode()),'catalog':len(catalog.encode()),'bootstrap':budgeted_bootstrap_bytes(initial['additional_context'],ROOT),
           'unchanged_continuation':len(unchanged['additional_context'].encode()),'changed_core':len(changed['additional_context'].encode()),
           'root_path_excluded':len(json.dumps(str(ROOT.resolve())).encode())}
    failures=[]
    if sizes['core']>CORE_BUDGET:failures.append('core exceeds 5.5 KiB delivery budget')
    if sizes['bootstrap']>BOOTSTRAP_BUDGET:failures.append('bootstrap exceeds 8 KiB delivery budget')
    if sizes['catalog']>8192 or sizes['bootstrap']>65536:failures.append('context hard bounds exceeded')
    if sizes['unchanged_continuation']!=0:failures.append('unchanged continuation repeated context')
    if changed['changed']!=['core']:failures.append('changed core repeated other sections')
    return {'schema':'skills-ai/measure/1','bytes':sizes,
            'budgets':{'core':CORE_BUDGET,'bootstrap':BOOTSTRAP_BUDGET},
            'estimated_bootstrap_tokens':math.ceil(sizes['bootstrap']/4),
            'token_measurement':'bytes/4 estimate, not tokenizer output or total task savings',
            'process_latency_ms':{'median':round(statistics.median(latencies),3),'maximum':round(max(latencies),3)},
            'failures':failures,'candidate_bodies_loaded':0,'semantic_acceptance':'not-measured','repeat':repeat,'authority':'none'}


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repeat',type=int,default=3);parser.add_argument('--json',action='store_true')
    args=parser.parse_args(argv)
    if not 1<=args.repeat<=20:parser.error('repeat must be 1..20')
    result=measure(repeat=args.repeat);print(json.dumps(result,indent=2,sort_keys=True));return bool(result['failures'])

if __name__=='__main__':raise SystemExit(main())
