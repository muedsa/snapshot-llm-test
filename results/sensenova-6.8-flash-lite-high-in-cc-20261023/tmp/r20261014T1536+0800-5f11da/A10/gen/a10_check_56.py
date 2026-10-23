"""A10 ⑤⑥ 对照：⑥ 必须在圆内与 ⑤ 逐像素相同、圆外为白底。

⑤⑥ 共享同一份基础场景、颜色、阴影与滤镜参数，唯一差异是最外层多一个圆形裁剪。
所以圆内两格应该完全一致，圆外只有 ⑥ 被裁掉。

用法：
  python -I tmp/<rid>/A10/gen/a10_check_56.py <png 相对路径> <label>
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve()
ROOT = HERE.parents[4]

O5 = (10, 10)      # ⑤ 区域原点（subset 画布布局）
O6 = (338, 10)     # ⑥ 区域原点
CIRC = (160, 120, 100)   # 圆心（区域局部）与半径

# 圆内取样点（区域局部）：必须 ⑤⑥ 完全相同
INSIDE = {
    "dark_rect1_100_120": (100, 120),
    "dark_rect2_230_70": (230, 70),
    "transparent_gap_160_120": (160, 120),
    "light_rect_230_180": (230, 180),
    "near_center_160_120": (160, 120),
    "quarter_160_30": (160, 30),
}
# 圆外取样点：⑥ 应为白底 (255,255,255)，⑤ 应有场景内容
OUTSIDE = {
    "corner_16_16": (16, 16),
    "left_mid_16_120": (16, 120),
    "bottom_mid_160_225": (160, 225),
    "top_mid_160_5": (160, 5),
}
# 圆周上的点（应抗锯齿过渡）
EDGE = {"on_circle_left_60_120": (60, 120), "on_circle_right_260_120": (260, 120),
        "on_circle_top_160_20": (160, 20), "on_circle_bottom_160_220": (160, 220)}


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    png_rel, label = sys.argv[1], sys.argv[2]
    im = Image.open(ROOT / png_rel).convert("RGBA")
    print("png", png_rel, "size", im.size)
    rec = {"source_png": png_rel, "image_size": list(im.size)}

    def grab(origin, pts):
        return {k: list(im.getpixel((origin[0] + x, origin[1] + y)))
                for k, (x, y) in pts.items()}

    inside5, inside6 = grab(O5, INSIDE), grab(O6, INSIDE)
    outside5, outside6 = grab(O5, OUTSIDE), grab(O6, OUTSIDE)
    edge5, edge6 = grab(O5, EDGE), grab(O6, EDGE)

    rec["inside_5"] = inside5
    rec["inside_6"] = inside6
    rec["outside_5"] = outside5
    rec["outside_6"] = outside6
    rec["edge_5"] = edge5
    rec["edge_6"] = edge6

    worst = 0
    for k in INSIDE:
        d = max(abs(inside5[k][i] - inside6[k][i]) for i in range(4))
        worst = max(worst, d)
        print("inside %-26s ⑤ %-16s ⑥ %-16s diff=%d" % (k, inside5[k], inside6[k], d))
    print("圆内最大逐像素差 =", worst)
    for k in OUTSIDE:
        print("outside %-26s ⑤ %-16s ⑥ %s" % (k, outside5[k], outside6[k]))
    for k in EDGE:
        print("edge    %-26s ⑤ %-16s ⑥ %s" % (k, edge5[k], edge6[k]))

    import os
    out = ROOT / "tmp" / os.environ.get("SNAPSHOT_RUN_ID") / "A10" / (
        "check-56-" + label + ".json")
    out.write_text(json.dumps(rec, ensure_ascii=False, indent=2), encoding="utf-8")
    print("written", out.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
