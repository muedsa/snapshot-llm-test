from PIL import Image
from pathlib import Path
import sys,json,datetime
manifest=Path(sys.argv[1]);out=Path(sys.argv[2])
if out.exists(): raise SystemExit('Refuse evidence overwrite')
cards=json.loads(manifest.read_text(encoding='utf-8'))['cards'];records=[]
for c in cards:
    im=Image.open(c['image_path']).convert('RGB');r=c['title_region'];x,y,w,h=[round(r[k]) for k in ['x','y','width','height']]
    bg=im.getpixel((0,0));rows=[]
    for yy in range(y,y+h):
        n=sum(sum(abs(a-b) for a,b in zip(im.getpixel((xx,yy)),bg))>=100 for xx in range(x,x+w))
        if n>=3: rows.append(yy)
    bands=[]
    for yy in rows:
        if not bands or yy-bands[-1][-1]>8: bands.append([yy])
        else: bands[-1].append(yy)
    spans=[[p[0],p[-1]+1] for p in bands]
    xs=[];ys=[]
    for yy in range(im.height):
        for xx in range(im.width):
            if sum(abs(a-b) for a,b in zip(im.getpixel((xx,yy)),bg))>=100:
                xs.append(xx);ys.append(yy)
    bb=[min(xs),min(ys),max(xs)+1,max(ys)+1] if xs else None
    records.append({'id':c['id'],'original_png':c['image_path'],'title_row_bands_xy':spans,'title_detected_band_count':len(spans),'foreground_threshold_bbox':bb,'foreground_margins_ltrb':[bb[0],bb[1],im.width-bb[2],im.height-bb[3]] if bb else None})
r={'task_id':'A14','measured_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Read-only original PNG foreground-row profiles in known title boxes. Bands aid actual line-count inspection; threshold boxes are measured ink/shape extents, not inferred source textbox extents. No visual pass inferred.','method':'RGB distance>=100 from actual background; title rows at least3 foreground pixels; gaps<=8 merged. Original images unchanged.','cards':records}
out.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(records,ensure_ascii=False))
