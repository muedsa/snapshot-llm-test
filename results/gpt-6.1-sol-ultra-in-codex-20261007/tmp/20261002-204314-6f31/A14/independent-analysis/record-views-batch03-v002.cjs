const fs=require('fs'),path=require('path'),s=require('../../_suite/suite.cjs');
const observations=[
 '实际原图K03v002：44px原标题完整一行，孤字级已消除；顾行/10:20/候补/品牌日期均保留，标题区域和状态不撞。',
 '实际原图K07v002：44px、920px活动区，两行全文，第二行为数据与视觉检查；视觉不再拆开，原双破折号和Northstar Research · 林川仍完整。',
 '实际原图K08v002：44px、920px活动区，两行全文，第二行为能力的最后一公里；原引号/冒号完整，两行较v001均衡，周禾/15:00开放保留。'
];
const entries=observations.map((observation,i)=>{const n=i+9,meta=JSON.parse(fs.readFileSync(path.resolve(__dirname,`../requests/A14-request-${String(n).padStart(6,'0')}/render-result.json`),'utf8'));return s.view('A14',meta.image_path,{tool:'view_image',reviewer:'a10_audit_resume',version_id:meta.version_id,case_id:meta.case_id,is_preview:false,observation});});
fs.writeFileSync(path.join(__dirname,'actual-views-batch03-v002.json'),JSON.stringify({task_id:'A14',reviewer:'a10_audit_resume',entries,observed_title_lines:{K03:1,K07:2,K08:2},observed_speaker_lines:{K03:1,K07:1,K08:1},actual_comparison_to_baseline_completed:true,unresolved:[]},null,2)+'\n',{flag:'wx'});
process.stdout.write(JSON.stringify(entries.map(e=>({id:e.id,version_id:e.version_id,case_id:e.case_id}))));
