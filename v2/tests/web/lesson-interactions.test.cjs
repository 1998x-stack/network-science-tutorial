const test=require('node:test');const assert=require('node:assert/strict');const Lesson=require('../../apps/shared/lesson-interactions.js');
test('ER expectations are analytical values',()=>{const x=Lesson.erExpected(100,0.05);assert.equal(x.degree,4.95);assert.equal(x.edges,247.5);assert.equal(Lesson.erExpected(1,0.5).edges,0);});
test('WS slider describes qualitative regimes only',()=>{assert.match(Lesson.wsRegime(0),/规则环/);assert.match(Lesson.wsRegime(0.05),/少量重连/);assert.match(Lesson.wsRegime(0.5),/中等重连/);assert.match(Lesson.wsRegime(1),/高度重连/);});
test('metric explanations distinguish clustering and transitivity',()=>{assert.match(Lesson.metricText('clustering'),/全局传递性/);assert.match(Lesson.metricText('distance'),/不可达/);});
