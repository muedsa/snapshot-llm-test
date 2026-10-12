'use strict';
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../../..');
const s=require(path.join(root,'tmp/20261002-204314-6f31/_suite/suite.cjs'));
const map=JSON.parse(fs.readFileSync(path.join(__dirname,'text-map-final-draft-v004.json'),'utf8'));
const glyph=JSON.parse(fs.readFileSync(path.join(__dirname,'final-glyph-measure-v002.json'),'utf8'));
const views=s.countsFor('A11').views;
const sha=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
map.status='reviewed';
map.reviewed_by='root and invoice_producer; independent reviewer additional evidence retained in independent-analysis';
map.actual_whole_page_view_ids=['A11-view-000009','A11-view-000007'];
map.final_actual_glyph_margin_audit=glyph;
map.footer_glyph_measurement_scope='Final p01v002 and p02v001 original PNGs both measured. Actual ink/decorative foreground margins [64,64,64,58]px, all >=48. Layout box caveat remains separate.';
for(const p of map.final_page_versions){
  const meta=JSON.parse(fs.readFileSync(p.render_meta,'utf8'));
  p.root_actual_view_id=p.page===1?'A11-view-000009':'A11-view-000007';
  const view=views.find(v=>v.id===p.root_actual_view_id);
  if(!view||view.reviewer!=='root'||view.version_id!==p.version_id||view.sha256!==meta.response_sha256)throw new Error('Missing or mismatched root final view evidence');
  p.original_png=meta.image_path;
  p.original_dsl=meta.dsl_path;
  p.png_sha256=sha(meta.image_path);
  p.dsl_sha256=sha(meta.dsl_path);
  p.actual_root_viewed_at=view.viewed_at;
}
map.text_entry_count=map.text_entries.length;
fs.writeFileSync(path.join(__dirname,'text-map-reviewed-v005.json'),JSON.stringify(map,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({path:path.join(__dirname,'text-map-reviewed-v005.json'),entry_count:map.text_entries.length,status:map.status,root_views:map.actual_whole_page_view_ids,glyph_margins:[64,64,64,58],production_finished_writing:true}));
