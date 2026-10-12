'use strict';
// Preserve v001 unchanged. v002 adds direct schema support and keeps geometry rules.
const fs=require('node:fs'),path=require('node:path');
let text=fs.readFileSync(path.join(__dirname,'audit-geometry-v001.cjs'),'utf8');
text=text.replace("const add=(type,details)=>issues.push({type,...details});","const add=(type,details)=>issues.push({...details,type});");
text=text.replace("box:e.box ?? e.label_box ?? e.label?.box,","box:e.box ?? e.label_box ?? e.label?.box ?? e.label,");
text=text.replace("fontSize:e.font_size ?? e.fontSize ?? e.label?.font_size ?? e.label?.fontSize,","fontSize:e.font_size ?? e.fontSize ?? e.label?.font_size ?? e.label?.fontSize ?? raw.label_style?.font_size,");
text=text.replace("declared:meta.plot ?? meta.plot_bounds ?? null","declared:meta.plot ?? meta.plot_bounds ?? meta.map ?? null");
text=text.replace("declared:meta.highest_three??meta.top3??meta.highest3??null","declared:meta.highest_three??meta.top3??meta.highest3??meta.top3_ids??null");
text=text.replaceAll('A20-independent-geometry-v001','A20-independent-geometry-v002').replaceAll('geometry-selftest-v001.json','geometry-selftest-v002.json').replaceAll("'-independent-audit-v001.json'","'-independent-audit-v002.json'");
fs.writeFileSync(path.join(__dirname,'audit-geometry-v002.cjs'),text,{flag:'wx'});
console.log('Created immutable geometry v002; geometry collision/spacing/intersection rules unchanged.');
