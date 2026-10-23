"""成品细节复核：负压底色范围、行注释与绘图区的相对位置。"""
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

# 先在纯底纹区取样，拿到真实底色值
print("压差绘图区取样：白底 vs 底纹")
for x in (300, 700, 1200):
    print(f"  x={x} y=460:", tuple(int(c) for c in img[460, x]),
          " y=561:", tuple(int(c) for c in img[561, x]))
ref = np.array(img[462, 700], dtype=int)
print(f"  底纹参考值 {tuple(ref)}")
sub = img[459:562, :, :].astype(int)
pink = np.all(np.abs(sub - ref) <= 4, axis=2)
cols = np.where(pink.any(axis=0))[0]
print(f"  负压底纹列范围 x={cols.min()}..{cols.max()}  宽 {cols.max()-cols.min()+1}")
negx = [m["_model_only"]["x_px"][n["sample_id"]] for n in m["negative_samples"]]
print(f"  期望 x={min(negx)}..{max(negx)}  宽 {max(negx)-min(negx)+1:.1f}")

def ink_box(x0, x1, y0, y1):
    blk = img[y0:y1, x0:x1].mean(axis=2) < 210
    ys = np.where(blk.any(axis=1))[0]
    return None if not ys.size else (y0 + int(ys.min()), y0 + int(ys.max()))

print("\n行注释墨迹 vs 绘图区顶（不得压到折线区）")
for k, cfg in m["_model_only"]["rows"].items():
    tb = ink_box(762, 1382, int(cfg["header_top"]) - 2, int(cfg["y0"]) - 1)
    print(f"  {k}: 注释墨迹 y={tb}  绘图区顶 y={int(cfg['y0'])}  "
          f"{'不重叠' if tb and tb[1] < cfg['y0'] else '重叠！'}")
