// Legacy standalone Graph Lab: thin compatibility adapter over shared S02 graph components.
// This page can still open through file:// without a build step.
(function(){
'use strict';
const $=id=>document.getElementById(id),C=window.NetsciContract,V=window.NetsciCanvas;
const descriptions={er:['ER · 随机网络','每一对节点独立随机连接。'],ws:['WS · 小世界网络','从规则环出发，通过重连形成少量全局捷径。'],ba:['BA · 优先连接网络','新节点倾向于连接已有高度节点。']};
const view=new V.GraphView($('graph'),{onSelect:(node,neighbors)=>{$('selection').textContent=node?`节点 ${node.id} · 度 ${node.degree} · 邻居：${neighbors.slice(0,24).join(', ')}${neighbors.length>24?'…':''}`:'点击节点可查看邻居关系。';},onHover:node=>{const t=$('tip');t.hidden=!node;if(node)t.textContent=`节点 ${node.id} · 度 ${node.degree}`;}});
let artifact;
function setData(input){try{
  const valid=C.validate(input);view.setArtifact(valid);artifact=valid;
  $('chart-title').textContent=descriptions[valid.experiment.model]?.[0]||'导入网络';
  $('model-description').textContent=descriptions[valid.experiment.model]?.[1]||'外部导入的结构数据';
  for(const btn of document.querySelectorAll('[data-model]'))btn.setAttribute('aria-pressed',String(btn.dataset.model===valid.experiment.model));
  $('metrics').replaceChildren();for(const [key,label] of C.METRICS){const box=document.createElement('div'),name=document.createElement('span'),value=document.createElement('strong');box.className='metric';name.textContent=label;value.textContent=C.format(valid.metrics[key]);box.append(name,value);$('metrics').append(box);}
  $('metadata').replaceChildren();for(const [key,value] of Object.entries({模型:valid.experiment.model,种子:valid.experiment.seed,参数:JSON.stringify(valid.experiment.params),数据协议:valid.schema_version})){const row=document.createElement('div'),dt=document.createElement('dt'),dd=document.createElement('dd');dt.textContent=key;dd.textContent=String(value);row.append(dt,dd);$('metadata').append(row);}
  return true;
}catch(e){alert('无法导入实验：'+e.message);return false;}}
for(const btn of document.querySelectorAll('[data-model]'))btn.addEventListener('click',()=>setData(window.NETSCI_SAMPLES[btn.dataset.model]));
$('zoom-in').addEventListener('click',()=>view.adjustZoom(1.25));$('zoom-out').addEventListener('click',()=>view.adjustZoom(.8));$('reset').addEventListener('click',()=>view.reset());
$('size').addEventListener('input',e=>{view.nodeScale=Number(e.target.value)/10;$('size-value').textContent=view.nodeScale.toFixed(1)+'x';view.draw();});
$('edges').addEventListener('input',e=>{view.edgeAlpha=Number(e.target.value)/100;$('edge-value').textContent=e.target.value+'%';view.draw();});
$('upload').addEventListener('change',async e=>{const f=e.target.files?.[0];if(!f)return;try{if(f.size>5000000)throw Error('文件不能超过 5MB');setData(JSON.parse(await f.text()));}catch(error){alert(error.message)}});
$('export').addEventListener('click',()=>{if(!artifact)return;const blob=new Blob([JSON.stringify(artifact,null,2)],{type:'application/json'}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=`${artifact.experiment.model}-experiment.json`;a.click();setTimeout(()=>URL.revokeObjectURL(url),500);});
setData(window.NETSCI_SAMPLES.er);
})();
