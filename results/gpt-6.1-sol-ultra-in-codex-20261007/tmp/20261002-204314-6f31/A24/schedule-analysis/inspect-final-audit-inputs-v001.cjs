'use strict';
const fs=require('node:fs'),path=require('node:path');
const base='D:/workspaces/gpt-6.1-sol-ultra/tmp/20261002-204314-6f31/A24';
for(const name of ['content-map-v001.json','root-final-review-v001.json']){
 const x=JSON.parse(fs.readFileSync(path.join(base,name),'utf8'));
 if(name.startsWith('root-'))console.log(JSON.stringify({name,data:x},null,2));
 else console.log(JSON.stringify({name,keys:Object.keys(x),summary:Object.fromEntries(Object.entries(x).map(([k,v])=>[k,Array.isArray(v)?{count:v.length,first_keys:v[0]&&typeof v[0]==='object'?Object.keys(v[0]):v[0]}:v&&typeof v==='object'?{keys:Object.keys(v)}:v]))},null,2));
}
for(const id of ['000004','000002','000003']){
 const p=path.join(base,'requests/A24-request-'+id+'/render-result.json'),x=JSON.parse(fs.readFileSync(p,'utf8'));
 console.log(JSON.stringify({id,metadata:x},null,2));
}
