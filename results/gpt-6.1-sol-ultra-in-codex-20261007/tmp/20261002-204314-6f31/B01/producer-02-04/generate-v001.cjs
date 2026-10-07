'use strict';
const fs=require('fs');
const path=require('path');
const {Canvas,tag,matrix2d}=require('../../_suite/dsl.cjs');
const out=__dirname;
function save(name,value){fs.writeFileSync(path.join(out,name),value,{flag:'wx',encoding:'utf8'});}
function txt(c,x,y,w,h,t,s,col,extra={}){c.text(x,y,w,h,t,s,col,{lineHeight:1.15,...extra});}
function ring(c,x,y,r,col,width=2){c.circle(x,y,r,'transparent',{border:`${width} SOLID ${col}`});}
function ellipse(c,cx,cy,w,h,col,a=0){const rad=a*Math.PI/180;c.at(cx-w/2,cy-h/2,w,h,tag('Transform',{matrix:matrix2d(Math.cos(rad),Math.sin(rad),-Math.sin(rad),Math.cos(rad)),alignment:'CENTER'},tag('ClipOval',{clipBehavior:'ANTI_ALIAS'},tag('Container',{width:w,height:h,color:col}))));}
function star(c,x,y,r,col){c.line(x-r,y,x+r,y,col,2);c.line(x,y-r,x,y+r,col,2);}
function dotted(c,x1,y1,x2,y2,col,width=2){let n=Math.ceil(Math.hypot(x2-x1,y2-y1)/15);for(let i=0;i<n;i++){const a=i/n,b=Math.min((i+.45)/n,1);c.line(x1+(x2-x1)*a,y1+(y2-y1)*a,x1+(x2-x1)*b,y1+(y2-y1)*b,col,width);}}

// CASE 02: original spatial route / visitor timetable. No geographic claim.
{
 const c=new Canvas(1200,1500,{background:'#081622'}),ink='#ECF5F6',muted='#A9C0C7',orange='#FFAB73',teal='#6FCDC3';
 for(let i=0;i<58;i++){const x=50+(i*179)%1100,y=40+(i*131)%960;c.circle(x,y,i%5===0?2.2:1.2,i%3===0?'#6A9AA8':'#294657');}
 txt(c,64,48,650,42,'在地天文馆  /  HERE & BEYOND',24,teal,{bold:true,letterSpacing:1});
 txt(c,64,110,850,90,'把宇宙装进口袋',66,ink,{bold:true});
 txt(c,67,212,650,48,'90分钟参观路线 · 10:00–11:30',29,muted);
 c.rect(940,58,190,68,orange,{radius:34});txt(c,960,74,150,35,'首次来访',23,'#17232C',{bold:true,align:'CENTER'});
 txt(c,65,298,900,38,'1F 示意地图  /  跟随橙色箭头，时段已包含移动',23,muted);
 // A single curved-space floor plan: outer boundary and connecting concourse.
 c.rect(94,365,1012,600,'#102B39',{radius:120,border:'2 SOLID #365666'});
 c.rect(185,483,830,330,'#1A3A48',{radius:130});
 // Painted corridor establishes a clockwise sequence; rooms sit above it.
 const route=[[220,852],[220,650],[360,650],[360,460],[590,460],[815,460],[935,650],[935,852]];
 for(let i=1;i<route.length;i++)c.line(...route[i-1],...route[i],'#FFAB7333',28,{roundCaps:true});
 for(let i=1;i<route.length;i++)c.arrow(...route[i-1],...route[i],orange,4,{headLength:16,headWidth:7});
 // Telescope gallery, with telescope geometry inside the room.
 c.rect(125,528,325,234,'#153B4A',{radius:40,border:'2 SOLID #608B95'});
 txt(c,153,548,252,40,'01  观测舱',30,ink,{bold:true});
 txt(c,153,595,252,35,'10:00–10:20',23,teal);
 c.line(281,680,336,702,'#C4DCE0',22,{roundCaps:true});c.line(303,686,295,735,'#C4DCE0',5);c.line(295,709,267,735,'#C4DCE0',5);c.line(295,709,323,735,'#C4DCE0',5);c.circle(276,679,14,teal);
 txt(c,155,666,103,72,'看太阳系\n尺度模型',20,muted);
 // Light lab: organized star points rather than a generic chart.
 c.rect(470,371,276,230,'#173545',{radius:40,border:'2 SOLID #608B95'});
 txt(c,493,395,230,40,'02  星光实验室',27,ink,{bold:true});txt(c,493,441,230,35,'10:20–10:40',23,teal);
 const stars=[[510,522],[556,488],[604,537],[661,497],[704,540]];c.polyline(stars,'#567A8B',2);stars.forEach((p,i)=>star(c,...p,i===2?9:6,teal));txt(c,490,565,235,27,'动手拼出一组星座',18,muted);
 // Spherical theatre visual and seat-entry details.
 c.circle(902,640,166,'#173545',{border:'2 SOLID #608B95'});ring(c,902,640,145,'#365B6C',1);ring(c,902,640,118,'#365B6C',1);
 c.line(800,555,1005,718,'#32586A',1);c.line(797,718,1007,555,'#32586A',1);
 txt(c,782,548,240,42,'03  球幕剧场',30,ink,{bold:true,align:'CENTER'});txt(c,786,602,232,38,'10:45场 · 30分钟',24,orange,{align:'CENTER',bold:true});
 txt(c,788,658,228,62,'10:40出发前往\n10:45前完成入座',20,muted,{align:'CENTER'});
 // Entrance/exit landmarks are distinct; map has no ambiguous crossing.
 c.rect(136,811,175,77,'#F3EEE4',{radius:19});txt(c,150,832,147,35,'入口 / 10:00',22,'#15313E',{bold:true,align:'CENTER'});
 c.rect(847,811,185,77,'#F3EEE4',{radius:19});txt(c,861,832,157,35,'出口 / 11:30',22,'#15313E',{bold:true,align:'CENTER'});
 txt(c,443,831,328,38,'04  宇宙商店 · 离馆',25,ink,{bold:true,align:'CENTER'});txt(c,443,872,328,36,'11:15–11:30 / 可自由跳过',20,muted,{align:'CENTER'});
 c.line(596,901,596,944,teal,2);c.circle(596,924,4,teal);txt(c,401,921,390,32,'休息区位于中央连廊',19,muted,{align:'CENTER'});
 txt(c,65,1023,550,46,'你的90分钟，一眼排好',34,ink,{bold:true});
 const times=[['20','观测舱','10:00–10:20'],['20','星光实验室','10:20–10:40'],['05','移动与入座','10:40–10:45'],['30','球幕电影','10:45–11:15'],['15','商店与离馆','11:15–11:30']];
 const widths=[235,235,132,354,176],x0=65,y=1123;let x=x0;
 times.forEach((row,i)=>{const w=widths[i];c.rect(x,y,w-6,92,i===2?'#4A4950':i===3?'#386462':'#244453',{radius:14});txt(c,x+13,y+14,w-32,38,row[0]+' min',i===2?22:29,i===3?'#FFFFFF':ink,{bold:true});x+=w;});
 let yy=1251;times.forEach((row,i)=>{const col=i<3?0:1,j=i<3?i:i-3,xx=65+col*578;txt(c,xx,yy+j*51,545,36,`${row[2]}  ${row[1]}`,22,muted);});
 c.line(65,1436,1135,1436,'#294552',1);txt(c,65,1452,1070,28,'虚构展馆与场次 · 设计演示 · 地图为路线示意，不代表真实建筑或消防疏散图',17,'#7C9AA5');
 save('case-02-v001.snapshot',c.toString());
 const meta={case_id:'case-02',title:'在地天文馆 · 90分钟参观导览',dimensions:[1200,1500],audience:'首次到馆的个人或亲子参观者',viewing_environment:'入口数字立牌、购票后的手机行程预览',user_action:'在90分钟内按顺序参观两展厅并准时到球幕剧场入座后离馆',data_provenance:'全部展馆、场次、地图与文案均为自拟演示。纯DSL，无外部素材。',completion_criteria:['入口、出口与四段体验可识别；路线箭头连续且无交叉','20+20+5+30+15=90，10:00–11:30无空缺重叠','10:40移动、10:45前入座、10:45–11:15电影语义一致','各文本实际渲染后可读且不越界；说明示意图性质'],data_validation:{minutes:[20,20,5,30,15],total_minutes:90,intervals:['10:00–10:20','10:20–10:40','10:40–10:45','10:45–11:15','11:15–11:30'],map_route:route,source:'generated in this script'},visual_choice:'房间与圆形球幕构成原创建筑示意，橙色路线穿过深蓝空间；底部时间宽度按分钟比例绘制（11.8px/min）',status:'draft; root service rendering and real visual review pending'};
 save('case-02-content-v001.json',JSON.stringify(meta,null,2)+'\n');
 save('case-02-notes-v001.md','# 在地天文馆 · 90分钟参观导览\n\n'+meta.audience+'在'+meta.viewing_environment+'查看，目的是'+meta.user_action+'。\n\n'+meta.data_provenance+'\n\n'+meta.visual_choice+'。五段时间20+20+5+30+15=90，含移动，不把参观时长另加移动时间。未来场次与真实建筑均未使用。入口和出口独立标记，箭头按连续路线绘制。实际服务渲染、看图与最终判断由root补入，当前不能称完成。\n');
}

// CASE 03: a phone-scale plant-care decision interface.
{
 const c=new Canvas(900,1500,{background:'#F3F3E9'}),ink='#244333',green='#347C50',muted='#6B7767',light='#E4EADB',clay='#C57759';
 txt(c,48,42,360,42,'慢叶  /  LEAF SLOW',26,green,{bold:true,letterSpacing:1});txt(c,610,45,240,35,'周二 · 08:30',22,muted,{align:'END'});
 txt(c,48,115,700,75,'今天先看这盆',55,ink,{bold:true});txt(c,51,195,700,43,'龟背竹 · 客厅东窗 · 今日状态待确认',24,muted);
 // Original leaf architecture: central stems, tilted leaves, holes and a pot.
 c.oval(109,572,340,45,'#CCD7C3');
 c.line(271,556,282,344,'#3E6B42',10);c.line(282,434,185,344,'#3E6B42',8);c.line(282,450,395,383,'#3E6B42',8);c.line(277,530,176,463,'#3E6B42',8);
 ellipse(c,185,337,166,114,'#3E8053',-33);ellipse(c,295,309,151,184,'#2D6E47',21);ellipse(c,398,376,171,108,'#469264',-38);ellipse(c,167,465,155,108,'#54845E',30);
 [[170,309,13,33,-25],[215,328,11,29,20],[286,277,12,36,0],[323,313,10,31,-15],[386,351,13,28,30],[426,389,13,28,-20],[156,447,12,30,15]].forEach(([x,y,w,h,a])=>ellipse(c,x,y,w,h,'#F3F3E9',a));
 c.line(287,321,277,420,'#A3BD8D',2);c.line(182,338,254,400,'#A3BD8D',2);c.line(394,377,308,428,'#A3BD8D',2);c.line(166,464,264,521,'#A3BD8D',2);
 c.rect(193,524,168,104,clay,{radius:20});c.oval(191,510,172,42,'#D49072');c.oval(207,517,139,22,'#775340');c.rect(204,545,145,78,'#C57759',{radius:15});c.line(227,551,227,605,'#DAA58B',3);c.line(257,551,257,605,'#DAA58B',3);c.line(287,551,287,605,'#DAA58B',3);c.line(317,551,317,605,'#DAA58B',3);
 c.rect(518,302,332,269,'#E4EADB',{radius:32});txt(c,543,327,278,35,'先检查，不按日历浇水',23,ink,{bold:true});
 txt(c,544,389,269,84,'距上次记录\n6 天',32,green,{bold:true});txt(c,544,493,270,53,'天数仅供回顾\n是否浇水由土壤决定',20,muted);
 c.rect(48,673,804,344,'#FFFFFF',{radius:32,border:'1 SOLID #DDE4D7'});c.circle(98,727,23,green);txt(c,76,710,43,35,'01',20,'#FFFFFF',{bold:true,align:'CENTER'});
 txt(c,140,704,668,48,'确认土壤，再决定浇水',31,ink,{bold:true});txt(c,77,779,731,53,'把手指探入土表下约2cm，感受是否仍潮湿。',24,muted);
 c.line(449,860,449,979,'#DDE4D7',1);
 c.circle(98,888,8,'#689CAD');txt(c,121,867,300,39,'仍潮湿 → 今天不浇',24,ink,{bold:true});txt(c,79,923,338,58,'先放回原位，保持通风。\n明天再检查。',20,muted);
 c.circle(498,888,8,'#C58E4C');txt(c,521,867,287,39,'已干 → 缓慢浇透',24,ink,{bold:true});txt(c,479,923,329,70,'底孔少量出水后停止，\n倒掉托盘积水。',20,muted);
 txt(c,49,1073,660,42,'另外两盆，今天只观察',29,ink,{bold:true});
 function miniPlant(x,y,type){c.rect(x+17,y+55,43,38,'#9A765B',{radius:7});c.oval(x+15,y+49,48,16,'#B78B6C');if(type==='pothos'){c.line(x+37,y+55,x+36,y+4,green,3);ellipse(c,x+25,y+20,25,16,green,-32);ellipse(c,x+49,y+7,27,18,'#60965A',20);ellipse(c,x+44,y+41,23,15,green,-20);}else{c.line(x+38,y+54,x+36,y-2,'#527244',8);c.line(x+38,y+54,x+22,y+7,'#66895A',9);c.line(x+38,y+54,x+53,y+4,'#46643D',8);}}
 c.rect(48,1140,389,154,'#E4EADB',{radius:24});miniPlant(64,1169,'pothos');txt(c,151,1168,259,35,'绿萝 · 书架',25,ink,{bold:true});txt(c,151,1223,259,45,'观察叶片，暂不操作',20,muted);
 c.rect(463,1140,389,154,'#E4EADB',{radius:24});miniPlant(479,1169,'snake');txt(c,566,1168,259,35,'虎尾兰 · 门厅',25,ink,{bold:true});txt(c,566,1223,259,45,'确认盆底无积水',20,muted);
 c.rect(48,1350,804,75,green,{radius:24});txt(c,78,1368,744,40,'记录检查结果',29,'#FFFFFF',{bold:true,align:'CENTER'});
 txt(c,50,1451,800,28,'静态照护界面 · 植物与记录为演示，操作前确认盆土与实际状态',17,'#7B8473',{align:'CENTER'});
 save('case-03-v001.snapshot',c.toString());
 const meta={case_id:'case-03',title:'慢叶 · 今天先看这盆',dimensions:[900,1500],audience:'家里养三盆植物、容易按固定日期浇水的人',viewing_environment:'晨间手机照护清单，原设计可在约390px宽屏幕预览',user_action:'先检查龟背竹土壤，再选择等待或浇水，随后记录结果',data_provenance:'自拟品牌、植物清单、6天记录与当前时刻；照护文案为该演示界面的条件化指导，不假称传感器数据。纯DSL原创盆栽与叶片。',completion_criteria:['主植物与待确认状态清晰','6天仅为历史，不能读成必须今天浇水','潮湿与已干两分支明确；底孔与托盘要求可读','另两盆观察动作和记录按钮可见；静态性质声明','实际渲染叶片孔洞、茎、盆栽不遮挡正文'],data_validation:{plant_count:3,days_since_record:6,observed_soil_state:'unknown',branches:['still_moist: do not water today, check tomorrow','dry: water slowly until small drainage, empty saucer'],buttons:'visual static; no functional app claim'},visual_choice:'大幅原创龟背竹插画上接一条具体操作，白色决策区把土壤触感分成两个分支，底部只保留两项观察与一个记录动作',status:'draft; root service rendering and real visual review pending'};
 save('case-03-content-v001.json',JSON.stringify(meta,null,2)+'\n');save('case-03-notes-v001.md','# 慢叶 · 今天先看这盆\n\n'+meta.audience+'在'+meta.viewing_environment+'查看。用途：'+meta.user_action+'。\n\n'+meta.data_provenance+'\n\n'+meta.visual_choice+'。界面没有自动判定盆土，不以6天强迫浇水。绿色叶片、孔洞、茎和陶土花盆全部由DSL椭圆、矩形与线段生成。实际服务渲染、看图与最终判断由root补入。\n');
}

// CASE 04: editorial menu with fully priced ordering choices.
{
 const c=new Canvas(1200,1600,{background:'#F3E9D5'}),ink='#593525',muted='#89684F',clay='#B75735',line='#D8C5AA',light='#E9D9BC';
 txt(c,66,46,740,48,'溪边焙房  /  RIVERSIDE ROAST',28,ink,{bold:true,letterSpacing:1});txt(c,830,49,307,43,'10:00–18:00',23,muted,{align:'END'});c.line(66,111,1135,111,ink,2);
 txt(c,64,168,630,180,'喝一口，\n慢下来。',79,ink,{bold:true,lineHeight:1.04});txt(c,70,384,620,46,'现磨咖啡 / 每日烘焙 / 窗边片刻',25,muted);
 // Original cup: handle, body, coffee rim, saucer and rising steam.
 c.oval(747,430,356,57,'#DCC5A4');ellipse(c,1033,337,123,148,clay);ellipse(c,1032,337,71,99,'#F3E9D5');c.rect(778,249,245,191,clay,{radius:36});c.oval(777,225,246,75,'#C5754E');c.oval(794,237,213,47,'#5A3525');
 c.line(799,283,799,395,'#D88A62',7,{roundCaps:true});
 // Steam is a line-generated smooth polyline; no pre-rendered bitmap.
 for(let k=0;k<3;k++){const pts=[];for(let i=0;i<=18;i++)pts.push([833+k*48+Math.sin(i*.32+k)*10,214-i*6]);c.polyline(pts,'#B99C7A',3,{roundCaps:true});}
 txt(c,827,306,151,44,'溪 边',25,'#F3E9D5',{bold:true,align:'CENTER'});
 c.line(66,494,1135,494,ink,2);txt(c,66,535,650,50,'咖啡，选你熟悉的那一杯',33,ink,{bold:true});txt(c,847,543,285,41,'价格：¥ / 杯',23,muted,{align:'END'});
 c.line(766,620,766,1214,line,1);
 const drinks=[['01','浓缩 Espresso','双份 · 60ml · 仅热','20'],['02','美式 Americano','300ml · 热 / 冰','24'],['03','澳白 Flat white','200ml · 仅热 · 含乳','28'],['04','拿铁 Latte','300ml · 热 / 冰 · 含乳','30'],['05','橙香气泡浓缩','350ml · 仅冰 · 含果汁','32']];
 drinks.forEach((r,i)=>{const y=630+i*115;txt(c,66,y+7,54,37,r[0],20,clay,{bold:true});txt(c,132,y,471,44,r[1],29,ink,{bold:true});txt(c,132,y+52,485,34,r[2],22,muted);txt(c,641,y+4,82,48,r[3],34,ink,{bold:true,align:'END'});if(i<4)c.line(132,y+100,723,y+100,line,1);});
 txt(c,808,632,320,43,'今日烘焙',29,clay,{bold:true});txt(c,808,702,220,37,'肉桂卷',26,ink,{bold:true});txt(c,1054,702,75,37,'18',26,ink,{bold:true,align:'END'});txt(c,808,747,320,31,'含小麦 / 乳 / 蛋',19,muted);c.line(808,791,1129,791,line,1);
 txt(c,808,824,220,37,'黄油司康',26,ink,{bold:true});txt(c,1054,824,75,37,'16',26,ink,{bold:true,align:'END'});txt(c,808,869,320,31,'含小麦 / 乳 / 蛋',19,muted);
 c.rect(798,947,337,258,'#DFCAA5',{radius:22});txt(c,826,974,280,35,'午后组合',27,ink,{bold:true});txt(c,826,1025,280,41,'拿铁 + 肉桂卷',24,ink);txt(c,826,1070,178,61,'¥42',48,clay,{bold:true});txt(c,1005,1101,100,34,'原价48',19,muted);txt(c,826,1153,280,31,'默认标准奶 · 热 / 冰',19,muted);
 c.rect(66,1265,1069,193,'#E9D9BC',{radius:22});txt(c,91,1289,978,40,'按你的口味，再做一点调整',28,ink,{bold:true});
 txt(c,91,1356,464,36,'换燕麦奶 +¥4   /   加浓缩 +¥6',23,ink,{bold:true});txt(c,91,1406,470,30,'燕麦奶替换适用于澳白、拿铁',19,muted);
 txt(c,617,1356,491,36,'橙香：标准甜 / 半甜 / 无额外糖',21,ink,{bold:true});txt(c,617,1406,491,30,'果汁自带糖分；冰饮可选标准冰 / 少冰',18,muted);
 c.line(66,1504,1135,1504,ink,1);txt(c,67,1525,1068,28,'虚构品牌 · 演示菜单 · 组合42=30+18−6；加料费用另计 · 烘焙售完即止',17,muted);
 txt(c,67,1560,1068,26,'点单示例：冰拿铁换燕麦奶 ¥34；午后组合换燕麦奶 ¥46。',17,muted);
 save('case-04-v001.snapshot',c.toString());
 const meta={case_id:'case-04',title:'溪边焙房 · 完整点单菜单',dimensions:[1200,1600],audience:'正在吧台排队或桌边选择饮品的顾客',viewing_environment:'店内立牌或手机菜单预览',user_action:'选择咖啡、温度、适用换奶/加浓缩与甜度冰量，清楚知道单品和组合总价',data_provenance:'自拟品牌、营业时间、配方容量、价格和过敏原；无客户部署或真实门店背书。纯DSL原创建模杯具，不含外部素材。',completion_criteria:['五种咖啡各有名称、容量、温度和价格','糕点、价格和所含小麦/乳/蛋清晰','组合42=30+18−6，换燕麦奶组合46，单独冰拿铁换燕麦奶34','换奶适用范围、甜度与果汁自含糖说明不歧义','实际看图菜单正文、杯具、价格列不遮挡越界'],data_validation:{drinks:drinks.map(d=>({name:d[1],description:d[2],price:Number(d[3])})),pastries:[{name:'肉桂卷',price:18},{name:'黄油司康',price:16}],combo:{latte:30,roll:18,discount:6,total:42},options:{oat:4,extra_espresso:6},examples:{oat_iced_latte:34,oat_combo:46},currency:'CNY (fictional prices)'},visual_choice:'陶土色大杯具与克制编辑排版形成温暖咖啡馆气氛；左侧五杯纵向价格列、右侧烘焙与组合、底部定制规则，让顾客沿自然阅读顺序完成点单',status:'draft; root service rendering and real visual review pending'};
 save('case-04-content-v001.json',JSON.stringify(meta,null,2)+'\n');save('case-04-notes-v001.md','# 溪边焙房 · 完整点单菜单\n\n'+meta.audience+'在'+meta.viewing_environment+'查看。用途：'+meta.user_action+'。\n\n'+meta.data_provenance+'\n\n'+meta.visual_choice+'。价格算术逐项核验：30+18−6=42；30+4=34；42+4=46。菜单没有将半甜或无额外糖称为无糖，明确果汁自带糖分。实际服务渲染、看图与最终判断由root补入。\n');
}
save('production-evidence-v001.json',JSON.stringify({created_at:new Date().toISOString(),producer:'b01_cases_02_03_04',run_id:'20261002-204314-6f31',source_reads:['tasks/B01-ten-real-world-showcases/TASK.md','tasks/B01-ten-real-world-showcases/AGENTS.md','tasks/B01-ten-real-world-showcases/task.json','tasks/B01-ten-real-world-showcases/run-config.json','tasks/B01-ten-real-world-showcases/inputs/README.md','run-config.json','tmp/20261002-204314-6f31/_suite/shared-doc-000001-response.txt','tmp/20261002-204314-6f31/_suite/shared-doc-000004-readable.txt','tmp/20261002-204314-6f31/_suite/dsl.cjs','tmp/20261002-204314-6f31/_suite/dsl-README.md'],tools:'PowerShell file reads; apply_patch authoring; Node pure-DSL generation; no HTTP, render, image view or public state mutation',files:['case-02-v001.snapshot','case-03-v001.snapshot','case-04-v001.snapshot'],asset_policy:'pure DSL chosen within DSL-primary supporting-assets policy',status:'drafts waiting for root rendering'},null,2)+'\n');
console.log(JSON.stringify({created:['case-02-v001.snapshot','case-03-v001.snapshot','case-04-v001.snapshot'],dimensions:[[1200,1500],[900,1500],[1200,1600]],directory:out}));
