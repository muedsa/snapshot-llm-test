from PIL import Image
from pathlib import Path
import json
base=Path(__file__).resolve().parent
meta=json.loads((base/'render-baseline-v001.json').read_text(encoding='utf-8'))
data=json.loads((base/'scene-data-grid-v001.json').read_text(encoding='utf-8'))
image=Image.open(meta['image_path']).convert('RGB')
results=[]
for obj in data['objects']:
    l,t,r,b=map(int,obj['bbox']);points=[]
    for y in range(t,b):
        for x in range(l,r):
            px=image.getpixel((x,y))
            if max(255-v for v in px)>2:points.append((x,y))
    measured=[min(x for x,y in points),min(y for x,y in points),max(x for x,y in points)+1,max(y for x,y in points)+1]
    delta=[a-b for a,b in zip(measured,obj['bbox'])]
    if any(abs(d)>1 for d in delta):raise AssertionError((obj['id'],measured,obj['bbox']))
    cx,cy=map(int,obj['center'])
    expected=tuple(int(obj['color_hex'][i:i+2],16) for i in (1,3,5))
    sample=(cx+obj['size']*3//8,cy) if obj['shape']=='ring' else (cx,cy)
    actual=image.getpixel(sample)
    if actual!=expected:raise AssertionError((obj['id'],'color',actual,expected))
    result={'id':obj['id'],'expected_bbox':obj['bbox'],'measured_nonwhite_support_bbox':measured,'bbox_delta':delta,'color_sample_coordinate':sample,'sample_RGB':actual,'expected_RGB':expected}
    if obj['shape']=='ring':
        white=[]
        for x in range(cx-obj['size']//4,cx+obj['size']//4):
            if image.getpixel((x,cy))==(255,255,255):white.append(x)
        result['pure_white_inner_horizontal_span']=[min(white),max(white)+1]
        result['pure_white_inner_diameter']=len(white)
        result['expected_inner_diameter']=obj['inner_diameter']
        result['pure_white_core_note']='Antialias edge may remove up to 2px from the fully white core; geometric inner circle is exactly outer/2 in submitted DSL.'
        if not (obj['inner_diameter']-2<=len(white)<=obj['inner_diameter']):raise AssertionError((obj['id'],'ring inner white core',len(white)))
    results.append(result)
out={'actual_service_image':meta['image_path'],'objects_checked':len(results),'all_support_bbox_within1px':True,'all_body_color_samples_match':True,'actual_raw_PNG_not_modified':True,'method':'Measured raw service pixels inside each data-defined body ROI; excludes ID and gridline regions. Supports actual-image/source consistency, does not replace actual visual review.','objects':results}
with (base/'service-pixel-geometry-check-v001.json').open('x',encoding='utf-8') as f:json.dump(out,f,ensure_ascii=False,indent=2)
print(json.dumps({'objects_checked':len(results),'support_bbox_max_abs_delta':max(abs(d) for r in results for d in r['bbox_delta']),'ring_white_cores':[{k:o[k] for k in ['id','pure_white_inner_diameter','expected_inner_diameter']} for o in results if 'expected_inner_diameter' in o]}))
