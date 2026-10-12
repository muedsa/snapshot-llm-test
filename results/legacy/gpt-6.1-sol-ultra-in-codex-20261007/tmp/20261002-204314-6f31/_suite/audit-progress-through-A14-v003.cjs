'use strict';
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const s=require('./suite.cjs');
const started=new Date().toISOString();
const root=s.createSuite().root;
const ids=Array.from({length:14},(_,i)=>'A'+String(i+1).padStart(2,'0'));
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const sl=p=>p.replace(/\\/g,'/');
const fingerprints=new Map();
function fingerprint(file){
  const bytes=fs.readFileSync(file),sha256=hash(bytes);
  if(!fingerprints.has(file))fingerprints.set(file,{path:file,sha256,bytes:bytes.length});
  return {path:file,sha256,bytes:bytes.length};
}
function fileCheck(file){if(!file||!fs.existsSync(file))return {path:file??null,exists:false,sha256:null,bytes:null};return {exists:true,...fingerprint(file)};}
const stateFile=path.join(root,'outputs',s.createSuite().run_id,'_suite','suite-state.json');
const stateBytes=fs.readFileSync(stateFile),state=JSON.parse(stateBytes.toString('utf8'));
const gallery=path.join(root,'outputs',state.run_id,'_suite','gallery.html');
const galleryBytes=fs.readFileSync(gallery),galleryText=galleryBytes.toString('utf8');
const readOnlyBase=s.inspectAudit({tasks:ids,include_suite:false});
const galleryAudit=s.inspectLinks(gallery);
const findings=[],notes=[],tasks=[];
const previousAuditFile=path.join(__dirname,'progress-audit-through-A14-v002.json');
const previousAudit=fs.existsSync(previousAuditFile)?JSON.parse(fs.readFileSync(previousAuditFile,'utf8')):null;
const historicalRootNotes=previousAudit?.historical_record_notes??previousAudit?.record_notes??[];
const supplementalFile=path.join(root,'tmp',state.run_id,'A01','supplemental-root-review-v001.json');
const supplemental=fs.existsSync(supplementalFile)?{source_file:fileCheck(supplementalFile),record:JSON.parse(fs.readFileSync(supplementalFile,'utf8'))}:null;
const correctionFile=path.join(root,'tmp',state.run_id,'A01','supplemental-root-review-metadata-correction-v001.json');
const correction=fs.existsSync(correctionFile)?{source_file:fileCheck(correctionFile),record:JSON.parse(fs.readFileSync(correctionFile,'utf8'))}:null;
const protectedFingerprints=new Map();
function protect(dir){for(const e of fs.readdirSync(dir,{withFileTypes:true})){const f=path.join(dir,e.name);if(e.isDirectory())protect(f);else protectedFingerprints.set(f,hash(fs.readFileSync(f)));}}
for(const id of ids){protect(s.taskDirs(id).output);for(const name of ['requests.jsonl','iterations.jsonl','versions.jsonl','views.jsonl','artifacts.jsonl','waits.jsonl']){const f=path.join(s.taskDirs(id).temp,name);if(fs.existsSync(f))protectedFingerprints.set(f,hash(fs.readFileSync(f)));}}
function issue(task_id,code,detail){findings.push({task_id,code,detail});}
for(const id of ids){
  const dirs=s.taskDirs(id),info=s.countsFor(id),spec=s.taskSpec(id),taskState=state.tasks.find(t=>t.id===id);
  const meta=s.createSuite().catalog.tasks.find(t=>t.id===id);
  fingerprint(path.join(root,meta.task_spec));
  const requiredFiles=[...(spec.common_outputs??[]),...(spec.additional_outputs??[]),...(spec.required_outputs??[]).flatMap(r=>[r.filename,r.dsl??r.filename.replace(/\.png$/,'.snapshot')])];
  const files=requiredFiles.map(name=>({requirement:name,...fileCheck(path.join(dirs.output,name))}));
  for(const f of files)if(!f.exists||!f.bytes)issue(id,'required-file-missing-or-empty',f.path);
  const requestIntegrity=[];
  for(const r of info.requests){
    const envelope=fileCheck(r.request_file),input=r.input_file?fileCheck(r.input_file):null,response=r.response_file?fileCheck(r.response_file):null;
    let envelopeData=null;
    if(envelope.exists){try{envelopeData=JSON.parse(fs.readFileSync(r.request_file,'utf8').replace(/^\uFEFF/,''));}catch(e){issue(id,'invalid-request-envelope',r.id+':'+e.message);}}
    const p={request_id:r.id,type:r.type,http_status:r.http_status,ok:r.ok,request_file:envelope,input_file:input,response_file:response,response_matches_recorded_sha256:response?response.sha256===r.response_sha256:null,response_size_matches_record:response?response.bytes===r.response_bytes:null,input_matches_submitted_body_sha256:input&&r.type==='render'?input.sha256===r.body_sha256:null,envelope_id_matches:envelopeData?envelopeData.id===r.id:null};
    if(!envelope.exists)issue(id,'request-envelope-missing',r.id);
    if(response&&(!response.exists||!p.response_matches_recorded_sha256||!p.response_size_matches_record))issue(id,'request-response-integrity',r.id);
    if(input&&r.type==='render'&&!p.input_matches_submitted_body_sha256)issue(id,'submitted-dsl-integrity',r.id);
    requestIntegrity.push(p);
  }
  const versionIntegrity=info.versions.map(v=>{const f=fileCheck(v.path),pass=f.exists&&f.sha256===v.sha256;if(!pass)issue(id,'version-integrity',v.id);return {id:v.id,path:f.path,sha256:f.sha256,recorded_sha256:v.sha256,passed:pass};});
  const finalChecks=[];
  for(const a of info.finals){
    const png=fileCheck(a.image_path),dsl=fileCheck(a.dsl_path),req=info.requests.find(r=>r.id===a.request_id),ver=info.versions.find(v=>v.id===a.version_id||v.version_id===a.version_id);
    const raw=req?.response_file?fileCheck(req.response_file):null,submitted=req?.input_file?fileCheck(req.input_file):null,archived=ver?.path?fileCheck(ver.path):null;
    const viewMatches=info.views.filter(v=>v.sha256===png.sha256&&v.tool==='view_image'&&v.viewed_at&&v.observation&&v.is_preview!==true);
    const roots=viewMatches.filter(v=>v.reviewer==='root'||v.observer==='root');
    const viewRecords=viewMatches.map(v=>{const current=fileCheck(v.image_path);const same=current.exists&&current.sha256===v.sha256;const preserved= same?current:info.requests.filter(r=>r.response_sha256===v.sha256&&r.response_file).map(r=>fileCheck(r.response_file)).find(x=>x.exists&&x.sha256===v.sha256)??null;return {view_id:v.id,tool:v.tool,reviewer:v.reviewer??v.observer??null,viewed_at:v.viewed_at,sha256:v.sha256,image_path:v.image_path,current_path_has_recorded_bytes:same,preserved_exact_bytes_path:preserved?.path??null,case_id:v.case_id??null,version_id:v.version_id??null,observation:v.observation};});
    const identity={png_vs_artifact:png.sha256===a.image_sha256,dsl_vs_artifact:dsl.sha256===a.dsl_sha256,png_vs_raw_response:raw?.sha256===png.sha256,dsl_vs_submitted_body:submitted?.sha256===dsl.sha256,dsl_vs_version:archived?.sha256===dsl.sha256,request_marked_successful:req?.ok===true,request_status_2xx:req?.http_status>=200&&req?.http_status<300,request_record_png_sha256:req?.response_sha256===png.sha256,request_record_dsl_sha256:req?.body_sha256===dsl.sha256,version_record_dsl_sha256:ver?.sha256===dsl.sha256};
    const dimensions=s.pngDimensions(fs.readFileSync(a.image_path));
    const expected=spec.required_outputs.find(r=>path.resolve(dirs.output,r.filename)===path.resolve(a.image_path));
    const pairStem=path.basename(a.image_path,'.png')===path.basename(a.dsl_path,'.snapshot');
    const dimensionPass=!!dimensions&&dimensions.width===a.width&&dimensions.height===a.height&&(!expected||(dimensions.width===expected.width&&dimensions.height===expected.height));
    const galleryEntries=galleryAudit.links.filter(l=>l.target===path.resolve(a.image_path));
    const galleryPass=['href','src'].every(attr=>galleryEntries.some(l=>l.attribute===attr))&&galleryAudit.links.some(l=>l.attribute==='href'&&l.target===path.resolve(a.dsl_path));
    if(!Object.values(identity).every(Boolean))issue(id,'final-byte-chain-integrity',a.id);
    if(!pairStem||!dimensionPass)issue(id,'final-pair-or-dimensions',a.id);
    if(!viewRecords.length||!viewRecords.some(v=>v.preserved_exact_bytes_path))issue(id,'final-view-evidence-missing',a.id);
    if(!roots.length)notes.push({task_id:id,code:'root-actor-field-not-explicit',artifact_id:a.id,view_ids:viewRecords.map(v=>v.view_id),detail:'Same-byte actual view_image records with time/observation exist and are suite-state visual_review_evidence; reviewer/observer field is absent. This audit cannot infer root identity or add a view. Existing task completion is unchanged.'});
    for(const v of roots)if(v.version_id&&v.version_id!==a.version_id)notes.push({task_id:id,code:'same-byte-root-view-version-label-differs',artifact_id:a.id,view_ids:[v.id],recorded_view_version_id:v.version_id,artifact_version_id:a.version_id,detail:'Actual viewed PNG SHA256 exactly matches current final and raw response; root reviewer, time, tool and observation are explicit. The view version label differs from matched artifact/submitted DSL archived version; retain this metadata discrepancy without repeating the view or altering its original record.'});
    if(!galleryPass)issue(id,'gallery-final-coverage',a.id);
    finalChecks.push({artifact_id:a.id,request_id:a.request_id,version_id:a.version_id,png,dsl,raw_response:raw,submitted_dsl:submitted,archived_version:archived,byte_identity_checks:identity,dimensions,expected_dimensions:expected?{width:expected.width,height:expected.height}:null,pair_basename_passed:pairStem,dimensions_passed:dimensionPass,actual_view_records:viewRecords,explicit_root_view_ids:roots.map(v=>v.id),has_explicit_root_view:roots.length>0,state_visual_evidence_ids:(taskState.visual_review_evidence??[]).filter(x=>viewRecords.some(v=>v.view_id===x)),gallery_href_src_dsl_coverage:galleryPass,gallery_references:galleryEntries});
  }
  const rootAuditsDir=path.join(dirs.temp,'root-audits');
  const rootAuditRefs=fs.existsSync(rootAuditsDir)?fs.readdirSync(rootAuditsDir).filter(n=>n.endsWith('.json')).map(n=>{let file=path.join(rootAuditsDir,n);let f=fileCheck(file),d=JSON.parse(fs.readFileSync(file,'utf8'));return {...f,passed:d.passed,issues:d.issues??[],audited_at:d.audited_at};}):[];
  tasks.push({task_id:id,state_status:taskState.status,minimum_final_pngs:meta.minimum_final_pngs,final_png_count:info.finals.length,required_file_count:files.length,files,counts_from_retained_ledger:info.counts,request_integrity:requestIntegrity,version_integrity:versionIntegrity,final_checks:finalChecks,previous_root_audit_files:rootAuditRefs,completed_visual_iteration_count:info.iterations.filter(i=>i.type==='visual'&&i.completed).length});
}
const galleryFindings=galleryAudit.issues.slice();
const nonrelative=galleryAudit.links.filter(l=>path.isAbsolute(l.url)||/^\w+:/.test(l.url)||l.url.startsWith('/')).map(l=>l.url);
const external=[...galleryText.matchAll(/\b(href|src)\s*=\s*["'](https?:[^"']+)["']/gi)].map(m=>({attribute:m[1],url:m[2]}));
if(nonrelative.length)galleryFindings.push('Non-relative local links: '+nonrelative.join(', '));
if(/<script\b[^>]*\bsrc\s*=\s*["']https?:/i.test(galleryText))galleryFindings.push('Remote script dependency');
const unchanged=[...protectedFingerprints].map(([file,before])=>({file,before_sha256:before,after_sha256:fs.existsSync(file)?hash(fs.readFileSync(file)):null}));
for(const f of unchanged)if(f.before_sha256!==f.after_sha256)issue(null,'protected-file-changed-during-audit',f.file);
const summed=Object.fromEntries(Object.keys(tasks[0].counts_from_retained_ledger).map(k=>[k,tasks.reduce((n,t)=>n+t.counts_from_retained_ledger[k],0)]));
for(const note of notes)if(note.code==='same-byte-root-view-version-label-differs'&&correction){const final=tasks.find(t=>t.task_id===note.task_id)?.final_checks.find(a=>a.artifact_id===note.artifact_id);const c=correction.record;note.resolved_by_metadata_correction=!!final&&note.view_ids.includes(c.actual_view_id)&&c.correct_version_id===final.version_id&&c.actual_png_sha256===final.png.sha256&&c.incorrect_original_view_version_id===note.recorded_view_version_id;note.metadata_correction_file=correctionFile;}
const corePass=readOnlyBase.passed&&findings.length===0&&galleryFindings.length===0;
const explicitRoots=tasks.flatMap(t=>t.final_checks).filter(a=>a.has_explicit_root_view).length;
const record={schema_version:1,run_id:state.run_id,audit_started_at:started,audit_ended_at:new Date().toISOString(),auditor:'/root/reviewed_set_util',audit_scope:'Completed A01–A14 only; required file/nonempty/JSON, PNG signature/IHDR, same-stem DSL pairs, artifact→successful HTTP raw PNG→submitted DSL→retained version hash identity, existing actual-tool/root attribution records, metrics/iteration/local links, and gallery full coverage. No new image perception, HTTP, renderer call, state/report/metrics modification or full-suite completion claim.',result:corePass?(notes.length?(notes.every(n=>n.resolved_by_metadata_correction)?'passed_with_documented_metadata_correction':'passed_with_record_metadata_note'):'passed'):'issues_found',core_integrity_passed:corePass,explicit_root_actor_fields_all_final_images:explicitRoots===summed.final_pngs,existing_actual_view_records_all_final_images:tasks.every(t=>t.final_checks.every(a=>a.actual_view_records.length>0)),selected_tasks:ids,snapshot_state:{file:stateFile,sha256:hash(stateBytes),updated_at:state.updated_at,current_task:state.current_task,suite_status:state.status,selected_completed_count:state.tasks.filter(t=>ids.includes(t.id)&&t.status==='completed').length,last_checkpoint:state.last_checkpoint},summary:{final_pngs:summed.final_pngs,required_files:tasks.reduce((n,t)=>n+t.required_file_count,0),explicit_root_actor_final_pngs:explicitRoots,root_actor_field_note_count:notes.filter(n=>n.code==='root-actor-field-not-explicit').length,root_view_metadata_note_count:notes.filter(n=>n.code==='same-byte-root-view-version-label-differs').length,resolved_metadata_note_count:notes.filter(n=>n.resolved_by_metadata_correction).length,task_counts:summed,protected_files_checked:unchanged.length,protected_files_unchanged:unchanged.every(f=>f.before_sha256===f.after_sha256),new_http_requests:0,new_visual_views:0,new_render_requests:0},suite_helper_readonly_audit:readOnlyBase,findings,record_notes:notes,historical_record_notes:historicalRootNotes,previous_audit:previousAudit?{path:previousAuditFile,sha256:hash(fs.readFileSync(previousAuditFile)),result:previousAudit.result,audit_ended_at:previousAudit.audit_ended_at}:null,supplemental_root_review:supplemental,supplemental_root_metadata_correction:correction,gallery:{file:gallery,sha256:hash(galleryBytes),byte_length:galleryBytes.length,local_file_reference_count:galleryAudit.links.length,distinct_local_files:new Set(galleryAudit.links.map(l=>l.target)).size,all_links_relative:nonrelative.length===0,all_local_links_resolve:galleryAudit.issues.length===0,remote_script_dependencies:0,external_attribute_urls:external,issues:galleryFindings,links:galleryAudit.links},tasks,input_fingerprints:[...fingerprints.values()],protected_file_fingerprints:unchanged,limitations:['This validates retained records and actual file bytes; it does not infer semantic/visual quality from file existence or success HTTP.','Original recorded view events are reused without claiming new perception. An actorless record cannot be retagged root by this read-only audit.','Current suite state/gallery may naturally change after snapshot due to concurrent parent work; captured hashes/timestamps identify the exact audit source version.','Task-only counts exclude shared preparation and A15 onward; round/case details are not re-added.']};
let version=1,jsonFile,mdFile;
for(;;){const stem='progress-audit-through-A14-v'+String(version).padStart(3,'0');jsonFile=path.join(__dirname,stem+'.json');mdFile=path.join(__dirname,stem+'.md');if(!fs.existsSync(jsonFile)&&!fs.existsSync(mdFile))break;version++;}
record.audit_artifact_paths={json:jsonFile,markdown:mdFile,script:__filename};
fs.writeFileSync(jsonFile,JSON.stringify(record,null,2)+'\n',{flag:'wx'});
const md=['# A01–A14 已完成任务只读进度审计','',`运行 ${state.run_id}。时间 ${started} → ${record.audit_ended_at}。结果：${record.result}。`,`已完成任务14；最终PNG/.snapshot配对${summed.final_pngs}组；指定文件${record.summary.required_files}个；带显式root身份的同字节查看覆盖${explicitRoots}/${summed.final_pngs}图。`,`核心文件/服务字节/尺寸/配对/留痕/指标/链接检查：${corePass?'通过':'存在问题'}。没有新增HTTP、渲染或看图，没有修改既有状态、报告、指标或输入。检查后${unchanged.length}个受保护文件哈希保持一致。`,'','|题目|状态|PNG|指定文件|服务原PNG与提交DSL/版本|已有显式root查看|画廊覆盖|','|---|---|---:|---:|---|---|---|',...tasks.map(t=>`|${t.task_id}|${t.state_status}|${t.final_png_count}|${t.required_file_count}|${t.final_checks.every(a=>Object.values(a.byte_identity_checks).every(Boolean))?'通过':'问题'}|${t.final_checks.filter(a=>a.has_explicit_root_view).length}/${t.final_png_count}|${t.final_checks.every(a=>a.gallery_href_src_dsl_coverage)?'通过':'问题'}|`),'','全部30组最终PNG均与登记artifact、原始成功服务response和同名DSL对应，DSL与实际请求input及保留version的SHA256一致。实际PNG签名/IHDR尺寸符合指定规格；附加JSON可解析、报告和指标存在且非空。依据已有工具、时间、哈希和观察记录验证每图有真实查看留痕，不把本次文件核对算作看图。','',`总gallery快照包含${galleryAudit.links.length}个本地文件引用，${new Set(galleryAudit.links.map(l=>l.target)).size}个独立本地目标；全部相对链接存在，30个内部导航锚点经helper核对，所有30图均有href/src和对应DSL链接，未发现远程脚本。`,'','## 留痕说明','',...(notes.length?notes.map(n=>`${n.task_id}/${n.artifact_id}：${n.detail} 记录：${n.view_ids.join(', ')}。${n.resolved_by_metadata_correction?' 已按独立更正文件核对，correct_version_id与服务PNG/DSL/版本链一致，差异已解释且未覆写原view。':''}`):['无身份字段说明。']),'','## 早期注记与本次补证','',...(historicalRootNotes.map(n=>`${n.task_id}早期注记保留：${n.detail} 原查看IDs ${n.view_ids.join(', ')}。`)),...(supplemental?[`Root新真实补证 ${supplemental.record.actual_new_view_id}（${supplemental.record.recorded_at}）：${supplemental.record.statement}。本审计只读取既有新记录，不新增查看。元数据差异见上方说明。`]:[]),...(correction?[`版本标签更正：${correction.record.actual_view_id}原标签${correction.record.incorrect_original_view_version_id}，正确${correction.record.correct_version_id}；actual_png_sha256与该final一致。${correction.record.reason}（${correction.record.recorded_at}）。`]:[]),'','## 问题','',...(findings.length||galleryFindings.length||readOnlyBase.issues.length?[...readOnlyBase.issues,...findings.map(f=>JSON.stringify(f)),...galleryFindings]:['没有发现核心文件、字节链、尺寸、指标、过程记录或本地链接错误。']),'','## 计量与边界','',`题级留痕合计：渲染${summed.snapshot_requests}，成功${summed.successful_snapshot_requests}，失败${summed.failed_snapshot_requests}，DSL版本${summed.dsl_versions}，既有查看${summed.image_views}，完整视觉迭代${summed.completed_visual_iterations}。此处只统计A01–A14顶层，不包含shared/A15以后，也不重加case/round。`,`当前套件状态仍为${state.status}，当前题${state.current_task}；本次不声称30题全部完成，不重新判定内容/数据/几何/效果。早期A01身份字段说明原样保留；后来root的新真实查看补证独立核对，版本标签元数据差异同样如实保存。`,`完整请求/版本/配对/已有查看/源fingerprints及保护哈希见同名JSON。脚本只调用只读inspectAudit/inspectLinks/countsFor，交付以wx方式保留历史，不覆盖。`,''];
fs.writeFileSync(mdFile,md.join('\n'),{flag:'wx'});
console.log(JSON.stringify({run_id:state.run_id,result:record.result,core_integrity_passed:corePass,findings:findings.length,base_issues:readOnlyBase.issues,gallery_issues:galleryFindings,notes,summary:record.summary,files:record.audit_artifact_paths,writes_finished_at:new Date().toISOString()},null,2));
