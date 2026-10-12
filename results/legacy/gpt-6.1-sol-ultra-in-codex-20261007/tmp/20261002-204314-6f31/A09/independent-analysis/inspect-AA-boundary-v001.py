"""Focused read-only follow-up to preserved pure-fill T11 gold bound failure.

Tolerance remains 1.5 px. This documents the task's antialias edge exception,
using actual RGB mixtures at the analytic corner instead of changing tolerance.
"""
import argparse, datetime, hashlib, json, math, pathlib
from PIL import Image

parser=argparse.ArgumentParser()
parser.add_argument('png');parser.add_argument('facts');parser.add_argument('prior');parser.add_argument('output')
args=parser.parse_args()
im=Image.open(args.png).convert('RGB'); pixels=im.load()
facts=json.loads(pathlib.Path(args.facts).read_text(encoding='utf-8'))
prior=json.loads(pathlib.Path(args.prior).read_text(encoding='utf-8'))
sample=next(t for t in facts['transforms'] if t['id']=='T11')
old=next(t for t in prior['transforms'] if t['id']=='T11')['rectangles'][2]
rectangle=sample['rectangles'][2]; corners=rectangle['world_corners']
expected=old['expected_bounds']; color=tuple(int(rectangle['color'][i:i+2],16) for i in (1,3,5))
background=(255,255,255); direction=[color[i]-background[i] for i in range(3)]
length2=sum(v*v for v in direction)
supports=[]
for y in range(math.floor(expected['top']-3),math.ceil(expected['bottom']+3)):
 for x in range(math.floor(expected['left']-3),math.ceil(expected['right']+3)):
  value=pixels[x,y]
  alpha=sum((value[i]-background[i])*direction[i] for i in range(3))/length2
  residual=math.sqrt(sum((value[i]-(background[i]+alpha*direction[i]))**2 for i in range(3)))
  if .15<=alpha<=1.015 and residual<=18:
   supports.append(dict(pixel=[x,y],pixel_center=[x+.5,y+.5],rgb=value,estimated_paint_coverage=alpha,blend_residual_rgb=residual))
actual=dict(left=min(p['pixel'][0] for p in supports),top=min(p['pixel'][1] for p in supports),right=max(p['pixel'][0]+1 for p in supports),bottom=max(p['pixel'][1]+1 for p in supports))
error={k:actual[k]-expected[k] for k in expected}
left_pixels=[p for p in supports if p['pixel'][0]==actual['left']]
corner_checks=[]
for corner in corners:
 nearest=min(supports,key=lambda p:math.dist(p['pixel_center'],corner))
 corner_checks.append(dict(expected=corner,distance_px=math.dist(nearest['pixel_center'],corner),actual_pixel=nearest))
result=dict(generated_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),task_id='A09',
 source_png=str(pathlib.Path(args.png).resolve()),source_png_sha256=hashlib.sha256(pathlib.Path(args.png).read_bytes()).hexdigest(),
 previous_preserved_report=str(pathlib.Path(args.prior).resolve()),scope='Only T11 gold rectangle pure-fill bound failure; no artifact changes or tolerance increase',
 previous_pure_fill_pass=False,previous_left_error_px=old['bound_errors']['left'],tolerance_px=1.5,
 expected_bounds=expected,observed_AA_supported_bounds=actual,bound_errors=error,actual_left_boundary_pixels=left_pixels,
 corner_checks=corner_checks,supported_bounds_pass=max(abs(v) for v in error.values())<=1.5,
 antialias_exception_confirmed=max(abs(v) for v in error.values())<=1.5 and all(c['distance_px']<=1.5 for c in corner_checks),
 interpretation='The exact-color interior starts at x983; mixed-color real edge pixels exist at the predicted x981.464 corner. Preserve the 1.5359px pure-fill failure and record this measured AA-edge exception explicitly. All other v001 geometry checks remain unchanged.')
with pathlib.Path(args.output).open('x',encoding='utf-8') as f:
 json.dump(result,f,ensure_ascii=False,indent=2); f.write('\n')
print(json.dumps(result,ensure_ascii=False,indent=2))
