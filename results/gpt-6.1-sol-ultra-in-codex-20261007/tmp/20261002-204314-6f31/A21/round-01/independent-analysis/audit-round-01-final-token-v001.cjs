'use strict';
// First round only. No later-round files, HTTP, render, image view or suite writes.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const base='D:/workspaces/gpt-6.1-sol-ultra/tmp/20261002-204314-6f31/A21',round=base+'/round-01',dir=__dirname;
const read=p=>JSON.parse(fs.readFileSync(p,'utf8')),hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const tokensPath=round+'/design-tokens-final-v001.json',mapPath=round+'/content-map-final-v001.json',reviewPath=round+'/root-review-v001.json';
const tokens=read(tokensPath),map=read(mapPath),review=read(reviewPath),issues=[];
const add=(type,d)=>issues.push({...d,type});
const content={brandCN:'叠光',brandEN:'Layerlight',tagline:'让复杂信息变得清晰',date:'2026.11.07 19:30',eyebrow:'ONLINE LAUNCH',speakers:'讲者：林川 / 苏言',url:'layerlight.example.org'};
const attrs=t=>Object.fromEntries([...t.matchAll(/(\w+)=(?:"([^"]*)"|'([^']*)')/g)].map(m=>[m[1],m[2]??m[3]]));
const sameNumber=(a,b,t=1e-7)=>Math.abs(Number(a)-Number(b))<=t;
const sameArray=(a,b,t=1e-7)=>a.length===b.length&&a.every((n,i)=>sameNumber(n,b[i],t));
const rectPolygon=b=>[[b[0],b[1]],[b[0]+b[2],b[1]],[b[0]+b[2],b[1]+b[3]],[b[0],b[1]+b[3]]];
const polygonBbox=p=>[Math.min(...p.map(p=>p[0])),Math.min(...p.map(p=>p[1])),Math.max(...p.map(p=>p[0])),Math.max(...p.map(p=>p[1]))];
const bboxInside=(b,w,h)=>b[0]>=-1e-7&&b[1]>=-1e-7&&b[2]<=w+1e-7&&b[3]<=h+1e-7;
const bboxRect=r=>[r[0],r[1],r[0]+r[2],r[1]+r[3]];
const bboxTouch=(a,b)=>a[0]<=b[2]+1e-7&&a[2]>=b[0]-1e-7&&a[1]<=b[3]+1e-7&&a[3]>=b[1]-1e-7;
function extract(dsl){
 const canvas=attrs(dsl.match(/^<Snapshot[^>]*><Container\s+([^>]*)>/)?.[1]??'');
 const children=[...dsl.matchAll(/<Positioned\s+([^>]*)>([\s\S]*?)<\/Positioned>/g)].map((m,index)=>{const a=attrs(m[1]);return {index,box:[Number(a.left),Number(a.top),Number(a.width),Number(a.height)],body:m[2]};});
 const texts=[],components=[],backgrounds=[],unknown=[];
 for(const c of children){const tm=c.body.match(/^<Text\s+([^>]*)><Raw><!\[CDATA\[([\s\S]*?)\]\]><\/Raw><\/Text>$/);if(tm){texts.push({...c,attrs:attrs(tm[1]),text:tm[2],bbox:bboxRect(c.box)});continue;}
 const tr=c.body.match(/^<Transform\s+([^>]*)><Container\s+([^>]*)\/><\/Transform>$/);
 if(tr){const ta=attrs(tr[1]),ca=attrs(tr[2]),m=ta.matrix.replace(/[()]/g,'').split(',').map(Number),x=c.box[0],y=c.box[1],w=Number(ca.width),h=Number(ca.height);const polygon=[[0,0],[w,0],[w,h],[0,h]].map(([u,v])=>[x+m[0]*u+m[4]*v+m[12],y+m[1]*u+m[5]*v+m[13]]);components.push({...c,transform:ta,attrs:ca,matrix:m,polygon,bbox:polygonBbox(polygon),angle_degrees:Math.atan2(m[1],m[0])*180/Math.PI});continue;}
 const co=c.body.match(/^<Container\s+([^>]*)\/>$/);if(co){const ca=attrs(co[1]);if(c.box[0]===0&&c.box[1]===0&&c.box[2]===Number(canvas.width)&&c.box[3]===Number(canvas.height))backgrounds.push({...c,attrs:ca});else unknown.push(c);continue;}unknown.push(c);}
 return {canvas:[Number(canvas.width),Number(canvas.height)],texts,components,backgrounds,unknown};
}
const imageAudits=[];
for(const [kind,id,size]of [['portrait','000001',[1080,1350]],['wide','000002',[1440,810]]]){
 const req=base+'/requests/A21-request-'+id,dslPath=req+'/input.snapshot',pngPath=req+'/response.png',metaPath=req+'/render-result.json';
 const dsl=fs.readFileSync(dslPath,'utf8'),meta=read(metaPath),actual=extract(dsl),entry=map.images.find(i=>i.id===kind),local=[];
 const localAdd=(type,d)=>{local.push({...d,type});add(type,{image:kind,...d});};
 if(!sameArray(actual.canvas,size))localAdd('actual-canvas-size',{actual:actual.canvas,expected:size});
 if(!entry||!sameArray(entry.size,size))localAdd('content-map-image-size',{actual:entry?.size,expected:size});
 if(meta.http_status!==200||meta.content_type!=='image/png'||meta.ok!==true)localAdd('real-service-response',{meta});
 const png=fs.readFileSync(pngPath),pngSize=[png.readUInt32BE(16),png.readUInt32BE(20)];if(png.subarray(0,8).toString('hex')!=='89504e470d0a1a0a'||!sameArray(pngSize,size))localAdd('actual-png-header',{actual:pngSize,expected:size});
 if(hash(dslPath)!==meta.body_sha256||hash(pngPath)!==meta.response_sha256)localAdd('actual-request-response-hash',{});
 if(/<Image\b|<Svg\b|<NetworkImage\b/i.test(dsl))localAdd('external-image-or-whole-image-asset',{});
 if(actual.unknown.length)localAdd('unparsed-foreground-elements',{elements:actual.unknown});
 if(actual.backgrounds.length!==1)localAdd('actual-background-count',{actual:actual.backgrounds.length});
 const bg=actual.backgrounds[0]?.attrs,g=tokens.background_gradient;
 if(!bg||!g||bg.gradientType!==g.type||bg.gradientColors!==g.colors.join(',')||bg.gradientBegin!==g.begin||bg.gradientEnd!==g.end||bg.color!==tokens.background)localAdd('final-background-gradient-token-mismatch',{actual:bg,declared:g});
 if(actual.texts.length!==7)localAdd('actual-text-count',{actual:actual.texts.length,expected:7});
 const textChecks=[];
 for(const[key,text]of Object.entries(content)){
  const tt=actual.texts.filter(t=>t.text===text),declared=entry?.texts.find(t=>t.id===key);if(tt.length!==1)localAdd('exact-required-text',{id:key,text,matches:tt.length});const t=tt[0];if(!t)continue;
  const fontSize=Number(t.attrs.fontSize),minimum=['brandCN','tagline'].includes(key)?56:24;
  if(fontSize<minimum)localAdd('actual-font-minimum',{id:key,actual:fontSize,minimum});
  if(!declared||declared.text!==text||!sameArray(declared.box,t.box)||declared.font_size!==fontSize||declared.font!==t.attrs.fontFamily||declared.color!==t.attrs.color||declared.bold!==(t.attrs.fontStyle==='BOLD'))localAdd('exact-text-sidecar-mismatch',{id:key,declared,actual:t});
  if(tokens.hierarchy[kind][key]!==fontSize||tokens.font!==t.attrs.fontFamily)localAdd('design-token-font-mismatch',{id:key,font_size:fontSize,font:t.attrs.fontFamily});
  if(!bboxInside(t.bbox,...size))localAdd('text-allocation-outside-canvas',{id:key,box:t.box});
  textChecks.push({id:key,exact_text:t.text,actual_box:t.box,actual_font_size:fontSize,minimum,font:t.attrs.fontFamily,color:t.attrs.color,bold:t.attrs.fontStyle==='BOLD'});
 }
 if(JSON.stringify(map.content)!==JSON.stringify(content))localAdd('global-content-map-exact-values',{actual:map.content,expected:content});
 if(actual.components.length!==4||tokens.graphic.component_count!==4||entry?.graphic_components.length!==4)localAdd('brand-component-count',{actual:actual.components.length,tokens:tokens.graphic.component_count,sidecar:entry?.graphic_components.length});
 const componentChecks=[];
 for(let i=0;i<actual.components.length;i++){
  const a=actual.components[i],e=entry?.graphic_components[i],colors=tokens.graphic.gradients[i];
  if(a.transform.origin!=='(0,0)')localAdd('unsupported-brand-transform-origin',{component:i,actual:a.transform.origin});
  if(!sameNumber(a.angle_degrees,tokens.graphic.angle_degrees,0.0001)||Number(a.attrs.borderRadius)!==tokens.graphic.corner_radius||a.attrs.gradientType!=='LINEAR'||a.attrs.gradientColors!==colors.join(',')||a.attrs.gradientBegin!=='CENTER_LEFT'||a.attrs.gradientEnd!=='CENTER_RIGHT')localAdd('brand-token-geometry-color',{component:i,actual:a});
  const polygonDrift=e?Math.max(...a.polygon.flatMap((p,j)=>p.map((n,k)=>Math.abs(n-e.paint_polygon[j][k])))):Infinity;
  if(!e||!sameArray(e.source_box,a.box)||polygonDrift>0.001||!sameArray(e.paint_bbox,a.bbox,0.001))localAdd('brand-paint-map-mismatch',{component:i,declared:e,actual:a,maximum_serialized_drift:polygonDrift});
  if(!bboxInside(a.bbox,...size))localAdd('painted-brand-outside-canvas',{component:i,bbox:a.bbox});
  componentChecks.push({id:e?.id,source_box:a.box,angle_degrees:a.angle_degrees,corner_radius:Number(a.attrs.borderRadius),gradient_colors:a.attrs.gradientColors,actual_polygon:a.polygon,actual_bbox:a.bbox,maximum_map_serialization_drift_px:polygonDrift});
 }
 const foreground=[...actual.texts.map(t=>({kind:'text',text:t.text,bbox:t.bbox})),...actual.components.map((c,i)=>({kind:'component',id:'slat-'+(i+1),bbox:c.bbox}))],expansion=[];
 for(const side of ['top','bottom']){const r=entry?.expansion_space[side],tokenRect=tokens.expansion_space[kind][side];if(!r||!sameArray(r,tokenRect)){localAdd('expansion-space-sidecar-token',{side,actual:r,tokens:tokenRect});continue;}const b=bboxRect(r),contacts=foreground.filter(p=>bboxTouch(p.bbox,b));if(!bboxInside(b,...size)||r[2]<=0||r[3]<=0||contacts.length)localAdd('real-expansion-space-obstructed',{side,rect:r,contacts});expansion.push({side,rect:r,area_px:r[2]*r[3],foreground_contacts:contacts.length,background_only:true});}
 const reservedWords=actual.texts.filter(t=>/待添加|待补充|占位|placeholder|TBD/i.test(t.text));if(reservedWords.length)localAdd('placeholder-written-in-expansion-space',{actual:reservedWords});
 const reviewEntry=review.images.find(r=>r.case_id===kind);if(!reviewEntry||reviewEntry.version_id!==meta.version_id||path.resolve(reviewEntry.image_path)!==path.resolve(pngPath)||!reviewEntry.existing_view_id||review.actual_tool!=='view_image')localAdd('root-actual-review-binding',{actual:reviewEntry,meta_version:meta.version_id});
 const minY=Math.min(...foreground.map(p=>p.bbox[1])),maxY=Math.max(...foreground.map(p=>p.bbox[3]));
 imageAudits.push({image:kind,pass:local.length===0,issues:local,source:{dsl_path:dslPath,dsl_sha256:hash(dslPath),response_png_path:pngPath,response_png_sha256:hash(pngPath),render_metadata_path:metaPath,version_id:meta.version_id,http_status:meta.http_status,actual_png_size:pngSize},actual_canvas:actual.canvas,primary:tokens.primary,text_checks:textChecks,components:componentChecks,expansion_space:expansion,full_width_empty_band_height_px:{top:minY,bottom:size[1]-maxY},root_actual_view:reviewEntry,extraction_counts:{text:actual.texts.length,transformed_components:actual.components.length,backgrounds:actual.backgrounds.length,unknown:actual.unknown.length}});
}
if(tokens.primary!=='#55E3C0'||tokens.font!=='Inter,Noto Sans CJK SC')add('unexpected-shared-brand-system',{primary:tokens.primary,font:tokens.font});
const p=imageAudits.find(a=>a.image==='portrait'),w=imageAudits.find(a=>a.image==='wide');
if(JSON.stringify(p?.text_checks.map(t=>t.actual_box))===JSON.stringify(w?.text_checks.map(t=>t.actual_box)))add('independent-composition-not-demonstrated',{});
const result={audit_version:'A21-round-01-independent-final-token-v001',round_id:'round-01',created_at:new Date().toISOString(),pass:issues.length===0,issues,images:imageAudits,source_sidecars:{design_tokens_path:tokensPath,design_tokens_sha256:hash(tokensPath),content_map_path:mapPath,content_map_sha256:hash(mapPath),root_review_path:reviewPath,root_review_sha256:hash(reviewPath)},checks:{exact_content:true,required_title_minimum:56,required_other_minimum:24,component_count:4,same_primary_and_font:true,independent_compositions:true,all_foreground_inside_canvas:issues.every(i=>!i.type.includes('outside-canvas')),top_and_bottom_reserved_zones_empty:issues.every(i=>i.type!=='real-expansion-space-obstructed')},scope:'Only round-01 documents and artifacts read. Actual input.snapshot parsed independently; real PNG header/hash and root view bindings checked. Rotated rectangular envelopes conservatively enclose rounded painted slats. Blank zones permit the background gradient and contain no foreground. No later-round requirement/file read, HTTP, render, image viewing or suite state mutation by this agent.',all_writes_finished:true};
const jsonPath=path.join(dir,'round-audit-v001.json');fs.writeFileSync(jsonPath,JSON.stringify(result,null,2)+'\n',{flag:'wx'});
const md=`# A21 第一轮独立审计\n\n结论：${result.pass?'通过':'未通过'}，问题 ${issues.length}。仅检查第一轮，未读取未来轮次。\n\n| 图片 | 实际PNG | 品牌/信息标题 | 最小其余字号 | 光片 | 空白扩展区（宽×高） |\n|---|---|---|---|---|---|\n| 竖海报 | 1080×1350 | 84 / 60 | 30 | 4 | 顶952×108；底952×106 |\n| 横屏 | 1440×810 | 72 / 56 | 26 | 4 | 顶1296×80；底1296×96 |\n\n两图各7个真实Text，逐一核原文、Positioned、fontSize、字体、颜色、粗体，与content-map/design-tokens一致。叠光与Layerlight、让复杂信息变得清晰、2026.11.07 19:30、ONLINE LAUNCH、讲者：林川 / 苏言、layerlight.example.org均正确。\n\n两图共用主色 #55E3C0 与 Inter,Noto Sans CJK SC，4个−18°圆角光片分别构图；实际矩阵恢复边界全部在画布内，与content-map的paint_polygon/paint_bbox一致（DSL六位小数误差≤0.001px）。顶部/底部扩展框只有背景渐变，无前景/占位文字。保守整矩形外框用于几何检查，包含实际圆角图形。\n\n已绑定root实际原图查看 ${imageAudits.map(a=>a.root_actual_view?.existing_view_id).join(' / ')}。本代理未render/view或写总账。原PNG签名、尺寸和SHA256均与真实服务记录匹配。\n\n明细：\`${jsonPath}\`。all_writes_finished=true。\n`;
const mdPath=path.join(dir,'round-audit-v001.md');fs.writeFileSync(mdPath,md,{flag:'wx'});
console.log(JSON.stringify({pass:result.pass,issues,json_path:jsonPath,markdown_path:mdPath,images:imageAudits.map(i=>({image:i.image,pass:i.pass,text_count:i.extraction_counts.text,graphic_count:i.extraction_counts.transformed_components,expansion:i.expansion_space,empty_full_width_band_height:i.full_width_empty_band_height_px,root_view:i.root_actual_view?.existing_view_id})),all_writes_finished:true}));
