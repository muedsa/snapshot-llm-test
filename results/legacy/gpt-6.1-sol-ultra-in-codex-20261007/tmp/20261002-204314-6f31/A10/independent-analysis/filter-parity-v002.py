from PIL import Image
from pathlib import Path
import json,sys,math,datetime
src=Path(sys.argv[1]);out=Path(sys.argv[2]);im=Image.open(src).convert('RGB');p=im.load()
if out.exists():raise SystemExit('Refuse prior evidence overwrite')
inside=[];outside=[];parity=[]
for y in range(240):
 for x in range(320):
  if not(40<=x<280 and 40<=y<200):
   a=p[1000+x,230+y];b=p[120+x,710+y]
   if a!=b:outside.append({'xy':[x,y],'03':list(a),'04':list(b)})
  if math.hypot(x+.5-160,y+.5-120)<98:
   a=p[560+x,710+y];b=p[1000+x,710+y];inside.append((x,y))
   if a!=b:parity.append({'xy':[x,y],'05':list(a),'06':list(b),'max_delta':max(abs(a[j]-b[j])for j in range(3))})
r={'task_id':'A10','reviewer':'a10_audit_resume','measured_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'actual_service_png':str(src.resolve()),'outside03_04_card_rect_comparison':{'mismatches':len(outside),'sample':outside[:20],'same_clear_stripes':not outside},'inside_circle05_06_comparison':{'pixel_count':len(inside),'mismatches':len(parity),'sample':parity[:20],'same_filtered_pixels':not parity},'scope':'read-only actual PNG comparisons; circle parity excludes2px AA ring.'}
out.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print(json.dumps(r))
