const test=require('node:test');
const assert=require('node:assert/strict');
const L=require('../../apps/shared/lesson-interactions.js');

test('16: common-neighbor and Adamic-Adar candidate scores computed on train edges',()=>{
 const ad=L.linkPredictionScores('AD'),ae=L.linkPredictionScores('AE');
 assert.equal(ad.cn,2);assert.deepEqual(ad.common,['B','C']);
 assert.ok(Math.abs(ad.jaccard-2/3)<1e-12);
 assert.ok(Math.abs(ad.adamic-2/Math.log(3))<1e-12);
 assert.deepEqual(ae,{cn:0,jaccard:0,adamic:0,common:[]});
 assert.throws(()=>L.linkPredictionScores('AB'),RangeError);
});
test('18: original event log is not an undirected edge list',()=>{
 const raw=L.collectionProjection('events'),projection=L.collectionProjection('graph');
 assert.equal(raw.count,6);assert.equal(projection.count,4);
 assert.equal(raw.nodes,projection.nodes);
 assert.throws(()=>L.collectionProjection('unknown'),RangeError);
});
test('19: supra paths, flat paths and blocked coupling differ',()=>{
 assert.deepEqual(L.multiplexPath('allowed').distance,3);
 assert.deepEqual(L.multiplexPath('flat').distance,2);
 assert.equal(L.multiplexPath('blocked').distance,null);
 assert.equal(L.multiplexPath('allowed').switches,1);
 assert.throws(()=>L.multiplexPath('bad'),RangeError);
});
test('20: strict temporal scan rejects causal order inversions',()=>{
 assert.deepEqual(L.temporalEarliest('ordered'),{A:0,B:1,C:2,D:3});
 assert.deepEqual(L.temporalEarliest('scrambled'),{A:0,B:3});
 assert.deepEqual(L.temporalEarliest('simultaneous'),{A:0,B:1});
 assert.throws(()=>L.temporalEarliest('future'),RangeError);
});
