'use strict';
const fs=require('node:fs');
const s=require('../_suite/suite.cjs');
(async()=>{
  for(const [stem,width,height] of [['agenda-wide',1920,1200],['agenda-mobile',720,1280]]){
    const r=await s.render('A02',fs.readFileSync(`${__dirname}/${stem}-v001.snapshot`,'utf8'),{version_id:`A02-${stem}-v001`,type:'baseline',stem,width,height});
    s.taskCheckpoint('A02',{resume_notes:`${stem} baseline rendered; actual image inspection pending`,checkpoint:`rendered-A02-${stem}-v001`});
    s.writeTaskMetrics('A02');
    console.log(JSON.stringify({stem,ok:r.ok,status:r.http_status,image_path:r.image_path,meta_path:r.meta_path,request_id:r.id,dimensions:r.png_dimensions,error:r.error_summary}));
  }
})().catch(e=>{console.error(e);process.exitCode=1;});
