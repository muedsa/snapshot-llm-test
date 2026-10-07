const fs=require('fs'),path=require('path');
const [,,geometryFile,outputFile]=process.argv;
if(!geometryFile||!outputFile)throw new Error('Usage: checker geometry.json output.json');
const g=JSON.parse(fs.readFileSync(geometryFile,'utf8'));
const n=JSON.parse(fs.readFileSync('tasks/A07-transit-topology/inputs/network.json','utf8'));
const nodes=Object.fromEntries(g.nodes.map(s=>[s.id,s]));
const eq=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
const angle=(a,b)=>Math.atan2(b[1]-a[1],b[0]-a[0])*180/Math.PI;
const normalized=(deg)=>(deg%360+360)%360;
const segmentChecks=[],turnChecks=[],edgeChecks=[],facilityChecks=[];
const segments=[];
for(const station of n.stations){
 const drawn=nodes[station.id];
 facilityChecks.push({id:station.id,name_matches:drawn?.name===station.name,accessible_matches:drawn?.accessible===station.accessible,
   lines_match:drawn&&eq(drawn.lines,n.lines.filter(l=>l.stations.includes(station.id)).map(l=>l.id))});
}
for(const line of n.lines){
 const drawn=g.line_geometry.find(l=>l.id===line.id),allPoints=[];
 if(!drawn)throw new Error('Missing line '+line.id);
 for(let i=0;i<drawn.edges.length;i++){
   const edge=drawn.edges[i];
   edgeChecks.push({line:line.id,from:edge.from,to:edge.to,expected_pair:[line.stations[i],line.stations[i+1]],
     station_order_matches:edge.from===line.stations[i]&&edge.to===line.stations[i+1],
     source_matches_station_point:eq(edge.points[0],nodes[edge.from].point),target_matches_station_point:eq(edge.points.at(-1),nodes[edge.to].point)});
   edge.points.forEach((p,j)=>{if(!allPoints.length||!eq(p,allPoints.at(-1)))allPoints.push(p);});
   for(let j=1;j<edge.points.length;j++){
     const degrees=angle(edge.points[j-1],edge.points[j]);
     const valid=Math.abs(degrees/45-Math.round(degrees/45))<1e-8;
     segmentChecks.push({line:line.id,edge:[edge.from,edge.to],segment:j-1,degrees,valid_45_grid:valid});
     segments.push({line:line.id,from:edge.from,to:edge.to,a:edge.points[j-1],b:edge.points[j]});
   }
 }
 for(let i=1;i<allPoints.length-1;i++){
   const previous=angle(allPoints[i-1],allPoints[i]),next=angle(allPoints[i],allPoints[i+1]);
   const deflection=Math.min(normalized(next-previous),normalized(previous-next));
   turnChecks.push({line:line.id,point:allPoints[i],deflection,valid:[0,45,90].some(v=>Math.abs(deflection-v)<1e-8)});
 }
}
function cross(a,b){return a[0]*b[1]-a[1]*b[0];}
function intersection(A,B){
 const p=A.a,q=B.a,r=[A.b[0]-p[0],A.b[1]-p[1]],s=[B.b[0]-q[0],B.b[1]-q[1]];
 const determinant=cross(r,s);if(Math.abs(determinant)<1e-8)return null;
 const diff=[q[0]-p[0],q[1]-p[1]],t=cross(diff,s)/determinant,u=cross(diff,r)/determinant;
 if(t< -1e-8||t>1+1e-8||u< -1e-8||u>1+1e-8)return null;
 return [p[0]+t*r[0],p[1]+t*r[1]];
}
const crossMap=new Map();
for(let i=0;i<segments.length;i++)for(let j=i+1;j<segments.length;j++){
 const A=segments[i],B=segments[j];if(A.line===B.line)continue;
 const point=intersection(A,B);if(!point)continue;
 const rounded=point.map(v=>+v.toFixed(6)),key=rounded.join(',');
 const shared=g.nodes.find(node=>Math.hypot(node.point[0]-point[0],node.point[1]-point[1])<1e-6&&node.lines.includes(A.line)&&node.lines.includes(B.line));
 crossMap.set(key,{point:rounded,lines:[A.line,B.line],shared_station:shared?.id??null,
   declared_nonstation_bridge:!shared&&g.non_station_crossings.some(c=>Math.hypot(c.point[0]-point[0],c.point[1]-point[1])<1e-6&&!c.is_transfer)});
}
const crossings=[...crossMap.values()];
const pass=g.nodes.length===16&&new Set(g.nodes.map(s=>s.id)).size===16&&facilityChecks.every(c=>c.name_matches&&c.accessible_matches&&c.lines_match)&&
 edgeChecks.length===16&&edgeChecks.every(c=>c.station_order_matches&&c.source_matches_station_point&&c.target_matches_station_point)&&
 segmentChecks.every(c=>c.valid_45_grid)&&turnChecks.every(c=>c.valid)&&crossings.every(c=>c.shared_station||c.declared_nonstation_bridge);
const out={generated_at:new Date().toISOString(),task_id:'A07',scope:'Computed geometry verification from saved JSON; visual review recorded separately',
 source_geometry:path.resolve(geometryFile),all_checks_pass:pass,node_count:g.nodes.length,edge_count:edgeChecks.length,facility_checks:facilityChecks,
 edge_checks:edgeChecks,segment_checks:segmentChecks,turn_checks:turnChecks,crossings,
 nonstation_bridge_count:crossings.filter(c=>!c.shared_station).length};
fs.writeFileSync(outputFile,JSON.stringify(out,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({all_checks_pass:pass,node_count:out.node_count,edge_count:out.edge_count,crossings},null,2));
