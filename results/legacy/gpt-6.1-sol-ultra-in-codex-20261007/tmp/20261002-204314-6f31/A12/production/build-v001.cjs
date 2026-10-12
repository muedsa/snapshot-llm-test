'use strict';
const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'../../../..');
const s=require(path.join(root,'tmp/20261002-204314-6f31/_suite/suite.cjs'));
const {Canvas}=require(path.join(root,'tmp/20261002-204314-6f31/_suite/dsl.cjs'));
const input=JSON.parse(fs.readFileSync(path.join(root,'tasks/A12-responsive-system/inputs/content.json'),'utf8'));
fs.mkdirSync(__dirname,{recursive:true});
const write=(name,v)=>fs.writeFileSync(path.join(__dirname,name),typeof v==='string'?v:JSON.stringify(v,null,2)+'\n',{flag:'wx'});
const color={paper:'#F5F4EE',ink:'#192F35',muted:'#4E656A',teal:'#0A8686',lime:'#D8F079',card:'#FFFFFF',border:'#D9DDD2'};
const fonts={body:'Inter,Noto Sans CJK SC',mono:'DejaVu Sans Mono,Noto Sans CJK SC'};
const map=[];
function text(c,layout,field,x,y,w,h,value,size,col=color.ink,o={}){
  c.text(x,y,w,h,value,size,col,{font:fonts.body,...o});
  map.push({layout,field,source_text:value,page_dimensions:{width:c.width,height:c.height},position:{x,y,width:w,height:h},font_family:o.font??fonts.body,font_size:size,color:col,font_style:o.bold?'BOLD':'NORMAL',text_align:o.align??'START',source_preserved:true,source_encoding:'Raw CDATA, unmodified source string',line_height:o.height??null,actual_visual_status:'awaiting_render_and_review'});
}
function motif(c,x,y,size,line){
  // Same two interlocking corner frames, rebuilt from actual DSL Containers.
  // No raster asset, Image, SVG or canvas drawing is embedded.
  c.rect(x,y,size,size,color.paper,{border:line+' SOLID '+color.teal,radius:3});
  const offset=size*.24;
  c.rect(x+offset,y+offset,size*.72,size*.72,color.lime,{border:line+' SOLID '+color.ink,radius:3});
  c.rect(x+offset,y+offset,line,size*.28,color.ink);
  c.rect(x+offset,y+offset,size*.28,line,color.ink);
}
function card(c,layout,item,index,x,y,w,h,mode){
  c.rect(x,y,w,h,color.card,{radius:mode.radius,border:'1 SOLID '+color.border});
  const badge=mode.badge,bx=x+mode.pad,by=y+(h-badge)/2;
  c.rect(bx,by,badge,badge,color.lime,{radius:mode.badgeRadius});
  text(c,layout,`cards[${index}].id`,bx,by+(badge-mode.idH)/2,badge,mode.idH,item.id,mode.idSize,color.ink,{font:fonts.mono,bold:true,align:'CENTER'});
  const tx=bx+badge+mode.textGap,tw=x+w-mode.pad-tx;
  text(c,layout,`cards[${index}].title`,tx,y+mode.titleY,tw,mode.titleH,item.title,mode.titleSize,color.ink,{bold:true});
  text(c,layout,`cards[${index}].detail`,tx,y+mode.detailY,tw,mode.detailH,item.detail,mode.detailSize,color.muted,{height:mode.detailLineHeight??1.25});
}
function button(c,layout,x,y,w,h,size){
  c.rect(x,y,w,h,color.teal,{radius:10});
  text(c,layout,'cta',x+16,y+(h-(size+12))/2,w-32,size+12,input.cta,size,color.card,{bold:true,align:'CENTER',softWrap:'false',maxLines:1});
}
function mobile(){
  const c=new Canvas(360,800,{background:color.paper,font:fonts.body});
  text(c,'mobile','title',16,16,328,100,input.title,40,color.ink,{bold:true,height:1.1});
  text(c,'mobile','subtitle',16,124,328,28,input.subtitle,16,color.muted);
  text(c,'mobile','date',16,160,128,26,input.date,16,color.teal,{font:fonts.mono,bold:true});
  text(c,'mobile','time',156,160,170,26,input.time,16,color.teal,{font:fonts.mono,bold:true});
  text(c,'mobile','location',16,196,244,28,input.location,16,color.muted);
  motif(c,292,178,44,2);
  const mode={radius:10,pad:16,badge:32,badgeRadius:4,idH:24,idSize:16,textGap:10,titleY:7,titleH:26,titleSize:18,detailY:34,detailH:22,detailSize:16,detailLineHeight:1.2};
  input.cards.forEach((v,i)=>card(c,'mobile',v,i,16,244+i*70,328,62,mode));
  button(c,'mobile',16,704,328,44,16);
  text(c,'mobile','website',16,764,328,20,input.website,16,color.ink,{font:fonts.mono,align:'CENTER',softWrap:'false',maxLines:1});
  return c;
}
function tablet(){
  const c=new Canvas(768,1024,{background:color.paper,font:fonts.body});
  text(c,'tablet','title',32,40,704,90,input.title,64,color.ink,{bold:true,height:1.1});
  text(c,'tablet','subtitle',32,148,704,56,input.subtitle,28,color.muted);
  text(c,'tablet','date',32,228,240,40,input.date,24,color.teal,{font:fonts.mono,bold:true});
  text(c,'tablet','time',286,228,264,40,input.time,24,color.teal,{font:fonts.mono,bold:true});
  text(c,'tablet','location',32,282,480,40,input.location,24,color.muted);
  motif(c,628,218,86,3);
  const mode={radius:12,pad:20,badge:42,badgeRadius:5,idH:32,idSize:20,textGap:16,titleY:30,titleH:44,titleSize:26,detailY:84,detailH:48,detailSize:22};
  input.cards.forEach((v,i)=>card(c,'tablet',v,i,32+(i%2)*360,354+Math.floor(i/2)*162,344,146,mode));
  button(c,'tablet',32,880,704,60,24);
  text(c,'tablet','website',32,966,704,26,input.website,20,color.ink,{font:fonts.mono,align:'CENTER',softWrap:'false',maxLines:1});
  return c;
}
function desktop(){
  const c=new Canvas(1440,900,{background:color.paper,font:fonts.body});
  text(c,'desktop','title',48,64,472,208,input.title,78,color.ink,{bold:true,height:1.1});
  text(c,'desktop','subtitle',48,304,472,88,input.subtitle,30,color.muted,{height:1.35});
  text(c,'desktop','date',48,438,472,42,input.date,26,color.teal,{font:fonts.mono,bold:true});
  text(c,'desktop','time',48,492,472,42,input.time,26,color.teal,{font:fonts.mono,bold:true});
  text(c,'desktop','location',48,548,472,42,input.location,26,color.muted);
  motif(c,1226,62,126,4);
  c.line(568,238,1392,238,color.teal,3);
  const mode={radius:12,pad:24,badge:48,badgeRadius:6,idH:36,idSize:22,textGap:18,titleY:34,titleH:48,titleSize:30,detailY:94,detailH:56,detailSize:24};
  input.cards.forEach((v,i)=>card(c,'desktop',v,i,568+(i%2)*424,286+Math.floor(i/2)*184,400,168,mode));
  button(c,'desktop',48,706,472,76,26);
  text(c,'desktop','website',48,814,472,38,input.website,24,color.ink,{font:fonts.mono,softWrap:'false',maxLines:1});
  return c;
}
function stage(){
  const c=new Canvas(1920,1080,{background:color.paper,font:fonts.body});
  text(c,'stage','title',64,80,628,234,input.title,88,color.ink,{bold:true,height:1.1});
  text(c,'stage','subtitle',64,350,628,84,input.subtitle,34,color.muted,{height:1.35});
  text(c,'stage','date',64,466,628,52,input.date,32,color.teal,{font:fonts.mono,bold:true});
  text(c,'stage','time',64,534,628,52,input.time,32,color.teal,{font:fonts.mono,bold:true});
  text(c,'stage','location',64,604,628,52,input.location,32,color.muted);
  motif(c,1640,76,152,5);
  c.line(754,280,1856,280,color.teal,4);
  const mode={radius:16,pad:24,badge:48,badgeRadius:6,idH:38,idSize:24,textGap:16,titleY:68,titleH:52,titleSize:32,detailY:136,detailH:84,detailSize:26,detailLineHeight:1.35};
  input.cards.forEach((v,i)=>card(c,'stage',v,i,754+(i%3)*376,340+Math.floor(i/3)*276,350,252,mode));
  button(c,'stage',64,850,628,80,30);
  text(c,'stage','website',64,974,628,42,input.website,28,color.ink,{font:fonts.mono,softWrap:'false',maxLines:1});
  return c;
}
const tokens={schema_version:1,task_id:'A12',run_id:'20261002-204314-6f31',colors:color,fonts,font_cache:'tmp/20261002-204314-6f31/_suite/shared-fonts-000001-response.txt',components:{card:{fill:'card',stroke:'border',radius_by_layout:{mobile:10,tablet:12,desktop:12,stage:16},id_badge:'lime filled rounded square, mono ID, same original source ID'},cta:{fill:'teal',foreground:'card',radius:10,full_original_text:true},decorative_motif:'Two interlocking outlined corner frames from Container rectangles; same motif repositions/scales per canvas',title:{weight:'BOLD',color:'ink',natural_wrap:true,source_text_unmodified:true}},breakpoints:{mobile:{width:360,height:800,safe_margin:16,main_title:40,body:16,card_title:18,card_gap:8,card_columns:1},tablet:{width:768,height:1024,safe_margin:32,main_title:64,body:22,card_title:26,card_gap:16,card_columns:2},desktop:{width:1440,height:900,safe_margin:48,main_title:78,body:24,card_title:30,card_gap:24,card_columns:2},stage:{width:1920,height:1080,safe_margin:64,main_title:88,body:26,card_title:32,card_gap:26,card_columns:3}},source_data:'tasks/A12-responsive-system/inputs/content.json',all_content_from_source:true,no_external_images:true};
(async()=>{
  const pages=[['mobile',mobile()],['tablet',tablet()],['desktop',desktop()],['stage',stage()]];
  write('design-tokens-draft-v001.json',tokens);
  write('content-map-draft-v001.json',{schema_version:1,task_id:'A12',run_id:'20261002-204314-6f31',status:'awaiting_actual_visual_review',original_input:input,fields:map,expected_field_count_per_layout:25,expected_total_field_count:100});
  for(const [name,c] of pages){
    const dsl=c.toString();write(name+'-v001.snapshot',dsl);
    const result=await s.render('A12',dsl,{version_id:'A12-v001-'+name,type:'baseline',stem:name,width:c.width,height:c.height,case_id:name,purpose:'A12 full source event poster at '+name+' breakpoint'});
    console.log(JSON.stringify({name,ok:result.ok,meta_path:result.meta_path,image_path:result.image_path,dimension_error:result.dimension_error??null}));
  }
})().catch(e=>{console.error(e);process.exitCode=1});
