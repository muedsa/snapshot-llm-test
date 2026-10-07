const fs=require('node:fs'),path=require('node:path');const {Canvas,P,T,header,footer,patch,stitch}=require('../project-system-v001.cjs');
fs.mkdirSync(__dirname,{recursive:true});const events=fs.readFileSync(path.join(__dirname,'../../_suite/events.jsonl'),'utf8').trim().split(/\r?\n/).map(JSON.parse);
function save(id,c,m){const start=events.find(e=>e.task_id==='B02'&&e.case_id===id&&e.type==='case-creative-start');fs.writeFileSync(path.join(__dirname,id+'-v001.snapshot'),c.toString(),{flag:'wx'});fs.writeFileSync(path.join(__dirname,id+'-metadata-v001.json'),JSON.stringify({id,...m,dimensions:[c.width,c.height],content_basis:'自拟再线RETHREAD社区项目；运营/地址/价格/数据/参与者均为静态设计演示，未部署。',creative_started_at:start.time,creative_start_scope:start.scope,created_at:new Date().toISOString(),supporting_assets:[]},null,2)+'\n',{flag:'wx'});}
// A complete street recruitment poster, oversized mended garment as identity.
{
 const c=new Canvas(1200,1600,{background:P.paper});header(c,'街区织补开放日');
 T(c,64,143,1070,152,'让旧衣，\n再走一段。',88,P.ink,true);T(c,68,384,980,51,'补一个洞，也把邻里重新连起来。',32,P.clay);
 c.rect(56,493,1088,559,P.ink,{radius:24});
 // Garment drawn with sleeves, collar cutout and repaired patch.
 c.rect(224,620,215,127,P.sage,{radius:16});c.rect(766,620,215,127,P.sage,{radius:16});c.rect(388,572,416,408,P.sage,{radius:28});c.circle(594,572,76,P.ink);c.circle(594,576,56,P.paper);c.rect(521,527,146,42,P.ink);
 for(let x=407;x<796;x+=23)c.line(x,957,x+10,957,P.paper,2);patch(c,622,749,140,134,P.clay);c.line(664,778,716,848,P.paper,3);c.line(653,813,722,813,P.paper,3);
 T(c,88,521,300,45,'穿过时间的补丁',25,P.paper,true);T(c,96,961,240,51,'带来一件\n想继续穿的旧衣',21,P.paper);
 T(c,64,1114,1070,63,'10月24日 周六  /  10:00–18:00',40,P.ink,true);T(c,66,1197,1040,49,'澄巷12号 · 再线社区工坊（虚构地址）',29,P.ink);
 const cells=[['先评估','带衣物，到评估台说明损伤。'],['再预约','45分钟基础体验 ¥30，含基础布料/线。'],['一起学','复杂损伤先评估报价，不先承诺修复。']];
 cells.forEach((a,i)=>{const y=1280+i*68;c.circle(82,y+21,17,P.clay);T(c,73,y+6,24,31,String(i+1),21,P.paper,true);T(c,120,y,171,44,a[0],26,P.ink,true);T(c,320,y+1,799,49,a[1],25,P.ink);});
 footer(c,'自拟项目/活动/地址/价格 · 静态设计演示 · 平日周三–周日10:00–18:00开放');
 save('case-01',c,{title:'再线 · 街区织补开放日',audience:'街区路过者与有旧衣修补需求的居民',use_context:'1200×1600街区招募海报，正文近看',user_goal:'理解项目、活动时间/地点、体验费用和先评估再预约的参与方式',visual_intent:'大幅原创修补衬衣使补丁成为品牌主张；三步招募信息帮助迈入工坊',completion_criteria:['活动与常规开放区分','45分钟¥30含材料条件明确','复杂先评估','大标题可远看，正文近读'],checks:{date:'2026-10-24',weekday:'Saturday',fee_cny:30,minutes:45}});
}
// A usable exchange catalogue, six distinct material/size/condition entries.
{
 const c=new Canvas(1600,1100,{background:P.paper});header(c,'织物交换目录');T(c,48,125,1440,76,'你留下的，也许正好被需要。',51,P.ink,true);T(c,52,214,1490,49,'10月24日示例库存 · 清洁织物1件换1张交换券；每件需先核验标签，瑕疵照实告知。',25,P.ink);
 const goods=[{id:'E01',name:'条纹棉布',mat:'棉100%',size:'60 × 80 cm',def:'一角有2cm磨损',col:P.sage,mode:0},{id:'E02',name:'深蓝牛仔布',mat:'棉98% / 弹性纤维2%',size:'45 × 55 cm',def:'褪色，边缘未锁',col:P.ink,mode:1},{id:'E03',name:'暖橙围巾',mat:'羊毛混纺，比例未确认',size:'30 × 140 cm',def:'2处轻微起球',col:P.clay,mode:2},{id:'E04',name:'格纹布片',mat:'材质待核验',size:'50 × 50 cm',def:'背面笔迹，不作肤贴用',col:P.sage,mode:3},{id:'E05',name:'亚麻餐垫一组',mat:'亚麻100%，标签自述',size:'35 × 45 cm / 2片',def:'一片边缘开线',col:'#A88768',mode:4},{id:'E06',name:'米色帆布袋',mat:'棉100%',size:'38 × 42 cm',def:'把手已有补缝',col:'#D6C7AD',mode:5}];
 goods.forEach((a,i)=>{const x=48+(i%3)*510,y=294+Math.floor(i/3)*350;c.rect(x,y,490,325,P.light,{radius:15,border:'1 SOLID #CFC3B0'});c.rect(x+25,y+35,139,168,a.col,{radius:6});stitch(c,x+36,y+46,117,146,a.col===P.ink?P.paper:P.ink);if(a.mode===0){for(let k=0;k<7;k++)c.line(x+27,y+48+k*20,x+161,y+48+k*20,P.paper,4);}if(a.mode===1){c.line(x+36,y+183,x+155,y+70,P.paper,2);patch(c,x+67,y+83,55,53,P.clay);}if(a.mode===2){for(let k=0;k<7;k++)c.line(x+38+k*17,y+202,x+38+k*17,y+229,P.clay,3);}if(a.mode===3){for(let k=0;k<6;k++){c.line(x+26,y+53+k*26,x+163,y+53+k*26,P.paper,2);c.line(x+33+k*24,y+35,x+33+k*24,y+201,P.paper,2);}}if(a.mode===4){c.rect(x+35,y+47,135,167,'#C3A386',{radius:3});stitch(c,x+45,y+57,115,147,P.paper);}if(a.mode===5){c.oval(x+62,y+19,66,48,P.ink);c.oval(x+69,y+25,52,42,P.light);c.rect(x+25,y+64,139,145,a.col,{radius:8});patch(c,x+68,y+102,52,51,P.sage);}
 T(c,x+190,y+24,271,43,a.id+'  /  '+a.name,24,P.ink,true);T(c,x+191,y+87,270,73,a.mat,21,P.ink);T(c,x+191,y+168,270,50,a.size,23,P.clay,true);T(c,x+25,y+252,441,53,'瑕疵：'+a.def,22,P.ink);});
 c.rect(48,1010,1504,35,P.ink,{radius:5});T(c,62,1013,1470,32,'交换台核验 → 登记入库 → 持券选1件  /  未确认材质保持“待核验”，不补造标签。',21,P.paper);footer(c,'自拟示例库存与交换规则 · 不提供实际商品或交易服务');
 save('case-08',c,{title:'再线 · 织物交换目录',audience:'想交换剩余织物、寻找修补材料的居民',use_context:'1600×1100交换台目录，平板/印刷近看',user_goal:'比较六件织物的材质、尺寸与瑕疵，持券选一件并在交换台核验',visual_intent:'六个原创织物/袋具图形形成样本架，但每个都有具体库存信息与可行动交换规则',completion_criteria:['6件唯一编号','每件材质/尺寸/瑕疵','未知材质不编造','1件1券1件规则清楚'],checks:{item_count:6,ids:goods.map(a=>a.id),items:goods,exchange_ratio:'1 accepted textile : 1 ticket : 1 selected item'}});
}
// September demo feedback: unit quilt plus truthful batch accounting.
{
 const c=new Canvas(1500,1100,{background:P.paper});header(c,'2026.09  ·  社区反馈');T(c,48,123,1340,71,'48份修补记录，织回一点日常。',48,P.ink,true);T(c,51,211,1350,44,'9月演示月报 · 同批记录统计；未测碳排或垃圾减量，不据此推算环境效益。',24,P.ink);
 const kpi=[['48','接收记录'],['44','已完成'],['4','待处理'],['18 h','志愿服务']];kpi.forEach((a,i)=>{const x=48+i*352;c.line(x,304,x+327,304,P.line,2);T(c,x,324,327,72,a[0],53,i===2?P.clay:P.ink,true);T(c,x,409,327,44,a[1],25,P.ink);});
 T(c,49,491,640,52,'每块补丁 = 1份接收记录',28,P.ink,true);
 for(let i=0;i<48;i++){const x=50+i%8*67,y=559+Math.floor(i/8)*67;c.rect(x,y,51,51,i<44?P.clay:P.paper,{radius:3,border:'2 SOLID #BC5338'});if(i<44){c.line(x+10,y+25,x+20,y+35,P.paper,3);c.line(x+20,y+35,x+41,y+12,P.paper,3);}}
 c.rect(50,986,26,26,P.clay,{radius:3});T(c,87,983,206,37,'已完成44份',21,P.ink);c.rect(319,986,26,26,P.paper,{border:'2 SOLID #BC5338'});T(c,356,983,231,37,'待处理4份',21,P.ink);
 T(c,705,491,713,51,'一周一周，核对进度',29,P.ink,true);T(c,709,551,230,36,'接收 / 完成',22,P.ink);c.rect(1240,556,20,15,P.sage);T(c,1268,548,143,31,'接收',19,P.ink);c.rect(1331,588,20,15,P.ink);T(c,1359,580,99,31,'完成',19,P.ink);
 const rec=[9,12,15,12],done=[8,11,14,11];for(let i=0;i<4;i++){const y=615+i*73;T(c,710,y-3,100,36,'第'+(i+1)+'周',23,P.ink);c.rect(828,y,rec[i]*24,20,P.sage,{radius:3});c.rect(828,y+28,done[i]*24,20,P.ink,{radius:3});T(c,1215,y,204,47,rec[i]+' / '+done[i],25,P.ink,true);}
 c.line(711,930,1439,930,P.line,1);T(c,711,949,726,57,'完成率 44 / 48 = 91.7%  ·  接收分类31贴补 / 11补缝 / 6纽扣',23,P.ink,true);T(c,710,1014,731,39,'参与者24位 · 志愿者9位；数量均为自拟样本。',20,P.ink);footer(c,'自拟9月样本记录 · 不代表实际社区成效 · 10月开放日信息见招募海报');
 save('case-09',c,{title:'再线 · 9月社区反馈',audience:'居民、志愿者与项目组织者',use_context:'1500×1100社区反馈板/平板近读',user_goal:'核对同批接收/完成/待处理记录与志愿时间，看到演示进度而不误信环保推算',visual_intent:'48块逐件补丁构成品牌数据隐喻，四周双条形核验进度',completion_criteria:['48块其中44实4空','周接收合计48/完成44','44/48=91.7%','31+11+6=48','明确9月演示与未测环境效益'],checks:{month:'2026-09',received:rec,completed:done,pending:4,volunteer_hours:18,participants:24,volunteers:9,type_counts:[31,11,6],completed_pct:91.7}});
}
// Volunteer shift board: three service lanes, overlap shown at real scale.
{
 const c=new Canvas(1600,1000,{background:P.paper});header(c,'10月24日  ·  志愿者班次');T(c,48,127,1488,77,'每个工位，有人接住。',54,P.ink,true);T(c,50,215,1470,47,'周六开放10:00–18:00 · 13:00–13:15双方在原工位交接 · 以下人员/岗位均为示例。',25,P.ink);
 const x0=455,scale=1004/525,at=m=>x0+m*scale;T(c,50,298,355,44,'工位 / 上午 → 下午',27,P.ink,true);
 [0,30,90,150,210,270,330,390,450,510,525].forEach(m=>{c.line(at(m),375,at(m),667,P.line,1);if([0,30,150,270,390,510,525].includes(m)){const hh=9+Math.floor((30+m)/60),mm=(30+m)%60;T(c,at(m)-25,319,99,45,`${String(hh).padStart(2,'0')}:${String(mm).padStart(2,'0')}`,19,P.ink);}});
 const roles=[['01','评估台','林 → 舟','损伤判断、预约费用确认'],['02','教学桌','岚 → 乔','演示针法、逐件完成检查'],['03','物料台','禾 → 宁','交换登记、工具借还归位']];
 roles.forEach((r,i)=>{const y=393+i*92;T(c,50,y,91,44,r[0],30,P.clay,true);T(c,142,y,284,39,r[1]+'  '+r[2],25,P.ink,true);T(c,142,y+43,291,42,r[3],18,P.ink);c.rect(at(0),y+9,225*scale,31,P.sage,{radius:4});c.rect(at(210),y+45,315*scale,31,P.ink,{radius:4});T(c,at(0)+15,y+8,360,32,'09:30–13:15  上午',19,P.paper,true);T(c,at(210)+15,y+44,471,32,'13:00–18:15  下午',19,P.paper,true);});
 c.rect(at(210),373,15*scale,299,'#BC533833');c.line(at(210),373,at(210),676,P.clay,2);c.line(at(225),373,at(225),676,P.clay,2);T(c,793,686,512,45,'交接15分钟：订单、工具、待办',23,P.clay,true);
 const cards=[['09:30','开门前','点工具、看当天预约\n确认评估/教学/物料台。'],['13:00','交接时','逐件核待办，不口头略过；\n双方确认编号与状态。'],['18:00','闭门后','停止接待，工具与物料归位；\n18:15核对后离开。']];
 cards.forEach((a,i)=>{const x=49+i*510;c.rect(x,768,490,168,P.light,{radius:12,border:'1 SOLID #CFC3B0'});T(c,x+24,787,155,45,a[0],29,P.clay,true);T(c,x+188,790,275,37,a[1],25,P.ink,true);T(c,x+25,848,441,74,a[2],22,P.ink);});footer(c,'自拟班次 · 工坊实际开放与岗位安排须由组织者确认 · 排班图为静态演示');
 save('case-10',c,{title:'再线 · 志愿者班次作战板',audience:'10月24日参与工坊的六位示例志愿者',use_context:'1600×1000工坊排班大屏，详细说明近读',user_goal:'找到岗位和班次，按15分钟双人在岗交接，完成开门/交接/闭门核对',visual_intent:'三工位双轨排程用真实时间比例显示15分钟重叠，职责和交接卡使排程可行动',completion_criteria:['三工位两班均在开放时段覆盖','09:30–13:15与13:00–18:15相交15分钟','比例1004/525px/min','10–18开放与前后准备收尾区分'],checks:{canvas_minutes:525,pixels_per_minute:scale,am:[0,225],pm:[210,525],overlap_minutes:15,opening:[30,510],role_count:3,people:6}});
}
