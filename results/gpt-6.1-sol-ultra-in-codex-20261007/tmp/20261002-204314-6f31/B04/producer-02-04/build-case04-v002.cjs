'use strict';
const fs=require('fs');const path=require('path');const {Canvas}=require('../../_suite/dsl.cjs');
const dir=__dirname;const started=new Date().toISOString();
const FONT='Inter,Noto Sans CJK SC';
function writeNew(name,data){const f=path.join(dir,name);fs.writeFileSync(f,data,{flag:'wx'});return f;}
function save(id,c,meta){let now=new Date().toISOString();writeNew(id+'-v002.snapshot',c.toString());writeNew(id+'-metadata-v002.json',JSON.stringify({case_id:id,...meta,dimensions:{width:c.width,height:c.height},creative_started_at:started,created_at:now,supporting_assets:[],render_status:'unrendered; root will render and visually review',checks:{factual_source_read:true,arithmetic_checked:true,visual_review_passed:null},documentation_reuse:['shared guide','parser Container/Text/Stack/Positioned/Transform','fonts Inter,Noto Sans CJK SC']},null,2)+'\n');}
function moduleIcon(c,x,y,w,h,color){c.rect(x,y,w,h,color,{radius:12,border:'2 SOLID #192F40'});c.rect(x-10,y+h*.28,10,h*.44,'#A4B4BE');c.rect(x+w,y+h*.28,10,h*.44,'#A4B4BE');for(let i=1;i<4;i++)c.line(x+w*i/4,y+4,x+w*i/4,y+h-4,'#192F4060',2);c.circle(x+w*.5,y+h*.5,h*.18,'#EAF0EC',{border:'2 SOLID #192F40'});}
function person(c,x,y,col,s=1){c.circle(x,y,12*s,col);c.line(x,y+17*s,x,y+53*s,col,9*s,{roundCaps:true});c.line(x,y+30*s,x-23*s,y+40*s,col,7*s,{roundCaps:true});c.line(x,y+30*s,x+23*s,y+40*s,col,7*s,{roundCaps:true});c.line(x,y+51*s,x-18*s,y+80*s,col,7*s,{roundCaps:true});c.line(x,y+51*s,x+18*s,y+80*s,col,7*s,{roundCaps:true});}
// 04: Newton-style continuous fall and a shared-fall interior explanation.
{
const c=new Canvas(1400,1500,{background:'#0E2540',font:FONT});const pale='#E4F2F4',mint='#82D2BE',gold='#F5BD74';
for(let i=0;i<76;i++){let xx=55+((i*177)%1290),yy=325+((i*107)%531);c.circle(xx,yy,i%7===0?2.4:1.1,'#BDD9E94D');}
c.text(63,46,1250,35,'环绕地球的日常   /   ISS 视觉特辑 04',23,mint,{bold:true});c.text(63,98,1260,92,'一起下落，为什么漂浮',66,pale,{bold:true});
c.text(68,210,1240,74,'引力仍在拉住空间站；空间站、乘员和舱内物体一起绕着地球自由下落。',29,pale,{height:1.25});
// Orbit is a visual model, not a scale or altitude diagram.
const cx=412,cy=591,r=179,ro=268;const pts=[];for(let i=0;i<=130;i++){const a=2*Math.PI*i/130;pts.push([cx+Math.cos(a)*ro,cy+Math.sin(a)*ro]);}c.polyline(pts,'#5B7F9866',3);c.circle(cx,cy,r,'#19465D');c.circle(cx,cy,r-13,'#286D74');
// Meridians and parallels use exact sampled lines as an illustrative globe.
for(let f of [.35,.70]){let p=[];for(let i=0;i<=60;i++){let a=2*Math.PI*i/60;p.push([cx+Math.cos(a)*r*f,cy+Math.sin(a)*r*.93]);}c.polyline(p,'#8ECCC345',2);}for(let yoff of [-70,0,70]){let half=Math.sqrt(r*r-yoff*yoff);c.line(cx-half+13,cy+yoff,cx+half-13,cy+yoff,'#8ECCC345',2);}c.text(cx-80,cy-25,160,52,'地球',35,pale,{bold:true,align:'CENTER'});
const a=-.85,sx=cx+Math.cos(a)*ro,sy=cy+Math.sin(a)*ro;c.rect(sx-31,sy-18,62,36,'#D5E2E8',{radius:5});c.rect(sx-70,sy-32,32,65,gold);c.rect(sx+38,sy-32,32,65,gold);c.line(sx-39,sy,sx+39,sy,pale,3);c.arrow(sx-38,sy+45,cx+108,cy-123,mint,5,{headLength:17});c.arrow(sx+55,sy+10,sx+132,sy+83,gold,5,{headLength:17});
c.text(677,383,189,38,'向前运动',21,gold,{bold:true});c.text(533,488,165,72,'引力拉向\n地球中心',21,mint,{height:1.2});
c.text(758,345,565,54,'轨道，是连续的自由落体',32,pale,{bold:true});c.text(758,419,563,138,'物体有足够的横向速度时，\n它不断下落，也不断绕过地球。\n这不是摆脱引力。',26,pale,{height:1.45});
c.rect(760,617,564,179,'#183D57',{radius:18,border:'1 SOLID #56869B'});c.text(790,637,505,48,'88.8%',45,gold,{bold:true});c.text(790,701,505,78,'NASA示例：距地表约250英里处，\n引力强度仍约为地表的88.8%。',23,pale,{height:1.4});
c.text(68,878,1242,47,'同一舱内：人、苹果、空间站一起下落',33,pale,{bold:true});
c.rect(64,949,762,334,'#E4F2F4',{radius:26});c.rect(92,975,706,244,'#18415A',{radius:21,border:'3 SOLID #6BB7B6'});c.line(94,1088,795,1088,'#3A6480',2);person(c,276,1023,pale,1.38);c.circle(539,1055,31,gold);c.line(539,1027,548,1013,mint,7,{roundCaps:true});c.line(250,1167,315,1167,mint,6);c.rect(220,1174,126,18,'#50868C',{radius:8});
c.arrow(277,1106,277,1150,mint,4,{headLength:13});c.arrow(540,1106,540,1150,mint,4,{headLength:13});c.arrow(724,1045,724,1150,mint,4,{headLength:13});c.text(137,1230,623,40,'绿色箭头：共同下落的方向（概念示意）',21,'#133C4C',{align:'CENTER'});
c.text(875,963,438,48,'为什么看起来“浮着”？',29,mint,{bold:true});c.text(877,1031,438,157,'因为人与周围舱体共同下落，\n物体不会像地面上的苹果那样\n迅速落到脚下。\n这种环境称为微重力。',25,pale,{height:1.4});
c.rect(63,1331,1273,79,'#F5BD74',{radius:12});c.text(85,1347,1229,50,'质量仍在，引力仍在。改变的是共同自由下落时，相对于舱体的运动与支撑感。',25,'#172F41',{bold:true});
c.text(67,1437,1250,42,'来源：NASA What is Microgravity?（2009） ·  读取 2026-10-06  ·  轨道、物体、箭头均非比例；88.8%只用于约250英里示例',17,'#C1D9E3');
save('case-04',c,{title:'一起下落，为什么漂浮',audience:'中学生、家庭与科学展览观众',use_context:'基础物理展板或课堂讲解，完整图近读',user_goal:'解释为什么轨道中的漂浮不是没有引力，而是空间站、乘员与物体共同自由下落',content_basis:{kind:'NASA原理说明与原创概念图',facts:['约250英里距地表处，引力强度约为地表88.8%','轨道可解释为横向运动与持续自由下落','空间站、乘员和舱内物体共同下落，使物体显得漂浮','质量不因进入轨道而消失'],limitations:['88.8%不是任意ISS高度的固定实时值','图示轨道、高度、物体尺寸、箭头均非工程比例','微重力不等于完全无引力','未展示扰动和残余加速度的详细量化']},source_ids:['microgravity'],visual_intent:'上半幅地球和轨道的宇宙视角，下半幅舱体剖面的共同下落视角；金色表示前向运动/苹果，绿色表示引力与共同下落',completion_criteria:['图文明确微重力与无引力不同','250英里与88.8%成对限定','轨道速度切线箭头和向地球中心箭头易分','舱内三箭头共同方向','声明概念图非比例','实际服务PNG看图后判断完整']});
}
