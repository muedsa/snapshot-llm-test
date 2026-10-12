'use strict';
const fs=require('fs'),path=require('path'),crypto=require('crypto'),readline=require('readline');
const root=path.resolve(__dirname,'../../../..'),run='20261002-204314-6f31';
const tmp=path.join(root,'tmp',run),out=path.join(root,'outputs',run);
const sha=x=>crypto.createHash('sha256').update(x).digest('hex');
(async()=>{
 const recovery=JSON.parse(fs.readFileSync(path.join(tmp,'B04/research-search-v002-recovery-v001.json'),'utf8'));
 const saved=fs.readFileSync(recovery.result_path);
 const exported=fs.readFileSync(recovery.original_event_file,'utf8').trim().split(/\r?\n/).map(JSON.parse);
 const matches=[];let ordinal=0;
 for await(const line of readline.createInterface({input:fs.createReadStream(recovery.source_session,{encoding:'utf8'}),crlfDelay:Infinity})){
  ordinal++;
  if(!line.includes(recovery.original_call_id))continue;
  let parsed;try{parsed=JSON.parse(line);}catch{continue;}
  if(parsed.payload?.call_id===recovery.original_call_id&&['custom_tool_call','custom_tool_call_output'].includes(parsed.payload.type))matches.push({ordinal,line,parsed});
 }
 if(matches.length!==2)throw new Error('Expected exactly2 original call/output events; found'+matches.length);
 fs.writeFileSync(path.join(__dirname,'verification-original-session-events-v001.jsonl'),matches.map(x=>x.line).join('\n')+'\n',{flag:'wx'});
 const sameEvents=exported.map(e=>{
  const orig=matches.find(x=>x.parsed.payload.type===e.payload.type),copy={...e};delete copy.ordinal;
  return{payload_type:e.payload.type,timestamp:e.timestamp,call_id:e.payload.call_id,source_line:orig?.ordinal,exported_ordinal:e.ordinal,exact_full_event_semantics_except_added_ordinal:JSON.stringify(copy)===JSON.stringify(orig?.parsed)};
 });
 const call=matches.find(x=>x.parsed.payload.type==='custom_tool_call').parsed;
 const response=matches.find(x=>x.parsed.payload.type==='custom_tool_call_output').parsed;
 const actualRaw=response.payload.output.find(x=>x.text?.length===17182)?.text;
 if(typeof actualRaw!=='string')throw new Error('Could not identify original17182-char native result block');
 const rawBytes=Buffer.from(actualRaw,'utf8'),native=JSON.parse(actualRaw);
 const data={checked_at:new Date().toISOString(),call_id:recovery.original_call_id,original_call_at:call.timestamp,original_result_at:response.timestamp,source_session:recovery.source_session,exact_event_checks:sameEvents,call_is_original_search_service_invocation:call.payload.input.includes('tools.mcp__codex_apps__search_service_web_run'),original_search_queries:['site.nasa.gov space station 98 percent water recovery June 2023','site.nasa.gov station first crew November 2 2000 Zarya November 20 1998 Unity December 1998 exercise 2 hours'],original_result_character_count:actualRaw.length,original_utf8_bytes:rawBytes.length,recovered_utf8_bytes:saved.length,recovered_equals_original_native_output_bytes:saved.equals(rawBytes),recovered_sha256:sha(saved),source_native_text_sha256:sha(rawBytes),recovery_record_hash_matches:sha(saved)===recovery.result_sha256,native_json_top_level_keys:Object.keys(native),new_search_or_http:false,network_internal_requests:recovery.network_internal_requests,limitations:['Exported selected call/output events add ordinal as source-line metadata; excluding this added field, original source event JSON semantics match exactly.','Byte verification applies to recovered native result text, not a new search or reconstruction.','No native internal HTTP count, network byte count or billing measurement was supplied.']};
 if(!data.recovered_equals_original_native_output_bytes||!data.recovery_record_hash_matches||sameEvents.some(x=>!x.exact_full_event_semantics_except_added_ordinal))throw new Error('Recovery verification failed');
 fs.writeFileSync(path.join(__dirname,'recovery-byte-verification-v001.json'),JSON.stringify(data,null,2),{flag:'wx'});
 console.log(JSON.stringify(data));
})();
