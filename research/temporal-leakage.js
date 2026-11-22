/* Research-level cross-chapter demonstration: no third-party libraries and no network requests. */
(function(root,factory){
 'use strict';
 const api=factory();
 if(typeof module==='object'&&module.exports)module.exports=api;
 if(root)root.TemporalLeakageResearch=api;
 if(typeof document!=='undefined'){
   const run=()=>api.init(document);
   if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',run,{once:true});else run();
 }
})(typeof globalThis!=='undefined'?globalThis:this,function(){
 'use strict';
 const states={
  2:{edges:4,cn:0,walk:0,gcn:0,observed:false,status:'仅训练期 t≤2：四条边，E 是孤立节点。'},
  3:{edges:5,cn:0,walk:0,gcn:0,observed:false,status:'合法累积历史 t≤3：DE 可见；未来 BD 仍然不可见。'},
  5:{edges:6,cn:1,walk:1/3,gcn:1/4,observed:true,status:'违规反例：未来 BD@5 已污染邻接。B–D 不再是合法未观察候选。'}
 };
 function snapshotToy(cutoff){
  if(!Object.prototype.hasOwnProperty.call(states,cutoff))throw new RangeError('cutoff must be 2, 3, or 5');
  return {...states[cutoff]};
 }
 function recommendationToy(useFuture){
  if(typeof useFuture!=='boolean')throw new TypeError('boolean future mode required');
  return {U1X:useFuture?.5:1/Math.sqrt(2),U2X:useFuture?.5:0,contaminated:useFuture};
 }
 const paths={
  ordered:{A:0,B:1,C:2,D:3},
  reordered:{A:0,B:3,C:null,D:null},
  simultaneous:{A:0,B:1,C:null,D:null}
 };
 function temporalPathToy(name){
  if(!Object.prototype.hasOwnProperty.call(paths,name))throw new RangeError('unknown contact order');
  return {...paths[name]};
 }
 function init(doc){
  const place=(sel,value)=>{const el=doc.querySelector(sel);if(el)el.textContent=String(value);};
  const pressed=(selector,current)=>doc.querySelectorAll(selector).forEach(node=>node.setAttribute('aria-pressed',String(node===current)));
  const updateCutoff=button=>{
   const r=snapshotToy(Number(button.dataset.temporalCutoff));
   pressed('[data-temporal-cutoff]',button);
   place('[data-ui-edge-count]',r.edges);
   place('[data-ui-cn-be]',r.cn);
   place('[data-ui-walk-bd]',r.walk.toFixed(3));
   place('[data-ui-gcn-bd]',r.gcn.toFixed(3));
   place('[data-ui-observed-bd]',r.observed?'是':'否');
   place('[data-ui-candidate-eligible]',r.observed?'不可候选（已是训练边）':'可以候选');
   place('[data-ui-warning]',r.status);
   const warning=doc.querySelector('[data-ui-warning]');
   if(warning)warning.classList.toggle('research-safe',!r.observed);
  };
  doc.querySelectorAll('[data-temporal-cutoff]').forEach(button=>button.addEventListener('click',()=>updateCutoff(button)));
  const initial=doc.querySelector('[data-temporal-cutoff="3"]');if(initial)updateCutoff(initial);
  const updateItem=button=>{
   const v=recommendationToy(button.dataset.uiItemFuture==='on');
   pressed('[data-ui-item-future]',button);
   place('[data-ui-item-u1x]',v.U1X.toFixed(4));
   place('[data-ui-item-u2x]',v.U2X.toFixed(4));
  };
  doc.querySelectorAll('[data-ui-item-future]').forEach(button=>button.addEventListener('click',()=>updateItem(button)));
  const initItem=doc.querySelector('[data-ui-item-future="off"]');if(initItem)updateItem(initItem);
  const updatePath=button=>{
   pressed('[data-ui-path-case]',button);
   const a=temporalPathToy(button.dataset.uiPathCase);
   place('[data-ui-earliest]',Object.entries(a).map(([key,val])=>key+':'+(val===null?'不可达':val)).join('，'));
  };
  doc.querySelectorAll('[data-ui-path-case]').forEach(button=>button.addEventListener('click',()=>updatePath(button)));
  const initPath=doc.querySelector('[data-ui-path-case="ordered"]');if(initPath)updatePath(initPath);
 }
 return {snapshotToy,recommendationToy,temporalPathToy,init};
});
