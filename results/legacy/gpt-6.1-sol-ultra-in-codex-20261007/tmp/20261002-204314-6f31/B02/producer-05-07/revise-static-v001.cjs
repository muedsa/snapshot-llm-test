'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');const base=__dirname;
function save(n,v){fs.writeFileSync(path.join(base,n),typeof v==='string'?v:JSON.stringify(v,null,2),{encoding:'utf8',flag:'wx'});}
let s=fs.readFileSync(path.join(base,'generate-v001.cjs'),'utf8');
function sub(a,b){if(!s.includes(a))throw Error('target missing '+a);s=s.replace(a,b);}
sub("end:'最终适配仍由评估台确认。'", "end:'不接受 / 不符合 → 先评估方案。'");
sub("c.rect(58,822,1384,190,P.ink", "txt(c,65,790,1360,28,'符合基础条件也需由评估台确认；不接受可见补丁，可以先了解其他方案。',18);\n+ c.rect(58,822,1384,190,P.ink");
sub("c.arrow(x+86,685,x+235,685,P.clay,2,{double:true,headLength:8});txt(c,x+105,669,130,27,'每边10 mm',15,P.clay,true);", "c.arrow(x+188,614,x+232,614,P.clay,2,{double:true,headLength:5});txt(c,x+58,708,255,24,'本例余量10 mm/边 · 非比例图',14,P.clay,true);");
sub("for(const fn of [assessment,learning,receipt])", "for(const fn of [assessment,learning])");
sub("function write(n,v){fs.writeFileSync(path.join(base,n),", "function write(n,v){n=n.replace('-v001.snapshot','-v002.snapshot').replace('-metadata-v001.json','-metadata-v002.json').replace('-content-v001.md','-content-v002.md').replace('source-read-evidence-v001.json','source-read-evidence-v002.json');fs.writeFileSync(path.join(base,n),");
save('generate-static-v002.cjs',s);vm.runInNewContext(s,{require,__dirname:base,console},{filename:'generate-static-v002.cjs'});
save('static-revision-v001.json',{recorded_at:new Date().toISOString(),reason:'独立审计语义与几何静态补全，root尚未渲染05/06',category:'alternative/static_refinement',cases:[{id:'case-05',parent:'case-05-v001.snapshot',version:'case-05-v002.snapshot',changes:['第三门不接受/不符合明确转先评估方案','卡片下补评估适配与了解其他方案路径']},{id:'case-06',parent:'case-06-v001.snapshot',version:'case-06-v002.snapshot',changes:['10mm/边不再用跨全补丁宽的尺寸箭头','改从损伤边至补丁右边的短箭头，注释本例余量与非比例图']}],measured_data:'品牌/地址/运营价格及损伤/针法示例自拟。10mm与5mm为练习示意，无实物测量数据，不宣称图中坐标对应实物尺寸。',service_request:false,visual_iteration:false});
