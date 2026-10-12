import sys
from PIL import Image

p = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004\outputs\20261004-182918\A18\three-act-story.png"
im = Image.open(p).convert("RGB")
px = im.load()
cx, cy = int(sys.argv[1]), int(sys.argv[2])
print("scan y=%d (cy-28)" % (cy - 28))
for x in range(cx - 44, cx + 45):
    print(x, x - cx, px[x, cy - 28])