from PIL import Image, ImageDraw
import glob, os
out='D:/mine/test/glm-5.3-flash/outputs/20261016T164020-m1/A23'
st='D:/mine/test/glm-5.3-flash/tmp/20261016T164020-m1/A23/steps'
reps=sorted(glob.glob('D:/mine/test/glm-5.3-flash/tmp/20261016T164020-m1/A23/renders/a23-frame-0*.resp'), key=os.path.getmtime)[-6:]
print('reps',len(reps))
pad=8; cell=260
sheet=Image.new('RGB',(pad+(cell+pad)*6, cell+pad*3+40),(232,236,242))
d=ImageDraw.Draw(sheet)
for i,fp in enumerate(reps):
    im=Image.open(fp)
    if im.mode!='RGBA': print('frame',i+1,'mode',im.mode)
    img=im.resize((cell,cell), Image.LANCZOS)
    sheet.paste(img,(pad+i*(cell+pad), pad+30), img)
    d.text((pad+i*(cell+pad)+cell//2-20, pad+8), f'F{i+1} t={i*250}ms', fill=(30,40,60))
cov=Image.open(out+'/cover.png')
cov.resize((900,600), Image.LANCZOS).save(st+'/a23-cover-half.png')
import numpy as np
for i,fp in enumerate(reps,1):
    a=np.array(Image.open(fp))[:,:,3]
    trans=(a==0).sum(); op=(a>250).sum()
    print(f'frame-{i:02d} alpha==0 {trans}  alpha>250 {op}  frac_transparent {trans/a.size:.3f}')
sheet.save(st+'/a23-frames-sheet.png')
print('sheet ok', sheet.size)
