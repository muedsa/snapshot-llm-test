'use strict';
const fs=require('fs'),path=require('path');
const {Canvas}=require('../../_suite/dsl.cjs');
const dir=__dirname;
const started='2026-10-07T04:08:14Z';
const source=JSON.parse(fs.readFileSync(path.join(dir,'../problem-plan-v001.json'),'utf8'));
function save(n,c,extra){
 const id='case-'+String(n).padStart(2,'0'),p=source.cases.find(x=>x.id===id);
 fs.writeFileSync(path.join(dir,id+'-v001.snapshot'),c.toString(),'utf8');
 const m={case_id:id,title:p.title,audience:p.audience,use_context:p.use_context,user_goal:extra.goal,content_basis:{type:'fictional_static_demo',description:source.content_boundary,data:p.data},visual_intent:extra.intent,completion_criteria:[...p.checks,...extra.criteria],checks:{visual_verified:false,service_request_by_this_agent:false,visual_review_owner:'root',static_data_consistency:'matches B06 problem-plan-v001',...extra.checks},dimensions:p.dimensions,creative_started_at:started,creative_started_at_source:'clock tool at actual resumed producer start',created_at:new Date().toISOString(),supporting_assets:[],dsl_capabilities:['Container','Positioned','Stack','Text/Raw','Transform','programmatic geometry']};
 fs.writeFileSync(path.join(dir,id+'-metadata-v001.json'),JSON.stringify(m,null,2));
}
// 05: fridge inventory is reorganised by label date, then mapped to location.
{
 const c=new Canvas(1200,1500,{background:'#F5F0DF'}),ink='#2D3B2A',green='#496E39',orange='#D96336';
 c.text(70,50,730,40,'KITCHEN / 先用队列',26,green,{bold:true,letterSpacing:2});
 c.text(70,111,1000,104,'今晚先用哪一盒',66,ink,{bold:true});
 c.text(72,218,780,60,'先看标签日期，再找到它的位置。',30,ink);
 c.card(874,50,254,72,ink,{radius:36});c.text(894,63,214,44,'2026.10.10',27,'#F5F0DF',{bold:true,align:'CENTER'});
 c.text(74,317,612,58,'按示例标签日期排序',33,ink,{bold:true});
 c.text(762,317,370,58,'位置小地图',33,ink,{bold:true});
 const foods=[['01','豆腐','1盒','10月11日','中层前排',orange],['02','蘑菇','1袋','10月12日','抽屉左侧',green],['03','菠菜','1把','10月13日','抽屉右侧','#748455']];
 foods.forEach((f,i)=>{
  const y=401+i*215;
  c.card(70,y,630,190,'#FFFCF3',{radius:22,border:'2 SOLID #D4D9BF'});
  c.rect(70,y,10,190,f[5],{borderRadiusTopLeft:22,borderRadiusBottomLeft:22});
  c.circle(126,y+56,30,f[5]);c.text(102,y+37,48,45,f[0],25,'#FFFFFF',{bold:true,align:'CENTER'});
  c.text(174,y+22,254,64,f[1],44,ink,{bold:true});
  c.text(458,y+31,182,46,f[2],30,ink,{align:'END'});
  c.text(174,y+93,390,50,'标签：'+f[3],31,f[5],{bold:true});
  c.text(174,y+140,420,40,f[4],26,ink);
 });
 // Schematic locations carry identical words as the queue, without safety claims.
 c.card(755,401,375,620,'#E6EAD7',{radius:40,border:'4 SOLID #7F946C'});
 c.text(787,429,306,47,'冰箱正面示意',26,green,{bold:true,align:'CENTER'});
 c.line(781,509,1105,509,'#9BAE87',4);
 c.card(787,535,310,192,'#F8FAEE',{radius:16});
 c.text(810,550,266,42,'中层 · 前排',25,green,{bold:true});
 c.card(818,609,245,89,'#F9DDD0',{radius:14,border:'3 SOLID #D96336'});
 c.text(833,624,213,54,'01  豆腐',32,ink,{bold:true,align:'CENTER'});
 c.line(781,760,1105,760,'#9BAE87',4);
 c.card(787,790,146,174,'#F8FAEE',{radius:15,border:'2 SOLID #7F946C'});
 c.card(951,790,146,174,'#F8FAEE',{radius:15,border:'2 SOLID #7F946C'});
 c.text(798,804,126,44,'抽屉左',25,green,{bold:true,align:'CENTER'});
 c.text(963,804,124,44,'抽屉右',25,green,{bold:true,align:'CENTER'});
 c.text(798,857,126,85,'02\n蘑菇',30,ink,{bold:true,align:'CENTER',lineHeight:1.15});
 c.text(963,857,124,85,'03\n菠菜',30,ink,{bold:true,align:'CENTER',lineHeight:1.15});
 c.card(70,1080,1060,246,ink,{radius:28});
 c.text(102,1105,472,43,'今晚的选择',27,'#C8DFAE',{bold:true});
 c.text(102,1154,455,75,'豆腐 ＋ 蘑菇',48,'#FFFCF3',{bold:true});
 c.text(104,1242,480,48,'按实际状态确认后再使用',26,'#D7E3CB');
 c.line(618,1112,618,1290,'#718665',2);
 c.text(659,1115,400,45,'要买：米 1份',31,'#FFFCF3',{bold:true});
 c.text(659,1172,420,44,'不用再买：豆腐、蘑菇',28,'#D7E3CB');
 c.text(659,1231,400,43,'菠菜保留在位置索引中',25,'#D7E3CB');
 c.text(70,1370,1060,97,'自拟标签示例，不判断食品安全。开封／储存状态与实际包装优先；\n发现异常时按真实情况处理。此卡不是保质期或剩余寿命保证。',24,ink,{lineHeight:1.3});
 save(5,c,{goal:'从演示日期队列找到豆腐与蘑菇，确定今晚要用及无需重复购买的项目',intent:'暖纸色先用队列配正面冰箱小地图；序号连接日期和位置，深绿晚餐卡把库存转为下一步',criteria:['队列三项有数量/标签日期/位置','今晚食材、需买米1份与不重复买项均完整','位置图仅为示意、未宣称食物安全'],checks:{queue_order:['10月11日','10月12日','10月13日'],location_map_matches:true}});
}
// 06: date chips and decisive verbs form an actionable library digest.
{
 const c=new Canvas(1200,1500,{background:'#EEE9F5'}),ink='#2A2343',purple='#6857A4';
 c.rect(0,0,1200,22,purple);
 c.text(68,57,715,44,'北窗图书馆 / 借阅行动摘要',27,purple,{bold:true,letterSpacing:1});
 c.text(68,118,1050,95,'三本书，三种下一步',63,ink,{bold:true});
 c.text(70,227,960,54,'不用逐项猜状态，先看今天该做什么。',30,ink);
 c.text(70,304,630,46,'今天 2026.10.10',28,purple,{bold:true});
 c.text(715,304,415,46,'营业 09:00–18:00',28,purple,{align:'END'});
 const rows=[
 {y:399,color:'#C4553C',fill:'#FFF6EF',action:'归还',title:'城市里的树',badge:'不可续借',d1:'10 / 11',d2:'18:00 前',l1:'已有他人预约，不能续借。',l2:'请在截止前把书带回图书馆。'},
 {y:719,color:'#6857A4',fill:'#FBF8FF',action:'取书',title:'雨天地图',badge:'预约已到馆',d1:'10 / 12',d2:'18:00 前',l1:'1层预约架 R-08',l2:'到馆取书；截止时间不要漏看。'},
 {y:1039,color:'#2E7874',fill:'#F2FFFA',action:'申请续借',title:'慢读笔记',badge:'可续借一次',d1:'10 / 14',d2:'当前到期',l1:'尚未申请；成功后才改为10月28日。',l2:'先提交申请，再核对成功结果。'}
 ];
 rows.forEach((r,i)=>{
  c.card(68,r.y,1064,279,r.fill,{radius:23,border:'2 SOLID #C6BCD8'});
  c.rect(68,r.y,228,279,r.color,{borderRadiusTopLeft:23,borderRadiusBottomLeft:23});
  c.text(90,r.y+26,184,47,'0'+(i+1),26,'#FFFFFF',{bold:true});
  c.text(85,r.y+87,194,75,r.d1,38,'#FFFFFF',{bold:true,align:'CENTER'});
  c.text(86,r.y+174,192,54,r.d2,27,'#FFFFFF',{bold:true,align:'CENTER'});
  c.text(328,r.y+24,470,72,r.action,48,r.color,{bold:true});
  c.card(831,r.y+27,267,53,'#FFFFFF',{radius:26,border:'1 SOLID #C6BCD8'});
  c.text(842,r.y+36,245,40,r.badge,25,r.color,{bold:true,align:'CENTER'});
  c.text(329,r.y+106,738,64,'《'+r.title+'》',38,ink,{bold:true});
  c.text(329,r.y+179,743,43,r.l1,27,ink);
  c.text(329,r.y+228,743,38,r.l2,25,ink);
 });
 c.text(72,1372,1056,84,'图书馆、书名、规则与日期均为自拟演示。续借不是自动成功；\n实际资格、截止时间、营业与取书位置以你的图书馆记录为准。',24,ink,{lineHeight:1.3});
 save(6,c,{goal:'先归还不可续借的书、到馆取预约书，并把第三本的续借申请与结果区别开',intent:'行动票据式纵向摘要，左侧日期、右侧动词与状态；按截止动作先后重排原始书单',criteria:['三书名/状态/动作与期限一一对应','R-08位置与营业时间齐全','续借明确尚未申请且成功后才改期'],checks:{display_order:['归还','取书','申请续借'],conditional_extension:true}});
}
// 07: literal numbered doors and row/column coordinates make the target redundant.
{
 const c=new Canvas(1600,1120,{background:'#101D2A'}),ink='#EAF1F4',muted='#ADC0CB',yellow='#FFD965';
 c.text(67,50,950,50,'北院 A柜 / 包裹定位',28,yellow,{bold:true,letterSpacing:2});
 c.text(66,110,1070,92,'你的包裹，在这扇门',65,ink,{bold:true});
 c.text(67,222,1070,52,'核对 A柜 → 输入本人真实取件码 → 找到 17号门',30,muted);
 c.card(1169,51,363,141,yellow,{radius:22});
 c.text(1195,69,313,44,'目标位置',27,'#162431',{bold:true});
 c.text(1195,112,314,65,'第3行 · 第5列',35,'#162431',{bold:true});
 const x=126,y=403,w=126,h=101,gx=18,gy=20;
 for(let col=0;col<6;col++)c.text(x+col*(w+gx),341,w,48,String(col+1)+'列',26,muted,{align:'CENTER',bold:true});
 for(let row=0;row<4;row++){
  c.text(54,y+row*(h+gy)+32,66,43,String(row+1)+'行',25,muted,{bold:true});
  for(let col=0;col<6;col++){
   const n=row*6+col+1,tx=x+col*(w+gx),ty=y+row*(h+gy),target=n===17;
   c.card(tx,ty,w,h,target?yellow:'#26394A',{radius:12,border:target?'5 SOLID #FFF4CC':'2 SOLID #597488'});
   c.text(tx+9,ty+18,w-18,63,String(n).padStart(2,'0'),target?45:34,target?'#101D2A':ink,{bold:true,align:'CENTER'});
   c.rect(tx+w-13,ty+39,4,24,target?'#101D2A':'#7892A5',{radius:2});
  }
 }
 c.arrow(826,649,886,649,yellow,5,{headLength:18,headWidth:10});
 c.text(800,881,234,43,'17号门 · 目标',26,yellow,{bold:true,align:'CENTER'});
 c.line(1136,331,1136,918,'#4B6476',2);
 c.text(1193,323,340,172,'17',132,yellow,{bold:true});
 c.text(1195,503,340,56,'小件包裹 · 1件',31,ink,{bold:true});
 c.text(1195,580,340,90,'取件截止\n10月12日20:00',28,muted,{lineHeight:1.4});
 c.card(1190,716,343,167,'#26394A',{radius:18,border:'2 SOLID #597488'});
 c.text(1215,734,294,54,'还没有开门',31,yellow,{bold:true});
 c.text(1215,801,294,64,'这张卡只帮你定位；\n开门请按柜机提示。',25,ink,{lineHeight:1.15});
 c.card(67,957,1466,112,'#192C3D',{radius:19});
 c.text(94,977,1410,76,'编号从左向右、逐行递增，共4行×6列＝24扇门。\n自拟定位示意：未接入真实柜机，不提供可用取件码。实际位置与取件状态以柜机为准。',25,muted,{lineHeight:1.25});
 save(7,c,{goal:'在24门的A柜中可靠定位第3行第5列17号门，并理解尚未开门、仍须本人真实取件码',intent:'夜间深色柜门矩阵与琥珀目标；行列数字、门号、边框和箭头重复编码，右侧保留截止与状态',criteria:['24门完整不重号且17正确映射3行5列','颜色之外有数字/边框/箭头定位','本人真实取件码提示、尚未开门及未接入边界明确'],checks:{door_count:24,unique_door_count:24,target_row:Math.floor((17-1)/6)+1,target_col:(17-1)%6+1}});
}
fs.writeFileSync(path.join(dir,'production-v001.json'),JSON.stringify({producer:'b06_cases_05_07_resume',started_at:started,ended_at:new Date().toISOString(),read_sources:['tasks/B06-everyday-information-reinvented/TASK.md','tasks/B06-everyday-information-reinvented/AGENTS.md','tasks/B06-everyday-information-reinvented/task.json','tasks/B06-everyday-information-reinvented/run-config.json','tasks/B06-everyday-information-reinvented/inputs/README.md','tmp/20261002-204314-6f31/B06/problem-plan-v001.json','tmp/20261002-204314-6f31/_suite/shared-doc-000001-response.txt','tmp/20261002-204314-6f31/_suite/shared-doc-000004-readable.txt','tmp/20261002-204314-6f31/_suite/dsl.cjs'],no_new_http:true,candidates:[5,6,7].map(n=>'case-'+String(n).padStart(2,'0')+'-v001.snapshot'),visual_verified:false},null,2));
console.log(JSON.stringify({cases:[5,6,7],directory:dir,render_required:true}));
