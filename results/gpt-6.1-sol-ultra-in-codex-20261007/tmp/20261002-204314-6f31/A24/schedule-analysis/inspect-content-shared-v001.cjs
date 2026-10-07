'use strict';
const fs=require('node:fs'),path=require('node:path');
const base='D:/workspaces/gpt-6.1-sol-ultra/tmp/20261002-204314-6f31/A24';
const x=JSON.parse(fs.readFileSync(path.join(base,'content-map-v001.json'),'utf8'));
console.log(JSON.stringify({facts:x.shared_facts,images:x.images.map(im=>({stem:im.stem,keys:Object.keys(im),canvas:im.canvas,dsl_path:im.dsl_path,dsl_sha256:im.dsl_sha256})),final_request_ids:x.final_request_ids,view_ids:x.view_ids},null,2));
const y=fs.readFileSync(path.join(base,'iterations.jsonl'),'utf8').trim().split(/\r?\n/).map(JSON.parse);
console.log(JSON.stringify({iteration_count:y.length,complete:y.filter(x=>x.completed===true),types:[...new Set(y.map(x=>x.type))]},null,2));
