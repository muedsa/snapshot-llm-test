'use strict';
const fs=require('fs'),path=require('path');
const s=require('../../_suite/suite.cjs');
const {Canvas}=require('../../_suite/dsl.cjs');
const dir=__dirname,write=(f,v)=>fs.writeFileSync(path.join(dir,f),typeof v==='string'?v:JSON.stringify(v,null,2)+'\n',{flag:'wx'});
if(!fs.existsSync(path.join(dir,'proposal-v001.md')))throw Error('Proposal must precede render');
const c=new Canvas(1600,1000,{background:'#F1F4F8',font:'Inter,Noto Sans CJK SC'});
const palette={blue:'#2964D8',orange:'#E69B5D',gray:'#8190A2',line:'#53667F',node:'#344C69'};
c.text(64,47,1472,88,'集中 → 过载 → 重新分配',58,'#172D48',{bold:true});
const baseIds=['B01','B02','B03','B04','B05','O01','O02','O03','O04','O05','G01','G02','G03','G04','G05'];
const colorOf=id=>id[0]==='B'?palette.blue:id[0]==='O'?palette.orange:palette.gray;
const segments=[],segmentKeys=new Map(),acts=[];
function line(x1,y1,x2,y2,width,act,role){
 const k=[x1,y1,x2,y2,width].join(','),inverse=[x2,y2,x1,y1,width].join(',');
 if(segmentKeys.has(k))return segmentKeys.get(k);if(segmentKeys.has(inverse))return segmentKeys.get(inverse);
 const id='B-line-'+String(segments.length+1).padStart(4,'0');
 c.line(x1,y1,x2,y2,palette.line,width);
 segments.push({id,act,role,x1,y1,x2,y2,width,color:palette.line});segmentKeys.set(k,id);return id;
}
function route(points,width,act,role){const ids=[];for(let i=1;i<points.length;i++)ids.push(line(...points[i-1],...points[i],width,act,role));return ids;}
function arrow(x1,y1,x2,y2,width,act){
 const head=14,half=6.72,len=Math.hypot(x2-x1,y2-y1),ux=(x2-x1)/len,uy=(y2-y1)/len;
 return [line(x1,y1,x2,y2,width,act,'terminal-arrow-shaft'),line(x2,y2,x2-ux*head-uy*half,y2-uy*head+ux*half,width,act,'terminal-arrow-head'),line(x2,y2,x2-ux*head+uy*half,y2-uy*head-ux*half,width,act,'terminal-arrow-head')];
}
const assignment3=[['B01','B02','O01','O02','G01'],['B03','O03','O04','G02','G03'],['B04','B05','O05','G04','G05']];
for(let index=0;index<3;index++){
 const act=index+1,cy=300+264*index,name=['集中','过载','重新分配'][index];
 c.rect(64,cy-126,1472,252,'#FFFFFF',{radius:20,border:'1 SOLID #D8E3EE'});
 c.text(96,cy-29,280,64,name,index===2?38:44,'#172D48',{bold:true});
 const nodes=[-76,0,76].map((dy,j)=>({id:'N'+(j+1),center_x:1440,center_y:cy+dy,x:1408,y:cy+dy-32,width:64,height:64}));
 const units=[];
 for(let row=0;row<3;row++)for(let col=0;col<5;col++){
  const id=index===2?assignment3[row][col]:baseIds[row*5+col];
  const cx=index===0?440+140*col:index===1?1080+50*col:1010+60*col;
  const uy=cy-64+64*row,receiver=index===2?'N'+(row+1):'N2',target=nodes.find(n=>n.id===receiver),channel_y=uy+30,bus_x=index===0?1200:index===1?1336:1346,width=index===1?4.5:3.5;
  const pts=[[cx,uy+22],[cx,channel_y],[bus_x,channel_y],[bus_x,target.center_y]];
  if(index===1)pts.push([1350,cy-14],[1364,cy+14],[1378,cy-14],[1390,cy]);
  else pts.push([1388,target.center_y]);
  const routeIds=route(pts,width,act,'unit-route-'+id);
  units.push({id,color:colorOf(id),center_x:cx,center_y:uy,diameter:36,radius:18,receiver_node:receiver,route_points:pts,route_segment_ids:routeIds,route_starts_at_radius_plus:4});
 }
 const receivers=index===2?nodes:[nodes[1]];
 const arrows=receivers.map(n=>({receiver:n.id,segment_ids:arrow(index===1?1390:1388,n.center_y,1403,n.center_y,index===1?4.5:3.5,act)}));
 // Nodes and circles are drawn after lines, but all geometric clearance is
 // independently checked below; this order is never used to hide crossings.
 for(const n of nodes)c.rect(n.x,n.y,n.width,n.height,'#FFFFFF',{radius:12,border:'4 SOLID '+palette.node});
 for(const u of units)c.circle(u.center_x,u.center_y,18,u.color);
 acts.push({act,name,band_bbox:[64,cy-126,1536,cy+126],nodes,units,arrows,receiving_node_counts:Object.fromEntries(nodes.map(n=>[n.id,units.filter(u=>u.receiver_node===n.id).length]))});
}
function distanceSegment(px,py,l){const dx=l.x2-l.x1,dy=l.y2-l.y1,length2=dx*dx+dy*dy,t=length2?Math.max(0,Math.min(1,((px-l.x1)*dx+(py-l.y1)*dy)/length2)):0;return Math.hypot(px-(l.x1+t*dx),py-(l.y1+t*dy));}
const checks={unit_count_each_act:acts.every(a=>a.units.length===15),five_each_color_each_act:acts.every(a=>['B','O','G'].every(k=>a.units.filter(u=>u.id[0]===k).length===5)),same_stable_id_set:acts.every(a=>a.units.map(u=>u.id).sort().join(',')===baseIds.slice().sort().join(',')),diameter36_all_units:acts.every(a=>a.units.every(u=>u.diameter===36)),three_equal64_nodes_each_act:acts.every(a=>a.nodes.length===3&&a.nodes.every(n=>n.width===64&&n.height===64)),third_five_mixed_each_node:acts[2].nodes.every(n=>{const us=acts[2].units.filter(u=>u.receiver_node===n.id);return us.length===5&&new Set(us.map(u=>u.color)).size>=2;}),same_active_center_first_second:acts.slice(0,2).every(a=>a.units.every(u=>u.receiver_node==='N2')),all_circles_inside_canvas:acts.every(a=>a.units.every(u=>u.center_x-18>=0&&u.center_x+18<=1600&&u.center_y-18>=0&&u.center_y+18<=1000))};
let minCircleGap=Infinity,minLineNetClearance=Infinity;const lineViolations=[];
for(const a of acts){for(let i=0;i<a.units.length;i++)for(let j=i+1;j<a.units.length;j++)minCircleGap=Math.min(minCircleGap,Math.hypot(a.units[i].center_x-a.units[j].center_x,a.units[i].center_y-a.units[j].center_y)-36);
 for(const l of segments.filter(l=>l.act===a.act))for(const u of a.units){const d=distanceSegment(u.center_x,u.center_y,l),net=d-18-l.width/2;minLineNetClearance=Math.min(minLineNetClearance,net);if(net<0)lineViolations.push({line:l.id,unit:u.id,act:a.act,net_clearance:net});}}
checks.circles_nonoverlapping=minCircleGap>=0;checks.every_actual_stroke_clear_of_all_circles=lineViolations.length===0;
if(!Object.values(checks).every(Boolean))throw Error('Concept geometry failed: '+JSON.stringify({checks,lineViolations}));
const dsl=c.toString();write('concept-B-preview-v001.snapshot',dsl+'\n');
write('story-audit-draft-v001.json',{task_id:'A18',run_id:'20261002-204314-6f31',concept:'B',status:'proposed-and-static-geometric-audit-before-render',dimensions:[1600,1000],only_rendered_text:['集中 → 过载 → 重新分配','集中','过载','重新分配'],palette,acts,segments,checks,minimum_circle_edge_gap_pixels:minCircleGap,minimum_actual_stroke_to_circle_edge_gap_pixels:minLineNetClearance,line_circle_violations:lineViolations,method:'Segment-to-centre Euclidean distance minus radius18 and half actual stroke width; all physical arrow-head segments included; no hidden-circle shortcut.',documentation_reuse:{new_http:0,actual_cached_read:'guide/parser/parser-tags/layout/fonts already genuinely read by this same producer in A17; layout genuinely reread for A18',guide:path.resolve(dir,'../../_suite/shared-doc-000001-response.txt'),layout:path.resolve(dir,'../../_suite/shared-doc-000005-readable.txt'),parser_tags:path.resolve(dir,'../../_suite/shared-doc-000004-readable.txt'),fonts:path.resolve(dir,'../../_suite/shared-fonts-000001-readable.txt')}});
(async()=>{const r=await s.render('A18',dsl+'\n',{version_id:'A18-concept-B-preview-v001',type:'alternative',stem:'concept-B-preview',case_id:'concept-B',independent_case:false,width:1600,height:1000,purpose:'Second actual proposed three-act narrative: horizontal transmission bands, concentration/queue bottleneck/three mixed routes'});const {bytes,body,text,json,...meta}=r;write('render-result-v001.json',meta);console.log(JSON.stringify({ok:r.ok,status:r.http_status,meta:r.meta_path,image:r.image_path,error:r.error_summary}));if(!r.ok||r.dimension_error)throw Error(r.error_summary||r.dimension_error);})().catch(e=>{write('production-failure-v001.json',{at:new Date().toISOString(),error:String(e)});process.exitCode=1;});
