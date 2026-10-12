from PIL import Image
from pathlib import Path
import json,hashlib
base=Path(__file__).resolve().parent
meta=json.loads((base/'render-baseline-v001.json').read_text(encoding='utf-8'))
data=json.loads((base/'scene-data-grid-v001.json').read_text(encoding='utf-8'))
raw=Path(meta['image_path']).read_bytes()
with (base/'grid-scene-v001.png').open('xb') as f:f.write(raw)
im=Image.open(meta['image_path'])
quad=[('Q1',[160,248,800,888],range(1,5),range(1,5)),('Q2',[800,248,1440,888],range(1,5),range(5,9)),('Q3',[160,888,800,1528],range(5,9),range(1,5)),('Q4',[800,888,1440,1528],range(5,9),range(5,9))]
records=[]
for name,box,rows,cols in quad:
    dest=base/f'grid-{name}-qa-v001.png'
    if dest.exists():raise FileExistsError(dest)
    im.crop(box).save(dest)
    objects=[o for o in data['objects'] if o['row'] in rows and o['column'] in cols]
    records.append({'quadrant':name,'bbox':box,'path':str(dest),'expected_objects':[{k:o[k] for k in ['id','color_name','shape','size','center','label_bbox']} for o in objects],'QA_only':True})
out={'original_service_image':meta['image_path'],'raw_pair_copy':str(base/'grid-scene-v001.png'),'raw_bytes_unchanged':(base/'grid-scene-v001.png').read_bytes()==raw,'SHA256':hashlib.sha256(raw).hexdigest(),'quadrants':records}
with (base/'qa-quadrant-provenance-v001.json').open('x',encoding='utf-8') as f:json.dump(out,f,ensure_ascii=False,indent=2)
print(json.dumps({'quadrants':[{'quadrant':r['quadrant'],'path':r['path'],'ids':[o['id'] for o in r['expected_objects']]} for r in records]},ensure_ascii=False))
