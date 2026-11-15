const K='a13',R=['Director de misión','Ingeniero eléctrico','Navegación','Soporte vital y comunicaciones'];
const N={o:'Oxígeno',p:'Energía',w:'Agua',f:'Comida',c:'CO₂',i:'Integridad',s:'Tripulación',t:'Trayectoria'};
const fresh=pl=>({pl,m:1,t:0,err:0,k:1,fin:0,scenario:'apollo',objective:'',science:0,data:0,design:null,r:{o:100,p:100,w:100,f:100,c:0,i:100,s:100,t:70}});
let S=null;try{S=JSON.parse(localStorage.getItem(K))}catch(e){}
const save=()=>{try{localStorage.setItem(K,JSON.stringify(S))}catch(e){}};
const $=q=>document.querySelector(q),cl=v=>Math.max(0,Math.min(100,v));
let AC;function beep(f=440,d=.15,ty='sine'){try{AC=AC||new AudioContext();const o=AC.createOscillator(),g=AC.createGain();o.type=ty;o.frequency.value=f;g.gain.value=.05;o.connect(g);g.connect(AC.destination);o.start();o.stop(AC.currentTime+d)}catch(e){}}
const met=s=>{s*=6;const p=n=>String(n).padStart(2,'0');return p(Math.floor(s/3600))+':'+p(Math.floor(s%3600/60))+':'+p(Math.floor(s%60))};
function bars(){const b=$('#bars');if(!b||!S)return;if(!b.children.length)b.innerHTML=Object.keys(N).map(k=>`<div class="bar" id="b${k}"><span>${N[k]}</span><i><b></b></i><em></em></div>`).join('');
for(const k in N){const v=S.r[k],bad=k=='c'?v:100-v,e=$('#b'+k);e.className='bar'+(bad>75?' d':bad>50?' w':'');e.querySelector('b').style.width=v+'%';e.querySelector('em').textContent=Math.round(v)+'%'}}
let al=0;function draw(){bars();const c=$('#clk');if(c)c.textContent=met(S.t);const r=S.r,a=r.o<25||r.p<20||r.c>70||r.s<30;document.body.classList.toggle('alarm',a);const l=$('#led');if(l)l.className='led'+(a?' r':'');if(a&&++al%3==0)beep(880,.12,'square')}
function tick(){const r=S.r,k=S.k,e=S.m<3?.4:1,d=S.designTotals||{battery:0,solar:0,instruments:0};r.o=cl(r.o-.04*k*e);r.p=cl(r.p-Math.max(.008,(.05+(d.instruments||0)*.001-(d.solar||0)*.002)/(1+(d.battery||0)/35))*k*e);r.w=cl(r.w-.03*k*e);r.f=cl(r.f-.02*k*e);if(S.m>=3)r.c=cl(r.c+.05*k);if(r.c>80||r.o<10||r.p<=0)r.s=cl(r.s-.15);if(S.designTotals){S.science=Math.min(100,(S.science||0)+(S.designTotals.science||0)*.0005);S.data=Math.min(100,(S.data||0)+(S.designTotals.data||0)*.0005)}S.t++;save();draw();if(S.t>=1200||r.o<=0||r.s<=0||r.i<=0)location.href='Final.html'}
function designOptions(){return{
 hull:[{id:'command',name:'Cápsula compacta',mass:180,cost:150,life:1},{id:'service',name:'Módulo de servicio',mass:240,cost:230,life:1.15},{id:'orbiter',name:'Plataforma orbital',mass:130,cost:190,life:.9}],
 battery:[{id:'basic',name:'Batería estándar',mass:45,cost:80,capacity:18},{id:'extended',name:'Batería extendida',mass:80,cost:150,capacity:38},{id:'redundant',name:'Baterías redundantes',mass:120,cost:230,capacity:58}],
 solar:[{id:'compact',name:'Panel compacto',mass:25,cost:55,generation:4},{id:'array',name:'Panel desplegable',mass:55,cost:120,generation:12},{id:'large',name:'Panel de alta potencia',mass:95,cost:205,generation:22}],
 launcher:[{id:'light',name:'Lanzador ligero',mass:0,capacity:520,cost:100},{id:'medium',name:'Lanzador medio',mass:0,capacity:780,cost:190},{id:'heavy',name:'Lanzador pesado',mass:0,capacity:1050,cost:320}],
 orbit:[{id:'free-return',scenario:'apollo',name:'Retorno libre lunar',cost:120,minCapacity:700},{id:'direct-return',scenario:'apollo',name:'Retorno directo',cost:180,minCapacity:900},{id:'low-lunar',scenario:'lunar',name:'Órbita lunar baja',cost:80,minCapacity:650},{id:'polar-lunar',scenario:'lunar',name:'Órbita polar lunar',cost:140,minCapacity:760},{id:'sun-sync',scenario:'earth',name:'Órbita heliosíncrona baja',cost:50,minCapacity:400},{id:'geostationary',scenario:'earth',name:'Órbita geoestacionaria',cost:180,minCapacity:750}],
 instruments:[{id:'basic',name:'Paquete de sensores básico',mass:35,cost:70,science:10,data:12,power:4},{id:'mapping',name:'Cámara cartográfica',mass:70,cost:150,science:23,data:25,power:9},{id:'advanced',name:'Laboratorio multiespectral',mass:115,cost:250,science:38,data:42,power:16}],
 antenna:[{id:'standard',name:'Antena estándar',mass:15,cost:45,capacity:18},{id:'highgain',name:'Antena de alta ganancia',mass:30,cost:100,capacity:38},{id:'relay',name:'Antena de retransmisión',mass:50,cost:175,capacity:65}]
}}
const option=(group,id)=>designOptions()[group].find(x=>x.id===id);
function designTotals(d){
 const parts=['hull','battery','solar','launcher','instruments','antenna'].map(k=>option(k,d[k])),orbit=option('orbit',d.orbit);
 return{mass:parts.reduce((n,x)=>n+x.mass,0),cost:parts.reduce((n,x)=>n+x.cost,0)+orbit.cost,power:10+parts[2].generation-parts[4].power,data:parts[4].data,comms:parts[5].capacity,science:parts[4].science,capacity:parts[3].capacity,orbitRequirement:orbit.minCapacity,orbitName:orbit.name,battery:parts[1].capacity,solar:parts[2].generation,instruments:parts[4].power}
}
function pagDiseno(){
 if(!S){location.href='index.html';return}
 const q=new URLSearchParams(location.search),scenario=q.get('scenario')||S.scenario||'apollo';
 S.scenario=SCENARIOS[scenario]?scenario:'apollo';
 const prior=S.design||{hull:'command',battery:'extended',solar:'array',launcher:'medium',orbit:'free-return',instruments:'mapping',antenna:'highgain',transfer:0};
 const fields={hull:'Nave / plataforma',battery:'Baterías',solar:'Paneles solares',launcher:'Lanzador',orbit:'Órbita',instruments:'Instrumentos',antenna:'Antena'};
 $('#designTitle').textContent=SCENARIOS[S.scenario].name;$('#scenarioSelect').value=S.scenario;
 for(const key in fields){const choices=key==='orbit'?designOptions().orbit.filter(x=>x.scenario===S.scenario):designOptions()[key];if(!choices.some(x=>x.id===prior[key]))prior[key]=choices[0].id;$('#d'+key).innerHTML=choices.map(x=>`<option value="${x.id}" ${prior[key]===x.id?'selected':''}>${x.name} · ${x.mass?x.mass+' kg · ':''}${x.cost} créditos</option>`).join('')}
 $('#objectiveSelect').innerHTML=SCENARIOS[S.scenario].objectives.map(x=>`<option value="${x}" ${S.objective===x?'selected':''}>${x}</option>`).join('');
 $('#playerLabel').textContent=S.pl+' jugador'+(S.pl===1?'':'es')+' · decisiones por rol';
 $('#budgetLevel').value=prior.budgetLevel||'1';
 const transfer=$('#transferBudget');transfer.value=prior.transfer||0;
 function update(){
  const d={};for(const key in fields)d[key]=$('#d'+key).value;d.transfer=+transfer.value;d.budgetLevel=$('#budgetLevel').value;
  const t=designTotals(d),sc=SCENARIOS[S.scenario],budget=Math.round(sc.budget*(+$('#budgetLevel').value)),supportBudget=budget*.25+d.transfer,sharedBudget=budget*.75-d.transfer;
  const engineeringCost=option('hull',d.hull).cost+option('battery',d.battery).cost+option('solar',d.solar).cost+option('launcher',d.launcher).cost+option('orbit',d.orbit).cost,supportCost=option('instruments',d.instruments).cost+option('antenna',d.antenna).cost;
  const flags=[[t.mass<=sc.mass,'Masa total: '+t.mass+' / '+sc.mass+' kg'],[t.mass<=t.capacity,'Lanzador: '+t.mass+' / '+t.capacity+' kg de capacidad'],[t.capacity>=t.orbitRequirement,'Órbita elegida requiere lanzador de '+t.orbitRequirement+' kg de capacidad'],[t.cost<=budget,'Presupuesto total: '+t.cost+' / '+budget+' créditos'],[engineeringCost<=sharedBudget,'Ingeniería/Navegación: '+engineeringCost+' / '+Math.round(sharedBudget)+' créditos'],[supportCost<=supportBudget,'Soporte/Ciencia: '+supportCost+' / '+Math.round(supportBudget)+' créditos'],[t.power>0,'Balance de potencia: '+(t.power>=0?'+':'')+t.power+' unidades'],[t.data<=t.comms,'Datos/comunicaciones: '+t.data+' / '+t.comms+' unidades'],[t.data>=sc.dataGoal,'Datos requeridos: '+t.data+' / '+sc.dataGoal],[t.science>=sc.scienceGoal,'Ciencia requerida: '+t.science+' / '+sc.scienceGoal]];
  const bar=(name,value,max,ok,detail)=>`<div class="design-metric ${ok?'':'invalid'}"><div><span>${name}</span><b>${detail}</b></div><i><b style="width:${Math.min(100,Math.max(0,value/max*100))}%"></b></i></div>`;
  $('#designBars').innerHTML=bar('Masa',t.mass,sc.mass,t.mass<=sc.mass,`${t.mass} / ${sc.mass} kg`)+bar('Potencia',Math.max(0,t.power),30,t.power>0,`${t.power>=0?'+':''}${t.power} · paneles − instrumentos`)+bar('Presupuesto',t.cost,budget,t.cost<=budget,`${t.cost} / ${budget} créditos`)+bar('Datos',t.data,sc.dataGoal,t.data>=sc.dataGoal,`${t.data} / ${sc.dataGoal} requeridos`)+bar('Comunicaciones',t.comms,Math.max(t.comms,t.data),t.comms>=t.data,`${t.comms} capacidad · ${t.data} generados`);
  $('#validation').innerHTML=flags.map(([ok,text])=>`<li class="${ok?'valid':'invalid'}">${ok?'✓':'×'} ${text}</li>`).join('');
  $('#designNote').textContent=`Objetivo: ${$('#objectiveSelect').value}. Ciencia del paquete: ${t.science} / ${sc.scienceGoal} requerida.`;
  $('#startDesign').disabled=flags.some(x=>!x[0]);S.design=d;S.objective=$('#objectiveSelect').value;save()
 }
 $('#designForm').onchange=update;transfer.oninput=update;$('#scenarioSelect').onchange=e=>{S.scenario=e.target.value;S.objective='';save();location.href='Diseno.html?scenario='+encodeURIComponent(S.scenario)};
 $('#startDesign').onclick=()=>{S.design={};for(const key in fields)S.design[key]=$('#d'+key).value;S.design.transfer=+transfer.value;S.design.budgetLevel=$('#budgetLevel').value;S.objective=$('#objectiveSelect').value;S.scenario=$('#scenarioSelect').value;S.fin=0;S.m=1;S.t=0;S.err=0;S.k=1;S.science=0;S.data=0;S.decisions=[];S.r={o:100,p:Math.min(100,68+option('battery',S.design.battery).capacity*.55),w:100,f:100,c:0,i:100,s:100,t:70};S.designTotals=designTotals(S.design);save();location.href='intro.html'};
 update()
}
function pagMision(){if(!S){location.href='index.html';return}
const q=Math.min(8,Math.max(1,+new URLSearchParams(location.search).get('m')||S.m));S.m=q;save();const M=S.scenario&&S.scenario!=='apollo'?ALT_STEPS[q-1]:MS[q-1],lead=M.lead,cov=S.pl>lead;
$('#mn').textContent='Jugadores: '+S.pl;$('#ttl').textContent=M.t;$('#txt').textContent=M.txt;
$('#tel').innerHTML=(M.tel||[['Estado','Nominal']]).map(x=>`<span>${x[0]}: <b>${x[1]}</b></span>`).join('');
$('#who').textContent='Especialista: '+R[lead]+(cov?' (presente: los daños se reducen un 40%)':' (sin cubrir)')+' · Decide: '+R[(q-1)%S.pl]+' · '+SCENARIOS[S.scenario||'apollo'].name;
const feed=$('#feed'),msg=(w,t)=>{feed.insertAdjacentHTML('afterbegin',`<p><small>${w}</small>${t}</p>`);beep(660,.08)};
let n=0;const pool=(M.h||G).concat(G.sort(()=>Math.random()-.5));msg(...pool[n++]);const fi=setInterval(()=>msg(...pool[n++%pool.length]),12000);
let left=45,done=0;const cd=$('#cd');
$('#ops').innerHTML=M.op.map((o,i)=>`<button data-i="${i}">${'ABCD'[i]}) ${o.t}</button>`).join('');
document.querySelectorAll('#ops button').forEach(b=>b.onclick=()=>pick(+b.dataset.i));
const ct=setInterval(()=>{if(done)return;cd.textContent='Decide en '+--left+' s';if(left<=0)pick(M.op.length-1,1)},1000);cd.textContent='Decide en 45 s';
function pick(i,auto){if(done)return;done=1;clearInterval(ct);const o=M.op[i],fx=o.fx;
let impact=0;for(const k in fx){let v=fx[k];if(k=='err'){S.err+=v;impact+=v*8}else if(k=='k'){S.k=v;impact+=Math.abs(1-v)*10}else{if(cov&&(k=='c'?v>0:v<0))v*=.6;S.r[k]=cl(S.r[k]+v);impact+=Math.abs(v)*(k=='s'||k=='i'?1.5:.7)}}
if(S.designTotals){S.science=Math.min(100,(S.science||0)+S.designTotals.science*.13*(1+Math.max(-.3,Math.min(.3,(fx.t||0)/100))));S.data=Math.min(100,(S.data||0)+S.designTotals.data*.13)}
S.decisions=S.decisions||[];S.decisions.push({mission:M.t,choice:o.t,impact});
document.querySelectorAll('#ops button').forEach(b=>b.disabled=1);const rs=$('#res');rs.hidden=0;
const nx=q<8?'Mision.html?m='+(q+1):'Final.html';if(q>=8)S.fin=1;S.m=Math.min(8,q+(q<8?1:0));save();draw();
rs.innerHTML=(auto?'<b>Tiempo agotado: se aplicó la opción pasiva.</b><br>':'')+o.r+`<a class="btn go" href="${nx}">${q<8?'Siguiente misión':'Ver resultado'}</a>`;msg('Director de vuelo',o.r);beep(300,.2)}
draw();setInterval(tick,1000)}
function pagFinal(){if(!S){location.href='index.html';return}bars();const r=S.r,scenario=SCENARIOS[S.scenario||'apollo'];
const sc=Math.round((r.o+r.p+r.w+r.f+(100-r.c)+r.i+r.s+r.t)/8-S.err*4+(S.t<800?5:0));
const apollo=(S.scenario||'apollo')==='apollo',goalsMet=apollo||((S.data||0)>=scenario.dataGoal&&(S.science||0)>=scenario.scienceGoal);
const ok=S.fin&&r.s>0&&r.o>0&&r.i>0&&goalsMet;
$('#fn').textContent=ok?(apollo?(sc>=75?'Regreso ejemplar':'Regreso conseguido'):'Objetivo científico cumplido'):'Misión incompleta';
$('#fd').textContent=ok?(apollo?'La tripulación regresó. Revisa qué decisiones protegieron la nave y los recursos.':'La nave completó la operación y reunió suficiente ciencia y datos para el objetivo.'):(apollo?'La misión terminó antes de confirmar el regreso seguro.':'No se alcanzaron todos los objetivos científicos o de seguridad.');
$('#sc').textContent=ok?sc+' pts':'—';
$('#st').textContent=`Escenario: ${scenario.name} · Objetivo: ${S.objective||scenario.objectives[0]} · Tiempo: ${met(S.t)} · Errores: ${S.err} · Ciencia: ${Math.round(S.science||0)}/${scenario.scienceGoal} · Datos: ${Math.round(S.data||0)}/${scenario.dataGoal}`;
const weak=Object.entries({oxígeno:r.o,energía:r.p,agua:r.w,comida:r.f,integridad:r.i,tripulación:r.s,trayectoria:r.t}).sort((a,b)=>a[1]-b[1])[0];
$('#reasons').textContent=ok?`Se cumplió el objetivo y el recurso con menor reserva fue ${weak[0]} (${Math.round(weak[1])}%). ${S.err?`Se registraron ${S.err} errores.`:'No se registraron errores.'}`:`Causa principal: ${!goalsMet?'faltó ciencia o datos transmitidos':r.s<=0?'la tripulación llegó a estado crítico':r.i<=0?'la integridad de la nave llegó a cero':'no se confirmó el cierre de la misión'}. El recurso más comprometido fue ${weak[0]} (${Math.round(weak[1])}%).`;
const most=(S.decisions||[]).slice().sort((a,b)=>b.impact-a.impact)[0];
$('#influence').textContent=most?`Mayor efecto estimado durante «${most.mission}»: «${most.choice}». Sus cambios tuvieron el mayor impacto combinado en recursos, integridad y errores.`:'No hay decisiones registradas para comparar.';
const suggestions=[];if((S.science||0)<scenario.scienceGoal)suggestions.push('elige instrumentos de mayor rendimiento científico');if((S.data||0)<scenario.dataGoal)suggestions.push('aumenta la capacidad de la antena o reduce la carga de datos');if(r.p<40)suggestions.push('añade baterías o paneles, o acuerda más presupuesto para Ingeniería');if(r.s<60||r.i<60)suggestions.push('prioriza el módulo de servicio y decisiones conservadoras');if(!suggestions.length)suggestions.push('prueba una configuración más ligera o un presupuesto austero para comparar resultados');
$('#suggestions').textContent=suggestions.map(x=>'• '+x).join(' · ');
$('#replay').href='Diseno.html?scenario='+encodeURIComponent(S.scenario||'apollo')}
