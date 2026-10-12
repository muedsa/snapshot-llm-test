const fs = require('fs');
const path = require('path');
const src = process.argv[2];
const target = process.argv[3];
if (!src || !target) throw new Error('Usage: check-geometry-v001.cjs AUDIT_JSON OUTPUT_JSON');
const audit = JSON.parse(fs.readFileSync(src, 'utf8'));
const graph = JSON.parse(fs.readFileSync('tasks/A06-dependency-graph/inputs/graph.json', 'utf8'));
const nodes = Object.fromEntries(audit.nodes.map(n => [n.id, n]));
const eps=1e-6;
function onBoundary(p,b) {
  const [x,y]=p; return x>=b.x-eps&&x<=b.x+b.width+eps&&y>=b.y-eps&&y<=b.y+b.height+eps&&
    (Math.abs(x-b.x)<eps||Math.abs(x-b.x-b.width)<eps||Math.abs(y-b.y)<eps||Math.abs(y-b.y-b.height)<eps);
}
function segmentHitsInterior(a,z,b) {
  // Liang-Barsky segment/rectangle clipping, with epsilon inset to exclude boundary-only touches.
  const low=[b.x+eps,b.y+eps], high=[b.x+b.width-eps,b.y+b.height-eps];
  let lo=0, hi=1;
  for(let k=0;k<2;k++) {
    const delta=z[k]-a[k];
    if(Math.abs(delta)<eps) { if(a[k]<low[k]||a[k]>high[k]) return false; }
    else {
      let t0=(low[k]-a[k])/delta,t1=(high[k]-a[k])/delta;
      if(t0>t1)[t0,t1]=[t1,t0]; lo=Math.max(lo,t0);hi=Math.min(hi,t1);
      if(lo>hi) return false;
    }
  }
  return hi>=lo;
}
const routeChecks=[];
for(const [kind, routes, input] of [['solid',audit.solid_edges,graph.solid_edges],['feedback',audit.feedback_edges,graph.feedback_edges]]) {
  for(const route of routes) {
    const from=nodes[route.from], to=nodes[route.to], points=route.points;
    const crosses=[];
    for(let i=1;i<points.length;i++) for(const n of audit.nodes) {
      if(n.id===from.id||n.id===to.id) continue;
      if(segmentHitsInterior(points[i-1],points[i],n.bounds)) crosses.push({segment:i-1,node:n.id});
    }
    const fromOn=onBoundary(points[0],from.bounds),toOn=onBoundary(points.at(-1),to.bounds);
    const inputExists=input.some(([f,t])=>f===route.from&&t===route.to);
    routeChecks.push({id:route.id,kind,from:route.from,to:route.to,input_edge_exists:inputExists,
      source_on_boundary:fromOn,target_on_boundary:toOn,
      direction:kind==='solid'?to.layer>from.layer:to.layer<from.layer,
      solid_route_y_monotonic:kind==='solid'?points.every((p,j)=>!j||p[1]>=points[j-1][1]):null,
      node_interior_intersections:crosses,
      arrow_anchor:points.at(-1),
      passes:inputExists&&fromOn&&toOn&&!crosses.length&&(kind==='solid'?to.layer>from.layer:to.layer<from.layer)});
  }
}
const missing=[];
for(const [kind, routes, input] of [['solid',audit.solid_edges,graph.solid_edges],['feedback',audit.feedback_edges,graph.feedback_edges]]) {
  for(const [from,to] of input) if(!routes.some(e=>e.from===from&&e.to===to)) missing.push({kind,from,to});
}
const overlaps=[];
for(let i=0;i<audit.nodes.length;i++)for(let j=i+1;j<audit.nodes.length;j++) {
  const a=audit.nodes[i],b=audit.nodes[j],A=a.bounds,B=b.bounds;
  if(A.x<B.x+B.width&&B.x<A.x+A.width&&A.y<B.y+B.height&&B.y<A.y+A.height) overlaps.push([a.id,b.id]);
}
const result={generated_at:new Date().toISOString(),task_id:'A06',run_id:'20261002-204314-6f31',
  scope:'Independent route and node geometry from saved JSON; does not replace actual image inspection',
  source_audit:path.resolve(src),node_count:audit.nodes.length,solid_route_count:audit.solid_edges.length,
  feedback_route_count:audit.feedback_edges.length,missing_input_edges:missing,node_overlaps:overlaps,
  all_geometry_passes:routeChecks.every(r=>r.passes)&&!missing.length&&!overlaps.length,
  route_checks:routeChecks,
  feedback_targets_exact: audit.feedback_edges.every(e=>e.to==='N08')&&audit.feedback_edges.some(e=>e.from==='N09')&&audit.feedback_edges.some(e=>e.from==='N10'),
  annotations_note:'Text intersections are checked separately: v001 long N04→N13 crosses layer number boxes 02 and 09. Producer confirmed this in actual image; v002 moves boxes to x412..442.'};
fs.writeFileSync(target,JSON.stringify(result,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({all_geometry_passes:result.all_geometry_passes,counts:[result.node_count,result.solid_route_count,result.feedback_route_count],node_overlaps:overlaps,missing,route_failures:routeChecks.filter(r=>!r.passes)},null,2));
