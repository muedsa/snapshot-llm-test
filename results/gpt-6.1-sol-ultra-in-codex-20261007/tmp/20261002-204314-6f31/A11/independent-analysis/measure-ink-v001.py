from PIL import Image
from pathlib import Path
import json,sys,datetime
root=Path(__file__).resolve().parent.parent
m=json.loads((root/'production/text-map-v001.json').read_text(encoding='utf-8'))
entries=m['text_entries'];paths=[root/'requests/A11-request-000003/response.png',root/'requests/A11-request-000004/response.png']
images=[Image.open(p).convert('RGB')for p in paths]
def ink(a,b):return max(abs(a[i]-b[i])for i in range(3))>50
def components(im,box,bg):
 p=im.load();x0,y0,x1,y1=box;pixels={(x,y)for y in range(y0,y1)for x in range(x0,x1)if ink(p[x,y],bg)};cs=[]
 while pixels:
  start=pixels.pop();seen=[start];q=[start]
  while q:
   x,y=q.pop()
   for dx in [-1,0,1]:
    for dy in [-1,0,1]:
     k=(x+dx,y+dy)
     if k in pixels:pixels.remove(k);q.append(k);seen.append(k)
  xs=[x for x,y in seen];ys=[y for x,y in seen];cs.append({'bbox':[min(xs),min(ys),max(xs)+1,max(ys)+1],'count':len(seen),'width':max(xs)-min(xs)+1,'height':max(ys)-min(ys)+1})
 return sorted(cs,key=lambda c:c['bbox'][0])
pages=[]
for n,im in enumerate(images):
 p=im.load();xs=[];ys=[]
 for y in range(im.height):
  for x in range(im.width):
   if p[x,y]!=(255,255,255):xs.append(x);ys.append(y)
 b=[min(xs),min(ys),max(xs)+1,max(ys)+1];pages.append({'page':n+1,'png':str(paths[n]),'nonwhite_bbox_xyxy':b,'nonwhite_margin_ltrb':[b[0],b[1],im.width-b[2],im.height-b[3]],'all_ink_inside48':min(b[0],b[1],im.width-b[2],im.height-b[3])>=48})
amounts=[]
for e in entries:
 if e['page']!=1 or not('amount' in e['id']or'unit-price' in e['id'])or e['id'].startswith('table-head'):continue
 b=e['position'];box=[b['x'],b['y'],b['x']+b['width'],b['y']+b['height']]
 bg=(241,246,245)if e['id'].startswith(('item-1-','item-3-'))else(255,255,255)
 cs=components(images[0],box,bg)
 dots=[v for v in cs if v['width']<=7 and v['height']<=8 and v['count']>=3]
 amounts.append({'id':e['id'],'string':e['source_text'],'font_size':e['font_size'],'components':cs,'period_candidates':dots})
result={'task_id':'A11','reviewer':'a10_audit_resume','measured_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Read-only connected component geometry from actual PNG; period candidates distinguish small punctuation from full-height numerals.','pages':pages,'amounts':amounts}
out=Path(__file__).resolve().parent/'ink-metrics-v001.json'
if out.exists():raise SystemExit('Refuse prior evidence overwrite')
out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps({'pages':pages,'decimal_candidates':[{k:v[k]for k in ['id','font_size','period_candidates']}for v in amounts]},indent=2))
