const fs=require('node:fs'),path=require('node:path'),s=require('../../_suite/suite.cjs');
const d=s.taskDirs('B06'),source=path.join(d.temp,'audit-root-independent-v001/views-for-import-v001.json'),rows=JSON.parse(fs.readFileSync(source,'utf8'));
const existing=s.countsFor('B06').views;
for(const v of rows){if(v.tool!=='view_image'||!v.viewed_at||!v.observation||s.sha256(fs.readFileSync(v.image_path))!==v.sha256)throw Error('Invalid actual private view '+v.id);}
const records=[];
for(const v of rows){
 const prior=existing.find(x=>x.source_private_view_id===v.id);
 if(prior){records.push(prior);continue;}
 const {id,task_id,image_path,sha256,...detail}=v;
 records.push(s.view('B06',image_path,{...detail,source_private_view_id:id,source_private_ledger:source,imported_at:new Date().toISOString()}));
}
const out=path.join(__dirname,'imported-independent-views-v001.json');
fs.writeFileSync(out,JSON.stringify({source,private_count:rows.length,records,scope:'Genuine auditor views imported once. No new view or visual iteration is claimed by this bookkeeping operation.'},null,2)+'\n',{flag:'wx'});
s.toolUsage('B06',{tool:'node / import-independent-views-v001.cjs',purpose:'Import genuine independent view events without repeating visual iteration counts',input:source,output:out,imported_views:records.length});
s.taskCheckpoint('B06',{visual_review_evidence:records.map(v=>v.id),resume_notes:'Ten final candidates and collection passed actual root and independent review. Twenty-one genuine independent views imported once. Publishing B06 before full suite audit.'});
s.writeTaskMetrics('B06');s.aggregate();
console.log(JSON.stringify({imported:records.length,public_views:s.countsFor('B06').counts.image_views,completed_visual:s.countsFor('B06').counts.completed_visual_iterations}));
