'use strict';
const fs=require('node:fs'),path=require('node:path'),s=require('./suite.cjs');
const info=s.countsFor('A07');
const matches=info.finals.map(a=>{const r=info.requests.find(r=>r.id===a.request_id);return {artifact_id:a.id,image_path:a.image_path,version_id:a.version_id,request_id:a.request_id,http_success:r?.ok??null,request_ended_at:r?.ended_at??null,registered_at:a.registered_at};});
const chronological=matches.filter(m=>m.http_success&&typeof m.request_ended_at==='string'&&Number.isFinite(Date.parse(m.request_ended_at))).sort((a,b)=>Date.parse(a.request_ended_at)-Date.parse(b.request_ended_at));
const result={run_id:'20261002-204314-6f31',inspected_at:new Date().toISOString(),task_id:'A07',scope:'Read-only current-final request chronology; no state or metric mutation',current_final_order:matches,old_first_by_array:matches[0]??null,earliest_known_successful_current_final:chronological[0]??null,array_order_differs_from_chronology:matches[0]?.request_id!==chronological[0]?.request_id};
fs.writeFileSync(path.join(__dirname,'first-usable-order-evidence-000001.json'),JSON.stringify(result,null,2)+'\n',{flag:'wx'});
process.stdout.write(JSON.stringify(result)+'\n');
