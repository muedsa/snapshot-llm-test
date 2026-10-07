const fs=require('fs'),path=require('path'),s=require('../../_suite/suite.cjs');
const descriptions=[
 '实际原图K04：A < B & C > D：不要把文本当成标签完整一行，角括号/ampersand未被解释成DSL标签；苏言/11:00/开放清楚。',
 '实际原图K05：Color, Alpha & Contrast / 从颜色到可读性完整一行，comma/ampersand/slash保真；孟澄/13:00/开放清楚。',
 '实际原图K06：原标题完整一行、许宁、13:40、取消原串都在；粉橙叉+取消与底部本场取消齐全，保持统一浅色卡片。',
 '实际原图K07：全文两行，末行觉检查，视觉一词被跨行拆分，建议泛化窄化长标题区以改善两行平衡。Northstar Research · 林川原串完整一行；14:20候补清楚。',
 '实际原图K08：原中文引号、冒号与全文完整两行，末行最后一公里；周禾/15:00/开放清楚。八张主题区域、字号体系、品牌日期均一致，无裁切或状态徽标碰撞。'
];
const entries=descriptions.map((observation,i)=>{const n=i+4,meta=JSON.parse(fs.readFileSync(path.resolve(__dirname,`../requests/A14-request-${String(n).padStart(6,'0')}/render-result.json`),'utf8'));return s.view('A14',meta.image_path,{tool:'view_image',reviewer:'a10_audit_resume',version_id:meta.version_id,case_id:meta.case_id,is_preview:false,observation});});
fs.writeFileSync(path.join(__dirname,'actual-views-batch02-v001.json'),JSON.stringify({task_id:'A14',reviewer:'a10_audit_resume',entries,observed_title_lines:{K04:1,K05:1,K06:1,K07:2,K08:2},observed_speaker_lines:{K04:1,K05:1,K06:1,K07:1,K08:1},K07_visual_issue:'视觉 split after视 with觉检查 on second line'},null,2)+'\n',{flag:'wx'});
process.stdout.write(JSON.stringify(entries.map(e=>({id:e.id,version_id:e.version_id,case_id:e.case_id}))));
