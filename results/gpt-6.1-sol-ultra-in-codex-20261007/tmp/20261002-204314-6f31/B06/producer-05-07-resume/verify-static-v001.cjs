const fs=require('fs'),path=require('path'),crypto=require('crypto');
const p=JSON.parse(fs.readFileSync(path.join(__dirname,'../problem-plan-v001.json'),'utf8'));
const cases=p.cases.filter(x=>['case-05','case-06','case-07'].includes(x.id));
const checks=cases.map(x=>{
 const suffix=x.id==='case-07'?'v002':'v001';
 const dsl=fs.readFileSync(path.join(__dirname,x.id+'-'+suffix+'.snapshot'),'utf8');
 const fields=x.id==='case-05'?['豆腐','蘑菇','菠菜','1盒','1袋','1把','10月11日','10月12日','10月13日','中层前排','抽屉左侧','抽屉右侧','米 1份','不用再买：豆腐、蘑菇','不判断食品安全']:x.id==='case-06'?['城市里的树','慢读笔记','雨天地图','不可续借','可续借一次','预约已到馆','R-08','尚未申请','成功后才改为10月28日','09:00–18:00']:['北院 A柜','17','第3行 · 第5列','本人真实取件码','还没有开门','10月12日20:00','4行×6列＝24扇门','未接入真实柜机'];
 const present=fields.map(f=>({text:f,present:dsl.includes(f)}));
 const rawNumbers=[...dsl.matchAll(/<!\[CDATA\[(\d{2})\]\]>/g)].map(m=>m[1]);
 return{case_id:x.id,file:x.id+'-'+suffix+'.snapshot',sha256:crypto.createHash('sha256').update(dsl).digest('hex'),dimension_container_present:dsl.includes('<Container width="'+x.dimensions[0]+'" height="'+x.dimensions[1]+'">'),fields:present,all_fields_present:present.every(z=>z.present),door_numbers:x.id==='case-07'?rawNumbers:null,door_number_set_complete:x.id==='case-07'?[...Array(24)].every((_,i)=>rawNumbers.includes(String(i+1).padStart(2,'0'))):null,visual_review_status:'not yet rendered; syntax/content check cannot establish visual quality'};
});
if(checks.some(x=>!x.all_fields_present||!x.dimension_container_present))throw new Error('Static field audit failed');
fs.writeFileSync(path.join(__dirname,'static-audit-v001.json'),JSON.stringify({at:new Date().toISOString(),checks},null,2));
console.log(JSON.stringify(checks.map(x=>({case_id:x.case_id,fields:x.fields.length,pass:x.all_fields_present,door_number_set_complete:x.door_number_set_complete}))));
