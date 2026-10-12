'use strict';
const fs=require('fs'),path=require('path'),dir=__dirname;
const prior=path.join(dir,'../final-integrity-prep-v001');
const source=fs.readFileSync(path.join(prior,'audit-readonly-v001.cjs'),'utf8');
for(const [name,n,scope] of [['audit-29-v001.cjs',29,'29 completed tasks; B06 candidate separately checked.'],['audit-30-v001.cjs',30,'All30 completed tasks after B06 publication.']]){
let s=source.replace("'final-integrity-prep-v001'","'final-integrity-v002'").replace('catalog.tasks.slice(0,28)','catalog.tasks.slice(0,'+n+')').replaceAll("'/root/b04_cases_02_04'","'/root/b06_cases_02_04_resume'").replace('A01-A24 and B01-B04 completed only. B05-B06 excluded.',scope).replace('This is not a new 104-image perceptual review. This final-integrity audit opened no images; it independently revalidates existing file evidence.','This is not a new suite-image perceptual review. This file audit opened no images; it independently revalidates recorded view evidence and current bytes.').replaceAll("'integrity-audit-v001.json'","'integrity-'+n+'-v001.json'");
fs.writeFileSync(path.join(dir,name),s,{flag:'wx'});
}
const raster=fs.readFileSync(path.join(prior,'raster-audit-v001.py'),'utf8').replace("/'final-integrity-prep-v001'","/'final-integrity-v002'").replace("['B01','B02','B03','B04']","['B01','B02','B03','B04','B05','B06']").replaceAll("'/root/b04_cases_02_04'","'/root/b06_cases_02_04_resume'").replace('for104 preserved final files','for124 preserved final files').replace('for 104 preserved final files','for124 preserved final files');
fs.writeFileSync(path.join(dir,'raster-124-v001.py'),raster,{flag:'wx'});
fs.writeFileSync(path.join(dir,'suite-state-at-incremental-read-v001.json'),fs.readFileSync(path.join(process.cwd(),'outputs','20261002-204314-6f31','_suite','suite-state.json')),{flag:'wx'});
console.log(JSON.stringify({directory:dir,prepared:['audit-29-v001.cjs','audit-30-v001.cjs','raster-124-v001.py']}));
