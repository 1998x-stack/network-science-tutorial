(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;root.NetsciComparison=api;})(typeof globalThis!=='undefined'?globalThis:this,function(){
 'use strict';
 const LABELS={er:'ER 随机网络',ws:'WS 小世界',ba:'BA 优先连接'};
 const METRICS=[['mean_degree','平均度'],['mean_local_clustering','平均聚集系数'],['global_transitivity','全局传递性'],['average_shortest_path_lcc','最大分量平均路径'],['largest_component_fraction','最大分量占比']];
 function summarize(report,key){
   if(!report||report.schema_version!=='1.0.0'||!Array.isArray(report.runs))throw Error('比较数据协议错误');
   if(!METRICS.some(k=>k[0]===key))throw Error('未知指标');
   return ['er','ws','ba'].map(model=>{
     const values=report.runs.filter(x=>x.model===model).map(x=>x.metrics?.[key]).filter(x=>typeof x==='number'&&Number.isFinite(x));
     if(!values.length) return {model,label:LABELS[model],mean:null,sd:null,n:0};
     const mean=values.reduce((a,b)=>a+b,0)/values.length;
     const sd=values.length===1?null:Math.sqrt(values.reduce((acc,x)=>acc+(x-mean)**2,0)/(values.length-1));
     return {model,label:LABELS[model],mean,sd,n:values.length};
   });
 }
 return {LABELS,METRICS,summarize};
});
