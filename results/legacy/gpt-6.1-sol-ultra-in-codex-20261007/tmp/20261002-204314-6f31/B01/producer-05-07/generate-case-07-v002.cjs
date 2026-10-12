'use strict';
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const {Canvas}=require('../../_suite/dsl.cjs');
const base=__dirname;
function write(name,data){name=name.replace('-v001.snapshot','-v002.snapshot').replace('-metadata-v001.json','-metadata-servicefix-v001.json').replace('-content-v001.md','-content-servicefix-v001.md').replace('source-read-evidence-v001.json','source-read-evidence-v002.json');fs.writeFileSync(path.join(base,name),typeof data==='string'?data:JSON.stringify(data,null,2),'utf8',{flag:'wx'});}
function label(c,x,y,w,t,size=20,color='#D3E1E8',bold=false){c.text(x,y,w,size*1.7,t,size,color,{bold});}
function pill(c,x,y,w,text,color,bg){c.rect(x,y,w,34,bg,{radius:17});c.text(x,y+5,w,28,text,17,color,{align:'CENTER',bold:true});}
function harbor(){
 const c=new Canvas(1600,1000,{background:'#081A27'}),cyan='#72E2DA',white='#F2F7F7',muted='#91ACBB',amber='#FFC66E',coral='#F28269';
 // Technical frame and a quiet nautical grid.
 for(let x=40;x<1570;x+=40)c.line(x,198,x,788,'#173442',.8);
 for(let y=198;y<800;y+=40)c.line(40,y,1000,y,'#173442',.8);
 label(c,54,42,400,'TIDELINE / OPERATIONS',19,cyan,true);
 label(c,50,78,650,'潮汐港 · 作业次序',54,white,true);
 label(c,52,151,900,'调度屏 / 10:20 静态截面 · 泊位与起重机任务一眼对应',22,muted);
 c.rect(1220,45,328,112,'#102F3B',{radius:8,border:'1 SOLID #2E5863'});
 label(c,1240,58,275,'下一步调度',17,muted);
 label(c,1240,88,275,'11:00 → C02 / B泊位',25,cyan,true);
 c.rect(1020,199,528,595,'#0D2635',{radius:10,border:'1 SOLID #214A5B'});
 label(c,1060,220,440,'当班任务清单',28,white,true);
 label(c,1060,261,440,'箱量 / 单次作业上限 · TEU',18,muted);
 // Quayside strip and independent container stacks.
 c.rect(72,225,167,545,'#294450',{radius:5});
 label(c,86,241,140,'陆侧堆场',19,white,true);
 const fills=['#3F727B','#569592','#A0BFAB','#A37E58'];
 for(let r=0;r<12;r++)for(let k=0;k<3;k++){c.rect(87+k*43,288+r*35,35,25,fills[(r+k)%4],{border:'1 SOLID #B5CCD255'});for(let a=0;a<3;a++)c.line(92+k*43+a*8,292+r*35,92+k*43+a*8,309+r*35,'#07212B66',1);}
 const jobs=[
  {id:'A',y:375,shipY:304,name:'北辰 08',amount:72,cap:120,start:'10:00',end:'11:30',status:'正在卸箱',color:cyan,crane:'C01'},
  {id:'B',y:535,shipY:464,name:'海屿 16',amount:126,cap:180,start:'11:00',end:'13:00',status:'靠泊待装',color:amber,crane:'C02'},
  {id:'C',y:695,shipY:624,name:'白鹭 03',amount:54,cap:90,start:'13:30',end:'15:00',status:'待泊预约',color:coral,crane:'C01'}
 ];
 jobs.forEach((j,i)=>{
  c.rect(225,j.y,644,29,'#45606C',{radius:3});c.line(247,j.y+5,843,j.y+5,'#B8CDD6',2);
  label(c,252,j.y+35,270,`${j.id} / ${j.crane} · ${j.amount}/${j.cap} TEU`,19,j.color,true);
  const sx=i===2?639:425,sy=j.shipY;
  c.rect(sx,sy,330,56,i===2?'#303F4C':'#4B6F7B',{radius:26,border:`2 SOLID ${j.color}`});
  c.rect(sx+15,sy+14,44,28,'#DDE9E8',{radius:3});
  for(let k=0;k<5;k++)c.rect(sx+72+k*44,sy+13,36,30,i===1?'#B98D50':'#497F78',{border:'1 SOLID #B2D6D4'});
  label(c,sx+78,sy-30,220,j.name,18,white,true);
  if(i<2){const q=320;c.line(q,j.y-5,q,j.y-90,j.color,6);c.line(q,j.y-87,q+160,j.y-87,j.color,6);c.line(q+145,j.y-85,q+145,sy+20,j.color,2);c.line(q,j.y-65,q+48,j.y-85,j.color,3);c.rect(q-15,j.y-12,30,17,j.color,{radius:2});}
  else c.arrow(940,sy+85,897,sy+28,coral,3,{headLength:12});
  const ty=309+i*145;
  label(c,1060,ty,50,j.id,36,j.color,true);
  label(c,1124,ty+4,200,j.name,24,white,true);
  pill(c,1363,ty+4,146,j.status,j.color,'#203D49');
  label(c,1124,ty+44,365,`${j.start}–${j.end}  /  ${j.crane}`,22,white);
  c.rect(1124,ty+88,285,7,'#294755',{radius:3});c.rect(1124,ty+88,285*j.amount/j.cap,7,j.color,{radius:3});
  label(c,1420,ty+78,90,`${Math.round(j.amount/j.cap*100)}%`,20,j.color,true);
 });
 label(c,74,786,905,'平面为几何示意 · C船在外侧等待，13:30进入预约泊位',18,muted);
 // Time plan is proportional to the displayed hours; each crane is a separate row.
 c.rect(52,827,1496,126,'#0F2B38',{radius:9});
 label(c,76,845,200,'起重机排程',24,white,true);
 const tx=320,unit=230;
 for(let h=0;h<=5;h++){c.line(tx+h*unit,842,tx+h*unit,935,'#365465',1);label(c,tx+h*unit-17,840,70,`${10+h}:00`,16,muted);}
 label(c,197,880,90,'C01',19,cyan,true);label(c,197,918,90,'C02',19,amber,true);
 c.rect(tx,878,unit*1.5,28,cyan,{radius:4});label(c,tx+14,879,310,'A · 卸72 TEU',18,'#082B32',true);
 c.rect(tx+unit*3.5,878,unit*1.5,28,coral,{radius:4});label(c,tx+unit*3.5+14,879,310,'C · 卸54 TEU',18,'#35231F',true);
 c.rect(tx+unit,916,unit*2,28,amber,{radius:4});label(c,tx+unit+14,917,420,'B · 装126 TEU',18,'#342B1C',true);
 label(c,55,965,1490,'自拟港口、船名与演示数据 / 单位 TEU 为标准箱换算量；作业上限不是堆场实时库存。',16,muted);
 return {dsl:c.toString(),metadata:{case_id:'case-05',title:'潮汐港 · 作业次序',dimensions:[1600,1000],audience:'港口当班调度员',task:'确认下一次起重机派工，并对照泊位、船舶、作业容量及资源排程',viewing_environment:'桌面调度大屏',fictional:true,source:'全部品牌、船名、任务数据为原创演示；未使用外部素材',jobs,time_scale_pixels_per_hour:unit,now:'10:20',completion_checks:['泊位A/B/C、三船、两起重机均可对照','TEU比例为60%、70%、60%','C01 A10:00–11:30与C13:30–15:00不重叠；C02 B11:00–13:00','下一次派工11:00 C02→B与清单一致','逐图视觉审查由root执行，尚未渲染']} };
}
function theatre(){
 const c=new Canvas(1200,1600,{background:'#F8EFE9'}),ink='#38243A',plum='#643D63',pink='#E6BDD0',orange='#DA644D',muted='#886D81';
 label(c,66,52,700,'FOLDLINE THEATRE / 折线剧场',21,plum,true);
 label(c,65,100,700,'《光落在这里》',64,ink,true);
 label(c,70,188,700,'选两席，坐进同一束光。',29,plum);
 c.circle(1060,111,73,'#E4BECC');c.circle(1038,94,10,orange);c.line(1055,125,1110,150,plum,4);c.line(1047,131,1000,176,plum,4);
 // A theatre light motif, made of individual DSL segments.
 for(let i=0;i<30;i++){c.line(163,250,390+i*14,419,'#DFB5C755',7);c.line(1037,250,806-i*14,419,'#EBC39D44',7);}
 c.rect(109,236,120,34,ink,{radius:10});c.rect(971,236,120,34,ink,{radius:10});
 c.rect(72,289,1056,95,'#FFFFFFB8',{radius:12});
 label(c,96,305,240,'2026.11.14 · 周六',22,ink,true);
 label(c,385,305,280,'18:45 入场',24,ink,true);
 label(c,711,305,300,'19:30 开演',24,ink,true);
 label(c,96,346,900,'全程90分钟，无中场休息 / 折线厅 · 自拟演出与场馆',18,muted);
 c.rect(72,417,1056,739,'#FFFFFF',{radius:26,border:'1 SOLID #E3D0DC'});
 label(c,103,438,250,'面向舞台',21,muted,true);
 c.rect(302,481,596,71,ink,{radius:20});label(c,302,496,596,'舞   台',27,'#F7D6BF',true);
 for(let i=0;i<9;i++)c.line(342+i*60,566,346+i*59,579,'#C59CB5',3);
 const rows='ABCDEFGH'.split(''),start=166,seatW=46,gap=14,aisle=48,seatH=39;
 function seatX(n){return start+(n-1)*(seatW+gap)+(n>7?aisle:0);}
 for(let n=1;n<=14;n++)c.text(seatX(n),590,seatW,28,String(n).padStart(2,'0'),15,muted,{align:'CENTER'});
 let occupied=0,available=0;const seats=[];
 rows.forEach((r,ri)=>{
  const y=631+ri*57;label(c,104,y+6,45,r,22,ink,true);
  for(let n=1;n<=14;n++){
   const selected=r==='D'&&(n===6||n===7);
   const sold=!selected&&((ri*11+n*7)%13<4 ||(ri===0&&n>4&&n<11));
   const fill=selected?orange:sold?'#D3D0D5':pink;
   if(sold)occupied++;else if(!selected)available++;
   c.rect(seatX(n),y,seatW,seatH,fill,{radius:9});c.rect(seatX(n)+4,y+seatH-5,seatW-8,7,sold?'#B8B3BC':selected?'#AC4539':'#B97D9E',{radius:3});
   c.text(seatX(n),y+8,seatW,24,String(n).padStart(2,'0'),15,selected?'#FFFFFF':sold?'#7D7983':plum,{align:'CENTER',bold:selected});
   if(sold)c.line(seatX(n)+12,y+10,seatX(n)+34,y+29,'#8C858F',1);
   seats.push({row:r,number:n,price:ri<4?280:180,status:selected?'selected':sold?'sold':'available'});
  }
 });
 label(c,575,658,54,'过\n道',18,'#AB98A4');
 c.line(143,864,1061,864,'#E9D6E1',1);
 label(c,152,1110,850,'A–D排 ¥280 / E–H排 ¥180 · 每排14席，共112席',20,plum);
 const legend=[['#E6BDD0','可选'],['#D3D0D5','已售'],[orange,'已选']];legend.forEach((a,i)=>{c.rect(99+i*245,1184,24,24,a[0],{radius:6});label(c,136+i*245,1180,180,a[1],21,ink);});
 label(c,852,1183,250,`${available}席可选 / ${occupied}席已售`,18,muted);
 c.rect(72,1242,1056,273,ink,{radius:24});
 label(c,108,1269,640,'D06 + D07',41,'#FFE6D5',true);
 label(c,108,1330,630,'两席同侧相邻 · 靠近中轴',24,'#DDBFD5');
 label(c,108,1373,640,'2 × ¥280 = ¥560 / 不含额外费用',22,'#DDBFD5');
 c.rect(818,1292,263,121,orange,{radius:17});label(c,836,1310,226,'确认这两席',24,'#FFFFFF',true);label(c,836,1347,226,'¥560',36,'#FFFFFF',true);
 label(c,108,1451,930,'入场时核对演出日期、厅名与座位 / 这是静态选座演示。',18,'#DDBFD5');
 label(c,75,1544,1050,'场馆、演出、时间、票价与座位状态全部为原创虚构示例；未提供真实订票服务。',17,muted);
 return {dsl:c.toString(),metadata:{case_id:'case-06',title:'折线剧场 · 光落在这里',dimensions:[1200,1600],audience:'购买双人演出票的观众',task:'找到两席相邻可用座位并核对价格、舞台方向与入场时间',viewing_environment:'桌面或平板静态选座页面',fictional:true,source:'原创虚构演出/场馆/数据，纯DSL，无外部素材',seats,counts:{total:112,available,occupied,selected:2},selected:['D06','D07'],price_each:280,total_price:560,admission:'18:45',start:'19:30',duration_minutes:90,completion_checks:['8排×14座=112完整座位，状态与计数一致','D06/D07位于同侧且紧邻，无过道隔离','2×280=560','A–D280/E–H180价格与元数据一致','root须真实服务与逐图审查，当前仅构造初稿']} };
}
function ridge(){
 const c=new Canvas(1600,1100,{background:'#EDE9DB'}),ink='#243C31',green='#446751',pale='#DADFCC',muted='#687567',orange='#D57741';
 label(c,52,40,500,'RIDGELINE / WEEKEND FIELD GUIDE',18,green,true);
 label(c,48,78,980,'山脊 · 把今天走成一条线',52,ink,true);
 label(c,51,151,990,'北门 → 松林 → 岩台 → 山脊 → 溪口 / 虚构路线，地形示意',22,muted);
 c.rect(1150,54,394,122,ink,{radius:12});
 label(c,1178,72,330,'6.2 km / 2 h 10 min',31,'#F4ECD7',true);
 label(c,1178,125,340,'10:00出发 → 12:10到达',21,'#BFCDB7');
 c.rect(42,211,1068,667,'#DDE1CB',{radius:24,border:'1 SOLID #C4CEB7'});
 // Original closed contour polylines. Two asymmetric hills are generated analytically.
 function contour(cx,cy,rx,ry,k,segments=40){const p=[];for(let j=0;j<=segments;j++){const a=j/segments*Math.PI*2;const mod=1+.035*Math.sin(5*a+k*.25)+.025*Math.cos(3*a-k*.32);p.push([cx+rx*Math.cos(a)*mod,cy+ry*Math.sin(a)*mod]);}return p;}
 for(let k=0;k<16;k++){const rx=420-k*21,ry=269-k*14;c.polyline(contour(621,523,rx,ry,k),k%4===0?'#8EAA84':'#B5C4A2',k%4===0?1.6:.8,{closed:true});}
 for(let k=0;k<9;k++)c.polyline(contour(282,670,180-k*17,122-k*10,k,24),'#BAC9AB',.9,{closed:true});
 c.polyline([[900,247],[894,310],[926,363],[911,411],[953,472],[940,520],[976,597],[953,653],[983,717],[964,801]],'#B3D0CA',19,{roundCaps:true});
 c.polyline([[900,247],[894,310],[926,363],[911,411],[953,472],[940,520],[976,597],[953,653],[983,717],[964,801]],'#729E9B',1.5,{roundCaps:true});
 label(c,974,699,105,'溪沟',17,'#5B8C89');
 label(c,676,566,80,'420 m',17,'#7B9271');label(c,437,430,80,'300 m',17,'#7B9271');label(c,313,699,80,'180 m',17,'#7B9271');
 const points=[[177,744],[329,621],[551,471],[756,392],[921,585]];
 c.polyline(points,'#F4EFDF',13,{roundCaps:true});c.polyline(points,orange,6,{roundCaps:true});
 for(let i=0;i<points.length;i++){c.circle(...points[i],17,ink);c.text(points[i][0]-18,points[i][1]-11,36,30,String(i+1),19,'#F5EDD9',{align:'CENTER',bold:true});}
 const tags=[{x:87,y:785,w:233,t:'01 北门 · 120 m'}, {x:181,y:556,w:255,t:'02 松林岔口 · 210 m'}, {x:420,y:402,w:255,t:'03 岩台 · 360 m'}, {x:690,y:318,w:295,t:'04 山脊瞭望 · 420 m'}, {x:826,y:620,w:246,t:'05 溪口 · 160 m'}];
 tags.forEach(t=>{c.rect(t.x,t.y,t.w,43,'#F4F0DFE6',{radius:7});label(c,t.x+12,t.y+8,t.w-20,t.t,18,ink,true);});
 // Compass is a visual orientation aid, without claiming geographic accuracy.
 c.arrow(1032,311,1032,260,ink,3,{headLength:13});label(c,1016,232,40,'N',18,ink,true);
 label(c,72,235,420,'步道示意 / 非等比例导航地图',18,green,true);
 label(c,69,846,985,'图中等高线为原创图形，非测绘数据；正式出行请使用可靠地图并核查开放情况。',16,muted);
 c.rect(1140,211,408,667,'#F7F3E7',{radius:19});label(c,1174,238,332,'沿途节奏',30,ink,true);
 const stages=[
  {num:'01',name:'北门 → 松林岔口',dist:1.2,min:20,time:'10:00–10:20',note:'进入步道，确认方向'},
  {num:'02',name:'松林岔口 → 岩台',dist:1.6,min:35,time:'10:20–10:55',note:'岩台停5分钟，检查饮水'},
  {num:'03',name:'岩台 → 山脊瞭望',dist:1.4,min:30,time:'11:00–11:30',note:'山脊停5分钟，观察天气'},
  {num:'04',name:'山脊瞭望 → 溪口',dist:2,min:35,time:'11:35–12:10',note:'下降路段，保持步幅'}
 ];
 stages.forEach((s,i)=>{const y=300+i*121;c.circle(1193,y+21,20,green);label(c,1174,y+8,44,s.num,18,'#F7F2E4',true);label(c,1227,y,290,s.name,20,ink,true);label(c,1227,y+34,278,`${s.dist.toFixed(1)} km · ${s.min} min`,21,orange,true);label(c,1227,y+68,280,`${s.time}`,17,muted);label(c,1176,y+99,340,s.note,17,green);});
 c.rect(1172,813,344,40,pale,{radius:6});label(c,1183,822,325,'步行120 min + 停留10 min',18,ink,true);
 // Distance-proportional height profile, to support pacing rather than decoration.
 c.rect(43,909,1067,156,'#F7F3E7',{radius:18});label(c,67,925,230,'海拔节奏',23,ink,true);label(c,67,964,240,'上升300 m / 下降260 m',17,muted);
 const cumulative=[0,1.2,2.8,4.2,6.2],alts=[120,210,360,420,160],px=352,pw=706,baseY=1032,ph=78;
 const chartPts=cumulative.map((d,i)=>[px+d/6.2*pw,baseY-(alts[i]-100)/320*ph]);
 c.line(px,baseY,px+pw,baseY,'#BFCBB7',1);c.polyline(chartPts,green,3,{roundCaps:true});
 chartPts.forEach((p,i)=>{c.circle(...p,5,orange);c.text(p[0]-33,p[1]-27,68,25,`${alts[i]}m`,14,muted,{align:'CENTER'});c.text(p[0]-29,1040,68,24,`${cumulative[i]}km`,14,muted,{align:'CENTER'});});
 c.rect(1140,909,408,156,ink,{radius:18});label(c,1171,927,336,'出发前的一分钟',23,'#F3EAD4',true);c.text(1171,968,335,76,'携带饮水 · 核对天气与路线\n沿途未承诺可饮水源',20,'#C6D1BC');
 label(c,50,1070,1480,'自拟路线、场所、地形与时间全部用于设计演示；不代表真实景区、实际开放情况或导航建议。',15,muted);
 return {dsl:c.toString(),metadata:{case_id:'case-07',title:'山脊 · 把今天走成一条线',dimensions:[1600,1100],audience:'计划周末步行的游客',task:'理解路线先后、每段距离时间与停留点，准备饮水并判断完成时间',viewing_environment:'平板路线计划或印刷随行卡',fictional:true,source:'所有场所、线路、海拔与时间为原创虚构；等高线解析生成，无外部素材',stages,total_distance_km:6.2,walking_minutes:120,stopping_minutes:10,total_minutes:130,start:'10:00',finish:'12:10',cumulative_distance_km:cumulative,altitude_m:alts,ascent_m:300,descent_m:260,completion_checks:['四段距离合计6.2km','四段步行20+35+30+35=120min，加两次5min停留=130min','10:00–12:10含10:55–11:00和11:30–11:35两处停留','海拔折线横坐标按累计距离，升降300/260m','视觉实际服务与检查由root完成，当前仅初稿']} };
}
for(const build of [ridge]){const {dsl,metadata}=build();write(`${metadata.case_id}-v001.snapshot`,dsl);write(`${metadata.case_id}-metadata-v001.json`,metadata);write(`${metadata.case_id}-content-v001.md`,`# ${metadata.title}\n\n受众：${metadata.audience}。使用任务：${metadata.task}。观看环境：${metadata.viewing_environment}。\n\n来源：${metadata.source}。\n\n本稿为纯DSL初稿，未调用真实服务，未作视觉通过声明。root将渲染、逐图打开并记录保留/修订理由。\n\n完成标准：\n${metadata.completion_checks.map(x=>'- '+x).join('\n')}\n`);}
const sources=['tasks/B01-ten-real-world-showcases/TASK.md','tasks/B01-ten-real-world-showcases/AGENTS.md','tasks/B01-ten-real-world-showcases/task.json','tasks/B01-ten-real-world-showcases/run-config.json','tasks/B01-ten-real-world-showcases/inputs/README.md','run-config.json','tmp/20261002-204314-6f31/_suite/dsl.cjs','tmp/20261002-204314-6f31/_suite/dsl-README.md','tmp/20261002-204314-6f31/_suite/shared-doc-000004-readable.txt'];
write('source-read-evidence-v001.json',{agent:'b01_cases_05_06_07',recorded_at:new Date().toISOString(),method:'实际Get-Content完整读取，共享缓存复用，无新HTTP',sources:sources.map(p=>({path:p,sha256:crypto.createHash('sha256').update(fs.readFileSync(path.resolve(p))).digest('hex')}))});
console.log('Created three self-contained Snapshot initial drafts and metadata; no rendering or suite state writes.');
