const fs=require('node:fs'),s=require('../../_suite/suite.cjs');
const m=JSON.parse(fs.readFileSync('tmp/20261002-204314-6f31/A17/requests/A17-request-000009/render-result.json','utf8'));
const v=s.view('A17',m.image_path,{tool:'view_image',reviewer:'/root/a17_auditor',version_id:m.version_id,case_id:m.case_id,observation:'独立审查实际打开handbook04-v002：省略说明完整一行无裁切，16行真实编号片段与清晰左/模糊右图示语义一致，复现/视觉自检正文完整。图内BACKGROUND/SUBTREE仍20，root现从严要求全部可读图示文字≥24，待对应example与手册同步修改后再审查。',scope:'actual displayed image; visual note fix confirmed, stricter annotation font update pending'});
fs.writeFileSync(require('node:path').join(__dirname,'handbook04-v002-actual-view-v001.json'),JSON.stringify(v,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify(v));
