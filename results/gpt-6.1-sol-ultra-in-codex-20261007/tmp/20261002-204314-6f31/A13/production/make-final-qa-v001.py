from PIL import Image
from pathlib import Path
import hashlib,json
root=Path(__file__).resolve().parents[4]
temp=root/'tmp'/'20261002-204314-6f31'/'A13'
records=[]
originals={}
for name,request in [('symbol-color','000003'),('symbol-black','000004'),('brand-banner','000005'),('launch-poster','000006')]:
    src=temp/'requests'/f'A13-request-{request}'/'response.png'
    image=Image.open(src).convert('RGBA')
    originals[name]=image
    if image.width==image.height:
        small=image.resize((32,32),Image.Resampling.LANCZOS)
    else:
        contained=image.copy()
        contained.thumbnail((32,32),Image.Resampling.LANCZOS)
        small=Image.new('RGBA',(32,32),(0,0,0,0))
        small.alpha_composite(contained,((32-contained.width)//2,(32-contained.height)//2))
    p=temp/'production'/f'{name}-qa32-v001.png'
    small.save(p)
    plate=Image.new('RGBA',(32,32),'white');plate.alpha_composite(small)
    pp=temp/'production'/f'{name}-qa32-on-white-v001.png';plate.convert('RGB').save(pp)
    zoom=temp/'production'/f'{name}-qa32-nearest-zoom-v001.png';plate.resize((320,320),Image.Resampling.NEAREST).convert('RGB').save(zoom)
    full_plate=None
    if name=='symbol-black':
        white=Image.new('RGBA',image.size,'white');white.alpha_composite(image)
        full_plate=temp/'production'/'symbol-black-qa512-on-white-v001.png';white.convert('RGB').save(full_plate)
    records.append({'name':name,'original_png':str(src),'original_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'qa32':str(p),'qa32_white_plate':str(pp),'qa32_nearest_zoom':str(zoom),'qa512_white_plate':str(full_plate) if full_plate else None,'method':'QA only: icons resized32x32; applications contained with original aspect in32x32 transparent plate; white alpha-composite/NEAREST zoom aid inspection. Final response unchanged.'})
color=originals['symbol-color'];black=originals['symbol-black']
bad_black=sum(1 for r,g,b,a in black.getdata() if a>0 and (r!=0 or g!=0 or b!=0))
alpha_same=color.getchannel('A').tobytes()==black.getchannel('A').tobytes()
audit={'color_mode':'RGBA','black_mode':'RGBA','color_alpha_extrema':color.getchannel('A').getextrema(),'black_alpha_extrema':black.getchannel('A').getextrema(),'identical_alpha_arrays':alpha_same,'black_nontransparent_nonzero_rgb_count':bad_black,'black_nontransparent_pixel_count':sum(1 for r,g,b,a in black.getdata() if a>0),'both_icon_alpha_bounds':{'color':color.getchannel('A').getbbox(),'black':black.getchannel('A').getbbox()},'audit_pass':bad_black==0 and alpha_same,'method':'Read-only exact original RGBA alpha byte arrays and every nontransparent black pixel RGB; no tolerance or guessed service measurements.'}
(temp/'production'/'final-qa-provenance-v001.json').write_text(json.dumps({'records':records,'rgba_audit':audit},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(audit,ensure_ascii=False))
