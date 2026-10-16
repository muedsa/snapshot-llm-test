from PIL import Image
for name in ["symbol-color.png","symbol-black.png","brand-banner.png","launch-poster.png"]:
    p = f"outputs/run-20261016/A13/{name}"
    im = Image.open(p)
    print(name, im.size)
