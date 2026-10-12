from PIL import Image
from pathlib import Path
import json,hashlib
base=Path(__file__).resolve().parent
pairs=[('03','handbook-03-render-v001.json','example-03-render-v001.json'),('04','handbook-04-render-v002.json','example-04-render-v001.json')]
results=[]
for page,page_meta,example_meta in pairs:
    p=json.loads((base/page_meta).read_text(encoding='utf-8'));e=json.loads((base/example_meta).read_text(encoding='utf-8'))
    pi=Image.open(p['image_path']).convert('RGBA');ei=Image.open(e['image_path']).convert('RGBA')
    crop=pi.crop((748,606,1148,846))
    thumb=pi.resize((600,800),Image.Resampling.LANCZOS)
    code=pi.crop((64,594,714,1187))
    for name,im in [('figure',crop),('thumbnail',thumb),('code',code)]:
        dest=base/f'handbook-{page}-{name}-qa-v001.png'
        if dest.exists():raise FileExistsError(dest)
        im.save(dest)
    exact=crop.tobytes()==ei.tobytes();n=sum(a!=b for a,b in zip(crop.getdata(),ei.getdata()))
    result={'page':int(page),'page_image':p['image_path'],'independent_example_image':e['image_path'],'crop_bbox':[748,606,1148,846],'embedded_vs_independent_RGBA_exact':exact,'different_pixels':n,'qa_only_not_final_postprocessing':True}
    if page=='03':result['alpha_patch_actual_RGBA']={'opaque_red':ei.getpixel((64,130)),'trailing_80_on_white':ei.getpixel((260,130))}
    results.append(result)
out=base/'qa-pixel-and-previews-v001.json'
if out.exists():raise FileExistsError(out)
out.write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(results,ensure_ascii=False))
