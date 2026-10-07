'use strict';
const fs=require('node:fs'),path=require('node:path');
const s=require('../_suite/suite.cjs');
const results=[1,2].map(n=>JSON.parse(fs.readFileSync(path.join(__dirname,'requests',`A02-request-${String(n).padStart(6,'0')}`,'render-result.json'),'utf8')));
const observations=[
  '实际 view_image 打开 1920×1200 全图：三条泳道共用 09:00–16:00 横向线性时间轴，S01–S15 全部编号及时长可见；三个索引完整显示编号、标题、讲者、起止与类别。A/B/C 容量 320/80/160 人正确。12:00–13:00 公共午休跨三泳道单独标明，短 30/35/40 分钟色块保持较短宽度。中文与英文均清晰，索引最后 S15 行完整，没有观察到重叠、截字、漏项或错误类别。',
  '实际 view_image 打开 720×1280 全图：独立上午、午休、下午列表；S01–S15 完整保留编号、标题、会场、起止及类别，S04/S05/S06 依次为 10:00/10:10/10:15 开始。12:00–13:00 公共午休单独一行。讲者详见完整日程提示清楚；长中文标题单行完整，最后 S15 与页脚均未裁切，没有观察到重叠、截字或漏项。'
];
const views=results.map((r,i)=>s.view('A02',r.image_path,{tool:'view_image',version_id:r.version_id,detail:'original',scope:'whole original service PNG',observation:observations[i]}));
const crop=s.view('A02',path.join(__dirname,'qa-wide-10am-v001.png'),{tool:'view_image',version_id:results[0].version_id,detail:'original',source_image_path:results[0].image_path,scope:'actual service-derived QA crop [430,260,850,690]',observation:'实际查看 10 点附近三泳道局部：S03 右边缘与 10:00 网格重合，S04 左边缘同在 10:00；S05 在右侧 10:10 开始，S06 又晚 5 分钟于 10:15 开始。S06 35 min 明显窄于 S04 45 min 与 S05 60 min；C 会场 10:00–10:15 和 10:50–11:05 两个 15 分钟空档保留，文本没有相撞。'});
s.toolUsage('A02',{tool:'PIL via inspect-image.py',purpose:'Create immutable crop of real wide PNG solely for actual dense-region visual QA; no final postprocessing',input_paths:[results[0].image_path],output_paths:[path.join(__dirname,'qa-wide-10am-v001.png')],crop:[430,260,850,690],is_final:false});
results.forEach((r,i)=>s.iteration('A02',{type:'baseline',version_id:r.version_id,completed:true,image_path:r.image_path,request_id:r.id,after_view_id:views[i].id,additional_view_ids:i===0?[crop.id]:[],observation:observations[i],comparison:'基线实际查看符合要求，无需人为制造修改或视觉迭代。'}));
const finals=results.map(r=>s.acceptFinal('A02',r.stem,r,{title:r.stem==='agenda-wide'?'Structure / Vision 2026 全日日程':'Structure / Vision 2026 手机导览',version_id:r.version_id}));
fs.writeFileSync(path.join(__dirname,'producer-accepted-v001.json'),JSON.stringify({results,views,crop,finals},null,2)+'\n',{flag:'wx'});
s.taskCheckpoint('A02',{artifacts:finals,visual_review_evidence:[...views.map(v=>v.id),crop.id],resume_notes:'A02 both baselines actually inspected and accepted, original service PNGs and full DSL published; final-path views/audit/report pending.',checkpoint:'A02-published-baselines'});
s.writeTaskMetrics('A02');
console.log(JSON.stringify({finals:finals.map(f=>({image_path:f.image_path,dsl_path:f.dsl_path})),view_ids:[...views.map(v=>v.id),crop.id]}));
