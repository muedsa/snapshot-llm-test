const fs=require('node:fs'),path=require('node:path');
const p=__dirname,src=path.join(p,'case-07-v001.snapshot');
const d=fs.readFileSync(src,'utf8');
const fixed=d.replace(/fontSize="27"/g,'fontSize="28"');
fs.writeFileSync(path.join(p,'case-07-v002.snapshot'),fixed,{flag:'wx'});
const m=JSON.parse(fs.readFileSync(path.join(p,'case-07-metadata-v001.json'),'utf8'));
m.created_at=new Date().toISOString();m.parent_version='case-07-v001.snapshot';m.pre_render_static_change='3 descriptive/time text widgets were 27px; raised to28px to comply with shared minimum body size before any render. This is not a visual iteration.';
fs.writeFileSync(path.join(p,'case-07-metadata-v002.json'),JSON.stringify(m,null,2),{flag:'wx'});
console.log(JSON.stringify({candidate:'case-07-v002.snapshot',metadata:'case-07-metadata-v002.json'}));
