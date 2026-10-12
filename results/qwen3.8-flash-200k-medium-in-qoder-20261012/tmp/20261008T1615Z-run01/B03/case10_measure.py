"""case-10 测量脚本：按 data.json.bands 的坐标扫描成品 PNG，量出墨迹宽度/浓度/行距。

用法：python case10_measure.py --png <成品.png> --out case10-measure-vNN.json
（--out 的名字就是**下一版**要读的那个文件，所以本版印的是上一版的实测值。）

测量口径（写进页面页脚，也写进 json）：
- 背景取全图众数色（不能取 (0,0)：页眉有 6px 色带）；像素与背景的欧氏色距 > 40 记为墨迹。
- width：测量带内首列/末列墨迹之差（px），即该样本的实际排版宽度。
- ink：测量带内墨迹像素占带面积的比例（%），用来证明字重行之间确有浓淡差。
- pitch（仅 §04 行高栏）：把带内按行投影，取墨迹行段的中心，相邻中心之差的中位数即行距。
"""
import argparse
import json
import os
from pathlib import Path

import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("--png", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--remap", default="",
                    help="键名迁移，如 h-0=h-def,h-2=h-1.25；用于测量带改名后沿用上一版实测值")
a = ap.parse_args()

ROOT = Path(os.environ["SNAPSHOT_TASK_ROOT"])
RID = os.environ["SNAPSHOT_RUN_ID"]
DATA = json.loads((ROOT / "outputs" / RID / "B03" / "case-10" / "data.json")
                  .read_text(encoding="utf-8"))
px = np.asarray(__import__("PIL.Image", fromlist=["Image"]).open(a.png)
                .convert("RGB"), dtype=np.int16)
# 背景取全图众数色（不能取 (0,0)：页眉有 6px 色带，取到它会把整幅判成墨迹）
flat = px[::3, ::3].reshape(-1, 3)
codes = flat[:, 0] * 65536 + flat[:, 1] * 256 + flat[:, 2]
vals, cnts = np.unique(codes, return_counts=True)
c = int(vals[cnts.argmax()])
bg = np.array([(c >> 16) & 255, (c >> 8) & 255, c & 255], dtype=np.float64)


def ink_mask(x0, y0, x1, y1):
    box = px[int(y0):int(y1), int(x0):int(x1)].astype(np.float64)
    return ((box - bg) ** 2).sum(axis=2) > 40 ** 2


def measure(key, b):
    x0, x1 = b["x"]
    y0, y1 = b["y"]
    m = ink_mask(x0, y0, x1, y1)
    cols = m.any(axis=0)
    rows = m.any(axis=1)
    out = {"area_px": int(m.sum()), "band": [x0, y0, x1, y1]}
    out["w"] = round(float(np.where(cols)[0].max() - np.where(cols)[0].min() + 1),
                     1) if cols.any() else None
    out["ink"] = round(100.0 * float(m.sum()) / m.size, 2)
    if rows.any():
        idx = np.where(rows)[0]
        groups, cur = [], [idx[0]]
        for v in idx[1:]:
            if v - cur[-1] <= 2:
                cur.append(v)
            else:
                groups.append(cur)
                cur = [v]
        groups.append(cur)
        centers = [float(np.mean(g)) for g in groups]
        out["row_groups"] = len(groups)
        out["pitch"] = (round(float(np.median(np.diff(centers))), 1)
                        if len(centers) > 1 else None)
        out["first_row_top"] = round(y0 + centers[0], 1)
    return out


REMAP = dict(x.split("=") for x in a.remap.split(",") if x)
res, meta = {}, {}
for key, b in DATA["bands"].items():
    key = REMAP.get(key, key)
    r = measure(key, b)
    meta[key] = r
    if key.startswith("w-"):                       # 字重行看墨迹浓度
        res[key] = r["ink"]
    elif key.startswith("h-"):                     # 行高栏看行距
        res[key] = r.get("pitch")
    else:
        res[key] = r.get("w")

Path(a.out).write_text(json.dumps({
    "measured_png": a.png, "threshold": "与背景欧氏色距 > 40 记为墨迹",
    "units": {"w-": "墨迹面积占测量带百分比", "h-": "相邻两行墨迹中心间距 px",
              "其余": "测量带内首末墨迹列之差 px"},
    "values": res, "meta": meta}, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps(res, ensure_ascii=False, indent=1))
print("bands", len(DATA["bands"]), "->", a.out)
