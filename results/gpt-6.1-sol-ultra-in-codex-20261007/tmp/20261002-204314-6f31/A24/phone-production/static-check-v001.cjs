'use strict';
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const dir=__dirname,dslBytes=fs.readFileSync(path.join(dir,'action-card-v001.snapshot')),dsl=dslBytes.toString('utf8'),layout=JSON.parse(fs.readFileSync(path.join(dir,'action-card-layout-v001.json'),'utf8'));
const sha=crypto.createHash('sha256').update(dslBytes).digest('hex'),sizes=[...dsl.matchAll(/fontSize="([^"]+)"/g)].map(x=>Number(x[1]));
const result={created_at:new Date().toISOString(),kind:'read_only_static_cross_check',dsl_sha256:sha,hash_matches_map:sha===layout.dsl_sha256,actual_text_tags:(dsl.match(/<Text\b/g)||[]).length,map_text_count:layout.elements.filter(x=>x.type==='text').length,actual_min_font_px:Math.min(...sizes),external_asset_tag_found:/<Image\b|<Svg\b|<Canvas\b/.test(dsl),root_dimension_match:/<Container width="720" height="1280">/.test(dsl),row_ids:layout.rows.map(x=>x.id),risk_task_ids:layout.risks.map(x=>x.task),risk_mitigations:layout.risks.map(x=>x.displayed_mitigation),rendered:false,viewed:false};
if(!result.hash_matches_map||result.actual_text_tags!==result.map_text_count||result.actual_min_font_px<20||result.external_asset_tag_found||!result.root_dimension_match)throw Error('Static cross-check failed');
fs.writeFileSync(path.join(dir,'static-check-v001.json'),JSON.stringify(result,null,2)+'\n',{flag:'wx'});
fs.writeFileSync(path.join(dir,'static-check-shell-error-v001.txt'),'Earlier PowerShell inline node -e verification failed before Node ran (exit code 1):\nParserError: Line 2: Missing type name after [ in an incorrectly shell-escaped fontSize regular expression.\nRecovered using this literal stdin-written .cjs file; no draft changes or render calls resulted from the failed command.\n',{flag:'wx'});
console.log(JSON.stringify(result));
