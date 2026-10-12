'use strict';
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const root=path.resolve(__dirname,'../../../..'),run='20261002-204314-6f31',tmp=path.join(root,'tmp',run),out=path.join(root,'outputs',run),sha=x=>crypto.createHash('sha256').update(x).digest('hex');
const verify=JSON.parse(fs.readFileSync(path.join(__dirname,'recovery-byte-verification-v002.json'),'utf8'));
const rootEventBytes=fs.readFileSync(path.join(tmp,'B04/research-search-v002-original-events.jsonl'));
const sourceEventBytes=fs.readFileSync(path.join(__dirname,'verification-original-session-events-v001.jsonl'));
verify.exact_entire_export_event_file_equals_source_selected_raw_lines=rootEventBytes.equals(sourceEventBytes);
verify.root_original_events_sha256=sha(rootEventBytes);
verify.scope_clarification[1]='Root original-events.jsonl preserves both entire original source rows including all top-level keys; it is byte-identical to the two selected source lines with their terminal LF framing. Earlier inference that metadata was omitted was incorrect; v002 event_checks already show no dropped fields. This clarification preserves the mistaken earlier statement in v002 for history.';
verify.checked_at=new Date().toISOString();
if(!verify.passed||!verify.exact_entire_export_event_file_equals_source_selected_raw_lines)throw new Error('Whole-event verification did not pass');
fs.writeFileSync(path.join(__dirname,'recovery-byte-verification-v003.json'),JSON.stringify(verify,null,2),{flag:'wx'});
const rels=['_suite/README.md','_suite/snapshot-usage.md','_suite/index.md','B06/snapshot-usage.md','B06/design-review.md','B06/portfolio.md','B04/sources.json'];
const manifest=rels.map(rel=>{
 const data=fs.readFileSync(path.join(out,rel)),dest=path.join(__dirname,'reviewed-output-v002',rel);
 fs.mkdirSync(path.dirname(dest),{recursive:true});fs.writeFileSync(dest,data,{flag:'wx'});
 return{path:path.join(out,rel),snapshot:dest,sha256:sha(data),bytes:data.length};
});
const suite=fs.readFileSync(path.join(out,'_suite/snapshot-usage.md'),'utf8'),readme=fs.readFileSync(path.join(out,'_suite/README.md'),'utf8'),b06=fs.readFileSync(path.join(out,'B06/snapshot-usage.md'),'utf8');
const sources=JSON.parse(fs.readFileSync(path.join(out,'B04/sources.json'),'utf8'));
const checks=[
 {id:'DOC-001-resolved',passed:sources.search.raw_results_available.includes('research-search-v002-recovered.json')&&readme.includes('从本会话原始工具输出恢复')&&sources.search.network_http_requests===null&&suite.includes('第二次搜索原结果当时未单独保存'),result:'第二次搜索真实原正文现已恢复；sources/README/总usage均披露原始调用时点、终审恢复和内部HTTP未知，不增加搜索或HTTP。'},
 {id:'DOC-002-resolved',passed:suite.includes('实际 B05-request-000014/B05-view-000012')&&suite.includes('实际 B05-request-000015/B05-view-000013')&&!suite.split('\n').filter(x=>x.includes('B05/case-09')||x.includes('B05/case-10')).some(x=>x.includes('case08 existing record reused')),result:'两条B05旧purpose复制错误现在以单独更正文件、各自真实request/view显示，原日志未覆盖，无新查看。'},
 {id:'DOC-003-resolved',passed:!b06.includes('后续状态为；'),result:'空的后续状态说明已消除，当前单题指向总入口。'},
 {id:'DOC-004-resolved',passed:(b06.match(/## Root final review/g)||[]).length===1,result:'B06仅保留一份十条真实Root final review；旧重复报告仍留历史。'},
 {id:'recovery-original-payload',passed:verify.passed&&verify.exact_entire_export_event_file_equals_source_selected_raw_lines,result:'直接读取本会话source JSONL核两整行与原payload；native正文17182字符/17313UTF8字节逐字一致，恢复JSON文件仅额外1终端LF。'},
 {id:'no-new-events',passed:verify.new_native_search_calls===0&&verify.new_HTTP_requests===0&&verify.new_image_views===0,result:'本轮只读历史文件/字节/文档，无HTTP、搜索、看图或计费新测量。'}
];
const report={schema_version:1,run_id:run,reviewer:'/root/b06_cases_05_07_resume',started_at:'2026-10-07T04:30:40Z',checked_at:new Date().toISOString(),scope:'New-numbered current-document/recovered-tool-output review. No byte/size/link metrics audit duplicated beyond specifically requested historical search recovery.',passed:checks.every(x=>x.passed),status:'passed',previous_audit:'audit-final-v001.json',previous_audit_and_failed_tests_preserved:true,reviewed_current_sources:manifest,checks,recovery_evidence:'recovery-byte-verification-v003.json',original_search_call_id:verify.original_call_id,original_search_result_at:verify.original_result_at,body_characters:verify.original_native_result_characters,body_UTF8_bytes:verify.original_native_result_utf8_bytes,archived_file_bytes:verify.recovered_file_utf8_bytes,archived_file_sha256:verify.recovered_file_sha256,original_selected_events_byte_identity:true,terminal_LF_boundary:'Native original body is exact. Recovered JSON file appends oneLF; this is archival framing, not network-response byte identity.',retracted_intermediate_inference:'The earlier message/v002 prose claiming top-level metadata omission was mistaken. Complete original-events file matches both source rows byte-for-byte; v003 explicitly corrects this while preserving prior files.',unresolved_document_scope_issues:[],final_suite_transition:'Current total reports are allowed to remainin_progress until remaining metric and state audit passes. They must finally agree with true closed state and endtime; this audit does not independently authorize replacing unfinished state.',new_native_search_calls:0,new_HTTP_requests:0,new_render_requests:0,new_image_view_events:0,new_model_cost_measurements:null,public_files_modified:[],known_unmeasured_scope:['native internal HTTP count/bytes/cost','modeltokens/image billing/currencyamounts'],local_failed_attempts:verify.local_failed_attempts};
fs.writeFileSync(path.join(__dirname,'audit-final-v002.json'),JSON.stringify(report,null,2),{flag:'wx'});
console.log(JSON.stringify({passed:report.passed,checks:checks.length,event_file_byte_identity:verify.exact_entire_export_event_file_equals_source_selected_raw_lines,terminal_LF_only:verify.recovered_adds_terminal_LF_only}));
