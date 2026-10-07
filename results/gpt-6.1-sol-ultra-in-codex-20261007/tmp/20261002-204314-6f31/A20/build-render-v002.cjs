const fs=require('node:fs'),path=require('node:path');
const s=require('../_suite/suite.cjs');
const {Canvas}=require('../_suite/dsl.cjs');
const [layoutPath,versionId='A20-v001']=process.argv.slice(2);
const layout=JSON.parse(fs.readFileSync(layoutPath,'utf8'));
const c=new Canvas(1600,1100,{background:'#F5F3EE',clipBehavior:'NONE'});
const ink='#253337',blue='#286688',accent='#B14D39',rule='#D5DCDB';
c.text(48,30,900,57,'密集点，也能一眼对应',42,ink,{bold:true});
c.text(50,94,1000,34,'24 个观测点  /  示意坐标  /  原点左下  /  数值单位：指数',22,'#5A6B6E');
c.card(1130,30,422,100,'#EDE5D8',{radius:12});
c.text(1150,44,382,28,'最高三点  ·  TOP 3',20,accent,{bold:true});
c.text(1150,78,382,32,'广场 93  ·  中庭 91  ·  研究所 90',20,ink);
c.rect(280,160,1040,760,'#FCFDFC',{border:'1 SOLID #BDC9C8'});
for(let t=0;t<=100;t+=20){
 const x=280+10.4*t,y=920-7.6*t;
 c.line(x,160,x,920,rule,1);
 c.line(280,y,1320,y,rule,1);
 c.text(x-23,927,46,27,String(t),18,'#687B7E',{align:'CENTER'});
 c.text(228,y-13,43,28,String(t),18,'#687B7E',{align:'END'});
}
c.text(1272,963,60,28,'x →',21,ink);
c.text(182,142,38,28,'y ↑',21,ink);
for(const m of layout.markers){
 const col=['M10','M08','M23'].includes(m.id)?accent:blue;
 if(m.polyline?.length>1)c.polyline(m.polyline,col,1.8);
}
for(const m of layout.markers){
 const col=['M10','M08','M23'].includes(m.id)?accent:blue;
 const a=m.anchor,b=m.label;
 c.circle(a.x,a.y,(m.diameter??12)/2,col);
 c.card(b.x,b.y,b.width,b.height,'#FFFFFF',{radius:5,border:`1 SOLID ${['M10','M08','M23'].includes(m.id)?'#D9A89B':'#CCD6D8'}`});
 if(b.height>=52){
  c.text(b.x+10,b.y+5,b.width-20,28,`${m.id}  ${m.name}`,20,ink,{bold:true});
  c.text(b.x+10,b.y+30,b.width-20,b.height-32,`${m.value} 指数`,20,col);
 }else{
  c.text(b.x+9,b.y+5,b.width-48,b.height-8,`${m.id} ${m.name}`,20,ink,{bold:true});
  c.text(b.x+b.width-44,b.y+5,34,b.height-8,String(m.value),20,col,{bold:true,align:'END'});
 }
}
c.line(48,1000,1552,1000,'#C5CECB',1);
c.circle(60,1031,6,blue);c.text(78,1017,380,31,'观测点  ·  标注含编号、名称与指数',20,ink);
c.circle(521,1031,6,accent);c.text(539,1017,290,31,'暖色标记为最高三点',20,ink);
c.text(953,1017,599,31,'引导线追溯原点  /  逻辑范围 x、y 均为 0–100',20,'#586B6E',{align:'END'});
const dsl=c.toString();
(async()=>{const r=await s.render('A20',dsl,{version_id:versionId,type:'visual',parent_version:'A20-v001',before_view_id:'A20-view-000001',changes:'简化8条自身回折共线短引线，保留24锚点/标签；y↑横向与100刻度分离。',width:1600,height:1100,stem:'annotated-map',purpose:'24 exact mapped markers and audited direct label leaders'});console.log(JSON.stringify({id:r.id,ok:r.ok,error:r.error_summary,meta_path:r.meta_path,image_path:r.image_path,version_id:r.version_id}));})();
