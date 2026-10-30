(function(){
'use strict';
const $=id=>document.getElementById(id),Compare=globalThis.NetsciComparison,report=globalThis.NETSCI_COMPARISON;
const format=n=>n==null?'N/A':n.toFixed(4).replace(/0+$/,'').replace(/\.$/,'');
function draw(key){let rows;try{rows=Compare.summarize(report,key)}catch(e){$('plot-error').textContent=e.message;return;}
 const label=Compare.METRICS.find(x=>x[0]===key)[1], max=Math.max(0.00001,...rows.map(r=>(r.mean||0)+(r.sd||0)))*1.15;
 const svg=$('plot');svg.replaceChildren();const NS='http://www.w3.org/2000/svg';function element(tag,attrs,text){const el=document.createElementNS(NS,tag);for(const [k,v] of Object.entries(attrs))el.setAttribute(k,v);if(text!=null)el.textContent=text;svg.appendChild(el);return el;}
 element('title',{},`${label}：三个模型五种子均值与样本标准差`);
 for(let i=0;i<=4;i++){const x=240+i*155;element('line',{x1:x,y1:20,x2:x,y2:235,stroke:'#344960','stroke-dasharray':'3 6'});element('text',{x,y:258,'text-anchor':'middle',fill:'#a8bfd7','font-size':'12'},format(max*i/4));}
 rows.forEach((r,i)=>{const y=36+i*72,width=r.mean===null?0:r.mean/max*620;element('text',{x:8,y:y+24,fill:'#e7f1ff','font-size':'14'},r.label);element('rect',{x:240,y,width,height:30,rx:6,fill:['#70dbc3','#85b5ff','#f4bc7c'][i]});if(r.sd!==null){const x=240+r.mean/max*620,offset=r.sd/max*620;element('line',{x1:Math.max(240,x-offset),y1:y+15,x2:Math.min(860,x+offset),y2:y+15,stroke:'#fff','stroke-width':'2'});element('line',{x1:x,y1:y+8,x2:x,y2:y+22,stroke:'#fff','stroke-width':'2'});}
 element('text',{x:Math.min(865,248+width),y:y+20,fill:'#ffffff','font-size':'12'},format(r.mean));});
 const tbody=$('comparison-table');tbody.replaceChildren();for(const r of rows){const tr=document.createElement('tr');for(const value of [r.label,format(r.mean),format(r.sd),String(r.n)]){const td=document.createElement('td');td.textContent=value;tr.appendChild(td);}tbody.appendChild(tr);}
 $('metric-explainer').textContent=`${label} · 数据来自 Python 生成的 ${report.runs.length} 次实验运行；误差线为样本标准差，不代表置信区间。`;
}
$('metric-selector').addEventListener('change',e=>draw(e.target.value));draw($('metric-selector').value);
})();
