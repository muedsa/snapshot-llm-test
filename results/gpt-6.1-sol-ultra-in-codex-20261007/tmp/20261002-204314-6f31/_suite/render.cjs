const fs=require('fs'),path=require('path');const s=require('./suite.cjs');
(async()=>{
const [task,file,version,type='baseline',parent='',caseId='',roundId='']=process.argv.slice(2);
if(!task||!file||!version)throw new Error('Usage: render.cjs TASK FILE VERSION [TYPE] [PARENT] [CASE] [ROUND]');
const dsl=fs.readFileSync(file,'utf8');const dirs=s.taskDirs(task);
const v=s.saveVersion(task,dsl,{version_id:version,parent_version:parent||null,type,case_id:caseId||null,round_id:roundId||null});
const r=await s.request({task,type:'render',url:s.createSuite().config.service_base_url+'/snapshot',method:'POST',headers:{'Content-Type':'text/plain; charset=utf-8'},body:dsl,dsl:true,expect_png:true,case_id:caseId||null,round_id:roundId||null,purpose:version});
const meta={...r};delete meta.bytes;delete meta.body;delete meta.text;delete meta.json;meta.version=v;
const mp=path.join(dirs.temp,version+'-render.json');fs.writeFileSync(mp,JSON.stringify(meta,null,2),{flag:'wx'});
s.iteration(task,{version_id:version,parent_version:parent||null,type,image_path:r.ok?r.response_file:null,request_id:r.id,completed:false,error:r.error_summary,case_id:caseId||null,round_id:roundId||null});
s.taskCheckpoint(task,{resume_notes:'Rendered '+version+'. Needs real image view/acceptance.',checkpoint:'rendered-'+version});s.writeTaskMetrics(task);s.aggregate();
console.log(JSON.stringify({ok:r.ok,status:r.http_status,image:r.response_file,metadata:mp,dimensions:r.png_dimensions,error:r.error_summary,server_timing:r.server_timing,retry_after:r.retry_after}));
})().catch(e=>{console.error(e);process.exitCode=1;});
