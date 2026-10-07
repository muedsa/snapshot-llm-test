const fs=require('fs'),path=require('path'),s=require('../../_suite/suite.cjs');
const descriptions=[
 '实际原图K01：开始完整一行；林川/09:00/开放/日期品牌清楚，绿色勾+原状态；边距与徽标无碰撞。',
 '实际原图K02：标题完整一行；周禾 / 许宁/09:40/满额原串清楚，蓝灰方块+原状态；日期品牌统一，无裁切。',
 '实际原图K03：标题完整两行但末字级独占第二行，存在明显孤行；顾行/10:20/候补原串清楚，黄色时钟+原状态。建议泛化字号/换行规则修正孤行。'
];
const entries=descriptions.map((observation,i)=>{const n=i+1,meta=JSON.parse(fs.readFileSync(path.resolve(__dirname,`../requests/A14-request-${String(n).padStart(6,'0')}/render-result.json`),'utf8'));return s.view('A14',meta.image_path,{tool:'view_image',reviewer:'a10_audit_resume',version_id:meta.version_id,case_id:meta.case_id,is_preview:false,observation});});
fs.writeFileSync(path.join(__dirname,'actual-views-batch01-v001.json'),JSON.stringify({task_id:'A14',reviewer:'a10_audit_resume',entries,observed_title_lines:{K01:1,K02:1,K03:2},observed_speaker_lines:{K01:1,K02:1,K03:1},K03_visual_issue:'single final character级 on second line'},null,2)+'\n',{flag:'wx'});
process.stdout.write(JSON.stringify(entries.map(e=>({id:e.id,version_id:e.version_id,case_id:e.case_id}))));
