'use strict';
// Single-writer suite ledger. Importing this module performs no writes.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');

const RUN_ID = '20261002-204314-6f31';
const json = f => JSON.parse(fs.readFileSync(f, 'utf8').replace(/^\uFEFF/, ''));
const now = () => new Date().toISOString();
const sha256 = b => crypto.createHash('sha256').update(b).digest('hex');
const mkdir = d => fs.mkdirSync(d, {recursive: true});
const slash = p => p.replace(/\\/g, '/');
const html = v => String(v ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const unique = a => [...new Set(a)];
function lines(f) {
  if (!fs.existsSync(f)) return [];
  return fs.readFileSync(f, 'utf8').split(/\r?\n/).filter(Boolean).map((line, i) => {
    try { return JSON.parse(line); } catch { throw new Error(`Invalid JSONL at ${f}:${i + 1}`); }
  });
}
function atomicJson(f, obj) {
  mkdir(path.dirname(f));
  const staged = `${f}.write-${crypto.randomUUID()}`;
  fs.writeFileSync(staged, JSON.stringify(obj, null, 2) + '\n', {flag: 'wx'});
  fs.renameSync(staged, f);
}
function immutable(f, data) { mkdir(path.dirname(f)); fs.writeFileSync(f, data, {flag: 'wx'}); return f; }
function append(f, obj) { mkdir(path.dirname(f)); fs.appendFileSync(f, JSON.stringify(obj) + '\n'); return obj; }
function safeName(v) { return String(v).replace(/[^\w.-]/g, '-'); }
const secretKey = /authorization|cookie|api[-_]?key|access[-_]?token|password|secret/i;
function sanitizedUrl(value) {
  const u = new URL(value); u.username = ''; u.password = '';
  for (const k of [...u.searchParams.keys()]) if (secretKey.test(k)) u.searchParams.set(k, '[REDACTED]');
  return u.toString();
}
function sanitizedHeaders(headers) {
  const out = {};
  for (const [k, v] of new Headers(headers ?? {}).entries()) if (!secretKey.test(k)) out[k] = v;
  return out;
}
function redactObject(value) {
  if (Array.isArray(value)) return value.map(redactObject);
  if (value && typeof value === 'object') return Object.fromEntries(Object.entries(value).map(([k,v]) => [k, secretKey.test(k) ? '[REDACTED]' : redactObject(v)]));
  return value;
}
function fileWalk(dir, suffix, out = []) {
  if (!fs.existsSync(dir)) return out;
  for (const e of fs.readdirSync(dir, {withFileTypes: true})) {
    const p = path.join(dir, e.name);
    if (e.isDirectory()) fileWalk(p, suffix, out);
    else if (!suffix || e.name.endsWith(suffix)) out.push(p);
  }
  return out;
}
function pngDimensions(bytes) {
  if (bytes.length >= 24 && bytes.subarray(0,8).equals(Buffer.from([137,80,78,71,13,10,26,10]))) return {width: bytes.readUInt32BE(16), height: bytes.readUInt32BE(20)};
  return null;
}
function latestBy(records, key) {
  const values = new Map(); for (const r of records) values.set(r[key] ?? r.id, r); return [...values.values()];
}

function createSuite(options = {}) {
  const root = path.resolve(options.root ?? path.join(__dirname, '..', '..', '..'));
  const run_id = options.run_id ?? RUN_ID;
  const config = options.config ?? json(path.join(root, 'run-config.json'));
  const catalog = options.catalog ?? json(path.join(root, 'catalog.json'));
  const outputRoot = path.resolve(root, config.output_root, run_id);
  const tempRoot = path.resolve(root, config.temp_root, run_id);
  const outputSuite = path.join(outputRoot, '_suite');
  const tempSuite = path.join(tempRoot, '_suite');
  const statePath = path.join(outputSuite, 'suite-state.json');
  const readState = () => json(statePath);
  const catalogTask = task => catalog.tasks.find(t => t.id === task);
  function taskDirs(task = 'shared') {
    if (task !== 'shared' && !catalogTask(task)) throw new Error(`Unknown task: ${task}`);
    return {output: path.join(outputRoot, task === 'shared' ? '_suite' : task), temp: path.join(tempRoot, task === 'shared' ? '_suite' : task)};
  }
  function nextId(task, kind, file) {
    const prefix = `${task}-${kind}-`;
    let n = 0;
    for (const r of lines(file)) if (r.id?.startsWith(prefix)) n = Math.max(n, Number(r.id.slice(prefix.length)) || 0);
    return prefix + String(n + 1).padStart(6, '0');
  }
  function event(type, data = {}) {
    const f = path.join(tempSuite, 'events.jsonl');
    return append(f, {...data, id: nextId(data.task_id ?? 'shared', 'event', f), time: now(), type, run_id});
  }
  function checkpoint(type = 'checkpoint', data = {}, mutate = null) {
    const state = readState();
    if (mutate) mutate(state);
    state.updated_at = now();
    const dir = path.join(tempSuite, 'checkpoints'); mkdir(dir);
    let n = fs.readdirSync(dir).reduce((m,f) => Math.max(m, Number(/^state-(\d+)\.json$/.exec(f)?.[1] ?? 0)), 0) + 1;
    let target;
    // wx protects the immutable history, including after an interrupted run.
    for (;;) {
      target = path.join(dir, `state-${String(n).padStart(6, '0')}.json`);
      state.last_checkpoint = target;
      try { immutable(target, JSON.stringify(state, null, 2) + '\n'); break; }
      catch (e) { if (e.code !== 'EEXIST') throw e; n++; }
    }
    atomicJson(statePath, state);
    event(type, {...data, checkpoint: target});
    return state;
  }
  function taskStart(task, details = {}) {
    const dirs = taskDirs(task); mkdir(dirs.output); mkdir(dirs.temp);
    for (const f of ['requests.jsonl','iterations.jsonl','views.jsonl','versions.jsonl','waits.jsonl']) if (!fs.existsSync(path.join(dirs.temp,f))) immutable(path.join(dirs.temp,f), '');
    if (task.startsWith('B') && !fs.existsSync(path.join(dirs.temp,'tool-usage.jsonl'))) immutable(path.join(dirs.temp,'tool-usage.jsonl'), '');
    return checkpoint('task-start', {task_id: task, ...details}, state => {
      const t = state.tasks.find(t => t.id === task);
      Object.assign(t, {status: 'in_progress', started_at: t.started_at ?? now(), ended_at: null, output_dir: dirs.output, temp_dir: dirs.temp}, details);
      Object.assign(state, {status: 'in_progress', current_task: task, current_round: details.round_id ?? null, current_case: details.case_id ?? null});
    });
  }
  function taskCheckpoint(task, details = {}) {
    return checkpoint(details.event_type ?? 'task-checkpoint', {task_id: task, ...details}, state => {
      const t = state.tasks.find(t => t.id === task);
      for (const k of ['artifacts','visual_review_evidence','completed_rounds','completed_cases']) if (details[k]) t[k] = unique([...(t[k] ?? []), ...details[k]]);
      for (const k of ['status','resume_notes','unresolved_issues']) if (Object.hasOwn(details,k)) t[k] = details[k];
      state.current_task = task;
      if (Object.hasOwn(details,'round_id')) state.current_round = details.round_id;
      if (Object.hasOwn(details,'case_id')) state.current_case = details.case_id;
    });
  }
  function taskEnd(task, status = 'completed', details = {}) {
    if (!['completed','partial','blocked'].includes(status)) throw new Error('Invalid task end status');
    const state = checkpoint('task-' + status, {task_id: task, ...details}, state => {
      const t = state.tasks.find(t => t.id === task);
      for (const k of ['artifacts','visual_review_evidence','completed_rounds','completed_cases']) if (details[k]) t[k] = unique([...(t[k] ?? []), ...details[k]]);
      Object.assign(t, {status, ended_at: now(), unresolved_issues: details.unresolved_issues ?? t.unresolved_issues ?? [], resume_notes: details.resume_notes ?? t.resume_notes});
      const next = catalog.task_order.find(id => state.tasks.find(t => t.id === id)?.status !== 'completed');
      Object.assign(state, {current_task: next ?? null, current_round: null, current_case: null});
      // An explicit suite audit must run before any suite-completed transition.
    });
    writeTaskMetrics(task, details.metrics ?? {});
    aggregate();
    return state;
  }

  async function request(args) {
    const task = args.task ?? args.task_id ?? 'shared';
    const dirs = taskDirs(task); mkdir(dirs.temp);
    const log = path.join(dirs.temp, 'requests.jsonl');
    let id = nextId(task, 'request', log);
    let requestDir;
    mkdir(path.join(dirs.temp, 'requests'));
    for (;;) {
      requestDir = path.join(dirs.temp, 'requests', id);
      try { fs.mkdirSync(requestDir); break; }
      catch(e) { if(e.code !== 'EEXIST') throw e; id = `${task}-request-${String(Number(id.split('-').at(-1))+1).padStart(6,'0')}`; }
    }
    const started_at = now(); const started = performance.now();
    const method = args.method ?? (args.body === undefined ? 'GET' : 'POST');
    const headers = new Headers(args.headers ?? {});
    let body = args.body;
    if (body && typeof body === 'object' && !Buffer.isBuffer(body) && !(body instanceof Uint8Array) && !(body instanceof ArrayBuffer)) {
      body = JSON.stringify(body); if (!headers.has('content-type')) headers.set('content-type','application/json');
    }
    const request_file = path.join(requestDir, 'request.json');
    const envelope = {id, task_id: task, case_id: args.case_id ?? null, round_id: args.round_id ?? null, type: args.type ?? 'other-service', method, url: sanitizedUrl(args.url), headers: sanitizedHeaders(headers), started_at, timezone:'UTC', body_sha256: body === undefined ? null : sha256(Buffer.from(body)), purpose: args.purpose ?? null};
    immutable(request_file, JSON.stringify(envelope, null, 2) + '\n');
    let input_file = null;
    if (body !== undefined) {
      input_file = path.join(requestDir, args.dsl ? 'input.snapshot' : 'request-body.txt');
      let saved = body;
      if (!args.dsl && headers.get('content-type')?.includes('json')) { try { saved = JSON.stringify(redactObject(JSON.parse(body)), null, 2); } catch {} }
      immutable(input_file, saved);
    }
    let status = null, content_type = null, response_headers = {}, bytes = null, error = null, response_file = null;
    try {
      const response = await (options.fetch ?? globalThis.fetch)(args.url, {method, headers, body, signal: args.signal ?? AbortSignal.timeout(args.timeout_ms ?? 120000), redirect: args.redirect ?? 'follow'});
      status = response.status; content_type = response.headers.get('content-type');
      response_headers = sanitizedHeaders(response.headers);
      // The service entity bytes are kept unchanged; no transcoding/postprocessing.
      bytes = Buffer.from(await response.arrayBuffer());
      const png = pngDimensions(bytes);
      const ext = png ? 'png' : (content_type?.includes('json') ? 'json' : content_type?.startsWith('text/') ? 'txt' : 'bin');
      response_file = immutable(path.join(requestDir, 'response.' + ext), bytes);
      immutable(path.join(requestDir, 'response-headers.json'), JSON.stringify(response_headers, null, 2) + '\n');
      if (!response.ok) error = bytes.toString('utf8').slice(0,2000);
      else if (args.expect_png && !png) error = 'Expected PNG but response does not have a valid PNG signature and IHDR.';
    } catch (e) {
      error = String(e.stack ?? e); immutable(path.join(requestDir, 'network-error.txt'), error);
    }
    const ended_at = now();
    const record = { ...envelope, ended_at, duration_seconds:(performance.now()-started)/1000, http_status:status, content_type, request_file, input_file, response_file, response_bytes:bytes?.length ?? null, response_sha256:bytes ? sha256(bytes) : null, request_id:response_headers['x-request-id'] ?? response_headers['request-id'] ?? null, server_timing:response_headers['server-timing'] ?? null, retry_after:response_headers['retry-after'] ?? null, retry_of:args.retry_of ?? null, error_summary:error, ok:status >= 200 && status < 300 && !error, png_dimensions:bytes ? pngDimensions(bytes) : null };
    append(log, record);
    event('http-request', {task_id:task, request_id:id, type:record.type, http_status:status, ok:record.ok});
    return {...record, bytes, body:bytes, text:() => bytes?.toString('utf8') ?? '', json:() => JSON.parse(bytes.toString('utf8'))};
  }
  function saveVersion(task, dsl, details = {}) {
    const dirs = taskDirs(task); const log = path.join(dirs.temp,'versions.jsonl');
    const id = details.version_id ?? nextId(task,'version',log);
    const file = immutable(path.join(dirs.temp, 'versions', safeName(id) + '.snapshot'), dsl);
    return append(log, {...details, id, version_id:id, task_id:task, time:now(), path:file, sha256:sha256(dsl), parent_version:details.parent_version ?? null, type:details.type ?? 'baseline', case_id:details.case_id ?? null, round_id:details.round_id ?? null});
  }
  function view(task, image_path, details = {}) {
    if (!fs.existsSync(image_path)) throw new Error('Cannot record view for missing image: ' + image_path);
    // Call ONLY after a real view_image/browser visual tool; caller supplies that evidence.
    if (!details.tool) throw new Error('View event requires actual visual tool name');
    const f = path.join(taskDirs(task).temp,'views.jsonl');
    return append(f, {...details, id:nextId(task,'view',f), task_id:task, viewed_at:details.viewed_at ?? now(), timezone:'UTC', image_path:path.resolve(image_path), sha256:sha256(fs.readFileSync(image_path)), observation:details.observation ?? null, case_id:details.case_id ?? null, round_id:details.round_id ?? null});
  }
  function iteration(task, details) {
    if (!['baseline','visual','syntax-fix','retry','alternative','requirement-change'].includes(details.type)) throw new Error('Iteration type is required');
    if (details.type === 'visual' && details.completed && (!details.before_view_id || !details.after_view_id || !details.changes || !details.comparison)) throw new Error('Complete visual iteration needs before/after view IDs, changes, comparison');
    const f = path.join(taskDirs(task).temp,'iterations.jsonl');
    return append(f, {...details, id:nextId(task,'iteration',f), task_id:task, recorded_at:now(), case_id:details.case_id ?? null, round_id:details.round_id ?? null});
  }
  function toolUsage(task, details) {
    const f = path.join(taskDirs(task).temp,'tool-usage.jsonl');
    return append(f, {...details, id:nextId(task,'tool',f), task_id:task, recorded_at:now(), case_id:details.case_id ?? null, round_id:details.round_id ?? null});
  }
  function waitRecord(task, kind, seconds, details = {}) {
    const f = path.join(taskDirs(task).temp,'waits.jsonl');
    return append(f, {...details, id:nextId(task,'wait',f), task_id:task, recorded_at:now(), kind, seconds});
  }
  function artifact(task, image_path, dsl_path, details = {}) {
    if (!fs.existsSync(image_path) || !fs.existsSync(dsl_path)) throw new Error('Missing final image or DSL');
    const dimensions = pngDimensions(fs.readFileSync(image_path));
    if (!dimensions) throw new Error('Final image is not PNG');
    if (path.basename(image_path,'.png') !== path.basename(dsl_path,'.snapshot')) throw new Error('Final PNG and DSL must have same basename');
    const f = path.join(taskDirs(task).temp,'artifacts.jsonl');
    return append(f, {...details, id:nextId(task,'artifact',f), task_id:task, registered_at:now(), image_path:path.resolve(image_path), dsl_path:path.resolve(dsl_path), ...dimensions, image_sha256:sha256(fs.readFileSync(image_path)), dsl_sha256:sha256(fs.readFileSync(dsl_path)), case_id:details.case_id ?? null, round_id:details.round_id ?? null});
  }
  function publish(task, rendered, dsl, relative = 'final', details = {}) {
    if (!rendered.ok || !rendered.png_dimensions) throw new Error('Only successful actual PNG response can be published');
    if (relative.includes('..') || path.isAbsolute(relative)) throw new Error('Publish relative path must stay inside task output');
    const base = path.join(taskDirs(task).output, relative);
    const image = immutable(base + '.png', rendered.bytes); const snapshot = immutable(base + '.snapshot', dsl);
    return artifact(task, image, snapshot, {...details, request_id:rendered.id});
  }
  async function render(task, dsl, details = {}) {
    const version = saveVersion(task, dsl, details);
    iteration(task,{type:details.type??'baseline',version_id:version.id,parent_version:details.parent_version??null,case_id:details.case_id??null,round_id:details.round_id??null,completed:false,phase:'render-started',changes:details.changes??null,before_view_id:details.before_view_id??null});
    const response = await request({task, type:'render', url:config.service_base_url.replace(/\/$/,'')+'/snapshot',method:'POST',body:dsl,dsl:true,headers:{'Content-Type':'text/plain; charset=utf-8',...details.headers},expect_png:true,timeout_ms:details.timeout_ms,case_id:details.case_id,round_id:details.round_id,retry_of:details.retry_of,purpose:details.purpose ?? details.stem ?? version.id});
    const result = {...response, version_id:version.id, dsl_path:version.path, image_path:response.response_file, stem:details.stem??'final', expected_width:details.width??null, expected_height:details.height??null, iteration_type:details.type??'baseline',parent_version:details.parent_version??null};
    if(response.ok&&details.width&&response.png_dimensions.width!==details.width)result.dimension_error=`Width ${response.png_dimensions.width} expected ${details.width}`;
    if(response.ok&&details.height&&response.png_dimensions.height!==details.height)result.dimension_error=`Height ${response.png_dimensions.height} expected ${details.height}`;
    iteration(task,{type:details.type??'baseline',version_id:version.id,parent_version:details.parent_version??null,case_id:details.case_id??null,round_id:details.round_id??null,completed:false,phase:response.ok?'awaiting-actual-image-view':'render-failed',request_id:response.id,image_path:response.response_file,error_summary:response.error_summary,changes:details.changes??null,before_view_id:details.before_view_id??null});
    const {bytes,body,text,json,...serializable}=result;
    result.meta_path=immutable(path.join(path.dirname(response.request_file),'render-result.json'),JSON.stringify(serializable,null,2)+'\n');
    return result;
  }
  function acceptFinal(task, stem, result, details = {}) {
    const rendered=typeof result==='string'?json(result):result;
    if(rendered.dimension_error)throw new Error(rendered.dimension_error);
    if(!rendered.ok||!rendered.png_dimensions)throw new Error('Failed or non-PNG render cannot be accepted');
    const bytes=rendered.bytes??fs.readFileSync(rendered.response_file??rendered.image_path);
    if(!lines(path.join(taskDirs(task).temp,'views.jsonl')).some(v=>v.sha256===sha256(bytes)))throw new Error('Call view()/recordView() after actual tool view before acceptFinal()');
    return publish(task,{...rendered,bytes},fs.readFileSync(rendered.dsl_path,'utf8'),stem??rendered.stem??'final',details);
  }
  function countsFor(task, filter = null) {
    const d = taskDirs(task).temp;
    const select = r => !filter || Object.entries(filter).every(([k,v]) => r[k] === v);
    const requests = lines(path.join(d,'requests.jsonl')).filter(select).map(r=>({...r,http_status:r.http_status??r.status??null,ok:r.ok??((r.http_status??r.status)>=200&&(r.http_status??r.status)<300&&!r.error),request_id:r.request_id??r.requestId??null,error_summary:r.error_summary??r.error??null}));
    const versions = lines(path.join(d,'versions.jsonl')).filter(select);
    const views = lines(path.join(d,'views.jsonl')).filter(select);
    const iterations = latestBy(lines(path.join(d,'iterations.jsonl')).filter(select),'version_id');
    const tools = lines(path.join(d,'tool-usage.jsonl')).filter(select);
    const finals = lines(path.join(d,'artifacts.jsonl')).filter(select);
    const isRender = r => ['render','snapshot','open-snapshot'].includes(r.type);
    const renders = requests.filter(isRender);
    return {counts:{snapshot_requests:renders.length, successful_snapshot_requests:renders.filter(r=>r.ok).length, failed_snapshot_requests:renders.filter(r=>!r.ok).length, retry_requests:requests.filter(r=>r.retry_of).length, other_service_requests:requests.filter(r=>!isRender(r)&&!['document','documentation'].includes(r.type)).length, document_requests:requests.filter(r=>['document','documentation'].includes(r.type)).length, dsl_versions:versions.length, image_views:views.length, completed_visual_iterations:iterations.filter(i=>i.type==='visual'&&i.completed).length, incomplete_visual_iterations:iterations.filter(i=>i.type==='visual'&&!i.completed).length, baseline_versions:iterations.filter(i=>i.type==='baseline').length, syntax_fixes:iterations.filter(i=>i.type==='syntax-fix').length, alternative_versions:iterations.filter(i=>i.type==='alternative').length, requirement_changes:iterations.filter(i=>i.type==='requirement-change').length, other_tool_calls:tools.length, final_pngs:finals.length, independent_creative_cases:unique(finals.filter(f=>f.independent_case!==false&&f.case_id).map(f=>f.case_id)).length}, requests, versions, views, iterations, tools, finals};
  }
  const unknownUsage = {input_tokens:null,output_tokens:null,total_tokens:null,image_input_usage:null,image_input_unit:null,cost:null,currency:null,billing_scope:null,source:null,unknown_fields_reason:'The tools/service did not provide actual model token, image input, or billing consumption for this run.'};
  function writeTaskMetrics(task, extra = {}) {
    const dirs = taskDirs(task); const t = readState().tasks.find(t=>t.id===task);
    const info = countsFor(task); const waits = lines(path.join(dirs.temp,'waits.jsonl'));
    const firstAccepted = info.finals[0];
    const first = firstAccepted ? info.requests.find(r=>r.id===firstAccepted.request_id)?.ended_at ?? firstAccepted.registered_at : null;
    const metric = {schema_version:2,task_id:task,run_id,task_round:null,status:t.status,stop_reason:extra.stop_reason??null,output_dir:dirs.output,temp_dir:dirs.temp,timings:{started_at:t.started_at,ended_at:t.ended_at,elapsed_seconds:t.started_at?((new Date(t.ended_at??now())-new Date(t.started_at))/1000):null,first_usable_image_seconds:first&&t.started_at?((new Date(first)-new Date(t.started_at))/1000):null,user_feedback_wait_seconds:waits.filter(w=>w.kind==='user-feedback').reduce((s,w)=>s+w.seconds,0),rate_limit_wait_seconds:waits.filter(w=>w.kind==='rate-limit').reduce((s,w)=>s+w.seconds,0),queue_wait_seconds:extra.queue_wait_seconds??null,request_duration_sum_seconds:info.requests.reduce((s,r)=>s+(r.duration_seconds??0),0),server_timing_source:info.requests.some(r=>r.server_timing)?'Preserved response Server-Timing headers':null},counts:info.counts,usage:{...unknownUsage,...extra.usage},logs:{requests:path.join(dirs.temp,'requests.jsonl'),iterations:path.join(dirs.temp,'iterations.jsonl'),views:path.join(dirs.temp,'views.jsonl'),versions:path.join(dirs.temp,'versions.jsonl'),tool_usage:task.startsWith('B')?path.join(dirs.temp,'tool-usage.jsonl'):null},outputs:info.finals,candidates:info.versions,rounds:extra.rounds??[],case_metrics:extra.case_metrics??[],final_case_count:info.counts.independent_creative_cases,asset_policy:config.asset_policy_by_track[catalogTask(task).track],unresolved_issues:t.unresolved_issues??[]};
    for(const [k,v] of Object.entries(extra)) if(!['usage','queue_wait_seconds'].includes(k)) metric[k]=v;
    const history=path.join(dirs.temp,'metrics');mkdir(history);immutable(path.join(history,'task-metrics-'+String(fs.readdirSync(history).length+1).padStart(6,'0')+'.json'),JSON.stringify(metric,null,2)+'\n');
    atomicJson(path.join(dirs.output,'task-metrics.json'),metric); return metric;
  }
  function report(task, text) {
    const dirs = taskDirs(task); const f = path.join(dirs.output,'snapshot-usage.md');
    // Current reports are pointers; all prior report content is archived in temp.
    const history = path.join(dirs.temp,'reports'); mkdir(history);
    const n = fs.readdirSync(history).length + 1;
    immutable(path.join(history,`snapshot-usage-${String(n).padStart(6,'0')}.md`),text);
    fs.writeFileSync(f,text); return f;
  }
  function aggregate(options = {}) {
    const state=readState(); const shared=countsFor('shared');
    const metrics=state.tasks.map(t=>{const f=path.join(taskDirs(t.id).output,'task-metrics.json');return fs.existsSync(f)?json(f):null;}).filter(Boolean);
    const names=Object.keys(shared.counts),counts=Object.fromEntries(names.map(k=>[k,(shared.counts[k]??0)+metrics.reduce((s,m)=>s+(m.counts[k]??0),0)]));
    const statusCounts={completed:0,partial:0,blocked:0,pending:0,in_progress:0};for(const t of state.tasks)statusCounts[t.status]=(statusCounts[t.status]??0)+1;
    const overall={schema_version:1,suite_version:catalog.suite_version,run_id,profile:state.profile,status:state.status,stop_reason:options.stop_reason??state.stop_reason??null,started_at:state.started_at,ended_at:state.ended_at??null,elapsed_seconds:(new Date(state.ended_at??now())-new Date(state.started_at))/1000,task_status_counts:statusCounts,counts,shared_preparation:{counts:shared.counts,request_duration_sum_seconds:shared.requests.reduce((s,r)=>s+(r.duration_seconds??0),0),requests_log:path.join(tempSuite,'requests.jsonl')},task_summaries:metrics.map(m=>({task_id:m.task_id,status:m.status,timings:m.timings,counts:m.counts,metric_file:path.join(taskDirs(m.task_id).output,'task-metrics.json')})),usage:{...unknownUsage,...options.usage},aggregation_rule:'Only task-level totals plus shared preparation; never add round/case detail again.',output_dir:outputRoot,temp_dir:tempRoot,unresolved_issues:state.tasks.flatMap(t=>(t.unresolved_issues??[]).map(issue=>({task_id:t.id,issue})))};
    atomicJson(path.join(outputSuite,'task-metrics.json'),overall);
    const rel=f=>slash(path.relative(outputSuite,f));
    const md=['# Snapshot 套件 '+run_id,'',`状态：${state.status}。当前题：${state.current_task??'无'}。`,`更新：${state.updated_at}。最终PNG：${counts.final_pngs}，独立创作用例：${counts.independent_creative_cases}。`,'','[全图画廊](gallery.html) · [使用报告](snapshot-usage.md) · [指标](task-metrics.json) · [进度](suite-state.json)','','|任务|状态|入口 / 轮次与用例|输出路径|临时路径|','|---|---|---|---|---|'];
    const sections=[];
    for(const t of state.tasks){const meta=catalogTask(t.id),d=taskDirs(t.id),finals=countsFor(t.id).finals;md.push(`|${t.id} ${meta.title}|${t.status}|[报告](${rel(path.join(d.output,'snapshot-usage.md'))}) / ${(t.completed_rounds??[]).join(', ')} ${(t.completed_cases??[]).join(', ')}|${slash(d.output)}|${slash(d.temp)}|`);sections.push(`<section id="${t.id}"><h2>${html(t.id+' '+meta.title)} <small>${html(t.status)}</small></h2><div class="grid">${finals.map(a=>`<figure><a href="${html(rel(a.image_path))}" target="_blank"><img loading="lazy" src="${html(rel(a.image_path))}" alt="${html(a.title??a.case_id??a.round_id??t.id)}"></a><figcaption>${html(a.title??a.case_id??a.round_id??path.basename(a.image_path))}<br>${a.width} × ${a.height} · <a href="${html(rel(a.dsl_path))}">完整 DSL</a></figcaption></figure>`).join('')}</div>${finals.length?'':'<p>尚无已登记最终图片。</p>'}</section>`);}
    fs.writeFileSync(path.join(outputSuite,'index.md'),md.join('\n')+'\n');
    fs.writeFileSync(path.join(outputSuite,'gallery.html'),'<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Snapshot '+html(run_id)+'</title><style>body{margin:0;background:#111826;color:#e7edf5;font:16px system-ui,sans-serif}header,main{max-width:1400px;margin:auto;padding:24px}a{color:#83d9eb}nav{display:flex;gap:14px;flex-wrap:wrap}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:20px}figure{margin:0;background:#202b3d;border-radius:12px;overflow:hidden}img{width:100%;max-height:480px;object-fit:contain;background:#fff}figcaption{padding:14px}section{margin:48px 0}small{font-size:14px;color:#aab8cc}</style><header><h1>Snapshot 套件 '+html(run_id)+'</h1><p>状态 '+html(state.status)+' · '+counts.final_pngs+' 张最终图片 · 点击图像打开服务原始尺寸。</p><nav>'+state.tasks.map(t=>`<a href="#${t.id}">${t.id}</a>`).join('')+'</nav></header><main>'+sections.join('')+'</main></html>');
    return overall;
  }
  function audit() {
    const state=readState(),issues=[];
    for(const f of ['index.md','gallery.html','snapshot-usage.md','task-metrics.json','suite-state.json'])if(!fs.existsSync(path.join(outputSuite,f)))issues.push(`_suite: missing ${f}`);
    for(const t of state.tasks){const d=taskDirs(t.id),meta=catalogTask(t.id),info=countsFor(t.id);if(t.status!=='completed')issues.push(`${t.id}: status ${t.status}`);if(info.finals.length<meta.minimum_final_pngs)issues.push(`${t.id}: ${info.finals.length}/${meta.minimum_final_pngs} final PNGs`);if(meta.minimum_independent_cases&&info.counts.independent_creative_cases<meta.minimum_independent_cases)issues.push(`${t.id}: insufficient independent cases`);if(meta.round_count>1&&(t.completed_rounds??[]).length<meta.round_count)issues.push(`${t.id}: missing completed rounds`);for(const f of ['snapshot-usage.md','task-metrics.json'])if(!fs.existsSync(path.join(d.output,f)))issues.push(`${t.id}: missing ${f}`);for(const a of info.finals){if(!fs.existsSync(a.image_path)||!fs.existsSync(a.dsl_path)){issues.push(`${t.id}: missing pair ${a.image_path}`);continue;}const bytes=fs.readFileSync(a.image_path);if(!pngDimensions(bytes))issues.push(`${t.id}: invalid PNG ${a.image_path}`);if(sha256(bytes)!==a.image_sha256)issues.push(`${t.id}: final image bytes changed ${a.image_path}`);if(sha256(fs.readFileSync(a.dsl_path))!==a.dsl_sha256)issues.push(`${t.id}: final DSL bytes changed ${a.dsl_path}`);if(!info.views.some(v=>v.sha256===a.image_sha256))issues.push(`${t.id}: no actual image-view event ${a.image_path}`);if(a.request_id&&!info.requests.some(r=>r.id===a.request_id&&r.ok&&r.response_sha256===a.image_sha256))issues.push(`${t.id}: final image missing matching successful service response ${a.image_path}`);}}
    const result={audited_at:now(),run_id,passed:issues.length===0,issues,scope:'Automated file/count/hash/view-log audit only; content, geometry, data and actual visual judgment require human-agent review.'};
    const dir=path.join(tempSuite,'audits');mkdir(dir);immutable(path.join(dir,'audit-'+String(fs.readdirSync(dir).length+1).padStart(6,'0')+'.json'),JSON.stringify(result,null,2)+'\n');return result;
  }
  function suiteEnd(status, details = {}) {
    if(!['completed','partial','blocked'].includes(status))throw new Error('Invalid suite status');
    if(status==='completed'){const result=audit();if(!result.passed)throw new Error('Suite audit has unresolved issues: '+result.issues.join('; '));if(!details.visual_audit_passed)throw new Error('Explicit completed content/visual suite audit required');}
    const state=checkpoint('suite-'+status,details,s=>Object.assign(s,{status,ended_at:now(),stop_reason:details.stop_reason??null,current_task:status==='completed'?null:s.current_task,current_round:status==='completed'?null:s.current_round,current_case:status==='completed'?null:s.current_case}));aggregate(details);return state;
  }
  return {root,run_id,config,catalog,outputRoot,tempRoot,outputSuite,tempSuite,statePath,readState,taskDirs,event,checkpoint,taskStart,taskCheckpoint,taskEnd,request,render,acceptFinal,saveVersion,view,recordView:view,iteration,logIteration:iteration,toolUsage,waitRecord,artifact,publish,countsFor,writeTaskMetrics,report,aggregate,audit,suiteEnd};
}

module.exports = {createSuite, pngDimensions, sha256, json, lines, immutable};
// Ergonomic default singleton methods, initialized lazily and still read-only on import.
let singleton;
for(const key of ['readState','taskDirs','event','checkpoint','taskStart','taskCheckpoint','taskEnd','request','render','acceptFinal','saveVersion','view','recordView','iteration','logIteration','toolUsage','waitRecord','artifact','publish','countsFor','writeTaskMetrics','report','aggregate','audit','suiteEnd'])module.exports[key]=(...args)=>(singleton??=createSuite())[key](...args);
