'use strict';
const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'../../../..'),s=require(path.join(root,'tmp/20261002-204314-6f31/_suite/suite.cjs'));
(async()=>{
  for(const [name,request,w,h] of [['desktop','000003',1440,900],['stage','000004',1920,1080]]){
    const dsl=fs.readFileSync(path.join(__dirname,name+'-v001.snapshot'),'utf8');
    const r=await s.render('A12',dsl,{version_id:'A12-v002-'+name,parent_version:'A12-v001-'+name,type:'retry',retry_of:'A12-request-'+request,stem:name,width:w,height:h,case_id:name,purpose:'Retry identical DSL after actual 500 INTERNAL_ERROR with no Retry-After header'});
    console.log(JSON.stringify({name,ok:r.ok,meta_path:r.meta_path,http_status:r.http_status,image_path:r.image_path,error:r.error_summary}));
  }
})().catch(e=>{console.error(e);process.exitCode=1});
