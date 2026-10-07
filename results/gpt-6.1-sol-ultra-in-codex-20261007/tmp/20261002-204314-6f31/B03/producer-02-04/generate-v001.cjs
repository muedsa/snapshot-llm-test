'use strict';
const fs=require('fs'),path=require('path');
const {Canvas,tag,position}=require('../../_suite/dsl.cjs');
const plan=JSON.parse(fs.readFileSync(path.join(__dirname,'../plan-v001.json'),'utf8'));
const selected=process.argv[2]??'all';
function save(n,v){fs.writeFileSync(path.join(__dirname,n),v,{flag:'wx',encoding:'utf8'});}
function t(c,x,y,w,h,s,size,col,options={}){c.text(x,y,w,h,s,size,col,{lineHeight:1.12,...options});}
function clippedStack(c,x,y,w,h,parts,clip='ClipOval'){c.at(x,y,w,h,tag(clip,{clipBehavior:'ANTI_ALIAS'},tag('Container',{width:w,height:h},tag('Stack',{fit:'EXPAND',clipBehavior:'HARD_EDGE'},parts))));}
function body(c){return c.children.join('\n');}
function finalize(n,c,m,technique){
 const id=`case-${n}`,dsl=c.toString(),count=(dsl.match(/<[A-Za-z]/g)||[]).length;if(count>=4096)throw new Error('Element cap exceeded');
 save(`${id}-v001.snapshot`,dsl);
 const meta={task_id:'B03',run_id:'20261002-204314-6f31',case_id:id,title:m.title,dimensions:[c.width,c.height],audience:m.audience,use_context:m.use_context,user_goal:m.user_goal,visual_intent:m.visual_intent,content_basis:m.content_basis,completion_criteria:m.completion_criteria,creative_started_at:plan.case_creative_starts[id],creative_time_scope:'共同作品方案启动至交付（含并行）',created_at:new Date().toISOString(),dsl_capabilities:technique.capabilities,checks:{...m.checks,element_count:count,element_limit:4096,external_images:0,actual_visual_review:null,actual_visual_review_reason:'本代理只生成DSL；root串行真实服务、实际打开PNG后再写通过证据。'},technique_evidence_file:`${id}-technique-v001.md`};
 save(`${id}-metadata-v001.json`,JSON.stringify(meta,null,2)+'\n');
 save(`${id}-technique-v001.md`,`# ${m.title}\n\n${m.visual_intent}\n\n文档依据：已实际阅读缓存shared-doc-000004-readable.txt（来自https://snapshot.muedsa.com/ Parser参考），其中${technique.documentation}。共享dsl.cjs只序列化字符串，不渲染图像。\n\n算法与数据：${technique.algorithm}\n\n应用：${m.user_goal}\n\n已知边界：${technique.limitations} 当前未由本代理请求服务或看图，真实能力成立与视觉阅读性必须由root实图确认。元素${count}，低于4096。原稿与脚本保留，所有主体/文本均DSL，不含Image资产。\n`);
 console.log(JSON.stringify({case_id:id,snapshot:path.join(__dirname,`${id}-v001.snapshot`),metadata:path.join(__dirname,`${id}-metadata-v001.json`),elements:count}));
}

if(selected==='all'||selected==='02'){
 const c=new Canvas(1400,1000,{background:'#F0EFDE'}),ink='#244B35',olive='#727C51',white='#FAF9EE';
 t(c,50,37,700,39,'青坡种子交换 / SEED SWAP',22,ink,{bold:true,letterSpacing:1});
 t(c,49,100,900,82,'沿着叶脉，找到下一季。',55,ink,{bold:true});t(c,1010,46,338,64,'11.01 / SUN',34,ink,{bold:true,align:'END'});t(c,1010,119,338,39,'2026 · 14:00–16:00',23,olive,{align:'END'});
 c.line(50,217,1350,217,'#B9C3A5',2);t(c,50,243,550,43,'叶脉索引 / 交换目录',27,ink,{bold:true});t(c,661,243,688,40,'一袋换一袋，先核对名称、年份与粒数',23,ink);
 const leaf=new Canvas(500,530,{background:'transparent'});leaf.rect(0,0,500,530,'#316E42',{gradientType:'LINEAR',gradientColors:'#779962,#205638',gradientBegin:'TOP_LEFT',gradientEnd:'BOTTOM_RIGHT'});
 const veinData={spine:[],branches:[]};function spine(y){return 250+17*Math.sin((y-28)/484*Math.PI);}
 for(let k=0;k<=32;k++){const y=28+k*484/32;veinData.spine.push([spine(y),y]);}leaf.polyline(veinData.spine,'#DBE1A5',5);
 for(let j=0;j<9;j++){const y=90+j*45;for(const side of [-1,1]){const x=spine(y),length=(180-4*Math.abs(j-4))*side,dy=-44;const points=[];for(let k=0;k<=6;k++){let q=k/6;points.push([x+length*q,y+dy*q-9*Math.sin(q*Math.PI)]);}leaf.polyline(points,'#C0D398',2.3);let subs=[];for(let k=1;k<=4;k++){const q=k/5,px=x+length*q,py=y+dy*q-9*Math.sin(q*Math.PI);const end=[px+side*(23+4*k),py-24];leaf.line(px,py,...end,'#A8C385',1.2);subs.push([[px,py],end]);}veinData.branches.push({side,node:[x,y],points,secondary:subs});}}
 // Veins continue to the oval edge and are genuinely clipped there.
 clippedStack(c,60,304,500,530,body(leaf));c.line(309,818,296,857,ink,4,{roundCaps:true});
 t(c,71,876,503,53,'计算叶脉 / 形态插画\n不是物种标本或科学测量',19,olive,{align:'CENTER'});
 const seeds=[{name:'紫苏',count:20,year:2026,wants:'花卉种子',color:'#685A45',shape:'round'},{name:'罗勒',count:12,year:2026,wants:'香草种子',color:'#3E4C3B',shape:'tiny'},{name:'金盏菊',count:15,year:2025,wants:'紫苏种子',color:'#9A733F',shape:'curved'},{name:'旱金莲',count:8,year:2026,wants:'罗勒种子',color:'#857652',shape:'large'}];
 seeds.forEach((s,i)=>{const y=306+i*142;c.rect(655,y,694,122,white,{radius:20,border:'1 SOLID #C8CEB4'});const sample=new Canvas(92,92,{background:'transparent'});sample.rect(0,0,92,92,'#E0E1C8');for(let k=0;k<5;k++){const xx=21+(k*29)%58,yy=22+(k*19)%55;if(s.shape==='curved'){sample.circle(xx,yy,9,s.color);sample.circle(xx+4,yy-2,7,'#E0E1C8');}else sample.oval(xx-7,yy-5,s.shape==='large'?16:12,s.shape==='tiny'?6:11,s.color);}clippedStack(c,672,y+15,92,92,body(sample));t(c,788,y+17,273,38,`0${i+1}  ${s.name}`,28,ink,{bold:true});t(c,788,y+68,314,31,`纸袋 ${s.count}粒  /  ${s.year}年示例`,20,olive);t(c,1111,y+18,206,38,'想换',20,olive,{bold:true});t(c,1111,y+66,206,33,s.wants,23,ink,{bold:true});});
 c.line(50,932,1350,932,'#B9C3A5',1);t(c,50,948,1300,35,'青坡社区花园南门长桌（虚构） · 带已标注纸袋 → 双方核对 → 登记交换 · 所有品类/数量均为自拟演示，不保证发芽率',17,ink);
 save('case-02-vein-data-v001.json',JSON.stringify({algorithm:'curved spine and9 bilateral branch pairs,4 secondary veins each',...veinData},null,2)+'\n');
 finalize('02',c,{title:'种子交换 · 叶脉索引',audience:'参加社区种子交换、需要比较和登记纸袋种子的居民',use_context:'交换长桌上的横向目录牌，近距阅读；展示植物形态与交换记录',user_goal:'比较四袋名称、粒数、年份与想换品类，带标注纸袋到指定时地完成双方核对和交换',visual_intent:'算法叶脉形成具有生长张力的左侧视觉索引，右侧四个ClipOval种子形态窗配结构化信息；绿色与纸色让交换目录具有标本册感',content_basis:'活动、地点与交换记录全部自拟；名称为常见种子类别，形态为原创抽象插画，年份/数量非真实库存，未陈述科学测量或发芽率。',completion_criteria:['四种种子名称/粒数/纸袋/年份/想换品类可比较','11月1日周日14:00–16:00与虚构地点清楚','一袋换一袋、先核对再登记的动作完整','叶脉与标本窗是真正DSL计算/ClipOval，不嵌入预绘图','可视说明与表格无遮挡，root真实看图'],checks:{seed_records:seeds,total_example_seeds:55,exchange:'one labelled paper bag for one labelled paper bag; mutual verification',event:{date:'2026-11-01',weekday:'Sunday',time:['14:00','16:00'],venue:'青坡社区花园南门长桌（虚构）'},vein_model:{spine_segments:32,bilateral_pairs:9,secondary_segments:72,scientific_measurement:false}}},{capabilities:['computed branch geometry','ClipOval specimen windows','Transform line segments','Container gradient','Text/Raw catalogue'],documentation:'ClipOval采用ANTI_ALIAS裁剪；Stack/Positioned组合定位；Transform是16值列主序矩阵；Container支持LINEAR gradient；Text/Raw保留文本',algorithm:'主脉x(y)=250+17sin((y−28)/484π)，32段；9对侧脉各6段并各4条次脉，总18条侧脉、72条次脉；ClipOval固定边界。目录20+12+15+8=55粒示例；交换不按粒数计价。',limitations:'图形不是植物形态学测量或真实种子照片；任何发芽率、品系纯度与科学尺寸均未主张。交换记录是演示，不显示真实库存。'});
}

if(selected==='all'||selected==='03'){
 const c=new Canvas(1200,1600,{background:'#F4EFD9'}),ink='#182342',blue='#3157BD',red='#E34E36';
 t(c,58,45,1080,43,'字在场 / INDEPENDENT BOOK FAIR',27,ink,{bold:true,letterSpacing:1});c.line(58,111,1142,111,ink,2);
 t(c,60,145,1080,40,'字成为形，书成为相遇的地方。',25,ink);
 // Text remains real text. Offset outline layers give it spatial presence.
 const art='字在场',sx=47,sy=244,sw=1115,sh=408,sz=337;
 t(c,sx+16,sy+20,sw,sh,art,sz,'#CCBFA0',{bold:true,textShadow:'6 8 3 #8F806B55'});
 t(c,sx+10,sy+11,sw,sh,art,sz,blue,{bold:true,foregroundColor:blue,foregroundMode:'STROKE',foregroundStrokeWidth:5});
 t(c,sx,sy,sw,sh,art,sz,ink,{bold:true,foregroundColor:ink,foregroundMode:'STROKE',foregroundStrokeWidth:4.5});
 // A thin red underline provides a quiet reading direction beneath the sculpture.
 c.rect(58,683,1084,10,red);t(c,58,722,1084,71,'把阅读，放进现实。',48,ink,{bold:true});
 c.line(58,839,1142,839,ink,2);t(c,58,875,606,79,'2026 / 11.07–11.08',43,ink,{bold:true});t(c,757,881,385,62,'每日 12:00–19:00',29,ink,{bold:true,align:'END'});
 t(c,60,986,1080,49,'东栈1号 · 旧仓厅（虚构）',33,ink,{bold:true});t(c,60,1049,1080,39,'免费入场 · 无需预约 · 纸书、小刊与独立出版',24,ink);
 const activities=[['12:00–19:00','独立出版市集','翻阅小刊，与作者聊聊。'],['14:00–15:00','编辑对谈','听见一本书如何被做出。'],['16:00–17:00','小册装订体验','把一张纸折成自己的刊。']];
 activities.forEach((r,i)=>{const x=58+i*367;c.line(x,1133,x+335,1133,i===1?blue:red,5);t(c,x,1160,335,40,r[0],24,ink,{bold:true});t(c,x,1220,335,45,r[1],29,ink,{bold:true});t(c,x,1285,335,66,r[2],22,ink);});
 t(c,58,1388,1084,43,'以上活动两天同一时段；现场自由参加，体验席位按到场顺序。',23,ink);
 c.line(58,1470,1142,1470,ink,1);t(c,58,1500,1084,61,'自拟书展、地址、活动与参展内容 · 设计演示，未真实举办\n主视觉由Text前景描边、偏移层和文字阴影构造，无图片文字后处理',18,ink);
 finalize('03',c,{title:'字在场 · 独立书展',audience:'对独立出版、小刊和手工书感兴趣的城市读者',use_context:'竖版街区海报、活动页主视觉；近距详情阅读',user_goal:'识别展期地点、免费参与条件及每日三个活动时段后决定到访',visual_intent:'巨大的真实汉字以墨色outline、钴蓝偏移描边和纸色文字阴影成为立体雕塑；文字仍承担主题而非转成光栅资产，下半部秩序清楚地组织时地与活动',content_basis:'展览、地址、活动和免费入场规则全部自拟演示，未举办；2026-11-07/08为真实日历日期，不虚构参展者背书。',completion_criteria:['字在场主标题可识别且前景STROKE实际成立','2026-11-07至08、每日12:00–19:00、虚构地址清楚','三活动时间均在开放时段内，两天同一时段说明清楚','免费/无需预约/体验到场顺序不矛盾','outline装饰不遮挡底部必要信息，真实看图证据'],checks:{event_dates:['2026-11-07','2026-11-08'],weekdays:['Saturday','Sunday'],opening:['12:00','19:00'],activities:activities,admission:'free; no reservation; seats by arrival',text_layers:{main:'STROKE width4.5',blue_offset:[10,11],back_offset:[16,20],shadow:'6 8 3 #8F806B55'},actual_visual_review:null}},{capabilities:['foreground STROKE typography','textShadow','offset layered Text','Text/Raw copy','editorial absolute layout'],documentation:'Text只有设foregroundColor后才能使用foregroundMode与foregroundStrokeWidth；STROKE为合法模式；textShadow格式x y blurSigma color；文字仍可通过Raw CDATA完整保存',algorithm:'主标题使用相同337字号汉字，底层偏移(16,20)并加文字阴影，中层钴蓝STROKE偏移(10,11)，顶层墨色STROKE宽4.5；三组真实Text相同内容，因此不是图像后处理。展期两天，每日12–19；14–15与16–17都在展时内。',limitations:'偏移是静态排版，不是交互或真正3D模型；字形由服务实际字体Inter,Noto Sans CJK SC提供，描边空腔/阴影质量须实图检验。此处不宣称图像透明文字或隐藏显示能力。'});
}

if(selected==='all'||selected==='04'){
 const c=new Canvas(1500,1000,{background:'#081F38'}),light='#DBF5F3',muted='#91B5C4',orange='#FFA36D';
 t(c,48,40,1000,37,'蓝屿水族馆 / BLUE ISLE AQUARIUM',24,light,{bold:true,letterSpacing:1});t(c,48,103,1050,76,'潜入蓝色，慢慢看。',52,light,{bold:true});t(c,1060,108,390,42,'一层首访路线 · 建议45分钟',23,muted,{align:'END'});
 const centers=[250,750,1250];
 function fish(layer,x,y,w,col){layer.oval(x-w/2,y-w*.22,w,w*.44,col);layer.line(x-w/2+3,y,x-w*.75,y-w*.2,col,w*.16);layer.line(x-w/2+3,y,x-w*.75,y+w*.2,col,w*.16);layer.circle(x+w*.27,y-2,2.5,'#102B4B');}
 function makeScene(kind){const s=new Canvas(380,380,{background:'transparent'});s.rect(0,0,380,380,'#175975',{gradientType:'LINEAR',gradientColors:'#358E9A,#103E63',gradientBegin:'TOP_CENTER',gradientEnd:'BOTTOM_CENTER'});
  // Outer porthole contains a mid-distance oval, itself containing a far oval.
  const middle=new Canvas(318,318,{background:'transparent'});middle.rect(0,0,318,318,'#1D6282');
  const far=new Canvas(220,220,{background:'transparent'});far.rect(0,0,220,220,'#163D69',{gradientType:'RADIAL',gradientColors:'#3C8296,#123358',gradientCenter:'CENTER',gradientRadius:.7});fish(far,122,107,56,'#5AA6B1');fish(far,67,160,35,'#427A97');
  clippedStack(middle,58,41,220,220,body(far));middle.oval(48,225,283,125,'#17516C');clippedStack(s,33,30,318,318,body(middle));
  // Front stage extends across the nested circles but remains in the outer crop.
  s.oval(-30,300,430,130,'#0C3451');
  if(kind===0){
   s.line(91,338,92,264,'#E28B67',11,{roundCaps:true});s.line(92,284,52,248,'#E28B67',8,{roundCaps:true});s.line(91,295,128,250,'#E28B67',8,{roundCaps:true});s.line(110,272,126,230,'#E28B67',6,{roundCaps:true});
   [[248,298,32],[280,280,27],[301,311,23]].forEach(([x,y,r])=>s.circle(x,y,r,'#83B9A9'));
   for(let j=0;j<4;j++)s.oval(140+j*22,293-j*14,42,61,'#4A9694');fish(s,188,181,90,'#F6CA80');
  }else if(kind===1){
   for(const [x,y,r,col] of [[120,141,42,'#C7DCED'],[244,180,32,'#82CACB']]){s.oval(x-r,y-r*.8,r*2,r*1.4,col);s.rect(x-r,y+r*.3,r*2,4,'#B2DADA',{radius:2});for(let j=0;j<6;j++){const pts=[];for(let k=0;k<=10;k++)pts.push([x-r*.7+j*r*.28+Math.sin(k*.4+j)*4,y+r*.4+k*(j%2===0?6:9)]);s.polyline(pts,col,2.5);}}
  }else{
   fish(s,230,241,109,'#A8CDBF');fish(s,149,282,62,'#337995');s.line(63,347,58,273,'#367F87',9,{roundCaps:true});s.line(78,347,90,254,'#367F87',7,{roundCaps:true});s.oval(234,327,121,69,'#174969');
  }
  for(let k=0;k<9;k++)s.circle(38+(k*47)%315,34+(k*31)%146,2+k%3,'#8ED4D566');return body(s);
 }
 centers.forEach((x,i)=>{c.circle(x,445,204,'#5C7F91',{border:'2 SOLID #82B9C5'});c.circle(x,445,194,'#14334D');clippedStack(c,x-190,255,380,380,makeScene(i));for(let j=0;j<8;j++){let a=j*Math.PI/4;c.circle(x+198*Math.cos(a),445+198*Math.sin(a),4,'#A7C6CC');}});
 const zones=[['01','浅礁窗口','找出三种不同轮廓','枝状 / 圆形 / 叶形'],['02','水母光廊','比较触须的长与短','停一会，观察两组线条'],['03','深蓝观察窗','从前景到远景找三层','鱼、岩石与更远的蓝']];
 zones.forEach((z,i)=>{const x=centers[i]-200;t(c,x,681,400,48,z[0]+'  '+z[1],32,light,{bold:true,align:'CENTER'});t(c,x,742,400,37,z[2],24,light,{align:'CENTER'});t(c,x,787,400,35,z[3],20,muted,{align:'CENTER'});});
 c.arrow(335,852,665,852,orange,3,{headLength:16,headWidth:7});c.arrow(835,852,1165,852,orange,3,{headLength:16,headWidth:7});centers.forEach((x,i)=>{c.circle(x,852,21,orange);t(c,x-19,837,38,33,String(i+1),23,'#082238',{bold:true,align:'CENTER'});});
 t(c,48,909,1404,37,'周二–周日 10:00–18:00 · 最后入馆17:00  /  蓝屿路8号（虚构）  /  沿编号顺行，每区约15分钟',21,light,{align:'CENTER'});
 t(c,48,961,1404,26,'自拟水族馆与路线 · 非真实建筑或物种测量 · 纯DSL静态深度插画，45分钟为自拟参观建议',17,muted,{align:'CENTER'});
 finalize('04',c,{title:'潜入蓝色 · 水族馆导览',audience:'第一次来水族馆、希望慢看三个主题窗口的参观者',use_context:'馆内横向路线说明屏，近距看图与观察任务阅读',user_goal:'沿01浅礁、02水母光廊、03深蓝窗依次观看，并通过轮廓/触须/前后层完成三项观察任务',visual_intent:'三层真正嵌套ClipOval构成舷窗里的前景/中景/远景；岩石、鱼和形态块依绘制顺序构成静态深度，三个观察任务把图形实验转为参观动作',content_basis:'蓝屿水族馆、虚构地址、开放规则与45分钟路线均为自拟；鱼/水母/珊瑚轮廓为原创抽象插画，不映射真实物种或科学测量。',completion_criteria:['三舷窗都有实际ClipOval嵌套而非只画圆边框','01/02/03标题、箭头和观察任务匹配','浅礁含枝状/圆形/叶形三种轮廓；水母有长短触须','开放时段与最后入馆17:00前后关系正确','15+15+15=建议45分钟，不冒称测量结果','地址虚构/静态深度/无科学测量声明清楚，实际看图完整'],checks:{route:zones,opening:{days:'Tuesday–Sunday',hours:['10:00','18:00'],last_admission:'17:00'},suggested_stop_minutes:[15,15,15],total_suggested_minutes:45,nested_clip_levels_per_scene:3,model_species:false,actual_visual_review:null}},{capabilities:['three-level nested ClipOval','Container gradients','Stack occlusion order','computed polyline tentacles','original fish/coral geometry','Transform route arrows'],documentation:'ClipOval最多一个子节点且可用ANTI_ALIAS；内部Container+Stack与Positioned形成真正子树裁剪；Container支持LINEAR/RADIAL渐变，参数不混用；Transform线与Opacity色值符合Parser',algorithm:'每个380px舷窗内，318px中景ClipOval再嵌220px远景ClipOval；先远景，再中景，再前景，按照Stack顺序遮挡。水母每组6条触须，交替6/9px每步长度，10步显式计算长短；建议每区15min共45min。',limitations:'这是静态平面遮挡形成的深度错觉，不声称真实3D或动态视差；形态不是物种准确复原，不报告生物尺寸/数量/生境事实。观察任务针对这张演示插画。'});
}
