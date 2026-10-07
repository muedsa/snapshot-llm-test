const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),s=require('../../_suite/suite.cjs');
const hash=x=>crypto.createHash('sha256').update(x).digest('hex'),write=(n,d)=>fs.writeFileSync(path.join(__dirname,n),d,{flag:'wx'});
const drafts=JSON.parse(fs.readFileSync(path.join(__dirname,'examples-draft-v001.json'),'utf8'));
const baselines=JSON.parse(fs.readFileSync(path.join(__dirname,'baseline-view-records-v001.json'),'utf8'));
const page04before=JSON.parse(fs.readFileSync(path.join(__dirname,'refined-view-record-v002.json'),'utf8'));
const newDrafts=[],jobs=[];
for(const page of ['03','04']){
 const stem='example-'+page,previous=fs.readFileSync(path.join(__dirname,stem+'-v001.snapshot'),'utf8');
 const current=previous.replaceAll('fontSize="20"','fontSize="24"').replace('<Raw>FF = 255/255   80 = 128/255</Raw>','<Raw>FF 255/255   80 128/255</Raw>');
 const prefix='<Snapshot type="png" background="#FFFFFF">\n',suffix='\n</Snapshot>\n';
 const oldWidget=previous.slice(prefix.length,-suffix.length),widget=current.slice(prefix.length,-suffix.length);
 write(stem+'-v002.snapshot',current);
 const pageVersion=page==='04'?'v003':'v002',pageBefore=page==='04'?'v002':'v001',pageStem='handbook-'+page;
 const pageSource=fs.readFileSync(path.join(__dirname,pageStem+'-'+pageBefore+'.snapshot'),'utf8');
 if(!pageSource.includes(oldWidget))throw Error('exact before widget absent');
 const newPage=pageSource.replace(oldWidget,widget);write(pageStem+'-'+pageVersion+'.snapshot',newPage);
 const oldDraft=drafts.find(e=>e.page===Number(page)),fullLines=current.trimEnd().split('\n');
 const draft={...oldDraft,complete_dsl_file:path.join(__dirname,stem+'-v002.snapshot'),root_widget_sha256:hash(widget),full_dsl_sha256:hash(current),printed_source_lines:oldDraft.printed_source_lines.map(r=>({line:r.line,source:fullLines[r.line-1]})),all_figure_text_font_min:24};newDrafts.push(draft);
 jobs.push({stem,version:'v002',parent:'v001',dsl:current,before:baselines.find(r=>r.stem===stem).view_id,changes:page==='03'?'实际图示底部alpha说明20→24px；为同列完整可见，删去等号，保留FF/80与255/255/128/255内容。':'实际图示外部BACKGROUND/SUBTREE标题20→24px；两过滤输入及SHARP字不变。'});
 jobs.push({stem:pageStem,version:pageVersion,parent:pageBefore,dsl:newPage,before:page==='04'?page04before.id:baselines.find(r=>r.stem===pageStem).view_id,changes:'按正文24px目标同步替换直接嵌入的独立示例构件；其余正文、16真实代码行及说明不变。'});
}
write('examples-draft-v002.json',JSON.stringify(newDrafts,null,2)+'\n');
(async()=>{
 const out=await Promise.all(jobs.map(async j=>{const r=await s.render('A17',j.dsl,{version_id:'A17-'+j.version+'-'+j.stem,parent_version:'A17-'+j.parent+'-'+j.stem,type:'visual',stem:j.stem,case_id:j.stem,width:j.stem.startsWith('example')?400:1200,height:j.stem.startsWith('example')?240:1600,before_view_id:j.before,changes:j.changes,purpose:'A17 illustration readable-font refinement '+j.stem});
 const small={stem:j.stem,ok:r.ok,http_status:r.http_status,content_type:r.content_type,png_dimensions:r.png_dimensions,meta_path:r.meta_path,image_path:r.image_path,version_id:r.version_id,parent_version:'A17-'+j.parent+'-'+j.stem,before_view_id:j.before,changes:j.changes,error_summary:r.error_summary};
 write(j.stem+'-render-'+j.version+'.json',JSON.stringify(small,null,2)+'\n');return small;}));
 console.log(JSON.stringify(out));
})().catch(e=>{console.error(e.stack);process.exitCode=1;});
