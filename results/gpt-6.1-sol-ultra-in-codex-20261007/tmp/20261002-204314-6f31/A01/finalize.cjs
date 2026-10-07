const fs=require('fs'),path=require('path'),s=require('../_suite/suite.cjs');
const d=s.taskDirs('A01');const m=JSON.parse(fs.readFileSync(path.join(d.temp,'A01-v003-render.json'),'utf8'));
const v=s.view('A01',m.response_file,{tool:'view_image',version_id:'A01-v003',observation:'Actual 1600×1000 PNG inspected. All KPI, six bars/groups/months, aligned mini chart months, six table rows and conclusion readable. Vertical clipping fixed; unit no longer touches 250k tick.'});
s.iteration('A01',{version_id:'A01-v003',parent_version:'A01-v002',type:'visual',completed:true,image_path:m.response_file,before_view_id:'A01-view-000001',after_view_id:v.id,changes:'Split conclusion into independent positioned lines with 32/35px boxes; moved amount unit; clarified monthly conversion title.',comparison:'v002 clipped the second conclusion line and final recommendation; v003 shows all five lines in the card and the unit separately.'});
const dsl=fs.readFileSync(m.version.path,'utf8');const r={...m,bytes:fs.readFileSync(m.response_file)};
const a=s.publish('A01',r,dsl,'operations',{title:'Northstar 六个月经营诊断',version_id:'A01-v003'});
fs.copyFileSync(path.join(d.temp,'computed-data-v003.json'),path.join(d.output,'computed-data.json'));
s.taskCheckpoint('A01',{artifacts:[a],visual_review_evidence:[v.id],resume_notes:'Final service bytes published. Final-path image view and report pending.'});
console.log(JSON.stringify(a));
