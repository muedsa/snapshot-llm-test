# -*- coding: utf-8 -*-
"""A14：把 renders/ 最新终版响应映射为 card-Kxx.png；并生成 2×4 接触表（一致性参照，不替代逐张查看）。"""
import io, sys, os, re, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from PIL import Image
RUN = "20261016T164020-m1"
REND = f"tmp/{RUN}/A14/renders"
OUT = f"outputs/{RUN}/A14"
copied = {}
for f in sorted(os.listdir(REND)):
    m = re.match(r"card-K(\d\d)-v(\d\d)-(\d+)\.resp$", f)
    if not m:
        continue
    k, v, ts = m.groups()
    key = f"K{k}"
    prev = copied.get(key)
    if not prev or (v, ts) > (prev[1], prev[2]):
        copied[key] = (f, v, ts)
for k, (f, v, ts) in sorted(copied.items()):
    os.replace(os.path.join(REND, f), os.path.join(REND, "?TMP?" + f)) if False else None
for k, (f, v, ts) in sorted(copied.items()):
    import shutil
    shutil.copyfile(os.path.join(REND, f), os.path.join(OUT, f"card-{k}.png"))
    print("copied", k, "v" + v, ts)

# 接触表 2 列 × 4 行
cell_w, cell_h, gap = 1200 // 2, 630 // 2, 12
W2, H2 = cell_w * 2 + gap * 3, cell_h * 4 + gap * 5
sheet = Image.new("RGB", (W2, H2), (24, 32, 54))
for i, k in enumerate([f"K{n:02d}" for n in range(1, 9)]):
    im = Image.open(os.path.join(OUT, f"card-{k}.png")).resize((cell_w, cell_h), Image.LANCZOS)
    r, c = divmod(i, 2)
    sheet.paste(im, (gap + c * (cell_w + gap), gap + r * (cell_h + gap)))
sheet.save(f"tmp/{RUN}/A14/steps/contact-sheet.png")
print("contact sheet ok", sheet.size)
