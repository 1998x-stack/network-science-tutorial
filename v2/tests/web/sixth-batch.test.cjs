const test=require('node:test');
const assert=require('node:assert/strict');
const api=require('../../apps/shared/lesson-interactions.js');
const near=(a,b)=>assert.ok(Math.abs(a-b)<1e-10,String(a)+' != '+String(b));
test('26 LightGCN symmetric norm differs from naive mean',()=>{
 near(api.lightGCN26(1).symmetric,1/Math.sqrt(2));
 near(api.lightGCN26(1).naive,.5);
 assert.throws(()=>api.lightGCN26(NaN),RangeError);
});
test('26 BPR pairwise loss decreases as positive score margin grows',()=>{
 near(api.bpr26(0).loss,Math.log(2));
 near(api.bpr26(2).loss,Math.log1p(Math.exp(-2)));
 near(api.bpr26(0).sigmoid,.5);
 assert.ok(api.bpr26(2).loss<api.bpr26(0).loss);
});
test('27 brain threshold preserves node universe even when no edges',()=>{
 assert.deepEqual(api.brain27(.5),{edges:2,components:1});
 assert.deepEqual(api.brain27(.7),{edges:1,components:2});
 assert.deepEqual(api.brain27(1),{edges:0,components:3});
});
test('27 synthetic demographic parity gap is explicit math only',()=>{
 assert.deepEqual(api.fairness27(1),{a:.75,b:.25,gap:.5});
 assert.deepEqual(api.fairness27(3),{a:.75,b:.75,gap:0});
 assert.throws(()=>api.fairness27(5),RangeError);
});
test('28 training cutoff changes score but no future edge becomes train edge',()=>{
 assert.deepEqual(api.capstone28(1),{edges:2,score:0,futureIncluded:false});
 assert.deepEqual(api.capstone28(3),{edges:5,score:1,futureIncluded:false});
 assert.throws(()=>api.capstone28(5),RangeError);
});

