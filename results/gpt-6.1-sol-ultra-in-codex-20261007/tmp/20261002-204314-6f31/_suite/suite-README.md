# Suite ledger API

This CommonJS helper handles durable bookkeeping, original response bytes and local delivery navigation. It constructs no artwork and supplies no visual judgment. Importing it is read-only. The existing run state is retained. Only the root agent should mutate state; independent readers are safe. Task execution remains in catalog order.

```js
const fs = require('node:fs');
const s = require('./tmp/20261002-204314-6f31/_suite/suite.cjs');
s.taskStart('A01', {resume_notes:'Inputs actually read; preparing baseline.'});
const result = await s.render('A01', completeDsl, {
  version_id:'A01-v001', parent_version:null, type:'baseline',
  stem:'dashboard', width:1600, height:1000,
});
console.log(JSON.stringify({
  ok:result.ok,status:result.http_status,image_path:result.image_path,
  dsl_path:result.dsl_path,meta_path:result.meta_path,
  error:result.error_summary,dimensions:result.png_dimensions,
}));
```

The root then opens `result.image_path` with the real visual tool. In a later script, record the actual observation and publish only after it passes:

```js
const r = JSON.parse(fs.readFileSync(actualRenderMetaPath,'utf8'));
const inspected = s.view('A01', r.image_path, {
  tool:'view_image', version_id:r.version_id,
  observation:'Specific actual observations, including content and geometry.',
});
s.iteration('A01', {
  type:'baseline',version_id:r.version_id,completed:true,
  image_path:r.image_path,after_view_id:inspected.id,
  observation:inspected.observation,
});
const final = s.acceptFinal('A01','dashboard',actualRenderMetaPath);
s.report('A01',actualUsageMarkdown);
s.taskEnd('A01','completed', {
  artifacts:[final.image_path,final.dsl_path],
  visual_review_evidence:[inspected.id],
  resume_notes:'Completed actual checks; continue A02.',
});
```

`render()` archives a complete `.snapshot` version, immutable request/body/headers/raw response files, request metadata and an incomplete iteration. A failed response is retained. No final is published by rendering. `acceptFinal()` checks successful PNG, expected dimensions and a matching real-view log; it copies the original PNG bytes and full DSL with matching basenames. Its writes use `wx`; repeating an existing final name fails instead of overwriting history. `publish()` is a lower-level method; prefer the checked `acceptFinal()`.

For a visual change, record the original view ID, changed DSL and observable change. Render with `type:'visual',parent_version:'A01-v001',before_view_id:...`. After actual new-image inspection, finish its iteration with `completed:true`, `before_view_id`, `after_view_id`, `changes`, and `comparison`. Metrics use the last iteration record for each version. Syntax repair, retries, alternatives and requirement changes remain separate categories. Render retries should use `retry_of:actualFailedRequestId` and a new version/request ID. `Retry-After` is returned and archived; the helper does not automatically sleep or retry.

Round/case IDs are passed as `round_id:'round-01'` / `case_id:'case-01'` to every relevant method. Publish round outputs as `round-01/name` and creative outputs as `case-01/final`. Supply title/independence/source metadata as the fourth argument of `acceptFinal()`. Each independent creative case is counted once by `case_id`; additional images or versions do not add another case. Parent-generated round/case reports and metrics can be attached through task-level metric options without being added again to suite totals.

- `taskCheckpoint(task,{round_id,case_id,completed_rounds:[],completed_cases:[],artifacts:[],visual_review_evidence:[],resume_notes})` merges durable progress and creates an immutable numbered state snapshot plus event.
- `request({task:'shared',type:'document',url,...})` returns preserved `bytes`, `response_file`, status, headers, duration and actual request ID. It is compatible with the legacy 7 shared request records already present. Request IDs have atomically reserved directories, so concurrent independent HTTP calls retain distinct attempts.
- `saveVersion(task,dsl,{version_id,parent_version,type,...})` archives independent generated DSL without rendering.
- `toolUsage(task,{tool,purpose,input_paths,output_paths,case_id,...})` records only actual auxiliary tool use. It does not count referenced HTTP events a second time.
- `waitRecord(task,'rate-limit',seconds,{request_id})` records measured waiting. Queue timing remains unknown unless a real observation supplies it.
- `report(task,text)` writes the current `snapshot-usage.md` and archives every supplied report version in temp. `report('shared',text)` writes the suite report.
- `writeTaskMetrics(task,extra)` creates the current task metric and immutable history. Token/image/cost fields remain null with an explicit reason unless actual platform values are supplied. First usable image timing is taken from the first accepted final's matching successful request.
- `aggregate()` rebuilds all-task index, all-final-image relative-link gallery and suite metrics. It sums shared plus top-level task metrics; round/case details are not double counted.
- `audit()` records an immutable automated integrity audit: statuses, count minima, PNG/DSL pairs and hashes, matching service response/view logs and required suite pointers. Its scope is explicitly file/integrity checks; the root must still review task content, geometry, data, effect and B-case independence.
- `suiteEnd('completed',{visual_audit_passed:true,...})` requires the automated audit and root's explicit completed content/visual review. Partial/blocked transitions preserve current task and stop reason.

The helper test uses a separate `helper-test-*` directory, `TEST` run ID, `fixture.invalid` URLs and mocked responses. It creates zero real requests and mutates zero real suite states. Its PNG-signature fixture is not artwork and has no bearing on the task's visual checks or consumption.

## Added integrity/report functions

`inspectAudit({tasks:['A01'],include_suite:false})` is entirely read-only. With no options it covers all catalog tasks plus required suite files. It lazily reads each actual task.json for required named PNG/DSL sizes, additional/common outputs, per-round sidecars and B-case artifacts; it never reads round-02.md or round-03.md. It verifies file dimensions, byte identity with raw service response and submitted DSL, actual-view records, current metric counts/request durations, local Markdown/HTML links, all-gallery original-image href/src coverage and unregistered output PNGs. `audit(options)` performs those same checks and archives its result. These file checks supply **no actual visual audit**. Root review must still assess all image content/data/geometry/effects and creative-case independence.

`inspectLinks(absolutePath)` is read-only and returns local link targets and missing links. Pending index rows use plain text until a report exists. Generated file URLs encode special filename characters. Every aggregate's metrics/index/gallery is archived under `_suite/aggregate-history/`.

`writeSuiteReport({audit_result,audit_file,visual_audit_statement,lessons,remaining_issues,stop_reason})` creates the suite `snapshot-usage.md` with preserved report history. It uses actual shared/task request logs, task summaries, completed visual change records, real failures, actual remaining states/checkpoint, and `shared-applications-*.json` declarations of genuinely read/applied docs/tools. Download records alone do not become claimed reading. Supplied visual_audit_statement must describe root's actual review; the generator never infers visual success.

`countsFor(task).resources` and generated metrics include measured response entity/file bytes, render/document/other response bytes, original final PNG bytes and archived DSL bytes. Legacy shared logs are measured from preserved raw files. Missing response sizes are counted separately. These are real artifact measurements, never token, billing or wire-transfer proxies; token/image-input/cost remain null. Suite request-duration sum is shared plus task top-level totals, separate from wall time, without adding case/round detail again. Regenerating task metrics preserves previous custom validation and detail fields and archives every version.
