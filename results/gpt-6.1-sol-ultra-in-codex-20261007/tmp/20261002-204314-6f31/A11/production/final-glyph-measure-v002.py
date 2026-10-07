from pathlib import Path
from PIL import Image
import json,hashlib
root=Path(__file__).resolve().parents[4]
temp=root/'tmp'/'20261002-204314-6f31'/'A11'
records=[]
for page,request,version in [(1,'000005','A11-v002-p01'),(2,'000004','A11-v001-p02')]:
    original=temp/'requests'/f'A11-request-{request}'/'response.png'
    pixels=Image.open(original).convert('RGB').load()
    coords=[]
    for y in range(1600):
        for x in range(1200):
            if min(pixels[x,y])<230:
                coords.append((x,y))
    bounds=[min(x for x,y in coords),min(y for x,y in coords),max(x for x,y in coords),max(y for x,y in coords)]
    footer=[(x,y) for x,y in coords if y>=1500]
    fb=[min(x for x,y in footer),min(y for x,y in footer),max(x for x,y in footer),max(y for x,y in footer)]
    margins=[bounds[0],bounds[1],1199-bounds[2],1599-bounds[3]]
    records.append({'page':page,'version_id':version,'original_png':str(original),'png_sha256':hashlib.sha256(original.read_bytes()).hexdigest(),'foreground_bounds_inclusive':bounds,'edge_margins_px_left_top_right_bottom':margins,'footer_glyph_bounds_inclusive':fb,'minimum_glyph_and_foreground_margin':min(margins),'required_margin_px':48,'pass':min(margins)>=48})
result={'method':'Exact scan of final original PNG pixels min(R,G,B)<230; includes foreground ink, decoration and dark anti-alias support. Footer range y1500:1600 separately bounds actual glyphs, not Text layout boxes. Final PNG files are read only.','records':records}
(temp/'production'/'final-glyph-measure-v002.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(result,ensure_ascii=False))
