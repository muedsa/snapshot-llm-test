"""A09 探针：确定服务端矩阵约定（列主序 vs 行主序）。"""
import sys
import time
from pathlib import Path

sys.path.insert(0, "tmp/run-20261013-174209/_suite")
import render as R  # noqa: E402

TMP = Path("tmp/run-20261013-174209/A09")

# 单矩形 28x92 在 (8,8)。容器 120x120 放在 (100,100)。
# 我们试 4 个矩阵，看哪个把它旋转 90° 后仍留在容器附近。
def body(mat):
    return (f'<Positioned left="100" top="100" width="120" height="120">'
            f'<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE" '
            f'transform="{mat}" transformAlignment="TOP_LEFT">'
            f'<Positioned left="8" top="8" width="28" height="92">'
            f'<Container color="#E54B4B"/></Positioned>'
            f'</Stack></Positioned>')

MATS = {
    # 列主序 90° 顺时针: [[0,-1,60],[1,0,60]] -> (0,1,0,0, -1,0,0,0, 0,0,1,0, 60,60,0,1)
    "col_cw90": "(0,1,0,0,-1,0,0,0,0,0,1,0,60,60,0,1)",
    # 行主序同值
    "row_cw90": "(0,-1,0,0,1,0,0,0,0,0,1,0,60,60,0,1)",
    # 列主序 90° 逆时针
    "col_ccw90": "(0,-1,0,0,1,0,0,0,0,0,1,0,60,60,0,1)",
}
for name, mat in MATS.items():
    text = (f'<Snapshot type="png" background="#FFFFFF"><Container width="400" height="400">'
            f'<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE">'
            + body(mat) + "</Stack></Container></Snapshot>")
    for attempt in range(3):
        r = R.post_render(text, "https://open-snapshot.muedsa.com/snapshot", timeout=90)
        if r.get("status") == 200:
            break
        time.sleep(2)
    if r.get("status") == 200:
        (TMP / f"conv-{name}.png").write_bytes(r["body"])
    print(f"{name}: {r.get('status')} len={len(r.get('body') or b'')}")
