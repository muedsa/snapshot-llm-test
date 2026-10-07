'use strict';
const fs=require('node:fs'),path=require('node:path'),s=require('../_suite/suite.cjs');
const image=path.join(__dirname,'requests/A07-request-000003/response.png');
const view=s.view('A07',image,{tool:'view_image',reviewer:'infrastructure_resume',version_id:'A07-travel-v002',observation:'Actually reopened full v002 following independent semantic review: Q2 orange notice begins 普通路线不适用 and ends 不能换乘. This can imply the ordinary trip cannot transfer at S05, while the real restriction applies only to an accessible trip. All route facts and layout remain correct. Change the notice prefix to 无障碍不适用 to scope its prohibition accurately.'});
let source=fs.readFileSync(path.join(__dirname,'build-travel-v002.cjs'),'utf8');
const edits=[
  ['普通路线不适用：东桥 S05 设施不足，不能换乘。','无障碍不适用：东桥 S05 设施不足，不能换乘。'],
  ['travel-card-v002.snapshot','travel-card-v003.snapshot'],
  ['travel-card-content-v002.json','travel-card-content-v003.json'],
  ["version_id:'A07-travel-v002'","version_id:'A07-travel-v003'"],
  ["parent_version:'A07-travel-v001',before_view_id:'A07-view-000001',changes:'Center R/B/G letters in every colored line chip after actual baseline edge-crowding observation'",`parent_version:'A07-travel-v002',before_view_id:'${view.id}',changes:'Clarify that the Q2 S05 transfer prohibition is for accessible trips by changing the notice prefix from ordinary route to accessibility'`]
];
for(const [old,next] of edits){if(!source.includes(old))throw Error('Missing exact edit target: '+old);source=source.split(old).join(next);}
fs.writeFileSync(path.join(__dirname,'build-travel-v003.cjs'),source,{flag:'wx'});
fs.writeFileSync(path.join(__dirname,'travel-edit-v003.json'),JSON.stringify({version_id:'A07-travel-v003',parent_version:'A07-travel-v002',before_view_id:view.id,before_view:view,edits,source:'build-travel-v002.cjs',result:'build-travel-v003.cjs',published_final_modified:false},null,2)+'\n',{flag:'wx'});
process.stdout.write(JSON.stringify({before_view_id:view.id})+'\n');
