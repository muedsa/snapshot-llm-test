"""复核 2：负压底纹的精确列范围（按每列底色像素数量，滤掉折线抗锯齿假命中）。"""
import json, sys
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0, str(Path(__file__).resolve().parent))
import a05_io as IO
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
_, tmp = IO.dirs()
m = json.loads((tmp / "model.json").read_text(encoding="utf-8"))["model"]
img = np.asarray(Image.open(Path(sys.argv[1])).convert("RGB"))

ref = np.array((252, 238, 238), dtype=int)
sub = img[458:563, :, :].astype(int)
pink = np.all(np.abs(sub - ref) <= 4, axis=2)
cnt = pink.sum(axis=0)
cols = np.where(cnt > 30)[0]          # 底纹应贯穿绘图区全高（105 行）
print(f"底纹贯穿列 x={cols.min()}..{cols.max()}  共 {cols.size} 列  "
      f"（该列底色像素 {cnt[cols].min()}–{cnt[cols].max()} / 105 行）")
negx = [m["_model_only"]["x_px"][n["sample_id"]] for n in m["negative_samples"]]
print(f"期望 x={min(negx):.1f}..{max(negx):.1f}  宽 {max(negx)-min(negx)+1:.1f}px")
print(f"负压采样点 x: " + ", ".join(f'{n["time"]}={x:.1f}'
      for n, x in zip(m["negative_samples"], negx)))
# 底纹不该越过这两个端点：检查端点外 6px 是否仍是纯白
for x in (min(negx) - 8, max(negx) + 8):
    xi = int(round(x))
    col = img[458:563, xi]
    print(f"  端点外 x={xi}: 底色像素 {(np.all(np.abs(col.astype(int)-ref)<=4, axis=1)).sum()}/105  "
          f"样本 {tuple(int(c) for c in col[52])}")
