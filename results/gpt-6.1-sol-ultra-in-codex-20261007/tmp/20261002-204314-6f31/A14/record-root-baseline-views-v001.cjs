const fs=require('fs'),path=require('path'),s=require('../_suite/suite.cjs'),d=s.taskDirs('A14');
const obs=[
 'K01完整原图真看：开始1行72px，林川与09:00完整，开放绿勾，品牌/日期统一，安全与区域清楚。',
 'K02完整原图真看：读文档，也要读懂布局约束1行56px，周禾 / 许宁与09:40、满额方块/文字完整。',
 'K03完整原图真看：原标题完整48px两行，但第2行只剩级字，出现明显孤字尾行；候补钟/文字、顾行与10:20清楚。须修改通用排版规则消除尾行。',
 'K04完整原图真看：A < B & C > D：不要把文本当成标签1行48px，特殊符号显示原样，苏言/11:00与开放清楚。',
 'K05完整原图真看：Color, Alpha & Contrast / 从颜色到可读性1行48px，逗号&斜线与原文完整，孟澄/13:00/开放可读。',
 'K06完整原图真看：全文标题48px1行、许宁/13:40保留，右上红叉取消及右下本场取消并存，主内容仍深墨可读。',
 'K07完整原图真看：标题44px两行，末行觉检查，跨行把视觉拆分；Northstar Research · 林川1行28px和14:20候补完整。通用换行规则可改进均衡。',
 'K08完整原图真看：标题44px两行，中文引号完整、最后一公里尾文保留，周禾/15:00及开放清楚。'
];
const images=obs.map((observation,i)=>{const case_id='K'+String(i+1).padStart(2,'0'),image_path=path.join(d.temp,'requests/A14-request-'+String(i+1).padStart(6,'0')+'/response.png'),version_id='A14-v001-'+case_id;const v=s.view('A14',image_path,{tool:'view_image',reviewer:'root',version_id,case_id,observation});return {image_path,version_id,case_id,observation,existing_view_id:v.id};});
fs.writeFileSync(path.join(d.temp,'root-baseline-review-v001.json'),JSON.stringify({task_id:'A14',reviewer:'root',actual_tool:'view_image',images,issues:['K03第2行单字孤行','K07跨行拆视觉词，可由通用长标题布局改善'],not_final_pass:true},null,2)+'\n',{flag:'wx'});console.log(images.map(v=>({case_id:v.case_id,view:v.existing_view_id})));
