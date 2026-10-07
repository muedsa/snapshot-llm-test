'use strict';
const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'../../../..'),s=require(path.join(root,'tmp/20261002-204314-6f31/_suite/suite.cjs'));
const result=[];
for(const [layout,req,obs] of [['mobile','000001','Actual complete narrow phone view: full Structure / Vision wraps naturally in two lines; original subtitle/date/time/location and C1-C6 id/title/detail all readable, single-column cards preserve every word. CTA and full website visible with >=16px canvas margin. No text-box overlap or cropping.'],['tablet','000002','Actual complete tablet view: full title on one line, full subtitle/date/time/location; all six original card IDs/titles/details visible in 2-column 3-row grid, full CTA and website. Same ivory/teal/lime system and interlocking frames. No crop, clipping or overlap, >=32px margin.']]){
  const image_path=path.join(root,'tmp/20261002-204314-6f31/A12/requests/A12-request-'+req+'/response.png');
  const v=s.view('A12',image_path,{tool:'view_image',reviewer:'invoice_producer',case_id:layout,version_id:'A12-v001-'+layout,observation:obs});
  s.iteration('A12',{type:'baseline',version_id:'A12-v001-'+layout,parent_version:null,case_id:layout,completed:true,phase:'actual-image-reviewed',request_id:'A12-request-'+req,image_path,after_view_id:v.id,observation:obs,unresolved_issues:[]});
  result.push(v);
}
fs.writeFileSync(path.join(__dirname,'first-actual-reviews-v001.json'),JSON.stringify(result,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify(result.map(v=>({layout:v.case_id,view_id:v.id}))));
