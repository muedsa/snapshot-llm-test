"""A09 探针：Transform 作为外层 Stack 直接子节点时的线性变换。"""
import sys
import time
from pathlib import Path

sys.path.insert(0, "tmp/run-20261013-174209/_suite")
import render as R  # noqa: E402

from PIL import Image  # noqa: E402
import io  # noqa: E402

TMP = Path("tmp/run-20261013-174209/A09")

MARK = '<Positioned left="10" top="20" width="20" height="10"><Container color="#E54B4B"/></Positioned>'


def run(mat, label, origin=None):
    oattr = f' origin="{origin}"' if origin else ""
    text = (f'<Snapshot type="png" background="#FFFFFF"><Container width="400" height="400">'
            f'<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE">'
            f'<Transform matrix="{mat}"{oattr}>'
            f'<SizedBox width="120" height="120"><Stack alignment="TOP_LEFT" fit="EXPAND" '
            f'clipBehavior="NONE">{MARK}</Stack></SizedBox>'
            f'</Transform></Stack></Container></Snapshot>')
    for attempt in range(3):
        r = R.post_render(text, "https://open-snapshot.muedsa.com/snapshot", timeout=90)
        if r.get("status") == 200:
            break
        time.sleep(2)
    if r.get("status") != 200:
        print(f"{label}: FAIL {(r.get('error') or '')[:90]}")
        return
    im = Image.open(io.BytesIO(r["body"])).convert("RGB")
    pts = [(x, y) for y in range(400) for x in range(400)
           if all(abs(a - b) <= 20 for a, b in zip(im.getpixel((x, y)), (229, 75, 75)))]
    if pts:
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        print(f"{label}: x {min(xs)}-{max(xs)} y {min(ys)}-{max(ys)} "
              f"size {max(xs)-min(xs)+1}x{max(ys)-min(ys)+1}")
    else:
        print(f"{label}: none")


# 恒等
run("(1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1)", "identity")
# 纯线性 swap
run("(0,1,0,0,1,0,0,0,0,0,1,0,0,0,0,1)", "swap")
# 90° 顺时针纯线性 [[0,-1],[1,0]]
run("(0,1,0,0,-1,0,0,0,0,0,1,0,0,0,0,1)", "rot90cw")
# 90° 顺时针 + 平移 120,-60（围绕 60,60）
run("(0,1,0,0,-1,0,0,0,0,0,1,0,120,-60,0,1)", "rot90cw+pivot")
