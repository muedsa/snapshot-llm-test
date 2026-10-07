'use strict';
const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'../../../..'),s=require(path.join(root,'tmp/20261002-204314-6f31/_suite/suite.cjs'));
(async()=>{
for(const [name,w,h] of [['desktop',1440,900],['stage',1920,1080]]){
  const original=fs.readFileSync(path.join(__dirname,name+'-v001.snapshot'),'utf8');
  // The only structural element unique to both failed large layouts is their
  // horizontal Transform separator. Test the same finite-size rectangle.
  const re=/<Transform matrix="\(1,0,0,0,0,1,0,0,0,0,1,0,0,-[12](?:\.5)?,0,1\)" origin="\(0,0\)">(<Container width="\d+" height="[34]" color="#0A8686"\/>)(<\/Transform>)/;
  if(!re.test(original))throw new Error('Cannot isolate separator');
  const dsl=original.replace(re,'$1');
  fs.writeFileSync(path.join(__dirname,name+'-v003-separator-diagnostic.snapshot'),dsl,{flag:'wx'});
  const r=await s.render('A12',dsl,{version_id:'A12-v003-'+name,parent_version:'A12-v002-'+name,type:'alternative',stem:name,width:w,height:h,case_id:name,purpose:'Controlled diagnostic: replace horizontal Transform divider by equivalent plain Container rectangle after repeated true500; cause still unconfirmed',changes:'Replace separator Transform subtree with same finite plain Container rectangle.'});
  console.log(JSON.stringify({name,ok:r.ok,meta_path:r.meta_path,image_path:r.image_path,error:r.error_summary}));
}
})().catch(e=>{console.error(e);process.exitCode=1});
