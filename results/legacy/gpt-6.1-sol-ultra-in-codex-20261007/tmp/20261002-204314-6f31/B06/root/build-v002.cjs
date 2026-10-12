const fs=require('node:fs'),path=require('node:path'),{Canvas}=require('../../_suite/dsl.cjs');
const dir=__dirname,started=new Date().toISOString(),plan=JSON.parse(fs.readFileSync(path.join(dir,'../problem-plan-v001.json'))),wx=(name,data)=>fs.writeFileSync(path.join(dir,name),data,{flag:'wx'});
const ink='#263B45';
function txt(c,x,y,w,h,t,s=28,col=ink,bold=false){c.text(x,y,w,h,t,s,col,{bold});}
function header(c,id,title,sub,col=ink){txt(c,65,34,c.width-130,45,'把信息变成下一步   /   日常信息实验 '+id,23,col,true);txt(c,64,105,c.width-128,185,title,65,col,true);txt(c,66,285,c.width-132,70,sub,27,col);}
function footer(c,t,col=ink){c.line(65,c.height-74,c.width-65,c.height-74,col,1,{opacity:.2});txt(c,65,c.height-56,c.width-130,48,t,19,col);}
function save(id,c,extra){if(id==='case-09')return;const p=plan.cases.find(p=>p.id===id);wx(id+'-v002.snapshot',c.toString());wx(id+'-metadata-v002.json',JSON.stringify({...p,user_goal:extra.goal,content_basis:'作者自拟合理案例与演示数据；未做现场调研、用户实验或真实部署。',visual_intent:extra.intent,completion_criteria:p.checks,checks:{data:extra.checks,stage:'unrendered candidate'},supporting_assets:[],creative_started_at:started,creative_start_scope:'Root new DSL construction started in saved build file',created_at:new Date().toISOString()},null,2)+'\n');}
// 01: Room-first lookup, six independently labelled cartons and an explicit first-night target.
{
const c=new Canvas(1200,1500,{background:'#F5EFE3'}),orange='#BB593A',paper='#FFF9EE',tan='#E2C59C';header(c,'01','搬家之后，\n先找到热水壶','10月10日 · 急用物先按房间找，再按箱号开箱。');
c.rect(65,375,1070,125,orange,{radius:18});txt(c,90,395,290,82,'K02',63,paper,true);txt(c,352,392,748,88,'厨房 · 入口右侧下层\n热水壶 / 杯子',30,paper,true);
// Topology: entry is below kitchen. It is not a measured floor plan.
c.card(65,540,560,393,paper,{border:'3 SOLID #A7A899',radius:12});txt(c,90,554,340,50,'厨房  /  K',33,ink,true);
c.rect(99,638,193,181,tan,{radius:8});c.line(195,638,195,651,'#A58761',3);c.line(195,802,195,819,'#A58761',3);txt(c,121,660,144,60,'K01',39,ink,true);txt(c,117,743,156,55,'碗盘',28);
c.rect(374,693,198,181,'#F3BC79',{border:'4 SOLID '+orange,radius:8});c.line(473,693,473,708,orange,3);c.line(473,854,473,874,orange,3);txt(c,395,714,155,62,'K02',40,ink,true);txt(c,393,798,160,55,'壶 / 杯',28);
c.arrow(473,510,473,677,orange,5,{headLength:18});txt(c,114,859,234,46,'入口  ↑',27);c.line(282,931,373,931,'#F5EFE3',8);c.arrow(327,973,327,938,orange,5);
c.card(660,540,475,184,'#E5EBE0',{radius:12});txt(c,683,554,425,45,'卧室  /  B',32,ink,true);txt(c,684,625,417,75,'B01 床品     B02 衣服',29);
c.card(660,750,475,183,'#E0E9ED',{radius:12});txt(c,683,765,425,46,'书房  /  S',32,ink,true);txt(c,684,835,418,67,'S01 书       S02 线材',29);
txt(c,68,990,1060,63,'首晚先开：K02 → B01 → S02',37,orange,true);txt(c,69,1055,1050,54,'喝水、铺床、接好线；其他箱子按房间逐步拆。',27);
const entries=[['K01','厨房 · 碗盘'],['K02','厨房 · 热水壶/杯子'],['B01','卧室 · 床品'],['B02','卧室 · 衣服'],['S01','书房 · 书'],['S02','书房 · 线材']];
entries.forEach((e,i)=>{const x=65+(i%3)*362,y=1134+Math.floor(i/3)*124;c.card(x,y,342,106,paper,{radius:10});txt(c,x+17,y+9,300,43,e[0],28,ink,true);txt(c,x+17,y+54,310,43,e[1],25);});
footer(c,'自拟搬家箱位卡 · 6箱 / 3房 · 图为房间关系示意，不是建筑测量');
save('case-01',c,{goal:'定位热水壶在厨房K02入口右侧下层，按首晚优先顺序拆箱',intent:'纸箱暖色、房间拓扑和K02引线合一，读者从急用物大字直接落到实际箱号',checks:{boxes:6,rooms:3,target:'K02厨房入口右侧下层',first_night:['K02','B01','S02']}});
}
// 08: Resource ownership, return and five-minute check before handoff. T03 is already in stock.
{
const c=new Canvas(1600,1120,{background:'#142F35'}),white='#EFF4E9',blue='#82B5BC',gold='#EAC077',red='#DB8773';
txt(c,65,32,1450,45,'把信息变成下一步   /   日常信息实验 08',23,'#B6CDCA',true);txt(c,65,96,1460,102,'先还什么，再借什么',66,white,true);txt(c,67,210,1450,64,'10月10日 14:00 · 归还不等于可领；下一位等检查完成后再接手。',28,'#B6CDCA');
const origin=505,scale=25;for(let i=0;i<=4;i++){const x=origin+i*10*scale;txt(c,x-47,302,99,42,'14:'+String(i*10).padStart(2,'0'),24,'#B6CDCA');c.line(x,348,x,881,'#496068',1,{opacity:.45});}
const rows=[{id:'T01',title:'测距仪',holder:'小林',until:15,next:'阿青',ready:20},{id:'T02',title:'夹具',holder:'阿青',until:30,next:'小满',ready:35},{id:'T03',title:'工作灯',holder:'库内',until:10,next:'老周',ready:10}];
rows.forEach((r,i)=>{const y=371+i*175;c.circle(100,y+50,33,i===2?gold:blue);txt(c,72,y+29,71,43,r.id,21,'#173C41',true);txt(c,155,y+7,304,66,r.title,40,white,true);txt(c,157,y+78,317,55,i<2?r.holder+'持有 · 14:'+String(r.until).padStart(2,'0')+'归还':'库内 · 管理员登记后领取',25,'#B6CDCA');
c.rect(origin,y,r.until*scale,106,i===2?'#9DAEB0':blue,{radius:9});txt(c,origin+15,y+16,r.until*scale-30,70,i===2?'库内可领':r.holder+'使用中',28,'#16363C',true);
if(i<2){c.rect(origin+r.until*scale,y,5*scale,106,gold);txt(c,origin+r.until*scale+11,y+17,105,79,'检查\n5分钟',24,'#463E28',true);}
const nx=origin+r.ready*scale;c.rect(nx,y,(40-r.ready)*scale,106,red,{radius:9});txt(c,nx+12,y+13,(40-r.ready)*scale-22,80,r.next+'\n14:'+String(r.ready).padStart(2,'0')+(i===1?'':'领取'),i===1?22:28,'#412F2D',true);if(i===1)txt(c,157,y+117,317,44,'小满 · 14:35领取',24,'#B6CDCA');});
c.rect(65,938,1470,105,'#24484C',{radius:15});txt(c,86,946,1428,87,'T01 / T02：归还 → 管理员检查5分钟 → 下一位领取\nT03已在库：14:10完成领取登记，无待归还检查时段。',27,white);
footer(c,'自拟工坊借还排程 · 时间带25像素/分钟 · 预约不代表实物已在库 · 未接入实时库存','#B6CDCA');
save('case-08',c,{goal:'看清三件工具的持有人、归还/检查/可领时间，按各自下一动作交接',intent:'时间像资源交接的接力带，所有者、5分钟检查和下一位用不同色段与文字同步呈现',checks:{T01_return:'14:15',T01_check:'14:15–14:20',T01_next:'14:20',T02_return:'14:30',T02_check:'14:30–14:35',T02_next:'14:35',T03:'already in stock, pickup registration14:10',px_per_minute:25}});
}
// 09: A notice that prioritises scope/date/window and makes restoration conditional.
{
const c=new Canvas(1200,1500,{background:'#F7F8EF'}),navy='#223F56',yellow='#F0C86B',muted='#5A6D74';header(c,'09','明天停水，\n先看与你有关的','发布10月10日 · 南苑供水设施例行维护（演示）',navy);
c.rect(65,375,1070,203,navy,{radius:18});txt(c,89,389,805,54,'10月11日  /  星期日',32,'#F7F8EF',true);txt(c,87,452,1044,112,'10:00 — 12:00',71,'#F7F8EF',true);
txt(c,66,617,800,57,'受影响：2号楼、3号楼',42,navy,true);txt(c,872,624,267,47,'1号楼不受影响',26,muted,true);
function building(x,n,fill){c.rect(x,704,296,193,fill,{radius:8});for(let row=0;row<3;row++)for(let col=0;col<4;col++)c.rect(x+21+col*68,720+row*44,42,23,'#FFFFFF',{radius:2});txt(c,x+21,851,250,45,n+'号楼',31,navy,true);}
building(65,2,yellow);building(394,3,yellow);building(826,1,'#DDE4DD');
const steps=[['今晚','按个人需求准备明日用水'],['明日10:00前','安排洗衣等用水事项'],['预计12:00后','先看管理处恢复公告；延迟另行通知']];
steps.forEach((r,i)=>{const y=956+i*116;c.circle(90,y+34,23,navy);txt(c,74,y+14,39,43,String(i+1),26,'#FFFFFF',true);txt(c,135,y-3,983,49,r[0],29,navy,true);txt(c,136,y+46,975,61,r[1],28,muted);});
txt(c,66,1320,1060,86,'预计停水2小时，恢复时间以公告为准。\n咨询：管理处1层服务台 · 08:00–18:00',27,navy,true);
footer(c,'全部场所、日期与安排为自拟演示 · 非真实公告 · 未进行住户测试',muted);
save('case-09',c,{goal:'判断自己楼栋是否受影响，核10月11日两小时时窗并知道恢复需看公告',intent:'深蓝时间巨字、两栋受影响的黄色楼体和三阶段行动形成可扫描的公告',checks:{date:'2026-10-11',published:'2026-10-10',affected:[2,3],unaffected:1,duration_hours:2,restoration:'estimated12:00, check notice'}});
}
// 10: Exact capacity strip, then four GB from the downloads category, preserving photo/video categories.
{
const c=new Canvas(1500,1120,{background:'#EEEFF7'}),purple='#493F72',secondary='#6D6981',colors=['#7B7C92','#B09ACA','#8DABD0','#79B6AC','#E7B475','#D9DEEA'];
txt(c,65,32,1370,47,'把信息变成下一步   /   日常信息实验 10',23,secondary,true);txt(c,65,98,1370,115,'先腾出4GB，不碰家庭照片',62,purple,true);txt(c,67,220,1360,65,'从已确认可再获取的下载文件开始；先核备份，再手动选择。',28,secondary);
txt(c,66,324,680,62,'当前：54GB已用 / 10GB可用',31,purple,true);txt(c,830,324,605,62,'目标：50GB已用 / 14GB可用',31,purple,true);
const segments=plan.cases.find(p=>p.id==='case-10').data.segments,scale=1360/64;let x=70;segments.forEach((s,i)=>{const w=s[1]*scale;c.rect(x,410,w,154,colors[i]);txt(c,x+8,429,w-16,49,s[0],27,i===0?'#FFFFFF':purple,true);txt(c,x+8,493,w-16,51,s[1]+'GB',30,i===0?'#FFFFFF':purple,true);x+=w;});
txt(c,70,578,900,43,'总容量64GB · 所有区段按同一GB口径成比例',24,secondary);
const dx=70+46*scale;c.line(dx,406,dx,581,purple,3);c.line(dx+8*scale,406,dx+8*scale,581,purple,3);c.arrow(dx+4*scale,651,dx+4*scale,600,purple,4,{headLength:14});txt(c,952,660,480,49,'下载8GB中选择4GB',29,purple,true);
const steps=[['01  先核备份','确认重要文件已有\n可访问的备份。\n家庭照片与视频保留。'],['02  再看清单','逐项查看下载列表，\n只选已确认可再获取的文件。'],['03  手动确认','核对所选约4GB，再手动删除。\n实际可释放量以设备为准。']];
steps.forEach((s,i)=>{const px=65+i*465;c.card(px,748,440,244,'#FFFFFF',{radius:18});txt(c,px+21,766,398,60,s[0],32,purple,true);txt(c,px+23,838,392,142,s[1],27,secondary);});
footer(c,'自拟容量案例 · 不是实机扫描或自动删除 · 54−4=50，10+4=14 · 未进行用户实验',secondary);
save('case-10',c,{goal:'读64GB组成，在确认备份后从下载区选择可再获取的4GB，理解可用量10到14变化',intent:'容量成为一条完整货架，等比分类与下载局部目标连接到三个可执行的整理步骤',checks:{segments,scale_px_per_gb:scale,total:64,used_before:54,free_before:10,clear:4,used_after:50,free_after:14,download_total:8}});
}
wx('production-notes-v002.json',JSON.stringify({started,actual_docs:['B06四源与inputs完整读取','shared-doc-000001 actual guide reread','dsl-README and actual parser cache excerpts'],no_assets:true,local_read_failure:'Attempted nonexistent B01/root/build-v001; no mutation or HTTP. Parser heading regex returned no match; switched to actual cache opening.',platform_interruption:'Previous independent auditor usage-limit message; no audit completed after B06 plan. Root resumed same run2026-10-07, prior state retained.',case08_plan_clarification:'T01/T02 returned instruments get5min check; T03 already in stock, pickup registration14:10. No fake missing check interval.'},null,2)+'\n');
console.log(JSON.stringify({started,cases:['case-01','case-08','case-09','case-10']}));
