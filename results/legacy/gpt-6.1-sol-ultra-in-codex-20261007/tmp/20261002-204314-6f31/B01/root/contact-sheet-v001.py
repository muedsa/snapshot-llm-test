import json,hashlib
from pathlib import Path
from PIL import Image,ImageDraw
base=Path(__file__).parent
selection=json.loads((base/'reviewed-selection-v001.json').read_text(encoding='utf-8'))
sheet=Image.new('RGB',(1800,1180),'#172333');draw=ImageDraw.Draw(sheet);evidence=[]
for i,c in enumerate(selection['cases']):
    source=Path(c['image_path']);raw=source.read_bytes();im=Image.open(source).convert('RGB');original_size=im.size;im.thumbnail((320,510),Image.Resampling.LANCZOS)
    x=20+(i%5)*355+(320-im.width)//2;y=40+(i//5)*580+(510-im.height)//2;sheet.paste(im,(x,y));draw.text((20+(i%5)*355,560+(i//5)*580),c['id'],fill='#E8ECF0')
    evidence.append({'case_id':c['id'],'source':str(source),'source_sha256':hashlib.sha256(raw).hexdigest(),'source_size':original_size,'preview_size':im.size})
out=base/'contact-sheet-v001.png'
with out.open('xb') as f: sheet.save(f,format='PNG')
with (base/'contact-sheet-evidence-v001.json').open('x',encoding='utf-8') as f:json.dump({'purpose':'temporary preview only; original final service PNGs unchanged','sources':evidence},f,ensure_ascii=False,indent=2)
print(str(out))
