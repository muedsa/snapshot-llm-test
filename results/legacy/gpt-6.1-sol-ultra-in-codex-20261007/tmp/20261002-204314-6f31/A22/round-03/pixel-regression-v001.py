from pathlib import Path
from PIL import Image
import numpy as np, hashlib, json
rd=Path(__file__).resolve().parent; td=rd.parent
files=[td/'requests/A22-request-000005/response.png',td/'requests/A22-request-000007/response.png']
images=[np.asarray(Image.open(p).convert('RGBA')) for p in files]
regions={'chart_title_legend':[40,348,820,66],'chart_caption':[156,414,670,30],'axis_left_ticks':[49,436,91,306],'table_header':[902,446,636,44],'method':[40,957,1520,31]}
records=[]
for name,(x,y,w,h) in regions.items():
    a,b=images[0][y:y+h,x:x+w],images[1][y:y+h,x:x+w]
    records.append({'region':name,'box':[x,y,w,h],'compared_pixels':w*h,'different_RGBA_pixels':int(np.any(a!=b,axis=2).sum())})
result={'task_id':'A22','round_id':'round-03','method':'Actual prior-round and final original service PNG RGBA, read only. Chosen regions remained identical in actual submitted source. Reflowed data regions are intentionally excluded.', 'sources':[{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files],'unchanged_regions':records,'pass':all(r['different_RGBA_pixels']==0 for r in records),'new_HTTP_or_view_events':0}
with (rd/'pixel-regression-v001.json').open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2)
print(json.dumps({'pass':result['pass'],'region_count':len(records),'compared_pixels':sum(r['compared_pixels'] for r in records)}))
if not result['pass']:raise SystemExit(1)
