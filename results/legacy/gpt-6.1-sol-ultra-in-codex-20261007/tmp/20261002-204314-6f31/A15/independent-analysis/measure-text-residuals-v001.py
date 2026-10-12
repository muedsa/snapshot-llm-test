from pathlib import Path
from PIL import Image
import numpy as np,json
dest=Path(__file__).parent
paths=[Path('tasks/A15-reference-reconstruction/inputs/reference.png').resolve(),dest.parent/'requests/A15-request-000001/response.png']
rois={'main-title':[260,25,1000,80],'kpi-revenue':[280,190,590,240],'kpi-orders':[660,190,980,240],'kpi-refund':[1040,190,1370,240],'chart-title':[280,328,760,370],'activity-title':[1050,328,1390,375],'table-title':[280,638,950,680]}
rows=[]
for name,box in rois.items():
 row={'id':name,'roi':box,'mask_rule':'All RGB channels<120: strong dark text foreground, not full AA bounds.'}
 for tag,p in zip(['reference','reconstruction'],paths):
  a=np.asarray(Image.open(p).convert('RGB'))[box[1]:box[3],box[0]:box[2]];m=(a.max(axis=2)<120);yy,xx=np.where(m);row[tag+'_bbox']=[int(xx.min()+box[0]),int(yy.min()+box[1]),int(xx.max()+box[0]+1),int(yy.max()+box[1]+1)]
 row['difference_xyxy']=[b-a for a,b in zip(row['reference_bbox'],row['reconstruction_bbox'])];rows.append(row)
record={'task_id':'A15','reviewer':'a10_audit_resume','source_paths':[str(p) for p in paths],'measurement_scope':'Strong-text threshold foreground in fixed ROIs; no claim of exact glyph/AA pixel extent. These are residual comparison details, not the rectangle anchor audit.','rows':rows}
(dest/'text-residuals-baseline-v001.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf8');print(json.dumps(rows))
