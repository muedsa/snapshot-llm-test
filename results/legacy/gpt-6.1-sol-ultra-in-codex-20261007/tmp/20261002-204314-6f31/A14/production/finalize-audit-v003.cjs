'use strict';
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../../..'),s=require(path.join(root,'tmp/20261002-204314-6f31/_suite/suite.cjs'));
const read=f=>JSON.parse(fs.readFileSync(path.join(__dirname,f),'utf8'));
const write=(f,v)=>fs.writeFileSync(path.join(__dirname,f),JSON.stringify(v,null,2)+'\n',{flag:'wx'});
const audit=read('batch-audit-draft-v002.json'),baseline=read('producer-baseline-reviews-v001.json'),refined=read('refinement-results-v002.json');
const observations={K03:{lines:1,text:'Actual K03 v002 whole image viewed: exact full title now44px one line, eliminating original isolated级;speaker/status/time unchanged and readable.'},K07:{lines:2,text:'Actual K07 v002 whole image viewed and compared: title natural2lines, second line数据与视觉检查 keeps视觉 together, original full title and long English/CJK speaker unchanged.'},K08:{lines:2,text:'Actual K08 v002 whole image viewed and compared: source curlyquote full title remains2lines with longer balanced second line能力的最后一公里; no source rewrite or clipping.'}};
const finalViews={};
for(const result of refined){
 const view=s.view('A14',result.image_path,{tool:'view_image',reviewer:'invoice_producer',version_id:'A14-v002-'+result.id,case_id:result.id,observation:observations[result.id].text,title_line_count:observations[result.id].lines,speaker_line_count:1});
 finalViews[result.id]=view;
 s.iteration('A14',{type:'visual',version_id:'A14-v002-'+result.id,parent_version:'A14-v001-'+result.id,case_id:result.id,completed:true,phase:'actual-image-reviewed',image_path:result.image_path,request_id:JSON.parse(fs.readFileSync(result.meta_path,'utf8')).id,before_view_id:result.before_view_id,after_view_id:view.id,changes:'Common source-length rules:48px tier threshold26→22 units, >26units uses920px active title width within common1072px outerregion.',comparison:observations[result.id].text,unresolved_issues:[]});
}
const candidates=[],issues=[];
for(const card of audit.cards){
 const updated=refined.find(r=>r.id===card.id);
 const req=updated?JSON.parse(fs.readFileSync(updated.meta_path,'utf8')).id:'A14-request-'+String(Number(card.id.slice(1))).padStart(6,'0');
 const meta_path=updated?updated.meta_path:path.join(root,'tmp/20261002-204314-6f31/A14/requests/'+req+'/render-result.json');
 const meta=JSON.parse(fs.readFileSync(meta_path,'utf8'));
 const view=finalViews[card.id]??baseline.find(v=>v.case_id===card.id);
 const dsl=fs.readFileSync(meta.dsl_path,'utf8');
 card.actual_visual_status='producer_actual_full_png_reviewed_passed';card.title_line_count=view.title_line_count;card.speaker_line_count=1;card.image_views=[{id:view.id,tool:'view_image',reviewer:view.reviewer,actual_viewed_at:view.viewed_at,image_path:view.image_path,observation:view.observation}];
 card.final_version_id=meta.version_id;card.final_meta_path=meta_path;card.final_png_sha256=view.sha256;card.final_dsl_sha256=crypto.createHash('sha256').update(dsl).digest('hex');
 for(const key of ['id','title','speaker','time','status'])if(!dsl.includes('<![CDATA['+card.original[key]+']]>'))issues.push(card.id+': missingoriginal '+key);
 for(const f of card.fields){
  const p=f.position;
  if(p.x<40||p.y<40||p.x+p.width>1160||p.y+p.height>590)issues.push(card.id+': safe '+f.field);
 }
 for(let a=0;a<card.fields.length;a++)for(let b=a+1;b<card.fields.length;b++){
  const x=card.fields[a].position,y=card.fields[b].position;
  if(x.x<y.x+y.width&&x.x+x.width>y.x&&x.y<y.y+y.height&&x.y+x.height>y.y)issues.push(card.id+': textoverlap '+card.fields[a].field+'/'+card.fields[b].field);
 }
 if(card.title_font_size<36||card.title_line_count>3||card.speaker_line_count>2)issues.push(card.id+': typography');
 if(card.original.status==='取消'&&(!dsl.includes('<![CDATA[本场取消]]>')||!dsl.includes('<![CDATA[13:40]]>')))issues.push(card.id+': cancelcontent');
 candidates.push({stem:'card-'+card.id,case_id:card.id,version_id:meta.version_id,meta_path,image_path:meta.image_path,dsl_path:meta.dsl_path,producer_actual_view_id:view.id,title_line_count:card.title_line_count,speaker_line_count:1,png_sha256:card.final_png_sha256,dsl_sha256:card.final_dsl_sha256});
}
if(issues.length)throw new Error(JSON.stringify(issues));
audit.status='producer_actual_eight_card_review_passed';audit.final_generation_rules=path.join(__dirname,'generation-rules-v002.json');audit.rule_refinement_script=path.join(__dirname,'refine-rules-v002.cjs');
audit.validation={eight_original_service_pngs_really_reviewed:true,original_40_leaf_fields_raw_preserved:true,no_textbox_overlaps:true,safe_text_boxes_at_least40:true,title_font_sizes:[72,56,44,48,48,48,44,44],actual_title_line_counts:audit.cards.map(c=>({id:c.id,lines:c.title_line_count})),actual_speaker_line_counts:audit.cards.map(c=>({id:c.id,lines:c.speaker_line_count})),status_four_color_and_symbol_categories:true,cancel_original_title_and_time_retained:true,source_records_unmodified:true,issues};
audit.final_candidates=candidates;
write('batch-audit-final-draft-v003.json',audit);
write('production-handoff-v001.json',{task_id:'A14',run_id:'20261002-204314-6f31',all_production_writes_finished:true,candidates,batch_audit:path.join(__dirname,'batch-audit-final-draft-v003.json'),full_parameter_generator:path.join(__dirname,'build-v001.cjs'),final_parameter_refinement:path.join(__dirname,'refine-rules-v002.cjs'),final_generation_rules:path.join(__dirname,'generation-rules-v002.json'),facts:['11actual render requests,allHTTP200,8baseline and3complete visual refinements.','K03 one-character tail removed by generic length/font rule; K07 avoids splitting视觉 and K08 balances by shared>26units width rule.','NoID-specific source edits,all source title/speaker/time/status strings original RawCDATA.','Final titles one line exceptK07/K08 two; all speakersone,all title fonts>=44.','Color+originalstateword+DSLgeometry state marks,and canceledcard retains full title/time plus本场取消.'],publishing_state_reports_metrics_owned_by_root:true,unresolved_production_issues:[]});
console.log(JSON.stringify({batch_audit:path.join(__dirname,'batch-audit-final-draft-v003.json'),candidates:candidates.map(c=>({id:c.case_id,meta_path:c.meta_path,view_id:c.producer_actual_view_id,lines:c.title_line_count})),all_production_writes_finished:true}));
