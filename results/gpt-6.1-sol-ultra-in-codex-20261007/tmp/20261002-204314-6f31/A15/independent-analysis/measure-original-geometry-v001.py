from PIL import Image
from pathlib import Path
from collections import deque
import numpy as np,json,hashlib,datetime,sys
dest=Path(__file__).parent
src=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('tasks/A15-reference-reconstruction/inputs/reference.png').resolve()
name=sys.argv[2] if len(sys.argv)>2 else 'reference-pixel-geometry-v001.json'
im=Image.open(src).convert('RGB');a=np.asarray(im);H,W=a.shape[:2]
def component(seed,expand=0):
 x,y=seed;rgb=a[y,x].copy();mask=(a==rgb).all(axis=2);seen=np.zeros((H,W),dtype=bool);q=deque([(x,y)]);seen[y,x]=True;loX=hiX=x;loY=hiY=y;count=0
 while q:
  x,y=q.popleft();count+=1;loX=min(loX,x);hiX=max(hiX,x);loY=min(loY,y);hiY=max(hiY,y)
  for nx,ny in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]:
   if 0<=nx<W and 0<=ny<H and mask[ny,nx] and not seen[ny,nx]:seen[ny,nx]=True;q.append((nx,ny))
 return {'bbox_exclusive':[loX-expand,loY-expand,hiX+1+expand,hiY+1+expand],'sample_rgb':[int(v) for v in rgb],'connected_exact_color_pixel_count':count,'outer_border_inference_expand':expand}
boxes={n:component(p,e) for n,p,e in [('sidebar',(210,400),0),('nav-selected',(24,140),0),('export',(1380,70),0),('kpi1',(600,270),1),('kpi2',(985,270),1),('kpi3',(1370,270),1),('chart',(990,585),1),('activity',(1380,585),1),('table',(1380,830),1),('table-header',(1355,705),0),('status-progress',(1040,742),0),('workspace',(24,820),0)]}
bar_centers=[384,485,586,687,788,889];bars=[]
for i,x in enumerate(bar_centers):
 b=component((x,535));box=b['bbox_exclusive'];b.update({'index':i,'month':['Apr','May','Jun','Jul','Aug','Sep'][i],'source_value':[54,72,63,90,81,108][i],'pixel_height':box[3]-box[1],'continuous_expected_height':1.2*[54,72,63,90,81,108][i]});bars.append(b)
grid_rgb=a[405,340].copy();grid_y=[y for y in range(395,555) if np.array_equal(a[y,340],grid_rgb)]
anchors=[{'id':'sidebar-right','xy':[boxes['sidebar']['bbox_exclusive'][2],0]}, {'id':'nav-selected-top-left','xy':boxes['nav-selected']['bbox_exclusive'][:2]}, {'id':'export-top-left','xy':boxes['export']['bbox_exclusive'][:2]}, {'id':'first-kpi-top-left','xy':boxes['kpi1']['bbox_exclusive'][:2]}, {'id':'first-kpi-bottom-right','xy':boxes['kpi1']['bbox_exclusive'][2:]}, {'id':'second-kpi-top-left','xy':boxes['kpi2']['bbox_exclusive'][:2]}, {'id':'third-kpi-top-left','xy':boxes['kpi3']['bbox_exclusive'][:2]}, {'id':'chart-top-left','xy':boxes['chart']['bbox_exclusive'][:2]}, {'id':'chart-bottom-right','xy':boxes['chart']['bbox_exclusive'][2:]}, {'id':'activity-top-left','xy':boxes['activity']['bbox_exclusive'][:2]}, {'id':'plot120-grid-left','xy':[333,min(grid_y)]}, {'id':'plot-zero-grid-left','xy':[333,max(grid_y)]}, {'id':'table-top-left','xy':boxes['table']['bbox_exclusive'][:2]}, {'id':'table-bottom-right','xy':boxes['table']['bbox_exclusive'][2:]}, {'id':'table-header-top-left','xy':boxes['table-header']['bbox_exclusive'][:2]}, {'id':'status-progress-top-left','xy':boxes['status-progress']['bbox_exclusive'][:2]}, {'id':'workspace-card-top-left','xy':boxes['workspace']['bbox_exclusive'][:2]}, {'id':'workspace-card-bottom-right','xy':boxes['workspace']['bbox_exclusive'][2:]}]
record={'task_id':'A15','reviewer':'a10_audit_resume','source':str(src),'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'measured_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'dimensions':[W,H],'boxes':boxes,'anchors':anchors,'bars':bars,'grid_y':grid_y,'method':'Read original PNG exact fill connected components; white card interiors expanded1 for visible border. Bounding corner intersection estimates ignore corner AA. Bar integer pixel extents compared with continuous expected height1.2×value; font and pixel residuals not inferred from this geometry check.'}
out=dest/name;out.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'path':str(out),'anchors':anchors,'grid_y':grid_y,'bars':[b['bbox_exclusive'] for b in bars]},ensure_ascii=False))
