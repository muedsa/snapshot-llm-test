'use strict';
const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'../../../..'),s=require(path.join(root,'tmp/20261002-204314-6f31/_suite/suite.cjs'));
const {Canvas}=require(path.join(root,'tmp/20261002-204314-6f31/_suite/dsl.cjs'));
const source=path.join(root,'tasks/A14-content-stress-batch/inputs/cards.json');
const cards=JSON.parse(fs.readFileSync(source,'utf8'));
fs.mkdirSync(__dirname,{recursive:true});
const write=(name,v)=>fs.writeFileSync(path.join(__dirname,name),typeof v==='string'?v:JSON.stringify(v,null,2)+'\n',{flag:'wx'});
const color={paper:'#F5F4EE',ink:'#192F35',muted:'#4E656A',teal:'#0A8686',line:'#D3DDD6'};
const font='Inter,Noto Sans CJK SC',mono='DejaVu Sans Mono,Noto Sans CJK SC';
const statuses={
 '开放':{fill:'#DDF4E9',ink:'#11765C',symbol:'check',meaning:'开放'},
 '满额':{fill:'#E4E8F2',ink:'#35445B',symbol:'solid-square',meaning:'满额'},
 '候补':{fill:'#FFF0C8',ink:'#91621B',symbol:'clock',meaning:'候补'},
 '取消':{fill:'#F9E0D7',ink:'#A64529',symbol:'cross',meaning:'取消'}
};
const titleUnits=str=>[...str].reduce((n,ch)=>n+(ch.codePointAt(0)>0x2FF?1:0.55),0);
function titleSize(str){const u=titleUnits(str);return u<=6?72:u<=17?56:u<=26?48:44;}
const audits=[];
function text(c,fields,field,x,y,w,h,value,size,ink=color.ink,o={}){
 c.text(x,y,w,h,value,size,ink,{font,...o});
 fields.push({field,original_text:value,position:{x,y,width:w,height:h},font_family:o.font??font,font_size:size,font_style:o.bold?'BOLD':'NORMAL',color:ink,text_align:o.align??'START',raw_cdata:true,maximum_lines:o.maxLines??null});
}
function statusSymbol(c,kind,ink){
 const cx=990,cy=74;
 if(kind==='check'){c.line(cx-10,cy,cx-3,cy+7,ink,3,{roundCaps:true});c.line(cx-3,cy+7,cx+10,cy-9,ink,3,{roundCaps:true});}
 else if(kind==='solid-square')c.rect(cx-9,cy-9,18,18,ink,{radius:2});
 else if(kind==='clock'){c.circle(cx,cy,11,'transparent',{border:'2 SOLID '+ink});c.line(cx,cy,cx,cy-7,ink,2);c.line(cx,cy,cx+6,cy+3,ink,2);}
 else if(kind==='cross'){c.line(cx-8,cy-8,cx+8,cy+8,ink,3,{roundCaps:true});c.line(cx-8,cy+8,cx+8,cy-8,ink,3,{roundCaps:true});}
}
function make(card){
 const c=new Canvas(1200,630,{background:color.paper,font}),fields=[],status=statuses[card.status];
 if(!status)throw new Error('Unknown source status');
 text(c,fields,'brand',64,48,730,44,'Structure / Vision',28,color.ink,{bold:true});
 text(c,fields,'id',862,50,74,44,card.id,26,color.teal,{font:mono,bold:true});
 c.rect(968,48,184,52,status.fill,{radius:8});
 statusSymbol(c,status.symbol,status.ink);
 text(c,fields,'status',1018,59,118,38,card.status,24,status.ink,{bold:true});
 c.rect(64,128,1088,2,color.line);
 const size=titleSize(card.title);
 text(c,fields,'title',64,166,1072,252,card.title,size,color.ink,{bold:true,height:1.2,maxLines:3});
 text(c,fields,'speaker-label',64,452,96,38,'讲者',24,color.muted);
 text(c,fields,'speaker',174,446,962,72,card.speaker,28,color.ink,{height:1.2,maxLines:2});
 c.rect(64,520,1088,2,color.line);
 text(c,fields,'date',64,536,340,44,'2026.11.07',26,color.teal,{font:mono,bold:true});
 text(c,fields,'time-label',456,540,80,42,'时间',24,color.muted);
 text(c,fields,'time',550,532,226,52,card.time,36,color.ink,{font:mono,bold:true});
 if(card.status==='取消')text(c,fields,'cancellation-note',918,540,218,42,'本场取消',26,status.ink,{bold:true,align:'RIGHT'});
 const a={id:card.id,original:card,layout:'shared-1200x630-event-card',canvas:{width:1200,height:630},safe_margin_required:40,title_visual_units:titleUnits(card.title),title_font_size:size,title_line_count:null,speaker_line_count:null,title_region:{x:64,y:166,width:1072,height:252},status_region:{x:968,y:48,width:184,height:52},status_encoding:status,extra_cancellation_note:card.status==='取消'?'本场取消':null,fields,actual_visual_status:'awaiting_actual_render_and_view',image_views:[],source_strings_rewritten:false};
 audits.push(a);return c.toString();
}
(async()=>{
 const dsls=cards.map(card=>({card,dsl:make(card)}));
 write('generation-rules-v001.json',{task_id:'A14',run_id:'20261002-204314-6f31',input:source,color,font,mono,shared_title_region:{x:64,y:166,width:1072,height:252},title_rules:{visual_unit_weight:{cjk:1,ascii:.55},font_sizes:[{maximum_units:6,size:72},{maximum_units:17,size:56},{maximum_units:26,size:48},{otherwise:true,size:44}],minimum36:true,max_lines:3,exact_raw_source:true,natural_wrap:true,no_per_id_exceptions:true},speaker:{font_size:28,max_lines:2,exact_raw_source:true},state_system:statuses,full_canvas_scaling:false,no_images:true});
 write('batch-audit-draft-v001.json',{schema_version:1,task_id:'A14',run_id:'20261002-204314-6f31',status:'awaiting_actual_visual_review',source_file:source,generator_script:path.join(__dirname,'build-v001.cjs'),cards:audits});
 for(const {card,dsl} of dsls){
  write('card-'+card.id+'-v001.snapshot',dsl);
  const r=await s.render('A14',dsl,{version_id:'A14-v001-'+card.id,type:'baseline',stem:'card-'+card.id,width:1200,height:630,case_id:card.id,purpose:'A14 parameterized source-preserving event card '+card.id});
  console.log(JSON.stringify({id:card.id,ok:r.ok,meta_path:r.meta_path,image_path:r.image_path,error:r.error_summary}));
 }
})().catch(e=>{console.error(e);process.exitCode=1});
