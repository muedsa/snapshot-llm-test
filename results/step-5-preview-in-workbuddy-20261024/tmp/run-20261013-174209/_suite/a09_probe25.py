"""A09 探针：测试不同的矩阵线性部分排列，找出真正生效的布局。"""
import sys
import time
from pathlib import Path

sys.path.insert(0, "tmp/run-20261013-174209/_suite")
import render as R  # noqa: E402

from PIL import Image  # noqa: E402
import io  # noqa: E402

TMP = Path("tmp/run-20261013-174209/A09")

# 一个明显的非对称标记：20x10 矩形在 (10,20)
MARK = '<Positioned left="10" top="20" width="20" height="10"><Container color="#E54B4B"/></Positioned>'


def run(mat, label):
    text = (f'<Snapshot type="png" background="#FFFFFF"><Container width="400" height="400">'
            f'<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE">'
            f'<Transform matrix="{mat}">'
            f'<SizedBox width="200" height="200"><Stack alignment="TOP_LEFT" fit="EXPAND" '
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
# 交换 x/y（列主序解读 (0,1,0,0, 1,0,0,0) => 行主序 [[0,1],[1,0]]）
run("(0,1,0,0,1,0,0,0,0,0,1,0,0,0,0,1)", "swap_v1")
# 列主序解读 (1,0,0,0, 0,1,0,0) 但写成 (0,1,...) 开头
run("(0,0,1,0,1,0,0,0,0,1,0,0,0,0,0,1)", "shift_v2")
# x 取反
run("(-1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1)", "neg_x")
# y 取反
run("(1,0,0,0,0,-1,0,0,0,0,1,0,0,0,0,1)", "neg_y")
