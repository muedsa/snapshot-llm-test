'use strict';
// Isolated helper tests. Mock responses below are TEST FIXTURES, not Snapshot results.
// These tests do not mutate real suite-state or contribute requests to run metrics.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {createSuite,sha256,lines}=require('./suite.cjs');
const dir=path.join(__dirname,'helper-test-'+Date.now());fs.mkdirSync(dir);
const fixtureConfig={output_root:'output',temp_root:'temp',service_base_url:'https://fixture.invalid',asset_policy_by_track:{advanced:'dsl_only'}};
const fixtureCatalog={suite_version:'test',task_order:['A01'],tasks:[{id:'A01',track:'advanced',minimum_final_pngs:1,title:'TEST FIXTURE'}]};
const stateDir=path.join(dir,'output','TEST','_suite');fs.mkdirSync(stateDir,{recursive:true});
const state={run_id:'TEST',profile:'all',status:'in_progress',started_at:new Date().toISOString(),updated_at:new Date().toISOString(),tasks:[{id:'A01',status:'pending',started_at:null,ended_at:null,artifacts:[],completed_rounds:[],completed_cases:[],visual_review_evidence:[],unresolved_issues:[]}]};
fs.writeFileSync(path.join(stateDir,'suite-state.json'),JSON.stringify(state));
// Minimal PNG-signature/IHDR fixture, deliberately no actual artwork or service call.
const bytes=Buffer.alloc(24);Buffer.from([137,80,78,71,13,10,26,10]).copy(bytes);bytes.writeUInt32BE(100,16);bytes.writeUInt32BE(50,20);
const s=createSuite({root:dir,run_id:'TEST',config:fixtureConfig,catalog:fixtureCatalog,fetch:async(url,args)=>new Response(url.includes('failure')?Buffer.from('{"code":"TEST_ONLY"}'):bytes,{status:url.includes('failure')?400:200,headers:{'Content-Type':url.includes('failure')?'application/json':'image/png','X-Request-Id':'test-fixture-id'}})});
(async()=>{
  s.taskStart('A01',{resume_notes:'Isolated helper fixture test'});
  const r=await s.render('A01','<Snapshot/>',{version_id:'A01-test-v1',width:100,height:50});
  assert.equal(r.ok,true);assert.deepEqual(r.png_dimensions,{width:100,height:50});
  assert.throws(()=>s.acceptFinal('A01','final',r.meta_path),/actual tool view/);
  // Test recordView behavior only; this is a fixture, not a visual-inspection claim.
  const v=s.view('A01',r.image_path,{tool:'TEST-FIXTURE-NO-REAL-VIEW',observation:'API fixture test'});
  s.iteration('A01',{type:'baseline',version_id:r.version_id,completed:true,image_path:r.image_path,after_view_id:v.id});
  const a=s.acceptFinal('A01','final',r.meta_path);assert.equal(a.image_sha256,sha256(bytes));assert.equal(fs.readFileSync(a.image_path).equals(bytes),true);
  assert.throws(()=>s.acceptFinal('A01','final',r.meta_path),e=>e.code==='EEXIST');
  const bad=await s.request({task:'A01',type:'document',url:'https://fixture.invalid/failure?api_key=not-a-real-key',body:{password:'not-a-real-password',fine:1},headers:{Authorization:'TEST ONLY'}});
  assert.equal(bad.ok,false);assert.equal(bad.http_status,400);
  assert.equal(fs.readFileSync(bad.request_file,'utf8').includes('not-a-real-key'),false);
  assert.equal(fs.readFileSync(bad.input_file,'utf8').includes('not-a-real-password'),false);
  assert.equal(fs.readFileSync(bad.request_file,'utf8').includes('TEST ONLY'),false);
  s.report('A01','# TEST FIXTURE ONLY\n');
  s.taskEnd('A01','completed',{artifacts:[a.image_path,a.dsl_path],visual_review_evidence:[v.id]});
  s.writeSuiteReport({visual_audit_statement:'TEST FIXTURE ONLY; this is not actual visual inspection.'});
  assert.equal(s.inspectLinks(path.join(s.outputSuite,'snapshot-usage.md')).issues.length,0);
  const m=JSON.parse(fs.readFileSync(path.join(s.taskDirs('A01').output,'task-metrics.json')));
  assert.equal(m.counts.snapshot_requests,1);assert.equal(m.counts.document_requests,1);assert.equal(m.counts.image_views,1);assert.equal(m.counts.final_pngs,1);assert.equal(m.counts.baseline_versions,1);assert.equal(m.usage.cost,null);
  assert.equal(s.audit().passed,true);assert.throws(()=>s.suiteEnd('completed'),/visual suite audit/);
  assert.equal(lines(path.join(s.taskDirs('A01').temp,'requests.jsonl')).length,2);
  assert.equal(fs.readdirSync(path.join(s.tempSuite,'checkpoints')).length,2);
  console.log(JSON.stringify({passed:true,isolated_test_dir:dir,real_requests:0,real_suite_state_mutations:0}));
})().catch(e=>{console.error(e);process.exitCode=1});
