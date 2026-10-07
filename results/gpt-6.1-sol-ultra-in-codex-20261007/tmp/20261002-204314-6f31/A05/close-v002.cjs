const fs=require('node:fs'),path=require('node:path'),s=require('../_suite/suite.cjs');
const pre=s.inspectAudit({tasks:['A05'],include_suite:false});
if(pre.issues.some(i=>i!=='A05: status in_progress'))throw Error(JSON.stringify(pre.issues));
s.taskEnd('A05','completed',{visual_review_evidence:['A05-view-000001'],resume_notes:'Baseline full actual image, data and report validated. Status-only preclose audit finding resolved by this transition; continue A06.'});
const post=s.inspectAudit({tasks:['A05'],include_suite:false});fs.writeFileSync(path.join(s.taskDirs('A05').temp,'final-integrity-audit-v002.json'),JSON.stringify(post,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify(post));
s.writeSuiteReport({visual_audit_statement:'Root has actually reviewed final A01–A05 images. Subsequent tasks remain pending.',remaining_issues:['A06–A24 and B01–B06 remain to execute; full-suite review pending.']});
s.taskStart('A06',{resume_notes:'A05 completed. Full A06 requirements and graph actually read; preparing directed graph and independent computation.'});
