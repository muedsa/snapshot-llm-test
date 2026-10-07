// Copies source evidence without changing task bank. Use only for the current task.
const fs=require('fs'),path=require('path'),s=require('./suite.cjs');
const [id]=process.argv.slice(2);const suite=s.createSuite();const meta=suite.catalog.tasks.find(x=>x.id===id);if(!meta)throw new Error('Unknown task');
const d=s.taskDirs(id),base=path.join(d.temp,'source-evidence');fs.mkdirSync(base,{recursive:true});
let n=fs.readdirSync(base).filter(x=>x.startsWith('read-')).length+1;const target=path.join(base,'read-'+String(n).padStart(6,'0'));fs.mkdirSync(target);
const files=['TASK.md','AGENTS.md','task.json','run-config.json'];const records=[];const transcript=[];
for(const f of files){const src=path.resolve(meta.directory,f),bytes=fs.readFileSync(src);fs.writeFileSync(path.join(target,f),bytes,{flag:'wx'});records.push({file:src,bytes:bytes.length,sha256:s.sha256(bytes)});transcript.push('\nFILE '+src+'\n'+bytes.toString('utf8'));}
const inputs=JSON.parse(fs.readFileSync(path.join(meta.directory,'task.json'),'utf8').replace(/^\uFEFF/,'')).inputs||[];
for(const f of inputs){const src=path.resolve(meta.directory,f),bytes=fs.readFileSync(src);records.push({file:src,bytes:bytes.length,sha256:s.sha256(bytes),role:'task-input'});if(/\.(json|csv|tsv|md|snapshot|txt)$/i.test(f)){const dest=path.join(target,f);fs.mkdirSync(path.dirname(dest),{recursive:true});fs.writeFileSync(dest,bytes,{flag:'wx'});transcript.push('\nINPUT '+src+'\n'+bytes.toString('utf8'));}}
fs.writeFileSync(path.join(target,'source-manifest.json'),JSON.stringify({task_id:id,read_at:new Date().toISOString(),records},null,2),{flag:'wx'});
fs.writeFileSync(path.join(target,'command-output.txt'),transcript.join('\n'),{flag:'wx'});
console.log(transcript.join('\n'));
