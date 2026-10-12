const fs=require('fs'),path=require('path'),s=require('../_suite/suite.cjs'),d=s.taskDirs('A13');
const finals=[
 ['000003','symbol-color','彩色原512图两错位框笔画比预览更稳，中央共同负空间仍开放；偏移、外形清晰。'],
 ['000004','symbol-black','原512透明纯黑PNG已打开，工具黑底使轮廓不可见；另实际打开白底QA512及32确认两叠框轮廓与中心开口，alpha/RGB另独立测量。'],
 ['000005','brand-banner','实际1200×400横幅左图标右字标，叠光 Layerlight及整句口号清楚，字形无裁切，紫线保持横向结构。'],
 ['000006','launch-poster','实际1080×1350海报为独立竖向发布构图：OPEN BETA、双语字标、完整口号，上下留白与居中大叠框；日期ONLINE及网站完整可读。']
].map(([n,stem,observation])=>{const image_path=path.join(d.temp,'requests/A13-request-'+n+'/response.png'),version_id='A13-final-v002-'+stem;const v=s.view('A13',image_path,{tool:'view_image',reviewer:'root',version_id,case_id:stem,observation});return {image_path,version_id,case_id:stem,observation,existing_view_id:v.id};});
const qa=[
 ['symbol-black-qa512-on-white-v001.png','symbol-black','实际白底512检查板中纯黑两错位空心方框清晰，中心空窗与外部透明背景经白底显示，几何同彩色。'],
 ['symbol-color-qa32-on-white-v001.png','symbol-color','实际32×32彩色缩略两层外轮廓与中央开口仍能识别，加粗后笔画稳定。'],
 ['symbol-black-qa32-on-white-v001.png','symbol-black','实际32×32纯黑缩略仍可识别两错位空窗与共同负空间，黑色交接未封闭中心。'],
 ['symbol-color-qa32-nearest-zoom-v001.png','symbol-color','实际最近邻放大32像素板：约2.5px笔画，中央约7px负空间保留，可逐层追踪，不以放大板替代32原尺寸查看。'],
 ['symbol-black-qa32-nearest-zoom-v001.png','symbol-black','实际最近邻32像素板：纯黑连接更统一，两个外轮廓与共同开口均保持，细角抗锯齿可见。']
].map(([file,stem,observation])=>s.view('A13',path.join(d.temp,'production',file),{tool:'view_image',reviewer:'root',version_id:'A13-final-v002-'+stem,case_id:stem,is_preview:true,observation}));
fs.writeFileSync(path.join(d.temp,'root-final-review-v001.json'),JSON.stringify({task_id:'A13',reviewer:'root',actual_tool:'view_image',images:finals,qa_view_ids:qa.map(v=>v.id),resume_notes:'A13原4PNG和512白底/32缩略实际审查通过，待独立alpha/几何审查与交付文件完成后关闭。'},null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({final_view_ids:finals.map(v=>v.existing_view_id),qa_view_ids:qa.map(v=>v.id)}));
