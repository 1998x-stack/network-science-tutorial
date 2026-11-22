(function(root,factory){'use strict';const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;if(root)root.NetsciLesson=api;if(typeof document!=='undefined'){const boot=()=>api.init(document);if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot,{once:true});else boot();}})(typeof globalThis!=='undefined'?globalThis:this,function(){'use strict';function erExpected(n,p){return {degree:(n-1)*p,edges:n*(n-1)*p/2};}function wsRegime(beta){if(beta<=0)return '规则环：局部连接完整保留，路径通常较长。';if(beta<=0.1)return '少量重连区间：局部连接大多保留，少数捷径可能显著缩短全局路径。';if(beta<=0.5)return '中等重连：局部聚集逐步下降，网络路径继续缩短。';return '高度重连：网络趋向随机化，局部聚集结构明显减弱。';}function metricText(key){return ({degree:'度数描述单个节点的连接数量；度分布描述这些连接在全网如何分配。',density:'密度把实际边数与最多可能的边数比较；比较不同规模网络时，它比单看边数更有意义。',clustering:'聚集系数衡量一个节点的邻居是否彼此连接；平均局部聚集与全局传递性并不是同一个量。',distance:'路径长度衡量节点间需要经过几条边；不连通网络必须先说明如何处理不可达节点对。'})[key]||'选择一个指标，查看它回答的结构问题。';}function init(doc){doc.querySelectorAll('[data-lesson-action]').forEach(button=>button.addEventListener('click',()=>{const action=button.dataset.lessonAction;if(action==='euler-check'){const out=doc.getElementById('euler-result');if(out)out.textContent='度数为 3、3、5、3：共有 4 个奇度顶点。连通无向多重图只有 0 或 2 个奇度顶点时才存在欧拉回路或欧拉路径，因此七桥图无解。';}if(action==='representation'){const value=button.dataset.value,group=button.closest('[data-demo="representation"]');group.querySelectorAll('[data-representation-panel]').forEach(panel=>panel.hidden=panel.dataset.representationPanel!==value);group.querySelectorAll('[data-lesson-action="representation"]').forEach(item=>item.setAttribute('aria-pressed',String(item===button)));const out=group.querySelector('#representation-result');if(out)out.textContent='当前显示 '+({matrix:'邻接矩阵',list:'邻接表',edges:'边列表'}[value])+'；三种形式仍然表示同一组四条边。';}if(action==='metric'){const group=button.closest('[data-demo="metrics"]');group.querySelectorAll('[data-lesson-action="metric"]').forEach(item=>item.setAttribute('aria-pressed',String(item===button)));const out=group.querySelector('#metric-result');if(out)out.textContent=metricText(button.dataset.value);}}));doc.querySelectorAll('[data-er-p]').forEach(input=>{const update=()=>{const p=Number(input.value),n=100,v=erExpected(n,p),group=input.closest('[data-demo="er"]');group.querySelector('[data-er-p-value]').textContent=p.toFixed(3);group.querySelector('[data-er-degree]').textContent=v.degree.toFixed(3);group.querySelector('[data-er-edges]').textContent=v.edges.toFixed(3);group.querySelector('[data-er-note]').textContent='n 固定为 100；理论期望平均度为 '+v.degree.toFixed(3)+'，理论期望边数为 '+v.edges.toFixed(3)+'。单次抽样的实际值会随机波动。';};input.addEventListener('input',update);update();});doc.querySelectorAll('[data-ws-beta]').forEach(input=>{const update=()=>{const beta=Number(input.value),group=input.closest('[data-demo="ws"]');group.querySelector('[data-ws-beta-value]').textContent=beta.toFixed(2);group.querySelector('[data-ws-regime]').textContent=wsRegime(beta);};input.addEventListener('input',update);update();});}
function baProbability(degree,total){if(total<=0||degree<0||degree>total)throw new RangeError('invalid degree weights');return degree/total;}
function degreeFrequency(k){const counts={0:2,1:2,2:2,3:1,5:1};return Object.prototype.hasOwnProperty.call(counts,k)?counts[k]/8:0;}
function pagerankDistribution(steps,alpha=0.85){
 if(!Number.isInteger(steps)||steps<0||steps>1000||alpha<0||alpha>=1)throw new RangeError('invalid PageRank parameters');
 const neighbors=[[1],[2],[1],[]];let rank=[.25,.25,.25,.25];
 for(let t=0;t<steps;t++){
  const next=Array(4).fill((1-alpha)/4);
  for(let i=0;i<4;i++){
   const dest=neighbors[i].length?neighbors[i]:[0,1,2,3];
   for(const j of dest)next[j]+=alpha*rank[i]/dest.length;
  }
  rank=next;
 }
 return rank;
}
function toyModularity(partition){if(partition==='two')return 5/14;if(partition==='all')return 0;throw new RangeError('invalid partition');}
function initAdvanced(doc){
 const setPressed=(group,attribute,selected)=>group.querySelectorAll('['+attribute+']').forEach(x=>x.setAttribute('aria-pressed',String(x===selected)));
 doc.querySelectorAll('[data-demo="ba"]').forEach(group=>{
  const degrees={A:3,B:2,C:2,D:2,E:1},out=group.querySelector('[data-ba-result]');
  group.querySelectorAll('[data-ba-node]').forEach(button=>button.addEventListener('click',()=>{
   const key=button.dataset.baNode,k=degrees[key];
   setPressed(group,'data-ba-node',button);
   out.textContent=key+' 的权重是 '+k+'/10，被选中概率为 '+(100*baProbability(k,10)).toFixed(0)+'%。';
  }));
 });
 doc.querySelectorAll('[data-demo="degree"]').forEach(group=>{
  const out=group.querySelector('[data-degree-result]');
  group.querySelectorAll('[data-degree-k]').forEach(button=>button.addEventListener('click',()=>{
   const k=Number(button.dataset.degreeK),count=Math.round(8*degreeFrequency(k));
   setPressed(group,'data-degree-k',button);
   out.textContent='度数 '+k+'：'+count+'/8 个节点，频率 '+(degreeFrequency(k)*100).toFixed(1).replace('.0','')+'%。';
  }));
 });
 doc.querySelectorAll('[data-demo="centrality"]').forEach(group=>{
  const out=group.querySelector('[data-cent-result]');
  const descriptions={
   degree:'度中心性：C、D 各为 3/5=0.6。它只衡量直接连接数量。',
   between:'介数中心性：C、D 各为 6/10=0.6；其余四个节点为 0。这里计算的是非端点最短路径。',
   eigen:'特征向量中心性：连接高分邻居也会提高得分。实际数值应由邻接矩阵的主特征向量计算。'
  };
  group.querySelectorAll('[data-cent-kind]').forEach(button=>button.addEventListener('click',()=>{
   setPressed(group,'data-cent-kind',button);out.textContent=descriptions[button.dataset.centKind];
  }));
 });
 doc.querySelectorAll('[data-demo="pagerank"]').forEach(group=>{
  const slider=group.querySelector('[data-pr-steps]'),label=group.querySelector('[data-pr-step-value]'),note=group.querySelector('[data-pr-note]');
  const draw=()=>{
   const steps=Number(slider.value),r=pagerankDistribution(steps);
   label.textContent=String(steps);
   for(const [i,key] of ['A','B','C','D'].entries())group.querySelector('[data-pr-node="'+key+'"]').textContent=r[i].toFixed(4);
   note.textContent='第 '+steps+' 步：概率总和 = '+r.reduce((a,b)=>a+b,0).toFixed(6)+'；每步包含 α=0.85 的链接转移与悬挂概率重分配。';
  };
  slider.addEventListener('input',draw);draw();
 });
 doc.querySelectorAll('[data-demo="modularity"]').forEach(group=>{
  const count=group.querySelector('[data-mod-count]'),value=group.querySelector('[data-mod-value]'),note=group.querySelector('[data-mod-explain]');
  group.querySelectorAll('[data-mod-part]').forEach(button=>button.addEventListener('click',()=>{
   setPressed(group,'data-mod-part',button);
   const type=button.dataset.modPart;
   count.textContent=type==='two'?'2':'1';
   value.textContent=toyModularity(type).toFixed(6);
   note.textContent=type==='two'?'每组内部 3 条边、总度数 7，Q=5/14。只对这张固定的 7 边图有效。':'整张图视为一个社团时，内部边与随机基线相等，Q=0。';
  }));
 });
}


function kCoreNodes(k) {
 if (!Number.isInteger(k) || k<0 || k>10) throw new RangeError('invalid core level');
 const adj={A:['B','X','L1'],B:['A','X'],X:['A','B','C','D'],
 C:['X','D'],D:['X','C','L2'],L1:['A'],L2:['D']};
 let remaining=new Set(Object.keys(adj));
 while(true){
  const bad=[...remaining].filter(v=>adj[v].filter(w=>remaining.has(w)).length<k);
  if(bad.length===0)break;
  for(const v of bad)remaining.delete(v);
 }
 return [...remaining].sort();
}
function sirRisk(beta,m){
 if(!Number.isFinite(beta)||beta<0||beta>1||!Number.isInteger(m)||m<0)throw new RangeError('invalid infection parameters');
 return 1-Math.pow(1-beta,m);
}
function sirPathState(t){
 if(!Number.isInteger(t)||t<0||t>5)throw new RangeError('invalid SIR step');
 return Array.from({length:5},(_,i)=>i<t?'R':i===t?'I':'S');
}
function cascadeHistory(threshold,steps=4){
 if(![1,2].includes(threshold)||!Number.isInteger(steps)||steps<0||steps>100)throw new RangeError('invalid cascade parameters');
 const adj={A:['C'],B:['C','D'],C:['A','B','D','E'],D:['B','C','E'],E:['C','D','F'],F:['E']};
 let active=new Set(['A','B']),history=[[...active].sort()];
 for(let t=0;t<steps;t++){
  const added=Object.keys(adj).filter(v=>!active.has(v)&&adj[v].filter(u=>active.has(u)).length>=threshold);
  active=new Set([...active,...added]);
  history.push([...active].sort());
 }
 return history;
}
function donationPayoffs(benefit,cost=1){
 if(!Number.isFinite(benefit)||!Number.isFinite(cost)||benefit<0||cost<0)throw new RangeError('invalid donation game parameters');
 return [benefit-cost,benefit-2*cost,benefit,0];
}
function voterCopy(neighbor){
 if(neighbor==='A')return ['C','C','D','D'];
 if(neighbor==='C')return ['C','D','D','D'];
 throw new RangeError('B can only copy A or C');
}
function robustnessAfterRemoval(choice){
 if(choice==='leaf')return {largest:6,remaining:6,fraction:1};
 if(choice==='hub')return {largest:1,remaining:6,fraction:1/6};
 throw new RangeError('invalid node removal');
}
function overloadAfterFailure(capacity){
 if(!Number.isFinite(capacity)||capacity<0)throw new RangeError('invalid capacity');
 const load=4+4/2;
 return {load,extra:load>capacity?2:0};
}
function initThirdBatch(doc) {
 const press=(group,attr,selected)=>group.querySelectorAll('['+attr+']').forEach(b=>b.setAttribute('aria-pressed',String(b===selected)));
 doc.querySelectorAll('[data-demo="core"]').forEach(group=>{
  const out=group.querySelector('[data-core-output]');
  group.querySelectorAll('[data-core-k]').forEach(b=>b.addEventListener('click',()=>{
   const k=Number(b.dataset.coreK),nodes=kCoreNodes(k);
   press(group,'data-core-k',b);
   out.textContent=k+'-core 保留 '+nodes.length+' 个节点：'+(nodes.length?nodes.join('、'):'空集')+'。';
  }));
 });
 doc.querySelectorAll('[data-demo="sir-risk"]').forEach(group=>{
  const beta=group.querySelector('[data-sir-beta]'),label=group.querySelector('[data-sir-beta-label]'),out=group.querySelector('[data-sir-risk-output]');
  let m=2;
  const update=()=>{
   const b=Number(beta.value);
   label.textContent=b.toFixed(2);
   out.textContent='m='+m+'，β='+b.toFixed(2)+'；至少一次成功的理论概率 = '+(100*sirRisk(b,m)).toFixed(2)+'%。';
  };
  group.querySelectorAll('[data-sir-m]').forEach(button=>button.addEventListener('click',()=>{m=Number(button.dataset.sirM);press(group,'data-sir-m',button);update();}));
  beta.addEventListener('input',update);update();
 });
 doc.querySelectorAll('[data-demo="sir-path"]').forEach(group=>{
  const slider=group.querySelector('[data-sir-t]'),label=group.querySelector('[data-sir-t-label]'),out=group.querySelector('[data-sir-state]');
  const draw=()=>{
   const t=Number(slider.value),s=sirPathState(t);
   label.textContent=String(t);
   for(const status of ['S','I','R'])group.querySelector('[data-sir-'+status.toLowerCase()+']').textContent=String(s.filter(v=>v===status).length);
   out.textContent='t='+t+'：'+s.map((v,i)=>'ABCDE'[i]+'='+v).join('，')+'。';
  };
  slider.addEventListener('input',draw);draw();
 });
 doc.querySelectorAll('[data-demo="cascade"]').forEach(group=>{
  const slider=group.querySelector('[data-cascade-step]'),label=group.querySelector('[data-cascade-t-label]'),out=group.querySelector('[data-cascade-status]');
  let rule=2;
  const draw=()=>{
   const t=Number(slider.value),history=cascadeHistory(rule,4),active=history[t];
   const last=t?history[t-1]:[];
   const newly=active.filter(v=>!last.includes(v));
   label.textContent=String(t);
   group.querySelector('[data-cascade-count]').textContent=active.length+' / 6';
   group.querySelector('[data-cascade-new]').textContent=String(newly.length);
   out.textContent='t='+t+'：已采纳 '+active.join('、')+'；未采纳 '+['A','B','C','D','E','F'].filter(v=>!active.includes(v)).join('、')+'。';
  };
  group.querySelectorAll('[data-cascade-rule]').forEach(b=>b.addEventListener('click',()=>{rule=Number(b.dataset.cascadeRule);press(group,'data-cascade-rule',b);draw();}));
  slider.addEventListener('input',draw);draw();
 });
 doc.querySelectorAll('[data-demo="game"]').forEach(group=>{
  const slider=group.querySelector('[data-game-benefit]'),label=group.querySelector('[data-game-b-label]'),out=group.querySelector('[data-game-result]');
  const draw=()=>{
   const b=Number(slider.value),pay=donationPayoffs(b);
   label.textContent=b.toFixed(1);
   ['a','b','c','d'].forEach((name,i)=>group.querySelector('[data-game-'+name+']').textContent=pay[i].toFixed(1));
   out.textContent='b='+b.toFixed(1)+'，c=1；当前策略始终为 C、C、D、D。改变收益参数并不会自动更新策略。';
  };
  slider.addEventListener('input',draw);draw();
 });
 doc.querySelectorAll('[data-demo="voter"]').forEach(group=>{
  const out=group.querySelector('[data-voter-result]');
  group.querySelectorAll('[data-voter-neighbor]').forEach(b=>b.addEventListener('click',()=>{
   const from=b.dataset.voterNeighbor,s=voterCopy(from);
   press(group,'data-voter-neighbor',b);
   out.textContent='B 复制 '+from+' 后变为'+(s[1]==='C'?'合作':'背叛')+'；全网状态为 '+s.join('、')+'。';
  }));
 });
 doc.querySelectorAll('[data-demo="robust"]').forEach(group=>{
  const size=group.querySelector('[data-robust-size]'),r=group.querySelector('[data-robust-r]'),note=group.querySelector('[data-robust-note]');
  group.querySelectorAll('[data-robust-choice]').forEach(b=>b.addEventListener('click',()=>{
   press(group,'data-robust-choice',b);
   const which=b.dataset.robustChoice,v=robustnessAfterRemoval(which);
   size.textContent=v.largest+' / '+v.remaining;r.textContent=v.fraction.toFixed(3);
   note.textContent=which==='hub'?'移除中心枢纽：六个叶子彼此断开，最大连通分量只有 1/6。':'移除叶子：剩余 6 个节点仍连成一块，连通比例 1。';
  }));
 });
 doc.querySelectorAll('[data-demo="overload"]').forEach(group=>{
  const load=group.querySelector('[data-overload-load]'),count=group.querySelector('[data-overload-fail]'),status=group.querySelector('[data-overload-status]');
  group.querySelectorAll('[data-overload-cap]').forEach(b=>b.addEventListener('click',()=>{
   press(group,'data-overload-cap',b);
   const capacity=Number(b.dataset.overloadCap),v=overloadAfterFailure(capacity);
   load.textContent=String(v.load);count.textContent=String(v.extra);
   status.textContent=v.extra?'容量 '+capacity+'，小于重新分配后的负载 6：A 与 C 均超载失效；包括原始 B 故障在内，共 3 台停止工作。':'容量 '+capacity+'，等于每台剩余负载 6：A 与 C 继续工作，但不再通过已失效的 B 连通。';
  }));
 });
}


function linkPredictionScores(candidate){
 if(candidate==='AD')return {cn:2,jaccard:2/3,adamic:2/Math.log(3),common:['B','C']};
 if(candidate==='AE')return {cn:0,jaccard:0,adamic:0,common:[]};
 throw new RangeError('unknown training-graph candidate');
}
function collectionProjection(kind){
 if(kind==='events')return {count:6,nodes:5,explanation:'六条独立的原始交互事件；方向、时间与同一对节点的重复事件均保留。'};
 if(kind==='graph')return {count:4,nodes:5,explanation:'无向简单图：A→B 与 B→A 合并，自环 C→C 排除；剩余 A–B、B–C、C–D、D–E 四条边。'};
 throw new RangeError('unknown collection projection');
}
function multiplexPath(mode){
 if(mode==='allowed')return {distance:3,switches:1,explanation:'多层路径：B_social → C_social → C_collab → D_collab，共 3 条边、1 次层间切换。'};
 if(mode==='flat')return {distance:2,switches:null,explanation:'扁平化把不同关系合并：B → C → D 是 2 条边，但已无法表达层间转换。'};
 if(mode==='blocked')return {distance:null,switches:0,explanation:'跨层边被禁用：(B,social) 到 (D,collab) 不可达；两个层虽然共享实体名字，却是分离状态。'};
 throw new RangeError('unknown multilayer coupling mode');
}
function temporalEarliest(schedule) {
 const plans={
  ordered:[['A','B',1],['B','C',2],['C','D',3]],
  scrambled:[['A','B',3],['B','C',1],['C','D',2]],
  simultaneous:[['A','B',1],['B','C',1],['C','D',1]]
 };
 if(!Object.prototype.hasOwnProperty.call(plans,schedule))throw new RangeError('unknown schedule');
 const events=plans[schedule],arrivals={A:0};
 const times=[...new Set(events.map(item=>item[2]))].sort((a,b)=>a-b);
 for(const t of times){
  const prior={...arrivals},pending={...arrivals};
  for(const [a,b,when] of events){
   if(when!==t)continue;
   for(const [source,target] of [[a,b],[b,a]]){
    if(Object.prototype.hasOwnProperty.call(prior,source)&&prior[source]<t){
     pending[target]=Math.min(pending[target]??Infinity,t);
    }
   }
  }
  Object.assign(arrivals,pending);
 }
 return arrivals;
}
function initFourthBatch(doc){
 const press=(group,attr,selected)=>group.querySelectorAll('['+attr+']').forEach(b=>b.setAttribute('aria-pressed',String(b===selected)));
 doc.querySelectorAll('[data-demo="link-prediction"]').forEach(group=>{
  const cn=group.querySelector('[data-lp-cn]'),j=group.querySelector('[data-lp-j]'),aa=group.querySelector('[data-lp-aa]'),out=group.querySelector('[data-lp-explain]');
  group.querySelectorAll('[data-lp-pair]').forEach(b=>b.addEventListener('click',()=>{
   const candidate=b.dataset.lpPair,r=linkPredictionScores(candidate);
   press(group,'data-lp-pair',b);
   cn.textContent=String(r.cn);j.textContent=r.jaccard.toFixed(4);aa.textContent=r.adamic.toFixed(4);
   out.textContent=candidate==='AD'?'A–D 的共同邻居是 B、C。评分来自训练图，不表示已发生新边。':'A–E 没有共同邻居：在这个基于邻居的特征里分数为零；不等于未来永远不连边。';
  }));
 });
 doc.querySelectorAll('[data-demo="layout"]').forEach(group=>{
  const picture=group.querySelector('[data-layout-image]'),caption=group.querySelector('[data-layout-caption]'),out=group.querySelector('[data-layout-output]');
  const defaultImage=picture.getAttribute('src');
  const circularImage=group.querySelector('[data-layout-circular-payload]').getAttribute('src');
  group.querySelectorAll('[data-layout-mode]').forEach(b=>b.addEventListener('click',()=>{
   const mode=b.dataset.layoutMode;
   press(group,'data-layout-mode',b);
   picture.setAttribute('src',mode==='circular'?circularImage:defaultImage);
   picture.setAttribute('alt',mode==='schematic'?'两组三角形由 C–D 一条桥相连的结构示意布局。':'相同六节点七边在圆周上的示意布局。');
   caption.textContent=mode==='schematic'?'当前展示手工结构布局；全部七条边保持不变。':'当前展示圆周布局；全部七条边保持不变。';
   out.textContent=mode==='schematic'?'结构示意：桥边 C–D 易于辨认，图中横向距离不是任何实测距离。':'圆周示意：节点均匀排布、边交叉可能改变，但七条边的存在状态完全不变。';
  }));
 });
 doc.querySelectorAll('[data-demo="collection"]').forEach(group=>{
  const count=group.querySelector('[data-collection-count]'),nodes=group.querySelector('[data-collection-nodes]'),out=group.querySelector('[data-collection-output]');
  group.querySelectorAll('[data-collection-view]').forEach(b=>b.addEventListener('click',()=>{
   const view=b.dataset.collectionView,r=collectionProjection(view);
   press(group,'data-collection-view',b);
   count.textContent=String(r.count);nodes.textContent=String(r.nodes);out.textContent=r.explanation;
  }));
 });
 doc.querySelectorAll('[data-demo="multilayer"]').forEach(group=>{
  const length=group.querySelector('[data-multi-length]'),switches=group.querySelector('[data-multi-switch]'),out=group.querySelector('[data-multi-output]');
  group.querySelectorAll('[data-multi-mode]').forEach(b=>b.addEventListener('click',()=>{
   const mode=b.dataset.multiMode,r=multiplexPath(mode);
   press(group,'data-multi-mode',b);
   length.textContent=r.distance===null?'不可达':String(r.distance);
   switches.textContent=r.switches===null?'已折叠':String(r.switches);
   out.textContent=r.explanation;
  }));
 });
 doc.querySelectorAll('[data-demo="temporal"]').forEach(group=>{
  const count=group.querySelector('[data-temporal-count]'),arrival=group.querySelector('[data-temporal-arrival]'),out=group.querySelector('[data-temporal-output]');
  group.querySelectorAll('[data-temporal-schedule]').forEach(b=>b.addEventListener('click',()=>{
   const schedule=b.dataset.temporalSchedule,r=temporalEarliest(schedule);
   press(group,'data-temporal-schedule',b);
   count.textContent=Object.keys(r).length+' / 4';
   arrival.textContent=r.D===undefined?'不可达':String(r.D);
   out.textContent=schedule==='ordered'?'严格时间递增：A@0 → B@1 → C@2 → D@3。静态图的距离始终是 3 条边。':schedule==='scrambled'?'错序：B–C@1 和 C–D@2 都早于 A–B@3；A 只能在 t=3 到达 B。':'同时：三条边都在 t=1，严格递增模型不允许同一时间的多跳；A 只到 B。';
  }));
 });
}


/* Batch 21–25: pure, deterministic arithmetic contracts shared by the lesson UI and unit tests. */
function node2vecToy(p,q) {
 if(!Number.isFinite(p)||!Number.isFinite(q)||p<=0||q<=0)throw new RangeError('p and q must be positive');
 const a=1/p,c=1,d=1/q,total=a+c+d;
 return {A:a/total,C:c/total,D:d/total};
}
function gcnToy(x) {
 if(!Number.isFinite(x))throw new RangeError('x must be finite');
 return {normalized:x/Math.sqrt(6),mean:x/3};
}
function gatToy(logit) {
 if(!Number.isFinite(logit))throw new RangeError('logit must be finite');
 const c=1/(1+Math.exp(-logit));
 return {A:1-c,C:c};
}
function bridgeToy(which) {
 if(which==='keep')return {components:2,lcc:6,density:1/3};
 if(which==='drop')return {components:3,lcc:3,density:2/7};
 throw new RangeError('choose keep or drop');
}
function labelAlignmentToy(which) {
 if(which==='same')return {raw:1,aligned:1,description:'算法 A A B B：完全相同。'};
 if(which==='swap')return {raw:0,aligned:1,description:'算法 B B A A：编号整体交换，划分仍相同。'};
 if(which==='mixed')return {raw:.5,aligned:.5,description:'算法 A B B A：无法通过整体置换消除分歧。'};
 throw new RangeError('unknown partition');
}
function projectionEdges(n) {
 if(!Number.isInteger(n)||n<2||n>10000)throw new RangeError('invalid paper author count');
 return n*(n-1)/2;
}
function sparseMemoryToy(n,m=5*n) {
 if(!Number.isInteger(n)||n<2||!Number.isInteger(m)||m<0||m>n*(n-1)/2)throw new RangeError('invalid simple graph');
 return {denseBytes:8*n*n,csrBytes:8*(n+1)+32*m};
}
function starSampleToy(leaves) {
 if(!Number.isInteger(leaves)||leaves<1)throw new RangeError('star needs leaves');
 return {uniform:1/(leaves+1),stationary:0.5};
}
function initFifthBatch(doc){
 const updateText=(scope,selector,value)=>{const el=scope.querySelector(selector);if(el)el.textContent=String(value);};
 const press=(scope,attr,chosen)=>scope.querySelectorAll('['+attr+']').forEach(el=>el.setAttribute('aria-pressed',String(el===chosen)));
 doc.querySelectorAll('[data-demo="n2v"]').forEach(group=>{
  const p=group.querySelector('[data-n2v-p]'),q=group.querySelector('[data-n2v-q]');
  const update=()=>{const a=Number(p.value),b=Number(q.value),r=node2vecToy(a,b);
   updateText(group,'[data-n2v-p-label]',a.toFixed(2));updateText(group,'[data-n2v-q-label]',b.toFixed(2));
   for(const k of ['A','C','D'])updateText(group,'[data-n2v-'+k.toLowerCase()+']',r[k].toFixed(3));
   updateText(group,'[data-n2v-note]','总概率 = '+(r.A+r.C+r.D).toFixed(3)+'；调整 p/q 改变局部权重，不产生训练后节点嵌入。');
  };
  p.addEventListener('input',update);q.addEventListener('input',update);update();
 });
 doc.querySelectorAll('[data-demo="gcn"]').forEach(group=>{
  const inp=group.querySelector('[data-gcn-x]'),update=()=>{const x=Number(inp.value),r=gcnToy(x);
   updateText(group,'[data-gcn-x-label]',x.toFixed(2));
   updateText(group,'[data-gcn-output]',r.normalized.toFixed(4));
   updateText(group,'[data-gcn-mean]',r.mean.toFixed(4));};
  inp.addEventListener('input',update);update();
 });
 doc.querySelectorAll('[data-demo="gat"]').forEach(group=>{
  const inp=group.querySelector('[data-gat-logit]'),update=()=>{const l=Number(inp.value),r=gatToy(l);
   updateText(group,'[data-gat-logit-label]',l.toFixed(2));
   updateText(group,'[data-gat-a]',r.A.toFixed(3));
   updateText(group,'[data-gat-c]',r.C.toFixed(3));};
  inp.addEventListener('input',update);update();
 });
 doc.querySelectorAll('[data-demo="bridge"]').forEach(group=>{
  const update=b=>{press(group,'data-bridge-choice',b);const r=bridgeToy(b.dataset.bridgeChoice);
   updateText(group,'[data-bridge-components]',r.components);
   updateText(group,'[data-bridge-lcc]',r.lcc+' / 7');
   updateText(group,'[data-bridge-density]',r.density.toFixed(6));
   updateText(group,'[data-bridge-note]',b.dataset.bridgeChoice==='keep'?'桥保留：六节点分量连通，G 孤立。':'移除桥：两组三角形分离，G 仍孤立。');};
  group.querySelectorAll('[data-bridge-choice]').forEach(b=>b.addEventListener('click',()=>update(b)));
  update(group.querySelector('[data-bridge-choice="keep"]'));
 });
 doc.querySelectorAll('[data-demo="labels"]').forEach(group=>{
  const update=b=>{press(group,'data-label-choice',b);const r=labelAlignmentToy(b.dataset.labelChoice);
   updateText(group,'[data-label-raw]',(r.raw*100)+'%');
   updateText(group,'[data-label-aligned]',(r.aligned*100)+'%');
   updateText(group,'[data-label-note]','真实标签 A A B B；'+r.description);};
  group.querySelectorAll('[data-label-choice]').forEach(b=>b.addEventListener('click',()=>update(b)));
  update(group.querySelector('[data-label-choice="same"]'));
 });
 doc.querySelectorAll('[data-demo="projection"]').forEach(group=>{
  const inp=group.querySelector('[data-projection-n]'),update=()=>{const n=Number(inp.value);
   updateText(group,'[data-projection-n-label]',n);
   updateText(group,'[data-projection-bipartite]',n);
   updateText(group,'[data-projection-edges]',projectionEdges(n));};
  inp.addEventListener('input',update);update();
 });
 doc.querySelectorAll('[data-demo="memory"]').forEach(group=>{
  const inp=group.querySelector('[data-memory-n]'),update=()=>{const n=Number(inp.value),r=sparseMemoryToy(n);
   updateText(group,'[data-memory-n-label]',n);
   updateText(group,'[data-memory-dense]',(r.denseBytes/1e6).toFixed(1)+' MB');
   updateText(group,'[data-memory-csr]',(r.csrBytes/1e6).toFixed(1)+' MB');};
  inp.addEventListener('input',update);update();
 });
 doc.querySelectorAll('[data-demo="sampling"]').forEach(group=>{
  const inp=group.querySelector('[data-sampling-leaves]'),update=()=>{const n=Number(inp.value),r=starSampleToy(n);
   updateText(group,'[data-sampling-leaves-label]',n);
   updateText(group,'[data-sampling-uniform]',r.uniform.toFixed(4));
   updateText(group,'[data-sampling-walk]',r.stationary.toFixed(4));};
  inp.addEventListener('input',update);update();
 });
}


/* Chapters 26–28: pure numerical contracts and progressively enhanced controls. */
function lightGCN26(x) {
 if(!Number.isFinite(x))throw new RangeError('finite initial signal required');
 return {symmetric:x/Math.sqrt(2),naive:x/2};
}
function bpr26(delta) {
 if(!Number.isFinite(delta))throw new RangeError('finite score difference required');
 return {sigmoid:1/(1+Math.exp(-delta)),loss:Math.log1p(Math.exp(-delta))};
}
function brain27(tau) {
 if(!Number.isFinite(tau)||tau<0||tau>1)throw new RangeError('0 <= threshold <= 1');
 const count=[.8,.6,.2].filter(w=>w+1e-10>=tau).length;
 return {edges:count,components:count>=2?1:count===1?2:3};
}
function fairness27(count) {
 if(!Number.isInteger(count)||count<0||count>4)throw new RangeError('count 0..4');
 return {a:.75,b:count/4,gap:Math.abs(.75-count/4)};
}
function capstone28(cutoff) {
 if(cutoff===1)return {edges:2,score:0,futureIncluded:false};
 if(cutoff===3)return {edges:5,score:1,futureIncluded:false};
 throw new RangeError('cutoff must be 1 or 3');
}
function initSixthBatch(doc) {
 const write=(group,selector,value)=>{const el=group.querySelector(selector);if(el)el.textContent=String(value);};
 doc.querySelectorAll('[data-demo="final-lightgcn"]').forEach(group=>{
  const slider=group.querySelector('[data-f26-x]');
  const update=()=>{const x=Number(slider.value),v=lightGCN26(x);
   write(group,'[data-f26-x-label]',x.toFixed(2));
   write(group,'[data-f26-norm]',v.symmetric.toFixed(4));
   write(group,'[data-f26-mean]',v.naive.toFixed(4));};
  slider.addEventListener('input',update);update();
 });
 doc.querySelectorAll('[data-demo="final-bpr"]').forEach(group=>{
  const slider=group.querySelector('[data-f26-delta]');
  const update=()=>{const x=Number(slider.value),v=bpr26(x);
   write(group,'[data-f26-delta-label]',x.toFixed(1));
   write(group,'[data-f26-sigmoid]',v.sigmoid.toFixed(4));
   write(group,'[data-f26-loss]',v.loss.toFixed(6));};
  slider.addEventListener('input',update);update();
 });
 doc.querySelectorAll('[data-demo="final-brain"]').forEach(group=>{
  const slider=group.querySelector('[data-f27-tau]');
  const update=()=>{const x=Number(slider.value),v=brain27(x);
   write(group,'[data-f27-tau-label]',x.toFixed(1));
   write(group,'[data-f27-edges]',v.edges+' / 3');
   write(group,'[data-f27-components]',v.components);};
  slider.addEventListener('input',update);update();
 });
 doc.querySelectorAll('[data-demo="final-fairness"]').forEach(group=>{
  const slider=group.querySelector('[data-f27-b]');
  const update=()=>{const count=Number(slider.value),v=fairness27(count);
   write(group,'[data-f27-b-label]',count);
   write(group,'[data-f27-a-rate]',(100*v.a)+'%');
   write(group,'[data-f27-b-rate]',(100*v.b)+'%');
   write(group,'[data-f27-gap]',(100*v.gap)+' pp');};
  slider.addEventListener('input',update);update();
 });
 doc.querySelectorAll('[data-demo="final-capstone"]').forEach(group=>{
  const buttons=[...group.querySelectorAll('[data-f28-cutoff]')];
  const update=button=>{const cutoff=Number(button.dataset.f28Cutoff),v=capstone28(cutoff);
   buttons.forEach(x=>x.setAttribute('aria-pressed',String(x===button)));
   write(group,'[data-f28-edges]',v.edges);
   write(group,'[data-f28-score]',v.score);
   write(group,'[data-f28-leak]',v.futureIncluded?'是':'否');
   write(group,'[data-f28-note]',cutoff===1?'仅 AB、AC 两条训练边；D 和 E 暂时孤立。':'截至 t=3 有五条训练边；未来 BD@5 不在训练邻接。');};
  buttons.forEach(x=>x.addEventListener('click',()=>update(x)));
  update(group.querySelector('[data-f28-cutoff="3"]'));
 });
}
return {erExpected,wsRegime,metricText,baProbability,degreeFrequency,pagerankDistribution,toyModularity,kCoreNodes,sirRisk,sirPathState,cascadeHistory,donationPayoffs,voterCopy,robustnessAfterRemoval,overloadAfterFailure,linkPredictionScores,collectionProjection,multiplexPath,temporalEarliest,node2vecToy,gcnToy,gatToy,bridgeToy,labelAlignmentToy,projectionEdges,sparseMemoryToy,starSampleToy,lightGCN26,bpr26,brain27,fairness27,capstone28,init(doc){init(doc);initAdvanced(doc);initThirdBatch(doc);initFourthBatch(doc);initFifthBatch(doc);initSixthBatch(doc);}};});