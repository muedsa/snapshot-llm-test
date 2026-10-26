"""A09 探针：测试科学计数法矩阵是否被服务端拒绝/忽略。"""
import sys
import time
from pathlib import Path

sys.path.insert(0, "tmp/run-20261013-174209/_suite")
import render as R  # noqa: E402

TMP = Path("tmp/run-20261013-174209/A09")

BODY_T = ('<Positioned left="574.0" top="284.0" width="120" height="120">'
          '<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE" '
          'transform="{M}" transformAlignment="TOP_LEFT">'
          '<Positioned left="8" top="8" width="28" height="92"><Container color="#E54B4B"/></Positioned>'
          '<Positioned left="36" top="72" width="68" height="28"><Container color="#2364DB"/></Positioned>'
          '</Stack></Positioned>')

MATS = {
    "exact": "(0,1,0,0,-1,0,0,0,0,0,1,0,120,0,0,1)",
    "sci": "(6.12323e-17,1,0,0,-1,6.12323e-17,0,0,0,0,1,0,120,-7.10543e-15,0,1)",
    "sci2": "(6.123233995736766e-17,1.0,0,0,-1.0,6.123233995736766e-17,0,0,0,0,1,0,120,-7.105427357601002e-15,0,1)",
}
for name, mat in MATS.items():
    text = (f'<Snapshot type="png" background="#FFFFFF"><Container width="1600" height="1200">'
            f'<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE">'
            + BODY_T.replace("{M}", mat) + "</Stack></Container></Snapshot>")
    for attempt in range(3):
        r = R.post_render(text, "https://open-snapshot.muedsa.com/snapshot", timeout=90)
        if r.get("status") == 200:
            break
        time.sleep(2)
    ok = r.get("status") == 200
    info = ""
    if ok:
        (TMP / f"mat-{name}.png").write_bytes(r["body"])
        from PIL import Image
        import io
        im = Image.open(io.BytesIO(r["body"])).convert("RGB")
        xs, ys = [], []
        for yy in range(245, 435):
            for xx in range(492, 776):
                p = im.getpixel((xx, yy))
                if all(abs(a - b) <= 14 for a, b in zip(p, (229, 75, 75))):
                    xs.append(xx); ys.append(yy)
        info = (f"R1 {max(xs)-min(xs)+1}x{max(ys)-min(ys)+1}" if xs else "NONE")
    print(f"{name}: {r.get('status')} {info} {(r.get('error') or '')[:100]}")
