const ORIGINAL=JSON.parse(document.getElementById('project-data').textContent);
let project=structuredClone(ORIGINAL);
const $=id=>document.getElementById(id);
const esc=x=>String(x).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const fmt=x=>x==null?'Infeasible':Number(x).toFixed(4);
const get=(o,path)=>path.reduce((v,k)=>v[k],o);
function setStatus(message,error=false){$('status').textContent=message;$('status').className='status'+(error?' error':'');}
function leaf(value,path,key){
  const label=esc(key),id='f-'+path.map(x=>String(x).replace(/[^a-zA-Z0-9]/g,'_')).join('-');
  const type=typeof value;
  const choices={capacity_policy:['equal_total','variable_total'],allocation_rule:['optimal','priority_first_fit'],decision_rule:['baseline','minimax_regret','minimax_loss'],kind:key==='kind'&&path[0]==='plan'?['schematic','measured']:['direct','cbe_pmv'],split:['development','holdout']};
  const control=type==='boolean'?`<select id="${id}" data-path="${esc(JSON.stringify(path))}" data-type="boolean"><option value="true"${value?' selected':''}>true</option><option value="false"${!value?' selected':''}>false</option></select>`:
    type==='number'?`<input id="${id}" data-path="${esc(JSON.stringify(path))}" data-type="number" type="number" step="any" value="${value}">`:
    choices[key]?`<select id="${id}" data-path="${esc(JSON.stringify(path))}" data-type="string">${choices[key].map(x=>`<option value="${x}"${value===x?' selected':''}>${x}</option>`).join('')}</select>`:
    `<input id="${id}" data-path="${esc(JSON.stringify(path))}" data-type="string" type="text" value="${esc(value===null?'':value)}">`;
  return `<div class="field${String(value).length>50?' wide':''}"><label for="${id}">${label}</label>${control}</div>`;
}
function node(value,path,key){
  if(value===null||typeof value!=='object')return leaf(value,path,key);
  if(Array.isArray(value)){
    const items=value.map((item,i)=>`<div class="entity"><div class="entity-title">${esc(item?.id||item?.name||key+' '+(i+1))}<button class="danger" type="button" data-remove="${esc(JSON.stringify([...path,i]))}">Remove</button></div>${node(item,[...path,i],key+' '+(i+1))}</div>`).join('');
    const itemNames={zones:'zone',profiles:'profile',metrics:'metric',designs:'design',scenarios:'scenario',score_worlds:'score world',allowed_zones:'allowed zone'};
    return `<div class="section"><h3>${esc(key)} <small>(${value.length})</small></h3>${items}<div class="toolbar"><button type="button" data-add="${esc(JSON.stringify(path))}">Add ${esc(itemNames[path.at(-1)]||'item')}</button></div></div>`;
  }
  const entries=Object.entries(value);
  const simple=entries.filter(([,v])=>v===null||typeof v!=='object').map(([k,v])=>node(v,[...path,k],k)).join('');
  const nested=entries.filter(([,v])=>v!==null&&typeof v==='object').map(([k,v])=>`<div class="nested"><div class="nested-title">${esc(k)}</div>${node(v,[...path,k],k)}</div>`).join('');
  return `<div class="fields">${simple}</div>${nested}`;
}
const OPTIONAL={capacity_policy:'equal_total',allocation_rule:'optimal',decision_rule:'minimax_regret',allow_partial_occupancy:false,max_individual_loss:1,design_scores_source:'Document the evidence for design-specific scores',design_scores:null,score_worlds:[],plan:{kind:'schematic',source:'Document plan source'}};
function renderEditor(){
  const meta=Object.fromEntries(Object.entries(project).filter(([k])=>!['zones','profiles','metrics','designs','scenarios','score_worlds','design_scores'].includes(k)));
  const sections=[['Project and rules',meta],['Space: zones',project.zones],['Users: profiles',project.profiles],['Evaluation: metrics and score matrices',project.metrics],['Design: capacities',project.designs],['Demand: scenarios',project.scenarios],['Verification: score worlds',project.score_worlds||[]]];
  let html=sections.map(([name,v],i)=>`<div class="section"><h3>${esc(name)}</h3>${i===0?node(v,[],name):node(v,[['zones','profiles','metrics','designs','scenarios','score_worlds'][i-1]],name)}</div>`).join('');
  if(project.design_scores)html+=`<div class="section"><h3>Design-specific scores</h3>${node(project.design_scores,['design_scores'],'design_scores')}</div>`;
  const missing=Object.keys(OPTIONAL).filter(k=>!(k in project));
  html+=`<div class="section"><h3>Optional schema fields</h3><div class="toolbar">${missing.map(k=>`<button type="button" data-optional="${k}">Add ${k}</button>`).join('')||'<span class="small">All optional fields shown.</span>'}</div></div>`;
  $('editor').innerHTML=html;$('json').value=JSON.stringify(project,null,2);
}
function minCostAssignment(counts,capacities,costs,allowed,ceiling){
  const t=counts.length,z=capacities.length,n=2+t+z,source=0,sink=n-1,graph=Array.from({length:n},()=>[]),links=[];
  function edge(u,v,cap,cost){const i=graph[u].length,j=graph[v].length;graph[u].push({to:v,rev:j,cap,cost});graph[v].push({to:u,rev:i,cap:0,cost:-cost});return i;}
  counts.forEach((c,i)=>edge(source,1+i,c,0));
  counts.forEach((c,i)=>capacities.forEach((_,j)=>{if(allowed[i][j]&&(ceiling==null||costs[i][j]<=ceiling+1e-12))links.push({i,j,u:1+i,e:edge(1+i,1+t+j,c,costs[i][j]),original:c});}));
  capacities.forEach((c,j)=>edge(1+t+j,sink,c,0));
  let flow=0,total=0,target=counts.reduce((a,b)=>a+b,0);
  while(flow<target){const dist=Array(n).fill(Infinity),prev=Array(n).fill(null);dist[source]=0;
    for(let pass=0;pass<n-1;pass++){let changed=false;for(let u=0;u<n;u++){if(!Number.isFinite(dist[u]))continue;graph[u].forEach((e,k)=>{const v=dist[u]+e.cost;if(e.cap>0&&v<dist[e.to]-1e-12){dist[e.to]=v;prev[e.to]=[u,k];changed=true;}});}if(!changed)break;}
    if(!prev[sink])return {feasible:false,loss:null};
    let amount=target-flow;for(let v=sink;v!==source;){const [u,k]=prev[v];amount=Math.min(amount,graph[u][k].cap);v=u;}
    for(let v=sink;v!==source;){const [u,k]=prev[v],e=graph[u][k];e.cap-=amount;graph[v][e.rev].cap+=amount;total+=amount*e.cost;v=u;}flow+=amount;
  }
  const allocation=counts.map(()=>capacities.map(()=>0));links.forEach(a=>allocation[a.i][a.j]=a.original-graph[a.u][a.e].cap);
  return {feasible:true,loss:total/target,allocation};
}
function firstFit(counts,capacities,costs,allowed,ceiling){
  const remaining=capacities.slice(),allocation=counts.map(()=>capacities.map(()=>0));
  for(let i=0;i<counts.length;i++){let left=counts[i];const choices=capacities.map((_,z)=>z).filter(z=>allowed[i][z]&&(ceiling==null||costs[i][z]<=ceiling+1e-12)).sort((a,b)=>costs[i][a]-costs[i][b]||a-b);
    for(const z of choices){const take=Math.min(left,remaining[z]);allocation[i][z]=take;remaining[z]-=take;left-=take;if(!left)break;}if(left)return {feasible:false,loss:null};
  }
  let total=0;allocation.forEach((a,i)=>a.forEach((n,z)=>total+=n*costs[i][z]));return {feasible:true,loss:total/counts.reduce((a,b)=>a+b,0),allocation};
}
function validate(p){
  if(p.schema_version!==2)throw Error('schema_version must be 2.');
  for(const [key,min,max] of [['zones',2,8],['profiles',1,8],['metrics',1,5],['designs',3,20],['scenarios',2,100]])if(!Array.isArray(p[key])||p[key].length<min||p[key].length>max)throw Error(`${key} must contain ${min}–${max} items.`);
  if(!Number.isInteger(p.total_people)||p.total_people<1||p.total_people>80)throw Error('total_people must be an integer from 1 to 80.');
  if(p.allow_partial_occupancy!==undefined&&typeof p.allow_partial_occupancy!=='boolean')throw Error('allow_partial_occupancy must be true or false.');
  const ids={};for(const key of ['zones','profiles','metrics','designs','scenarios']){ids[key]=p[key].map(x=>x.id);if(ids[key].some(x=>typeof x!=='string'||!x)||new Set(ids[key]).size!==ids[key].length)throw Error(`${key} IDs must be unique nonempty strings.`);}
  if(!['equal_total','variable_total'].includes(p.capacity_policy||'equal_total'))throw Error('Invalid capacity_policy.');
  if(!['optimal','priority_first_fit'].includes(p.allocation_rule||'optimal'))throw Error('Invalid allocation_rule.');
  if(!['baseline','minimax_regret','minimax_loss'].includes(p.decision_rule||'minimax_regret'))throw Error('Invalid decision_rule.');
  if(p.plan&&(!['schematic','measured'].includes(p.plan.kind)||!p.plan.source||(p.plan.kind==='measured'&&!p.plan.scale)))throw Error('Plan needs kind, source and measured scale.');
  const zones=ids.zones,profiles=ids.profiles,metrics=ids.metrics;
  for(const z of p.zones)if(!Number.isInteger(z.max_capacity)||z.max_capacity<0||!z.source)throw Error(`Invalid maximum capacity or source in ${z.id}.`);
  for(const t of p.profiles)if(!Array.isArray(t.allowed_zones)||!t.allowed_zones.length||t.allowed_zones.some(z=>!zones.includes(z))||!t.source)throw Error(`Invalid allowed zones or source in ${t.id}.`);
  for(const d of p.designs){if(!d.capacity||Object.keys(d.capacity).length!==zones.length||zones.some(z=>!Number.isInteger(d.capacity[z])||d.capacity[z]<0||d.capacity[z]>p.zones.find(v=>v.id===z).max_capacity))throw Error(`Invalid zone capacities in ${d.id}.`);if((p.capacity_policy||'equal_total')==='equal_total'&&Object.values(d.capacity).reduce((a,b)=>a+b,0)!==p.total_people)throw Error(`${d.id} capacities must total ${p.total_people} under equal_total.`);}
  for(const s of p.scenarios){const occupied=Object.values(s.counts||{}).reduce((a,b)=>a+b,0);if(!['development','holdout'].includes(s.split)||!s.counts||Object.keys(s.counts).length!==profiles.length||profiles.some(t=>!Number.isInteger(s.counts[t])||s.counts[t]<0)||!(p.allow_partial_occupancy?occupied>=1&&occupied<=p.total_people:occupied===p.total_people))throw Error(`Invalid split or counts in ${s.id}; occupancy must ${p.allow_partial_occupancy?'be 1–':'total '}${p.total_people}.`);}
  if(!p.scenarios.some(s=>s.split==='development')||!p.scenarios.some(s=>s.split==='holdout'))throw Error('Need development and holdout scenarios.');
  if(!ids.designs.includes(p.existing_design)||!p.scenarios.some(s=>s.id===p.baseline_scenario&&s.split==='development'))throw Error('Invalid existing_design or baseline_scenario.');
  if(Math.abs(p.metrics.reduce((a,m)=>a+m.weight,0)-1)>1e-9)throw Error('Metric weights must sum to 1.');
  for(const m of p.metrics){if(!m.source||!Number.isFinite(m.weight)||m.weight<0||m.weight>1)throw Error(`Invalid source or weight in ${m.id}.`);if(m.kind==='direct')checkScores(m.scores,profiles,zones,`Metric ${m.id}`);else if(m.kind==='cbe_pmv'){
      if(!Number.isFinite(m.threshold)||m.threshold<.1||m.threshold>1)throw Error(`${m.id}: PMV threshold must be 0.1–1.`);
      for(const z of p.zones)for(const [k,lo,hi] of [['ta',15,32],['tr',15,40],['v',0,1],['rh',10,90]])if(!Number.isFinite(z[k])||z[k]<lo||z[k]>hi)throw Error(`${z.id}: ${k} must be ${lo}–${hi}.`);
      for(const t of p.profiles)for(const [k,lo,hi] of [['met',1,2],['clo',.2,1.5]])if(!Number.isFinite(t[k])||t[k]<lo||t[k]>hi)throw Error(`${t.id}: ${k} must be ${lo}–${hi}.`);
    }else throw Error(`Invalid metric kind in ${m.id}.`);}
  if(p.max_individual_loss!==undefined&&(!Number.isFinite(p.max_individual_loss)||p.max_individual_loss<0||p.max_individual_loss>1))throw Error('max_individual_loss must be 0–1.');
  if(p.design_scores){if(p.score_worlds?.length)throw Error('design_scores and score_worlds cannot be combined.');if(!p.design_scores_source||Object.keys(p.design_scores).length!==ids.designs.length)throw Error('design_scores need a source and every design.');for(const d of ids.designs){if(Object.keys(p.design_scores[d]||{}).length!==metrics.length)throw Error(`Incomplete design_scores for ${d}.`);for(const m of metrics)checkScores(p.design_scores[d][m],profiles,zones,`${d}/${m}`);}}
  if((p.score_worlds||[]).length>30)throw Error('At most 30 score worlds.');for(const w of p.score_worlds||[]){if(!w.id||Object.keys(w.scores||{}).length!==metrics.length)throw Error('World needs ID and every metric.');for(const m of metrics)checkScores(w.scores[m],profiles,zones,`${w.id}/${m}`);}
}
function checkScores(scores,profiles,zones,label){if(!scores||Object.keys(scores).length!==profiles.length)throw Error(`${label}: score table must cover every profile.`);for(const t of profiles){if(!scores[t]||Object.keys(scores[t]).length!==zones.length)throw Error(`${label}: missing zone score for ${t}.`);for(const z of zones)if(!Number.isFinite(scores[t][z])||scores[t][z]<0||scores[t][z]>1)throw Error(`${label}: ${t}/${z} score must be 0–1.`);}}
function metricScores(p){
  const scores={},ledger=[];
  for(const m of p.metrics){if(m.kind==='direct'){scores[m.id]=m.scores;continue;}
    if(typeof comf==='undefined'||typeof comf.pmvElevatedAirspeed!=='function')throw Error('CBE calculation scripts did not load.');
    comf.useSelfGeneratedAirSpeed=true;scores[m.id]={};
    for(const t of p.profiles){scores[m.id][t.id]={};for(const z of p.zones){
      const result=comf.pmvElevatedAirspeed(z.ta,z.tr,z.v,z.rh,t.met,t.clo,0);
      if(!Number.isFinite(result.pmv)||!Number.isFinite(result.ppd))throw Error(`CBE calculation failed for ${t.id}/${z.id}.`);
      const loss=Math.min(1,Math.max(0,Math.abs(result.pmv)-m.threshold));
      scores[m.id][t.id][z.id]=loss;
      ledger.push({metric:m.id,profile:t.id,zone:z.id,pmv:result.pmv,ppd:result.ppd,loss,ta:z.ta,tr:z.tr,v:z.v,rh:z.rh,met:t.met,clo:t.clo});
    }}
  }
  return {scores,ledger};
}
function winners(designs,values){const valid=values.filter(x=>x!==null&&Number.isFinite(x));if(!valid.length)return[];const best=Math.min(...valid);return designs.filter((_,i)=>values[i]!==null&&Math.abs(values[i]-best)<1e-10).map(d=>d.id);}
function evaluate(p,computed,override){const zs=p.zones.map(x=>x.id),ts=p.profiles.map(x=>x.id),ds=p.designs,allowed=p.profiles.map(t=>zs.map(z=>t.allowed_zones.includes(z)));
  const base=override||computed.scores;
  const rows=p.scenarios.map(s=>{const counts=ts.map(t=>s.counts[t]);const out=ds.map(d=>{const scores=p.design_scores?.[d.id]||base,costs=ts.map(t=>zs.map(z=>p.metrics.reduce((a,m)=>a+m.weight*scores[m.id][t][z],0))),caps=zs.map(z=>d.capacity[z]);const o=(p.allocation_rule||'optimal')==='optimal'?minCostAssignment(counts,caps,costs,allowed,p.max_individual_loss):firstFit(counts,caps,costs,allowed,p.max_individual_loss);if(o.feasible)o.type_loss=counts.map((n,i)=>n?o.allocation[i].reduce((a,c,z)=>a+c*costs[i][z],0)/n:null);return o;});const feasible=out.filter(x=>x.feasible).map(x=>x.loss),best=feasible.length?Math.min(...feasible):null;return {scenario:s,out:out.map(o=>({...o,regret:o.feasible?o.loss-best:null}))};});
  const dev=rows.filter(r=>r.scenario.split==='development'),hold=rows.filter(r=>r.scenario.split==='holdout'),baseRow=dev.find(r=>r.scenario.id===p.baseline_scenario);
  const score=(subset,field)=>ds.map((_,i)=>subset.length&&subset.every(r=>r.out[i].feasible)?Math.max(...subset.map(r=>r.out[i][field])):null);
  const baseline=score([baseRow],'loss'),regret=score(dev,'regret'),maxloss=score(dev,'loss'),holdout=score(hold,'regret');
  return {rows,baseline,regret,maxloss,holdout,baselineWinners:winners(ds,baseline),regretWinners:winners(ds,regret),maxlossWinners:winners(ds,maxloss),thermal:computed.ledger};
}
function clearResults(){for(const id of ['decision','designs','bars','matrix-head','matrix-body','burden','worlds','rule-note','thermal-ledger'])$(id).innerHTML='';}
function renderResults(p,r,computed){const rule=p.decision_rule||'minimax_regret',selected=rule==='baseline'?r.baselineWinners:rule==='minimax_loss'?r.maxlossWinners:r.regretWinners;
  const cards=[['Existing',p.existing_design,'Reference'],['Baseline',r.baselineWinners.join(' / ')||'Unresolved',p.baseline_scenario],['Minimax regret',r.regretWinners.join(' / ')||'Unresolved','Development'],['Minimax loss',r.maxlossWinners.join(' / ')||'Unresolved','Development'],['Selected rule',selected.join(' / ')||'Unresolved',rule],['Holdout max regret',selected.map(id=>fmt(r.holdout[p.designs.findIndex(d=>d.id===id)])).join(' / ')||'Unresolved','Frozen selection']];
  $('decision').innerHTML=cards.map(([name,value,note])=>`<div${name==='Selected rule'?' class="selected"':''}><small>${esc(name)}</small><b>${esc(value)}</b><small>${esc(note)}</small></div>`).join('');
  $('rule-note').textContent=`Allocation: ${p.allocation_rule||'optimal'} · Capacity policy: ${p.capacity_policy||'equal_total'} · Lower loss is better. Ties are preserved.`;
  $('designs').innerHTML=p.designs.map(d=>`<div${selected.includes(d.id)?' class="selected"':''}><b>${esc(d.id)}</b><small>${esc(d.name||'')}</small><div>${p.zones.map(z=>`${esc(z.id)}: ${d.capacity[z.id]}`).join(' · ')}</div><small>Total: ${Object.values(d.capacity).reduce((a,b)=>a+b,0)}</small></div>`).join('');
  const base=r.rows.find(x=>x.scenario.id===p.baseline_scenario),max=Math.max(.001,...base.out.filter(o=>o.feasible).map(o=>o.loss));
  $('bars').innerHTML=base.out.map((o,i)=>`<div class="bar-row"><span>${esc(p.designs[i].id)}</span><i style="width:${o.feasible?Math.max(2,65*o.loss/max):0}%"></i><b>${fmt(o.loss)}</b></div>`).join('');
  $('matrix-head').innerHTML='<tr><th>Scenario</th>'+p.designs.map(d=>`<th>${esc(d.id)}</th>`).join('')+'</tr>';
  $('matrix-body').innerHTML=r.rows.map(row=>`<tr><td>${esc(row.scenario.id)} · ${esc(row.scenario.name||'')} ${row.scenario.split==='holdout'?'(holdout)':''}</td>${row.out.map(o=>`<td>${fmt(o.loss)}</td>`).join('')}</tr>`).join('');
  $('burden').innerHTML=selected.map(id=>{const i=p.designs.findIndex(d=>d.id===id),o=base.out[i];return `<p><strong>${esc(id)} in ${esc(p.baseline_scenario)}:</strong> ${o.feasible?p.profiles.map((t,j)=>`${esc(t.id)} ${fmt(o.type_loss[j])}`).join(' · '):'Infeasible'}</p>`;}).join('')||'<p>Unresolved selection.</p>';
  $('thermal-ledger').innerHTML=r.thermal.length?'<table><thead><tr><th>Profile</th><th>Zone</th><th>PMV</th><th>PPD %</th><th>Exceedance loss</th></tr></thead><tbody>'+r.thermal.map(x=>`<tr><td>${esc(x.profile)}</td><td>${esc(x.zone)}</td><td>${x.pmv.toFixed(3)}</td><td>${x.ppd.toFixed(1)}</td><td>${x.loss.toFixed(3)}</td></tr>`).join('')+'</tbody></table><p class="small">CBE pmvElevatedAirspeed; self-generated air speed on; external work = 0. Source and GPL-2.0 notice are in the bundled CBE files.</p>':'<p class="small">No CBE PMV metric in this project.</p>';
  if(p.score_worlds?.length){const worlds=p.score_worlds.map(w=>({id:w.id,result:evaluate(p,computed,w.scores)}));$('worlds').innerHTML='<h3>Score-world sensitivity</h3><div class="table-wrap"><table><thead><tr><th>World</th><th>Minimax-regret winner</th><th>Selected-design holdout regret</th></tr></thead><tbody>'+worlds.map(w=>`<tr><td>${esc(w.id)}</td><td>${esc(w.result.regretWinners.join(' / ')||'Unresolved')}</td><td>${esc(selected.map(id=>fmt(w.result.holdout[p.designs.findIndex(d=>d.id===id)])).join(' / '))}</td></tr>`).join('')+'</tbody></table></div>';}
  else $('worlds').innerHTML='<p class="small">No score worlds supplied. Add complete alternate score matrices to examine uncertainty.</p>';
  window.peoplecomfortDemo={project:structuredClone(p),result:r};
}
function refresh(edit=true){if(edit)renderEditor();try{validate(project);const computed=metricScores(project),r=evaluate(project,computed);renderResults(project,r,computed);setStatus(`Valid project · ${project.zones.length} zones · ${project.profiles.length} profiles · ${project.designs.length} designs · ${project.scenarios.length} scenarios.`);}catch(e){clearResults();setStatus(e.message,true);}}
$('editor').addEventListener('change',event=>{const el=event.target;if(!el.dataset.path)return;const path=JSON.parse(el.dataset.path);const value=el.dataset.type==='number'?(el.value.trim()===''?NaN:Number(el.value)):el.dataset.type==='boolean'?el.value==='true':el.value;get(project,path.slice(0,-1))[path.at(-1)]=value;$('json').value=JSON.stringify(project,null,2);try{validate(project);const computed=metricScores(project);renderResults(project,evaluate(project,computed),computed);setStatus('Valid project · PMV and results updated.');}catch(e){clearResults();setStatus(e.message,true);}});
$('editor').addEventListener('click',event=>{const el=event.target;if(el.dataset.remove){const path=JSON.parse(el.dataset.remove),arr=get(project,path.slice(0,-1));arr.splice(path.at(-1),1);refresh();}else if(el.dataset.add){const path=JSON.parse(el.dataset.add),arr=get(project,path),kind=path[0];let item;if(kind==='zones')item={id:`Z${arr.length+1}`,name:'New zone',max_capacity:project.total_people,source:'Document source',ta:25,tr:25,v:.1,rh:50};else if(kind==='profiles')item={id:`P${arr.length+1}`,name:'New profile',allowed_zones:project.zones.map(z=>z.id),source:'Document source',met:1.2,clo:.5};else if(kind==='designs')item={id:`D${arr.length}`,name:'New design',capacity:Object.fromEntries(project.zones.map(z=>[z.id,0]))};else if(kind==='scenarios')item={id:`S${arr.length}`,name:'New scenario',split:'development',counts:Object.fromEntries(project.profiles.map(t=>[t.id,0]))};else if(kind==='metrics')item={id:`metric_${arr.length+1}`,name:'New metric',kind:'cbe_pmv',weight:0,threshold:.5,source:'Document source'};else if(kind==='score_worlds')item={id:`W${arr.length+1}`,scores:structuredClone(metricScores(project).scores)};else item=arr.length?structuredClone(arr.at(-1)):'';arr.push(item);refresh();}else if(el.dataset.optional){const k=el.dataset.optional;project[k]=k==='design_scores'?Object.fromEntries(project.designs.map(d=>[d.id,structuredClone(metricScores(project).scores)])):structuredClone(OPTIONAL[k]);refresh();}});
$('reset').addEventListener('click',()=>{project=structuredClone(ORIGINAL);refresh();});
$('apply-json').addEventListener('click',()=>{try{const next=JSON.parse($('json').value);if(!next||typeof next!=='object'||Array.isArray(next))throw Error('Expected a project object.');project=next;refresh();}catch(e){setStatus(`JSON parse error: ${e.message}`,true);}});
$('copy-json').addEventListener('click',async()=>{try{await navigator.clipboard.writeText($('json').value);setStatus('Project JSON copied.');}catch(e){setStatus('Clipboard unavailable; select and copy the JSON text.',true);}});
$('download').addEventListener('click',()=>{const data=new Blob([JSON.stringify(project,null,2)+'\n'],{type:'application/json'}),url=URL.createObjectURL(data),a=document.createElement('a');a.href=url;a.download='peoplecomfort-project.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});
$('upload').addEventListener('change',async e=>{const file=e.target.files[0];if(!file)return;try{project=JSON.parse(await file.text());refresh();}catch(err){setStatus(`Import failed: ${err.message}`,true);}e.target.value='';});
refresh();
