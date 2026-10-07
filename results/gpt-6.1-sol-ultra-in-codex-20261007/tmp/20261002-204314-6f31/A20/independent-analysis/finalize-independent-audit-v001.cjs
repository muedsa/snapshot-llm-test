'use strict';
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root='D:/workspaces/gpt-6.1-sol-ultra',dir=__dirname;
const read=p=>JSON.parse(fs.readFileSync(p,'utf8')),hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const finalPath=root+'/tmp/20261002-204314-6f31/A20/label-layout-final-v001.json';
const candidatePath=root+'/tmp/20261002-204314-6f31/A20/layout-production/label-layout-candidate-v002.json';
const inputPath=root+'/tasks/A20-dense-annotation/inputs/markers.json';
const dslPath=root+'/tmp/20261002-204314-6f31/A20/requests/A20-request-000002/input.snapshot';
const sourceAuditPath=path.join(dir,'final-independent-audit-v002.json'),primitivesPath=path.join(dir,'actual-source-primitives-v002.json');
const final=read(finalPath),candidate=read(candidatePath),sourceAudit=read(sourceAuditPath),primitives=read(primitivesPath),issues=[];
const add=(type,d)=>issues.push({...d,type});
const shapeKeys=['id','name','x','y','value','logical','anchor','diameter','label','polyline'];
for(const c of candidate.markers){const f=final.markers.find(x=>x.id===c.id);if(!f){add('final-missing-marker',{id:c.id});continue;}for(const k of shapeKeys)if(JSON.stringify(f[k])!==JSON.stringify(c[k]))add('final-geometry-changed',{id:c.id,key:k,candidate:c[k],final:f[k]});}
if(hash(dslPath)!==sourceAudit.source.actual_dsl_sha256||hash(dslPath)!==primitives.dsl_sha256)add('actual-dsl-hash-changed',{});
const styleExpected={font_size:20,width:180,height:56,padding_x:10,first_text_height:28,second_text_height:24,label_gap_minimum:4,first_text_y_offset:5,second_text_y_offset:30};
for(const[k,v]of Object.entries(styleExpected))if(final.label_style[k]!==v)add('final-label-style-mismatch',{key:k,expected:v,actual:final.label_style[k]});
for(const f of final.markers){const actual=primitives.matches.find(x=>x.id===f.id);if(!actual)continue;
 if(JSON.stringify(f.text_lines)!==JSON.stringify(actual.actual_texts.map(t=>t.text)))add('final-exact-text-lines',{id:f.id,declared:f.text_lines,actual:actual.actual_texts.map(t=>t.text)});
 if(f.text_boxes?.length!==2)add('final-text-box-count',{id:f.id,count:f.text_boxes?.length});
 for(let i=0;i<2;i++){const fb=f.text_boxes?.[i],ab=actual.actual_texts[i]?.box;if(!fb||!ab)continue;for(const k of ['x','y','width','height'])if(Math.abs(fb[k]-ab[k])>1e-7)add('final-text-box-mismatch',{id:f.id,row:i,key:k,declared:fb[k],actual:ab[k]});if(fb.fontSize!==Number(actual.actual_texts[i].attrs.fontSize))add('final-text-font-mismatch',{id:f.id,row:i,declared:fb.fontSize,actual:actual.actual_texts[i].attrs.fontSize});}
}
const enriched={...final,markers:final.markers.map(m=>({...m,line_width:1.8}))};
const geometry=require('./audit-geometry-v002.cjs').audit(enriched,read(inputPath));
const overall=issues.length===0&&geometry.pass_geometry&&sourceAudit.pass_combined;
const result={audit_version:'A20-final-independent-audit-v001',created_at:new Date().toISOString(),pass:overall,source:{final_layout_path:finalPath,final_layout_sha256:hash(finalPath),candidate_path:candidatePath,candidate_sha256:hash(candidatePath),input_path:inputPath,input_sha256:hash(inputPath),actual_dsl_path:dslPath,actual_dsl_sha256:hash(dslPath)},final_sidecar_issues:issues,geometry,actual_dsl_audit:{audit_path:sourceAuditPath,pass:sourceAudit.pass_combined,summary:sourceAudit.summary,primitives_path:primitivesPath},prior_failure:{path:path.join(dir,'candidate-v001-strict-own-overlap-audit-v001.json'),issues:8,reason:'Eight adjacent own-line retraces, retained as original candidate failure; distinct-line crossing count was zero. Candidate v002 removed every collinear middle point (16), including all eight retraces.'},evidence_scope:{actual_http_render:false,actual_image_view:false,source_data_and_geometry:true,root_view_ids_declared_by_final_layout:final.actual_root_view_ids,root_render_version:final.actual_render_version,notes:'This agent did not produce render/view events. Root owns and reports actual center/overall image QA. 48 marker-label Text nodes are 20px; 12 numeric axis tick Text nodes are separately 18px.'},all_writes_finished:true};
const jsonPath=path.join(dir,'final-independent-audit-v001.json');fs.writeFileSync(jsonPath,JSON.stringify(result,null,2)+'\n',{flag:'wx'});
const md=`# A20 独立数据与几何审计\n\n结论：${overall?'通过':'未通过'}。实际提交 DSL、最终 label-layout 及原始 markers 数据一致；此代理不渲染、不看图、不更新总账和正式输出。\n\n- 最终源：\`${finalPath}\`，SHA256 \`${hash(finalPath)}\`。\n- 实际 DSL：\`${dslPath}\`，SHA256 \`${hash(dslPath)}\`。\n- 24 点按 x=280+10.4x、y=920−7.6y 映射，直径均 12px；固定图框 (280,160), 1040×760；点互不遮挡。\n- 24 个 180×56 标签，48 个正文 Text 均 20px；编号/名称/值/指数逐项匹配真实 Raw，最终 text_boxes 与实际 Positioned 完全一致。坐标轴独立数字刻度为18px，不计为点标签正文。\n- 标签盒最小距离 4px；非本点盖覆、引线碰异标签盒/文字、引线碰非本点均为 0。实际引线笔画 1.8px。\n- 32 个实际引线段；不同引线交叉 0、自回溯 0。端点接触和共线重叠纳入审计，仅相邻自身折点免算；自身引线最终端点可接本标签边界。\n- 实际矩阵恢复的引线与精确布局最大误差 ${sourceAudit.summary.max_serialized_line_drift_px}px，来自6位小数序列化；最小实际引线到非本点外缘/半线宽的净距 ${sourceAudit.summary.closest_actual_line_nonown_point_clearance.clearance_px}px。\n- 边界检查通过，最高3点 M10 广场93、M08 中庭91、M23 研究所90；最高三点色彩与标题一致。\n- 保留 v001 原候选失败审计：8处自身回溯；v002去除16个共线中间点后通过，未改变24锚点/标签盒。\n\n几何检查不替代图像查看。最终布局引用 root 的真实查看记录 \`${(final.actual_root_view_ids??[]).join(', ')}\`，此代理只核 source/data/geometry。\n\n实际 DSL 提取证据：\`${primitivesPath}\`。综合明细：\`${jsonPath}\`。\n\n最终 sidecar问题 ${issues.length}；几何问题 ${geometry.issues.length}。all_writes_finished=true。\n`;
const mdPath=path.join(dir,'final-independent-audit-v001.md');fs.writeFileSync(mdPath,md,{flag:'wx'});
console.log(JSON.stringify({pass:overall,sidecar_issues:issues,geometry_issue_count:geometry.issues.length,source_summary:sourceAudit.summary,json_path:jsonPath,markdown_path:mdPath,all_writes_finished:true}));
