const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const root=path.join(__dirname,'../..');
const Contract=require(path.join(root,'apps/shared/contract.js'));
const Layout=require(path.join(root,'apps/shared/layout.js'));
const Progress=require(path.join(root,'apps/shared/progress.js'));
const Compare=require(path.join(root,'apps/shared/comparison.js'));
function globals(script,varname){const x={window:{}};vm.runInNewContext(fs.readFileSync(path.join(root,script),'utf8'),x,{timeout:2000});return x.window[varname]}
const samples=globals('apps/graph-lab/samples.js','NETSCI_SAMPLES');
const report=globals('apps/web/data/comparison.js','NETSCI_COMPARISON');
const curriculum=JSON.parse(fs.readFileSync(path.join(root,'content/curriculum.json'),'utf8'));
const clone=x=>JSON.parse(JSON.stringify(x));

test('S01 three real artifacts pass strict contract',()=>{for(const key of ['er','ws','ba'])assert.equal(Contract.validate(samples[key]).experiment.model,key)});
test('reject mismatched metric counts',()=>{const x=clone(samples.er);x.metrics.nodes++;assert.throws(()=>Contract.validate(x),/数量/)});
test('reject duplicate edges reversed in undirected graph',()=>{const x=clone(samples.er);const e=x.graph.edges[0];x.graph.edges.push({source:e.target,target:e.source});x.metrics.edges++;assert.throws(()=>Contract.validate(x),/重复边/)});
test('reject duplicate ids, dangling edge, loops and directed input',()=>{
 const base=samples.er,x=clone(base);x.graph.nodes[1].id=x.graph.nodes[0].id;assert.throws(()=>Contract.validate(x),/节点 ID/);
 const y=clone(base);y.graph.edges[0].source='__missing__';assert.throws(()=>Contract.validate(y),/端点/);
 const z=clone(base);z.graph.edges[0].target=z.graph.edges[0].source;assert.throws(()=>Contract.validate(z),/自环/);
 const d=clone(base);d.graph.directed=true;assert.throws(()=>Contract.validate(d),/无向/);
});
test('reject missing or nonfinite scientific indicators',()=>{const x=clone(samples.ws);x.metrics.mean_degree='6';assert.throws(()=>Contract.validate(x),/有限数/);delete x.metrics.mean_degree;assert.throws(()=>Contract.validate(x),/指标/)});
test('force layout is deterministic, stable and retains isolated nodes',()=>{
 const a=Layout.createLayout(samples.ba.graph.nodes,samples.ba.graph.edges,{passes:3}),b=Layout.createLayout(samples.ba.graph.nodes,samples.ba.graph.edges,{passes:3});
 assert.deepEqual(a.points,b.points);assert.equal(a.points.length,samples.ba.graph.nodes.length);
 for(const p of a.points)assert.ok(Number.isFinite(p.x)&&Number.isFinite(p.y)&&Math.abs(p.x)<=1.000001&&Math.abs(p.y)<=1.000001);
});
test('comparison uses actual independent runs and sample SD',()=>{const r=Compare.summarize(report,'mean_degree');assert.deepEqual(r.map(x=>x.n),[5,5,5]);assert.equal(r.find(x=>x.model==='ws').mean,6);assert.ok(r.find(x=>x.model==='er').sd>0);});
test('28 chapters contiguous, source structure and links generated',()=>{assert.equal(curriculum.chapters.length,28);for(let i=0;i<28;i++){const id=String(i+1).padStart(2,'0');assert.equal(curriculum.chapters[i].num,id);const file=path.join(root,'apps/web/lessons',`${id}.html`);assert.ok(fs.existsSync(file));assert.match(fs.readFileSync(file,'utf8'),new RegExp('第'+(i+1)+'章'));}});
test('legacy reading progress works and storage-disabled mode is safe',()=>{
 const values=new Map(),storage={getItem:key=>values.get(key)||null,setItem:(key,v)=>values.set(key,v)};
 Progress.mark(storage,'03',true);Progress.setLast(storage,'03');assert.equal(Progress.completed(storage,'03'),true);assert.equal(Progress.resume(storage),'03');assert.equal(Progress.count(storage,curriculum.chapters),1);
 const blocked={getItem:()=>{throw Error('blocked');},setItem:()=>{throw Error('blocked');}};
 assert.equal(Progress.completed(blocked,'02'),false);assert.equal(Progress.mark(blocked,'02',true),false);
});
test('web scripts use only local relative assets',()=>{for(const html of ['index.html','lab.html','compare.html','datasets.html']){const doc=fs.readFileSync(path.join(root,'apps/web',html),'utf8');assert.doesNotMatch(doc,/src="https?:\/\//);assert.match(doc,/<main/);}});
