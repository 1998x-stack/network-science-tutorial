const test=require('node:test');
const assert=require('node:assert/strict');
const L=require('../../apps/shared/lesson-interactions.js');
test('11: exact iterative k-core retains 7, 5, 0 nodes',()=>{
 assert.deepEqual(L.kCoreNodes(1),['A','B','C','D','L1','L2','X']);
 assert.deepEqual(L.kCoreNodes(2),['A','B','C','D','X']);
 assert.deepEqual(L.kCoreNodes(3),[]);
 assert.throws(()=>L.kCoreNodes(-1),RangeError);
});
test('12: SIR transmission contact probability handles endpoints',()=>{
 assert.ok(Math.abs(L.sirRisk(.3,2)-.51)<1e-12);
 assert.equal(L.sirRisk(.4,0),0);
 assert.equal(L.sirRisk(1,3),1);
 assert.throws(()=>L.sirRisk(1.2,2),RangeError);
});
test('12: deterministic path obeys S+I+R=5 and one step infectious',()=>{
 const states=Array.from({length:6},(_,t)=>L.sirPathState(t));
 assert.deepEqual(states[0],['I','S','S','S','S']);
 assert.deepEqual(states[2],['R','R','I','S','S']);
 assert.deepEqual(states[5],['R','R','R','R','R']);
 assert.deepEqual(states.map(s=>s.filter(x=>x==='I').length),[1,1,1,1,1,0]);
});
test('13: synchronous absolute threshold yields exact differing cascade histories',()=>{
 assert.deepEqual(L.cascadeHistory(1).map(s=>s.length),[2,4,5,6,6]);
 assert.deepEqual(L.cascadeHistory(2).map(s=>s.length),[2,3,4,5,5]);
 assert.deepEqual(L.cascadeHistory(2)[1],['A','B','C']);
 assert.equal(L.cascadeHistory(2)[4].includes('F'),false);
 assert.equal(L.cascadeHistory(1)[4].includes('F'),true);
});
test('14: game payoffs and neutral voter copying are distinct functions',()=>{
 assert.deepEqual(L.donationPayoffs(3,1),[2,1,3,0]);
 assert.deepEqual(L.voterCopy('A'),['C','C','D','D']);
 assert.deepEqual(L.voterCopy('C'),['C','D','D','D']);
 assert.throws(()=>L.voterCopy('D'),RangeError);
});
test('15: hub and leaf deletion produce different LCC ratios',()=>{
 assert.deepEqual(L.robustnessAfterRemoval('leaf'),{largest:6,remaining:6,fraction:1});
 assert.deepEqual(L.robustnessAfterRemoval('hub'),{largest:1,remaining:6,fraction:1/6});
 assert.throws(()=>L.robustnessAfterRemoval('invalid'),RangeError);
});
test('15: load redistribution and capacity are separate from connectivity',()=>{
 assert.deepEqual(L.overloadAfterFailure(5),{load:6,extra:2});
 assert.deepEqual(L.overloadAfterFailure(6),{load:6,extra:0});
 assert.throws(()=>L.overloadAfterFailure(-1),RangeError);
});
