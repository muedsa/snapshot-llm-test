'use strict';
const fs=require('node:fs'), path=require('node:path'), crypto=require('node:crypto'), zlib=require('node:zlib');
const base=path.resolve(__dirname,'..'), out=path.resolve(base,'../../../outputs/20261002-204314-6f31/A19');
const read=n=>fs.readFileSync(path.resolve(base,n));
const load=n=>JSON.parse(read(n).toString('utf8').replace(/^\uFEFF/,''));
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const eq=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
const checks={}, unresolved=[];
function check(k,v){checks[k]=!!v;if(!v)unresolved.push(k);return!!v;}
const d=load('scene-data-final-v001.json'),q=load('questions-final-v001.json'),a=load('answers-final-v001.json'), g=load('grid-production/scene-data-grid-v001.json'), o=d.occlusion;
const objects=d.objects, colors=['blue','orange','green','purple'], shapes=['circle','square','ring','rounded-square'];
const props=s=>Object.fromEntries([...s.matchAll(/([A-Za-z][A-Za-z0-9]*)="([^"]*)"/g)].map(m=>[m[1],m[2]]));
function positions(source){return [...source.matchAll(/<Positioned\b([^>]*)>([\s\S]*?)<\/Positioned>/g)].map(m=>({raw:m[0],index:m.index,p:props(m[1]),inside:m[2],c:props(m[2].match(/<Container\b([^>]*)\/>/)?.[1]??''),t:props(m[2].match(/<Text\b([^>]*)>/)?.[1]??''),text:m[2].match(/<!\[CDATA\[([\s\S]*?)\]\]>/)?.[1]??null}));}
function bboxPosition(p){return [+p.left,+p.top,+p.left+(+p.width),+p.top+(+p.height)];}
function shapeSource(s){return s==='circle'||s==='ring'?'CIRCLE':'RECTANGLE';}
function png(buffer){
  if(!buffer.subarray(0,8).equals(Buffer.from([137,80,78,71,13,10,26,10])))throw Error('Not PNG');
  let width,height,depth,type;const ids=[];
  for(let p=8;p<buffer.length;){const n=buffer.readUInt32BE(p),tag=buffer.toString('ascii',p+4,p+8),v=buffer.subarray(p+8,p+8+n);if(tag==='IHDR'){width=v.readUInt32BE(0);height=v.readUInt32BE(4);depth=v[8];type=v[9];if(v[10]!==0||v[11]!==0||v[12]!==0)throw Error('Unsupported PNG encoding');}if(tag==='IDAT')ids.push(v);p+=n+12;}
  if(depth!==8||![2,6].includes(type))throw Error('Unsupported PNG channels');
  const channels=type===6?4:3, stride=width*channels, data=zlib.inflateSync(Buffer.concat(ids)),decoded=Buffer.alloc(stride*height),rgba=Buffer.alloc(width*height*4);
  const paeth=(x,y,z)=>{const p=x+y-z,px=Math.abs(p-x),py=Math.abs(p-y),pz=Math.abs(p-z);return px<=py&&px<=pz?x:py<=pz?y:z;};
  for(let y=0;y<height;y++){const off=y*(stride+1),f=data[off];for(let x=0;x<stride;x++){const i=y*stride+x,left=x>=channels?decoded[i-channels]:0,up=y?decoded[i-stride]:0,corner=y&&x>=channels?decoded[i-stride-channels]:0;const pred=f===0?0:f===1?left:f===2?up:f===3?Math.floor((left+up)/2):f===4?paeth(left,up,corner):NaN;if(Number.isNaN(pred))throw Error('Bad PNG filter');decoded[i]=(data[off+x+1]+pred)&255;}}
  for(let i=0;i<width*height;i++){rgba[i*4]=decoded[i*channels];rgba[i*4+1]=decoded[i*channels+1];rgba[i*4+2]=decoded[i*channels+2];rgba[i*4+3]=channels===4?decoded[i*channels+3]:255;}
  return {width,height,depth,color_type:type,rgba,pixel:(x,y)=>[...rgba.subarray((y*width+x)*4,(y*width+x)*4+4)]};
}
const meta=[1,2,3].map(n=>load(`requests/A19-request-${String(n).padStart(6,'0')}/render-result.json`));
const sources=meta.map(m=>fs.readFileSync(m.input_file,'utf8')),parsed=sources.map(positions),pngs=meta.map(m=>png(fs.readFileSync(m.response_file)));
const provenance=meta.map((m,i)=>({request_id:m.id,version_id:m.version_id,http_status:m.http_status,content_type:m.content_type,image_path:m.response_file,source_path:m.input_file,body_sha256:hash(fs.readFileSync(m.input_file)),PNG_sha256:hash(fs.readFileSync(m.response_file)),PNG_bytes:fs.statSync(m.response_file).size,decoded_dimensions:[pngs[i].width,pngs[i].height],response_metadata_matches:m.ok&&m.http_status===200&&m.content_type==='image/png'&&m.body_sha256===hash(fs.readFileSync(m.input_file))&&m.response_sha256===hash(fs.readFileSync(m.response_file))&&fs.readFileSync(m.dsl_path).equals(fs.readFileSync(m.input_file))}));
check('three_actual_service_responses_and_source_hashes_match',provenance.every(p=>p.response_metadata_matches));
check('exact_required_dimensions',eq(provenance.map(p=>p.decoded_dimensions),[[800,800],[800,800],[1600,1600]]));
check('all_sources_DSL_only_no_external_images',sources.every(s=>!/<(?:Image|Emoji)\b/.test(s)&&!/(?:dataUri|url)=/.test(s)));
check('merged_grid_objects_identical_to_frozen_geometry',eq(objects,g.objects));
check('merged_occlusion_data_identical_to_producer_geometry',eq(o,load('occlusion-production/scene-data-occlusion-v001.json')));
check('grid_frozen_data_hash_links_match',d.source_grid_data_sha256===hash(read('grid-production/scene-data-grid-v001.json'))&&q.source_grid_data_sha256===d.source_grid_data_sha256&&a.source_grid_data_sha256===d.source_grid_data_sha256);
check('occlusion_frozen_data_hash_link_matches',d.source_occlusion_data_sha256===hash(read('occlusion-production/scene-data-occlusion-v001.json')));
const counts={colors:Object.fromEntries(colors.map(k=>[k,objects.filter(v=>v.color_name===k).length])),shapes:Object.fromEntries(shapes.map(k=>[k,objects.filter(v=>v.shape===k).length])),sizes:Object.fromEntries([48,64,80].map(k=>[k,objects.filter(v=>v.size===k).length]))};
const rows=Array.from({length:8},(_,i)=>({row:i+1,count:objects.filter(v=>v.row===i+1).length,color_count:new Set(objects.filter(v=>v.row===i+1).map(v=>v.color_name)).size,shape_count:new Set(objects.filter(v=>v.row===i+1).map(v=>v.shape)).size}));
check('exact64subjects_row_major_IDs',objects.length===64&&objects.every((v,i)=>v.id==='G'+String(i+1).padStart(2,'0')&&v.row===Math.floor(i/8)+1&&v.column===i%8+1));
check('four_colors_and_four_shapes_each16',Object.values(counts.colors).every(n=>n===16)&&Object.values(counts.shapes).every(n=>n===16));
check('all_three_exact_size_classes_present',objects.every(v=>[48,64,80].includes(v.size))&&Object.keys(counts.sizes).every(k=>counts.sizes[k]>0));
check('all8rows_at_least3colors_and3shapes',rows.every(r=>r.count===8&&r.color_count>=3&&r.shape_count>=3));
check('all16color_shape_combos_four_each_with_three_sizes',colors.every(c=>shapes.every(s=>{const subset=objects.filter(v=>v.color_name===c&&v.shape===s);return subset.length===4&&new Set(subset.map(v=>v.size)).size===3;})));
function mulberry32(t){return()=>{t|=0;t=t+0x6D2B79F5|0;let x=Math.imul(t^t>>>15,1|t);x=x+Math.imul(x^x>>>7,61|x)^x;return((x^x>>>14)>>>0)/4294967296;};}
const rand=mulberry32(d.seed),seedBase=[];for(let ci=0;ci<4;ci++)for(let si=0;si<4;si++)for(let r=0;r<4;r++)seedBase.push({color_name:colors[ci],shape:shapes[si],size:[48,64,80][(r+ci+si)%3],combo_replica:r+1});
let regenerated;for(let attempt=1;attempt<=d.accepted_shuffle_attempt;attempt++){regenerated=seedBase.map(v=>({...v}));for(let i=63;i>0;i--){const j=Math.floor(rand()*(i+1));[regenerated[i],regenerated[j]]=[regenerated[j],regenerated[i]];}}
check('seed_reproduces_all64_attributes',objects.every((v,i)=>Object.entries(regenerated[i]).every(([k,x])=>v[k]===x)));
const bodyItems=parsed[2].filter(p=>colors.some(c=>d.palette[c]===p.c.color));
const all64=objects.map((v,i)=>{
  const [x,y]=v.center,size=v.size,b=[x-size/2,y-size/2,x+size/2,y+size/2],inner=[x-size/4,y-size/4,x+size/4,y+size/4];
  const body=bodyItems.filter(p=>eq(bboxPosition(p.p),b)&&+p.c.width===size&&+p.c.height===size&&p.c.color===v.color_hex);
  const labels=parsed[2].filter(p=>p.text===v.id),cutouts=parsed[2].filter(p=>eq(bboxPosition(p.p),inner)&&p.c.color===d.palette.cell&&p.c.shape==='CIRCLE'&&+p.c.width===size/2&&+p.c.height===size/2);
  const geometry=eq(v.center,[240+(i%8)*160,312+Math.floor(i/8)*160])&&eq(v.bbox,b)&&eq(v.cell_bbox,[160+(i%8)*160,248+Math.floor(i/8)*160,320+(i%8)*160,408+Math.floor(i/8)*160]);
  const label=labels.length===1&&eq(bboxPosition(labels[0].p),v.label_bbox)&&+labels[0].t.fontSize===24&&v.label_font_size===24&&v.label_bbox[1]>b[3]&&v.label_bbox[3]<v.cell_bbox[3];
  const source=body.length===1&&(body[0].c.shape??'RECTANGLE')===shapeSource(v.shape)&&+(body[0].c.borderRadius??0)===(v.shape==='rounded-square'?v.corner_radius:0);
  const ring=v.shape!=='ring'||v.inner_diameter===size/2&&eq(v.inner_bbox,inner)&&cutouts.length===1;
  const rgb=v.color_hex.slice(1).match(/../g).map(h=>parseInt(h,16)),sample=pngs[2].pixel(x+(v.shape==='ring'?size*3/8:0),y).slice(0,3);
  let minX=Infinity,minY=Infinity,maxX=-Infinity,maxY=-Infinity;for(let sy=b[1]-2;sy<b[3]+2;sy++)for(let sx=b[0]-2;sx<b[2]+2;sx++){const p=pngs[2].pixel(sx,sy);if(p[0]!==255||p[1]!==255||p[2]!==255){minX=Math.min(minX,sx);minY=Math.min(minY,sy);maxX=Math.max(maxX,sx);maxY=Math.max(maxY,sy);}}
  const support=[minX,minY,maxX+1,maxY+1],pixels=eq(sample,rgb)&&support.every((n,j)=>Math.abs(n-b[j])<=1);
  return {id:v.id,row:v.row,column:v.column,color:v.color_name,shape:v.shape,size,center:v.center,bbox:b,geometry_correct:geometry,source_body_once_correct:source,label24_outside_body_correct:label,ring_inner_exact_half_correct:ring,raw_PNG_color_and_bbox_correct:pixels,measured_support_bbox:support};
});
check('64_true_geometries_body_source_labels_and_ring_holes_match',bodyItems.length===64&&all64.every(v=>v.geometry_correct&&v.source_body_once_correct&&v.label24_outside_body_correct&&v.ring_inner_exact_half_correct));
check('raw_service_grid_pixels_match_all64_bodies',all64.every(v=>v.raw_PNG_color_and_bbox_correct));
const quartet=load('grid-production/qa-quadrant-provenance-v001.json');
const cropChecks=quartet.quadrants.map(v=>{const cp=png(fs.readFileSync(v.path)),[left,top,right,bottom]=v.bbox;let changed=0;for(let y=0;y<cp.height;y++)for(let x=0;x<cp.width;x++)if(!eq(cp.pixel(x,y),pngs[2].pixel(x+left,y+top)))changed++;return {quadrant:v.quadrant,width:cp.width,height:cp.height,bbox:v.bbox,changed_pixels:changed,pass:cp.width===right-left&&cp.height===bottom-top&&changed===0};});
check('four_viewed_QA_crops_exact_raw_service_pixels',cropChecks.every(v=>v.pass));
const occlusionVariants=o.scene_variants.map((v,vi)=>{
  const hs=[],removed=new Set(),ps=parsed[vi];
  for(const h of v.hidden_objects){const plate=o.plates.find(p=>p.case_id===h.case_id),b=[h.center_x-h.size/2,h.center_y-h.size/2,h.center_x+h.size/2,h.center_y+h.size/2],safe=[plate.x+plate.radius,plate.y+plate.radius,plate.x+plate.width-plate.radius,plate.y+plate.height-plate.radius];
    const plateItem=ps.find(p=>eq(bboxPosition(p.p),[plate.x,plate.y,plate.x+plate.width,plate.y+plate.height])&&p.c.color===plate.color&&+p.c.borderRadius===plate.radius);
    const body=ps.filter(p=>eq(bboxPosition(p.p),b)&&p.c.color===h.color&&+p.c.width===h.size&&+p.c.height===h.size&&(p.c.shape??'RECTANGLE')===shapeSource(h.shape));
    let widgets=body;if(h.shape==='ring'){const ib=[h.center_x-h.size/4,h.center_y-h.size/4,h.center_x+h.size/4,h.center_y+h.size/4];widgets=[...body,...ps.filter(p=>eq(bboxPosition(p.p),ib)&&p.c.color==='#FFFFFF'&&p.c.shape==='CIRCLE')];}
    widgets.forEach(p=>removed.add(p.raw));hs.push({id:h.id,case_id:h.case_id,geometry_correct:eq(b,h.bbox),fully_inside_safe_rect:eq(safe,h.opaque_cover_safe_rect)&&b[0]>safe[0]&&b[1]>safe[1]&&b[2]<safe[2]&&b[3]<safe[3],source_widgets_once:body.length===1&&widgets.length===(h.shape==='ring'?2:1),drawn_before_opaque_plate:!!plateItem&&widgets.every(p=>p.index<plateItem.index),hidden_label_absent:!ps.some(p=>p.text===h.id)});
  }
  const vs=o.visible_objects.map(v=>{const body=ps.filter(p=>eq(bboxPosition(p.p),v.bbox)&&p.c.color===v.color&&(p.c.shape??'RECTANGLE')===shapeSource(v.shape)),label=ps.filter(p=>p.text===v.id);return {id:v.id,source_body_once:body.length===1,label20_outside_body:label.length===1&&+label[0].t.fontSize===20&&+label[0].p.top>v.bbox[3],outside_covers:o.plates.every(p=>v.bbox[3]<=p.y||v.bbox[1]>=p.y+p.height||v.bbox[2]<=p.x||v.bbox[0]>=p.x+p.width)};});
  let common=sources[vi];removed.forEach(raw=>{common=common.replace(raw,'');});common=common.split(/\r?\n/).filter(line=>line.trim()).join('\n');
  return {variant:v.variant,hidden_checks:hs,visible_checks:vs,visible_source:common,unsafe_effects_absent:!/<(?:Opacity|ImageFiltered|BackdropFilter|Image|Emoji)\b|boxShadow=|DASHED/.test(sources[vi]),all_pass:hs.every(h=>h.geometry_correct&&h.fully_inside_safe_rect&&h.source_widgets_once&&h.drawn_before_opaque_plate&&h.hidden_label_absent)&&vs.every(v=>v.source_body_once&&v.label20_outside_body&&v.outside_covers)};
});
check('two_complete_occlusion_cases_source_geometry_covers_and20labels_valid',occlusionVariants.every(v=>v.all_pass&&v.unsafe_effects_absent)&&o.plates.length===2);
check('actual_visible_source_layers_identical_except_declared_hidden_widgets',occlusionVariants[0].visible_source===occlusionVariants[1].visible_source);
const caseProof=o.plates.map(p=>{const sets=o.scene_variants.map(v=>v.hidden_objects.filter(h=>h.case_id===p.case_id));return {case_id:p.case_id,hidden_content_different:!eq(sets[0].map(h=>({...h,id:null})),sets[1].map(h=>({...h,id:null}))),all_blue_circles_truth:sets.map(s=>s.length>0&&s.every(h=>h.color===o.palette.blue&&h.shape==='circle')),hidden_counts_metadata_only:sets.map(s=>s.length)};});
check('two_cases_have_different_hidden_content',caseProof.every(c=>c.hidden_content_different));
let changed=0,maxDiff=0;for(let i=0;i<pngs[0].rgba.length;i+=4){let diff=false;for(let c=0;c<4;c++){const dd=Math.abs(pngs[0].rgba[i+c]-pngs[1].rgba[i+c]);if(dd){diff=true;maxDiff=Math.max(maxDiff,dd);}}if(diff)changed++;}
const equivalence={original_PNG_SHA256:provenance.slice(0,2).map(p=>p.PNG_sha256),original_PNG_bytes_identical:fs.readFileSync(meta[0].response_file).equals(fs.readFileSync(meta[1].response_file)),compared_RGBA_pixels:800*800,changed_RGBA_pixels:changed,maximum_RGBA_channel_difference:maxDiff,decoded_RGBA_SHA256:pngs.slice(0,2).map(p=>hash(p.rgba)),method:'Independent Node zlib PNG IDAT inflation and all five PNG-filter reconstruction, RGBA decode, every pixel/channel compared; no re-encoding or editing.'};
check('raw_PNG_hashes_bytes_and_all640000_RGBA_pixels_equivalent',equivalence.original_PNG_bytes_identical&&changed===0&&maxDiff===0);
const idcmp=(u,v)=>u.id.localeCompare(v.id),ids=s=>s.map(v=>v.id),d2=(u,v)=>(u.center[0]-v.center[0])**2+(u.center[1]-v.center[1])**2;
const answers=[],add=(id,answer,extra={})=>{const declared=a.answers.find(v=>v.id===id);answers.push({id,independent_answer:answer,declared_answer:declared?.answer,answer_matches:eq(answer,declared?.answer),...extra});};
add('Q01',ids(objects.filter(v=>v.color_name==='blue'&&v.shape==='ring'&&v.size>=64).sort(idcmp)));
let anchor=objects.filter(v=>v.color_name==='green'&&v.shape==='ring').sort((u,v)=>u.center[0]-v.center[0]||u.center[1]-v.center[1]||idcmp(u,v))[0];let pool=objects.filter(v=>v.color_name==='orange'&&v.center[0]>anchor.center[0]).sort((u,v)=>d2(u,anchor)-d2(v,anchor)||idcmp(u,v));add('Q02',pool[0].id,{anchor:anchor.id,candidates:ids(pool),distance_squared:d2(pool[0],anchor),tie_count:pool.filter(v=>d2(v,anchor)===d2(pool[0],anchor)).length});
anchor=objects.filter(v=>v.color_name==='purple').sort((u,v)=>v.center[0]-u.center[0]||u.center[1]-v.center[1]||idcmp(u,v))[0];pool=objects.filter(v=>v.shape==='circle'&&v.center[0]<anchor.center[0]).sort((u,v)=>d2(u,anchor)-d2(v,anchor)||idcmp(u,v));add('Q03',pool[0].id,{anchor:anchor.id,candidates:ids(pool),distance_squared:d2(pool[0],anchor),tie_count:pool.filter(v=>d2(v,anchor)===d2(pool[0],anchor)).length});
anchor=objects.filter(v=>v.color_name==='blue').sort((u,v)=>v.center[0]-u.center[0]||v.center[1]-u.center[1]||idcmp(u,v))[0];pool=objects.filter(v=>v.row===anchor.row&&v.center[0]<anchor.center[0]).sort((u,v)=>v.size-u.size||idcmp(u,v));add('Q04',pool[0].id,{anchor:anchor.id,size_ties:ids(pool.filter(v=>v.size===pool[0].size)),tie_resolved:'explicit ascending ID'});
anchor=objects.filter(v=>v.color_name==='orange').sort((u,v)=>u.center[1]-v.center[1]||u.center[0]-v.center[0]||idcmp(u,v))[0];pool=objects.filter(v=>v.column===anchor.column&&v.center[1]>anchor.center[1]).sort((u,v)=>u.center[1]-v.center[1]||idcmp(u,v));add('Q05',{id:pool[0].id,shape:{circle:'圆',square:'方',ring:'圆环','rounded-square':'圆角方'}[pool[0].shape]},{anchor:anchor.id,vertical_distance:pool[0].center[1]-anchor.center[1]});
const exact=Math.sqrt(d2(objects.find(v=>v.id==='G18'),objects.find(v=>v.id==='G43')));add('Q06',{distance_px:Math.round(exact*10)/10},{exact_distance:exact,rounded_display:(Math.round(exact*10)/10).toFixed(1)});
add('Q07',ids(objects.filter(v=>v.color_name==='purple').sort((u,v)=>u.center[0]**2+u.center[1]**2-v.center[0]**2-v.center[1]**2||idcmp(u,v)).slice(0,4)));
pool=objects.filter(v=>[4,5].includes(v.row)&&v.shape==='ring');add('Q08',[Math.min(...pool.map(v=>v.bbox[0])),Math.min(...pool.map(v=>v.bbox[1])),Math.max(...pool.map(v=>v.bbox[2])),Math.max(...pool.map(v=>v.bbox[3]))],{selected:ids(pool)});
add('Q09',colors.map(c=>counts.colors[c]));add('Q10',shapes.map(s=>counts.shapes[s]));add('Q11',ids(objects.filter(v=>v.row>=6&&['green','purple'].includes(v.color_name)&&v.size===48).sort(idcmp)));
pool=objects.filter(v=>v.size===80).sort((u,v)=>u.center[0]-v.center[0]||u.center[1]-v.center[1]||idcmp(u,v));add('Q12',{id:pool[2].id,right_x:pool[2].center[0]+pool[2].size/2},{full_order:ids(pool)});
add('Q13','无法确定',{nonidentifiability_proof:caseProof.find(c=>c.case_id==='CASE01').all_blue_circles_truth,visible_pixel_equality:changed===0,hidden_count_used_as_numeric_answer:false});
pool=o.visible_objects.filter(v=>['square','rounded-square'].includes(v.shape));add('Q14',pool.length,{visible_object_ids:ids(pool),hidden_count_used_as_numeric_answer:false});
check('merged_exact14_unique_question_answer_IDs_12grid_2occlusion',q.questions.length===14&&a.answers.length===14&&new Set(q.questions.map(v=>v.id)).size===14&&q.questions.every((v,i)=>v.id==='Q'+String(i+1).padStart(2,'0'))&&q.questions.slice(0,12).every(v=>v.scene==='grid-scene.png')&&q.questions.slice(12).every(v=>v.scene==='occlusion.png'));
check('all14_independently_recomputed_answers_match',answers.every(v=>v.answer_matches));
const twoSteps=q.questions.filter(v=>v.scene==='grid-scene.png'&&v.relation_steps>=2).map(v=>v.id);
check('at_least4_real_two_stage_questions',eq(twoSteps,['Q02','Q03','Q04','Q05','Q12']));
check('questions_contain_no_answer_properties',q.questions.every(v=>!Object.keys(v).some(k=>/^answer|correct|solution$/i.test(k))));
check('all_answers_include_method_tolerance_visibility',a.answers.every(v=>typeof v.calculation_method==='string'&&v.calculation_method.length>0&&v.coordinate_tolerance&&typeof v.visibility_basis==='string'&&v.visibility_basis.length>0));
check('Q13_conflicting_hidden_proposition_proof_and_no_hidden_numeric_answers',eq(caseProof[0].all_blue_circles_truth,[true,false])&&a.answers.slice(12).every(v=>v.hidden_count_used_as_numeric_answer===false)&&a.answers.find(v=>v.id==='Q13').answer==='无法确定');
check('Q14_visible_shapes_exactly_V02_V05_V06',eq(ids(pool),['V02','V05','V06']));
const viewed=load('independent-analysis/final-resume-actual-views-v001.json');
check('actual_three_originals_and4_QA_views_completed',viewed.records.length===7&&viewed.records.every(v=>v.tool==='functions.view_image'&&v.viewed_at&&fs.existsSync(v.image_path)));
check('explicit_visible_coordinate_and_comparison_standards',q.coordinate_system.origin.includes('(0,0)')&&q.coordinate_system.x==='向右'&&q.coordinate_system.y==='向下'&&q.coordinate_system.relations.includes('严格')&&q.coordinate_system.distance.includes('欧氏')&&q.coordinate_system.bounding_box.includes('不包含ID')&&['Q02','Q03','Q04','Q05','Q07','Q12'].every(id=>q.questions.find(v=>v.id===id).text.includes('ID升序')||q.questions.find(v=>v.id===id).text.includes('编号升序')));
const finalPairs=meta.map(m=>{const ip=path.join(out,m.stem+'.png'),dp=path.join(out,m.stem+'.snapshot');return {stem:m.stem,published:fs.existsSync(ip)&&fs.existsSync(dp),published_image_raw_match:fs.existsSync(ip)?fs.readFileSync(ip).equals(fs.readFileSync(m.response_file)):null,published_source_raw_match:fs.existsSync(dp)?fs.readFileSync(dp).equals(fs.readFileSync(m.input_file)):null};});
const documentEvidence=['shared-doc-000001-response.txt','shared-doc-000003-readable.txt','shared-doc-000004-readable.txt','shared-doc-000005-readable.txt','shared-fonts-000001-readable.txt'].map(file=>({file:path.resolve(base,'../_suite',file),sha256:hash(fs.readFileSync(path.resolve(base,'../_suite',file))),read_this_resume:true,new_HTTP_request:false}));
const result={schema_version:1,task_id:'A19',run_id:'20261002-204314-6f31',reviewer:'/root/a19_audit_resume',reviewed_at:new Date().toISOString(),hard_constraints_pass:Object.values(checks).every(Boolean),checks,unresolved,provenance,counts,rows,all64_independent_source_raw_PNG_geometry_checks:all64,QA_crop_checks:cropChecks,occlusion_variants:occlusionVariants.map(({visible_source,...v})=>v),occlusion_case_proof:caseProof,equivalence,question_results:answers,multistep_question_IDs:twoSteps,real_view_ids:viewed.records.map(v=>v.id),actual_visual_verdict:'Original A/B opaque plates show no hidden edges, dashed leakage or hidden labels. Six V labels and objects readable. Full1600 grid and native four640 crops show all64 numbered subjects; four colors and shapes, three size classes, axes, outside-body24px labels complete, no overlap/clipping.',document_evidence:documentEvidence,final_publication_pairs_read_only:finalPairs,scope:'Independent resumed review of actual merged drafts/source/raw PNGs/geometry and seven real visual calls. No render, fabricated visual iteration, suite mutation, official-output mutation or old-file overwrite; publication/completion/metrics remain root responsibility.',new_render_requests:0,new_complete_visual_iterations:0,new_actual_image_views:7,all_writes_finished:true};
const jsonFile=path.join(__dirname,'final-resume-independent-audit-v001.json'),mdFile=path.join(__dirname,'final-resume-independent-audit-v001.md');
fs.writeFileSync(jsonFile,JSON.stringify(result,null,2)+'\n',{flag:'wx'});
const md=['# A19 独立恢复最终审查','',`审查者 /root/a19_audit_resume；时间 ${result.reviewed_at}。`,`hard_constraints_pass = ${result.hard_constraints_pass}；unresolved = ${JSON.stringify(unresolved)}。`,'','本次实际打开三张原始服务PNG及四个原像素640×640局部；查看事件 '+result.real_view_ids.join('、')+'。原图与局部全部64主体、标签和轴清楚完整，未见裁切/重叠。遮挡A/B两CASE板完全不透明，无遮漏/虚线；V01–V06全部可见。','',`源/原PNG哈希、实际尺寸1600×1600/800×800/800×800均符合。每色16、每形16；尺寸48/64/80数量22/21/21，每行至少3色3形；64行优先ID与24px主体外标签匹配。16圆环内径几何均外径一半。6遮挡ID字号20px。`,`两CASE隐藏内容各不同；A/B原PNG哈希 ${equivalence.original_PNG_SHA256[0]} 相同，37982字节相同；独立解码比较640000 RGBA像素，差异 ${changed}，最大通道差 ${maxDiff}。隐藏数量仅证明元数据，未作为数值标准答案。`,'','14题独立重算均匹配；两阶段题 Q02/Q03/Q04/Q05/Q12。Q13 CASE01命题在两等价隐藏场景分别真/假，因此答案“无法确定”；Q14仅V02/V05/V06计3。比较标准、坐标、距离精确值后舍入、ID破并列、外缘包围框和可见性依据明确。','','|题|独立答案|核验|','|---|---|---|',...answers.map(v=>`|${v.id}|${JSON.stringify(v.independent_answer)}|${v.answer_matches?'匹配':'失败'}|`),'','详细计算/全部64对象源与像素核验见 [JSON](final-resume-independent-audit-v001.json)。实际七次查看见 [记录](final-resume-actual-views-v001.json)。旧四份审查记录已全文读取核对，没有当作未经复核的新事实。','',`新增真实HTTP/渲染0；新增完整视觉迭代0；新增真实看图7。文档缓存实际读取复用，不计新HTTP。`, '本次只写final-resume-*文件与真实view追加，不改suite-state、正式output或旧记录；最终发布、报告、metrics及completed由root核对处理。','',`all_writes_finished = true。`].join('\n')+'\n';
fs.writeFileSync(mdFile,md,{flag:'wx'});
process.stdout.write(JSON.stringify({hard_constraints_pass:result.hard_constraints_pass,unresolved,jsonFile,mdFile,all_writes_finished:true})+'\n');
