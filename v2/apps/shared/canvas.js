(function(root,factory){const api=factory(root.NetsciLayout,root);if(typeof module==='object'&&module.exports)module.exports=(layout)=>factory(layout,globalThis);root.NetsciCanvas=api;})(typeof globalThis!=='undefined'?globalThis:this,function(Layout,root){
 'use strict';
 class GraphView {
   constructor(canvas,{onSelect=()=>{},onHover=()=>{}}={}){
     if(!Layout) throw Error('Load layout.js first');
     this.canvas=canvas;this.ctx=canvas.getContext('2d');this.onSelect=onSelect;this.onHover=onHover;
     this.artifact=null;this.points=[];this.byId=new Map();this.neighbors=new Map();this.selected=null;this.hovered=null;
     this.zoom=1;this.nodeScale=1;this.edgeAlpha=.23;this.centerX=0;this.centerY=0;
     canvas.tabIndex=0;canvas.setAttribute('role','img');canvas.setAttribute('aria-label','交互式网络结构画布，方向键移动视图，加减键缩放，Escape 清除选择');
     canvas.addEventListener('pointermove',event=>{const p=this.hit(event); if(p?.id!==this.hovered){this.hovered=p?.id??null;this.onHover(p);this.draw();}});
     canvas.addEventListener('pointerleave',()=>{this.hovered=null;this.onHover(null);this.draw()});
     canvas.addEventListener('click',event=>{const p=this.hit(event);this.select(p?.id??null)});
     canvas.addEventListener('wheel',event=>{event.preventDefault();this.adjustZoom(event.deltaY>0?.9:1.1);},{passive:false});
     canvas.addEventListener('keydown',event=>{
       const keys={ArrowLeft:[-20,0],ArrowRight:[20,0],ArrowUp:[0,-20],ArrowDown:[0,20]};
       if(keys[event.key]){event.preventDefault();this.centerX+=keys[event.key][0];this.centerY+=keys[event.key][1];this.draw();}
       else if(['+','='].includes(event.key)){event.preventDefault();this.adjustZoom(1.2);}
       else if(event.key==='-'){event.preventDefault();this.adjustZoom(.8333);}
       else if(event.key==='Escape'){this.select(null);}
     });
     if(typeof ResizeObserver!=='undefined'){this.resizeObserver=new ResizeObserver(()=>this.draw());this.resizeObserver.observe(canvas.parentElement);}
     else root.addEventListener('resize',()=>this.draw());
   }
   setArtifact(data){this.artifact=data;const l=Layout.createLayout(data.graph.nodes,data.graph.edges);this.points=l.points;this.neighbors=l.neighbors;this.byId=new Map(this.points.map(p=>[p.id,p]));this.selected=null;this.hovered=null;this.zoom=1;this.centerX=this.centerY=0;this.onSelect(null,[]);this.draw();}
   destroy(){this.resizeObserver?.disconnect();}
   radius(p){return Math.min(15,(3.4+Math.sqrt(Math.max(0,p.degree||0))*.8)*this.nodeScale);}
   coords(p){const w=this.canvas.clientWidth,h=this.canvas.clientHeight,u=.45*Math.min(w,h)*this.zoom;return [w/2+this.centerX+p.x*u,h/2+this.centerY+p.y*u];}
   hit(event){if(!this.artifact)return null;const r=this.canvas.getBoundingClientRect(),x=event.clientX-r.left,y=event.clientY-r.top;let result=null,distance=Infinity;for(const p of this.points){const [px,py]=this.coords(p),d=(x-px)**2+(y-py)**2;if(d<(this.radius(p)+5)**2&&d<distance){result=p;distance=d;}}return result;}
   select(id){this.selected=id;this.onSelect(id===null?null:this.byId.get(id),id===null?[]:[...(this.neighbors.get(id)||[])].sort());this.draw();}
   adjustZoom(factor){this.zoom=Math.max(.4,Math.min(5,this.zoom*factor));this.draw();}
   reset(){this.selected=null;this.zoom=1;this.centerX=this.centerY=0;this.onSelect(null,[]);this.draw();}
   draw(){const canvas=this.canvas,ctx=this.ctx;if(!ctx)return;
     const w=Math.max(canvas.clientWidth,1),h=Math.max(canvas.clientHeight,1),dpr=Math.min(root.devicePixelRatio||1,2);
     if(canvas.width!==Math.round(w*dpr)||canvas.height!==Math.round(h*dpr)){canvas.width=Math.round(w*dpr);canvas.height=Math.round(h*dpr);}
     ctx.setTransform(dpr,0,0,dpr,0,0);ctx.clearRect(0,0,w,h);
     if(!this.artifact)return;
     ctx.beginPath();ctx.lineWidth=.65;ctx.strokeStyle=`rgba(129,156,201,${this.edgeAlpha})`;
     for(const edge of this.artifact.graph.edges){const a=this.byId.get(edge.source),b=this.byId.get(edge.target);if(!a||!b)continue;const [x,y]=this.coords(a),[xx,yy]=this.coords(b);ctx.moveTo(x,y);ctx.lineTo(xx,yy);}
     ctx.stroke();
     for(const p of this.points){const [x,y]=this.coords(p),isSelected=this.selected===p.id,adjacent=this.selected!==null&&this.neighbors.get(this.selected)?.has(p.id),isHovered=this.hovered===p.id;
       ctx.globalAlpha=this.selected!==null&&!isSelected&&!adjacent?.28:1;
       ctx.beginPath();ctx.arc(x,y,this.radius(p)+(isSelected?1.5:0),0,2*Math.PI);
       ctx.fillStyle=isSelected?'#f7b96e':adjacent?'#8de1cf':`hsl(${Math.max(160,215-Math.min(45,p.degree*2))} 68% ${isHovered?76:64}%)`;
       ctx.fill();if(isSelected||isHovered){ctx.lineWidth=2;ctx.strokeStyle='#fff';ctx.stroke();}ctx.globalAlpha=1;
     }
   }
 }
 return {GraphView};
});
