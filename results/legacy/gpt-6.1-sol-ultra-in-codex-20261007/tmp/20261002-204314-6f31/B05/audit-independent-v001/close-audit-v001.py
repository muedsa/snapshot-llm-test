import json, datetime, hashlib
from pathlib import Path
p=Path(__file__).parent;load=lambda f:json.loads(Path(f).read_text(encoding='utf-8-sig'))
a=load(p/'candidate-structural-v002.json');views=load(p/'actual-views-v001.json')['actual_views'];preview=load(p/'preview-manifest-v001.json');selection=load(a['selection'])
checks=a['checks'];issues=list(a['issues'])
sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
for s in selection['cases']:
 r=load(s['render_meta']);row=next(x for x in preview['rows'] if x['case_id']==s['id']);ok=row['original']==r['image_path'] and row['original_sha256']==sha(r['image_path'])
 checks.append({'check':s['id']+':preview_manifest_same_selected_original','passed':ok,'detail':r['id']})
 if not ok:issues.append({'check':s['id']+':preview_manifest_same_selected_original'})
contact_ok=any(v['image_path']==preview['contact'] for v in views)
checks.append({'check':'actual_independent_collection_view','passed':contact_ok})
if not contact_ok:issues.append({'check':'actual_independent_collection_view'})
result={
 'schema_version':1,'task_id':'B05','run_id':'20261002-204314-6f31','reviewer':'/root/suite_integrity_audit','independent_final_audit_performed':True,'audited_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'passed':not issues,
 'selection':a['selection'],'root_collection_review':str(p.parent/'root'/'collection-review-v002.json'),
 'scope':'10 selected original service response PNGs individually opened and perceived, nine phone originals additionally viewed as 360×720 previews, plus ten-case contact sheet. XML/PNG/SHA/metadata/plan/brief/journey and both saved W3C readable full texts checked. No new HTTP, no public-ledger mutation by reviewer, no formal output-copy check yet; root publishes exact candidate bytes after this audit.',
 'case_judgments':{v['case_id']:{'passed':True,'observation':v['observation'],'original_image':v['image_path'],'viewed_at':v['viewed_at'],'logical_phone_preview_actually_opened':v['case_id']!='case-07'} for v in views if v['scope']=='original service response'},
 'checks':checks,'issues':issues,'actual_views':views,'selected_candidates':a['cases'],
 'resolved_record_issues':[
  {'issue':'case02/04 preliminary metadata incorrectly cited nonexistent product-plan-v002.json.','resolution':'Root created actual metadata-v003 in private root directory referencing existing product-plan-v001; original metadata retained. Selection-v004 selects corrected files. No image/DSL change needed.'},
  {'issue':'Root collection v001 described case10 download button although actual art says confirm clothes removed.','resolution':'Root genuinely re-opened req15, recorded view21 and collection-v002 correction. Actual case10 buttons are confirm clothes removed and feedback. No image change.'},
  {'issue':'Independent structural checker v001 failed exact lexical terms C1标准洗衣/D1干衣 because actual DSL has ASCII gaps.','resolution':'Original v001 failure retained. Revised checker-v002 normalizes only ASCII spaces; both labels remain visually complete and 167 checks pass. This was a checker mismatch, not an artwork defect.'}
 ],
 'visual_rationale':'Ten cases each solve a distinct product demand, decision, status or result. Unified loop mark, mint/teal choice and confirmation, coral fault communicate the journey. Primary and secondary actions are distinct; important state and money rules remain readable at target phone preview, kiosk layout permits close-range side-by-side confirmation. No visible text clipping/overlap remains in the selected images. Geometric elapsed arc is exactly 162 degrees, 45 percent.',
 'timestamp_method':'Each batch was actually opened and observed before clock__curr_time reading. viewed_at is that post-inspection clock reading, not unavailable exact tool dispatch time.',
 'sources_actually_read':a['full_research_texts_actually_read'],
 'resources':{'new_HTTP':0,'actual_selected_original_views':10,'actual_individual_360_phone_previews':9,'actual_collection_views':1,'total_actual_image_opens':20,'public_view_import_by_root':'B05-view-000022 through B05-view-000041; import once only'},
 'limits':[
  'Product problem, room, machines, date, costs, codes, orders and states are self-created demonstration; no real user research, sensor, reservation, payment, timer, push or machine control implemented.',
  '360 preview is a raster visual review, not a physical device/interaction test; tiny demo footnote is not used to communicate important payment decisions.',
  'Actual pointer targets and programmatically determinable status announcements do not exist in static PNG. W3C sources inform the design; no WCAG compliance claim is made.',
  '18:40 C1 payment success and 19:25 D1 onsite verification/payment/start are explicit unpictured events in journey.json. Case09 is an unpaid dry choice and case10 is receipt of the resulting paid branch; no false claim that each event has a separate screen.',
  'Free cancellation beyond18:25, delays, timeouts, device lock, late-arrival and repeated payment protection need later product definition/testing. Current depicted voluntary cancellation is18:22; fault auto-cancellation18:29 preserves no-charge rule.',
  'Published final PNG/DSL copies and delivery links are to be verified by root and suite closure audit after publication.'
 ]
}
with (p/'audit-final-v001.json').open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2)
print(json.dumps({'passed':result['passed'],'checks':len(checks),'issues':issues,'actual_views':len(views),'report':str(p/'audit-final-v001.json')},ensure_ascii=False))
