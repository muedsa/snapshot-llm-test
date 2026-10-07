from PIL import Image
from pathlib import Path
from collections import Counter, deque
import hashlib, json, shutil
from datetime import datetime, timezone

root = Path(r'D:\workspaces\gpt-6.1-sol-ultra')
source = root / 'tasks/A15-reference-reconstruction/inputs/reference.png'
destination = root / 'tmp/20261002-204314-6f31/A15/reference-measurements'
destination.mkdir(parents=True, exist_ok=True)
img = Image.open(source).convert('RGB')
def hexcolor(c): return '#' + ''.join(f'{i:02X}' for i in c)
def write_json(name, data):
    with (destination/name).open('x',encoding='utf-8') as f: json.dump(data,f,ensure_ascii=False,indent=2)
def save_new(name, image):
    with (destination/name).open('xb') as f: image.save(f,format='PNG')
with (destination/'reference-original-v001.png').open('xb') as f: f.write(source.read_bytes())
thumb=img.copy(); thumb.thumbnail((720,450)); save_new('reference-thumbnail-v001.png',thumb)
crops={
  'top-left':(0,0,670,300),
  'chart':(250,300,1012,607),
  'table':(250,614,1410,852),
  'right-and-sidebar-bottom':(1020,130,1410,606),
  'workspace-bottom':(0,730,240,900)
}
for key,box in crops.items(): save_new(f'reference-crop-{key}-v001.png',img.crop(box))
points={
 'sidebar':(10,500), 'main_background':(1410,500), 'white_card':(280,180),
 'card_border':(260,180), 'selected_nav':(25,140), 'workspace_card':(30,800),
 'brand_mint':(33,46), 'primary_button':(1190,65), 'bar_blue':(370,510),
 'chart_grid':(340,405), 'table_header':(290,690), 'table_separator':(310,760),
 'status_progress_fill':(1040,740), 'status_review_fill':(1040,775), 'status_done_fill':(1040,810),
 'activity_yellow':(1059,402), 'activity_blue':(1059,462), 'activity_green':(1059,522)
}
sampled=[{'name':name,'point':list(p),'rgb':list(img.getpixel(p)),'hex':hexcolor(img.getpixel(p)),'method':'exact input pixel'} for name,p in points.items()]
def runs_horizontal(y,x0=0,x1=1440,minlen=1):
    result=[]; start=x0; color=img.getpixel((x0,y))
    for x in range(x0+1,x1+1):
        c=img.getpixel((x,y)) if x<x1 else None
        if c!=color:
            if x-start>=minlen: result.append({'start_x':start,'end_x_inclusive':x-1,'length':x-start,'hex':hexcolor(color)})
            start=x;color=c
    return result
def runs_vertical(x,y0=0,y1=900,minlen=1):
    result=[]; start=y0;color=img.getpixel((x,y0))
    for y in range(y0+1,y1+1):
        c=img.getpixel((x,y)) if y<y1 else None
        if c!=color:
            if y-start>=minlen: result.append({'start_y':start,'end_y_inclusive':y-1,'length':y-start,'hex':hexcolor(color)})
            start=y;color=c
    return result
def component(seed):
    color=img.getpixel(seed); q=deque([seed]); seen={seed}; xx=[];yy=[]
    while q:
        x,y=q.popleft();xx.append(x);yy.append(y)
        for p in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
            if 0<=p[0]<img.width and 0<=p[1]<img.height and p not in seen and img.getpixel(p)==color:
                seen.add(p);q.append(p)
    return {'seed':list(seed),'hex':hexcolor(color),'pixel_count':len(seen),'bbox_inclusive':[min(xx),min(yy),max(xx),max(yy)]}
components={name:component(seed) for name,seed in {
 'selected_nav':(25,140),'button':(1190,65),'workspace_card':(30,800),
 'Apr_bar':(384,510),'May_bar':(485,510),'Jun_bar':(586,510),
 'Jul_bar':(687,510),'Aug_bar':(788,510),'Sep_bar':(889,510),
 'status_progress':(1040,740),'status_review':(1040,775),'status_done':(1040,810),
 'header_strip':(290,690)
}.items()}
data={
 'task_id':'A15','recorded_at':datetime.now(timezone.utc).isoformat(),
 'input_path':str(source),'input_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
 'dimensions':[img.width,img.height],'mode':img.mode,
 'top_colors':[{'rgb':list(c),'hex':hexcolor(c),'count':n} for c,n in Counter(img.getdata()).most_common(20)],
 'samples':sampled,'exact_color_connected_components':components,
 'horizontal_runs':{str(y):runs_horizontal(y,minlen=3) for y in (0,140,180,250,340,405,441,477,513,549,620,690,705,743,760,778,795,813,840,899)},
 'vertical_runs':{str(x):runs_vertical(x,minlen=3) for x in (10,220,260,270,500,644,650,999,1001,1028,1030,1040,1374,1399)},
 'qa_images':[{'name':'reference-original-v001.png','source_box':[0,0,1440,900],'purpose':'byte identical original QA view'}, {'name':'reference-thumbnail-v001.png','source_box':[0,0,1440,900],'size':[720,450],'purpose':'whole-layout thumbnail QA'}] + [ {'name':f'reference-crop-{key}-v001.png','source_box':list(box),'size':[box[2]-box[0],box[3]-box[1]],'purpose':'QA crop only, prohibited as reconstruction DSL asset'} for key,box in crops.items()],
 'method_limits':['No reference source-generation code or evaluator materials read.','Exact-color component bboxes represent non-antialiased pixels; rounded geometric bounds require straight-edge row/column intersections.','The pixel-space lower/right geometric bounds are exclusive; inclusive pixel bboxes are labelled explicitly.','No reconstructed output sampled yet; these are reference-only measurements.']
}
write_json('reference-pixels-v001.json',data)
print(json.dumps({'input_sha256':data['input_sha256'],'dimensions':data['dimensions'],'samples':sampled,'components':components,'qa_count':len(data['qa_images'])},ensure_ascii=False,indent=2))
