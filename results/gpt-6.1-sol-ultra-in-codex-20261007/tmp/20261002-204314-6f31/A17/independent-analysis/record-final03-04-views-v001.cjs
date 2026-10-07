const fs=require('node:fs'),path=require('node:path'),s=require('../../_suite/suite.cjs');
const details=[
 ['000012','独立实际打开example03-v002：底部alpha标签已24，FF255/255及80128/255完整并未碰边，实体/Raw空白/蓝色粗体与两红块保持清晰；对比初版文字更可读。'],
 ['000016','独立实际打开handbook03-v003：嵌入图alpha标签已24与实际独立例一致；16行编号代码完整，省略说明准确改成5–8/10–17/20–21/23–24，明确跳过9；全文无裁切，正文和图示可读。'],
 ['000014','独立实际打开example04-v002：BACKGROUND和SUBTREE已24，完整不裁切；左清晰字/模糊背景、右模糊字与深条的滤镜对照仍成立，两180×176区域范围明确。'],
 ['000015','独立实际打开handbook04-v003：直接图示标题24与独立例一致；16行真实源号代码无换行裁字，省略说明一行完整；滤背景与滤子树、ClipRect限制、实际自检和可复现交付正文正确清晰。']
];
const views=details.map(([id,observation])=>{const m=JSON.parse(fs.readFileSync(`tmp/20261002-204314-6f31/A17/requests/A17-request-${id}/render-result.json`,'utf8'));return s.view('A17',m.image_path,{tool:'view_image',reviewer:'/root/a17_auditor',version_id:m.version_id,case_id:m.case_id,observation,scope:'actual final candidate image displayed; baseline physically reviewed earlier'});});
fs.writeFileSync(path.join(__dirname,'final03-04-view-records-v001.json'),JSON.stringify(views,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify(views,null,2));
