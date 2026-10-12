"""Read-only measurements of actual Snapshot PNG. No image alterations."""
from PIL import Image
from pathlib import Path
import json, sys, hashlib, math, datetime
src=Path(sys.argv[1]).resolve();layout_path=Path(sys.argv[2]).resolve();out=Path(sys.argv[3]).resolve()
if out.exists():raise SystemExit('Refuse overwrite prior evidence')
im=Image.open(src).convert('RGB');p=im.load();layout=json.loads(layout_path.read_text(encoding='utf-8'))
cells=layout['cells'];index={c['id']:c for c in cells}
def rgb(i,x,y):
 c=index[i];return list(p[c['x']+x,c['y']+y])
def lum(v):return .2126*v[0]+.7152*v[1]+.0722*v[2]
def roi(i,bounds):
 x0,y0,x1,y1=bounds;c=index[i]
 rows=[[lum(rgb(i,x,y)) for x in range(x0,x1)] for y in range(y0,y1)]
 flat=[v for row in rows for v in row]
 dx=[abs(row[k+1]-row[k]) for row in rows for k in range(len(row)-1)]
 dy=[abs(rows[k+1][j]-rows[k][j]) for k in range(len(rows)-1) for j in range(len(rows[0]))]
 return {'local_xyxy':bounds,'min_luminance':min(flat),'max_luminance':max(flat),'max_adjacent_luminance_jump':max(dx+dy),'mean_adjacent_luminance_jump':sum(dx+dy)/len(dx+dy),'pixels_luminance_below70':sum(v<70 for v in flat),'pixel_count':len(flat)}
def row(i,x0,x1,y):
 vals=[rgb(i,x,y) for x in range(x0,x1)];l=[lum(v) for v in vals]
 return {'local_start':[x0,y],'local_end':[x1-1,y],'rgb':vals,'max_adjacent_luminance_jump':max(abs(l[k+1]-l[k]) for k in range(len(l)-1)),'luminance_range':max(l)-min(l)}
alpha=128/255;expected1=[127,(255*(1-alpha))*(1-alpha),255*alpha+255*(1-alpha)*(1-alpha)]
expected2=[127.5,127.5,255]
over=[]
for i,expected in [('01',expected1),('02',expected2)]:
 c=index[i];actual=rgb(i,180,100);patch={tuple(rgb(i,x,y)) for y in range(97,104) for x in range(177,184)}
 over.append({'id':i,'local_sample':[180,100],'global_sample':[c['x']+180,c['y']+100],'expected_float_rgb':expected,'expected_nearest_rgb':[round(v) for v in expected],'actual_rgb':actual,'absolute_delta_from_ideal':[abs(actual[j]-expected[j]) for j in range(3)],'uniform_7x7_patch':len(patch)==1,'patch_colors':[list(v) for v in sorted(patch)],'within_8bit_rounding_1':all(abs(actual[j]-expected[j])<=1 for j in range(3))})
blur_stats={i:{'text':roi(i,[60,67,240,100]),'background_inside':row(i,80,200,60),'background_outside':row(i,0,320,20),'shape':roi(i,[60,126,182,164])}for i in ['03','04']}
circle={'center_local':[160,120],'radius':100,'outside_gt_2px_count':0,'outside_gt_2px_nonwhite_count':0,'outside_gt_2px_examples':[],'ring_points':[]}
for y in range(240):
 for x in range(320):
  d=math.hypot(x+.5-160,y+.5-120)
  if d>102:
   circle['outside_gt_2px_count']+=1
   v=rgb('06',x,y)
   if v!=[255,255,255]:
    circle['outside_gt_2px_nonwhite_count']+=1
    if len(circle['outside_gt_2px_examples'])<20:circle['outside_gt_2px_examples'].append({'xy':[x,y],'rgb':v,'radial_distance':d})
for xy in [(59,120),(60,120),(61,120),(259,120),(260,120),(160,19),(160,20),(160,21),(160,219),(160,220),(160,221)]:circle['ring_points'].append({'xy':list(xy),'rgb':rgb('06',*xy)})
soft=[{'local_xy':list(xy),'rgb':rgb('05',*xy)}for xy in [(50,70),(55,70),(59,70),(60,70),(61,70),(70,70),(260,110),(265,110),(270,110),(280,110),(160,10),(160,20),(160,30),(160,50),(160,90),(160,200),(160,220),(160,230)]]
stripe_bounds=[]
for i in ['03','04']:
 c=index[i];pts=[]
 for x in range(320,332):pts.append({'local_xy':[x,20],'rgb':list(p[c['x']+x,c['y']+20])})
 stripe_bounds.append({'id':i,'outside_right_points':pts,'all_suite_background':all(v['rgb']==[237,241,245]for v in pts)})
r={'task_id':'A10','reviewer':'a10_audit_resume','measured_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'actual_service_png':str(src),'png_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'layout':str(layout_path),'dimensions':list(im.size),'dimensions_correct':im.size==(1440,1100),'overlap_samples':over,'blur_stats':blur_stats,'circle_clip':circle,'experiment05_soft_edges_and_gap_samples':soft,'stripe_experimental_boundary':stripe_bounds,'measurement_notes':['RGB values are actual decoded PNG bytes, not synthesized expectations.','Quantitative image sampling complements the separately logged actual visual inspection.','A 2px exclusion outside analytic circle avoids mixing antialias boundary coverage with geometric leakage.','Luminance edge energy is supporting comparison, not an inverse sigma estimator.']}
out.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'written':str(out),'overlap':over,'circle_outside_nonwhite':circle['outside_gt_2px_nonwhite_count'],'stripe_right_pass':[x['all_suite_background']for x in stripe_bounds],'text_metrics':{i:blur_stats[i]['text']for i in ['03','04']}},ensure_ascii=False))
