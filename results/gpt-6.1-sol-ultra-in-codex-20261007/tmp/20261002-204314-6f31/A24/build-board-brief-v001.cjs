const fs=require('fs'),path=require('path'),s=require('../_suite/suite.cjs'),{Canvas}=require('../_suite/dsl.cjs');
const schedulePath=path.join(__dirname,'schedule-analysis/schedule.json'),d=JSON.parse(fs.readFileSync(schedulePath,'utf8'));
const rows=d.tasks.map(t=>({...t,start_min:t.start_minute,end_min:t.end_minute,start_time:t.start_clock,end_time:t.end_clock}));
const palette={bg:'#F2F5F1',card:'#FFFFFF',ink:'#18373C',muted:'#536F71',design:'#248C91',engineering:'#DFAC50',grid:'#D6E2DA',idle:'#E6ECE6',deadline:'#A84939'};
const maps=[];
function make(stem,w,h){const c=new Canvas(w,h,{background:palette.bg}),m={stem,width:w,height:h,schedule_source:schedulePath,schedule_sha256:s.sha256(fs.readFileSync(schedulePath)),texts:[],shapes:[],time_blocks:[],body_min_font:stem==='decision-brief'?24:20};maps.push(m);const T=(id,x,y,width,height,text,size=24,color=palette.ink,o={})=>{c.text(x,y,width,height,text,size,color,o);m.texts.push({id,box:[x,y,width,height],text,font_size:size,color,options:o});};const R=(id,x,y,width,height,color,o={})=>{c.rect(x,y,width,height,color,o);m.shapes.push({id,box:[x,y,width,height],color,options:o});};return {c,m,T,R};}
function board(){const {c,m,T,R}=make('execution-board',1920,1080),plotX=280,plotW=1540,scale=plotW/420;
 T('brand',64,38,980,83,d.input_snapshot?'叠光 · 发布演练':'叠光 · 发布演练',60,palette.ink,{bold:true});
 T('subtitle',67,133,940,44,'双团队执行泳道  /  2026-11-07',30,palette.muted);
 T('finish',1140,48,300,64,'13:20 完成',44,palette.design,{bold:true});
 T('buffer',1480,48,375,64,'160 min 缓冲',42,palette.ink,{bold:true});
 T('basis',1140,132,715,40,'已核可行排程 · 09:00 开工 / 16:00 截止',24,palette.muted);
 R('header-rule',64,201,1792,2,palette.grid);
 const annotations={R01:[280,383,200],R04:[350,493,244],R07:[622,383,244],R09:[819,493,250],R10:[987,383,262],R12:[1120,493,246],R02:[280,773,200],R03:[347,883,230],R05:[490,773,245],R06:[592,883,245],R08:[780,773,260],R11:[962,883,280]};
 for(const [team,baseY,axisY]of [['design',300,246],['engineering',682,628]]){
  const color=palette[team],teamName=team==='design'?'设计团队':'工程团队';
  T(team+'-label',65,baseY+2,190,44,teamName,30,palette.ink,{bold:true});
  T(team+'-latin',65,baseY+48,190,35,team,20,palette.muted);
  R(team+'-band',plotX,baseY,plotW,66,palette.idle,{radius:7});
  for(let hour=9;hour<=16;hour++){const px=plotX+(hour-9)*60*scale;T(team+'-tick-'+hour,px-43,axisY,86,35,String(hour).padStart(2,'0')+':00',22,palette.muted,{align:'CENTER'});R(team+'-grid-'+hour,px,baseY-8,1,82,palette.grid);}
  for(const t of rows.filter(t=>t.team===team)){
   const x=plotX+t.start_min*scale,w=t.minutes*scale;
   R('task-'+t.id,x,baseY,w,66,color,{radius:5});
   T('block-id-'+t.id,x+4,baseY+7,w-8,30,t.id,24,team==='design'?'#FFFFFF':palette.ink,{bold:true,align:'CENTER'});
   T('block-minutes-'+t.id,x+4,baseY+38,w-8,25,t.minutes+'m',20,team==='design'?'#FFFFFF':palette.ink,{align:'CENTER'});
   const [ax,ay,aw]=annotations[t.id],center=x+w/2;
   c.line(center,baseY+68,ax+aw/2,ay-6,palette.muted,1);
   R('annotation-'+t.id,ax,ay,aw,96,palette.card,{radius:8,border:'1 SOLID '+palette.grid});
   T('label-'+t.id,ax+12,ay+8,aw-24,31,t.label,22,palette.ink,{bold:true});
   T('times-'+t.id,ax+12,ay+42,aw-24,27,t.start_time+'–'+t.end_time,20,palette.ink);
   T('dependencies-'+t.id,ax+12,ay+71,aw-24,25,'依赖 '+(t.depends.length?t.depends.join(' · '):'—'),20,palette.muted);
   m.time_blocks.push({id:t.id,label:t.label,team,start_minute:t.start_min,end_minute:t.end_min,minutes:t.minutes,box:[x,baseY,w,66],annotation_box:[ax,ay,aw,96],x_scale_px_per_minute:scale});
  }
  R(team+'-finish-mark',plotX+260*scale,baseY-8,2,82,palette.design);
  R(team+'-deadline',plotX+420*scale,baseY-12,3,90,palette.deadline);
 }
 T('design-idle',280,596,1130,33,'空档 10:25–10:30   ·   工作 255 min   ·   同团队任务不重叠',22,palette.muted);
 T('buffer-band-caption',1316,321,425,36,'13:20–16:00  计划缓冲',24,palette.muted);
 T('engineering-idle',280,991,1460,34,'空档 12:20–12:25、12:55–13:20   ·   工作 230 min   ·   13:20后进入全局缓冲',22,palette.muted);
 T('engineering-free-caption',1324,701,425,36,'12:55后工程团队空闲',24,palette.muted);
 T('footer',64,1042,1784,30,'真实时间同尺度：09:00 → 16:00  /  任务编号连接标签与依赖索引  /  12项完整执行，保留全部检查',20,palette.muted);
 m.timeline={origin_x:plotX,width:plotW,start_time:'09:00',end_time:'16:00',span_minutes:420,scale_px_per_minute:scale,deadline_x:plotX+plotW,finish_x:plotX+260*scale,finish_minutes:260};
 return {c,m};}
function brief(){const {c,m,T,R}=make('decision-brief',1200,1600);
 T('brand',60,40,1080,61,'叠光 · 发布演练',42,palette.ink,{bold:true});
 T('title',60,116,1080,82,'先排资源，再作交付。',56,palette.ink,{bold:true});
 T('date',63,204,1070,40,'2026-11-07  /  09:00 开工  /  16:00 截止',26,palette.muted);
 const cards=[['finish','13:20','计划完成',60,266,palette.design],['buffer','160 min','截止前缓冲',616,266,palette.ink],['work','485 min','总工作量；÷2下界242.5min',60,434,palette.ink],['cp','255 min','忽略资源关键路径；综合下界255min',616,434,palette.ink]];
 for(const [id,val,label,x,y,color]of cards){R('card-'+id,x,y,524,148,palette.card,{radius:14});T('kpi-'+id,x+24,y+18,476,73,val,54,color,{bold:true});T('kpi-label-'+id,x+24,y+104,476,34,label,24,palette.muted);}
 T('dependencies-title',60,617,1080,48,'依赖概览  /  原时长与先决保持',32,palette.ink,{bold:true});
 for(let i=0;i<12;i++){const t=rows[i],col=i<6?0:1,r=i%6,x=60+col*556,y=679+r*66;R('dep-rule-'+t.id,x,y+61,524,1,palette.grid);T('dep-label-'+t.id,x,y,524,32,t.id+'  '+t.label,24,palette.ink,{bold:true});T('dep-list-'+t.id,x,y+32,524,30,'先决 '+(t.depends.length?t.depends.join(' / '):'无')+'  ·  '+t.minutes+'min',24,palette.muted);}
 T('risks-title',60,1100,1080,50,'三项风险，三项现场对策',32,palette.ink,{bold:true});
 for(let i=0;i<3;i++){const risk=d.risks[i],y=1160+i*99;R('risk-'+risk.id,60,y,1080,88,palette.card,{radius:10});T('risk-impact-'+risk.id,80,y+10,1035,34,risk.id+' / '+risk.task+'  '+risk.impact,26,palette.ink,{bold:true});T('risk-mitigation-'+risk.id,80,y+48,1035,33,risk.mitigation,24,palette.muted);}
 T('method1',60,1470,1080,39,'依据：单团队无并行、不可抢占；可选团队仅择一执行。',24,palette.ink);
 T('method2',60,1513,1080,39,'已核可行260min，距基础下界5min；不在此宣称全局最优。',24,palette.muted);
 T('method3',60,1554,1080,34,'关键路径 R01 → R04 → R07 → R09 → R10 → R12',24,palette.muted);
 m.summary={finish:'13:20',buffer_minutes:160,total_work_minutes:485,critical_path_minutes:255,workload_lower_bound_minutes:242.5,combined_lower_bound_minutes:255,feasible_makespan_minutes:260};return {c,m};}
const outputs=[board(),brief()];for(const {c,m}of outputs){const p=path.join(__dirname,m.stem+'-draft-v001.snapshot');fs.writeFileSync(p,c.toString(),{flag:'wx'});m.dsl_path=p;m.dsl_sha256=s.sha256(c.toString());fs.writeFileSync(path.join(__dirname,m.stem+'-map-v001.json'),JSON.stringify(m,null,2)+'\n',{flag:'wx'});}
fs.writeFileSync(path.join(__dirname,'board-brief-build-result-v001.json'),JSON.stringify({files:maps.map(m=>({stem:m.stem,dsl_path:m.dsl_path,map_path:path.join(__dirname,m.stem+'-map-v001.json')})),all_writes_finished:true},null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({files:maps.map(m=>m.dsl_path),all_writes_finished:true}));
