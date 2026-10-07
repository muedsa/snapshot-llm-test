import json,sys,os,math
from PIL import Image,ImageDraw,ImageFont
root=os.path.abspath(os.path.join(os.path.dirname(__file__),'../../..'))
state_path=os.path.join(root,'outputs','20261002-204314-6f31','_suite','suite-state.json')
state=json.load(open(state_path,encoding='utf-8-sig'))
images=[dict(a,task_id=t['id']) for t in state['tasks'] for a in t['artifacts']]
seen=set(); unique=[]
for x in images:
 if x['image_path'] not in seen: seen.add(x['image_path']); unique.append(x)
if len(unique)!=124: raise ValueError('Final suite overview requires actual124 registered finals, got '+str(len(unique)))
out=os.path.join(os.path.dirname(__file__),'final-overviews-v001');os.makedirs(out,exist_ok=True)
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',18)
pages=[]
for page in range(math.ceil(len(unique)/24)):
 batch=unique[page*24:(page+1)*24]; canvas=Image.new('RGB',(2400,4*350),'#101926');dr=ImageDraw.Draw(canvas)
 for i,a in enumerate(batch):
  x=i%6*400;y=i//6*350
  im=Image.open(a['image_path']);im.load();im.thumbnail((374,290),Image.Resampling.LANCZOS)
  if im.mode=='RGBA': bg=Image.new('RGBA',im.size,'#e8e8e8');bg.alpha_composite(im);im=bg.convert('RGB')
  elif im.mode!='RGB': im=im.convert('RGB')
  canvas.paste(im,(x+(400-im.width)//2,y+43))
  label=a['task_id']+' / '+str(a.get('round_id') or a.get('case_id') or a.get('title') or os.path.basename(a['image_path']))
  dr.text((x+12,y+9),label[:30],font=font,fill='#e8edf0')
 f=os.path.join(out,'overview-'+str(page+1).zfill(2)+'.png');canvas.save(f);pages.append({'page':page+1,'image_path':f,'artifacts':batch})
json.dump({'purpose':'Final full-suite overview only; does not substitute previously actual per-original views','final_count':len(unique),'pages':pages},open(os.path.join(out,'manifest.json'),'x',encoding='utf-8'),ensure_ascii=False,indent=2)
print(json.dumps({'finals':len(unique),'pages':len(pages),'manifest':os.path.join(out,'manifest.json')}))
