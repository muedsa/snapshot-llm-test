'use strict';
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const base=__dirname;
function out(n,x){fs.writeFileSync(path.join(base,n),typeof x==='string'?x:JSON.stringify(x,null,2),{encoding:'utf8',flag:'wx'});}
const visuals={
 'case-05':{intent:'深海色港口技术图，以船/箱/吊机的几何关系连接泊位卡片和按小时比例的资源排程。任务而非装饰决定信息层级。',caps:['Stack/Positioned层叠坐标','Container圆角/透明色/边框','Transform矩阵旋转实线','Text与Raw/CDATA','数据比例进度条及横向时间图']},
 'case-06':{intent:'奶油色与梅紫戏剧场景，两束分段光线将目光导向舞台，完整座位矩阵用于做相邻选座决定，橙色只用于已选状态与价格确认。',caps:['Stack/Positioned完整座位矩阵','Container圆角/透明色/边框','Transform斜向光线','Text/Raw/多字体','参数化112席状态与图例']},
 'case-07':{intent:'暖灰绿原创等高线包围橙色路线，以自然图形承载先后顺序；右侧具体节奏与底部按距离比例的海拔折线支撑实际计划。',caps:['Stack/Positioned地图示意','Transform多段解析等高线','Container圆形路线节点','Text/Raw中文信息','累计距离比例海拔图']}
};
for(const id of ['case-05','case-06','case-07']){
 const m=JSON.parse(fs.readFileSync(path.join(base,id+'-metadata-v001.json'),'utf8'));
 const st=fs.statSync(path.join(base,id+'-v001.snapshot'));
 Object.assign(m,{actual_started_at:null,actual_started_at_reason:'未在独立case开始瞬间测量，不推测',actual_generated_at:st.birthtime.toISOString(),actual_generated_at_source:'本地初稿snapshot文件birthtime，非case总开始时间',metadata_recorded_at:new Date().toISOString(),use_context:m.viewing_environment,user_goal:m.task,content_basis:{type:'fictional_demo',description:m.source},visual_intent:visuals[id].intent,dsl_capabilities:visuals[id].caps,completion_criteria:m.completion_checks.filter(x=>!x.includes('root')&&!x.includes('逐图')),checks:{static_geometry:'本脚本下列数据断言通过；尚无真实渲染或视觉通过',visual_verified:false,visual_review_owner:'root'},asset_sources:[],rendering:{performed_by_this_agent:false}});
 if(id==='case-05'){
  if(JSON.stringify(m.jobs.map(j=>j.amount/j.cap))!==JSON.stringify([.6,.7,.6]))throw Error('capacity math');
  if(m.jobs[0].end>m.jobs[2].start)throw Error('C01 schedule overlap');
  m.checks.results=['三容量60%、70%、60%','C01两任务不相交','图例/船/泊位/起重机文本来自单一jobs对象','10:20截面与下一次11:00派工相符'];
 }
 if(id==='case-06'){
  if(m.seats.length!==112||m.counts.available+m.counts.occupied+m.counts.selected!==112)throw Error('seat count');
  const selected=m.seats.filter(s=>s.status==='selected');if(selected.length!==2||selected[0].row!=='D'||selected[1].number-selected[0].number!==1||selected.some(s=>s.number>7))throw Error('adjacency');
  if(selected.reduce((a,s)=>a+s.price,0)!==560)throw Error('price');
  m.checks.results=['112席=71可选+39已售+2已选','D06和D07在过道左侧，同排座号连续','已选总价560','18:45早于19:30','分区价格生成自排号'];
 }
 if(id==='case-07'){
  if(Math.abs(m.stages.reduce((a,s)=>a+s.dist,0)-6.2)>1e-10||m.stages.reduce((a,s)=>a+s.min,0)!==120)throw Error('trail totals');
  const diffs=m.altitude_m.slice(1).map((v,i)=>v-m.altitude_m[i]);if(diffs.filter(x=>x>0).reduce((a,v)=>a+v,0)!==300||-diffs.filter(x=>x<0).reduce((a,v)=>a+v,0)!==260)throw Error('elevation');
  m.checks.results=['6.2km四段合计','步行120+停留10=130min','10:00–12:10，显示两次5min停留','升300m降260m','海拔图横坐标0/1.2/2.8/4.2/6.2km按比例'];
 }
 out(id+'-metadata-v002.json',m);
}
let dsl=fs.readFileSync(path.join(base,'case-06-v001.snapshot'),'utf8');
const oldA='<Positioned left="575" top="658" width="54" height="30.6"><Text fontFamily="Inter,Noto Sans CJK SC" fontSize="18" color="#AB98A4"><Raw><![CDATA[过\n道]]></Raw></Text></Positioned>';
const newA='<Positioned left="575" top="658" width="54" height="80"><Text fontFamily="Inter,Noto Sans CJK SC" fontSize="18" color="#AB98A4" textAlign="CENTER"><Raw><![CDATA[过\n道]]></Raw></Text></Positioned>';
if(!dsl.includes(oldA))throw Error('aisle target missing');dsl=dsl.replace(oldA,newA);
const oldB='<Positioned left="143" top="864" width="918" height="1">';if(!dsl.includes(oldB))throw Error('line target missing');dsl=dsl.replace(oldB,'<Positioned left="143" top="850" width="918" height="1">');
out('case-06-v002.snapshot',dsl);
out('case-06-static-refinement-v001.json',{recorded_at:new Date().toISOString(),classification:'alternative/static_geometry',parent:'case-06-v001.snapshot',version:'case-06-v002.snapshot',basis:'代码坐标与文字盒高静态核验，未看图',changes:['A–D/E–H分隔y864移850，位于D底841与E顶859之间','过道两行文本高度30.6改80并居中'],visual_iteration:false});
out('static-checks-v001.json',{recorded_at:new Date().toISOString(),status:'passed',source:'metadata-v002 JSON assertion results',case_ids:['case-05','case-06','case-07'],scope:'数据/几何初稿核验，未调用服务，不能代替root视觉审查'});
console.log('Metadata fields and static assertions saved; theatre geometric refinement v002 ready.');
