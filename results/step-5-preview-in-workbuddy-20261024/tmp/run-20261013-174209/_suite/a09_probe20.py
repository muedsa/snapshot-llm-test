"""A09 探针：用多个小矩形精确标定 Transform 的坐标映射。"""
import sys
import time
from pathlib import Path

sys.path.insert(0, "tmp/run-20261013-174209/_suite")
import render as R  # noqa: E402

from PIL import Image  # noqa: E402
import io  # noqa: E402

TMP = Path("tmp/run-20261013-174209/A09")

MAT = "(0,1,0,0,-1,0,0,0,0,0,1,0,120,0,0,1)"

# 放 4 个 2x2 小方块在 4 个角，标定映射
MARKS = "".join(
    f'<Positioned left="{x}" top="{y}" width="2" height="2">'
    f'<Container color="#E54B4B"/></Positioned>'
    for x, y in [(0, 0), (118, 0), (0, 118), (118, 118)]
)
text = (f'<Snapshot type="png" background="#FFFFFF"><Container width="400" height="400">'
        f'<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE">'
        f'<Transform matrix="{MAT}" origin="(60,60)">'
        f'<SizedBox width="120" height="120"><Stack alignment="TOP_LEFT" fit="EXPAND" '
        f'clipBehavior="NONE">{MARKS}</Stack></SizedBox>'
        f'</Transform></Stack></Container></Snapshot>')
for attempt in range(3):
    r = R.post_render(text, "https://open-snapshot.muedsa.com/snapshot", timeout=90)
    if r.get("status") == 200:
        break
    time.sleep(2)
im = Image.open(io.BytesIO(r["body"])).convert("RGB")
pts = [(x, y) for y in range(400) for x in range(400)
       if all(abs(a - b) <= 20 for a, b in zip(im.getpixel((x, y)), (229, 75, 75)))]
print("mark pixels:", sorted(pts))
print()
print("局部点 -> 画布点:")
for lx, ly in [(0, 0), (118, 0), (0, 118), (118, 118)]:
    # 列主序矩阵 [[0,-1],[1,0]] + 平移 (120,0)，绕 origin (60,60)
    # 假设: canvas = origin + M @ (local - origin) + T
    # 试算 M=[[0,-1],[1,0]] (即 x'=-y, y'=x)
    dx, dy = lx - 60, ly - 60
    mx, my = -dy, dx
    print(f"  ({lx},{ly}) -> M@(l-o)=({mx},{my}) ; +o=({mx+60},{my+60}) ; "
          f"+o+(120,0)=({mx+180},{my+60})")
