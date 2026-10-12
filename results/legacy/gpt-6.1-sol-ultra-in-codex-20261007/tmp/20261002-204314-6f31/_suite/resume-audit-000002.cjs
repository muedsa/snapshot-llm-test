const fs=require('fs'),path=require('path'),s=require('./suite.cjs');
const a=s.inspectAudit({tasks:['A01','A02','A03','A04','A05','A06','A07','A08','A09'],include_suite:true});
fs.writeFileSync(path.join(__dirname,'resume-file-audit-000002.json'),JSON.stringify({generated_at:new Date().toISOString(),kind:'file_integrity_and_links_only_not_new_visual_review',audit:a},null,2)+'\n',{flag:'wx'});
s.taskCheckpoint('A10',{resume_notes:'Same run resumed. A01–A09 completed with actual visuals; file/link audit passed. A10 production/document/pixel review in progress. No task scope changes.'});
const m=s.aggregate();
console.log(JSON.stringify({audit_passed:a.passed,counts:m.counts,statuses:m.task_status_counts}));
