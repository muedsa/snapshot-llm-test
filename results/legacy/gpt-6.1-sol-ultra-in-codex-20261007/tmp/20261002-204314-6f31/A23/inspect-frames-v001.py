"""Read-only original-PNG inspection and labelled contact sheet. Never modifies final PNGs."""
from pathlib import Path
from PIL import Image, ImageDraw
import json, hashlib, datetime
base=Path(__file__).resolve().parent
meta=json.loads((base/'render-frame-manifest-v001.json').read_text(encoding='utf-8'))
records=[]
sheet=Image.new('RGB',(1260,900),'#10262A')
draw=ImageDraw.Draw(sheet)
for n,entry in enumerate(meta['frames']):
    p=Path(entry['image_path']); raw=p.read_bytes(); im=Image.open(p).convert('RGBA')
    alpha=im.getchannel('A'); hist=alpha.histogram()
    opaque=hist[255]; zero=hist[0]; partial=sum(hist[1:255])
    colors=im.getcolors(maxcolors=1000000)
    nontransparent={str(c):count for count,c in colors if c[3]>0}
    records.append({'frame':n+1,'source':str(p),'sha256':hashlib.sha256(raw).hexdigest(),'size':list(im.size),'original_mode':Image.open(p).mode,'transparent_pixels':zero,'opaque_pixels':opaque,'partial_alpha_pixels':partial,'alpha_extrema':list(alpha.getextrema()),'foreground_bbox':list(alpha.getbbox()),'visible_colors':nontransparent,'pass_size':im.size==(600,600),'pass_real_transparency':zero>300000 and opaque>20000 and alpha.getextrema()==(0,255)})
    # QA preview checkerboard is not a submitted/final work or a service response.
    bg=Image.new('RGBA',(600,600),'#E7EDEA'); d=ImageDraw.Draw(bg)
    for yy in range(0,600,30):
        for xx in range(0,600,30):
            if (xx//30+yy//30)%2==0:d.rectangle((xx,yy,xx+29,yy+29),fill='#CCD8D4')
    preview=Image.alpha_composite(bg,im).convert('RGB').resize((390,390),Image.Resampling.LANCZOS)
    x=20+(n%3)*420;y=35+(n//3)*440
    sheet.paste(preview,(x,y))
    draw.text((x,y+400),f"FRAME {n+1:02d}   {n*250} ms",fill='#EAF7F2')
result={'task_id':'A23','kind':'read_only_original_png_alpha_QA','checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'frames':records,'all_pass':all(r['pass_size'] and r['pass_real_transparency'] for r in records),'contact_sheet':'contact-sheet-v001.png','scope':'Pillow only reads originals and creates temporary QA preview; no final bytes changed.'}
(base/'png-alpha-audit-v001.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sheet.save(base/'contact-sheet-v001.png')
print(json.dumps({'pass':result['all_pass'],'frames':len(records),'alpha':[[r['transparent_pixels'],r['opaque_pixels'],r['partial_alpha_pixels']] for r in records],'contact_sheet':str(base/'contact-sheet-v001.png')}))
