"""A09 探针：用非对称标记精确推断矩阵约定。"""
import sys
import time
from pathlib import Path

sys.path.insert(0, "tmp/run-20261013-174209/_suite")
import render as R  # noqa: E402

from PIL import Image  # noqa: E402
import io  # noqa: E402

TMP = Path("tmp/run-20261013-174209/A09")

# 单个矩形：左上角在 (10,20)，尺寸 30x10（明显非对称）
def body(mat):
    return (f'<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE" '
            f'transform="{mat}" transformAlignment="TOP_LEFT">'
            f'<Positioned left="10" top="20" width="30" height="10">'
            f'<Container color="#E54B4B"/></Positioned></Stack>')


MATS = {
    "identity": "(1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1)",
    "swap_xy": "(0,1,0,0,1,0,0,0,0,0,1,0,0,0,0,1)",
    "neg_x": "(-1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1)",
    "neg_y": "(1,0,0,0,0,-1,0,0,0,0,1,0,0,0,0,1)",
}
for name, mat in MATS.items():
    text = (f'<Snapshot type="png" background="#FFFFFF"><Container width="300" height="300">'
            + body(mat) + "</Container></Snapshot>")
    for attempt in range(3):
        r = R.post_render(text, "https://open-snapshot.muedsa.com/snapshot", timeout=90)
        if r.get("status") == 200:
            break
        time.sleep(2)
    if r.get("status") != 200:
        print(name, "FAIL", (r.get("error") or "")[:80])
        continue
    im = Image.open(io.BytesIO(r["body"])).convert("RGB")
    pts = [(x, y) for y in range(300) for x in range(300)
           if all(abs(a - b) <= 14 for a, b in zip(im.getpixel((x, y)), (229, 75, 75)))]
    if pts:
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        print(f"{name}: bbox x {min(xs)}-{max(xs)} y {min(ys)}-{max(ys)} "
              f"size {max(xs)-min(xs)+1}x{max(ys)-min(ys)+1}")
    else:
        print(name, "no pixels")
