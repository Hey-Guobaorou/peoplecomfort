const BASE=JSON.parse(document.getElementById('project-data').textContent);
const $=id=>document.getElementById(id);
const fmt=x=>x==null?'Infeasible':x.toFixed(4);
function escapeHTML(v){return String(v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));}
function minCostAssignment(counts,capacities,costs,allowed){
  const t=counts.length,z=capacities.length,n=2+t+z,source=0,sink=n-1;
  const graph=Array.from({length:n},()=>[]),links=[];
  function edge(u,v,cap,cost){const i=graph[u].length,j=graph[v].length;graph[u].push({to:v,rev:j,cap,cost});graph[v].push({to:u,rev:i,cap:0,cost:-cost});return i;}
  counts.forEach((c,i)=>edge(source,1+i,c,0));
  counts.forEach((c,i)=>capacities.forEach((_,j)=>{if(allowed[i][j])links.push({i,j,u:1+i,e:edge(1+i,1+t+j,c,costs[i][j]),original:c});}));
  capacities.forEach((c,j)=>edge(1+t+j,sink,c,0));
  let flow=0,total=0,target=counts.reduce((a,b)=>a+b,0);
  while(flow<target){
    const distance=Array(n).fill(Infinity),previous=Array(n).fill(null);distance[source]=0;
    for(let pass=0;pass<n-1;pass++){let changed=false;for(let u=0;u<n;u++){if(!Number.isFinite(distance[u]))continue;graph[u].forEach((e,k)=>{const candidate=distance[u]+e.cost;if(e.cap>0&&candidate<distance[e.to]-1e-12){distance[e.to]=candidate;previous[e.to]=[u,k];changed=true;}});}if(!changed)break;}
    if(!previous[sink])return {feasible:false,loss:null};
    let amount=target-flow;for(let v=sink;v!==source;){const [u,k]=previous[v];amount=Math.min(amount,graph[u][k].cap);v=u;}
    for(let v=sink;v!==source;){const [u,k]=previous[v],e=graph[u][k];e.cap-=amount;graph[v][e.rev].cap+=amount;total+=amount*e.cost;v=u;}
    flow+=amount;
  }
  const allocation=counts.map(()=>capacities.map(()=>0));links.forEach(a=>allocation[a.i][a.j]=a.original-graph[a.u][a.e].cap);
  return {feasible:true,loss:total/target,allocation};
}
function projectFromControls(){
  const p=structuredClone(BASE),focus=Number($('focus').value),collab=Number($('collab').value),z1=Number($('z1').value),z3=Number($('z3').value),z2=12-z1-z3;
  p.scenarios[0].counts={P1:focus,P2:12-focus-collab,P3:collab};
  p.metrics[0].weight=Number($('weight').value)/100;p.metrics[1].weight=1-p.metrics[0].weight;
  p.designs.push({id:'D3',name:'Your configuration',capacity:{Z1:z1,Z2:z2,Z3:z3}});
  return p;
}
function evaluate(p){
  const zones=p.zones.map(z=>z.id),profiles=p.profiles.map(t=>t.id);
  const costs=profiles.map(t=>zones.map(z=>p.metrics.reduce((sum,m)=>sum+m.weight*m.scores[t][z],0)));
  const allowed=p.profiles.map(t=>zones.map(z=>t.allowed_zones.includes(z)));
  const rows=p.scenarios.map(s=>{
    const counts=profiles.map(t=>s.counts[t]);
    const outcomes=p.designs.map(d=>minCostAssignment(counts,zones.map(z=>d.capacity[z]),costs,allowed));
    const optimum=Math.min(...outcomes.filter(o=>o.feasible).map(o=>o.loss));
    return {scenario:s,outcomes:outcomes.map((o,i)=>({...o,design:p.designs[i].id,regret:o.feasible?o.loss-optimum:null}))};
  });
  const dev=rows.filter(r=>r.scenario.split==='development'),hold=rows.filter(r=>r.scenario.split==='holdout');
  const score=(subset,field)=>p.designs.map((d,i)=>subset.every(r=>r.outcomes[i].feasible)?Math.max(...subset.map(r=>r.outcomes[i][field])):null);
  const baseline=score([dev.find(r=>r.scenario.id===p.baseline_scenario)],'loss'),robust=score(dev,'regret'),holdout=score(hold,'regret');
  const winners=scores=>{const valid=scores.filter(v=>v!==null);return valid.length?p.designs.filter((d,i)=>scores[i]!==null&&Math.abs(scores[i]-Math.min(...valid))<1e-10).map(d=>d.id):[];};
  return {rows,baseline,robust,holdout,baselineWinners:winners(baseline),robustWinners:winners(robust)};
}
function render(){
  let focus=Number($('focus').value),collab=Number($('collab').value);
  if(focus+collab>12){if(document.activeElement===$('focus')){$('collab').value=12-focus;}else{$('focus').value=12-collab;}focus=Number($('focus').value);collab=Number($('collab').value);}
  let z1=Number($('z1').value),z3=Number($('z3').value);let z2=12-z1-z3;
  if(z2<0||z2>8){
    if(document.activeElement===$('z1')){
      const lo=Math.max(0,4-z1),hi=Math.min(8,12-z1);
      $('z3').value=Math.max(lo,Math.min(hi,z3));
    }else{
      const lo=Math.max(0,4-z3),hi=Math.min(8,12-z3);
      $('z1').value=Math.max(lo,Math.min(hi,z1));
    }
    z1=Number($('z1').value);z3=Number($('z3').value);z2=12-z1-z3;
  }
  $('capacityWarning').textContent=z2<0||z2>8?'Choose zone capacities between 0 and 8.':'';
  $('focusValue').textContent=focus;$('collabValue').textContent=collab;$('mixedValue').textContent=12-focus-collab;
  $('z1Value').textContent=z1;$('z3Value').textContent=z3;$('z2Value').textContent=z2;
  $('taskWeight').textContent=$('weight').value+'%';$('environmentWeight').textContent=(100-Number($('weight').value))+'%';
  if(z2<0||z2>8)return;
  const p=projectFromControls(),r=evaluate(p),ids=p.zones.map(z=>z.id);
  $('designs').innerHTML=p.designs.map(d=>'<div'+(r.robustWinners.includes(d.id)?' class="highlight"':'')+'><b>'+escapeHTML(d.id)+'</b><small>'+escapeHTML(d.name)+'</small><div class="zones">'+ids.map(z=>'<div class="zone"><strong>'+escapeHTML(z)+'</strong><small>'+escapeHTML(p.zones.find(a=>a.id===z).name)+'</small>'+d.capacity[z]+' places</div>').join('')+'</div></div>').join('');
  $('decision').innerHTML='<div><small>Existing</small><b>'+escapeHTML(p.existing_design)+'</b><small>Reference configuration</small></div><div><small>Baseline: S0</small><b>'+escapeHTML(r.baselineWinners.join(' / ')||'Unresolved')+'</b><small>Best in edited S0 mix</small></div><div class="highlight"><small>Robust: S0–S2</small><b>'+escapeHTML(r.robustWinners.join(' / ')||'Unresolved')+'</b><small>Minimum maximum regret</small></div><div><small>Holdout check</small><b>'+escapeHTML(r.robustWinners.map(id=>{const i=p.designs.findIndex(d=>d.id===id);return fmt(r.holdout[i]);}).join(' / ')||'—')+'</b><small>Maximum regret of robust choice</small></div>';
  const first=r.rows[0].outcomes,max=Math.max(.001,...first.filter(x=>x.feasible).map(x=>x.loss));
  $('bars').innerHTML=first.map(o=>'<div class="result'+(r.baselineWinners.includes(o.design)?' best':'')+'"><span class="name">'+escapeHTML(o.design)+'</span><span class="bar"><i style="width:'+(o.feasible?Math.max(2,100*o.loss/max):0)+'%"></i></span><strong class="value">'+fmt(o.loss)+'</strong></div>').join('');
  $('matrixHead').innerHTML='<tr><th>Mix</th>'+p.designs.map(d=>'<th>'+escapeHTML(d.id)+'</th>').join('')+'</tr>';
  $('matrixBody').innerHTML=r.rows.map(row=>'<tr><td>'+escapeHTML(row.scenario.id)+' · '+escapeHTML(row.scenario.name)+(row.scenario.split==='holdout'?' (holdout)':'')+'</td>'+row.outcomes.map(o=>'<td>'+fmt(o.loss)+'</td>').join('')+'</tr>').join('');
  window.peoplecomfortDemo={project:p,result:r};
}
['focus','collab','weight','z1','z3'].forEach(id=>$(id).addEventListener('input',render));
$('reset').addEventListener('click',()=>{for(const [id,value] of Object.entries({focus:5,collab:2,weight:60,z1:4,z3:3}))$(id).value=value;render();});
render();
