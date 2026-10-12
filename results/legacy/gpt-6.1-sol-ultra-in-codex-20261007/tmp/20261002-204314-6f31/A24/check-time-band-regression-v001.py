from pathlib import Path
from PIL import Image,ImageChops
import json,hashlib
base=Path(__file__).resolve().parent
p1=base/'requests/A24-request-000001/response.png'
p2=base/'requests/A24-request-000004/response.png'
a=Image.open(p1).convert('RGBA');b=Image.open(p2).convert('RGBA')
rows=[]
for name,box in [('design',(280,292,1824,368)),('engineering',(280,674,1824,750))]:
    left=a.crop(box);right=b.crop(box)
    count=sum(x!=y for x,y in zip(left.getdata(),right.getdata()))
    rows.append({'id':name,'box':list(box),'pixels':left.width*left.height,'different_RGBA_pixels':count,'unchanged':count==0})
out={'task_id':'A24','kind':'actual_original_service_PNG_time_band_regression','original_sha256':hashlib.sha256(p1.read_bytes()).hexdigest(),'refined_sha256':hashlib.sha256(p2.read_bytes()).hexdigest(),'regions':rows,'all_pass':all(r['unchanged'] for r in rows),'scope':'Read-only regression of task/idle/time bands, not a new physical image view; originals untouched.'}
(base/'time-band-regression-v001.json').open('x',encoding='utf-8').write(json.dumps(out,indent=2)+'\n')
print(json.dumps(out))
