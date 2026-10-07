'use strict';
const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'../../../..'),s=require(path.join(root,'tmp/20261002-204314-6f31/_suite/suite.cjs'));
const draft=JSON.parse(fs.readFileSync(path.join(__dirname,'reconstruction-audit-draft-v001.json'),'utf8'));
const before=JSON.parse(fs.readFileSync(path.join(__dirname,'before-actual-reviews-v001.json'),'utf8'));
let dsl=fs.readFileSync(path.join(__dirname,'reconstructed-v001.snapshot'),'utf8');
const updates=[{id:'title',size:32,y:32},{id:'chart_title',size:22,y:331},{id:'activity_title',size:22,y:331},{id:'table_title',size:22,y:641},...Array.from({length:3},(_,i)=>({id:'kpis['+i+'].value',size:32,y:193}))];
for(const u of updates){
 const field=draft.text_map.find(f=>f.id===u.id),p=field.position;
 const old=`<Positioned left="${p.x}" top="${p.y}" width="${p.width}" height="${p.height}"><Text fontFamily="Inter,Noto Sans CJK SC" fontSize="${field.font_size}"`;
 const next=`<Positioned left="${p.x}" top="${u.y}" width="${p.width}" height="${p.height}"><Text fontFamily="Inter,Noto Sans CJK SC" fontSize="${u.size}"`;
 if(!dsl.includes(old))throw new Error('Missing expected field '+u.id);
 dsl=dsl.replace(old,next);field.position.y=u.y;field.font_size=u.size;
}
dsl=dsl.replace(/#1B2D45/g,'#18283F');draft.palette.ink='#18283F';
for(const t of draft.text_map)if(t.color==='#1B2D45')t.color='#18283F';
draft.status='awaiting_actual_v002_review';draft.font_correction={before_actual_metrics:path.join(__dirname,'text-metrics-before-v001.json'),updates,source_exact_primary_ink:'#18283F',reason:'Actual original/v001 pureink bounding boxes show20px main and11..14px section width excess; only approximate type sizes/baselines corrected. All structural/plot coordinates and source strings unchanged.'};
fs.writeFileSync(path.join(__dirname,'reconstructed-v002.snapshot'),dsl,{flag:'wx'});
fs.writeFileSync(path.join(__dirname,'reconstruction-audit-draft-v002.json'),JSON.stringify(draft,null,2)+'\n',{flag:'wx'});
(async()=>{const r=await s.render('A15',dsl,{version_id:'A15-v002',parent_version:'A15-v001',type:'visual',stem:'reconstructed',width:1440,height:900,before_view_id:before.baseline_view_id,changes:'Use32px main/KPI values and22px section headings with1–2px baseline adjustments; match actual primaryink#18283F. Geometry/charts/rows/source strings unchanged.',purpose:'A15 true visual typography refinement after original/crops and pureink bbox comparison'});console.log(JSON.stringify({ok:r.ok,meta_path:r.meta_path,image_path:r.image_path,error:r.error_summary}));})().catch(e=>{console.error(e);process.exitCode=1});
