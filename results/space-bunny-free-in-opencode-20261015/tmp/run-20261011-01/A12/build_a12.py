#!/usr/bin/env python
"""A12 四断点完整内容视觉系统 —— 同一份内容 + 同一套设计令牌生成四张完整 DSL。

启动基准：总任务根 (suite_root)。输入 tasks/A12-responsive-system/inputs/content.json 只读。

要点：
  * 四个画布各自生成**完整**的 DSL（不是裁切/拉伸/整图 Image），共用同一套 design tokens；
  * 装饰使用相同核心构件（hero 几何组合 / 卡片刻意式 / CTA 条 / meta 行），只按断点重排；
  * 每个必显字段都登记实际文字盒，输出 content-map.json；
  * 所有字面量走 `text="…"` 属性（实测本服务不解码 XML 实体，见 A11）。
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, "tmp/run-20261011-01/_suite/scripts")
import snapkit as sk  # noqa: E402

TASK = "A12"
BASE = "tasks/A12-responsive-system"
CONTENT_IN = f"{BASE}/inputs/content.json"
DRAFTS = f"tmp/run-20261011-01/{TASK}/drafts"

F_HEAD = "Inter Semi Bold"
F_NUM = "Inter Medium"
F_LATIN = "Inter"
F_SC = "Noto Sans CJK SC"
F_MIX = f"{F_LATIN},{F_SC}"
F_MIX_HEAD = f"{F_HEAD},{F_SC}"

# ------------------------------------------------------------------ 设计令牌（四尺寸统一）
TOKENS = {
    "color": {
        "brand": "#1D4ED8", "brand_soft": "#DBEAFE", "brand_tint": "#EFF6FF",
        "accent": "#0F766E", "accent_soft": "#CCFBF1",
        "ink": "#0F172A", "ink_2": "#1E293B", "muted": "#64748B", "faint": "#94A3B8",
        "paper": "#FFFFFF", "canvas": "#F5F8FC",
        "line": "#E2E8F0", "line_strong": "#CBD5E1", "cta_text": "#FFFFFF",
        "hero_deco_line": "#BFDBFE",
    },
    "radius": {"card": 16, "card_bar": 3, "chip": 10, "cta": 14, "badge": 13, "pill": 999},
    "shadow": {"card": "0 2 10 0 #0F172A0F", "cta": "0 6 18 0 #1D4ED833"},
    "type_scale": {
        "display": {"mobile": 40, "tablet": 56, "desktop": 72, "stage": 88},
        "subtitle": {"mobile": 18, "tablet": 24, "desktop": 26, "stage": 30},
        "card_title": {"mobile": 19, "tablet": 22, "desktop": 24, "stage": 26},
        "card_detail": {"mobile": 17, "tablet": 20, "desktop": 20, "stage": 22},
        "meta_label": {"mobile": 16, "tablet": 15, "desktop": 16, "stage": 17},
        "meta_value": {"mobile": 17, "tablet": 20, "desktop": 20, "stage": 22},
        "cta": {"mobile": 18, "tablet": 22, "desktop": 24, "stage": 26},
        "section": {"mobile": 17, "tablet": 20, "desktop": 21, "stage": 23},
        "badge": {"mobile": 16, "tablet": 15, "desktop": 16, "stage": 17},
        "footer": {"mobile": 16, "tablet": 15, "desktop": 15, "stage": 16},
    },
    "spacing": {
        "margin": {"mobile": 16, "tablet": 32, "desktop": 32, "stage": 48},
        "unit": {"mobile": 8, "tablet": 12, "desktop": 14, "stage": 18},
        "card_gap": {"mobile": 8, "tablet": 16, "desktop": 24, "stage": 28},
        "card_pad": {"mobile": 10, "tablet": 20, "desktop": 22, "stage": 26},
    },
    "layout_rules": {
        "mobile": "单列：页眉条 → 主标题 → 副标题 → meta 两列 → CTA → 六张卡纵向单列 → 页脚",
        "tablet": "单列宽版：页眉条 → 主标题 → 副标题 → meta 两列 → CTA → 六张卡 2 列 × 3 行 → 页脚",
        "desktop": "单列宽版：页眉条 → 主标题 → 副标题 → meta 四列一行 → CTA → 六张卡 3 列 × 2 行 → 页脚",
        "stage": "单列宽版：页眉条 → 主标题 → 副标题 → meta 四列一行 → CTA → 六张卡 3 列 × 2 行（加大留白）→ 页脚",
        "shared": "四个断点的色彩、圆角、卡片刻意式、CTA 形态与层级完全一致，只有列数、间距与字号缩放不同",
    },
    "component_rules": [
        {"component": "顶栏条", "rule": "左侧品牌块（6×字号高的品牌色圆角条 + 品牌名），右侧标注当前断点名；四个断点同一构件"},
        {"component": "Hero 几何组合", "rule": "描边方块 + 实心圆 + 两根圆角横条，按断点缩放并重排到主标题右上/右侧；不随文字裁切"},
        {"component": "主标题 display", "rule": "Inter Semi Bold + Noto Sans CJK SC，≥40px，按可用宽度自动折行，不缩字"},
        {"component": "meta 行", "rule": "标签（faint，小字）+ 值（ink，较大），按断点 2 列（手机/平板）或 4 列（桌面/大屏）排布"},
        {"component": "CTA 条", "rule": "品牌色填充圆角矩形 + 白色 CTA 文案 + 左侧实心圆点，四个断点同一形态"},
        {"component": "卡片", "rule": "白底 + 细边 + 圆角 + 左侧 6px 品牌色竖条；编号徽章（胶囊）+ 卡标题 + detail；四个断点同一构件，仅尺寸与列数变化"},
        {"component": "页脚", "rule": "细分隔线 + 断点尺寸 + 活动编号式说明；四个断点同一构件"},
    ],
    "constraints": {
        "mobile_body_min_px": 16, "card_title_min_px": 18,
        "other_body_min_px": 20, "display_min_px": 40,
        "safe_margin_min": {"mobile": 16, "tablet": 32, "desktop": 32, "stage": 32},
        "actual_margin_used": {"mobile": 16, "tablet": 32, "desktop": 32, "stage": 48},
        "forbidden": ["裁切", "拉伸", "整图 <Image> 适配", "省略号", "缩写", "改写", "删句", "二维码"],
    },
}

BREAKPOINTS = [
    {"meta_span": [1, 1, 2, 2], "footer_web": False, "key": "mobile", "label": "窄手机", "w": 360, "h": 800, "cols": 1, "card_rows": 6,
     "meta_cols": 2, "deco_s": 20, "top_h": 26, "cta_h": 44,
     "card_h": 52, "card_gap": 4, "card_pad": 5, "card_variant": "inline",
     "badge": (38, 18), "gap_title": 8, "gap_detail": 4},
    {"meta_span": [1, 1, 1, 1], "footer_web": True, "key": "tablet", "label": "平板", "w": 768, "h": 1024, "cols": 2, "card_rows": 3,
     "meta_cols": 2, "deco_s": 36, "top_h": 36, "cta_h": 64,
     "card_h": 160, "card_gap": 16, "card_pad": 20, "card_variant": "stack",
     "badge": (52, 24), "gap_title": 8, "gap_detail": 10},
    {"meta_span": [1, 1, 1, 1], "footer_web": True, "key": "desktop", "label": "桌面", "w": 1440, "h": 900, "cols": 3, "card_rows": 2,
     "meta_cols": 4, "deco_s": 50, "top_h": 40, "cta_h": 72,
     "card_h": 168, "card_gap": 24, "card_pad": 22, "card_variant": "stack",
     "badge": (52, 24), "gap_title": 8, "gap_detail": 10},
    {"meta_span": [1, 1, 1, 1], "footer_web": True, "key": "stage", "label": "大屏", "w": 1920, "h": 1080, "cols": 3, "card_rows": 2,
     "meta_cols": 4, "deco_s": 58, "top_h": 48, "cta_h": 84,
     "card_h": 180, "card_gap": 28, "card_pad": 26, "card_variant": "stack",
     "badge": (56, 26), "gap_title": 10, "gap_detail": 12},
]

C = TOKENS["color"]
R = TOKENS["radius"]


# ------------------------------------------------------------------ 图元
def rect(x, y, w, h, color, radius=0, border=None, shadow=None):
    b = f' border="1.5 SOLID {border}"' if border else ""
    sh = f' boxShadow="{shadow}"' if shadow else ""
    return (f'<Positioned left="{round(x, 2)}" top="{round(y, 2)}" '
            f'width="{round(w, 2)}" height="{round(h, 2)}">'
            f'<Container width="{round(w, 2)}" height="{round(h, 2)}" '
            f'color="{color}" borderRadius="{radius}"{b}{sh}/></Positioned>')


def outline(x, y, w, h, color, t=2.0, radius=0):
    return (f'<Positioned left="{round(x - t, 2)}" top="{round(y - t, 2)}" '
            f'width="{round(w + 2 * t, 2)}" height="{round(h + 2 * t, 2)}">'
            f'<Container width="{round(w + 2 * t, 2)}" height="{round(h + 2 * t, 2)}" '
            f'color="#FFFFFF00" border="{t} SOLID {color}" borderRadius="{radius}"/></Positioned>')


def q(s: str) -> str:
    """把字面量直接放进属性值的引号之间。

    本服务的解析器不解码 XML 实体（见 A11 实测），所以这里**不能**做 XML 转义；
    `text` 属性以双引号界定，故只断言字符串不含双引号。
    """
    assert '"' not in s, f"text 属性无法承载双引号：{s!r}"
    return '"' + s + '"'


def txt(boxes, canvas, field, path, text, *, x, y, w, h, size, family, color,
        align=None, role="body"):
    assert '"' not in text, f"text 属性无法承载双引号：{text!r}"
    at = (f' fontSize="{size}" color="{color}" fontFamily="{family}"'
          + (f' textAlign="{align}"' if align else ""))
    node = f"<Text{at} text={q(text)}/>"
    boxes.append({
        "canvas": canvas, "field": field, "field_path": path, "role": role,
        "source_text": text, "displayed_text": text, "complete": True,
        "box_px": [round(x, 2), round(y, 2), round(w, 2), round(h, 2)],
        "x": round(x, 2), "y": round(y, 2), "width": round(w, 2), "height": round(h, 2),
        "font_size": size, "font_family": family, "color": color,
        "text_align": align or "START", "size_unit": "px", "path_base": "canvas_px",
        "wrapping": "允许自动折行；未使用省略号、缩写、改写或删句",
    })
    return (f'<Positioned left="{round(x, 2)}" top="{round(y, 2)}" '
            f'width="{round(w, 2)}" height="{round(h, 2)}">{node}</Positioned>')


def circle(x, y, d, color):
    return (f'<Positioned left="{round(x, 2)}" top="{round(y, 2)}" '
            f'width="{round(d, 2)}" height="{round(d, 2)}">'
            f'<ClipOval><Container width="{round(d, 2)}" height="{round(d, 2)}" '
            f'color="{color}"/></ClipOval></Positioned>')


def dot(x, y, d, color):
    return (f'<Positioned left="{round(x, 2)}" top="{round(y, 2)}" '
            f'width="{round(d, 2)}" height="{round(d, 2)}">'
            f'<ClipRRect borderRadius="{round(d / 2, 2)}">'
            f'<Container width="{round(d, 2)}" height="{round(d, 2)}" color="{color}"/>'
            f'</ClipRRect></Positioned>')


def seg(x1, y1, x2, y2, t, color):
    import math
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy)
    if L < 0.01:
        return ""
    ang = math.degrees(math.atan2(dy, dx))
    cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
    bw = L + t
    return (f'<Positioned left="{round(cx - bw / 2, 2)}" top="{round(cy - t / 2, 2)}" '
            f'width="{round(bw, 2)}" height="{t}">'
            f'<Transform matrix="{sk.rot_matrix(ang)}" alignment="CENTER">'
            f'<Container width="{round(bw, 2)}" height="{t}" color="{color}" '
            f'borderRadius="{round(t / 2, 2)}"/></Transform></Positioned>')


def deco(cx, cy, s):
    """Hero 几何组合：描边方块 + 实心圆 + 两根圆角横条（四个断点同一构件，仅缩放/重排）。"""
    out = [outline(cx - s, cy - s, 2 * s, 2 * s, C["hero_deco_line"], max(2.0, s * 0.07), 18)]
    out.append(circle(cx + s * 0.34, cy - s * 0.72, s * 0.62, C["brand_soft"]))
    out.append(seg(cx - s * 1.15, cy + s * 0.55, cx + s * 0.15, cy + s * 0.55,
                   max(5.0, s * 0.16), C["brand"]))
    out.append(seg(cx - s * 1.15, cy + s * 0.95, cx - s * 0.25, cy + s * 0.95,
                   max(5.0, s * 0.16), C["accent"]))
    return "".join(out)


# ------------------------------------------------------------------ 单画布构建
def build(bp: dict, c: dict) -> tuple[str, list]:
    k, W, H = bp["key"], bp["w"], bp["h"]
    M = TOKENS["spacing"]["margin"][k]
    U = TOKENS["spacing"]["unit"][k]
    GAP = TOKENS["spacing"]["card_gap"][k]
    PAD = TOKENS["spacing"]["card_pad"][k]
    TS = TOKENS["type_scale"]
    CW = W - 2 * M
    P, boxes = [], []
    A = P.append

    A(rect(0, 0, W, H, C["canvas"]))
    # 顶部品牌色带（四个断点同一构件）
    A(rect(0, 0, W, max(5, round(H * 0.006)), C["brand"]))

    y = M + 6

    # ---------- 顶栏条
    th = bp["top_h"]
    bar_h = TS["badge"][k] + 12
    A(rect(M, y + (th - bar_h) / 2, 6, bar_h, C["brand"], R["card_bar"]))
    A(txt(boxes, k, "brand", "brand", "云构 · Structure",
          x=M + 16, y=y + (th - TS["badge"][k] - 4) / 2, w=240, h=TS["badge"][k] + 8,
          size=TS["badge"][k], family=F_MIX_HEAD, color=C["ink"], role="chrome"))
    A(txt(boxes, k, "breakpoint_label", "breakpoint_label", f"{bp['label']} · {W}×{H}",
          x=W - M - 260, y=y + (th - TS["badge"][k] - 4) / 2, w=260, h=TS["badge"][k] + 8,
          size=TS["badge"][k], family=F_MIX, color=C["faint"], align="RIGHT", role="chrome"))
    A(seg(M, y + th + U // 2, W - M, y + th + U // 2, 1.4, C["line"]))
    y += th + U

    # ---------- Hero：主标题 + 副标题 + 几何组合
    ds = TS["display"][k]
    deco_s = bp["deco_s"]
    deco_w = deco_s * 2.4
    text_w = CW - deco_w - U
    tl = sk.est_lines(c["title"], text_w, ds)
    th_line = int(ds * 1.18)
    th_box = tl * th_line
    A(txt(boxes, k, "title", "title", c["title"],
          x=M, y=y, w=text_w, h=th_box, size=ds, family=F_MIX_HEAD, color=C["ink"],
          role="display"))
    A(deco(M + CW - deco_s, y + th_box / 2, deco_s))
    y += th_box + U // 2

    ss = TS["subtitle"][k]
    sl_ = sk.est_lines(c["subtitle"], CW, ss)
    sh = sl_ * int(ss * 1.45)
    A(txt(boxes, k, "subtitle", "subtitle", c["subtitle"],
          x=M, y=y, w=CW, h=sh, size=ss, family=F_MIX, color=C["ink_2"]))
    y += sh + U

    # ---------- meta 行（date / time / location / website）
    # 每个字段声明占几列：窄屏时地点与官网各占满整行，避免数值被裁
    mc = bp["meta_cols"]
    mlab, mval = TS["meta_label"][k], TS["meta_value"][k]
    labels = {"date": "日期 DATE", "time": "时间 TIME",
              "location": "地点 LOCATION", "website": "官网 WEBSITE"}
    values = {"date": c["date"], "time": c["time"],
              "location": c["location"], "website": c["website"]}
    span_map = bp["meta_span"]
    unit_w = (CW - (mc - 1) * U) // mc
    mh = mlab + mval + 14
    cursor, row_top = 0, y
    for f, sp in zip(["date", "time", "location", "website"], span_map):
        w = unit_w * sp + U * (sp - 1)
        x = M + cursor * (unit_w + U)
        A(rect(x, row_top, w, mh, C["paper"], R["chip"], C["line"]))
        A(rect(x, row_top, 4, mh, C["accent"], R["card_bar"]))
        A(txt(boxes, k, f, f, labels[f],
              x=x + 14, y=row_top + 6, w=w - 24, h=mlab + 4, size=mlab,
              family=F_MIX, color=C["faint"], role="meta_label"))
        A(txt(boxes, k, f, f, values[f],
              x=x + 14, y=row_top + 8 + mlab, w=w - 24, h=mval + 8, size=mval,
              family=F_MIX_HEAD, color=C["ink"], role="meta_value"))
        cursor += sp
        if cursor >= mc:
            cursor = 0
            y += mh + U // 2
            row_top = y
    y += U // 2

    # ---------- CTA
    ch = bp["cta_h"]
    cs = TS["cta"][k]
    A(rect(M, y, CW, ch, C["brand"], R["cta"], None, TOKENS["shadow"]["cta"]))
    A(dot(M + U + 2, y + ch / 2 - 6, 12, C["cta_text"]))
    A(txt(boxes, k, "cta", "cta", c["cta"],
          x=M + U + 24, y=y, w=CW - 2 * (U + 24), h=ch, size=cs,
          family=F_MIX_HEAD, color=C["cta_text"], role="cta"))
    y += ch + U

    # ---------- 小节标题
    sec_s = TS["section"][k]
    A(txt(boxes, k, "section_cards", "section_cards", "六项能力 · SIX CAPABILITIES",
          x=M, y=y, w=CW, h=sec_s + 6, size=sec_s, family=F_MIX_HEAD, color=C["brand"],
          role="section"))
    y += sec_s + 8

    # ---------- 六张卡（同一构件；手机把编号徽章与卡标题并排以省出纵向空间）
    cols = bp["cols"]
    GAP = bp["card_gap"]
    PAD = bp["card_pad"]
    card_w = (CW - (cols - 1) * GAP) // cols
    card_h = bp["card_h"]
    ct, cd = TS["card_title"][k], TS["card_detail"][k]
    bw, bh = bp["badge"]
    inner_w = card_w - PAD * 2 - 12
    for i, card in enumerate(c["cards"]):
        r, cidx = divmod(i, cols)
        cx = M + cidx * (card_w + GAP)
        cy = y + r * (card_h + GAP)
        A(rect(cx, cy, card_w, card_h, C["paper"], R["card"], C["line_strong"],
               TOKENS["shadow"]["card"]))
        A(rect(cx, cy, 6, card_h, C["brand"], R["card_bar"]))
        bx, by = cx + PAD + 6, cy + PAD
        if bp["card_variant"] == "inline":
            # 编号徽章与卡标题同一行
            A(rect(bx, by, bw, bh, C["brand_tint"], R["badge"]))
            A(txt(boxes, k, f"card[{i}].id", f"cards[{i}].id", card["id"],
                  x=bx, y=by, w=bw, h=bh, size=TS["badge"][k], family=F_HEAD,
                  color=C["brand"], align="CENTER", role="card_id"))
            ty = by - 3
            A(txt(boxes, k, f"card[{i}].title", f"cards[{i}].title", card["title"],
                  x=bx + bw + bp["gap_title"], y=ty, w=inner_w - bw - bp["gap_title"], h=ct + 5,
                  size=ct, family=F_MIX_HEAD, color=C["ink"], role="card_title"))
            A(txt(boxes, k, f"card[{i}].detail", f"cards[{i}].detail", card["detail"],
                  x=bx, y=by + bh + bp["gap_detail"], w=inner_w, h=cd + 5,
                  size=cd, family=F_MIX, color=C["ink_2"], role="card_detail"))
        else:
            # 编号徽章 / 卡标题 / detail 纵向堆叠
            A(rect(bx, by, bw, bh, C["brand_tint"], R["badge"]))
            A(txt(boxes, k, f"card[{i}].id", f"cards[{i}].id", card["id"],
                  x=bx, y=by, w=bw, h=bh, size=TS["badge"][k], family=F_HEAD,
                  color=C["brand"], align="CENTER", role="card_id"))
            A(txt(boxes, k, f"card[{i}].title", f"cards[{i}].title", card["title"],
                  x=bx, y=by + bh + bp["gap_title"], w=inner_w, h=ct + 10,
                  size=ct, family=F_MIX_HEAD, color=C["ink"], role="card_title"))
            A(txt(boxes, k, f"card[{i}].detail", f"cards[{i}].detail", card["detail"],
                  x=bx, y=by + bh + bp["gap_title"] + ct + 14, w=inner_w, h=cd + 30,
                  size=cd, family=F_MIX, color=C["ink_2"], role="card_detail"))
    y += bp["card_rows"] * card_h + (bp["card_rows"] - 1) * GAP

    # ---------- 页脚
    # 窄屏横向空间不足：官网已在上方 meta 芯片完整显示，页脚不再重复，只留一行说明
    fy = H - M - (TS["footer"][k] + 10)
    A(seg(M, fy - U, W - M, fy - U, 1.4, C["line"]))
    if bp["footer_web"]:
        lw = int(CW * 0.58)
        A(txt(boxes, k, "footer.canvas", "footer.canvas",
              f"{bp['label']} {W}×{H} · 6 张卡全部完整显示",
              x=M, y=fy, w=lw - 8, h=TS["footer"][k] + 6, size=TS["footer"][k],
              family=F_MIX, color=C["faint"], role="footer"))
        A(txt(boxes, k, "footer.id", "footer.id", c["website"],
              x=M + lw, y=fy, w=CW - lw, h=TS["footer"][k] + 6, size=TS["footer"][k],
              family=F_MIX, color=C["faint"], align="RIGHT", role="footer"))
    else:
        A(txt(boxes, k, "footer.canvas", "footer.canvas",
              f"{W}×{H} · 6 张卡全部完整显示",
              x=M, y=fy, w=CW, h=TS["footer"][k] + 6, size=TS["footer"][k],
              family=F_MIX, color=C["faint"], role="footer"))

    dsl = (f'<Snapshot type="png">\n<Container width="{W}" height="{H}" color="{C["canvas"]}">'
           f'<Stack fit="EXPAND">{"".join(P)}</Stack></Container>\n</Snapshot>\n')
    return dsl, boxes


# ------------------------------------------------------------------ 审计
def build_tokens_audit(boxes_by_canvas, c):
    fields = ["title", "subtitle", "date", "time", "location", "cta", "website"]
    per_canvas = []
    for bp in BREAKPOINTS:
        k = bp["key"]
        bs = boxes_by_canvas[k]
        rows = []
        for f in fields:
            hit = [b for b in bs if b["field"] == f and b["role"] == "meta_value"] \
                or [b for b in bs if b["field"] == f]
            rows.append({
                "field": f, "field_path": f, "role": hit[0]["role"] if hit else "",
                "source_text": c[f] if f in c else "",
                "displayed_text": hit[0]["displayed_text"] if hit else "",
                "box_px": hit[0]["box_px"] if hit else None,
                "font_size_px": hit[0]["font_size"] if hit else None,
                "font_family": hit[0]["font_family"] if hit else None,
                "complete": bool(hit) and hit[0]["complete"],
                "present_in_canvas": bool(hit),
            })
        for i, card in enumerate(c["cards"]):
            for part in ("title", "detail", "id"):
                hit = [b for b in bs if b["field"] == f"card[{i}].{part}"]
                rows.append({
                    "field": f"card[{i}].{part}",
                    "field_path": f"cards[{i}].{part}",
                    "role": hit[0]["role"] if hit else "",
                    "card_id": card["id"],
                    "source_text": card[part],
                    "displayed_text": hit[0]["displayed_text"] if hit else "",
                    "box_px": hit[0]["box_px"] if hit else None,
                    "font_size_px": hit[0]["font_size"] if hit else None,
                    "font_family": hit[0]["font_family"] if hit else None,
                    "complete": bool(hit) and hit[0]["complete"],
                    "present_in_canvas": bool(hit),
                    "required": part in ("title", "detail"),
                    "note": "id 仅用于稳定追踪卡片身份，允许印在图上，不是「一字不丢」的必显文案"
                            if part == "id" else "必显文案，原文完整显示",
                })
        per_canvas.append({
            "canvas": k, "label": bp["label"], "size_px": [bp["w"], bp["h"]],
            "png": f"{k}.png", "dsl": f"{k}.snapshot",
            "card_columns": bp["cols"], "card_rows": bp["card_rows"],
            "meta_columns": bp["meta_cols"],
            "safe_margin_px": TOKENS["spacing"]["margin"][k],
            "required_fields": rows,
            "required_total": len([r for r in rows if r.get("required", True)]),
            "required_complete": len([r for r in rows if r.get("required", True)
                                      and r["complete"]]),
            "all_required_complete": all(r["complete"] for r in rows if r.get("required", True)),
            "min_body_px": min(r["font_size_px"] for r in rows
                               if r["font_size_px"] and r["role"] in
                               ("body", "meta_value", "card_detail", "cta", "display")),
            "min_card_title_px": min(r["font_size_px"] for r in rows
                                     if r["font_size_px"] and r["field"].endswith(".title")
                                     and r["field"].startswith("card[")),
        })
    return per_canvas


def main() -> None:
    ver = sys.argv[1] if len(sys.argv) > 1 else "v1"
    base = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
    c = json.loads((base / CONTENT_IN).read_text(encoding="utf-8"))
    d = base / DRAFTS
    d.mkdir(parents=True, exist_ok=True)

    boxes_by_canvas = {}
    for bp in BREAKPOINTS:
        dsl, boxes = build(bp, c)
        (d / f"a12-{bp['key']}-{ver}.snapshot").write_text(dsl, encoding="utf-8")
        boxes_by_canvas[bp["key"]] = boxes
        req = [b for b in boxes if not b["field"].startswith(("brand", "breakpoint", "section",
                                                              "footer", "card[0].id"))
               or b["field"].endswith((".title", ".detail"))]
        print(f"{bp['key']:8s} {bp['w']}x{bp['h']}  bytes={len(dsl.encode()):6d} "
              f"segments={len(boxes):3d}  boxes_bottom={max(b['y'] + b['height'] for b in boxes):.0f} "
              f"(limit {bp['h'] - TOKENS['spacing']['margin'][bp['key']]})")

    tok = dict(TOKENS)
    tok.update({
        "schema_version": 1, "task_id": TASK, "path_base": "output_dir", "round": "round-01",
        "title": "四断点完整内容视觉系统",
        "source": {"content": "inputs/content.json", "modified": False},
        "breakpoints": [{"key": b["key"], "label": b["label"], "size_px": [b["w"], b["h"]],
                         "card_columns": b["cols"], "card_rows": b["card_rows"],
                         "meta_columns": b["meta_cols"],
                         "safe_margin_px": TOKENS["spacing"]["margin"][b["key"]]}
                        for b in BREAKPOINTS],
        "font_families": {"latin": F_LATIN, "latin_head": F_HEAD, "latin_num": F_NUM,
                          "cjk_sc": F_SC, "mixed": F_MIX,
                          "source": "run 级 GET /fonts 实际返回的 27 个字体族"},
        "outputs": [{"kind": "png", "filename": f"{b['key']}.png",
                     "dsl": f"{b['key']}.snapshot", "width": b["w"], "height": b["h"]}
                    for b in BREAKPOINTS]
                    + [{"kind": "json", "filename": "design-tokens.json"},
                       {"kind": "json", "filename": "content-map.json"}],
    })
    (d / "design-tokens-raw.json").write_text(json.dumps(tok, ensure_ascii=False, indent=2),
                                              encoding="utf-8")

    cmap = {
        "schema_version": 1, "task_id": TASK, "path_base": "output_dir", "round": "round-01",
        "title": "必显字段逐画布映射",
        "coordinate_base": {"unit": "px", "origin": "各画布左上角外边界",
                            "x_direction": "right", "y_direction": "down",
                            "box_format": "[x, y, width, height]"},
        "source": {"content": "inputs/content.json", "modified": False},
        "card_identity": [{"index": i + 1, "id": card["id"],
                           "field_paths": [f"cards[{i}].title", f"cards[{i}].detail",
                                           f"cards[{i}].id"]}
                          for i, card in enumerate(c["cards"])],
        "rule": ("四种尺寸均须完整显示 title、subtitle、date、time、location、cta、website "
                 "以及六张卡的 title 与 detail；允许自动折行或增加不改变词语的换行，"
                 "保留原文字词、数字、大小写、标点及有意义的空格；"
                 "不使用省略号、缩写、改写或删句；cards[].id 仅用于稳定追踪身份，"
                 "允许印在图上但不作为必显文案判定依据"),
        "canvases": build_tokens_audit(boxes_by_canvas, c),
        "omitted_text": None,
        "qr_code": {"generated": False, "reason": "CTA 为文字，不需要生成二维码"},
        "adaptation_method": "从同一份内容与设计参数分别生成四份完整 DSL；未使用裁切、拉伸或整图 <Image>",
    }
    (d / "content-map-raw.json").write_text(json.dumps(cmap, ensure_ascii=False, indent=2),
                                            encoding="utf-8")
    ok = all(cv["all_required_complete"] for cv in cmap["canvases"])
    print("all required fields complete on every canvas:", ok)
    for cv in cmap["canvases"]:
        print(f"  {cv['canvas']:8s} required {cv['required_complete']}/{cv['required_total']} "
              f"min_body={cv['min_body_px']} min_card_title={cv['min_card_title_px']}")


if __name__ == "__main__":
    main()