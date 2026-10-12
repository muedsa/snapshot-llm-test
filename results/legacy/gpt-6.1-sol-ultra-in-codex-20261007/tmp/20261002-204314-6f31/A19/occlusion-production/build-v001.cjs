'use strict';
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const s=require('../../_suite/suite.cjs');const {Canvas}=require('../../_suite/dsl.cjs');
const dir=__dirname,write=(f,v)=>fs.writeFileSync(path.join(dir,f),typeof v==='string'?v:JSON.stringify(v,null,2)+'\n',{flag:'wx'}),sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const palette={blue:'#2964D8',orange:'#E69B5D',green:'#36A887',purple:'#8060C8'};
const plates=[{case_id:'CASE01',x:84,y:298,width:264,height:252,radius:14,color:'#203957'},{case_id:'CASE02',x:452,y:298,width:264,height:252,radius:14,color:'#203957'}];
const visible=[
 {id:'V01',case_id:'CASE01',shape:'circle',color:palette.blue,size:64,center_x:128,center_y:620},
 {id:'V02',case_id:'CASE01',shape:'square',color:palette.orange,size:64,center_x:216,center_y:620},
 {id:'V03',case_id:'CASE01',shape:'ring',color:palette.green,size:64,inner_diameter:32,center_x:304,center_y:620},
 {id:'V04',case_id:'CASE02',shape:'circle',color:palette.purple,size:64,center_x:496,center_y:620},
 {id:'V05',case_id:'CASE02',shape:'square',color:palette.green,size:64,center_x:584,center_y:620},
 {id:'V06',case_id:'CASE02',shape:'rounded-square',color:palette.orange,size:64,corner_radius:14,center_x:672,center_y:620}
].map(o=>({...o,bbox:[o.center_x-o.size/2,o.center_y-o.size/2,o.center_x+o.size/2,o.center_y+o.size/2],id_font_size:20,visibility:'fully-visible'}));
const hidden={A:[
 {id:'A-C1-H01',case_id:'CASE01',shape:'circle',color:palette.blue,size:120,center_x:216,center_y:425},
 {id:'A-C2-H01',case_id:'CASE02',shape:'ring',color:palette.orange,size:80,inner_diameter:40,center_x:522,center_y:390},
 {id:'A-C2-H02',case_id:'CASE02',shape:'square',color:palette.purple,size:72,center_x:641,center_y:476}
],B:[
 {id:'B-C1-H01',case_id:'CASE01',shape:'circle',color:palette.blue,size:60,center_x:146,center_y:363},
 {id:'B-C1-H02',case_id:'CASE01',shape:'square',color:palette.orange,size:58,center_x:261,center_y:367},
 {id:'B-C1-H03',case_id:'CASE01',shape:'ring',color:palette.green,size:72,inner_diameter:36,center_x:172,center_y:486},
 {id:'B-C1-H04',case_id:'CASE01',shape:'rounded-square',color:palette.purple,size:70,corner_radius:18,center_x:267,center_y:479},
 ...[366,476].flatMap((cy,row)=>[504,588,672].map((cx,col)=>({id:'B-C2-H'+String(row*3+col+1).padStart(2,'0'),case_id:'CASE02',shape:'circle',color:[palette.green,palette.purple,palette.blue,palette.orange][(row*3+col)%4],size:40,center_x:cx,center_y:cy})))
]};
function drawObject(c,o){const half=o.size/2;if(o.shape==='circle'||o.shape==='ring'){c.circle(o.center_x,o.center_y,half,o.color);if(o.shape==='ring')c.circle(o.center_x,o.center_y,o.inner_diameter/2,'#FFFFFF');}else c.rect(o.center_x-half,o.center_y-half,o.size,o.size,o.color,o.shape==='rounded-square'?{radius:o.corner_radius}:{});}
function visibleLayer(c){
 // Identical visible bytes/geometry in both source trees; no hidden labels.
 c.text(44,44,712,65,'可见的，才是证据',40,'#172D48',{bold:true});
 c.text(44,120,712,38,'专用遮挡场景 / Opaque evidence',24,'#536780');
 for(const p of plates){
  const panelX=p.x-40;c.rect(panelX,204,344,516,'#FFFFFF',{radius:18,border:'1 SOLID #D8E3EE'});
  c.text(panelX+24,228,296,44,p.case_id==='CASE01'?'CASE 01':'CASE 02',26,'#172D48',{bold:true});
 }
}
function finalCoverAndVisibleObjects(c){
 for(const p of plates){c.rect(p.x,p.y,p.width,p.height,p.color,{radius:p.radius});c.text(p.x+12,p.y+98,p.width-24,50,'遮挡板',28,'#FFFFFF',{align:'CENTER',bold:true});}
 for(const o of visible){drawObject(c,o);c.text(o.center_x-40,672,80,30,o.id,20,'#536780',{align:'CENTER'});}
}
const scenes=[];
for(const variant of ['A','B']){
 const c=new Canvas(800,800,{background:'#F1F4F8',font:'Inter,Noto Sans CJK SC'});visibleLayer(c);
 const hs=hidden[variant].map(o=>{const half=o.size/2,p=plates.find(p=>p.case_id===o.case_id),bbox=[o.center_x-half,o.center_y-half,o.center_x+half,o.center_y+half],safe=[p.x+p.radius,p.y+p.radius,p.x+p.width-p.radius,p.y+p.height-p.radius],inside=bbox[0]>=safe[0]&&bbox[1]>=safe[1]&&bbox[2]<=safe[2]&&bbox[3]<=safe[3];if(!inside)throw Error('Hidden object outside opaque safe region '+o.id);drawObject(c,o);return {...o,bbox,visibility:'fully-hidden',opaque_cover_safe_rect:safe,fully_inside_cover_safe_rect:inside};});
 finalCoverAndVisibleObjects(c);
 const stem=variant==='A'?'occlusion':'occlusion-alternative',dsl=c.toString()+'\n';write(stem+'-v001.snapshot',dsl);
 scenes.push({variant,stem,seed:'A19-occlusion-fixed-geometry-v001-'+variant,dimensions:[800,800],hidden_objects:hs,hidden_counts_by_case:Object.fromEntries(plates.map(p=>[p.case_id,hs.filter(o=>o.case_id===p.case_id).length])),source_dsl:path.join(dir,stem+'-v001.snapshot'),source_dsl_sha256:sha(dsl)});
}
write('scene-data-occlusion-v001.json',{schema_version:1,task_id:'A19',run_id:'20261002-204314-6f31',coordinate_origin:'top-left; +x right, +y down; pixels',palette,plates,visible_objects:visible,visible_source_layers_identical:true,cover_alpha:1,hidden_have_no_shadow_or_filter:true,hidden_drawn_before_opaque_covers:true,scene_variants:scenes,geometry_method:'All hidden full bboxes inside rectangular area inset by plate corner radius14; outer curved-edge antialias cannot expose hidden objects.',audience_question_scope:'Only final visible pixels and V labels; hidden counts are proof metadata, never a numeric question answer.'});
write('questions-occlusion-draft-v001.json',[
 {id:'Q13',scene:'occlusion',category:'visibility/insufficient-information',question:'只根据800×800遮挡图的可见像素，CASE 01遮挡板后的全部主体是否都是蓝色圆？能否作出唯一结论？',comparison_standard:'只根据最终可见像素；遮挡板后的内容不可见，不读取DSL或scene-data。',coordinate_origin:'左上角(0,0)，x向右、y向下'},
 {id:'Q14',scene:'occlusion',category:'visible-shape-count',question:'两张白色场景框中，遮挡板之外完整可见的方形或圆角方形主体共几个？只计V开头编号对应主体，不计场景框、遮挡板、文字或圆环。',comparison_standard:'方形与圆角方形均四边等长；以V编号主体计数。',coordinate_origin:'左上角(0,0)，x向右、y向下'}
]);
write('answers-occlusion-draft-v001.json',[
 {question_id:'Q13',answer:'无法确定',method:'CASE01遮挡板是不透明完整遮挡，可见图中没有该板后主体形状/颜色证据；因此不能从可见像素确认全部为蓝圆。两真实可見等价场景提供反例证明：A满足此命题，B不满足；二者原PNG/RGBA比较由equivalence证明。',coordinate_tolerance_pixels:2,visibility_basis:'隐藏主体的全部几何支持位于opaque cover内部安全矩形；无虚线、露边或隐藏标签。',hidden_count_used_as_numeric_answer:false},
 {question_id:'Q14',answer:3,object_ids:['V02','V05','V06'],method:'逐一检查最终可见V编号主体：V02/V05为方形，V06为圆角方形；V01/V04是圆，V03是圆环。仅对可见集合计数。',coordinate_tolerance_pixels:2,visibility_basis:'六主体完整位于遮挡板外；V02/V05/V06的64×64bbox和ID在最终图清楚可见。',hidden_count_used_as_numeric_answer:false}
]);
const sources=['tasks/A19-visual-puzzle-authoring/TASK.md','tasks/A19-visual-puzzle-authoring/AGENTS.md','tasks/A19-visual-puzzle-authoring/task.json','tasks/A19-visual-puzzle-authoring/run-config.json','run-config.json'].map(f=>({path:path.resolve(process.cwd(),f),sha256:sha(fs.readFileSync(f))}));
write('source-read-provenance-v001.json',{read_at:new Date().toISOString(),sources,actual_cached_document_reuse:['shared-doc-000001-response.txt (guide)','shared-doc-000003-readable.txt (parser)','shared-doc-000004-readable.txt (registered Container/shape/Border/Text tags)','shared-doc-000005-readable.txt (layout)','shared-fonts-000001-readable.txt (Inter,Noto Sans CJK SC)'],cache_root:path.resolve(dir,'../../_suite'),same_producer_actual_prior_reads:'A17 actual complete cache reads and A18 layout reread retained; reuse no additional HTTP',new_document_http_requests:0});
(async()=>{for(const scene of scenes){const dsl=fs.readFileSync(scene.source_dsl,'utf8'),r=await s.render('A19',dsl,{version_id:'A19-occlusion-'+scene.variant+'-v001',type:scene.variant==='A'?'baseline':'alternative',stem:scene.stem,case_id:'occlusion-'+scene.variant,independent_case:false,width:800,height:800,purpose:'Two fully hidden cases with distinct hidden scenes and identical visible layer: variant '+scene.variant});const {bytes,body,text,json,...meta}=r;write(scene.stem+'-render-result-v001.json',meta);console.log(JSON.stringify({variant:scene.variant,stem:scene.stem,ok:r.ok,status:r.http_status,metadata:r.meta_path,image:r.image_path,error:r.error_summary}));if(!r.ok||r.dimension_error)throw Error(r.error_summary||r.dimension_error);}})().catch(e=>{write('production-failure-v001.json',{at:new Date().toISOString(),error:String(e)});process.exitCode=1;});
