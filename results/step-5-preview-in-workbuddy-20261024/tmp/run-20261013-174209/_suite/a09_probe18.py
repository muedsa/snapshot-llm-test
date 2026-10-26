"""A09 探针：确定哪种 Widget 的 transform 真正生效。"""
import sys
import time
from pathlib import Path

sys.path.insert(0, "tmp/run-20261013-174209/_suite")
import render as R  # noqa: E402

from PIL import Image  # noqa: E402
import io  # noqa: E402

TMP = Path("tmp/run-20261013-174209/A09")

MAT = 'transform="(0,1,0,0,-1,0,0,0,0,0,1,0,120,0,0,1)" transformAlignment="TOP_LEFT"'
RECT = '<Positioned left="8" top="8" width="28" height="92"><Container color="#E54B4B"/></Positioned>'

CASES = {
    # A: Transform widget（matrix 必填）
    "A_transform_widget":
        f'<Snapshot type="png" background="#FFFFFF"><Container width="400" height="400">'
        f'<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE">'
        f'<Transform matrix="(0,1,0,0,-1,0,0,0,0,0,1,0,120,0,0,1)" origin="(60,60)">'
        f'<SizedBox width="120" height="120"><Stack alignment="TOP_LEFT" fit="EXPAND" '
        f'clipBehavior="NONE">{RECT}</Stack></SizedBox>'
        f'</Transform></Stack></Container></Snapshot>',
    # B: Container transform 单个矩形
    "B_container_tf":
        f'<Snapshot type="png" background="#FFFFFF"><Container width="400" height="400">'
        f'<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE">'
        f'<Positioned left="0" top="0" width="120" height="120" {MAT}>'
        f'<Container width="28" height="92" color="#E54B4B" margin="(8,8)"/>'
        f'</Positioned></Stack></Container></Snapshot>',
    # C: Container transform + 单子 Container
    "C_container_tf_nested":
        f'<Snapshot type="png" background="#FFFFFF"><Container width="400" height="400">'
        f'<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE">'
        f'<Positioned left="0" top="0" width="120" height="120" {MAT}>'
        f'<Container color="transparent"><Container width="28" height="92" color="#E54B4B" '
        f'margin="(8,8)"/></Container>'
        f'</Positioned></Stack></Container></Snapshot>',
}
for name, text in CASES.items():
    for attempt in range(3):
        r = R.post_render(text, "https://open-snapshot.muedsa.com/snapshot", timeout=90)
        if r.get("status") == 200:
            break
        time.sleep(2)
    if r.get("status") != 200:
        print(f"{name}: FAIL {(r.get('error') or '')[:110]}")
        continue
    im = Image.open(io.BytesIO(r["body"])).convert("RGB")
    pts = [(x, y) for y in range(400) for x in range(400)
           if all(abs(a - b) <= 14 for a, b in zip(im.getpixel((x, y)), (229, 75, 75)))]
    if pts:
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        print(f"{name}: R1 bbox x {min(xs)}-{max(xs)} y {min(ys)}-{max(ys)} "
              f"size {max(xs)-min(xs)+1}x{max(ys)-min(ys)+1}")
    else:
        print(f"{name}: no pixels")
    (TMP / f"tf-{name}.png").write_bytes(r["body"])
print("expected rotated: x 20-112 y 8-36 (93x29)")
