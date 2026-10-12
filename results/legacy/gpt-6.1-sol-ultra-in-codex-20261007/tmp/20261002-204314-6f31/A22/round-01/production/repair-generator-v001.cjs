'use strict';
const fs=require('node:fs'),path=require('node:path');
const from=path.join(__dirname,'build-dashboard-v001.cjs'),to=path.join(__dirname,'build-dashboard-v002.cjs');
const original=fs.readFileSync(from,'utf8');
const fixed=original.replace("k==='month'?vals[i]:Number(vals[i])])));","k==='month'?vals[i]:Number(vals[i])]));").replace('y_max:240000,ticks:[0,60000,120000,180000,240000]','y_max:250000,ticks:[0,50000,100000,150000,200000,250000]').replaceAll('node tmp/20261002-204314-6f31/A22/round-01/production/build-dashboard-v001.cjs','node tmp/20261002-204314-6f31/A22/round-01/production/build-dashboard-v002.cjs');
if(fixed===original)throw Error('Expected correction was not made');
fs.writeFileSync(to,fixed,{flag:'wx'});
fs.writeFileSync(path.join(__dirname,'generator-repair-evidence-v001.json'),JSON.stringify({created_at:new Date().toISOString(),failed_generator:from,fixed_generator:to,error:'SyntaxError: Unexpected token ) in line8 Object.fromEntries(keys.map(...)), observed in actual Node invocation.',request_created:false,changes:['Remove one unmatched closing parenthesis.','Adopt independently suggested fixed shared chart axis 0–250000, 50000 steps.'],classification:'Local generator syntax repair before DSL generation; no render request and no rendered DSL syntax-fix version.'},null,2)+'\n',{flag:'wx'});
console.log(to);
