const fs=require('fs'),path=require('path');
const s=require('../../_suite/suite.cjs');
const facts=JSON.parse(fs.readFileSync(path.join(__dirname,'transform-facts-v001.json'),'utf8'));
const produced=JSON.parse(fs.readFileSync(path.join(__dirname,'../geometry-audit-v001.json'),'utf8'));
const dsl=fs.readFileSync(path.join(__dirname,'../transform-atlas-v001.snapshot'),'utf8');
const pixels=JSON.parse(fs.readFileSync(path.join(__dirname,'pixel-review-v001.json'),'utf8'));
const aa=JSON.parse(fs.readFileSync(path.join(__dirname,'T11-gold-AA-exception-v001.json'),'utf8'));
const maxDifference=(a,b)=>Math.max(...a.map((v,i)=>Math.abs(v-b[i])));
const matrices=produced.samples.map(sample=>{
 const independent=facts.transforms.find(t=>t.id===sample.id);
 const local=maxDifference(sample.matrix_column_major_4x4,independent.local_pivot_affine_4x4_column_major);
 const world=maxDifference(sample.global_placement_matrix_column_major_4x4,independent.world_affine_4x4_column_major);
 const corners=sample.rectangles.map((r,i)=>maxDifference(r.global_corners.flat(),independent.rectangles[i].world_corners.flat()));
 const dot=maxDifference(sample.dot.global_center,independent.dot.world_center);
 return {id:sample.id,local_matrix_max_difference:local,world_matrix_max_difference:world,
  rectangle_corner_max_differences:corners,dot_center_max_difference:dot,
  actual_DSL_matrix_literal_present:dsl.includes('matrix="'+sample.actual_dsl_matrix+'"'),
  matches:local<1e-6&&world<1e-6&&corners.every(v=>v<1e-6)&&dot<1e-6};
});
const subjectMatches=dsl.split(produced.subject_raw_dsl).length-1;
const view=s.view('A09','D:/workspaces/gpt-6.1-sol-ultra/tmp/20261002-204314-6f31/A09/requests/A09-request-000001/response.png',{
 tool:'view_image',reviewer:'graph_auditor',version_id:'A09-v001',
 observation:'实际查看1600×1200服务原图：12个300×250格按4×3整体居中且间32；编号/短名/刻度/四彩色形状图例完整，中心不随外框移动，T07/T08图形和黑点位置清晰有顺序差异，T10圆点随非等比缩放呈扁椭圆，T11/T12超120局部框仍未裁切。真实纯色分割有T11金角bbox左侧1.5359px边缘检测失败，已另用RGB混色20.38%覆盖/距理论角0.2869px确认AA例外并永久保留原失败记录。'
});
const report={generated_at:new Date().toISOString(),task_id:'A09',independent_matrix_corner_dot_checks:matrices,
  original_subject_DSL_repeated_count:subjectMatches,has_external_image_tag: /<Image\b/.test(dsl),
  all_independent_geometry_matches:matrices.every(m=>m.matches&&m.actual_DSL_matrix_literal_present)&&subjectMatches===12,
  preserved_raw_pixel_report:'pixel-review-v001.json',raw_pixel_all_checks_pass:pixels.all_checks_pass,
  AA_boundary_exception_file:'T11-gold-AA-exception-v001.json',AA_boundary_exception_confirmed:aa.antialias_exception_confirmed,
  tolerance_pixels:1.5,no_tolerance_increase:true,
  total_rectangles_checked:pixels.transforms.reduce((n,t)=>n+t.rectangles.length,0),total_corners_checked:pixels.transforms.reduce((n,t)=>n+t.rectangles.reduce((k,r)=>k+r.corners.length,0),0),
  AA_corner_exceptions:pixels.antialias_corner_exceptions,
  dot_center_max_error_px:Math.max(...pixels.transforms.map(t=>t.dot.center_error_px)),
  total_subject_bbox_max_error_px:Math.max(...pixels.transforms.flatMap(t=>Object.values(t.subject_bound_errors).map(Math.abs))),
  visual_view:view};
fs.writeFileSync(path.join(__dirname,'geometry-and-visual-review-v001.json'),JSON.stringify(report,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({all_independent_geometry_matches:report.all_independent_geometry_matches,subjectMatches,rectangles:report.total_rectangles_checked,corners:report.total_corners_checked,AA:pixels.antialias_corner_exceptions,dot_max:report.dot_center_max_error_px,bbox_max:report.total_subject_bbox_max_error_px,view_id:view.id},null,2));
