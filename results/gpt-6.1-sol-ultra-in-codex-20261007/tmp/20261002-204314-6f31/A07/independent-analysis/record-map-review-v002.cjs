const fs=require('fs'),path=require('path');
const s=require('../../_suite/suite.cjs');
const old=JSON.parse(fs.readFileSync(path.join(__dirname,'../map-geometry-v001.json'),'utf8'));
const next=JSON.parse(fs.readFileSync(path.join(__dirname,'../map-geometry-v002.json'),'utf8'));
function diff(a,b,p='$',out=[]){
 if(JSON.stringify(a)===JSON.stringify(b))return out;
 if(a&&b&&typeof a==='object'&&typeof b==='object'){
  for(const key of new Set([...Object.keys(a),...Object.keys(b)]))diff(a[key],b[key],p+'.'+key,out);
 }else out.push({path:p,before:a,after:b});
 return out;
}
const changes=diff(old,next);
const expectedOnly=changes.length===1&&changes[0].path==='$.nodes.6.label.x'&&changes[0].before===95&&changes[0].after===180;
const view=s.view('A07','D:/workspaces/gpt-6.1-sol-ultra/outputs/20261002-204314-6f31/A07/network-map.png',{
 tool:'view_image',reviewer:'graph_auditor',version_id:'A07-map-v002',
 observation:'实际查看最终地图v002：S07名称/无障碍说明已右移，与B端点色块分开，仍明确属于S07圆站。其余16站标记/设施、三线序、45/90体系、唯一非站过桥与非地理说明维持清晰；无标签裁切或误作新换乘。'
});
const result={generated_at:new Date().toISOString(),task_id:'A07',changes_from_v001:changes,
 only_s07_label_x_changed:expectedOnly,routes_unchanged:JSON.stringify(old.line_geometry)===JSON.stringify(next.line_geometry),
 previous_full_geometry_review:'map-geometry-review-v001.json',view_event:view};
fs.writeFileSync(path.join(__dirname,'map-final-review-v002.json'),JSON.stringify(result,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify(result,null,2));
