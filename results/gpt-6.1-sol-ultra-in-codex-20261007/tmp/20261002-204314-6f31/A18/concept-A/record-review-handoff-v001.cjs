const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),s=require('../../_suite/suite.cjs');
const read=n=>JSON.parse(fs.readFileSync(path.join(__dirname,n),'utf8')),write=(n,d)=>fs.writeFileSync(path.join(__dirname,n),d,{flag:'wx'});
const r=read('render-v001.json'),audit=read('story-audit-draft-v001.json');
const originalObservation='实际打开1600×1000原服务预览：仅总标题和3幕名，三幕各15个相同36圆（蓝橙灰各5）完整可见。第一幕3层疏密距离、5条中性箭头阶梯朝一个中央深色节点，另两同尺寸节点闲置；第二幕15圆呈紧3×5队列，三条队列出口汇同中心，圆之间仍有缝隙；第三幕3簇每簇5个，箭头独立到各处理节点，每簇有蓝橙灰。没有线掩盖圆、警告字或单位缩小。';
const v=s.view('A18',r.image_path,{tool:'view_image',viewer:'a18_concept_A_producer',version_id:r.version_id,case_id:'concept-A',observation:originalObservation});
const thumb=s.view('A18',path.join(__dirname,'concept-A-thumbnail-v001.png'),{tool:'view_image',viewer:'a18_concept_A_producer',version_id:r.version_id,case_id:'concept-A',view_kind:'400px_thumbnail',observation:'实际打开400×250缩略：第一幕斜向放射/汇流与两个闲节点可辨；第二幕15个9px缩略圆的紧矩形团明显比前幕密集，仍辨3×5；第三幕三个节点各围五圆的均分结构可辨，不依赖颜色说明，三幕名称读得出。'});
s.iteration('A18',{type:'alternative',version_id:r.version_id,parent_version:null,case_id:'concept-A',completed:true,after_view_id:v.id,additional_view_ids:[thumb.id],image_path:r.image_path,observation:originalObservation,purpose:'真实构图A探索预览，暂未被root选为最终方案。'});
write('producer-view-records-v001.json',JSON.stringify([v,thumb],null,2)+'\n');
const cacheRoot=path.resolve(__dirname,'../../_suite');
const documents=[
 {url:'https://open-snapshot.muedsa.com/ai-guide.md',request_id:'shared-doc-000001',cache:'shared-doc-000001-response.txt',reading:'已在同一代理A17阶段完整实际读，A18复用服务契约与PNG真实性方法。'},
 {url:'https://snapshot.muedsa.com/reference/parser-tags/',request_id:'shared-doc-000004',cache:'shared-doc-000004-readable.txt',reading:'已在同一代理A17阶段完整实际读，A18复用Container形状CIRCLE、Stack/Positioned和Transform16列主序语法。'},
 {url:'https://snapshot.muedsa.com/guides/layout/',request_id:'shared-doc-000005',cache:'shared-doc-000005-readable.txt',reading:'本A18生产再次完整实际读，应用根有界1600×1000、Positioned坐标及绘制裁剪区分。'},
 {url:'https://open-snapshot.muedsa.com/fonts',request_id:'shared-fonts-000001',cache:'shared-fonts-000001-readable.txt',reading:'同代理A17完整实际读的成功fonts缓存，A18复用Inter/Noto Sans CJK SC。'}
].map(d=>({...d,absolute_cache_path:path.join(cacheRoot,d.cache),cache_SHA256:crypto.createHash('sha256').update(fs.readFileSync(path.join(cacheRoot,d.cache))).digest('hex'),new_HTTP_request:false}));
write('source-use-v001.json',JSON.stringify({task_id:'A18',concept:'A',read_task_files:['TASK.md','AGENTS.md','task.json','run-config.json'],pure_helper_read:path.join(cacheRoot,'dsl-README.md'),documents,new_document_HTTP_requests:0,new_font_HTTP_requests:0},null,2)+'\n');
const rationale='首幕三层距离和五条箭头阶梯朝同一中心汇流，两节点闲置。中幕同15圆压为仅4px间隙的三行队列，队尾挤向同一入口，未靠缩小或遮挡制造过载。末幕五圆一组，十五条独立箭头分到三节点；分组距离和连接关系比颜色更先被读到。400px缩略仍能辨出放射汇流、紧矩形团和三路均分。';
if([...rationale].length>300)throw Error('Rationale too long');write('rationale-draft-v001.md',rationale+'\n');
const summary={task_id:'A18',concept:'A',version_id:r.version_id,render_meta_path:r.meta_path,png_path:path.join(__dirname,'concept-A-v001.png'),dsl_path:path.join(__dirname,'concept-A-v001.snapshot'),thumbnail:path.join(__dirname,'concept-A-thumbnail-v001.png'),actual_views:[v.id,thumb.id],status:'preview_reviewed_not_selected',HTTP_render_requests:1,render_successes:1,render_failures:0,local_build_validation_failures:1,completed_visual_iterations:0,alternative_previews:1,geometry_checks:audit.geometry_checks,all_geometry_lines_include_heads_and_transition:true,min_global_line_edge_clearance:audit.global_min_line_clearance,min_unit_node_clearance:audit.global_min_node_clearance,original_service_bytes_preserved:true,no_Image:true,all_writing_completed_at:new Date().toISOString(),no_official_outputs_published:true};
write('handoff-v001.json',JSON.stringify(summary,null,2)+'\n');
let md='# A18 构图A交接\n\n全部预览生产写入已结束；等待root在两个实际候选中选择后再完善，未改共享状态/正式报告/指标或发布最终。\n\n';
md+=`真实${r.version_id}，200/image/png，1600×1000；render metadata ${r.meta_path}。便捷原字节PNG与DSL同名concept-A-v001，SHA已在thumbnail-provenance-v001.json记录。实际原图view ${v.id}，400×250缩略view ${thumb.id}。\n\n`;
md+='story-audit-draft-v001.json含每幕稳定ID/颜色/36px圆中心/bbox/receiver、3节点64×64bbox、所有实际箭头三线段及线宽（含2幕间transition）。本地初稿第三幕邻组圆距离不足，几何校验先于HTTP发现；local-geometry-failure-v001.json和原builder均保留。修复后各圆不重叠、线实际不穿圆（不依赖绘制层遮盖）、圆不交节点，第三幕每node5圆且至少2色。\n\n';
md+=`1次真实render成功，0服务失败；2次实际看图，1个alternative预览，0完整视觉迭代。全局线边到圆边最小间距${audit.global_min_line_clearance.toFixed(3)}px。未知token/费用null。复用已有真读官方缓存，无新文档HTTP。\n`;
write('handoff-v001.md',md);console.log(JSON.stringify({writing_done:true,view_ids:[v.id,thumb.id],min_line_clearance:audit.global_min_line_clearance,minimum_circle_distances:audit.geometry_checks.map(c=>({act:c.act_id,min:c.minimum_circle_center_distance})),meta:r.meta_path}));
