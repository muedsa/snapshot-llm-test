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
// Checkpoints deserialize artifact objects, so object reference equality cannot
// identify an already registered artifact. Preserve the first real record while
// deduplicating by either its ledger ID or canonical image path.
function uniqueArtifacts(records) {
  const ids = new Set(), imagePaths = new Set(), anonymous = new Set(), out = [];
  for (const record of records) {
    if (!record || typeof record !== 'object') {
      if (!anonymous.has(record)) { anonymous.add(record); out.push(record); }
      continue;
    }
    const id = record.id ?? null;
    const imagePath = record.image_path ? slash(path.resolve(record.image_path)).toLowerCase() : null;
    if ((id !== null && ids.has(id)) || (imagePath !== null && imagePaths.has(imagePath))) continue;
    if (id === null && imagePath === null && anonymous.has(record)) continue;
    if (id !== null) ids.add(id);
    if (imagePath !== null) imagePaths.add(imagePath);
    if (id === null && imagePath === null) anonymous.add(record);
    out.push(record);
  }
  return out;
}
const relativeUrl = (base, target) => slash(path.relative(base,target)).split('/').map(part=>encodeURIComponent(part)).join('/');
const mdCell = text => String(text??'').replace(/\|/g,'\\|').replace(/\r?\n/g,' ');
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
  function taskSpec(task) {
    const meta=catalogTask(task);
    const f=meta?.task_spec?path.resolve(root,meta.task_spec):meta?.directory?path.resolve(root,meta.directory,'task.json'):null;
    return f&&fs.existsSync(f)?json(f):null;
  }
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
      for (const k of ['artifacts','visual_review_evidence','completed_rounds','completed_cases']) if (details[k]) t[k] = (k === 'artifacts' ? uniqueArtifacts : unique)([...(t[k] ?? []), ...details[k]]);
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
      for (const k of ['artifacts','visual_review_evidence','completed_rounds','completed_cases']) if (details[k]) t[k] = (k === 'artifacts' ? uniqueArtifacts : unique)([...(t[k] ?? []), ...details[k]]);
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
    if(details.type==='visual'&&details.completed){const actualViews=lines(path.join(taskDirs(task).temp,'views.jsonl'));for(const id of [details.before_view_id,details.after_view_id])if(!actualViews.some(v=>v.id===id))throw new Error('Visual iteration refers to missing actual view event: '+id);}
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
    return artifact(task, image, snapshot, {version_id:rendered.version_id??null,case_id:rendered.case_id??null,round_id:rendered.round_id??null,...details, request_id:rendered.id});
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
    const artifacts_all = lines(path.join(d,'artifacts.jsonl')).filter(select);
    const finals = latestBy(artifacts_all,'image_path');
    const isRender = r => ['render','snapshot','open-snapshot'].includes(r.type);
    const renders = requests.filter(isRender);
    const responseSize=r=>Number.isFinite(r.response_bytes)?r.response_bytes:r.response_file&&fs.existsSync(r.response_file)?fs.statSync(r.response_file).size:null;
    const resources={response_entity_bytes:requests.reduce((sum,r)=>sum+(responseSize(r)??0),0),render_response_bytes:renders.reduce((sum,r)=>sum+(responseSize(r)??0),0),document_response_bytes:requests.filter(r=>['document','documentation'].includes(r.type)).reduce((sum,r)=>sum+(responseSize(r)??0),0),other_service_response_bytes:requests.filter(r=>!isRender(r)&&!['document','documentation'].includes(r.type)).reduce((sum,r)=>sum+(responseSize(r)??0),0),response_size_unknown_requests:requests.filter(r=>responseSize(r)===null).length,delivered_final_png_bytes:finals.reduce((sum,a)=>sum+(fs.existsSync(a.image_path)?fs.statSync(a.image_path).size:0),0),archived_dsl_version_bytes:versions.reduce((sum,v)=>sum+(fs.existsSync(v.path)?fs.statSync(v.path).size:0),0)};
    return {counts:{snapshot_requests:renders.length, successful_snapshot_requests:renders.filter(r=>r.ok).length, failed_snapshot_requests:renders.filter(r=>!r.ok).length, retry_requests:requests.filter(r=>r.retry_of).length, other_service_requests:requests.filter(r=>!isRender(r)&&!['document','documentation'].includes(r.type)).length, document_requests:requests.filter(r=>['document','documentation'].includes(r.type)).length, dsl_versions:versions.length, image_views:views.length, completed_visual_iterations:iterations.filter(i=>i.type==='visual'&&i.completed).length, incomplete_visual_iterations:iterations.filter(i=>i.type==='visual'&&!i.completed).length, baseline_versions:iterations.filter(i=>i.type==='baseline').length, syntax_fixes:iterations.filter(i=>i.type==='syntax-fix').length, alternative_versions:iterations.filter(i=>i.type==='alternative').length, requirement_changes:iterations.filter(i=>i.type==='requirement-change').length, other_tool_calls:tools.length, final_pngs:finals.length, independent_creative_cases:unique(finals.filter(f=>f.independent_case!==false&&f.case_id).map(f=>f.case_id)).length}, resources, requests, versions, views, iterations, tools, finals, artifacts_all};
  }
  const unknownUsage = {input_tokens:null,output_tokens:null,total_tokens:null,image_input_usage:null,image_input_unit:null,cost:null,currency:null,billing_scope:null,source:null,unknown_fields_reason:'The tools/service did not provide actual model token, image input, or billing consumption for this run.'};
  function writeTaskMetrics(task, extra = {}) {
    const dirs = taskDirs(task); const t = readState().tasks.find(t=>t.id===task);
    const info = countsFor(task); const waits = lines(path.join(dirs.temp,'waits.jsonl'));
    // Same-path supersession keeps the Map insertion order, not request time.
    // Use only known completion timestamps from successful current-final requests;
    // an unknown request time stays unknown rather than using registration time.
    const first = info.finals.map(a=>info.requests.find(r=>r.id===a.request_id&&r.ok)?.ended_at)
      .filter(time=>typeof time==='string'&&Number.isFinite(Date.parse(time)))
      .sort((a,b)=>Date.parse(a)-Date.parse(b))[0] ?? null;
    const priorPath=path.join(dirs.output,'task-metrics.json'),prior=fs.existsSync(priorPath)?json(priorPath):{};
    const metric = {...prior,schema_version:2,task_id:task,run_id,task_round:null,status:t.status,stop_reason:extra.stop_reason??prior.stop_reason??null,output_dir:dirs.output,temp_dir:dirs.temp,timings:{started_at:t.started_at,ended_at:t.ended_at,elapsed_seconds:t.started_at?((new Date(t.ended_at??now())-new Date(t.started_at))/1000):null,first_usable_image_seconds:first&&t.started_at?((new Date(first)-new Date(t.started_at))/1000):null,user_feedback_wait_seconds:waits.filter(w=>w.kind==='user-feedback').reduce((s,w)=>s+w.seconds,0),rate_limit_wait_seconds:waits.filter(w=>w.kind==='rate-limit').reduce((s,w)=>s+w.seconds,0),queue_wait_seconds:extra.queue_wait_seconds??prior.timings?.queue_wait_seconds??null,request_duration_sum_seconds:info.requests.reduce((s,r)=>s+(r.duration_seconds??0),0),server_timing_source:info.requests.some(r=>r.server_timing)?'Preserved response Server-Timing headers':null},counts:info.counts,usage:{...unknownUsage,...prior.usage,...extra.usage},logs:{requests:path.join(dirs.temp,'requests.jsonl'),iterations:path.join(dirs.temp,'iterations.jsonl'),views:path.join(dirs.temp,'views.jsonl'),versions:path.join(dirs.temp,'versions.jsonl'),tool_usage:task.startsWith('B')?path.join(dirs.temp,'tool-usage.jsonl'):null},outputs:info.finals,candidates:info.versions,rounds:extra.rounds??prior.rounds??[],case_metrics:extra.case_metrics??prior.case_metrics??[],final_case_count:info.counts.independent_creative_cases,asset_policy:config.asset_policy_by_track[catalogTask(task).track],unresolved_issues:t.unresolved_issues??[]};
    for(const [k,v] of Object.entries(extra)) if(!['usage','queue_wait_seconds','counts','outputs','candidates','logs','timings','task_id','run_id','status','output_dir','temp_dir'].includes(k)) metric[k]=v;
    metric.resources=info.resources;metric.resource_measurement='Preserved HTTP response entity/file bytes and delivered original PNG bytes, measured from real files. These are not network-wire byte, token, image-input or cost estimates.';
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
    const resources=Object.fromEntries(Object.keys(shared.resources).map(k=>[k,shared.resources[k]+metrics.reduce((sum,m)=>sum+((m.resources??countsFor(m.task_id).resources)[k]??0),0)]));
    const statusCounts={completed:0,partial:0,blocked:0,pending:0,in_progress:0};for(const t of state.tasks)statusCounts[t.status]=(statusCounts[t.status]??0)+1;
    const overall={schema_version:1,suite_version:catalog.suite_version,run_id,profile:state.profile,status:state.status,stop_reason:options.stop_reason??state.stop_reason??null,started_at:state.started_at,ended_at:state.ended_at??null,elapsed_seconds:(new Date(state.ended_at??now())-new Date(state.started_at))/1000,task_status_counts:statusCounts,counts,shared_preparation:{counts:shared.counts,request_duration_sum_seconds:shared.requests.reduce((s,r)=>s+(r.duration_seconds??0),0),requests_log:path.join(tempSuite,'requests.jsonl')},task_summaries:metrics.map(m=>({task_id:m.task_id,status:m.status,timings:m.timings,counts:m.counts,metric_file:path.join(taskDirs(m.task_id).output,'task-metrics.json')})),usage:{...unknownUsage,...options.usage},aggregation_rule:'Only task-level totals plus shared preparation; never add round/case detail again.',output_dir:outputRoot,temp_dir:tempRoot,unresolved_issues:state.tasks.flatMap(t=>(t.unresolved_issues??[]).map(issue=>({task_id:t.id,issue})))};
    overall.resources=resources;overall.resource_measurement='Preserved response entity bytes measured from actual raw response files, delivered original final PNG bytes and archived DSL version bytes. Unknown response sizes are counted separately. Values are not billing/token/network-wire proxies.';overall.timings={total_wall_seconds:overall.elapsed_seconds,request_duration_sum_seconds:shared.requests.reduce((sum,r)=>sum+(r.duration_seconds??0),0)+metrics.reduce((sum,m)=>sum+(m.timings?.request_duration_sum_seconds??0),0),shared_request_duration_seconds:shared.requests.reduce((sum,r)=>sum+(r.duration_seconds??0),0),scope:'Shared preparation plus task-level totals only; case/round details are not summed again.'};overall.shared_preparation.resources=shared.resources;
    const history=path.join(tempSuite,'aggregate-history');mkdir(history);const sequence=String(fs.readdirSync(history).filter(f=>f.endsWith('.json')).length+1).padStart(6,'0');immutable(path.join(history,'task-metrics-'+sequence+'.json'),JSON.stringify(overall,null,2)+'\n');
    atomicJson(path.join(outputSuite,'task-metrics.json'),overall);
    const rel=f=>relativeUrl(outputSuite,f);
    const reportPointer=fs.existsSync(path.join(outputSuite,'snapshot-usage.md'))?'[使用报告](snapshot-usage.md)':'使用报告尚未生成';
    const md=['# Snapshot 套件 '+run_id,'',`状态：${state.status}。当前题：${state.current_task??'无'}。`,`更新：${state.updated_at}。最终PNG：${counts.final_pngs}，独立创作用例：${counts.independent_creative_cases}。`,'',`[全图画廊](gallery.html) · ${reportPointer} · [指标](task-metrics.json) · [进度](suite-state.json)`,'','|任务|状态|入口 / 轮次与用例|输出路径|临时路径|','|---|---|---|---|---|'];
    const sections=[];
    for(const t of state.tasks){const meta=catalogTask(t.id),d=taskDirs(t.id),finals=countsFor(t.id).finals;const report=path.join(d.output,'snapshot-usage.md'),entry=fs.existsSync(report)?`[报告](${rel(report)})`:'报告尚未生成';const roundEntries=(t.completed_rounds??[]).map(round=>{const f=path.join(d.output,round,'snapshot-usage.md');return fs.existsSync(f)?`[${round}](${rel(f)})`:round;});md.push(`|${mdCell(t.id+' '+meta.title)}|${t.status}|${entry}${roundEntries.length?' / '+roundEntries.join(', '):''} ${(t.completed_cases??[]).join(', ')}|${mdCell(slash(d.output))}|${mdCell(slash(d.temp))}|`);sections.push(`<section id="${t.id}"><h2>${html(t.id+' '+meta.title)} <small>${html(t.status)}</small></h2><div class="grid">${finals.map(a=>{const label=[a.round_id,a.case_id,a.title??path.basename(a.image_path)].filter(Boolean).join(' / ');return `<figure><a href="${html(rel(a.image_path))}" target="_blank"><img loading="lazy" src="${html(rel(a.image_path))}" alt="${html(label)}"></a><figcaption>${html(label)}<br>${a.width} × ${a.height} · <a href="${html(rel(a.dsl_path))}">完整 DSL</a></figcaption></figure>`;}).join('')}</div>${finals.length?'':'<p>尚无已登记最终图片。</p>'}</section>`);}
    const index=md.join('\n')+'\n';immutable(path.join(history,'index-'+sequence+'.md'),index);fs.writeFileSync(path.join(outputSuite,'index.md'),index);
    const gallery='<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Snapshot '+html(run_id)+'</title><style>body{margin:0;background:#111826;color:#e7edf5;font:16px system-ui,sans-serif}header,main{max-width:1400px;margin:auto;padding:24px}a{color:#83d9eb}nav{display:flex;gap:14px;flex-wrap:wrap}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:20px}figure{margin:0;background:#202b3d;border-radius:12px;overflow:hidden}img{width:100%;max-height:480px;object-fit:contain;background:#fff}figcaption{padding:14px}section{margin:48px 0}small{font-size:14px;color:#aab8cc}</style><header><h1>Snapshot 套件 '+html(run_id)+'</h1><p>状态 '+html(state.status)+' · '+counts.final_pngs+' 张最终图片 · 点击图像打开服务原始尺寸。</p><nav>'+state.tasks.map(t=>`<a href="#${t.id}">${t.id}</a>`).join('')+'</nav></header><main>'+sections.join('')+'</main></html>';
    immutable(path.join(history,'gallery-'+sequence+'.html'),gallery);fs.writeFileSync(path.join(outputSuite,'gallery.html'),gallery);
    return overall;
  }
  function inspectLinks(file) {
    if(!fs.existsSync(file))return {file,links:[],issues:['Missing link source '+file]};
    const content=fs.readFileSync(file,'utf8'),isHtml=file.endsWith('.html');
    const values=isHtml?[...content.matchAll(/\b(href|src)\s*=\s*["']([^"']+)["']/gi)].map(m=>({raw:m[2],attribute:m[1].toLowerCase()})):[...content.matchAll(/!?\[[^\]]*\]\(([^\s)]+)(?:\s+["'][^"']*["'])?\)/g)].map(m=>({raw:m[1],attribute:'markdown'}));
    const ids=isHtml?new Set([...content.matchAll(/\bid\s*=\s*["']([^"']+)["']/gi)].map(m=>m[1])):null;
    const issues=[],links=[];
    for(const value of values){let raw=value.raw.replace(/&amp;/g,'&').replace(/&quot;/g,'"').replace(/&#39;/g,"'");if(/^(?:https?:|mailto:|data:|codex:|app:)/i.test(raw))continue;if(raw.startsWith('#')){if(isHtml&&!ids.has(decodeURIComponent(raw.slice(1))))issues.push(`${file}: missing anchor ${raw}`);continue;}let target;try{target=path.resolve(path.dirname(file),decodeURIComponent(raw.split('#')[0].split('?')[0]));}catch{issues.push(`${file}: invalid encoded link ${raw}`);continue;}links.push({url:raw,target,attribute:value.attribute});if(!fs.existsSync(target))issues.push(`${file}: broken local link ${raw}`);}
    if(isHtml&&/<script\b[^>]*\bsrc\s*=\s*["']https?:/i.test(content))issues.push(`${file}: gallery has remote script dependency`);
    return {file,links,issues};
  }
  function inspectAudit(auditOptions = {}) {
    const state=readState(),issues=[],checks=[];
    const includeSuite=auditOptions.include_suite??!auditOptions.tasks;
    const chosen=new Set(auditOptions.tasks??state.tasks.map(t=>t.id));
    const suiteGallery=includeSuite&&fs.existsSync(path.join(outputSuite,'gallery.html'))?inspectLinks(path.join(outputSuite,'gallery.html')):null;
    const localIssues=[];
    function requireFile(task,name,base){const file=path.resolve(base,name);if(!file.startsWith(path.resolve(base)+path.sep)&&file!==path.resolve(base)){issues.push(`${task}: requirement path escapes output: ${name}`);return null;}if(!fs.existsSync(file)){issues.push(`${task}: missing ${slash(path.relative(taskDirs(task).output,file))}`);return null;}const bytes=fs.readFileSync(file);if(bytes.length===0)issues.push(`${task}: empty file ${name}`);if(file.endsWith('.json')){try{JSON.parse(bytes.toString('utf8').replace(/^\uFEFF/,''));}catch(e){issues.push(`${task}: invalid JSON ${name}: ${e.message}`);}}return file;}
    if(includeSuite){for(const f of ['index.md','gallery.html','snapshot-usage.md','task-metrics.json','suite-state.json'])if(!fs.existsSync(path.join(outputSuite,f)))issues.push(`_suite: missing ${f}`);for(const f of ['index.md','gallery.html','snapshot-usage.md'])if(fs.existsSync(path.join(outputSuite,f)))localIssues.push(...inspectLinks(path.join(outputSuite,f)).issues);}
    for(const t of state.tasks.filter(t=>chosen.has(t.id))){
      const d=taskDirs(t.id),meta=catalogTask(t.id),info=countsFor(t.id),spec=taskSpec(t.id);
      const taskIssueStart=issues.length;
      if(t.status!=='completed'&&!auditOptions.allow_incomplete)issues.push(`${t.id}: status ${t.status}`);
      if(info.finals.length<(meta.minimum_final_pngs??0))issues.push(`${t.id}: ${info.finals.length}/${meta.minimum_final_pngs} final PNGs`);
      if(meta.minimum_independent_cases&&info.counts.independent_creative_cases<meta.minimum_independent_cases)issues.push(`${t.id}: ${info.counts.independent_creative_cases}/${meta.minimum_independent_cases} independent cases`);
      if(meta.round_count>1&&(t.completed_rounds??[]).length<meta.round_count)issues.push(`${t.id}: missing completed rounds`);
      const roundSidecars=new Set((spec?.rounds??[]).flatMap(r=>r.additional_outputs??[]));
      for(const f of spec?.common_outputs??['snapshot-usage.md','task-metrics.json'])requireFile(t.id,f,d.output);
      for(const f of spec?.additional_outputs??[])if(!roundSidecars.has(f)||fs.existsSync(path.join(d.output,f)))requireFile(t.id,f,d.output);
      for(const r of spec?.rounds??[]){const round=r.output_subdirectory??'round-'+String(r.round).padStart(2,'0');for(const f of [...(r.additional_outputs??[]),...(r.common_outputs??[])])requireFile(t.id,f,path.join(d.output,round));}
      for(const r of spec?.required_outputs??[]){const image=requireFile(t.id,r.filename,d.output),snapshot=requireFile(t.id,r.dsl??r.filename.replace(/\.png$/,'.snapshot'),d.output);if(image){const actual=pngDimensions(fs.readFileSync(image));if(!actual)issues.push(`${t.id}: required file is not PNG ${r.filename}`);else if((r.width&&actual.width!==r.width)||(r.height&&actual.height!==r.height))issues.push(`${t.id}: ${r.filename} is ${actual.width}x${actual.height}, expected ${r.width}x${r.height}`);if(!info.finals.some(a=>path.resolve(a.image_path)===image))issues.push(`${t.id}: required PNG lacks registered final evidence ${r.filename}`);}if(snapshot&&!snapshot.endsWith('.snapshot'))issues.push(`${t.id}: DSL extension invalid ${snapshot}`);}
      for(const f of spec?.log_files??['requests.jsonl','iterations.jsonl'])if(!fs.existsSync(path.join(d.temp,f)))issues.push(`${t.id}: missing process log ${f}`);
      for(const a of info.finals){
        if(!fs.existsSync(a.image_path)||!fs.existsSync(a.dsl_path)){issues.push(`${t.id}: missing pair ${a.image_path}`);continue;}
        const bytes=fs.readFileSync(a.image_path),dimensions=pngDimensions(bytes),dsl=fs.readFileSync(a.dsl_path);
        if(!dimensions)issues.push(`${t.id}: invalid PNG ${a.image_path}`);
        else if(dimensions.width!==a.width||dimensions.height!==a.height)issues.push(`${t.id}: logged dimensions differ from actual PNG ${a.image_path}`);
        if(path.basename(a.image_path,'.png')!==path.basename(a.dsl_path,'.snapshot'))issues.push(`${t.id}: PNG/DSL names differ ${a.image_path}`);
        if(suiteGallery){for(const attribute of ['href','src'])if(!suiteGallery.links.some(l=>l.attribute===attribute&&l.target===path.resolve(a.image_path)))issues.push(`${t.id}: suite gallery lacks ${attribute} for ${a.image_path}`);}
        if(sha256(bytes)!==a.image_sha256)issues.push(`${t.id}: final image bytes changed ${a.image_path}`);
        if(sha256(dsl)!==a.dsl_sha256)issues.push(`${t.id}: final DSL bytes changed ${a.dsl_path}`);
        if(!info.views.some(v=>v.sha256===a.image_sha256&&v.tool&&v.viewed_at))issues.push(`${t.id}: no actual-tool image-view record ${a.image_path}`);
        const matched=info.requests.find(r=>r.id===a.request_id&&r.ok&&r.response_sha256===a.image_sha256);
        if(!matched)issues.push(`${t.id}: no matching successful service response ${a.image_path}`);
        else {if(matched.body_sha256&&matched.body_sha256!==a.dsl_sha256)issues.push(`${t.id}: final DSL differs from submitted body ${a.dsl_path}`);if(!matched.response_file||!fs.existsSync(matched.response_file))issues.push(`${t.id}: missing preserved raw response ${a.request_id}`);else if(sha256(fs.readFileSync(matched.response_file))!==a.image_sha256)issues.push(`${t.id}: final PNG differs from raw response ${a.request_id}`);}
        if(spec?.case_artifacts&&a.case_id)for(const name of spec.case_artifacts)requireFile(t.id,name,path.join(d.output,a.case_id));
      }
      for(const i of info.iterations.filter(i=>i.type==='visual'&&i.completed)){if(!i.before_view_id||!i.after_view_id||!i.changes||!i.comparison||![i.before_view_id,i.after_view_id].every(id=>info.views.some(v=>v.id===id)))issues.push(`${t.id}: visual iteration ${i.version_id} lacks full before/change/after evidence`);}
      const metricFile=path.join(d.output,'task-metrics.json');if(fs.existsSync(metricFile)){try{const metric=json(metricFile);for(const [k,v] of Object.entries(info.counts))if(metric.counts?.[k]!==v)issues.push(`${t.id}: metric ${k}=${metric.counts?.[k]} differs from actual ledger ${v}`);if(metric.status!==t.status)issues.push(`${t.id}: metric status differs from state`);if(Math.abs((metric.timings?.request_duration_sum_seconds??0)-info.requests.reduce((n,r)=>n+(r.duration_seconds??0),0))>0.001)issues.push(`${t.id}: request duration sum differs from ledger`);}catch(e){issues.push(`${t.id}: metrics cannot be audited: ${e.message}`);}}
      if(t.id.startsWith('B')){const portfolio=path.join(d.output,'portfolio.json');if(fs.existsSync(portfolio)){try{const p=json(portfolio);const cases=p.cases??[];if(unique(cases.map(c=>c.id)).length!==cases.length)issues.push(`${t.id}: portfolio has duplicate case IDs`);for(const caseId of unique(info.finals.filter(a=>a.independent_case!==false).map(a=>a.case_id).filter(Boolean)))if(!cases.some(c=>c.id===caseId))issues.push(`${t.id}: portfolio missing ${caseId}`);}catch(e){issues.push(`${t.id}: invalid portfolio: ${e.message}`);}}}
      for(const f of fileWalk(d.output).filter(f=>/\.(?:md|html)$/.test(f)))localIssues.push(...inspectLinks(f).issues);
      const actualPNGs=fileWalk(d.output,'.png');for(const image of actualPNGs)if(!info.finals.some(a=>path.resolve(a.image_path)===image))issues.push(`${t.id}: unregistered output PNG ${slash(path.relative(d.output,image))}`);
      checks.push({task_id:t.id,status:t.status,required_final_pngs:meta.minimum_final_pngs,actual_final_pngs:info.finals.length,independent_cases:info.counts.independent_creative_cases,issue_count:issues.length-taskIssueStart});
    }
    issues.push(...localIssues);
    return {audited_at:now(),run_id,passed:issues.length===0,issues,task_checks:checks,link_issues:localIssues,selected_tasks:[...chosen],scope:'Automated file, required-output/dimension, byte-identity, recorded-view, count, metrics and local-link verification only. No visual perception, content/data/geometry/effect evaluation or creative independence judgment is inferred from these file checks. The root must perform the real full-image and suite visual audit.'};
  }
  function audit(auditOptions = {}) {
    const result=inspectAudit(auditOptions),dir=path.join(tempSuite,'audits');mkdir(dir);immutable(path.join(dir,'audit-'+String(fs.readdirSync(dir).length+1).padStart(6,'0')+'.json'),JSON.stringify(result,null,2)+'\n');return result;
  }
  function writeSuiteReport(extra = {}) {
    const state=readState(),shared=countsFor('shared'),taskInfos=state.tasks.map(t=>({state:t,info:countsFor(t.id)}));
    const requestMap=new Map([...shared.requests,...taskInfos.flatMap(t=>t.info.requests)].map(r=>[r.id,r]));
    const applicationFiles=fs.existsSync(tempSuite)?fs.readdirSync(tempSuite).filter(f=>/^shared-applications-\d+\.json$/.test(f)).map(f=>path.join(tempSuite,f)):[];
    const applications=applicationFiles.map(file=>({file,record:json(file)}));
    const totals=Object.fromEntries(Object.keys(shared.counts).map(k=>[k,(shared.counts[k]??0)+taskInfos.reduce((sum,t)=>sum+(t.info.counts[k]??0),0)]));
    const statuses={pending:0,in_progress:0,completed:0,partial:0,blocked:0};for(const t of state.tasks)statuses[t.status]=(statuses[t.status]??0)+1;
    const link=(label,file)=>fs.existsSync(file)?`[${label}](${relativeUrl(outputSuite,file)})`:`${label}（文件尚未生成）`;
    const text=['# Snapshot 全套实际使用报告','',`运行：${run_id}；生成时间：${now()}；配置：${state.profile}；状态：${state.status}。`,`当前题：${state.current_task??'无'}；轮次：${state.current_round??'无'}；用例：${state.current_case??'无'}。`,`实际输出目录：${slash(outputRoot)}。实际临时目录：${slash(tempRoot)}。`,'',`状态数量：completed ${statuses.completed}，in_progress ${statuses.in_progress}，partial ${statuses.partial}，blocked ${statuses.blocked}，pending ${statuses.pending}。`,`已登记最终 PNG ${totals.final_pngs}；独立创作用例 ${totals.independent_creative_cases}；实际渲染请求 ${totals.snapshot_requests}（成功 ${totals.successful_snapshot_requests}，失败 ${totals.failed_snapshot_requests}）；文档请求 ${totals.document_requests}；其他服务请求 ${totals.other_service_requests}；完整视觉迭代 ${totals.completed_visual_iterations}；未完成视觉迭代 ${totals.incomplete_visual_iterations}；实际查看记录 ${totals.image_views}。`,'','## 真实文档与 DSL 应用','','下面的实际阅读/应用来自执行者保存的 shared-applications 记录；单纯取得文档响应不被当作已经阅读或应用。相同缓存跨题复用不新增 HTTP 请求。'];
    if(applications.length===0)text.push('尚无共享应用声明记录；已下载文档只能作为缓存证据列出。');
    for(const app of applications){text.push('',`${link(app.record.id??path.basename(app.file),app.file)}：${app.record.scope??'共享应用记录'}。`);for(const doc of app.record.read_documents??[]){const req=requestMap.get(doc.request_id);text.push(`- ${doc.request_id}：${doc.url}。${doc.application??''}${req?.ok?' 对应实际成功请求已保留。':' 对应成功请求尚未核对到，不能据此确认访问成功。'}`);}if(app.record.fonts_request){const fonts=app.record.fonts_request;const req=requestMap.get(fonts.request_id);text.push(`- 字体 ${fonts.request_id}：${(fonts.selected_actual_families??[]).join(', ')}；实际请求核验 ${req?.ok?'成功':'未确认'}。`);}}
    for(const doc of extra.documentation_applications??[])text.push(`- ${doc.request_id??'执行者补充记录'}：${doc.url??''} ${doc.application??''}`);
    text.push('','## 缓存与真实请求证据','','|范围|请求 ID|类型|HTTP|原始响应|','|---|---|---|---|---|');
    for(const req of shared.requests)text.push(`|shared|${req.id}|${req.type}|${req.http_status??'未知'}|${req.response_file?link('原始响应',req.response_file):'未取得'}|`);
    text.push('','## 实际工具与方法','');
    const declaredTools=unique(applications.flatMap(a=>a.record.tools_applied??[]));for(const name of declaredTools)text.push('- '+name+'。');
    const toolRecords=taskInfos.flatMap(t=>t.info.tools.map(tool=>({task_id:t.state.id,...tool})));for(const tool of toolRecords)text.push(`- ${tool.task_id}/${tool.case_id??'shared'}：${tool.tool??tool.name??'记录中的工具'}；${tool.purpose??''}；证据 ID ${tool.id}。`);
    if(!declaredTools.length&&!toolRecords.length)text.push('尚无实际辅助工具应用记录。');
    text.push('','所有最终图片保留原服务 PNG 字节并与完整同名 .snapshot 配对；本报告生成器读取留痕，不代替执行者的实际图像查看。','', '## 逐题状态与产物','', '|任务|状态|最终图/独立用例|渲染成功/失败|DSL/看图|完整/未完视觉迭代|入口|','|---|---|---|---|---|---|---|');
    for(const row of taskInfos){const c=row.info.counts,d=taskDirs(row.state.id);text.push(`|${row.state.id}|${row.state.status}|${c.final_pngs}/${c.independent_creative_cases}|${c.successful_snapshot_requests}/${c.failed_snapshot_requests}|${c.dsl_versions}/${c.image_views}|${c.completed_visual_iterations}/${c.incomplete_visual_iterations}|${link('单题报告',path.join(d.output,'snapshot-usage.md'))}|`);}
    text.push('','## 可观察问题、修复与验证','');
    const lessons=[...applications.flatMap(a=>(a.record.lessons_observed??[]).map(l=>({...l,evidence_file:a.file}))),...extra.lessons??[]];
    const completeVisuals=taskInfos.flatMap(t=>t.info.iterations.filter(i=>i.type==='visual'&&i.completed).map(i=>({task_id:t.state.id,...i})));
    for(const lesson of lessons)text.push(`- ${lesson.task_id??'shared'}：${lesson.observed??''} 修改：${lesson.change??''} 验证：${lesson.verification??''}${lesson.evidence_file?'；'+link('记录',lesson.evidence_file):''}。`);
    for(const i of completeVisuals)text.push(`- ${i.task_id}/${i.version_id}：${i.changes} 比较结果：${i.comparison}；前后实际查看事件 ${i.before_view_id} → ${i.after_view_id}。`);
    const failures=[...shared.requests,...taskInfos.flatMap(t=>t.info.requests)].filter(r=>!r.ok);
    if(failures.length){text.push('','真实失败响应：');for(const req of failures)text.push(`- ${req.id} HTTP ${req.http_status??'未取得'}：${mdCell(req.error_summary??'错误原因未记录')}；${req.response_file?link('保留响应',req.response_file):'网络错误文件保留在请求目录'}。`);}else text.push('','当前实际请求日志未记录 HTTP/网络失败；可观察版面问题已按真实查看与改动记录列出，不补造服务错误。');
    text.push('','## 三轮预置与复用范围','','A21/A22按第一轮归档后再执行第二、第三轮。轮次需求可提前访问，此模式不声称隐藏反馈盲测。每轮图像、DSL、报告、指标与变化证据分别归档；总指标只累计各题顶层加 shared，轮次/用例明细不再次相加。','');
    const auditResult=extra.audit_result??null;
    text.push('## 总审查与剩余事项','');
    if(auditResult)text.push(`文件/指标/链接审查时间：${auditResult.audited_at??'未记录'}；自动结果：${auditResult.passed?'通过':'未通过'}；问题 ${auditResult.issues?.length??0} 项。${extra.audit_file?' '+link('完整审查记录',extra.audit_file):''}`);
    text.push(extra.visual_audit_statement??'本报告不从文件存在、成功 HTTP 或查看记录推断实际视觉审查已经通过。逐图内容、数据、几何、效果、独立作品与目标观看尺寸的质量结论，以执行者真实查看及单题/轮次/用例报告为准。');
    const remaining=state.tasks.filter(t=>t.status!=='completed');if(remaining.length)text.push('',`尚未完成：${remaining.map(t=>t.id+' '+t.status).join('、')}。`);else text.push('','所有题状态均为 completed；是否全套可最终交付仍需总审查记录与实际视觉审查结论支持。');
    for(const t of state.tasks)for(const issue of t.unresolved_issues??[])text.push(`- ${t.id}：${typeof issue==='string'?issue:JSON.stringify(issue)}。`);
    for(const item of extra.remaining_issues??[])text.push('- '+item+'。');
    if(state.stop_reason||extra.stop_reason)text.push('',`停止/中断原因：${extra.stop_reason??state.stop_reason}。`);
    text.push('',`恢复检查点：${state.last_checkpoint?link('最新不可覆盖状态快照',state.last_checkpoint):'尚无'}。恢复同一运行时沿用 ${run_id}，核对实际产物与日志后从未完成处继续。`,'','## 真实消耗与计量边界','',`总墙钟起点：${state.started_at}；结束：${state.ended_at??'仍在执行'}；当前墙钟 ${(new Date(state.ended_at??now())-new Date(state.started_at))/1000} 秒。`,`实际请求耗时之和（shared 加每题日志）：${[...shared.requests,...taskInfos.flatMap(t=>t.info.requests)].reduce((sum,r)=>sum+(r.duration_seconds??0),0)} 秒；此值不等于总墙钟。`,`真实 token、图像输入计费与金额：null。原因：${unknownUsage.unknown_fields_reason}`,`完整消费汇总：${link('task-metrics.json',path.join(outputSuite,'task-metrics.json'))}。已下载缓存、测试夹具与仅复用文档不作为新真实服务请求累计。`);
    return report('shared',text.join('\n')+'\n');
  }
  function suiteEnd(status, details = {}) {
    if(!['completed','partial','blocked'].includes(status))throw new Error('Invalid suite status');
    if(status==='completed'){const result=audit();if(!result.passed)throw new Error('Suite audit has unresolved issues: '+result.issues.join('; '));if(!details.visual_audit_passed)throw new Error('Explicit completed content/visual suite audit required');}
    const state=checkpoint('suite-'+status,details,s=>Object.assign(s,{status,ended_at:now(),stop_reason:details.stop_reason??null,current_task:status==='completed'?null:s.current_task,current_round:status==='completed'?null:s.current_round,current_case:status==='completed'?null:s.current_case}));aggregate(details);return state;
  }
  return {root,run_id,config,catalog,outputRoot,tempRoot,outputSuite,tempSuite,statePath,readState,taskDirs,taskSpec,event,checkpoint,taskStart,taskCheckpoint,taskEnd,request,render,acceptFinal,saveVersion,view,recordView:view,iteration,logIteration:iteration,toolUsage,waitRecord,artifact,publish,countsFor,writeTaskMetrics,report,writeSuiteReport,aggregate,inspectLinks,inspectAudit,audit,suiteEnd};
}

module.exports = {createSuite, pngDimensions, sha256, json, lines, immutable};
// Ergonomic default singleton methods, initialized lazily and still read-only on import.
let singleton;
for(const key of ['readState','taskDirs','taskSpec','event','checkpoint','taskStart','taskCheckpoint','taskEnd','request','render','acceptFinal','saveVersion','view','recordView','iteration','logIteration','toolUsage','waitRecord','artifact','publish','countsFor','writeTaskMetrics','report','writeSuiteReport','aggregate','inspectLinks','inspectAudit','audit','suiteEnd'])module.exports[key]=(...args)=>(singleton??=createSuite())[key](...args);
