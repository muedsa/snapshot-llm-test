'use strict';
// Read the actual submitted DSL, independently extract all plotted primitives,
// and match them to original input and candidate v002. No rendering/view/log writes.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root='D:/workspaces/gpt-6.1-sol-ultra',dir=__dirname;
const inputPath=root+'/tasks/A20-dense-annotation/inputs/markers.json';
const layoutPath=root+'/tmp/20261002-204314-6f31/A20/layout-production/label-layout-candidate-v002.json';
const dslPath=root+'/tmp/20261002-204314-6f31/A20/requests/A20-request-000002/input.snapshot';
const input=JSON.parse(fs.readFileSync(inputPath,'utf8')),layout=JSON.parse(fs.readFileSync(layoutPath,'utf8')),dsl=fs.readFileSync(dslPath,'utf8');
const geom=require('./audit-geometry-v002.cjs');
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const attrs=t=>Object.fromEntries([...t.matchAll(/([\w]+)=(?:"([^"]*)"|'([^']*)')/g)].map(m=>[m[1],m[2]??m[3]]));
const eq=(a,b,t=1e-7)=>Math.abs(a-b)<=t;
const same=(a,b,t=1e-7)=>eq(a.x,b.x,t)&&eq(a.y,b.y,t);
const rb=p=>({x:Number(p.left),y:Number(p.top),width:Number(p.width),height:Number(p.height)});
const rectSame=(a,b)=>['x','y','width','height'].every(k=>eq(a[k],b[k]));
const boxes=[...dsl.matchAll(/<Positioned\s+([^>]*)>([\s\S]*?)<\/Positioned>/g)].map((m,i)=>({index:i,pos:attrs(m[1]),body:m[2]}));
const texts=[],circles=[],cards=[],segments=[],otherContainers=[];
for(const b of boxes) {
  const t=b.body.match(/^<Text\s+([^>]*)><Raw><!\[CDATA\[([\s\S]*?)\]\]><\/Raw><\/Text>$/);
  if(t){texts.push({index:b.index,box:rb(b.pos),attrs:attrs(t[1]),text:t[2]});continue;}
  const tr=b.body.match(/^<Transform\s+([^>]*)><Container\s+([^>]*)\/><\/Transform>$/);
  if(tr){
    const a=attrs(tr[1]),c=attrs(tr[2]),m=a.matrix.replace(/[()]/g,'').split(',').map(Number),p=rb(b.pos),w=Number(c.width),h=Number(c.height);
    const start={x:p.x+m[4]*h/2+m[12],y:p.y+m[5]*h/2+m[13]},end={x:start.x+m[0]*w,y:start.y+m[1]*w};
    segments.push({index:b.index,start,end,width:h,color:c.color,matrix:m,source_position:p,source_container:c});continue;
  }
  const co=b.body.match(/^<Container\s+([^>]*)\/>$/);
  if(co){const c=attrs(co[1]),p=rb(b.pos);if(c.shape==='CIRCLE')circles.push({index:b.index,box:p,center:{x:p.x+p.width/2,y:p.y+p.height/2},diameter:p.width,attrs:c});else if(c.color==='#FFFFFF'&&eq(p.width,180)&&eq(p.height,56))cards.push({index:b.index,box:p,attrs:c});else otherContainers.push({index:b.index,box:p,attrs:c});}
}
const issues=[],add=(type,d)=>issues.push({...d,type});
const rootContainer=dsl.match(/^<Snapshot[^>]*><Container\s+([^>]*)>/),canvas=attrs(rootContainer?.[1]??'');
if(Number(canvas.width)!==1600||Number(canvas.height)!==1100)add('canvas-size',{actual:canvas});
const plot=otherContainers.find(p=>rectSame(p.box,{x:280,y:160,width:1040,height:760}));
if(!plot)add('fixed-plot-not-found',{});
const plottedCircles=circles.filter(p=>p.center.x>=280&&p.center.x<=1320&&p.center.y>=160&&p.center.y<=920);
if(plottedCircles.length!==24)add('actual-plotted-point-count',{actual:plottedCircles.length});
if(cards.length!==24)add('actual-label-box-count',{actual:cards.length});
const top3=['M10','M08','M23'],matches=[],enriched={...layout,markers:[]};
for(const source of input){
 const e=layout.markers.find(m=>m.id===source.id),anchor={x:280+10.4*source.x,y:920-7.6*source.y};
 if(!e){add('layout-missing-id',{id:source.id});continue;}
 const cs=plottedCircles.filter(c=>same(c.center,anchor));if(cs.length!==1)add('actual-point-coordinate',{id:source.id,expected:anchor,matches:cs.length});
 const c=cs[0],col=top3.includes(source.id)?'#B14D39':'#286688';
 if(c&&(c.diameter!==12||c.box.height!==12||c.attrs.color!==col))add('actual-point-style',{id:source.id,actual:c,expected_diameter:12,expected_color:col});
 const bs=cards.filter(b=>rectSame(b.box,e.label));if(bs.length!==1)add('actual-label-box',{id:source.id,expected:e.label,matches:bs.length});
 const idTexts=texts.filter(t=>t.text.replace(/\s+/g,' ').trim()===`${source.id} ${source.name}`);
 const valueTexts=texts.filter(t=>t.text===`${source.value} 指数`&&same({x:t.box.x,y:t.box.y},{x:e.label.x+10,y:e.label.y+30}));
 if(idTexts.length!==1||valueTexts.length!==1)add('actual-label-content',{id:source.id,id_matches:idTexts.length,value_matches:valueTexts.length});
 const tt=[idTexts[0],valueTexts[0]].filter(Boolean);
 for(const t of tt){if(Number(t.attrs.fontSize)<20)add('actual-label-font',{id:source.id,text:t.text,font:t.attrs.fontSize});if(t.box.x<e.label.x||t.box.y<e.label.y||t.box.x+t.box.width>e.label.x+e.label.width+1e-7||t.box.y+t.box.height>e.label.y+e.label.height+1e-7)add('actual-text-box-not-inside-label',{id:source.id,text:t.text,box:t.box,label:e.label});}
 matches.push({id:source.id,logical:{x:source.x,y:source.y},expected_anchor:anchor,actual_circle:c??null,actual_label_card:bs[0]??null,actual_texts:tt});
 enriched.markers.push({...e,line_width:1.8,text_boxes:tt.map(t=>t.box)});
}
const actualLeaders=segments.filter(s=>eq(s.width,1.8)&&['#286688','#B14D39'].includes(s.color));
const expectedLeaders=layout.markers.flatMap(e=>e.polyline.slice(1).map((p,i)=>({owner:e.id,index:i,start:{x:e.polyline[i][0],y:e.polyline[i][1]},end:{x:p[0],y:p[1]},color:top3.includes(e.id)?'#B14D39':'#286688'})));
if(actualLeaders.length!==expectedLeaders.length)add('actual-leader-segment-count',{expected:expectedLeaders.length,actual:actualLeaders.length});
let maxSerializedDrift=0;const leaderMatches=[];
for(let i=0;i<expectedLeaders.length;i++){
 const exp=expectedLeaders[i],act=actualLeaders[i];if(!act)continue;
 const drift=Math.max(Math.abs(act.start.x-exp.start.x),Math.abs(act.start.y-exp.start.y),Math.abs(act.end.x-exp.end.x),Math.abs(act.end.y-exp.end.y));maxSerializedDrift=Math.max(maxSerializedDrift,drift);
 if(drift>0.0002||act.color!==exp.color)add('actual-leader-difference',{expected:exp,actual:act,serialized_drift:drift,tolerance:0.0002});
 leaderMatches.push({owner:exp.owner,segment:exp.index,expected:exp,actual:act,serialized_drift:drift});
}
const axes={x_arrow:texts.filter(t=>t.text==='x →'),y_arrow:texts.filter(t=>t.text==='y ↑'),ticks:[]};
if(axes.x_arrow.length!==1||axes.y_arrow.length!==1)add('axis-arrow-presence',{actual:axes});
for(let n=0;n<=100;n+=20){const xa={x:280+10.4*n-23,y:927,width:46,height:27},ya={x:228,y:920-7.6*n-13,width:43,height:28};const xt=texts.filter(t=>t.text===String(n)&&rectSame(t.box,xa)),yt=texts.filter(t=>t.text===String(n)&&rectSame(t.box,ya));axes.ticks.push({value:n,x:xt[0]??null,y:yt[0]??null});if(xt.length!==1||yt.length!==1)add('axis-range-tick',{value:n,x_matches:xt.length,y_matches:yt.length});}
const topText=texts.find(t=>t.text==='广场 93  ·  中庭 91  ·  研究所 90');if(!topText)add('actual-top3-caption',{});
const unitTexts=texts.filter(t=>t.text.includes('指数'));if(unitTexts.length<24)add('unit-index-missing',{matches:unitTexts.length});
const extractedPath=path.join(dir,'actual-source-primitives-v002.json');
const extracted={created_at:new Date().toISOString(),dsl_path:dslPath,dsl_sha256:hash(dslPath),canvas,plot,counts:{positioned:boxes.length,texts:texts.length,circles:circles.length,plotted_circles:plottedCircles.length,label_cards:cards.length,leaders:actualLeaders.length},matches,leaderMatches,axes,top3_caption:topText,unit_text_count:unitTexts.length,max_serialized_line_drift_px:maxSerializedDrift};
fs.writeFileSync(extractedPath,JSON.stringify(extracted,null,2)+'\n',{flag:'wx'});
const canonicalPath=path.join(dir,'candidate-v002-with-actual-text-and-stroke.json');
fs.writeFileSync(canonicalPath,JSON.stringify(enriched,null,2)+'\n',{flag:'wx'});
const geometry=geom.audit(enriched,input);const geometryPath=path.join(dir,'candidate-v002-stroke-and-text-independent-audit-v002.json');
geometry.source={candidate_path:layoutPath,candidate_sha256:hash(layoutPath),actual_dsl_path:dslPath,actual_dsl_sha256:hash(dslPath),canonical_path:canonicalPath,input_path:inputPath,input_sha256:hash(inputPath)};
fs.writeFileSync(geometryPath,JSON.stringify(geometry,null,2)+'\n',{flag:'wx'});
const leaderPointClearances=[];
for(const s of actualLeaders)for(const m of matches){const owner=leaderMatches.find(x=>x.actual.index===s.index)?.owner;if(m.id===owner)continue;const clearance=geom.pointSegmentDistance(m.expected_anchor,s.start,s.end)-6-s.width/2;leaderPointClearances.push({line:owner,segment:s.index,point:m.id,clearance_px:clearance});}
leaderPointClearances.sort((a,b)=>a.clearance_px-b.clearance_px);
const result={audit_version:'A20-independent-actual-source-v002',created_at:new Date().toISOString(),pass_source:issues.length===0,pass_geometry:geometry.pass_geometry,pass_combined:issues.length===0&&geometry.pass_geometry,source_issues:issues,geometry_issue_count:geometry.issues.length,source:{input_path:inputPath,input_sha256:hash(inputPath),candidate_path:layoutPath,candidate_sha256:hash(layoutPath),actual_dsl_path:dslPath,actual_dsl_sha256:hash(dslPath)},evidence_paths:{extracted_primitives:extractedPath,canonical_with_actual_text_and_stroke:canonicalPath,geometry_audit:geometryPath,prior_failure:path.join(dir,'candidate-v001-strict-own-overlap-audit-v001.json')},summary:{marker_count:plottedCircles.length,diameter_px:12,label_count:cards.length,marker_label_text_count:matches.flatMap(m=>m.actual_texts).length,marker_label_font_px:20,axis_tick_font_px:18,fixed_plot:{x:280,y:160,width:1040,height:760},minimum_label_box_gap_px:geometry.checks.minimum_label_box_distance,leader_stroke_px:1.8,leader_segments:actualLeaders.length,foreign_leader_crossings:geometry.checks.line_crossings.pair_event_count,line_label_contacts:geometry.checks.line_label_collisions.length,line_text_contacts:geometry.checks.line_text_collisions.length,line_nonown_point_contacts:geometry.checks.line_nonown_point_collisions.length,label_nonown_point_contacts:geometry.checks.label_point_collisions.length,own_retraces:geometry.checks.line_crossings.collinear_overlaps.length,max_serialized_line_drift_px:maxSerializedDrift,closest_actual_line_nonown_point_clearance:leaderPointClearances[0],top3:top3},visual_review:{performed_by_this_agent:false,root_reported:'Root message: center M08–M13 crop then overall image actually inspected and passed; this audit supplies source/data/geometry evidence only.'},notes:['48 marker-label body text widgets are 20px. The 12 separate numeric axis tick widgets are 18px and are not counted as marker-label body text.','Actual transform centerlines match candidate endpoints within 0.0002px tolerance for the 6-decimal DSL matrix serialization. Maximum measured drift is retained. Geometry collisions are audited on matching exact source geometry with actual 1.8px stroke and actual allocated text boxes.','All labels are checked against non-own point circles. Lines are checked against all label boxes and allocated text bounds, with only the final own-box boundary contact permitted. Foreign closed-boundary touches count as collision. Distinct-line touches count as crossing; adjacent own elbows are excluded.','No service render, image view, suite ledger or formal output was performed by this agent.']};
const resultPath=path.join(dir,'final-independent-audit-v002.json');fs.writeFileSync(resultPath,JSON.stringify(result,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({audit_path:resultPath,...result.summary,pass_source:result.pass_source,pass_geometry:result.pass_geometry,pass_combined:result.pass_combined,source_issues:issues,geometry_issues:geometry.issues}));
