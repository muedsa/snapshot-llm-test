'use strict';
const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'../../../..'),s=require(path.join(root,'tmp/20261002-204314-6f31/_suite/suite.cjs'));
const reference=path.join(root,'tasks/A15-reference-reconstruction/inputs/reference.png');
const records=[];
for(const [file,original,version,observation] of [
[reference,reference,null,'Actual original1440x900 reference viewed: sidebar220, KPIrow at138, chart/activity310, table624, selectednav116; full source text and reference proportions inspected.'],
[path.join(__dirname,'reference-thumb-v001.png'),reference,null,'Actual720px reference thumbnail viewed: complete density/layout hierarchy, four quadrants and separate table/card right boundaries inspected.'],
[path.join(__dirname,'reference-chart-crop-v001.png'),reference,null,'Actual reference chart crop viewed: ticks0/30/60/90/120, zero549/top405, six bars proportional, monthlabels andNetrevenue title complete.'],
[path.join(__dirname,'reference-table-crop-v001.png'),reference,null,'Actual reference table crop viewed: three source rows ordered, pillprogressblue/reviewyellow/donegreen, headings and owner/due fields complete.'],
[path.join(root,'tmp/20261002-204314-6f31/A15/requests/A15-request-000001/response.png'),null,'A15-v001','Actual baseline1440x900 service image viewed: reconstructed structure/cards/grid and sixbars visually align, all source text retained. Main title andsection headings wider than reference; true pureink metrics show+20/+11..14px right-edge differences requiring font correction.'],
[path.join(__dirname,'reconstructed-thumb-v001.png'),null,'A15-v001','Actual baseline720px thumbnail viewed and compared with reference: matching overall arrangement/card hierarchy, mildly oversized header/section typography visible.'],
[path.join(__dirname,'reconstructed-chart-crop-v001.png'),null,'A15-v001','Actual baseline chart crop viewed: exact geometric data proportions and ticks preserved; title slightly larger than reference.'],
[path.join(__dirname,'reconstructed-table-crop-v001.png'),null,'A15-v001','Actual baseline table crop viewed: table rows/status mapping complete, table heading slightly wider than reference.']]){
const r=s.view('A15',file,{tool:'view_image',reviewer:'invoice_producer',version_id:version,case_id:version?'reconstructed':'reference',original_image_path:original,observation});records.push(r);
}
const baseline=records.find(v=>v.version_id==='A15-v001'&&v.image_path.includes('requests'));
s.iteration('A15',{type:'baseline',version_id:'A15-v001',parent_version:null,completed:true,phase:'actual-image-reviewed',image_path:baseline.image_path,after_view_id:baseline.id,observation:baseline.observation,unresolved_issues:['Typography approximate: main and3section pureink right edges exceed8px tolerance until correction.']});
fs.writeFileSync(path.join(__dirname,'before-actual-reviews-v001.json'),JSON.stringify({records,baseline_view_id:baseline.id},null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({baseline_view_id:baseline.id,views:records.map(v=>v.id)}));
