"""Rebuild the revised A3 comparison and figures from the declared project."""
from collections import Counter
import csv
from itertools import product
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from peoplecomfort.core import analyze


def ppd_rows(project,thermal):
    lookup={(r['type'],r['zone']):r['output']['ppd'] for r in thermal}
    zones=[z['id'] for z in project['zones']]
    rows=[]
    for scenario in project['scenarios']:
        counts=[scenario['counts'][t['id']] for t in project['profiles']]
        occupied=sum(counts)
        for design in project['designs']:
            possibilities=[]
            for first_zone in product(*(range(c+1) for c in counts)):
                if sum(first_zone)>design['seats'][zones[0]] or occupied-sum(first_zone)>design['seats'][zones[1]]:
                    continue
                if any((first_zone[i] and zones[0] not in t['allowed_zones']) or
                       (counts[i]-first_zone[i] and zones[1] not in t['allowed_zones'])
                       for i,t in enumerate(project['profiles'])):
                    continue
                loss=sum(first_zone[i]*lookup[t['id'],zones[0]]+
                         (counts[i]-first_zone[i])*lookup[t['id'],zones[1]]
                         for i,t in enumerate(project['profiles']))/occupied
                possibilities.append(loss)
            rows.append({'scenario':scenario['id'],'design':design['id'],
                         'mean_ppd':min(possibilities) if possibilities else None})
    return rows


def max_regret(rows,scenarios,designs,field):
    by_scenario={s: min(r[field] for r in rows if r['scenario']==s and r[field] is not None) for s in scenarios}
    return {d:max(next(r[field] for r in rows if r['scenario']==s and r['design']==d)-by_scenario[s]
                  for s in scenarios) for d in designs}


def figures(project,result,ppd,summary):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10})
    out=ROOT/'coursework'
    ds=project['designs'];ss=project['scenarios'];ids=[d['id'] for d in ds]
    fig,ax=plt.subplots(figsize=(10,4),layout='constrained')
    positions=np.arange(len(ds));cool=[d['seats']['Z1'] for d in ds]
    ax.bar(positions,cool,color='#397d83',label='Z1 cooler')
    ax.bar(positions,[12-v for v in cool],bottom=cool,color='#c69155',label='Z2 warmer')
    ax.set_xticks(positions,[d['id']+'\n'+str(d['seats']['Z1'])+'/'+str(d['seats']['Z2']) for d in ds]);ax.set_ylim(0,13);ax.set_ylabel('Capacity units');ax.legend(ncol=2,frameon=False)
    ax.set_title('Seven feasible capacity alternatives in one fixed two-zone abstraction')
    fig.savefig(out/'figure_extended_designs.png',dpi=180);plt.close(fig)
    values=np.array([[next(r['loss'] for r in result['rows'] if r['scenario']==s['id'] and r['design']==d) for d in ids] for s in ss])
    fig,ax=plt.subplots(figsize=(10,7),layout='constrained')
    im=ax.imshow(values,cmap='YlGnBu',aspect='auto')
    ax.set_xticks(range(len(ids)),ids);ax.set_yticks(range(len(ss)),[s['id']+' ('+'/'.join(map(str,s['counts'].values()))+')' for s in ss]);ax.axhline(2.5,color='white',linewidth=2)
    for i in range(len(ss)):
        for j in range(len(ids)):
            ax.text(j,i,f'{values[i,j]:.3f}',ha='center',va='center',fontsize=7,color='white' if values[i,j]>.22 else '#173d38')
    fig.colorbar(im,ax=ax,label='Mean PMV exceedance',shrink=.8)
    ax.set_title('Development S0-S2; H0-H9 held out, including extremes and 8-person occupancy')
    fig.savefig(out/'figure_extended_matrix.png',dpi=180);plt.close(fig)
    counts=Counter(d for w in result['uncertainty'] for d in w['development_winners'])
    fig,axes=plt.subplots(1,2,figsize=(10,3.7),layout='constrained')
    axes[0].bar(ids,[counts[d] for d in ids],color=['#8baea7' if d!='D4' else '#267466' for d in ids]);axes[0].set_ylabel('Winner count / 81 stress conditions');axes[0].set_title('No single stable winner')
    axes[1].bar(['D0 existing','D4 robust'],[summary['holdout_max_regret']['D0'],summary['holdout_max_regret']['D4']],color=['#8baea7','#267466']);axes[1].set_ylabel('Maximum holdout regret');axes[1].set_title('Extended holdout comparison')
    fig.savefig(out/'figure_extended_decision.png',dpi=180);plt.close(fig)


def main():
    project=json.loads((ROOT/'examples/extended-a3/project.json').read_text(encoding='utf-8'))
    result=analyze(project,True)
    ppd=ppd_rows(project,result['thermal_ledger'])
    ids=[d['id'] for d in project['designs']]
    dev=[s['id'] for s in project['scenarios'] if s['split']=='development']
    hold=[s['id'] for s in project['scenarios'] if s['split']=='holdout']
    ppd_development=max_regret(ppd,dev,ids,'mean_ppd')
    ppd_holdout=max_regret(ppd,hold,ids,'mean_ppd')
    chosen=result['selection']['T3']['winners']
    if len(chosen)!=1:raise ValueError('This report expects one nominal robust winner; report ties separately')
    selected=chosen[0];existing=project['existing_design']
    holdout=result['selection']['holdout']['scores']
    relative=(holdout[existing]-holdout[selected])/holdout[existing]
    rule=project['design_action_rule']
    comparable=sum(w['holdout_regret_by_design'][selected] <= w['holdout_regret_by_design'][existing]+rule['stress_tolerance'] for w in result['uncertainty'])
    stress_counts={str(t):sum(w['holdout_regret_by_design'][selected] <= w['holdout_regret_by_design'][existing]+t for w in result['uncertainty']) for t in (0.01,0.02)}
    holdout_rows=[r for r in result['rows'] if r['scenario'] in hold]
    mean_holdout_regret={d:sum(r['regret'] for r in holdout_rows if r['design']==d)/len(hold) for d in ids}
    holdout_pair_wins={selected:sum(next(r['regret'] for r in holdout_rows if r['scenario']==s and r['design']==selected)<next(r['regret'] for r in holdout_rows if r['scenario']==s and r['design']==existing)-1e-12 for s in hold)}
    best_development=min(result['selection']['T3']['scores'].values())
    near_optimal=[d for d,v in result['selection']['T3']['scores'].items() if v<=best_development+0.01+1e-12]
    action=relative >= rule['minimum_relative_improvement'] and comparable/len(result['uncertainty']) >= rule['stress_noninferiority_fraction']
    summary={'input_sha256':result['input_sha256'],'development_winner':selected,
             'baseline_winner':result['selection']['T2']['winners'],
             'development_max_regret':result['selection']['T3']['scores'],
             'holdout_max_regret':holdout,'relative_improvement_vs_existing':relative,
             'mean_holdout_regret':mean_holdout_regret,'holdout_pair_wins':holdout_pair_wins,
             'near_optimal_development_0_01':near_optimal,'stress_noninferiority_by_tolerance':stress_counts,
             'stress_winner_counts':dict(Counter(d for w in result['uncertainty'] for d in w['development_winners'])),
             'stress_noninferiority_count':comparable,'stress_total':len(result['uncertainty']),
             'action_rule':rule,'action_rule_passed':action,
             'ppd_development_max_regret':ppd_development,'ppd_holdout_max_regret':ppd_holdout,
             'ppd_development_winner':min(ppd_development,key=ppd_development.get),
             'ppd_holdout_winner':min(ppd_holdout,key=ppd_holdout.get)}
    out=ROOT/'coursework';out.mkdir(exist_ok=True)
    (out/'extended_results.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    with (out/'extended_matrix.csv').open('w',newline='',encoding='utf-8') as handle:
        writer=csv.DictWriter(handle,fieldnames=['scenario','split','occupied_people','design','loss','regret','mean_ppd']);writer.writeheader()
        for r in result['rows']:
            writer.writerow({k:(next(x['mean_ppd'] for x in ppd if x['scenario']==r['scenario'] and x['design']==r['design']) if k=='mean_ppd' else r[k]) for k in writer.fieldnames})
    figures(project,result,ppd,summary)
    print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
