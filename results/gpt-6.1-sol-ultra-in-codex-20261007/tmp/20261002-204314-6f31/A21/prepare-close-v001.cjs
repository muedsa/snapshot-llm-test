const fs=require('node:fs'),path=require('node:path'),s=require('../_suite/suite.cjs');
const d=s.taskDirs('A21');
s.taskCheckpoint('A21',{event_type:'round-archive-verified',round_id:'round-03',completed_rounds:['round-03'],resume_notes:'第三轮真实指标wx归档通过；三轮六图实际审查完整，准备整题关闭。'});
const rounds=[1,2,3].map(i=>JSON.parse(fs.readFileSync(path.join(d.output,`round-0${i}/task-metrics.json`),'utf8')));
s.writeTaskMetrics('A21',{rounds,quantitative_contrast_pending:false,contrast_minimum:6.5456167376});
const images=[1,2,3].flatMap(i=>JSON.parse(fs.readFileSync(path.join(d.temp,`round-0${i}/root-review-v001.json`),'utf8')).images);
const review={task_id:'A21',reviewer:'root',actual_tool:'view_image',images,validation:{preloaded_sequential:true,blind_feedback:false,three_rounds_archived:true,all_six_exact_final_PNGs_actually_viewed:true,round03_contrast_regions:20,round03_contrast_minimum:6.5456167376,round03_content_geometry_audit_pass:true,earlier_round_files_unchanged:true,unresolved_issues:[]},resume_notes:'A21三轮6原PNG/DSL实际查看与对比度/内容/几何/不可覆盖归档核通过；立即A22预置三轮。'};
fs.writeFileSync(path.join(d.temp,'root-final-review-v001.json'),JSON.stringify(review,null,2)+'\n',{flag:'wx'});
s.aggregate();
