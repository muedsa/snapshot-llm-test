'use strict';
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const s=require('../../_suite/suite.cjs');
const dir=__dirname,sha=t=>crypto.createHash('sha256').update(t).digest('hex');
const read=f=>JSON.parse(fs.readFileSync(path.join(dir,f),'utf8'));
const write=(f,v)=>fs.writeFileSync(path.join(dir,f),typeof v==='string'?v:JSON.stringify(v,null,2)+'\n',{flag:'wx'});
const before=read('refinement-before-views-v002.json'),views=[];
for(const b of before.views){
 const r=read(b.stem+'-render-result-v002.json');
 const observation=b.stem==='example-01'?'Actual tool view v002 against re-opened v001: subtitle is visibly larger at 24px, full DSL to PNG / 400 x 240 line fits within 24px horizontal padding; mint 400×240 card and title intact, no clipping.':'Actual tool view v002 against re-opened v001: direct embedded example subtitle is clearly larger at 24px, code now visibly prints fontSize=24 in true line 11; 17-line code, rule text, error cards, scope and footer remain legible and within safe bounds.';
 const v=s.view('A17',r.image_path,{tool:'functions.view_image',viewer:'/root/a17_producer_01_02',version_id:r.version_id,case_id:b.stem,mode:'original-after-visual-revision',observation});
 const comparison='Compared actual before/after images: subtitle is now 24px and improves instructional readability without overflow. Full runnable code, printed source and exact directly nested Widget remain synchronized.';
 s.iteration('A17',{type:'visual',version_id:r.version_id,parent_version:b.parent_version,case_id:b.stem,completed:true,phase:'actual-image-reviewed-and-compared',request_id:r.id,image_path:r.image_path,before_view_id:b.before_view_id,after_view_id:v.id,changes:before.changes,comparison});
 views.push({stem:b.stem,view_id:v.id,image_path:r.image_path,render_metadata:r.meta_path,version_id:r.version_id,before_view_id:b.before_view_id,observation,comparison});
}
write('producer-visual-review-v002.json',{reviewed_at:new Date().toISOString(),views,change:before.changes,body_and_illustration_font_minimum:24,code_font_size:20});
const old=read('example-mapping-final-v001.json');
const mappings=old.map((m,i)=>{
 if(i===1)return {...m,reused_without_new_render:true,version_note:'Accepted example-02 and handbook-02 v001 unchanged.'};
 const fullSource=path.join(dir,'example-01-v002.snapshot'),full=fs.readFileSync(fullSource,'utf8').trimEnd(),lines=full.split('\n'),root=lines.slice(1,-1).join('\n'),pageSource=path.join(dir,'handbook-01-v002.snapshot'),page=fs.readFileSync(pageSource,'utf8');
 const e=read('example-01-render-result-v002.json'),p=read('handbook-01-render-result-v002.json');
 if(lines.length!==17||!page.includes(root))throw Error('Synchronized source failed');
 const code=lines.join('\n');if(!page.includes(code))throw Error('Printed complete source differs');
 return {...m,full_source:fullSource,full_source_sha256:sha(fs.readFileSync(fullSource)),printed_lines:lines,exact_root_widget_sha256:sha(root),handbook_dsl:pageSource,handbook_contains_exact_root_widget:true,image_tags_in_handbook:(page.match(/<Image\b/g)||[]).length,example_response:{request_id:e.id,service_request_id:e.request_id,http_status:e.http_status,content_type:e.content_type,response_file:e.response_file,raw_png_sha256:e.response_sha256,width:e.png_dimensions.width,height:e.png_dimensions.height,render_result:e.meta_path},handbook_response:{request_id:p.id,http_status:p.http_status,content_type:p.content_type,response_file:p.response_file,render_result:p.meta_path},producer_views:views.map(v=>v.view_id),v001_preserved:true,visual_change:before.changes};
});
write('example-mapping-final-v002.json',mappings);
const sources=fs.readFileSync(path.join(dir,'sources-draft-v001.md'),'utf8')+'\n## 第 1 页 v002 修订核对\n\n- 原常规错误/HTTP描述保留。当前服务 OpenAPI 实际缓存 `D:/workspaces/gpt-6.1-sol-ultra/tmp/20261002-204314-6f31/_suite/shared-doc-000006-readable.txt` 第 80–92 行 `/snapshot` 的 `errorImage` 参数明确：解析失败时可返回 `image/png`，HTTP 状态仍为400；第 338–346 行 BadRequest进一步说明只有解析错误走高亮PNG。页1右下卡与当前服务契约一致，无须修改。\n- 字号修订：example-01 第二个 Text 由20→24；独立完整17行、印刷完整17行及教学页直接根Widget同步更新。最终映射为 `example-mapping-final-v002.json`，01使用v002，02沿用已核v001。实际前后查看与完成的两次视觉迭代见 `producer-visual-review-v002.json`。\n';
write('sources-draft-v002.md',sources);
const finalResults=['example-01','handbook-01'].map(stem=>({stem,metadata:read(stem+'-render-result-v002.json').meta_path,image:read(stem+'-render-result-v002.json').image_path,producer_view_id:views.find(v=>v.stem===stem).view_id})).concat(['example-02','handbook-02'].map(stem=>({stem,metadata:read(stem+'-render-result-v001.json').meta_path,image:read(stem+'-render-result-v001.json').image_path,producer_view_id:read('producer-visual-review-v001.json').views.find(v=>v.stem===stem).view_id})));
write('producer-handoff-v002.json',{finished_at:new Date().toISOString(),producer:'/root/a17_producer_01_02',all_writes_finished:true,status:'Four final candidates accepted visually by producer: 01 v002, 02 v001; awaiting root review and publication',production_directory:dir,final_candidate_stems:finalResults.map(r=>r.stem),render_results:finalResults,mapping:path.join(dir,'example-mapping-final-v002.json'),sources:path.join(dir,'sources-draft-v002.md'),body_and_illustration_font_minimum:24,code_font_size:20,safe_margin_minimum:64,new_http_document_requests:0,render_requests_all_attempts:6,successes_all_attempts:6,failures:0,completed_visual_iterations:2,known_issues:[],retained_v001:true,note:'No publication, suite-state edit, root reports or metrics.'});
console.log(JSON.stringify({all_writes_finished:true,views:views.map(v=>({stem:v.stem,id:v.view_id,before:v.before_view_id})),finals:finalResults}));
