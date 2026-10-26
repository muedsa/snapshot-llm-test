"""A09 探针：用 1x1 标记但在大画布上精确标定（排除块尺寸干扰）。"""
import sys
import time
from pathlib import Path

sys.path.insert(0, "tmp/run-20261013-174209/_suite")
import render as R  # noqa: E402

from PIL import Image  # noqa: E402
import io  # noqa: E402

TMP = Path("tmp/run-20261013-174209/A09")

PURE = "(0,1,0,0,-1,0,0,0,0,0,1,0,0,0,0,1)"

# 1x1 标记
MARKS = "".join(
    f'<Positioned left="{x}" top="{y}" width="1" height="1">'
    f'<Container color="#E54B4B"/></Positioned>'
    for x, y in [(0, 0), (119, 0), (0, 119), (119, 119), (60, 60)]
)
text = (f'<Snapshot type="png" background="#FFFFFF"><Container width="600" height="600">'
        f'<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE">'
        f'<Positioned left="100" top="100" width="120" height="120">'
        f'<Transform matrix="{PURE}" origin="(60,60)">'
        f'<SizedBox width="120" height="120"><Stack alignment="TOP_LEFT" fit="EXPAND" '
        f'clipBehavior="NONE">{MARKS}</Stack></SizedBox>'
        f'</Transform></Positioned>'
        f'</Stack></Container></Snapshot>')
for attempt in range(3):
    r = R.post_render(text, "https://open-snapshot.muedsa.com/snapshot", timeout=90)
    if r.get("status") == 200:
        break
    time.sleep(2)
im = Image.open(io.BytesIO(r["body"])).convert("RGB")
pts = [(x, y) for y in range(600) for x in range(600)
       if all(abs(a - b) <= 25 for a, b in zip(im.getpixel((x, y)), (229, 75, 75)))]
print("pixels:", sorted(pts))
print()
print("Positioned=(100,100), origin=(60,60), M=[[0,-1],[1,0]] (列主序 0,1,-1,0)")
print("预期(若 canvas = Positioned + M@(local-origin) + origin):")
for lx, ly in [(0, 0), (119, 0), (0, 119), (119, 119), (60, 60)]:
    dx, dy = lx - 60, ly - 60
    mx, my = -dy, dx
    print(f"  local({lx},{ly}) -> ({100+mx+60},{100+my+60})")
