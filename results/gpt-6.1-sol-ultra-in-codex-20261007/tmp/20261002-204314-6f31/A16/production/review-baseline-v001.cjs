'use strict';
const fs=require('node:fs'),path=require('node:path');const root=path.resolve(__dirname,'../../../..');
const s=require(path.join(root,'tmp/20261002-204314-6f31/_suite/suite.cjs'));
const meta=path.join(root,'tmp/20261002-204314-6f31/A16/requests/A16-request-000001/render-result.json');
const r=JSON.parse(fs.readFileSync(meta,'utf8'));
const v=s.view('A16',r.image_path,{tool:'functions.view_image',detail:'high',version_id:r.version_id,role:'producer-full-baseline-review',observation:'Actual1280×900 correctedreport visually shows8squarebarswithcommonbaseline0,blue收入andorange成本legendconsistent,Q3blue128lowerthanQ2blue135,allquartersprofit30/27/32/54withcalculations,clearlyhighlightQ4profit54andmargin30.0%,subtitlecorrectsourcecomparisons,bodyreadablewithno clipping oroverlap. No observeddefectneedsvisualrevision.'});
const i=s.iteration('A16',{type:'baseline',version_id:r.version_id,parent_version:null,completed:true,phase:'actual-image-reviewed',request_id:r.id,image_path:r.image_path,after_view_id:v.id,observation:'All source-accurate8bar/legend/axis/profit/narrative requirements appear visually satisfied on actual raw service PNG; no manufacturediteration.',unresolved_issues:[]});
fs.writeFileSync(path.join(__dirname,'producer-baseline-review-v001.json'),JSON.stringify({task_id:'A16',run_id:'20261002-204314-6f31',version_id:r.version_id,view_id:v.id,iteration_id:i.id,actual_image_path:r.image_path,meta_path:meta,passed:true,observed_remaining_problems:[],review_scope:'Actual service1280×900 wholeimage; pixelgeometry separately pending independentmeasurement.'},null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({view_id:v.id,iteration_id:i.id}));
