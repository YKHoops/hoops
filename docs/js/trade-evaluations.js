/* Shared selectors; all grades originate in the validated offline evaluator. */
(function(root){
'use strict';
const finite=n=>typeof n==='number'&&Number.isFinite(n);
function valid(bundle,descriptor){return !!bundle&&bundle.schema_version===1&&bundle.dashboard_sha256===descriptor?.dashboard_sha256&&Array.isArray(bundle.events);}
async function load(descriptor,fetcher=fetch){
 if(!descriptor)return {bundle:null,error:'Trade evaluations have not been built for this snapshot.'};
 try{const r=await fetcher(descriptor.path,{signal:AbortSignal.timeout(8000)});if(!r.ok)throw Error('Evaluation file unavailable');const bytes=await r.arrayBuffer(),hash=[...new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))].map(x=>x.toString(16).padStart(2,'0')).join('');if(hash!==descriptor.sha256)throw Error('Evaluation checksum mismatch');const bundle=JSON.parse(new TextDecoder().decode(bytes));if(!valid(bundle,descriptor))throw Error('Evaluation edition mismatch');return {bundle,error:null};}catch(e){return {bundle:null,error:e.message};}
}
function archives(bundle,event){return (bundle?.archive||[]).filter(a=>a.event_id===event.event_id&&a.status!=='duplicate_alias');}
function sides(bundle,event,method){return method==='historical'?archives(bundle,event).flatMap(a=>a.sides.map(s=>({...s,archive_id:a.archive_id,status:s.grade&&s.grade!=='INC'?'historical':'incomplete'}))):event.improvement.sides;}
function filter(bundle,opts={}){
 const {season,owner,partner,type,method='historical',letter,status,q='',operator,confidence}=opts;const needle=q.toLocaleLowerCase();
 return (bundle?.events||[]).filter(e=>(!season||e.season===season)&&(!owner||e.parties.includes(owner))&&(!partner||e.parties.includes(partner))&&(!type||e.type===type)&&e.search.toLocaleLowerCase().includes(needle)).filter(e=>{
 const ss=sides(bundle,e,method).filter(s=>(!owner||s.franchise===owner)&&(!operator||s.recorded_operator===operator));
 return (!confidence||archives(bundle,e).some(a=>a.sides.some(s=>(!owner||s.franchise===owner)&&s.original?.confidence===confidence)))&&(!operator||ss.length)&&(!letter||ss.some(s=>letter==='INC'?s.status==='incomplete':s.grade===letter))&&(!status||(status==='historical'?archives(bundle,e).length:status==='eligible'?e.improvement.verdict.status==='eligible':e.improvement.sides.some(s=>s.status==='incomplete')));
 }).sort((a,b)=>(b.date||b.season).localeCompare(a.date||a.season)||a.event_id.localeCompare(b.event_id));
}
function summaries(events,scope='franchise'){
 const groups=new Map();for(const e of events)for(const s of e.improvement.sides){const who=s[scope]||'Operator unresolved';if(!groups.has(who))groups.set(who,{owner:who,total:0,eligible:0,incomplete:0,excluded_picks:0,gpas:[],event_ids:[],favored:0,even:0});const r=groups.get(who);r.total++;r.excluded_picks+=s.excluded_picks.length;
 if(s.status==='eligible'&&finite(s.gpa)&&e.improvement.verdict.status==='eligible'&&who!=='Operator unresolved'){r.eligible++;r.gpas.push(s.gpa);r.event_ids.push(e.event_id);r.favored+=e.improvement.verdict.favored===s.franchise?1:0;r.even+=e.improvement.verdict.favored===null?1:0;}else r.incomplete++;}
 const rows=[...groups.values()].map(r=>({...r,mean:r.gpas.length?r.gpas.reduce((a,b)=>a+b,0)/r.gpas.length:null,rank:null}));
 for(const r of rows)if(r.eligible>=3)r.rank=1+rows.filter(x=>x.eligible>=3&&x.mean>r.mean).length;
 return rows.sort((a,b)=>(a.rank??Infinity)-(b.rank??Infinity)||(b.mean??-1)-(a.mean??-1)||a.owner.localeCompare(b.owner));
}
function featured(events){return events.filter(e=>e.improvement.verdict.status==='eligible'&&finite(e.improvement.verdict.gap)).sort((a,b)=>b.improvement.verdict.gap-a.improvement.verdict.gap||a.event_id.localeCompare(b.event_id)).slice(0,8);}
const api={valid,load,archives,sides,filter,summaries,featured};if(typeof module!=='undefined')module.exports=api;else root.YKTradeEvaluations=api;
})(typeof window==='undefined'?this:window);
