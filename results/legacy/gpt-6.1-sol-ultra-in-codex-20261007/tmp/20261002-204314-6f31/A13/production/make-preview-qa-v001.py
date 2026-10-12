from PIL import Image
from pathlib import Path
import json,hashlib
root=Path(__file__).resolve().parents[4]
temp=root/'tmp'/'20261002-204314-6f31'/'A13'
records=[]
for direction,request in [('direction-A','000001'),('direction-B','000002')]:
    src=temp/'requests'/f'A13-request-{request}'/'response.png'
    image=Image.open(src).convert('RGBA')
    small=image.resize((32,32),Image.Resampling.LANCZOS)
    small_path=temp/'production'/f'preview-{direction}-32-v001.png'
    small.save(small_path)
    plate=Image.new('RGBA',(32,32),'white')
    plate.alpha_composite(small)
    plate_path=temp/'production'/f'preview-{direction}-32-on-white-v001.png'
    plate.convert('RGB').save(plate_path)
    zoom=plate.resize((320,320),Image.Resampling.NEAREST)
    zoom_path=temp/'production'/f'preview-{direction}-32-nearest-zoom-v001.png'
    zoom.convert('RGB').save(zoom_path)
    records.append({'direction':direction,'original_png':str(src),'original_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'qa_32_rgba':str(small_path),'qa_32_white_plate':str(plate_path),'qa_32_nearest_zoom':str(zoom_path),'actual_png_mode':image.mode,'alpha_extrema':image.getchannel('A').getextrema(),'final_png_untouched':True,'method':'QA-only LANCZOS thumbnail; white compositing and NEAREST320 enlargement only aid inspection. None are final artifacts.'})
(temp/'production'/'preview-qa-provenance-v001.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(records,ensure_ascii=False))
