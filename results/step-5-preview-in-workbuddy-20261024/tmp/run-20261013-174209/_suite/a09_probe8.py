"""A09 探针：渲染图谱前 N 个元素，找出变换开始失效的临界点。"""
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, "tmp/run-20261013-174209/_suite")
import render as R  # noqa: E402

TMP = Path("tmp/run-20261013-174209/A09")
full = (TMP / "transform-atlas.snapshot").read_text(encoding="utf-8")

# 按 Positioned 顶层子元素切分（图谱外层 Stack 的直接子节点）
m = re.search(r'<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE">(.*)</Stack></Container></Snapshot>', full, re.S)
inner = m.group(1)
# 用栈匹配切分顶层元素
def split_top(s):
    parts, depth, start = [], 0, None
    i = 0
    while i < len(s):
        if s[i] == "<":
            j = s.find(">", i)
            if j == -1:
                break
            tag = s[i + 1:j]
            selfclose = tag.endswith("/")
            name = tag.rstrip("/").split()[0].lstrip("/")
            if not selfclose and not tag.startswith("/"):
                if depth == 0:
                    start = i
                depth += 1
            elif tag.startswith("/"):
                depth -= 1
                if depth == 0:
                    parts.append(s[start:j + 1])
            else:
                if depth == 0:
                    parts.append(s[i:j + 1])
            i = j + 1
        else:
            i += 1
    return parts

parts = split_top(inner)
print("top-level children:", len(parts))

for n in [4, 10, 20, 40, 80, 150, 250, len(parts)]:
    sub = (f'<Snapshot type="png" background="#F8FAFC">'
           f'<Container width="1600" height="1200">'
           f'<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE">'
           + "".join(parts[:n]) + "</Stack></Container></Snapshot>")
    for attempt in range(3):
        r = R.post_render(sub, "https://open-snapshot.muedsa.com/snapshot", timeout=90)
        if r.get("status") == 200:
            break
        time.sleep(2)
    ok = r.get("status") == 200
    # 统计 T02 cell 内 R1 的宽度
    info = ""
    if ok:
        (TMP / f"slice-{n}.png").write_bytes(r["body"])
        from PIL import Image
        import io
        im = Image.open(io.BytesIO(r["body"])).convert("RGB")
        # T02 区域 x 484-784, y 211-461
        xs, ys = [], []
        for yy in range(245, 435):
            for xx in range(492, 776):
                p = im.getpixel((xx, yy))
                if all(abs(a - b) <= 14 for a, b in zip(p, (229, 75, 75))):
                    xs.append(xx); ys.append(yy)
        if xs:
            info = f"T02_R1 {max(xs)-min(xs)+1}x{max(ys)-min(ys)+1}"
        else:
            info = "T02_R1 NONE"
    print(f"n={n}: {r.get('status')} len={len(r.get('body') or b'')} {info} "
          f"{(r.get('error') or '')[:60]}")
