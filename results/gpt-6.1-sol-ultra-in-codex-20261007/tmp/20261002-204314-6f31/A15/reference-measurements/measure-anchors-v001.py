from PIL import Image
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone
import json, hashlib

root=Path(r'D:\workspaces\gpt-6.1-sol-ultra')
source=root/'tasks/A15-reference-reconstruction/inputs/reference.png'
dest=root/'tmp/20261002-204314-6f31/A15/reference-measurements'
im=Image.open(source).convert('RGB')
def matching_bbox(box,color):
    coords=[(x,y) for y in range(box[1],box[3]) for x in range(box[0],box[2]) if im.getpixel((x,y))==color]
    if not coords: raise ValueError(f'no matching pixels in {box}')
    return [min(x for x,y in coords),min(y for x,y in coords),max(x for x,y in coords)+1,max(y for x,y in coords)+1]
color=(226,232,241)
cards={name:{'search_box':box,'color':'#E2E8F1','bbox_exclusive':matching_bbox(box,color),'method':'min/max exact border-color pixels in visual region'} for name,box in {
 'revenue':[250,125,625,290], 'orders':[635,125,1010,290], 'refund_rate':[1020,125,1395,290],
 'net_revenue':[250,300,1015,605], 'team_activity':[1020,300,1410,605], 'recent_projects':[250,614,1410,852]
}.items()}
anchors=[]
def add(name,xy,method,kind,region,evidence):
    anchors.append({'id':f'A15-reference-anchor-{len(anchors)+1:03d}','name':name,'reference_xy':xy,'measurement_type':method,'geometry_kind':kind,'region':region,'evidence':evidence,'reconstruction_xy':None,'error_px':None})
add('sidebar-main boundary at canvas top',[220,0],'exact flat-color transition','edge','top-left','horizontal y=0: #14233C x0..219, #F3F6FB x220..1439')
add('selected navigation top-left',[18,116],'exact component bbox','rectangle corner','top-left','selected_nav exact #294467 connected component')
add('selected navigation bottom-right',[202,164],'exact component bbox exclusive','rectangle corner','top-left','selected_nav inclusive bbox [18,116,201,163]')
add('export button top-left',[1184,43],'exact component bbox','rectangle corner','top-right','button exact #245CE4 connected component')
add('export button bottom-right',[1400,91],'exact component bbox exclusive','rectangle corner','top-right','button inclusive bbox [1184,43,1399,90]')
for name,card in cards.items():
    b=card['bbox_exclusive']; region='top-left' if name in ('revenue','orders') else 'top-right' if name=='refund_rate' else 'chart' if name=='net_revenue' else 'right-center' if name=='team_activity' else 'bottom-main'
    add(f'{name} card top-left',b[:2],'exact border pixels bbox','rectangle corner',region,card)
    add(f'{name} card bottom-right',b[2:],'exact border pixels bbox exclusive','rectangle corner',region,card)
add('plot top grid left',[333,405],'exact color run','plot anchor','chart','y405 exact #E7EDF5 run x333..969')
add('plot zero grid right-exclusive',[970,549],'exact color run exclusive right','plot anchor','chart','y549 exact #E7EDF5 run x333..969 with bars ending y548')
add('Jul bar top center',[687,441],'horizontal center geometry from raster range','bar anchor','chart','inclusive pure-color x660..713 => geometric center687; first full blue row441')
add('Sep bar top center',[889,419.4],'estimated subpixel top from exact raster and input data ratio','bar anchor','chart','pure-color first y420; chart span144 and value108/120 => estimated549-129.6=419.4')
add('workspace card top-left',[22,752],'exact component bbox','rectangle corner','bottom-left','workspace card #233954 inclusive bbox [22,752,197,867]')
add('workspace card bottom-right',[198,868],'exact component bbox exclusive','rectangle corner','bottom-left','workspace card #233954 inclusive bbox [22,752,197,867]')
add('table header top-left',[284,688],'exact component bbox','rectangle corner','bottom-main','header #F3F6FB component inclusive bbox [284,688,1373,721]')
add('table header bottom-right',[1374,722],'exact component bbox exclusive','rectangle corner','bottom-right','header #F3F6FB component inclusive bbox [284,688,1373,721]')
add('first project separator left',[284,760],'exact color run','table rule','bottom-main','y760 exact #EBEFF5 run x284..1373')
add('second project separator right-exclusive',[1374,795],'exact color run exclusive','table rule','bottom-right','y795 exact #EBEFF5 run x284..1373')
add('In progress pill top-left',[1028,729],'exact component bbox','rectangle corner','bottom-right','#E7EFFF component bbox')
add('Done pill bottom-right',[1176,827],'exact component bbox exclusive','rectangle corner','bottom-right','#DCF5EC inclusive bbox [1028,799,1175,826]')
add('workspace title first ink top-left',[260,39],'visual estimate checked by dark pixel bounding ROI','text ink anchor','top-main','This is ink location, not DSL text block origin or baseline; font geometry may differ.')
text_regions={name:{'search_box':box,'ink_color':rgb,'bbox_exclusive':matching_bbox(box,tuple(rgb)),'method':'exact foreground pixels; antialiased outer pixels excluded'} for name,box,rgb in [
 ('title',[250,20,1000,75],[24,40,63]),
 ('chart_title',[275,325,650,365],[24,40,63]),
 ('table_title',[275,635,650,675],[24,40,63]),
 ('refund_value',[1040,190,1220,234],[24,40,63])
]}
# Chart evidence spans all 5 rules; bars occlude portions of intermediate lines.
grid=[]
for y in [405,441,477,513,549]:
    runs=[];start=None
    for x in range(320,981):
        hit=(x<980 and im.getpixel((x,y))==(231,237,245))
        if hit and start is None: start=x
        if not hit and start is not None: runs.append([start,x]);start=None
    grid.append({'y':y,'x_runs_exclusive':runs})
data={'task_id':'A15','recorded_at':datetime.now(timezone.utc).isoformat(),'source_path':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'canvas':[1440,900],'coordinate_convention':'left/top inclusive; continuous rectangles right/bottom exclusive; raster inclusive bboxes explicitly labelled in reference-pixels-v001.json','cards':cards,'anchors':anchors,'anchor_count':len(anchors),'text_ink_measurements':text_regions,'grid_rules':grid,'chart_geometry_inference':{'plot_left':333,'plot_right_exclusive':970,'plot_top_grid_y':405,'zero_y':549,'range_max':120,'height':144,'bar_width':54,'bar_center_x':[384,485,586,687,788,889],'bar_top_y_ratio_estimate':[484.2,462.6,473.4,441,451.8,419.4],'note':'subpixel tops estimated using input values and measured rule span; not asserted as source DSL geometry'},'limits':['Reference-only; reconstructed coordinates and measured errors intentionally null until producer/root measures output.','Exact-color bboxes do not establish font face, baseline, or rounded radius.','No reference generator, DSL tree, evaluator or hidden grading material accessed.']}
with (dest/'reference-anchors-v001.json').open('x',encoding='utf-8') as f:json.dump(data,f,ensure_ascii=False,indent=2)
print(json.dumps({'anchor_count':len(anchors),'cards':cards,'text':text_regions,'grid_rules':grid},ensure_ascii=False,indent=2))
