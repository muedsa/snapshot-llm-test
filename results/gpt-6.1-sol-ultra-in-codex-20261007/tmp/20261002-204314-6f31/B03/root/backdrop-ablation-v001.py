from PIL import Image,ImageChops,ImageStat
import json,os
b=os.path.dirname(__file__);r=os.path.join(b,'..','requests')
a=Image.open(os.path.join(r,'B03-request-000005','response.png')).convert('RGBA')
z=Image.open(os.path.join(r,'B03-request-000007','response.png')).convert('RGBA')
d=ImageChops.difference(a,z);bbox=d.convert('RGB').getbbox()
out={'comparison':'actual original service PNG defaultSRC_OVER18 versus0','diff_bbox_rgb':bbox,'mean_absolute_channels':ImageStat.Stat(d).mean,'stripe_roi':[875,525,994,645],'stripe_mean_absolute_channels':ImageStat.Stat(d.crop((875,525,994,645))).mean,'note':'Pixel comparison supplements genuine full-image views5/7; no image bytes edited or used as final. Exact no-difference applies only to this configuration.'}
with open(os.path.join(b,'backdrop-ablation-v001.json'),'x',encoding='utf8') as f:json.dump(out,f,ensure_ascii=False,indent=2)
print(json.dumps(out,ensure_ascii=False))
