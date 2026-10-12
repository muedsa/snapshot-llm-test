'use strict';
const fs=require('node:fs'),path=require('node:path');
const {Canvas}=require('../_suite/dsl.cjs');
const input=path.resolve('tasks/A02-conference-schedule/inputs');
const temp=__dirname;
const venues=JSON.parse(fs.readFileSync(path.join(input,'venues.json'),'utf8'));
const raw=fs.readFileSync(path.join(input,'agenda.csv'),'utf8').trim().split(/\r?\n/);
const headers=raw.shift().split(',');
const minute=t=>{const [h,m]=t.split(':').map(Number);return h*60+m;};
const time=m=>`${String(Math.floor(m/60)).padStart(2,'0')}:${String(m%60).padStart(2,'0')}`;
const rows=raw.filter(Boolean).map(line=>Object.fromEntries(line.split(',').map((v,i)=>[headers[i],v]))).map(r=>({...r,start_minute:minute(r.start),end_minute:minute(r.end),duration_minutes:minute(r.end)-minute(r.start)}));
const colors={keynote:'#6743B1',workshop:'#087A76',talk:'#2861A8',demo:'#AC5908',panel:'#A04464'};
const ink='#17243B',muted='#56647A',navy='#152B4B',light='#F4F6FA';
const x0=300,x1=1810,ppm=(x1-x0)/420;
const venueYs={A:310,B:440,C:570};
const indexXs={A:64,B:684,C:1304};
const wideMapping=[];
const mobileMapping=[];

function wide(){
  const c=new Canvas(1920,1200,{background:light});
  c.rect(0,0,1920,142,navy);
  c.text(64,26,1370,68,'Structure / Vision 2026',44,'#FFFFFF',{bold:true});
  c.text(66,95,1470,35,'2026.11.07  ·  云构中心 · A / B / C 会场  ·  Asia/Shanghai',22,'#DDE6F3');
  c.text(1556,30,286,46,'15 场 / 3 会场',30,'#FFFFFF',{bold:true,align:'right'});
  c.text(1560,88,282,36,'全日日程 09:00–16:00',20,'#DDE6F3',{align:'right'});
  let lx=64;
  for(const [key,label] of Object.entries(venues.categories)){
    c.circle(lx+8,169,7,colors[key]);c.text(lx+25,151,170,34,label,20,ink);lx+=190;
  }
  c.text(1040,151,802,36,'活动色彩表示类别；午休独立于全部会议',20,muted,{align:'right'});
  c.card(40,199,1840,541,'#FFFFFF',{radius:18});
  c.text(66,214,1700,48,'按真实时长阅读三会场',28,ink,{bold:true});
  for(const v of ['A','B','C']){
    c.rect(x0,venueYs[v],x1-x0,102,'#F6F8FC',{radius:7});
    c.text(70,venueYs[v]+10,202,45,`${v} 会场`,30,ink,{bold:true});
    c.text(72,venueYs[v]+60,202,35,`容量 ${venues[v].capacity} 人`,22,muted);
  }
  // Shared lunch is an exact 60-minute full-height band across all three lanes.
  const lunchX=x0+(720-540)*ppm,lunchW=60*ppm;
  c.rect(lunchX,299,lunchW,385,'#E7EBF2',{radius:6});
  c.text(lunchX+10,295,lunchW-20,38,'公共午休',24,muted,{bold:true,align:'center'});
  c.text(lunchX+7,341,lunchW-14,32,'12:00–13:00',20,muted,{align:'center'});
  for(let m=540;m<=960;m+=30){
    const x=x0+(m-540)*ppm;
    c.line(x,291,x,678,m%60===0?'#D5DFEB':'#E8EDF4',m%60===0?1.5:1);
    if(m%60===0)c.text(x-45,268,90,30,time(m),20,muted,{align:'center'});
  }
  for(const r of rows){
    const x=x0+(r.start_minute-540)*ppm,w=r.duration_minutes*ppm,y=venueYs[r.venue];
    c.rect(x,y,w,102,colors[r.category],{radius:6});
    c.text(x+6,y+15,w-12,42,r.id,26,'#FFFFFF',{bold:true,align:'center'});
    c.text(x+6,y+58,w-12,33,`${r.duration_minutes} min`,20,'#FFFFFF',{align:'center'});
    const venueItems=rows.filter(s=>s.venue===r.venue),ri=venueItems.findIndex(s=>s.id===r.id),ix=indexXs[r.venue],iy=825+ri*58;
    wideMapping.push({id:r.id,venue:r.venue,chart:{x,y,width:w,height:102,display_fields:['id','duration_minutes'],category_color:colors[r.category]},index:{x:ix,y:iy,width:552,height:56,display_fields:['id','title','speaker','start','end','category']}});
  }
  c.text(68,694,1748,35,'读图：横向距离 = 实际分钟；留白 = 空档。色块编号对应下方详单，短场次不拉长。',20,muted);
  c.text(64,753,1500,46,'完整日程 / SESSION INDEX',28,ink,{bold:true});
  for(const v of ['A','B','C']){
    const ix=indexXs[v];
    c.text(ix,795,552,33,`${v} 会场  ·  ${rows.filter(r=>r.venue===v).length} 场`,22,ink,{bold:true});
    rows.filter(r=>r.venue===v).forEach((r,ri)=>{
      const y=825+ri*58;
      c.rect(ix,y+7,5,42,colors[r.category],{radius:2});
      c.text(ix+14,y,538,31,`${r.id}  ${r.title}`,21,ink,{bold:true,softWrap:false,maxLines:1});
      c.text(ix+14,y+28,538,31,`${r.start}–${r.end} · ${r.speaker} · ${venues.categories[r.category]}`,20,muted,{softWrap:false,maxLines:1});
    });
  }
  return c.toString();
}
function mobile(){
  const c=new Canvas(720,1280,{background:'#FFFFFF'});
  c.rect(0,0,720,171,navy);
  c.text(30,20,660,55,'Structure / Vision 2026',34,'#FFFFFF',{bold:true});
  c.text(32,70,655,44,'手机导览',28,'#FFFFFF',{bold:true});
  c.text(32,114,655,30,'2026.11.07  ·  Asia/Shanghai',20,'#DDE6F3');
  c.text(32,141,655,29,'云构中心 · A / B / C 会场',20,'#DDE6F3');
  c.text(30,182,660,32,'上午  /  09:00–11:50',22,ink,{bold:true});
  const morning=rows.filter(r=>r.start_minute<720),afternoon=rows.filter(r=>r.start_minute>=780);
  function list(items,y0,section){
    items.forEach((r,ri)=>{
      const y=y0+ri*57;
      c.rect(30,y+8,54,36,colors[r.category],{radius:7});
      c.text(30,y+12,54,30,r.id,18,'#FFFFFF',{bold:true,align:'center'});
      c.text(102,y,588,32,r.title,21,ink,{bold:true,softWrap:false,maxLines:1});
      c.text(102,y+30,588,27,`${r.venue} 会场  ·  ${r.start}–${r.end}  ·  ${venues.categories[r.category]}`,18,muted,{softWrap:false,maxLines:1});
      c.line(102,y+56,690,y+56,'#EDF0F4',1);
      mobileMapping.push({id:r.id,section,order:mobileMapping.length+1,x:30,y,width:660,height:57,display_fields:['id','title','venue','start','end','category'],speaker_location:'agenda-wide session index'});
    });
  }
  list(morning,220,'morning');
  c.rect(30,688,660,56,'#E7EBF2',{radius:10});
  c.text(47,698,625,37,'12:00–13:00  ·  公共午休',22,muted,{bold:true});
  c.text(30,758,660,32,'下午  /  13:00–16:00',22,ink,{bold:true});
  list(afternoon,798,'afternoon');
  c.rect(0,1212,720,68,'#F4F6FA');
  c.text(32,1228,655,31,'讲者详见完整日程',20,muted);
  return c.toString();
}

function audit(){
  const gaps={},venueConflicts=[],speakerConflicts=[],allPairs=[];
  for(const v of ['A','B','C']){
    const list=rows.filter(r=>r.venue===v).sort((a,b)=>a.start_minute-b.start_minute);let cur=540;gaps[v]=[];
    for(const r of list){if(r.start_minute>cur)gaps[v].push({start:time(cur),end:r.start,duration_minutes:r.start_minute-cur});cur=Math.max(cur,r.end_minute);}
    if(cur<960)gaps[v].push({start:time(cur),end:'16:00',duration_minutes:960-cur});
    for(const g of gaps[v]){g.includes_public_lunch=minute(g.start)<=720&&minute(g.end)>=780;g.non_lunch_parts=[];const a=minute(g.start),b=minute(g.end);if(a<720)g.non_lunch_parts.push({start:time(a),end:time(Math.min(b,720)),duration_minutes:Math.min(b,720)-a});if(b>780)g.non_lunch_parts.push({start:time(Math.max(a,780)),end:time(b),duration_minutes:b-Math.max(a,780)});if(!g.includes_public_lunch&&!g.non_lunch_parts.length)g.non_lunch_parts.push({start:g.start,end:g.end,duration_minutes:g.duration_minutes});}
  }
  for(let i=0;i<rows.length;i++)for(let j=i+1;j<rows.length;j++){
    const a=rows[i],b=rows[j],overlap=Math.min(a.end_minute,b.end_minute)-Math.max(a.start_minute,b.start_minute);
    if(overlap>0){allPairs.push({ids:[a.id,b.id],overlap_minutes:overlap,different_venues:a.venue!==b.venue});if(a.venue===b.venue)venueConflicts.push({ids:[a.id,b.id],venue:a.venue,overlap_minutes:overlap});const aa=a.speaker.split('/').map(x=>x.trim()),bb=b.speaker.split('/').map(x=>x.trim());for(const speaker of aa.filter(s=>bb.includes(s)))speakerConflicts.push({ids:[a.id,b.id],speaker,overlap_minutes:overlap});}
  }
  const lunchOverlaps=rows.filter(r=>Math.min(r.end_minute,780)>Math.max(r.start_minute,720)).map(r=>r.id);
  return {task_id:'A02',run_id:'20261002-204314-6f31',input_sources:['tasks/A02-conference-schedule/inputs/agenda.csv','tasks/A02-conference-schedule/inputs/venues.json'],timezone:'Asia/Shanghai',date:'2026-11-07',event:'Structure / Vision 2026',venue:'云构中心 · A / B / C 会场',sessions:rows.map(r=>({...r,category_label:venues.categories[r.category],speaker_people:r.speaker.split('/').map(s=>s.trim())})),totals:{session_count:rows.length,per_venue:Object.fromEntries(['A','B','C'].map(v=>[v,{sessions:rows.filter(r=>r.venue===v).length,meeting_minutes:rows.filter(r=>r.venue===v).reduce((s,r)=>s+r.duration_minutes,0),capacity:venues[v].capacity}]))},public_lunch:{start:'12:00',end:'13:00',duration_minutes:60,separate_from_sessions:true,wide:{x:x0+180*ppm,y:299,width:60*ppm,height:385,spans_venues:['A','B','C']},mobile:{x:30,y:688,width:660,height:56}},venue_gaps:gaps,conflict_check:{interval_semantics:'half-open [start,end); equal end/start is not a conflict',venue_conflicts:venueConflicts,speaker_conflicts:speakerConflicts,lunch_overlapping_session_ids:lunchOverlaps,parallel_sessions_in_different_venues:allPairs,passed:!venueConflicts.length&&!speakerConflicts.length&&!lunchOverlaps.length},wide_geometry:{canvas:{width:1920,height:1200},orientation:'horizontal timeline / three venue lanes',axis_start:'09:00',axis_end:'16:00',axis_minutes:420,axis_x_start:x0,axis_x_end:x1,pixels_per_minute:ppm,position_formula:'x=300+(start_minute-540)*(1510/420)',width_formula:'width=duration_minutes*(1510/420)',lane_y:venueYs,block_height:102,rounded_corners_preserve_nominal_interval_edges:true,actual_time_changed:false,font_minimum_body:20,font_minimum_time:20},mobile_geometry:{canvas:{width:720,height:1280},layout:'independent chronological morning/lunch/afternoon list',font_minimum_body:18,reuses_wide_pixels:false,speaker_notice:'讲者详见完整日程'},content_mapping:{wide:wideMapping,mobile:mobileMapping,wide_all_ids_present:rows.every(r=>wideMapping.some(m=>m.id===r.id)),mobile_all_ids_present:rows.every(r=>mobileMapping.some(m=>m.id===r.id)),speaker_omission_mobile_only:true},visual_review:{status:'pending actual image review',view_event_ids:[]}};
}
const wd=wide(),md=mobile(),a=audit();
fs.writeFileSync(path.join(temp,'agenda-wide-v001.snapshot'),wd,{flag:'wx'});
fs.writeFileSync(path.join(temp,'agenda-mobile-v001.snapshot'),md,{flag:'wx'});
fs.writeFileSync(path.join(temp,'schedule-audit-v001.json'),JSON.stringify(a,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({sessions:rows.length,wide_dsl_bytes:Buffer.byteLength(wd),mobile_dsl_bytes:Buffer.byteLength(md),audit:a.totals,conflicts:a.conflict_check.venue_conflicts.length,speaker_conflicts:a.conflict_check.speaker_conflicts.length,pixels_per_minute:ppm}));
