const fs=require('node:fs'),path=require('node:path'),s=require('../../_suite/suite.cjs');
const write=(n,d)=>fs.writeFileSync(path.join(__dirname,n),d,{flag:'wx'}),read=n=>JSON.parse(fs.readFileSync(path.join(__dirname,n),'utf8'));
const qaObservations={
 '03-thumbnail':'实际打开最终handbook03 v003的600×800临时缩略：16代码源行、正确省略范围、alpha标签24px、正文/底卡/页脚层级完整。',
 '03-figure':'实际打开最终400×240临时局部：首行<A> & B、Style blue & literal、FF 255/255和80 128/255标签完整；左右红与半透明红对照正确。',
 '04-thumbnail':'实际打开最终handbook04 v003的600×800临时缩略：图示标题24px、16源行及短省略说明完整，滤镜两侧差异明显，无布局越界。',
 '04-figure':'实际打开最终400×240临时局部：BACKGROUND/SUBTREE标题24px完整，左SHARP和深色条锐利，右同字同条blur3，外部白底与剪裁边界明确。'
};
const qaViews=Object.entries(qaObservations).map(([key,observation])=>{const [page,kind]=key.split('-');return s.view('A17',path.join(__dirname,`handbook-${page}-final-${kind}-qa-v001.png`),{tool:'view_image',viewer:'a17_producer_03_04',version_id:'A17-v003-handbook-'+page,case_id:'handbook-'+page,view_kind:'temporary_final_'+kind,observation});});
write('final-qa-view-records-v001.json',JSON.stringify(qaViews,null,2)+'\n');
const sources=read('sources-final-draft-v001.json');sources.claims.find(c=>c.id==='03-cdata').handbook_illustration='第3页底部实际印出 &lt; 字符串，实体未解码。';sources.editorial_revision='只更正来源草案字段的实体字串说明；实际图和技术结论不改。';write('sources-final-draft-v002.json',JSON.stringify(sources,null,2)+'\n');
s.toolUsage('A17',{tool:'Python/Pillow actual QA scripts',owner:'a17_producer_03_04',purpose:'生成临时原图缩略/代码局部/插图局部并逐像素比较直接构件与独立服务例；只QA，最终原PNG字节不动。',input_paths:read('final-candidates-v001.json').map(f=>f.image_path),output_paths:[path.join(__dirname,'qa-pixel-and-previews-v001.json'),path.join(__dirname,'final-pixel-check-v001.json')],scripts:[path.join(__dirname,'qa-pixel-and-previews-v001.py'),path.join(__dirname,'final-pixel-check-v001.py')],new_HTTP_requests:0});
const before=read('producer-summary-v001.json'),all=s.countsFor('A17');
const summary={...before,producer_actual_views:all.views.filter(v=>v.viewer==='a17_producer_03_04').length,writing_done_at:new Date().toISOString(),final_pixel_equality_check:path.join(__dirname,'final-pixel-check-v001.json'),all_final_figure_text_font_min:24,source_json:path.join(__dirname,'sources-final-draft-v002.json'),all_writing_completed:true};write('producer-summary-v002.json',JSON.stringify(summary,null,2)+'\n');
let md='# A17 第3、4页生产交接\n\n全部生产写入已结束；没有发布正式产物、改suite-state、写正式报告或指标。root可读取 final-candidates-v001.json 并在真实root看图/独立审查后发布。\n\n';
for(const f of before.final_candidates)md+=`- ${f.stem}: ${f.version_id}, ${f.request_id}, ${f.width}×${f.height}; service meta: ${f.meta_path}; producer views: ${f.producer_actual_view_ids.join(', ')}。\n`;
md+='\n入门手册统一64px边距；正文含示例说明全部至少24px，代码20px。每页印16个真源行（最大49ASCII视觉列），明确省略其他行。完整独立例与手册插图是相同根Widget，未用Image；最终每个400×240局部与独立例RGBA逐像素相同。\n\n';
md+='修订：04短源行说明修复裁切；03底部alpha说明和04例标题20→24px同步独立例/页；03源行范围改5–8、10–17、20–21、23–24，以准确标明第9行省略。初版和所有尝试原样保留。真实10次render全部200/image/png成功；6次完整视觉迭代；生产方真实20次查看；没有新文档HTTP（8份官方缓存已实际读）。旧local-command-failure-v001.json仍保留，非HTTP请求。未知token/费用null。\n\n';
md+='供root合并：examples-final-draft-v001.json（完整source/真行号/省略/服务响应/实际view/exactwidgetSHA）；sources-final-draft-v002.json + sources-final-draft-v001.md（每claim实际url/cache/原请求/页/例）；final-pixel-check-v001.json（最终RGBA一致和alpha采样）；producer-summary-v002.json（最终完整生产状态）。\n\n';
md+='文件完整性与像素比较只作为证据，内容通过依赖实际视图记录；正式总审查仍由root执行。\n';write('handoff-v001.md',md);
console.log(JSON.stringify({all_writing_completed:true,actual_requests:summary.actual_render_requests,actual_views:summary.producer_actual_views,completed_visual_iterations:summary.completed_visual_iterations,finals:before.final_candidates.map(f=>f.stem)}));
