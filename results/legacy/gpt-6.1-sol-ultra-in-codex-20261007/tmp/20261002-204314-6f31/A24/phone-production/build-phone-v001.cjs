'use strict';
// A24 phone production: pure DSL + records only. No HTTP, render, view, output or suite-state writes.
const fs = require('node:fs'), path = require('node:path'), crypto = require('node:crypto');
const {Canvas, DEFAULT_FONT} = require('../../_suite/dsl.cjs');
const dir = __dirname, created = new Date().toISOString();
const schedulePath = path.resolve(dir, '../schedule-analysis/schedule.json');
const inputPath = path.resolve(dir, '../../../../tasks/A24-release-plan-capstone/inputs/release.json');
const hash = b => crypto.createHash('sha256').update(b).digest('hex');
const scheduleBytes = fs.readFileSync(schedulePath), inputBytes = fs.readFileSync(inputPath);
const schedule = JSON.parse(scheduleBytes), input = JSON.parse(inputBytes);
const save = (name, value) => fs.writeFileSync(path.join(dir,name), typeof value === 'string' ? value : JSON.stringify(value,null,2)+'\n', {flag:'wx'});
const expectedIds = Array.from({length:12},(_,i)=>'R'+String(i+1).padStart(2,'0'));
if(schedule.source_input_sha256 !== hash(inputBytes)) throw Error('Canonical source input hash mismatch');
if(schedule.makespan_minutes !== 260 || schedule.finish_clock !== '13:20' || schedule.deadline_buffer_minutes !== 160) throw Error('Parent-confirmed summary differs');
if(schedule.start !== input.start || schedule.deadline !== input.deadline) throw Error('Start/deadline differs from original input');
if(!Array.isArray(schedule.tasks) || schedule.tasks.length !== 12 || new Set(schedule.tasks.map(t=>t.id)).size !==12) throw Error('Task count/uniqueness');
const sourceById = new Map(input.tasks.map(t=>[t.id,t]));
const rows = schedule.tasks.map(t=>{
 const original = sourceById.get(t.id);
 if(!original || t.label !== original.label || t.minutes !== original.minutes || JSON.stringify(t.depends)!==JSON.stringify(original.depends) || !original.teams.includes(t.team)) throw Error('Source task mismatch '+t.id);
 if(t.end_minute-t.start_minute !== original.minutes) throw Error('Duration mismatch '+t.id);
 const clock = m => {const q=540+m;return String(Math.floor(q/60)).padStart(2,'0')+':'+String(q%60).padStart(2,'0');};
 if(t.start_clock !== clock(t.start_minute) || t.end_clock !== clock(t.end_minute)) throw Error('Clock mismatch '+t.id);
 return {...t};
}).sort((a,b)=>a.start_minute-b.start_minute || a.id.localeCompare(b.id));
if(expectedIds.some(id=>!rows.find(t=>t.id===id)) || rows[0].id!=='R01' || rows[1].id!=='R02') throw Error('Ordering/coverage');
const dependencyChecks = rows.flatMap(t=>t.depends.map(id=>({task:t.id,depends_on:id,pass:rows.find(p=>p.id===id).end_minute<=t.start_minute})));
if(dependencyChecks.some(d=>!d.pass)) throw Error('Dependency check');
const conflicts=[];
for(const team of input.teams){ const lane=rows.filter(t=>t.team===team).sort((a,b)=>a.start_minute-b.start_minute); for(let i=1;i<lane.length;i++) if(lane[i-1].end_minute>lane[i].start_minute) conflicts.push([lane[i-1].id,lane[i].id]); }
if(conflicts.length) throw Error('Resource conflict');
if(JSON.stringify(schedule.risks)!==JSON.stringify(input.risks)) throw Error('Risk source mismatch');
const palette={ink:'#18373C',background:'#F2F5F1',design:'#248C91',engineering:'#DFAC50',white:'#FFFFFF',alternate:'#F7F9F5',muted:'#5B726E',risk:'#E5EEEA',rule:'#D4E1DB',design_text:'#176D70',engineering_text:'#685127'};
const c = new Canvas(720,1280,{background:palette.background,font:DEFAULT_FONT});
const elements=[];
function shape(id,x,y,w,h,color,options={}){ c.rect(x,y,w,h,color,options);elements.push({id,type:'shape',x,y,width:w,height:h,color,options}); }
function text(id,x,y,w,h,value,size=20,color=palette.ink,options={}){
 const actual={lineHeight:1.03,maxLines:1,softWrap:false,...options};
 c.text(x,y,w,h,value,size,color,actual);elements.push({id,type:'text',x,y,width:w,height:h,text:String(value),font_size_px:size,font_family:DEFAULT_FONT,color,options:actual});
}
text('brand',36,28,648,37,'叠光 · 发布演练',28,palette.ink,{bold:true});
text('release-date',36,73,330,28,schedule.planning_date.replaceAll('-','.'),21,palette.muted);
text('release-window',390,73,294,28,'09:00 至 16:00',21,palette.muted,{align:'END'});
text('title',36,108,648,47,'发布日行动卡',38,palette.ink,{bold:true});
shape('summary-panel',36,164,648,102,palette.ink,{radius:18});
shape('summary-divider',322,181,1,61,'#466264');
text('finish-label',56,176,242,26,'预计完成',20,palette.background);
text('finish-value',56,205,242,52,schedule.finish_clock,44,palette.white,{bold:true});
text('buffer-label',348,176,312,26,'至 16:00 截止剩余',20,palette.background);
text('buffer-value',348,207,312,48,schedule.deadline_buffer_minutes+' 分钟',36,palette.white,{bold:true});
text('list-heading',36,282,348,30,'12 项行动 · 按开工顺序',24,palette.ink,{bold:true});
text('list-order',486,286,198,27,'同刻可并行',20,palette.muted,{align:'END'});
const rowMap=[];
rows.forEach((t,i)=>{
 const y=320+i*58,accent=t.team==='design'?palette.design:palette.engineering,teamColor=t.team==='design'?palette.design_text:palette.engineering_text;
 shape(t.id+'-row',36,y,648,56,i%2?palette.alternate:palette.white,{radius:8});
 shape(t.id+'-team-stripe',36,y+8,4,40,accent,{radius:2});
 text(t.id+'-id',52,y+2,60,26,t.id,22,palette.ink,{bold:true});
 text(t.id+'-time',128,y+2,280,27,t.start_clock+' — '+t.end_clock,23,palette.ink,{bold:true});
 text(t.id+'-duration',518,y+3,142,26,t.minutes+' min',20,palette.muted,{align:'END'});
 text(t.id+'-label',128,y+29,366,26,t.label,22,palette.ink);
 text(t.id+'-team',518,y+30,142,26,t.team,20,teamColor,{align:'END',bold:true});
 rowMap.push({order:i+1,id:t.id,label:t.label,team:t.team,minutes:t.minutes,start_minute:t.start_minute,end_minute:t.end_minute,start_clock:t.start_clock,end_clock:t.end_clock,depends:[...t.depends],bounds:{x:36,y,width:648,height:56},text_element_ids:[t.id+'-id',t.id+'-time',t.id+'-duration',t.id+'-label',t.id+'-team']});
});
shape('risk-panel',36,1030,648,224,palette.risk,{radius:16});
text('risk-heading',52,1048,608,30,'风险 / 执行提醒',24,palette.ink,{bold:true});
const riskMap=[];
schedule.risks.forEach((risk,i)=>{
 const y=1084+i*54,title=risk.task+' · '+risk.impact;
 text(risk.id+'-impact',52,y,608,25,title,20,palette.ink,{bold:true});
 text(risk.id+'-mitigation',52,y+25,608,25,risk.mitigation,20,palette.ink);
 riskMap.push({id:risk.id,task:risk.task,original_impact:risk.impact,original_mitigation:risk.mitigation,displayed_title:title,displayed_mitigation:risk.mitigation,text_element_ids:[risk.id+'-impact',risk.id+'-mitigation']});
});
const allWithin=elements.every(e=>e.x>=0&&e.y>=0&&e.width>=0&&e.height>=0&&e.x+e.width<=720&&e.y+e.height<=1280);
const texts=elements.filter(e=>e.type==='text'),minimumFont=Math.min(...texts.map(e=>e.font_size_px));
const textBoxOverlaps=[];
for(let i=0;i<texts.length;i++)for(let j=i+1;j<texts.length;j++){
 const a=texts[i],b=texts[j];if(Math.min(a.x+a.width,b.x+b.width)>Math.max(a.x,b.x)&&Math.min(a.y+a.height,b.y+b.height)>Math.max(a.y,b.y)) textBoxOverlaps.push([a.id,b.id]);
}
if(!allWithin || minimumFont<20 || textBoxOverlaps.length) throw Error('Layout bounds/font/text-box overlap '+JSON.stringify(textBoxOverlaps));
const dsl=c.toString();
if(/<Image\b|<Svg\b|<Canvas\b/.test(dsl)) throw Error('External/prefab asset forbidden');
const layout={schema_version:1,task_id:'A24',run_id:'20261002-204314-6f31',version_id:'phone-v001',producer:'/root/a20_geometry_audit',created_at:created,status:'Pure DSL draft with computational content/bounds checks. Actual service rendering and visual inspection pending and owned by root.',canvas:{width:720,height:1280},brand:'叠光 · 发布演练',planning_date:schedule.planning_date,timezone:'Asia/Shanghai / UTC+08:00',window:{start:schedule.start,deadline:schedule.deadline,displayed:'09:00 至 16:00'},summary:{makespan_minutes:schedule.makespan_minutes,completion_time:schedule.finish_clock,remaining_buffer_minutes:schedule.deadline_buffer_minutes,optimality_claim:false},canonical_schedule:{path:schedulePath,sha256:hash(scheduleBytes),source_input_path:inputPath,source_input_sha256:hash(inputBytes),field_map:{row_start:'tasks[].start_minute',row_end:'tasks[].end_minute',display_start:'tasks[].start_clock',display_end:'tasks[].end_clock',actual_team:'tasks[].team'},ordering:'Ascending start_minute; ties ascending id, matching canonical display_tie_break.'},palette,font_family:DEFAULT_FONT,rows:rowMap,risks:riskMap,elements,computational_checks:{task_count:rows.length,unique_ids:true,original_task_content_preserved:true,duration_checks_pass:true,dependencies_pass:dependencyChecks.every(d=>d.pass),dependency_checks:dependencyChecks,resource_conflicts:conflicts,all_declared_element_bounds_inside_canvas:allWithin,minimum_font_px:minimumFont,text_element_count:texts.length,text_box_overlaps:textBoxOverlaps,pure_dsl_no_external_assets:true},visual_qa:{rendered:false,viewed:false,claim:'Bounds/text-box checks do not prove glyph fit or visual quality. Root must inspect actual 720×1280 service PNG, especially engineering, long Chinese labels, summary and Retry-After line.'},documentation:{reused_guide_cache:path.resolve(dir,'../../_suite/shared-doc-000001-response.txt'),reused_parser_cache:path.resolve(dir,'../../_suite/shared-doc-000004-readable.txt'),reused_font_cache:path.resolve(dir,'../../_suite/shared-fonts-000001-readable.txt'),helper_path:path.resolve(dir,'../../_suite/dsl.cjs'),new_document_http_requests:0,applied_dsl_tags:['Snapshot','Container','Stack','Positioned','Text','Raw/CDATA'],applied_attributes:['fontFamily','fontSize','fontStyle','height','maxLines','softWrap','textAlign','borderRadius']},dsl_path:path.join(dir,'action-card-v001.snapshot'),dsl_sha256:hash(dsl),all_writes_finished:true};
const filenames=['action-card-v001.snapshot','action-card-layout-v001.json','build-result-v001.json'];
for(const name of filenames) if(fs.existsSync(path.join(dir,name))) throw Error('Immutable output already exists: '+name);
save(filenames[0],dsl);save(filenames[1],layout);
const result={created_at:new Date().toISOString(),version_id:'phone-v001',script_path:__filename,dsl_path:layout.dsl_path,dsl_sha256:layout.dsl_sha256,layout_path:path.join(dir,filenames[1]),canonical_schedule_path:schedulePath,canonical_schedule_sha256:layout.canonical_schedule.sha256,row_order:rowMap.map(t=>t.id),task_count:rows.length,risk_count:riskMap.length,minimum_font_px:minimumFont,all_declared_bounds_inside_canvas:allWithin,text_box_overlaps:textBoxOverlaps,all_writes_finished:true,no_render_or_view:true};
save(filenames[2],result);console.log(JSON.stringify(result));
