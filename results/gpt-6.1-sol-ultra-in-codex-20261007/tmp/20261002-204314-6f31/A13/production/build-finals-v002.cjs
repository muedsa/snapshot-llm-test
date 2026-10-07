'use strict';
const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'../../../..'),s=require(path.join(root,'tmp/20261002-204314-6f31/_suite/suite.cjs'));
const {Canvas}=require(path.join(root,'tmp/20261002-204314-6f31/_suite/dsl.cjs'));
const selectionPath=path.join(__dirname,'direction-selection-v001.json');
const selection=JSON.parse(fs.readFileSync(selectionPath,'utf8'));
if(selection.selected_direction!=='direction-A'||selection.final_assets_created!==false)throw new Error('Requires actual archived preview decision before final construction');
const write=(name,v)=>fs.writeFileSync(path.join(__dirname,name),typeof v==='string'?v:JSON.stringify(v,null,2)+'\n',{flag:'wx'});
const color={navy:'#133E49',violet:'#7966FF',paper:'#F4F3FF',pale:'#E3DEFF',muted:'#4D6470'};
const font='Inter,Noto Sans CJK SC';
const mono='DejaVu Sans Mono,Noto Sans CJK SC';
const mappings=[];
function symbol(c,x,y,size,palette,application){
  const frame=size*.8,offset=size*.2,stroke=size*.125,radius=size*.15;
  c.rect(x,y,frame,frame,'transparent',{border:stroke+' SOLID '+palette[0],radius});
  c.rect(x+offset,y+offset,frame,frame,'transparent',{border:stroke+' SOLID '+palette[1],radius});
  mappings.push({application,bounds:{x,y,width:size,height:size},unit_geometry:{frame_ratio:.8,offset_ratio:.2,stroke_ratio:.125,radius_ratio:.15},components:[{type:'hollow_rounded_square',x,y,width:frame,height:frame,stroke,radius,color:palette[0]},{type:'hollow_rounded_square',x:x+offset,y:y+offset,width:frame,height:frame,stroke,radius,color:palette[1]}],major_component_count:2,background_is_transparent_or_application_color:true,same_geometry_generator:'symbol(c,x,y,size,palette,application)',minimum_clear_space:stroke});
}
const textmap=[];
function text(c,application,id,x,y,w,h,value,size,col=color.navy,o={}){
 c.text(x,y,w,h,value,size,col,{font,...o});
 textmap.push({application,id,source_text:value,position:{x,y,width:w,height:h},font_family:o.font??font,font_size:size,color:col,font_style:o.bold?'BOLD':'NORMAL',raw_cdata:true});
}
function colorIcon(){
 const c=new Canvas(512,512,{background:'transparent',clipBehavior:'NONE'});
 symbol(c,96,96,320,[color.navy,color.violet],'symbol-color');return c;
}
function blackIcon(){
 const c=new Canvas(512,512,{background:'transparent',clipBehavior:'NONE'});
 symbol(c,96,96,320,['#000000','#000000'],'symbol-black');return c;
}
function banner(){
 const c=new Canvas(1200,400,{background:color.paper,font});
 symbol(c,56,72,256,[color.navy,color.violet],'brand-banner');
 text(c,'brand-banner','wordmark',384,104,752,84,'叠光 Layerlight',56,color.navy,{bold:true});
 text(c,'brand-banner','tagline',384,212,752,58,'把复杂信息，组织成清晰画面',32,color.muted);
 c.rect(384,310,752,4,color.violet);
 return c;
}
function poster(){
 const c=new Canvas(1080,1350,{background:color.paper,font});
 c.rect(64,64,220,52,color.pale,{radius:8});
 text(c,'launch-poster','open-beta',80,76,188,38,'OPEN BETA',26,color.violet,{font:mono,bold:true});
 text(c,'launch-poster','wordmark',64,156,952,88,'叠光 Layerlight',64,color.navy,{bold:true});
 text(c,'launch-poster','tagline',64,270,952,62,'把复杂信息，组织成清晰画面',34,color.muted);
 symbol(c,260,440,560,[color.navy,color.violet],'launch-poster');
 c.rect(64,1080,952,3,color.violet);
 text(c,'launch-poster','date-mode',64,1130,952,56,'2026.11.07 · ONLINE',32,color.navy,{font:mono,bold:true});
 text(c,'launch-poster','website',64,1230,952,48,'layerlight.example.org',30,color.muted,{font:mono});
 return c;
}
(async()=>{
const pages=[['symbol-color',colorIcon(),512,512,'visual','A13-preview-v001-direction-A','A13-final-v002-symbol-color'],['symbol-black',blackIcon(),512,512,'baseline',null,'A13-final-v002-symbol-black'],['brand-banner',banner(),1200,400,'baseline',null,'A13-final-v002-brand-banner'],['launch-poster',poster(),1080,1350,'baseline',null,'A13-final-v002-launch-poster']];
write('brand-system-draft-v001.json',{schema_version:1,task_id:'A13',run_id:'20261002-204314-6f31',status:'awaiting_actual_final_visual_review',brand:{name:'叠光 / Layerlight',concept:'信息叠加后仍然清晰'},colors:color,font_family:font,selected_direction:'direction-A',direction_selection_evidence:selectionPath,preview_selection_recorded_at:selection.selection_recorded_at,final_construction_started_at:new Date().toISOString(),icon:{major_component_count:2,normalized_bounds:320,frame_size:256,layer_offset:64,stroke:40,radius:48,common_negative_space:{rectangle:[200,200,112,112],size_in_32px:7},minimum_icon_display_size:32,minimum_clear_space_rule:'At least one stroke width (1/8 symbol outer bounding box) between symbol and other content.',black_variant:'Same geometry, both stroke colors #000000, transparent interiors; actual alpha and nontransparent RGB checked after service.'},application_mappings:mappings,text_map:textmap,no_external_assets:true,no_image_tag:true,geometry_rule_reused_in_applications:true,poster_composition:'Vertical release announcement: beta label and wordmark above centered hero symbol, date and URL in separate footer; independent of horizontal banner composition.',planned_visual_refinement:'Selected A source stroke32→40 makes about2px→2.5px at32. Radius40→48 keeps corner inner radius positive and proportional.'});
for(const [name,c,w,h,type,parent_version,version_id] of pages){
 const dsl=c.toString();write(name+'-v002.snapshot',dsl);
 const r=await s.render('A13',dsl,{version_id,parent_version,type,stem:name,width:w,height:h,case_id:name,before_view_id:type==='visual'?'A13-view-000001':null,changes:type==='visual'?'After actual512/32 preview choice, thicken the same two frames from32 to40px; radius40→48, offset/size unchanged.':null,purpose:'A13 '+name+' final candidate constructed after true preview selection, pure shared DSL geometry'});
 console.log(JSON.stringify({name,ok:r.ok,meta_path:r.meta_path,image_path:r.image_path,error:r.error_summary}));
}
})().catch(e=>{console.error(e);process.exitCode=1});
