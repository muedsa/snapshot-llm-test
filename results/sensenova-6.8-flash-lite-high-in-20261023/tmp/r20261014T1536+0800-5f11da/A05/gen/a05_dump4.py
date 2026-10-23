"""诊断 4：明细表逐行墨迹带的真实像素位置。"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0, str(Path(__file__).resolve().parent))
import a05_io as IO
import a05_inspect as INS

_, tmp = IO.dirs()
m = __import__("json").loads((tmp / "model.json").read_text(encoding="utf-8"))["model"]
img = np.asarray(Image.open(Path(sys.argv[1])).convert("RGB"))
tbl = INS.ink_mask(img[INS.TABLE_Y:INS.TABLE_Y + INS.TABLE_H, 60:1360], lum_max=210.0)
prof = tbl.any(axis=1)
print("墨迹带 (相对 TABLE_Y, 绝对 y):")
for a, b in INS.run_lengths(prof):
    print(f"  [{a:3d},{b:3d}]  y={INS.TABLE_Y + a:4d}..{INS.TABLE_Y + b:4d}  "
          f"高 {b - a + 1}")
print("\n逐行窗口实际抓到的墨迹行：")
for i, s in enumerate(m["samples"]):
    yy = INS.T_ROW0 + i * INS.T_PITCH
    lo = int(np.clip(int(yy - 4) - INS.TABLE_Y, 0, tbl.shape[0] - 1))
    hi = int(np.clip(int(yy + INS.T_PITCH + 3) - INS.TABLE_Y, 0, tbl.shape[0] - 1))
    rows = np.where(prof[lo:hi])[0] + lo
    print(f"  行{i:2d} {s['time']} yy={yy:.1f} 窗口[{lo},{hi}) 墨迹相对行 "
          f"{rows.tolist() if rows.size < 40 else str(rows.size) + ' 行'}")
