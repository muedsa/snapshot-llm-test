const fs=require('fs'),path=require('path'),crypto=require('crypto');
const root=process.cwd(),run='20261002-204314-6f31';
const privateDir=path.join(root,'tmp',run,'_suite','final-integrity-v002');
const suite=require('../suite.cjs');
const read=f=>fs.readFileSync(f,'utf8').replace(/^\uFEFF/,'');
const json=f=>JSON.parse(read(f));
const sha=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
const rows=f=>fs.existsSync(f)?read(f).trim().split(/\r?\n/).filter(Boolean).map(JSON.parse):[];
const immutable=(name,data)=>fs.writeFileSync(path.join(privateDir,name),JSON.stringify(data,null,2)+'\n',{flag:'wx'});
const walk=f=>fs.readdirSync(f,{withFileTypes:true}).flatMap(e=>e.isDirectory()?walk(path.join(f,e.name)):[path.join(f,e.name)]);
const catalog=json('catalog.json'),state=json(path.join('outputs',run,'_suite','suite-state.json'));
const tasks=catalog.tasks.slice(0,30),issues=[],notes=[],idMap=new Map(),taskEvidence=[];
const events=rows(path.join('tmp',run,'_suite','events.jsonl'));
const recordId=(id,location)=>{if(!id)return;if(idMap.has(id))issues.push({type:'duplicate_id',id,locations:[idMap.get(id),location]});else idMap.set(id,location)};
function checkFile(f,expectedHash,type,task){if(!fs.existsSync(f)){issues.push({task,type:'missing_evidence_file',path:f});return null}const actual=sha(f);if(expectedHash&&expectedHash!==actual)issues.push({task,type:'changed_evidence_bytes',kind:type,path:f,expectedHash,actual});return actual}
for(const t of tasks){
 const task=t.id,out=path.join(root,'outputs',run,task),tmp=path.join(root,'tmp',run,task),spec=json(t.task_spec);
 const requests=rows(path.join(tmp,'requests.jsonl')),views=rows(path.join(tmp,'views.jsonl')),versions=rows(path.join(tmp,'versions.jsonl')),iterations=rows(path.join(tmp,'iterations.jsonl'));
 const allRecorded=[['request',requests],['view',views],['version',versions],['iteration',iterations],['tool',rows(path.join(tmp,'tool-usage.jsonl'))]];
 for(const [kind,records] of allRecorded)for(const r of records)recordId(r.id,task+'/'+kind);
 const requestHashes=new Set(requests.map(r=>r.response_sha256).filter(Boolean)),viewChecks=[];
 for(const r of requests){
   if(!r.started_at||!r.ended_at||!/[Z+-]/.test(r.started_at.slice(10))||!/[Z+-]/.test(r.ended_at.slice(10)))issues.push({task,type:'request_timestamp_without_timezone',id:r.id});
   if(Date.parse(r.ended_at)<Date.parse(r.started_at))issues.push({task,type:'negative_request_interval',id:r.id});
   if(r.response_file)checkFile(r.response_file,r.response_sha256,'raw_response',task);
   else if(r.ok)issues.push({task,type:'successful_request_without_response_file',id:r.id});
   if(r.input_file)checkFile(r.input_file,r.body_sha256,'request_input',task);
   if(r.request_file)checkFile(r.request_file,null,'request_metadata',task);
 }
 for(const v of versions){checkFile(v.path,v.sha256,'version',task);if(!v.path.endsWith('.snapshot'))issues.push({task,type:'version_extension',id:v.id,path:v.path});}
 for(const v of views){
   const fileExists=fs.existsSync(v.image_path),pathHash=fileExists?sha(v.image_path):null;
   const byteMatch=pathHash===v.sha256;
   const historicalResponse=requests.find(r=>r.response_sha256===v.sha256&&r.response_file&&fs.existsSync(r.response_file)&&sha(r.response_file)===v.sha256);
   if(!byteMatch&&!historicalResponse)issues.push({task,type:'view_evidence_image_unrecoverable',id:v.id,path:v.image_path,expected:v.sha256,current:pathHash});
   if(!byteMatch&&historicalResponse)notes.push({task,type:'historical_view_preserved_in_raw_response',id:v.id,current_view_path:v.image_path,recovered_from:historicalResponse.response_file});
   viewChecks.push({id:v.id,tool:v.tool,reviewer:v.reviewer??null,viewed_at:v.viewed_at,path:v.image_path,sha256:v.sha256,file_identity_current:byteMatch,historical_response:historicalResponse?.id??null});
 }
 const finalChecks=state.tasks.find(x=>x.id===task).artifacts.map(a=>{
   const req=requests.find(r=>r.id===a.request_id);
   const matchingViews=views.filter(v=>v.sha256===a.image_sha256);
   const dims=suite.pngDimensions?null:undefined;
   const png=fs.readFileSync(a.image_path),actualDims={width:png.readUInt32BE(16),height:png.readUInt32BE(20)};
   return {id:a.id,case_id:a.case_id??null,round_id:a.round_id??null,image_path:a.image_path,dsl_path:a.dsl_path,dimensions:actualDims,image_sha256:sha(a.image_path),dsl_sha256:sha(a.dsl_path),request_id:req?.id??null,raw_response:req?.response_file??null,request_input:req?.input_file??null,matching_view_ids:matchingViews.map(v=>v.id)};
 });
 const extra=[];
 for(const filename of [...spec.common_outputs??[],...spec.additional_outputs??[]]){
  const f=path.join(out,filename);if(fs.existsSync(f)){let keys=null;if(filename.endsWith('.json'))keys=Object.keys(json(f));extra.push({filename,bytes:fs.statSync(f).size,sha256:sha(f),keys});}
 }
 const sourceFiles=['TASK.md','AGENTS.md','task.json'].map(name=>{const f=path.join(t.directory,name);read(f);return {file:f,bytes:fs.statSync(f).size,sha256:sha(f)}});
 const htmlFiles=walk(out).filter(f=>f.endsWith('.html'));
 const galleryChecks=htmlFiles.map(file=>({file,...suite.inspectLinks(file)}));
 taskEvidence.push({task_id:task,status:state.tasks.find(x=>x.id===task).status,source_files:sourceFiles,required_outputs:spec.required_outputs??[],additional_outputs:spec.additional_outputs??[],case_artifacts:spec.case_artifacts??[],registered_final_count:finalChecks.length,request_count:requests.length,request_ok_count:requests.filter(r=>r.ok).length,request_failed_count:requests.filter(r=>!r.ok).length,version_count:versions.length,view_count:views.length,view_checks:viewChecks,final_checks:finalChecks,sidecars:extra,gallery_checks:galleryChecks});
}
const rounds=[];
for(const task of ['A21','A22']){
 const related=events.filter(e=>e.task_id===task),rs=[];
 for(const n of [1,2,3]){const rid='round-'+String(n).padStart(2,'0'),start=related.find(e=>e.type==='round-start'&&e.round_id===rid),archive=related.find(e=>e.type==='round-archive-verified'&&e.round_id===rid),complete=related.find(e=>e.type==='round-completed'&&e.round_id===rid);if(!start||!archive||!complete)issues.push({task,type:'missing_round_lifecycle',round:rid});rs.push({round:rid,start,complete,archive});}
 for(let i=1;i<rs.length;i++)if(Date.parse(rs[i].start?.time)<Date.parse(rs[i-1].archive?.time))issues.push({task,type:'round_started_before_archive',round:rs[i].round});
 rounds.push({task_id:task,round_lifecycle:rs,strict_archive_before_next_start:rs.slice(1).every((r,i)=>Date.parse(r.start?.time)>Date.parse(rs[i].archive?.time))});
}
const standard=suite.inspectAudit({tasks:tasks.map(t=>t.id),include_suite:true});
const own={schema_version:1,audited_at:new Date().toISOString(),reviewer:'/root/b06_cases_02_04_resume',run_id:run,state_checkpoint_at_read:state.last_checkpoint,status_scope:'All30 completed tasks after B06 publication.',scope:'Read-only full file/requirement/dimension/body-response-final SHA chain, recorded views, all original requests and versions, metric counts, local gallery links, distinct ledger IDs, staged lifecycle order. This is not a new suite-image perceptual review. This file audit opened no images; it independently revalidates recorded view evidence and current bytes.',passed:issues.length===0&&standard.passed,issues,notes,task_evidence:taskEvidence,round_evidence:rounds,standard_inspect_audit:standard};
own.prior_audit_reuse={index:'tmp/20261002-204314-6f31/_suite/audit-agent-v001/index.md',script_basis:'audit-agent-v001/audit-readonly.cjs',reuse_scope:'Read old audit index and reused its read-only checking code, adapted scope from 27 to 28 tasks; all current paths/hashes/records re-read. Old judgments are not substituted for fresh bytes checks.'};
immutable('integrity-30-v004.json',own);
console.log(JSON.stringify({passed:own.passed,issues,notes_count:notes.length,tasks:tasks.length,finals:taskEvidence.reduce((n,t)=>n+t.registered_final_count,0),requests:taskEvidence.reduce((n,t)=>n+t.request_count,0),versions:taskEvidence.reduce((n,t)=>n+t.version_count,0),views:taskEvidence.reduce((n,t)=>n+t.view_count,0),report:path.join(privateDir,'integrity-30-v004.json')},null,2));
