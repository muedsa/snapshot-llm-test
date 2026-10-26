"""A09 探针：精确复刻首个成功用例并测量。"""
import sys
import time
from pathlib import Path

sys.path.insert(0, "tmp/run-20261013-174209/_suite")
import render as R  # noqa: E402

from PIL import Image  # noqa: E402
import io  # noqa: E402

TMP = Path("tmp/run-20261013-174209/A09")

# 首个"成功"用例
text = """<Snapshot background="#FFFFFF" type="png">
  <Container width="400" height="400">
    <Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE" transform="(0,1,0,0,-1,0,0,0,0,0,1,0,120,0,0,1)" transformAlignment="TOP_LEFT">
      <Positioned left="8" top="8" width="28" height="92"><Container color="#E54B4B"/></Positioned>
      <Positioned left="36" top="72" width="68" height="28"><Container color="#2364DB"/></Positioned>
    </Stack>
  </Container>
</Snapshot>
"""
for attempt in range(3):
    r = R.post_render(text, "https://open-snapshot.muedsa.com/snapshot", timeout=90)
    if r.get("status") == 200:
        break
    time.sleep(2)
im = Image.open(io.BytesIO(r["body"])).convert("RGB")
print("size", im.size)
for cname, c in [("R1", (229, 75, 75)), ("R2", (35, 100, 219))]:
    pts = [(x, y) for y in range(400) for x in range(400)
           if all(abs(a - b) <= 14 for a, b in zip(im.getpixel((x, y)), c))]
    if pts:
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        print(f"{cname}: bbox x {min(xs)}-{max(xs)} y {min(ys)}-{max(ys)} "
              f"size {max(xs)-min(xs)+1}x{max(ys)-min(ys)+1}")

# 预期（90° 顺时针绕 (60,60)）：
# R1 (8,8,28,92): 角点 (8,8)->(112,8); (36,8)->(112,36); (36,100)->(20,36); (8,100)->(20,8)
#   => bbox x 20-112, y 8-36  => 93x29
# R2 (36,72,68,28): (36,72)->(48,36); (104,72)->(48,104); (104,100)->(20,104); (36,100)->(20,36)
#   => bbox x 20-48, y 36-104 => 29x69
print("expected R1: x 20-112 y 8-36 (93x29)")
print("expected R2: x 20-48 y 36-104 (29x69)")
