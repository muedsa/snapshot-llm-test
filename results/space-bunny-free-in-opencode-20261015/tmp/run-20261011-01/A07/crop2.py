from PIL import Image
im = Image.open("tmp/run-20261011-01/A07/preview/a07-v1-card.png"); im.load()
im.crop((0, 1150, 720, 1280)).resize((1440, 260), Image.LANCZOS).save("tmp/run-20261011-01/A07/preview/a07-v1-card-foot.png")
m = Image.open("tmp/run-20261011-01/A07/preview/a07-v1-map.png"); m.load()
m.crop((820, 220, 1180, 560)).resize((1080, 1020), Image.LANCZOS).save("tmp/run-20261011-01/A07/preview/a07-v1-crop-cross.png")
m.crop((820, 560, 1180, 990)).resize((1080, 1290), Image.LANCZOS).save("tmp/run-20261011-01/A07/preview/a07-v1-crop-right.png")
print("ok")
