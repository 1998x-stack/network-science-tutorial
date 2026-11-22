const test=require('node:test');
const assert=require('node:assert/strict');
const Lesson=require('../../apps/shared/lesson-interactions.js');
test('BA choice probabilities normalize to one',()=>{
 assert.equal(Lesson.baProbability(3,10),.3);
 assert.ok(Math.abs([3,2,2,2,1].reduce((a,k)=>a+Lesson.baProbability(k,10),0)-1)<1e-12);
 assert.throws(()=>Lesson.baProbability(3,0),RangeError);
});
test('degree distribution from eight vertices includes isolates',()=>{
 assert.equal(Lesson.degreeFrequency(0),.25);
 assert.equal(Lesson.degreeFrequency(3),.125);
 assert.equal([0,1,2,3,5].reduce((a,k)=>a+Lesson.degreeFrequency(k),0),1);
 assert.equal(Lesson.degreeFrequency(4),0);
});
test('PageRank mass is conserved for every iteration including dangling redistribution',()=>{
 for(const steps of [0,1,2,10,30,250]){
  const rank=Lesson.pagerankDistribution(steps);
  assert.equal(rank.length,4);
  assert.ok(Math.abs(rank.reduce((a,b)=>a+b,0)-1)<1e-12);
  assert.ok(rank.every(x=>x>0));
 }
 const first=Lesson.pagerankDistribution(1);
 assert.ok(Math.abs(first[0]-.090625)<1e-12);
 assert.ok(Math.abs(first[1]-.515625)<1e-12);
 assert.ok(Math.abs(first[2]-.303125)<1e-12);
 assert.ok(Math.abs(first[3]-.090625)<1e-12);
 assert.throws(()=>Lesson.pagerankDistribution(-1),RangeError);
});
test('Toy modularity computes exact 5/14 for two triangles with a bridge',()=>{
 assert.equal(Lesson.toyModularity('two'),5/14);
 assert.equal(Lesson.toyModularity('all'),0);
 assert.throws(()=>Lesson.toyModularity('none'),RangeError);
});
