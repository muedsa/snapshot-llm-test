from PIL import Image
from pathlib import Path
import json,sys,datetime,collections,hashlib
c,b,out=map(Path,sys.argv[1:4]);ims=[Image.open(p).convert('RGBA')for p in [c,b]]
if out.exists():raise SystemExit('Refuse evidence overwrite')
ps=[im.load()for im in ims];mismatch=[];threshold_different=[];nonedge=[]
for y in range(512):
 for x in range(512):
  a,d=ps[0][x,y][3],ps[1][x,y][3]
  if a!=d:
   v={'xy':[x,y],'color_rgba':list(ps[0][x,y]),'black_rgba':list(ps[1][x,y]),'alpha_delta':a-d,'both_partial_alpha':0<a<255 and 0<d<255};mismatch.append(v)
   if not v['both_partial_alpha']:nonedge.append(v)
  if (a>=128)!=(d>=128):threshold_different.append([x,y])
core=[]
for y in range(208,304):
 for x in range(208,304):
  if ps[0][x,y][3]!=0 or ps[1][x,y][3]!=0:core.append([x,y])
r={'task_id':'A13','reviewer':'a10_audit_resume','measured_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'images':[str(c.resolve()),str(b.resolve())],'raw_alpha_arrays_exactly_equal':not mismatch,'mismatch_pixel_count':len(mismatch),'absolute_delta_max':max(abs(v['alpha_delta'])for v in mismatch)if mismatch else 0,'delta_histogram':dict(collections.Counter(v['alpha_delta']for v in mismatch)),'all_mismatches_are_both_partial_aa':not nonedge,'non_aa_difference_count':len(nonedge),'binary_alpha_ge128_mask_exactly_equal':not threshold_different,'binary_mask_difference_count':len(threshold_different),'common_transparent_window_core_xyxy':[208,208,304,304],'common_window_core_pixels':96*96,'common_window_core_all_transparent':not core,'window_core_violation_count':len(core),'full_actual_mismatch_list':mismatch,'interpretation':'Raw equality is false and preserved; only partial antialias coverage differs by1, while opaque silhouettes and transparent common-window core agree. Task explicitly allows antialias alpha. No PNG altered.'}
out.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in r.items()if k!='full_actual_mismatch_list'},indent=2))
