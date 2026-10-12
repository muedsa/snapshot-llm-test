const fs=require('node:fs'),p=require('node:path'),s=require('../../_suite/suite.cjs');
const {Canvas,tag,matrix2d}=require('../../_suite/dsl.cjs');
const round='round-01',dir=__dirname;
const content={brandCN:'叠光',brandEN:'Layerlight',tagline:'让复杂信息变得清晰',date:'2026.11.07 19:30',eyebrow:'ONLINE LAUNCH',speakers:'讲者：林川 / 苏言',url:'layerlight.example.org'};
const tokens={schema_version:1,task_id:'A21',round_id:round,brand:'叠光 Layerlight',primary:'#55E3C0',background:'#0B1E26',ink:'#EDF9F5',secondary:'#A9C3BE',font:'Inter,Noto Sans CJK SC',graphic:{id:'four-light-slats',component_count:4,angle_degrees:-18,corner_radius:14,colors:['#1C585B','#2C8B81','#55E3C0','#C5FFF0']},hierarchy:{portrait:{brandCN:84,brandEN:42,tagline:60,date:46,eyebrow:30,speakers:36,url:30},wide:{brandCN:72,brandEN:36,tagline:56,date:38,eyebrow:26,speakers:32,url:30}},composition:{portrait:'Vertical brand → four-slats emblem → message → event information',wide:'Information at left, independently recomposed emblem at right'},expansion_space:{portrait:{top:[64,36,952,108],bottom:[64,1180,952,106]},wide:{top:[72,24,1296,80],bottom:[72,650,1296,96]}},asset_policy:'dsl_only_no_external_images',mode:'preloaded_sequential; future requirements accessible but not read before this round is archived'};
const map={schema_version:1,task_id:'A21',round_id:round,content,images:[]};
function build(kind){
 const portrait=kind==='portrait',w=portrait?1080:1440,h=portrait?1350:810,c=new Canvas(w,h,{background:tokens.background,clipBehavior:'NONE'}),texts=[];
 c.rect(0,0,w,h,tokens.background,{gradientType:'LINEAR',gradientColors:'#123036,#071B22',gradientBegin:'TOP_LEFT',gradientEnd:'BOTTOM_RIGHT'});
 function t(id,x,y,width,height,color=tokens.ink,bold=false){const size=tokens.hierarchy[kind][id];c.text(x,y,width,height,content[id],size,color,{bold});texts.push({id,text:content[id],box:[x,y,width,height],font_size:size,font:tokens.font,color,bold});}
 if(portrait){
  t('brandCN',64,176,240,115,tokens.ink,true);t('brandEN',286,212,620,65,tokens.primary,true);
  t('eyebrow',66,292,900,46,tokens.secondary);
 }else{
  t('brandCN',72,132,200,100,tokens.ink,true);t('brandEN',268,163,390,55,tokens.primary,true);
  t('eyebrow',74,236,660,41,tokens.secondary);
 }
 const gx=portrait?260:850,gy=portrait?530:326,L=portrait?590:440,H=portrait?58:48,gap=portrait?72:56,angle=-18*Math.PI/180,cos=Math.cos(angle),sin=Math.sin(angle),components=[];
 for(let i=0;i<4;i++){
  const x=gx,y=gy+i*gap,col=tokens.graphic.colors[i];
  c.at(x,y,L,H,tag('Transform',{matrix:matrix2d(cos,sin,-sin,cos),origin:'(0,0)'},tag('Container',{width:L,height:H,borderRadius:14,gradientType:'LINEAR',gradientColors:col+','+tokens.graphic.colors[Math.min(3,i+1)],gradientBegin:'CENTER_LEFT',gradientEnd:'CENTER_RIGHT'})));
  const pts=[[0,0],[L,0],[L,H],[0,H]].map(([u,v])=>[x+u*cos-v*sin,y+u*sin+v*cos]);components.push({id:'slat-'+(i+1),source_box:[x,y,L,H],angle_degrees:-18,color:col,paint_polygon:pts,paint_bbox:[Math.min(...pts.map(t=>t[0])),Math.min(...pts.map(t=>t[1])),Math.max(...pts.map(t=>t[0])),Math.max(...pts.map(t=>t[1]))]});
 }
 if(portrait){
  t('tagline',64,848,952,94,tokens.ink,true);t('date',66,970,940,67,tokens.primary,true);
  t('speakers',66,1052,940,58,tokens.ink);t('url',66,1126,940,46,tokens.secondary);
 }else{
  t('tagline',72,308,700,92,tokens.ink,true);t('date',74,424,700,58,tokens.primary,true);
  t('speakers',74,496,700,50,tokens.ink);t('url',74,568,700,47,tokens.secondary);
 }
 map.images.push({id:kind,filename:'launch-'+kind+'.png',size:[w,h],texts,graphic_components:components,expansion_space:tokens.expansion_space[kind]});return c.toString();
}
const [kind]=process.argv.slice(2);
if(!['portrait','wide'].includes(kind))throw Error('portrait or wide required');
const dsl=build(kind);
fs.writeFileSync(p.join(dir,'content-map-'+kind+'-v001.json'),JSON.stringify(map,null,2)+'\n',{flag:'wx'});
if(!fs.existsSync(p.join(dir,'design-tokens-v001.json')))fs.writeFileSync(p.join(dir,'design-tokens-v001.json'),JSON.stringify(tokens,null,2)+'\n',{flag:'wx'});
(async()=>{const r=await s.render('A21',dsl,{version_id:'A21-round-01-'+kind+'-v001',type:'baseline',round_id:round,case_id:kind,width:kind==='portrait'?1080:1440,height:kind==='portrait'?1350:810,stem:round+'/launch-'+kind,purpose:'First-round independent '+kind+' launch composition with four-brand-slats and real blank expansion space'});console.log(JSON.stringify({id:r.id,ok:r.ok,error:r.error_summary,meta_path:r.meta_path,image_path:r.image_path,version_id:r.version_id}));})();
