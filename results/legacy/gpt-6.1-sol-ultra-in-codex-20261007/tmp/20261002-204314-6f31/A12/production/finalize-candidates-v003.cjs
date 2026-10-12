'use strict';
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../../..'),s=require(path.join(root,'tmp/20261002-204314-6f31/_suite/suite.cjs'));
const read=f=>JSON.parse(fs.readFileSync(path.join(__dirname,f),'utf8'));
const write=(f,v)=>fs.writeFileSync(path.join(__dirname,f),JSON.stringify(v,null,2)+'\n',{flag:'wx'});
const image_path=path.join(root,'tmp/20261002-204314-6f31/A12/requests/A12-request-000013/response.png');
const v=s.view('A12',image_path,{tool:'view_image',reviewer:'invoice_producer',version_id:'A12-v005-stage',case_id:'stage',observation:'Actual complete stage v005 viewed and compared with v004: all six exact details now read on one line with full-width302px box; no lonely trailing characters. IDs sit beside titles, preserved 3x2 grid and all original content. Same size/colors/components. No text overlap or clipping.'});
s.iteration('A12',{type:'visual',version_id:'A12-v005-stage',parent_version:'A12-v004-stage',case_id:'stage',completed:true,phase:'actual-image-reviewed',request_id:'A12-request-000013',image_path,before_view_id:'A12-view-000010',after_view_id:v.id,changes:'Move all stage card details to302px full width below heading and badges beside title.',comparison:'C1/C2/C6 single-character wrap in v004 removed in v005; all six detail strings unchanged and readable. All25 main/card fields complete.',unresolved_issues:[]});
const map=read('content-map-draft-v002.json');
const candidates=[['mobile','000001','A12-v001-mobile','A12-view-000001'],['tablet','000002','A12-v001-tablet','A12-view-000002'],['desktop','000011','A12-v004-desktop','A12-view-000009'],['stage','000013','A12-v005-stage',v.id]].map(([layout,request,version_id,view_id])=>{
  const meta_path=path.join(root,'tmp/20261002-204314-6f31/A12/requests/A12-request-'+request+'/render-result.json');
  const meta=JSON.parse(fs.readFileSync(meta_path,'utf8'));
  return {layout,version_id,request_id:'A12-request-'+request,meta_path,image_path:meta.image_path,dsl_path:meta.dsl_path,producer_actual_view_id:view_id,png_sha256:crypto.createHash('sha256').update(fs.readFileSync(meta.image_path)).digest('hex'),dsl_sha256:crypto.createHash('sha256').update(fs.readFileSync(meta.dsl_path)).digest('hex'),width:meta.png_dimensions.width,height:meta.png_dimensions.height};
});
const issues=[];
for(const candidate of candidates){
const fields=map.fields.filter(f=>f.layout===candidate.layout),dsl=fs.readFileSync(candidate.dsl_path,'utf8'),margin=candidate.layout==='mobile'?16:32;
if(fields.length!==25)issues.push(candidate.layout+': wrongfieldcount');
for(const field of fields){
  field.actual_visual_status='producer_actual_image_reviewed_passed';
  field.actual_view_id=candidate.producer_actual_view_id;
  field.final_version_id=candidate.version_id;
  const p=field.position;
  if(p.x<margin||p.y<margin||p.x+p.width>candidate.width-margin||p.y+p.height>candidate.height-margin)issues.push(candidate.layout+':margin '+field.field);
  if(!dsl.includes('<![CDATA['+field.source_text+']]>'))issues.push(candidate.layout+':raw '+field.field);
}
for(let a=0;a<fields.length;a++)for(let b=a+1;b<fields.length;b++){
 const x=fields[a].position,y=fields[b].position;
 if(x.x<y.x+y.width&&x.x+x.width>y.x&&x.y<y.y+y.height&&x.y+x.height>y.y)issues.push(candidate.layout+': overlap '+fields[a].field+' '+fields[b].field);
}
}
if(issues.length)throw new Error(JSON.stringify(issues));
map.status='producer_actual_visual_review_passed';map.final_candidates=candidates;
map.static_field_validation={all_100_source_fields_in_exact_Raw_CDATA:true,expected_25_fields_per_layout:true,all_text_boxes_within_required_safe_margin:true,all_text_box_pairs_nonoverlapping:true,checked_pairs_per_layout:300,issues};
map.final_review_scope='Producer actual whole-page views cover all four final candidates; root and independent auditor perform additional final review before publication.';
write('content-map-final-draft-v003.json',map);
const tokens=read('design-tokens-draft-v001.json');
tokens.components.decorative_motif={construction:'Two interlocking outlined corner frames from Container rectangles, same motif repositions/scales per canvas.',border_radius_by_layout:{mobile:3,tablet:3,desktop:8,stage:8},border_width_by_layout:{mobile:2,tablet:3,desktop:4,stage:5},rule:'Border radius is at least stroke width in actual accepted motif geometry.',real_render_observation:'Original desktop/stage with radius3 and borders4/5 returned500; changing only motif radius to8 made both complete original DSLs return200. Service internals are unknown; correlation is confirmed, internal cause is not asserted.'};
for(const [layout,x,y,minbody] of [['mobile',8,8,16],['tablet',16,16,20],['desktop',24,16,22],['stage',26,24,24]]){
 delete tokens.breakpoints[layout].card_gap;
 tokens.breakpoints[layout].card_gap_horizontal=x;tokens.breakpoints[layout].card_gap_vertical=y;tokens.breakpoints[layout].minimum_body_size=minbody;
}
tokens.components.card.stage_detail_layout='Full card width below heading:302px; ID badge beside title. Avoids single trailing character soft wraps at26px.';
tokens.status='producer_actual_visual_review_passed';tokens.final_candidate_versions=candidates.map(c=>({layout:c.layout,version_id:c.version_id,producer_actual_view_id:c.producer_actual_view_id}));
write('design-tokens-final-draft-v002.json',tokens);
write('production-handoff-v001.json',{task_id:'A12',run_id:'20261002-204314-6f31',candidates,content_map:path.join(__dirname,'content-map-final-draft-v003.json'),design_tokens:path.join(__dirname,'design-tokens-final-draft-v002.json'),all_production_writes_finished:true,no_final_artifacts_published:true,notes:['All25 source fields present in each canvas,100 mapped fields, Raw/CDATA unchanged.','True500 responses and retries, geometry/text diagnostic branches all retained.','v004 repair initial render label syntax-fix was corrected via latest iteration to alternative because errors were INTERNAL_ERROR, not parsing errors.','One actual visual stage refinement, after a successfully viewed full picture.'],unresolved_production_issues:[]});
console.log(JSON.stringify({candidates:candidates.map(c=>({layout:c.layout,meta_path:c.meta_path,view_id:c.producer_actual_view_id})),content_map:path.join(__dirname,'content-map-final-draft-v003.json'),design_tokens:path.join(__dirname,'design-tokens-final-draft-v002.json'),all_production_writes_finished:true}));
