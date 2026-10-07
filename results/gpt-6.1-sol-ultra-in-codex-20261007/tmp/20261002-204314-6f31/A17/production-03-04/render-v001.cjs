const fs=require('node:fs'),path=require('node:path'),s=require('../../_suite/suite.cjs');
const stems=['example-03','handbook-03','example-04','handbook-04'];
(async()=>{
 const results=await Promise.all(stems.map(async stem=>{
  const result=await s.render('A17',fs.readFileSync(path.join(__dirname,stem+'-v001.snapshot'),'utf8'),{version_id:'A17-v001-'+stem,parent_version:null,type:'baseline',stem,case_id:stem,width:stem.startsWith('example')?400:1200,height:stem.startsWith('example')?240:1600,purpose:'A17 true baseline '+stem+'; pure DSL exact example widget'});
  const small={stem,ok:result.ok,http_status:result.http_status,content_type:result.content_type,png_dimensions:result.png_dimensions,meta_path:result.meta_path,image_path:result.image_path,version_id:result.version_id,error_summary:result.error_summary};
  fs.writeFileSync(path.join(__dirname,stem+'-render-v001.json'),JSON.stringify(small,null,2)+'\n',{flag:'wx'});return small;
 }));
 console.log(JSON.stringify(results));
})().catch(e=>{console.error(e.stack);process.exitCode=1;});
