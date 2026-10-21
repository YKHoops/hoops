/* Basketball equivalents of the active baseball story calculations. Missing evidence stays missing. */
(function(root){
'use strict';
const finite=x=>typeof x==='number'&&Number.isFinite(x);
function observedRace(matches,period,owners,metric='points',cumulative=false){
 const stats=new Map(owners.map(owner=>[owner,{owner,points:0,against:0,w:0,l:0,t:0,games:0}]));
 for(const m of matches.filter(m=>cumulative?m.period<=period:m.period===period)){
  if(!finite(m.home_score)||!finite(m.away_score))continue;
  for(const [side,other] of [['home','away'],['away','home']]){const r=stats.get(m[side+'_owner']);if(!r)continue;const score=m[side+'_score'],opp=m[other+'_score'];r.points+=score;r.against+=opp;r.games++;r.w+=score>opp?1:0;r.l+=score<opp?1:0;r.t+=score===opp?1:0;}
 }
 const rows=[...stats.values()].map(r=>({...r,value:r.games?(metric==='win_pct'?(r.w+.5*r.t)/r.games:r.points):null}));
 for(const r of rows)r.rank=r.value===null?null:1+rows.filter(o=>o.value!==null&&o.value>r.value).length;
 return rows.sort((a,b)=>(a.rank??Infinity)-(b.rank??Infinity)||a.owner.localeCompare(b.owner));
}
function draftCohort(picks,rosterMap,owners,ownerKey=x=>x){
 const rows=owners.map(owner=>{const selected=picks.filter(p=>ownerKey(p.owner)===owner),matched=selected.filter(p=>p.player_id),rostered=matched.filter(p=>rosterMap[p.player_id]),retained=rostered.filter(p=>rosterMap[p.player_id].owner_real_name===owner);return {owner,selected:selected.length,matched:matched.length,rostered:rostered.length,retained:retained.length,rate:matched.length?rostered.length/matched.length:null,retention:matched.length?retained.length/matched.length:null};});
 for(const r of rows)r.rank=r.rate===null?null:1+rows.filter(o=>o.rate!==null&&o.rate>r.rate).length;
 return rows.sort((a,b)=>(a.rank??Infinity)-(b.rank??Infinity)||a.owner.localeCompare(b.owner));
}
function draftHistory(classes,rosterMap,owners,ownerKey=x=>x){
 const rows=owners.map(owner=>{const cohorts=classes.map(d=>({...draftCohort(d.picks,rosterMap,owners,ownerKey).find(r=>r.owner===owner),year:d.draft_year})).filter(r=>r.rank!==null);return {owner,classes:cohorts,average:cohorts.length?cohorts.reduce((a,r)=>a+r.rank,0)/cohorts.length:null};});
 for(const r of rows)r.rank=r.average===null?null:1+rows.filter(o=>o.average!==null&&o.average<r.average).length;
 return rows.sort((a,b)=>(a.rank??Infinity)-(b.rank??Infinity));
}
function tradeRoutes(events,owner){
 const routes=new Map();for(const t of events.filter(t=>t.parties.includes(owner)))for(const other of t.parties.filter(p=>p!==owner)){if(!routes.has(other))routes.set(other,{owner:other,events:0,incoming:0,outgoing:0});const r=routes.get(other);r.events++;r.incoming+=t.assets.filter(a=>a.sender===other&&a.recipient===owner).length;r.outgoing+=t.assets.filter(a=>a.sender===owner&&a.recipient===other).length;}return [...routes.values()].sort((a,b)=>b.events-a.events);
}
function journey(p){
 const events=(p.transfers||[]).map(t=>({...t,title:'Exported transfer',kind:'transfer',sort:t.date}));
 const represented=new Set(events.map(e=>[e.season,e.sender,e.recipient].join('|')));
 for(const m of p.reported_moves||[])if(!represented.has([m.season,m.from,m.to].join('|')))events.push({...m,title:'Reported trade',kind:'reported',sender:m.from,recipient:m.to,sort:m.date||m.season.slice(0,4)+'-07-01',undated:!m.date});
 for(const o of p.observations||[])events.push({...o,title:'Roster observation',sort:o.date||o.season.slice(0,4)+'-07-01',undated:!o.date});
 return events.sort((a,b)=>a.sort.localeCompare(b.sort)||a.title.localeCompare(b.title));
}
function production(players,stats){
 const unique=[...new Set(players.filter(Boolean))],rows=unique.map(id=>stats.find(r=>r.player_id===id)).filter(Boolean),exact=rows.filter(r=>r.totals&&finite(r.totals.fp));return {players:unique.length,covered:rows.length,exact:exact.length,total:exact.length?exact.reduce((n,r)=>n+r.totals.fp,0):null,gp:exact.reduce((n,r)=>n+r.gp,0)};
}
const api={observedRace,draftCohort,draftHistory,tradeRoutes,journey,production};
if(typeof module!=='undefined')module.exports=api;else root.YKInsights=api;
})(typeof window==='undefined'?this:window);
