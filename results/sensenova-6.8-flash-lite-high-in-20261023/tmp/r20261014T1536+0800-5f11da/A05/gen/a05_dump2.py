"""诊断 2：在给定 x 列附近找「最饱和」的像素，判断标记究竟画在哪。"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import a05_io as IO  # noqa: E402
import a05_inspect as INS  # noqa: E402

_, tmp = IO.dirs()
m = json.loads((tmp / "model.json").read_text(encoding="utf-8"))["model"]
X = m["_model_only"]["x_px"]
Y = m["_model_only"]["y_px"]

img = np.asarray(Image.open(Path(sys.argv[1])).convert("RGB"))
print(f"图像 {img.shape[1]}x{img.shape[0]}")

TARGETS = [("temperature_c", "S01"), ("temperature_c", "S09"),
           ("humidity_pct", "S01"), ("pressure_kpa", "S12"),
           ("pressure_kpa", "S06"), ("temperature_c", "S05"),
           ("humidity_pct", "S06")]

for key, sid in TARGETS:
    cx = int(round(X[sid]))
    v = Y[key][sid]
    hexc = INS.ROWS[key][0]
    if v is None:
        print(f"\n{key} {sid} 缺测 (x={cx})，找 WEAK 灰环：")
        win = img[max(0, cx - 12):cx + 13, 200:600]
        ma = INS.series_mask(win, "#94A3B8", min_dark=20, tol=60, min_chroma=0)
        ys, xs = np.where(ma)
        if ys.size:
            print(f"   命中 {ys.size} 像素, x∈[{xs.min() + cx - 12},{xs.max() + cx - 12}]"
                  f" y∈[{ys.min() + 200},{ys.max() + 200}] 最暗 "
                  f"{tuple(int(c) for c in win[ys[np.argmin(win[ys, xs].mean(axis=1))], xs[np.argmin(win[ys, xs].mean(axis=1))]])}")
        else:
            print("   无命中")
        continue
    cy = int(round(v))
    print(f"\n{key} {sid} = {v} 期望标记中心 ({cx},{cy}) 色 {hexc}")
    for (y0, y1) in [(cy - 12, cy + 13), (cy - 40, cy + 41)]:
        win = img[y0:y1, cx - 12:cx + 13]
        ma = INS.series_mask(win, hexc)
        if key == "pressure_kpa":
            ma |= INS.series_mask(win, "#DC2626")
        ys, xs = np.where(ma)
        if ys.size:
            print(f"   y窗口[{y0},{y1}) 命中 {ys.size} 像素, "
                  f"x∈[{xs.min() + cx - 12},{xs.max() + cx - 12}] "
                  f"y∈[{ys.min() + y0},{ys.max() + y0}] 中心偏移 "
                  f"({xs.mean() + cx - 12 - cx:.1f},{ys.mean() + y0 - cy:.1f})")
        else:
            print(f"   y窗口[{y0},{y1}) 无命中")
    # 该列最饱和的几行
    col = img[cy - 40:cy + 41, cx]
    ch = col.max(axis=1).astype(int) - col.min(axis=1).astype(int)
    top = np.argsort(ch)[::-1][:5]
    print("   该列最饱和 5 行:",
          [(int(t + cy - 40), tuple(int(c) for c in col[t]), int(ch[t])) for t in top])
