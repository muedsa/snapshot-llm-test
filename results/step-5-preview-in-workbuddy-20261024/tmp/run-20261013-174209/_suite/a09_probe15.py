"""A09 探针：确认 transform 应放在 Positioned 上（而非 Stack）。"""
import sys
import time
from pathlib import Path

sys.path.insert(0, "tmp/run-20261013-174209/_suite")
import render as R  # noqa: E402

from PIL import Image  # noqa: E402
import io  # noqa: E402

TMP = Path("tmp/run-20261013-174209/A09")

# 90° 顺时针围绕 (60,60)：[[0,-1,120],[1,0,0]]
# 列主序: (0,1,0,0, -1,0,0,0, 0,0,1,0, 120,0,0,1)
MAT = 'transform="(0,1,0,0,-1,0,0,0,0,0,1,0,120,0,0,1)" transformAlignment="TOP_LEFT"'

# 变换放在 Positioned 上
text = (f'<Snapshot type="png" background="#FFFFFF"><Container width="300" height="300">'
        f'<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE">'
        f'<Positioned left="0" top="0" width="120" height="120" {MAT}>'
        f'<Positioned left="8" top="8" width="28" height="92">'
        f'<Container color="#E54B4B"/></Positioned>'
        f'</Positioned>'
        f'</Stack></Container></Snapshot>')
for attempt in range(3):
    r = R.post_render(text, "https://open-snapshot.muedsa.com/snapshot", timeout=90)
    if r.get("status") == 200:
        break
    time.sleep(2)
print("status", r.get("status"), (r.get("error") or "")[:100])
if r.get("status") == 200:
    im = Image.open(io.BytesIO(r["body"])).convert("RGB")
    pts = [(x, y) for y in range(300) for x in range(300)
           if all(abs(a - b) <= 14 for a, b in zip(im.getpixel((x, y)), (229, 75, 75)))]
    if pts:
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        print(f"R1 bbox x {min(xs)}-{max(xs)} y {min(ys)}-{max(ys)} "
              f"size {max(xs)-min(xs)+1}x{max(ys)-min(ys)+1}")
    (TMP / "pos-transform-test.png").write_bytes(r["body"])
