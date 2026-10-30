(() => {
  'use strict';
  const $ = id => document.getElementById(id);
  const labels = {
    er: ['ER · 随机网络', '每一对节点独立随机连接。比较连通性、平均度和聚集系数。'],
    ws: ['WS · 小世界网络', '从规则环网络出发，少量随机重连可以大幅缩短路径。'],
    ba: ['BA · 优先连接网络', '网络持续增长，新节点偏向连接已有高节点度的节点。']
  };
  const display = [
    ['nodes', '节点数'], ['edges', '边数'], ['mean_degree', '平均度'],
    ['mean_local_clustering', '平均聚集系数'], ['global_transitivity', '全局传递性'],
    ['largest_component_fraction', '最大分量占比'], ['average_shortest_path_lcc', '最大分量平均路径'], ['density', '网络密度']
  ];
  const canvas = $('graph'), ctx = canvas.getContext('2d');
  const wrapper = $('canvas-wrap');
  let artifact, points = [], neighborSets = new Map(), selected = null, hovered = null;
  let zoom = 1, nodeScale = 1, edgeAlpha = .30;
  const number = n => n == null ? 'N/A' : typeof n === 'number' && !Number.isInteger(n) ? n.toFixed(3) : String(n);

  function validate(data) {
    if (!data || data.schema_version !== '1.0.0' || !data.experiment || !data.graph || !data.metrics) throw Error('需要 schema_version=1.0.0 的网络实验 JSON');
    const ns = data.graph.nodes, es = data.graph.edges;
    if (!Array.isArray(ns) || !Array.isArray(es) || ns.length > 3000 || es.length > 60000) throw Error('图数据无效或超过此浏览器实验查看器的规模限制');
    const ids = new Set(ns.map(n => n.id));
    if (ids.size !== ns.length || ns.some(n => typeof n.id !== 'string')) throw Error('节点 ID 必须唯一且为字符串');
    if (es.some(e => !ids.has(e.source) || !ids.has(e.target))) throw Error('边引用了不存在的节点');
    return data;
  }

  // Deterministic layout owned by the renderer; NO metric calculations here.
  function layout(data) {
    const ns = data.graph.nodes;
    const es = data.graph.edges;
    const n = ns.length;
    const byId = new Map();
    points = ns.map((node, i) => {
      const a = 2 * Math.PI * ((i * 0.61803398875) % 1);
      const r = Math.sqrt((i + .5) / Math.max(1,n)) * 190;
      const p = {id: node.id, degree: node.degree, x: Math.cos(a)*r, y: Math.sin(a)*r, vx: 0, vy: 0};
      byId.set(p.id, p); return p;
    });
    neighborSets = new Map(ns.map(x => [x.id, new Set()]));
    const pairs = [];
    for (const edge of es) {
      const a = byId.get(edge.source), b = byId.get(edge.target);
      pairs.push([a,b]); neighborSets.get(a.id).add(b.id); neighborSets.get(b.id).add(a.id);
    }
    // Approximate force placement with bounded work to keep large uploads responsive.
    if (n <= 400) {
      const count = n < 180 ? 130 : 65;
      const repulsion = 95;
      for (let t = 0; t < count; t++) {
        for (let i=0;i<n;i++) for (let j=i+1;j<n;j++) {
          const a=points[i],b=points[j],dx=b.x-a.x,dy=b.y-a.y,dist2=dx*dx+dy*dy+30;
          const f=repulsion/dist2, fx=dx*f,fy=dy*f;
          a.vx-=fx;a.vy-=fy;b.vx+=fx;b.vy+=fy;
        }
        for (const [a,b] of pairs) {
          const dx=b.x-a.x,dy=b.y-a.y;
          a.vx+=dx*.015;a.vy+=dy*.015;b.vx-=dx*.015;b.vy-=dy*.015;
        }
        for (const a of points) {
          a.vx=(a.vx-a.x*.002)*.76;a.vy=(a.vy-a.y*.002)*.76;
          a.x+=Math.max(-6,Math.min(6,a.vx));a.y+=Math.max(-6,Math.min(6,a.vy));
        }
      }
    }
    const extent = Math.max(1, ...points.map(p => Math.max(Math.abs(p.x),Math.abs(p.y))));
    points.forEach(p => {p.x/=extent;p.y/=extent;});
  }

  function coords(p) {
    const w=canvas.clientWidth,h=canvas.clientHeight,unit=.46*Math.min(w,h)*zoom;
    return [w/2+p.x*unit,h/2+p.y*unit];
  }
  function radius(p) { return Math.min(15, (3.4 + Math.sqrt(Math.max(0,p.degree||0))*.8)*nodeScale); }
  function render() {
    const dpr=window.devicePixelRatio||1;
    const w=wrapper.clientWidth,h=wrapper.clientHeight;
    if (canvas.width!==Math.round(w*dpr)||canvas.height!==Math.round(h*dpr)) {canvas.width=Math.round(w*dpr);canvas.height=Math.round(h*dpr)}
    ctx.setTransform(dpr,0,0,dpr,0,0);ctx.clearRect(0,0,w,h);
    if (!artifact) return;
    const byId = new Map(points.map(p => [p.id,p]));
    ctx.lineWidth=.7;ctx.strokeStyle=`rgba(146,182,224,${edgeAlpha})`;
    ctx.beginPath();for (const e of artifact.graph.edges) {
      const a=byId.get(e.source),b=byId.get(e.target),[x,y]=coords(a),[xx,yy]=coords(b);
      ctx.moveTo(x,y);ctx.lineTo(xx,yy);
    }ctx.stroke();
    for (const p of points) {
      const [x,y]=coords(p),chosen=p.id===selected,adjacent=selected!==null && neighborSets.get(selected)?.has(p.id),isHovered=p.id===hovered;
      const hue=Math.max(145,205-Math.min(55,(p.degree||0)*2.2));
      ctx.beginPath();ctx.arc(x,y,radius(p)+(chosen?2:0),0,2*Math.PI);
      ctx.fillStyle=chosen?'#ffd18e':adjacent?'#9ffde0':`hsl(${hue} 75% ${isHovered?74:60}%)`;
      ctx.globalAlpha=selected!==null && !chosen && !adjacent ? .32 : 1;ctx.fill();ctx.globalAlpha=1;
      if(chosen||isHovered){ctx.lineWidth=2;ctx.strokeStyle='#fff';ctx.stroke()}
    }
  }
  function setData(input) {
    try {artifact=validate(input);selected=hovered=null;zoom=1;layout(artifact);renderMetrics();render();$('selection').textContent='点击一个节点查看相邻节点。';}
    catch(error){alert('无法导入实验结果：'+error.message)}
  }
  function renderMetrics() {
    $('metrics').replaceChildren();
    for(const [key,title] of display){const box=document.createElement('div');box.className='metric';const label=document.createElement('span');label.textContent=title;const val=document.createElement('strong');val.textContent=number(artifact.metrics[key]);box.append(label,val);$('metrics').append(box)}
    $('metadata').replaceChildren();
    const meta={模型:artifact.experiment.model,种子:artifact.experiment.seed,参数:JSON.stringify(artifact.experiment.params),数据协议:artifact.schema_version};
    for(const [key,val] of Object.entries(meta)){const row=document.createElement('div'),dt=document.createElement('dt'),dd=document.createElement('dd');dt.textContent=key;dd.textContent=String(val);row.append(dt,dd);$('metadata').append(row)}
    const model=artifact.experiment.model;
    $('chart-title').textContent=labels[model]?.[0]||'导入网络';
    $('model-description').textContent=labels[model]?.[1]||'外部导入的结构数据';
    for(const tab of document.querySelectorAll('[data-model]'))tab.setAttribute('aria-pressed',String(tab.dataset.model===model));
  }
  function hit(event) {
    const bounds=canvas.getBoundingClientRect(),x=event.clientX-bounds.left,y=event.clientY-bounds.top;
    let found=null,best=Infinity;
    for(const p of points){const [px,py]=coords(p),d=(px-x)**2+(py-y)**2;if(d<best && d<(radius(p)+5)**2){best=d;found=p}}
    return found;
  }
  canvas.addEventListener('pointermove',event=>{const h=hit(event);hovered=h?.id??null;const tip=$('tip');tip.hidden=!h;if(h){const r=wrapper.getBoundingClientRect();tip.style.left=Math.min(event.clientX-r.left+14,r.width-125)+'px';tip.style.top=Math.max(10,event.clientY-r.top-30)+'px';tip.textContent=`节点 ${h.id} · 度 ${h.degree}`;}render()});
  canvas.addEventListener('pointerleave',()=>{hovered=null;$('tip').hidden=true;render()});
  canvas.addEventListener('click',event=>{const h=hit(event);selected=h?.id??null;const adj=selected===null?[]:[...neighborSets.get(selected)].sort((a,b)=>Number(a)-Number(b));$('selection').textContent=h?`节点 ${h.id} · 度 ${h.degree} · 邻居：${adj.slice(0,24).join(', ')}${adj.length>24?'…':''}`:'点击网络中的节点，查看度数及相邻节点。';render()});
  canvas.addEventListener('wheel',event=>{event.preventDefault();zoom=Math.max(.45,Math.min(4,zoom*(event.deltaY>0?.9:1.1)));render()},{passive:false});
  $('zoom-in').addEventListener('click',()=>{zoom=Math.min(4,zoom*1.25);render()});
  $('zoom-out').addEventListener('click',()=>{zoom=Math.max(.45,zoom/1.25);render()});
  $('reset').addEventListener('click',()=>{zoom=1;selected=null;render()});
  $('size').addEventListener('input',e=>{nodeScale=Number(e.target.value)/10;$('size-value').textContent=nodeScale.toFixed(1)+'x';render()});
  $('edges').addEventListener('input',e=>{edgeAlpha=Number(e.target.value)/100;$('edge-value').textContent=e.target.value+'%';render()});
  $('upload').addEventListener('change',async e=>{const file=e.target.files?.[0];if(!file)return;try{setData(JSON.parse(await file.text()))}catch(ex){alert('JSON 解析失败：'+ex.message)}});
  $('export').addEventListener('click',()=>{if(!artifact)return;const blob=new Blob([JSON.stringify(artifact,null,2)],{type:'application/json'}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=`${artifact.experiment.model}-experiment.json`;a.click();URL.revokeObjectURL(url)});
  for(const tab of document.querySelectorAll('[data-model]')) tab.addEventListener('click',()=>setData(window.NETSCI_SAMPLES[tab.dataset.model]));
  window.addEventListener('resize',render);
  if(window.NETSCI_SAMPLES?.er) setData(window.NETSCI_SAMPLES.er);
})();
