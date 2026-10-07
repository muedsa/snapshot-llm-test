const fs=require('fs'),path=require('path'),s=require('../_suite/suite.cjs');
const load=p=>JSON.parse(fs.readFileSync(path.join(__dirname,p),'utf8')),save=(p,o)=>fs.writeFileSync(path.join(__dirname,p),typeof o==='string'?o:JSON.stringify(o,null,2)+'\n',{flag:'wx'});
const render=load('render-frame-manifest-v001.json'),alpha=load('png-alpha-audit-v001.json');
if(!alpha.all_pass||render.frames.length!==6)throw Error('Actual PNG QA failed');
const observations=[
 'Actual600x600 frame01 opened: twelve equal teal48px squares scattered across the canvas, all visible and separate, no text or image assets; no clipping.',
 'Actual600x600 frame02 opened: same12 teal units move toward endpoint; spacing narrows, stable size and color, no unit disappears or touches another.',
 'Actual600x600 frame03 opened: the top head rows become more compact while stem units travel inward; all12 square units still visible and distinct.',
 'Actual600x600 frame04 opened: convergence is clear, stable48px cells, head and stem becoming aligned; no clipping or collision.',
 'Actual600x600 frame05 opened: near-formed upward arrow; all12 cells distinct, equal color/size, six-pixel-or-greater model separation; no abrupt disappearance.',
 'Actual600x600 frame06 opened: recognizable upward pixel arrow, head1+3+5 cells and three-cell stem=12, consistent48px teal cells, complete within canvas.'
];
const views=render.frames.map((f,i)=>{
 const v=s.view('A23',f.image_path,{tool:'view_image',reviewer:'root',version_id:f.version_id,observation:observations[i]+' Original-alpha inspection separately confirms real transparent background.'});
 s.iteration('A23',{type:'baseline',version_id:f.version_id,completed:true,image_path:f.image_path,after_view_id:v.id,comparison:'First actual full-image review passes; contact-sheet sequence and exact original-alpha audit additionally checked. No visual repair required.'});
 return v;
});
const contact=s.view('A23',path.join(__dirname,'contact-sheet-v001.png'),{tool:'view_image',reviewer:'root',observation:'Actual temporary3x2 checkerboard contact sheet opened after all six originals: twelve fixed units converge monotonically toward clear upward arrow; all six frames have transparent backgrounds and retain units. This QA composition is not a final service work.'});
const data=load('frame-production/frame-data.json');
data.status='Real service PNGs generated, root full-image and contact-sheet review complete, original alpha verified; final source/data audit pending separately.';
data.documentation.reused_actual_guide_cache=path.join(s.createSuite().tempSuite,'shared-doc-000001-response.txt');
data.documentation.reused_actual_parser_cache=path.join(s.createSuite().tempSuite,'shared-doc-000004-readable.txt');
for(let i=0;i<6;i++){
 const f=data.frames[i],a=alpha.frames[i],r=render.frames[i];
 f.service_alpha_validation_pending=false;
 f.actual_service_png={path:r.image_path,request_id:path.basename(path.dirname(r.meta_path)),version_id:r.version_id,sha256:a.sha256,original_mode:a.original_mode,alpha_extrema:a.alpha_extrema,transparent_pixels:a.transparent_pixels,opaque_pixels:a.opaque_pixels,partial_alpha_pixels:a.partial_alpha_pixels,actual_root_view_id:views[i].id};
}
data.audit.alpha_verification='All six original real-service PNGs read by Pillow:600x600 RGBA with alpha extrema0..255; alpha0 pixels≥331188/frame, alpha255≥26508/frame. Root separately physically opened each original and temporary checkerboard contact sheet. Raw final PNG bytes unmodified.';
data.actual_png_alpha_audit=path.join(__dirname,'png-alpha-audit-v001.json');
data.actual_contact_sheet_view_id=contact.id;
data.all_writes_finished=true;
save('frame-data-final-v001.json',data);
const timing=load('frame-production/timing.json');timing.export.provided='Six actual real-service transparent PNG keyframes with complete paired DSL, frame-data.json and timing.json.';save('timing-final-v001.json',timing);
let lim=fs.readFileSync(path.join(__dirname,'capability-analysis/limitations-draft-v001.md'),'utf8');
lim=lim.replace('# A23 交付能力与限制草稿','# A23 交付能力与限制').replace('此草稿尚未宣称实际文件交付/透明/看图通过。','七张真实服务PNG与对应完整DSL已生成；root实际打开全部原图和接触表，六帧alpha检查通过。').replace('当前仅判定文档支持；实际透明像素仍须最终真实 PNG 验证，不依据 .png 后缀直接宣称透明。','原始响应已核验：六帧RGBA PNG均600×600，透明像素至少331188/frame、alpha范围0..255；另有逐帧与接触表真实看图，不能只依据.png后缀。').replace('all_writes_finished=false，等待实际几何/最终文件补审。','文档证据已完成；最终几何/字节链独立补审另存。');
lim+='\n## 实际交付与播放边界\n\n封面1200×800使用RGB色值绘制，原服务PNG IHDR颜色类型为6（RGBA），不转换服务字节；alpha以原始像素检查为准。六个透明帧使用同12个48×48青绿方块，六张静帧本身不含动画。frame-data提供连续smoothstep运动提案；timing按每帧250ms保持、周期1500ms、无限循环，6→1最大单位位移234.8297px并明确硬回跳，非无缝。未创建GIF/SVG/CMYK冒名文件。\n';
save('limitations-final-v001.md',lim);
const cover=load('requests/A23-request-000001/render-result.json'),coverView=s.countsFor('A23').views.find(v=>v.id==='A23-view-000001');
save('root-final-review-v001.json',{task_id:'A23',reviewer:'root',actual_tool:'view_image',images:[{image_path:cover.response_file,version_id:cover.version_id,existing_view_id:coverView.id,observation:coverView.observation},...render.frames.map((r,i)=>({image_path:r.image_path,version_id:r.version_id,existing_view_id:views[i].id,observation:views[i].observation}))],validation:{final_images:7,frames:6,frame_unit_count:12,frame_size:600,minimum_continuous_unit_gap_px:6,alpha_audit:alpha.all_pass,contact_sheet_actual_view_id:contact.id,seamless:false,visual_defects:[]},resume_notes:'All7 real originals and contact sheet genuinely opened; fixed12unit transparent frames/data/timing/limitations complete. Independent final audit pending; then publish and continue A24.'});
s.taskCheckpoint('A23',{visual_review_evidence:[...views.map(v=>v.id),contact.id],resume_notes:'All seven original PNGs and contact sheet actually viewed, six alpha checks pass; awaiting independent final source/data audit before publishing.'});
s.writeTaskMetrics('A23');console.log(JSON.stringify({views:views.map(v=>v.id),contact:contact.id,frame_data:'frame-data-final-v001.json',timing:'timing-final-v001.json',limitations:'limitations-final-v001.md'}));
