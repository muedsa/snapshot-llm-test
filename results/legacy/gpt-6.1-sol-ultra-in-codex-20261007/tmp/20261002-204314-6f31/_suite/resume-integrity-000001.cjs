'use strict';
// Read-only real task/file checks. Only this new verification JSON is written.
// No service requests, actual visual views, state transitions or metrics writes.
const fs=require('node:fs'),path=require('node:path');
const s=require('./suite.cjs');
const tasks=['A01','A02','A03','A04','A05'];
const state=s.readState();
const outputSuite=path.join(__dirname,'../../../outputs/20261002-204314-6f31/_suite');
const audit=s.inspectAudit({tasks,include_suite:false});
const sources=['index.md','gallery.html','snapshot-usage.md'];
const suiteLinks=sources.map(name=>s.inspectLinks(path.join(outputSuite,name)));
const gallery=suiteLinks.find(r=>r.file.endsWith('gallery.html'));
const finals=tasks.flatMap(task=>s.countsFor(task).finals);
const galleryCoverage=finals.map(a=>({task_id:a.task_id,image:a.image_path,dsl:a.dsl_path,image_href:gallery.links.some(l=>l.attribute==='href'&&l.target===path.resolve(a.image_path)),image_src:gallery.links.some(l=>l.attribute==='src'&&l.target===path.resolve(a.image_path)),dsl_href:gallery.links.some(l=>l.attribute==='href'&&l.target===path.resolve(a.dsl_path))}));
const galleryIssues=galleryCoverage.filter(c=>!c.image_href||!c.image_src||!c.dsl_href).map(c=>'Gallery lacks required image/DSL link for '+c.image);
const stateArtifactWarnings=tasks.flatMap(task=>{const t=state.tasks.find(t=>t.id===task),ids=(t.artifacts??[]).map(a=>a.id),paths=(t.artifacts??[]).map(a=>a.image_path),registered=s.countsFor(task).finals;return [(new Set(ids).size<ids.length||new Set(paths).size<paths.length)?task+': current state has duplicate artifact pointers; root maintenance pending':null,registered.some(a=>!(t.artifacts??[]).some(x=>x.id===a.id||x.image_path===a.image_path))?task+': some real registered finals are not in current state.artifacts; root maintenance pending':null].filter(Boolean);});
const normalized=JSON.parse(fs.readFileSync(path.join(outputSuite,'../A05/normalized-data.json'),'utf8'));
const issues=[...audit.issues,...suiteLinks.flatMap(r=>r.issues),...galleryIssues];
const evidenceFiles=sources.map(name=>{const file=path.join(outputSuite,name),b=fs.readFileSync(file);return {file,bytes:b.length,sha256:s.sha256(b)};});
const result={id:'shared-resume-integrity-000001',run_id:state.run_id,verified_at:new Date().toISOString(),state_updated_at:state.updated_at,state_checkpoint:state.last_checkpoint,task_scope:tasks,scope:'Read-only file, byte identity, required outputs, dimensions, recorded-view metadata and local link checks. No actual visual perception or content approval is claimed by this verifier. State pointer warnings are recorded separately from real-file integrity.',passed:issues.length===0,issues,state_artifact_pointer_warnings:stateArtifactWarnings,task_audit:audit,suite_link_checks:suiteLinks,gallery_coverage:galleryCoverage,final_png_count:finals.length,evidence_files:evidenceFiles,A05_normalized_visual_review_metadata:normalized.visual_review};
fs.writeFileSync(path.join(__dirname,'resume-integrity-000001.json'),JSON.stringify(result,null,2)+'\n',{flag:'wx'});
process.stdout.write(JSON.stringify({file:path.join(__dirname,'resume-integrity-000001.json'),passed:result.passed,issues,state_artifact_pointer_warnings:stateArtifactWarnings,final_png_count:result.final_png_count})+'\n');
