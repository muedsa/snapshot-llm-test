from PIL import Image
from pathlib import Path
import json
base=Path(__file__).resolve().parent
finals=json.loads((base/'final-candidates-v001.json').read_text(encoding='utf-8'))
out=[]
for page in ['03','04']:
    p=next(f for f in finals if f['stem']=='handbook-'+page)
    e=next(f for f in finals if f['stem']=='example-'+page)
    pi=Image.open(p['image_path']).convert('RGBA');ei=Image.open(e['image_path']).convert('RGBA')
    crop=pi.crop((748,606,1148,846))
    exact=crop.tobytes()==ei.tobytes()
    item={'page':int(page),'handbook_version':p['version_id'],'example_version':e['version_id'],'embedded_widget_bbox':[748,606,1148,846],'embedded_vs_independent_RGBA_exact':exact,'different_pixels':sum(a!=b for a,b in zip(crop.get_flattened_data(),ei.get_flattened_data())),'original_PNGs_unchanged':True,'QA_only':True}
    if page=='03':item['alpha_patch_actual_RGBA']={'opaque_red':ei.getpixel((64,130)),'trailing_80_on_white':ei.getpixel((260,130))}
    for name,im in [('figure',crop),('thumbnail',pi.resize((600,800),Image.Resampling.LANCZOS))]:
        dest=base/f'handbook-{page}-final-{name}-qa-v001.png'
        if dest.exists():raise FileExistsError(dest)
        im.save(dest)
    if not exact:raise AssertionError(item)
    out.append(item)
dest=base/'final-pixel-check-v001.json'
if dest.exists():raise FileExistsError(dest)
dest.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(out,ensure_ascii=False))
