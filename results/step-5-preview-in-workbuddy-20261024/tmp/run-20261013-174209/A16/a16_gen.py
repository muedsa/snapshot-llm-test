"""A16 修正版报告生成器（1280x900）。

数据与几何来自 a16_data.py（corrected-data.json）；文本位置由 a16_probe.json
的墨迹偏移驱动：LEFT 对齐盒坐标 = 目标墨迹 - 探针偏移。
设计要点：四季收入/成本分组柱、共同零起点、图例与数据一致、单位万元、
利润明细卡、数据依据标题、重点观察 Q4、全年合计 KPI 条。
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
OUT = ROOT / "outputs" / RUN_ID / "A16"
OUT.mkdir(parents=True, exist_ok=True)

P = json.load(open(TMP / "a16_probe.json"))
D = json.load(open(OUT / "corrected-data.json"))

W, H = 1280, 900

C = {
    "bg": "#F5F7FA", "card": "#FFFFFF", "border": "#E2E8F1",
    "ink": "#18283F", "body": "#334155", "label": "#64748F", "sub": "#8995AA",
    "rev": "#245CE4", "cost": "#E88E35", "profit": "#168267",
    "rev_tx": "#245CE4", "cost_tx": "#B45309",
    "grid": "#E7EDF5", "axis": "#94A3B8", "tick": "#7C8CA1",
    "amber_bg": "#FFF7E8", "amber_bd": "#F0D9A8", "amber_tx": "#8A5A12", "amber_body": "#6B4A1E",
    "hair": "#EEF2F7", "footer": "#7B8BA3",
}

NOTO = "Noto Sans CJK SC"
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
    rect(x, y, w, 1, color)


def vline(x, y, h, color):
    rect(x, y, 1, h, color)


def text_left(key, tx, ty, box_w=None, color=None):
    """按探针偏移放置 LEFT 对齐文本：盒 = 目标墨迹 - 偏移。"""
    p = P[key]
    left = tx - p["ink_left"]
    top = ty - p["ink_top"]
    w = box_w if box_w else p["ink_w"] + 12
    col = color if color else C["body"]
    nodes.append(f'<Positioned left="{left:.2f}" top="{top:.2f}" width="{w:.2f}" height="{p["size"] + 14:.2f}">'
                 f'<Container color="transparent" alignment="TOP_LEFT">'
                 f'<Text fontSize="{p["size"]}" fontFamily="{p["family"]}" fontStyle="{p["style"]}" '
                 f'color="{col}" textAlign="LEFT" softWrap="false" maxLines="1">'
                 f'<![CDATA[{p["text"]}]]></Text></Container></Positioned>')


def text_center(key, cx, ink_top, box_w, color, box_h=None):
    """水平居中 + 垂直居中的文本（值标签/刻度/季度标签）。"""
    p = P[key]
    bh = box_h if box_h else p["ink_h"] + 14
    # 垂直居中：盒顶 = 目标墨迹顶 - (盒高-墨迹高)/2
    top = ink_top - (bh - p["ink_h"]) / 2
    nodes.append(f'<Positioned left="{cx - box_w / 2:.2f}" top="{top:.2f}" width="{box_w:.2f}" height="{bh:.2f}">'
                 f'<Container color="transparent" alignment="CENTER">'
                 f'<Text fontSize="{p["size"]}" fontFamily="{p["family"]}" fontStyle="{p["style"]}" '
                 f'color="{color}" textAlign="CENTER" softWrap="false" maxLines="1">'
                 f'<![CDATA[{p["text"]}]]></Text></Container></Positioned>')


# ================= 背景 =================
rect(0, 0, W, H, C["bg"])

# ================= 页眉 =================
text_left("h1", 60, 46, box_w=560, color=C["ink"])
text_left("h2", 60, 102, box_w=1000, color=C["label"])

# ================= 图表卡 =================
rect(60, 160, 770, 500, C["card"], r=12, border=C["border"])
text_left("c_title", 88, 186, box_w=260, color=C["ink"])
text_left("c_unit", 712, 190, box_w=120, color=C["sub"])

# 图例（与数据一致：蓝=收入，橙=成本）
rect(616, 214, 20, 20, C["rev"], r=4)
text_left("lg_rev", 644, 218, box_w=80)
rect(716, 214, 20, 20, C["cost"], r=4)
text_left("lg_cost", 744, 218, box_w=80)

# 网格线 + 零线
ax = D["axes"]
for t in ax["ticks"]:
    gy = ax["tick_y_px"][str(t)]
    if t == 0:
        rect(ax["plot"]["left"], gy, ax["plot"]["right"] - ax["plot"]["left"], 2, C["axis"])
    else:
        line(ax["plot"]["left"], gy, ax["plot"]["right"] - ax["plot"]["left"], C["grid"])

# 刻度标签（右对齐至 x=140，垂直居中于网格线）
tick_keys = {0: "tick_0", 50: "tick_50", 100: "tick_100", 150: "tick_150", 200: "tick_200"}
for t in ax["ticks"]:
    gy = ax["tick_y_px"][str(t)]
    text_center(tick_keys[t], 40 + 51, gy, 102, C["tick"])  # 盒中心 x=91，右缘=142

# 柱 + 值标签
for b in ax["bars"]:
    color = C["rev"] if b["series"] == "revenue" else C["cost"]
    rect(b["x"], b["top_y"], b["width"], b["height"], color, r=4)
    vkey = {120: "v_120", 90: "v_90", 135: "v_135", 108: "v_108",
            128: "v_128", 96: "v_96", 180: "v_180", 126: "v_126"}[int(b["value_wan"])]
    tx_color = C["rev_tx"] if b["series"] == "revenue" else C["cost_tx"]
    text_center(vkey, b["x"] + b["width"] / 2, b["top_y"] - 21, 100, tx_color)

# 季度标签
qkeys = ["q_Q1", "q_Q2", "q_Q3", "q_Q4"]
centers = [231, 394, 556, 719]
for k, cx in zip(qkeys, centers):
    text_center(k, cx, 616, 120, C["body"])

# ================= 利润明细卡 =================
rect(850, 160, 370, 270, C["card"], r=12, border=C["border"])
text_left("p_title", 878, 186, box_w=240, color=C["ink"])
text_left("p_sub", 878, 218, box_w=320, color=C["sub"])
rows = [("p_q1", "p_v1"), ("p_q2", "p_v2"), ("p_q3", "p_v3"), ("p_q4", "p_v4")]
for i, (lk, vk) in enumerate(rows):
    ry = 250 + i * 46
    text_left(lk, 878, ry + 9, box_w=60, color=C["label"])
    text_left(vk, 1104, ry + 5, box_w=100, color=C["ink"])
    if i < 3:
        line(878, ry + 38, 314, C["hair"])

# ================= 重点观察卡 =================
rect(850, 450, 370, 210, C["amber_bg"], r=12, border=C["amber_bd"])
text_left("o_title", 878, 476, box_w=280, color=C["amber_tx"])
for i, k in enumerate(["o_l1", "o_l2", "o_l3", "o_l4"]):
    text_left(k, 878, 520 + i * 34, box_w=314, color=C["amber_body"])

# ================= 全年合计 KPI 条 =================
rect(60, 690, 1160, 110, C["card"], r=12, border=C["border"])
vline(433, 712, 66, C["hair"])
vline(793, 712, 66, C["hair"])
kpis = [("k_l1", "k_v1", 253, C["rev"]), ("k_l2", "k_v2", 613, C["cost_tx"]), ("k_l3", "k_v3", 973, C["profit"])]
for lk, vk, cx, vc in kpis:
    text_left(lk, cx - P[lk]["ink_w"] / 2 - P[lk]["ink_left"], 716, box_w=200, color=C["label"])
    text_left(vk, cx - P[vk]["ink_w"] / 2 - P[vk]["ink_left"], 748, box_w=200, color=vc)

# ================= 页脚 =================
text_left("f1", 60, 854, box_w=940, color=C["footer"])

# ================= 输出 =================
dsl = (f'<Snapshot type="png" background="{C["bg"]}">'
       f'<Container width="{W}" height="{H}">'
       f'<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE">'
       + "".join(nodes) + "</Stack></Container></Snapshot>")

dsl_file = TMP / "corrected-v1.snapshot"
dsl_file.write_text(dsl, encoding="utf-8")
log = R.Log(ROOT, RUN_ID, "A16")
res = R.render(dsl_file, TMP / "corrected-v1.png", ROOT, log, label="A16-corrected-v1")
print("render:", res["record"]["status"], res["record"].get("error") or "", "nodes:", len(nodes))
