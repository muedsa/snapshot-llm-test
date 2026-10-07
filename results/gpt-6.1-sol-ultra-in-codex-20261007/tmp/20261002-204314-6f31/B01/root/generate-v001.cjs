const fs=require('node:fs'),path=require('node:path');
const {Canvas}=require('../../_suite/dsl.cjs');
const dir=__dirname;fs.mkdirSync(dir,{recursive:true});
function save(id,c,meta){fs.writeFileSync(path.join(dir,id+'-v001.snapshot'),c.toString(),{flag:'wx'});fs.writeFileSync(path.join(dir,id+'-meta-v001.json'),JSON.stringify({...meta,id,dimensions:[c.width,c.height],created_at:new Date().toISOString(),content_basis:'自拟品牌、场所与演示内容；未实际部署；无外部素材',supporting_assets:[],dsl_capabilities:['Snapshot','Stack','Positioned','Container','Text/Raw/CDATA','Transform.matrix','ClipOval']},null,2)+'\n',{flag:'wx'});}
function T(c,x,y,w,h,t,s,col,bold=false){c.text(x,y,w,h,t,s,col,{bold});}
function star(c,x,y,r,col){c.line(x-r,y,x+r,y,col,2);c.line(x,y-r,x,y+r,col,2);}
// 01: evening train ticket: route spine, boarding sequence and original train.
{
 const c=new Canvas(1200,1600,{background:'#081728'}),ink='#F7EEDA',muted='#AABCCC',gold='#EDC17C';
 for(let i=0;i<54;i++){const x=60+(i*179)%1080,y=35+(i*73)%420;c.circle(x,y,i%7===0?2.5:1,'#536A7F');}
 c.line(70,94,1120,94,'#31445B',1);T(c,70,43,850,45,'NIGHTLINE  /  夜行',25,gold,true);T(c,925,45,200,38,'乘车信息卡',22,muted);
 T(c,70,136,1020,90,'把今晚交给旅途',66,ink,true);T(c,73,243,1000,43,'北岸站 → 星湾站  /  N218  /  10月18日出发',28,muted);
 c.rect(70,330,1060,333,'#10243A',{radius:24,border:'1 SOLID #32475F'});
 T(c,110,367,440,47,'北岸  NORTH BANK',26,muted);T(c,110,421,420,98,'23:40',76,ink,true);T(c,110,534,380,50,'10月18日 · 今晚出发',25,gold);
 T(c,710,367,380,47,'星湾  STAR BAY',26,muted);T(c,710,421,380,98,'07:20',76,ink,true);T(c,710,534,380,50,'10月19日 · 次日抵达',25,gold);
 c.arrow(490,482,665,482,gold,3,{headLength:16,headWidth:7});T(c,479,528,215,40,'7小时40分',22,muted);
 c.line(111,612,1087,612,'#32475F',1);T(c,110,624,960,31,'软卧 · 06车 / 08下铺     示例票面，请以实际车票为准',20,muted);
 T(c,70,710,540,62,'登车前，只做这三步',37,ink,true);
 c.line(117,825,117,1135,gold,4);
 const steps=[['01','23:00 前','到达北岸站','预留安检与步行时间'],['02','23:15–23:30','在 4 号检票口检票','备好车票与有效证件'],['03','23:40','列车出发 · 4 站台','核对 N218，再找到 06 车']];
 steps.forEach((a,i)=>{const y=805+i*143;c.circle(117,y+29,27,gold);T(c,92,y+9,51,41,a[0],25,'#081728',true);T(c,172,y,360,45,a[1],28,gold,true);T(c,570,y,535,44,a[2],30,ink,true);T(c,570,y+49,535,45,a[3],23,muted);});
 c.rect(70,1240,1060,208,'#122A40',{radius:18});
 c.rect(108,1285,573,84,'#D9E4DE',{radius:20});c.rect(124,1296,92,38,'#173A50',{radius:7});c.rect(232,1296,92,38,'#173A50',{radius:7});c.rect(340,1296,92,38,'#173A50',{radius:7});c.rect(448,1296,92,38,'#173A50',{radius:7});c.rect(556,1296,92,38,'#173A50',{radius:7});
 c.circle(173,1371,18,'#EDC17C');c.circle(594,1371,18,'#EDC17C');c.line(92,1395,700,1395,'#687C87',3);T(c,755,1272,324,55,'4 站台',38,gold,true);T(c,755,1340,330,75,'沿地面导向标识前往\n遇到变更，查看站内屏幕',21,ink);
 T(c,70,1504,1040,42,'虚构线路与时刻 · 静态设计演示 · 不作为实际乘车凭证',21,muted);
 save('case-01',c,{title:'夜行 · 北岸站',audience:'晚间乘坐卧铺列车的旅客',use_context:'1200×1600可下载出行卡，手机放大阅读',user_goal:'确认跨日到达、检票截止、检票口、站台与车厢',visual_intent:'星空与金色时间脊柱，把长途夜行转为清晰的三步登车',completion_criteria:['跨日日期清晰','23:40至次日07:20=7小时40分','三步与4号口/4站台对应','演示凭证性质明确'],checks:{duration_minutes:460,boarding_window_minutes:15,gate:4,platform:4,coach:'06'}});
}
// 08: original pasta plate and ingredient measure rail.
{
 const c=new Canvas(1500,1100,{background:'#F5EFDF'}),ink='#173A2C',green='#466E43',red='#C55038';
 c.rect(0,0,530,1100,'#C8D498');T(c,48,43,420,44,'青柠  /  LITTLE LIME',25,ink,true);T(c,46,126,440,163,'一锅意面\n今晚就吃好',59,ink,true);T(c,48,319,410,75,'2人份 · 一口锅 · 15分钟参考',25,ink);
 c.circle(265,633,230,'#EBE7D4');c.circle(265,633,201,'#FCF8E9');c.circle(265,633,165,'#DAB864');
 for(let k=0;k<23;k++){const p=[];for(let j=0;j<23;j++){const a=j*.27+k*.9,r=45+k*4.4;p.push([265+Math.cos(a)*r,633+Math.sin(a)*r*.82]);}c.polyline(p,k%2?'#E6C16D':'#EFCF80',5,{roundCaps:true});}
 [[205,576],[339,605],[228,708],[320,724],[153,634]].forEach(([x,y])=>{c.circle(x,y,24,red);c.circle(x-6,y-6,7,'#EC8B56');});
 [[260,543],[337,665],[177,690]].forEach(([x,y],i)=>{c.oval(x,y,54,24,green);c.line(x+3,y+13,x+49,y+13,'#C8D498',2);});
 T(c,46,954,437,102,'自拟食谱 · 时间受锅具与火力影响\n按包装熟制要求调整，不以计时替代检查',19,ink);
 T(c,590,51,849,64,'先备齐，再开火',43,ink,true);T(c,592,121,844,41,'食材清单  /  2人份',23,green);
 const ing=[['意面','160 g'],['小番茄','200 g'],['清水','500 ml'],['蒜','2 瓣'],['橄榄油','1 汤匙'],['盐 / 罗勒','适量']];
 ing.forEach((a,i)=>{const x=590+(i%3)*287,y=190+Math.floor(i/3)*122;c.line(x,y+96,x+258,y+96,'#D8D9C1',1);T(c,x,y,250,35,a[0],24,green);T(c,x,y+39,250,50,a[1],32,ink,true);});
 T(c,590,480,830,60,'15 MIN  /  一路煮到底',38,ink,true);
 const step=[['04','分钟','准备','切番茄、拍蒜。把全部食材\n与水放入锅中。'],['09','分钟','煮制','煮开后保持微沸，常搅拌。\n按包装建议检查面条熟度。'],['02','分钟','收尾','面条熟后收汁；偏干补少量水。\n关火，加入罗勒并调味。']];
 step.forEach((a,i)=>{const y=568+i*146;c.circle(625,y+46,35,i===1?red:green);T(c,599,y+18,63,51,a[0],34,'#FFF9E8',true);T(c,682,y+3,167,46,a[2],30,ink,true);T(c,683,y+48,160,31,a[1],20,green);T(c,870,y+10,551,99,a[3],25,ink);if(i<2)c.line(625,y+85,625,y+141,'#A6B48B',3);});
 c.rect(590,1010,850,55,ink,{radius:12});T(c,612,1020,804,36,'完成标准：面条熟透、汁液挂面；趁热分成两份。',23,'#FFF9E8');
 save('case-08',c,{title:'青柠 · 一锅意面',audience:'下班后为两人准备简餐的人',use_context:'1500×1100厨房食谱卡，平板/横屏',user_goal:'备齐2人食材并按4+9+2分钟参考流程完成意面',visual_intent:'从真实可读食材到原创盘面，再用大分钟节点引导一锅流程',completion_criteria:['6项食材有单位','4+9+2=15','熟度参考包装，实际检查优先','图中食物仅DSL几何'],checks:{servings:2,phase_minutes:[4,9,2],total_minutes:15}});
}
// 09: bicycle inspection, blueprint silhouette and timed checklist.
{
 const c=new Canvas(1600,1100,{background:'#0C2740'}),ink='#E2F6FB',cyan='#68D9DF',muted='#9ABDCF';
 for(let x=45;x<1600;x+=40)c.line(x,0,x,1100,'#15354F',1);for(let y=18;y<1100;y+=40)c.line(0,y,1600,y,'#15354F',1);
 T(c,60,46,1160,43,'圆周  /  READY TO RIDE',26,cyan,true);T(c,60,118,1200,75,'出发前，给车 60 秒',59,ink,true);T(c,63,215,1380,45,'四次确认，每次15秒。发现异常，先处理再出发。',26,muted);
 const wx=[360,1170],wy=500,rr=164;wx.forEach(x=>{c.circle(x,wy,rr,'#0C2740',{border:'5 SOLID #CDEFF5'});c.circle(x,wy,rr-12,'#0C2740',{border:'1 SOLID #5C899F'});for(let i=0;i<16;i++){const a=i*Math.PI/8;c.line(x,wy,x+(rr-15)*Math.cos(a),wy+(rr-15)*Math.sin(a),'#466E85',1);}c.circle(x,wy,10,cyan);});
 c.polyline([[360,500],[625,310],[700,500],[360,500],[555,480],[625,310],[1080,310],[700,500],[555,480]],cyan,9,{roundCaps:true});c.line(1080,310,1170,500,cyan,9);c.line(625,310,610,278,cyan,9);c.line(568,272,643,272,ink,11,{roundCaps:true});c.polyline([[1080,310],[1068,270],[1130,254],[1151,280]],ink,9,{roundCaps:true});c.circle(700,500,31,'#0C2740',{border:'5 SOLID #E2F6FB'});c.line(700,500,749,542,ink,6);c.line(735,549,771,549,cyan,6);
 T(c,748,398,284,42,'60 SEC CHECK',23,cyan,true);T(c,748,445,284,42,'检查图 · 非维修手册',20,muted);
 const items=[['01','轮胎','目视有无裂口与异物。\n按胎侧范围确认胎压。'],['02','刹车','推车捏前、后刹车，\n确认两轮能可靠停住。'],['03','传动','转动曲柄，确认链条顺畅。\n检查快拆或轴已锁紧。'],['04','可见性','头盔戴稳；按出行条件\n确认前后灯与反光件。']];
 items.forEach((a,i)=>{const x=60+i*383,y=724;c.rect(x,y,348,270,'#12334F',{radius:16,border:'1 SOLID #41667D'});T(c,x+24,y+20,120,45,a[0],32,cyan,true);T(c,x+235,y+25,92,40,'15秒',22,muted);T(c,x+24,y+80,300,49,a[1],31,ink,true);T(c,x+24,y+144,302,98,a[2],22,ink);});
 c.polyline([[360,590],[170,680],[170,707]],cyan,2);c.polyline([[1142,398],[640,656],[640,707]],cyan,2);c.polyline([[700,530],[934,684],[934,707]],cyan,2);c.polyline([[1112,257],[1450,357],[1450,707]],cyan,2);
 T(c,60,1036,1490,37,'静态设计演示 · 不提供统一胎压值 · 60秒是检查节奏建议，处理异常需要额外时间',20,muted);
 save('case-09',c,{title:'圆周 · 骑行前60秒',audience:'准备出发的通勤骑行者',use_context:'1600×1100车库/手机横屏检查卡',user_goal:'按轮胎、刹车、传动、可见性顺序完成出发前检查',visual_intent:'工程蓝图自行车与四条连接线，把可检查部位连接到操作',completion_criteria:['四项各15秒','不给统一胎压','具体可操作检查语句','发现异常处理后出发'],checks:{step_seconds:[15,15,15,15],total_seconds:60}});
}
// 10: 90 exact minute ticks, current time and three phase arcs.
{
 const c=new Canvas(1200,1200,{background:'#FBF7EE'}),ink='#242A3A',orange='#CF693E',mint='#689E90',muted='#727684';
 T(c,60,38,1050,40,'专注90  /  MAKE ROOM FOR DEEP WORK',24,ink,true);T(c,60,101,1080,72,'留一段时间，完成一件事',47,ink,true);
 const cx=414,cy=564,r=294;const phases=[{m:15,c:orange},{m:60,c:ink},{m:15,c:mint}];
 const point=(min,rad)=>{const a=-Math.PI/2+min/90*2*Math.PI;return[cx+rad*Math.cos(a),cy+rad*Math.sin(a)];};
 for(let m=0;m<90;m++){const col=m<15?orange:m<75?ink:mint;c.line(...point(m,r-20),...point(m,r+(m%5===0?12:0)),col,m<38?5:2.5);}
 let s=0;for(const a of phases){const p=[];for(let q=0;q<=a.m*4;q++)p.push(point(s+q/4,r-46));c.polyline(p,a.c,8,{roundCaps:true});s+=a.m;}
 c.circle(cx,cy,227,'#F5F0E5');c.circle(...point(38,r-46),11,orange,{border:'4 SOLID #FBF7EE'});c.line(cx,cy,...point(38,170),orange,3,{roundCaps:true});
 T(c,cx-150,cy-100,300,54,'现在 14:38',31,muted);T(c,cx-167,cy-38,334,91,'52',79,ink,true);T(c,cx-130,cy+53,260,48,'分钟剩余',25,muted);T(c,280,223,276,42,'14:00 开始',24,orange);T(c,283,884,286,43,'15:30 完成',24,mint);
 T(c,779,264,355,54,'今天的唯一目标',28,ink,true);T(c,779,330,355,96,'写出一页\n项目摘要',38,ink,true);
 const info=[['14:00–14:15','准备 15分钟','关提醒，打开材料；\n写下3个关键问题。',orange],['14:15–15:15','深度工作 60分钟','按问题整理要点；\n写成3段摘要。',ink],['15:15–15:30','收束 15分钟','检查事实与遗漏；\n留下下一步行动。',mint]];
 info.forEach((a,i)=>{let y=482+i*146;c.line(779,y,1125,y,'#D8D5CB',1);c.circle(787,y+31,6,a[3]);T(c,808,y+13,331,37,a[0],23,a[3],true);T(c,779,y+55,354,39,a[1],24,ink,true);T(c,779,y+96,354,73,a[2],20,muted);});
 c.rect(60,1007,1080,94,ink,{radius:16});T(c,87,1030,1025,55,'完成标准  /  一页摘要包含：结论、3条依据、1个下一步。',26,'#FBF7EE');
 T(c,60,1133,1090,33,'静态计时演示 · 14:38已过38分钟 / 90分钟 · 每格1分钟，整圈90格',20,muted);
 save('case-10',c,{title:'专注90 · 一件事的时间',audience:'安排90分钟学习或写作时段的人',use_context:'1200×1200桌面学习计划/平板静态演示',user_goal:'知道当前处于深度工作阶段，剩52分钟，并有明确交付标准',visual_intent:'90个真实分钟刻度和三色阶段弧，让时间结构成为主图',completion_criteria:['90刻度','15+60+15=90','14:38已38分钟剩52','3阶段及完成标准完整'],checks:{tick_count:90,total_minutes:90,phase_minutes:[15,60,15],elapsed_minutes:38,remaining_minutes:52}});
}
