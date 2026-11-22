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

return {erExpected,wsRegime,metricText,baProbability,degreeFrequency,pagerankDistribution,toyModularity,kCoreNodes,sirRisk,sirPathState,cascadeHistory,donationPayoffs,voterCopy,robustnessAfterRemoval,overloadAfterFailure,init(doc){init(doc);initAdvanced(doc);initThirdBatch(doc);}};});