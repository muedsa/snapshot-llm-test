from PIL import Image
m = Image.open("tmp/run-20261011-01/A07/preview/a07-v1-map.png"); m.load()
m.crop((1184, 110, 1600, 1000)).resize((832, 1780), Image.LANCZOS).save("tmp/run-20261011-01/A07/preview/a07-v1-crop-panel.png")
