'use strict';
const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'../../../..'),s=require(path.join(root,'tmp/20261002-204314-6f31/_suite/suite.cjs'));
(async()=>{
for(const [name,w,h] of [['desktop',1440,900],['stage',1920,1080]]){
  const original=fs.readFileSync(path.join(__dirname,name+'-v001.snapshot'),'utf8');
  const fixed=original.replace(/borderRadius="3"/g,'borderRadius="8"');
  if(fixed===original)throw new Error('No motif corner fix');
  fs.writeFileSync(path.join(__dirname,name+'-v004.snapshot'),fixed,{flag:'wx'});
  const r=await s.render('A12',fixed,{version_id:'A12-v004-'+name,parent_version:'A12-v003-'+name,type:'syntax-fix',stem:name,width:w,height:h,case_id:name,changes:'Change motif rounded border radius from3 to8px, greater than4/5px border widths. All content/coordinates/fonts unchanged; restores original separator.',purpose:'A12 controlled geometry correction of motif radius after actual500 diagnosis'});
  console.log(JSON.stringify({name,ok:r.ok,meta_path:r.meta_path,image_path:r.image_path,error:r.error_summary}));
}
})().catch(e=>{console.error(e);process.exitCode=1});
