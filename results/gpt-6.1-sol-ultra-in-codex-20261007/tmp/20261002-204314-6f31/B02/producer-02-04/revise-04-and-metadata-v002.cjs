'use strict';
const fs=require('fs'),path=require('path');
const started=new Date().toISOString();
let source=fs.readFileSync(path.join(__dirname,'generate-v001.cjs'),'utf8');
source=source.replaceAll('B02-one-project-visual-ecosystem','B02-one-client-ten-touchpoints');
source=source.replace('case_id:id,dimensions:','case_id:id,title:meta.title,dimensions:');
source=source.replace('x1+62,y1+67','x1+62,y1+159').replace('x1+133,y1+69','x1+133,y1+157');
source=source.replace('x1+78,y1+88,x1+149,y1+174','x1+78,y1+138,x1+149,y1+52').replace('x1+117,y1+89,x1+47,y1+174','x1+117,y1+137,x1+47,y1+52').replace('x1+98,y1+115','x1+98,y1+111');
source=source.replaceAll('-v001.snapshot','-v002.snapshot').replaceAll('-metadata-v001.json','-metadata-v002.json').replaceAll('-notes-v001.md','-notes-v002.md');
new Function('require','__dirname','process','console',source)(require,__dirname,{argv:['node','generate-v001.cjs','04']},console);
for(const [n,title] of [['02','预约确认界面'],['03','到店签到与空间导览']]){
 const meta=JSON.parse(fs.readFileSync(path.join(__dirname,`case-${n}-metadata-v001.json`),'utf8'));
 meta.title=title;meta.source_reads=meta.source_reads.map(s=>s.replaceAll('B02-one-project-visual-ecosystem','B02-one-client-ten-touchpoints'));
 fs.writeFileSync(path.join(__dirname,`case-${n}-metadata-v002.json`),JSON.stringify(meta,null,2)+'\n',{flag:'wx'});
 const old=fs.readFileSync(path.join(__dirname,`case-${n}-notes-v001.md`),'utf8');fs.writeFileSync(path.join(__dirname,`case-${n}-notes-v002.md`),old.replace(`# case-${n} /`,`# ${title} /`),{flag:'wx'});
}
fs.writeFileSync(path.join(__dirname,'revision-evidence-v002.json'),JSON.stringify({started_at:started,ended_at:new Date().toISOString(),changes:[{case_id:'case-04',before:'v001',after:'v002',type:'local draft consistency correction before service',reason:'剪刀手柄图形朝上但文字要求朝下，将剪刀纵坐标镜像，使手柄朝下/刀刃朝上；正文和工具数量不变'},{case_ids:['case-02','case-03','case-04'],metadata:'补标题并改实际任务资料目录为B02-one-client-ten-touchpoints'}],http_called:false,image_viewed:false,public_logs_mutated:false},null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({snapshots:['case-02-v001.snapshot','case-03-v001.snapshot','case-04-v002.snapshot'],metadata:['case-02-metadata-v002.json','case-03-metadata-v002.json','case-04-metadata-v002.json']}));
