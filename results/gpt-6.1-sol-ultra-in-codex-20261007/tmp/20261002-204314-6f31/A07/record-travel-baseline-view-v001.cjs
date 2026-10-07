'use strict';
const fs=require('node:fs'),path=require('node:path'),s=require('../_suite/suite.cjs');
const image=path.join(__dirname,'requests/A07-request-000001/response.png');
const view=s.view('A07',image,{tool:'view_image',reviewer:'infrastructure_resume',version_id:'A07-travel-v001',observation:'Actual full 720x1280 phone baseline viewed: all 3 ordinary station sequences and line segments readable; Q1 6/1 accessible; Q2 6/1 inaccessible at S05 and complete 6/2 alternative at S08/S04; Q3 4/1 accessible with S05 same-line passage; 20px rules/notes fit and no content clips. R/B/G glyphs sit too close to left chip edge, so center them for clearer repeated line encoding.'});
s.iteration('A07',{type:'baseline',version_id:'A07-travel-v001',completed:true,phase:'actual-baseline-viewed',image_path:image,view_id:view.id,observed_problem:'Line letter glyphs left aligned at chip edge; information complete and no clipping.',comparison:'Initial actual image reviewed; no before/after comparison yet.'});
fs.writeFileSync(path.join(__dirname,'travel-baseline-review-v001.json'),JSON.stringify({view,changes_required:['Center R/B/G glyphs within line chips'],information_review_passed:true,final_published:false},null,2)+'\n',{flag:'wx'});
process.stdout.write(JSON.stringify({view_id:view.id})+'\n');
