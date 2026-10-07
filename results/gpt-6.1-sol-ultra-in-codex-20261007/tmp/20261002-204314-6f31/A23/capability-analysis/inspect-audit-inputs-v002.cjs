'use strict';
const fs=require('node:fs'),path=require('node:path');
const base='D:/workspaces/gpt-6.1-sol-ultra/tmp/20261002-204314-6f31/A23';
const x=JSON.parse(fs.readFileSync(path.join(base,'frame-data-final-v002.json'),'utf8'));
const clip=v=>Array.isArray(v)?{length:v.length,first:v[0]}:v;
console.log(JSON.stringify({frame:x.frames[0],audit:Object.fromEntries(Object.entries(x.audit).map(([k,v])=>[k,clip(v)])),trajectory_keys:Object.keys(x.trajectory),per_key_step_first:x.trajectory.per_key_steps[0],},null,2));
