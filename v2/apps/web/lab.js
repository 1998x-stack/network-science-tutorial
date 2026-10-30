(function(){
'use strict';
const C=globalThis.NetsciContract,V=globalThis.NetsciCanvas, data=globalThis.NETSCI_SAMPLES;
const $=id=>document.getElementById(id), view=new V.GraphView($('graph'),{
 onSelect:(node,neighbors)=>{$('selection').textContent=node?`节点 ${node.id} · 度 ${node.degree} · 邻居（${neighbors.length}）：${neighbors.slice(0,32).join('、')}${neighbors.length>32?'…':''}`:'选择画布节点，可查看其邻居。';},
 onHover:node=>{const tip=$('tip');tip.hidden=!node;if(node)tip.textContent=`节点 ${node.id} · 度 ${node.degree}`;}
});
let artifact;
const labels={er:'ER · 随机网络',ws:'WS · 小世界网络',ba:'BA · 优先连接网络'};
function setError(msg){$('error').textContent=msg||'';}
function show(input){try{
 const valid=C.validate(input);view.setArtifact(valid);artifact=valid;setError('');
 $('experiment-title').textContent=labels[valid.experiment.model]||'已导入网络';$('model').value=labels[valid.experiment.model]?valid.experiment.model:'custom';
 const metrics=$('metrics');metrics.replaceChildren();for(const [key,label] of C.METRICS){const card=document.createElement('div'),name=document.createElement('span'),value=document.createElement('strong');card.className='metric';name.textContent=label;value.textContent=C.format(valid.metrics[key]);card.append(name,value);metrics.appendChild(card);}
 const meta=$('metadata');meta.replaceChildren();for(const [key,value] of Object.entries({模型:valid.experiment.model,种子:valid.experiment.seed,参数:JSON.stringify(valid.experiment.params),协议:valid.schema_version})){
   const dt=document.createElement('dt'),dd=document.createElement('dd');dt.textContent=key;dd.textContent=value==null?'N/A':String(value);meta.append(dt,dd);}
 return true;
}catch(e){setError(e.message);return false;}}
$('model').addEventListener('change',e=>{const m=e.target.value;if(data[m])show(data[m]);});
$('zoom-in').addEventListener('click',()=>view.adjustZoom(1.25));
$('zoom-out').addEventListener('click',()=>view.adjustZoom(.8));
$('reset').addEventListener('click',()=>view.reset());
$('size').addEventListener('input',e=>{view.nodeScale=Number(e.target.value)/10;$('size-value').textContent=view.nodeScale.toFixed(1)+'×';view.draw()});
$('edges').addEventListener('input',e=>{view.edgeAlpha=Number(e.target.value)/100;$('edge-value').textContent=e.target.value+'%';view.draw()});
$('upload').addEventListener('change',async e=>{const file=e.target.files?.[0];if(!file)return;if(file.size>5_000_000){setError('文件不能超过 5MB');return;}try{show(JSON.parse(await file.text()));}catch(err){setError('JSON 解析失败：'+err.message);}});
$('export').addEventListener('click',()=>{if(!artifact)return;const b=new Blob([JSON.stringify(artifact,null,2)],{type:'application/json'}),u=URL.createObjectURL(b),a=document.createElement('a');a.href=u;a.download=`${artifact.experiment.model||'network'}-run.json`;a.click();setTimeout(()=>URL.revokeObjectURL(u),500);});
show(data.er);
})();
