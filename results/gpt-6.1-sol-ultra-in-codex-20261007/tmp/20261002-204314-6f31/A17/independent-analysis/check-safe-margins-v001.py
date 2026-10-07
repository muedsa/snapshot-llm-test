from PIL import Image,ImageChops
from pathlib import Path
import json,datetime
here=Path(__file__).resolve().parent
source=json.loads((here/'source-pair-audit-v001.json').read_text(encoding='utf-8'))
checks=[]
for pair in source['pairs']:
    h=Image.open(pair['handbook_meta']['image_path']).convert('RGB')
    background=Image.new('RGB',h.size,(241,244,248))
    difference=ImageChops.difference(h,background)
    box=difference.getbbox()
    left,top,right,bottom=box
    checks.append({'page':pair['page'],'version':pair['handbook_meta']['version_id'],'actual_nonbackground_bbox':list(box),'actual_min_left_top_right_bottom_margin':[left,top,1200-right,1600-bottom],'safe48_pass':min(left,top,1200-right,1600-bottom)>=48,'scope':'Actual original PNG pixel bounds; supports source margin values and actual visual review.'})
result={'task':'A17','generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks':checks,'all_pages_safe48':all(c['safe48_pass'] for c in checks)}
with (here/'safe-margin-audit-v001.json').open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2)
print(json.dumps(result,ensure_ascii=False,indent=2))
