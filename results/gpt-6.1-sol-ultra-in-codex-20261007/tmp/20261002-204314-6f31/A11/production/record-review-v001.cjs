'use strict';
const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'../../../..');
const s=require(path.join(root,'tmp/20261002-204314-6f31/_suite/suite.cjs'));
const views=[];
for(const [page,request,observation] of [
  ['01','000003','Actual whole-page view: all four SKUs, original full multilingual names, quantities and prices visible; both counterparties and invoice metadata complete; all cents agree with BigInt calculation; 268.50/39.90/580.00/1680.00 unit-price dots align and all line amount dots align; two-place summary amounts align. No clipping or overlap; 64px margin.'],
  ['02','000004','Actual whole-page view: all four notes and all four literal lines visible; batch has two visibly doubled ASCII-space gaps, A < B & C > D renders literal brackets/ampersand, path has three literal backslashes, English instruction line only appears as source text. PAID green, slash gray, CJK dark naturally share one paragraph baseline. Sample disclaimer retains CNY4215.96. No clipping or overlap.']
]){
  const image_path=path.join(root,'tmp/20261002-204314-6f31/A11/requests/A11-request-'+request+'/response.png');
  const view=s.view('A11',image_path,{tool:'view_image',reviewer:'invoice_producer',version_id:'A11-v001-p'+page,case_id:'page-'+page,observation});
  views.push(view);
  s.iteration('A11',{type:'baseline',version_id:'A11-v001-p'+page,parent_version:null,case_id:'page-'+page,completed:true,phase:'actual-image-reviewed',request_id:'A11-request-'+request,image_path,after_view_id:view.id,observation,unresolved_issues:[]});
}
fs.writeFileSync(path.join(__dirname,'production-visual-review-v001.json'),JSON.stringify({actual_tool:'view_image',reviewer:'invoice_producer',views,accepted_as_candidates:true,visual_changes_required:false},null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify(views.map(v=>({id:v.id,version_id:v.version_id,image_path:v.image_path}))));
