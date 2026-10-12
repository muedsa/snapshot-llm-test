'use strict';
const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'../../../..'),s=require(path.join(root,'tmp/20261002-204314-6f31/_suite/suite.cjs'));
const views=JSON.parse(fs.readFileSync(path.join(__dirname,'large-actual-reviews-v004.json'),'utf8'));
const before_view_id=views.find(v=>v.case_id==='stage').id;
let dsl=fs.readFileSync(path.join(__dirname,'stage-v004.snapshot'),'utf8');
const map=JSON.parse(fs.readFileSync(path.join(__dirname,'content-map-draft-v001.json'),'utf8'));
for(let i=0;i<6;i++){
const x=754+(i%3)*376,y=340+Math.floor(i/3)*276;
const before=`<Positioned left="${x+88}" top="${y+136}" width="238" height="84">`;
const after=`<Positioned left="${x+24}" top="${y+146}" width="302" height="72">`;
if(!dsl.includes(before))throw new Error('Missing detail box '+i);
dsl=dsl.replace(before,after)
  .replace(`<Positioned left="${x+24}" top="${y+102}" width="48" height="48">`,`<Positioned left="${x+24}" top="${y+68}" width="48" height="48">`)
  .replace(`<Positioned left="${x+24}" top="${y+107}" width="48" height="38">`,`<Positioned left="${x+24}" top="${y+73}" width="48" height="38">`);
const detail=map.fields.find(f=>f.layout==='stage'&&f.field===`cards[${i}].detail`);
detail.position={x:x+24,y:y+146,width:302,height:72};
const id=map.fields.find(f=>f.layout==='stage'&&f.field===`cards[${i}].id`);
id.position.y=y+73;
}
fs.writeFileSync(path.join(__dirname,'stage-v005.snapshot'),dsl,{flag:'wx'});
fs.writeFileSync(path.join(__dirname,'content-map-draft-v002.json'),JSON.stringify(map,null,2)+'\n',{flag:'wx'});
(async()=>{
const r=await s.render('A12',dsl,{version_id:'A12-v005-stage',parent_version:'A12-v004-stage',type:'visual',stem:'stage',width:1920,height:1080,case_id:'stage',before_view_id,changes:'After actual stage view showed 3 single trailing-character wraps, widen every card detail to full302px below the heading; move ID badge beside title. Original Raw source strings and font sizes unchanged.',purpose:'A12 large-screen card readability visual refinement'});
console.log(JSON.stringify({ok:r.ok,meta_path:r.meta_path,image_path:r.image_path,before_view_id,error:r.error_summary}));
})().catch(e=>{console.error(e);process.exitCode=1});
