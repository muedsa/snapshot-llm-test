from PIL import Image
p = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tasks\A15-reference-reconstruction\inputs\reference.png"
im = Image.open(p).convert("RGB"); px = im.load()
for y in (128, 134, 140, 146, 152, 158):
    row = " ".join("%02X%02X%02X" % px[x, y] for x in range(30, 56, 3))
    print(y, row)
print("--- scan for green in the pill area")
best = None
for y in range(116, 164):
    for x in range(18, 64):
        r, g, b = px[x, y]
        if g > 120 and g - r > 30:
            best = (x, y, "#%02X%02X%02X" % (r, g, b))
            break
    if best: break
print("first greenish pixel:", best)
