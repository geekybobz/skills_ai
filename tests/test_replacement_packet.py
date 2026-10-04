"""Rehearse exact replacement against staged, dirty and unrelated user files."""
import copy
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from test_registry_runtime import ROOT
import sys
sys.path.insert(0,str(ROOT/'scripts'))
from replacement_packet import export,apply,recover,ContextError
class ReplacementTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
  self.git('init','-q');self.git('config','user.email','test@example.invalid');self.git('config','user.name','Test')
  (self.root/'owned.txt').write_text('old user content');(self.root/'removed.txt').write_text('remove after acceptance')
  self.git('add','.');self.git('commit','-qm','baseline');self.baseline=self.git('rev-parse','HEAD').strip()
  (self.root/'owned.txt').write_text('new implementation');(self.root/'removed.txt').unlink();(self.root/'new.txt').write_text('added')
  self.git('add','-A');self.git('commit','-qm','replacement');self.packet=export(self.root,self.baseline,'HEAD')
  self.git('checkout',self.baseline,'--','owned.txt','removed.txt');(self.root/'new.txt').unlink()
  (self.root/'unrelated.txt').write_text('preserve me')
 def git(self,*args):return subprocess.check_output(['git','-C',str(self.root),*args],text=True)
 def test_preview_is_read_only_and_apply_rollback_preserve_index_and_unrelated_files(self):
  index=(self.root/'.git/index').read_bytes();before=self.git('status','--porcelain')
  apply(self.root,self.packet);self.assertEqual(before,self.git('status','--porcelain'))
  backup=self.root/'rollback.json';apply(self.root,self.packet,write=True,backup=backup)
  self.assertEqual('new implementation',(self.root/'owned.txt').read_text());self.assertFalse((self.root/'removed.txt').exists())
  apply(self.root,json.loads(backup.read_text()),rollback=True,write=True)
  self.assertEqual('old user content',(self.root/'owned.txt').read_text());self.assertFalse((self.root/'new.txt').exists())
  self.assertEqual('preserve me',(self.root/'unrelated.txt').read_text());self.assertEqual(index,(self.root/'.git/index').read_bytes())
 def test_drift_blocks_before_any_file_is_written(self):
  (self.root/'owned.txt').write_text('new user edits')
  with self.assertRaisesRegex(ContextError,'CONTENT_CONFLICT'):apply(self.root,self.packet,write=True,backup=self.root/'backup.json')
  self.assertFalse((self.root/'new.txt').exists());self.assertFalse((self.root/'backup.json').exists())
 def test_rollback_does_not_overwrite_post_deployment_edits(self):
  apply(self.root,self.packet,write=True,backup=self.root/'backup.json');(self.root/'owned.txt').write_text('later edits')
  with self.assertRaisesRegex(ContextError,'CONTENT_CONFLICT'):apply(self.root,self.packet,rollback=True,write=True)
  self.assertEqual('later edits',(self.root/'owned.txt').read_text());self.assertTrue((self.root/'new.txt').exists())
 def test_malicious_paths_tampering_and_symlink_parents_are_blocked(self):
  for name in ('../escape','.git/config','/absolute','theory-reference/file'):
   packet=copy.deepcopy(self.packet);packet['entries'][0]['path']=name
   with self.assertRaises(ContextError):apply(self.root,packet)
  packet=copy.deepcopy(self.packet);packet['entries'][0]['after']['data']='Zm9yZ2Vk'
  with self.assertRaisesRegex(ContextError,'DIGEST'):apply(self.root,packet)
  (self.root/'linked').symlink_to(self.root,target_is_directory=True);packet=copy.deepcopy(self.packet);packet['entries'][0]['path']='linked/owned.txt'
  with self.assertRaisesRegex(ContextError,'UNSAFE'):apply(self.root,packet)
 def test_mid_apply_failure_restores_completed_writes(self):
  from replacement_packet import atomic_file
  count=0
  def fail_once(*args):
   nonlocal count
   count+=1
   if count==3:raise OSError('simulated interrupted write')
   return atomic_file(*args)
  with patch('replacement_packet.atomic_file',side_effect=fail_once):
   with self.assertRaises(OSError):apply(self.root,self.packet,write=True,backup=self.root/'backup.json')
  self.assertEqual('old user content',(self.root/'owned.txt').read_text());self.assertFalse((self.root/'new.txt').exists());self.assertTrue((self.root/'removed.txt').exists())

 def test_killed_partial_apply_can_be_recovered_idempotently(self):
  # A process died after replacing one file; others still have baseline bytes.
  (self.root/'owned.txt').write_text('new implementation')
  index=(self.root/'.git/index').read_bytes()
  self.assertEqual(1,recover(self.root,self.packet)['files'])
  recover(self.root,self.packet,write=True)
  self.assertEqual('old user content',(self.root/'owned.txt').read_text())
  self.assertEqual('already-restored',recover(self.root,self.packet,write=True)['action'])
  self.assertEqual(index,(self.root/'.git/index').read_bytes())
 def test_partial_recovery_refuses_new_user_edits_before_any_write(self):
  (self.root/'owned.txt').write_text('new implementation');(self.root/'removed.txt').write_text('new user edit')
  with self.assertRaisesRegex(ContextError,'RECOVERY_CONTENT_CONFLICT'):recover(self.root,self.packet,write=True)
  self.assertEqual('new implementation',(self.root/'owned.txt').read_text())
  self.assertEqual('new user edit',(self.root/'removed.txt').read_text())
