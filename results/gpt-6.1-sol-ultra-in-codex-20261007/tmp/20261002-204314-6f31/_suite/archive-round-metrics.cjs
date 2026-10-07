'use strict';
// Import and --help are read-only. No render/view/iteration/state/report methods
// are called. Case inspection is explicitly not a round execution.
const fs = require('node:fs');
const path = require('node:path');
const {createSuite, lines, sha256} = require('./suite.cjs');

const HELP = `Usage:
  node archive-round-metrics.cjs TASK ROUND_ID [--check-only]
    [--start-event EVENT_ID --end-event EVENT_ID]
  node archive-round-metrics.cjs --inspect-case TASK CASE_ID
  node archive-round-metrics.cjs --help

Round mode filters actual task logs by round_id. True start/end must come from
matching recorded round-start/round-started and round-complete/round-completed
events in _suite/events.jsonl; no timestamps or facts are invented.
Without explicit event IDs, each boundary must have exactly one matching event.
--check-only reports metadata and writes nothing. --inspect-case is read-only;
existing cases/pages are never relabelled rounds and boundary times stay null.
Archive writes an immutable temp copy and OUTPUT/TASK/ROUND_ID/task-metrics.json
with wx. Existing destinations are refused; state, reports and task-level metrics
are untouched. Source bytes/hashes and recorded IDs are verified, not perceived.
Round/case detail must never be added again to task/suite top-level totals.
`;
const unknownUsage = {
  input_tokens:null,output_tokens:null,total_tokens:null,image_input_usage:null,
  image_input_unit:null,cost:null,currency:null,billing_scope:null,source:null,
  unknown_fields_reason:'No actual token, image-input or billing consumption is attributable to this scope in the preserved logs. No allocation from task totals or estimate is made.'
};
const isRender = record => ['render','snapshot','open-snapshot'].includes(record.type);
const validTime = value => typeof value === 'string' && Number.isFinite(Date.parse(value));
const canonical = file => {
  const result=path.resolve(file).replace(/\\/g,'/');
  return process.platform==='win32'?result.toLowerCase():result;
};
function safeSegment(value,name) {
  if(typeof value!=='string'||!value||!/^[-A-Za-z0-9_]+$/.test(value)||/^(?:CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])$/i.test(value))throw new Error(name+' must be a safe nonempty directory segment');
  return value;
}
function statMaybe(file) {
  try{return fs.lstatSync(file);}catch(error){if(error.code==='ENOENT')return null;throw error;}
}
function regularBytes(file,name) {
  if(typeof file!=='string'||!fs.existsSync(file)||!fs.statSync(file).isFile())throw new Error(name+' file missing: '+file);
  return fs.readFileSync(file);
}
function within(base,file) {
  const relative=path.relative(path.resolve(base),path.resolve(file));
  return relative===''||(!path.isAbsolute(relative)&&relative!=='..'&&!relative.startsWith('..'+path.sep));
}
function safeDestination(base,file,allowExisting=false) {
  if(!within(base,file)||canonical(base)===canonical(file))throw new Error('Destination escapes archive base: '+file);
  const baseStat=statMaybe(base);
  if(!baseStat||!baseStat.isDirectory()||baseStat.isSymbolicLink()||canonical(fs.realpathSync(base))!==canonical(base))throw new Error('Archive base must be an existing unredirected directory: '+base);
  let cursor=base;
  for(const component of path.relative(base,path.dirname(file)).split(path.sep).filter(Boolean)){
    cursor=path.join(cursor,component);const stat=statMaybe(cursor);
    if(stat&&(stat.isSymbolicLink()||!stat.isDirectory()))throw new Error('Archive parent is not a plain directory: '+cursor);
  }
  if(!allowExisting&&statMaybe(file))throw new Error('wx archive destination already exists: '+file);
}
function pickBoundary(events,task,round,key,id) {
  const types=key==='start'?['round-start','round-started']:['round-complete','round-completed'];
  const candidates=events.filter(event=>event.task_id===task&&event.round_id===round&&types.includes(event.type));
  const selected=id?candidates.find(event=>event.id===id):candidates.length===1?candidates[0]:null;
  if(!selected)throw new Error(id?'Matching '+key+' boundary event not found: '+id:'Need exactly one '+key+' boundary event or explicit --'+key+'-event ID; found '+candidates.length);
  if(!validTime(selected.time))throw new Error('Boundary lacks a real valid event timestamp: '+selected.id);
  return {event_id:selected.id,event_type:selected.type,time:selected.time};
}
function waitTotal(records,kind,unknownWhenAbsent=false) {
  const selected=records.filter(record=>record.kind===kind);
  if(unknownWhenAbsent&&!selected.length)return null;
  if(selected.some(record=>!Number.isFinite(record.seconds)||record.seconds<0))return null;
  return selected.reduce((sum,record)=>sum+record.seconds,0);
}

function collectScope(task,filter,options={}) {
  safeSegment(task,'task');
  const keys=Object.keys(filter??{});
  if(keys.length!==1||!['round_id','case_id'].includes(keys[0]))throw new Error('Scope requires exactly one round_id or case_id filter');
  const key=keys[0],scopeId=safeSegment(filter[key],key),isRound=key==='round_id';
  const s=options.suite??createSuite(),dirs=s.taskDirs(task);
  if(task==='shared')throw new Error('A real task is required');
  const taskState=s.readState().tasks.find(item=>item.id===task);
  if(!taskState)throw new Error('Task missing from run state: '+task);
  const logNames=['requests','versions','views','iterations','waits','artifacts','tool-usage'];
  const raw={},selected={},sourceLogs=[];
  for(const name of logNames){
    const file=path.join(dirs.temp,name+'.jsonl');
    const exists=fs.existsSync(file);
    raw[name]=exists?lines(file):[];
    selected[name]=raw[name].filter(record=>record[key]===scopeId);
    if(selected[name].some(record=>record.task_id!==task))throw new Error('Scope contains a mismatched task_id in '+name);
    sourceLogs.push({name,path:file,exists,bytes:exists?fs.statSync(file).size:0,sha256:exists?sha256(fs.readFileSync(file)):null});
  }
  if(!Object.values(selected).some(records=>records.length))throw new Error('No actual records match '+task+' '+key+'='+scopeId);
  const info=s.countsFor(task,{[key]:scopeId});
  const selectedVersions=new Set(info.versions.map(v=>v.version_id??v.id));
  const tagIssues=[];
  // Never silently infer a round/case from a version. Warn about omitted or
  // conflicting scope tags so the root can append an honest bookkeeping fix.
  for(const name of ['views','iterations','artifacts']){
    for(const record of raw[name])if(selectedVersions.has(record.version_id)&&record[key]!==scopeId)tagIssues.push({log:name,id:record.id,version_id:record.version_id,actual_scope:record[key]??null,expected_scope:scopeId});
  }
  const timestamps=[];
  const timeFields={requests:['started_at','ended_at'],versions:['time'],views:['viewed_at'],iterations:['recorded_at'],waits:['recorded_at'],artifacts:['registered_at'],'tool-usage':['recorded_at']};
  const evidenceChecks={request_hashes:0,version_hashes:0,view_file_hashes:0,final_pair_hashes:0,root_reviewed_finals:0,completed_visual_evidence:0};
  for(const [name,records]of Object.entries(selected)){
    for(const record of records)for(const field of timeFields[name]){
      if(!validTime(record[field]))throw new Error('Invalid/missing actual '+field+' for '+record.id);
      timestamps.push({record_id:record.id,log:name,field,time:record[field]});
    }
  }
  for(const request of info.requests){
    if(Date.parse(request.ended_at)<Date.parse(request.started_at))throw new Error('Request ended before it started: '+request.id);
    if(request.response_file){
      const bytes=regularBytes(request.response_file,'Raw response');
      if(request.response_sha256&&sha256(bytes)!==request.response_sha256)throw new Error('Raw response hash changed: '+request.id);
      if(Number.isFinite(request.response_bytes)&&bytes.length!==request.response_bytes)throw new Error('Raw response length differs: '+request.id);
      evidenceChecks.request_hashes++;
    }
  }
  for(const version of info.versions){
    if(sha256(regularBytes(version.path,'Version'))!==version.sha256)throw new Error('Version hash changed: '+version.id);
    evidenceChecks.version_hashes++;
  }
  const viewSourceResolutions=[];
  for(const view of info.views){
    if(!view.tool)throw new Error('View lacks actual tool: '+view.id);
    let preservedPath=null;
    if(typeof view.image_path==='string'&&fs.existsSync(view.image_path)&&fs.statSync(view.image_path).isFile()&&sha256(fs.readFileSync(view.image_path))===view.sha256)preservedPath=view.image_path;
    // A delivered current pointer may have been superseded after an honest
    // historical view. Retain/count that event if the same original bytes are
    // still preserved in a real raw response; do not invent another viewing.
    if(!preservedPath){
      const original=raw.requests.find(request=>request.response_sha256===view.sha256&&typeof request.response_file==='string'&&fs.existsSync(request.response_file)&&fs.statSync(request.response_file).isFile()&&sha256(fs.readFileSync(request.response_file))===view.sha256);
      preservedPath=original?.response_file??null;
    }
    if(!preservedPath)throw new Error('Viewed bytes have no unchanged preserved source: '+view.id);
    viewSourceResolutions.push({view_id:view.id,recorded_image_path:view.image_path,preserved_source:preservedPath,uses_preserved_raw_response:canonical(preservedPath)!==canonical(view.image_path)});
    evidenceChecks.view_file_hashes++;
  }
  const rootViewIds=[];
  for(const final of info.finals){
    if(sha256(regularBytes(final.image_path,'Final PNG'))!==final.image_sha256||sha256(regularBytes(final.dsl_path,'Final DSL'))!==final.dsl_sha256)throw new Error('Final pair hashes changed: '+final.id);
    const request=info.requests.find(item=>item.id===final.request_id&&item.ok&&item.response_sha256===final.image_sha256);
    const version=info.versions.find(item=>(item.version_id??item.id)===final.version_id&&item.sha256===final.dsl_sha256);
    if(!request||!version||request.body_sha256!==final.dsl_sha256)throw new Error('Final lacks matching scoped request/version: '+final.id);
    const rootView=info.views.find(view=>view.reviewer==='root'&&view.tool==='view_image'&&view.sha256===final.image_sha256);
    if(rootView){evidenceChecks.root_reviewed_finals++;rootViewIds.push(rootView.id);}
    evidenceChecks.final_pair_hashes++;
    if(isRound&&!within(path.join(dirs.output,scopeId),final.image_path))throw new Error('Round final is outside its own archive directory: '+final.image_path);
  }
  for(const iteration of info.iterations.filter(item=>item.type==='visual'&&item.completed)){
    if(!iteration.before_view_id||!iteration.after_view_id||!iteration.changes||!iteration.comparison||![iteration.before_view_id,iteration.after_view_id].every(id=>raw.views.some(view=>view.id===id&&view.tool&&validTime(view.viewed_at))))throw new Error('Completed visual iteration lacks actual before/change/after evidence: '+iteration.version_id);
    // Before-view may honestly belong to a previous round. Do not move it or
    // include it in this round's image-view count.
    evidenceChecks.completed_visual_evidence++;
  }
  const ordered=[...timestamps].sort((a,b)=>Date.parse(a.time)-Date.parse(b.time));
  let boundaries=null,eventLog=null;
  if(isRound){
    eventLog=path.join(s.tempSuite,'events.jsonl');
    const events=lines(eventLog);
    const start=pickBoundary(events,task,scopeId,'start',options.startEventId);
    const end=pickBoundary(events,task,scopeId,'end',options.endEventId);
    boundaries={start,end};
    if(Date.parse(end.time)<Date.parse(start.time))throw new Error('Round end event predates round start');
    const outside=timestamps.filter(item=>Date.parse(item.time)<Date.parse(start.time)||Date.parse(item.time)>Date.parse(end.time));
    if(outside.length)throw new Error('Actual scoped records fall outside chosen boundaries: '+outside.map(item=>item.record_id+'/'+item.field).join(', '));
    const eventBytes=regularBytes(eventLog,'Event ledger');
    sourceLogs.push({name:'suite-events',path:eventLog,exists:true,bytes:eventBytes.length,sha256:sha256(eventBytes)});
  }
  const knownDurations=info.requests.filter(request=>Number.isFinite(request.duration_seconds)&&request.duration_seconds>=0);
  const first=info.finals.map(final=>info.requests.find(request=>request.id===final.request_id&&request.ok)?.ended_at).filter(validTime).sort((a,b)=>Date.parse(a)-Date.parse(b))[0]??null;
  const metric={
    schema_version:1,kind:isRound?'round_detail':'case_readonly_inspection',
    run_id:s.run_id,task_id:task,round_id:isRound?scopeId:null,task_round:isRound?scopeId:null,case_id:isRound?null:scopeId,
    generated_at:new Date().toISOString(),task_status_read_only:taskState.status,
    status:isRound?'recorded_round_evidence':'existing_case_inspected_not_a_round',
    output_dir:isRound?path.join(dirs.output,scopeId):null,temp_dir:dirs.temp,
    filter:{[key]:scopeId},boundaries,
    timings:{
      started_at:boundaries?.start.time??null,ended_at:boundaries?.end.time??null,
      elapsed_seconds:boundaries?(Date.parse(boundaries.end.time)-Date.parse(boundaries.start.time))/1000:null,
      timing_source:boundaries?'Actual matching suite round boundary events':'No case boundary claim; first/last log observation is not case start/end.',
      first_usable_image_seconds:boundaries&&first?(Date.parse(first)-Date.parse(boundaries.start.time))/1000:null,
      first_current_final_response_at:first,
      request_duration_sum_seconds:knownDurations.length===info.requests.length?knownDurations.reduce((sum,request)=>sum+request.duration_seconds,0):null,
      known_request_duration_sum_seconds:knownDurations.reduce((sum,request)=>sum+request.duration_seconds,0),
      request_duration_unknown_count:info.requests.length-knownDurations.length,
      user_feedback_wait_seconds:waitTotal(selected.waits,'user-feedback'),
      rate_limit_wait_seconds:waitTotal(selected.waits,'rate-limit'),
      queue_wait_seconds:waitTotal(selected.waits,'queue',true),
      wait_scope:'Only explicitly matching recorded waits. Absent records do not establish an unmeasured platform/queue gap duration.',
      server_timing_source:info.requests.some(request=>request.server_timing)?'Preserved response Server-Timing headers':null
    },
    observed_log_span:ordered.length?{first:ordered[0],last:ordered.at(-1),seconds:(Date.parse(ordered.at(-1).time)-Date.parse(ordered[0].time))/1000,scope:'Observed log timestamps only; never substituted for true boundary wall clock.'}:null,
    counts:info.counts,resources:info.resources,usage:{...unknownUsage},
    resource_measurement:'Preserved HTTP entity/file and original PNG/DSL bytes. Not wire bytes, token/image-input usage or billing estimates.',
    source_logs:sourceLogs,
    record_ids:{requests:info.requests.map(r=>r.id),versions:info.versions.map(v=>v.version_id??v.id),views:info.views.map(v=>v.id),iterations_history:selected.iterations.map(i=>i.id),iterations_current:info.iterations.map(i=>i.id),waits:selected.waits.map(w=>w.id),artifacts_history:info.artifacts_all.map(a=>a.id),artifacts_current:info.finals.map(a=>a.id),tools:info.tools.map(t=>t.id)},
    records:{requests:info.requests,versions:info.versions,views:info.views,iterations_current:info.iterations,iterations_history:selected.iterations,waits:selected.waits,artifacts_current:info.finals,artifacts_history:info.artifacts_all,tools:info.tools},
    evidence_checks:evidenceChecks,view_preserved_source_resolution:viewSourceResolutions,root_view_ids:rootViewIds,scope_tag_issues:tagIssues,
    aggregation_rule:'Detail only. Task top-level metrics already count the same underlying logs; suite sums task top-level plus shared only. Never add these scope counts again.',
    quality_limit:'Recorded file/hash, scope and time evidence only. No new visual perception, task/round completion, content correctness or future requirements are inferred.',
    changes_state:false,changes_report:false,changes_task_level_metrics:false
  };
  return {s,task,scopeId,isRound,dirs,metric};
}
function metadata(plan) {
  const m=plan.metric;
  return {task_id:m.task_id,run_id:m.run_id,kind:m.kind,round_id:m.round_id,case_id:m.case_id,filter:m.filter,status:m.status,counts:m.counts,timings:m.timings,observed_log_span:m.observed_log_span,evidence_checks:m.evidence_checks,record_ids:m.record_ids,scope_tag_issues:m.scope_tag_issues,aggregation_rule:m.aggregation_rule,changes_state:false,changes_report:false,changes_task_level_metrics:false};
}
function inspectCase(task,caseId,options={}) {return metadata(collectScope(task,{case_id:caseId},options));}
function archiveRound(task,roundId,options={}) {
  const plan=collectScope(task,{round_id:roundId},options);
  const m=plan.metric;
  if(m.scope_tag_issues.length)throw new Error('Related records omit/conflict with round_id; inspect and append honest corrections before archiving: '+JSON.stringify(m.scope_tag_issues));
  if(m.evidence_checks.root_reviewed_finals!==m.counts.final_pngs)throw new Error('Every current round final requires an existing matching root view_image record');
  if(options.checkOnly)return {...metadata(plan),status:'round-preflight-passed',archived:false};
  const output=path.join(plan.dirs.output,roundId,'task-metrics.json');
  const historyDir=path.join(plan.dirs.temp,roundId,'metrics');
  const sequence=fs.existsSync(historyDir)?fs.readdirSync(historyDir).reduce((max,name)=>Math.max(max,Number(/^round-metrics-(\d+)\.json$/.exec(name)?.[1]??0)),0)+1:1;
  const history=path.join(historyDir,'round-metrics-'+String(sequence).padStart(6,'0')+'.json');
  safeDestination(plan.s.outputRoot,output);
  safeDestination(plan.s.tempRoot,history);
  // Recheck whole source ledgers immediately before wx writes. Concurrent root
  // changes are refused rather than combined into an ambiguous archive.
  for(const source of m.source_logs){
    const exists=fs.existsSync(source.path);
    if(exists!==source.exists||(exists&&sha256(fs.readFileSync(source.path))!==source.sha256))throw new Error('Source log changed during collection: '+source.path);
  }
  m.archived_at=new Date().toISOString();
  m.archive={output_metrics:output,temp_history:history,mode:'wx immutable files; no pointer overwrite'};
  const bytes=Buffer.from(JSON.stringify(m,null,2)+'\n');
  const progress={temp_history_written:false,output_metrics_written:false,temp_history:history,output_metrics:output};
  try{
    fs.mkdirSync(historyDir,{recursive:true});fs.writeFileSync(history,bytes,{flag:'wx'});progress.temp_history_written=true;
    fs.mkdirSync(path.dirname(output),{recursive:true});fs.writeFileSync(output,bytes,{flag:'wx'});progress.output_metrics_written=true;
  }catch(error){error.archive_progress=progress;throw error;}
  return {...metadata(plan),status:'round-metrics-archived',archived:true,archive:progress,metrics_sha256:sha256(bytes),metrics_bytes:bytes.length};
}
function main(args) {
  if(args.length===1&&['--help','-h'].includes(args[0])){process.stdout.write(HELP);return;}
  let result;
  if(args[0]==='--inspect-case'){
    if(args.length!==3)throw new Error('Expected --inspect-case TASK CASE_ID');
    result=inspectCase(args[1],args[2]);
  }else{
    const positional=[],options={};
    for(let i=0;i<args.length;i++){
      if(args[i]==='--check-only')options.checkOnly=true;
      else if(['--start-event','--end-event'].includes(args[i])){
        const key=args[i]==='--start-event'?'startEventId':'endEventId';
        if(options[key]||!args[i+1]||args[i+1].startsWith('--'))throw new Error('Boundary event flag requires one ID');
        options[key]=args[++i];
      }else if(args[i].startsWith('--'))throw new Error('Unknown option: '+args[i]);
      else positional.push(args[i]);
    }
    if(positional.length!==2)throw new Error('Expected TASK ROUND_ID; use --help');
    result=archiveRound(positional[0],positional[1],options);
  }
  process.stdout.write(JSON.stringify(result,null,2)+'\n');
}
module.exports={collectScope,inspectCase,archiveRound,metadata,HELP};
if(require.main===module){
  try{main(process.argv.slice(2));}
  catch(error){process.stderr.write(JSON.stringify({status:'round-metrics-error',error:error.message,archive_progress:error.archive_progress??null,changes_state:false,changes_report:false,changes_task_level_metrics:false,note:'No cleanup/rollback. Preserve any partial immutable archive and reconcile actual files before retry.'},null,2)+'\n');process.exitCode=1;}
}
