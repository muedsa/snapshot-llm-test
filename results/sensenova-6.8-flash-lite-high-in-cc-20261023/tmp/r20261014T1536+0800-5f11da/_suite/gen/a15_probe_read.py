"""A15 探针读数：从探针渲染里量出服务对 Inter 的真实排版行为。

四件事需要服务说了算，不能靠假设：
1. 「盒顶 → 墨迹顶」的 em 偏移——本任务首版沿用 A14 在 Noto Sans CJK SC 上的 0.32，
   Inter 字面框不同。探针在三个字号下画一条 1 px 红线标出目标墨迹顶，直接量
   (盒顶 → 实际墨迹顶) 得到真实 EM_INK_TOP。
2. 特殊字形 ¥ − – · → 是否缺字（豆腐块）。
3. borderRadiusTopLeft/TopRight 是否只在顶部生效（柱顶圆角）。
4. shape="CIRCLE" + border 是否画成圆环。
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve()
ROOT = HERE.parents[4]
# 只从目录名取 run_id，不写死盘符；与 PATHS.md 的可迁移要求一致。
os.environ.setdefault(
    "SNAPSHOT_RUN_ID", HERE.parents[2].parent.name)
sys.path.insert(0, str(ROOT / "tools"))
import suite as S  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

TMP = S.task_dirs("A15")[1]
P = TMP / "preview" / "a15-probe.png"

A = np.asarray(Image.open(P).convert("RGB")).astype(int)
RED = np.array([238, 17, 17])
INK = np.array([24, 40, 63])
MINT = np.array([100, 219, 182])
BLUE = np.array([36, 92, 228])
EM_INK_TOP = 0.32        # 本任务当前假设值，探针就是来验证它的


def ink_box(x0, y0, x1, y1, tol=60):
    seg = A[y0:y1 + 1, x0:x1 + 1]
    d = np.abs(seg - INK).max(axis=2)
    m = d < tol
    ys, xs = np.nonzero(m)
    if not len(xs):
        return None
    return [int(xs.min()) + x0, int(ys.min()) + y0,
            int(xs.max()) + x0, int(ys.max()) + y0]


def red_line_x(y, x0=50, x1=700):
    d = np.abs(A[y, x0:x1] - RED).max(axis=1)
    xs = np.flatnonzero(d < 40)
    return (int(xs.min()) + x0, int(xs.max()) + x0, int(len(xs))) if len(xs) else None


print("== 画布尺寸 ==", A.shape[1], "x", A.shape[0])

# 探针页布局（与 a15_pages.build_probe 同步）：
#   字重对照块 y = 56 / 160 / 264；特殊字形行墨迹顶 376；
#   柱顶圆角柱 x = 80/170/260 顶 y = 502；圆环圆心 y = 656；
#   字号标定块墨迹顶 y = 708 / 764 / 820（对应 13/22/36 px）。
print("\n== ① EM_INK_TOP 校准（红线 y 即目标墨迹顶；(实际墨迹顶 − 盒顶)/字号 = 实测偏移）==")
for sz, y_target in ((13.0, 708), (22.0, 764), (36.0, 820)):
    box_top = y_target - EM_INK_TOP * sz   # build_probe 里写的盒顶
    rl = red_line_x(y_target - 1)
    ib = ink_box(60, y_target - 2, 700, y_target + int(sz * 1.6))
    if ib and rl:
        off = ib[1] - box_top
        print("  fontSize %5g  盒顶 %7.2f  目标墨迹顶 %d  实测墨迹顶 %d  "
              "→ em=%6.4f" % (sz, box_top, y_target, ib[1], off / sz))
    else:
        print("  fontSize %5g  未检出（红线 %s 墨迹 %s）" % (sz, rl, ib))

print("\n== ② 特殊字形是否缺字（缺字会画出空心方框，宽度异常且内部为空）==")
yrow = 376
ib = ink_box(60, yrow - 6, 1400, yrow + 30)
print("  特殊字形行整体墨迹框：", ib)

print("\n== ③ 柱顶圆角（borderRadiusTopLeft / borderRadiusTopRight）==")
for i, cx in enumerate((80, 170, 260)):
    r = (0.0, 3.0, 6.0)[i]
    seg = A[498:540, cx:cx + 54]
    m = np.abs(seg - BLUE).max(axis=2) < 60
    if not m.any():
        print("  柱 %d 未检出" % i)
        continue
    ys, xs = np.nonzero(m)
    top = ys.min() + 498
    toprow = np.flatnonzero(m[0])          # 顶行填充宽度：圆角会让它变窄
    print("  柱 %d radius %g  顶行 y=%d x %d..%d（宽 %d / 54）"
          % (i, r, top, toprow.min() + cx, toprow.max() + cx, len(toprow)))

print("\n== ④ 圆环（shape=CIRCLE + border）==")
seg = A[620:692, 74:138]
m = np.abs(seg - MINT).max(axis=2) < 40
ys, xs = np.nonzero(m)
if len(xs):
    print("  mint 描边 bbox x %d..%d y %d..%d"
          % (xs.min() + 74, xs.max() + 74, ys.min() + 620, ys.max() + 620))

