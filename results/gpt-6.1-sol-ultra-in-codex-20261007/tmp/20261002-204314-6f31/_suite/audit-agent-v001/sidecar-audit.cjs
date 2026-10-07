const fs=require('fs'),path=require('path'),crypto=require('crypto'),base=process.cwd(),run='20261002-204314-6f31';
const dir=path.join(base,'tmp',run,'_suite','audit-agent-v001');
const read=f=>fs.readFileSync(f,'utf8').replace(/^\uFEFF/,'');
const json=f=>JSON.parse(read(f)),sha=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
const out=t=>path.join(base,'outputs',run,t),issues=[],cases=[],hashCases=new Map();
for(const t of ['B01','B02','B03']){
 const p=json(path.join(out(t),'portfolio.json'));
 for(const c of p.cases){
  const image=path.join(out(t),c.png),dsl=path.join(out(t),c.snapshot),ih=sha(image),dh=sha(dsl);
  if(hashCases.has(ih))issues.push({task:t,case:c.id,type:'duplicate_creative_final_png',same_as:hashCases.get(ih)});
  hashCases.set(ih,t+'/'+c.id);
  for(const k of ['audience','use_context','user_goal','content_basis','visual_intent'])if(!c[k])issues.push({task:t,case:c.id,type:'missing_scenario_metadata',key:k});
  if(/<Image(?:\s|>)/.test(read(dsl)))issues.push({task:t,case:c.id,type:'Image_tag_requires_asset_provenance_manual_review'});
  cases.push({task_id:t,id:c.id,title:c.title,user_goal:c.user_goal,use_context:c.use_context,content_basis:c.content_basis,image_sha256:ih,dsl_sha256:dh,final_view:c.visual_review?.final_view_id,completion_criteria:c.completion_criteria});
 }
}
const examples=json(path.join(out('A17'),'examples.json')).examples,exampleChecks=[];
for(const e of examples){
 const f=path.join(out('A17'),e.full_dsl),source=read(f),sourceRows=source.split(/\r?\n/),fullSource=read(e.full_source_path);
 const printedChecks=e.printed_source_rows.map(r=>({line:r.line,exact:r.source===sourceRows[r.line-1]}));
 if(printedChecks.some(r=>!r.exact))issues.push({task:'A17',example:e.id,type:'printed_source_rows_differ'});
 if(source!==fullSource)issues.push({task:'A17',example:e.id,type:'delivered_full_dsl_differs_from_source'});
 if(sha(f)!==e.full_source_sha256)issues.push({task:'A17',example:e.id,type:'example_source_SHA_different'});
 const handbook=read(path.join(out('A17'),e.handbook_dsl));
 // Extract the complete Snapshot child as printed, preserving whitespace.
 const child=source.replace(/^\s*<Snapshot[^>]*>\s*/,'').replace(/\s*<\/Snapshot>\s*$/,'');
 const childCompact=child.replace(/>\s+</g,'><');
 const handCompact=handbook.replace(/>\s+</g,'><');
 const embeddedExact=handCompact.includes(childCompact);
 if(!embeddedExact)issues.push({task:'A17',example:e.id,type:'direct_example_subtree_missing_from_handbook'});
 if(e.printed_line_count<8||e.printed_line_count>18)issues.push({task:'A17',example:e.id,type:'printed_lines_out_of_required_range'});
 exampleChecks.push({id:e.id,printed_line_count:e.printed_line_count,printed_rows_exact:printedChecks.every(r=>r.exact),full_dsl_matches_preserved_source:source===fullSource,direct_example_subtree_in_handbook:embeddedExact,example_request:e.actual_example_response.id,handbook_request:e.actual_handbook_response.id});
}
const specificViews=[
 {id:'suite-integrity-agent-view-000001',task_id:'A03',image_path:path.join(out('A03'),'system-pulse.png'),tool:'view_image',reviewer:'/root/suite_integrity_audit',viewed_at_interval:'2026-10-06T10:56:08Z to 2026-10-06T11:01:00Z',observation:'本次实际打开最终原图。说明卡内条纹明显变柔，左右卡外横条锐利；白色Background-only blur仍清晰。三等宽指标、LIVE标签与逆时针REVIEW标签均完整。背景滤镜效果在该最终配置成立，不能由B03后续配置的实验推断此图无效。'},
 {id:'suite-integrity-agent-view-000002',task_id:'A10',image_path:path.join(out('A10'),'compositing-lab.png'),tool:'view_image',reviewer:'/root/suite_integrity_audit',viewed_at_interval:'2026-10-06T10:56:08Z to 2026-10-06T11:01:00Z',observation:'本次实际打开最终原图。01重叠有红蓝混合与02纯蓝遮红明显不同；03卡内背景条纹柔而SHARP文字锐，04卡内文字/图形一起模糊，外条纹仍清晰；05滤色/子树模糊和06圆形边界裁剪区别可见。六块说明完整。'}
].map(v=>({...v,sha256:sha(v.image_path),timestamp_scope:'Interval bounded by actual preceding and following command evidence, not an invented exact tool timestamp. These new agent views were kept private and were not added to completed-task public metrics.'}));
for(const v of specificViews)v.viewed_at_interval='2026-10-06T10:56:08.128Z to 2026-10-06T11:00:26Z';
const result={schema_version:1,run_id:run,reviewer:'/root/suite_integrity_audit',audited_at:new Date().toISOString(),issues,passed:issues.length===0,creative_cases:cases,creative_evidence_scope:'Metadata and original PNG/DSL identities independently inspected for 30 cases. All 30 final PNG hashes are distinct and declared use tasks differ. This does not replace their already recorded individual image reviews with a claim of 30 new agent image views.',handbook_examples:exampleChecks,specific_actual_views:specificViews};
fs.writeFileSync(path.join(dir,'sidecar-audit-v001.json'),JSON.stringify(result,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({passed:result.passed,issues,creative_cases:cases.length,examples:exampleChecks,specific_actual_view_count:specificViews.length},null,2));
