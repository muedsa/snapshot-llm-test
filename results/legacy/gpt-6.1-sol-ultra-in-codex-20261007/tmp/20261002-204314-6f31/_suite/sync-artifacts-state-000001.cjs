const s=require('./suite.cjs');
s.checkpoint('sync-current-artifact-evidence',{purpose:'Attach existing registered final objects to current state; zero new images/requests/views.'},state=>{for(const task of state.tasks){task.artifacts=s.countsFor(task.id).finals;}});
s.aggregate();console.log(s.readState().last_checkpoint);
