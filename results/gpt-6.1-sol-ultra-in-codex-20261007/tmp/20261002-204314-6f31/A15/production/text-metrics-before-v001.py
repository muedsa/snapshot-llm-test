from pathlib import Path
from PIL import Image
import json
root=Path(__file__).resolve().parents[4]
temp=root/'tmp'/'20261002-204314-6f31'/'A15'
ref=Image.open(root/'tasks'/'A15-reference-reconstruction'/'inputs'/'reference.png').convert('RGB')
target=Image.open(temp/'requests'/'A15-request-000001'/'response.png').convert('RGB')
regions={'main-title':[250,20,1060,78],'chart-title':[280,320,720,366],'activity-title':[1050,320,1380,366],'table-title':[280,634,780,681],'revenue-value':[280,185,600,239],'orders-value':[660,185,990,239],'refund-value':[1044,185,1370,239]}
records=[]
for name,rect in regions.items():
    boxes=[]
    for image,col in [(ref,(24,40,63)),(target,(27,45,69))]:
        p=image.load();coords=[(x,y) for y in range(rect[1],rect[3]) for x in range(rect[0],rect[2]) if p[x,y]==col]
        if not coords:raise Exception(f'No ink {name} {col}')
        boxes.append([min(x for x,y in coords),min(y for x,y in coords),max(x for x,y in coords)+1,max(y for x,y in coords)+1])
    records.append({'name':name,'reference_ink_bbox_exclusive':boxes[0],'v001_ink_bbox_exclusive':boxes[1],'difference_target_minus_reference_edges':[a-b for a,b in zip(boxes[1],boxes[0])],'method':'Exact pure ink pixel bbox; not Text layout boxes or geometry.'})
(temp/'production'/'text-metrics-before-v001.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(records,ensure_ascii=False))
