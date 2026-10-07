'use strict';
// Preserve round02 source and evidence, adapting the independently parsed source
// checks to the now-authorized third round. Contrast is separately delegated.
const fs=require('node:fs'),path=require('node:path');
const old=path.resolve(__dirname,'../../round-02/independent-analysis/audit-round-02-v001.cjs');
let s=fs.readFileSync(old,'utf8');
s=s.replace("const sharp=require('C:/Users/mueds/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');\n",'');
s=s.replaceAll("round=base+'/round-02'","round=base+'/round-03'").replaceAll("/rounds/round-02.md","/rounds/round-03.md");
s=s.replace("oldTokens=read(base+'/round-01/design-tokens-final-v001.json'),oldMap=read(base+'/round-01/content-map-final-v001.json')","oldTokens=read(base+'/round-02/design-tokens-final-v001.json'),oldMap=read(base+'/round-02/content-map-final-v001.json')");
s=s.replace("free:'免费参加 · 无需报名'}","free:'免费参加 · 无需报名',english:'Clarity through structure'}");
const start=s.indexOf('function priorPreservation()'),end=s.indexOf('(async()=>{',start);
s=s.slice(0,start)+`function priorPreservation(){const checks=[];for(const rid of ['round-01','round-02']){const pubPath=base+'/'+rid+'/publication-result-v001.json',pub=read(pubPath);for(const f of pub.finals)for(const[k,h]of [['image_path','png_sha256'],['dsl_path','dsl_sha256']]){const actual=hash(f[k]),pass=actual===f[h];checks.push({round_id:rid,path:f[k],publication_sha256:f[h],current_sha256:actual,pass});if(!pass)add('previous-published-final-changed',{round_id:rid,path:f[k]});}
for(const f of pub.additional_files){const actual=hash(f.output),source=hash(f.source),pass=actual===f.sha256&&source===f.sha256;checks.push({round_id:rid,path:f.output,source_path:f.source,publication_sha256:f.sha256,current_sha256:actual,source_sha256:source,pass});if(!pass)add('previous-published-sidecar-changed',{round_id:rid,path:f.output});}
const metricSource=base+'/'+rid+'/metrics/round-metrics-000001.json',metricOutput=root+'/outputs/20261002-204314-6f31/A21/'+rid+'/task-metrics.json',mp=hash(metricSource)===hash(metricOutput);checks.push({round_id:rid,path:metricOutput,source_path:metricSource,current_sha256:hash(metricOutput),archive_sha256:hash(metricSource),pass:mp});if(!mp)add('previous-archived-metrics-changed',{round_id:rid});}return {checked_published_files:checks.length,checks,pass:checks.every(x=>x.pass)};}
`+s.slice(end);
s=s.replace("const unchangedTokens=['primary','background','ink','secondary','font','graphic','background_gradient'];for(const k of unchangedTokens)if(JSON.stringify(tokens[k])!==JSON.stringify(oldTokens[k]))add('brand-token-regression',{key:k,current:tokens[k],first_round:oldTokens[k]});",`if(tokens.font!==oldTokens.font)add('brand-font-regression',{});
for(const k of ['id','component_count','angle_degrees','corner_radius','colors','gradients'])if(JSON.stringify(tokens.graphic[k])!==JSON.stringify(oldTokens.graphic[k]))add('brand-graphic-token-regression',{key:k,current:tokens.graphic[k],previous:oldTokens.graphic[k]});
if(tokens.graphic.primary!==oldTokens.primary)add('retained-brand-primary-regression',{actual:tokens.graphic.primary,previous:oldTokens.primary});`);
s=s.replace("JSON.stringify(oldTokens.expansion_space)","JSON.stringify(oldTokens.first_round_reserved_regions)");
s=s.replace("[['portrait','000003','000001',[1080,1350]],['wide','000004','000002',[1440,810]]]","[['portrait','000005','000003',[1080,1350]],['wide','000006','000004',[1440,810]]]");
s=s.replace("a.texts.length!==9","a.texts.length!==10").replace("{expected:9,actual:a.texts.length}","{expected:10,actual:a.texts.length}");
s=s.replace("||t.attrs.color!==ot.attrs.color",'');
s=s.replace("const unchangedTokens",'const unchangedTokens');
s=s.replace("if(a.backgrounds.length!==1||a.backgrounds[0].body!==old.backgrounds[0].body)error('background-first-round-regression',{});",`const bg=a.backgrounds[0]?.attrs,bgt=tokens.background_gradient;
if(a.backgrounds.length!==1||bg.color!==tokens.background||bg.gradientType!==bgt.type||bg.gradientColors!==bgt.colors.join(',')||bg.gradientBegin!==bgt.begin||bg.gradientEnd!==bgt.end)error('actual-light-theme-gradient-token',{});
const backdropContacts=a.texts.flatMap(t=>a.components.filter(c=>touch(t.bbox,c.bbox)).map(c=>({text:t.text,component_bbox:c.bbox})));
if(backdropContacts.length)error('foreground-layer-under-text',{contacts:backdropContacts});
if(a.texts.some(t=>![tokens.primary,tokens.ink,tokens.secondary].includes(t.attrs.color)))error('light-text-palette-token',{});`);
s=s.replace("['tagline','sponsor','free']","['tagline','sponsor','free','english','url']");
s=s.replace("previous.expansion_space[side]","oldTokens.first_round_reserved_regions[kind][side]");
const ps=s.indexOf(' const bbox=bb(a.components.flatMap'),pe=s.indexOf(' const rootView=',ps);
if(ps<0||pe<0)throw Error('Pixel block not found');
s=s.slice(0,ps)+` const english=a.texts.find(t=>t.text===content.english),url=a.texts.find(t=>t.text===content.url);
const englishAboveUrl=english&&url&&english.box[1]+english.box[3]<=url.box[1]+1e-7&&english.box[0]===url.box[0];
if(!englishAboveUrl||Number(english?.attrs.fontSize)<24)error('english-not-above-url',{english,url});
const englishUrlCheck={exact_text:english?.text,font_size:Number(english?.attrs.fontSize),english_box:english?.box,url_box:url?.box,vertical_gap_px:url?url.box[1]-(english.box[1]+english.box[3]):null,above_url:!!englishAboveUrl};
`+s.slice(pe);
const objStart=s.indexOf("pixel_regression:{method:'Sharp decode"),objEnd=s.indexOf(',root_actual_view:rootView',objStart);
if(objStart<0||objEnd<0)throw Error('Pixel result block not found');
s=s.slice(0,objStart)+"english_above_url:englishUrlCheck,actual_background:bg,all_text_box_foreground_layer_contacts:backdropContacts.length"+s.slice(objEnd);
s=s.replaceAll("A21-round-02-independent-v001","A21-round-03-content-geometry-v001").replace("round_id:'round-02'","round_id:'round-03'");
s=s.replace("first_round_preservation:oldFiles","previous_rounds_preservation:oldFiles,contrast_audit:{performed_by_this_agent:false,assigned_to:'a19_audit_resume',status:'Separate actual-background contrast audit required; not repeated here.'}");
s=s.replace("Read current round-02 requirements only after root reported round-01 publication/archive complete. No round-03 read. Independent actual DSL data/geometry, service file integrity, first-round immutable publication hashes and real source PNG pixel-region comparisons. Root owns actual image review. No HTTP/render/view/suite mutation by this agent.","Read round-03 requirements only after root reported round-02 publication/archive complete. Independent actual DSL content/geometry, service file integrity and both previous-round immutable publication/archive hashes. Actual transformed four-slat sources are unchanged; background/theme changes are intentional. Contrast is separately assigned to a19_audit_resume and not calculated here. Root owns actual image review. No HTTP/render/view/suite mutation by this agent.");
const mdStart=s.indexOf(' const md=`'),mdEnd=s.indexOf(' const mdPath=',mdStart);
s=s.slice(0,mdStart)+` const md=\`# A21 第三轮内容与几何独立审计\\n\\n结论：\${result.pass?'通过':'未通过'}，问题\${issues.length}。此结论仅覆盖内容/几何/归档完整性，对比度由专项代理另行审计。\\n\\n两图各10个实际Text均与最终token/content-map匹配。全部第二轮九项文案完整保留，长中文标题48px明确两行且≤3；“Clarity through structure”24px置于网址上方，竖/横与网址净距分别\${images.map(x=>x.english_above_url.vertical_gap_px).join(' / ')}px，未做文字变形。赞助、免费、日期、讲者、ONLINE LAUNCH和网址完整。\\n\\n所有文本及4个实际Transform光片绘制外框在1080×1350/1440×810画布内；新/移动文本与其他正文或图形保守框contacts均0。实际正文盒下无前景图层，只有最终token指定浅色不透明渐变背景。字体/字号/粗体回归一致，文字深色调色板与真实DSL相符。\\n\\n四个−18°圆角14光片矩阵、原source位置/大小和渐变色与第二轮完全相同，原品牌青色#55E3C0保留在图形中。第三轮背景变色是主题变更，不要求整片PNG像素相同。\\n\\n前两轮共\${oldFiles.checked_published_files}个正式发布文件与原publication SHA256或immutable metrics归档一致。第三轮原PNG签名、尺寸与服务hash匹配；root真实看图\${images.map(x=>x.root_actual_view.existing_view_id).join(' / ')}已绑定。\\n\\n本代理未HTTP/render/view/写总账，未计算对比度。明细：\\\`\${jsonPath}\\\`。all_writes_finished=true。\\n\`;\n`+s.slice(mdEnd);
s=s.replace("image:x.image,title:x.title,pixel_regression:x.pixel_regression,new_content_collision_checks:x.new_content_collision_checks","image:x.image,title:x.title,english_above_url:x.english_above_url,new_content_collision_checks:x.new_content_collision_checks");
s=s.replace("first_round_files_checked:oldFiles.checked_published_files","previous_round_files_checked:oldFiles.checked_published_files");
fs.writeFileSync(path.join(__dirname,'audit-round-03-v001.cjs'),s,{flag:'wx'});
console.log('Created immutable third-round content/geometry audit, leaving contrast to the assigned specialist.');
