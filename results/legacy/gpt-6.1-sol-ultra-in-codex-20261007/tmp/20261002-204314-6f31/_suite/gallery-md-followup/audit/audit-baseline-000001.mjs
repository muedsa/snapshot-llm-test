import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';

const root = path.resolve('.');
const run = '20261002-204314-6f31';
const out = path.join(root, 'outputs', run);
const temp = path.join(root, 'tmp', run);
const suite = path.join(out, '_suite');
const auditDir = path.join(temp, '_suite', 'gallery-md-followup', 'audit');
const read = p => JSON.parse(fs.readFileSync(p, 'utf8').replace(/^\uFEFF/, ''));
const hash = p => crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const relative = p => path.relative(root, p).replaceAll('\\', '/');
const statePath = path.join(suite, 'suite-state.json');
const state = read(statePath);
const metricsPath = path.join(suite, 'task-metrics.json');
const metrics = read(metricsPath);
const files = new Map();
function record(p, type) {
  if (fs.existsSync(p)) files.set(relative(p), {type, bytes:fs.statSync(p).size, sha256:hash(p)});
}
for (const task of state.tasks) {
  record(path.join(out, task.id, 'task-metrics.json'), 'task-metrics');
  for (const artifact of task.artifacts) {
    record(artifact.image_path, 'final-png');
    record(artifact.dsl_path, 'final-dsl');
  }
}
function logs(p) {
  for (const item of fs.readdirSync(p, {withFileTypes:true})) {
    const q = path.join(p,item.name);
    if (item.isDirectory()) {
      if (item.name !== 'gallery-md-followup') logs(q);
    } else if (/^(requests|iterations|tool-usage|views)\.jsonl$/.test(item.name)) record(q,'execution-log');
  }
}
logs(temp);
const result = {
  audit_id:'gallery-md-independent-baseline-000001',
  captured_at:new Date().toISOString(),
  scope:'Read-only metadata/hash baseline; no service HTTP, rendering or visual image inspection.',
  run_id:run,
  suite_state_sha256:hash(statePath),
  suite_metrics_sha256:hash(metricsPath),
  original_checkpoint:state.last_checkpoint,
  original_suite_artifacts:state.suite_artifacts,
  task_states:state.tasks,
  metrics,
  files:Object.fromEntries(files),
  metrics_counts:metrics.counts,
  original_index_sha256:hash(path.join(suite,'index.md')),
  gallery_md_existed:fs.existsSync(path.join(suite,'gallery.md'))
};
fs.mkdirSync(auditDir,{recursive:true});
const destination = path.join(auditDir,'audit-000001-baseline.json');
fs.writeFileSync(destination,JSON.stringify(result,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({saved:relative(destination),file_count:files.size,artifact_count:state.tasks.reduce((n,t)=>n+t.artifacts.length,0),metrics_counts:metrics.counts,gallery_md_existed:result.gallery_md_existed}));
