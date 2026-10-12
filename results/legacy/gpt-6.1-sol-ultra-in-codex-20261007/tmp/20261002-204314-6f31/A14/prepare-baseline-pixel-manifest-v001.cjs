const fs=require('fs'),path=require('path'),s=require('../_suite/suite.cjs'),d=s.taskDirs('A14');
const j=JSON.parse(fs.readFileSync(path.join(d.temp,'production/batch-audit-draft-v001.json'),'utf8'));
j.cards.forEach((c,i)=>c.image_path=path.join(d.temp,'requests/A14-request-'+String(i+1).padStart(6,'0')+'/response.png'));
fs.writeFileSync(path.join(d.temp,'pixel-manifest-baseline-v001.json'),JSON.stringify(j,null,2)+'\n',{flag:'wx'});
