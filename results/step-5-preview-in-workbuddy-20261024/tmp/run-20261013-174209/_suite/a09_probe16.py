"""A09 探针：transform 放在 Positioned 上 + 内部 Stack 承载多个矩形。"""
import sys
import time
from pathlib import Path

sys.path.insert(0, "tmp/run-20261013-174209/_suite")
import render as R  # noqa: E402

from PIL import Image  # noqa: E402
import io  # noqa: E402

TMP = Path("tmp/run-20261013-174209/A09")

MAT = 'transform="(0,1,0,0,-1,0,0,0,0,0,1,0,120,0,0,1)" transformAlignment="TOP_LEFT"'

# 关键：Positioned 带 transform，内部用 Stack 放多个矩形
text = (f'<Snapshot type="png" background="#FFFFFF"><Container width="300" height="300">'
        f'<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE">'
        f'<Positioned left="0" top="0" width="120" height="120" {MAT}>'
        f'<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE">'
        f'<Positioned left="8" top="8" width="28" height="92">'
        f'<Container color="#E54B4B"/></Positioned>'
        f'<Positioned left="36" top="72" width="68" height="28">'
        f'<Container color="#2364DB"/></Positioned>'
        f'</Stack></Positioned>'
        f'</Stack></Container></Snapshot>')
for attempt in range(3):
    r = R.post_render(text, "https://open-snapshot.muedsa.com/snapshot", timeout=90)
    if r.get("status") == 200:
        break
    time.sleep(2)
print("status", r.get("status"), (r.get("error") or "")[:120])
if r.get("status") == 200:
    im = Image.open(io.BytesIO(r["body"])).convert("RGB")
    for cname, c in [("R1", (229, 75, 75)), ("R2", (35, 100, 219))]:
        pts = [(x, y) for y in range(300) for x in range(300)
               if all(abs(a - b) <= 14 for a, b in zip(im.getpixel((x, y)), c))]
        if pts:
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            print(f"{cname}: bbox x {min(xs)}-{max(xs)} y {min(ys)}-{max(ys)} "
                  f"size {max(xs)-min(xs)+1}x{max(ys)-min(ys)+1}")
        else:
            print(f"{cname}: none")
    (TMP / "pos-tf-stack.png").write_bytes(r["body"])
