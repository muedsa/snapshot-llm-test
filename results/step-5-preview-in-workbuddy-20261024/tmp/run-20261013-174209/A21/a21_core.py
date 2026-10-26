"""A21 核心：品牌系统、设计令牌、三构图布局、场景收集。

品牌图形“叠光 Layerlight”= 5 个可识别构件（外环 / 中盘 / 内核 / 三条层纹 / 斜光束），
跨轮与跨尺寸保持同一几何参数，仅按主题切换色值与不透明度。
"""
from __future__ import annotations
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent.parent
RUN_ID = "run-20261013-174209"
TMP = ROOT / "tmp" / RUN_ID / "A21"
OUT = ROOT / "outputs" / RUN_ID / "A21"

CJK = "Noto Sans CJK SC"
LATIN = "Inter"
LATIN_BLACK = "Inter Black"
LATIN_SEMI = "Inter Semi Bold"

# ---------------------------------------------------------------- 令牌
TOKENS = {
    1: {
        "round": 1, "theme": "dark",
        "page_bg": "#0B1020",
        "card_bg": "#151B2E",
        "card_border": "#2A3352",
        "divider": "#6366F1",
        "brand_500": "#6366F1", "brand_300": "#A5B4FC", "brand_700": "#4338CA",
        "accent_cyan": "#22D3EE", "accent_amber": "#FBBF24",
        "text_primary": "#F8FAFC", "text_secondary": "#B9C2D6",
        "text_brand": "#A5B4FC",
        "emblem_alphas": {"disc": 0.50, "dot": 0.95, "beam": 0.50,
                          "bar": 1.00, "ring": 1.00},
        "pill_bg": "#141B31", "pill_border": "#6366F1", "pill_text": "#C7D2FE",
    },
    2: {
        "round": 2, "theme": "dark",
        "page_bg": "#0B1020",
        "card_bg": "#151B2E",
        "card_border": "#2A3352",
        "divider": "#6366F1",
        "brand_500": "#6366F1", "brand_300": "#A5B4FC", "brand_700": "#4338CA",
        "accent_cyan": "#22D3EE", "accent_amber": "#FBBF24",
        "text_primary": "#F8FAFC", "text_secondary": "#B9C2D6",
        "text_brand": "#A5B4FC",
        "emblem_alphas": {"disc": 0.50, "dot": 0.95, "beam": 0.50,
                          "bar": 1.00, "ring": 1.00},
        "pill_bg": "#141B31", "pill_border": "#6366F1", "pill_text": "#C7D2FE",
    },
    3: {
        "round": 3, "theme": "light",
        "page_bg": "#F6F7FB",
        "card_bg": "#FFFFFF",
        "card_border": "#D7DCEA",
        "divider": "#4F46E5",
        "brand_500": "#4F46E5", "brand_300": "#4338CA", "brand_700": "#3730A3",
        "accent_cyan": "#0E7490", "accent_amber": "#B45309",
        "text_primary": "#0F172A", "text_secondary": "#3A4560",
        "text_brand": "#4338CA",
        "emblem_alphas": {"disc": 0.30, "dot": 0.95, "beam": 0.40,
                          "bar": 0.90, "ring": 1.00},
        "pill_bg": "#EEF0FA", "pill_border": "#4F46E5", "pill_text": "#3730A3",
    },
}

TYPO = {
    "cjk_family": CJK, "latin_family": LATIN,
    "latin_black": LATIN_BLACK, "latin_semi": LATIN_SEMI,
    "line_height_ratio": 1.45,
}

# ---------------------------------------------------------------- 文案
TITLE_R1 = "让复杂信息变得清晰"
TITLE_R2_LINES = ["当所有信息都想成为标题：", "让复杂信息变得清晰的", "结构化方法"]
SUBTITLE = "叠光 Layerlight 线上发布活动 · 结构化信息设计"
DATE_TEXT = "2026.11.07 19:30"
SPEAKERS_TEXT = "讲者：林川 / 苏言"
URL_TEXT = "layerlight.example.org"
BADGE_TEXT = "ONLINE LAUNCH"
FREE_TEXT = "免费参加 · 无需报名"
SPONSORS_TEXT = "赞助方：Northstar Research / 云构工具"
EN_TEXT = "Clarity through structure"
WORDMARK = "叠光 Layerlight"


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def alpha_hex(hexc: str, a: float) -> str:
    """#RRGGBB + alpha -> #RRGGBBAA"""
    h = hexc.lstrip("#")
    return f"#{h}{int(round(max(0.0, min(1.0, a)) * 255)):02X}"


def positioned(left, top, w, h, inner):
    return (f'<Positioned left="{left:.2f}" top="{top:.2f}" width="{w:.2f}" '
            f'height="{h:.2f}">{inner}</Positioned>')


def rect(left, top, w, h, color, radius=0.0, border=None):
    b = f' border="{border}"' if border else ""
    r = f' borderRadius="{radius:.2f}"' if radius else ""
    return (f'<Container width="{w:.2f}" height="{h:.2f}" color="{color}"{r}{b}/>')


def circle(cx, cy, d, color, border=None):
    b = f' border="{border}"' if border else ""
    return (f'<Container width="{d:.2f}" height="{d:.2f}" color="{color}"{b} '
            f'shape="CIRCLE"/>')


def text_node(s, left, top, w, h, size, color, align="LEFT", style="NORMAL",
              family=CJK):
    return positioned(left, top, w, h,
                      f'<Container color="transparent" alignment="TOP_LEFT">'
                      f'<Text fontSize="{size}" fontFamily="{family}" '
                      f'fontStyle="{style}" color="{color}" textAlign="{align}" '
                      f'softWrap="false" maxLines="1">{esc(s)}</Text></Container>')


def line_seg(x1, y1, x2, y2, w=1.0, color="#6366F1"):
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy)
    if L < 1e-6:
        return ""
    ux, uy = dx / L, dy / L
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    m = (ux, uy, 0, 0, -uy, ux, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1)
    mat = "(" + ",".join(f"{v:.9f}" for v in m) + ")"
    return (f'<Positioned left="{mx - L / 2:.2f}" top="{my - w / 2:.2f}" '
            f'width="{L:.2f}" height="{w:.2f}" alignment="CENTER">'
            f'<Transform matrix="{mat}">'
            f'<Container width="{L:.2f}" height="{w:.2f}" color="{color}"/>'
            f'</Transform></Positioned>')


# ---------------------------------------------------------------- 品牌图形
EMBLEM = {
    "components": [
        {"id": "C1", "name": "外环", "kind": "ring", "d": 140.0, "border": 12.0,
         "dx": -56.0, "dy": 0.0, "color_role": "brand_500", "alpha_key": "ring"},
        {"id": "C2", "name": "中盘", "kind": "disc", "d": 76.0,
         "dx": -56.0, "dy": 0.0, "color_role": "brand_500", "alpha_key": "disc"},
        {"id": "C3", "name": "内核", "kind": "disc", "d": 30.0,
         "dx": -56.0, "dy": 0.0, "color_role": "brand_300", "alpha_key": "dot"},
        {"id": "C4", "name": "层纹三条", "kind": "bars",
         "widths": [116.0, 84.0, 52.0], "height": 9.0, "pitch": 13.0,
         "dx": 30.0, "dy": -49.0, "color_role": "brand_500", "alpha_key": "bar"},
        {"id": "C5", "name": "斜光束", "kind": "beam", "len": 120.0, "thick": 9.0,
         "angle": -30.0, "dx": 10.0, "dy": -42.0, "color_role": "accent_amber",
         "alpha_key": "beam"},
    ],
    "extent": {"w": 272.0, "h": 145.9},
    "bbox_offsets": {"left": -126.0, "top": -75.9, "right": 146.0, "bottom": 70.0},
}


def emblem_nodes(cx, cy, s, tok):
    """5 构件品牌图形；s 为缩放（1.0 时整体约 272x148）。"""
    out = []
    al = tok["emblem_alphas"]
    for c in EMBLEM["components"]:
        col = alpha_hex(tok[c["color_role"]], al[c["alpha_key"]])
        if c["kind"] == "ring":
            d = c["d"] * s
            out.append(positioned(cx + c["dx"] * s - d / 2, cy + c["dy"] * s - d / 2,
                                  d, d,
                                  circle(0, 0, d, "transparent",
                                         border=f'{c["border"] * s:.2f} SOLID {col}')))
        elif c["kind"] == "disc":
            d = c["d"] * s
            out.append(positioned(cx + c["dx"] * s - d / 2, cy + c["dy"] * s - d / 2,
                                  d, d, circle(0, 0, d, col)))
        elif c["kind"] == "bars":
            x0 = cx + c["dx"] * s
            y0 = cy + c["dy"] * s
            hgt = c["height"] * s
            for i, w in enumerate(c["widths"]):
                out.append(positioned(x0, y0 + i * c["pitch"] * s, w * s, hgt,
                                      rect(0, 0, w * s, hgt, col, radius=hgt / 2)))
        elif c["kind"] == "beam":
            L, T = c["len"] * s, c["thick"] * s
            bcx, bcy = cx + c["dx"] * s, cy + c["dy"] * s
            ang = math.radians(c["angle"])
            ux, uy = math.cos(ang), math.sin(ang)
            m = (ux, uy, 0, 0, -uy, ux, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1)
            mat = "(" + ",".join(f"{v:.9f}" for v in m) + ")"
            # alignment="CENTER" 必须放在 Transform 上（绕子节点中心旋转）；
            # 放在 Positioned 上会变成绕框左上角旋转，整条光束偏移约 (L/2·sin, ...)
            out.append(f'<Positioned left="{bcx - L / 2:.2f}" top="{bcy - T / 2:.2f}" '
                       f'width="{L:.2f}" height="{T:.2f}">'
                       f'<Transform matrix="{mat}" alignment="CENTER">'
                       f'<Container width="{L:.2f}" height="{T:.2f}" color="{col}" '
                       f'borderRadius="{T / 2:.2f}"/></Transform></Positioned>')
    return out


def emblem_extent(s):
    return EMBLEM["extent"]["w"] * s, EMBLEM["extent"]["h"] * s


EMBLEM_BBOX = EMBLEM["bbox_offsets"]


# ---------------------------------------------------------------- 文案条目
def content_entries(rnd):
    """稳定文案 ID；文本随轮变化，ID 不变。"""
    if rnd == 1:
        title = [TITLE_R1]
    else:
        title = list(TITLE_R2_LINES)
    ents = [
        {"id": "title", "kind": "main_title", "text": title,
         "min_size": 56 if rnd == 1 else 48},
        {"id": "badge", "kind": "badge", "text": [BADGE_TEXT], "min_size": 24},
        {"id": "wordmark", "kind": "wordmark", "text": [WORDMARK], "min_size": 24},
        {"id": "subtitle", "kind": "subtitle", "text": [SUBTITLE], "min_size": 24},
        {"id": "datetime", "kind": "meta", "text": [DATE_TEXT], "min_size": 24},
        {"id": "speakers", "kind": "meta", "text": [SPEAKERS_TEXT], "min_size": 24},
        {"id": "url", "kind": "url", "text": [URL_TEXT], "min_size": 24},
    ]
    if rnd >= 2:
        ents.append({"id": "free_entry", "kind": "badge", "text": [FREE_TEXT],
                     "min_size": 24})
        ents.append({"id": "sponsors", "kind": "meta", "text": [SPONSORS_TEXT],
                     "min_size": 24})
    if rnd >= 3:
        ents.append({"id": "en_tagline", "kind": "tagline", "text": [EN_TEXT],
                     "min_size": 24})
    return ents
