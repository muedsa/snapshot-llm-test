from PIL import Image
im = Image.open("tmp/run-20261011-01/A08/preview/a08-v4.png"); im.load()
crops = {
  "z1-entry": (60, 540, 360, 770),
  "z3-exit": (840, 420, 1110, 620),
  "z5-doorE": (900, 380, 1110, 520),
}
for k,(a,b,c,d) in crops.items():
    im.crop((a,b,c,d)).resize(((c-a)*3,(d-b)*3), Image.LANCZOS).save(f"tmp/run-20261011-01/A08/preview/a08-v4-{k}.png")
print("ok")
