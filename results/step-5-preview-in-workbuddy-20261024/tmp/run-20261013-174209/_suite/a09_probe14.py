"""A09 探针：确定 transform 生效所需的嵌套条件。"""
import sys
import time
from pathlib import Path

sys.path.insert(0, "tmp/run-20261013-174209/_suite")
import render as R  # noqa: E402

from PIL import Image  # noqa: E402
import io  # noqa: E402

TMP = Path("tmp/run-20261013-174209/A09")

INNER = ('<Positioned left="10" top="20" width="30" height="10">'
         '<Container color="#E54B4B"/></Positioned>')
MAT = 'transform="(0,1,0,0,1,0,0,0,0,0,1,0,0,0,0,1)" transformAlignment="TOP_LEFT"'

CASES = {
    # 1: Stack(transform) 直接子是 Container
    "c1_stack_in_container":
        f'<Snapshot type="png" background="#FFFFFF"><Container width="300" height="300">'
        f'<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE" {MAT}>{INNER}</Stack>'
        f'</Container></Snapshot>',
    # 2: Positioned(transform) 直接子是 Container，外层 Stack
    "c2_positioned_in_stack":
        f'<Snapshot type="png" background="#FFFFFF"><Container width="300" height="300">'
        f'<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE">'
        f'<Positioned left="0" top="0" width="300" height="300" {MAT}>{INNER}</Positioned>'
        f'</Stack></Container></Snapshot>',
    # 3: Stack(transform) 在 Positioned 内，外层 Stack（图谱结构）
    "c3_stack_in_positioned_in_stack":
        f'<Snapshot type="png" background="#FFFFFF"><Container width="300" height="300">'
        f'<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE">'
        f'<Positioned left="0" top="0" width="300" height="300">'
        f'<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE" {MAT}>{INNER}</Stack>'
        f'</Positioned></Stack></Container></Snapshot>',
    # 4: Container(transform) 内含 Stack
    "c4_container_transform":
        f'<Snapshot type="png" background="#FFFFFF"><Container width="300" height="300">'
        f'<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE">'
        f'<Positioned left="0" top="0" width="300" height="300" {MAT}>'
        f'<Container color="transparent">{INNER}</Container>'
        f'</Positioned></Stack></Container></Snapshot>',
}
for name, text in CASES.items():
    for attempt in range(3):
        r = R.post_render(text, "https://open-snapshot.muedsa.com/snapshot", timeout=90)
        if r.get("status") == 200:
            break
        time.sleep(2)
    if r.get("status") != 200:
        print(f"{name}: FAIL {(r.get('error') or '')[:90]}")
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
        print(f"{name}: no pixels")
