'use strict';
const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'../../../..'),s=require(path.join(root,'tmp/20261002-204314-6f31/_suite/suite.cjs'));
const audit=JSON.parse(fs.readFileSync(path.join(__dirname,'batch-audit-draft-v001.json'),'utf8'));
const oldRules=JSON.parse(fs.readFileSync(path.join(__dirname,'generation-rules-v001.json'),'utf8'));
const views=JSON.parse(fs.readFileSync(path.join(__dirname,'producer-baseline-reviews-v001.json'),'utf8'));
const write=(f,v)=>fs.writeFileSync(path.join(__dirname,f),typeof v==='string'?v:JSON.stringify(v,null,2)+'\n',{flag:'wx'});
const titleUnits=str=>[...str].reduce((n,ch)=>n+(ch.codePointAt(0)>0x2FF?1:.55),0);
const titleSize=u=>u<=6?72:u<=17?56:u<=22?48:44;
const titleWidth=u=>u>26?920:1072;
const rules={...oldRules,version:'v002',title_rules:{...oldRules.title_rules,font_sizes:[{maximum_units:6,size:72},{maximum_units:17,size:56},{maximum_units:22,size:48},{otherwise:true,size:44}],active_title_width_rules:[{maximum_units:26,width:1072},{otherwise:true,width:920}],outer_title_region_remains_uniform:true,reason:'Actual v001 K03 isolated one last character and K07 split视觉; reduce48px capacity threshold and balance longer titles in narrower active region. Rules are length-based, noIDexception.'}};
write('generation-rules-v002.json',rules);
(async()=>{
const results=[];
for(const card of audit.cards){
const units=titleUnits(card.original.title),size=titleSize(units),width=titleWidth(units),before=views.find(v=>v.case_id===card.id);
const old=card.fields.find(f=>f.field==='title');
if(old.font_size===size&&old.position.width===width){card.final_version_id='A14-v001-'+card.id;continue;}
const dsl=fs.readFileSync(path.join(__dirname,'card-'+card.id+'-v001.snapshot'),'utf8');
const prefix=`<Positioned left="64" top="166" width="${old.position.width}" height="252"><Text fontFamily="Inter,Noto Sans CJK SC" fontSize="${old.font_size}"`;
if(!dsl.includes(prefix))throw new Error('Cannot locate exact title prefix');
const fixed=dsl.replace(prefix,`<Positioned left="64" top="166" width="${width}" height="252"><Text fontFamily="Inter,Noto Sans CJK SC" fontSize="${size}"`);
write('card-'+card.id+'-v002.snapshot',fixed);
old.font_size=size;old.position.width=width;card.title_font_size=size;card.title_region={...card.title_region,width};card.outer_title_region={x:64,y:166,width:1072,height:252};card.final_version_id='A14-v002-'+card.id;
const r=await s.render('A14',fixed,{version_id:card.final_version_id,parent_version:'A14-v001-'+card.id,type:'visual',stem:'card-'+card.id,width:1200,height:630,case_id:card.id,before_view_id:before.id,changes:'Shared length rule:48px font threshold26→22units; titleunits>26 use920px active width inside1072px common region. Source strings unchanged, noperIDexception.',purpose:'A14 generically balanced title layout '+card.id});
results.push({id:card.id,ok:r.ok,meta_path:r.meta_path,image_path:r.image_path,before_view_id:before.id,error:r.error_summary});
console.log(JSON.stringify(results.at(-1)));
}
write('batch-audit-draft-v002.json',audit);write('refinement-results-v002.json',results);
})().catch(e=>{console.error(e);process.exitCode=1});
