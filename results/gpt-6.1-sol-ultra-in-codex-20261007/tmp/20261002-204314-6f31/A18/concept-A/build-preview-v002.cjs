const fs=require('node:fs'),path=require('node:path'),{Canvas}=require('../../_suite/dsl.cjs'),s=require('../../_suite/suite.cjs');
const out=__dirname,write=(n,d)=>fs.writeFileSync(path.join(out,n),d,{flag:'wx'});
const p={background:'#EEF2F7',panel:'#FAFCFE',ink:'#20354D',muted:'#8695AA',line:'#71869F',border:'#D5DFEB',blue:'#367BE7',orange:'#E8953E',gray:'#A1ADBE'};
const c=new Canvas(1600,1000,{background:p.background});
c.text(64,65,1472,90,'集中 → 过载 → 重新分配',54,p.ink,{bold:true});
const panels=[{id:'act-01',name:'集中',x:64},{id:'act-02',name:'过载',x:568},{id:'act-03',name:'重新分配',x:1072}];
const colorNames=['blue','orange','gray'],units=Array.from({length:15},(_,i)=>({id:colorNames[i%3][0].toUpperCase()+String(Math.floor(i/3)+1).padStart(2,'0'),color_name:colorNames[i%3],color:p[colorNames[i%3]],diameter:36}));
const baseY=270,center={x:340,y:334},nodeCenters=[{id:'N1',x:340,y:110},{id:'N2',...center},{id:'N3',x:340,y:544}],theta=[-1.04,-.52,0,.52,1.04];
const audit={task_id:'A18',concept:'A',version:'A18-concept-A-v001',canvas:{width:1600,height:1000},only_text:['集中 → 过载 → 重新分配','集中','过载','重新分配'],unit_diameter:36,node_size:{width:64,height:64},acts:[],all_line_segments:[]};
function global(panel,x,y){return{x:panel.x+x,y:baseY+y};}
function drawArrow(panel,x1,y1,x2,y2,details={}){
 const a=global(panel,x1,y1),b=global(panel,x2,y2),width=details.width??2.5,headLength=details.headLength??9,headWidth=details.headWidth??4;
 c.arrow(a.x,a.y,b.x,b.y,p.line,width,{headLength,headWidth});
 const len=Math.hypot(b.x-a.x,b.y-a.y),ux=(b.x-a.x)/len,uy=(b.y-a.y)/len;
 const segments=[{from:[a.x,a.y],to:[b.x,b.y],width},{from:[b.x,b.y],to:[b.x-ux*headLength-uy*headWidth,b.y-uy*headLength+ux*headWidth],width},{from:[b.x,b.y],to:[b.x-ux*headLength+uy*headWidth,b.y-uy*headLength-ux*headWidth],width}];
 const record={id:panel.id+'-arrow-'+String(audit.all_line_segments.filter(l=>l.act_id===panel.id).length+1).padStart(2,'0'),act_id:panel.id,color:p.line,...details,segments};audit.all_line_segments.push(record);return record.id;
}
function edgeArrow(panel,from,to,targetRadius=20,details={}){const dx=to.x-from.x,dy=to.y-from.y,len=Math.hypot(dx,dy),ux=dx/len,uy=dy/len;return drawArrow(panel,from.x+ux*20,from.y+uy*20,to.x-ux*targetRadius,to.y-uy*targetRadius,details);}
function drawNode(panel,n,active){const q=global(panel,n.x,n.y);c.rect(q.x-32,q.y-32,64,64,active?p.ink:'#FAFCFE',{radius:12,border:'2 SOLID '+(active?p.ink:'#A7B5C8')});[16,28,40].forEach(d=>c.rect(q.x-14,q.y-32+d,28,5,active?'#D8E9F4':'#A7B5C8',{radius:2}));return{id:n.id,center:[q.x,q.y],bbox:[q.x-32,q.y-32,q.x+32,q.y+32],width:64,height:64,active,shape:'rounded_rectangle',receives:[]};}
function sceneUnits(index){
 if(index===0)return units.map((u,i)=>{const radius=[106,176,246][Math.floor(i/5)],angle=Math.PI+theta[i%5];return{...u,x:center.x+radius*Math.cos(angle),y:center.y+radius*Math.sin(angle),receiver:'N2',radial_lane:i%5,radial_level:Math.floor(i/5)};});
 if(index===1)return units.map((u,i)=>({...u,x:112+(i%5)*40,y:294+Math.floor(i/5)*40,receiver:'N2',queue_row:Math.floor(i/5),queue_column:i%5}));
 return units.map((u,i)=>{const group=Math.floor(i/5),n=nodeCenters[group],angle=Math.PI+[-.92,-.46,0,.46,.92][i%5];return{...u,x:n.x+106*Math.cos(angle),y:n.y+106*Math.sin(angle),receiver:n.id,distribution_group:group};});
}
panels.forEach((panel,index)=>{
 c.text(panel.x,205,464,52,panel.name,34,p.ink,{bold:true});c.rect(panel.x,270,464,660,p.panel,{radius:26,border:'1 SOLID '+p.border});
 const scene=sceneUnits(index),nodes=nodeCenters.map(n=>drawNode(panel,n,index===2||n.id==='N2'));
 if(index===0){for(let lane=0;lane<5;lane++){const laneUnits=scene.filter(u=>u.radial_lane===lane).sort((a,b)=>b.radial_level-a.radial_level);for(let i=0;i<laneUnits.length-1;i++){const from=laneUnits[i],to=laneUnits[i+1];edgeArrow(panel,from,to,20,{from_unit:from.id,to_unit:to.id,receiver:'N2',role:'converging_flow'});}const from=laneUnits.at(-1);edgeArrow(panel,from,center,48,{from_unit:from.id,receiver:'N2',role:'center_inlet'});}}
 if(index===1){for(let row=0;row<3;row++){drawArrow(panel,40,294+row*40,86,294+row*40,{role:'arrival_pressure',receiver:'N2'});const last=scene.find(u=>u.queue_row===row&&u.queue_column===4);const target={x:304,y:314+row*20};const dx=target.x-last.x,dy=target.y-last.y,len=Math.hypot(dx,dy);drawArrow(panel,last.x+20*dx/len,last.y+20*dy/len,target.x,target.y,{from_unit:last.id,receiver:'N2',role:'packed_queue_inlet',headLength:8,headWidth:3.5});}}
 if(index===2)for(const u of scene){const n=nodeCenters.find(n=>n.id===u.receiver);edgeArrow(panel,u,n,48,{from_unit:u.id,receiver:u.receiver,role:'independent_receiving_route'});}
 for(const u of scene){const q=global(panel,u.x,u.y);c.circle(q.x,q.y,18,u.color);u.center=[q.x,q.y];u.bbox=[q.x-18,q.y-18,q.x+18,q.y+18];delete u.x;delete u.y;nodes.find(n=>n.id===u.receiver).receives.push(u.id);}
 audit.acts.push({id:panel.id,name:panel.name,panel_bbox:[panel.x,270,panel.x+464,930],units:scene,nodes});
});
// Neutral transition marks sit in the gaps and add no text or information unit.
[[540,556],[1044,1060]].forEach(([x1,x2],i)=>{c.arrow(x1,600,x2,600,p.muted,2.5,{headLength:7,headWidth:4});audit.all_line_segments.push({id:'transition-'+(i+1),act_id:'transition',role:'between_acts',color:p.muted,segments:[{from:[x1,600],to:[x2,600],width:2.5},{from:[x2,600],to:[x2-7,604],width:2.5},{from:[x2,600],to:[x2-7,596],width:2.5}]});});
function distanceToSegment(p,a,b){const vx=b[0]-a[0],vy=b[1]-a[1],len=vx*vx+vy*vy,t=len?Math.max(0,Math.min(1,((p[0]-a[0])*vx+(p[1]-a[1])*vy)/len)):0;return Math.hypot(p[0]-a[0]-t*vx,p[1]-a[1]-t*vy);}
const checks=[];
for(const act of audit.acts){let minPair=Infinity,minClearance=Infinity;for(let i=0;i<act.units.length;i++){const u=act.units[i];for(let j=i+1;j<act.units.length;j++)minPair=Math.min(minPair,Math.hypot(u.center[0]-act.units[j].center[0],u.center[1]-act.units[j].center[1]));const box=act.panel_bbox;if(u.bbox[0]<box[0]||u.bbox[1]<box[1]||u.bbox[2]>box[2]||u.bbox[3]>box[3])throw Error('Unit clipped');}
 for(const line of audit.all_line_segments.filter(l=>l.act_id===act.id))for(const seg of line.segments)for(const u of act.units){const clear=distanceToSegment(u.center,seg.from,seg.to)-18-seg.width/2;minClearance=Math.min(minClearance,clear);if(clear<0)throw Error('Line intersects unit '+act.id+' '+u.id+' '+line.id+' '+clear);}
 if(minPair<36)throw Error('Unit overlap');
 const counts=Object.fromEntries(colorNames.map(color=>[color,act.units.filter(u=>u.color_name===color).length]));if(Object.values(counts).some(n=>n!==5))throw Error('Wrong color count');
 checks.push({act_id:act.id,color_counts:counts,stable_IDs:act.units.map(u=>u.id).sort(),minimum_circle_center_distance:minPair,minimum_line_edge_to_circle_edge_clearance:minClearance,all_circles_inside_panel:true,all_unit_diameters_36:true,all_three_nodes_equal_64:true,receiver_counts:act.nodes.map(n=>({id:n.id,count:n.receives.length,colors:[...new Set(act.units.filter(u=>u.receiver===n.id).map(u=>u.color_name))]}))});
}
let globalMinLineClearance=Infinity,minNodeClearance=Infinity; for(const line of audit.all_line_segments)for(const seg of line.segments)for(const act of audit.acts)for(const u of act.units){const clearance=distanceToSegment(u.center,seg.from,seg.to)-18-seg.width/2;globalMinLineClearance=Math.min(globalMinLineClearance,clearance);if(clearance<0)throw Error('Global line intersects circle '+line.id+' '+u.id);}for(const act of audit.acts)for(const u of act.units)for(const n of act.nodes){const nx=Math.max(n.bbox[0],Math.min(n.bbox[2],u.center[0])),ny=Math.max(n.bbox[1],Math.min(n.bbox[3],u.center[1])),clear=Math.hypot(u.center[0]-nx,u.center[1]-ny)-18;minNodeClearance=Math.min(minNodeClearance,clear);if(clear<0)throw Error('Unit intersects node');}audit.global_min_line_clearance=globalMinLineClearance;audit.global_min_node_clearance=minNodeClearance;audit.geometry_checks=checks;audit.final=false;audit.preview_only=true;audit.no_Image=true;audit.generated_at=new Date().toISOString();
const dsl=c.toString();write('concept-A-v001.snapshot',dsl);write('story-audit-draft-v001.json',JSON.stringify(audit,null,2)+'\n');
(async()=>{const r=await s.render('A18',dsl,{version_id:'A18-concept-A-v001',parent_version:null,type:'alternative',stem:'concept-A',case_id:'concept-A',width:1600,height:1000,purpose:'A18 composition A real 1600×1000 preview; geometric conservation'});const out={ok:r.ok,http_status:r.http_status,content_type:r.content_type,png_dimensions:r.png_dimensions,meta_path:r.meta_path,image_path:r.image_path,version_id:r.version_id,error_summary:r.error_summary};write('render-v001.json',JSON.stringify(out,null,2)+'\n');console.log(JSON.stringify(out));})().catch(e=>{console.error(e.stack);process.exitCode=1;});
