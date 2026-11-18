"""Independent small-problem checks and deployed-CBE reference checks."""
import copy
from itertools import product
import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from peoplecomfort.core import analyze,allocate,select,validate
from peoplecomfort.comfort import calculate,provenance


def demo(): return json.loads((ROOT/'src/peoplecomfort/data/demo.json').read_text(encoding='utf-8'))


class ReferenceTests(unittest.TestCase):
    def test_deployed_cbe_12_cases(self):
        reference=json.loads((ROOT/'tests/cbe_reference.json').read_text())
        computed=calculate([x['inputs'] for x in reference['cases']])
        for item,out in zip(reference['cases'],computed):
            for metric in ('pmv','ppd','cooling_effect'):
                self.assertAlmostEqual(out[metric],item['output'][metric],places=8,msg=item['id']+' '+metric)

    def test_profile_corrections_are_once_only(self):
        x=calculate([dict(ta=25,tr=25,v=.1,rh=50,met=1.6,clo=.5)])[0]
        self.assertAlmostEqual(x['relative_air_speed'],.28)
        self.assertAlmostEqual(x['dynamic_clothing'],.425)

    def test_invalid_numeric_inputs_are_rejected(self):
        with self.assertRaises(ValueError):calculate([dict(ta=None,tr=25,v=.1,rh=50,met=1.2,clo=.5)])


class AllocationTests(unittest.TestCase):
    def test_against_individual_enumeration(self):
        # Independent oracle enumerates each person's seat zone, rather than type counts.
        persons=[0,0,1,1,1]
        matrix=[[-1.2,.1],[.2,1.4]]
        candidates=[]
        for seats in product((0,1),repeat=5):
            if seats.count(0)<=2 and seats.count(1)<=3:
                candidates.append(sum(max(0,abs(matrix[t][z])-.5) for t,z in zip(persons,seats))/5)
        actual=allocate([2,3],[2,3],matrix,.5,[[True,True],[True,True]])
        self.assertAlmostEqual(actual['loss'],min(candidates))
        self.assertEqual(sum(sum(x) for x in actual['allocation']),5)

    def test_manual_burden_and_denominator(self):
        r=allocate([2,1],[2,1],[[-1,.2],[.2,1]],.5,[[True,True],[True,True]])
        self.assertAlmostEqual(r['loss'],.5/3)
        self.assertEqual(r['flagged'],1)

    def test_no_feasible_assignment_is_not_zero(self):
        r=allocate([3,1],[2,2],[[0,0],[0,0]],.5,[[True,False],[True,True]])
        self.assertFalse(r['feasible']);self.assertIsNone(r['loss'])

    def test_equal_environment_gives_equal_objective(self):
        a=allocate([4,2],[3,3],[[.7,.7],[.1,.1]],.5,[[True,True]]*2)
        b=allocate([4,2],[5,1],[[.7,.7],[.1,.1]],.5,[[True,True]]*2)
        self.assertAlmostEqual(a['loss'],b['loss'])

    def test_ties_are_retained(self):
        rows=[{'design':d,'scenario':'a','feasible':True,'regret':0} for d in ['D1','D2']]
        self.assertEqual(select(rows,['a'],['D1','D2'])['winners'],['D1','D2'])

    def test_hand_calculated_minimax(self):
        rows=[{'design':d,'scenario':s,'feasible':True,'regret':v} for d,s,v in [('A','x',0),('A','y',4),('B','x',2),('B','y',1)]]
        self.assertEqual(select(rows,['x','y'],['A','B'])['winners'],['B'])


class EndToEndTests(unittest.TestCase):
    def test_no_input_mutation_and_repeatability(self):
        p=demo();original=copy.deepcopy(p);a=analyze(p,False);b=analyze(p,False)
        self.assertEqual(p,original);self.assertEqual(a,b)

    def test_holdout_does_not_choose_training_winner(self):
        p=demo();a=analyze(p,False)
        for s in p['scenarios']:
            if s['split']=='holdout':s['counts']={'P1':12,'P2':0,'P3':0}
        b=analyze(p,False)
        self.assertEqual(a['selection']['T2'],b['selection']['T2'])
        self.assertEqual(a['selection']['T3'],b['selection']['T3'])

    def test_counts_capacity_and_missing_fields_rejected(self):
        p=demo();p['scenarios'][0]['counts']['P1']=9
        with self.assertRaises(ValueError):validate(p)
        p=demo();p['designs'][0]['seats']['Z1']=10
        with self.assertRaises(ValueError):validate(p)
        p=demo();del p['zones'][0]['source']
        with self.assertRaises(ValueError):validate(p)

    def test_fixed_selection_stress_grid(self):
        r=analyze(demo(),True)
        self.assertEqual(len(r['rows']),27)
        self.assertEqual(len(r['uncertainty']),81)
        self.assertEqual(r['selection']['T2']['winners'],['D2'])
        self.assertEqual(r['selection']['T3']['winners'],['D1'])
        self.assertTrue(all(sum(sum(pair) for pair in x['allocation'])==12 for x in r['rows']))


if __name__=='__main__': unittest.main()
