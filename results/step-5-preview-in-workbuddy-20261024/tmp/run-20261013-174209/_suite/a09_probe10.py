"""A09 探针：矩阵方向测试 —— 用同一矩阵在不同画布/不同矩阵值验证旋转方向。"""
import sys
import time
from pathlib import Path

sys.path.insert(0, "tmp/run-20261013-174209/_suite")
import render as R  # noqa: E402

TMP = Path("tmp/run-20261013-174209/A09")

# 只放一个矩形，便于判断方向
def body(mat):
    return (f'<Positioned left="100" top="100" width="120" height="120">'
            f'<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE" '
            f'transform="{mat}" transformAlignment="TOP_LEFT">'
            f'<Positioned left="8" top="8" width="28" height="92">'
            f'<Container color="#E54B4B"/></Positioned>'
            f'</Stack></Positioned>')

MATS = {
    "m_01_10": "(0,1,0,0,-1,0,0,0,0,0,1,0,120,0,0,1)",
    "m_10_01": "(1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1)",
    "m_neg01": "(0,-1,0,0,1,0,0,0,0,0,1,0,120,0,0,1)",
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
        (TMP / f"dir-{name}.png").write_bytes(r["body"])
    print(f"{name}: {r.get('status')} len={len(r.get('body') or b'')} "
          f"{(r.get('error') or '')[:80]}")
