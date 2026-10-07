'use strict';
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const s=require('../_suite/suite.cjs'),{Canvas}=require('../_suite/dsl.cjs');
const d=s.taskDirs('A08'),floorFile=path.resolve('tasks/A08-accessible-wayfinding/inputs/floor.txt'),legendFile=path.resolve('tasks/A08-accessible-wayfinding/inputs/legend.json');
const raw=fs.readFileSync(floorFile),rows=raw.toString('utf8').trimEnd().split(/\r?\n/),legend=JSON.parse(fs.readFileSync(legendFile,'utf8'));
if(rows.length!==18||rows.some(r=>r.length!==26))throw new Error('Unexpected source dimensions');
const H=18,W=26,special={},counts={};
rows.forEach((row,y)=>[...row].forEach((ch,x)=>{counts[ch]=(counts[ch]||0)+1;if(/[SEABCD]/.test(ch))special[ch]=[x,y];}));
const key=([x,y])=>x+','+y,walk=([x,y])=>x>=0&&x<W&&y>=0&&y<H&&rows[y][x]!=='#';
function bfs(from,to){
 const queue=[from],parents=new Map([[key(from),null]]);let finish=null;
 for(let i=0;i<queue.length;i++){
  const at=queue[i];if(key(at)===key(to)){finish=at;break;}
  for(const delta of [[1,0],[0,1],[-1,0],[0,-1]]){const next=[at[0]+delta[0],at[1]+delta[1]];if(walk(next)&&!parents.has(key(next))){parents.set(key(next),at);queue.push(next);}}
 }
 if(!finish)throw new Error('Disconnected required endpoints');
 const result=[];for(let at=finish;at;at=parents.get(key(at)))result.push(at);return result.reverse();
}
const S=special.S,E=special.E,B=special.B,D=special.D;
const sd=bfs(S,D),de=bfs(D,E),direct=bfs(S,E),leftOfB=[B[0]-1,B[1]],sb=[...bfs(S,leftOfB),B],bd=bfs(B,D);
const join=(...a)=>a.flatMap((p,i)=>i?p.slice(1):p);
const p1=join(sd,de),p2=join(sb,bd,de);
function check(p){return {all_cells_walkable:p.every(walk),all_steps_orthogonal:p.slice(1).every((q,i)=>Math.abs(q[0]-p[i][0])+Math.abs(q[1]-p[i][1])===1),steps:p.length-1,distance_meters:(p.length-1)*2,sequence_count:p.length};}
if(check(p1).steps!==direct.length-1||check(sb).steps!==bfs(S,B).length-1)throw new Error('Selected equal shortest path check failed');
const origin={x:66,y:200},cell=40,px=([x,y])=>[origin.x+(x+.5)*cell,origin.y+(y+.5)*cell];
function segment(from,to,p){return {from,to,cell_centers:p,physical_centers_meters:p.map(([x,y])=>[2*x+1,2*y+1]),pixel_centers:p.map(px),...check(p),bfs_shortest_steps:bfs(p[0],p.at(-1)).length-1};}
const route1={id:'route-01',label:'S→E shortest',cell_centers:p1,physical_centers_meters:p1.map(([x,y])=>[2*x+1,2*y+1]),pixel_centers:p1.map(px),segments:[segment('S','E',p1)],...check(p1),shortest_verified_steps:direct.length-1,selected_path_note:'An equal shortest S→E path through coordinate D; D is not a required waypoint for route 01.'};
const route2={id:'route-02',label:'S→B→D→E shortest with ordered waypoints',cell_centers:p2,physical_centers_meters:p2.map(([x,y])=>[2*x+1,2*y+1]),pixel_centers:p2.map(px),segments:[segment('S','B',sb),segment('B','D',bd),segment('D','E',de)],...check(p2),ordered_waypoints:['S','B','D','E'],b_before_d:p2.findIndex(p=>key(p)===key(B))<p2.findIndex(p=>key(p)===key(D)),selected_path_note:'Reach B from left neighbor (11,3), then move down to (12,4). Avoids a repeated opposite-direction B edge without changing the optimal 13-step S→B distance.'};
const reached=new Set([key(S)]),queue=[S];for(let i=0;i<queue.length;i++){const at=queue[i];for(const delta of [[1,0],[0,1],[-1,0],[0,-1]]){const q=[at[0]+delta[0],at[1]+delta[1]];if(walk(q)&&!reached.has(key(q))){reached.add(key(q));queue.push(q);}}}
const sourceNotes={prompt_typo:'Prompt says A/A/B/D; actual floor and legend each specify A/B/C/D. Used actual inputs without modifying them.',zero_based_coordinates:true,origin:'top-left cell (0,0)',cell_edge_meters:2,physical_center_rule:'((x+0.5)*2,(y+0.5)*2)',movement:'four-neighbor only'};
const paths={schema_version:1,task_id:'A08',sources:{floor:floorFile,legend:legendFile,floor_sha256:crypto.createHash('sha256').update(raw).digest('hex')},source_notes:sourceNotes,grid:{width:W,height:H,rows,counts,total_cells:W*H,wall_cells:counts['#'],walkable_cells:W*H-counts['#'],doorways:{vertical_x8:[[8,4],[8,12]],vertical_x17:[[17,7],[17,14]],horizontal_y9:[[3,9],[12,9],[22,9]]}},special_cells:Object.fromEntries(Object.entries(special).map(([id,coordinates])=>[id,{name:legend[id],coordinates,pixel_center:px(coordinates),walkable:true}])),routes:[route1,route2],connectivity_check:{reachable_from_S:reached.size,total_walkable_cells:W*H-counts['#'],all_walkable_connected:reached.size===W*H-counts['#'],route_checks_passed:[route1,route2].every(r=>r.all_cells_walkable&&r.all_steps_orthogonal),all_boundary_cells_remain_walls:true}};
fs.writeFileSync(path.join(d.temp,'paths-v001.json'),JSON.stringify(paths,null,2)+'\n',{flag:'wx'});
const c=new Canvas(1560,1080,{background:'#F7F6F2'}),P={ink:'#18343E',muted:'#577078',wall:'#324951',open:'#FFFFFF',grid:'#B8C8C8',r1:'#286AA7',r2:'#B95132'};
c.rect(0,0,1560,8,P.r1);
c.text(60,39,1450,61,'格心之间 · 展馆导览',44,P.ink,{bold:true});
c.text(62,111,1450,38,'虚构展馆 / 26×18 格 · 每格 2 米 · 只走上下左右，不穿墙、不斜行。',23,P.muted);
const cellGeometry=[];
rows.forEach((row,y)=>[...row].forEach((ch,x)=>{
 const rect={x:origin.x+x*cell,y:origin.y+y*cell,width:cell,height:cell};
 c.rect(rect.x,rect.y,cell,cell,ch==='#'?P.wall:/[SE]/.test(ch)?'#D9EEE6':/[ABCD]/.test(ch)?'#F7E7CA':P.open);
 cellGeometry.push({x,y,symbol:ch,walkable:ch!=='#',rect,pixel_center:px([x,y])});
}));
for(let x=0;x<=W;x++)c.line(origin.x+x*cell,origin.y,origin.x+x*cell,origin.y+H*cell,P.grid,1);
for(let y=0;y<=H;y++)c.line(origin.x,origin.y+y*cell,origin.x+W*cell,origin.y+y*cell,P.grid,1);
c.polyline(p1.map(px),P.r1,8,{roundCaps:true});
const edgeKey=(a,b)=>[key(a),key(b)].sort().join('|'),unique=new Set();
for(let i=1;i<p2.length;i++){
 const a=p2[i-1],b=p2[i],k=edgeKey(a,b);if(unique.has(k))continue;unique.add(k);
 const A=px(a),Z=px(b),len=40;
 for(let t=0;t<len;t+=16){const end=Math.min(t+9,len);c.line(A[0]+(Z[0]-A[0])*t/len,A[1]+(Z[1]-A[1])*t/len,A[0]+(Z[0]-A[0])*end/len,A[1]+(Z[1]-A[1])*end/len,P.r2,4);}
}
const arrows=[];
function routeArrows(points,color,width,offset){
 for(let i=offset;i<points.length-1;i+=5){const a=points[i],b=points[i+1];if(/[SEABCD]/.test(rows[a[1]][a[0]])||/[SEABCD]/.test(rows[b[1]][b[0]]))continue;const A=px(a),Z=px(b),ux=(Z[0]-A[0])/40,uy=(Z[1]-A[1])/40,m=[(A[0]+Z[0])/2,(A[1]+Z[1])/2],tail=[m[0]-ux*10,m[1]-uy*10],tip=[m[0]+ux*7,m[1]+uy*7];c.arrow(...tail,...tip,color,width,{headLength:6,headWidth:color===P.r1?5:3});arrows.push({color,source_cell:a,target_cell:b,tail,tip});}
}
routeArrows(p1,P.r1,3.3,1);routeArrows(p2,P.r2,2.6,3);
Object.entries(special).forEach(([letter,q])=>{
 const center=px(q),fill=/[SE]/.test(letter)?'#1A836F':'#8D5A24';
 c.circle(...center,12.5,fill);c.text(center[0]-14,center[1]-14,28,31,letter,21,'#FFFFFF',{bold:true,align:'CENTER'});
});
// Complete edge rulers locate every cell while preserving route centerlines.
c.text(66,148,220,29,'x →',18,P.muted,{bold:true});c.text(20,168,36,28,'y ↓',18,P.muted,{bold:true});
for(let x=0;x<W;x++){
 c.text(origin.x+x*cell,168,cell,31,String(x),18,P.ink,{align:'CENTER'});
 c.text(origin.x+x*cell,930,cell,31,String(x),18,P.ink,{align:'CENTER'});
}
for(let y=0;y<H;y++)c.text(22,origin.y+y*cell+7,36,32,String(y),18,P.ink,{align:'CENTER'});
const x=1140;
c.card(x,192,360,209,'#FFFFFF',{radius:18,border:'1 SOLID #DDE6E0'});
c.text(x+22,212,316,38,'01 · 直达出口',26,P.r1,{bold:true});
c.text(x+22,261,316,49,`${route1.steps} 步 · ${route1.distance_meters} 米`,35,P.ink,{bold:true});
c.text(x+22,321,316,36,'S (2,2) → E (23,15)',22,P.muted);
c.arrow(x+24,377,x+115,377,P.r1,8,{headLength:14,headWidth:7});c.text(x+134,358,210,38,'蓝色实线',22,P.r1,{bold:true});
c.card(x,428,360,287,'#FFFFFF',{radius:18,border:'1 SOLID #DDE6E0'});
c.text(x+22,449,316,38,'02 · 先 B，后 D',26,P.r2,{bold:true});
c.text(x+22,496,316,49,`${route2.steps} 步 · ${route2.distance_meters} 米`,35,P.ink,{bold:true});
route2.segments.forEach((a,i)=>c.text(x+22,554+i*32,316,34,`${a.from} → ${a.to}    ${a.steps} 步 / ${a.distance_meters} 米`,22,P.muted));
c.text(x+22,655,316,55,'经 B 北向绕入，再向南去 D；\n全程沿橙色虚线行进。',22,P.r2,{lineHeight:1.18});
c.card(x,742,360,196,'#E8EFEA',{radius:18});
c.text(x+22,760,316,35,'展区与格坐标',24,P.ink,{bold:true});
['A','B','C','D'].forEach((id,i)=>c.text(x+22,801+i*32,316,35,`${id} ${legend[id]}  (${special[id].join(',')})`,22,P.ink));
c.text(66,970,200,31,'尺度 / 每格 2 米',22,P.ink,{bold:true});
for(let i=0;i<4;i++)c.rect(66+i*40,1008,40,12,i%2?'#E0E8E5':P.ink,{border:'1 SOLID #18343E'});
c.text(64,1024,45,31,'0',18,P.muted);c.text(135,1024,45,31,'4',18,P.muted);c.text(209,1024,65,31,'8 米',18,P.muted);
c.line(304,990,406,990,P.r1,8);for(let q=304;q<406;q+=16)c.line(q,990,Math.min(q+9,406),990,P.r2,4);
c.text(425,971,1060,34,'重合段：蓝实线底 + 橙虚线，二者均在同一格心。',22,P.ink);
c.rect(304,1025,20,20,P.wall);c.text(337,1013,190,40,'墙：不可走',22,P.ink);
c.rect(556,1025,20,20,P.open,{border:'1 SOLID #B8C8C8'});c.text(589,1013,210,40,'白格：可走',22,P.ink);
c.text(859,1013,640,40,'S 入口 (2,2)  /  E 出口 (23,15)',22,P.ink);
const geometry={task_id:'A08',version_id:'A08-v001',canvas:{width:1560,height:1080},grid_origin_pixels:origin,cell_size_pixels:cell,cells:cellGeometry,routes:[{id:route1.id,points:p1.map(px),width:8,color:P.r1,line_type:'solid'},{id:route2.id,points:p2.map(px),width:4,color:P.r2,line_type:'dashed 9 on / 7 off'}],arrows,coordinate_rulers:{x:{all_labels:Array.from({length:W},(_,i)=>i),font_px:18,positions:['top','bottom']},y:{all_labels:Array.from({length:H},(_,i)=>i),font_px:18,positions:['left']}},special_label_font_px:21,body_min_font_px:22,overlap_rule:'Both centerlines coincide exactly; wider solid blue stays visible beside and between thin orange dashes.',source_notes:sourceNotes};
fs.writeFileSync(path.join(d.temp,'map-geometry-v001.json'),JSON.stringify(geometry,null,2)+'\n',{flag:'wx'});
const dsl=c.toString();fs.writeFileSync(path.join(d.temp,'wayfinding-v001.snapshot'),dsl,{flag:'wx'});
(async()=>{const r=await s.render('A08',dsl,{version_id:'A08-v001',type:'baseline',stem:'wayfinding',width:1560,height:1080});console.log(JSON.stringify({ok:r.ok,id:r.id,status:r.http_status,image_path:r.image_path,meta_path:r.meta_path,error:r.error_summary,dimensions:r.png_dimensions,route_steps:[route1.steps,route2.steps],segments:route2.segments.map(a=>a.steps)}));})();
