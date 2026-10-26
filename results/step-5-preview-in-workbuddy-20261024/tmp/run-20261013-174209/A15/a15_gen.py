"""A15 复杂界面视觉复刻生成器 v2（1440x900）。

在 v1 基础上按锚点对比结果逐项修正（见 iterations.jsonl）：
- KPI 卡高 143→144；导航选中态高 47→48；网格线左端 334→333、宽 637
- 柱顶改用 ceil(549 - v*1.2)；标题/各文本按实测墨迹差微调 1px
- 副标题 18px 左对齐至 x=261；导航字距 ls=1.4；活动名 17.5px
- ¥ thousand 13px；按钮文字 16.5px 上移 2.5px； pill 文字上移 2px
- 页脚左端 265；刻度标签右端 321
"""
from __future__ import annotations
import math
import os
import sys
import time
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "run")
sys.path.insert(0, str(ROOT / "tmp" / RUN_ID / "_suite"))
import render as R  # noqa: E402

TASK = "A15"
TMP = ROOT / "tmp" / RUN_ID / TASK
TMP.mkdir(parents=True, exist_ok=True)

W, H = 1440, 900

C = {
    "bg": "#F3F6FB", "sidebar": "#14233C", "sel": "#294467",
    "dot_idle": "#7791B3", "mint": "#64DBB6", "nav_text": "#BECADD",
    "white": "#FFFFFF", "card_border": "#E2E8F1", "label": "#63748F",
    "ink": "#18283F", "green": "#168267", "blue": "#245CE4",
    "pro_card": "#233954", "pro_text": "#5CC9AB", "pro_sub": "#B3C5D8",
    "grid": "#E7EDF5", "month": "#8D9EAD", "tick": "#7C8CA1",
    "unit": "#8995AA", "divider": "#EBEFF5", "time": "#8693A8",
    "footer": "#7B8BA3", "amber_bg": "#FFF3D7", "amber_tx": "#9D6613",
    "green_bg": "#DCF5EC", "blue_bg": "#E7EFFF", "orange": "#EAAF40",
}

nodes = []


def rect(x, y, w, h, color, r=None, border=None):
    if border:
        nodes.append(f'<Positioned left="{x:.2f}" top="{y:.2f}" width="{w:.2f}" height="{h:.2f}">'
                     f'<Container color="{color}" border="1 SOLID {border}" borderRadius="{r}"/></Positioned>')
    else:
        rb = f' borderRadius="{r}"' if r else ""
        nodes.append(f'<Positioned left="{x:.2f}" top="{y:.2f}" width="{w:.2f}" height="{h:.2f}">'
                     f'<Container color="{color}"{rb}/></Positioned>')


def line(x, y, w, color):
    nodes.append(f'<Positioned left="{x:.2f}" top="{y:.2f}" width="{w:.2f}" height="1.00">'
                 f'<Container color="{color}"/></Positioned>')


def text(s, left, top, w, size, style, family, color,
         align="LEFT", ls=None, box_h=None, center_v=False):
    ls_attr = f' letterSpacing="{ls}"' if ls else ""
    bh = f' height="{box_h:.2f}"' if box_h else ""
    inner = (f'<Text fontSize="{size}" fontFamily="{family}" fontStyle="{style}"{ls_attr} '
             f'color="{color}" textAlign="{align}" softWrap="false" maxLines="1">'
             f'<![CDATA[{s}]]></Text>')
    if center_v:
        nodes.append(f'<Positioned left="{left:.2f}" top="{top:.2f}" width="{w:.2f}"{bh}>'
                     f'<Container color="transparent" alignment="CENTER">{inner}</Container></Positioned>')
    else:
        nodes.append(f'<Positioned left="{left:.2f}" top="{top:.2f}" width="{w:.2f}"{bh}>'
                     f'<Container color="transparent">{inner}</Container></Positioned>')


# ============ 侧栏 ============
rect(0, 0, 220, H, C["sidebar"])
rect(30, 33, 28, 28, C["mint"], r=7)
rect(38, 40, 14, 14, C["sidebar"], r=3)
text("NORTHSTAR", 72, 34, 140, 19, "BOLD", "Inter", C["white"])
rect(18, 116, 184, 48, C["sel"], r=10)
rect(34, 128, 12, 12, C["mint"], r=6)
rect(34, 192, 12, 12, C["dot_idle"], r=6)
rect(34, 256, 12, 12, C["dot_idle"], r=6)
rect(34, 320, 12, 12, C["dot_idle"], r=6)
text("Overview", 63, 124, 130, 16, "BOLD", "Inter", C["white"], ls="1.4")
text("Projects", 63, 187, 130, 16, "NORMAL", "Inter", C["nav_text"], ls="1.4")
text("Analytics", 63, 251, 130, 16, "NORMAL", "Inter", C["nav_text"], ls="1.4")
text("Settings", 64, 315, 130, 16, "NORMAL", "Inter", C["nav_text"], ls="1.4")
rect(22, 752, 176, 116, C["pro_card"], r=12)
text("PRO WORKSPACE", 37, 767, 140, 13, "BOLD", "Inter", C["pro_text"])
text("12 team members", 38, 800, 145, 16, "NORMAL", "Inter", C["white"])
text("Manage access →", 38, 832, 145, 14.5, "NORMAL", "Inter", C["pro_sub"])

# ============ 页头 ============
text("Workspace Overview", 260, 32, 360, 32, "BOLD", "Inter", C["ink"])
text("Saturday, 07 November 2026", 260, 83, 260, 18, "NORMAL", "Inter", C["label"])
rect(1184, 43, 216, 48, C["blue"], r=10)
text("Export report", 1184, 36.5, 216, 16.5, "BOLD", "Inter", C["white"],
     align="CENTER", box_h=48, center_v=True)

# ============ KPI 卡片 ============
for cx in (260, 644, 1028):
    rect(cx, 138, 356, 144, C["white"], r=12, border=C["card_border"])
text("REVENUE", 284, 157, 110, 14, "NORMAL", "Inter Semi Bold", C["label"])
text("ORDERS", 669, 157, 110, 14, "NORMAL", "Inter Semi Bold", C["label"])
text("REFUND RATE", 1052, 157, 130, 14, "NORMAL", "Inter Semi Bold", C["label"])
text("¥128,400", 284, 192, 210, 32, "BOLD", "Inter", C["ink"])
text("426", 668, 192, 110, 32, "BOLD", "Inter", C["ink"])
text("3.2%", 1052, 192, 130, 32, "BOLD", "Inter", C["ink"])
text("+12.4%", 284, 243, 110, 17, "NORMAL", "Inter Semi Bold", C["green"])
text("+8.1%", 668, 243, 110, 17, "NORMAL", "Inter Semi Bold", C["green"])
text("−0.8 pp", 1052, 243, 110, 17, "NORMAL", "Inter Semi Bold", C["green"])

# ============ 图表卡 ============
rect(260, 310, 742, 286, C["white"], r=12, border=C["card_border"])
text("Net revenue", 284, 331, 170, 22, "BOLD", "Inter", C["ink"])
text("Apr – Sep", 860, 334, 114, 17, "NORMAL", "Inter", C["label"], align="RIGHT")
text("¥ thousand", 288, 373, 100, 13, "NORMAL", "Inter", C["unit"])
for lbl, ty in (("120", 395), ("90", 431), ("60", 467), ("30", 503), ("0", 539)):
    text(lbl, 252, ty, 69, 13, "NORMAL", "Inter", C["tick"], align="RIGHT")
for gy in (405, 441, 477, 513, 549):
    line(333, gy, 637, C["grid"])
bars = [("Apr", 357, 54), ("May", 458, 72), ("Jun", 559, 63),
        ("Jul", 660, 90), ("Aug", 761, 81), ("Sep", 862, 108)]
for name, bx, val in bars:
    top = math.ceil(549 - val * 1.2)
    rect(bx, top, 54, 549 - top, C["blue"])
for (name, bx, val), cx in zip(bars, (383.5, 484.5, 585.5, 686.5, 787.5, 888.5)):
    text(name, cx - 40, 557, 80, 13, "NORMAL", "Inter", C["month"], align="CENTER")

# ============ 活动卡 ============
rect(1030, 310, 370, 286, C["white"], r=12, border=C["card_border"])
text("Team activity", 1054, 331, 170, 22, "BOLD", "Inter", C["ink"])
acts = [
    ("Design review", "08:40", 397, C["orange"]),
    ("Dataset updated", "09:15", 457, C["blue"]),
    ("Render complete", "10:05", 517, C["green"]),
]
for i, (nm, tm, dy, dc) in enumerate(acts):
    rect(1054, dy, 10, 10, dc, r=5)
    text(nm, 1077, 392 + i * 61, 170, 17.5, "NORMAL", "Inter Semi Bold", C["ink"])
    text(tm, 1077, 419 + i * 59, 90, 14, "NORMAL", "Inter", C["time"])

# ============ 项目表格卡 ============
rect(260, 624, 1140, 218, C["white"], r=12, border=C["card_border"])
text("Recent projects", 284, 641, 210, 22, "BOLD", "Inter", C["ink"])
rect(284, 688, 1090, 34, C["bg"])
for lbl, lx in (("PROJECT", 298), ("OWNER", 782), ("STATUS", 1033), ("DUE", 1230)):
    text(lbl, lx, 695, 90, 12, "BOLD", "Inter", C["label"])
line(284, 760, 1090, C["divider"])
line(284, 795, 1090, C["divider"])
rows = [
    ("Atlas / Visual system", "Lin Chuan", "In progress", "Nov 09", 729, C["blue_bg"], C["blue"]),
    ("Pulse / Dashboard", "Zhou He", "Review", "Nov 11", 764, C["amber_bg"], C["amber_tx"]),
    ("Orbit / Launch", "Su Yan", "Done", "Nov 12", 799, C["green_bg"], C["green"]),
]
for i, (proj, owner, status, due, py, pbg, ptx) in enumerate(rows):
    ty = 731 + i * 35
    text(proj, 298, ty, 230, 16, "NORMAL", "Inter Semi Bold", C["ink"])
    text(owner, 782, ty, 130, 16, "NORMAL", "Inter", C["label"])
    text(due, 1230, ty, 110, 16, "NORMAL", "Inter", C["label"])
    rect(1028, py, 148, 28, pbg, r=8)
    text(status, 1028, py - 2, 148, 13, "NORMAL", "Inter Semi Bold", ptx,
         align="CENTER", box_h=28, center_v=True)

# ============ 页脚 ============
text("All data is fictional · Snapshot benchmark", 260, 864, 290, 13,
     "NORMAL", "Inter", C["footer"])

dsl = (f'<Snapshot type="png" background="{C["bg"]}">'
       f'<Container width="{W}" height="{H}">'
       f'<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE">'
       + "".join(nodes) + "</Stack></Container></Snapshot>")

dsl_file = TMP / "reconstructed-v4.snapshot"
dsl_file.write_text(dsl, encoding="utf-8")
log = R.Log(ROOT, RUN_ID, TASK)
res = None
for attempt in range(4):
    res = R.render(dsl_file, TMP / "reconstructed-v4.png", ROOT, log,
                   req_type="render", label="A15-v2")
    if res["record"]["status"] == "ok":
        break
    err = res["record"].get("error") or ""
    if any(k in err for k in ("Timeout", "URLError", "RemoteDisconnected",
                              "handshake", "EOF occurred", "timed out")):
        time.sleep(2 + attempt * 2)
        continue
    break
if res["record"]["status"] != "ok":
    print("RENDER FAILED:", res["record"].get("error"))
    sys.exit(1)
print("rendered v2 ok,", res["record"].get("elapsed_s"), "s, nodes:", len(nodes))
