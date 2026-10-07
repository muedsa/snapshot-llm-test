'use strict';
const fs=require('node:fs'),path=require('node:path'),dir=__dirname;
let source=fs.readFileSync(path.join(dir,'audit-final-three-v001.cjs'),'utf8');
const replacements=[
 ['const a=p.texts[i];return{id:m.id,pass:a&&','const candidates=p.texts.filter(a=>boxeq(a.box,m.box)&&a.raw===m.text);const a=candidates[0];return{id:m.id,pass:candidates.length===1&&a&&'],
 ['const a=p.shapes[i];return{id:m.id,pass:a&&','const candidates=p.shapes.filter(a=>boxeq(a.box,m.box)&&a.style.color===m.color);const a=candidates[0];return{id:m.id,pass:candidates.length===1&&a&&'],
 ['Math.max(...lineIndexes)<Math.min(...cardIndexes)',"['design','engineering'].every(team=>{const y=team==='design'?368:750,lanes=lineIndexes.filter(i=>near(boardParsed.positioned[i].box[1],y)),cards=boardAfter.time_blocks.filter(t=>t.team===team).map(t=>boardParsed.positioned.findIndex(p=>p.kind==='shape'&&boxeq(p.box,t.annotation_box)));return lanes.length===6&&cards.length===6&&Math.max(...lanes)<Math.min(...cards);})"],
 ['All twelve leaders precede all annotation cards.','For each separate lane, all six leaders precede all six annotation cards in that lane.'],
 ['final-three-source-audit-v001.json','final-three-source-audit-v002.json'],
 ['final-three-source-audit-v001.md','final-three-source-audit-v002.md'],
 ['12leader先画再画卡片','各泳道6条leader先画再画该泳道卡片']
];
for(const [old,value]of replacements){if(!source.includes(old))throw Error('Repair pattern missing: '+old);source=source.split(old).join(value);}
const marker='const evidencePaths=';
if(!source.includes(marker))throw Error('Supplement marker missing');
const extra="const regression=json('time-band-regression-v001.json');\ncheck('actual-PNG-time-band-regression-hash-and-zero-difference',regression.task_id==='A24'&&regression.original_sha256===beforePNG.sha256&&regression.refined_sha256===finals.find(f=>f.stem==='execution-board').PNG.sha256&&regression.all_pass===true&&regression.regions.length===2&&regression.regions.every(r=>r.pixels===117344&&r.different_RGBA_pixels===0&&r.unchanged===true&&(r.box[2]-r.box[0])*(r.box[3]-r.box[1])===r.pixels),{actual_parent_read_only_PNG_audit:regression,total_RGBA_pixels:regression.regions.reduce((s,r)=>s+r.pixels,0),new_independent_views:0});\n";
source=source.replace(marker,extra+marker);
source=source.replace("'root-final-review-v001.json','requests.jsonl'","'root-final-review-v001.json','time-band-regression-v001.json','requests.jsonl'");
source=source.replace("producer_metadata_interpretation:","prior_audit_false_positive_correction:{prior_file:'final-three-source-audit-v001.json',cause:'Map records construction order while source v002 paint order was changed. Ordinal pairing falsely rejected valid elements; source/map are now uniquely paired by geometry/content/style. Leader layer order is per nonintersecting lane, not global.',prior_failed_checks:3,no_source_artwork_changed:true},producer_metadata_interpretation:");
fs.writeFileSync(path.join(dir,'audit-final-three-v002.cjs'),source,{flag:'wx'});
console.log(JSON.stringify({repaired_script:path.join(dir,'audit-final-three-v002.cjs'),failed_sources_preserved:true}));
