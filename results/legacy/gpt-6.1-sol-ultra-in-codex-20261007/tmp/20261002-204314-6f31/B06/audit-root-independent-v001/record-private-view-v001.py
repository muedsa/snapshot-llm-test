import json,sys
from pathlib import Path
from datetime import datetime,timezone
root=Path(r'D:\workspaces\gpt-6.1-sol-ultra'); run='20261002-204314-6f31'; tmp=root/'tmp'/run/'B06'; private=tmp/'audit-root-independent-v001'
spec=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
dest=private/'private-views.jsonl'
existing=[json.loads(s) for s in dest.read_text(encoding='utf-8').splitlines()] if dest.exists() else []
for s in spec:
    i=s.pop('request_number',None)
    if i is not None:
        rq=json.loads((tmp/'requests'/f'B06-request-{i:06}'/'render-result.json').read_text(encoding='utf-8'))
        s.update({'request_id':rq['id'],'case_id':rq['case_id'],'version_id':rq['version_id'],'image_path':rq['image_path'],'sha256':rq['response_sha256']})
    s.update({'id':f'B06-independent-private-view-{len(existing)+1:06}','task_id':'B06','reviewer':'/root/b06_final_audit_resume','tool':'view_image','timezone':'UTC'})
    if 'viewed_at' not in s: s['viewed_at']=datetime.now(timezone.utc).isoformat()
    with dest.open('a',encoding='utf-8') as f:f.write(json.dumps(s,ensure_ascii=False)+'\n')
    existing.append(s)
print(json.dumps({'recorded':len(spec),'total_private_views':len(existing)},ensure_ascii=False))
