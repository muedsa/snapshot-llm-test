'use strict';
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const s=require('../../_suite/suite.cjs');
const {handbook}=require('../handbook-style-v001.cjs');
const dir=__dirname;
const write=(f,t)=>fs.writeFileSync(path.join(dir,f),t,{flag:'wx'});
const sha=t=>crypto.createHash('sha256').update(t).digest('hex');
const example01=[
'<Snapshot type="png">',
'<Container width="400" height="240"',
'  color="#DDF6EF" padding="24">',
'<Column mainAxisAlignment="CENTER"',
'  crossAxisAlignment="START">',
'<Text fontFamily="Inter" fontSize="32"',
'  color="#172D48" fontStyle="BOLD">',
'<Raw>Hello Snapshot</Raw>',
'</Text>',
'<Container height="12"/>',
'<Text fontFamily="Inter" fontSize="20"',
'  color="#2964D8">',
'<Raw>DSL to PNG / 400 x 240</Raw>',
'</Text>',
'</Column>',
'</Container>',
'</Snapshot>'
];
const example02=[
'<Snapshot type="png">',
'<Container width="400" height="240"',
'  color="#FFFFFF" padding="16">',
'<Column crossAxisAlignment="STRETCH">',
'<Expanded>',
'<Row crossAxisAlignment="STRETCH">',
'<Expanded flex="2">',
'<Container color="#2964D8"',
'  alignment="CENTER">',
'<Text fontSize="24" color="#FFFFFF">',
'<Raw>Row 2</Raw>',
'</Text>',
'</Container>',
'</Expanded>',
'<Expanded flex="1">',
'<Container color="#7EE1C3"',
'  alignment="CENTER">',
'<Text fontSize="24" color="#172D48">',
'<Raw>1</Raw>',
'</Text>',
'</Container>',
'</Expanded>',
'</Row>',
'</Expanded>',
'<Container height="16"/>',
'<Expanded>',
'<Stack fit="EXPAND">',
'<Container color="#E8EFF8"/>',
'<Positioned left="12" top="12"',
'  width="150" height="52">',
'<Container color="#2964D8"',
'  alignment="CENTER">',
'<Text fontSize="24" color="#FFFFFF">',
'<Raw>Stack</Raw>',
'</Text>',
'</Container>',
'</Positioned>',
'<Positioned right="12" bottom="12"',
'  width="90" height="40">',
'<Container color="#7EE1C3"',
'  alignment="CENTER">',
'<Text fontSize="24" color="#172D48">',
'<Raw>Tip</Raw>',
'</Text>',
'</Container>',
'</Positioned>',
'</Stack>',
'</Expanded>',
'</Column>',
'</Container>',
'</Snapshot>'
];
const e1=example01.join('\n'),e2=example02.join('\n');
const widget1=example01.slice(1,-1).join('\n'),widget2=example02.slice(1,-1).join('\n');
const specs=[
 {page:1,title:'01 / 先调用，再核对响应',intro:'把类 DOM 文本提交给 Snapshot 服务。它将 Widget 树布局、绘制并编码为图片；先识别响应类型，再保存可复现结果。',principles:[
   'POST /snapshot；请求体是 UTF-8 纯文本，Content-Type 为 text/plain。',
   'type="png" / "jpg" / "webp"；成功 200 返回对应格式的图片字节。',
   '检查 HTTP 状态与 Content-Type，再把原字节保存为匹配的后缀。'
 ],codeLines:example01,codeScope:'完整示例：第 1–17 行，无省略。400×240 根尺寸由 Container 布局给出。',exampleWidget:widget1,figureTitle:'真实 DSL 构件 / 400×240',figureNotes:'右侧由同一示例的根 Widget 直接绘制。\n\n另存 example-01.snapshot，独立请求可复现此图。',leftTitle:'遇到错误：先读消息',leftBody:'常规错误 JSON 含 code、message、requestId。400 修 DSL；413 缩小请求体；401 检查凭据。错误体不能当 PNG。',rightTitle:'重试与关联记录',rightBody:'429 / 部分 503 参考 Retry-After。保留 X-Request-Id。默认不加 errorImage=png；错误图仍为 400。'} ,
 {page:2,title:'02 / 先给约束，再谈位置',intro:'根尺寸来自布局协议。父节点传递约束，子节点报告尺寸：Row/Column 分配空间，Stack 让构件层叠定位。',principles:[
   '先用 Container / SizedBox 给出有限尺寸；根图必须有非零宽高。',
   'Row 横向、Column 纵向；主轴有界，Expanded 才能分配剩余空间。',
   'Expanded 直属 Flex；Positioned 直属 Stack / IndexedStack。'
 ],codeLines:example02.slice(5,23),codeScope:'节选完整示例第 6–23 行；省略 1–5 与 24–51 行，见 example-02.snapshot。',exampleWidget:widget2,figureTitle:'上：Flex / 下：Stack',figureNotes:'上行 Expanded 的份额为 2:1。\n\n下层按 left/top 与 right/bottom 定位；背景与标签层叠。',leftTitle:'有限空间中的 Flex',leftBody:'完整根为 400×240，内边距 16。Column 的两个 Expanded 分配纵向空间，Row 的 Expanded 分配横向空间。',rightTitle:'定位与裁剪要分清',rightBody:'同一轴的 left / right / width 最多填两项，纵轴同理。Stack 默认 HARD_EDGE；裁剪只决定绘制可见范围。'}
];
const records=[];
for(let i=0;i<2;i++){
 const stem='example-'+String(i+1).padStart(2,'0'),full=[e1,e2][i],root=[widget1,widget2][i],spec=specs[i];
 write(stem+'-v001.snapshot',full+'\n');
 const pageDsl=handbook(spec);write('handbook-'+String(i+1).padStart(2,'0')+'-v001.snapshot',pageDsl+'\n');
 records.push({id:stem,page:i+1,purpose:i===0?'真实 POST 输入及图片输出的最小文本卡':'有限 Row/Column/Expanded 与 Stack/Positioned 对照',full_source:path.join(dir,stem+'-v001.snapshot'),line_count:[example01,example02][i].length,printed_source_lines:i===0?[1,17]:[6,23],omitted_source_line_ranges:i===0?[]:[[1,5],[24,51]],printed_lines:spec.codeLines,exact_root_widget_sha256:sha(root),embedded_as:'direct root Widget inside Positioned 400 x 240; no Image',handbook_dsl:path.join(dir,'handbook-'+String(i+1).padStart(2,'0')+'-v001.snapshot'),print_max_ascii_columns:Math.max(...spec.codeLines.map(t=>t.length)),declared_width:400,declared_height:240});
}
write('example-mapping-v001.json',JSON.stringify(records,null,2)+'\n');
write('shared-document-read-v001.json',JSON.stringify({read_at:new Date().toISOString(),reader:'/root/a17_producer_01_02',mode:'actual cached-response reuse; no additional HTTP counted',documents:[['guide','https://open-snapshot.muedsa.com/ai-guide.md','shared-doc-000001-response.txt'],['parser','https://snapshot.muedsa.com/guides/parser/','shared-doc-000003-readable.txt'],['parser tags','https://snapshot.muedsa.com/reference/parser-tags/','shared-doc-000004-readable.txt'],['layout','https://snapshot.muedsa.com/guides/layout/','shared-doc-000005-readable.txt'],['OpenAPI','https://open-snapshot.muedsa.com/openapi.yaml','shared-doc-000006-readable.txt'],['fonts','https://open-snapshot.muedsa.com/fonts','shared-fonts-000001-readable.txt']].map(([kind,url,file])=>({kind,url,cache:path.resolve(dir,'../../_suite',file)}))},null,2)+'\n');
async function main(){
 for(const stem of ['example-01','handbook-01','example-02','handbook-02']){
  const dsl=fs.readFileSync(path.join(dir,stem+'-v001.snapshot'),'utf8');
  const isExample=stem.startsWith('example');
  const result=await s.render('A17',dsl,{version_id:'A17-v001-'+stem,stem,case_id:stem,independent_case:false,type:'baseline',width:isExample?400:1200,height:isExample?240:1600,purpose:'A17 producer 01/02 '+stem+'; exact runnable illustration'});
  const {bytes,body,text,json,...r}=result;write(stem+'-render-result-v001.json',JSON.stringify(r,null,2)+'\n');console.log(JSON.stringify({stem,ok:r.ok,status:r.http_status,meta:r.meta_path,image:r.image_path,error:r.error_summary}));
  if(!result.ok||result.dimension_error)throw Error('Actual render failed for '+stem+': '+result.error_summary);
 }
}
main().catch(e=>{write('production-error-v001.json',JSON.stringify({at:new Date().toISOString(),error:String(e)},null,2));process.exitCode=1;});
