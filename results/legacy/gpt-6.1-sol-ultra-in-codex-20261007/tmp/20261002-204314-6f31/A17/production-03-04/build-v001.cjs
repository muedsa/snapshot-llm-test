// Generates original, pure Snapshot DSL. No network, view, publication or state changes.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const {handbook}=require('../handbook-style-v001.cjs');
const dir=__dirname,hash=x=>crypto.createHash('sha256').update(x).digest('hex');
const write=(n,d)=>fs.writeFileSync(path.join(dir,n),d,{flag:'wx'});
function lineCols(x){return [...x].reduce((a,c)=>a+(/[\u0020-\u007e]/.test(c)?1:2),0);}
function example(page,widget,printed){
 const source='<Snapshot type="png" background="#FFFFFF">\n'+widget+'\n</Snapshot>\n';
 const lines=source.trimEnd().split('\n'),rows=printed.map(i=>({line:i,source:lines[i-1]}));
 const codeLines=rows.map(r=>String(r.line).padStart(3,'0')+' '+r.source.trimStart());
 if(rows.some(r=>!r.source))throw Error('missing selected line');
 if(codeLines.some(r=>lineCols(r)>49))throw Error('long print source: '+JSON.stringify(codeLines.filter(r=>lineCols(r)>49)));
 write(`example-${page}-v001.snapshot`,source);
 const info={page:Number(page),stem:`example-${page}`,complete_dsl_file:path.join(dir,`example-${page}-v001.snapshot`),root_widget_sha256:hash(widget),full_dsl_sha256:hash(source),printed_source_lines:rows,printed_display_lines:codeLines,omitted_source_lines:lines.map((_,i)=>i+1).filter(n=>!printed.includes(n)),exact_root_widget_directly_embedded:true,uses_Image:false};
 return {widget,source,info,codeLines};
}
const w3=[
'<Container width="400" height="240" color="#FFFFFF">',
' <Padding padding="16">',
'  <Column crossAxisAlignment="START">',
'   <Text fontFamily="DejaVu Sans Mono"',
'     fontSize="24" color="#172D48">',
'    <Raw><![CDATA[  <A> & B  ]]></Raw>',
'   </Text>',
'   <SizedBox height="10"/>',
'   <Text fontFamily="Inter" fontSize="24"',
'     color="#172D48">',
'    <Raw>Style: </Raw>',
'    <Text color="#2964D8" fontStyle="BOLD">',
'     blue',
'    </Text>',
'    <Raw> & literal</Raw>',
'   </Text>',
'   <SizedBox height="18"/>',
'   <Row>',
'    <Container width="176" height="64"',
'      color="#FF0000FF"/>',
'    <SizedBox width="16"/>',
'    <Container width="176" height="64"',
'      color="#FF000080"/>',
'   </Row>',
'   <SizedBox height="10"/>',
'   <Text fontFamily="DejaVu Sans Mono"',
'     fontSize="20" color="#536780">',
'    <Raw>FF = 255/255   80 = 128/255</Raw>',
'   </Text>',
'  </Column>',
' </Padding>',
'</Container>'
].join('\n');
const e3=example('03',w3,[5,6,7,8,10,11,12,13,14,15,16,17,20,21,23,24]);
const p3=handbook({page:3,title:'文字保真：空白、字面字符与样式',intro:'先区分解析文本和绘制样式，再确认颜色的透明度。\nRaw 保留空白；CDATA 让尖括号保持为文本。',
 principles:['Raw 保留首尾空格与换行；普通 Text 文本会 trim。','CDATA 保留 <、>；解析器不会解码 HTML 实体。','嵌套 Text 是行内 Span；#RRGGBBAA 的 AA 在尾部。'],
 codeLines:e3.codeLines,codeScope:'印 example-03 第 5–17、20–21、23–24 行；其余行省略，完整源附后。',exampleWidget:e3.widget,figureTitle:'同一构件的真实输出',figureNotes:'首行保留两端空格与 <A> & B。\nblue 是嵌套 Text 的蓝色粗体。\n下方红块：左 FF、右 80；\n白底上右侧显示约 50% 红色。',
 leftTitle:'别让实体改变原文',leftBody:'要印 <A>，用 CDATA。\n写 &lt; 不会变成尖括号。\nRaw 只能在 Text 的行内树里。\n字体固定为已查询的字体族。',rightTitle:'颜色的最后两位',rightBody:'#FF0000FF：不透明红色。\n#FF000080：128/255 alpha。\n当前 Parser 采用尾部 alpha。\n旧 #AARRGGBB 写法不能照搬。'});
write('handbook-03-v001.snapshot',p3);
function pos(x,y,w,h,lines){return [`<Positioned left="${x}" top="${y}"`, ` width="${w}" height="${h}">`,...lines,'</Positioned>'];}
function stripes(){const a=['<Container width="180" height="176"', ' color="#FFFFFF">','<Stack fit="EXPAND">'];for(let x=0;x<180;x+=18){a.push(...pos(x,0,10,176,[`<Container color="${x%36===0?'#193E68':'#19A99D'}"/>`]));}a.push('</Stack>','</Container>');return a;}
function foreground(){return ['<Container width="180" height="176"',' color="#FFFFFF99">','<Stack fit="EXPAND">',...pos(22,56,148,42,['<Text fontFamily="Inter" fontSize="28"',' color="#172D48" fontStyle="BOLD">','<Raw>SHARP</Raw>','</Text>']),...pos(22,114,104,22,['<Container color="#172D48"/>']),'</Stack>','</Container>'];}
const w4lines=['<Container width="400" height="240"',' color="#FFFFFF">','<Stack fit="EXPAND">',...pos(12,8,180,30,['<Text fontFamily="Inter" fontSize="20"',' color="#536780"><Raw>BACKGROUND</Raw></Text>']),...pos(208,8,180,30,['<Text fontFamily="Inter" fontSize="20"',' color="#536780"><Raw>SUBTREE</Raw></Text>']),...pos(12,48,180,176,stripes()),...pos(208,48,180,176,stripes()),...pos(12,48,180,176,['<ClipRect>','<BackdropFilter sigmaX="3" sigmaY="3">',...foreground(),'</BackdropFilter>','</ClipRect>']),...pos(208,48,180,176,['<ClipRect>','<ImageFiltered sigmaX="3" sigmaY="3">','<Container width="180" height="176">','<Stack fit="EXPAND">',...pos(0,0,180,176,stripes()),...pos(0,0,180,176,foreground()),'</Stack>','</Container>','</ImageFiltered>','</ClipRect>']),'</Stack>','</Container>'];
const w4=w4lines.join('\n'),fulllines=('<Snapshot type="png" background="#FFFFFF">\n'+w4+'\n</Snapshot>').split('\n');
// Derive selected source lines from literal actual source, avoiding invented snippets.
function findAll(s){return fulllines.flatMap((l,i)=>l===s?[i+1]:[]);}
const backdrop=findAll('<BackdropFilter sigmaX="3" sigmaY="3">')[0],image=findAll('<ImageFiltered sigmaX="3" sigmaY="3">')[0];
const leftText=findAll('<Raw>SHARP</Raw>')[0],rightText=findAll('<Raw>SHARP</Raw>')[1];
const selected4=[backdrop-1,backdrop,backdrop+1,backdrop+2,leftText-2,leftText-1,leftText,leftText+1,findAll('</BackdropFilter>')[0],image-1,image,rightText-2,rightText-1,rightText,rightText+1,findAll('</ImageFiltered>')[0]].sort((a,b)=>a-b);
const e4=example('04',w4,selected4);
const p4=handbook({page:4,title:'滤镜语义：先有背景，再看差别',intro:'同一条纹、同一文字，放进不同滤镜会得到不同结果。\n先判定过滤输入，再检查原图、缩略图与局部。',
 principles:['Stack 先画条纹，再画裁剪区中的背景滤镜。','BackdropFilter 读已画背景；它的前景字仍清晰。','ImageFiltered 处理子树；内部文字和图形一起模糊。'],
 codeLines:e4.codeLines,codeScope:`印 example-04 第 ${e4.info.printed_source_lines.map(r=>r.line).join('、')} 行；其余行省略。`,exampleWidget:e4.widget,figureTitle:'sigma 3 的真实对照',figureNotes:'左：条纹变柔，SHARP 清晰。\n右：子树里的字与深色条变柔。\n两侧输入条纹和前景相同。\nClipRect 限定每个 180×176 区域。',
 leftTitle:'视觉自检顺序',leftBody:'先查 HTTP 状态与 Content-Type。\n再看文字、边界和模糊范围。\n打开原尺寸、缩略与局部。\n失败响应保留后再修 DSL。',rightTitle:'可复现交付',rightBody:'保留完整 .snapshot 与原 PNG。\n记录字体、响应头与 request ID。\n保存每版查看、变化与比较。\n图片和源码使用同名文件。'});
write('handbook-04-v001.snapshot',p4);
write('examples-draft-v001.json',JSON.stringify([e3.info,e4.info],null,2)+'\n');
write('construction-audit-v001.json',JSON.stringify({generated_at:new Date().toISOString(),pages:[{stem:'handbook-03',width:1200,height:1600,body_font_min:24,code_font:20,safe_margin:64,code_printed_lines:e3.codeLines.length,max_print_columns:Math.max(...e3.codeLines.map(lineCols)),contains_exact_example_widget:p3.includes(w3),widget_sha256:hash(w3)},{stem:'handbook-04',width:1200,height:1600,body_font_min:24,code_font:20,safe_margin:64,code_printed_lines:e4.codeLines.length,max_print_columns:Math.max(...e4.codeLines.map(lineCols)),contains_exact_example_widget:p4.includes(w4),widget_sha256:hash(w4)}],no_images:![p3,p4,w3,w4].some(s=>/<Image\b/.test(s)),pure_DSL:true},null,2)+'\n');
console.log(JSON.stringify({files:['example-03-v001.snapshot','handbook-03-v001.snapshot','example-04-v001.snapshot','handbook-04-v001.snapshot'],print3:e3.info.printed_source_lines.map(r=>r.line),print4:e4.info.printed_source_lines.map(r=>r.line)}));
