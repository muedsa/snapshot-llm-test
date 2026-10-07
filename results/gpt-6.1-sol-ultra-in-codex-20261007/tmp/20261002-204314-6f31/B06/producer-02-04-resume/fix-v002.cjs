'use strict';
const fs=require('fs'),path=require('path');
const old=path.resolve(__dirname,'..','producer-02-04'),source=path.join(old,'case-04-v001.snapshot');
let dsl=fs.readFileSync(source,'utf8');
const edits=[
['<Positioned left="69" top="250" width="375" height="45">','<Positioned left="150" top="250" width="375" height="45">'],
['<Positioned left="967" top="836" width="122" height="39">','<Positioned left="1055" top="836" width="122" height="39">']
];
for(const [a,b] of edits){if(dsl.split(a).length!==2)throw new Error('Expected one match: '+a);dsl=dsl.replace(a,b);}
fs.writeFileSync(path.join(__dirname,'case-04-v002.snapshot'),dsl,{flag:'wx'});
const meta=JSON.parse(fs.readFileSync(path.join(old,'case-04-metadata-v001.json'),'utf8'));
meta.creative_started_at=null;
meta.creative_time_note='Previous producer saved only build execution start; actual creative starting time was not measured.';
meta.created_at=new Date().toISOString();meta.parent_dsl=source;meta.parent_metadata=path.join(old,'case-04-metadata-v001.json');
meta.modification_started_at='2026-10-07T04:11:55Z';meta.modification_timing_note='Actual view tool batch began at this recorded clock time; modification followed inspection. No elapsed creative estimate inferred.';
meta.view_evidence='visual-reviews-v001.json#case-04';
meta.revisions=['Move cumulative-currency label from x69 to x150 so its glyphs no longer overlap 2000 y-axis tick.','Move month-end unit from x967 to x1055 so it no longer collides with 24-month tick.'];
meta.checks={data_checked:true,geometry_computed:true,rendered:false,visual_passed:null};
meta.visual_revision_status='Old image actually viewed; changed DSL awaiting real render and comparison. Not yet a completed visual iteration.';
fs.writeFileSync(path.join(__dirname,'case-04-metadata-v002.json'),JSON.stringify(meta,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({dsl:path.join(__dirname,'case-04-v002.snapshot'),metadata:path.join(__dirname,'case-04-metadata-v002.json'),data_values_unchanged:true,month_zero_A:100,month_zero_B:0}));
