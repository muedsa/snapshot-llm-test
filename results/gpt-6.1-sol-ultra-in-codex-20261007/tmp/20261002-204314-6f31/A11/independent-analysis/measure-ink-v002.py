from PIL import Image
from pathlib import Path
import json,sys,datetime,hashlib
map_path,p1,p2,out=map(Path,sys.argv[1:5])
if out.exists():raise SystemExit('Refuse prior evidence overwrite')
m=json.loads(map_path.read_text(encoding='utf-8'));entries=m['text_entries'];paths=[p1,p2];images=[Image.open(p).convert('RGB')for p in paths]
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
 b=[min(xs),min(ys),max(xs)+1,max(ys)+1];pages.append({'page':n+1,'png':str(paths[n].resolve()),'sha256':hashlib.sha256(paths[n].read_bytes()).hexdigest(),'dimensions':list(im.size),'nonwhite_bbox_xyxy':b,'nonwhite_margin_ltrb':[b[0],b[1],im.width-b[2],im.height-b[3]],'all_ink_inside48':min(b[0],b[1],im.width-b[2],im.height-b[3])>=48})
amounts=[]
for e in entries:
 if e['page']!=1 or not('amount' in e['id']or'unit-price' in e['id'])or e['id'].startswith('table-head'):continue
 b=e['position'];box=[b['x'],b['y'],b['x']+b['width'],b['y']+b['height']];bg=(241,246,245)if e['id'].startswith(('item-1-','item-3-'))else(255,255,255)
 cs=components(images[0],box,bg);dots=[v for v in cs if v['width']<=7 and v['height']<=8 and v['count']>=3]
 period=max(dots,key=lambda c:c['bbox'][3]);center=(period['bbox'][0]+period['bbox'][2])/2
 amounts.append({'id':e['id'],'string':e['source_text'],'font_family':e['font_family'],'font_size':e['font_size'],'text_align':e['text_align'],'right_edge':b['x']+b['width'],'period':period,'period_ink_center_x':center,'period_selection':'Lowest baseline small connected component; excludes internal dotted-zero marks above baseline.'})
groups=[]
for name,values in [('unit_price',[v for v in amounts if 'unit-price'in v['id']]),('line_amounts_and_summary',[v for v in amounts if 'unit-price'not in v['id']])]:
 centers=[v['period_ink_center_x']for v in values];nominal={(v['font_family'],v['font_size'],v['text_align'],v['right_edge'])for v in values}
 groups.append({'column':name,'ids':[v['id']for v in values],'period_ink_center_x':centers,'ink_center_spread':max(centers)-min(centers),'same_nominal_decimal_anchor':len(nominal)==1,'all_fixed_two_decimal':all(len(v['string'].split('.')[-1])==2 for v in values),'description':'Same mono font family/size/right edge and two fractional digits give common typographic decimal anchor. Bold dots may have wider ink despite same advance.'})
result={'task_id':'A11','reviewer':'a10_audit_resume','measured_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Read-only measurements of actual service PNG, supporting real visual review. No final image editing.','text_map':str(map_path.resolve()),'pages':pages,'amounts':amounts,'decimal_alignment_groups':groups}
out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'pages':pages,'decimal_alignment':groups},ensure_ascii=False,indent=2))
