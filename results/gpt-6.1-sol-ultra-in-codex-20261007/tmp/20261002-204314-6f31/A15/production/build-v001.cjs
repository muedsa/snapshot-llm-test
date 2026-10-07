'use strict';
const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'../../../..'),s=require(path.join(root,'tmp/20261002-204314-6f31/_suite/suite.cjs'));
const {Canvas}=require(path.join(root,'tmp/20261002-204314-6f31/_suite/dsl.cjs'));
const source=path.join(root,'tasks/A15-reference-reconstruction/inputs');
const input=JSON.parse(fs.readFileSync(path.join(source,'content.json'),'utf8'));
fs.mkdirSync(__dirname,{recursive:true});
const write=(f,v)=>fs.writeFileSync(path.join(__dirname,f),typeof v==='string'?v:JSON.stringify(v,null,2)+'\n',{flag:'wx'});
const color={background:'#F3F6FB',sidebar:'#14233C',white:'#FFFFFF',border:'#E2E8F1',selected:'#294467',blue:'#245CE4',grid:'#E7EDF5',separator:'#EBEFF5',workspace:'#233954',mint:'#64DBB6',ink:'#1B2D45',muted:'#697F9E',nav:'#BAC8DC',green:'#0B8F70'};
const c=new Canvas(1440,900,{background:color.background,font:'Inter,Noto Sans CJK SC'}),textmap=[];
function text(id,x,y,w,h,value,size=16,col=color.ink,o={}){
 c.text(x,y,w,h,value,size,col,o);textmap.push({id,source_text:value,position:{x,y,width:w,height:h},font_family:o.font??'Inter,Noto Sans CJK SC',font_size:size,color:col,font_style:o.bold?'BOLD':'NORMAL',raw_cdata:true});
}
function panel(x,y,w,h){c.rect(x,y,w,h,color.white,{radius:12,border:'1 SOLID '+color.border});}
c.rect(0,0,220,900,color.sidebar);
c.rect(30,33,28,28,color.mint,{radius:6});c.rect(38,41,12,12,color.sidebar,{radius:2});
text('brand',72,32,136,32,input.brand,20,color.white,{bold:true});
c.rect(18,116,184,48,color.selected,{radius:8});
input.navigation.forEach((v,i)=>{const cy=134+i*64;c.circle(40,cy,6,i===0?color.mint:'#829CBD');text('navigation['+i+']',61,122+i*64,143,32,v,19,i===0?color.white:color.nav,{bold:i===0});});
c.rect(22,752,176,116,color.workspace,{radius:12});
text('workspace_info[0]',38,766,148,28,input.workspace_info[0],13,color.mint,{bold:true});
text('workspace_info[1]',38,800,148,28,input.workspace_info[1],16,color.white);
text('workspace_info[2]',38,831,148,28,input.workspace_info[2],14,color.nav);
text('title',260,30,810,56,input.title,34,color.ink,{bold:true});
text('subtitle',260,81,810,36,input.subtitle,18,color.muted);
c.rect(1184,43,216,48,color.blue,{radius:10});text('button',1196,51,192,34,input.button,18,color.white,{bold:true,align:'CENTER'});
input.kpis.forEach((k,i)=>{
 const x=260+i*384;panel(x,138,356,144);
 text('kpis['+i+'].label',x+24,157,306,26,k.label,14,color.muted,{bold:true});
 text('kpis['+i+'].value',x+24,192,306,52,k.value,34,color.ink,{bold:true});
 text('kpis['+i+'].change',x+24,242,306,30,k.change,16,color.green,{bold:true});
});
panel(260,310,742,286);panel(1030,310,370,286);
text('chart_title',284,330,420,40,input.chart_title,24,color.ink,{bold:true});
text('chart_period',868,332,106,34,input.chart_period,17,color.muted,{align:'RIGHT'});
text('chart_unit',286,372,190,26,input.chart_unit,13,color.muted);
const chart={plot:{left:333,right:970,top:405,zero:549},domain:{minimum:0,maximum:120},pixels_per_thousand:1.2,bars:[]};
input.chart_ticks.forEach((tick,i)=>{
 const y=549-tick*1.2;c.rect(333,y,637,1,color.grid);
 text('chart_ticks['+i+']',284,y-10,37,24,String(tick),14,color.muted,{align:'RIGHT'});
});
input.chart_values.forEach((v,i)=>{
 const x=357+i*101,h=v*1.2,y=549-h;
 c.rect(x,y,54,h,color.blue,{radius:6});
 text('months['+i+']',x-9,557,72,28,input.months[i],14,color.muted,{align:'CENTER'});
 chart.bars.push({month:input.months[i],value:v,x,y,width:54,height:h,bottom:549});
});
text('activity_title',1054,330,320,42,input.activity_title,24,color.ink,{bold:true});
input.activity.forEach((row,i)=>{
 const y=390+i*60;c.circle(1059,y+12,5,['#F2B238',color.blue,'#148B6D'][i]);
 text('activity['+i+'][0]',1076,y,298,34,row[0],18,color.ink,{bold:true});
 text('activity['+i+'][1]',1076,y+29,298,28,row[1],14,color.muted);
});
panel(260,624,1140,218);
text('table_title',284,640,800,42,input.table_title,24,color.ink,{bold:true});
c.rect(284,688,1090,34,color.background,{radius:4});
const columns=[298,782,1033,1230],widths=[466,230,180,138];
input.table_columns.forEach((v,i)=>text('table_columns['+i+']',columns[i],695,widths[i],24,v,12,color.muted,{bold:true}));
const states={'In progress':{fill:'#E7EFFF',ink:'#245CFF'},'Review':{fill:'#FFF3D7',ink:'#A9690C'},'Done':{fill:'#DCF5EC',ink:'#079675'}};
input.rows.forEach((row,i)=>{
 const y=730+i*35;
 text('rows['+i+'][0]',298,y,466,28,row[0],16,color.ink,{bold:true});
 text('rows['+i+'][1]',782,y,230,28,row[1],16,color.muted);
 const status=states[row[2]];c.rect(1028,729+i*35,148,28,status.fill,{radius:8});
 text('rows['+i+'][2]',1036,733+i*35,132,24,row[2],13,status.ink,{bold:true,align:'CENTER'});
 text('rows['+i+'][3]',1230,y,138,28,row[3],16,color.muted);
 if(i<2)c.rect(284,760+i*35,1090,1,color.separator);
});
text('footer',260,864,1110,28,input.footer,13,color.muted);
const reconstructed={
'sidebar-right':[220,0],'nav-selected-top-left':[18,116],'export-top-left':[1184,43],'first-kpi-top-left':[260,138],'first-kpi-bottom-right':[616,282],'second-kpi-top-left':[644,138],'third-kpi-top-left':[1028,138],'chart-top-left':[260,310],'chart-bottom-right':[1002,596],'activity-top-left':[1030,310],'plot120-grid-left':[333,405],'plot-zero-grid-left':[333,549],'table-top-left':[260,624],'table-bottom-right':[1400,842],'table-header-top-left':[284,688],'status-progress-top-left':[1028,729],'workspace-card-top-left':[22,752],'workspace-card-bottom-right':[198,868]
};
const referenceMeasurePath=path.join(root,'tmp/20261002-204314-6f31/A15/independent-analysis/reference-measurements-v001.json');
const ref=JSON.parse(fs.readFileSync(referenceMeasurePath,'utf8'));
const anchors=ref.anchor_estimates.map(a=>({...a,reconstructed:reconstructed[a.id],estimated_difference_xy:[reconstructed[a.id][0]-a.reference[0],reconstructed[a.id][1]-a.reference[1]],reference_provenance:referenceMeasurePath,verification_state:'Model coordinates match reference estimates; actual rendered pixels still require independent review.'}));
const dsl=c.toString();write('reconstructed-v001.snapshot',dsl);
write('reconstruction-audit-draft-v001.json',{schema_version:1,task_id:'A15',run_id:'20261002-204314-6f31',status:'awaiting_actual_render_review',reference_png:path.join(source,'reference.png'),reference_measurement_provenance:referenceMeasurePath,anchor_count:anchors.length,anchors,chart,original_content:input,text_map:textmap,palette:color,table_status_encoding:states,no_reference_asset_embedded:true,no_image_tag:true,source_crop_previews_used_only_for_visual_inspection:true,fonts_cache:'tmp/20261002-204314-6f31/_suite/shared-fonts-000001-response.txt',residual_expected:'Font metrics are approximated with available Inter family; no exact pixel equivalence claimed.'});
(async()=>{
 const r=await s.render('A15',dsl,{version_id:'A15-v001',type:'baseline',stem:'reconstructed',width:1440,height:900,purpose:'A15 reconstruct actual source UI from measured/observed geometry, no embedded source image'});
 console.log(JSON.stringify({ok:r.ok,meta_path:r.meta_path,image_path:r.image_path,error:r.error_summary}));
})().catch(e=>{console.error(e);process.exitCode=1});
