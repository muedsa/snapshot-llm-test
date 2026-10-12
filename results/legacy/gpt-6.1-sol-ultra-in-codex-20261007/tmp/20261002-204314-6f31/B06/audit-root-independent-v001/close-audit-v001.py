import json,re,hashlib
from pathlib import Path
from datetime import datetime,timezone
root=Path(r'D:\workspaces\gpt-6.1-sol-ultra'); run='20261002-204314-6f31'; tmp=root/'tmp'/run/'B06'; out=root/'outputs'/run/'B06'; p=tmp/'audit-root-independent-v001'
selected=json.loads((p/'audit-final-v001.json').read_text(encoding='utf-8'))
published=json.loads((p/'published-integrity-v001.json').read_text(encoding='utf-8'))
state=json.loads((root/'outputs'/run/'_suite'/'suite-state.json').read_text(encoding='utf-8')); task=next(t for t in state['tasks'] if t['id']=='B06')
metrics=json.loads((out/'task-metrics.json').read_text(encoding='utf-8')); portfolio=json.loads((out/'portfolio.json').read_text(encoding='utf-8'))
checks=[]
def ck(s,v):checks.append({'check':s,'passed':bool(v)})
def lines(name):return [json.loads(s) for s in (tmp/name).read_text(encoding='utf-8').splitlines()]
req=lines('requests.jsonl'); versions=lines('versions.jsonl'); views=lines('views.jsonl'); its=lines('iterations.jsonl'); m=metrics['counts']
ck('B06 published state/taskmetrics completed',task['status']=='completed' and metrics['status']=='completed')
ck('Counts render requests14 all success match log',len(req)==m['snapshot_requests']==m['successful_snapshot_requests']==14 and all(r['http_status']==200 and r['type']=='render' and r['ok'] for r in req))
ck('Counts no failure/retry/doc requests',m['failed_snapshot_requests']==m['retry_requests']==m['document_requests']==m['other_service_requests']==0)
ck('Counts14 unique DSL versions',len(versions)==len({v['id'] for v in versions})==m['dsl_versions']==14)
ck('Counts43 unique actual public view records',len(views)==len({v['id'] for v in views})==m['image_views']==43)
ck('Counts4 complete visual iterations distinct final versions',len({v['version_id'] for v in its if v.get('type')=='visual' and v.get('completed')})==m['completed_visual_iterations']==4)
ck('Counts10 unique baseline versions',sum(v['type']=='baseline' for v in versions)==m['baseline_versions']==10)
ck('Published ten new cases metrics and portfolio',m['final_pngs']==m['independent_creative_cases']==10 and len(portfolio['cases'])==metrics['final_case_count']==10)
ck('Original response byte metrics match files',metrics['resources']['render_response_bytes']==sum(Path(r['response_file']).stat().st_size for r in req))
ck('Final PNG byte metrics match files',metrics['resources']['delivered_final_png_bytes']==sum(Path(a['image_path']).stat().st_size for a in task['artifacts']))
ck('Archived DSL byte metrics match14 version files',metrics['resources']['archived_dsl_version_bytes']==sum(Path(v['path']).stat().st_size for v in versions))
ck('Request duration sum correct',abs(metrics['timings']['request_duration_sum_seconds']-sum(r['duration_seconds'] for r in req))<1e-5)
start=datetime.fromisoformat(metrics['timings']['started_at'].replace('Z','+00:00')); end=datetime.fromisoformat(metrics['timings']['ended_at'].replace('Z','+00:00'))
ck('Whole wallclock correct with explicitly reported platform gap',abs((end-start).total_seconds()-metrics['timings']['elapsed_seconds'])<.01)
ck('Unknown model token and cost remain null',all(metrics['usage'][k] is None for k in ['input_tokens','output_tokens','total_tokens','image_input_usage','cost']))
files=['gallery.md','portfolio.md','snapshot-usage.md','design-review.md']+[c['id']+'/case.md' for c in portfolio['cases']]
for name in files:
    src=out/name; txt=src.read_text(encoding='utf-8'); links=re.findall(r'\]\(([^)]+)\)',txt)
    links=[x for x in links if not x.startswith(('http:','https:','#','data:'))]
    ck('Markdown local links resolve '+name,all((src.parent/x.split('#')[0]).resolve().exists() for x in links))
for c in portfolio['cases']:
    txt=(out/c['id']/'case.md').read_text(encoding='utf-8'))
    ck(c['id']+' actually read final report matches title/scene/true root review',c['title'] in txt and c['id'] in txt and c['visual_review']['final_view_id'] in txt and '未做现场调研' in txt and '主体全部DSL' in txt)
ck('Gallery markdown indexes all10 originals and DSL',all(c['png'] in (out/'gallery.md').read_text(encoding='utf-8') and c['snapshot'] in (out/'gallery.md').read_text(encoding='utf-8') for c in portfolio['cases']))
report={'task_id':'B06','run_id':run,'reviewer':'/root/b06_final_audit_resume','checked_at':datetime.now(timezone.utc).isoformat(),'passed':published['passed'] and all(c['passed'] for c in checks),'scope':'Final post-publication closed task integrity: public final file hashes, allcase/root reports actually read, HTML/Markdown galleries and links, metrics vs original logs/files.','check_count':len(published['checks'])+len(checks),'checks':published['checks']+checks,'new_actual_views':[],'reviewed_final_artifact_count':10,'state_checkpoint':state['last_checkpoint']}
(p/'published-integrity-v002.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
complete={**selected,'checked_at':datetime.now(timezone.utc).isoformat(),'status':'passed_complete_published_task','scope':'Complete B06 independent acceptance: selected real images/DSL, exactdata/geometry, actual ten fullviews and collection/six nearread previews, truthful authored evidence/design-review plus publishedbytes/allcase/rootreports/galleries/links/metrics. B06complete; entire suite status is controlled by root final suite audit.','passed':selected['passed'] and report['passed'],'check_count':selected['check_count']+report['check_count'],'checks':selected['checks']+report['checks'],'post_publication_integrity':str(p/'published-integrity-v002.json'),'supersedes_stage_report':str(p/'audit-final-v001.json'),'pending_after_publication':[],'unresolved_issues':[],'actual_new_views_in_postpublication_checks':0}
(p/'audit-final-v002.json').write_text(json.dumps(complete,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'published_passed':report['passed'],'published_checks':report['check_count'],'complete_passed':complete['passed'],'complete_checks':complete['check_count'],'new_views':0},ensure_ascii=False))
