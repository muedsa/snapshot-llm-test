import json, hashlib, re
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image

root=Path(r'D:\workspaces\gpt-6.1-sol-ultra')
run='20261002-204314-6f31'
out=root/'outputs'/run/'B06'
tmp=root/'tmp'/run/'B06'
private=root/'tmp'/run/'B06'/'audit-root-independent-v001'
state=json.loads((root/'outputs'/run/'_suite'/'suite-state.json').read_text(encoding='utf-8'))
task=next(t for t in state['tasks'] if t['id']=='B06')
reqs={r['id']:r for r in map(json.loads,(tmp/'requests.jsonl').read_text(encoding='utf-8').splitlines())}
views={r['id']:r for r in map(json.loads,(tmp/'views.jsonl').read_text(encoding='utf-8').splitlines())}
versions={r['id']:r for r in map(json.loads,(tmp/'versions.jsonl').read_text(encoding='utf-8').splitlines())}
portfolio=json.loads((out/'portfolio.json').read_text(encoding='utf-8'))
checks=[]
def check(label, value): checks.append({'check':label,'passed':bool(value)})
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
check('B06 ten distinct registered artifacts',len(task['artifacts'])==10 and len(set(a['case_id'] for a in task['artifacts']))==10)
for name in ['portfolio.json','portfolio.md','gallery.html','snapshot-usage.md','task-metrics.json','problem-evidence.json','design-review.md']:
    check('required root file '+name,(out/name).is_file() and (out/name).stat().st_size>0)
imgs=[]
for a in task['artifacts']:
    case=a['case_id']; p=Path(a['image_path']); d=Path(a['dsl_path']); rq=reqs[a['request_id']]; v=versions[a['version_id']]
    with Image.open(p) as im:
        im.load(); dims=im.size; fmt=im.format
    check(case+' complete PNG decoded/dimensions',fmt=='PNG' and dims==(a['width'],a['height']))
    check(case+' immutable service PNG sha chain',sha(p)==a['image_sha256']==rq['response_sha256']==sha(rq['response_file']))
    check(case+' complete DSL input/version sha chain',sha(d)==a['dsl_sha256']==rq['body_sha256']==sha(rq['input_file'])==v['sha256']==sha(v['path']))
    check(case+' original successful real render',rq['type']=='render' and rq['http_status']==200 and rq['ok'] and rq['content_type']=='image/png')
    pc=next(c for c in portfolio['cases'] if c['id']==case)
    check(case+' portfolio mapping and report', (out/pc['png']).resolve()==p.resolve() and (out/pc['snapshot']).resolve()==d.resolve() and (out/case/'case.md').stat().st_size>0)
    actual=pc['visual_review']['final_view_id']; vw=views[actual]
    check(case+' existing true reviewed evidence matching final bytes',vw['sha256']==a['image_sha256'] and sha(vw['image_path'])==a['image_sha256'])
    imgs.append(a['image_sha256'])
check('B06 ten nonduplicate PNG byte hashes',len(set(imgs))==10)
html=(out/'gallery.html').read_text(encoding='utf-8')
links=[x for x in re.findall(r'(?:href|src)="([^"]+)"',html) if not x.startswith(('#','http','data:'))]
check('B06 gallery local file links all resolve',all((out/x.split('#')[0]).exists() for x in links))
check('B06 gallery indexes all ten full final PNGs',all(c['png'] in links for c in portfolio['cases']))
metrics=json.loads((out/'task-metrics.json').read_text(encoding='utf-8'))
check('B06 metrics final case count',metrics['final_case_count']==10)
selected=json.loads((private/'audit-final-v001.json').read_text(encoding='utf-8'))['artifacts']
for a in task['artifacts']:
    s=next(s for s in selected if s['case_id']==a['case_id'])
    check(a['case_id']+' published original bytes match independently reviewed selected artifacts',a['image_sha256']==s['image_sha256'] and a['dsl_sha256']==s['dsl_sha256'])
report={'task_id':'B06','scope':'Post-publication incremental integrity verification for suite final audit. No additional image-view claims: decoded final files and matched prior independently reviewed selected original bytes.','reviewer':'/root/b06_final_audit_resume','checked_at':datetime.now(timezone.utc).isoformat(),'passed':all(c['passed'] for c in checks),'check_count':len(checks),'checks':checks,'new_actual_views':[],'artifacts':task['artifacts']}
(private/'published-integrity-v001.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:report[k] for k in ['task_id','passed','check_count','scope']},ensure_ascii=False))
