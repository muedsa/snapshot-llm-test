from pathlib import Path
from PIL import Image
from collections import deque
from decimal import Decimal
import csv,json,hashlib,datetime,numpy as np
dest=Path(__file__).parent;dest.mkdir(parents=True,exist_ok=True)
csvpath=Path('tasks/A16-visual-data-forensics/inputs/source.csv').resolve();pngpath=csvpath.parent/'flawed-report.png'
rows=[]
with csvpath.open(encoding='utf-8-sig',newline='') as f:
 for r in csv.DictReader(f):
  revenue=int(r['revenue_wan']);cost=int(r['cost_wan']);profit=revenue-cost
  rows.append({'quarter':r['quarter'],'revenue_wan':revenue,'cost_wan':cost,'profit_wan':profit,'profit_margin_percent':float(Decimal(profit)*100/Decimal(revenue))})
a=np.asarray(Image.open(pngpath).convert('RGB'));H,W=a.shape[:2]
def component(seed):
 x,y=seed;rgb=a[y,x].copy();mask=(a==rgb).all(axis=2);seen=np.zeros((H,W),dtype=bool);q=deque([(x,y)]);seen[y,x]=True;lx=hx=x;ly=hy=y
 while q:
  x,y=q.popleft();lx=min(lx,x);hx=max(hx,x);ly=min(ly,y);hy=max(hy,y)
  for nx,ny in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]:
   if 0<=nx<W and 0<=ny<H and mask[ny,nx] and not seen[ny,nx]:seen[ny,nx]=True;q.append((nx,ny))
 return {'exact_fill_bbox_exclusive':[lx,ly,hx+1,hy+1],'rgb':[int(v) for v in rgb]}
bars=[]
for i,r in enumerate(rows):
 for series,x,seed_y in [('revenue',256+i*236,530),('cost',332+i*236,530)]:
  b=component((x,seed_y));box=b['exact_fill_bbox_exclusive'];value=r[series+'_wan'];b.update({'quarter':r['quarter'],'source_series_identified_by_numeric_labels':series,'source_value':value,'pixel_height':box[3]-box[1],'image_numeric_label':value,'legend_names_series': '成本' if series=='revenue' else '收入','axis_interpolated_value_at_top_using_displayed100_200':100+(565-box[1])/2.7,'note':'Exact-fill core boundary excludes some antialias fringe. Displayed grid axis uses54px/20wan.'});bars.append(b)
gridrgb=a[295,160].copy();grid_y=[y for y in range(285,575) if np.array_equal(a[y,160],gridrgb)]
checks={'source_rows':rows,'totals':{'revenue_wan':sum(r['revenue_wan'] for r in rows),'cost_wan':sum(r['cost_wan'] for r in rows),'profit_wan':sum(r['profit_wan'] for r in rows)},'highest_profit_quarter':max(rows,key=lambda r:r['profit_wan'])['quarter'],'q3_revenue_change_wan':rows[2]['revenue_wan']-rows[1]['revenue_wan'],'q3_revenue_change_percent':float((Decimal(rows[2]['revenue_wan'])/Decimal(rows[1]['revenue_wan'])-1)*100),'q3_profit_shown':42,'q3_profit_actual':rows[2]['profit_wan'],'q3_profit_overstatement':42-rows[2]['profit_wan'],'actual_displayed_grid_y':grid_y,'bars':bars}
record={'task_id':'A16','reviewer':'a10_audit_resume','recorded_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'trusted_csv':str(csvpath),'csv_sha256':hashlib.sha256(csvpath.read_bytes()).hexdigest(),'flawed_png':str(pngpath),'flawed_sha256':hashlib.sha256(pngpath.read_bytes()).hexdigest(),'scope':'Only actual flawed image and trusted CSV; no old DSL read or inferred. Geometry color-core measurement supplements real visual inspection.','checks':checks}
(dest/'source-numeric-geometry-diagnosis-v001.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'path':str(dest/'source-numeric-geometry-diagnosis-v001.json'),'rows':rows,'grid_y':grid_y,'bar_bboxes':[b['exact_fill_bbox_exclusive'] for b in bars],'totals':checks['totals']},ensure_ascii=False))
