"""General multi-zone, multi-criterion spatial capacity comparison (schema v2)."""
from copy import deepcopy
from hashlib import sha256
import json
import math
from .comfort import calculate, provenance
from . import __version__

MAX_ZONES=8
MAX_PROFILES=8
MAX_DESIGNS=20
MAX_SCENARIOS=100
MAX_PEOPLE=80
MAX_WORLDS=30


def _ids(group, label):
    values=[v['id'] for v in group]
    if len(values)!=len(set(values)) or not all(isinstance(v,str) and v for v in values):
        raise ValueError(f'{label} IDs must be unique non-empty strings')
    return values


def _finite(v, label, lo=0, hi=1e9):
    if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or not lo<=v<=hi:
        raise ValueError(f'{label} must be finite and within [{lo},{hi}]')
    return float(v)


def validate(project):
    p=deepcopy(project)
    if p.get('schema_version')!=2:raise ValueError('schema_version must be 2')
    zones=p['zones'];profiles=p['profiles'];designs=p['designs'];scenarios=p['scenarios'];metrics=p['metrics']
    if not 2<=len(zones)<=MAX_ZONES:raise ValueError('Need 2-8 zones')
    if not 1<=len(profiles)<=MAX_PROFILES:raise ValueError('Need 1-8 profiles')
    if not 3<=len(designs)<=MAX_DESIGNS:raise ValueError('Need 3-20 designs')
    if not 2<=len(scenarios)<=MAX_SCENARIOS:raise ValueError('Need 2-100 scenarios')
    if not 1<=len(metrics)<=5:raise ValueError('Need 1-5 metrics')
    zid=_ids(zones,'Zone');pid=_ids(profiles,'Profile');did=_ids(designs,'Design');sid=_ids(scenarios,'Scenario');mid=_ids(metrics,'Metric')
    n=p['total_people']
    if isinstance(n,bool) or not isinstance(n,int) or not 1<=n<=MAX_PEOPLE:raise ValueError('total_people must be 1-80')
    for z in zones:
        cap=z['max_capacity']
        if isinstance(cap,bool) or not isinstance(cap,int) or cap<0:raise ValueError('Invalid zone maximum capacity')
        if not z.get('source'):raise ValueError('Zone source required')
    for t in profiles:
        if not set(t['allowed_zones']) or not set(t['allowed_zones'])<=set(zid):raise ValueError('Invalid allowed_zones')
        if not t.get('source'):raise ValueError('Profile source required')
    for d in designs:
        if set(d['capacity'])!=set(zid):raise ValueError('Design must specify every zone capacity')
        if any(isinstance(d['capacity'][z],bool) or not isinstance(d['capacity'][z],int) or not 0<=d['capacity'][z]<=zones[zid.index(z)]['max_capacity'] for z in zid):raise ValueError('Invalid design capacity')
        if sum(d['capacity'].values())!=n:raise ValueError('Each design must offer exactly total_people places')
    for s in scenarios:
        if s['split'] not in ('development','holdout'):raise ValueError('Scenario split must be development or holdout')
        if set(s['counts'])!=set(pid) or any(isinstance(v,bool) or not isinstance(v,int) or v<0 for v in s['counts'].values()) or sum(s['counts'].values())!=n:raise ValueError('Scenario counts must be nonnegative integers totaling total_people')
    if not any(s['split']=='development' for s in scenarios) or not any(s['split']=='holdout' for s in scenarios):raise ValueError('Need development and holdout scenarios')
    if p['existing_design'] not in did or p['baseline_scenario'] not in [s['id'] for s in scenarios if s['split']=='development']:raise ValueError('Invalid existing design or baseline scenario')
    total_weight=0
    for m in metrics:
        total_weight+=_finite(m['weight'],'metric weight',0,1)
        if not m.get('source'):raise ValueError('Metric source required')
        if m['kind'] not in ('direct','cbe_pmv'):raise ValueError('Metric kind must be direct or cbe_pmv')
        if m['kind']=='direct':
            if set(m['scores'])!=set(pid) or any(set(m['scores'][t])!=set(zid) for t in pid):raise ValueError('Direct scores must cover every profile and zone')
            for t in pid:
                for z in zid:_finite(m['scores'][t][z],'direct loss',0,1)
        else:
            _finite(m['threshold'],'PMV threshold',.1,1)
            for z in zones:
                for key,lo,hi in [('ta',15,32),('tr',15,40),('v',0,1),('rh',10,90)]:_finite(z[key],key,lo,hi)
            for t in profiles:
                for key,lo,hi in [('met',1,2),('clo',.2,1.5)]:_finite(t[key],key,lo,hi)
    if abs(total_weight-1)>1e-9:raise ValueError('Metric weights must sum to 1')
    if 'design_scores' in p:
        if set(p['design_scores'])!=set(did):raise ValueError('design_scores must cover every design')
        for d in did:
            if set(p['design_scores'][d])!=set(mid):raise ValueError('design_scores must cover every metric')
            for m in mid:
                if set(p['design_scores'][d][m])!=set(pid) or any(set(p['design_scores'][d][m][t])!=set(zid) for t in pid):raise ValueError('Design score table incomplete')
                for t in pid:
                    for z in zid:_finite(p['design_scores'][d][m][t][z],'design loss',0,1)
        if not p.get('design_scores_source'):raise ValueError('design_scores_source required')
    for w in p.get('score_worlds',[]):
        if not w.get('id'):raise ValueError('Score world ID required')
        if set(w['scores'])!=set(mid):raise ValueError('Score world must cover all metrics')
        for m in mid:
            if set(w['scores'][m])!=set(pid) or any(set(w['scores'][m][t])!=set(zid) for t in pid):raise ValueError('World score table incomplete')
            for t in pid:
                for z in zid:_finite(w['scores'][m][t][z],'world loss',0,1)
    if p.get('score_worlds') and p.get('design_scores'):raise ValueError('score_worlds and design_scores cannot be combined in v2.0')
    if len(p.get('score_worlds',[]))>MAX_WORLDS:raise ValueError('At most 30 score worlds')
    if 'max_individual_loss' in p:_finite(p['max_individual_loss'],'max_individual_loss',0,1)
    if 'plan' in p:
        plan=p['plan']
        if plan.get('kind') not in ('schematic','measured'):raise ValueError('Plan kind must be schematic or measured')
        if not plan.get('source'):raise ValueError('Plan source required')
        if plan['kind']=='measured' and not plan.get('scale'):raise ValueError('Measured plan requires scale metadata')
    return p


def _metric_scores(p):
    zones=p['zones'];profiles=p['profiles'];mid=[m['id'] for m in p['metrics']]
    out={}
    for metric in p['metrics']:
        if metric['kind']=='direct':out[metric['id']]=metric['scores'];continue
        cases=[{'ta':z['ta'],'tr':z['tr'],'v':z['v'],'rh':z['rh'],'met':t['met'],'clo':t['clo']} for t in profiles for z in zones]
        values=calculate(cases);threshold=metric['threshold'];j=0;out[metric['id']]={}
        for t in profiles:
            out[metric['id']][t['id']]={}
            for z in zones:
                out[metric['id']][t['id']][z['id']]=min(1,max(0,abs(values[j]['pmv'])-threshold));j+=1
    return out


def _assignment(counts,capacities,loss,allowed,ceiling=None):
    # Integer min-cost flow, Bellman-Ford residual graph. Costs are normalized per person.
    tnum=len(counts);znum=len(capacities);N=1+tnum+znum+1;source=0;sink=N-1
    graph=[[] for _ in range(N)]
    def edge(u,v,cap,cost):
        graph[u].append([v,len(graph[v]),cap,cost]);graph[v].append([u,len(graph[u])-1,0,-cost])
        return len(graph[u])-1
    links={}
    for i,c in enumerate(counts):edge(source,1+i,c,0)
    for i,c in enumerate(counts):
        for z in range(znum):
            if allowed[i][z] and (ceiling is None or loss[i][z]<=ceiling+1e-12):
                links[(i,z)]=(1+i,edge(1+i,1+tnum+z,c,loss[i][z]),c)
    for z,c in enumerate(capacities):edge(1+tnum+z,sink,c,0)
    flow=0;cost=0
    while flow<sum(counts):
        dist=[float('inf')]*N;prev=[None]*N;dist[source]=0
        for _ in range(N-1):
            changed=False
            for u in range(N):
                if not math.isfinite(dist[u]):continue
                for ei,e in enumerate(graph[u]):
                    v,_,cap,price=e
                    if cap and dist[u]+price<dist[v]-1e-12:
                        dist[v]=dist[u]+price;prev[v]=(u,ei);changed=True
            if not changed:break
        if prev[sink] is None:return {'feasible':False,'loss':None,'reason':'No full assignment satisfies capacity, access and loss ceiling'}
        amount=sum(counts)-flow;v=sink
        while v!=source:
            u,ei=prev[v];amount=min(amount,graph[u][ei][2]);v=u
        v=sink
        while v!=source:
            u,ei=prev[v];e=graph[u][ei];e[2]-=amount;graph[v][e[1]][2]+=amount;cost+=amount*e[3];v=u
        flow+=amount
    allocation=[[0]*znum for _ in counts]
    for (i,z),(u,ei,c) in links.items():allocation[i][z]=c-graph[u][ei][2]
    burdens=[sum(allocation[i][z]*loss[i][z] for z in range(znum)) for i in range(tnum)]
    return {'feasible':True,'loss':cost/sum(counts),'allocation':allocation,'type_loss':[burdens[i]/c if c else None for i,c in enumerate(counts)],'worst_type_loss':max((burdens[i]/c for i,c in enumerate(counts) if c),default=0)}


def _select(rows,scenarios,designs,metric):
    scores={}
    for d in designs:
        subset=[r for r in rows if r['design']==d and r['scenario'] in scenarios]
        scores[d]=max(r[metric] for r in subset) if len(subset)==len(scenarios) and all(r['feasible'] for r in subset) else None
    valid=[v for v in scores.values() if v is not None]
    return {'winners':[d for d,v in scores.items() if v is not None and abs(v-min(valid))<=1e-10] if valid else [],'scores':scores}


def _evaluate(p,metric_scores):
    zs=[z['id'] for z in p['zones']];ts=[t['id'] for t in p['profiles']];ds=[d['id'] for d in p['designs']]
    weights={m['id']:m['weight'] for m in p['metrics']}
    allowed=[[z in t['allowed_zones'] for z in zs] for t in p['profiles']]
    rows=[]
    for s in p['scenarios']:
        group=[];counts=[s['counts'][t] for t in ts]
        for d in p['designs']:
            effective=p.get('design_scores',{}).get(d['id'],metric_scores)
            combined=[[sum(weights[m]*effective[m][t][z] for m in weights) for z in zs] for t in ts]
            capacities=[d['capacity'][z] for z in zs]
            row=_assignment(counts,capacities,combined,allowed,p.get('max_individual_loss'))
            row.update(design=d['id'],scenario=s['id'],split=s['split'])
            if row['feasible']:
                row['metric_losses']={m:sum(row['allocation'][i][j]*effective[m][t][z] for i,t in enumerate(ts) for j,z in enumerate(zs))/p['total_people'] for m in weights}
            group.append(row)
        best=min((x['loss'] for x in group if x['feasible']),default=None)
        for row in group:row['regret']=row['loss']-best if row['feasible'] else None
        rows.extend(group)
    dev=[s['id'] for s in p['scenarios'] if s['split']=='development'];hold=[s['id'] for s in p['scenarios'] if s['split']=='holdout']
    selection={'existing':[p['existing_design']], 'baseline':_select(rows,[p['baseline_scenario']],ds,'loss'), 'minimax_regret':_select(rows,dev,ds,'regret'), 'minimax_loss':_select(rows,dev,ds,'loss'), 'holdout':_select(rows,hold,ds,'regret')}
    return rows,selection


def analyze(project,uncertainty=True):
    p=validate(project);scores=_metric_scores(p);rows,selection=_evaluate(p,scores)
    worlds=[]
    if uncertainty:
        for world in p.get('score_worlds',[]):
            wr,ws=_evaluate(p,world['scores'])
            worlds.append({'id':world['id'],'development_winners':ws['minimax_regret']['winners'],'holdout_max_regret':ws['holdout']['scores']})
    digest=sha256(json.dumps(p,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
    return {'schema_version':2,'software_version':__version__,'project':p,'input_sha256':digest,'metric_scores':scores,'rows':rows,'selection':selection,'score_worlds':worlds,'engine':provenance() if any(m['kind']=='cbe_pmv' for m in p['metrics']) else {'mode':'direct loss tables'},'interpretation':'Zone-capacity comparison under ideal managed matching. Plan evidence and field validity must be reviewed separately.'}
