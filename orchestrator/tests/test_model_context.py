"""Checks of instruction delivery and evaluation artifacts, not semantic certification."""
import json
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
class SpecificationTests(unittest.TestCase):
 def test_case_set_is_unique_and_covers_boundary_scenarios(self):
  data=json.loads((ROOT/'orchestrator/tests/model_orchestration_cases.json').read_text())
  cases=data['cases'];self.assertEqual(83,len(cases));self.assertEqual(83,len({c['id'] for c in cases}))
  self.assertTrue({'use-none','use-multiple','use-conflict','mode-conflict','receipt-new','receipt-native-partial','receipt-resume'} <= {c['id'] for c in cases})
  for c in cases:
   self.assertTrue(c['request']);self.assertTrue(c['rubric']);self.assertEqual(['codex','claude'],c['hosts'])
 def test_contract_schema_does_not_grant_activation_or_authority(self):
  schema=json.loads((ROOT/'orchestrator/runtime/skill-contract.schema.json').read_text())
  self.assertFalse(schema['additionalProperties'])
  self.assertNotIn('activation',schema['properties']['package']['properties'])
  self.assertNotIn('permission_grants',schema['properties'])
 def test_entry_is_compact_and_detailed_modules_are_on_demand(self):
  entry=(ROOT/'orchestrator/runtime/SKILL.md').read_text()
  self.assertLess(len(entry.encode()),2900)
  self.assertIn('No local router selects',entry)
  self.assertIn('only when required',entry)

import copy
import hashlib
import importlib.util
import os
import sys
import tempfile
from unittest.mock import patch
sys.path.insert(0,str(ROOT/'orchestrator'/'runtime'))
sys.path.insert(0,str(ROOT/'orchestrator'/'tools'))
from model_context import ContextError, discover, load_capability, read_relative, check_contract
from model_context import context_packet, core_text
from registry_runtime import build_manifest

class ExplicitAccessTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
  (self.root/'entries').mkdir();(self.root/'entries/a.md').write_text('A complete instruction body')
  self.manifest={'source_hash':'a'*64,'packages':{'a':{'state':'active'}},'routes':[{'package':'a','id':'a','path':'entries/a.md','description':'purpose','state':'active'}],'command_aliases':[]}
 def test_discovery_never_reads_capability_bodies(self):
  with patch('model_context.read_relative',side_effect=AssertionError('body read')):
   out=discover(self.root,self.manifest)
  self.assertEqual('a',out['items'][0]['capability']);self.assertNotIn('body',out['items'][0])
 def test_load_reads_exact_complete_body_and_identity(self):
  out=load_capability(self.root,self.manifest,'a')
  self.assertEqual('A complete instruction body',out['body'])
  self.assertEqual(hashlib.sha256(out['body'].encode()).hexdigest(),out['sha256'])
  with self.assertRaisesRegex(ContextError,'CONTENT_CHANGED'):load_capability(self.root,self.manifest,'a',expected_sha256='b'*64)
 def test_disabled_and_manual_require_exact_access(self):
  for state in ('off','hidden','deprecated','manual'):
   self.manifest['packages']['a']['state']=state
   with self.assertRaises(ContextError):load_capability(self.root,self.manifest,'a')
  self.assertEqual('none',load_capability(self.root,self.manifest,'a',explicit=True)['authority'])
  self.manifest['packages']['a']['state']='off'
  with self.assertRaisesRegex(ContextError,'DISABLED'):load_capability(self.root,self.manifest,'a',explicit=True)
 def test_unknown_does_not_substitute(self):
  with self.assertRaisesRegex(ContextError,'UNKNOWN'):load_capability(self.root,self.manifest,'imagined')
 def test_pagination_covers_large_catalog_without_rankings(self):
  for i in range(50):
   k=f'package-{i:03d}';self.manifest['packages'][k]={'state':'active'}
   self.manifest['routes'].append({'package':k,'id':k,'path':'entries/a.md','description':'purpose','state':'active'})
  found=[];offset=0
  while True:
   page=discover(self.root,self.manifest,offset=offset,limit=3,source_hash='a'*64)
   self.assertLessEqual(len(json.dumps(page,separators=(',',':')).encode()),12288)
   found.extend(i['capability'] for i in page['items']);offset=page['next_offset']
   if offset is None:break
  self.assertEqual(51,len(found));self.assertEqual(51,len(set(found)))
  with self.assertRaisesRegex(ContextError,'STALE'):discover(self.root,self.manifest,source_hash='b'*64)
 def test_traversal_symlink_directory_fifo_and_oversize_are_rejected(self):
  for path in ('/etc/passwd','../outside','entries/../a.md','entries//a.md'):
   with self.assertRaises(ContextError):read_relative(self.root,path)
  (self.root/'link').symlink_to(self.root/'entries',target_is_directory=True)
  (self.root/'entries/link.md').symlink_to(self.root/'entries/a.md')
  for path in ('link/a.md','entries/link.md','entries'):
   with self.assertRaises(ContextError):read_relative(self.root,path)
  os.mkfifo(self.root/'fifo')
  with self.assertRaisesRegex(ContextError,'NOT_REGULAR'):read_relative(self.root,'fifo')
  with self.assertRaisesRegex(ContextError,'FILE_TOO_LARGE'):read_relative(self.root,'entries/a.md',maximum=2)
 def test_compiled_live_metadata_has_no_body(self):
  out=discover(ROOT,build_manifest(ROOT))
  self.assertGreater(out['total'],0);self.assertNotIn('body',json.dumps(out))

class ContractShapeTests(unittest.TestCase):
 def contract(self):
  return {'schema':'skills-ai/package/1','package':{'id':'synthetic','version':'1.0.0','purpose':'Synthetic capability'},'capabilities':[{'id':'synthetic.run','entry':'entry.md','purpose':'Test','roles':['primary'],'dependencies':[]}],'rules':[],'verification':{'checks':[]}}
 def test_valid_synthetic_contract_and_invalid_required_shape(self):
  value=self.contract();check_contract(value,expected_id='synthetic')
  for mutate in (lambda c:c.update({'activation':'active'}),lambda c:c['package'].update({'id':'other'}),lambda c:c['capabilities'][0].update({'roles':['invented']}),lambda c:c['capabilities'][0].update({'entry':'../outside'}),lambda c:c['capabilities'].append(copy.deepcopy(c['capabilities'][0]))):
   c=copy.deepcopy(value);mutate(c)
   with self.assertRaises(ContextError):check_contract(c,expected_id='synthetic')
 def test_malformed_contract_fails_without_silent_entry_fallback(self):
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory);(root/'orchestrator/registry/contracts').mkdir(parents=True)
   (root/'orchestrator/registry/contracts/synthetic.json').write_text('{"schema":"bad"}')
   manifest={'packages':{'synthetic':{'state':'active'}},'routes':[],'source_hash':'a'*64}
   with self.assertRaises(ContextError):discover(root,manifest)

import subprocess
class DeliveryTests(unittest.TestCase):
 def test_simple_control_requests_receive_complete_shared_core_without_prompt_echo(self):
  core=core_text((ROOT/'orchestrator/runtime/skills-orchestrator/SKILL.md').read_text())
  for control in ('#> use none\n#> mode adaptive','#> use optimizer, theory-reference\n#> mode strict'):
   prompt=control+'\nReview private-fixture-489; do not execute the task.'
   result=subprocess.run(['node',str(ROOT/'orchestrator/adapters/claude/skills-ai-context.js'),'--root',str(ROOT)],input=json.dumps({'prompt':prompt,'cwd':str(ROOT)}),capture_output=True,text=True,timeout=4)
   self.assertEqual(0,result.returncode,result.stderr)
   context=json.loads(result.stdout)['hookSpecificOutput']['additionalContext']
   self.assertIn(core,context)
   self.assertNotIn('private-fixture-489',result.stdout+result.stderr)
   self.assertNotIn('## Resolve first',context)
 def test_claude_pilot_injects_core_and_metadata_without_candidate_bodies(self):
  result=subprocess.run(['node',str(ROOT/'orchestrator/adapters/claude/skills-ai-context.js'),'--root',str(ROOT),'--model-led'],input=json.dumps({'prompt':'#> optimizer status','cwd':str(ROOT)}),capture_output=True,text=True,timeout=4)
  self.assertEqual(0,result.returncode,result.stderr)
  context=json.loads(result.stdout)['hookSpecificOutput']['additionalContext']
  self.assertIn('model-led orchestration',context)
  self.assertNotIn('## Resolve first',context);self.assertNotIn('Selected local package:',context)
 def test_discovery_and_load_cli_are_exact_and_prompt_free(self):
  result=subprocess.run([sys.executable,'-B',str(ROOT/'orchestrator/tools/orchestrate.py'),'discover','--limit','1'],capture_output=True,text=True,timeout=3)
  self.assertEqual(0,result.returncode);self.assertEqual(1,len(json.loads(result.stdout)['items']))
  result=subprocess.run([sys.executable,'-B',str(ROOT/'orchestrator/tools/orchestrate.py'),'load','--capability','optimizer'],capture_output=True,text=True,timeout=3)
  self.assertEqual(2,result.returncode);self.assertEqual('EXPLICIT_INVOCATION_REQUIRED',json.loads(result.stdout)['reason'])

from model_context import load_reference, inspect_dependency_integrity
class SyntheticCompositionTests(unittest.TestCase):
 def test_explicit_primary_support_and_handoff_do_not_auto_load(self):
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory);(root/'orchestrator/registry/contracts').mkdir(parents=True);(root/'synthetic').mkdir()
   (root/'synthetic/producer.md').write_text('Produce a source ledger; do not edit theory output.')
   (root/'synthetic/consumer.md').write_text('Consume the ledger; own the explanation.')
   (root/'synthetic/notation.md').write_text('Preserve symbol x and fixed assumptions.')
   contract={'schema':'skills-ai/package/1','package':{'id':'synthetic','version':'1.0.0','purpose':'Synthetic composition'},
    'capabilities':[{'id':'producer','entry':'synthetic/producer.md','purpose':'Evidence producer','roles':['primary','reviewer'],'dependencies':[]},
                    {'id':'consumer','entry':'synthetic/consumer.md','purpose':'Theory consumer','roles':['primary'],'dependencies':[{'kind':'reference','target':'synthetic/notation.md'}],'inputs':['source ledger'],'outputs':['explanation']}],
    'rules':[],'verification':{'checks':['source ledger review']}}
   (root/'orchestrator/registry/contracts/synthetic.json').write_text(json.dumps(contract))
   manifest={'source_hash':'a'*64,'packages':{'synthetic':{'state':'active'}},'routes':[],'command_aliases':[]}
   first=load_capability(root,manifest,'producer');second=load_capability(root,manifest,'consumer')
   self.assertNotIn('fixed assumptions',first['body']+second['body'])
   support=load_reference(root,manifest,'consumer','synthetic/notation.md')
   self.assertIn('fixed assumptions',support['body'])
   self.assertEqual(2,len(second['bindings']))
   with self.assertRaisesRegex(ContextError,'UNDECLARED'):load_reference(root,manifest,'consumer','synthetic/producer.md')
 def test_cycle_unknown_dependency_and_reference_links(self):
  records=[{'capability':'a','dependencies':[{'kind':'capability','target':'b'}]}, {'capability':'b','dependencies':[]}]
  self.assertEqual('host-owned',inspect_dependency_integrity(records)['selection'])
  records[1]['dependencies']=[{'kind':'capability','target':'a'}]
  with self.assertRaisesRegex(ContextError,'CYCLE'):inspect_dependency_integrity(records)
  records[1]['dependencies']=[{'kind':'reference','target':'a'}]
  self.assertEqual('acyclic',inspect_dependency_integrity(records)['required_execution_graph'])
  records[0]['dependencies'][0]['target']='invented'
  with self.assertRaisesRegex(ContextError,'UNKNOWN'):inspect_dependency_integrity(records)

class MetadataMigrationTests(unittest.TestCase):
 def test_alias_metadata_is_delivered_without_local_decisions(self):
  manifest=build_manifest(ROOT)
  page=discover(ROOT,manifest)
  aliases={a['command']:(a['package'],a['mode']) for a in page['aliases']}
  self.assertEqual(('optimizer','build-system'),aliases['#> build-system'])
  self.assertEqual(('markdown-protocol','check'),aliases['#> md_check'])
  self.assertEqual(('markdown-protocol','deepen'),aliases['#> md_deepen'])
  self.assertEqual(('markdown-protocol','guided'),aliases['#> md_protocol'])
  self.assertEqual(('project-manager','route'),aliases['#> memory'])
  self.assertEqual(('project-manager','handoff'),aliases['#> handoff'])
  self.assertEqual(('project-manager','resume'),aliases['#> resume'])
  self.assertEqual(('project-manager','feedback'),aliases['#> feedback'])
  self.assertEqual(('research-context-scout','deepen'),aliases['#> scout-again'])
 def test_state_gate_is_capability_specific(self):
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory);(root/'orchestrator/registry/contracts').mkdir(parents=True)
   value=ContractShapeTests().contract();value['capabilities'][0]['id']='a'
   second=copy.deepcopy(value['capabilities'][0]);second['id']='b';value['capabilities'].append(second)
   (root/'orchestrator/registry/contracts/synthetic.json').write_text(json.dumps(value))
   manifest={'source_hash':'a'*64,'packages':{'synthetic':{'state':'active'}},'routes':[{'package':'synthetic','id':'a','state':'off'},{'package':'synthetic','id':'b','state':'active'}]}
   states={i['capability']:i['state'] for i in discover(root,manifest)['items']}
   self.assertEqual({'a':'off','b':'active'},states)
 def test_installed_codex_entry_binds_actual_checkout_from_another_project(self):
  from install_runtime_adapter import install_adapter
  with tempfile.TemporaryDirectory() as directory:
   target=Path(directory);install_adapter('codex',target)
   entry=(target/'skills/skills-ai-registry/SKILL.md').read_text()
   self.assertIn(str(ROOT),entry);self.assertNotIn('{{SKILLS_AI_ROOT}}',entry)

class ManifestBoundaryTests(unittest.TestCase):
 def test_malformed_duplicate_oversized_and_symlink_manifests_fail_closed_to_metadata(self):
  from registry_runtime import load_manifest,RegistryRuntimeError
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory);path=root/'manifest.json'
   for text in ('[]','{"schema_version":1,"schema_version":1}','{}','x'*1048577):
    path.write_text(text)
    with self.assertRaises(RegistryRuntimeError):load_manifest(path)
   path.unlink();outside=root/'outside.json';outside.write_text(json.dumps(build_manifest(ROOT)));path.symlink_to(outside)
   with self.assertRaises(RegistryRuntimeError):load_manifest(path)
 def test_claude_delivery_binds_source_root_and_still_omits_query(self):
  result=subprocess.run(['node',str(ROOT/'orchestrator/adapters/claude/skills-ai-context.js'),'--root',str(ROOT)],input=json.dumps({'prompt':'private-marker-root-test','cwd':'/private/tmp'}),capture_output=True,text=True,timeout=4)
  context=json.loads(result.stdout)['hookSpecificOutput']['additionalContext']
  self.assertIn('Skills AI repository tools root:',context);self.assertIn(str(ROOT),context);self.assertNotIn('private-marker-root-test',context)

class ContextDeliveryTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
  (self.root/'orchestrator/runtime/skills-orchestrator').mkdir(parents=True)
  (self.root/'orchestrator/runtime/skills-orchestrator/SKILL.md').write_text('---\nname: fixture\n---\nComplete core instructions')
  import shutil
  shutil.copy(ROOT/'orchestrator/runtime/repair_workspace.py',self.root/'orchestrator/runtime/repair_workspace.py')
  self.manifest={'source_hash':'a'*64,'packages':{},'routes':[],'command_aliases':[]}
 def packet(self,**kw):
  return context_packet(self.root,self.manifest,session='fixture-session',**kw)
 def test_continuation_and_bootstrap(self):
  self.assertIn('Complete core instructions',self.packet(delivery='continuation')['additional_context'])
  self.assertEqual('',self.packet(delivery='continuation')['additional_context'])
  self.assertIn('Complete core instructions',self.packet(delivery='bootstrap')['additional_context'])
 def test_changed_core_only(self):
  self.packet();(self.root/'orchestrator/runtime/skills-orchestrator/SKILL.md').write_text('Changed complete instructions')
  out=self.packet(delivery='continuation');self.assertEqual(['core'],out['changed']);self.assertNotIn('catalog',out['additional_context'])
 def test_changed_catalog_only(self):
  self.packet();self.manifest['command_aliases']=[{'command':'#> named','skill_id':'absent','mode':'new'}]
  out=self.packet(delivery='continuation');self.assertEqual(['catalog'],out['changed']);self.assertNotIn('Complete core',out['additional_context'])
 def test_large_catalog_startup_is_bounded_with_explicit_expansion(self):
  from model_context import STARTUP_CATALOG_BYTES
  for i in range(50):
   name=f'package-{i:03}';self.manifest['packages'][name]={'state':'active'}
   self.manifest['routes'].append({'package':name,'id':name,'path':'entry.md','description':'Meaningful purpose '*8,'state':'active'})
  out=self.packet();text=out['additional_context'];catalog=json.loads(text.split('permission:\n',1)[1])['catalog']
  self.assertLessEqual(len(catalog.encode()),STARTUP_CATALOG_BYTES)
  self.assertIn('of 50 capabilities',catalog);self.assertIn('discover --offset',catalog)
  self.assertFalse((self.root/'entry.md').exists())
 def test_invalid_marker_and_hash_only_private_storage(self):
  self.packet();marker=next((self.root/'.runtime/context-delivery').glob('*.json'))
  data=json.loads(marker.read_text());self.assertEqual({'core','catalog','project','repair'},set(data))
  self.assertTrue(all(len(v)==64 for v in data.values()));self.assertEqual(0o600,marker.stat().st_mode&0o777)
  marker.write_text('not JSON');self.assertTrue(self.packet(delivery='continuation')['additional_context'])
 def test_sessionless_read_and_invalid_session(self):
  context_packet(self.root,self.manifest);self.assertFalse((self.root/'.runtime').exists())
  with self.assertRaises(ContextError):context_packet(self.root,self.manifest,session='../outside')
 def test_symlink_state_is_rejected(self):
  (self.root/'.runtime').symlink_to(self.root/'runtime',target_is_directory=True)
  with self.assertRaises(OSError):self.packet()

class NativeHookDeliveryTests(unittest.TestCase):
 def test_all_session_events_and_unchanged_continuation(self):
  import shutil
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory);(root/'orchestrator/runtime').mkdir(parents=True);(root/'orchestrator/tools').mkdir(parents=True)
   shutil.copytree(ROOT/'orchestrator'/'runtime',root/'orchestrator/runtime',dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__'))
   for name in ('orchestrate.py','registry_runtime.py'):shutil.copy(ROOT/'orchestrator'/'tools'/name,root/'orchestrator/tools'/name)
   for source in build_manifest(ROOT)['sources']:
    target=root/source['path'];target.parent.mkdir(parents=True,exist_ok=True);shutil.copy(ROOT/source['path'],target)
   hook=ROOT/'orchestrator/adapters/claude/skills-ai-context.js'
   def run(event,source=None):
    payload={'hook_event_name':event,'session_id':'native-fixture','prompt':'private-fixture-never-forwarded'}
    if source:payload['source']=source
    return subprocess.run(['node',str(hook),'--root',str(root)],input=json.dumps(payload),text=True,capture_output=True,timeout=4)
   for source in ('startup','resume','clear','compact','fork'):
    result=run('SessionStart',source);self.assertEqual(0,result.returncode);out=json.loads(result.stdout)
    self.assertEqual('SessionStart',out['hookSpecificOutput']['hookEventName']);self.assertNotIn('private-fixture',result.stdout)
    self.assertEqual('',run('UserPromptSubmit').stdout)

class MetadataEfficiencyTests(unittest.TestCase):
 setUp = ExplicitAccessTests.setUp
 def test_compact_metadata_preserves_ids_alias_modes_and_overflow(self):
  from model_context import compact_catalog
  self.manifest['command_aliases']=[{'command':'#> a','skill_id':'a','mode':'review'}]
  self.manifest['routes'][0]['description']='Useful purpose '*30
  text=compact_catalog(discover(self.root,self.manifest))
  self.assertIn('"mode":"review"',text);self.assertIn('purpose_shortened',text);self.assertIn('--format json',text)
  self.assertLess(len(text.encode()),8192)
 def test_contract_change_invalidates_metadata_even_with_same_manifest(self):
  from model_context import capability_records
  (self.root/'orchestrator/registry/contracts').mkdir(parents=True)
  c=ContractShapeTests().contract();c['package']['id']='a';c['capabilities'][0].update(id='a',entry='entries/a.md')
  path=self.root/'orchestrator/registry/contracts/a.json';path.write_text(json.dumps(c))
  old=discover(self.root,self.manifest)
  c['verification']['checks']=['new check'];path.write_text(json.dumps(c))
  with self.assertRaisesRegex(ContextError,'STALE_METADATA'):discover(self.root,self.manifest,metadata_hash=old['metadata_hash'])
  self.assertNotEqual(old['metadata_hash'],discover(self.root,self.manifest)['metadata_hash'])
 def test_component_gate_and_unmapped_contract_family_gate(self):
  from model_context import capability_records
  (self.root/'orchestrator/registry/contracts').mkdir(parents=True)
  c=ContractShapeTests().contract();c['package']['id']='a';c['capabilities'][0].update(id='a.new',entry='entries/a.md')
  (self.root/'orchestrator/registry/contracts/a.json').write_text(json.dumps(c))
  self.manifest['components']={'a.new':{'state':'manual'}}
  self.assertEqual('manual',capability_records(self.root,self.manifest)[0]['state'])
  self.manifest['families']={'a':{'package':'a','state':'off'}}
  with self.assertRaisesRegex(ContextError,'DISABLED'):load_capability(self.root,self.manifest,'a.new',explicit=True)
 def test_interaction_capabilities_are_discoverable_with_real_component_states(self):
  page=discover(ROOT,build_manifest(ROOT),limit=32)
  self.assertEqual('project-manager',page['items'][0]['capability'])
  records={r['capability']:r for r in page['items']}
  self.assertEqual('interaction',records['interaction.math']['package_role'])
  self.assertEqual('supporting',records['project-manager']['package_role'])
  loaded=load_capability(ROOT,build_manifest(ROOT),'interaction.math',explicit=True)
  self.assertIn('"response_contract"',loaded['body']);self.assertIn('"math"',loaded['body'])
  project=load_capability(ROOT,build_manifest(ROOT),'project-manager')
  self.assertIn('private model memory',project['body'])

class EfficientLoadingTests(unittest.TestCase):
 setUp = ExplicitAccessTests.setUp
 def test_batch_has_complete_entries_and_no_dependency_loading(self):
  from model_context import load_capabilities
  self.manifest['routes'].append({'package':'a','id':'b','path':'entries/a.md','description':'Second purpose','state':'active'})
  out=load_capabilities(self.root,self.manifest,['a','b'])
  self.assertEqual(['a','b'],[i['capability']['capability'] for i in out['items']])
  self.assertTrue(all(i['body']=='A complete instruction body' for i in out['items']))
  self.assertEqual('host-owned',out['selection'])
 def test_batch_checks_every_access_gate_before_reading_bodies(self):
  from model_context import load_capabilities
  self.manifest['routes'].append({'package':'a','id':'b','path':'entries/a.md','description':'Manual support','state':'manual'})
  with patch('model_context.read_relative',side_effect=AssertionError('entry read')):
   with self.assertRaisesRegex(ContextError,'EXPLICIT'):load_capabilities(self.root,self.manifest,['a','b'])
   with self.assertRaisesRegex(ContextError,'UNKNOWN'):load_capabilities(self.root,self.manifest,['a','missing'])
  out=load_capabilities(self.root,self.manifest,['a','b'],explicit_capabilities=['b'])
  self.assertFalse(out['items'][0]['explicit_invocation_attested']);self.assertTrue(out['items'][1]['explicit_invocation_attested'])
  for selection in ([],['a','a']):
   with self.assertRaisesRegex(ContextError,'INVALID_CAPABILITY_SET'):load_capabilities(self.root,self.manifest,selection)
 def test_if_changed_identity_covers_contract_and_body_but_still_checks_access(self):
  from model_context import load_capability
  contract=ContractShapeTests().contract();contract['package']['id']='a'
  contract['capabilities'][0].update(id='a',entry='entries/a.md')
  (self.root/'orchestrator/registry/contracts').mkdir(parents=True);path=self.root/'orchestrator/registry/contracts/a.json';path.write_text(json.dumps(contract))
  first=load_capability(self.root,self.manifest,'a');identity=first['identity']
  same=load_capability(self.root,self.manifest,'a',if_changed=identity)
  self.assertEqual('unchanged',same['status']);self.assertNotIn('body',same)
  contract['verification']['checks']=['New required validation'];path.write_text(json.dumps(contract))
  new=load_capability(self.root,self.manifest,'a',if_changed=identity)
  self.assertEqual(first['sha256'],new['sha256']);self.assertNotEqual(identity,new['identity']);self.assertIn('body',new)
  (self.root/'entries/a.md').write_text('Changed complete instructions')
  self.assertEqual('loaded',load_capability(self.root,self.manifest,'a',if_changed=new['identity'])['status'])
  self.manifest['packages']['a']['state']='off'
  with self.assertRaisesRegex(ContextError,'DISABLED'):load_capability(self.root,self.manifest,'a',if_changed=identity)
 def test_cli_batch_and_refresh_reject_incompatible_flags(self):
  base=[sys.executable,'-B',str(ROOT/'orchestrator/tools/orchestrate.py'),'load']
  result=subprocess.run(base+['--capability','interaction.general','--capability','interaction.math','--explicit-capability','interaction.math'],capture_output=True,text=True)
  self.assertEqual(0,result.returncode,result.stdout);self.assertEqual(2,len(json.loads(result.stdout)['items']))
  result=subprocess.run(base+['--capability','interaction.general','--capability','interaction.math','--if-changed','a'*64],capture_output=True,text=True)
  self.assertEqual(2,result.returncode);self.assertEqual('SINGLE_CAPABILITY_REQUIRED',json.loads(result.stdout)['reason'])

class ContextAcknowledgementTests(unittest.TestCase):
 setUp = ContextDeliveryTests.setUp
 def test_no_suppression_before_output_acknowledgement(self):
  from model_context import acknowledge_context
  first=context_packet(self.root,self.manifest,session='delivery-fixture',defer_marker=True)
  self.assertFalse(list((self.root/'.runtime/context-delivery').glob('*.json')))
  again=context_packet(self.root,self.manifest,session='delivery-fixture',delivery='continuation',defer_marker=True)
  self.assertTrue(again['additional_context'])
  acknowledge_context(self.root,'delivery-fixture',first['revision'])
  self.assertEqual('',context_packet(self.root,self.manifest,session='delivery-fixture',delivery='continuation',defer_marker=True)['additional_context'])
  with self.assertRaisesRegex(ContextError,'INVALID_DELIVERY'):acknowledge_context(self.root,'delivery-fixture',{'permission':'granted'})
 def test_merged_codex_entry_matches_core_and_tracks_revision(self):
  from install_runtime_adapter import install_adapter, check_adapter
  with tempfile.TemporaryDirectory() as directory:
   config=Path(directory);install_adapter('codex',config)
   entry=(config/'skills/skills-ai-registry/SKILL.md').read_text()
   raw=(ROOT/'orchestrator/runtime/skills-orchestrator/SKILL.md').read_bytes()
   core=core_text(raw.decode())
   self.assertIn(core,entry);self.assertIn(hashlib.sha256(raw).hexdigest(),entry);self.assertTrue(check_adapter('codex',config))
   with patch('install_runtime_adapter.installed_content',return_value=b'New source core'):
    self.assertFalse(check_adapter('codex',config))
 def test_theory_direct_shared_entry_preserves_conditional_host_guidance(self):
  record=load_capability(ROOT,build_manifest(ROOT),'theory-reference')
  self.assertEqual('skills/theory-reference/shared/SKILL.md',record['capability']['entry'])
  self.assertIn('only if',record['extensions']['theory-reference:host-guidance']['claude_notes'])
  self.assertIn('## Loading rule',record['body'])

class ManifestFreshnessTests(unittest.TestCase):
 def test_source_drift_is_rejected_without_reading_skill_bodies(self):
  import shutil
  from registry_runtime import load_manifest, RegistryRuntimeError
  manifest=build_manifest(ROOT)
  self.assertNotIn('skills/interaction-protocol/protocol.json',[s['path'] for s in manifest['sources']])
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory);(root/'orchestrator/runtime').mkdir(parents=True)
   for source in manifest['sources']:
    target=root/source['path'];target.parent.mkdir(parents=True,exist_ok=True);shutil.copy(ROOT/source['path'],target)
   path=root/'orchestrator/runtime/manifest.json';path.write_text(json.dumps(manifest))
   self.assertEqual(manifest,load_manifest(path))
   activation=root/'orchestrator/registry/activation.md';activation.write_text(activation.read_text()+'\nChanged gate source.\n')
   with self.assertRaisesRegex(RegistryRuntimeError,'STALE_MANIFEST'):load_manifest(path)

class SharedLoadingTests(unittest.TestCase):
 setUp = ExplicitAccessTests.setUp
 def shared(self,state='active',path='entries/a.md'):
  self.manifest['routes'].append({'package':'a','id':'b','path':path,'description':'Support','state':state})
 def test_opt_in_dedup_reads_shared_entry_once_and_keeps_identity(self):
  from model_context import load_capabilities
  self.shared()
  default_batch=load_capabilities(self.root,self.manifest,['a','b'])
  with patch('model_context.read_relative',wraps=read_relative) as read:
   out=load_capabilities(self.root,self.manifest,['a','b'],deduplicate=True)
  self.assertEqual(1,sum(c.args[1]=='entries/a.md' for c in read.call_args_list))
  self.assertEqual('skills-ai/load-batch/2',out['schema']);self.assertEqual(1,len(out['bodies']))
  for old,new in zip(default_batch['items'],out['items']):
   self.assertEqual(old['identity'],new['identity']);self.assertNotIn('body',new)
   self.assertEqual(old['body'],out['bodies'][new['body_ref']]['body'])
  self.assertNotEqual(out['items'][0]['identity'],out['items'][1]['identity'])
 def test_dedup_checks_all_gates_before_entry_read(self):
  from model_context import load_capabilities
  self.shared('manual')
  with patch('model_context.read_relative',side_effect=AssertionError('body read')):
   with self.assertRaisesRegex(ContextError,'EXPLICIT'):load_capabilities(self.root,self.manifest,['a','b'],deduplicate=True)
  out=load_capabilities(self.root,self.manifest,['a','b'],explicit_capabilities=['b'],deduplicate=True)
  self.assertFalse(out['items'][0]['explicit_invocation_attested']);self.assertTrue(out['items'][1]['explicit_invocation_attested'])
  self.manifest['routes'][1]['state']='off'
  with patch('model_context.read_relative',side_effect=AssertionError('body read')):
   with self.assertRaisesRegex(ContextError,'DISABLED'):load_capabilities(self.root,self.manifest,['a','b'],explicit_capabilities=['b'],deduplicate=True)
 def test_equal_bytes_at_different_paths_do_not_merge_artifacts(self):
  from model_context import load_capabilities
  (self.root/'entries/b.md').write_text('A complete instruction body');self.shared(path='entries/b.md')
  out=load_capabilities(self.root,self.manifest,['a','b'],deduplicate=True)
  self.assertEqual(2,len(out['bodies']))
  self.assertNotEqual(out['items'][0]['body_ref'],out['items'][1]['body_ref'])
 def test_discovery_exposes_references_without_reading_them(self):
  (self.root/'orchestrator/registry/contracts').mkdir(parents=True)
  c=ContractShapeTests().contract();c['package']['id']='a';c['capabilities'][0].update(id='a',entry='entries/a.md')
  c['capabilities'][0]['dependencies']=[{'kind':'reference','target':'entries/optional.md'}]
  c['rules']=[{'class':'invariant','source':'entries/rules.md'}]
  (self.root/'orchestrator/registry/contracts/a.json').write_text(json.dumps(c))
  out=discover(self.root,self.manifest)
  self.assertEqual(['entries/optional.md','entries/rules.md'],out['items'][0]['references'])
  self.assertFalse((self.root/'entries/optional.md').exists())
 def test_cli_dedup_is_opt_in_and_single_use_is_rejected(self):
  cli=[sys.executable,'-B',str(ROOT/'orchestrator/tools/orchestrate.py'),'load']
  args=['--capability','interaction.general','--capability','interaction.math']
  default_batch=subprocess.run(cli+args,capture_output=True,text=True,timeout=4)
  new=subprocess.run(cli+args+['--deduplicate'],capture_output=True,text=True,timeout=4)
  self.assertEqual(0,new.returncode,new.stderr)
  self.assertEqual('skills-ai/load-batch/1',json.loads(default_batch.stdout)['schema'])
  packet=json.loads(new.stdout);self.assertEqual(1,len(packet['bodies']))
  self.assertEqual(load_capability(ROOT,build_manifest(ROOT),'interaction.general')['body'],next(iter(packet['bodies'].values()))['body'])
  bad=subprocess.run(cli+['--capability','interaction.general','--deduplicate'],capture_output=True,text=True,timeout=4)
  self.assertEqual(2,bad.returncode);self.assertIn('BATCH_REQUIRED',bad.stdout)

class SharedStatusTests(unittest.TestCase):
 setUp = ContextDeliveryTests.setUp
 def test_status_loads_no_body_creates_no_state_and_does_not_infer_controls(self):
  from model_context import status_packet
  def bounded(root,path,**kwargs):
   self.assertNotEqual('orchestrator/runtime/skills-orchestrator/SKILL.md',path)
   self.assertFalse(path.startswith('entries/'))
   return read_relative(root,path,**kwargs)
  with patch('model_context.read_relative',side_effect=bounded):
   out=status_packet(self.root,self.manifest,session='fresh-chat')
  self.assertEqual('off',out['repair']['repair']);self.assertFalse((self.root/'.runtime').exists())
  self.assertEqual(str(self.root.resolve()),out['repository_root'])
  self.assertEqual('none',out['authority']);self.assertNotIn('mode',out)
  self.assertIn('effective_controls_and_scope',out['host_fields'])
  self.assertEqual('unknown',status_packet(self.root,self.manifest)['repair']['repair'])
 def test_corrupt_known_association_stays_unresolved_without_guessing(self):
  from model_context import status_packet
  folder=self.root/'.runtime/repair/sessions';folder.mkdir(parents=True)
  spec=importlib.util.spec_from_file_location('status_fixture_repair',self.root/'orchestrator/runtime/repair_workspace.py')
  controller=importlib.util.module_from_spec(spec);spec.loader.exec_module(controller)
  marker=folder/(controller.session_key('fresh-chat')+'.json');marker.write_text('broken')
  out=status_packet(self.root,self.manifest,session='fresh-chat')
  self.assertEqual('unresolved',out['repair']['repair']);self.assertIn('never fall back',out['repair']['next'])
  self.assertEqual('broken',marker.read_text())
 def test_status_after_successful_containment_and_pause_uses_exact_association(self):
  from model_context import status_packet
  spec=importlib.util.spec_from_file_location('status_lifecycle_repair',self.root/'orchestrator/runtime/repair_workspace.py')
  controller=importlib.util.module_from_spec(spec);spec.loader.exec_module(controller)
  folder=self.root/'orchestrator/governance';folder.mkdir(parents=True)
  (folder/'CONTRACT.json').write_text('{"allowed_external_symlinks":[]}')
  (self.root/'.gitignore').write_text('.runtime/\n')
  controller.git(self.root,'init','-q')
  controller.git(self.root,'config','user.name','test');controller.git(self.root,'config','user.email','test@invalid')
  controller.git(self.root,'add','--all');controller.git(self.root,'commit','-qm','fixture')
  started=controller.start(self.root,'known-chat',write=True)
  out=status_packet(self.root,self.manifest,session='known-chat')
  self.assertEqual('on',out['repair']['repair']);self.assertEqual(started['working_root'],out['repair']['working_root'])
  controller.pause(self.root,'known-chat',write=True)
  paused=status_packet(self.root,self.manifest,session='known-chat')
  self.assertEqual('off',paused['repair']['repair']);self.assertEqual(started['workspace'],paused['repair']['workspace'])
  self.assertEqual('off',status_packet(self.root,self.manifest,session='other-chat')['repair']['repair'])
 def test_status_keeps_pagination_explicit_and_rejects_relative_project(self):
  from model_context import status_packet
  for i in range(40):
   name=f'p{i:02}';self.manifest['packages'][name]={'state':'active'}
   self.manifest['routes'].append({'package':name,'id':name,'path':'entry.md','description':'Purpose','state':'active'})
  out=status_packet(self.root,self.manifest)
  self.assertEqual(40,out['catalog']['total']);self.assertIsNotNone(out['catalog']['next_offset'])
  with self.assertRaisesRegex(ContextError,'ABSOLUTE_PROJECT'):status_packet(self.root,self.manifest,project_root=Path('relative'))
  with self.assertRaisesRegex(ContextError,'INVALID_SESSION'):status_packet(self.root,self.manifest,session='../invalid')
 def test_manifest_cannot_bind_arbitrary_files_or_omit_activation(self):
  import shutil
  from registry_runtime import load_manifest, RegistryRuntimeError
  manifest=build_manifest(ROOT)
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory);(root/'orchestrator/runtime').mkdir(parents=True)
   for source in manifest['sources']:
    target=root/source['path'];target.parent.mkdir(parents=True,exist_ok=True);shutil.copy(ROOT/source['path'],target)
   path=root/'orchestrator/runtime/manifest.json'
   manifest['sources'][0]['path']='entries/private.md';path.write_text(json.dumps(manifest))
   with self.assertRaisesRegex(RegistryRuntimeError,'INVALID_MANIFEST_BINDINGS'):load_manifest(path)

class CoreTextTests(unittest.TestCase):
 def test_core_text_strips_only_front_matter_and_the_home_footer(self):
  self.assertEqual('body\n',core_text('---\nname: x\n---\n\nbody\n\n---\n\n[⌂ Home](INDEX.md)\n'))
  self.assertEqual('plain text\n',core_text('plain text\n'))
  self.assertEqual('one\n\n---\n\ntwo\n',core_text('---\nname: x\n---\none\n\n---\n\ntwo\n'))
  self.assertEqual('text with [⌂ Home](INDEX.md) inside\n',core_text('text with [⌂ Home](INDEX.md) inside\n'))
