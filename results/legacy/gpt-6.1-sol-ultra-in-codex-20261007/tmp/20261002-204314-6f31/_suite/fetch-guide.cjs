const fs=require('fs'),path=require('path');
async function get(url,id) {
 const dir=path.join(process.cwd(),'tmp','20261002-204314-6f31','_suite');
 const start=new Date();
 const request={url,method:'GET',headers:{accept:'text/markdown, text/html, application/json, */*'}};
 fs.writeFileSync(path.join(dir,id+'-request.json'),JSON.stringify(request,null,2),{flag:'wx'});
 let status=null,ct=null,error=null,headers={};
 try { const r=await fetch(url,{headers:request.headers,signal:AbortSignal.timeout(45000)});status=r.status;headers=Object.fromEntries(r.headers);ct=r.headers.get('content-type');const b=Buffer.from(await r.arrayBuffer());fs.writeFileSync(path.join(dir,id+'-response.bin'),b,{flag:'wx'}); fs.writeFileSync(path.join(dir,id+'-response.txt'),b.toString('utf8'),{flag:'wx'});console.log(JSON.stringify({id,status,content_type:ct,bytes:b.length,body:b.toString('utf8')})); }
 catch(e) {error=String(e); fs.writeFileSync(path.join(dir,id+'-error.txt'),error,{flag:'wx'});console.log(JSON.stringify({id,error}));}
 fs.writeFileSync(path.join(dir,id+'-headers.json'),JSON.stringify(headers,null,2),{flag:'wx'});
 const end=new Date();fs.appendFileSync(path.join(dir,'requests.jsonl'),JSON.stringify({id,type:'document',url,started_at:start.toISOString(),ended_at:end.toISOString(),duration_seconds:(end-start)/1000,status,content_type:ct,request_file:path.join(dir,id+'-request.json'),response_file:status?path.join(dir,id+'-response.bin'):null,error,requestId:headers['x-request-id']||null,server_timing:headers['server-timing']||null})+'\n');
}
Promise.all([get('https://open-snapshot.muedsa.com/ai-guide.md','shared-doc-000001'),get('https://snapshot.muedsa.com/','shared-doc-000002')]);
