"""A09 探针：分离 matrix 平移分量与 origin 的作用。"""
import sys
import time
from pathlib import Path

sys.path.insert(0, "tmp/run-20261013-174209/_suite")
import render as R  # noqa: E402

from PIL import Image  # noqa: E402
import io  # noqa: E402

TMP = Path("tmp/run-20261013-174209/A09")

MARKS = "".join(
    f'<Positioned left="{x}" top="{y}" width="1" height="1">'
    f'<Container color="#E54B4B"/></Positioned>'
    for x, y in [(0, 0), (119, 0), (0, 119), (119, 119), (60, 60)]
)


def run(mat, origin, pos=(100, 100), label=""):
    oattr = f' origin="{origin}"' if origin else ""
    text = (f'<Snapshot type="png" background="#FFFFFF"><Container width="600" height="600">'
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
    pts = sorted((x, y) for y in range(600) for x in range(600)
                 if all(abs(a - b) <= 25 for a, b in zip(im.getpixel((x, y)), (229, 75, 75))))
    print(f"{label}: {pts}")


# 1: 纯线性 + origin
run("(0,1,0,0,-1,0,0,0,0,0,1,0,0,0,0,1)", "(60,60)", label="pure+origin")
# 2: 线性+平移120 + origin
run("(0,1,0,0,-1,0,0,0,0,0,1,0,120,0,0,1)", "(60,60)", label="trans120+origin")
# 3: 线性+平移120，无 origin
run("(0,1,0,0,-1,0,0,0,0,0,1,0,120,0,0,1)", None, label="trans120+no-origin")
# 4: 完整围绕 pivot 的矩阵（含平移 120,0），无 origin
run("(0,1,0,0,-1,0,0,0,0,0,1,0,120,0,0,1)", None, label="same as 3")
