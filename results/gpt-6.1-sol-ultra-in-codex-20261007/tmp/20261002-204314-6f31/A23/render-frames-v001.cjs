const fs=require('fs'),path=require('path'),s=require('../_suite/suite.cjs');
(async()=>{
 const data=JSON.parse(fs.readFileSync(path.join(__dirname,'frame-production/frame-data.json'),'utf8'));
 const results=[];
 for(const f of data.frames){
  const dsl=fs.readFileSync(f.dsl_path,'utf8');
  const r=await s.render('A23',dsl,{version_id:'A23-'+f.id+'-v001',stem:f.id,width:600,height:600,type:'baseline',purpose:'Twelve fixed-size units converging, transparent keyframe '+f.order});
  const entry={id:f.id,version_id:r.version_id,ok:r.ok,meta_path:r.meta_path,image_path:r.image_path,error:r.error_summary};
  results.push(entry); console.log(JSON.stringify(entry));
  if(!r.ok||r.dimension_error)throw Error('Actual service failure; preserve responses and inspect before retry: '+JSON.stringify(entry));
 }
 fs.writeFileSync(path.join(__dirname,'render-frame-manifest-v001.json'),JSON.stringify({task_id:'A23',frames:results},null,2)+'\n',{flag:'wx'});
})();
