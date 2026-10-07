from PIL import Image,ImageChops
from pathlib import Path
import json,datetime
here=Path(__file__).resolve().parent
source=json.loads((here/'source-pair-audit-v001.json').read_text(encoding='utf-8'))
checks=[]
for pair in source['pairs']:
    h=Image.open(pair['handbook_meta']['image_path']).convert('RGBA')
    e=Image.open(pair['example_meta']['image_path']).convert('RGBA')
    crop=h.crop((748,606,1148,846))
    diff=ImageChops.difference(e,crop)
    different=sum(1 for pixel in diff.getdata() if any(pixel))
    record={'page':pair['page'],'handbook_version':pair['handbook_meta']['version_id'],'example_version':pair['example_meta']['version_id'],'crop_bbox':[748,606,1148,846],'RGBA_pixel_equal':different==0,'different_pixels':different,'scope':'Auxiliary equality check of actual original responses, not substitute for visual view.'}
    if pair['page']==3:
        record['actual_alpha_samples']={'FF_on_white':list(e.getpixel((80,130))),'80_on_white':list(e.getpixel((270,130)))}
    checks.append(record)
result={'task':'A17','generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks':checks,'all_pairs_pixel_equal':all(c['RGBA_pixel_equal'] for c in checks)}
with (here/'pixel-pair-audit-v001.json').open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2)
print(json.dumps(result,ensure_ascii=False,indent=2))
