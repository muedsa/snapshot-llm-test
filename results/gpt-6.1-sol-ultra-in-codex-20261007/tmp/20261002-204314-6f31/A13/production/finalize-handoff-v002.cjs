'use strict';
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../../..'),s=require(path.join(root,'tmp/20261002-204314-6f31/_suite/suite.cjs'));
const read=f=>JSON.parse(fs.readFileSync(path.join(__dirname,f),'utf8'));
const write=(f,v)=>fs.writeFileSync(path.join(__dirname,f),typeof v==='string'?v:JSON.stringify(v,null,2)+'\n',{flag:'wx'});
const qa=read('final-qa-provenance-v001.json'),alpha=read('alpha-difference-review-v001.json');
const producerViews=[];
for(const [name,req,observation] of [
['symbol-color','000003','Actual512 color original reviewed: same two offset rounded windows with thicker40px stroke; outer contours stronger than preview and common center negative space remains open.'],
['symbol-black','000004','Actual512 black original opened, viewer black matte hides silhouette. Separate actual512 white QA plate viewed confirms same two-window outline and negative space. Exact original nontransparent RGB audit is0.'],
['brand-banner','000005','Actual1200x400 banner viewed: left symbol regenerated from shared DSL geometry, full brand wordmark and full original tagline clearly visible, no clipping or overlap.'],
['launch-poster','000006','Actual1080x1350 poster viewed: independent vertical composition, OPEN BETA label, full brand/tagline above large regenerated shared symbol, dateONLINE and URL below. No clipped text.']]){
const image_path=path.join(root,'tmp/20261002-204314-6f31/A13/requests/A13-request-'+req+'/response.png');
const version_id='A13-final-v002-'+name;
const v=s.view('A13',image_path,{tool:'view_image',reviewer:'invoice_producer',version_id,case_id:name,observation});
producerViews.push(v);
if(name==='symbol-color')s.iteration('A13',{type:'visual',version_id,parent_version:'A13-preview-v001-direction-A',case_id:name,completed:true,phase:'actual-image-reviewed',request_id:'A13-request-'+req,image_path,before_view_id:'A13-view-000001',after_view_id:v.id,changes:'Selected A: stroke32→40, rounded radius40→48, frame extents and64px offset unchanged.',comparison:'Original512 and actual32px final views show stronger window silhouette. Common negative center remains clearly open in color and black32; geometry direction unchanged.',unresolved_issues:[]});
else s.iteration('A13',{type:'baseline',version_id,parent_version:null,case_id:name,completed:true,phase:'actual-image-reviewed',request_id:'A13-request-'+req,image_path,after_view_id:v.id,observation,unresolved_issues:[]});
}
const qaViews=[];
for(const [name,file,observation] of [
['symbol-black','symbol-black-qa512-on-white-v001.png','Actual512 white QA plate viewed: solid pure black same overlapping-window geometry and open common negative space. Original PNG left unchanged.'],
['symbol-color','symbol-color-qa32-v001.png','Actual32px color thumbnail viewed and compared with selected preview32: thicker about2.5px strokes give steadier outline; layered windows and central opening remain recognizable.'],
['symbol-black','symbol-black-qa32-on-white-v001.png','Actual32px black thumbnail on white viewed: silhouette remains two offset windows, central negative space clear, not a closed black blob.']])qaViews.push(s.view('A13',path.join(__dirname,file),{tool:'view_image',reviewer:'invoice_producer',version_id:'A13-final-v002-'+name,case_id:name,purpose:'QA-only derived plate/thumbnail; final original unchanged',original_image_path:producerViews.find(v=>v.case_id===name).image_path,observation}));
const brand=read('brand-system-draft-v001.json');
const rootReview=JSON.parse(fs.readFileSync(path.join(root,'tmp/20261002-204314-6f31/A13/root-final-review-v001.json'),'utf8'));
const views=s.countsFor('A13').views;
brand.status='actual_final_visual_review_passed';
brand.icon.common_negative_space={axis_aligned_bounds:[200,200,312,312],nominal_bbox_size:112,guaranteed_interior_rectangle:[208,208,96,96],shape:'Intersection of two rounded frame interiors; common center open in actual512/32 views.',nominal_size_in32:7,guaranteed_core_size_in32:6};
brand.actual_rgba_audit={...qa.rgba_audit,exact_alpha_arrays_required_by_task:false,raw_array_identity_failure_preserved:true,geometry_pass_evidence:{identical_dsl_geometry_except_stroke_colors:true,both_alpha_bounds:[96,96,416,416],binary_alpha_ge128_identical:alpha.binary_alpha_ge128_identical,aa_alpha_difference_pixels:alpha.differing_alpha_pixel_count,max_aa_alpha_difference:alpha.maximum_alpha_delta,all_difference_pixels_antialiased_edges:alpha.all_differences_antialiased_edge_pixels},task_aa_allowance_assessment:'The task allows anti-aliased alpha. Both exact DSL geometries match; 154 edge pixels differ by alpha1 and the >=128 masks match. Black nontransparent RGB is exact0. Do not rewrite original false raw array-equality audit.',assessed_requirements_pass:qa.rgba_audit.black_nontransparent_nonzero_rgb_count===0&&alpha.maximum_alpha_delta===1&&alpha.all_differences_antialiased_edge_pixels&&alpha.binary_alpha_ge128_identical};
const colorDsl=fs.readFileSync(path.join(__dirname,'symbol-color-v002.snapshot'),'utf8');
const blackDsl=fs.readFileSync(path.join(__dirname,'symbol-black-v002.snapshot'),'utf8');
if(colorDsl.replace(/#133E49|#7966FF/g,'#000000')!==blackDsl)throw new Error('Color and black DSL geometry differ');
const candidates=[];
for(const entry of rootReview.images){
const v=views.find(v=>v.id===entry.existing_view_id);
const req=producerViews.find(v=>v.case_id===entry.case_id);
if(!v||v.reviewer!=='root'||v.sha256!==req.sha256)throw new Error('Missing true root final view');
const number={'symbol-color':'000003','symbol-black':'000004','brand-banner':'000005','launch-poster':'000006'}[entry.case_id];
const meta_path=path.join(root,'tmp/20261002-204314-6f31/A13/requests/A13-request-'+number+'/render-result.json');
const meta=JSON.parse(fs.readFileSync(meta_path,'utf8'));
candidates.push({stem:entry.case_id,version_id:entry.version_id,meta_path,png_sha256:req.sha256,dsl_sha256:crypto.createHash('sha256').update(fs.readFileSync(meta.dsl_path)).digest('hex'),root_actual_view_id:v.id,producer_actual_view_id:req.id,root_actual_viewed_at:v.viewed_at});
}
brand.final_candidates=candidates;brand.actual_qa_view_ids={producer:qaViews.map(v=>v.id),root:rootReview.qa_view_ids};
brand.final_small_size_refinement='40px stroke (2.5px at32) and48px corner radius confirmed by actual final color32/black32 views; center remains open.';
write('brand-system-reviewed-draft-v002.json',brand);
const rationale='方向A以两枚错位空心圆角框呈现信息层叠；方向B用六根切向条围成光圈。实际512与32像素预览中，A的层次和共用窗口更直接，B更像通用徽章，因此选A。将笔画由32增至40、圆角由40增至48，32像素轮廓更稳，中心负空间仍开放。彩色与黑版仅换颜色；横幅作横向识别，海报以居中大符号独立发布。';
if([...rationale].length>300)throw new Error('Rationale too long');
write('rationale-draft-v001.md',rationale+'\n');
write('production-handoff-v001.json',{task_id:'A13',run_id:'20261002-204314-6f31',all_production_writes_finished:true,candidates,brand_system:path.join(__dirname,'brand-system-reviewed-draft-v002.json'),rationale:path.join(__dirname,'rationale-draft-v001.md'),rationale_unicode_character_count:[...rationale].length,chronology:'Two real512 previews → original512/32 actual views → archived direction-selection-v001 → final same-A stroke refinement → real four final responses → actual whole/32 final reviews.',production_facts:['6 true render requests, all200; no service failure or retry.','2 genuinely different previews; same A selected before final code creation.','2 main icon components, noText/Image icon; applications use same symbol() DSL geometry.','1 complete actual visual refinement of selected icon stroke32→40 and radius40→48.','Black62420 nontransparent pixels allRGB0; alpha bounds same, exactalpha arrays false at154 AAedge pixels diff1, rawfailure kept.','All4 original final PNGs viewed by producer androot, icons32 andblackwhite QA actually viewed.'],reports_metrics_state_publishing_owned_by_root:true,unresolved_production_issues:[]});
console.log(JSON.stringify({candidates,brand_system:path.join(__dirname,'brand-system-reviewed-draft-v002.json'),rationale:path.join(__dirname,'rationale-draft-v001.md'),rationale_chars:[...rationale].length,all_production_writes_finished:true}));
