const fs=require('node:fs'),path=require('node:path'),s=require('../../_suite/suite.cjs'),{cdata}=require('../../_suite/dsl.cjs');
const draft=JSON.parse(fs.readFileSync(path.join(__dirname,'examples-draft-v001.json'),'utf8')).find(e=>e.page===4);
const oldText=`印 example-04 第 ${draft.printed_source_lines.map(r=>r.line).join('、')} 行；其余行省略。`;
const newText='印 example-04 所列 16 个源行号；中间与其余行省略，完整源附后。';
const baseline=fs.readFileSync(path.join(__dirname,'handbook-04-v001.snapshot'),'utf8');
if(!baseline.includes(cdata(oldText)))throw Error('before text absent');
const next=baseline.replace(cdata(oldText),cdata(newText));
fs.writeFileSync(path.join(__dirname,'handbook-04-v002.snapshot'),next,{flag:'wx'});
const before=JSON.parse(fs.readFileSync(path.join(__dirname,'baseline-view-records-v001.json'),'utf8')).find(r=>r.stem==='handbook-04');
(async()=>{
 const r=await s.render('A17',next,{version_id:'A17-v002-handbook-04',parent_version:'A17-v001-handbook-04',type:'visual',stem:'handbook-04',case_id:'handbook-04',width:1200,height:1600,before_view_id:before.view_id,changes:'将长源行号列表说明改成短说明，保留代码里的16个真实源行号；完整省略行映射留examples-draft-v001。',purpose:'A17 handbook04 actual visual clipping fix'});
 const out={ok:r.ok,http_status:r.http_status,content_type:r.content_type,meta_path:r.meta_path,image_path:r.image_path,version_id:r.version_id,png_dimensions:r.png_dimensions,error_summary:r.error_summary};
 fs.writeFileSync(path.join(__dirname,'handbook-04-render-v002.json'),JSON.stringify(out,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify(out));
})().catch(e=>{console.error(e.stack);process.exitCode=1;});
