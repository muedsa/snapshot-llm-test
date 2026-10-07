from PIL import Image
from pathlib import Path
import json
root=Path(__file__).resolve().parents[4]
temp=root/'tmp'/'20261002-204314-6f31'/'A11'
records=[]
for page,request in [('01','000003'),('02','000004')]:
    original=temp/'requests'/f'A11-request-{request}'/'response.png'
    im=Image.open(original).convert('RGB')
    pixels=im.load()
    coords=[]
    for y in range(1500,1600):
        for x in range(0,1200):
            r,g,b=pixels[x,y]
            # Footer glyphs only: rule y1488 is outside this region; colored
            # foreground and sufficiently dark AA are bounded separately.
            if min(r,g,b)<230:
                coords.append((x,y))
    bounds=[min(x for x,y in coords),min(y for x,y in coords),max(x for x,y in coords),max(y for x,y in coords)]
    exact=[(x,y) for x,y in coords if pixels[x,y]==(86,108,114)]
    exact_bounds=[min(x for x,y in exact),min(y for x,y in exact),max(x for x,y in exact),max(y for x,y in exact)]
    preview=temp/'production'/f'footer-glyph-p{page}-v001.png'
    im.crop((48,1498,1152,1560)).resize((1656,93)).save(preview)
    records.append({'page':int(page),'original_png':str(original),'view_preview':str(preview),'footer_pixel_bounds_inclusive':bounds,'exact_ink_pixel_bounds_inclusive':exact_bounds,'minimum_measured_glyph_edge_margin_pixels':min(bounds[0],bounds[1],1199-bounds[2],1599-bounds[3]),'required_margin_pixels':48,'measured_margin_pass':min(bounds[0],bounds[1],1199-bounds[2],1599-bounds[3])>=48,'method':'Enumerated real footer pixels at y1500:1600, min RGB<230 to include dark anti-alias support, exact ink RGB separately.'})
(temp/'production'/'footer-glyph-measure-v001.json').write_text(json.dumps({'method_does_not_edit_final_png':True,'records':records},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(records,ensure_ascii=False))
