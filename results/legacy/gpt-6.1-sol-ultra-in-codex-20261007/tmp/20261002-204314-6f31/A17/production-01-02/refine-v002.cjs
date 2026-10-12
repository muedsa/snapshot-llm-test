'use strict';
const fs=require('fs'),path=require('path');
const s=require('../../_suite/suite.cjs');
const dir=__dirname,write=(f,t)=>fs.writeFileSync(path.join(dir,f),typeof t==='string'?t:JSON.stringify(t,null,2)+'\n',{flag:'wx'});
const changes='Raise example-01 subtitle fontSize 20 to 24 for readable instructional text; synchronize full runnable source, printed 17-line source and exact directly nested root Widget. No geometry or contract text changed.';
const before=[];
for(const stem of ['example-01','handbook-01']){
 const r=JSON.parse(fs.readFileSync(path.join(dir,stem+'-render-result-v001.json'),'utf8'));
 const v=s.view('A17',r.image_path,{tool:'functions.view_image',viewer:'/root/a17_producer_01_02',version_id:r.version_id,case_id:stem,mode:'original-before-visual-revision',observation:'Actual re-open of v001: mint illustration subtitle is only 20px. Increasing to 24px will meet body-text target while preserving 400×240 dimensions and exact-source correspondence.'});
 before.push({stem,parent_version:r.version_id,before_view_id:v.id});
 const dsl=fs.readFileSync(path.join(dir,stem+'-v001.snapshot'),'utf8'),needle='fontFamily="Inter" fontSize="20"';
 const matches=dsl.split(needle).length-1;
 if(matches!==(stem==='example-01'?1:2))throw Error('Unexpected count '+stem+' '+matches);
 write(stem+'-v002.snapshot',dsl.replaceAll(needle,'fontFamily="Inter" fontSize="24"'));
}
write('refinement-before-views-v002.json',{changes,views:before});
(async()=>{
 for(const b of before){
  const {stem}=b,dsl=fs.readFileSync(path.join(dir,stem+'-v002.snapshot'),'utf8'),isExample=stem.startsWith('example');
  const result=await s.render('A17',dsl,{version_id:'A17-v002-'+stem,parent_version:b.parent_version,before_view_id:b.before_view_id,changes,type:'visual',stem,case_id:stem,independent_case:false,width:isExample?400:1200,height:isExample?240:1600,purpose:'A17 01 readable subtitle visual refinement'});
  const {bytes,body,text,json,...r}=result;write(stem+'-render-result-v002.json',r);console.log(JSON.stringify({stem,ok:r.ok,status:r.http_status,meta:r.meta_path,image:r.image_path,error:r.error_summary}));
  if(!result.ok||result.dimension_error)throw Error('Actual render failure '+stem);
 }
})().catch(e=>{write('production-error-v002.json',{at:new Date().toISOString(),error:String(e)});process.exitCode=1;});
