import json,sys,os
from PIL import Image,ImageOps,ImageDraw,ImageFont
task,selection,out=sys.argv[1:]
with open(selection,encoding='utf-8-sig') as f: rows=json.load(f)['cases']
canvas=Image.new('RGB',(1800,1120),'#101722');d=ImageDraw.Draw(canvas)
for k,r in enumerate(rows):
    with open(r['render_meta'],encoding='utf-8-sig') as f: meta=json.load(f)
    im=Image.open(meta['image_path']).convert('RGB');im=ImageOps.contain(im,(336,480))
    x=(k%5)*360+12+(336-im.width)//2;y=(k//5)*550+44
    canvas.paste(im,(x,y));d.text(((k%5)*360+16,(k//5)*550+14),task+' / '+r['id'],fill='#ffffff')
if os.path.exists(out): raise RuntimeError('Refusing to overwrite contact sheet')
canvas.save(out)
print(out)
