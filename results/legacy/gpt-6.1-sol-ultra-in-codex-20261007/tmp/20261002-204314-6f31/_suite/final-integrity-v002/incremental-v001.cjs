'use strict';
const fs=require('fs'),path=require('path'),crypto=require('crypto'),dir=__dirname,root=process.cwd(),run='20261002-204314-6f31';
const read=f=>fs.readFileSync(f,'utf8').replace(/^\uFEFF/,''),json=f=>JSON.parse(read(f)),sha=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex'),rows=f=>read(f).trim().split(/\r?\n/).filter(Boolean).map(JSON.parse);
const state=json(path.join(dir,'suite-state-at-incremental-read-v001.json')),selection=json(path.join(root,'tmp',run,'B06','root','selection-v001.json'));
const issues=[],cases=[],hashes=new Map(),oldHashes=new Map(),decode=[];
for(const task of state.tasks.filter(t=>t.id.startsWith('A')))for(const a of task.artifacts)oldHashes.set(sha(a.image_path),task.id+'/'+a.id);
for(const task of ['B01','B02','B03','B04','B05']){
const base=path.join(root,'outputs',run,task),portfolio=json(path.join(base,'portfolio.json')),t=state.tasks.find(t=>t.id===task);
if(portfolio.cases.length!==10)issues.push({task,type:'creative_count',actual:portfolio.cases.length});
for(const c of portfolio.cases){const image=path.join(base,c.png),dsl=path.join(base,c.snapshot),ih=sha(image),dh=sha(dsl);const a=t.artifacts.find(a=>a.case_id===c.id);
if(!a||a.image_sha256!==ih||a.dsl_sha256!==dh)issues.push({task,case_id:c.id,type:'formal_pair_mismatch'});
if(hashes.has(ih)||oldHashes.has(ih))issues.push({task,case_id:c.id,type:'identical_previous_final',previous:hashes.get(ih)||oldHashes.get(ih)});hashes.set(ih,task+'/'+c.id);
for(const k of ['audience','use_context','user_goal','content_basis','visual_intent','completion_criteria'])if(!c[k]||(Array.isArray(c[k])&&!c[k].length))issues.push({task,case_id:c.id,type:'missing_case_metadata',key:k});
cases.push({task_id:task,id:c.id,title:c.title,audience:c.audience,user_goal:c.user_goal,use_context:c.use_context,content_basis:c.content_basis,visual_intent:c.visual_intent,image_sha256:ih,dsl_sha256:dh});
if(task==='B05')decode.push({task_id:task,case_id:c.id,image_path:image,dsl_path:dsl,dimensions:c.dimensions});
}
}
const views=rows(path.join(root,'tmp',run,'B06','views.jsonl'));
for(const c of selection.cases){const r=json(c.render_meta),m=json(c.metadata),ih=sha(r.image_path),dh=sha(r.dsl_path);if(r.http_status!==200||!r.ok||ih!==r.response_sha256||sha(r.input_file)!==r.body_sha256||dh!==r.body_sha256)issues.push({task:'B06',case_id:c.id,type:'candidate_response_chain'});
if(!views.some(v=>v.id===c.view_id&&v.sha256===ih&&v.tool&&v.viewed_at))issues.push({task:'B06',case_id:c.id,type:'candidate_missing_actual_view',view:c.view_id});
if(hashes.has(ih)||oldHashes.has(ih))issues.push({task:'B06',case_id:c.id,type:'identical_previous_final',previous:hashes.get(ih)||oldHashes.get(ih)});hashes.set(ih,'B06/'+c.id);
for(const k of ['audience','use_context','user_goal','content_basis','visual_intent','completion_criteria'])if(!m[k]||(Array.isArray(m[k])&&!m[k].length))issues.push({task:'B06',case_id:c.id,type:'missing_case_metadata',key:k});
if(!fs.existsSync(c.problem_source))issues.push({task:'B06',case_id:c.id,type:'missing_problem_material'});
cases.push({task_id:'B06',id:c.id,title:m.title,audience:m.audience,user_goal:m.user_goal,use_context:m.use_context,content_basis:m.content_basis,visual_intent:m.visual_intent,image_sha256:ih,dsl_sha256:dh,request_id:r.id,view_id:c.view_id,problem_source:c.problem_source});decode.push({task_id:'B06',case_id:c.id,image_path:r.image_path,dsl_path:r.dsl_path,dimensions:m.dimensions});
}
const journey=json(path.join(root,'outputs',run,'B05','journey.json')),b05spec=json(path.join(root,'tasks','B05-product-from-zero','task.json')),extra=[];
for(const name of b05spec.additional_outputs){const file=path.join(root,'outputs',run,'B05',name);if(!fs.existsSync(file)||!fs.statSync(file).size)issues.push({task:'B05',type:'missing_extra',name});else extra.push({name,path:file,sha256:sha(file)});}
if(journey.screens.length!==10||journey.shared_state.total_paid_cny!==7||journey.arithmetic_checks.progress_fraction!==.45||journey.arithmetic_checks.handoff_gap_minutes!==5||!journey.unpictured_events.some(e=>e.at==='19:25'&&e.event.includes('¥3')))issues.push({task:'B05',type:'journey_content_incomplete'});
const b05Audit=json(path.join(root,'tmp',run,'B05','audit-independent-v001','audit-final-v001.json'));
if(!b05Audit.passed)issues.push({task:'B05',type:'independent_audit_not_passed'});
const result={schema_version:1,run_id:run,reviewer:'/root/b06_cases_02_04_resume',audited_at:new Date().toISOString(),status_scope:'B05 completed and B06 ten selected candidates. All-suite completion not yet claimed.',passed:issues.length===0,issues,creative_cases:cases,creative_case_count:cases.length,unique_creative_image_hash_count:hashes.size,B05_additional_outputs:extra,B05_independent_audit:{path:'B05/audit-independent-v001/audit-final-v001.json',passed:b05Audit.passed,scope:b05Audit.scope},documentary_independence_note:'Read declared goals, audiences, contexts and content for60 cases. Their different use tasks and original metadata support documentary independence. Byte hashes exclude identical copied finals; they do not establish visual originality. Actual perception remains in existing per-image and portfolio review evidence.',new_http_requests:0,new_image_views:0};
fs.writeFileSync(path.join(dir,'incremental-v001.json'),JSON.stringify(result,null,2)+'\n',{flag:'wx'});fs.writeFileSync(path.join(dir,'decode-20-input-v001.json'),JSON.stringify(decode,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({passed:result.passed,issues,cases:cases.length,unique:hashes.size,decode_pending:decode.length,titles:cases.map(c=>({task:c.task_id,id:c.id,title:c.title,goal:c.user_goal}))},null,2));
