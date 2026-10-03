from PIL import Image
import os, json, hashlib
OUT = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\outputs\20261003-114508-flashmax\A17"
for n in sorted(os.listdir(OUT)):
    if n.endswith(".png"):
        im = Image.open(os.path.join(OUT, n))
        print(f"{n:20s} {im.size[0]}x{im.size[1]} {im.format} {os.path.getsize(os.path.join(OUT,n))}")
# BOM check
for n in sorted(os.listdir(OUT)):
    if n.endswith(".snapshot"):
        head = open(os.path.join(OUT, n), "rb").read(3)
        print(n, "BOM" if head == b"\xef\xbb\xbf" else "no-BOM", os.path.getsize(os.path.join(OUT,n)))
ex = json.load(open(os.path.join(OUT, "examples.json"), encoding="utf-8"))
for e in ex["examples"]:
    print(e["id"], "full", e["dsl_full_lines"], "printed", e["printed_lines"], "elided", e["elided_lines"], "renders", len(e["renders"]))