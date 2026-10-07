from pathlib import Path
from PIL import Image
import json
root=Path(__file__).resolve().parents[4]
temp=root/'tmp'/'20261002-204314-6f31'/'A15'
ref=Image.open(root/'tasks'/'A15-reference-reconstruction'/'inputs'/'reference.png').convert('RGB')
target=Image.open(temp/'requests'/'A15-request-000002'/'response.png').convert('RGB')
regions={'main-title':[250,20,1060,78],'chart-title':[280,320,720,366],'activity-title':[1050,320,1380,366],'table-title':[280,634,780,681],'revenue-value':[280,185,600,239],'orders-value':[660,185,990,239],'refund-value':[1044,185,1370,239]}
records=[]
for name,rect in regions.items():
    boxes=[]
    for image in [ref,target]:
        p=image.load();coords=[(x,y) for y in range(rect[1],rect[3]) for x in range(rect[0],rect[2]) if p[x,y]==(24,40,63)]
        boxes.append([min(x for x,y in coords),min(y for x,y in coords),max(x for x,y in coords)+1,max(y for x,y in coords)+1])
    records.append({'name':name,'reference_ink_bbox_exclusive':boxes[0],'v002_ink_bbox_exclusive':boxes[1],'difference_target_minus_reference_edges':[a-b for a,b in zip(boxes[1],boxes[0])],'method':'Exact pure foreground ink#18283F bbox of both real original PNGs; not Text layout boxes.'})
result={'records':records,'maximum_absolute_edge_residual':max(abs(n) for r in records for n in r['difference_target_minus_reference_edges']),'known_scope':'Seven selected headline/value foreground bboxes, not full-image pixel equivalence.'}
(temp/'production'/'text-metrics-after-v002.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(result,ensure_ascii=False))
