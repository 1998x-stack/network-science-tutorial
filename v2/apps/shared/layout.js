(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  root.NetsciLayout = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';
  // Stable golden-angle placement followed by deterministic, bounded spring relaxation.
  // This is view geometry, not a graph-science metric.
  function createLayout(nodes, edges, options={}) {
    const n = nodes.length, points = nodes.map((node,i)=> {
      const a = 2*Math.PI*((i*0.618033988749895)%1), r=Math.sqrt((i+0.5)/Math.max(1,n))*190;
      return {id:node.id, degree:node.degree||0, x:r*Math.cos(a), y:r*Math.sin(a),vx:0,vy:0};
    });
    const byId = new Map(points.map(p=>[p.id,p]));
    const neighbors = new Map(points.map(p=>[p.id,new Set()]));
    const pairs = edges.map(e=>{
      const a=byId.get(e.source),b=byId.get(e.target);
      neighbors.get(a.id).add(b.id);neighbors.get(b.id).add(a.id);
      return [a,b];
    });
    const passes = n > 400 ? 0 : Math.min(n < 180 ? 110 : 55, options.passes ?? 110);
    for (let t=0;t<passes;t++) {
      for (let i=0;i<n;i++)for(let j=i+1;j<n;j++){
        const a=points[i], b=points[j],dx=b.x-a.x,dy=b.y-a.y,dist2=dx*dx+dy*dy+30, f=95/dist2;
        a.vx-=dx*f;a.vy-=dy*f;b.vx+=dx*f;b.vy+=dy*f;
      }
      for(const [a,b] of pairs){const dx=b.x-a.x,dy=b.y-a.y;a.vx+=dx*.015;a.vy+=dy*.015;b.vx-=dx*.015;b.vy-=dy*.015;}
      for(const p of points){p.vx=(p.vx-p.x*.002)*.76;p.vy=(p.vy-p.y*.002)*.76;p.x+=Math.max(-6,Math.min(6,p.vx));p.y+=Math.max(-6,Math.min(6,p.vy));}
    }
    const extent = Math.max(1,...points.map(p=>Math.max(Math.abs(p.x),Math.abs(p.y))));
    for(const p of points){p.x/=extent;p.y/=extent;delete p.vx;delete p.vy;}
    return {points,neighbors};
  }
  return {createLayout};
});
