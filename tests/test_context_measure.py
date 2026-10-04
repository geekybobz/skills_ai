import sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'));sys.path.insert(0,str(ROOT/'runtime'))
from measure_context import measure
class ContextMeasureTests(unittest.TestCase):
 def test_actual_flow_budgets_and_selective_refresh(self):
  result=measure(repeat=1)
  self.assertEqual([],result['failures'])
  self.assertEqual(0,result['bytes']['unchanged_continuation'])
  self.assertEqual(0,result['candidate_bodies_loaded'])
  self.assertEqual('not-measured',result['semantic_acceptance'])
