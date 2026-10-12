'use strict';
const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'../../../..'),s=require(path.join(root,'tmp/20261002-204314-6f31/_suite/suite.cjs'));
const {Canvas}=require(path.join(root,'tmp/20261002-204314-6f31/_suite/dsl.cjs'));
const original=fs.readFileSync(path.join(__dirname,'desktop-v003-separator-diagnostic.snapshot'),'utf8');
const re=/<Positioned[^>]*><Text[\s\S]*?<\/Text><\/Positioned>/g;
const allText=[...original.matchAll(re)].map(m=>m[0]);
if(allText.length!==25)throw new Error('Expected 25 direct field subtrees');
const geometry=original.replace(re,'');
const title=new Canvas(1440,900,{background:'#F5F4EE'});
title.text(48,64,472,208,'Structure / Vision',78,'#192F35',{font:'Inter,Noto Sans CJK SC',bold:true,height:1.1});
(async()=>{
for(const [id,dsl,purpose] of [['A12-probe-000001-geometry',geometry,'Controlled diagnosis: same desktop canvas/cards/motif, remove all 25 Text subtrees. Not final candidate.'],['A12-probe-000002-title',title.toString(),'Controlled diagnosis: desktop title at exact intended 78px and box only. Not final candidate.']]){
const r=await s.render('A12',dsl,{version_id:id,parent_version:'A12-v003-desktop',type:'alternative',width:1440,height:900,case_id:'diagnostic',purpose});
console.log(JSON.stringify({id,ok:r.ok,http_status:r.http_status,meta_path:r.meta_path,error:r.error_summary}));
}
})().catch(e=>{console.error(e);process.exitCode=1});
