'use strict';
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const {Canvas,tag,matrix2d}=require('../../_suite/dsl.cjs');
const plan=JSON.parse(fs.readFileSync(path.resolve(__dirname,'../plan-v001.json'),'utf8'));
function save(n,v){fs.writeFileSync(path.join(__dirname,n),typeof v==='string'?v:JSON.stringify(v,null,2),{encoding:'utf8',flag:'wx'});}
function txt(c,x,y,w,h,t,s,col,b=false,align='START'){c.text(x,y,w,h,t,s,col,{bold:b,align});}
function polar(cx,cy,r,index,div=12){const a=-Math.PI/2+index/div*Math.PI*2;return[cx+r*Math.cos(a),cy+r*Math.sin(a)];}
function common(id,title,w,h,audience,context,goal,intent,criteria,basis){return{case_id:id,title,dimensions:[w,h],audience,use_context:context,user_goal:goal,visual_intent:intent,content_basis:{type:'fictional_demo',description:basis},creative_started_at:plan.case_creative_starts[id],creative_started_at_source:'B03/plan-v001.json case_creative_starts, originally recorded suite actual events',created_at:new Date().toISOString(),completion_criteria:criteria,checks:{visual_verified:false,service_request_by_this_agent:false,visual_review_owner:'root'},asset_sources:[]};}
function output(id,c,m,evidence){const d=c.toString(),count=(d.match(/<[A-Za-z][^>]*>/g)||[]).length;if(count>=4096)throw Error(id+' elements '+count);m.checks.start_elements=count;m.checks.static_algorithm_checks='passed';save(id+'-v001.snapshot',d);save(id+'-metadata-v001.json',m);save(id+'-technique-evidence-v001.json',evidence);save(id+'-content-v001.md',`# ${m.title}\n\n使用者：${m.audience}。环境：${m.use_context}。任务：${m.user_goal}。\n\n${m.visual_intent}\n\n${m.content_basis.description}\n\n完成标准：\n${m.completion_criteria.map(x=>'- '+x).join('\n')}\n\n当前是自包含纯DSL初稿，尚未渲染或看图。\n`);console.log(id+' ready, '+count+' starting elements');}
const doc={source:'tmp/20261002-204314-6f31/_suite/shared-doc-000004-readable.txt',provenance:'真实共享Parser参考复用；本代理实际读取，无新增HTTP',supported:['Container shape CIRCLE、gradientType/gradientColors/gradientStops、border','Positioned left/top/width/height under Stack','Transform.matrix16列主序，有限数','Opacity0–1与透明CSS八位颜色','Text/Raw/CDATA与多字体列表']};
function rehearsal(){const id='case-05',c=new Canvas(1500,1100,{background:'#181129'}),white='#F1ECFA',muted='#B6A7CC',cyan='#76E4DF',amber='#FFD286';
 c.rect(0,0,1500,1100,'transparent',{gradientType:'LINEAR',gradientColors:'#261947,#120E20',gradientBegin:'TOP_LEFT',gradientEnd:'BOTTOM_RIGHT'});
 txt(c,56,45,1320,36,'PULSE ROOM / 拍点排练室',19,cyan,true);txt(c,51,93,1340,83,'同一圈，三击对四击。',57,white,true);txt(c,56,190,1330,43,'12个等时小格 / 左手3击，右手4击 / 一圈后两手在起点再相遇',24,muted);
 const cx=478,cy=558,ro=249,ri=179;
 for(let k=0;k<12;k++){const a=polar(cx,cy,ri-12,k),b=polar(cx,cy,ro+26,k);c.line(...a,...b,'#624E7733',1);c.circle(...polar(cx,cy,ro+27,k),3,'#726185');const p=polar(cx,cy,ro+64,k);txt(c,p[0]-25,p[1]-17,50,38,String(k+1),21,white,k===0,'CENTER');}
 c.circle(cx,cy,ro,'transparent',{border:'2 SOLID #76E4DF77'});c.circle(cx,cy,ri,'transparent',{border:'2 SOLID #FFD28677'});
 const triple=[0,4,8],quad=[0,3,6,9];const tpts=triple.map(k=>polar(cx,cy,ro,k)),qpts=quad.map(k=>polar(cx,cy,ri,k));c.polyline(tpts,'#76E4DF55',2,{closed:true});c.polyline(qpts,'#FFD28655',2,{closed:true});
 triple.forEach((k,i)=>{const p=polar(cx,cy,ro,k);c.circle(...p,19,cyan);txt(c,p[0]-17,p[1]-12,34,29,String(i+1),18,'#142F38',true,'CENTER');});
 quad.forEach((k,i)=>{const p=polar(cx,cy,ri,k);c.rect(p[0]-15,p[1]-15,30,30,amber,{radius:5});txt(c,p[0]-17,p[1]-11,34,28,String(i+1),17,'#432B1E',true,'CENTER');});
 txt(c,cx-143,cy-73,286,98,'3 : 4',66,white,true,'CENTER');txt(c,cx-150,cy+28,300,65,'一圈 = 4个主拍\n按1→12顺时针读格',20,muted,false,'CENTER');
 c.arrow(cx+34,cy-ro-32,cx+91,cy-ro-22,cyan,2,{headLength:9});
 c.rect(894,285,551,529,'#2B2140',{radius:24,border:'1 SOLID #594367'});
 txt(c,925,310,480,43,'6分钟合奏练习',29,white,true);
 const st=[['01 / 2 min','先单独读格','等距读1–12。右手只在\n1、4、7、10打击，共4击。'],['02 / 2 min','加入左手三击','左手在1、5、9打击。\n两手均匀，不追赶彼此。'],['03 / 2 min','一起回到第1格','连续做4圈，再停下复核：\n每圈左3右4，起点同击。']];
 st.forEach((s,i)=>{const y=378+i*137;txt(c,926,y,140,34,s[0],19,cyan,true);txt(c,1080,y,328,36,s[1],22,white,true);txt(c,926,y+47,470,74,s[2],22,muted);});
 txt(c,898,842,545,69,'11.06 · 20:00–20:30\n拍点排练室 / 自拟排练活动',20,muted);
 c.rect(56,941,1388,111,'#302440',{radius:15});txt(c,80,953,203,32,'击点核对',22,white,true);txt(c,80,990,120,26,'左手 3',18,cyan,true);txt(c,80,1023,120,26,'右手 4',18,amber,true);
 for(let k=0;k<12;k++){const x=254+k*78;txt(c,x-18,952,40,28,String(k+1),17,muted,false,'CENTER');c.circle(x,1001,7,triple.includes(k)?cyan:'#514060');c.rect(x-7,1029-7,14,14,quad.includes(k)?amber:'#514060',{radius:3});}
 txt(c,57,1068,1380,29,'击点序号为1起算；算法索引为0起算。静态节奏卡无音频或计时播放，活动与场所为虚构演示。',16,muted);
 if(JSON.stringify(triple)!=='[0,4,8]'||JSON.stringify(quad)!=='[0,3,6,9]'||triple.filter(k=>quad.includes(k)).length!==1)throw Error('rhythm geometry');
 const m=common(id,'三对四 · 合奏排练卡',1500,1100,'练习三对四复节奏的双手打击乐学习者','排练室平板或横向练习卡，近距阅读','按等距小格打出左3右4，并核对每圈同时回到起点','紫黑两层钟面把三角与方形击点真正重合在12等分上，兼有可操作练习和逐格核对条',['12格等时，顺时针编号1–12','3击0/4/8→显示1/5/9；4击0/3/6/9→显示1/4/7/10','左右每圈3和4且仅在起点重合','3个2min动作合计6min','静态无实际计时或音频，不冒称演奏数据'],'自拟排练场所/活动；复节奏点位按显式等分算法计算，未录制实际演奏');m.rhythm={subdivisions:12,left_zero_based:triple,right_zero_based:quad,left_display:[1,5,9],right_display:[1,4,7,10],cycle_main_beats:4,exercise_minutes:6};output(id,c,m,{...doc,technique:'同心极坐标＋三角/方形点集',formula:'angle=-π/2+index/12×2π; outer249px,inner179px',checks:['点位角差120°/90°','共有点只有index0','等分→编号转换+1'],limitations:['静态图无播放，不承诺节拍器精度','钟面角度等分是抽象节奏，不是音频波形']});}
function tea(){const id='case-06',c=new Canvas(1200,1600,{background:'#F1F5EF'}),ink='#194E45',muted='#678078',berry='#A8657C',pale='#B7D4C6';
 txt(c,62,46,1070,37,'CUPSCAPE / 一杯山形',21,ink,true);txt(c,55,105,1080,97,'沿着香气，慢慢走。',62,ink,true);txt(c,63,225,1075,73,'青岚：绿茶＋烘米（自拟茶品）\n三站品尝路线，把感受写成你自己的词。',27,muted);
 c.rect(62,332,1076,102,'#DEEADF',{radius:16});txt(c,84,348,710,44,'11.08 / 11:00–11:18 / 三站各6 min',24,ink,true);txt(c,84,392,990,34,'杯山体验桌 · 松巷6号（虚构） / 室内散射光，桌边近距阅读',19,muted);
 // New parametric scent sculpture; no reused topographic artwork.
 c.circle(435,674,195,'#B8DCCB44');c.circle(777,624,214,'#D6B1C744');c.circle(615,816,201,'#CCE2CB55');
 function ring(scale){const pts=[];for(let j=0;j<=48;j++){const a=j/48*Math.PI*2,r=1+.14*Math.cos(3*a+.55)+.08*Math.sin(2*a);pts.push([600+scale*315*r*Math.cos(a),692+scale*235*r*Math.sin(a)-scale*38*Math.cos(2*a)]);}return pts;}
 const scales=[];for(let k=0;k<14;k++){const scale=1-k*.049;scales.push(scale);c.polyline(ring(scale),k%3===0?berry:'#709F8A',k%3===0?1.7:1,{closed:true,opacity:k%3===0?.85:.65});}
 const route=[[337,551],[741,626],[567,865]];c.polyline(route,'#FFFFFFAA',7,{roundCaps:true});c.polyline(route,ink,2,{roundCaps:true});route.forEach((p,i)=>{c.circle(...p,21,ink);txt(c,p[0]-22,p[1]-13,44,34,String(i+1).padStart(2,'0'),19,'#F2F5EA',true,'CENTER');});
 txt(c,168,493,260,37,'01 / 叶香',23,ink,true);txt(c,814,581,250,37,'02 / 入口',23,ink,true);txt(c,672,861,330,37,'03 / 余韵',23,ink,true);
 // A translucent cup lip and handle anchor the aroma, rather than literal terrain.
 c.oval(361,919,470,89,'#B6CDBC66');c.rect(373,957,446,83,'#CFDED1',{radius:25});c.oval(388,930,416,62,'#789D8377');c.oval(820,951,110,64,'#AAC8B2');c.oval(839,961,73,42,'#F1F5EF');c.line(374,999,818,999,'#97B39D',1);
 txt(c,65,1069,1050,37,'三个停留点 / 18分钟，不设标准答案',24,ink,true);
 const stops=[{n:'01',y:1122,title:'叶香 · 看与轻嗅',body:'先看干茶，再轻嗅杯口；用自己的词写下第一印象。'}, {n:'02',y:1238,title:'入口 · 慢慢品尝',body:'待茶汤温度适口再小口品尝；记录入口的感受。'}, {n:'03',y:1354,title:'余韵 · 留出30秒',body:'停30秒，再感受余味；圈出与你最接近的词。'}];
 stops.forEach(s=>{c.rect(63,s.y,1074,100,'#FFFFFFAA',{radius:14});txt(c,83,s.y+18,90,50,s.n,29,berry,true);txt(c,178,s.y+12,836,42,s.title+' / 6 min',24,ink,true);txt(c,178,s.y+58,900,33,s.body,20,muted);});
 txt(c,63,1493,1075,48,'预约：到展桌选择场次（演示流程） / 请先确认成分与个人适饮条件。',18,ink);
 txt(c,63,1546,1075,38,'艺术等高线与香味词为自拟隐喻，非真实地形或感官测量；茶品、地点与活动均为虚构。',16,muted);
 if(scales.length!==14||scales.some(v=>v<=0)||6*3!==18)throw Error('tea algorithm');
 const m=common(id,'一杯山形 · 三站茶香体验路线',1200,1600,'到展桌体验茶香的成人访客','室内散射光桌边导览卡，近距阅读','在18分钟内完成叶香、入口、余味观察并写下主观词汇','新建三瓣香气参数圈与透明色层，由杯口升起的曲面承载三停体验；清晰文字在艺术层之外',['三站各6min合计18min，与11:00–11:18相符','各站分别有看嗅/温度适口品尝/30秒余味动作','茶配方明确绿茶＋烘米、自拟香味与艺术非测量','实际时地/预约路径/观看条件与成分提示完整','14圈×48段，少于4096元素'],'茶品/香味词/活动地点自拟，香气轮廓为原创解析艺术，不是实测地形或感官图');m.stops=stops;m.duration_minutes=18;m.contours={count:14,segments:48,formula:'r=1+0.14cos(3a+0.55)+0.08sin(2a); x=600+315sr cos(a),y=692+235sr sin(a)-38s cos(2a)'};output(id,c,m,{...doc,technique:'三瓣香气轮廓＋CSS透明层＋杯口几何',formula:m.contours.formula,checks:['14个递减正scale','每圈闭合48段','两个透明圆与杯形和图形主结构全部DSL','3×6=18min'],limitations:['艺术香气轮廓不编码温度、化学成分或品鉴评分','不复用B01地形图，不是导航或实际茶香测量','静态图无嗅觉效果']});}
function lantern(){const id='case-07',c=new Canvas(1600,1100,{background:'#211D22'}),paper='#FFE2A0',muted='#CCB59D',orange='#F8AB4E',cream='#F3E9D6';
 c.rect(0,0,1600,1100,'transparent',{gradientType:'LINEAR',gradientColors:'#221C28,#38271D',gradientBegin:'TOP_LEFT',gradientEnd:'BOTTOM_RIGHT'});
 txt(c,58,43,1450,40,'PAPER LIGHT / 纸灯工坊',21,orange,true);txt(c,54,91,1450,81,'纸上发光。',61,cream,true);txt(c,60,191,1400,45,'让折痕成为骨架，让LED成为光。四步做一盏可以带走的纸灯。',25,muted);
 // Layered paper facets assembled from documented skew/gradient primitives.
 c.circle(375,552,258,'transparent',{gradientType:'RADIAL',gradientColors:'#FFC26A33,#FFC26A00',gradientStops:'0,1',gradientRadius:.58});
 c.at(190,393,60,370,tag('Transform',{matrix:matrix2d(1,-.3,0,1,0,0),origin:'(0,0)'},tag('Container',{width:60,height:370,color:'#AE6934',gradientType:'LINEAR',gradientColors:'#C78947,#96512B'})));
 c.at(500,375,60,370,tag('Transform',{matrix:matrix2d(1,.3,0,1,0,0),origin:'(0,0)'},tag('Container',{width:60,height:370,color:'#CD853E',gradientType:'LINEAR',gradientColors:'#FFE0A0,#B57134'})));
 c.rect(250,375,250,370,'#FFD385',{gradientType:'LINEAR',gradientColors:'#E0AA5D,#FFE6AA,#D49A4F',gradientStops:'0,.48,1'});
 for(let y=327;y<394;y+=3){const w=(y-325)/68*370;c.rect(375-w/2,y,w,3,'#D39A57');}
 for(let y=745;y<812;y+=3){const w=(812-y)/67*370;c.rect(375-w/2,y,w,3,'#BA7B3C');}
 c.polyline([[190,393],[375,325],[560,393],[560,763],[375,812],[190,763],[190,393]],'#FFDEA17F',2);
 for(let i=1;i<8;i++){const x=250+i*31.25;c.line(x,387,x,735,i%2===0?'#B7773777':'#FFF2B155',2);}
 c.polyline([[250,375],[375,325],[500,375]],'#FFE7B7',2);c.polyline([[250,745],[375,812],[500,745]],'#DBA75B',2);
 c.circle(375,553,63,'transparent',{gradientType:'RADIAL',gradientColors:'#FFF3CEAA,#FFF3CE00',gradientRadius:.6});
 const handle=[];for(let j=0;j<=24;j++){const a=Math.PI+j/24*Math.PI;handle.push([375+72*Math.cos(a),305+57*Math.sin(a)]);}c.polyline(handle,orange,4,{roundCaps:true});c.line(375,305,375,325,orange,4);
 txt(c,166,845,433,43,'LED光源 / 不用明火',27,paper,true);txt(c,126,899,500,41,'纸层与折痕为课堂示意，不是精确展开裁切图。',18,muted);
 const steps=[{x:750,y:283,n:'01',t:'备好材料 / 10 min',body:'领取预裁纸、双面胶、夹子、\n悬挂绳与配套电池LED。\n清点后再开始折纸。',mode:'materials'}, {x:1170,y:283,n:'02',t:'折出骨架 / 20 min',body:'按带领者示范来回折叠。\n对齐边缘，压实折痕；\n先试折练习纸。',mode:'fold'}, {x:750,y:589,n:'03',t:'合围固定 / 30 min',body:'将首尾重叠并固定。\n用夹子暂夹连接处；\n确认连接牢固后取下。',mode:'join'}, {x:1170,y:589,n:'04',t:'安装LED / 30 min',body:'按产品说明安装电池LED。\n检查纸面、电线与悬挂点；\n带领者复核后点亮。',mode:'led'}];
 steps.forEach(s=>{const x=s.x,y=s.y;c.rect(x,y,371,273,'#F3E7D9',{radius:16});txt(c,x+20,y+16,70,54,s.n,32,'#A25833',true);txt(c,x+85,y+22,265,37,s.t,22,'#3F352F',true);txt(c,x+23,y+88,329,101,s.body,22,'#584A3E');
  const dy=y+208;if(s.mode==='materials'){c.rect(x+25,dy,68,45,'#DEC29D');c.rect(x+54,dy+9,69,40,'#E9D6B9');c.circle(x+169,dy+25,15,'#D3A75D');c.line(x+210,dy+4,x+278,dy+43,'#9F6C49',3);c.rect(x+295,dy+5,38,35,'#826B55',{radius:6});}if(s.mode==='fold'){c.rect(x+25,dy,306,43,'#D8C2A2');for(let k=0;k<7;k++){const xx=x+40+k*43;c.line(xx,dy+3,xx,dy+40,k%2===0?'#AF7852':'#F5E5C9',3);}c.arrow(x+46,dy-10,x+123,dy-10,'#9A6846',2,{headLength:7});}if(s.mode==='join'){c.oval(x+70,dy+3,206,42,'#B88B5E');c.oval(x+94,dy+8,158,26,'#F3E7D9');c.rect(x+246,dy+3,30,44,'#9A5A36',{radius:4});}if(s.mode==='led'){c.rect(x+45,dy+11,74,28,'#645443',{radius:5});c.polyline([[x+118,dy+25],[x+160,dy+25],[x+181,dy+4],[x+240,dy+21],[x+291,dy+9]],'#A67D45',2);for(const p of [[181,4],[240,21],[291,9]])c.circle(x+p[0],dy+p[1],7,'#FFE29A');}});
 c.rect(59,958,1482,94,'#F1E7D7',{radius:15});txt(c,82,974,860,38,'11.14 / 14:00–15:30 / 澄巷8号（虚构）',26,'#3A302B',true);txt(c,82,1018,870,28,'¥40含材料 · 13:45签到 · 到工坊选本场（演示报名流程）',20,'#6F5B4B');txt(c,1111,980,386,59,'12人小班\n4步共90分钟',22,'#9A5A36',true);
 txt(c,60,1066,1480,29,'自拟活动、价格、名额与地址。图中纸层仅表达制作原理，实际规格按课堂材料；不使用明火。',17,muted);
 if(steps.reduce((a,s)=>a+Number(s.t.match(/(\d+) min/)[1]),0)!==90)throw Error('class time');
 const m=common(id,'纸上发光 · 灯笼制作课',1600,1100,'希望参与纸艺灯笼制作的社区成人或受辅导参与者','工坊横向招募/课堂流程屏，桌边近距阅读','准备材料并按四步制作LED纸灯，理解时间/报名和检查条件','原创建构多面纸灯，用矩阵错切、渐变纸层、透明光晕把折痕从说明变为主体；右侧四步实际课程不靠艺术图猜尺寸',['四步材料/折叠/固定/LED检查齐全','10+20+30+30=90min，与14:00–15:30一致','LED按产品说明安装，不用明火','场所/时间/费用/人数/报名完整且虚构','折线纸层明确课堂示意非精确裁切展开图'],'原创虚构课堂运营；纸灯几何为艺术与制作原理示意，未进行实物发热或承重测试');m.steps=steps;m.duration_minutes=90;m.price=40;m.capacity=12;output(id,c,m,{...doc,technique:'错切矩阵纸面＋三色渐变＋逐层帽片＋透明径向光晕',geometry:{left_matrix:matrix2d(1,-.3,0,1,0,0),right_matrix:matrix2d(1,.3,0,1,0,0),front:[250,375,250,370]},checks:['左侧b=-.3、右侧b=.3均有限，错切上/下边与纸面接缝','所有高光在DSL内，未烘焙图片','四步分钟求和90'],limitations:['非精确展开纸样，不提供据图裁切尺寸','静态LED光感为渐变艺术，不是实物亮度/温升/承重测量','无明火，不声称灯具安全认证']});}
for(const fn of [rehearsal,tea,lantern])fn();
const td=fs.readdirSync(path.resolve('tasks')).find(x=>x.startsWith('B03-'));const sources=['TASK.md','AGENTS.md','task.json','run-config.json','inputs/README.md'].map(x=>'tasks/'+td+'/'+x).concat(['tmp/20261002-204314-6f31/B03/plan-v001.json','tmp/20261002-204314-6f31/_suite/shared-doc-000004-readable.txt','tmp/20261002-204314-6f31/_suite/dsl.cjs']);save('source-read-evidence-v001.json',{recorded_at:new Date().toISOString(),method:'Get-Content -Raw实际读取；Parser/DSL为同run真实缓存复用',sources:sources.map(p=>({path:p,sha256:crypto.createHash('sha256').update(fs.readFileSync(path.resolve(p))).digest('hex')}))});
