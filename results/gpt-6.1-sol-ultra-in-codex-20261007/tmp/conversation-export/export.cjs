const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const readline = require('node:readline');
const ids = `01a0fca2-9a0b-7a53-b717-67ce19406743
01a114aa-dd46-7b21-8f26-1ef178ce5538
01a1148c-4284-78c3-920c-ae7ea293ac61
01a1148c-1407-7c13-b642-528fab32b607
01a1148b-e7aa-7b03-8608-b899706cc2c1
01a110dc-73be-7da0-b555-c830bbda4bdd
01a110dc-3cff-7560-99e4-3dabfa7f373e
01a110da-ac4e-7ba2-8f80-6cdbe080d79b
01a10fa3-db54-79f2-8691-6e3ef2366125
01a10fa3-b2ea-75a0-a209-1a04744ac190
01a10fa3-8e3f-7601-8df1-9c7e2d2ec425
01a10c0e-f547-7322-a587-971a1a6270eb
01a10bee-e612-79a1-9426-af6b99da012f
01a10be5-39b3-7613-a61c-f60eab45522d
01a10997-ec79-72b2-8518-ec508e8bbaba
01a10992-6e01-7441-84a7-25b499f0b573
01a10991-cd2b-7063-8853-35143c1da2a8
01a10991-2564-77e3-99d5-38c4b4eb2059
01a1098b-e5e9-7db0-8842-602d6c06d67d
01a107c0-5e2f-7da1-a896-c160ee30d2ed
01a107c0-05aa-70e3-a5f6-61b06555ae90
01a107bf-b11e-7d00-bf56-ef1709c5676c
01a1057d-b348-7380-8ae7-c378e82bb161
01a1056e-dcde-7de0-88c2-1bcfa2201a85
01a10566-7aba-74a3-b88e-74dabe9f5ddd
01a102b6-a931-7ab3-bb4d-e6e9530cdc22
01a102b6-7a8c-7070-9fda-98578da2eafc
01a102b4-4b43-7361-aafa-c522cfe39ed3
01a0fca6-1b9f-7382-a2df-e8eba93ff9eb
01a0fca4-acf4-7640-a4c5-d40f63faacf7
01a0fca4-87af-7082-8993-3eb26cb9d0b5`.split('\n');
const codex = 'C:/Users/mueds/.codex';
const stamp = new Date().toISOString().replace(/[-:]/g,'').replace(/\..*/, '').replace('T','-');
const output = path.resolve('exports', `conversations-${stamp}-${crypto.randomBytes(2).toString('hex')}`);
const sources = new Map(ids.map(id => [id, []]));
function walk(dir) {
  if (!fs.existsSync(dir)) return;
  for (const e of fs.readdirSync(dir, {withFileTypes:true})) {
    const p = path.join(dir,e.name);
    if(e.isDirectory()) walk(p);
    else if(e.name.endsWith('.jsonl')) for(const id of ids) if(e.name.includes(id)) sources.get(id).push(p);
  }
}
walk(path.join(codex,'sessions')); walk(path.join(codex,'archived_sessions'));
for (const [id,files] of sources) if(files.length!==1) throw Error(`${id}: expected one source; found ${files.length}`);
fs.mkdirSync(path.join(output,'raw'),{recursive:true});
fs.mkdirSync(path.join(output,'markdown'),{recursive:true});
const names = new Map();
for(const line of fs.readFileSync(path.join(codex,'session_index.jsonl'),'utf8').split('\n')) {
  if(!line.trim()) continue;
  try {const r=JSON.parse(line); if(sources.has(r.id)) names.set(r.id,r.thread_name);}catch{}
}
function digest(p) {return crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');}
function fence(s,lang='') {
  s = typeof s==='string' ? s : JSON.stringify(s,null,2);
  const longest=Math.max(2,...Array.from(s.matchAll(/`+/g),m=>m[0].length));
  const ticks='`'.repeat(longest+1); return `${ticks}${lang}\n${s}\n${ticks}\n\n`;
}
function contentText(content) {
  if(typeof content==='string') return content;
  if(!Array.isArray(content)) return JSON.stringify(content??'',null,2);
  return content.map(c=>c.text??(c.type==='input_image'||c.type==='image' ? '[图像内容见同会话原始 JSONL；阅读版不复制 Base64 数据。]' : c.type==='encrypted_content' ? '' : `[${c.type} 内容见原始 JSONL]`)).filter(Boolean).join('\n\n');
}
async function main() {
  const manifest={schema_version:1,root_thread_id:ids[0],requested_thread_ids:ids,export_started_at:new Date().toISOString(),source_kind:'local_codex_rollout_jsonl',scope:'Main thread plus exactly the 30 user-specified child threads. Byte-preserving raw snapshots and chronological readable transcripts.',output_dir:output,threads:[],files:[],missing_threads:[]};
  for(const [position,id] of ids.entries()) {
    const source=sources.get(id)[0], before=fs.statSync(source);
    const rawRel=`raw/${id}.jsonl`,mdRel=`markdown/${id}.md`,raw=path.join(output,rawRel),md=path.join(output,mdRel);
    fs.copyFileSync(source,raw,fs.constants.COPYFILE_EXCL);
    const after=fs.statSync(source);
    if(before.size!==after.size||before.mtimeMs!==after.mtimeMs) throw Error(`Source changed during export: ${id}`);
    const recordTypes={},responseTypes={},readableCounts={user:0,assistant:0,agent_message:0,tool_call:0,tool_output:0,compaction:0};
    let meta,records=0,firstTimestamp,lastTimestamp,currentTurn=null,ownSectionStarted=false;
    const fd=fs.openSync(md,'wx');
    const write=s=>fs.writeSync(fd,s);
    for await (const line of readline.createInterface({input:fs.createReadStream(raw),crlfDelay:Infinity})) {
      if(!line.trim()) continue;
      const row=JSON.parse(line);records++; recordTypes[row.type]=(recordTypes[row.type]||0)+1;
      firstTimestamp??=row.timestamp;lastTimestamp=row.timestamp??lastTimestamp;
      const p=row.payload??{};
      if(row.type==='session_meta') {
        // Forked sessions also retain their parent's session_meta as inherited history.
        if(p.id!==id) continue;
        meta=p;
        const title=names.get(id)||(position===0?'执行Snapshot全套30题':`子线程 ${id}`);
        write(`# ${title}\n\n会话 ID：\`${id}\`\n\n父会话：${p.parent_thread_id||'无（主会话）'}\n\nAgent 路径：${p.agent_path||'未记录'}\n\n创建时间（原始 UTC）：${p.timestamp}\n\n[总索引](../index.md) · [原始完整 JSONL](../${rawRel})\n\n本文件按日志顺序呈现用户消息、助手公开回复、线程间消息及工具调用/返回，不截断工具文本。系统环境、底层事件、推理字段和加密内容保留在原始 JSONL，未转写到阅读版。图片 Base64 数据保留在原始文件。\n\n`);
        if(Number.isInteger(p.subagent_history_start_ordinal))write('## 继承的上下文\n\n以下内容来自创建子线程时继承的历史；原始日志保留这些内容。\n\n');
      }
      if(meta&&Number.isInteger(meta.subagent_history_start_ordinal)&&!ownSectionStarted&&row.ordinal>=meta.subagent_history_start_ordinal){write('## 本子线程的执行记录\n\n');ownSectionStarted=true;}
      if(row.type==='event_msg'&&p.type==='task_started')currentTurn=p.turn_id;
      if(row.type==='response_item') {
        responseTypes[p.type]=(responseTypes[p.type]||0)+1;
        const prefix=`时间：${row.timestamp||'未记录'} · 原始行：${records}${currentTurn?` · 轮次：${currentTurn}`:''}\n\n`;
        if(p.type==='message'&&(p.role==='user'||(p.role==='assistant'&&p.channel!=='analysis'))) {
          readableCounts[p.role]++;
          write(`## ${p.role==='user'?'用户':'助手'}${p.phase?` · ${p.phase}`:''}\n\n${prefix}${contentText(p.content)}\n\n`);
        } else if(p.type==='agent_message') {
          readableCounts.agent_message++;
          write(`## 线程间消息：${p.author||'未记录'} → ${p.recipient||'未记录'}\n\n${prefix}${contentText(p.content)}\n\n`);
        } else if(p.type==='function_call'||p.type==='custom_tool_call') {
          readableCounts.tool_call++;
          write(`## 工具调用：${p.namespace?p.namespace+'.':''}${p.name}\n\n${prefix}调用 ID：${p.call_id||p.id||'未记录'}\n\n${fence(p.arguments??p.input??'',p.type==='function_call'?'json':'text')}`);
        } else if(p.type==='function_call_output'||p.type==='custom_tool_call_output') {
          readableCounts.tool_output++;
          // Image/audio payloads remain in the byte-preserved raw snapshot.
          const value=p.output;
          let display=value;
          if(typeof value==='string'&&value.includes('data:image/')) display=value.replace(/data:image\/[a-zA-Z0-9.+-]+;base64,[A-Za-z0-9+/=]+/g,'[Base64 图像见原始 JSONL]');
          if(Array.isArray(value)) display=value.map(c=>c.type==='image'||c.type==='audio'?{type:c.type,note:'完整媒体数据见原始 JSONL'}:c);
          write(`## 工具返回\n\n${prefix}调用 ID：${p.call_id||'未记录'}\n\n${fence(display??'','text')}`);
        }
      } else if(row.type==='compacted') {
        readableCounts.compaction++;
        write(`## 上下文压缩记录\n\n时间：${row.timestamp}\n\n${p.message||'完整压缩记录见原始 JSONL。'}\n\n`);
      }
    }
    fs.closeSync(fd);
    if(!meta)throw Error(`No metadata for ${id}`);
    if(position>0&&!ids.includes(meta.parent_thread_id))throw Error(`Parent is outside requested thread set: ${id}`);
    const rawHash=digest(raw),sourceHash=digest(source);
    if(rawHash!==sourceHash)throw Error(`Copy mismatch: ${id}`);
    manifest.threads.push({id,kind:position===0?'main':'child',title:names.get(id)||null,parent_thread_id:meta.parent_thread_id||null,forked_from_id:meta.forked_from_id||null,subagent_history_start_ordinal:meta.subagent_history_start_ordinal??null,counts_include_inherited_history:true,agent_path:meta.agent_path||null,agent_nickname:meta.agent_nickname||null,source_path:source,source_bytes:before.size,source_mtime:before.mtime.toISOString(),created_at:meta.timestamp,first_record_at:firstTimestamp,last_record_at:lastTimestamp,records,record_types:recordTypes,response_types:responseTypes,readable_counts:readableCounts,raw_path:rawRel,markdown_path:mdRel,raw_sha256:rawHash,raw_copy_verified:true});
    console.log(JSON.stringify({progress:position+1,total:ids.length,id,bytes:before.size,records}));
  }
  manifest.export_completed_at=new Date().toISOString();
  manifest.totals={threads:manifest.threads.length,main_threads:1,child_threads:manifest.threads.length-1,raw_bytes:manifest.threads.reduce((n,t)=>n+t.source_bytes,0),raw_records:manifest.threads.reduce((n,t)=>n+t.records,0),user_messages:manifest.threads.reduce((n,t)=>n+t.readable_counts.user,0),assistant_messages:manifest.threads.reduce((n,t)=>n+t.readable_counts.assistant,0),tool_calls:manifest.threads.reduce((n,t)=>n+t.readable_counts.tool_call,0)};
  const index=['# 会话记录导出','',`主会话：${ids[0]}。共 **31 个会话（1 个主会话、30 个指定子线程）**。`,``,`导出完成时间（UTC）：${manifest.export_completed_at}`,'','每个会话同时提供原始 JSONL 和 Markdown 阅读版。原始文件逐字节复制，SHA-256 与源文件一致；阅读版按顺序包含用户、助手、线程间消息和工具调用/返回。日志中的图片数据保留在原始文件中；本导出不包含工作目录生成物或外部媒体文件。所有链接相对本目录，可随压缩包一起移动。','','[导出清单与校验](manifest.json) · [SHA-256 清单](SHA256SUMS.txt)','','|序号|会话 ID|类型 / Agent 路径|阅读版|原始日志|记录数|','|---:|---|---|---|---|---:|'];
  manifest.threads.forEach((t,i)=>index.push(`|${i+1}|${t.id}|${t.kind==='main'?'主会话':t.agent_path||'子线程'}|[Markdown](${t.markdown_path})|[JSONL](${t.raw_path})|${t.records}|`));
  fs.writeFileSync(path.join(output,'index.md'),index.join('\n')+'\n',{flag:'wx'});
  fs.copyFileSync(__filename,path.join(output,'export-script.cjs'),fs.constants.COPYFILE_EXCL);
  for(const rel of ['index.md','export-script.cjs',...manifest.threads.flatMap(t=>[t.raw_path,t.markdown_path])]) {
    const p=path.join(output,rel);manifest.files.push({path:rel,bytes:fs.statSync(p).size,sha256:digest(p)});
  }
  fs.writeFileSync(path.join(output,'manifest.json'),JSON.stringify(manifest,null,2)+'\n',{flag:'wx'});
  fs.writeFileSync(path.join(output,'SHA256SUMS.txt'),[...manifest.files.map(f=>`${f.sha256}  ${f.path}`),`${digest(path.join(output,'manifest.json'))}  manifest.json`].join('\n')+'\n',{flag:'wx'});
  fs.writeFileSync(path.join(__dirname,'latest-export.json'),JSON.stringify({output,totals:manifest.totals},null,2));
  console.log(JSON.stringify({output,totals:manifest.totals,all_sources_verified:true}));
}
main().catch(e=>{console.error(e);process.exitCode=1;});
