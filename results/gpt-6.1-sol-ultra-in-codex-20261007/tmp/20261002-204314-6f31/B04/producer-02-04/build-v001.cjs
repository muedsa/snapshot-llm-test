'use strict';
const fs=require('fs');const path=require('path');const {Canvas}=require('../../_suite/dsl.cjs');
const dir=__dirname;const started=new Date().toISOString();
const FONT='Inter,Noto Sans CJK SC';
function writeNew(name,data){const f=path.join(dir,name);fs.writeFileSync(f,data,{flag:'wx'});return f;}
function save(id,c,meta){let now=new Date().toISOString();writeNew(id+'-v001.snapshot',c.toString());writeNew(id+'-metadata-v001.json',JSON.stringify({case_id:id,...meta,dimensions:{width:c.width,height:c.height},creative_started_at:started,created_at:now,supporting_assets:[],render_status:'unrendered; root will render and visually review',checks:{factual_source_read:true,arithmetic_checked:true,visual_review_passed:null},documentation_reuse:['shared guide','parser Container/Text/Stack/Positioned/Transform','fonts Inter,Noto Sans CJK SC']},null,2)+'\n');}
function moduleIcon(c,x,y,w,h,color){c.rect(x,y,w,h,color,{radius:12,border:'2 SOLID #192F40'});c.rect(x-10,y+h*.28,10,h*.44,'#A4B4BE');c.rect(x+w,y+h*.28,10,h*.44,'#A4B4BE');for(let i=1;i<4;i++)c.line(x+w*i/4,y+4,x+w*i/4,y+h-4,'#192F4060',2);c.circle(x+w*.5,y+h*.5,h*.18,'#EAF0EC',{border:'2 SOLID #192F40'});}
function person(c,x,y,col,s=1){c.circle(x,y,12*s,col);c.line(x,y+17*s,x,y+53*s,col,9*s,{roundCaps:true});c.line(x,y+30*s,x-23*s,y+40*s,col,7*s,{roundCaps:true});c.line(x,y+30*s,x+23*s,y+40*s,col,7*s,{roundCaps:true});c.line(x,y+51*s,x-18*s,y+80*s,col,7*s,{roundCaps:true});c.line(x,y+51*s,x+18*s,y+80*s,col,7*s,{roundCaps:true});}
// 02: Historical narrative; spacing represents order, not elapsed time.
{
const c=new Canvas(1800,1080,{background:'#F5F0E6',font:FONT});const ink='#192F40',orange='#D76035',blue='#346E8B';
c.rect(0,0,1800,16,orange);c.text(72,50,1500,38,'环绕地球的日常   /   ISS 视觉特辑 02',24,ink,{bold:true,letterSpacing:1});
c.text(72,106,1560,95,'先连接，再常驻',76,ink,{bold:true});c.text(77,218,1550,58,'空间站不是一次升空的房子。它从两个在轨模块，逐步成为长期居住的地方。',27,ink);
c.line(92,310,1708,310,ink,2);c.text(93,329,1550,40,'四个早期节点    ·    1998—2000    ·    按事件顺序排布，间距不代表时间长度',23,ink);
const xs=[122,522,922,1322],w=356;
c.line(155,663,1650,663,'#B7B5A8',4);c.arrow(1640,663,1690,663,ink,4,{headLength:18});
// Separate, unconnected Zarya.
moduleIcon(c,178,435,220,84,'#CFDBD9');c.rect(226,389,42,46,'#346E8B');c.rect(302,389,42,46,'#346E8B');c.line(235,412,335,412,'#E8F1F4',2);
// Unity packaged with its mating adapters, not falsely connected yet.
moduleIcon(c,598,437,190,84,'#EDBE91');c.rect(644,410,97,27,'#EDBE91',{radius:8,border:'2 SOLID #192F40'});c.line(600,554,785,554,orange,3);c.text(579,571,240,40,'发射 ≠ 连接',21,orange,{bold:true,align:'CENTER'});
// Docked simplified pair.
moduleIcon(c,952,435,126,84,'#CFDBD9');moduleIcon(c,1100,435,126,84,'#EDBE91');c.rect(1078,461,22,32,ink);c.circle(1089,552,14,orange);c.line(1089,527,1089,536,orange,2);c.text(962,576,255,40,'两模块在轨相接',21,ink,{bold:true,align:'CENTER'});
// Long-duration crew, arbitrary three-person composition reflects Expedition 1 trio.
c.rect(1359,413,271,176,'#DCE4DC',{radius:28,border:'2 SOLID #192F40'});person(c,1428,450,ink,.85);person(c,1497,443,blue,.95);person(c,1566,450,ink,.85);c.text(1385,563,220,40,'首批三名常驻乘员',20,ink,{align:'CENTER'});
const rows=[['01','1998.11.20','Zarya 发射','首个模块抵达轨道。','unity'],['02','1998 年 12 月','Unity 发射','奋进号把第二个模块送入太空。','unity'],['03','1998.12.06','首次连接','STS-88 乘组将 Unity 与 Zarya 连接。','unity'],['04','2000.11.02','第一远征队入驻','长期有人居住的阶段由此开始。','history']];
for(let i=0;i<4;i++){let x=xs[i];c.circle(x+178,663,13,i===2?orange:ink);c.text(x,702,w,44,rows[i][0]+'  /  '+rows[i][1],25,ink,{bold:true});c.text(x,759,w,55,rows[i][2],31,ink,{bold:true});c.text(x,823,w,96,rows[i][3],24,ink,{height:1.45});}
c.rect(72,949,1656,72,ink,{radius:10});c.text(95,964,1608,46,'阅读提示：连接是组装事件，入驻是居住事件；这四个节点并不代表全部建造过程。',25,'#F5F0E6');
c.text(75,1034,1605,30,'来源：NASA Unity Module；International Space Station（历史）  ·  资料读取 2026-10-06  ·  模块为概念图，非工程比例',17,ink);
save('case-02',c,{title:'先连接，再常驻',audience:'中学生、家庭与科学展览观众',use_context:'科学展览历史导读横幅，近读和课堂投影',user_goal:'分清首模块发射、第二模块发射、首次连接与首批常驻入驻四件不同事情',content_basis:{kind:'真实历史事实与原创概念图',facts:['Zarya发射1998-11-20','Unity发射1998年12月（来源页日期冲突，未采用具体发射日）','两模块连接1998-12-06','Expedition 1于2000-11-02到站'],limitations:['时间轴间距不比例','模块形状示意','四节点为编辑选择，非完整建造史']},source_ids:['unity','history'],visual_intent:'横向四帧历史卷轴，模块形态从单体、运输、连接到乘员居住的叙事变化；暖纸色与橙色强调关键组装事件',completion_criteria:['四个日期和事件分开且准确','不将Unity冲突发射日伪装为精确事实','时间间距示意声明清晰','文字无遮挡且四幅图各自成立','实际服务PNG查看后才判定完成']});
}
// 03: Precise lengths. Endpoints and bar lengths have exactly 8 px/m.
{
const c=new Canvas(1500,1120,{background:'#EAF0ED',font:FONT});const ink='#133A35',light='#70928A',gold='#BB693B',x0=246,scale=8;
c.rect(0,0,34,1120,ink);c.text(76,49,1300,35,'环绕地球的日常   /   ISS 视觉特辑 03',23,ink,{bold:true});
c.text(76,100,1280,103,'109米，究竟多长',72,ink,{bold:true});c.text(80,213,1280,45,'读长度，先对齐零点。下面三条标尺采用同一线性比例：8像素 = 1米。',25,ink);
c.rect(78,283,1350,471,'#F8FAF7',{radius:16,border:'1 SOLID #C5D6CD'});
const ys=[392,530,668],lengths=[109,80,67],colors=[ink,gold,light],labels=['ISS 太阳阵列翼展','Airbus A380 翼展','ISS 加压舱段主轴'];
for(let i=0;i<3;i++){let y=ys[i];c.text(102,y-17,130,75,labels[i],24,ink,{bold:i!==2,height:1.1});c.rect(x0,y,lengths[i]*scale,20,colors[i]);c.line(x0,y-18,x0,y+40,ink,2);c.line(x0+lengths[i]*scale,y-18,x0+lengths[i]*scale,y+40,colors[i],2);c.text(x0+lengths[i]*scale+16,y-24,192,68,String(lengths[i])+' m',42,colors[i],{bold:true});}
c.line(x0,321,x0,719,'#B0C3BB',1);for(let m=0;m<=110;m+=10){let xx=x0+m*scale;c.line(xx,719,xx,731,ink,2);c.text(xx-22,731,44,29,String(m),16,ink,{align:'CENTER'});}c.line(x0,719,x0+110*scale,719,ink,2);c.text(1172,723,155,34,'单位：米',19,ink);
c.text(92,798,475,40,'29米',44,gold,{bold:true});c.text(94,855,522,82,'两种翼展的差：109 − 80 = 29。\n空间站翼展约为 A380 的 1.36 倍。',24,ink,{height:1.3});
c.line(655,797,655,938,'#B5C5BD',2);c.text(694,797,640,45,'“长”必须说明量的是哪一轴',29,ink,{bold:true});c.text(696,855,639,91,'67米指加压舱段的主轴长度，\n不是109米太阳阵列翼展的另一种写法。',24,ink,{height:1.3});
c.rect(80,975,1347,66,ink,{radius:10});c.text(104,988,1299,45,'只比较一维长度；这里没有按面积、体积或质量绘制，更不是空间站与飞机的结构图。',23,'#F4F8F3');
c.text(84,1071,1320,27,'来源：NASA Station Facts（109m / 80m / 67m）  ·  读取 2026-10-06  ·  网页事实值，非实时测量  ·  1.36为四舍五入值',17,ink);
writeNew('case-03-geometry-v001.json',JSON.stringify({case_id:'case-03',units:'m',px_per_m:scale,origin_x:x0,bars:lengths.map((m,i)=>({label:labels[i],metres:m,start_x:x0,end_x:x0+m*scale,pixel_length:m*scale,y:ys[i]})),difference_m:109-80,exact_ratio:109/80,shown_ratio:1.36,verification:'Exact arithmetic checked in this script; final service PNG remains to be visually inspected'},null,2)+'\n');
save('case-03',c,{title:'109米，究竟多长',audience:'中学生、亲子科学读者',use_context:'科学馆尺寸解读展板，印刷或平板近读',user_goal:'使用一致零点和同一线性尺度比较ISS翼展、A380翼展，区分翼展和加压舱段主轴',content_basis:{kind:'真实尺寸事实与派生计算',facts:{iss_solar_array_wingspan_m:109,airbus_a380_wingspan_m:80,iss_pressurized_module_major_axis_m:67},calculations:{difference_m:29,ratio_exact:1.3625,ratio_display:1.36,px_per_m:8},limitations:['只显示一维长度，不显示物体轮廓、面积、体积或质量','来源网页尺寸口径，不宣称当前实时测量']},source_ids:['facts'],visual_intent:'统一零点的三条精确线性标尺，以留白与材料色把一维测量从工程轮廓误解中分离；低部展开比较逻辑',completion_criteria:['109/80/67m长度分别为872/640/536px','三条共用x=246零点','区分翼展和舱段主轴','显示29m与约1.36倍派生值','文字清晰且单位和限制显著','真实PNG实际查看后完成']});
}
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
const a=-.85,sx=cx+Math.cos(a)*ro,sy=cy+Math.sin(a)*ro;c.rect(sx-31,sy-18,62,36,'#D5E2E8',{radius:5});c.rect(sx-70,sy-32,32,65,gold);c.rect(sx+38,sy-32,32,65,gold);c.line(sx-39,sy,sx+39,sy,pale,3);c.arrow(sx-38,sy+45,cx+150,cy-154,mint,5,{headLength:17});c.arrow(sx+55,sy+10,sx+132,sy+83,gold,5,{headLength:17});
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
writeNew('production-notes-v001.json',JSON.stringify({task_id:'B04',producer:'/root/b04_cases_02_04',time:started,source_reads:['TASK.md','AGENTS.md','task.json','run-config.json','inputs/README.md','editorial-plan-v001.json','research/unity-readable-v001.txt','research/history-readable-v001.txt','research/facts-readable-v001.txt','research/microgravity-readable-v001.txt'],shared_document_reuse:['shared-doc-000001-response.txt','shared-doc-000004-readable.txt','shared-fonts-000001-response.txt','dsl-README.md'],new_http_requests:0,images_viewed:0,local_errors:[{type:'wrong input path',attempt:'tasks/B04-research-visual-feature/inputs/README.md',recovered_by:'read source-evidence/read-000001/inputs/README.md'}],files:['case-02-v001.snapshot','case-03-v001.snapshot','case-04-v001.snapshot'],status:'Candidate DSL only; no claim of rendered quality'},null,2)+'\n');
console.log(JSON.stringify({started,dir,cases:['case-02','case-03','case-04']}));
