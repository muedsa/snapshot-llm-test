const fs=require('fs'),path=require('path');
const {Canvas}=require('../../_suite/dsl.cjs');
const old=fs.readFileSync(path.join(__dirname,'case-07-v001.snapshot'),'utf8');
const wrong=new Canvas(1600,1120);wrong.arrow(826,649,886,649,'#FFD965',5,{headLength:18,headWidth:10});
const right=new Canvas(1600,1120);right.arrow(680,696,698,696,'#FFD965',4,{headLength:9,headWidth:5});
let fixed=old.replace(wrong.children.join('\n'),right.children.join('\n'));
if(fixed===old)throw new Error('Arrow replacement did not match');
// Caption is located under the whole matrix; use it as a matrix description,
// leaving the exact target marker in the clear gap immediately left of door 17.
fixed=fixed.replace('17号门 · 目标','24扇门 · 正面示意');
fs.writeFileSync(path.join(__dirname,'case-07-v002.snapshot'),fixed);
const meta=JSON.parse(fs.readFileSync(path.join(__dirname,'case-07-metadata-v001.json'),'utf8'));
meta.created_at=new Date().toISOString();meta.pre_render_changes=['发现v001箭头坐标会指向18号门，未提交服务前移至17号门左侧空隙；矩阵下方文字改为示意标题。'];
fs.writeFileSync(path.join(__dirname,'case-07-metadata-v002.json'),JSON.stringify(meta,null,2));
fs.writeFileSync(path.join(__dirname,'pre-render-correction-v001.json'),JSON.stringify({at:new Date().toISOString(),case_id:'case-07',before:'case-07-v001.snapshot',after:'case-07-v002.snapshot',kind:'unrendered_geometry_correction',is_complete_visual_iteration:false,reason:'Arrow x826→886 passed into door18; target door17 is x702–828. Corrected x680→698 at y696, in gap left of17.'},null,2));
