const test = require('node:test');
const assert = require('node:assert/strict');
const api = require('../../apps/shared/lesson-interactions.js');
const near=(a,b,eps=1e-10)=>assert.ok(Math.abs(a-b)<eps, String(a)+' vs '+String(b));
test('node2vec second-order weights normalize with two different q values',()=>{
 const a=api.node2vecToy(1,2);
 near(a.A,.4);near(a.C,.4);near(a.D,.2);near(a.A+a.C+a.D,1);
 near(api.node2vecToy(1,.5).D,.5);
 assert.throws(()=>api.node2vecToy(0,1),RangeError);
});
test('GCN symmetric degree normalization differs from naive mean',()=>{
 const r=api.gcnToy(1);
 near(r.normalized,1/Math.sqrt(6));near(r.mean,1/3);
 assert.ok(Math.abs(r.normalized-r.mean)>0.07);
});
test('GAT softmax is normalized and responds to logits',()=>{
 const r=api.gatToy(1);
 near(r.C,1/(1+Math.exp(-1)));near(r.A+r.C,1);
 assert.ok(api.gatToy(-1).C<r.C);
});
test('bridge removal changes components and density',()=>{
 const a=api.bridgeToy('keep'),b=api.bridgeToy('drop');
 assert.deepEqual(a,{components:2,lcc:6,density:1/3});
 assert.deepEqual(b,{components:3,lcc:3,density:2/7});
});
test('partition labels are permutation invariant when aligned',()=>{
 assert.deepEqual(api.labelAlignmentToy('swap'),{
 raw:0,aligned:1,description:'算法 B B A A：编号整体交换，划分仍相同。'
 });
 near(api.labelAlignmentToy('mixed').aligned,.5);
});
test('one paper projection yields combinatorial pair count',()=>{
 assert.equal(api.projectionEdges(4),6);
 assert.equal(api.projectionEdges(100),4950);
 assert.throws(()=>api.projectionEdges(1),RangeError);
});
test('dense-vs-CSR byte budget is explicitly specified',()=>{
 assert.deepEqual(api.sparseMemoryToy(1_000_000,5_000_000),{denseBytes:8_000_000_000_000,csrBytes:168_000_008});
 assert.throws(()=>api.sparseMemoryToy(10,1000),RangeError);
});
test('random walk star center occupation differs from node uniform sample',()=>{
 near(api.starSampleToy(5).uniform,1/6);
 near(api.starSampleToy(5).stationary,.5);
});
