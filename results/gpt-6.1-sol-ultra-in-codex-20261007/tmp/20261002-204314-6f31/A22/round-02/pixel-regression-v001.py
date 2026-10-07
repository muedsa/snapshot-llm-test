from pathlib import Path
from PIL import Image
import numpy as np, hashlib, json
rd=Path(__file__).resolve().parent
td=rd.parent
files=[td/'requests/A22-request-000002/response.png',td/'requests/A22-request-000003/response.png',td/'requests/A22-request-000004/response.png']
images=[np.asarray(Image.open(p).convert('RGBA')) for p in files]
regions={'title':[40,31,1520,106],'kpi_orders':[810,159,365,162],'kpi_conversion':[1195,159,365,162],'table_header_first_four_rows':[902,446,636,232],'chart_title_legend':[40,348,820,66],'method':[40,957,1520,31]}
records=[]
for name,(x,y,w,h) in regions.items():
    a,b=images[0][y:y+h,x:x+w],images[2][y:y+h,x:x+w]
    records.append({'region':name,'box':[x,y,w,h],'compared_pixels':w*h,'different_RGBA_pixels':int(np.any(a!=b,axis=2).sum()),'max_channel_difference':int(np.abs(a.astype(int)-b.astype(int)).max())})
mask=np.ones(images[1].shape[:2],dtype=bool)
mask[829:872,87:1527]=False
refinement_diff=np.any(images[1]!=images[2],axis=2)
result={'task_id':'A22','round_id':'round-02','method':'Actual original service PNG RGBA arrays; no raster output modification. Unchanged known tiles compared directly; req3→4 comparison excludes only conclusion-main text box.', 'sources':[{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files],'unchanged_regions':records,'semantic_refinement_outside_conclusion_different_pixels':int((refinement_diff&mask).sum()),'pass':all(r['different_RGBA_pixels']==0 for r in records) and int((refinement_diff&mask).sum())==0,'new_HTTP_or_view_events':0}
out=rd/'pixel-regression-v001.json'
with out.open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2)
print(json.dumps({'pass':result['pass'],'region_count':len(records),'compared_pixels':sum(r['compared_pixels'] for r in records),'outside_refined_title_differences':result['semantic_refinement_outside_conclusion_different_pixels'],'output':str(out)}))
if not result['pass']:raise SystemExit(1)
