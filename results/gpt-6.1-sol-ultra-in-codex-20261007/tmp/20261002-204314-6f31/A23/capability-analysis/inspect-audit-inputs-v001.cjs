'use strict';
const fs=require('node:fs'),path=require('node:path');
const base='D:/workspaces/gpt-6.1-sol-ultra/tmp/20261002-204314-6f31/A23';
for (const name of ['frame-data-final-v002.json','png-alpha-audit-v001.json','root-final-review-v001.json','timing-final-v001.json']) {
  const x=JSON.parse(fs.readFileSync(path.join(base,name),'utf8'));
  console.log(JSON.stringify({name,keys:Object.keys(x),summary:Object.fromEntries(Object.entries(x).map(([k,v])=>[k,Array.isArray(v)?{array_length:v.length,first:v[0],last:v.length>1?v[v.length-1]:undefined}:v])),},null,2));
}
for (const name of ['views.jsonl','requests.jsonl','iterations.jsonl','versions.jsonl']) {
  const rows=fs.readFileSync(path.join(base,name),'utf8').trim().split(/\r?\n/).filter(Boolean).map(JSON.parse);
  console.log(JSON.stringify({name,count:rows.length,first:rows[0],last:rows[rows.length-1]},null,2));
}
