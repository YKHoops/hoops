/* Pure ranking calculations. One independent publisher per compatible overall list. */
(function(root){
'use strict';
const weights={PTS:1,REB:1,AST:2,STL:4,BLK:4,FGM:2,FGA:-1,FTM:1,FTA:-1,'3PM':1,TO:-2};
const group=s=>[s.season,s.scoring_format,s.horizon,s.rank_scope,...(['general_points','general_dynasty','custom_categories','yk_projection'].includes(s.scoring_format)?[s.id]:[])].join('|');
const positions=p=>String(p||'').split(/[\s,\/]+/).filter(x=>['PG','SG','SF','PF','C','G','F'].includes(x));
const primary=p=>positions(p)[0]||'Other';
function validate(s){
 for(const k of ['id','publisher','label','url','published_at','season','scoring_format','horizon','rank_scope','coverage','notes'])if(typeof s[k]!=='string'||!s[k])throw Error('Missing source field: '+k);
 if(!/^[a-z0-9_-]+$/.test(s.id)||!/^https?:\/\//.test(s.url))throw Error('Use a source ID and public source URL.');
 const sourceURL=new URL(s.url);if(sourceURL.username||sourceURL.password||[...sourceURL.searchParams.keys()].some(k=>['token','api_key','apikey','cookie','authorization'].includes(k.toLowerCase())))throw Error('Remove credentials from the source URL.');
 if(!/^\d{4}-\d{2}-\d{2}$/.test(s.published_at)||!Number.isFinite(Date.parse(s.published_at))||new Date(s.published_at).toISOString().slice(0,10)!==s.published_at||s.published_at>new Date().toISOString().slice(0,10))throw Error('Use a valid publication date, not a future date.');
 if(!/^20\d\d-\d\d$/.test(s.season)||(Number(s.season.slice(0,4))+1)%100!==Number(s.season.slice(5)))throw Error('Use a basketball season such as 2026-27.');
 if(!['nine_category','yk_points','general_points','general_dynasty','custom_categories','yk_projection'].includes(s.scoring_format)||!['dynasty','full_season','rest_of_season'].includes(s.horizon)||s.rank_scope!=='overall')throw Error('Unsupported scoring format, horizon or scope.');
 if(['yk_points','yk_projection'].includes(s.scoring_format)&&(Object.keys(s.points_weights||{}).length!==11||Object.entries(weights).some(([k,v])=>s.points_weights[k]!==v)))throw Error('Points weights must exactly match YK.');
 if(!Array.isArray(s.rows)||!s.rows.length)throw Error('No ranking rows.');
 const ids=new Set();const rows=s.rows.map(r=>{if(!/^(nba|unmatched):[a-z0-9]+$/.test(r.player_id)||typeof r.player_name!=='string'||!r.player_name||!Number.isInteger(r.original_rank)||r.original_rank<1||ids.has(r.player_id))throw Error('Invalid rank or duplicate/missing player identity.');ids.add(r.player_id);return {player_id:r.player_id,player_name:r.player_name,position:String(r.position||''),original_rank:r.original_rank,identity_status:r.player_id.startsWith('nba:')?'manual_id':'unresolved'};});
 const result=Object.fromEntries(['id','publisher','label','url','published_at','season','scoring_format','horizon','rank_scope','coverage','notes'].map(k=>[k,s[k]]));
 if(s.publication_precision!==undefined&&!['day','month','capture_only'].includes(s.publication_precision))throw Error('Unsupported publication precision');
 return {...result,publication_precision:s.publication_precision,points_weights:['yk_points','yk_projection'].includes(s.scoring_format)?weights:undefined,rows,list_size:rows.length,max_rank:Math.max(...rows.map(r=>r.original_rank)),imported_at:new Date().toISOString()};
}
function compatible(sources,selection){return sources.filter(s=>s.season===selection.season&&s.scoring_format===selection.scoring_format&&s.horizon===selection.horizon&&s.rank_scope==='overall');}
function aggregate(sources, roster=[], today=new Date().toISOString().slice(0,10)){
 if(new Set(sources.map(group)).size>1)throw Error('Incompatible ranking sources');
 if(new Set(sources.map(s=>s.publisher)).size!==sources.length)throw Error('One list per independent publisher');
 const map=new Map();
 for(const p of roster){if(map.has(p.player_id))throw Error('Duplicate roster player');map.set(p.player_id,{...p,ranks:[]});}
 for(const s of sources)for(const r of s.rows){let p=map.get(r.player_id);if(!p){p={...r,ranks:[]};map.set(r.player_id,p);}p.ranks.push({source_id:s.id,label:s.label,rank:r.original_rank,published_at:s.published_at,publication_precision:s.publication_precision,projected_fp_pg:r.projected_fp_pg,source_original_rank:r.source_original_rank});}
 const day=86400000;
 return [...map.values()].map(p=>{const rs=p.ranks.map(r=>r.rank),n=rs.length,mean=n?rs.reduce((a,b)=>a+b,0)/n:null;return {...p,mean_rank:mean,source_count:n,selected_count:sources.length,disagreement:n>1?Math.max(...rs)-Math.min(...rs):null,sd:n>1?Math.sqrt(rs.reduce((a,r)=>a+(r-mean)**2,0)/n):null,oldest_days:n&&!p.ranks.some(r=>r.publication_precision==='capture_only')?Math.max(...p.ranks.map(r=>Math.floor((Date.parse(today)-Date.parse(r.published_at))/day))):null,uneven:n>0&&n<sources.length};}).sort((a,b)=>(a.mean_rank??Infinity)-(b.mean_rank??Infinity)||a.player_name.localeCompare(b.player_name));
}
// Strictly decreasing for rank >= 1. Missing rank has no score, never zero.
const score=rank=>Number.isFinite(rank)&&rank>=1?100/(1+(rank-1)/25):null;
const diameter=rank=>score(rank)===null?null:54*Math.sqrt(score(rank)/100);
function teams(rows,owners){return owners.map(owner=>{const players=rows.filter(p=>p.owner_real_name===owner),ranked=players.filter(p=>p.mean_rank!==null);return {owner,players,ranked:ranked.length,total:players.length,index:ranked.length?ranked.reduce((n,p)=>n+score(p.mean_rank),0):null,complete:ranked.filter(p=>p.source_count===p.selected_count).length};}).sort((a,b)=>(b.index??-Infinity)-(a.index??-Infinity)||a.owner.localeCompare(b.owner));}
const api={weights,group,positions,primary,validate,compatible,aggregate,score,diameter,teams};
if(typeof module!=='undefined')module.exports=api;else root.YKRankingEngine=api;
})(typeof window==='undefined'?this:window);
