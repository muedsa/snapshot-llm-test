"""A09 探针：确定 Transform+origin 在图谱结构下的精确映射。"""
import sys
import time
from pathlib import Path

sys.path.insert(0, "tmp/run-20261013-174209/_suite")
import render as R  # noqa: E402

from PIL import Image  # noqa: E402
import io  # noqa: E402

TMP = Path("tmp/run-20261013-174209/A09")

# 图谱实际结构：外层 Stack > Positioned(gx-60, gy-60) > Transform(origin=(60,60)) > SizedBox > Stack > Positioned
# 用一个已知点标定
MARKS = "".join(
    f'<Positioned left="{x}" top="{y}" width="1" height="1">'
    f'<Container color="#E54B4B"/></Positioned>'
    for x, y in [(0, 0), (119, 0), (0, 119), (119, 119), (60, 60)]
)


def run(mat, origin, label, pos=(200, 200)):
    oattr = f' origin="{origin}"' if origin else ""
    text = (f'<Snapshot type="png" background="#FFFFFF"><Container width="800" height="600">'
            f'<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE">'
            f'<Positioned left="{pos[0]}" top="{pos[1]}" width="120" height="120">'
            f'<Transform matrix="{mat}"{oattr}>'
            f'<SizedBox width="120" height="120"><Stack alignment="TOP_LEFT" fit="EXPAND" '
            f'clipBehavior="NONE">{MARKS}</Stack></SizedBox>'
            f'</Transform></Positioned>'
            f'</Stack></Container></Snapshot>')
    for attempt in range(3):
        r = R.post_render(text, "https://open-snapshot.muedsa.com/snapshot", timeout=90)
        if r.get("status") == 200:
            break
        time.sleep(2)
    if r.get("status") != 200:
        print(f"{label}: FAIL {(r.get('error') or '')[:80]}")
        return
    im = Image.open(io.BytesIO(r["body"])).convert("RGB")
    pts = sorted((x, y) for y in range(600) for x in range(800)
                 if all(abs(a - b) <= 25 for a, b in zip(im.getpixel((x, y)), (229, 75, 75))))
    print(f"{label} pos={pos}:")
    for lx, ly in [(0, 0), (119, 0), (0, 119), (60, 60)]:
        print(f"   local({lx},{ly}) -> ?")
    print(f"   pixels: {pts}")


# 图谱用的矩阵：90° 顺时针绕 (60,60)，即 around_pivot(mat_rotate_cw(90))
# mat_rotate_cw(90) = [[0,-1,0],[1,0,0]]; around_pivot = T(60,60) M T(-60,-60)
# = [[0,-1,120],[1,0,-60]]
# 列主序: (0,1,0,0, -1,0,0,0, 0,0,1,0, 120,-60,0,1)
run("(0,1,0,0,-1,0,0,0,0,0,1,0,120,-60,0,1)", "(60,60)", "atlas-T02-matrix")
