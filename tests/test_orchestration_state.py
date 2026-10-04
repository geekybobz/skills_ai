"""Actual checkpoint invalidation, read-only behavior and atomic persistence."""
import copy,hashlib,json,os,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'runtime'))
from model_context import ContextError
from orchestration_state import inspect_state,save_state,validate_state
class CheckpointTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
  for p,text in [('entry.md','instruction'),('artifact.txt','output'),('check.txt','actual check record'),('effect.txt','external action receipt')]:
   (self.root/p).write_text(text)
  def b(p):return {'path':p,'sha256':hashlib.sha256((self.root/p).read_bytes()).hexdigest()}
  self.state={'schema':'skills-ai/checkpoint/1','objective':'complete the task','phase':'review','bindings':[b('entry.md')],'artifacts':[b('artifact.txt')],
              'evidence':[{'check':'domain check','artifact':b('artifact.txt'),'record':b('check.txt'),'outcome':'passed'}],
              'completed_effects':[{'id':'effect-1','receipt':b('effect.txt')}],'unresolved':[],'next_step':'inspect evidence'}
 def test_inspection_never_certifies_and_is_read_only(self):
  before=list(self.root.iterdir());out=inspect_state(self.root,self.root,self.state)
  self.assertTrue(out['content_matches']);self.assertEqual('not-assessed',out['verification']);self.assertEqual('none',out['authority'])
  self.assertEqual(before,list(self.root.iterdir()))
 def test_each_changed_or_missing_binding_is_detected(self):
  for p in ('entry.md','artifact.txt','check.txt','effect.txt'):
   old=(self.root/p).read_bytes();(self.root/p).write_text('changed')
   self.assertFalse(inspect_state(self.root,self.root,self.state)['content_matches']);(self.root/p).write_bytes(old)
  (self.root/'effect.txt').unlink();out=inspect_state(self.root,self.root,self.state)
  self.assertEqual('unavailable',out['observations'][-1]['status'])
 def test_permission_claims_commands_prompts_and_certification_fields_rejected(self):
  for field in ('approved_scope','permission_grants','commands','prompt','transcript','certified'):
   state=self.state|{field:'extra'}
   with self.assertRaises(ContextError):validate_state(state)
 def test_traversal_secrets_and_unbound_evidence_rejected(self):
  changes=[lambda s:s['bindings'][0].update(path='../escape'),lambda s:s.update(objective='password=abcdef'),lambda s:s['evidence'][0]['artifact'].update(path='another.txt')]
  for change in changes:
   s=copy.deepcopy(self.state);change(s)
   with self.assertRaises(ContextError):validate_state(s)
 def test_preview_creates_nothing_and_explicit_save_is_atomic_private(self):
  self.assertEqual('preview',save_state(self.root,'.skills-ai/task.json',self.state)['action'])
  self.assertFalse((self.root/'.skills-ai').exists())
  for i in range(2):
   self.assertEqual('saved',save_state(self.root,'.skills-ai/task.json',self.state,write=True)['action'])
   self.assertEqual(self.state,json.loads((self.root/'.skills-ai/task.json').read_text()))
  self.assertEqual(['task.json'],[p.name for p in (self.root/'.skills-ai').iterdir()])
  self.assertEqual(0o600,(self.root/'.skills-ai/task.json').stat().st_mode&0o777)
 def test_symlink_targets_and_directory_escape_rejected(self):
  (self.root/'.skills-ai').mkdir();(self.root/'.skills-ai/task.json').symlink_to(self.root/'artifact.txt')
  with self.assertRaises(ContextError):save_state(self.root,'.skills-ai/task.json',self.state,write=True)
  self.assertEqual('output',(self.root/'artifact.txt').read_text())
  with self.assertRaises(ContextError):save_state(self.root,'../outside.json',self.state,write=True)
 def test_duplicate_effects_and_oversized_state_rejected(self):
  self.state['completed_effects']*=2
  with self.assertRaisesRegex(ContextError,'DUPLICATE_EFFECT'):validate_state(self.state)
