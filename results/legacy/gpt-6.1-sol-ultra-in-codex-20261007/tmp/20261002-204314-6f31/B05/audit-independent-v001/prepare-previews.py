import json, hashlib
from pathlib import Path
from PIL import Image,ImageDraw
root=Path.cwd();run='20261002-204314-6f31';base=root/'tmp'/run/'B05';private=base/'audit-independent-v001'
read=lambda f:json.loads(Path(f).read_text(encoding='utf-8-sig'))
selection=read(base/'root'/'selection-v001.json');cases=selection if isinstance(selection,list) else selection['cases']
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();rows=[]
contact=Image.new('RGB',(1300,1080),'#18272D');draw=ImageDraw.Draw(contact)
for i,c in enumerate(cases):
 r=read(c['render_meta']);p=Path(r['image_path']);raw=Image.open(p).convert('RGB');before=sha(p)
 if raw.size==(720,1440):
  preview=raw.resize((360,720),Image.Resampling.LANCZOS);target=private/(c['id']+'-360.png')
  with target.open('xb') as f:preview.save(f,format='PNG')
 else:target=None
 small=raw.copy();small.thumbnail((236,472),Image.Resampling.LANCZOS);x=12+(i%5)*260;y=34+(i//5)*540
 draw.text((x,y-23),c['id'],fill='white');contact.paste(small,(x,y))
 rows.append({'case_id':c['id'],'original':str(p),'original_sha256':before,'preview_360':str(target) if target else None,'preview_sha256':sha(target) if target else None,'metadata':c['metadata'],'render_meta':c['render_meta'],'source_unchanged':sha(p)==before})
target=private/'contact-360-v001.png'
with target.open('xb') as f:contact.save(f,format='PNG')
with (private/'preview-manifest-v001.json').open('x',encoding='utf-8') as f:json.dump({'scope':'Inspection previews only, not final art or new service renders. All original service PNG bytes remained unchanged.','rows':rows,'contact':str(target)},f,ensure_ascii=False,indent=2)
print(json.dumps(rows,ensure_ascii=False,indent=2))
