'use strict';
const fs=require('fs'),path=require('path');
fs.writeFileSync(path.join(__dirname,'audit-30-v004.cjs'),fs.readFileSync(path.join(__dirname,'audit-30-v003.cjs'),'utf8').replaceAll('integrity-30-v003.json','integrity-30-v004.json'),{flag:'wx'});
const source=fs.readFileSync(path.join(__dirname,'pointer-and-overview-v001.cjs'),'utf8').replace("['index.md','gallery.html','snapshot-usage.md']","['index.md','gallery.html','snapshot-usage.md','README.md','final-audit.md']");
fs.writeFileSync(path.join(__dirname,'pointer-and-overview-v002.cjs'),source,{flag:'wx'});
console.log('Prepared new immutable byte/link verification reports.');
