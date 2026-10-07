'use strict';
const fs=require('node:fs'),path=require('node:path');
let source=fs.readFileSync(path.join(__dirname,'build-travel-v001.cjs'),'utf8');
const edits=[
  ["txt(x,y-2,w,line,20,'#FFFFFF',true,34);","c.text(x,y,w,30,line,20,'#FFFFFF',{bold:true,align:'center',...single});"],
  ["travel-card-v001.snapshot","travel-card-v002.snapshot"],
  ["travel-card-content-v001.json","travel-card-content-v002.json"],
  ["version_id:'A07-travel-v001'","version_id:'A07-travel-v002'"],
  ["type:'baseline',stem:'travel-card'","type:'visual',parent_version:'A07-travel-v001',before_view_id:'A07-view-000001',changes:'Center R/B/G letters in every colored line chip after actual baseline edge-crowding observation',stem:'travel-card'"],
  ["awaiting actual baseline view","awaiting actual revised image view"]
];
for(const [old,next] of edits){if(!source.includes(old))throw Error('Missing exact edit target: '+old);source=source.split(old).join(next);}
fs.writeFileSync(path.join(__dirname,'build-travel-v002.cjs'),source,{flag:'wx'});
fs.writeFileSync(path.join(__dirname,'travel-edit-v002.json'),JSON.stringify({version_id:'A07-travel-v002',parent_version:'A07-travel-v001',before_view_id:'A07-view-000001',edits,source:'build-travel-v001.cjs',result:'build-travel-v002.cjs'},null,2)+'\n',{flag:'wx'});
