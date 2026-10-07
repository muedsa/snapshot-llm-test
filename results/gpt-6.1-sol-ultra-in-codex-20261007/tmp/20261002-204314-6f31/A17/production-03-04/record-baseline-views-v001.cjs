const fs=require('node:fs'),path=require('node:path'),s=require('../../_suite/suite.cjs');
const observations={
 'example-03':'实际打开400×240服务原PNG：首行<A> & B的字面尖括号、&可见，Raw起始双空格产生左缩进；Style blue & literal完整且blue蓝色粗体。左红块饱和红，右红块在白底呈淡红；FF/80与255/255、128/255标注完整。无遮挡或溢出。',
 'handbook-03':'实际打开1200×1600服务原PNG：页码03/04、中文规则、16行带真实源行号的20px代码、400×240原构件插图、两底部24px说明和页脚完整。代码包含Raw/CDATA字面片段、嵌Text样式与两alpha色；省略源行说明未裁。正文与代码对比充分，边缘留64px安全区。',
 'example-04':'实际打开400×240服务原PNG：两侧蓝绿条纹源形态相同，左BACKGROUND上SHARP字和深条清晰，右SUBTREE内同字同深条明显模糊；两侧背景条纹已变柔，每侧180×176剪裁区边界可见，外部标题仍清晰。',
 'handbook-04':'实际打开1200×1600服务原PNG：规则、16真源行、相同实际滤镜对照、底部检查与交付清单都完整清晰；但代码块下的完整源行号列表太长，在固定32px文本框中裁掉后续编号和省略提示。需改短说明，保留代码中真实行号和examples映射。'
};
const records=Object.entries(observations).map(([stem,observation])=>{
 const r=JSON.parse(fs.readFileSync(path.join(__dirname,stem+'-render-v001.json'),'utf8'));
 const v=s.view('A17',r.image_path,{tool:'view_image',viewer:'a17_producer_03_04',version_id:r.version_id,case_id:stem,observation});
 s.iteration('A17',{type:'baseline',version_id:r.version_id,parent_version:null,case_id:stem,completed:true,after_view_id:v.id,image_path:r.image_path,observation,passes_visual_check:stem!=='handbook-04'});
 return {stem,view_id:v.id,observation};
});
fs.writeFileSync(path.join(__dirname,'baseline-view-records-v001.json'),JSON.stringify(records,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify(records.map(r=>({stem:r.stem,view_id:r.view_id}))));
