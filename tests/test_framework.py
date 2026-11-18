"""Independent small-case checks for the schema-v2 spatial decision framework."""
from copy import deepcopy
from itertools import product
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from peoplecomfort.framework import analyze,validate,_assignment,_priority_first_fit

ROOT=Path(__file__).resolve().parents[1]

class GeneralFrameworkTests(unittest.TestCase):
    def load(self):return json.loads((ROOT/'examples/general/project.json').read_text(encoding='utf-8'))

    def test_three_zone_two_metric_case_and_nonmutation(self):
        p=self.load();before=deepcopy(p);r=analyze(p)
        self.assertEqual(p,before)
        self.assertEqual(len(r['rows']),15)
        self.assertEqual(r['selection']['baseline']['winners'],['D0'])
        self.assertEqual(r['selection']['minimax_regret']['winners'],['D1'])
        self.assertAlmostEqual(r['rows'][0]['loss'],.10416666666666667)
        self.assertEqual(r,analyze(p))

    def test_small_independent_person_level_oracle(self):
        counts=[2,1];caps=[1,1,1];loss=[[.1,.4,.5],[.6,.2,.3]];allowed=[[True]*3,[True]*3]
        result=_assignment(counts,caps,loss,allowed)
        brute=min(sum(loss[t][z] for t,z in zip([0,0,1],places))/3 for places in product(range(3),repeat=3) if all(places.count(z)<=caps[z] for z in range(3)))
        self.assertAlmostEqual(result['loss'],brute)
        self.assertEqual([sum(x) for x in result['allocation']],counts)

    def test_access_and_loss_ceiling(self):
        r=_assignment([1,1],[1,1],[[.2,.9],[.9,.2]],[[True,False],[False,True]],.3)
        self.assertTrue(r['feasible']);self.assertAlmostEqual(r['loss'],.2)
        self.assertFalse(_assignment([1,1],[1,1],[[.2,.9],[.9,.2]],[[True,False],[False,True]],.1)['feasible'])

    def test_design_specific_environment_and_plan_boundary(self):
        p=self.load();scores={m['id']:m['scores'] for m in p['metrics']}
        p['design_scores']={d['id']:deepcopy(scores) for d in p['designs']};p['design_scores_source']='Constructed alternative environmental ratings'
        baseline=analyze(self.load());modified=analyze(p)
        self.assertEqual([x['loss'] for x in baseline['rows']],[x['loss'] for x in modified['rows']])
        p['design_scores']['D1']['task_fit']['P1']['Z1']=.9
        self.assertNotEqual([x['loss'] for x in modified['rows']],[x['loss'] for x in analyze(p)['rows']])
        p['plan']={'kind':'measured','source':'Survey image'}
        with self.assertRaisesRegex(ValueError,'scale'):validate(p)

    def test_weight_and_score_validation(self):
        p=self.load();p['metrics'][0]['weight']=.7
        with self.assertRaisesRegex(ValueError,'sum to 1'):validate(p)
        p=self.load();p['metrics'][0]['scores']['P1']['Z1']=1.4
        with self.assertRaisesRegex(ValueError,'direct loss'):validate(p)

    def test_worlds_and_holdout_separation(self):
        p=self.load();scores={m['id']:deepcopy(m['scores']) for m in p['metrics']};p['score_worlds']=[{'id':'W1','scores':scores}]
        r=analyze(p);self.assertEqual(len(r['score_worlds']),1)
        p['scenarios'][-1]['counts']={'P1':4,'P2':4,'P3':4}
        q=analyze(p)
        self.assertEqual(r['selection']['minimax_regret'],q['selection']['minimax_regret'])

    def test_variable_capacity_and_rule_selection(self):
        p=self.load();p['capacity_policy']='variable_total';p['decision_rule']='minimax_loss'
        p['designs'][0]['capacity']['Z1']=6
        result=analyze(p)
        self.assertFalse(result['rows'][0]['feasible'])
        self.assertEqual(result['selection']['selected_rule'],'minimax_loss')
        self.assertEqual(result['selection']['selected'],result['selection']['minimax_loss'])

    def test_priority_first_fit_can_differ_from_optimal(self):
        counts=[1,1];capacities=[1,1];loss=[[0,.2],[0,.9]]
        allowed=[[True,True],[True,False]]
        optimal=_assignment(counts,capacities,loss,allowed)
        greedy=_priority_first_fit(counts,capacities,loss,allowed)
        self.assertTrue(optimal['feasible'])
        self.assertAlmostEqual(optimal['loss'],.1)
        self.assertFalse(greedy['feasible'])

    def test_priority_rule_end_to_end(self):
        p=self.load();p['allocation_rule']='priority_first_fit'
        r=analyze(p)
        self.assertEqual(len(r['rows']),15)
        self.assertEqual(r['selection']['selected_rule'],'minimax_regret')
