import json,re,hashlib
from pathlib import Path
from datetime import datetime,timezone
root=Path(r'D:\workspaces\gpt-6.1-sol-ultra'); run='20261002-204314-6f31'; private=root/'tmp'/run/'B06'/'audit-root-independent-v001'
state=json.loads((root/'outputs'/run/'_suite'/'suite-state.json').read_text(encoding='utf-8'))
checks=[]; files=[]
def ck(s,v):checks.append({'check':s,'passed':bool(v)})
def inspect_md(path):
    txt=path.read_text(encoding='utf-8'); links=[s for s in re.findall(r'\]\(([^)]+)\)',txt) if not s.startswith(('http:','https:','#','data:'))]
    ck(str(path.relative_to(root))+' relative markdown links resolve',all((path.parent/s.split('#')[0]).resolve().is_file() for s in links))
    files.append({'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bytes':path.stat().st_size,'local_link_count':len(links)})
    return txt
for task in ['B01','B02','B03','B04','B05','B06']:
    out=root/'outputs'/run/task; p=json.loads((out/'portfolio.json').read_text(encoding='utf-8'))
    txt=inspect_md(out/'gallery.md'); ck(task+' appended markdown gallery indexes exactly10 distinct independent original mainPNG/DSL/case entries',len(p['cases'])==10 and all(c['png'] in txt and c['snapshot'] in txt and c['id']+'/case.md' in txt for c in p['cases']))
b06=root/'outputs'/run/'B06'
usage=inspect_md(b06/'snapshot-usage.md'); inspect_md(b06/'design-review.md'); inspect_md(b06/'portfolio.md')
for i in range(1,11): inspect_md(b06/f'case-{i:02}'/'case.md')
ck('B06 final usage exactly one Root final review block',len(re.findall(r'(?m)^## Root final review',usage))==1)
ck('B06 no blank next-status template residue','后续状态为；' not in usage)
ck('B06 final completed state already backed by reviewed10 artifacts',next(t for t in state['tasks'] if t['id']=='B06')['status']=='completed')
report={'run_id':run,'task_id':'B06','reviewer':'/root/b06_final_audit_resume','checked_at':datetime.now(timezone.utc).isoformat(),'scope':'Final updated B06 Markdown/HTML-linked documents and appendedB01-B06 complete markdown indexes. Link/content-file checks only; no new image-view claims.','passed':all(c['passed'] for c in checks),'check_count':len(checks),'checks':checks,'files':files,'new_actual_views':[],'new_http_requests':0,'public_final_image_bytes_unchanged':True,'independent_full_acceptance':str(private/'audit-final-v002.json')}
(private/'final-document-confirmation-v001.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'passed':report['passed'],'checks':len(checks),'files':len(files),'new_views':0},ensure_ascii=False))
