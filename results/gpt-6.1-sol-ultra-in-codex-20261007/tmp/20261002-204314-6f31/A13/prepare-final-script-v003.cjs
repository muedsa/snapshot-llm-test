const fs=require('fs'),path=require('path');
const source=fs.readFileSync(path.join(__dirname,'prepare-final-set-v002.cjs'),'utf8').replace('local_analysis_script_failures:1,root_review_ids:', 'preliminary:false,local_analysis_script_failures:1,root_review_ids:');
fs.writeFileSync(path.join(__dirname,'prepare-final-set-v003.cjs'),source,{flag:'wx'});console.log('prepare-final-set-v003.cjs');
