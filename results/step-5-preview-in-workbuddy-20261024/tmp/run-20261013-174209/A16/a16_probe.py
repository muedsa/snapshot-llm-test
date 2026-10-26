"""A16 批量文本探针：单画布渲染全部唯一字符串，量墨迹偏移与宽度。

输出 a16_probe.json：{key: {text,size,family,style,ink_left,ink_top,ink_w,ink_h}}
ink_left/ink_top = 墨迹相对盒(10, band_top)左上角的偏移；最终 LEFT 对齐盒坐标 =
目标墨迹 - 偏移。CENTER/RIGHT 对齐只需 ink_w 作适配参考。
"""
from __future__ import annotations
import json
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "run-20261013-174209")
sys.path.insert(0, str(ROOT / "tmp" / RUN_ID / "_suite"))
import render as R  # noqa: E402

TMP = ROOT / "tmp" / RUN_ID / "A16"
TMP.mkdir(parents=True, exist_ok=True)

NOTO = "Noto Sans CJK SC"

# (key, text, size, family, style)
ITEMS = [
    ("h1", "季度复盘：Q4 利润 54 万元居首", 34, NOTO, "BOLD"),
    ("h2", "Q4 收入 180 万元、利润 54 万元双双居首；Q3 收入环比回落 7 万元，为全年唯一收入下滑季", 22, NOTO, "NORMAL"),
    ("c_title", "收入与成本对比", 24, NOTO, "BOLD"),
    ("c_unit", "单位：万元", 18, NOTO, "NORMAL"),
    ("lg_rev", "收入", 20, NOTO, "NORMAL"),
    ("lg_cost", "成本", 20, NOTO, "NORMAL"),
    ("tick_0", "0", 18, "Inter", "NORMAL"),
    ("tick_50", "50", 18, "Inter", "NORMAL"),
    ("tick_100", "100", 18, "Inter", "NORMAL"),
    ("tick_150", "150", 18, "Inter", "NORMAL"),
    ("tick_200", "200", 18, "Inter", "NORMAL"),
    ("v_120", "120", 18, "Inter Semi Bold", "NORMAL"),
    ("v_90", "90", 18, "Inter Semi Bold", "NORMAL"),
    ("v_135", "135", 18, "Inter Semi Bold", "NORMAL"),
    ("v_108", "108", 18, "Inter Semi Bold", "NORMAL"),
    ("v_128", "128", 18, "Inter Semi Bold", "NORMAL"),
    ("v_96", "96", 18, "Inter Semi Bold", "NORMAL"),
    ("v_180", "180", 18, "Inter Semi Bold", "NORMAL"),
    ("v_126", "126", 18, "Inter Semi Bold", "NORMAL"),
    ("q_Q1", "Q1", 20, "Inter", "NORMAL"),
    ("q_Q2", "Q2", 20, "Inter", "NORMAL"),
    ("q_Q3", "Q3", 20, "Inter", "NORMAL"),
    ("q_Q4", "Q4", 20, "Inter", "NORMAL"),
    ("p_title", "利润明细", 24, NOTO, "BOLD"),
    ("p_sub", "利润 = 收入 − 成本，单位：万元", 18, NOTO, "NORMAL"),
    ("p_q1", "Q1", 22, "Inter", "NORMAL"),
    ("p_q2", "Q2", 22, "Inter", "NORMAL"),
    ("p_q3", "Q3", 22, "Inter", "NORMAL"),
    ("p_q4", "Q4", 22, "Inter", "NORMAL"),
    ("p_v1", "30 万元", 26, NOTO, "BOLD"),
    ("p_v2", "27 万元", 26, NOTO, "BOLD"),
    ("p_v3", "32 万元", 26, NOTO, "BOLD"),
    ("p_v4", "54 万元", 26, NOTO, "BOLD"),
    ("o_title", "重点观察 · Q4", 24, NOTO, "BOLD"),
    ("o_l1", "Q4 收入 180 万元、利润 54", 22, NOTO, "NORMAL"),
    ("o_l2", "万元、利润率 30%，均为全年", 22, NOTO, "NORMAL"),
    ("o_l3", "最高；Q3 收入环比回落 7 万", 22, NOTO, "NORMAL"),
    ("o_l4", "元，需关注回升节奏。", 22, NOTO, "NORMAL"),
    ("k_l1", "全年收入", 22, NOTO, "NORMAL"),
    ("k_l2", "全年成本", 22, NOTO, "NORMAL"),
    ("k_l3", "全年利润", 22, NOTO, "NORMAL"),
    ("k_v1", "563 万元", 34, NOTO, "BOLD"),
    ("k_v2", "420 万元", 34, NOTO, "BOLD"),
    ("k_v3", "143 万元", 34, NOTO, "BOLD"),
    ("f1", "数据来源：inputs/source.csv（唯一可信原始数据） · 单位：万元 · 利润 = 收入 − 成本 · Snapshot DSL 重制", 18, NOTO, "NORMAL"),
]

BAND = 46          # 每项带高（>= 最大字号 34 + 余量）
PAD_X = 10
PAD_TOP = 12
BOX_W = 900
n = len(ITEMS)
W = 1000
H = PAD_TOP + n * BAND + 12

parts = [f'<Snapshot type="png" background="transparent">'
         f'<Container width="{W}" height="{H}">'
         f'<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE">']
for i, (key, text, size, fam, style) in enumerate(ITEMS):
    y = PAD_TOP + i * BAND
    esc = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    parts.append(
        f'<Positioned left="{PAD_X}" top="{y}" width="{BOX_W}" height="{BAND}">'
        f'<Container color="transparent" alignment="TOP_LEFT">'
        f'<Text fontSize="{size}" fontFamily="{fam}" fontStyle="{style}" '
        f'textAlign="LEFT" softWrap="false" maxLines="1"><![CDATA[{esc}]]></Text>'
        f'</Container></Positioned>')
parts.append("</Stack></Container></Snapshot>")
dsl = "".join(parts)
dsl_file = TMP / "a16_probe.snapshot"
dsl_file.write_text(dsl, encoding="utf-8")

log = R.Log(ROOT, RUN_ID, "A16")
res = R.render(dsl_file, TMP / "a16_probe.png", ROOT, log, req_type="measure-batch",
               label=f"A16-probe({n}items)")
if res["record"]["status"] != "ok":
    print("RENDER FAILED:", res["record"].get("error"))
    sys.exit(1)

from PIL import Image  # noqa: E402
im = Image.open(TMP / "a16_probe.png").convert("RGBA")
px = im.load()
iw, ih = im.size
print("probe canvas:", im.size)

out = {}
for i, (key, text, size, fam, style) in enumerate(ITEMS):
    y0 = PAD_TOP + i * BAND
    y1 = y0 + BAND
    pts = [(x, y) for y in range(y0, min(y1, ih)) for x in range(iw) if px[x, y][3] > 0]
    if not pts:
        print(f"  !! {key}: NO INK")
        continue
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    rec = {
        "text": text, "size": size, "family": fam, "style": style,
        "ink_left": min(xs) - PAD_X, "ink_top": min(ys) - y0,
        "ink_w": max(xs) - min(xs) + 1, "ink_h": max(ys) - min(ys) + 1,
    }
    out[key] = rec
    print(f"  {key:9s} off=({rec['ink_left']},{rec['ink_top']}) ink={rec['ink_w']}x{rec['ink_h']}  {text[:22]}")

with open(TMP / "a16_probe.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
print("wrote", TMP / "a16_probe.json")
