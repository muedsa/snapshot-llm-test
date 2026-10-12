const fs=require('node:fs'),path=require('node:path'),s=require('../_suite/suite.cjs');
const {Canvas,tag,position,matrix2d}=require('../_suite/dsl.cjs');
const dirs=s.taskDirs('A09'),source=path.resolve('tasks/A09-transform-atlas/inputs');
const stamp=JSON.parse(fs.readFileSync(path.join(source,'stamp.json'),'utf8'));
const cases=JSON.parse(fs.readFileSync(path.join(source,'transforms.json'),'utf8'));
const labels=['顺时针 0°','顺时针 90°','顺时针 180°','顺时针 270°','左右镜像','上下镜像','左右镜像 → 顺90°','顺90° → 左右镜像','等比缩放 0.75','横1.25 / 纵0.75','顺时针 30°','上下镜像 → 顺30°'];
function multiply(u,v){return [u[0]*v[0]+u[1]*v[2],u[0]*v[1]+u[1]*v[3],u[2]*v[0]+u[3]*v[2],u[2]*v[1]+u[3]*v[3]];}
function clean(n){return Math.abs(n)<1e-12?0:Number(n.toFixed(9));}
function opmatrix([op,arg]){if(op==='rotate_clockwise_deg'){const a=arg*Math.PI/180;return [Math.cos(a),-Math.sin(a),Math.sin(a),Math.cos(a)];}if(op==='mirror_horizontal')return [-1,0,0,1];if(op==='mirror_vertical')return [1,0,0,-1];if(op==='scale_uniform')return [arg,0,0,arg];if(op==='scale_xy')return [arg[0],0,0,arg[1]];throw Error(op);}
let raw='';
for(const r of stamp.rectangles){const [x,y,w,h]=r.xywh;raw+=position(x,y,w,h,tag('Container',{width:w,height:h,color:r.color}));}
const dot=stamp.dot;raw+=position(dot.center[0]-dot.radius,dot.center[1]-dot.radius,2*dot.radius,2*dot.radius,tag('Container',{width:2*dot.radius,height:2*dot.radius,shape:'CIRCLE',color:dot.color}));
const subject=tag('Container',{width:120,height:120},tag('Stack',{fit:'EXPAND',clipBehavior:'NONE'},raw));
const c=new Canvas(1600,1200,{background:'#F4F5F1'}),ink='#17353E',muted='#607079',grid='#D4DFDF',accent='#157B84';
c.rect(0,0,1600,8,accent);
c.text(152,39,1296,65,'顺序，也有形状',46,ink,{bold:true});
c.text(152,107,1296,39,'同一枚非对称印章 · 12 组组合变换 · 黑点跟随主体，显露镜像与旋转的差别。',23,muted);
c.text(152,155,1296,32,'共同中心 (60,60)  →  每格中心  |  x 向右、y 向下；所有角度按图像顺时针。',21,accent);
const records=[];
cases.forEach((t,i)=>{
 const x=152+(i%4)*332,y=193+Math.floor(i/4)*282,cx=x+150,cy=y+125;
 c.rect(x,y,300,250,'#FFFFFF',{border:'1 SOLID #CCD7D7',radius:10});
 if(i===6||i===7)c.rect(x+1,y+1,298,4,accent);
 c.text(x+15,y+12,270,36,t.id+'  '+labels[i],20,ink,{bold:true,softWrap:false});
 c.line(cx-90,cy,cx+90,cy,'#E1E9E8',1);
 c.line(cx,cy-70,cx,cy+75,'#E1E9E8',1);
 const ry=cy+88,rx=x+54;
 c.line(cx-80,ry,cx+80,ry,grid,1.2);c.line(rx,cy-70,rx,cy+70,grid,1.2);
 for(const tick of [-60,0,60]){
  c.line(cx+tick,ry-4,cx+tick,ry+4,muted,1.2);
  c.text(cx+tick-29,ry+6,58,28,tick>0?'+'+tick:String(tick),20,muted,{align:'CENTER'});
  c.line(rx-4,cy+tick,rx+4,cy+tick,muted,1.2);
  c.text(x+5,cy+tick-14,41,30,tick>0?'+'+tick:String(tick),20,muted,{align:'END'});
 }
 c.circle(cx,cy,2,'#8DADAD');
 let m=[1,0,0,1];const steps=[];
 for(const op of t.operations){m=multiply(opmatrix(op),m);steps.push({operation:op,matrix_2x2:m.map(clean)});}
 const [a,cc,b,d]=m,tx=60-a*60-cc*60,ty=60-b*60-d*60;
 const matrix=matrix2d(a,b,cc,d,tx,ty);
 c.at(cx-60,cy-60,120,120,tag('Transform',{matrix,origin:'(0,0)'},subject));
 const project=([px,py])=>[clean(cx+a*(px-60)+cc*(py-60)),clean(cy+b*(px-60)+d*(py-60))];
 const rects=stamp.rectangles.map((r,j)=>{const [px,py,w,h]=r.xywh;const p=[[px,py],[px+w,py],[px+w,py+h],[px,py+h]].map(project);return {index:j,color:r.color,original_xywh:r.xywh,global_corners:p,bounds:{left:Math.min(...p.map(v=>v[0])),top:Math.min(...p.map(v=>v[1])),right:Math.max(...p.map(v=>v[0])),bottom:Math.max(...p.map(v=>v[1]))}};});
 const dc=project(dot.center),erx=dot.radius*Math.hypot(a,cc),ery=dot.radius*Math.hypot(b,d);
 const dotBounds={left:dc[0]-erx,top:dc[1]-ery,right:dc[0]+erx,bottom:dc[1]+ery};
 const bounds={left:Math.min(...rects.map(r=>r.bounds.left),dotBounds.left),top:Math.min(...rects.map(r=>r.bounds.top),dotBounds.top),right:Math.max(...rects.map(r=>r.bounds.right),dotBounds.right),bottom:Math.max(...rects.map(r=>r.bounds.bottom),dotBounds.bottom)};
 const localMatrix=[a,b,0,0,cc,d,0,0,0,0,1,0,tx,ty,0,1].map(clean);
 const globalMatrix=[a,b,0,0,cc,d,0,0,0,0,1,0,cx-a*60-cc*60,cy-b*60-d*60,0,1].map(clean);
 records.push({id:t.id,operations:t.operations,label:labels[i],cell:{x,y,width:300,height:250,center:[cx,cy]},operation_steps:steps,matrix_column_major_4x4:localMatrix,actual_dsl_matrix:matrix,positioned_offset:[cx-60,cy-60],global_placement_matrix_column_major_4x4:globalMatrix,pivot:[60,60],pivot_global:project([60,60]),rectangles:rects,dot:{original_center:dot.center,original_radius:dot.radius,global_center:dc,ellipse_axes_vectors:[[clean(a*8),clean(b*8)],[clean(cc*8),clean(d*8)]],bounds:dotBounds},final_bounds:bounds,not_clipped_by_cell:bounds.left>=x&&bounds.right<=x+300&&bounds.top>=y&&bounds.bottom<=y+250});
});
const sy=1053;
['#E54B4B','#2364DB','#EAB53B'].forEach((col,i)=>{c.rect(152+i*270,sy,20,20,col);c.text(184+i*270,sy-5,215,36,['竖条 · 红','横条 · 蓝','短条 · 金'][i],21,ink);});
c.circle(991,sy+10,8,'#111111');c.text(1017,sy-5,430,36,'黑点：保留非对称方向',21,ink);
c.text(152,1110,1296,35,'T07：先镜像再旋转   ≠   T08：先旋转再镜像。刻度为距各格中心的像素偏移。',22,ink,{bold:true});
c.text(152,1151,1296,33,'每格复用原始 120×120 图形；组合由 Transform 的列主序矩阵绘制，中心不随外接框移动。',20,muted);
const audit={schema_version:1,task_id:'A09',sources:{stamp:path.join(source,'stamp.json'),transforms:path.join(source,'transforms.json')},grid:{columns:4,rows:3,cell:[300,250],gap:32,outer_bounds:{x:152,y:193,width:1296,height:814},center:[800,600]},composition_rule:'Column vectors: newM=operationM*priorM, in listed order; clockwise screen rotation [[cos,-sin],[sin,cos]]. Every operation around original(60,60). Local matrix includes pivot translation, Positioned adds only grid placement. No center alignment/origin correction is applied twice.',subject_raw_dsl:subject,minimum_label_font_px:20,samples:records,pixel_check:{status:'pending actual service PNG',tolerance_pixels:1.5,method:'Segment each original opaque RGB fill within its cell on actual raw PNG. Compare projected quadrilateral bounds/corners and dot ellipse center/bounds to observed fill; use pixel centers x+0.5,y+0.5. Ignore intermediate antialias fringe, do not alter final pixels. Cross-check original DSL shape coordinates and matrix literals separately. Full actual view is also required.'}};
fs.writeFileSync(path.join(dirs.temp,'transform-atlas-v001.snapshot'),c.toString(),{flag:'wx'});
fs.writeFileSync(path.join(dirs.temp,'geometry-audit-v001.json'),JSON.stringify(audit,null,2)+'\n',{flag:'wx'});
(async()=>{const r=await s.render('A09',c.toString(),{version_id:'A09-v001',type:'baseline',stem:'transform-atlas',width:1600,height:1200});console.log(JSON.stringify({ok:r.ok,id:r.id,image_path:r.image_path,meta_path:r.meta_path,error:r.error_summary}));})();
