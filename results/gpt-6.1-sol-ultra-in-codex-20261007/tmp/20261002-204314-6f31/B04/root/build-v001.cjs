const fs=require('node:fs'),path=require('node:path'),{Canvas,tag,position}=require('../../_suite/dsl.cjs'),s=require('../../_suite/suite.cjs');
const dir=__dirname,started=new Date().toISOString(),navy='#101E30',ink='#172B3D',muted='#506374',paper='#F3F1E9',blue='#6AC5F0',orange='#F4AC62',mint='#B2DBC4';
const write=(f,v)=>fs.writeFileSync(path.join(dir,f),v,{flag:'wx'}),J=x=>JSON.stringify(x,null,2)+'\n';
function text(c,x,y,w,h,t,z=24,col=ink,bold=false){c.text(x,y,w,h,t,z,col,{bold});}
function stars(c,w,h){for(let i=0;i<72;i++){const x=(i*239+31)%w,y=(i*137+51)%h;c.circle(x,y,i%8===0?2:1,'#C2D9E0',{opacity:.45});}}
function ring(c,cx,cy,r,col,lw=2,a0=0,a1=2*Math.PI){const p=[];for(let i=0;i<=90;i++){const a=a0+(a1-a0)*i/90;p.push([cx+r*Math.cos(a),cy+r*Math.sin(a)]);}c.polyline(p,col,lw);}
function head(c,id,w,title,sub,dark=false){const col=dark?'#F8F7F0':ink;text(c,64,42,w-128,32,'环绕地球的日常   /   ISS 视觉特辑   /   '+id,20,dark?blue:muted);text(c,64,92,w-128,95,title,56,col,true);text(c,64,194,w-128,60,sub,24,dark?'#C5D5E0':muted);}
function footer(c,w,h,src,dark=false){c.line(64,h-92,w-64,h-92,dark?'#405163':'#B9C1C2',1);text(c,64,h-73,w-128,48,src+'  ·  独立编辑科普，非NASA官方设计',17,dark?'#B3C5D0':muted);}
function save(id,c,info){write(id+'-v001.snapshot',c.toString());const m={id,...info,dimensions:[c.width,c.height],creative_started_at:started,creative_start_scope:'B04 root design construction',created_at:new Date().toISOString(),supporting_assets:[],completion_criteria:info.completion_criteria??['内容自足、来源与示意界限明确','原尺寸近读无裁剪或遮挡','概念图与文字语义一致'],checks:info.checks??{conceptual_diagram:true}};write(id+'-metadata-v001.json',J(m));s.toolUsage('B04',{tool:'Node.js + Snapshot DSL construction',case_id:id,purpose:m.visual_intent,input:'research actual NASA text + editorial-plan-v001.json',output:path.join(dir,id+'-v001.snapshot'),source_ids:m.source_ids});return {id,dsl:path.join(dir,id+'-v001.snapshot'),width:c.width,height:c.height,extra:{type:'baseline'}};}
const batch=[];
{
const c=new Canvas(1600,1100,{background:navy});stars(c,1600,900);head(c,'01',1600,'90分钟，再绕一圈','从地面的一天，理解空间站的轨道节奏。',true);
c.circle(1120,820,285,'#286A89');c.circle(1064,780,248,'#3F93AE',{opacity:.45});
for(let i=0;i<8;i++){const y=620+i*55,x0=1120-Math.sqrt(Math.max(0,285*285-(y-820)**2)),x1=1120+Math.sqrt(Math.max(0,285*285-(y-820)**2));c.line(x0,y,x1,y,'#77B7BB',1);}
ring(c,1120,820,356,blue,3,-2.85,0.33);ring(c,1120,820,375,'#314D62',1,-2.85,0.33);
c.arrow(860,545,940,510,orange,4);text(c,1060,790,260,80,'地球',43,'#F2FBFA',true);
// Explicit conceptual spacecraft, not a measured engineering view.
c.rect(1210,408,120,25,'#D4DEE4',{radius:8});c.rect(1250,386,44,70,'#EAF0F2',{radius:12});
for(let q=0;q<4;q++){const x=1167+q*63;c.rect(x,300,44,89,'#497EB0',{border:'2 SOLID #95CDE5'});c.rect(x,463,44,89,'#497EB0',{border:'2 SOLID #95CDE5'});for(let k=1;k<6;k++){c.line(x,300+k*14,x+44,300+k*14,'#95CDE5',1);c.line(x,463+k*14,x+44,463+k*14,'#95CDE5',1);}}
text(c,64,332,660,146,'约90',122,'#F6F4EB',true);text(c,440,404,250,54,'分钟 / 一圈',30,blue);
text(c,69,530,560,67,'约28,000 km/h',48,orange,true);text(c,72,622,585,60,'轨道运行速度；不是相对你头顶的角速度。',23,'#D8E2E9');
c.rect(64,735,605,183,'#20364B',{radius:24});text(c,91,764,550,58,'24小时 ÷ 90分钟 ≈ 16圈',29,'#F8F8F0',true);text(c,91,823,530,62,'90分钟与16圈都是科普约数，实际轨道会变化。',22,'#C9D9E4');
text(c,933,914,570,36,'轨道与空间站轮廓为概念示意，不按比例。',20,'#B9D3E0');
footer(c,1600,1100,'来源：NASA Facts and Figures；Spot the Station FAQ（2025）',true);
batch.push(save('case-01',c,{title:'90分钟，再绕一圈',source_ids:['facts','sighting'],audience:'中学生与科学馆家庭观众',use_context:'1600×1100科学展览主海报，近读轨道约数',user_goal:'连接90分钟、一小时速度与一天约16圈的含义',content_basis:'NASA实际读取facts及2025-05-06 FAQ；约90分钟/圈、28000km/h、24小时约16圈。轨道和飞船轮廓为编辑概念示意。',visual_intent:'深蓝星野、巨大地球和偏心环轨，把轨道循环与三种时间尺度并置',checks:{calculation:'24*60/90=16',units:['min/orbit','km/h','orbit/day'],diagram:'not-to-scale'}}));}
{
const c=new Canvas(1600,1100,{background:paper});head(c,'08',1600,'五家机构，一个共同平台','合作是一张依赖网络：各伙伴负责自己提供的硬件。');
const nodes=[['NASA','美国',278,354,blue],['Roscosmos','俄罗斯',1300,352,orange],['ESA','欧洲空间局',1420,720,'#D7BBE3'],['JAXA','日本',840,883,mint],['CSA','加拿大',193,714,'#E7C77C']];
for(const [n,z,x,y,col] of nodes){const dx=800-x,dy=591-y,L=Math.hypot(dx,dy),ux=dx/L,uy=dy/L;c.line(x+ux*102,y+uy*70,800-ux*200,591-uy*95,col,13,{opacity:.72});}
c.card(575,455,450,238,navy,{radius:34});text(c,614,480,370,53,'ISS',45,'#F4F6F0',true);text(c,614,552,370,93,'一起运行\n共同使用的空间实验室',30,'#C3DDE8');
for(const [n,z,x,y,col] of nodes){c.card(x-122,y-68,244,135,col,{radius:25});text(c,x-102,y-51,205,56,n,n.length>8?26:35,ink,true);text(c,x-102,y+12,207,36,z,24,ink);}
text(c,530,333,520,63,'五家伙伴机构 ≠ 五个国家',29,ink,true);text(c,540,725,500,90,'共同平台依赖跨机构贡献；\n关系图不表示资金或贡献比例。',25,muted);
footer(c,1600,1100,'来源：NASA ISS Reference（页面更新2025-11-27）');
batch.push(save('case-08',c,{title:'五家机构，一个共同平台',source_ids:['history'],audience:'学生、展览观众和国际合作课程读者',use_context:'横向1600×1100合作网络展板，近读机构缩写',user_goal:'识别五家伙伴机构并理解互相依赖的运作',content_basis:'NASA ISS Reference说明五家伙伴机构共同运行、各自控制所供硬件。欧洲为跨国机构，不等同单个国家。无资金贡献数据。',visual_intent:'五条不同方向的彩带汇入共同实验室，不绘假地理地图或贡献占比',checks:{partner_agencies:['NASA','Roscosmos','ESA','JAXA','CSA'],edges:5,diagram:'relationship only; equal weight not contribution'}}));}
{
const c=new Canvas(1500,1200,{background:'#E9EFE9'});head(c,'09',1500,'把问题带到微重力里','看研究，先分清：在问什么、测了什么、能说明什么。');
c.rect(64,290,1372,44,ink,{radius:7});text(c,86,299,950,32,'两类研究问题   /   概念示意，不呈现实验结果或效应大小',19,'#FFFFFF');
const cards=[{x:64,title:'物理与材料',col:blue,question:'当重力效应减弱，\n流体与材料会如何表现？',measure:'研究者需要设计实验、测量条件，\n并说明与地面比较的方法。',limit:'这里的圆点仅是构图；\n没有把它们当成真实粒子轨迹。'},{x:764,title:'人体与运动',col:orange,question:'怎样减轻长期飞行中的\n骨骼与肌肉变化？',measure:'NASA综述介绍运动设备与多项研究；\n个体结果有差异，仍需改进措施。',limit:'平均锻炼时长不是效果保证，\n也不是公众训练处方。'}];
for(const a of cards){c.card(a.x,367,672,630,'#F9FBF5',{radius:22});c.rect(a.x,367,672,10,a.col);text(c,a.x+27,400,600,55,a.title,35,ink,true);text(c,a.x+27,496,600,80,a.question,29,ink,true);text(c,a.x+27,692,600,100,a.measure,24,muted);text(c,a.x+27,881,600,88,a.limit,23,muted);}
// A chamber and two abstract motion traces: no experimental data.
c.rect(106,592,520,72,'#DCEBF0',{radius:28});for(let i=0;i<9;i++)c.circle(151+i*52,628+(i%3-1)*12,6,ink);c.arrow(123,830,616,830,blue,3);text(c,140,790,490,32,'测量条件 + 对照 + 方法',22,ink);
// A restrained conceptual load icon.
c.circle(842,623,22,ink);c.line(840,650,839,680,ink,8);c.line(840,663,889,645,ink,7);c.line(869,634,900,634,orange,10);c.line(925,609,1340,609,orange,3);text(c,935,630,390,42,'证据来自研究，不来自插图',22,ink);
text(c,83,1032,1330,46,'阅读下一步：到原文核查研究名称、时间、样本、对照与限制；本文未逐篇阅读综述中的论文。',22,ink);
footer(c,1500,1200,'来源：NASA ISS Reference（2025）；Astronaut Exercise（2024-05-20）');
batch.push(save('case-09',c,{title:'把问题带到微重力里',source_ids:['history','exercise'],audience:'科学传播读者和中学生研究入门课程',use_context:'1500×1200导读板，阅读来源前先学习证据边界',user_goal:'把研究问题、来源综述与概念示意分开，知道下一步如何查证',content_basis:'研究领域来自NASA ISS Reference；运动问题及个体差异来自2024 Astronaut Exercise综述。原论文未逐篇访问；没有自造结果、样本或医疗保证。',visual_intent:'两种问题用双栏实验笔记呈现，中部图示与下方阅读行动强调证据界限',checks:{data_plot:false,peer_reviewed_papers_read:false,claim_type:'editorial interpretation based on NASA summaries'}}));}
{
const c=new Canvas(1200,1600,{background:navy});stars(c,1200,1250);head(c,'10',1200,'今晚，怎样看见空间站','从一条真实的观测通知，开始找天空中的移动亮点。',true);
text(c,67,299,1036,57,'第一步：查询你所在地的可见过境',35,'#F4F3EA',true);text(c,69,375,1000,86,'使用NASA Spot the Station，核对位置与当地时区。\n这张图没有实时预测；不要照图中的示意路径计时。',25,'#C3D6E2');
c.card(64,490,1072,194,'#233A50',{radius:24});const fields=[['时间','当地时间'],['时长','可见多久'],['高度','距地平线'],['方向','出现 → 消失']];fields.forEach((a,i)=>{const x=90+i*258;text(c,x,516,234,46,a[0],29,orange,true);text(c,x,579,234,43,a[1],24,'#E1E8EA');});
const cx=600,cy=1104,r=287;ring(c,cx,cy,r,blue,3,Math.PI,2*Math.PI);c.line(241,1104,959,1104,'#8CAAC0',3);text(c,246,1121,330,33,'地平线 0°',22,'#D8E2E8');text(c,550,753,220,35,'天顶 90°',22,'#D8E2E8');
const points=[];for(let i=0;i<31;i++){const x=325+i*18,y=1050-163*Math.sin(i/30*Math.PI);points.push([x,y]);}c.polyline(points,orange,6);c.arrow(...points[24],...points[28],orange,5);c.circle(505,906,9,'#FFFFFF');text(c,275,706,650,42,'第二步：到视野开阔处，按通知找方向',30,'#F4F3EA',true);
text(c,258,1174,740,54,'路径与角度只解释概念，非某地某晚的过境。',22,'#B2C9D9');
c.rect(64,1274,1072,174,'#20364B',{radius:22});text(c,90,1298,1010,48,'肉眼即可   ·   留意晨昏时的反射阳光',31,blue,true);text(c,92,1370,1000,61,'ISS反射太阳光；进入地球阴影会影响可见。\n头顶经过，也不一定满足可见条件。',23,'#CFDEE6');
footer(c,1200,1600,'来源：NASA Spot the Station FAQ（2025-05-06）',true);
batch.push(save('case-10',c,{title:'今晚，怎样看见空间站',source_ids:['sighting'],audience:'首次用肉眼观察ISS的公众与亲子家庭',use_context:'1200×1600近读行动折页或竖屏展示，出门前核对',user_goal:'查当地真实通知，读懂时间、方向、高度，选择开阔处观看',content_basis:'NASA FAQ 2025-05-06：反射太阳光、晨昏观测、肉眼可见、通知当地时区与最高高度及出现/消失方向。示意路径无日期、地点或预测功能。',visual_intent:'通知字段变成四步读法，半穹顶和移动亮点解释角度，夜空与行动条形成观测工具',checks:{real_time_prediction:false,elevation_concepts:[0,90],instructions_source:'sighting questions 3,10–15,24'}}));}
write('batch-v001.json',J(batch));s.taskCheckpoint('B04',{event_type:'research-and-root-drafts',resume_notes:'Seven NASA sources actually read; case01/08/09/10 DSL candidates ready, case02–07 in parallel private production.',case_id:null});s.writeTaskMetrics('B04');console.log(J(batch));
