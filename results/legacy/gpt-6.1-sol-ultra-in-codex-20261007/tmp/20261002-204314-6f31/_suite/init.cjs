const fs = require('fs');
const path = require('path');
const root = process.cwd();
const run = '20261002-204314-6f31';
const config = JSON.parse(fs.readFileSync('run-config.json','utf8').replace(/^\uFEFF/,''));
const catalog = JSON.parse(fs.readFileSync('catalog.json','utf8').replace(/^\uFEFF/,''));
const state = JSON.parse(fs.readFileSync('templates/suite-state-template.json','utf8').replace(/^\uFEFF/,''));
const out = path.resolve(root,config.output_root,run);
const temp = path.resolve(root,config.temp_root,run);
for(const id of ['_suite',...catalog.task_order]) {
  fs.mkdirSync(path.join(out,id),{recursive:true});
  fs.mkdirSync(path.join(temp,id),{recursive:true});
}
fs.mkdirSync(path.join(temp,'_suite','checkpoints'),{recursive:true});
const now = new Date().toISOString();
Object.assign(state,{run_id:run,profile:'all',status:'in_progress',started_at:now,updated_at:now,current_task:'A01',last_checkpoint:path.join(temp,'_suite','checkpoints','state-000001.json')});
for(const t of state.tasks) Object.assign(t,{output_dir:path.join(out,t.id),temp_dir:path.join(temp,t.id)});
Object.assign(state.tasks[0],{status:'in_progress',started_at:now,resume_notes:'Read all root entrance files and A01 TASK.md, AGENTS.md, task.json, monthly.csv. Shared service/DSL preparation follows.'});
const serial = JSON.stringify(state,null,2)+'\n';
fs.writeFileSync(path.join(out,'_suite','suite-state.json'),serial,{flag:'wx'});
fs.writeFileSync(state.last_checkpoint,serial,{flag:'wx'});
fs.appendFileSync(path.join(temp,'_suite','events.jsonl'),JSON.stringify({id:'shared-event-000001',time:now,type:'run-start',run_id:run,profile:'all',current_task:'A01'})+'\n');
for(const f of ['AGENTS.md','TASKS.md','catalog.json','run-config.json']) fs.copyFileSync(f,path.join(temp,'_suite','input-'+f));
fs.writeFileSync(path.join(out,'_suite','index.md'),'# Snapshot suite '+run+'\n\nStatus: in progress. All 30 tasks authorized, sequential.\n\n'+state.tasks.map(t=>'- '+t.id+': '+t.status+' | output: '+t.output_dir+' | temp: '+t.temp_dir).join('\n')+'\n');
console.log(JSON.stringify({run_id:run,output_root:out,temp_root:temp,checkpoint:state.last_checkpoint}));
