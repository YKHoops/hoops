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
