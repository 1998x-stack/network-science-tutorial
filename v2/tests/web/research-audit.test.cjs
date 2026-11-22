const test=require('node:test');
const assert=require('node:assert/strict');
const tool=require('../../../research/temporal-leakage.js');
const approx=(a,b)=>assert.ok(Math.abs(a-b)<1e-11,String(a)+' vs '+String(b));
test('time cutoff prevents or deliberately reveals future contamination',()=>{
 assert.deepEqual(tool.snapshotToy(2),{edges:4,cn:0,walk:0,gcn:0,observed:false,status:'仅训练期 t≤2：四条边，E 是孤立节点。'});
 const safe=tool.snapshotToy(3),illegal=tool.snapshotToy(5);
 assert.equal(safe.edges,5);assert.equal(safe.cn,0);assert.equal(safe.observed,false);
 assert.equal(illegal.edges,6);assert.equal(illegal.cn,1);assert.equal(illegal.observed,true);
 approx(illegal.walk,1/3);approx(illegal.gcn,1/4);
 assert.throws(()=>tool.snapshotToy(4),RangeError);
});
test('held-out user-item edge changes normalized LightGCN weights',()=>{
 const before=tool.recommendationToy(false),after=tool.recommendationToy(true);
 approx(before.U1X,1/Math.sqrt(2));approx(before.U2X,0);
 approx(after.U1X,.5);approx(after.U2X,.5);
 assert.throws(()=>tool.recommendationToy(1),TypeError);
});
test('temporal path ordering and same-time batching are distinct from static paths',()=>{
 assert.deepEqual(tool.temporalPathToy('ordered'),{A:0,B:1,C:2,D:3});
 assert.deepEqual(tool.temporalPathToy('reordered'),{A:0,B:3,C:null,D:null});
 assert.deepEqual(tool.temporalPathToy('simultaneous'),{A:0,B:1,C:null,D:null});
 assert.throws(()=>tool.temporalPathToy('future'),RangeError);
});
