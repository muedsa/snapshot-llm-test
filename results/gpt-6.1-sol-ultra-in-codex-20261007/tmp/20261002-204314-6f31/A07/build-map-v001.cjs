'use strict';
const fs=require('node:fs'),path=require('node:path');
const s=require('../_suite/suite.cjs');
const {Canvas}=require('../_suite/dsl.cjs');
const d=s.taskDirs('A07'),source=path.resolve('tasks/A07-transit-topology/inputs/network.json');
const n=JSON.parse(fs.readFileSync(source,'utf8'));
const byId=Object.fromEntries(n.stations.map(a=>[a.id,a]));
const adj=Object.fromEntries(n.stations.map(a=>[a.id,[]]));
n.lines.forEach(l=>{for(let i=1;i<l.stations.length;i++){const a=l.stations[i-1],b=l.stations[i];adj[a].push({to:b,line:l.id});adj[b].push({to:a,line:l.id});}});
function solve(from,to,accessible){
 if(accessible&&(!byId[from].accessible||!byId[to].accessible))return null;
 const queue=[{at:from,line:null,edges:0,transfers:0,stations:[from],lines:[]}],best=new Map();
 while(queue.length){
  queue.sort((a,b)=>a.edges-b.edges||a.transfers-b.transfers||a.stations.join().localeCompare(b.stations.join()));
  const cur=queue.shift(),key=cur.at+'|'+cur.line,old=best.get(key);
  if(old&&(old[0]<cur.edges||(old[0]===cur.edges&&old[1]<=cur.transfers)))continue;
  best.set(key,[cur.edges,cur.transfers]);
  if(cur.at===to){
   const segments=[],transferStations=[];
   cur.lines.forEach((l,i)=>{if(!segments.length||segments.at(-1).line!==l){if(i)transferStations.push(cur.stations[i]);segments.push({line:l,stations:[cur.stations[i]],edge_count:0});}segments.at(-1).stations.push(cur.stations[i+1]);segments.at(-1).edge_count++;});
   return {station_sequence:cur.stations,station_names:cur.stations.map(id=>byId[id].name),line_for_each_edge:cur.lines,line_segments:segments,edge_count:cur.edges,transfer_count:cur.transfers,transfer_stations:transferStations,accessible_as_drawn:[from,to,...transferStations].every(id=>byId[id].accessible),accessibility_failures:[from,to,...transferStations].filter(id=>!byId[id].accessible)};
  }
  for(const a of adj[cur.at]){const changes=cur.line&&cur.line!==a.line;if(accessible&&changes&&!byId[cur.at].accessible)continue;queue.push({at:a.to,line:a.line,edges:cur.edges+1,transfers:cur.transfers+(changes?1:0),stations:[...cur.stations,a.to],lines:[...cur.lines,a.line]});}
 }
 return null;
}
const routes={schema_version:1,task_id:'A07',source,city:'澄川',fictional_city:true,routing_rules:{objective:['minimum_station_edges','minimum_line_changes'],station_edges_bidirectional:true,all_station_edge_times_equal:true,first_boarding_is_transfer:false,accessibility:'Origin, destination and changed-line stations must have accessible=true; inaccessible stations may be passed while staying on the same line.'},stations:n.stations,lines:n.lines,queries:n.queries.map((q,i)=>{const ordinary=solve(q.from,q.to,false),accessible=solve(q.from,q.to,true);return {id:`Q${i+1}`,...q,ordinary,ordinary_is_accessible:ordinary.accessible_as_drawn,accessible,alternative_required:!ordinary.accessible_as_drawn};})};
fs.writeFileSync(path.join(d.temp,'routes-v001.json'),JSON.stringify(routes,null,2)+'\n',{flag:'wx'});
const xy={S01:[155,465],S02:[315,465],S03:[475,465],S04:[665,465],S05:[1010,465],S06:[1220,465],S07:[155,690],S08:[440,690],S09:[880,250],S10:[1120,250],S11:[1480,250],S12:[1480,465],S13:[155,840],S14:[290,840],S15:[785,690],S16:[1380,750]};
const labels={S01:[95,494,145],S02:[255,389,145],S03:[415,494,145],S04:[640,494,175],S05:[1038,494,170],S06:[1160,389,155],S07:[95,614,145],S08:[460,716,170],S09:[820,174,160],S10:[1060,174,160],S11:[1410,174,145],S12:[1410,494,145],S13:[95,864,140],S14:[235,864,140],S15:[730,716,165],S16:[1412,716,145]};
const geometry={schema_version:1,task_id:'A07',map_type:'non_geographic schematic',nodes:n.stations.map(a=>({...a,point:xy[a.id],label:{x:labels[a.id][0],y:labels[a.id][1],width:labels[a.id][2],height:66},lines:n.lines.filter(l=>l.stations.includes(a.id)).map(l=>l.id)})),line_geometry:n.lines.map(l=>({id:l.id,stations:l.stations,edges:l.stations.slice(1).map((to,i)=>{const from=l.stations[i];return {from,to,points:l.id==='G'&&from==='S05'?[[1010,465],[1010,360],[1380,360],[1380,750]]:[xy[from],xy[to]]};})})),non_station_crossings:[{point:[1380,465],line_edges:[{line:'R',from:'S06',to:'S12'},{line:'G',from:'S05',to:'S16'}],representation:'White gap in R track at x1363..1397 and uninterrupted G vertical bridge; no station ring.',is_transfer:false}],shared_stations:['S04','S08','S05'],styles:{background:'#F7F6F2',ink:'#18343E',muted:'#577078',R:'#C94745',B:'#286AA7',G:'#1A836F',station_name_font_px:23,facility_font_px:20},all_route_segment_angles:'0/45/90 degrees',geographic_accuracy_claim:false};
fs.writeFileSync(path.join(d.temp,'map-geometry-v001.json'),JSON.stringify(geometry,null,2)+'\n',{flag:'wx'});
const p={background:'#F7F6F2',ink:'#18343E',muted:'#577078',R:'#C94745',B:'#286AA7',G:'#1A836F'};
const c=new Canvas(1600,1000,{background:p.background});
c.rect(0,0,1600,8,p.G);
c.text(60,40,1050,62,'澄川 · 三线出行',44,p.ink,{bold:true});
c.text(62,111,1000,38,'虚构城市｜非地理地图 · 站距与走向仅表达拓扑',23,p.muted);
function badge(x,y,letter,color,small=false){c.card(x,y,small?43:48,small?34:43,color,{radius:10});c.text(x,y+1,small?43:48,small?32:40,letter,small?23:28,'#FFFFFF',{bold:true,align:'CENTER'});}
[['R','红线'],['B','蓝线'],['G','绿线']].forEach(([id,name],i)=>{const x=1150+i*130;badge(x,103,id,p[id],true);c.text(x+51,104,75,34,name,23,p.ink,{bold:true});});
geometry.line_geometry.filter(l=>l.id!=='G').forEach(l=>l.edges.forEach(e=>c.polyline(e.points,p[l.id],12,{roundCaps:true})));
// The R edge still connects S06-S12. Its local white cut is a visual bridge,
// not a station or a severed graph edge.
c.line(1363,465,1397,465,p.background,24);
geometry.line_geometry.find(l=>l.id==='G').edges.forEach(e=>c.polyline(e.points,p.G,12,{roundCaps:true}));
badge(57,444,'R',p.R);badge(57,669,'B',p.B);badge(57,819,'G',p.G);
c.card(60,570,300,48,'#E8EFEA',{radius:12});
c.text(76,578,268,36,'设施不全站仍可乘车通过',20,p.ink);
geometry.nodes.forEach(a=>{
 const [x,y]=a.point,shared=a.lines.length>1;
 c.circle(x,y,shared?19:13,p.ink);c.circle(x,y,shared?16:10,p.background);
 if(shared){c.circle(x,y,11,p.ink);c.circle(x,y,8,p.background);}
 if(a.accessible)c.circle(x,y,4.5,p.G);else c.line(x-5,y,x+5,y,'#768186',3);
 const q=a.label;
 c.text(q.x,q.y,q.width,34,a.id+' '+a.name,23,p.ink,{bold:true});
 c.text(q.x,q.y+36,q.width,30,a.accessible?'无障碍':'设施不全',20,a.accessible?p.G:'#768186');
});
c.text(1410,595,145,65,'跨线过桥\n不可换乘',20,p.muted,{lineHeight:1.3});
c.line(60,945,1540,945,'#D1DBD8',1);
c.circle(77,974,13,p.ink);c.circle(77,974,10,p.background);c.circle(77,974,7,p.ink);c.circle(77,974,4,p.background);
c.text(100,957,216,37,'双环：换乘站',20,p.ink);
c.circle(332,974,5,p.G);c.text(350,957,165,37,'点：无障碍',20,p.ink);
c.line(536,974,548,974,'#768186',3);c.text(566,957,328,37,'横杠：设施不全',20,p.ink);
c.line(915,974,970,974,p.R,8);c.line(936,963,936,985,p.background,18);c.line(936,963,936,985,p.G,8);
c.text(991,957,548,37,'过桥：线条交叉，不能换乘',20,p.ink);
const dsl=c.toString();
fs.writeFileSync(path.join(d.temp,'network-map-v001.snapshot'),dsl,{flag:'wx'});
(async()=>{const r=await s.render('A07',dsl,{version_id:'A07-map-v001',type:'baseline',stem:'network-map',width:1600,height:1000});console.log(JSON.stringify({ok:r.ok,id:r.id,status:r.http_status,image_path:r.image_path,meta_path:r.meta_path,error:r.error_summary,dimensions:r.png_dimensions}));})();
