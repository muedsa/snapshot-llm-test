const fs=require('node:fs'),path=require('node:path'),s=require('../../_suite/suite.cjs');
const r=JSON.parse(fs.readFileSync(path.join(__dirname,'handbook-04-render-v002.json'),'utf8'));
const before=JSON.parse(fs.readFileSync(path.join(__dirname,'baseline-view-records-v001.json'),'utf8')).find(r=>r.stem==='handbook-04');
const observation='实际再次打开1200×1600 handbook04 v002：代码块下短说明完整显示“所列16个源行号；中间与其余行省略，完整源附后”，不再裁字；代码16真源行、清晰/模糊对照、规则、底部清单和页脚保持完整。';
const v=s.view('A17',r.image_path,{tool:'view_image',viewer:'a17_producer_03_04',version_id:r.version_id,case_id:'handbook-04',observation});
s.iteration('A17',{type:'visual',version_id:r.version_id,parent_version:'A17-v001-handbook-04',case_id:'handbook-04',completed:true,before_view_id:before.view_id,after_view_id:v.id,image_path:r.image_path,changes:'长的全部源行号列表说明改为短说明，代码中16个真源行号不变，完整省略映射仍在JSON。',comparison:'实际v001长说明后半被32px框裁掉；v002完整显示短说明与省略提示，其余教学构件和真实对照不变。',passes_visual_check:true});
fs.writeFileSync(path.join(__dirname,'refined-view-record-v002.json'),JSON.stringify(v,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify({stem:'handbook-04',view_id:v.id}));
