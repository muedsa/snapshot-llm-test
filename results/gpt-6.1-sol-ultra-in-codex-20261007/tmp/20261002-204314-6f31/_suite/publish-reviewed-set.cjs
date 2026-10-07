'use strict';
// Shared helper for this run. Import and --help perform no writes.
// This helper trusts recorded root visual evidence; it never creates that evidence.
const fs = require('node:fs');
const path = require('node:path');
const {createSuite, json, sha256, pngDimensions} = require('./suite.cjs');

const HELP = `Usage:
  node publish-reviewed-set.cjs TASK manifest.json [--check-only]
  node publish-reviewed-set.cjs --help

Manifest:
  {
    "finals": [{"meta_path":".../render-result.json", "stem":"round-01/example",
      "title":"Actual reviewed result", "independent_case":false, "details":{}}],
    "additional_files": [{"source":".../audit.json", "relative_output":"audit.json"}],
    "report_from":".../actual-report.md",
    "metrics_extra": {}
  }

Source paths resolve relative to the manifest file, or may be absolute.
Stems and relative_output must stay inside the selected task output directory.
All sources, successful request/version evidence, PNG/DSL hashes, actual root
view_image records and unused destinations are checked before any publication.
--check-only reads and reports metadata; it publishes nothing.
Publication preserves source bytes and never overwrites final/additional files.
Only acceptFinal, wx additional-file copies, report and writeTaskMetrics are run.
The helper never renders, views, records iterations or changes suite/task state.
It does not judge report truth, creative independence or visual quality.
`;

function object(value, name) {
  if (!value || typeof value !== 'object' || Array.isArray(value)) throw new Error(`${name} must be an object`);
  for (const key of ['__proto__', 'prototype', 'constructor']) {
    if (Object.hasOwn(value, key)) throw new Error(`${name} contains a forbidden property: ${key}`);
  }
  return value;
}
function string(value, name) {
  if (typeof value !== 'string' || !value.trim() || /[\u0000-\u001f]/.test(value)) throw new Error(`${name} must be a nonempty string without control characters`);
  return value;
}
function canonical(file) {
  const resolved = path.resolve(file).replace(/\\/g, '/');
  return process.platform === 'win32' ? resolved.toLowerCase() : resolved;
}
function samePath(a, b) { return typeof a === 'string' && typeof b === 'string' && canonical(a) === canonical(b); }
function within(base, target) {
  const relative = path.relative(path.resolve(base), path.resolve(target));
  return relative === '' || (!path.isAbsolute(relative) && relative !== '..' && !relative.startsWith('..' + path.sep));
}
function statMaybe(file) {
  try { return fs.lstatSync(file); }
  catch (error) { if (error.code === 'ENOENT') return null; throw error; }
}
function regularBytes(file, name) {
  const stat = fs.statSync(file);
  if (!stat.isFile()) throw new Error(`${name} is not a regular file: ${file}`);
  const bytes = fs.readFileSync(file);
  if (!bytes.length) throw new Error(`${name} is empty: ${file}`);
  return bytes;
}
function utf8(bytes, name) {
  const text = bytes.toString('utf8');
  if (!Buffer.from(text, 'utf8').equals(bytes)) throw new Error(`${name} is not losslessly readable as UTF-8`);
  if (text.includes('\0')) throw new Error(`${name} contains a NUL character`);
  return text;
}
function resolveSource(manifestDir, value, name) {
  return path.resolve(manifestDir, string(value, name));
}
function safeRelative(value, name) {
  string(value, name);
  if (path.isAbsolute(value) || path.win32.isAbsolute(value) || value.includes('..')) throw new Error(`${name} must be a safe relative path without '..'`);
  const components = value.replace(/\\/g, '/').split('/');
  if (components.some(part => !part || part === '.' || /[<>:"|?*]/.test(part) || /[. ]$/.test(part) || /^(?:CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\.|$)/i.test(part))) {
    throw new Error(`${name} contains an unsafe path component`);
  }
  return components.join(path.sep);
}
function checkOutputParents(outputRoot, taskOutput, target) {
  if (!within(taskOutput, target) || samePath(taskOutput, target)) throw new Error(`Destination escapes task output: ${target}`);
  if (!within(outputRoot, taskOutput)) throw new Error(`Task output escapes suite output: ${taskOutput}`);
  const rootStat = statMaybe(outputRoot);
  if (!rootStat || !rootStat.isDirectory() || rootStat.isSymbolicLink()) throw new Error(`Suite output root must be an existing plain directory: ${outputRoot}`);
  if (!samePath(fs.realpathSync(outputRoot), outputRoot)) throw new Error(`Suite output root resolves through a redirected path: ${outputRoot}`);
  let cursor = outputRoot;
  for (const part of path.relative(outputRoot, path.dirname(target)).split(path.sep).filter(Boolean)) {
    cursor = path.join(cursor, part);
    const stat = statMaybe(cursor);
    if (stat && (stat.isSymbolicLink() || !stat.isDirectory())) throw new Error(`Destination parent is not a plain directory: ${cursor}`);
  }
  if (statMaybe(target)) throw new Error(`Destination already exists; publication requires wx: ${target}`);
}
function goodStatus(record) {
  const status = record.http_status ?? record.status;
  return record.ok === true && Number.isInteger(status) && status >= 200 && status < 300;
}
function checkDimensions(actual, declared, name) {
  if (!declared || actual.width !== declared.width || actual.height !== declared.height) throw new Error(`${name} dimensions do not match preserved PNG`);
}

function preflight(task, manifestPath, options = {}) {
  string(task, 'task');
  const file = path.resolve(string(manifestPath, 'manifest path'));
  const manifest = object(json(file), 'manifest');
  const manifestDir = path.dirname(file);
  const s = options.suite ?? createSuite();
  const state = s.readState();
  const taskState = state.tasks.find(item => item.id === task);
  if (!taskState || task === 'shared') throw new Error(`Unknown task: ${task}`);
  if (taskState.status !== 'in_progress' || state.current_task !== task) throw new Error(`Task ${task} must be the active in_progress task before publication`);
  const dirs = s.taskDirs(task);
  const info = s.countsFor(task);
  if (!Array.isArray(manifest.finals) || !manifest.finals.length) throw new Error('manifest.finals must be a nonempty array');
  const additional = manifest.additional_files ?? [];
  if (!Array.isArray(additional)) throw new Error('manifest.additional_files must be an array');
  const metricsExtra = object(manifest.metrics_extra ?? {}, 'metrics_extra');
  const destinationSet = new Set();
  const pointerTargets = new Set(['snapshot-usage.md', 'task-metrics.json'].map(name => canonical(path.join(dirs.output, name))));
  function destination(relative, name) {
    const target = path.resolve(dirs.output, safeRelative(relative, name));
    const key = canonical(target);
    if (pointerTargets.has(key)) throw new Error(`${name} conflicts with the managed report/metrics pointer`);
    if (destinationSet.has(key)) throw new Error(`Manifest has duplicate destination: ${target}`);
    checkOutputParents(s.outputRoot, dirs.output, target);
    destinationSet.add(key);
    return target;
  }
  const finals = manifest.finals.map((rawEntry, index) => {
    const prefix = `finals[${index}]`;
    const entry = object(rawEntry, prefix);
    const details = object(entry.details ?? {}, `${prefix}.details`);
    const protectedFields = ['id','task_id','registered_at','image_path','dsl_path','width','height','image_sha256','dsl_sha256','request_id','version_id','title','independent_case','reviewed_view_id','publisher'];
    for (const key of protectedFields) if (Object.hasOwn(details, key)) throw new Error(`${prefix}.details must not override ${key}`);
    string(entry.title, `${prefix}.title`);
    if (typeof entry.independent_case !== 'boolean') throw new Error(`${prefix}.independent_case must be an explicit boolean`);
    const stem = safeRelative(entry.stem, `${prefix}.stem`);
    if (/\.(?:png|snapshot)$/i.test(stem)) throw new Error(`${prefix}.stem must omit the PNG/DSL extension`);
    const metaPath = resolveSource(manifestDir, entry.meta_path, `${prefix}.meta_path`);
    if (!within(dirs.temp, metaPath)) throw new Error(`${prefix}.meta_path must belong to this task's temp directory`);
    const metaBytes = regularBytes(metaPath, `${prefix} render metadata`);
    const meta = object(JSON.parse(utf8(metaBytes, `${prefix} render metadata`).replace(/^\uFEFF/, '')), `${prefix} render metadata`);
    if (meta.task_id !== task || !goodStatus(meta) || meta.dimension_error || !meta.png_dimensions) throw new Error(`${prefix} is not a successful dimension-valid PNG render for ${task}`);
    string(meta.id, `${prefix} request id`);
    string(meta.version_id, `${prefix} version id`);
    const request = info.requests.find(record => record.id === meta.id && record.task_id === task);
    if (!request || !goodStatus(request) || !['render','snapshot','open-snapshot'].includes(request.type)) throw new Error(`${prefix} has no matching successful render request ledger entry`);
    if (!samePath(metaPath, path.join(path.dirname(string(request.request_file, `${prefix} request_file`)), 'render-result.json'))) throw new Error(`${prefix}.meta_path is not the original render-result.json beside its request`);
    const envelopePath = request.request_file;
    const envelopeBytes = regularBytes(envelopePath, `${prefix} original request envelope`);
    const envelope = object(JSON.parse(utf8(envelopeBytes, `${prefix} request envelope`).replace(/^\uFEFF/, '')), `${prefix} request envelope`);
    if (envelope.id !== meta.id || envelope.task_id !== task || envelope.body_sha256 !== request.body_sha256) throw new Error(`${prefix} original request envelope differs from its ledger`);
    const imagePath = path.resolve(string(meta.response_file ?? meta.image_path, `${prefix} original PNG path`));
    const dslPath = path.resolve(string(meta.dsl_path, `${prefix} original DSL path`));
    if (!within(dirs.temp, imagePath) || !within(dirs.temp, dslPath)) throw new Error(`${prefix} PNG and DSL sources must belong to this task's temp directory`);
    if (!samePath(imagePath, request.response_file) || (meta.image_path && !samePath(meta.image_path, imagePath))) throw new Error(`${prefix} PNG source differs from preserved raw request response`);
    if (!dslPath.toLowerCase().endsWith('.snapshot')) throw new Error(`${prefix} original DSL must use .snapshot`);
    const imageBytes = regularBytes(imagePath, `${prefix} original PNG`);
    const dslBytes = regularBytes(dslPath, `${prefix} original DSL`);
    utf8(dslBytes, `${prefix} original DSL`); // acceptFinal uses UTF-8; enforce exact byte round-trip.
    const imageHash = sha256(imageBytes), dslHash = sha256(dslBytes);
    const dimensions = pngDimensions(imageBytes);
    if (!dimensions || dimensions.width < 1 || dimensions.height < 1) throw new Error(`${prefix} source is not a positive-dimension PNG`);
    checkDimensions(dimensions, meta.png_dimensions, `${prefix} metadata`);
    checkDimensions(dimensions, request.png_dimensions, `${prefix} request ledger`);
    if ((meta.expected_width != null && dimensions.width !== meta.expected_width) || (meta.expected_height != null && dimensions.height !== meta.expected_height)) throw new Error(`${prefix} PNG does not match requested dimensions`);
    if (meta.response_sha256 !== imageHash || request.response_sha256 !== imageHash || request.body_sha256 !== dslHash || meta.body_sha256 !== dslHash) throw new Error(`${prefix} source hashes differ from original service request/response`);
    const inputPath = path.resolve(string(request.input_file, `${prefix} submitted input_file`));
    if (!within(dirs.temp, inputPath)) throw new Error(`${prefix} submitted input_file escapes task temp`);
    const inputBytes = regularBytes(inputPath, `${prefix} original submitted DSL`);
    if (!inputBytes.equals(dslBytes)) throw new Error(`${prefix} final DSL bytes differ from actually submitted DSL`);
    const version = info.versions.find(record => (record.id === meta.version_id || record.version_id === meta.version_id) && record.task_id === task);
    if (!version || !samePath(version.path, dslPath) || version.sha256 !== dslHash) throw new Error(`${prefix} has no matching original DSL version record`);
    for (const key of ['case_id','round_id']) {
      if (Object.hasOwn(details, key) && details[key] !== (meta[key] ?? null)) throw new Error(`${prefix}.details.${key} must match render metadata`);
    }
    if (entry.independent_case && (typeof meta.case_id !== 'string' || !meta.case_id.trim())) throw new Error(`${prefix} independent case must have a case_id in its original render metadata`);
    const rootViews = info.views.filter(view => view.task_id === task && view.reviewer === 'root' && view.tool === 'view_image' && view.sha256 === imageHash && typeof view.viewed_at === 'string' && Number.isFinite(Date.parse(view.viewed_at)) && typeof view.observation === 'string' && view.observation.trim());
    const selectedView = Object.hasOwn(details, 'root_view_id') ? rootViews.find(view => view.id === details.root_view_id) : rootViews.at(-1);
    if (!selectedView) throw new Error(`${prefix} lacks a matching recorded actual root view_image event with observation`);
    const viewedImageBytes = regularBytes(path.resolve(string(selectedView.image_path, `${prefix} root viewed image path`)), `${prefix} root viewed image`);
    if (sha256(viewedImageBytes) !== imageHash) throw new Error(`${prefix} actual root viewed file no longer matches its recorded hash`);
    const imageTarget = destination(stem + '.png', `${prefix}.stem PNG`);
    const dslTarget = destination(stem + '.snapshot', `${prefix}.stem DSL`);
    const publishDetails = {...details, title:entry.title, independent_case:entry.independent_case, reviewed_view_id:selectedView.id, publisher:'publish-reviewed-set.cjs'};
    delete publishDetails.root_view_id;
    return {metaPath,metaHash:sha256(metaBytes),meta,imagePath,imageBytes,imageHash,dslPath,dslBytes,dslHash,inputPath,inputHash:sha256(inputBytes),envelopePath,envelopeHash:sha256(envelopeBytes),stem,imageTarget,dslTarget,dimensions,rootView:selectedView,details:publishDetails};
  });
  const extraFiles = additional.map((rawEntry, index) => {
    const prefix = `additional_files[${index}]`;
    const entry = object(rawEntry, prefix);
    const source = resolveSource(manifestDir, entry.source, `${prefix}.source`);
    const bytes = regularBytes(source, `${prefix} source`);
    const target = destination(entry.relative_output, `${prefix}.relative_output`);
    if (target.toLowerCase().endsWith('.png')) throw new Error(`${prefix} PNGs must be published through finals so they retain response and visual evidence`);
    return {source,target,bytes,sha256:sha256(bytes)};
  });
  const reportSource = resolveSource(manifestDir, manifest.report_from, 'report_from');
  const reportBytes = regularBytes(reportSource, 'report_from');
  const reportText = utf8(reportBytes, 'report_from');
  // report/metrics are managed current pointers with archived history; unlike
  // final/additional destinations, existing pointer files are intentionally allowed.
  for (const pointer of ['snapshot-usage.md','task-metrics.json']) {
    const target = path.join(dirs.output, pointer);
    const stat = statMaybe(target);
    if (stat && (stat.isSymbolicLink() || !stat.isFile())) throw new Error(`Managed pointer is not a plain file: ${target}`);
  }
  return {s,task,manifestPath:file,manifestHash:sha256(regularBytes(file,'manifest')),dirs,finals,extraFiles,reportSource,reportHash:sha256(reportBytes),reportText,metricsExtra};
}

function summary(plan) {
  return {
    task_id:plan.task, run_id:plan.s.run_id, manifest_path:plan.manifestPath,
    output_dir:plan.dirs.output, temp_dir:plan.dirs.temp,
    finals:plan.finals.map(item => ({request_id:item.meta.id,version_id:item.meta.version_id,case_id:item.meta.case_id??null,round_id:item.meta.round_id??null,title:item.details.title,independent_case:item.details.independent_case,root_view_id:item.rootView.id,width:item.dimensions.width,height:item.dimensions.height,png_bytes:item.imageBytes.length,png_sha256:item.imageHash,dsl_bytes:item.dslBytes.length,dsl_sha256:item.dslHash,image_path:item.imageTarget,dsl_path:item.dslTarget})),
    additional_files:plan.extraFiles.map(item => ({source:item.source,output:item.target,bytes:item.bytes.length,sha256:item.sha256})),
    report_source:plan.reportSource, report_sha256:plan.reportHash,
    changes_state:false, creates_view_or_iteration_records:false,
    scope:'Verifies preserved files and recorded evidence only. Visual quality, creative independence and truth of supplied report/metrics annotations remain the root reviewer responsibility.'
  };
}
function verifyFreshness(plan) {
  function check(file, hash, name) {
    if (sha256(regularBytes(file, name)) !== hash) throw new Error(`${name} changed after preflight: ${file}`);
  }
  check(plan.manifestPath, plan.manifestHash, 'manifest');
  check(plan.reportSource, plan.reportHash, 'report source');
  for (const item of plan.finals) {
    check(item.metaPath,item.metaHash,'render metadata');
    check(item.imagePath,item.imageHash,'original PNG');
    check(item.dslPath,item.dslHash,'original DSL');
    check(item.inputPath,item.inputHash,'submitted DSL');
    check(item.envelopePath,item.envelopeHash,'request envelope');
    checkOutputParents(plan.s.outputRoot,plan.dirs.output,item.imageTarget);
    checkOutputParents(plan.s.outputRoot,plan.dirs.output,item.dslTarget);
  }
  for (const item of plan.extraFiles) {
    check(item.source,item.sha256,'additional source');
    checkOutputParents(plan.s.outputRoot,plan.dirs.output,item.target);
  }
  const state = plan.s.readState();
  if (state.current_task !== plan.task || state.tasks.find(task => task.id === plan.task)?.status !== 'in_progress') throw new Error('Active task state changed after preflight');
}
function publishReviewedSet(task, manifestPath, options = {}) {
  const plan = preflight(task,manifestPath,options);
  if (options.checkOnly) return {status:'preflight-passed',...summary(plan),published:false};
  const progress = {stage:'preflight-complete',published_finals:[],attempting_final:null,copied_additional_files:[],attempting_additional_file:null,report_written:false,metrics_written:false};
  try {
    verifyFreshness(plan);
    for (const item of plan.finals) {
      progress.stage = 'accept-final';
      progress.attempting_final = {request_id:item.meta.id,image_path:item.imageTarget,dsl_path:item.dslTarget};
      const artifact = plan.s.acceptFinal(task,item.stem,{...item.meta,bytes:item.imageBytes},item.details);
      progress.published_finals.push({id:artifact.id,image_path:artifact.image_path,dsl_path:artifact.dsl_path,request_id:artifact.request_id,reviewed_view_id:item.rootView.id});
      if (artifact.image_sha256 !== item.imageHash || artifact.dsl_sha256 !== item.dslHash) throw new Error('Published final bytes differ from preflight source bytes');
      progress.attempting_final = null;
    }
    for (const item of plan.extraFiles) {
      progress.stage = 'copy-additional-file';
      progress.attempting_additional_file = item.target;
      fs.mkdirSync(path.dirname(item.target),{recursive:true});
      fs.writeFileSync(item.target,item.bytes,{flag:'wx'});
      progress.copied_additional_files.push(item.target);
      progress.attempting_additional_file = null;
    }
    progress.stage = 'report';
    const reportPath = plan.s.report(task,plan.reportText);
    progress.report_written = true;
    progress.stage = 'metrics';
    const metrics = plan.s.writeTaskMetrics(task,plan.metricsExtra);
    progress.metrics_written = true;
    progress.stage = 'published';
    return {status:'published',...summary(plan),published:true,progress,report_path:reportPath,metrics_path:path.join(plan.dirs.output,'task-metrics.json'),counts:metrics.counts,task_status:metrics.status};
  } catch (error) {
    error.publication_progress = progress;
    throw error;
  }
}

function main(argv) {
  if (argv.length === 1 && ['--help','-h'].includes(argv[0])) { process.stdout.write(HELP); return; }
  const checkOnly = argv.includes('--check-only');
  const positional = argv.filter(arg => arg !== '--check-only');
  if (positional.length !== 2 || argv.some(arg => arg.startsWith('--') && arg !== '--check-only')) throw new Error('Expected TASK manifest.json [--check-only]; use --help');
  const result = publishReviewedSet(positional[0],positional[1],{checkOnly});
  process.stdout.write(JSON.stringify(result,null,2) + '\n');
}
module.exports = {preflight,publishReviewedSet,summary,HELP};
if (require.main === module) {
  try { main(process.argv.slice(2)); }
  catch (error) {
    process.stderr.write(JSON.stringify({status:error.publication_progress?'publication-interrupted':'preflight-failed',error:error.message,publication_progress:error.publication_progress??null,changes_state:false,note:'No cleanup or rollback was performed. Preserve retained files/logs and audit before retrying.'},null,2) + '\n');
    process.exitCode = 1;
  }
}
