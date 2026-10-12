import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';

const root = path.resolve('.');
const run = '20261002-204314-6f31';
const out = path.join(root,'outputs',run);
const suite = path.join(out,'_suite');
const tempSuite = path.join(root,'tmp',run,'_suite');
const auditDir = path.join(tempSuite,'gallery-md-followup','audit');
const json = p => JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
const sha = p => crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const rel = p => path.relative(root,p).replaceAll('\\','/');
const suiteRel = p => path.relative(suite,p).replaceAll('\\','/');
const baseline = json(path.join(auditDir,'audit-000001-baseline.json'));
const statePath = path.join(suite,'suite-state.json');
const state = json(statePath);
const catalog = json(path.join(root,'catalog.json'));
const config = json(path.join(root,'run-config.json'));
const galleryPath = path.join(suite,'gallery.md');
const text = fs.readFileSync(galleryPath,'utf8');
const metricsPath = path.join(suite,'task-metrics.json');
const metrics = json(metricsPath);
const artifacts = state.tasks.flatMap(t=>t.artifacts);
const errors = [];
const checks = [];
function check(id,fn) {
  try { const details=fn(); checks.push({id,passed:true,details:details??null}); }
  catch(e) { checks.push({id,passed:false,error:e.message}); errors.push({check:id,error:e.message}); }
}
const links = Array.from(text.matchAll(/(!?)\[([^\[\]\n]*)\]\((<[^>]+>|[^)\s]+)(?:\s+"[^"]*")?\)/g),m=>({
  preview:m[1]==='!',label:m[2],target:m[3].replace(/^<|>$/g,''),index:m.index,
}));
const previews = links.filter(l=>l.preview);
const ordinary = links.filter(l=>!l.preview);
const normalize = target => decodeURIComponent(target.split('#')[0]);
const markdownText = value => value.replace(/\\([\\`*{}\[\]()#+\-.!<>|])/g,'$1').replaceAll('&lt;','<').replaceAll('&gt;','>').replaceAll('&amp;','&');
function lookup(links,target) { return links.filter(l=>normalize(l.target)===target); }
const taskHeaders = Array.from(text.matchAll(/^##\s+(A\d{2}|B\d{2})\b[^\n]*$/gm),m=>({id:m[1],heading:m[0],index:m.index}));
const groupHeaders = Array.from(text.matchAll(/^###\s+(round-\d{2}|case-\d{2})\b[^\n]*$/gm),m=>({id:m[1],heading:m[0],index:m.index}));
const artifactEvidence = [];
check('gallery_all_30_tasks_in_catalog_order',()=>{
  assert.deepEqual(taskHeaders.map(h=>h.id),catalog.task_order);
  return taskHeaders.map(h=>h.id);
});
check('all_124_unique_registered_previews',()=>{
  assert.equal(artifacts.length,124);
  assert.equal(previews.length,124);
  assert.equal(new Set(previews.map(l=>normalize(l.target))).size,124);
  assert.deepEqual(previews.map(l=>normalize(l.target)).sort(),artifacts.map(a=>suiteRel(a.image_path)).sort());
  return {registered:artifacts.length,previews:previews.length,unique_preview_paths:124};
});
check('each_artifact_title_preview_original_png_and_dsl_link',()=>{
  for(const a of artifacts) {
    const png = suiteRel(a.image_path),dsl=suiteRel(a.dsl_path);
    const preview = lookup(previews,png);
    const original = lookup(ordinary,png);
    const snapshot = lookup(ordinary,dsl);
    assert.equal(preview.length,1,`${a.id}: preview count`);
    assert.equal(original.length,1,`${a.id}: original PNG link count`);
    assert.equal(snapshot.length,1,`${a.id}: snapshot link count`);
    const prevIndex = previews.filter(l=>l.index<preview[0].index).at(-1)?.index??0;
    const nextIndex = previews.find(l=>l.index>preview[0].index)?.index??text.length;
    const around = text.slice(prevIndex,nextIndex);
    assert.ok(markdownText(around).includes(a.title),`${a.id}: registered explicit title missing`);
    assert.ok(preview[0].label.length>0,`${a.id}: no alt/title`);
    const task = taskHeaders.filter(h=>h.index<preview[0].index).at(-1);
    assert.equal(task?.id,a.task_id,`${a.id}: task grouping`);
    if(a.round_id||/^B/.test(a.task_id)) {
      const group = groupHeaders.filter(h=>h.index>task.index&&h.index<preview[0].index).at(-1);
      assert.equal(group?.id,a.round_id||a.case_id,`${a.id}: round/case grouping`);
    }
    artifactEvidence.push({artifact_id:a.id,task_id:a.task_id,title:a.title,round_id:a.round_id??null,case_id:a.case_id??null,preview:preview[0].target,png:original[0].target,dsl:snapshot[0].target});
  }
  return {complete_triples:artifactEvidence.length};
});
check('A21_A22_rounds_and_B01_B06_cases',()=>{
  const roundCounts={};
  for(const id of ['A21','A22']) {
    const task = state.tasks.find(t=>t.id===id);
    const expectedPerRound=id==='A21'?2:1;
    assert.deepEqual(task.completed_rounds,['round-01','round-02','round-03']);
    const header=taskHeaders.find(h=>h.id===id);
    const nextHeader=taskHeaders.find(h=>h.index>header.index);
    assert.deepEqual(groupHeaders.filter(h=>h.index>header.index&&h.index<(nextHeader?.index??text.length)).map(h=>h.id),task.completed_rounds,`${id}: displayed round order`);
    roundCounts[id]={};
    for(const round of task.completed_rounds) {
      const n=task.artifacts.filter(a=>a.round_id===round).length;
      assert.equal(n,expectedPerRound);
      roundCounts[id][round]=n;
    }
  }
  const caseCounts={};
  for(const id of catalog.task_order.filter(id=>/^B/.test(id))) {
    const task=state.tasks.find(t=>t.id===id);
    const expected=Array.from({length:10},(_,i)=>'case-'+String(i+1).padStart(2,'0'));
    assert.deepEqual(task.completed_cases,expected);
    const header=taskHeaders.find(h=>h.id===id);
    const nextHeader=taskHeaders.find(h=>h.index>header.index);
    assert.deepEqual(groupHeaders.filter(h=>h.index>header.index&&h.index<(nextHeader?.index??text.length)).map(h=>h.id),expected,`${id}: displayed case order`);
    assert.deepEqual(task.artifacts.map(a=>a.case_id).sort(),expected);
    assert.ok(task.artifacts.every(a=>a.independent_case===true));
    caseCounts[id]=task.artifacts.length;
  }
  return {roundCounts,caseCounts};
});
check('all_gallery_links_relative_local_and_accessible',()=>{
  assert.ok(!/[A-Za-z]:[\\/]/.test(text),'Machine absolute path in gallery');
  assert.ok(!/\b(?:https?|file):\/\//i.test(text),'Remote/file URI in gallery');
  const resolved=[];
  for(const l of links) {
    const target=normalize(l.target);
    if(target==='') {
      const anchor=l.target.replace(/^#/,'');
      assert.ok(text.includes(`id="${anchor}"`),`Missing gallery anchor: ${l.target}`);
      continue;
    }
    assert.ok(!/^(?:[A-Za-z][A-Za-z\d+.-]*:|[\\/])/.test(target),`Nonrelative link: ${target}`);
    const file=path.resolve(suite,target);
    const runRelative=path.relative(out,file);
    assert.ok(!runRelative.startsWith('..')&&!path.isAbsolute(runRelative),`Link outside copied run: ${target}`);
    assert.ok(fs.existsSync(file),`Missing link: ${target}`);
    resolved.push(target);
  }
  return {checked_links:resolved.length,unique_linked_files:new Set(resolved).size};
});
check('clickable_previews_open_matching_original_png',()=>{
  const nested=Array.from(text.matchAll(/\[!\[[^\]\n]*\]\(([^)\s]+)\)\]\(([^)\s]+)\)/g));
  assert.equal(nested.length,124);
  for(const m of nested)assert.equal(m[1],m[2],'Preview click target differs from image');
  return {clickable_previews:nested.length};
});
check('actual_png_dsl_exists_matches_registration_and_dimensions',()=>{
  for(const a of artifacts) {
    assert.ok(fs.existsSync(a.image_path),`${a.id}: missing PNG`);
    assert.ok(fs.existsSync(a.dsl_path),`${a.id}: missing DSL`);
    assert.equal(sha(a.image_path),a.image_sha256,`${a.id}: registered image hash`);
    assert.equal(sha(a.dsl_path),a.dsl_sha256,`${a.id}: registered DSL hash`);
    const bytes=fs.readFileSync(a.image_path);
    assert.equal(bytes.subarray(0,8).toString('hex'),'89504e470d0a1a0a');
    assert.equal(bytes.readUInt32BE(16),a.width,`${a.id}: width`);
    assert.equal(bytes.readUInt32BE(20),a.height,`${a.id}: height`);
    assert.equal(path.parse(a.image_path).name,path.parse(a.dsl_path).name,`${a.id}: matching base names`);
    assert.ok(fs.statSync(a.dsl_path).size>0,`${a.id}: empty DSL`);
  }
  return {png_dsl_pairs:artifacts.length,hashes_checked:artifacts.length*2,png_headers_checked:artifacts.length};
});
check('suite_and_task_counts_logs_and_all_original_assets_unchanged',()=>{
  assert.deepEqual(metrics.counts,baseline.metrics_counts);
  const cleanupUnknown = obj => {
    if(!obj||typeof obj!=='object')return;
    for(const key of Object.keys(obj)) {
      if(key==='usage'&&obj[key]&&typeof obj[key]==='object'&&('input_tokens' in obj[key]||'cost' in obj[key])) {
        assert.ok(Object.entries(obj[key]).every(([name,value])=>name==='unknown_fields_reason'||value===null),'Measured usage removal is not allowed');
        delete obj[key];
      } else cleanupUnknown(obj[key]);
    }
    if(obj.additional_tool_consumption) for(const key of ['internal_http_requests','network_response_bytes','model_or_service_billing']) {
      if(obj.additional_tool_consumption[key]===null)delete obj.additional_tool_consumption[key];
    }
  };
  const originalMetrics=structuredClone(baseline.metrics);
  cleanupUnknown(originalMetrics);
  assert.deepEqual(metrics,originalMetrics,'Suite metric change exceeds unknown usage cleanup');
  assert.deepEqual(state.tasks,baseline.task_states,'Task state changed');
  const changedMetricFiles=[];
  for(const [p,b] of Object.entries(baseline.files)) {
    const file=path.join(root,p);
    assert.ok(fs.existsSync(file),`Original file missing: ${p}`);
    if(b.type==='task-metrics'&&sha(file)!==b.sha256) {
      const previous=path.join(tempSuite,'gallery-md-followup','before',path.relative(out,file));
      assert.ok(fs.existsSync(previous),`No retained original metric file: ${p}`);
      assert.equal(sha(previous),b.sha256,`Metric backup fails independent baseline hash: ${p}`);
      const original=json(previous);
      cleanupUnknown(original);
      assert.deepEqual(json(file),original,`Task metric change exceeds unknown usage cleanup: ${p}`);
      changedMetricFiles.push(p);
    } else {
      assert.equal(fs.statSync(file).size,b.bytes,`Original bytes changed: ${p}`);
      assert.equal(sha(file),b.sha256,`Original hash changed: ${p}`);
    }
  }
  return {baselined_files:Object.keys(baseline.files).length,unchanged_png_dsl_execution_logs:true,task_metric_changes_limited_to_unknown_usage_cleanup:changedMetricFiles,counts:metrics.counts};
});
check('index_links_required_markdown_gallery',()=>{
  const index=fs.readFileSync(path.join(suite,'index.md'),'utf8');
  assert.match(index,/\]\(gallery\.md\)/);
  return {index:'index.md',gallery:'gallery.md'};
});
check('all_37_metric_files_preserve_measurements_after_unknown_usage_cleanup',()=>{
  const manifest=json(path.join(tempSuite,'gallery-md-followup','manifest-v001.json'));
  const changed=manifest.cleaned_metric_files;
  assert.equal(changed.length,37);
  for(const current of changed) {
    const previous=path.join(tempSuite,'gallery-md-followup','before',path.relative(out,current));
    const old=json(previous),now=json(current);
    assert.deepEqual(now.counts,old.counts,`${rel(current)} counts changed`);
    assert.deepEqual(now.timings,old.timings,`${rel(current)} timings changed`);
    function cleanup(obj) {
      if(!obj||typeof obj!=='object')return;
      for(const key of Object.keys(obj)) {
        if(key==='usage'&&obj[key]&&typeof obj[key]==='object'&&('input_tokens' in obj[key]||'cost' in obj[key])) {
          assert.ok(Object.entries(obj[key]).every(([name,value])=>name==='unknown_fields_reason'||value===null));
          delete obj[key];
        } else cleanup(obj[key]);
      }
      if(obj.additional_tool_consumption)for(const k of ['internal_http_requests','network_response_bytes','model_or_service_billing'])if(obj.additional_tool_consumption[k]===null)delete obj.additional_tool_consumption[k];
    }
    cleanup(old);
    assert.deepEqual(now,old,`${rel(current)} changes exceed unknown placeholder removal`);
  }
  return {checked_metric_files:37,measurement_changes:0};
});
check('optional_original_html_file_kept',()=>{
  const p=path.join(suite,'gallery.html'),stat=fs.statSync(p);
  assert.equal(stat.size,43172,'HTML size differs from independently observed initial size');
  assert.ok(stat.mtime.toISOString()<baseline.captured_at,'HTML modified during follow-up audit');
  return {path:'gallery.html',bytes:stat.size,mtime:stat.mtime.toISOString(),sha256:sha(p),verification_limit:'Initial independent inspection recorded size/time, not HTML SHA; unchanged size and pre-follow-up mtime confirm no observed rewrite.'};
});
check('suite_required_artifacts_exist_and_suite_state_records_paths',()=>{
  assert.ok(Array.isArray(state.suite_artifacts),'suite_artifacts is not array');
  const paths=state.suite_artifacts.flatMap(a=>typeof a==='string'?[a]:Object.values(a).filter(v=>typeof v==='string'));
  for(const required of config.suite_required_artifacts) {
    const actual=path.join(suite,required);
    assert.ok(fs.existsSync(actual),`Required artifact missing: ${required}`);
    const matched=paths.find(p=>{
      try { return path.resolve(p)===actual||path.resolve(suite,p)===actual; } catch{return false;}
    });
    assert.ok(matched,`suite_artifacts lacks actual ${required} path`);
  }
  return {required:config.suite_required_artifacts,recorded:state.suite_artifacts};
});
check('completed_state_and_latest_checkpoint_consistent',()=>{
  assert.equal(state.run_id,run);
  assert.equal(state.status,'completed');
  assert.equal(state.tasks.length,30);
  assert.ok(state.tasks.every(t=>t.status==='completed'));
  assert.ok(fs.existsSync(state.last_checkpoint),'Current checkpoint missing');
  assert.deepEqual(json(state.last_checkpoint),state,'Latest checkpoint content differs from suite-state');
  const snapshots=fs.readdirSync(path.join(tempSuite,'checkpoints')).filter(s=>/^state-\d{6}\.json$/.test(s)).sort();
  assert.equal(path.basename(state.last_checkpoint),snapshots.at(-1),'State points to a nonlatest checkpoint');
  assert.notEqual(state.last_checkpoint,baseline.original_checkpoint,'No new checkpoint after index change');
  return {last_checkpoint:rel(state.last_checkpoint),checkpoint_count:snapshots.length};
});
const result={
  audit_id:'gallery-md-independent-audit-000002',
  created_at:new Date().toISOString(),
  run_id:run,
  scope:'Markdown gallery/index/state/checkpoint and unchanged artifact/log/metrics metadata only. This audit makes no new HTTP, render or visual-view claim.',
  passed:errors.length===0,
  checks,
  errors,
  artifact_evidence:artifactEvidence,
  gallery_sha256:sha(galleryPath),
  suite_state_sha256:sha(statePath),
  metrics_sha256:sha(metricsPath),
  baseline:'audit-000001-baseline.json',
};
const existing=fs.readdirSync(auditDir).map(n=>/^audit-(\d{6})-verification\.json$/.exec(n)).filter(Boolean).map(m=>Number(m[1]));
const sequence=String(Math.max(1,...existing)+1).padStart(6,'0');
const destination=path.join(auditDir,`audit-${sequence}-verification.json`);
fs.writeFileSync(destination,JSON.stringify(result,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({saved:rel(destination),passed:result.passed,check_count:checks.length,errors}));
if(errors.length)process.exitCode=1;
