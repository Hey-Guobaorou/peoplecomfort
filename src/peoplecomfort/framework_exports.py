"""Portable outputs for general schema v2 projects."""
import csv
import io
import json
from pathlib import Path
import platform
import subprocess
import shutil
import os
import zipfile


def _csv(rows,fields):
    out=io.StringIO(newline='');writer=csv.DictWriter(out,fieldnames=fields,extrasaction='ignore');writer.writeheader();writer.writerows(rows);return '\ufeff'+out.getvalue()


def files(result):
    p=result['project'];zs=[z['id'] for z in p['zones']];ts=[t['id'] for t in p['profiles']]
    comparison=[];allocations=[]
    for row in result['rows']:
        comparison.append({**{k:row.get(k) for k in ('design','scenario','split','feasible','loss','regret','worst_type_loss')},**{f'loss_{k}':v for k,v in row.get('metric_losses',{}).items()}})
        if row['feasible']:
            for i,t in enumerate(ts):
                for j,z in enumerate(zs):allocations.append({'design':row['design'],'scenario':row['scenario'],'profile':t,'zone':z,'count':row['allocation'][i][j]})
    node=os.environ.get('PEOPLECOMFORT_NODE') or shutil.which('node')
    manifest={'peoplecomfort':result['software_version'],'schema_version':2,'input_sha256':result['input_sha256'],'engine':result['engine'],'python':platform.python_version(),'node':subprocess.check_output([node,'--version'],text=True).strip() if node else None}
    scores=json.dumps(result['selection'],indent=2)
    html='<!doctype html><html lang="en"><meta charset="utf-8"><title>PeopleComfort general run</title><style>body{max-width:850px;margin:40px auto;font:16px/1.6 system-ui;color:#163e37}pre{background:#edf5ef;padding:20px;overflow:auto}</style><h1>PeopleComfort | General comparison</h1><p>Zone-capacity results under declared metrics and ideal managed matching. Inspect the full JSON and input provenance before design use.</p><h2>Selection</h2><pre>'+scores+'</pre><p>See comparison.csv, allocations.csv, metric_scores.json and project.json.</p></html>'
    keys=['design','scenario','split','feasible','loss','regret','worst_type_loss']+[f'loss_{m["id"]}' for m in p['metrics']]
    return {'project.json':json.dumps(p,indent=2),'result.json':json.dumps(result,indent=2),'run_manifest.json':json.dumps(manifest,indent=2),'metric_scores.json':json.dumps(result['metric_scores'],indent=2),'score_worlds.json':json.dumps(result['score_worlds'],indent=2),'comparison.csv':_csv(comparison,keys),'allocations.csv':_csv(allocations,['design','scenario','profile','zone','count']),'report.html':html}


def save(result,target):
    target=Path(target);target.mkdir(parents=True,exist_ok=True)
    for name,content in files(result).items():(target/name).write_text(content,encoding='utf-8')


def archive(result):
    out=io.BytesIO()
    with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
        for name,content in files(result).items():z.writestr(name,content)
    return out.getvalue()
