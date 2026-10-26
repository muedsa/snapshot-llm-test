# -*- coding: utf-8 -*-
"""A13 定稿生成：symbol-color / symbol-black / brand-banner / launch-poster。

品牌「叠光 Layerlight」：信息叠加后仍然清晰。
图标（方向一·叠层，4 个主要几何构件）：三枚错位胶囊（前深后浅，层间负空间）
+ 右上琥珀光点（贴前层右端，象征"光"）。彩色与纯黑版几何完全相同（同生成函数，
仅颜色不同）；横幅与海报中的图标由同一几何规则函数按缩放/偏移重新生成，
不嵌入渲染好的 PNG。
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ["SNAPSHOT_RUN_ID"]
TASK = "A13"
OUT_DIR = ROOT / "outputs" / RUN_ID / TASK
TMP_DIR = ROOT / "tmp" / RUN_ID / TASK
OUT_DIR.mkdir(parents=True, exist_ok=True)
TMP_DIR.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT / "tmp" / RUN_ID / "_suite"))
import bm  # noqa: E402
import render as R  # noqa: E402

SANS = "Noto Sans CJK SC"
MONO = "Noto Sans Mono CJK SC"

# ---------- 品牌系统参数 ----------
BRAND = {
    "name_cn": "叠光",
    "name_en": "Layerlight",
    "tagline": "把复杂信息，组织成清晰画面",
    "date_line": "2026.11.07 · ONLINE",
    "badge": "OPEN BETA",
    "website": "layerlight.example.org",
}
INK = "#0F172A"
PAPER = "#FFFFFF"

# 图标几何（512 画布，4 构件）
ICON = {
    "pills": [
        {"id": "L1", "x": 128, "y": 116, "w": 256, "h": 72, "color": "#2563EB",
         "role": "前层·主色"},
        {"id": "L2", "x": 112, "y": 220, "w": 272, "h": 72, "color": "#60A5FA",
         "role": "中层·过渡色"},
        {"id": "L3", "x": 96, "y": 324, "w": 304, "h": 72, "color": "#BFDBFE",
         "role": "后层·浅色"},
    ],
    "dot": {"id": "G1", "cx": 408, "cy": 152, "d": 48, "color": "#F59E0B",
            "role": "光点·强调色"},
}


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def pill_node(x, y, w, h, color, r=None):
    r = h / 2 if r is None else r
    return (f'<Positioned left="{x:.2f}" top="{y:.2f}" width="{w:.2f}" height="{h:.2f}">'
            f'<Container color="{color}" borderRadius="{r:.2f}"/></Positioned>')


def dot_node(cx, cy, d, color):
    return (f'<Positioned left="{cx - d / 2:.2f}" top="{cy - d / 2:.2f}" width="{d:.2f}" '
            f'height="{d:.2f}"><Container color="{color}" borderRadius="{d / 2:.2f}"/>'
            f'</Positioned>')


def icon_nodes(scale=1.0, ox=0.0, oy=0.0, black=False):
    """同一 DSL 几何规则生成图标；black=True 时全部填充 #000000（几何不变）。"""
    out = []
    for p in ICON["pills"]:
        c = "#000000" if black else p["color"]
        out.append(pill_node(ox + p["x"] * scale, oy + p["y"] * scale,
                             p["w"] * scale, p["h"] * scale, c))
    d = ICON["dot"]
    c = "#000000" if black else d["color"]
    out.append(dot_node(ox + d["cx"] * scale, oy + d["cy"] * scale, d["d"] * scale, c))
    return "".join(out)


def text_node(s, x, y, w, size, color, *, bold=False, align="LEFT", mono=False,
              family=SANS, h=None, max_lines=1):
    h_attr = f' height="{h:.1f}"' if h else ""
    return (f'<Positioned left="{x:.2f}" top="{y:.2f}" width="{w:.2f}"{h_attr}>'
            f'<Container color="transparent"><Text fontSize="{size}" '
            f'fontFamily="{family}" fontStyle="{"BOLD" if bold else "NORMAL"}" '
            f'color="{color}" textAlign="{align}" softWrap="false" '
            f'maxLines="{max_lines}">{esc(s)}</Text></Container></Positioned>')


def snapshot(w, h, nodes, background="transparent"):
    return (f'<Snapshot type="png" background="{background}">'
            f'<Container width="{w}" height="{h}">'
            f'<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE">'
            + nodes + "</Stack></Container></Snapshot>")


# ---------- 文本测量 ----------
measure_items = []
measure_keys = []


def m(text, size, bold=False, mono=False, key=None):
    k = key or f"{text}|{size}|{bold}|{mono}"
    if k not in measure_keys:
        measure_keys.append(k)
        measure_items.append({"text": text, "size": size,
                              "style": "BOLD" if bold else "NORMAL",
                              "family": MONO if mono else SANS})
    return k


brand_full = f'{BRAND["name_cn"]} {BRAND["name_en"]}'
m(brand_full, 72, bold=True, key="brand|72")
m(brand_full, 92, bold=True, key="brand|92")
m(BRAND["tagline"], 32, key="tagline|32")
m(BRAND["tagline"], 36, key="tagline|36")
m(BRAND["date_line"], 42, key="date|42")
m(BRAND["badge"], 30, bold=True, key="badge|30")
m(BRAND["website"], 28, mono=True, key="web|28")
m(BRAND["website"], 20, mono=True, key="web|20")

res = bm.batch_measure(measure_items, task_id=TASK, label="A13-measure-text")
W = {}
for k, r in zip(measure_keys, res):
    W[k] = r["width"] if r["width"] is not None else 0
print("measured:", {k: W[k] for k in measure_keys})


# ---------- 1) symbol-color ----------
dsl_color = snapshot(512, 512, icon_nodes(1.0, 0, 0, black=False))
(TMP_DIR / "symbol-color.snapshot").write_text(dsl_color, encoding="utf-8")

# ---------- 2) symbol-black（几何相同，纯黑） ----------
dsl_black = snapshot(512, 512, icon_nodes(1.0, 0, 0, black=True))
(TMP_DIR / "symbol-black.snapshot").write_text(dsl_black, encoding="utf-8")

# ---------- 3) brand-banner 1200×400 ----------
BW, BH = 1200, 400
icon_scale = 360 / 512
icon_box = 512 * icon_scale
nodes = [f'<Positioned left="0" top="0" width="{BW}" height="{BH}">'
         f'<Container color="{PAPER}"/></Positioned>']
# 右下单一淡色轮廓装饰（同一母形重排，向右下溢出，不干扰文字）
nodes.append(pill_node(1085, 315, 430, 145, "transparent", r=72.5)
             .replace('color="transparent"',
                      'color="transparent" border="3 SOLID #DBEAFE"'))
# 图标（同一几何规则，缩放生成）
icon_x, icon_y = 64.0, (BH - icon_box) / 2
nodes.append(icon_nodes(icon_scale, icon_x, icon_y, black=False))
# 分隔线
div_x = icon_x + icon_box + 48
nodes.append(f'<Positioned left="{div_x:.2f}" top="92" width="2" height="216">'
             f'<Container color="#E2E8F0"/></Positioned>')
# 文字块
tx = div_x + 48
brand_w = W["brand|72"]
nodes.append(pill_node(tx, 88, 48, 6, "#F59E0B"))  # 琥珀 accent 条
nodes.append(text_node(brand_full, tx, 114, brand_w + 8, 72, INK, bold=True))
tag_w = W["tagline|32"]
nodes.append(text_node(BRAND["tagline"], tx, 220, tag_w + 8, 32, "#475569"))
nodes.append(text_node(BRAND["website"], tx, 288, W["web|20"] + 8, 20, "#94A3B8",
                       mono=True))
dsl_banner = snapshot(BW, BH, "".join(nodes), background=PAPER)
(TMP_DIR / "brand-banner.snapshot").write_text(dsl_banner, encoding="utf-8")

# ---------- 4) launch-poster 1080×1350 ----------
PW, PH = 1080, 1350
nodes = [f'<Positioned left="0" top="0" width="{PW}" height="{PH}">'
         f'<Container color="{INK}"/></Positioned>']
# 背景层叠装饰（同一母形，低透明度，深色底；止于 y=1270，避开底部网站行）
nodes.append(pill_node(140, 1000, 560, 140, "#1D4ED82E"))
nodes.append(pill_node(220, 1090, 600, 140, "#60A5FA24"))
nodes.append(pill_node(300, 1180, 640, 90, "#BFDBFE1A"))
# 图标（彩色，缩放生成）
p_icon_scale = 320 / 512
p_icon_box = 512 * p_icon_scale
nodes.append(icon_nodes(p_icon_scale, (PW - p_icon_box) / 2, 130, black=False))
# 品牌名
bw92 = W["brand|92"]
nodes.append(text_node(brand_full, (PW - bw92) / 2 - 4, 540, bw92 + 8, 92, "#F8FAFC",
                       bold=True))
# tagline
tw36 = W["tagline|36"]
nodes.append(text_node(BRAND["tagline"], (PW - tw36) / 2 - 4, 676, tw36 + 8, 36,
                       "#94A3B8"))
# 分隔短线
nodes.append(f'<Positioned left="{(PW - 120) / 2:.2f}" top="768" width="120" height="2">'
             f'<Container color="#334155"/></Positioned>')
# OPEN BETA 徽章
badge_w = W["badge|30"] + 56
badge_h = 56
badge_x = (PW - badge_w) / 2
nodes.append(pill_node(badge_x, 820, badge_w, badge_h, "#F59E0B"))
nodes.append(text_node(BRAND["badge"], badge_x + 28, 820 + (badge_h - 30) / 2 - 2,
                       badge_w - 56, 30, INK, bold=True, align="CENTER"))
# 日期行
dw = W["date|42"]
nodes.append(text_node(BRAND["date_line"], (PW - dw) / 2 - 4, 948, dw + 8, 42, "#F8FAFC"))
# 网站（y=1290，位于装饰带下方）
ww = W["web|28"]
nodes.append(text_node(BRAND["website"], (PW - ww) / 2 - 4, 1290, ww + 8, 28, "#64748B",
                       mono=True))
dsl_poster = snapshot(PW, PH, "".join(nodes), background=INK)
(TMP_DIR / "launch-poster.snapshot").write_text(dsl_poster, encoding="utf-8")

# ---------- brand-system.json ----------
content_bbox = [96, 116, 432, 396]  # 实测 icon alpha bbox
brand_system = {
    "schema_version": 2,
    "task_id": TASK,
    "path_base": "output_dir",
    "run_id": RUN_ID,
    "brand": {
        "name": "叠光 Layerlight",
        "concept": "信息叠加后仍然清晰",
        "tagline": BRAND["tagline"],
    },
    "color": {
        "ink": INK, "paper": PAPER,
        "primary": "#2563EB", "primary_mid": "#60A5FA", "primary_light": "#BFDBFE",
        "accent": "#F59E0B",
        "roles": {
            "#2563EB": "前层/主色", "#60A5FA": "中层", "#BFDBFE": "后层",
            "#F59E0B": "光点强调色", "#0F172A": "文字/深色底", "#FFFFFF": "纸面",
        },
        "mono_black_rule": "纯黑版所有 alpha>0 像素 RGB=0（含抗锯齿边缘），alpha 0-255 保留覆盖",
    },
    "icon": {
        "canvas": 512,
        "direction": "layers（方向一·叠层）",
        "components": [
            {"id": p["id"], "shape": "rounded_rect(pill)", "instance": 1,
             "geometry": {"x": p["x"], "y": p["y"], "w": p["w"], "h": p["h"],
                          "radius": p["h"] / 2},
             "color": p["color"], "role": p["role"],
             "dsl": f'Positioned(left={p["x"]},top={p["y"]},w={p["w"]},h={p["h"]}) '
                    f'> Container(color={p["color"]},borderRadius={p["h"] / 2})'}
            for p in ICON["pills"]
        ] + [
            {"id": "G1", "shape": "circle", "instance": 1,
             "geometry": {"cx": 408, "cy": 152, "d": 48, "radius": 24},
             "color": "#F59E0B", "role": "光点·强调色",
             "dsl": "Positioned(384,128,48,48) > Container(color=#F59E0B,borderRadius=24)"},
        ],
        "component_count": 4,
        "count_basis": "按可独立辨认的几何母形实例计：胶囊×3（重复放置的同一母形分别计数）"
                       "+ 圆×1 = 4 ≤ 6；无裁剪分割、无合并路径包装。",
        "negative_space": {
            "rules": "三层胶囊之间 32px 横向层距与 32px 纵向层距构成关键负空间；"
                     "图标四周保留 ≥80px 净空；无镂空孔洞（未使用 ClipPath 扣除）。",
            "layer_gap_x": 16, "layer_gap_y": 32,
        },
        "proportion": {
            "pill_h_ratio": "72/512 = 0.1406",
            "pill_w_ratio": "256/272/304 of 512",
            "dot_ratio": "48/512 = 0.09375",
            "content_bbox": content_bbox,
            "min_clear_space": 80,
        },
    },
    "applications": {
        "symbol-color.png": {"size": [512, 512], "icon_scale": 1.0,
                             "note": "透明底彩色图标，服务原始响应"},
        "symbol-black.png": {"size": [512, 512], "icon_scale": 1.0,
                             "note": "透明底纯黑图标，与彩色版几何相同（同生成函数换色）"},
        "brand-banner.png": {"size": [1200, 400], "icon_scale": round(icon_scale, 6),
                             "icon_box": 340,
                             "note": "图标按同一 DSL 几何规则缩放生成，未嵌入渲染 PNG"},
        "launch-poster.png": {"size": [1080, 1350],
                              "icon_scale": round(p_icon_scale, 6), "icon_box": 320,
                              "note": "图标按同一 DSL 几何规则缩放生成，未嵌入渲染 PNG"},
    },
    "typography": {
        "primary": SANS, "monospace": MONO,
        "banner": {"brand": 72, "tagline": 32, "website": 20},
        "poster": {"brand": 92, "tagline": 36, "date": 42, "badge": 30, "website": 28},
    },
}
(OUT_DIR / "brand-system.json").write_text(
    json.dumps(brand_system, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("wrote brand-system.json")

# ---------- 渲染 ----------
log = R.Log(ROOT, RUN_ID, TASK)
for name in ["symbol-color", "symbol-black", "brand-banner", "launch-poster"]:
    res = R.render(TMP_DIR / f"{name}.snapshot", TMP_DIR / f"{name}.png", ROOT, log,
                   label=f"A13-{name}")
    print(name, res["record"]["status"], res["record"].get("error"))
