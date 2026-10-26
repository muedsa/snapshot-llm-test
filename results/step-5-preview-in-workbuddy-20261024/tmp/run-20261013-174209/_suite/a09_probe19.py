"""A09 探针：确定 Transform widget + origin 的正确定位方式。"""
import sys
import time
from pathlib import Path

sys.path.insert(0, "tmp/run-20261013-174209/_suite")
import render as R  # noqa: E402

from PIL import Image  # noqa: E402
import io  # noqa: E402

TMP = Path("tmp/run-20261013-174209/A09")

MAT = "(0,1,0,0,-1,0,0,0,0,0,1,0,120,0,0,1)"   # 90° 顺时针绕 (60,60)
RECT = '<Positioned left="8" top="8" width="28" height="92"><Container color="#E54B4B"/></Positioned>'


def measure(body, w=400, h=400):
    text = (f'<Snapshot type="png" background="#FFFFFF"><Container width="{w}" height="{h}">'
            f'<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE">{body}</Stack>'
            f'</Container></Snapshot>')
    for attempt in range(3):
        r = R.post_render(text, "https://open-snapshot.muedsa.com/snapshot", timeout=90)
        if r.get("status") == 200:
            break
        time.sleep(2)
    if r.get("status") != 200:
        return "FAIL " + (r.get("error") or "")[:80]
    im = Image.open(io.BytesIO(r["body"])).convert("RGB")
    pts = [(x, y) for y in range(h) for x in range(w)
           if all(abs(a - b) <= 14 for a, b in zip(im.getpixel((x, y)), (229, 75, 75)))]
    if not pts:
        return "none"
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return f"x {min(xs)}-{max(xs)} y {min(ys)}-{max(ys)} size {max(xs)-min(xs)+1}x{max(ys)-min(ys)+1}"


CASES = {
    # 1: Transform 直接子 Stack，无 SizedBox
    "t1": f'<Transform matrix="{MAT}" origin="(60,60)">'
          f'<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE">{RECT}</Stack></Transform>',
    # 2: Transform + SizedBox
    "t2": f'<Transform matrix="{MAT}" origin="(60,60)">'
          f'<SizedBox width="120" height="120"><Stack alignment="TOP_LEFT" fit="EXPAND" '
          f'clipBehavior="NONE">{RECT}</Stack></SizedBox></Transform>',
    # 3: Transform + SizedBox + Container
    "t3": f'<Transform matrix="{MAT}" origin="(60,60)">'
          f'<SizedBox width="120" height="120"><Container color="transparent">'
          f'<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE">{RECT}</Stack>'
          f'</Container></SizedBox></Transform>',
}
for name, body in CASES.items():
    print(name, "->", measure(body))
print("期望（90° 顺时针绕 (60,60)，画布 400x400，Transform 在 (0,0)）:")
print("  R1(8,8,28,92) 角点: (8,8)->(112,8), (36,8)->(112,36), (36,100)->(20,36), (8,100)->(20,8)")
print("  => bbox x 20-112 y 8-36 size 93x29")
