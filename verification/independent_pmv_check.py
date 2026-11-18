"""Compare six nominal CBE cases with an independently maintained PMV implementation.

Install pythermalcomfort==4.8.1, then run from the repository root:
    python verification/independent_pmv_check.py
This verification dependency is not needed by PeopleComfort at runtime.
"""
import json
import os
from pathlib import Path
import sys
from importlib.metadata import version

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from peoplecomfort.comfort import calculate, provenance
from pythermalcomfort.environment import v_relative
from pythermalcomfort.models import pmv_ppd_ashrae


def main():
    project=json.loads((ROOT/'examples/minimal/project.json').read_text(encoding='utf-8'))
    cases=[{'profile':t['id'],'zone':z['id'],'ta':z['ta'],'tr':z['tr'],
            'v':z['v'],'rh':z['rh'],'met':t['met'],'clo':t['clo']}
           for t in project['profiles'] for z in project['zones']]
    cbe=calculate(cases)
    rows=[]
    for case,result in zip(cases,cbe):
        other=pmv_ppd_ashrae(tdb=case['ta'],tr=case['tr'],
            vr=v_relative(v=case['v'],met=case['met']),rh=case['rh'],
            met=case['met'],clo=case['clo'],wme=0,limit_inputs=False,round_output=False)
        rows.append({**case,'cbe_pmv':result['pmv'],'independent_pmv':float(other.pmv),
                     'pmv_difference':result['pmv']-float(other.pmv),
                     'cbe_ppd':result['ppd'],'independent_ppd':float(other.ppd),
                     'ppd_difference':result['ppd']-float(other.ppd)})
    report={'reference':'pythermalcomfort '+version('pythermalcomfort')+' pmv_ppd_ashrae',
            'source':'https://pythermalcomfort.readthedocs.io/en/stable/documentation/models.html',
            'cbe_commit':provenance()['commit'],
            'method':'Relative air speed computed with pythermalcomfort.v_relative; wme=0; unrounded output; model input bounds disabled to expose exact numerical comparison.',
            'scope':'Independent software implementation of the same theoretical PMV model; not field validation. Library and CBE may differ in numerical details.',
            'maximum_absolute_pmv_difference':max(abs(x['pmv_difference']) for x in rows),
            'maximum_absolute_ppd_difference':max(abs(x['ppd_difference']) for x in rows),
            'cases':rows}
    target=ROOT/'verification/independent_pmv_comparison.json'
    target.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'cases':len(rows),'max_abs_pmv':report['maximum_absolute_pmv_difference'],
                      'max_abs_ppd':report['maximum_absolute_ppd_difference']},indent=2))


if __name__=='__main__':main()
