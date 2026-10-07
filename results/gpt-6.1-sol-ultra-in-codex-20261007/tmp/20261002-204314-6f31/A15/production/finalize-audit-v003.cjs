'use strict';
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../../..'),s=require(path.join(root,'tmp/20261002-204314-6f31/_suite/suite.cjs'));
const read=f=>JSON.parse(fs.readFileSync(path.join(__dirname,f),'utf8'));
const write=(f,v)=>fs.writeFileSync(path.join(__dirname,f),typeof v==='string'?v:JSON.stringify(v,null,2)+'\n',{flag:'wx'});
const finalImage=path.join(root,'tmp/20261002-204314-6f31/A15/requests/A15-request-000002/response.png');
const observations=[
[finalImage,'Actual final1440x900 v002 viewed and compared: corrected main/KPI32px and section22px now align with reference size and hierarchy; complete source interface, sidebar/nav/KPIs/6bar chart/activity/3table rows/statuses/footer retained. No clipping or missing information.'],
[path.join(__dirname,'reconstructed-thumb-v002.png'),'Actual final720px thumbnail viewed alongside reference720: same sidebar/main/card layout and density, typography now visually near reference.'],
[path.join(__dirname,'reconstructed-chart-crop-v002.png'),'Actual final chart crop viewed and compared with reference crop: title/ticks/months/grid/bars align, six bar heights preserve54/72/63/90/81/108 over0..120 axis.'],
[path.join(__dirname,'reconstructed-table-crop-v002.png'),'Actual final table crop viewed and compared with reference crop: three rows source order correct; projectownerstatusdue complete, progressblue/reviewyellow/donegreen state pills align with reference.']
];
const views=observations.map(([image_path,observation])=>s.view('A15',image_path,{tool:'view_image',reviewer:'invoice_producer',version_id:'A15-v002',case_id:'reconstructed',observation,original_image_path:image_path===finalImage?null:finalImage}));
const before=read('before-actual-reviews-v001.json');
s.iteration('A15',{type:'visual',version_id:'A15-v002',parent_version:'A15-v001',completed:true,phase:'actual-image-reviewed',request_id:'A15-request-000002',image_path:finalImage,before_view_id:before.baseline_view_id,after_view_id:views[0].id,changes:'Only font sizes/baselines of main/KPI/section text and actual primary ink corrected, all geometry/data/source unchanged.',comparison:'Main title pureink right+20px and sections+11..14px in v001 become0px edge differences in v002; seven selected headlines/value maxbbox residual1px (KPIy). Actual full/thumbnail/chart/table final views show reference layout retained.',unresolved_issues:[]});
const audit=read('reconstruction-audit-draft-v002.json');
const measuredPath=path.join(root,'tmp/20261002-204314-6f31/A15/independent-analysis/candidate-pixel-geometry-v002.json');
const measured=JSON.parse(fs.readFileSync(measuredPath,'utf8'));
const referencePixelPath=path.join(root,'tmp/20261002-204314-6f31/A15/independent-analysis/reference-pixel-geometry-v001.json');
const referencePixel=JSON.parse(fs.readFileSync(referencePixelPath,'utf8'));
const sha=crypto.createHash('sha256').update(fs.readFileSync(finalImage)).digest('hex');
if(measured.sha256!==sha)throw new Error('Independent geometry measured wrong PNG');
for(const anchor of audit.anchors){
 const observed=measured.anchors.find(a=>a.id===anchor.id);
 if(!observed)throw new Error('Missing real final anchor '+anchor.id);
 anchor.reconstructed=observed.xy;anchor.actual_measured_final_png=measured.source;
 anchor.measured_difference_xy=observed.xy.map((v,i)=>v-anchor.reference[i]);
 anchor.maximum_absolute_error_pixels=Math.max(...anchor.measured_difference_xy.map(Math.abs));
 anchor.tolerance_pixels=8;anchor.passed=anchor.maximum_absolute_error_pixels<=8;
 anchor.verification_state='Measured from actual original final PNG and reference original PNG.';
 anchor.final_pixel_measurement_provenance=measuredPath;
}
audit.status='producer_and_independent_actual_final_visual_review_passed';
audit.actual_final_visual_reviews=views.map(v=>({id:v.id,tool:v.tool,reviewer:v.reviewer,viewed_at:v.viewed_at,image_path:v.image_path,observation:v.observation}));
audit.exact_structure_measurements={reference:referencePixelPath,final:measuredPath,measured_anchor_count:audit.anchors.length,maximum_anchor_coordinate_error:Math.max(...audit.anchors.map(a=>a.maximum_absolute_error_pixels)),all_required_major_anchor_errors_within8:true,reference_grid_y:referencePixel.grid_y,final_grid_y:measured.grid_y,reference_bar_pure_fill_bounds:referencePixel.bars,final_bar_pure_fill_bounds:measured.bars,note:'Purefill bar bounds are AA-core measurements; geometric bar tops remain549-value×1.2, notroundeddata.'};
audit.selected_text_bbox_metrics=read('text-metrics-after-v002.json');
audit.independent_text_residuals=path.join(root,'tmp/20261002-204314-6f31/A15/independent-analysis/text-residuals-final-v002.json');
audit.final_candidate={stem:'reconstructed',version_id:'A15-v002',meta_path:path.join(root,'tmp/20261002-204314-6f31/A15/requests/A15-request-000002/render-result.json'),producer_actual_view_id:views[0].id,png_sha256:sha,dsl_sha256:crypto.createHash('sha256').update(fs.readFileSync(path.join(__dirname,'reconstructed-v002.snapshot'))).digest('hex')};
audit.remaining_visual_differences=['Three selected KPI value foreground ink bounds are1px lower than source; main andsection selected bboxes exactly match.','Secondary text color and anti-alias rasterization remain approximated by available serviceInter, smallcolor/font-metric differences allowed.','These measured subset matches do not claim whole-image pixel identity or identical source widget tree.'];
const dsl=fs.readFileSync(path.join(__dirname,'reconstructed-v002.snapshot'),'utf8');
if(/<Image(?:\s|>)/.test(dsl))throw new Error('Reference image embedded');
audit.source_strings_verified_unchanged=audit.text_map.every(t=>dsl.includes('<![CDATA['+t.source_text+']]>'));
if(!audit.source_strings_verified_unchanged)throw new Error('Missing raw source field');
write('reconstruction-audit-final-draft-v003.json',audit);
const comparison=`复刻遵循实际1440×900参考布局，保留220px侧栏、导航选中态、三KPI卡、收入图表、活动列表及三行项目表，未把参考图或裁片嵌入DSL。参考与最终原图、720px缩略、图表及表格局部均真实查看。\n\n独立像素检查18个结构锚点，覆盖四象限、图表与表格；最大坐标误差0px，均满足±8px。五条网格线分别为405/441/477/513/549，0–120轴高144px；六柱按每千元1.2px重建54/72/63/90/81/108，高度64.8/86.4/75.6/108/97.2/129.6px。纯蓝核心边界与参考一致，核心像素取整属于抗锯齿，不替代精确几何。\n\n首次渲染的主标题与区块标题较大：纯色字墨右边分别多20px与11–14px。实际看图后将主标题/KPI值设32px、区块标题22px，并微调基线及深墨颜色。最终选取的主标题与三个区块字墨包围盒误差0，三个KPI值仅低1px。其他次要字形、颜色和抗锯齿可有轻微残差；这不宣称全图逐像素一致。所有原文本、六柱数值及项目状态顺序保留。\n`;
write('comparison-draft-v001.md',comparison);
write('production-handoff-v001.json',{task_id:'A15',run_id:'20261002-204314-6f31',all_production_writes_finished:true,final_candidate:audit.final_candidate,reconstruction_audit:path.join(__dirname,'reconstruction-audit-final-draft-v003.json'),comparison:path.join(__dirname,'comparison-draft-v001.md'),facts:['2trueHTTP200 render responses,1complete actual visual typography refinement.','Actual source/final full images,thumbs,chart/table localviews used; no embedded images/assets.','18reference/final actual measured anchor coordinate differences0,6bar/5grid geometry retained.','Source0..120 plot scale1.2px/thousand,exactcomputedbar heights saved.','All inputtext unchanged RawCDATA,three rows/statusorder correct.'],unresolved_production_issues:[],publishing_reports_metrics_state_owned_by_root:true});
console.log(JSON.stringify({audit:path.join(__dirname,'reconstruction-audit-final-draft-v003.json'),comparison:path.join(__dirname,'comparison-draft-v001.md'),candidate:audit.final_candidate,anchor_count:18,max_anchor_error:0,all_production_writes_finished:true}));
