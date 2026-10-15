from PIL import Image, ImageDraw

names = ['ent2-attr-entity', 'ent2-attr-bare', 'ent2-cdata',
         'ent2-bare-gt-text', 'ent2-attr-cjk']
ims = [(n, Image.open(f'tmp/run-20261011-01/A11/preview/{n}.png').convert('RGB')) for n in names]
W = max(i.width for _, i in ims)
H = sum(i.height + 26 for _, i in ims)
out = Image.new('RGB', (W, H), 'white')
dr = ImageDraw.Draw(out)
y = 0
for n, im in ims:
    dr.text((10, y + 6), n, fill=(150, 0, 0))
    y += 26
    out.paste(im, (0, y))
    y += im.height
out = out.resize((int(W * 1.6), int(H * 1.6)), Image.LANCZOS)
out.save('tmp/run-20261011-01/A11/preview/ent2-all.png')
print(out.size)