'use strict';
const fs=require('fs'),path=require('path');
const {Canvas,P,T,mark,header,footer,stitch,patch}=require('../project-system-v001.cjs');
const plan=JSON.parse(fs.readFileSync(path.join(__dirname,'../plan-v001.json'),'utf8'));
const events=fs.readFileSync(path.join(__dirname,'../../_suite/events.jsonl'),'utf8').trim().split(/\r?\n/).map(x=>JSON.parse(x));
const selected=process.argv[2]??'all';
const reads=['tasks/B02-one-project-visual-ecosystem/TASK.md','tasks/B02-one-project-visual-ecosystem/AGENTS.md','tasks/B02-one-project-visual-ecosystem/task.json','tasks/B02-one-project-visual-ecosystem/run-config.json','tasks/B02-one-project-visual-ecosystem/inputs/README.md','B02/plan-v001.json','B02/project-system-v001.cjs','shared cached service guide and Parser read during B01'];
function save(name,v){fs.writeFileSync(path.join(__dirname,name),v,{flag:'wx',encoding:'utf8'});}
function label(c,x,y,w,h,t,size=24,col=P.ink,b=false,align='START'){c.text(x,y,w,h,t,size,col,{bold:b,align,lineHeight:1.15});}
function checked(c,x,y,size=26){c.rect(x,y,size,size,P.clay,{radius:5});c.polyline([[x+6,y+size*.5],[x+size*.44,y+size*.72],[x+size*.8,y+size*.28]],P.paper,3,{roundCaps:true});}
function circleBorder(c,x,y,r,col=P.ink,width=3){c.circle(x,y,r,'transparent',{border:`${width} SOLID ${col}`});}
function finish(n,c,meta){
 const id=`case-${n}`,started=events.find(e=>e.task_id==='B02'&&e.type==='case-creative-start'&&e.case_id===id);
 if(!started)throw new Error('Actual creative start event missing: '+id);
 const dsl=c.toString(),element_count=(dsl.match(/<[A-Za-z]/g)||[]).length;
 if(element_count>4096)throw new Error('Snapshot element limit exceeded');
 save(id+'-v001.snapshot',dsl);
 meta={task_id:'B02',run_id:'20261002-204314-6f31',case_id:id,dimensions:[c.width,c.height],project:plan.project,audience:meta.audience,use_context:meta.use_context,user_goal:meta.user_goal,content_basis:plan.content_basis,visual_intent:meta.visual_intent,dsl_capabilities:meta.dsl_capabilities,completion_criteria:meta.completion_criteria,checks:meta.checks,creative_started_at:started.time,creative_start_event_id:started.id,creative_time_scope:'共同项目方案启动至交付（含并行）',dsl_generated_at:new Date().toISOString(),shared_design_system:'../project-system-v001.cjs',asset_policy:'pure DSL; zero Image/Emoji tags; original geometric illustrations',source_reads:reads,status:'draft; root render and actual visual review pending'};
 meta.checks.programmatic={...meta.checks.programmatic,element_count,element_limit:4096,external_asset_count:0,canvas:[c.width,c.height]};
 save(id+'-metadata-v001.json',JSON.stringify(meta,null,2)+'\n');
 save(id+'-notes-v001.md',`# ${meta.title??id} / ${plan.project}\n\n受众：${meta.audience}。使用场景：${meta.use_context}。用户目标：${meta.user_goal}。\n\n${meta.content_basis}\n\n视觉：${meta.visual_intent}\n\n开始时间采用实际${started.id}事件${started.time}，范围为${meta.creative_time_scope}，不是独占执行时长。生成DSL元素${element_count}，低于4096。没有渲染、HTTP或图片查看；最终视觉证据由root填入。\n`);
 console.log(JSON.stringify({case_id:id,snapshot:path.join(__dirname,id+'-v001.snapshot'),metadata:path.join(__dirname,id+'-metadata-v001.json'),elements:element_count}));
}

if(selected==='all'||selected==='02'){
 const c=new Canvas(900,1500,{background:P.paper});header(c,'预约体验');
 label(c,48,138,740,66,'让旧物，再用一次。',47,P.ink,true);label(c,49,220,802,42,'预约确认 · 基础修补体验',25,P.clay,true);
 // The patch mark becomes the selected textile, not a stock photograph.
 c.rect(48,287,804,260,P.ink,{radius:24});patch(c,81,324,184,184,P.clay);c.rect(111,355,122,122,P.sage,{radius:4});stitch(c,119,363,106,106,P.paper);c.line(147,388,198,444,P.paper,3,{roundCaps:true});c.line(151,429,199,389,P.paper,3,{roundCaps:true});
 label(c,305,315,508,43,'已选：小面积破洞',31,P.paper,true);label(c,305,373,508,82,'带一件干净的棉 / 麻织物\n先由工作人员确认修补方式',24,P.paper);label(c,305,470,508,35,'不确定损伤？到店先评估。',20,'#C7D6D7');
 label(c,49,586,800,44,'01  时间与地点',28,P.ink,true);
 c.rect(48,650,804,173,P.light,{radius:20,border:`1 SOLID ${P.line}`});label(c,73,674,750,40,'2026年10月24日 · 周六',29,P.ink,true);label(c,73,730,750,45,'10:30–11:15  /  45分钟',33,P.clay,true);label(c,73,787,749,30,'澄巷12号 · 再线社区修补间',20,P.ink);
 label(c,49,863,800,43,'02  费用，先说清楚',28,P.ink,true);c.rect(48,923,804,207,'#E7DDD0',{radius:20});
 label(c,72,951,439,43,'基础体验',27,P.ink,true);label(c,624,944,195,62,'¥30',46,P.clay,true,'END');label(c,72,1011,746,37,'含基础布料与线 · 不额外收取基础材料费',22,P.ink);label(c,72,1068,746,36,'复杂损伤先评估再报价，本页不预收复杂修补费用。',20,P.ink);
 checked(c,52,1176,27);label(c,98,1173,720,39,'我知道：10:20先到店签到，再确认织物状态。',22,P.ink);
 c.rect(48,1254,804,84,P.clay,{radius:22});label(c,71,1274,758,45,'确认体验  ·  ¥30',31,P.paper,true,'CENTER');label(c,49,1363,803,36,'示例状态：待确认 · 静态画面不提供真实预约或支付',19,P.ink,'', 'CENTER');
 footer(c,'自拟项目 / 虚构地址 · 营业：周三–周日 10:00–18:00');
 finish('02',c,{title:'预约确认界面',audience:'想修补一件棉麻织物、第一次参加的社区居民',use_context:'预约前手机查看；可放大阅读静态设计，不代表真实可用名额',user_goal:'确认损伤类型、材料与费用、45分钟时段和提前10分钟签到后决定参与',visual_intent:'深墨色选中织物区与缝线补丁作为身份；日程和费用按操作顺序分段，唯一陶土色确认按钮突出最终行动',dsl_capabilities:['Stack/Positioned mobile layout','Container rounded decision regions','original patch/stitch geometry','Text/Raw labels and pricing','Transform line details'],completion_criteria:['2026-10-24确为周六','10:30–11:15为45分钟且签到10:20提前10分钟','¥30只包含基础布料与线；复杂损伤先评估再报价','选择、地址、日期、价格、条件与确认动作完整','静态待确认状态明确，不宣称完成真实预约','实际根代理看图无截断或重叠'],checks:{arithmetic:{date:'2026-10-24',weekday:'Saturday',start:'10:30',end:'11:15',duration_minutes:45,check_in:'10:20',early_minutes:10,price:30,currency:'CNY',complex_damage:'assessment before quote'},actual_visual_review:null}});
}

if(selected==='all'||selected==='03'){
 const c=new Canvas(1500,1000,{background:P.paper});header(c,'到店导览');
 label(c,49,134,990,71,'先签到，再上手。',54,P.ink,true);label(c,50,220,1000,40,'2026-10-24 · 周六开放日  /  澄巷12号（虚构）',25,P.clay,true);
 // Spatial plan deliberately reads from entrance to staffed workstations.
 c.rect(48,297,1008,577,P.light,{radius:26,border:`2 SOLID ${P.ink}`});
 label(c,76,323,910,40,'修补间平面示意  /  地图不按比例',24,P.ink,true);
 c.rect(85,510,247,231,'#E2D5C2',{radius:10,border:`2 SOLID ${P.line}`});patch(c,110,539,47,47,P.clay);label(c,176,543,130,41,'01 签到台',24,P.ink,true);
 label(c,112,608,190,76,'报预约时间\n领取工位编号',23,P.ink);label(c,111,695,191,28,'请先停在这里',18,P.clay,true);
 c.rect(405,510,256,231,'#DCE5DC',{radius:10,border:`2 SOLID ${P.sage}`});patch(c,429,539,47,47,P.sage);label(c,493,543,145,41,'02 评估台',24,P.ink,true);
 label(c,430,608,207,76,'摊开织物\n确认修法与费用',23,P.ink);label(c,430,695,207,28,'有疑问先问工作人员',17,P.ink);
 c.rect(744,415,277,326,'#DEE3E4',{radius:10,border:`2 SOLID ${P.ink}`});patch(c,771,444,47,47,P.ink);label(c,835,448,162,41,'03 修补工位',24,P.ink,true);
 // Two tables and four seats convey work area rather than a box-only flowchart.
 c.rect(779,525,208,83,P.paper,{radius:8,border:`2 SOLID ${P.ink}`});c.line(883,528,883,605,P.line,2);for(const [x,y] of [[801,505],[940,505],[801,630],[940,630]])c.rect(x,y,30,17,P.sage,{radius:4});
 label(c,772,674,223,42,'按编号入座 · T01–T04',20,P.ink,true);
 // Hallway route: entry branch, then two clear arrows between consecutive desks.
 c.rect(88,778,245,61,P.ink,{radius:8});label(c,106,791,208,34,'入口  →  先签到',22,P.paper,true,'CENTER');c.arrow(210,779,210,749,P.clay,5,{headLength:10,headWidth:5});
 c.arrow(339,623,396,623,P.clay,6,{headLength:13,headWidth:6});c.arrow(668,623,735,623,P.clay,6,{headLength:13,headWidth:6});
 c.rect(744,783,277,57,P.sage,{radius:7});label(c,759,795,248,32,'工具归位区 / 对照编号',20,P.paper,true,'CENTER');
 label(c,392,782,299,55,'共用连廊\n请保持通行',21,P.ink,false,'CENTER');
 c.rect(1095,297,357,577,P.ink,{radius:24});label(c,1122,329,299,49,'今天的三个动作',28,P.paper,true);
 const rows=[['10:20','签到，领工位号'],['随后','评估，确认修法'],['10:30','入座，开始体验']];rows.forEach((r,i)=>{let y=411+i*126;c.circle(1140,y+17,6,P.clay);label(c,1160,y-3,260,39,r[0],27,P.paper,true);label(c,1160,y+48,260,39,r[1],23,P.paper);if(i<2)c.line(1140,y+37,1140,y+116,P.sage,2);});
 label(c,1121,801,301,43,'体验至11:15 · 共45分钟',21,'#CDD7D4');
 footer(c,'自拟项目 · 演示平面与工位 · 营业：周三–周日10:00–18:00 · 非真实建筑或疏散图');
 finish('03',c,{title:'到店签到与空间导览',audience:'已经预约10:30基础体验、刚进入社区修补间的人',use_context:'入口横向数字立牌或前台导览板，近距阅读',user_goal:'先在签到台报预约领取工位号，再找到评估台确认修法，10:30进入修补工位',visual_intent:'从左到右的大空间块与陶土方向箭头落实三步，不依赖色彩判断；深墨时间侧栏将地图与预约时间连接，工位用原创桌椅几何表现',dsl_capabilities:['Stack/Positioned floor plan','Container room/table/seat geometry','patch/stitch identity','Transform directional arrows','Text/Raw numbered navigation'],completion_criteria:['入口明显且第一站为签到台','三个连续编号与箭头一致，不要求先走工具区','评估在修补前；10:20签到早于10:30体验','45分钟至11:15，与共同预约一致','工具归位区与工位编号可辨','标明非比例演示地图，实际看图文字完整'],checks:{arithmetic:{check_in:'10:20',experience:['10:30','11:15'],duration_minutes:45},spatial:{main_sequence:['入口','01签到台','02评估台','03修补工位'],return_area:'工具归位区',workstation_ids:['T01','T02','T03','T04'],geometry:'schematic, no scale or real building claim'},actual_visual_review:null}});
}

if(selected==='all'||selected==='04'){
 const c=new Canvas(1200,1400,{background:P.paper});header(c,'工具归位');
 label(c,49,136,1100,73,'用完，让它回到原位。',52,P.ink,true);label(c,50,222,1080,42,'工位 T03  /  对照编号，按原数量归还',26,P.clay,true);
 // Peg holes are wholly DSL circles and stay well under the service limit.
 c.rect(48,291,1104,659,'#E8DDCE',{radius:22});for(let x=72;x<1130;x+=32)for(let y=315;y<935;y+=32)c.circle(x,y,1.3,'#C7B9A4');
 const cards=[[72,324],[626,324],[72,641],[626,641]];cards.forEach(([x,y])=>{c.rect(x,y,503,274,P.light,{radius:15,border:`2 SOLID ${P.line}`});stitch(c,x+10,y+10,483,254,P.line);});
 // 01 scissors: two original handles, crossing blades, pivot and shelf.
 const x1=100,y1=347;c.circle(x1+62,y1+67,28,'transparent',{border:`9 SOLID ${P.clay}`});c.circle(x1+133,y1+69,28,'transparent',{border:`9 SOLID ${P.clay}`});c.line(x1+78,y1+88,x1+149,y1+174,P.ink,9,{roundCaps:true});c.line(x1+117,y1+89,x1+47,y1+174,P.ink,9,{roundCaps:true});c.circle(x1+98,y1+115,9,P.sage);c.line(x1+39,y1+209,x1+155,y1+209,P.line,3);
 label(c,310,349,235,40,'01  剪刀',29,P.ink,true);label(c,310,405,230,42,'1 把',31,P.clay,true);label(c,310,466,225,86,'合拢刀刃\n手柄朝下放回',24,P.ink);
 // 02 seam ripper with a visible separate cap shape, labels define actual order.
 c.rect(683,403,53,118,P.sage,{radius:20});c.line(709,401,709,358,P.ink,6);c.line(709,358,730,358,P.ink,5);c.circle(733,358,5,P.clay);c.rect(754,405,37,98,P.clay,{radius:12});label(c,671,542,144,30,'护帽在旁，归还需套上',14,P.ink);
 label(c,865,349,235,40,'02  拆线器',29,P.ink,true);label(c,865,405,230,42,'1 支',31,P.clay,true);label(c,865,466,225,86,'套回护帽\n放回同号位置',24,P.ink);
 // 03 needle box: six needle objects are countable; closed case is shown below.
 c.rect(113,703,148,125,'#DFE5DF',{radius:12,border:`2 SOLID ${P.sage}`});for(let k=0;k<6;k++){let xx=129+k*23;c.line(xx,724,xx,801,P.ink,2);circleBorder(c,xx,726,3,P.ink,1);};c.rect(113,841,148,21,P.sage,{radius:5});
 label(c,310,669,235,40,'03  缝针盒',29,P.ink,true);label(c,310,725,230,42,'6 枚针',31,P.clay,true);label(c,310,786,225,91,'逐枚清点，收入针盒\n少针：告知工作人员',21,P.ink);
 // 04 tape coil: concentric rings and marked tail.
 c.circle(735,770,70,P.paper,{border:`16 SOLID ${P.clay}`});circleBorder(c,735,770,45,P.clay,10);circleBorder(c,735,770,22,P.clay,7);c.line(795,802,795,869,P.clay,17);for(let i=0;i<5;i++)c.line(791,813+i*10,799,813+i*10,P.paper,2);
 label(c,865,669,235,40,'04  软尺',29,P.ink,true);label(c,865,725,230,42,'1 卷',31,P.clay,true);label(c,865,786,225,86,'松卷收好\n不打结、不拉扯',24,P.ink);
 label(c,49,991,1100,49,'归还前，做完这三件事',32,P.ink,true);
 const steps=[['1','核对数量','1把 / 1支 / 6针 / 1卷'],['2','告知缺损','有缺少或损坏，先报告'],['3','放回同号','四件归入工位 T03']];steps.forEach((r,i)=>{const x=48+i*375;c.rect(x,1071,354,218,i===2?P.ink:'#DDD2C1',{radius:18});c.circle(x+37,1112,17,i===2?P.clay:P.ink);label(c,x+24,1100,27,27,r[0],19,P.paper,true,'CENTER');label(c,x+69,1093,259,38,r[1],27,i===2?P.paper:P.ink,true);label(c,x+25,1161,303,81,r[2],22,i===2?P.paper:P.ink);});
 footer(c,'自拟社区项目 · 工位/工具数量为演示 · 针盒清点后合盖，再让下一位使用');
 finish('04',c,{title:'工作台工具归位板',audience:'完成基础修补的体验者与巡台志愿者',use_context:'工位T03近距工具墙/台面归还检查板，原尺寸文字可读性须由root实图确认',user_goal:'清点四种工具，识别缺损，按编号放回原位置，避免下一位借用缺件',visual_intent:'原创工具轮廓置于缝线框和打孔底板，数量用大字与实际可数6针双重表达；最后三步将图形识别转为完整归还动作',dsl_capabilities:['Stack/Positioned pegboard layout','circle/Container tool silhouettes','Transform line scissors and needles','stitched frame identity','Text/Raw quantity and return actions'],completion_criteria:['四种独立工具名称/编号/数量完整','针盒实际绘6针，与6枚文字相符','1剪刀+1拆线器+6针+1软尺，各归工位T03','拆线器护帽与剪刀合拢要求明确','缺损需报告，不能将未齐套件直接流转','三步动作与底部针盒合盖说明完整，实图无遮挡'],checks:{inventory:[{id:'01',tool:'剪刀',quantity:1,unit:'把'},{id:'02',tool:'拆线器',quantity:1,unit:'支'},{id:'03',tool:'缝针',quantity:6,unit:'枚'},{id:'04',tool:'软尺',quantity:1,unit:'卷'}],workstation:'T03',programmatic:{drawn_needle_objects:6,return_actions:['清点','告知缺损','放回同号']},actual_visual_review:null}});
}
