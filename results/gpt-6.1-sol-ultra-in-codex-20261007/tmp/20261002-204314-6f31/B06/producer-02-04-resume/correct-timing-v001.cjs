'use strict';
const fs=require('fs'),path=require('path');
const source=path.join(__dirname,'case-04-metadata-v002.json'),m=JSON.parse(fs.readFileSync(source,'utf8'));
m.modification_started_at='2026-10-07T04:12:24Z';
m.modification_timing_note='Actual clock read immediately before writing the fix script. Image viewing began at04:11:55Z; these are separate events. Original v002 metadata used view start in the modification field and is preserved as an erroneous historical file.';
m.supersedes_metadata=source;
fs.writeFileSync(path.join(__dirname,'case-04-metadata-v002-corrected-v001.json'),JSON.stringify(m,null,2)+'\n',{flag:'wx'});
console.log('Saved corrected timing derivative; all DSL and data unchanged.');
