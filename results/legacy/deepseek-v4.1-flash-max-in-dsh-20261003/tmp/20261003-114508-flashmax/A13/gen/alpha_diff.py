from PIL import Image
import json
OUT = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\outputs\20261003-114508-flashmax\A13"
a = Image.open(OUT + r"\symbol-color.png").convert("RGBA").getchannel("A")
b = Image.open(OUT + r"\symbol-black.png").convert("RGBA").getchannel("A")
da = a.load(); db = b.load()
w, h = a.size
diff = 0; geo = 0; maxd = 0; samples = []
for y in range(h):
    for x in range(w):
        va, vb = da[x, y], db[x, y]
        if va != vb:
            diff += 1
            maxd = max(maxd, abs(va - vb))
            if (va == 255) != (vb == 255):
                geo += 1
                if len(samples) < 8: samples.append([x, y, va, vb])
solid_a = sum(1 for y in range(h) for x in range(w) if da[x, y] == 255)
solid_b = sum(1 for y in range(h) for x in range(w) if db[x, y] == 255)
print(json.dumps({"alpha_diff_pixels": diff, "max_alpha_delta": maxd,
  "solid255_color": solid_a, "solid255_black": solid_b,
  "solid_geometry_differences": geo, "samples": samples}, indent=2))
