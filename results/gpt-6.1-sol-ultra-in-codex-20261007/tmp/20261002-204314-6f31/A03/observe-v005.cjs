const fs=require('node:fs'),path=require('node:path');const s=require('../_suite/suite.cjs');
const meta=JSON.parse(fs.readFileSync(path.join(__dirname,'A03-bounds-fixed-v005-render.json'),'utf8'));
const v=s.view('A03',meta.response_file,{tool:'view_image',version_id:'A03-bounds-fixed-v005',detail:'original',scope:'whole first successful semantic diagnostic PNG',observation:'实际查看1280×800语义诊断图：System Pulse 标题变成顶部居中小字，原 font-size=44 未生效；USAGE 72% 单卡占满整行且文字黑色。LIVE 只有小文字，无96×36标签。REVIEW 是不透明青色、字小、靠中下而非右下；虽已用真实矩阵修复角度，alpha/位置/字号仍错。说明卡整体连文字被模糊，且没有穿过卡片两侧边界的条纹，圆角/居中效果不可核验。缺 LATENCY148ms 和 SUCCESS99.2% 两项。'});
s.iteration('A03',{type:'syntax-fix',version_id:'A03-bounds-fixed-v005',parent_version:'A03-parent-fixed-v004',completed:true,image_path:meta.response_file,request_id:meta.id,after_view_id:v.id,observation:v.observation,comparison:'四类显式错误已消除，当前真实PNG仍显露待修复的静默与视觉语义问题，不可作为最终图。'});
fs.writeFileSync(path.join(__dirname,'diagnostic-view-v005.json'),JSON.stringify(v,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({view_id:v.id,image:meta.response_file}));
