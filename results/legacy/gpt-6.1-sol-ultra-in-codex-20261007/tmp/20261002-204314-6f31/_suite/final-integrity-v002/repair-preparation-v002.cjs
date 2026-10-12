'use strict';
const fs=require('fs'),path=require('path');
for(const n of [29,30]){
const source=path.join(__dirname,'audit-'+n+'-v001.cjs');
const s=fs.readFileSync(source,'utf8').replaceAll("'integrity-'+n+'-v001.json'","'integrity-"+n+"-v002.json'");
fs.writeFileSync(path.join(__dirname,'audit-'+n+'-v002.cjs'),s,{flag:'wx'});
}
fs.writeFileSync(path.join(__dirname,'attempts-v001.json'),JSON.stringify({created_at:new Date().toISOString(),new_http:0,new_image_views:0,failures:[{script:'audit-29-v001.cjs',error:'ReferenceError n is not defined at immutable output naming. Read-only checks completed in memory but report was not saved.',cause:'Preparation script placed loop variable n inside a generated string instead of resolving it while generating.',recovery:'Preserved v001 scripts; generated fixed audit-29-v002.cjs and audit-30-v002.cjs with literal unique output names.'}],side_effects:'No public files, outputs, images, ledger, state, or HTTP modified by failed run.'},null,2)+'\n',{flag:'wx'});
console.log('Prepared corrected audit scripts, original failed versions retained.');
