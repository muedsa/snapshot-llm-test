from pathlib import Path
from PIL import Image
import json,collections
root=Path(__file__).resolve().parents[4]
temp=root/'tmp'/'20261002-204314-6f31'/'A13'
c=Image.open(temp/'requests'/'A13-request-000003'/'response.png').convert('RGBA')
b=Image.open(temp/'requests'/'A13-request-000004'/'response.png').convert('RGBA')
cp,bp=c.load(),b.load();diff=[]
for y in range(512):
    for x in range(512):
        ca,ba=cp[x,y][3],bp[x,y][3]
        if ca!=ba:diff.append({'x':x,'y':y,'color_rgba':cp[x,y],'black_rgba':bp[x,y],'alpha_delta':ca-ba})
r={'differing_alpha_pixel_count':len(diff),'maximum_alpha_delta':max(abs(d['alpha_delta']) for d in diff) if diff else 0,'delta_histogram':dict(collections.Counter(d['alpha_delta'] for d in diff)),'all_differences_antialiased_edge_pixels':all(0<d['color_rgba'][3]<255 or 0<d['black_rgba'][3]<255 for d in diff),'binary_nontransparent_alpha_support_identical':all((cp[x,y][3]>0)==(bp[x,y][3]>0) for y in range(512) for x in range(512)),'binary_alpha_ge128_identical':all((cp[x,y][3]>=128)==(bp[x,y][3]>=128) for y in range(512) for x in range(512)),'differences':diff,'method':'Every actual original512x512 RGBA pixel inspected; raw false array identity preserved in final-qa-provenance-v001.json. No source files changed.'}
(temp/'production'/'alpha-difference-review-v001.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:v for k,v in r.items() if k!='differences'},ensure_ascii=False))
print(json.dumps(diff[:20],ensure_ascii=False))
