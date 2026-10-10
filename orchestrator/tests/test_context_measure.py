import json, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'orchestrator'/'tools'));sys.path.insert(0,str(ROOT/'orchestrator'/'runtime'))
from measure_context import budgeted_bootstrap_bytes, measure
class ContextMeasureTests(unittest.TestCase):
 def test_bootstrap_budget_does_not_depend_on_the_checkout_path(self):
  body='\nResolve tool and instruction paths from this root.\ncore and catalog'
  sizes=set()
  for root in ('/a','/Users/someone/skills_ai','/Users/billabobz/skills_ai/.runtime/repair/workspaces/repair-0123456789abcdef/repo'):
   context='Skills AI repository tools root: '+json.dumps(str(Path(root).resolve()))+body
   sizes.add(budgeted_bootstrap_bytes(context,root))
  self.assertEqual(1,len(sizes))
 def test_actual_flow_budgets_and_selective_refresh(self):
  result=measure(repeat=1)
  self.assertEqual([],result['failures'])
  self.assertEqual(0,result['bytes']['unchanged_continuation'])
  self.assertEqual(0,result['candidate_bodies_loaded'])
  self.assertEqual('not-measured',result['semantic_acceptance'])
  self.assertLessEqual(result['bytes']['core'],result['budgets']['core'])
  self.assertLessEqual(result['bytes']['bootstrap'],result['budgets']['bootstrap'])
  self.assertIn('not tokenizer output or total task savings',result['token_measurement'])
