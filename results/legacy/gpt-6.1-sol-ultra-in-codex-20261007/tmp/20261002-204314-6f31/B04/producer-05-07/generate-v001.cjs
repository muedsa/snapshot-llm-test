const fs=require('node:fs'),path=require('node:path');
const {Canvas,tag,matrix2d}=require('../../_suite/dsl.cjs');
const OUT=__dirname,started='2026-10-06T10:58:38Z';
function save(id,c,meta){fs.mkdirSync(OUT,{recursive:true});const stem=path.join(OUT,id+'-v001');fs.writeFileSync(stem+'.snapshot',c.toString(),{flag:'wx'});fs.writeFileSync(path.join(OUT,id+'-metadata-v001.json'),JSON.stringify({case_id:id,creative_started_at:started,creative_started_at_source:'clock tool at actual production start',created_at:new Date().toISOString(),dimensions:[c.width,c.height],checks:{visual_verified:false,service_request_by_this_agent:false,visual_review_owner:'root',static_geometry:'constructed within declared canvas'},supporting_assets:[],...meta},null,2),{flag:'wx'});}
function outline(c,x,y,r,color,width=2){c.circle(x,y,r,'transparent',{border:width+' SOLID '+color});}
function arc(c,cx,cy,r,a,b,color,width=2){const pts=[];for(let i=0;i<=Math.ceil((b-a)*32);i++){const t=a+(b-a)*i/Math.ceil((b-a)*32);pts.push([cx+r*Math.cos(t),cy+r*Math.sin(t)]);}c.polyline(pts,color,width);}
function footer(c,y,source,limitation,color='#57717E'){c.line(64,y,c.width-64,y,color,1);c.text(64,y+20,c.width-128,40,source,18,color);c.text(64,y+57,c.width-128,58,limitation,18,color);}
// 05: numbered event calendar, deliberately not a geographic orbit diagram.
{
 const c=new Canvas(1400,1500,{background:'#11192D'}),cream='#FFF2DC',gold='#FFBD68',faint='#65728E';
 c.text(64,42,1272,38,'环绕地球的日常  /  ISS 公众科学特辑  05',20,'#AAB8D0',{letterSpacing:2});
 c.text(64,108,1272,86,'一天里的16次日出',66,cream,{bold:true});
 c.text(68,210,1232,80,'地面的一昼夜，在空间站变成反复出现的晨光。\n沿编号读一圈：这是事件计数，不是实时光照时刻表。',25,'#C9D2E3',{lineHeight:1.4});
 const cx=700,cy=755,r=413;
 outline(c,cx,cy,r,'#3C4964',2);outline(c,cx,cy,r-65,'#293750',1);
 for(let i=0;i<16;i++){
  const a=-Math.PI/2+i*2*Math.PI/16,x=cx+r*Math.cos(a),y=cy+r*Math.sin(a);
  c.circle(x,y,53,'#192540',{border:'1 SOLID #46506B'});
  c.circle(x,y-5,21,gold);
  c.rect(x-24,y-4,48,24,'#192540');
  c.line(x-34,y-3,x+34,y-3,gold,2);
  for(let j=0;j<5;j++){const t=Math.PI+0.2+j*(Math.PI-0.4)/4;c.line(x+27*Math.cos(t),y-5+27*Math.sin(t),x+33*Math.cos(t),y-5+33*Math.sin(t),gold,2);}
  c.text(x-34,y+8,68,33,String(i+1).padStart(2,'0'),22,cream,{bold:true,align:'CENTER'});
 }
 c.circle(cx,cy,260,'#1B2A48',{border:'1 SOLID #586989',gradientType:'RADIAL',gradientColors:'#314466,#152039',gradientRadius:0.7});
 c.text(450,582,500,42,'每 24 小时',28,'#B5C5DF',{align:'CENTER'});
 c.text(450,635,500,182,'≈16',142,cream,{bold:true,align:'CENTER'});
 c.text(455,842,490,44,'次日出，也有约16次日落',26,cream,{align:'CENTER'});
 c.line(553,925,847,925,'#697B98',1);
 c.text(478,954,444,47,'每圈约90分钟',28,gold,{bold:true,align:'CENTER'});
 c.rect(64,1242,1272,108,'#263651',{radius:18});
 c.text(91,1261,1218,74,'读图提示  ·  16个晨光图标按顺序编号；等角排布只是版式。\n实际轨道与日照会变化，图中没有指定昼夜各45分钟。',22,'#E3EAF4',{lineHeight:1.45});
 footer(c,1380,'资料：NASA Station Facts；Spot the Station FAQ（2025-05-06）。访问：2026-10-06。','≈表示科普近似。此图为编辑性事件环历，不用于过境预测或任务调度。','#A4B2CA');
 save('case-05',c,{title:'一天里的16次日出',audience:'中学生、家庭和科学展览观众',use_context:'科学展厅竖版近读海报或大型平板，先数事件再讨论一天的含义',user_goal:'数出16次晨光，理解24小时与约90分钟一圈的关系，同时辨认示意与实时数据的区别',content_basis:{type:'researched_editorial',facts:['NASA事实页称24小时16圈并经历16次日出日落','NASA 2025 FAQ称每90分钟一圈，乘员每天见16次日出日落'],editorial_explanation:'等角编号是一种事件计数排版，未表现真实轨道或每段日照时长',uncertainty:'约数；未查询实时轨道或光照'},source_ids:['facts','sighting'],visual_intent:'暗夜底上的16个金色晨光印记组成计数环历，中央数字与周期构成节奏而非工程轨迹',completion_criteria:['16个独立日出图标与01–16完整编号','明确24小时、约16日出日落、约90分钟一圈','等角排布明确只是版式，无固定45/45昼夜主张','底部有NASA短来源、访问日期与示意限制'],algorithm:{sunrise_icons:16,angles_degrees:Array.from({length:16},(_,i)=>-90+i*22.5),sunrise_count_is_approximate:true}});
}
// 06: two separate representations: exactly 100 equal mass units, then unquantified process.
{
 const c=new Canvas(1700,1500,{background:'#EDF5F2'}),ink='#153A3A',teal='#008D85',orange='#D46943',muted='#436563';
 c.text(64,38,1572,34,'环绕地球的日常  /  ISS 公众科学特辑  06',20,muted,{letterSpacing:2});
 c.text(64,101,1572,87,'把98份水找回来',65,ink,{bold:true});
 c.text(68,210,1564,78,'2023年6月20日，NASA报道：空间站ECLSS技术演示达到98%总水回收。\n这是当时的系统里程碑；不是全站在所有条件下都能永久保持的保证。',25,muted,{lineHeight:1.4});
 c.rect(64,330,1572,330,'#FFFFFF',{radius:24,border:'1 SOLID #C6DCD4'});
 c.text(88,352,750,39,'质量标尺  ·  收集到的水 = 100单位',25,ink,{bold:true});
 for(let i=0;i<100;i++){const x=96+(i%25)*25,y=416+Math.floor(i/25)*41;c.rect(x,y,20,33,i<98?teal:orange,{radius:4});}
 c.text(88,596,820,37,'每格同一质量单位；98格回收，2格损失。',22,muted);
 c.text(855,368,500,140,'98%',102,teal,{bold:true});
 c.text(864,520,680,41,'回收 98 单位  /  损失 2 单位',30,ink,{bold:true});
 c.text(864,583,680,41,'图示的分母是所收集的水，不是各支路的水量。',21,muted);
 c.text(64,698,1568,42,'处理路线  ·  箭头只表示去向，不按流量定宽',27,ink,{bold:true});
 // Humidity route; WPA receives all collected water.
 c.rect(64,786,250,122,'#DDEBE5',{radius:14});c.text(84,805,210,80,'呼吸与汗\n释放的湿气',25,ink,{bold:true,lineHeight:1.35});
 c.rect(388,786,276,122,'#DDEBE5',{radius:14});c.text(410,805,230,80,'除湿设备\n捕集空气中的水',24,ink,{lineHeight:1.35});
 c.arrow(314,847,380,847,teal,3);c.arrow(664,847,833,847,teal,3);
 c.rect(64,995,250,123,'#DDEBE5',{radius:14});c.text(84,1019,210,70,'尿液',29,ink,{bold:true});
 c.rect(388,982,276,155,'#DDEBE5',{radius:14});c.text(410,1001,230,105,'UPA\n真空蒸馏\n得到水与含水卤水',24,ink,{lineHeight:1.3});
 c.arrow(314,1055,380,1055,teal,3);
 c.polyline([[664,1043],[751,1043],[751,886],[835,886]],teal,3);c.arrow(793,886,834,886,teal,3);c.text(684,961,124,32,'蒸馏出的水',19,muted);
 c.arrow(527,1137,527,1200,teal,3);c.text(555,1147,173,39,'仍含水的卤水',19,muted);
 c.rect(388,1207,276,131,'#DDEBE5',{radius:14});c.text(410,1224,232,94,'BPA\n膜处理＋暖干空气\n使剩余水蒸发',23,ink,{lineHeight:1.3});
 c.polyline([[664,1267],[790,1267],[790,908],[838,908]],teal,3);c.arrow(807,908,838,908,teal,3);c.text(686,1298,210,65,'成为湿空气\n再由收集系统捕集',19,muted,{lineHeight:1.35});
 c.rect(847,786,232,170,'#C5E0D7',{radius:14});c.text(869,814,188,102,'收集的水\n汇入处理系统',26,ink,{bold:true,lineHeight:1.4});
 c.arrow(1079,868,1146,868,teal,3);
 c.rect(1155,786,481,322,'#173F3D',{radius:24});c.text(1184,809,423,45,'WPA · 水处理组件',31,'#E7FFF6',{bold:true});
 c.text(1184,877,423,164,'1  专用过滤器\n2  催化反应器分解残留污染物\n3  传感器检查纯度\n4  合格水加碘抑制微生物',23,'#D4EFE5',{lineHeight:1.65});
 c.polyline([[1284,1108],[1284,1160],[1167,1160],[1167,1108]],orange,3);c.arrow(1167,1142,1167,1108,orange,3);c.text(1148,1184,459,38,'未达到纯度要求 → 再处理',22,orange,{bold:true});
 c.arrow(1458,1108,1458,1245,teal,3);
 c.rect(1258,1254,378,84,'#C5E0D7',{radius:14});c.text(1276,1274,342,49,'合格水储存，供乘员使用',23,ink,{bold:true,align:'CENTER'});
 footer(c,1385,'资料：NASA《Water Recovery Milestone》（2023-06-20；页面后续更新2026-03-02）。访问：2026-10-06。','事实：技术演示达到98%。编辑示意：100等质量单位与不含支路数据的流程；没有表示尿液可直接饮用。',muted);
 save('case-06',c,{title:'把98份水找回来',audience:'中学生、家庭与科学馆公众',use_context:'科学馆水循环展板，横向桌面屏或放大查看；从质量标尺进入设备处理路线',user_goal:'准确说明98%的分母和2023演示时点，追踪水如何经历收集、蒸馏、回收、过滤与纯度检验',content_basis:{type:'researched_editorial',fact:'NASA 2023-06-20文章报道ECLSS达到98%总水回收，并以收集100磅损失2磅说明分母',fact_process:['呼吸汗湿气被除湿捕集','UPA以真空蒸馏回收尿液的水，产生仍含水的卤水','BPA膜处理与暖干空气使卤水水分蒸发成湿空气，再收集','所有收集水经过WPA过滤和催化反应器、纯度检测；不合格再处理；合格加碘并储存'],editorial_demo:'100等质量单位是比例演示，流程无支路数值；不提供当前连续运行保证'},source_ids:['water'],visual_intent:'一百个等质量短柱构成准确的98/2标尺，下方把未定量的处理路线与数量清楚分离',completion_criteria:['100格面积一致，98青绿＋2橙色','分母所收集的水与历史报道日期写清','UPA/BPA/WPA路线符合原文','所有流程箭头无虚构支路数据，处理与量值分开','未达纯度要求再处理与合格水储存完整'],mass_scale:{total_units:100,recovered_units:98,lost_units:2,grid_columns:25,grid_rows:4,unit_width:20,unit_height:33,flow_width_encodes_quantity:false}});
}
// 07: different equipment silhouettes and roles, not a workout prescription.
{
 const c=new Canvas(1700,1450,{background:'#F4EFE5'}),ink='#232D31',muted='#5F6D71',red='#BF5744',blue='#477D92',gold='#B78935';
 c.text(64,37,1572,35,'环绕地球的日常  /  ISS 公众科学特辑  07',20,muted,{letterSpacing:2});
 c.text(64,100,1572,88,'漂浮之后，身体仍要用力',60,ink,{bold:true});
 c.text(68,211,1490,73,'微重力会让骨骼与肌肉面临流失。空间站把阻力、跑步与骑行带上轨道，\n研究怎样减轻这些变化；设备和运动方案仍在持续改进。',25,muted,{lineHeight:1.4});
 const xs=[64,600,1136],colors=[red,blue,gold],names=['ARED','T2','CEVIS'],kinds=['阻力训练','第二代跑步机','自行车测功设备'];
 for(let i=0;i<3;i++){
  c.rect(xs[i],337,500,658,'#FFFCF4',{radius:24,border:'1 SOLID #D9D7CA'});
  c.rect(xs[i]+24,360,72,7,colors[i],{radius:3});c.text(xs[i]+24,392,448,60,names[i],44,colors[i],{bold:true});c.text(xs[i]+24,468,448,40,kinds[i],26,ink,{bold:true});
  c.line(xs[i]+24,878,xs[i]+476,878,'#D9D7CA',1);
 }
 // ARED: loading concept, piston and flywheel; no loose gravity weights.
 {const x=64;c.rect(x+92,550,18,267,'#9B6D5F',{radius:5});c.rect(x+368,550,18,267,'#9B6D5F',{radius:5});c.rect(x+87,548,304,18,'#9B6D5F',{radius:5});c.rect(x+76,815,324,18,red,{radius:6});c.line(x+125,640,x+350,640,red,11,{roundCaps:true});c.circle(x+250,593,25,'#E5B893');c.line(x+250,625,x+250,709,ink,14,{roundCaps:true});c.polyline([[x+250,641],[x+210,674],[x+158,640]],ink,10,{roundCaps:true});c.polyline([[x+250,641],[x+290,674],[x+332,640]],ink,10,{roundCaps:true});c.polyline([[x+250,707],[x+210,758],[x+208,810]],ink,12,{roundCaps:true});c.polyline([[x+250,707],[x+297,758],[x+300,810]],ink,12,{roundCaps:true});c.rect(x+370,667,48,100,'#DCB6A8',{radius:10,border:'2 SOLID #A97966'});c.line(x+394,646,x+394,705,red,8);outline(c,x+394,798,25,red,6);c.text(x+24,902,450,70,'活塞与飞轮提供负荷，\n在失重中模拟举重。',23,ink,{lineHeight:1.45});}
 // T2: runner and a strong horizontal belt silhouette.
 {const x=600;c.rect(x+94,789,334,44,'#C1D5DA',{radius:14,border:'2 SOLID #7C9BA7'});c.rect(x+108,787,306,12,blue,{radius:6});for(let k=0;k<8;k++)c.line(x+128+k*35,793,x+145+k*35,803,'#7299A8',2);c.line(x+368,786,x+342,573,blue,13,{roundCaps:true});c.rect(x+307,554,104,58,'#2D5466',{radius:12});c.rect(x+321,568,66,18,'#A3CCCB',{radius:4});c.circle(x+232,585,25,'#E5B893');c.line(x+230,618,x+258,689,ink,13,{roundCaps:true});c.polyline([[x+239,641],[x+205,672],[x+183,644]],ink,10,{roundCaps:true});c.polyline([[x+239,641],[x+283,612],[x+303,635]],ink,10,{roundCaps:true});c.polyline([[x+258,689],[x+220,733],[x+192,782]],ink,12,{roundCaps:true});c.polyline([[x+258,689],[x+307,724],[x+346,710]],ink,12,{roundCaps:true});c.text(x+24,902,450,70,'跑步机让乘员在舱内\n进行跑步运动。',23,ink,{lineHeight:1.45});}
 // CEVIS: fixed-frame pedal machine, no saddle or conventional bicycle wheels.
 {const x=1136;c.rect(x+146,802,245,22,gold,{radius:8});c.line(x+160,802,x+195,676,'#9D844D',13,{roundCaps:true});c.line(x+195,676,x+346,676,'#9D844D',13,{roundCaps:true});c.line(x+346,676,x+372,803,'#9D844D',13,{roundCaps:true});outline(c,x+261,737,55,gold,10);c.line(x+228,733,x+294,743,gold,7);c.rect(x+207,725,37,15,ink,{radius:6});c.rect(x+280,739,37,15,ink,{radius:6});c.circle(x+214,559,25,'#E5B893');c.line(x+217,591,x+251,655,ink,13,{roundCaps:true});c.polyline([[x+228,615],[x+271,639],[x+331,611]],ink,10,{roundCaps:true});c.line(x+332,611,x+346,673,gold,9,{roundCaps:true});c.polyline([[x+251,655],[x+215,691],[x+226,730]],ink,12,{roundCaps:true});c.polyline([[x+251,655],[x+299,684],[x+298,744]],ink,12,{roundCaps:true});c.rect(x+353,575,86,67,'#5A543D',{radius:10});c.rect(x+365,586,62,27,'#DBCF9E',{radius:5});c.text(x+24,902,450,70,'计算机控制阻力，\n维持准确的骑行负荷。',23,ink,{lineHeight:1.45});}
 c.rect(64,1051,1572,224,'#273A40',{radius:24});
 c.text(92,1074,386,80,'平均约2小时/日',37,'#E7D7AF',{bold:true});
 c.text(92,1170,386,66,'2024-05-20 NASA综述\n描述的当时乘员平均值',21,'#CBD6D7',{lineHeight:1.4});
 c.line(520,1080,520,1249,'#577075',1);
 c.text(560,1080,1028,53,'运动能缓解变化，个体结果仍会不同。',31,'#FCF7EC',{bold:true});
 c.text(560,1147,1028,102,'图中的三种设备是器材艺术示意，不按工程比例。\n“2小时”用于理解空间生活，不是个人训练处方或健康保证。',24,'#CBD6D7',{lineHeight:1.5});
 footer(c,1315,'资料：NASA《Astronaut Exercise》（2024-05-20），访问：2026-10-06。','此图整理NASA综述，未逐篇复核其引用论文；未来长任务的设备与方案仍需研究。',muted);
 save('case-07',c,{title:'漂浮之后，身体仍要用力',audience:'中学生、家庭与科学馆观众',use_context:'学校科学课堂或展览横向设备图鉴，近读时比较阻力/跑步/骑行三种运动方式',user_goal:'辨认ARED、T2、CEVIS及其作用，理解平均2小时/日是2024综述的历史描述，个体结果有差异',content_basis:{type:'researched_editorial',facts:['NASA 2024-05-20综述列出ARED/T2/CEVIS并称当时乘员平均每日2小时运动','ARED活塞与飞轮提供模拟举重负荷','CEVIS计算机控制摩擦和阻力维持准确负荷','运动对肌肉骨骼变化可起调节作用，个体结果不同且未来长任务仍有局限'],editorial_demo:'三设备与人物由DSL艺术示意，不呈现工程比例或具体训练处方',limits:'只读NASA综述，未逐篇阅读参考论文，不给出医学保证'},source_ids:['exercise'],visual_intent:'暖纸色的三幅设备图鉴把阻力机、跑步机与固定架踏车画成不同轮廓，底部将历史均值和局限并列呈现',completion_criteria:['三种不同设备轮廓和ARED/T2/CEVIS清楚标识','2024-05-20与当时平均约2小时/日写清','ARED活塞飞轮、T2跑步、CEVIS控制阻力角色准确','器材不按比例、非训练处方、个体差异与未来研究限制完整'],equipment_count:3});
}
fs.writeFileSync(path.join(OUT,'source-application-v001.json'),JSON.stringify({task_id:'B04',producer:'05-07',read_completed_at:new Date().toISOString(),sources_read:['source-evidence/read-000001/command-output.txt','editorial-plan-v001.json','research/facts-readable-v001.txt','research/sighting-readable-v001.txt','research/water-readable-v001.txt','research/exercise-readable-v001.txt'],shared_reused:['shared-doc-000001-response.txt','shared-doc-000004-readable.txt: Snapshot/Container/Stack/Positioned/Opacity/Transform/Text/Raw sections','shared-fonts-000001-readable.txt: Inter,Noto Sans CJK SC','dsl-README.md','dsl.cjs'],new_http_requests:0,visual_review:'Root will render and actually open candidate images; producer makes no quality-pass claim'},null,2),{flag:'wx'});
console.log(JSON.stringify({generated:['case-05','case-06','case-07'],directory:OUT}));
