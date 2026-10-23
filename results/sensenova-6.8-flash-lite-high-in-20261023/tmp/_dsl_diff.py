"""临时排查：比较 v1/v2/v3 三版 DSL 的虚线形状与白色箭头图层数。"""
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
R = "r20261014T1536+0800-5f11da"
BASE = Path("tmp") / R / "A08" / "dsl"


def pts(path):
    n = [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?", path)]
    return list(zip(n[0::2], n[1::2]))


for v in ("v1", "v2", "v3"):
    t = (BASE / f"wayfinding.{v}.snapshot").read_text(encoding="utf-8")
    # 逐个 ClipPath 块解析：路径 + 填充色
    blocks = re.findall(
        r'<ClipPath path="(M[^"]+)" viewBox="0 0 1560 1080" fit="FILL">'
        r'<Container width="1560" height="1080" color="([^"]+)"></Container>'
        r'</ClipPath>', t)
    white_tri, dash_rect, deg, orange_blocks = [], [], [], 0
    for path, color in blocks:
        if color == "#E8590C":
            orange_blocks += 1
        pp = pts(path)
        distinct = {(round(a, 2), round(b, 2)) for a, b in pp}
        w = max(x for x, _ in pp) - min(x for x, _ in pp)
        h = max(y for _, y in pp) - min(y for _, y in pp)
        if color == "#FFFFFF" and len(distinct) == 3:
            white_tri.append(path)
        if color == "#E8590C" and {round(w, 2), round(h, 2)} == {24.0, 16.0}:
            dash_rect.append(path)
        if color == "#E8590C" and len(distinct) != 4:
            deg.append(path)
    n_white_text = len(re.findall(r"<Text text=[^>]*color=\"#FFFFFF\"", t))
    print(f"--- {v}: ClipPath 块 {len(blocks)}；橙色块 {orange_blocks}；"
          f"白色三角箭头 {len(white_tri)}；"
          f"24x16 矩形虚线 {len(dash_rect)}/47；橙色退化形 {len(deg)}；"
          f"白色 Text {n_white_text}")
    if deg:
        print(f"    退化形样例顶点: {pts(deg[0])}")
    if len(dash_rect) != len(deg):
        print(f"    橙色块 = {orange_blocks}，矩形 {len(dash_rect)} + "
              f"退化 {len(deg)} = {len(dash_rect) + len(deg)}")
