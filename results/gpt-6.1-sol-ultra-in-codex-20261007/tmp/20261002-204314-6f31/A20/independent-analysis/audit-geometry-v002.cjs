'use strict';
// Independent A20 geometry audit. This file writes only immutable results in its own
// independent-analysis directory. It does not render or update any suite ledger.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const EPS = 1e-7;
const ROOT = 'D:/workspaces/gpt-6.1-sol-ultra';
const INPUT = ROOT + '/tasks/A20-dense-annotation/inputs/markers.json';
const OUT = ROOT + '/tmp/20261002-204314-6f31/A20/independent-analysis';
const readJson = p => JSON.parse(fs.readFileSync(p, 'utf8').replace(/^\uFEFF/, ''));
const hash = p => crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const finite = n => typeof n === 'number' && Number.isFinite(n);
const near = (a,b) => Math.abs(a-b) <= EPS;
const point = p => Array.isArray(p) ? {x:Number(p[0]),y:Number(p[1])} : {x:Number(p.x),y:Number(p.y)};
const same = (a,b) => near(a.x,b.x) && near(a.y,b.y);
const dist = (a,b) => Math.hypot(a.x-b.x,a.y-b.y);
const cross = (a,b,c) => (b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x);
const rect = b => ({x:Number(b.x),y:Number(b.y),width:Number(b.width ?? b.w),height:Number(b.height ?? b.h)});
const validRect = b => [b.x,b.y,b.width,b.height].every(finite) && b.width>0 && b.height>0;
const right = b => b.x+b.width, bottom = b => b.y+b.height;
const pointRectDistance = (p,b) => Math.hypot(Math.max(b.x-p.x,0,p.x-right(b)),Math.max(b.y-p.y,0,p.y-bottom(b)));
const rectDistance = (a,b) => Math.hypot(Math.max(a.x-right(b),b.x-right(a),0),Math.max(a.y-bottom(b),b.y-bottom(a),0));
const inRect = (p,b,closed=true) => closed ? p.x>=b.x-EPS && p.x<=right(b)+EPS && p.y>=b.y-EPS && p.y<=bottom(b)+EPS : p.x>b.x+EPS && p.x<right(b)-EPS && p.y>b.y+EPS && p.y<bottom(b)-EPS;
const onBoundary = (p,b) => inRect(p,b) && (near(p.x,b.x)||near(p.x,right(b))||near(p.y,b.y)||near(p.y,bottom(b)));
function pointSegmentDistance(p,a,b) {
  const dx=b.x-a.x,dy=b.y-a.y,l=dx*dx+dy*dy;
  if(l<=EPS*EPS) return dist(p,a);
  const t=Math.max(0,Math.min(1,((p.x-a.x)*dx+(p.y-a.y)*dy)/l));
  return dist(p,{x:a.x+t*dx,y:a.y+t*dy});
}
function onSegment(p,a,b) { return Math.abs(cross(a,b,p))<=EPS && p.x>=Math.min(a.x,b.x)-EPS && p.x<=Math.max(a.x,b.x)+EPS && p.y>=Math.min(a.y,b.y)-EPS && p.y<=Math.max(a.y,b.y)+EPS; }
function segmentIntersection(a,b,c,d) {
  const rx=b.x-a.x,ry=b.y-a.y,sx=d.x-c.x,sy=d.y-c.y;
  const det=rx*sy-ry*sx, qx=c.x-a.x,qy=c.y-a.y;
  if(Math.abs(det)>EPS) {
    const t=(qx*sy-qy*sx)/det,u=(qx*ry-qy*rx)/det;
    if(t>=-EPS&&t<=1+EPS&&u>=-EPS&&u<=1+EPS) return {type:'point',point:{x:a.x+t*rx,y:a.y+t*ry},t,u};
    return null;
  }
  if(Math.abs(qx*ry-qy*rx)>EPS) return null;
  const contacts=[];
  for(const p of [a,b,c,d]) if(onSegment(p,a,b)&&onSegment(p,c,d)&&!contacts.some(q=>same(p,q))) contacts.push(p);
  if(!contacts.length) return null;
  if(contacts.length===1) return {type:'point',point:contacts[0],t:null,u:null};
  contacts.sort((p,q)=>Math.abs(rx)>=Math.abs(ry)?p.x-q.x:p.y-q.y);
  return {type:'overlap',from:contacts[0],to:contacts[contacts.length-1]};
}
function clipSegmentToRect(a,b,r) {
  // Closed Liang-Barsky clipping: a touch is reported, not discarded.
  const dx=b.x-a.x,dy=b.y-a.y,ps=[-dx,dx,-dy,dy],qs=[a.x-r.x,right(r)-a.x,a.y-r.y,bottom(r)-a.y];
  let lo=0,hi=1;
  for(let i=0;i<4;i++) {
    if(Math.abs(ps[i])<=EPS) { if(qs[i]<-EPS) return null; }
    else { const t=qs[i]/ps[i]; if(ps[i]<0)lo=Math.max(lo,t);else hi=Math.min(hi,t); if(lo>hi+EPS)return null; }
  }
  return {lo,hi,from:{x:a.x+lo*dx,y:a.y+lo*dy},to:{x:a.x+hi*dx,y:a.y+hi*dy}};
}
function segmentRectDistance(a,b,r) {
  if(clipSegmentToRect(a,b,r)) return 0;
  const corners=[{x:r.x,y:r.y},{x:right(r),y:r.y},{x:right(r),y:bottom(r)},{x:r.x,y:bottom(r)}];
  return Math.min(pointRectDistance(a,r),pointRectDistance(b,r),...corners.map(p=>pointSegmentDistance(p,a,b)));
}
function normalize(raw) {
  const entries=Array.isArray(raw)?raw:(raw.labels ?? raw.markers ?? raw.points ?? raw.layout);
  if(!Array.isArray(entries)) throw new Error('Expected array or labels/markers/points/layout array.');
  return {meta:raw,entries:entries.map(e=>({
    raw:e,id:e.id ?? e.marker_id,
    logical:e.logical ?? e.logical_coordinates ?? e.original ?? (e.x!==undefined&&e.y!==undefined?{x:e.x,y:e.y}:null),
    anchor:e.anchor ?? e.pixel_anchor ?? e.pixel ?? e.anchor_px,
    box:e.box ?? e.label_box ?? e.label?.box ?? e.label,
    polyline:e.polyline ?? e.leader ?? e.leader_line ?? e.label?.polyline ?? [],
    diameter:e.diameter ?? e.marker_diameter ?? e.point_diameter ?? e.point?.diameter,
    name:e.name ?? e.label?.name,value:e.value ?? e.label?.value,
    fontSize:e.font_size ?? e.fontSize ?? e.label?.font_size ?? e.label?.fontSize ?? raw.label_style?.font_size,
    lineWidth:e.line_width ?? e.leader_width ?? e.leader?.width,
    textBoxes:e.text_boxes ?? e.text_bounds ?? e.label?.text_boxes ?? [],
    highest:e.highest ?? e.top3 ?? e.is_top3,
  }))};
}
function audit(raw, markers, options={}) {
  const {meta,entries}=normalize(raw), issues=[], warnings=[], checks={};
  const add=(type,details)=>issues.push({...details,type});
  const originals=new Map(markers.map(m=>[m.id,m]));
  const ids=entries.map(e=>e.id), duplicates=ids.filter((id,i)=>ids.indexOf(id)!==i);
  checks.marker_count={expected:24,actual:entries.length,missing:markers.filter(m=>!ids.includes(m.id)).map(m=>m.id),extra:ids.filter(id=>!originals.has(id)),duplicates:[...new Set(duplicates)]};
  if(entries.length!==24||checks.marker_count.missing.length||checks.marker_count.extra.length||duplicates.length)add('marker-identity',checks.marker_count);
  const plot={x:280,y:160,width:1040,height:760}, canvas={x:0,y:0,width:1600,height:1100};
  checks.plot={expected:plot,declared:meta.plot ?? meta.plot_bounds ?? meta.map ?? null};
  if(checks.plot.declared && !Object.keys(plot).every(k=>near(Number(checks.plot.declared[k]),plot[k])))add('plot-bounds',{actual:checks.plot.declared,expected:plot});
  checks.mapping=[]; checks.label_content=[]; checks.diameter=[]; checks.boundary=[]; checks.leader_attachment=[];
  for(const e of entries) {
    const m=originals.get(e.id);if(!m)continue;
    e.anchor=e.anchor?point(e.anchor):{x:NaN,y:NaN};e.box=e.box?rect(e.box):{x:NaN,y:NaN,width:NaN,height:NaN};
    e.polyline=Array.isArray(e.polyline)?e.polyline.map(point):[];
    const expected={x:280+10.4*m.x,y:920-7.6*m.y};
    const mappingValid=[e.anchor.x,e.anchor.y].every(finite)&&same(e.anchor,expected);
    checks.mapping.push({id:e.id,logical:{x:m.x,y:m.y},expected,actual:e.anchor,pass:mappingValid});
    if(!mappingValid)add('mapping',{id:e.id,expected,actual:e.anchor});
    if(!e.logical||!near(Number(e.logical.x),m.x)||!near(Number(e.logical.y),m.y))add('original-logical-coordinate',{id:e.id,expected:{x:m.x,y:m.y},actual:e.logical});
    const contentValid=e.name===m.name&&Number(e.value)===m.value;
    checks.label_content.push({id:e.id,expected:{name:m.name,value:m.value},actual:{name:e.name,value:e.value},pass:contentValid});
    if(!contentValid)add('label-content',{id:e.id,expected:{name:m.name,value:m.value},actual:{name:e.name,value:e.value}});
    const d=Number(e.diameter);e.diameter=d;
    const allowedDense=options.allowedDenseIds??meta.dense_marker_ids??['M08','M09','M10','M11','M12'];
    const sizeValid=near(d,12)||(near(d,8)&&allowedDense.includes(e.id));
    checks.diameter.push({id:e.id,actual:d,pass:sizeValid,dense_reduction:near(d,8)});
    if(!sizeValid)add('point-diameter',{id:e.id,actual:d,allowed:allowedDense.includes(e.id)?[12,8]:[12]});
    if(!validRect(e.box))add('label-box-schema',{id:e.id,box:e.box});
    if(!finite(Number(e.fontSize)))warnings.push({type:'font-size-unavailable',id:e.id});
    else if(Number(e.fontSize)<20)add('label-font-size',{id:e.id,actual:e.fontSize,minimum:20});
    const labelInside=validRect(e.box)&&e.box.x>=-EPS&&e.box.y>=-EPS&&right(e.box)<=1600+EPS&&bottom(e.box)<=1100+EPS;
    const markerInside=mappingValid&&e.anchor.x-d/2>=280-EPS&&e.anchor.x+d/2<=1320+EPS&&e.anchor.y-d/2>=160-EPS&&e.anchor.y+d/2<=920+EPS;
    const lineInside=e.polyline.every(p=>[p.x,p.y].every(finite)&&inRect(p,canvas));
    checks.boundary.push({id:e.id,label_inside_canvas:labelInside,point_inside_plot:markerInside,line_inside_canvas:lineInside});
    if(!labelInside||!markerInside||!lineInside)add('boundary',{id:e.id,label_inside_canvas:labelInside,point_inside_plot:markerInside,line_inside_canvas:lineInside});
    const distance=pointRectDistance(e.anchor,e.box),needsLine=distance>24+EPS;
    const startValid=e.polyline.length>=2&&same(e.polyline[0],e.anchor),endValid=e.polyline.length>=2&&onBoundary(e.polyline[e.polyline.length-1],e.box);
    checks.leader_attachment.push({id:e.id,distance_to_box:distance,line_required:needsLine,line_present:e.polyline.length>=2,start_at_own_anchor:startValid,end_on_own_box:endValid});
    if(needsLine&&e.polyline.length<2)add('missing-required-leader',{id:e.id,distance_to_box:distance});
    if(e.polyline.length&&(!startValid||!endValid))add('leader-attachment',{id:e.id,start_at_own_anchor:startValid,end_on_own_box:endValid});
    for(let i=0;i+1<e.polyline.length;i++)if(same(e.polyline[i],e.polyline[i+1]))add('zero-length-leader-segment',{id:e.id,segment:i});
  }
  checks.label_pairs=[];checks.label_point_collisions=[];checks.point_point_collisions=[];
  let minGap=Infinity;
  for(let i=0;i<entries.length;i++)for(let j=i+1;j<entries.length;j++) {
    const a=entries[i],b=entries[j],gap=rectDistance(a.box,b.box);minGap=Math.min(minGap,gap);
    if(gap<4-EPS) { const row={a:a.id,b:b.id,distance:gap};checks.label_pairs.push(row);add('label-gap-under-4',row); }
    if(dist(a.anchor,b.anchor)<=a.diameter/2+b.diameter/2+EPS) { const row={a:a.id,b:b.id,distance:dist(a.anchor,b.anchor),minimum:a.diameter/2+b.diameter/2};checks.point_point_collisions.push(row);add('point-point-collision',row); }
  }
  checks.minimum_label_box_distance=minGap;
  for(const label of entries)for(const marker of entries)if(label.id!==marker.id) {
    const gap=pointRectDistance(marker.anchor,label.box)-marker.diameter/2;
    if(gap<=EPS) { const row={label:label.id,point:marker.id,circle_box_clearance:gap};checks.label_point_collisions.push(row);add('label-nonown-point-collision',row); }
  }
  const segs=[];for(const e of entries)for(let i=0;i+1<e.polyline.length;i++)segs.push({owner:e.id,index:i,a:e.polyline[i],b:e.polyline[i+1],count:e.polyline.length-1,lineWidth:finite(Number(e.lineWidth))?Number(e.lineWidth):0});
  checks.line_label_collisions=[];checks.line_text_collisions=[];checks.line_nonown_point_collisions=[];checks.line_stroke_clearance_warnings=[];
  for(const s of segs) {
    for(const label of entries) {
      const clip=clipSegmentToRect(s.a,s.b,label.box);
      const ownEnd=s.owner===label.id&&s.index===s.count-1&&clip&&near(clip.lo,1)&&near(clip.hi,1)&&same(clip.from,s.b)&&onBoundary(s.b,label.box);
      if(clip&&!ownEnd) { const row={line:s.owner,segment:s.index,label:label.id,contact:clip};checks.line_label_collisions.push(row);add('line-label-box-contact',row); }
      const clearance=segmentRectDistance(s.a,s.b,label.box);
      if(!clip&&s.lineWidth>0&&clearance<s.lineWidth/2-EPS) {
        const row={line:s.owner,segment:s.index,label:label.id,clearance,line_halfwidth:s.lineWidth/2};checks.line_stroke_clearance_warnings.push(row);add('line-stroke-label-contact',row);
      }
      const tbs=Array.isArray(label.textBoxes)?label.textBoxes:[];
      for(let k=0;k<tbs.length;k++) { const tb=rect(tbs[k]);if(!validRect(tb))continue;const tc=clipSegmentToRect(s.a,s.b,tb);if(tc) { const row={line:s.owner,segment:s.index,label:label.id,text_box:k,contact:tc};checks.line_text_collisions.push(row);add('line-text-contact',row); } }
    }
    for(const marker of entries)if(s.owner!==marker.id) {
      const distance=pointSegmentDistance(marker.anchor,s.a,s.b),required=marker.diameter/2+s.lineWidth/2;
      if(distance<=required+EPS) { const row={line:s.owner,segment:s.index,point:marker.id,distance,required};checks.line_nonown_point_collisions.push(row);add('line-nonown-point-contact',row); }
    }
  }
  const intersections=[],overlaps=[],selfIntersections=[];
  for(let i=0;i<segs.length;i++)for(let j=i+1;j<segs.length;j++) {
    const a=segs[i],b=segs[j],inter=segmentIntersection(a.a,a.b,b.a,b.b);if(!inter)continue;
    // Only the adjacent segments belonging to the same leader may share their own elbow.
    if(a.owner===b.owner&&Math.abs(a.index-b.index)===1&&inter.type==='point'&&same(inter.point,a.index<b.index?a.b:b.b))continue;
    const row={a:a.owner,a_segment:a.index,b:b.owner,b_segment:b.index,...inter};
    if(inter.type==='overlap') { overlaps.push(row);add('line-collinear-overlap',row); }
    else if(a.owner===b.owner) { selfIntersections.push(row);add('leader-self-intersection',row); }
    else intersections.push(row);
  }
  const pairEvents=[];for(const i of intersections)if(!pairEvents.some(j=>j.a===i.a&&j.b===i.b&&same(j.point,i.point)))pairEvents.push(i);
  const locations=[];for(const i of pairEvents)if(!locations.some(p=>same(p,i.point)))locations.push(i.point);
  checks.line_crossings={segment_events:intersections,pair_events:pairEvents,unique_locations:locations,pair_event_count:pairEvents.length,location_count:locations.length,collinear_overlaps:overlaps,self_intersections:selfIntersections,maximum:3};
  if(pairEvents.length>3)add('line-crossings-over-3',{count:pairEvents.length,unique_locations:locations.length});
  const top=markers.slice().sort((a,b)=>b.value-a.value).slice(0,3).map(m=>({id:m.id,name:m.name,value:m.value}));
  checks.highest_three={expected:top,declared:meta.highest_three??meta.top3??meta.highest3??meta.top3_ids??null,entry_flags:entries.filter(e=>e.highest===true).map(e=>e.id)};
  const declared=checks.highest_three.declared;
  if(declared) { const actual=declared.map(x=>typeof x==='string'?x:x.id); if(JSON.stringify(actual)!==JSON.stringify(top.map(x=>x.id)))add('highest-three',{expected:top,actual:declared}); }
  else if(checks.highest_three.entry_flags.length) { if(JSON.stringify(checks.highest_three.entry_flags.slice().sort())!==JSON.stringify(top.map(x=>x.id).sort()))add('highest-three-flags',{expected:top,actual:checks.highest_three.entry_flags}); }
  else warnings.push({type:'highest-three-rendering-not-declared',expected:top});
  return {audit_version:'A20-independent-geometry-v002',created_at:new Date().toISOString(),scope:'Independent source-data and closed geometry audit; no service render or image viewing. Own final leader endpoint may touch its own label boundary only. All foreign touches count as collision. Adjacent own elbows excluded; distinct leaders touching or crossing count. Collinear overlaps and self intersections fail. Pair events and unique physical locations both retained; conservative <=3 criterion uses pair events.',pass_geometry:issues.length===0,issues,warnings,checks};
}
function selftest() {
  const assert=require('node:assert/strict');
  const r={x:10,y:10,width:20,height:20};
  assert.equal(rectDistance(r,{x:34,y:10,width:20,height:20}),4);
  assert.equal(rectDistance(r,{x:32,y:32,width:20,height:20}),Math.sqrt(8));
  assert.equal(pointRectDistance({x:4,y:20},r),6);
  assert.ok(clipSegmentToRect({x:0,y:10},{x:10,y:10},r));
  assert.ok(!clipSegmentToRect({x:0,y:9},{x:40,y:9},r));
  assert.ok(clipSegmentToRect({x:0,y:20},{x:40,y:20},r).hi>clipSegmentToRect({x:0,y:20},{x:40,y:20},r).lo);
  assert.equal(segmentIntersection({x:0,y:0},{x:10,y:10},{x:0,y:10},{x:10,y:0}).type,'point');
  assert.equal(segmentIntersection({x:0,y:0},{x:10,y:0},{x:5,y:0},{x:20,y:0}).type,'overlap');
  assert.equal(segmentIntersection({x:0,y:0},{x:10,y:0},{x:10,y:0},{x:10,y:5}).type,'point');
  assert.equal(pointSegmentDistance({x:5,y:6},{x:0,y:0},{x:10,y:0}),6);
  return {selftest:'passed',assertions:10,created_at:new Date().toISOString(),purpose:'Boundary touches, proper crossings, collinear overlaps, diagonal label gaps and circle clearances independently exercise critical geometric edge cases.'};
}
if(require.main===module) {
  fs.mkdirSync(OUT,{recursive:true});
  if(process.argv[2]==='--selftest') {
    const result=selftest();const f=path.join(OUT,'geometry-selftest-v002.json');fs.writeFileSync(f,JSON.stringify(result,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify({path:f,...result}));
  } else {
    const p=path.resolve(process.argv[2]??'');if(!process.argv[2])throw new Error('Pass candidate JSON path.');
    const result=audit(readJson(p),readJson(INPUT));result.source={candidate_path:p,candidate_sha256:hash(p),input_path:INPUT,input_sha256:hash(INPUT)};
    const stem=process.argv[3]??path.basename(p).replace(/\.json$/i,'');const f=path.join(OUT,stem+'-independent-audit-v002.json');
    fs.writeFileSync(f,JSON.stringify(result,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify({audit_path:f,pass_geometry:result.pass_geometry,issue_count:result.issues.length,warning_count:result.warnings.length,issues:result.issues,crossings:result.checks.line_crossings.pair_event_count,minimum_box_gap:result.checks.minimum_label_box_distance}));
  }
}
module.exports={audit,normalize,rectDistance,pointRectDistance,clipSegmentToRect,segmentIntersection,pointSegmentDistance,selftest};
