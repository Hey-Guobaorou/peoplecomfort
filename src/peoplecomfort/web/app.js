let project,result,dirty=false;
const $=s=>document.querySelector(s);
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const num=(x,n=3)=>x==null?'Infeasible':Number(x).toFixed(n);
const table=(heads,rows)=>`<table><thead><tr>${heads.map(x=>`<th>${esc(x)}</th>`).join('')}</tr></thead><tbody>${rows.map(x=>`<tr>${x.join('')}</tr>`).join('')}</tbody></table>`;
const td=x=>`<td>${esc(x)}</td>`;
function input(path,val,type='number'){return `<input type="${type}" ${type==='number'?'step="any"':''} data-path="${esc(path)}" value="${esc(val)}" aria-label="${esc(path)}">`;}
function markDirty(){dirty=true;$('#export').disabled=true;$('#status').textContent='Inputs changed. Charts show the previous run; run again to update.';}
function download(data,name,type='application/json'){const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([data],{type}));a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(a.href),500);}
function editors(){
 $('#projectTitle').textContent=project.title;
 $('#evidenceLabel').textContent=project.evidence_status==='illustrative'?'Illustrative data':'Input provenance requires review';
 $('#zoneEditor').innerHTML=table(['Zone','Ta °C','MRT °C','RH %','Air speed m/s','Max. seats'],project.zones.map((z,i)=>[td(z.name),...['ta','tr','rh','v','max_seats'].map(k=>`<td>${input(`zones.${i}.${k}`,z[k])}</td>`)]));
 $('#profileEditor').innerHTML=table(['Profile','met','clo','Allowed zones (comma-separated)'],project.profiles.map((t,i)=>[td(t.name),`<td>${input(`profiles.${i}.met`,t.met)}</td>`,`<td>${input(`profiles.${i}.clo`,t.clo)}</td>`,`<td>${input(`profiles.${i}.allowed_zones`,t.allowed_zones.join(','),'text')}</td>`]));
 $('#designEditor').innerHTML=table(['Design',...project.zones.map(z=>z.name)],project.designs.map((d,i)=>[td(d.name),...project.zones.map(z=>`<td>${input(`designs.${i}.seats.${z.id}`,d.seats[z.id])}</td>`)]));
 $('#scenarioEditor').innerHTML=table(['Scenario','Role',...project.profiles.map(t=>t.id)],project.scenarios.map((s,i)=>[td(s.id+' '+s.name),td(s.split==='development'?'Development':'Holdout'),...project.profiles.map(t=>`<td>${input(`scenarios.${i}.counts.${t.id}`,s.counts[t.id])}</td>`)]));
 $('#uncertaintyEditor').innerHTML=Object.entries({temperature_offsets:'Common offset °C',gradient_offsets:'Opposing zone shifts °C',clothing_offsets:'Clothing offset clo',thresholds:'PMV screening threshold'}).map(([k,l])=>`<div class="fieldrow"><label>${l}</label>${input(`uncertainty.${k}`,project.uncertainty[k].join(','),'text')}</div>`).join('');
 document.querySelectorAll('[data-path]').forEach(el=>el.addEventListener('change',()=>{const parts=el.dataset.path.split('.');const key=parts.pop();let obj=project;parts.forEach(k=>obj=obj[k]);obj[key]=el.type==='number'?Number(el.value):el.value.split(',').map(x=>key==='allowed_zones'?x.trim():Number(x.trim()));markDirty();}));
}
function show(){
 const r=result,p=r.project,sel=r.selection,win=x=>x.length?x.join(' / '):'No jointly feasible design';
 $('#summary').innerHTML=[['T1 / EXISTING CONFIGURATION',win(sel.T1),'Retain the existing configuration'],['T2 / BASELINE SELECTION',win(sel.T2.winners),'Use only '+p.baseline_scenario+' to minimize mean exceedance'],['T3 / ROBUST SELECTION',win(sel.T3.winners),'Minimize maximum development regret']].map((x,i)=>`<div class="card ${i===2?'feature':''}"><label>${esc(x[0])}</label><b>${esc(x[1])}</b><p>${esc(x[2])}</p></div>`).join('');
 $('#plans').innerHTML='<div class="plans">'+p.designs.map(d=>`<div><div class="plan-name">${esc(d.id)} · ${esc(d.name)}</div>${p.zones.map((z,i)=>`<div class="room ${i?'warm':''}"><span class="zonelabel">${esc(z.name)} / ${d.seats[z.id]} seats</span>${'<i class="seat"></i>'.repeat(d.seats[z.id])}</div>`).join('')}</div>`).join('')+'</div>';
 $('#thermal').innerHTML=table(['Profile',...p.zones.map(z=>z.name)],p.profiles.map(t=>[td(t.name),...p.zones.map(z=>{const a=r.thermal_ledger.find(a=>a.type===t.id&&a.zone===z.id);return `<td class="metric ${Math.abs(a.output.pmv)<=p.pmv_limit?'winner':''}">${num(a.output.pmv)}</td>`;})]));
 $('#matrix').innerHTML=table(['Scenario','Counts '+p.profiles.map(t=>t.id).join('/'),'Role',...p.designs.map(d=>d.id)],p.scenarios.map(s=>[td(s.id),td(p.profiles.map(t=>s.counts[t.id]).join(' / ')),td(s.split==='development'?'Development':'Holdout'),...p.designs.map(d=>{const row=r.rows.find(x=>x.design===d.id&&x.scenario===s.id);return `<td class="metric ${row.regret!=null&&row.regret<1e-10?'winner':''}" title="Model-flagged count ${row.flagged??'—'} / ${p.total_people}">${num(row.loss)} ${row.regret!=null&&row.regret<1e-10?'★':''}</td>`;})]));
 const scores=sel.holdout.scores,max=Math.max(.001,...Object.values(scores).filter(x=>x!=null));
 $('#holdout').innerHTML=p.designs.map(d=>`<div class="barline"><span>${esc(d.id)}</span><div class="bar"><i style="width:${scores[d.id]==null?0:scores[d.id]/max*100}%"></i></div><b>${num(scores[d.id])}</b></div>`).join('');
 $('#sensitivity').innerHTML=r.uncertainty.length?`<p>Evaluated <b>${r.uncertainty.length}</b> joint input conditions.</p>`+p.designs.map(d=>{const n=r.uncertainty.filter(w=>w.development_winners.includes(d.id)).length;return `<div class="barline"><span>${esc(d.id)}</span><div class="bar"><i style="width:${n/r.uncertainty.length*100}%"></i></div><b>${n}/${r.uncertainty.length}</b></div>`;}).join(''):'<p>Stress testing was disabled for this run.</p>';
 $('#provenance').innerHTML=`<p>Input hash: <code>${esc(r.input_sha256)}</code></p><p>Mode: ${esc(r.engine.mode)}</p><p>CBE commit：<code>${esc(r.engine.commit)}</code></p>`+p.zones.map(z=>`<p><b>${esc(z.name)}</b>：${esc(z.source)} (${esc(z.evidence_status)})</p>`).join('');
 $('#allocation').innerHTML=table(['Scenario','Design','Feasible allocations',...p.profiles.map(t=>t.id+' → Z1 / Z2')],r.rows.map(x=>[td(x.scenario),td(x.design),td(x.feasible_allocations),...p.profiles.map((t,i)=>td(x.feasible?x.allocation[i].join(' / '):'Infeasible'))]));
}
async function run(){
 $('#error').hidden=true;$('#run').disabled=true;$('#export').disabled=true;$('#status').textContent='Calculating comfort and enumerating allocations…';
 try{const response=await fetch('/api/analyze',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({project,uncertainty:$('#uncertainty').checked})});const data=await response.json();if(!response.ok)throw Error(data.error);result=data;dirty=false;show();$('#status').textContent=`Completed ${result.rows.length} comparisons · ${result.uncertainty.length} stress conditions`;$('#export').disabled=false;}
 catch(e){$('#error').textContent='Run failed: '+e.message;$('#error').hidden=false;$('#status').textContent='Input or calculation error. Correct it and retry.';}finally{$('#run').disabled=false;}
}
$('.nav').classList.add('active');document.querySelectorAll('.nav').forEach(b=>b.onclick=()=>{document.querySelectorAll('.nav').forEach(x=>x.classList.remove('active'));b.classList.add('active');document.querySelectorAll('.view').forEach(x=>x.hidden=x.id!==b.dataset.view);});
$('#run').onclick=run;
$('#uncertainty').onchange=markDirty;
$('#saveproject').onclick=()=>download(JSON.stringify(project,null,2),'peoplecomfort-project.json');
$('#import').onchange=async e=>{try{const candidate=JSON.parse(await e.target.files[0].text());const check=await fetch('/api/analyze',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({project:candidate,uncertainty:false})});const reply=await check.json();if(!check.ok)throw Error(reply.error);project=candidate;editors();markDirty();$('#error').hidden=true;}catch(err){$('#error').textContent='Import failed: '+err.message;$('#error').hidden=false;}};
$('#export').onclick=async()=>{if(dirty||!result)return;$('#export').disabled=true;try{const res=await fetch('/api/export',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({project:result.project,uncertainty:result.uncertainty.length>0})});if(!res.ok)throw Error((await res.json()).error);download(await res.blob(),'peoplecomfort-results.zip','application/zip');}catch(e){$('#error').textContent=e.message;$('#error').hidden=false;}finally{$('#export').disabled=false;}};
fetch('/api/demo').then(x=>x.json()).then(p=>{project=p;editors();return run();}).catch(e=>{$('#error').hidden=false;$('#error').textContent=e.message;});
