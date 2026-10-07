'use strict';
const fs=require('fs'),path=require('path');
const revision_started_at=new Date().toISOString();
const source=fs.readFileSync(path.join(__dirname,'generate-v001.cjs'),'utf8');
let case02=source.slice(0,source.indexOf('// CASE 03:'));
case02=case02.replace('const widths=[235,235,132,354,176]','const widths=[236,236,59,354,177]');
case02=case02.replace("txt(c,x+13,y+14,w-32,38,row[0]+' min',i===2?22:29,i===3?'#FFFFFF':ink,{bold:true});","txt(c,x+(i===2?3:13),y+14,w-(i===2?12:32),38,i===2?'5':row[0]+' min',i===2?24:29,i===3?'#FFFFFF':ink,{bold:true,align:i===2?'CENTER':'START'});if(i===2)txt(c,x+3,y+55,w-12,25,'min',15,ink,{align:'CENTER'});");
case02=case02.replaceAll('case-02-v001.snapshot','case-02-v002.snapshot').replaceAll('case-02-content-v001.json','case-02-content-v002.json').replaceAll('case-02-notes-v001.md','case-02-notes-v002.md');
new Function('require','__dirname','console',case02)(require,__dirname,console);
for(const n of ['02','03','04']){
 const meta=JSON.parse(fs.readFileSync(path.join(__dirname,`case-${n}-content-${n==='02'?'v002':'v001'}.json`),'utf8'));
 meta.creation_start_time=null;meta.creation_start_time_unknown_reason='创作全过程未在开始时持久化UTC时间，不从文件mtime倒推。';
 meta.dsl_generated_at=fs.statSync(path.join(__dirname,`case-${n}-${n==='02'?'v002':'v001'}.snapshot`)).mtime.toISOString();
 meta.use_context=meta.viewing_environment;meta.user_goal=meta.user_action;meta.content_basis=meta.data_provenance;meta.visual_intent=meta.visual_choice;
 meta.dsl_capabilities=n==='02'?['Stack/Positioned spatial layout','Container circles and rounded room geometry','Transform lines and arrows','minute-scaled time segments','Text/Raw typography']:n==='03'?['transformed ClipOval leaves and cutouts','stem line geometry','rounded Container pot/UI','conditional decision branches in Text','phone-scale absolute layout']:['transformed ClipOval handle and layered cup geometry','polyline steam','Text/Raw price columns','Container editorial dividers','complete ordering rules'];
 meta.checks={arithmetic:meta.data_validation,programmatic:{self_contained:true,external_image_count:0,parser_tags_documented:true},actual_visual_review:null,actual_visual_review_reason:'root尚未调用真实服务或打开对应图片，不能把本数据核验作视觉通过。'};
 if(n==='02')meta.checks.programmatic.timeline_widths=[236,236,59,354,177];
 fs.writeFileSync(path.join(__dirname,`case-${n}-metadata-v002.json`),JSON.stringify(meta,null,2)+'\n',{flag:'wx'});
}
fs.writeFileSync(path.join(__dirname,'revision-evidence-v002.json'),JSON.stringify({revision_started_at,completed_at:new Date().toISOString(),changes:[{case:'case-02',parent:'v001',new:'v002',reason:'修复分钟条5分钟段错误宽度与越界',widths:[236,236,59,354,177],sum:1062,scale_px_per_minute:11.8,extent:[65,1127],canvas_width:1200}],metadata:'补全root所需字段；未测量的创作开始时间为null',render_called:false,public_logs_changed:false},null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({case02:'case-02-v002.snapshot',case03:'case-03-v001.snapshot',case04:'case-04-v001.snapshot',metadata:['case-02-metadata-v002.json','case-03-metadata-v002.json','case-04-metadata-v002.json']}));
