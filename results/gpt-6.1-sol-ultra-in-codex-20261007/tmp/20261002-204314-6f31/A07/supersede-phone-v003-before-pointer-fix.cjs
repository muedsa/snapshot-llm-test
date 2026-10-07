// Preserve formerly accepted output files before updating the named deliverable.
const fs=require('node:fs'),path=require('node:path'),s=require('../_suite/suite.cjs');
const d=s.taskDirs('A07'),version=s.countsFor('A07').versions.find(v=>v.id==='A07-travel-v003');
if(!version)throw Error('Real v003 version required');
const req=s.countsFor('A07').requests.find(r=>r.body_sha256===version.sha256&&r.ok);
if(!req)throw Error('Real successful v003 response required');
const meta=path.join(path.dirname(req.request_file),'render-result.json');
const old=s.countsFor('A07').finals.find(a=>path.basename(a.image_path)==='travel-card.png');
if(old.version_id!=='A07-travel-v002')throw Error('Expected current v002');
const archive=path.join(d.temp,'superseded-finals','travel-v002');
fs.mkdirSync(archive,{recursive:true});
for(const [field,suffix,hash] of [['image_path','.png',old.image_sha256],['dsl_path','.snapshot',old.dsl_sha256]]){
 const src=old[field],dest=path.join(archive,'travel-card'+suffix);
 if(fs.existsSync(dest))throw Error('Archive exists; resume inspection required, do not overwrite');
 if(s.sha256(fs.readFileSync(src))!==hash)throw Error('Current output identity mismatch');
 fs.renameSync(src,dest);
 if(s.sha256(fs.readFileSync(dest))!==hash)throw Error('Archive identity mismatch');
}
const next=s.acceptFinal('A07','travel-card',meta,{title:'澄川 · 三线出行旅行卡（无障碍语义已明确）',supersedes_artifact_id:old.id,superseded_files:archive});
fs.writeFileSync(path.join(archive,'supersession.json'),JSON.stringify({time:new Date().toISOString(),reason:'Orange Q2 warning explicitly scoped to accessible travel; ordinary S05 transfer remains valid.',previous:old,preserved_original_image:path.join(archive,'travel-card.png'),preserved_original_dsl:path.join(archive,'travel-card.snapshot'),current:next,no_original_response_or_version_overwritten:true},null,2)+'\n',{flag:'wx'});
s.taskCheckpoint('A07',{artifacts:s.countsFor('A07').finals,unresolved_issues:[],resume_notes:'Phone ambiguous scope corrected by real v003; former accepted output PNG/DSL preserved with hashes in superseded-finals. Root final true v003 review pending.'});
s.writeTaskMetrics('A07');s.aggregate();
console.log(JSON.stringify({new:next,archive,meta}));
