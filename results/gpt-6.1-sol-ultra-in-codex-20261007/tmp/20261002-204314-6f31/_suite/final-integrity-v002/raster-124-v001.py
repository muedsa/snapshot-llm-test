import json, hashlib, datetime
from pathlib import Path
from PIL import Image, ImageChops
root=Path.cwd(); run='20261002-204314-6f31'; private=root/'tmp'/run/'_suite'/'final-integrity-v002'
state=json.loads((root/'outputs'/run/'_suite'/'suite-state.json').read_text(encoding='utf-8-sig'))
checked=[];issues=[]
for t in state['tasks']:
 if t['id'] not in [f'A{n:02}' for n in range(1,25)]+['B01','B02','B03','B04','B05','B06']:continue
 for a in t['artifacts']:
  f=Path(a['image_path'])
  with Image.open(f) as raw:
   raw.load();rgba=raw.convert('RGBA');alpha=rgba.getchannel('A');hist=alpha.histogram()
   q={'task_id':t['id'],'artifact_id':a['id'],'file':str(f),'format':raw.format,'original_mode':raw.mode,'size':list(raw.size),'alpha_extrema':list(alpha.getextrema()),'transparent_pixels':hist[0],'fully_opaque_pixels':hist[255],'pixel_count':raw.width*raw.height}
   if raw.format!='PNG' or raw.size!=(a['width'],a['height']):issues.append({'file':str(f),'type':'PNG_decode_or_dimensions'})
   if t['id']=='A23' and f.name.startswith('frame-'):
    if hist[0]==0 or alpha.getextrema()[1]!=255:issues.append({'file':str(f),'type':'frame_not_transparent_or_subject_not_opaque'})
    q['four_corner_RGBA']=[list(rgba.getpixel(p)) for p in [(0,0),(raw.width-1,0),(0,raw.height-1),(raw.width-1,raw.height-1)]]
    if any(v[3]!=0 for v in q['four_corner_RGBA']):issues.append({'file':str(f),'type':'frame_corner_not_transparent'})
   if t['id']=='A13' and f.name=='symbol-black.png':
    nonblack=sum(1 for r,g,b,a0 in rgba.getdata() if a0>0 and (r!=0 or g!=0 or b!=0))
    q['visible_nonblack_pixels']=nonblack
    if nonblack:issues.append({'file':str(f),'type':'black_icon_visible_nonzero_RGB','count':nonblack})
    if hist[0]==0:issues.append({'file':str(f),'type':'black_icon_not_transparent'})
   if t['id']=='A13' and f.name=='symbol-color.png' and hist[0]==0:issues.append({'file':str(f),'type':'color_icon_not_transparent'})
   checked.append(q)
a=Image.open(root/'outputs'/run/'A19'/'occlusion.png').convert('RGBA')
b=Image.open(root/'outputs'/run/'A19'/'occlusion-alternative.png').convert('RGBA')
same=a.tobytes()==b.tobytes()
if not same:issues.append({'task_id':'A19','type':'occlusion_decoded_pixels_not_equivalent'})
record={'schema_version':1,'run_id':run,'reviewer':'/root/b06_cases_02_04_resume','audited_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Pillow full PNG decoding, actual dimensions and alpha/RGB checks for124 preserved final files; A19 decoded RGBA equality. This is a computational check, not a claim of visual perception. No raster file was modified.','passed':not issues,'issues':issues,'decoded_final_pngs':len(checked),'images':checked,'A19_actual_RGBA_equivalence':same}
with (private/'raster-audit-v001.json').open('x',encoding='utf-8') as f:json.dump(record,f,ensure_ascii=False,indent=2)
print(json.dumps({'passed':not issues,'issues':issues,'decoded_final_pngs':len(checked),'A19_RGBA_equivalence':same},ensure_ascii=False,indent=2))
