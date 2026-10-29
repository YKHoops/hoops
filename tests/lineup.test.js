const test=require('node:test');const assert=require('node:assert/strict');
const {usage,protectedReason,dailyForPlan}=require('../docs/js/lineup-ui.js');
test('70 percent cutoff and manual protection cannot be bypassed',()=>{
 const p={id:'A',rostered_pct:70};assert.equal(protectedReason(p,new Set(),false),null);
 p.rostered_pct=70.01;assert.equal(protectedReason(p,new Set(),false),'Over 70% rostered');
 p.rostered_pct=10;assert.equal(protectedReason(p,new Set(['A']),false),'Manually protected');
 assert.ok(protectedReason(p,new Set(),true));p.rostered_pct=null;assert.ok(protectedReason(p,new Set(),false));
});
test('usage counts selected games, including zero-start players',()=>{
 const result=usage({players:[{id:'A'},{id:'B'}]},{assignments:[{player_id:'A',points:20},{player_id:'A',points:30}]});
 assert.deepEqual(result.map(p=>[p.id,p.starts,p.points]),[['A',2,50],['B',0,0]]);
});

test('bench decisions follow the selected objective',()=>{
 const analysis={best:{assignments:[{date:'2026-11-02',player_id:'A'}]},daily:[{date:'2026-11-02',bench:[{player_id:'B'}],available:2}]};
 const daily=dailyForPlan(analysis,{assignments:[{date:'2026-11-02',player_id:'B'}]});
 assert.deepEqual(daily[0].bench.map(p=>p.player_id),['A']);
});

const {usageBreakdown,weeklyUsage,automaticProtection}=require('../docs/js/lineup-ui.js');
test('usage bars distinguish benched games from injury and inactive slots',()=>{
 const games=[{date:'2026-11-02',availability:'available'},{date:'2026-11-03',availability:'conditional'},{date:'2026-11-04',availability:'out'}];
 const input={players:[{id:'A',status:'ACTIVE',projection:{fp_pg:20},games},{id:'B',status:'IR',projection:{fp_pg:30},games}]};
 let r=usageBreakdown(input,{assignments:[{player_id:'A',points:20}]});
 assert.deepEqual(r.map(p=>[p.starts,p.benched,p.unavailable,p.scheduled]),[[1,0,2,3],[0,0,3,3]]);
 r=usageBreakdown(input,{assignments:[{player_id:'A',points:20}]},true);
 assert.deepEqual([r[0].starts,r[0].benched,r[0].unavailable],[1,1,1]);
});
test('weekly grid sorts weeks, honors objective, and separates zero from absent',()=>{
 const p={id:'A',name:'Player A',status:'ACTIVE',games:[{}]};
 const make=(start,players,n)=>({input:{period:{id:start,start},players},scenarios:{conservative:{best:{games:n,assignments:n?[{player_id:'A'}]:[]},reach:{games:1,assignments:[{player_id:'A'}]}}}});
 const entries=[make('2026-11-09',[p],0),make('2026-11-02',[],0),make('2026-11-16',[p],1)];
 assert.deepEqual(weeklyUsage(entries).rows[0].weeks.map(w=>w?.starts??null),[null,0,1]);
 assert.deepEqual(weeklyUsage(entries,'conservative','games').rows[0].weeks.map(w=>w?.starts??null),[null,1,1]);
});
test('automatic keep overrides droppable preference for high, stale or unknown ownership',()=>{
 assert.equal(automaticProtection({id:'A',rostered_pct:70},false),null);
 assert.ok(automaticProtection({id:'A',rostered_pct:71},false));
 assert.ok(automaticProtection({id:'A',rostered_pct:null},false));
 assert.ok(automaticProtection({id:'A',rostered_pct:20},true));
});
