const fs=require('node:fs'),path=require('node:path');
const {output}=JSON.parse(fs.readFileSync('tmp/conversation-export/latest-export.json'));
const manifest=JSON.parse(fs.readFileSync(path.join(output,'manifest.json')));
const report=JSON.parse(fs.readFileSync(path.join(__dirname,'ccusage-sessions.json')));
const fields=['input_tokens','cached_input_tokens','output_tokens','reasoning_output_tokens','total_tokens'];
const all=new Map(),results=[];
for(const t of manifest.threads){
  const own=new Map();let lastThreadUsage=null,compacted=0,compactionIds=[];
  for(const line of fs.readFileSync(path.join(output,t.raw_path),'utf8').split('\n')){
    if(!line.trim())continue;
    const r=JSON.parse(line),p=r.payload||{};
    if(r.type==='compacted'&&(t.subagent_history_start_ordinal===null||r.ordinal>=t.subagent_history_start_ordinal)){compacted++;compactionIds.push(p.response_id);}
    if(r.type==='token_usage_record'&&p.thread_id===t.id&&p.usage){
      if(!p.response_id)throw Error('Record without response ID');
      const prior=all.get(p.response_id);
      if(prior&&JSON.stringify(prior.usage)!==JSON.stringify(p.usage))throw Error('Conflicting usage for '+p.response_id);
      all.set(p.response_id,{thread_id:p.thread_id,usage:p.usage});
      own.set(p.response_id,p.usage);lastThreadUsage=p.thread_token_usage;
    }
  }
  const sums=Object.fromEntries(fields.map(k=>[k,[...own.values()].reduce((n,u)=>n+(u[k]||0),0)]));
  const cc=report.sessions.filter(s=>s.sessionId.endsWith(t.id)||s.sessionId.endsWith(t.id+'.jsonl'));
  if(cc.length!==1)throw Error('Expected one matching ccusage session for '+t.id+': '+cc.length);
  results.push({id:t.id,parent_thread_id:t.parent_thread_id,agent_path:t.agent_path,own_unique_response_records:own.size,own_record_sum:sums,last_thread_token_usage:lastThreadUsage,ccusage_total_tokens:cc[0].totalTokens,ccusage_input_including_cache:cc[0].inputTokens+cc[0].cacheReadTokens+cc[0].cacheCreationTokens,ccusage_output_tokens:cc[0].outputTokens,ccusage_minus_response_sum:cc[0].totalTokens-sums.total_tokens,own_compactions:compacted,compaction_response_ids:compactionIds});
}
const summary={version:'20.0.26',scope:'31 explicitly requested threads; per-response records restricted to owning thread_id, deduplicated by response_id; raw snapshot used as reference; ccusage run against live local logs',checked_at:new Date().toISOString(),threads:results.length,unique_response_records:all.size,response_record_tokens:[...all.values()].reduce((n,r)=>n+r.usage.total_tokens,0),ccusage_tokens:results.reduce((n,r)=>n+r.ccusage_total_tokens,0),matching_threads:results.filter(r=>r.ccusage_minus_response_sum===0).length,differing_threads:results.filter(r=>r.ccusage_minus_response_sum!==0).length};
fs.writeFileSync(path.join(__dirname,'comparison.json'),JSON.stringify({summary,threads:results},null,2));
console.log(JSON.stringify({summary,differences:results.filter(r=>r.ccusage_minus_response_sum!==0).map(r=>({id:r.id,reference:r.own_record_sum.total_tokens,ccusage:r.ccusage_total_tokens,delta:r.ccusage_minus_response_sum,compactions:r.own_compactions})),main:results[0]},null,2));
