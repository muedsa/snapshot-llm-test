import json, datetime, hashlib
from pathlib import Path
from PIL import Image
directory=Path(__file__).resolve().parent
items=json.loads((directory/'decode-20-input-v001.json').read_text(encoding='utf-8-sig'))
checked=[];issues=[]
for item in items:
    p=Path(item['image_path'])
    try:
        with Image.open(p) as image:
            image.load()
            row={**item,'format':image.format,'mode':image.mode,'actual_dimensions':list(image.size),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
            if image.format!='PNG' or list(image.size)!=item['dimensions']: issues.append({'task':item['task_id'],'case':item['case_id'],'type':'format_or_dimensions','actual':row})
            checked.append(row)
    except Exception as exc: issues.append({'path':str(p),'type':'decode_failed','error':str(exc)})
result={'run_id':'20261002-204314-6f31','reviewer':'/root/b06_cases_02_04_resume','audited_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Full PNG decoding of B05 ten formal files and B06 ten selected real response candidates. This is computational validation, no new perceptual image view.','passed':not issues,'issues':issues,'decoded':len(checked),'images':checked,'new_http_requests':0,'new_image_views':0}
with (directory/'decode-20-v001.json').open('x',encoding='utf-8') as handle: json.dump(result,handle,ensure_ascii=False,indent=2)
print(json.dumps({'passed':result['passed'],'issues':issues,'decoded':len(checked)},ensure_ascii=False))
