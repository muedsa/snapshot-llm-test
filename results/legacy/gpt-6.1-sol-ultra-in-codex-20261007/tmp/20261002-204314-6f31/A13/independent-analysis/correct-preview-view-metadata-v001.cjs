const fs=require('fs'),path=require('path'),dir=__dirname,t=path.resolve(dir,'..');
const views=fs.readFileSync(path.join(t,'views.jsonl'),'utf8').trim().split(/\r?\n/).map(JSON.parse);
const out=path.join(dir,'view-metadata-corrections-v001.jsonl');
if(fs.existsSync(out))throw Error('Prior correction file exists; preserve it');
const records=['000007','000008','000009','000010'].map((n,index)=>{
 const v=views.find(v=>v.id==='A13-view-'+n);if(!v||v.reviewer!=='a10_audit_resume')throw Error('Expected actual independent view missing');
 const direction=index%2===0?'A':'B';return {id:'A13-view-correction-'+String(index+1).padStart(6,'0'),task_id:'A13',recorded_at:new Date().toISOString(),original_view_id:v.id,original_image_path:v.image_path,original_sha256:v.sha256,original_version_id:v.version_id,correct_version_id:'A13-preview-v001-direction-'+direction,original_is_preview:v.is_preview,correct_is_preview:true,reason:'Metadata was assigned guessed version name instead of actual render-result.version_id; full512 direction images are design previews, not final artifacts. Original real view event and time remain unchanged.',actual_new_visual_call:false,additional_view_count:0};
});
for(const v of records)fs.appendFileSync(out,JSON.stringify(v)+'\n');
console.log(JSON.stringify({written:out,records:records.length,additional_view_calls:0}));
