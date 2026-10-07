// Bookkeeping only. Invoke only after root genuinely opens exact image bytes.
const fs=require('node:fs'),path=require('node:path'),s=require('./suite.cjs');
const [task,reviewFile]=process.argv.slice(2),review=JSON.parse(fs.readFileSync(reviewFile,'utf8'));
if(review.task_id!==task||review.reviewer!=='root'||review.actual_tool!=='view_image'||!review.observation)throw Error('Actual root review declaration required');
const meta=JSON.parse(fs.readFileSync(review.meta_path,'utf8'));
const v=s.view(task,meta.image_path,{tool:'view_image',reviewer:'root',version_id:meta.version_id,case_id:meta.case_id,observation:review.observation});
s.iteration(task,{type:meta.iteration_type,version_id:meta.version_id,parent_version:meta.parent_version,case_id:meta.case_id,completed:true,phase:'actual-image-reviewed',request_id:meta.id,after_view_id:v.id,observation:review.observation,...(review.iteration??{})});
s.toolUsage(task,{tool:'functions.view_image',case_id:meta.case_id,purpose:'Actual full service PNG review',input:meta.image_path,output:reviewFile,view_id:v.id});
fs.writeFileSync(path.join(path.dirname(reviewFile),path.basename(reviewFile,'.json')+'-recorded.json'),JSON.stringify({review_file:path.resolve(reviewFile),view:v,meta_path:review.meta_path},null,2)+'\n',{flag:'wx'});
s.taskCheckpoint(task,{case_id:meta.case_id,event_type:'case-reviewed',visual_review_evidence:[v.id],resume_notes:review.observation});s.writeTaskMetrics(task);
console.log(JSON.stringify({view_id:v.id,case_id:meta.case_id,version_id:meta.version_id}));
