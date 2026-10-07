const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),s=require('../../_suite/suite.cjs');
const hash=x=>crypto.createHash('sha256').update(x).digest('hex'),write=(n,d)=>fs.writeFileSync(path.join(__dirname,n),d,{flag:'wx'}),read=n=>JSON.parse(fs.readFileSync(path.join(__dirname,n),'utf8'));
const r=read('handbook-03-render-v003.json'),observation='实际再次打开1200×1600 handbook03 v003：源行范围完整且准确显示5–8、10–17、20–21、23–24；16已印源行逐一对应，无第9行；24px alpha标签、原构件、文字/色块/底部说明完整，范围修正没有引入裁切。';
const v=s.view('A17',r.image_path,{tool:'view_image',viewer:'a17_producer_03_04',case_id:'handbook-03',version_id:r.version_id,observation});
s.iteration('A17',{type:'visual',version_id:r.version_id,parent_version:r.parent_version,case_id:'handbook-03',completed:true,before_view_id:r.before_view_id,after_view_id:v.id,image_path:r.image_path,changes:'将print范围5–17更正为5–8、10–17，明确第9行间隔器省略；源码/16已印源行/示例不改。',comparison:observation,passes_visual_check:true});write('page03-range-view-record-v003.json',JSON.stringify(v,null,2)+'\n');
const finalSpecs=[['handbook-03','v003',1200,1600],['handbook-04','v003',1200,1600],['example-03','v002',400,240],['example-04','v002',400,240]];
const views=s.countsFor('A17').views.filter(v=>v.viewer==='a17_producer_03_04');
const finals=finalSpecs.map(([stem,version,width,height])=>{
 const meta=read(stem+'-render-'+version+'.json'),service=JSON.parse(fs.readFileSync(meta.meta_path,'utf8'));
 const matching=views.filter(v=>v.version_id===meta.version_id&&v.image_path===meta.image_path);
 if(!meta.ok||meta.png_dimensions.width!==width||meta.png_dimensions.height!==height||!matching.length)throw Error('Final lacking actual service/view evidence '+stem);
 return {stem,title:stem.startsWith('handbook')?'教学第'+stem.slice(-2)+'页':'第'+stem.slice(-2)+'页真实独立示例',version_id:meta.version_id,case_id:stem,independent_case:false,meta_path:meta.meta_path,image_path:meta.image_path,dsl_path:service.dsl_path,width,height,request_id:service.id,http_status:service.http_status,content_type:service.content_type,response_request_id:service.request_id,server_timing:service.server_timing,response_sha256:service.response_sha256,producer_actual_view_ids:matching.map(v=>v.id)};
});
const drafts=read('examples-draft-v002.json');
for(const e of drafts){const f=finals.find(f=>f.stem===e.stem),page=finals.find(f=>f.stem==='handbook-'+String(e.page).padStart(2,'0'));const source=fs.readFileSync(f.dsl_path,'utf8'),prefix='<Snapshot type="png" background="#FFFFFF">\n',suffix='\n</Snapshot>\n',widget=source.slice(prefix.length,-suffix.length),pageSource=fs.readFileSync(page.dsl_path,'utf8');
 if(hash(widget)!==e.root_widget_sha256||!pageSource.includes(widget))throw Error('Widget mismatch');
 const allLines=source.trimEnd().split('\n');for(const line of e.printed_source_lines)if(allLines[line.line-1]!==line.source)throw Error('Print source mismatch');
 const fontSizes=[...source.matchAll(/fontSize="([\d.]+)"/g)].map(m=>Number(m[1]));if(Math.min(...fontSizes)<24)throw Error('Figure font below24');
 e.complete_dsl_final_relative=e.stem+'.snapshot';e.independent_png_final_relative=e.stem+'.png';e.handbook_final_relative='handbook-'+String(e.page).padStart(2,'0')+'.png';e.purpose=e.page===3?'Raw保留空白、CDATA字面尖括号/与号、嵌Text行内样式、尾部alpha真实色块':'相同条纹/前景下背景滤镜与子树滤镜的高斯模糊输入对照';e.printing_policy='每行先印实际原源码行号；仅移除行首DSL缩进，Raw内容内的字面空格完整保留。';e.actual_response={request_id:f.request_id,http_status:f.http_status,content_type:f.content_type,png_dimensions:{width:f.width,height:f.height},response_sha256:f.response_sha256,response_request_id:f.response_request_id,server_timing:f.server_timing,meta_path:f.meta_path,original_png_path:f.image_path};e.actual_view_ids=f.producer_actual_view_ids;e.final_handbook_meta_path=page.meta_path;e.full_source=source;e.exact_widget_direct_embedding_verified=true;e.no_Image=true;e.all_figure_text_font_min=Math.min(...fontSizes);
}
write('examples-final-draft-v001.json',JSON.stringify(drafts,null,2)+'\n');write('final-candidates-v001.json',JSON.stringify(finals,null,2)+'\n');
const runBase=path.resolve(__dirname,'../..'),suite=path.join(runBase,'_suite');
const docs=[
 ['guide','https://open-snapshot.muedsa.com/ai-guide.md',path.join(suite,'shared-doc-000001-response.txt'),'shared-doc-000001'],
 ['parser','https://snapshot.muedsa.com/guides/parser/',path.join(suite,'shared-doc-000003-readable.txt'),'shared-doc-000003'],
 ['parser-tags','https://snapshot.muedsa.com/reference/parser-tags/',path.join(suite,'shared-doc-000004-readable.txt'),'shared-doc-000004'],
 ['fonts','https://open-snapshot.muedsa.com/fonts',path.join(suite,'shared-fonts-000001-readable.txt'),'shared-fonts-000001'],
 ['text','https://snapshot.muedsa.com/widgets/text/text/',path.join(runBase,'A11/requests/A11-request-000001/readable.txt'),'A11-request-000001'],
 ['rich-text','https://snapshot.muedsa.com/widgets/text/rich-text/',path.join(runBase,'A11/requests/A11-request-000002/readable.txt'),'A11-request-000002'],
 ['backdrop-filter','https://snapshot.muedsa.com/widgets/painting/backdrop-filter/',path.join(suite,'requests/shared-request-000001/readable.txt'),'shared-request-000001'],
 ['image-filtered','https://snapshot.muedsa.com/widgets/painting/image-filtered/',path.join(runBase,'A10/requests/A10-request-000002/readable.txt'),'A10-request-000002']
].map(([name,url,cache_path,original_request_id])=>({name,url,cache_path,original_request_id,cache_sha256:hash(fs.readFileSync(cache_path)),actually_read_in_this_production:true,reused_cached_request:true,new_http_request:false}));
const claims=[
 {id:'03-raw',page:3,claim:'普通Text原始文本trim；Raw保留首尾空白/换行，只能在最外层Text行内树中。',docs:['parser','parser-tags'],example:'example-03.snapshot',source_lines:[5,6,7,8]},
 {id:'03-cdata',page:3,claim:'CDATA用于字面< >；Parser不做HTML实体解码，&lt;原样保留。',docs:['parser'],example:'example-03.snapshot',source_lines:[7],handbook_illustration:'第3页底部实际印出的& lt;实体样式字符，未实体解码。'},
 {id:'03-rich',page:3,claim:'Parser嵌套Text是行内Span，并继承未覆盖样式；只最外层Text控制段落。',docs:['parser-tags','text','rich-text'],example:'example-03.snapshot',source_lines:[10,11,12,13,14,15,16,17],distinction:'text/rich-text官方页介绍Kotlin接口；类DOM Parser的支持与属性以parser-tags的Text段落为直接依据，不声称存在RichText标签。'},
 {id:'03-alpha',page:3,claim:'#RRGGBBAA采用尾部alpha：FF不透明；80为128/255，当前Parser不能沿用旧AARRGGBB。',docs:['guide','parser-tags'],example:'example-03.snapshot',source_lines:[20,21,23,24],evidence:'同题真实PNG红块采样；见final-pixel-check-v001.json。'},
 {id:'03-fonts',page:3,claim:'Inter、DejaVu Sans Mono、Noto Sans CJK SC是本服务真实字体列表中的字体。',docs:['fonts','guide','text'],example:'example-03.snapshot',source_lines:[5,10]},
 {id:'04-inputs',page:4,claim:'BackdropFilter读取背后已绘制内容，前景子Widget不属于背景过滤输入；ImageFiltered以自身子树为输入。',docs:['backdrop-filter','image-filtered','parser-tags'],example:'example-04.snapshot',source_lines:[114,122,137,197],evidence:'独立实际图左前景SHARP/深条清晰，右相同文本/条同blur3。'},
 {id:'04-scope',page:4,claim:'Parser两滤镜标签仅高斯模糊；用sigmaX/Y有限非负值，外层ClipRect限制背景读取/模糊显示区。',docs:['parser-tags','backdrop-filter','image-filtered'],example:'example-04.snapshot',source_lines:[113,114,136,137]},
 {id:'04-paint-order',page:4,claim:'先画条纹后画BackdropFilter，滤镜才能读取已有背景；Clip在外层，文字前景仍清晰。',docs:['backdrop-filter','parser-tags'],example:'example-04.snapshot',source_lines:[17,65,113,114],evidence:'独立完整源码里两个180×176背景先于后面的滤镜层，遵循已验证A10构造。'},
 {id:'04-status',page:4,claim:'查看前先查状态/Content-Type和PNG签名；失败响应保留，不能JSON冒充PNG。',docs:['guide'],example:'example-04.snapshot',evidence:'所有生产render-result.json有真实200/image/png/400×240或1200×1600，原响应未后处理。'},
 {id:'04-reproduce',page:4,claim:'以同名完整snapshot和原PNG交付，记录固定字体、响应头/requestId及真实查看修改比较以便复现。',docs:['guide','text'],example:'example-04.snapshot',evidence:'服务调用输入/response-headers/render-result及views/iterations；交付规范是本任务工作流要求，固定字体建议来自Text官方页。'}
];
write('sources-final-draft-v001.json',JSON.stringify({owner:'a17_producer_03_04',recorded_at:new Date().toISOString(),new_document_HTTP_requests:0,new_fonts_HTTP_requests:0,docs,claims},null,2)+'\n');
let md='# 第3、4页实际阅读来源与技术映射\n\n以下均在本次生产实际读取已有成功请求的缓存；复用不计新HTTP。完整原请求、响应和URL保持原任务归属。\n\n';
for(const d of docs)md+=`- ${d.name}: [官方页](${d.url})；原请求 ${d.original_request_id}；实际读取缓存 ${d.cache_path}；SHA-256 ${d.cache_sha256}。\n`;
md+='\n每条关键结论：\n\n';for(const c of claims)md+=`- ${c.id}（第${c.page}页，${c.example}${c.source_lines?'，真实源行 '+c.source_lines.join('、'):''}）：${c.claim} 来源 ${c.docs.join('、')}。${c.distinction??''}${c.evidence?' 验证：'+c.evidence:''}\n`;
md+='\n代码印刷16个真实源行/页；源码行号在页内显示，跳过的行明确省略。完整源与省略行列表在 examples-final-draft-v001.json。所有插图为同一完整根Widget直接嵌入，未使用Image、资产或最终图后处理。\n';write('sources-final-draft-v001.md',md);
const ownVersions=finalSpecs.flatMap(([stem])=>s.countsFor('A17').versions.filter(v=>v.case_id===stem));
const ownRequests=s.countsFor('A17').requests.filter(q=>ownVersions.some(v=>v.sha256===q.body_sha256));
write('producer-summary-v001.json',JSON.stringify({owner:'a17_producer_03_04',run_id:'20261002-204314-6f31',task_id:'A17',production_done:true,writing_done_at:new Date().toISOString(),final_candidates:finals,actual_render_requests:ownRequests.length,render_successes:ownRequests.filter(q=>q.ok).length,render_failures:ownRequests.filter(q=>!q.ok).length,new_document_requests:0,reused_docs:docs.length,producer_actual_views:views.length,completed_visual_iterations:s.countsFor('A17').iterations.filter(i=>i.type==='visual'&&i.completed&&finalSpecs.some(([stem])=>i.case_id===stem)).length,final_pngs_to_publish:4,independent_creative_cases:0,unknown_token_usage:null,unknown_cost:null,warning:'仅生产方内容/视觉通过，未正式发布；root仍需总审查/发布/指标。历史命令失败与初版/修订全部保留。'},null,2)+'\n');
console.log(JSON.stringify({writing_done:true,finals:finals.map(f=>({stem:f.stem,request_id:f.request_id,version:f.version_id})),own_requests:ownRequests.length,views:views.length}));
