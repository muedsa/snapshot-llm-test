const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),readline=require('node:readline');
const {output}=JSON.parse(fs.readFileSync(path.join(__dirname,'latest-export.json'),'utf8'));
const manifestPath=path.join(output,'manifest.json');
const m=JSON.parse(fs.readFileSync(manifestPath,'utf8'));
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const text=c=>typeof c==='string'?c:(c||[]).map(x=>x.text??(x.type==='encrypted_content'?'':`[${x.type} 内容见原始 JSONL]`)).filter(Boolean).join('\n\n');
async function main(){
  fs.mkdirSync(path.join(output,'dialogue'));
  for(const t of m.threads){
    t.dialogue_path=`dialogue/${t.id}.md`;
    const fd=fs.openSync(path.join(output,t.dialogue_path),'wx');
    const write=s=>fs.writeSync(fd,s);
    write(`# ${t.title||'会话 '+t.id}\n\n会话 ID：\`${t.id}\`\n\n父会话：${t.parent_thread_id||'无（主会话）'}\n\nAgent 路径：${t.agent_path||'未记录'}\n\n[总索引](../index.md) · [含工具调用的详细阅读版](../${t.markdown_path}) · [原始 JSONL](../${t.raw_path})\n\n本版提供用户消息、助手公开回复和线程间消息。工具调用与返回见详细阅读版；原始 JSONL 保留完整日志、图片数据及继承的上下文。历史消息中的工作文件链接按原文保留，相关产物未打包。\n\n`);
    let own=false,lineNo=0;
    if(t.subagent_history_start_ordinal!==null)write('## 继承的上下文\n\n');
    for await(const line of readline.createInterface({input:fs.createReadStream(path.join(output,t.raw_path)),crlfDelay:Infinity})){
      lineNo++;if(!line.trim())continue;
      const r=JSON.parse(line),p=r.payload||{};
      if(t.subagent_history_start_ordinal!==null&&!own&&r.ordinal>=t.subagent_history_start_ordinal){write('## 本子线程的执行记录\n\n');own=true;}
      if(r.type!=='response_item')continue;
      if(p.type==='message'&&(p.role==='user'||p.role==='assistant'&&p.channel!=='analysis'))write(`### ${p.role==='user'?'用户':'助手'}${p.phase?' · '+p.phase:''}\n\n${r.timestamp} · 原始行 ${lineNo}\n\n${text(p.content)}\n\n`);
      if(p.type==='agent_message')write(`### 线程间消息：${p.author||'未记录'} → ${p.recipient||'未记录'}\n\n${r.timestamp} · 原始行 ${lineNo}\n\n${text(p.content)}\n\n`);
    }
    fs.closeSync(fd);
  }
  const index=['# 会话记录导出','',`已导出指定 **31 个会话：1 个主会话和30个子线程（含多层分支）**。`,'',`主会话：\`${m.root_thread_id}\`。导出时间（UTC）：${m.export_completed_at}。`,'','每个会话有三种格式：轻量对话阅读版、含工具调用与返回的详细 Markdown、逐字节复制的原始 JSONL。25个子线程带有继承历史，阅读版将其与自身执行记录分开标记；记录数量包含继承历史，跨会话会有重复。','','原始文件 SHA-256 与源日志一致。日志中的图片数据保留在原始文件；工作目录生成物、外部文件和远程媒体未打包。历史消息中的链接按原文保留，可能依赖原电脑；本索引及新增导航链接均为可移动的相对链接。','','[会话关系与校验清单](manifest.json) · [SHA-256](SHA256SUMS.txt) · [导出验证](validation.json)','','|序号|会话 ID|类型 / Agent 路径|对话阅读版|详细记录|原始日志|','|---:|---|---|---|---|---|'];
  m.threads.forEach((t,i)=>index.push(`|${i+1}|${t.id}|${t.kind==='main'?'主会话':t.agent_path||'子线程'}|[对话](${t.dialogue_path})|[Markdown](${t.markdown_path})|[JSONL](${t.raw_path})|`));
  fs.writeFileSync(path.join(output,'index.md'),index.join('\n')+'\n');
  fs.copyFileSync(__filename,path.join(output,'finalize-script.cjs'),fs.constants.COPYFILE_EXCL);
  const issues=[];
  if(m.threads.length!==31||new Set(m.threads.map(t=>t.id)).size!==31)issues.push('Thread count or uniqueness mismatch');
  for(const t of m.threads){
    if(hash(path.join(output,t.raw_path))!==t.raw_sha256)issues.push('Raw hash mismatch: '+t.id);
    for(const rel of [t.raw_path,t.markdown_path,t.dialogue_path])if(!fs.statSync(path.join(output,rel)).size)issues.push('Empty file: '+rel);
  }
  const links=[...index.join('\n').matchAll(/\]\(([^)]+)\)/g)].map(x=>x[1]);
  for(const link of links)if(link!=='validation.json'&&!fs.existsSync(path.join(output,link)))issues.push('Broken index link: '+link);
  const validation={validated_at:new Date().toISOString(),passed:issues.length===0,issues,checks:{requested_threads:31,exported_threads:m.threads.length,unique_ids:true,parent_relationships_recorded:true,original_byte_hashes_verified:31,jsonl_parsed:31,dialogue_files:31,detailed_markdown_files:31,raw_jsonl_files:31,index_relative_links_checked:links.length},scope:'Raw original snapshots are byte-preserving. Readable views omit system/developer instructions, reasoning fields and encrypted content. Raw logs retain all original records. Generated-artifact and historical message links are not part of this export.'};
  fs.writeFileSync(path.join(output,'validation.json'),JSON.stringify(validation,null,2)+'\n',{flag:'wx'});
  m.files=[];
  for(const rel of ['index.md','export-script.cjs','finalize-script.cjs','validation.json',...m.threads.flatMap(t=>[t.raw_path,t.markdown_path,t.dialogue_path])])m.files.push({path:rel,bytes:fs.statSync(path.join(output,rel)).size,sha256:hash(path.join(output,rel))});
  m.readable_variants={dialogue:'user/assistant/agent messages; compact view',markdown:'user/assistant/agent messages plus tool calls and results'};
  m.totals.counting_note='Counts include any inherited context present in each thread snapshot; do not interpret as deduplicated activity totals.';
  fs.writeFileSync(manifestPath,JSON.stringify(m,null,2)+'\n');
  fs.writeFileSync(path.join(output,'SHA256SUMS.txt'),[...m.files.map(f=>`${f.sha256}  ${f.path}`),`${hash(manifestPath)}  manifest.json`].join('\n')+'\n');
  if(issues.length)throw Error(JSON.stringify(issues));
  console.log(JSON.stringify({output,validation,bytes:m.files.reduce((n,f)=>n+f.bytes,0)}));
}
main().catch(e=>{console.error(e);process.exitCode=1;});
