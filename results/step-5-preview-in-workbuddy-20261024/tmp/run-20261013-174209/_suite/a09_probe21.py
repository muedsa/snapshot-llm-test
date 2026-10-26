"""A09 探针：用大色块标定 Transform 映射（避免小标记被裁）。"""
import sys
import time
from pathlib import Path

sys.path.insert(0, "tmp/run-20261013-174209/_suite")
import render as R  # noqa: E402

from PIL import Image  # noqa: E402
import io  # noqa: E402

TMP = Path("tmp/run-20261013-174209/A09")

MAT = "(0,1,0,0,-1,0,0,0,0,0,1,0,120,0,0,1)"

# 用三种颜色的 20x20 块放在三个不同位置
BLOCKS = (
    '<Positioned left="0" top="0" width="20" height="20"><Container color="#E54B4B"/></Positioned>'
    '<Positioned left="100" top="0" width="20" height="20"><Container color="#2364DB"/></Positioned>'
    '<Positioned left="0" top="100" width="20" height="20"><Container color="#EAB53B"/></Positioned>'
)
text = (f'<Snapshot type="png" background="#FFFFFF"><Container width="500" height="500">'
        f'<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE">'
        f'<Transform matrix="{MAT}" origin="(60,60)">'
        f'<SizedBox width="120" height="120"><Stack alignment="TOP_LEFT" fit="EXPAND" '
        f'clipBehavior="NONE">{BLOCKS}</Stack></SizedBox>'
        f'</Transform></Stack></Container></Snapshot>')
for attempt in range(3):
    r = R.post_render(text, "https://open-snapshot.muedsa.com/snapshot", timeout=90)
    if r.get("status") == 200:
        break
    time.sleep(2)
im = Image.open(io.BytesIO(r["body"])).convert("RGB")
for cname, c in [("A(0,0)", (229, 75, 75)), ("B(100,0)", (35, 100, 219)),
                 ("C(0,100)", (234, 181, 59))]:
    pts = [(x, y) for y in range(500) for x in range(500)
           if all(abs(a - b) <= 20 for a, b in zip(im.getpixel((x, y)), c))]
    if pts:
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        print(f"{cname}: canvas x {min(xs)}-{max(xs)} y {min(ys)}-{max(ys)}")
    else:
        print(f"{cname}: none")
print()
print("若无旋转（纯平移 +120,0）: A->(120,0), B->(220,0), C->(120,100)")
print("若 90° 顺时针绕(60,60): A(0,0)->(120,0)... 需按 origin 规则")
