const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const E=require('../docs/js/rankings-engine.js');
const ROOT=process.env.YK_DASHBOARD_WORKSPACE||path.join(__dirname,'..');
const D=JSON.parse(fs.readFileSync(path.join(ROOT,'docs/data/dashboard.json'))),R=JSON.parse(fs.readFileSync(path.join(ROOT,'docs/data/rankings.json')));
const select=(scoring_format='nine_category',horizon='dynasty',season='2026-27')=>E.compatible(R.sources,{scoring_format,horizon,season});
test('compatible groups exclude different seasons, points formulas and horizons',()=>{
 assert.equal(select().length,2);assert.equal(select('nine_category','full_season').length,2);assert.equal(select('yk_points','full_season').length,1);assert.equal(select('yk_points','dynasty').length,0);assert.equal(select('nine_category','rest_of_season').length,0);
 assert.throws(()=>E.aggregate([...select(),...select('yk_points','full_season')]),/Incompatible/);
 assert.throws(()=>E.aggregate([select()[0],select()[0]]),/independent/);
 assert.equal(select('nine_category','dynasty','2025-26')[0].id,'all_access_20260218');
});
test('mean rank, disagreement and missing ranks are explicit',()=>{
 const a={...select()[0],rows:[{player_id:'nba:a',player_name:'A',original_rank:2},{player_id:'nba:b',player_name:'B',original_rank:80}]},b={...select()[1],rows:[{player_id:'nba:a',player_name:'A',original_rank:6}]};
 const rows=E.aggregate([a,b],[{player_id:'nba:c',player_name:'C'}],'2026-10-21');
 assert.equal(rows[0].mean_rank,4);assert.equal(rows[0].disagreement,4);assert.equal(rows[0].sd,2);
 assert.equal(rows[1].source_count,1);assert.equal(rows[1].mean_rank,80);assert.equal(rows[1].disagreement,null);assert.equal(rows[1].uneven,true);
 assert.equal(rows[2].mean_rank,null);assert.equal(E.score(rows[2].mean_rank),null);
});
test('roster identity, totals and multi-position players count once',()=>{
 const roster=D.rosters_by_season['2026-27'].players,rows=E.aggregate(select(),roster),teams=E.teams(rows,D.teams.owners.map(o=>o.real_name));
 assert.equal(teams.length,10);assert.equal(teams.reduce((n,t)=>n+t.total,0),roster.length);assert.equal(new Set(teams.flatMap(t=>t.players.map(p=>p.player_id))).size,roster.length);
 assert.equal(teams.reduce((n,t)=>n+t.ranked,0),roster.filter(p=>select().some(s=>s.rows.some(r=>r.player_id===p.player_id))).length);assert.equal(E.primary('PG/SG'),'PG');assert.deepEqual(E.positions('PG/SG'),['PG','SG']);
 const teamTotal=teams.reduce((n,t)=>n+t.index,0),playerTotal=teams.flatMap(t=>t.players).reduce((n,p)=>n+E.score(p.mean_rank),0);
 // Grouped versus flat sums can differ by IEEE-754 rounding. Bound only that
 // numerical error; identity, coverage and one-player-one-score checks stay exact.
 assert(Math.abs(teamTotal-playerTotal)<=Number.EPSILON*roster.length*Math.max(1,playerTotal));
 const partial=E.teams(E.aggregate(select('yk_points','full_season'),roster),D.teams.owners.map(o=>o.real_name));assert.equal(partial.reduce((n,t)=>n+t.ranked,0),roster.filter(p=>select('yk_points','full_season').some(s=>s.rows.some(r=>r.player_id===p.player_id))).length);
});
test('bubble area is proportional to monotonic score without hidden size floors',()=>{
 let previous=Infinity;for(const r of [1,2,25,100,500,1000]){assert(E.score(r)<previous);previous=E.score(r);assert(Math.abs(E.diameter(r)**2/(54**2)-E.score(r)/100)<1e-12);}
 assert.equal(E.diameter(null),null);assert.equal(E.score(0),null);
});
test('import validation rejects incompatible/missing metadata, invalid ranks and duplicate IDs',()=>{
 const valid={...select()[0],rows:select()[0].rows.slice(0,2)};assert.equal(E.validate(valid).rows.length,2);
 for(const s of [{...valid,published_at:''},{...valid,horizon:'unknown'},{...valid,rows:[]},{...valid,rows:[valid.rows[0],valid.rows[0]]},{...valid,rows:[{...valid.rows[0],original_rank:0}]},{...valid,scoring_format:'yk_points',points_weights:{PTS:1}}])assert.throws(()=>E.validate(s));
});
test('original ranks, pick exclusions and audited aliases persist',()=>{
 assert.equal(R.sources.find(s=>s.id==='hashtag_dynasty').rows.length,392);
 assert(!R.sources.flatMap(s=>s.rows).some(r=>r.player_name.startsWith('2027 Draft (')));
 for(const s of select())assert.equal(s.rows.find(r=>r.player_name==='Jaren Jackson Jr.').player_id,'nba:04qrj');
 for(const s of R.sources)assert.equal(new Set(s.rows.map(r=>r.player_id)).size,s.rows.length);
});

 test("capture-only source dates do not imply publication freshness",()=>{const source=R.sources.find(s=>s.id==="fantrax_yk_model");const imported=E.validate(source);assert.equal(imported.publication_precision,"capture_only");assert.equal(E.aggregate([imported])[0].oldest_days,null);});

test('October 21 roster and coverage remain a fixed baseline',()=>{const b=require(path.join(ROOT,'private/weekly_runs/2026-10-26/before/dashboard.json')),r=require(path.join(ROOT,'private/weekly_runs/2026-10-26/before/rankings.json'));const roster=b.rosters_by_season['2026-27'].players;const sources=E.compatible(r.sources,{scoring_format:'nine_category',horizon:'dynasty',season:'2026-27'});const t=E.teams(E.aggregate(sources,roster),b.teams.owners.map(o=>o.real_name));assert.equal(roster.length,233);assert.equal(t.reduce((n,t)=>n+t.ranked,0),233);});
