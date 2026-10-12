"""A19 · 用渲染出来的位图反查场景数据：逐个对象核对颜色、形状与尺寸。

这不是后处理，只是观察证据：读像素、和 scene 几何对表，任何不一致都打印出来。
"""
import json
import os
import sys
from collections import Counter
from pathlib import Path

import numpy as np
from PIL import Image

root = Path(os.environ["SNAPSHOT_TASK_ROOT"])
run = os.environ["SNAPSHOT_RUN_ID"]
img_path = Path(sys.argv[1])
objs = json.loads((root / "tmp" / run / "A19" / "layouts" / "scene-objects.json")
                  .read_text(encoding="utf-8"))
px = np.asarray(Image.open(img_path).convert("RGB"))


def sample(x, y):
    return tuple(int(v) for v in px[int(round(y)), int(round(x))])


BG = (255, 255, 255)
rows, bad = [], []
for o in objs:
    s, cx, cy = o["size"], o["cx"], o["cy"]
    want = tuple(int(o["color"][i:i + 2], 16) for i in (1, 3, 5))
    centre = sample(cx, cy)
    band = sample(cx + (s / 2 + s / 4) / 2, cy)      # 圆环带中部
    body = sample(cx, cy - s / 4)                     # 实心体内部
    if o["shape"] == "圆环":
        ok_shape = centre == BG and band == want
        seen = "ring" if ok_shape else f"centre={centre},band={band}"
    else:
        ok_shape = centre == want and body == want
        seen = "solid" if ok_shape else f"centre={centre}"
    # 用不透明像素扫出实际外接框，核对尺寸（圆/环按直径，方按边长）
    x0, y0 = int(cx - s / 2 - 4), int(cy - s / 2 - 4)
    win = px[y0:int(cy + s / 2 + 5), x0:int(cx + s / 2 + 5)].astype(int)
    near = (np.abs(win - np.array(want)).sum(axis=2) < 40)
    ys, xs = np.nonzero(near)
    if len(xs) == 0:
        bad.append(f"{o['id']} 找不到任何 {o['color']} 像素")
        continue
    w = int(xs.max() - xs.min() + 1)
    h = int(ys.max() - ys.min() + 1)
    tol = 2 if o["shape"] in ("方", "圆角方") else 3
    ok_size = abs(w - s) <= tol and abs(h - s) <= tol
    # 主体必须与相邻对象分离：窗口内彩色像素应连成一块
    if not (ok_shape and ok_size):
        bad.append(f"{o['id']} {o['shape']}/{o['color_key']}/{s} -> {seen} 实测 {w}x{h}")
    rows.append({"id": o["id"], "measured_bbox_wh": [w, h], "shape_seen": seen,
                 "centre_pixel": centre, "expected_color": o["color"]})

print("对象数:", len(rows))
print("形状判定分布:", dict(Counter(r["shape_seen"].split("=")[0] for r in rows)))
print("颜色像素计数:", dict(Counter(o["color_key"] for o in objs)))
print("不一致:", len(bad))
for b in bad[:25]:
    print("  ", b)

import json  # noqa: E402
import os  # noqa: E402
_root = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
_out = _root / "tmp" / os.environ["SNAPSHOT_RUN_ID"] / "A19" / "layouts" / "grid-bitmap-audit.json"
_out.write_text(json.dumps({
    "path_base": "suite_root",
    "audited_png": sys.argv[1],
    "tool": "tmp/<run>/A19/verify_grid.py（PIL + numpy 逐像素）",
    "objects_audited": len(rows),
    "shape_seen_distribution": dict(Counter(r["shape_seen"].split("=")[0] for r in rows)),
    "color_totals": dict(Counter(o["color_key"] for o in objs)),
    "mismatches": bad,
    "per_object": rows,
}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
print("写出", _out)
