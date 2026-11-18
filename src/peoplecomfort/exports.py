"""Portable, dependency-free CSV/JSON/SVG/HTML output generation."""
import csv
from html import escape
import io
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import zipfile


def comparison_svg(r):
    p=r["project"]
    rows=r["rows"]
    scenarios=p["scenarios"]
    designs=p["designs"]
    width,height=940,150+len(scenarios)*48
    parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
           '<rect width="100%" height="100%" fill="#f6f8f7"/>',
           '<style>text{font-family:Arial,Microsoft YaHei,sans-serif;fill:#173d3a} .small{font-size:12px}</style>',
           '<text x="24" y="32" font-size="22">Design x composition | Mean PMV exceedance</text>',
           '<text x="24" y="54" class="small">Illustrative scenarios | Lower is better | Not measured dissatisfaction | * Row optimum</text>']
    colw=min(210,650/len(designs))
    for j,d in enumerate(designs):
        parts.append(f'<text x="{240+j*colw}" y="88" font-size="14">{escape(d["name"])}</text>')
    maxloss=max((x["loss"] for x in rows if x["feasible"]),default=1) or 1
    for i,s in enumerate(scenarios):
        y=105+i*48
        parts.append(f'<text x="24" y="{y+24}" font-size="14">{escape(s["id"])} · {"Dev" if s["split"]=="development" else "Test"}</text>')
        for j,d in enumerate(designs):
            row=next(x for x in rows if x["scenario"]==s["id"] and x["design"]==d["id"])
            value=row["loss"]
            ratio=min(value/maxloss,1) if value is not None else 1
            color=f'rgb({int(232-60*ratio)},{int(244-130*ratio)},{int(239-140*ratio)})'
            x=220+j*colw
            label=f'{value:.3f}'+(' *' if row["regret"]<1e-10 else '') if value is not None else 'Infeasible'
            parts.append(f'<rect x="{x}" y="{y}" width="{colw-12}" height="39" rx="6" fill="{color}"/>')
            parts.append(f'<text x="{x+20}" y="{y+25}" font-size="17">{label}</text>')
    parts.append('</svg>')
    return ''.join(parts)


def csv_text(rows, fields):
    out=io.StringIO(newline='')
    writer=csv.DictWriter(out,fieldnames=fields,extrasaction='ignore')
    writer.writeheader(); writer.writerows(rows)
    return '\ufeff'+out.getvalue()


def files(r):
    node=os.environ.get('PEOPLECOMFORT_NODE') or shutil.which('node')
    node_version=subprocess.check_output([node,'--version'],text=True).strip() if node else 'PEOPLECOMFORT_NODE override; see engine'
    env={"python":platform.python_version(),"node":node_version,"platform":platform.platform(),
         "peoplecomfort":r['software_version'],"input_sha256":r['input_sha256'],"engine":r['engine']}
    thermal=[]
    for x in r['thermal_ledger']:
        thermal.append({"type":x['type'],"zone":x['zone'],**x['input'],**x['output']})
    allocations=[]
    for row in r['rows']:
        if row['feasible']:
            s=next(s for s in r['project']['scenarios'] if s['id']==row['scenario'])
            for i,t in enumerate(r['project']['profiles']):
                for j,z in enumerate(r['project']['zones']):
                    allocations.append({"design":row['design'],"scenario":row['scenario'],"type":t['id'],"zone":z['id'],
                                        "count":row['allocation'][i][j],"type_total":s['counts'][t['id']]})
    svg=comparison_svg(r)
    summary=escape(json.dumps(r['selection'],ensure_ascii=False,indent=2))
    report=f'''<!doctype html><meta charset="utf-8"><title>PeopleComfort run report</title>
<style>body{{max-width:1000px;margin:40px auto;font:16px/1.65 system-ui;color:#173d3a;background:#f6f8f7}}pre{{white-space:pre-wrap}}svg{{max-width:100%;height:auto}}</style>
<h1>PeopleComfort | Run results</h1><p>Conditional scenarios, not measured comfort. Allocation is ideal managed matching under constraints, not a behavioural prediction.</p>{svg}
<h2>Selection</h2><pre>{summary}</pre><p>Input SHA-256: {r['input_sha256']}</p>
<p>See comparison.csv, thermal_ledger.csv and allocations.csv. Full input: project.json.</p>'''
    out={"project.json":json.dumps(r['project'],ensure_ascii=False,indent=2),
         "result.json":json.dumps(r,ensure_ascii=False,indent=2),
         "run_manifest.json":json.dumps(env,ensure_ascii=False,indent=2),
         "comparison.csv":csv_text(r['rows'],['design','scenario','split','feasible','loss','regret','flagged','flagged_share','worst_type_loss','feasible_allocations']),
         "thermal_ledger.csv":csv_text(thermal,list(thermal[0])),
         "allocations.csv":csv_text(allocations,['design','scenario','type','zone','count','type_total']),
         "uncertainty.json":json.dumps(r['uncertainty'],ensure_ascii=False,indent=2),
         "comparison.svg":svg,"report.html":report}
    return out


def save(r, target):
    target=Path(target); target.mkdir(parents=True,exist_ok=True)
    for name,text in files(r).items(): (target/name).write_text(text,encoding='utf-8')


def archive(r):
    stream=io.BytesIO()
    with zipfile.ZipFile(stream,'w',zipfile.ZIP_DEFLATED) as z:
        for name,text in files(r).items(): z.writestr(name,text)
        z.writestr('README.txt','Run in the PeopleComfort source package: python run.py analyze --project project.json --out rerun\nThe full software source is supplied separately.\n')
    return stream.getvalue()
