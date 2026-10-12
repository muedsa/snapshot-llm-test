'use strict';
const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'../../../..'),s=require(path.join(root,'tmp/20261002-204314-6f31/_suite/suite.cjs'));
const views=[];
for(const [layout,request,obs] of [['desktop','000011','Actual full desktop view: all original 25 fields complete; full title natural 2-line wrap, subtitle/date/time/location, CTA/website and all six card IDs/titles/details. Spacious 2-column grid, correct common color and corner-frame motif. No clipping or text overlap.'],['stage','000012','Actual full stage view: all 25 original fields readable, same poster system and 3-column grid. C1,C2,C6 details naturally wrap with a single trailing CJK character on second line; this is complete but visually awkward at large screen. Improve card detail width while preserving full exact Raw strings.']]){
const image_path=path.join(root,'tmp/20261002-204314-6f31/A12/requests/A12-request-'+request+'/response.png');
const v=s.view('A12',image_path,{tool:'view_image',reviewer:'invoice_producer',case_id:layout,version_id:'A12-v004-'+layout,observation:obs});
views.push(v);
s.iteration('A12',{type:'alternative',version_id:'A12-v004-'+layout,parent_version:'A12-v003-'+layout,case_id:layout,completed:true,phase:'actual-image-reviewed',request_id:'A12-request-'+request,image_path,after_view_id:v.id,observation:obs,changes:'Only motif borderRadius3→8 in original full DSL, preserving original horizontal Transform divider.',classification_correction:'render initially labeled syntax-fix, but response was INTERNAL_ERROR, not PARSE_ERROR. Latest actual classification is controlled geometry alternative, without claiming internal implementation cause.',unresolved_issues:layout==='stage'?['Single trailing character wraps in three card details; next true visual version will widen details.']:[]});
}
fs.writeFileSync(path.join(__dirname,'large-actual-reviews-v004.json'),JSON.stringify(views,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify(views.map(v=>({layout:v.case_id,view_id:v.id}))));
