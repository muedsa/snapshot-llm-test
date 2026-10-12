'use strict';
const fs=require('node:fs'),path=require('node:path');
const dir=__dirname,input=path.join(dir,'audit-final-v001.cjs'),output=path.join(dir,'audit-final-v002.cjs');
let text=fs.readFileSync(input,'utf8');
function replaceOnce(from,to){if(text.split(from).length!==2)throw Error('Nonunique/absent checker patch: '+from);text=text.replace(from,to);}
replaceOnce("map:rd+'/layout-map-v001.json'","map:rd+'/layout-map-v002.json'");
text=text.replaceAll('A22-request-000006','A22-request-000007').replaceAll('A22-round-03-dashboard-v001','A22-round-03-dashboard-v002').replaceAll('A22-view-000007','A22-view-000009').replaceAll('req6/v001','req7/v002');
replaceOnce("changeAudit:rd+'/change-audit-final-v001.json'","changeAudit:rd+'/change-audit-final-v001.json',initialSource:base+'/requests/A22-request-000006/input.snapshot',initialMap:rd+'/layout-map-v001.json',refinement:rd+'/label-refinement-v001.json'");
replaceOnce("['font','font_size','color','bold','align'].every(k=>textById[t.id][k]===t[k])","['font','font_size','color','align'].every(k=>textById[t.id][k]===t[k])&&(/^bar-label-/.test(t.id)?textById[t.id].bold===false:textById[t.id].bold===t.bold)");
const addedChecks=`
// Actual req6->req7 visual refinement: exactly21 Text widgets; no shape/data alteration.
const initialSource=bytes.initialSource.toString('utf8'),initialMap=json('initialMap'),refinement=json('refinement'),initialNodes=parse(initialSource),initialTexts=initialNodes.filter(n=>n.type==='text'),initialById=Object.fromEntries(initialMap.texts.map((t,i)=>[t.id,{...t,source:initialTexts[i]}]));
const refinements=initialMap.texts.filter(t=>!same(t,map.texts.find(n=>n.id===t.id))).map(t=>({id:t.id,old:t,new:map.texts.find(n=>n.id===t.id)}));
check('actual_visual_refinement_records_exactly14amounts7months_no_data_shapes_change',refinements.length===21&&refinements.filter(e=>e.id.startsWith('bar-label-')).length===14&&refinements.filter(e=>e.id.startsWith('chart-month-')).length===7&&same(initialMap.shapes,map.shapes)&&same(initialMap.chart,map.chart)&&same(initialMap.table,map.table)&&refinement.changes.length===21&&refinements.every(e=>{const record=refinement.changes.find(c=>c.id===e.id);return record&&same(record.old,e.old)&&same(record.new,e.new);})&&refinement.data_and_shape_geometry_unchanged,{changed_ids:refinements.map(e=>e.id),count:refinements.length});
let refinedSource=initialSource;
for(const item of refinements){const beforeWidget=initialById[item.id].source.raw,afterWidget=textById[item.id].source.raw;if(refinedSource.split(beforeWidget).length!==2)throw Error('Nonunique initial label'+item.id);refinedSource=refinedSource.replace(beforeWidget,afterWidget);}
check('all_source_bytes_outside21_actual_visual_text_refinements_unchanged',refinedSource===source,{initial_request:'A22-request-000006',final_request:'A22-request-000007',all_other_source_bytes_unchanged:refinedSource===source});
check('all14_amount_labels_regular22_same_exact_value_family_color_bounds',map.texts.filter(t=>t.id.startsWith('bar-label-')).length===14&&refinements.filter(e=>e.id.startsWith('bar-label-')).every(e=>same(e.old.box,e.new.box)&&e.old.text===e.new.text&&e.old.font===e.new.font&&e.old.font_size===22&&e.new.font_size===22&&e.old.color===e.new.color&&e.old.bold===true&&e.new.bold===false&&e.new.align===e.old.align));
const staggerEvidence=ind.monthly.map((r,i)=>{const t=textById['chart-month-'+r.month],center=px+pw/7*(i+.5),expected=[center-46,i%2===0?735:756,92,29];return{id:t.id,text:t.source.text,box:t.source.box,expected_box:expected,pass:t.source.text===r.month&&arr(t.source.box,expected)&&Number(t.source.attrs.fontSize)===22&&t.source.attrs.fontFamily===map.main_styles.font&&contain(map.regions.chart,t.source.box)};});
check('seven_original_month_labels_stagger735_756_height29_font22_in_chart',staggerEvidence.every(e=>e.pass),staggerEvidence);
`;
replaceOnce('const result={schema_version:1,task_id:',addedChecks+'\nconst result={schema_version:1,task_id:');
replaceOnce('static_source_evidence:staticEvidence,prior_archive_hashes:','static_source_evidence:staticEvidence,visual_refinement_evidence:refinements.map(e=>({id:e.id,old:e.old,new:e.new})),staggered_month_evidence:staggerEvidence,prior_archive_hashes:');
replaceOnce('Actualaudit script: audit-final-v001.cjs','Actualaudit script: audit-final-v002.cjs');
replaceOnce('All7 axis ticks/grid source widgets remain unchanged.','All7 axis ticks/grid source widgets remain unchanged. Actual21Text visual refinements change14amountlabels to22pxregular and stagger7monthlabels735/756 while preserving exactstrings; allother sourcebytes unchanged.');
fs.writeFileSync(output,text,{flag:'wx'});
console.log(JSON.stringify({prepared:output,original_checker_preserved:input,final_report_names:['final-audit-v001.json','final-audit-v001.md']}));
