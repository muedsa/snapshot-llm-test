const fs=require('fs'),path=require('path'),dir=__dirname;
const old=fs.readFileSync(path.join(dir,'assemble-final-audit-v002.cjs'),'utf8'),fixedKeys=[];
const next=old.replace(/(?<=[{,])(\d+[A-Za-z_][A-Za-z0-9_]*)\s*:/g,(_,key)=>{fixedKeys.push(key);return "'"+key+"':";}).replace('visual-content-audit-final-v002.json','visual-content-audit-final-v003.json');
fs.writeFileSync(path.join(dir,'assembly-failures-v002.json'),JSON.stringify({recorded_at:new Date().toISOString(),script:'assemble-final-audit-v002.cjs',actual_exit_code:1,error:'SyntaxError: Numeric separators are not allowed at the end of numeric literals',cause:'Second numeric-leading object key100_input... remained unquoted after first repair',fixedKeys,final_images_altered:false,render_requests_caused:0},null,2)+'\n',{flag:'wx'});
fs.writeFileSync(path.join(dir,'assemble-final-audit-v003.cjs'),next,{flag:'wx'});console.log(JSON.stringify({fixedKeys}));
