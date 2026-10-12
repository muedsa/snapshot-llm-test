// Root-only orchestration after all images, data and supplied report were actually reviewed.
// Each dependency is checked before the next mutation. No render/view or inferred quality.
const fs=require('node:fs'),path=require('node:path'),cp=require('node:child_process'),s=require('./suite.cjs');
const [task,round,manifest]=process.argv.slice(2);
if(!task||!/^round-\d{2}$/.test(round)||!manifest)throw Error('TASK round-XX manifest.json required');
const d=s.taskDirs(task),rd=path.join(d.temp,round);fs.mkdirSync(rd,{recursive:true});
const seq=String(fs.readdirSync(rd).filter(f=>/^round-orchestration-\d+\.json$/.test(f)).length+1).padStart(6,'0');
const record={task_id:task,round_id:round,started_at:new Date().toISOString(),stages:[],scope:'Root invokes only after genuine visual and content review; no automated quality inference.'};
function run(script,args){const raw=cp.execFileSync(process.execPath,[path.join(__dirname,script),...args],{encoding:'utf8'});return JSON.parse(raw);}
try {
  const publication=run('publish-reviewed-set.cjs',[task,path.resolve(manifest)]);
  record.stages.push({stage:'publication',result:publication});
  if(!publication.published)throw Error('Publication did not succeed');
  s.taskCheckpoint(task,{event_type:'round-completed',round_id:round,artifacts:s.countsFor(task).finals,resume_notes:round+'已完成实际图与内容审查，全部产物发布，正在归档真实轮指标。'});
  const archive=run('archive-round-metrics.cjs',[task,round]);record.stages.push({stage:'archive',result:archive});
  if(!archive.archived)throw Error('Round archive did not succeed');
  s.taskCheckpoint(task,{event_type:'round-archive-verified',round_id:round,completed_rounds:[round],resume_notes:round+'真实wx指标归档通过；旧轮保留。'});
  const rounds=s.readState().tasks.find(t=>t.id===task).completed_rounds.map(r=>JSON.parse(fs.readFileSync(path.join(d.output,r,'task-metrics.json'),'utf8')));
  s.writeTaskMetrics(task,{rounds});s.aggregate();record.succeeded=true;
} catch(e) {record.succeeded=false;record.error=String(e.stack??e);throw e;}
finally {record.ended_at=new Date().toISOString();fs.writeFileSync(path.join(rd,'round-orchestration-'+seq+'.json'),JSON.stringify(record,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify({task,round,succeeded:record.succeeded,record:path.join(rd,'round-orchestration-'+seq+'.json')}));}
