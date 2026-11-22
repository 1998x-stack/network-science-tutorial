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

return {erExpected,wsRegime,metricText,baProbability,degreeFrequency,pagerankDistribution,toyModularity,init(doc){init(doc);initAdvanced(doc);}};});