const fs=require('node:fs'),path=require('node:path');
const p=path.join(__dirname,'case-09-v001.snapshot');let d=fs.readFileSync(p,'utf8');
d=d.replace(/<Positioned left="748" top="398"[\s\S]*?<\/Positioned>/,'').replace('<Positioned left="748" top="445" width="284" height="42">','<Positioned left="640" top="677" width="360" height="33">');
fs.writeFileSync(path.join(__dirname,'case-09-v002.snapshot'),d,{flag:'wx'});
fs.writeFileSync(path.join(__dirname,'iterate-09-v002.json'),JSON.stringify({type:'visual',parent_version:'B01-version-000003',before_view_id:'B01-view-000003',changes:'删除车架内部被斜杆穿过的重复60 SEC CHECK，将检查图·非维修手册移到640,677底部空隙。'},null,2)+'\n',{flag:'wx'});
