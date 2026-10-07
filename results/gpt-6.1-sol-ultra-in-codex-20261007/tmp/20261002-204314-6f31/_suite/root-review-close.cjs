// Invoke only after root has genuinely opened every listed image with view_image.
// Observations are supplied by root, never inferred by this bookkeeping script.
const fs=require('node:fs'),path=require('node:path'),s=require('./suite.cjs');
const [task,reviewPath]=process.argv.slice(2),review=JSON.parse(fs.readFileSync(reviewPath,'utf8'));
if(review.task_id!==task||review.reviewer!=='root'||review.actual_tool!=='view_image'||!review.images?.length)throw Error('Actual root review declaration required');
// Root can open original service responses or delivered PNGs. Compare their
// actual bytes, so every registered final must be covered by a true declaration.
const finals=s.countsFor(task).finals;
if(!finals.length)throw Error('No registered final images to close');
const declaredHashes=new Set(review.images.map(im=>s.sha256(fs.readFileSync(im.image_path))));
const uncovered=finals.filter(im=>!declaredHashes.has(s.sha256(fs.readFileSync(im.image_path))));
if(uncovered.length)throw Error('Root review declaration omits final images: '+uncovered.map(im=>im.image_path).join(', '));
const recordedViews=s.countsFor(task).views;
const views=review.images.map(im=>{
 if(im.existing_view_id){
  const prior=recordedViews.find(v=>v.id===im.existing_view_id);
  if(!prior||prior.reviewer!=='root'||prior.tool!=='view_image'||prior.sha256!==s.sha256(fs.readFileSync(im.image_path)))throw Error('Existing view must be genuine root view of these exact bytes');
  return prior;
 }
 return s.view(task,im.image_path,{tool:'view_image',reviewer:'root',version_id:im.version_id,case_id:im.case_id??null,round_id:im.round_id??null,observation:im.observation});
});
s.taskCheckpoint(task,{artifacts:s.countsFor(task).finals,visual_review_evidence:views.map(v=>v.id),resume_notes:review.resume_notes??'Root full-image review complete; verifying all required outputs.'});
const p=path.join(s.taskDirs(task).output,'snapshot-usage.md');
s.report(task,fs.readFileSync(p,'utf8')+'\n\n## Root final review\n\n'+views.map(v=>`${v.id}: ${v.observation}`).join('\n\n')+'\n');
s.writeTaskMetrics(task,{root_review_ids:views.map(v=>v.id),root_validation:review.validation??null});
const pre=s.inspectAudit({tasks:[task],include_suite:false});
const preIssues=pre.issues.filter(i=>i!==`${task}: status in_progress`);
const d=path.join(s.taskDirs(task).temp,'root-audits');fs.mkdirSync(d,{recursive:true});
const seq=String(fs.readdirSync(d).filter(f=>f.endsWith('.json')).length+1).padStart(6,'0');
fs.writeFileSync(path.join(d,'preclose-'+seq+'.json'),JSON.stringify(pre,null,2)+'\n',{flag:'wx'});
if(preIssues.length)throw Error(JSON.stringify(preIssues));
s.taskEnd(task,'completed',{visual_review_evidence:views.map(v=>v.id),resume_notes:review.resume_notes??'Root true visuals and integrity verified. Continue catalog order.'});
const post=s.inspectAudit({tasks:[task],include_suite:false});
fs.writeFileSync(path.join(d,'postclose-'+seq+'.json'),JSON.stringify(post,null,2)+'\n',{flag:'wx'});
if(!post.passed){
  s.taskEnd(task,'partial',{unresolved_issues:post.issues,resume_notes:'Root postclose audit failed; partial status retained for repair. See '+path.join(d,'postclose-'+seq+'.json')});
  throw Error(JSON.stringify(post.issues));
}
// A definitive closing note is written only after postclose file checks pass.
const reportText=fs.readFileSync(p,'utf8');
const headingEnd=reportText.indexOf('\n');
s.report(task,reportText.slice(0,headingEnd+1)+'\nFinal status: completed. Root actual image review and required-file audit both passed. Earlier production-stage notes are superseded by this closing result.\n'+reportText.slice(headingEnd+1));
s.writeSuiteReport({visual_audit_statement:`Root genuinely reviewed all registered final images of completed tasks through ${task}; full-suite final review pending.`,remaining_issues:s.readState().tasks.filter(t=>t.status!=='completed').map(t=>t.id+': '+t.status)});
console.log(JSON.stringify({task,root_views:views.map(v=>v.id),audit:post.passed,counts:s.countsFor(task).counts,current_task:s.readState().current_task}));
