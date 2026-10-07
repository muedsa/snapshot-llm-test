const s=require('./suite.cjs');
s.checkpoint('resume-current-artifact-deduplication',{purpose:'Correct current state pointer only; helper bug report and verification retained; no artifact/event/history/metric count invented.'},state=>{
 for(const task of state.tasks){
   const ids=new Set(),paths=new Set();
   task.artifacts=(task.artifacts??[]).filter(a=>{if(typeof a!=='object'||a===null)return true;const p=a.image_path?.toLowerCase().replaceAll('\\','/');if((a.id&&ids.has(a.id))||(p&&paths.has(p)))return false;if(a.id)ids.add(a.id);if(p)paths.add(p);return true;});
 }
});
s.writeTaskMetrics('A06');s.aggregate();
console.log(JSON.stringify(s.readState().tasks.slice(0,6).map(t=>({id:t.id,status:t.status,artifacts:t.artifacts.length}))));
