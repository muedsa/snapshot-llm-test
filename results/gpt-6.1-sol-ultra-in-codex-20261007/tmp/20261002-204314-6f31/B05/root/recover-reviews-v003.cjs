const fs=require('node:fs'),path=require('node:path'),s=require('../../_suite/suite.cjs');
const f=path.join(__dirname,'reviews-v003.json'),r=JSON.parse(fs.readFileSync(f));
const result=[];
for(const x of r.images){const m=JSON.parse(fs.readFileSync(x.meta_path));let v;
if(m.id==='B05-request-000013'){v=s.countsFor('B05').views.find(v=>v.id==='B05-view-000011');if(!v||v.sha256!==m.response_sha256)throw Error('Partial record mismatch');}
else v=s.view('B05',m.image_path,{tool:'view_image',reviewer:'root',version_id:m.version_id,case_id:m.case_id,observation:x.observation});
s.iteration('B05',{type:'visual',completed:true,phase:'actual-image-reviewed',version_id:m.version_id,parent_version:m.parent_version,case_id:m.case_id,request_id:m.id,after_view_id:v.id,observation:x.observation,...x.iteration,changes:x.iteration.comparison});
s.toolUsage('B05',{tool:'functions.view_image',case_id:m.case_id,input:m.image_path,output:f,view_id:v.id,purpose:'Real view occurred in previous context; delayed bookkeeping; case08 existing record reused.'});
s.taskCheckpoint('B05',{case_id:m.case_id,event_type:'case-reviewed',visual_review_evidence:[v.id],resume_notes:x.observation});result.push(v);}
fs.writeFileSync(path.join(__dirname,'reviews-v003-recovered.json'),JSON.stringify({original_failure:'record-reviews missing changes field stopped after view11, no HTTP; recovered existing view11 without duplicate count.',views:result},null,2),{flag:'wx'});s.writeTaskMetrics('B05');console.log(result.map(v=>v.id));
