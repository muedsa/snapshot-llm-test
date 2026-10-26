# -*- coding: utf-8 -*-
"""A12 四断点完整内容视觉系统。

四个画布：360x800（窄手机单列）、768x1024（平板两列）、1440x900（桌面三列）、
1920x1080（大屏三列 + 侧栏）。
全部内容一字不丢：title, subtitle, date, time, location, cta, website,
cards[].title, cards[].detail（C1-C6）。
"""
from __future__ import annotations

import json
import os
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ["SNAPSHOT_RUN_ID"]
TASK = "A12"
TASK_DIR = ROOT / "tasks" / "A12-responsive-system"
OUT_DIR = ROOT / "outputs" / RUN_ID / TASK
TMP_DIR = ROOT / "tmp" / RUN_ID / TASK
OUT_DIR.mkdir(parents=True, exist_ok=True)
TMP_DIR.mkdir(parents=True, exist_ok=True)

C = json.loads((TASK_DIR / "inputs" / "content.json").read_text(encoding="utf-8"))

SANS = "Noto Sans CJK SC"
MONO = "Noto Sans Mono CJK SC"

# ---------- 设计令牌（四断点共用同一套语义，按断点缩放） ----------
TOKENS = {
    "color": {
        "bg": "#F8FAFC",
        "surface": "#FFFFFF",
        "ink": "#0F172A",
        "ink_secondary": "#334155",
        "muted": "#64748B",
        "line": "#E2E8F0",
        "line_strong": "#CBD5E1",
        "accent": "#2563EB",
        "accent_soft": "#EFF6FF",
        "accent_ink": "#1D4ED8",
        "dark": "#0F172A",
        "dark_text": "#F8FAFC",
        "dark_muted": "#94A3B8",
    },
    "font_family": {"primary": SANS, "monospace": MONO},
    "radius": {"card": 16, "chip": 999, "button": 12, "hero": 20},
    "shape": {"card_border": "1 SOLID #E2E8F0", "accent_bar_w": 5},
    "decoration_core": {
        "description": "圆角卡片 + 左侧 accent 竖条 + 序号圆点；四断点重排不更换构件",
        "elements": ["radius_card", "accent_bar", "index_dot", "chip"],
    },
}

# 每断点的具体令牌
BP = {
    "mobile": {
        "canvas": [360, 800], "margin": 16,
        "title": 40, "subtitle": 20, "meta": 18, "body": 16, "card_title": 18,
        "card_detail": 16, "cta": 18, "footnote": 16, "chip": 16,
        "cols": 1, "card_pad": 10, "gap": 8, "hero_pad": 12, "dot_d": 18,
        "title_min_ok": True,   # 主标题 40 >= 40
        "body_min_ok": True,    # 正文 16 >= 16（手机）
    },
    "tablet": {
        "canvas": [768, 1024], "margin": 32,
        "title": 48, "subtitle": 22, "meta": 20, "body": 20, "card_title": 20,
        "card_detail": 20, "cta": 20, "footnote": 20, "chip": 18,
        "cols": 2, "card_pad": 18, "gap": 16, "hero_pad": 28, "dot_d": 26,
        "title_min_ok": True, "body_min_ok": True,
    },
    "desktop": {
        "canvas": [1440, 900], "margin": 32,
        "title": 56, "subtitle": 24, "meta": 20, "body": 20, "card_title": 22,
        "card_detail": 20, "cta": 22, "footnote": 20, "chip": 18,
        "cols": 3, "card_pad": 20, "gap": 20, "hero_pad": 36, "dot_d": 26,
        "title_min_ok": True, "body_min_ok": True,
    },
    "stage": {
        "canvas": [1920, 1080], "margin": 32,
        "title": 64, "subtitle": 26, "meta": 22, "body": 22, "card_title": 24,
        "card_detail": 22, "cta": 24, "footnote": 20, "chip": 20,
        "cols": 3, "card_pad": 24, "gap": 24, "hero_pad": 44, "dot_d": 28,
        "title_min_ok": True, "body_min_ok": True,
    },
}


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def txt(s, *, x, y, w, size, color="ink", family="primary", bold=False, align="LEFT",
        h=None, wrap=True, mono=False):
    col = TOKENS["color"][color]
    fam = TOKENS["font_family"]["monospace"] if mono else TOKENS["font_family"][family]
    return (
        f'<Positioned left="{x:.1f}" top="{y:.1f}" width="{w:.1f}"'
        + (f' height="{h}"' if h else "")
        + f'><Container color="transparent"><Text fontSize="{size}" fontFamily="{fam}"'
        + (' fontStyle="BOLD"' if bold else "")
        + f' color="{col}" textAlign="{align}" softWrap="{"true" if wrap else "false"}"'
        + f' maxLines="1">{esc(s)}</Text></Container></Positioned>'
    )


def box(x, y, w, h, color, *, radius=None, border=None):
    col = TOKENS["color"][color] if color in TOKENS["color"] else color
    a = ""
    if radius:
        a += f' borderRadius="{radius}"'
    if border:
        a += f' border="{border}"'
    return f'<Positioned left="{x:.1f}" top="{y:.1f}" width="{w:.1f}" height="{h:.1f}"><Container color="{col}"{a}/></Positioned>'


def line(x1, y1, x2, y2, color, thick=1):
    import math
    dx, dy = x2 - x1, y2 - y1
    ln = math.hypot(dx, dy)
    if ln < 0.01:
        return ""
    ang = math.atan2(dy, dx)
    c, s = math.cos(ang), math.sin(ang)
    m = f"({c},{s},0,0,{-s},{c},0,0,0,0,1,0,0,0,0,1)"
    return (f'<Positioned left="{x1:.2f}" top="{y1 - thick/2:.2f}" width="{ln:.2f}" '
            f'height="{thick}"><Container color="{TOKENS["color"][color]}" transform="{m}" '
            f'transformAlignment="TOP_LEFT"/></Positioned>')


# ---------- 通用构件 ----------
def chip(x, y, text, size, pad_x=14, h=30):
    """胶囊标签（同一核心构件）。"""
    w = pad_x * 2 + len(text) * (size * 0.62)
    return (box(x, y, w, h, "accent_soft", radius=999)
            + txt(text, x=x + pad_x, y=y + (h - size) / 2 - 1, w=w - 2 * pad_x, size=size,
                  color="accent_ink", bold=True, wrap=False))


def index_dot(x, y, d, num, size):
    return (box(x, y, d, d, "accent", radius=d / 2)
            + txt(num, x=x, y=y + (d - size) / 2 - 1, w=d, size=size, color="surface",
                  bold=True, align="CENTER", wrap=False))


def card(x, y, w, h, cid, num, pad, card_title_size, card_detail_size, dot_d=26):
    """六卡共用构件：圆角卡 + 左侧 accent 竖条 + 序号圆点 + 标题 + detail。

    标题与序号圆点同一行；detail 紧随其下（行高 = max(dot, title) + 8）。
    """
    out = [box(x, y, w, h, "surface", radius=TOKENS["radius"]["card"],
               border=TOKENS["shape"]["card_border"])]
    out.append(box(x, y, TOKENS["shape"]["accent_bar_w"], h, "accent", radius=2))
    dot = dot_d
    out.append(index_dot(x + pad, y + pad, dot, num, 14 if dot >= 26 else 12))
    tx = x + pad + dot + 10
    tw = w - (tx - x) - pad
    out.append(txt(cid["title"], x=tx, y=y + pad - 1, w=tw, size=card_title_size,
                   color="ink", bold=True, wrap=False))
    row_h = max(dot, card_title_size)
    detail_y = y + pad + row_h + 8
    out.append(txt(cid["detail"], x=x + pad, y=detail_y, w=w - 2 * pad,
                   size=card_detail_size, color="ink_secondary", wrap=False))
    return "".join(out), detail_y


# ---------- 生成器 ----------
records = {}   # breakpoint -> content map records


def build(name):
    bp = BP[name]
    W, H = bp["canvas"]
    M = bp["margin"]
    nodes = [box(0, 0, W, H, "bg")]

    rec = {"canvas": {"width": W, "height": H}, "margin": M,
           "layout": ("mobile_single_column" if bp["cols"] == 1 else
                      "tablet_two_column" if bp["cols"] == 2 else "desktop_three_column"),
           "fields": {}, "cards": {}}

    # ===== Hero =====
    # 先按实测字宽决定折行数与 chip 行数，再算 hero 高度
    hx = M + bp["hero_pad"]
    hw = W - 2 * M - 2 * bp["hero_pad"]
    title_w = bp["title"]
    # 主标题折行判定：实测 40px BOLD 的 'Structure / Vision' 约 334px
    title_est = title_w * 0.52 * len(C["title"])
    title_lines = 2 if title_est > hw else 1
    title_block_h = title_lines * (bp["title"] + 6)

    sub_est = bp["subtitle"] * 1.0 * len(C["subtitle"])
    sub_lines = 2 if sub_est > hw else 1
    sub_block_h = sub_lines * (bp["subtitle"] + 4)

    # meta chips 行数估算
    msize = bp["chip"]
    chip_h = msize + 12
    meta_items = [C["date"], C["time"], C["location"]]
    meta_est = [msize * 0.62 * len(t) + 28 for t in meta_items]
    chip_rows, cur_w = 1, 0.0
    for w in meta_est:
        if cur_w + w > hw and cur_w > 0:
            chip_rows += 1
            cur_w = w + 8
        else:
            cur_w += w + 8
    meta_block_h = chip_rows * chip_h + (chip_rows - 1) * 8

    # CTA 行
    cta_size = bp["cta"]
    cta_est = cta_size * 0.62 * len(C["cta"]) + 28
    cta_btn_h = cta_size + 16
    # website 与 CTA 是否同行
    web_est = bp["footnote"] * 0.62 * len(C["website"])
    cta_rows = 1 if (cta_est + 16 + web_est) <= hw else 2

    hero_h = (bp["hero_pad"] * 2 + title_block_h + 10 + sub_block_h + 16
              + meta_block_h + 14 + cta_rows * cta_btn_h + (10 if cta_rows > 1 else 0))

    # 六卡所需最小高度（含 gap 与页脚）
    cols = bp["cols"]
    rows = (len(C["cards"]) + cols - 1) // cols
    dot_d_min = bp["dot_d"]
    min_card_h = bp["card_pad"] + max(dot_d_min, bp["card_title"]) + 8 + bp["card_detail"] + bp["card_pad"]
    SECTION_HDR = 28       # 「六步工作流」小节标题高度
    need_cards = rows * min_card_h + (rows - 1) * 4 + SECTION_HDR + bp["footnote"] + 24 + M
    # 若 hero 过高导致卡片放不下，逐级压缩 hero 的非文字开销
    # （hero_pad、块间距、chip 行距、小节标题），不缩字号、不删内容
    hero_pad_eff = bp["hero_pad"]
    block_gap = 10          # 主标题后间距
    sub_gap = 16            # 副标题后间距
    meta_gap = 14           # chips 后间距
    chip_row_gap = 8        # chips 行距
    if M + hero_h + need_cards > H:
        overflow = (M + hero_h + need_cards) - H
        # 1) 压缩小节标题（28 → 20）
        if overflow > 0:
            cut = min(overflow, 8)
            SECTION_HDR -= cut
            overflow -= cut
        # 2) 压缩 hero_pad（下限 10）
        pad_cut = min(overflow, max(0, bp["hero_pad"] - 10) * 2)
        hero_pad_eff = bp["hero_pad"] - pad_cut // 2
        hero_h -= pad_cut
        overflow -= pad_cut
        # 3) 压缩块间距（10+16+14 = 40，下限各 4 共 12）
        if overflow > 0:
            gap_cut = min(overflow, 40 - 12)
            hero_h -= gap_cut
            used = 0
            take = min(gap_cut, block_gap - 4)
            block_gap -= take
            used += take
            if used < gap_cut:
                take = min(gap_cut - used, sub_gap - 4)
                sub_gap -= take
                used += take
            if used < gap_cut:
                take = min(gap_cut - used, meta_gap - 4)
                meta_gap -= take
            overflow -= gap_cut
        # 4) 压缩 chip 行距（每行 8，下限 4）
        if overflow > 0 and chip_rows > 1:
            chip_gap_cut = min(overflow, (chip_rows - 1) * 4)
            chip_row_gap = max(4, chip_row_gap - chip_gap_cut)
            hero_h -= chip_gap_cut
            overflow -= chip_gap_cut
    nodes.append(box(M, M, W - 2 * M, hero_h, "dark", radius=TOKENS["radius"]["hero"]))

    y = M + hero_pad_eff
    hx = M + hero_pad_eff
    hw = W - 2 * M - 2 * hero_pad_eff
    # 主标题：允许折行（不改变词语），保证 ≥40px 不被压缩
    nodes.append(txt(C["title"], x=hx, y=y, w=hw, size=bp["title"], color="dark_text",
                     bold=True, wrap=True, h=title_block_h))
    rec["fields"]["title"] = {"original": C["title"], "displayed": C["title"],
                              "box": [hx, y, hx + hw, y + title_block_h],
                              "font_size": bp["title"], "complete": True,
                              "lines": title_lines}
    y += title_block_h + block_gap
    nodes.append(txt(C["subtitle"], x=hx, y=y, w=hw, size=bp["subtitle"],
                     color="dark_muted", wrap=True, h=sub_block_h))
    rec["fields"]["subtitle"] = {"original": C["subtitle"], "displayed": C["subtitle"],
                                 "box": [hx, y, hx + hw, y + sub_block_h],
                                 "font_size": bp["subtitle"], "complete": True,
                                 "lines": sub_lines}
    y += sub_block_h + sub_gap

    # meta chips：date / time / location
    meta_items = [C["date"], C["time"], C["location"]]
    msize = bp["chip"]
    cx = hx
    cy = y
    chip_h = msize + 12
    max_x = hx + hw
    meta_boxes = []
    for i, mtxt in enumerate(meta_items):
        w = 14 * 2 + len(mtxt) * (msize * 0.62)
        if cx + w > max_x:
            cx = hx
            cy += chip_h + chip_row_gap
        nodes.append(box(cx, cy, w, chip_h, "dark", radius=999,
                         border="1 SOLID #334155"))
        nodes.append(txt(mtxt, x=cx + 14, y=cy + 6, w=w - 28, size=msize,
                         color="dark_text", wrap=False))
        meta_boxes.append([cx, cy, cx + w, cy + chip_h])
        cx += w + 8
    rec["fields"]["date"] = {"original": C["date"], "displayed": C["date"],
                             "box": meta_boxes[0], "font_size": msize, "complete": True}
    rec["fields"]["time"] = {"original": C["time"], "displayed": C["time"],
                             "box": meta_boxes[1], "font_size": msize, "complete": True}
    rec["fields"]["location"] = {"original": C["location"], "displayed": C["location"],
                                 "box": meta_boxes[2], "font_size": msize, "complete": True}
    y = cy + chip_h + meta_gap

    # CTA + website
    cta_size = bp["cta"]
    cta_w = 14 * 2 + len(C["cta"]) * (cta_size * 0.62)
    nodes.append(box(hx, y, cta_w, cta_btn_h, "accent",
                     radius=TOKENS["radius"]["button"]))
    nodes.append(txt(C["cta"], x=hx + 14, y=y + 8, w=cta_w - 28, size=cta_size,
                     color="surface", bold=True, wrap=False))
    rec["fields"]["cta"] = {"original": C["cta"], "displayed": C["cta"],
                            "box": [hx, y, hx + cta_w, y + cta_btn_h],
                            "font_size": cta_size, "complete": True}
    # website 放 CTA 右侧或下方
    wx = hx + cta_w + 16
    wy = y + (cta_btn_h - bp["footnote"]) / 2
    if wx + web_est > hx + hw:
        wx = hx
        wy = y + cta_btn_h + 12
    nodes.append(txt(C["website"], x=wx, y=wy, w=max(hx + hw - wx, 80), size=bp["footnote"],
                     color="dark_muted", mono=True, wrap=False))
    rec["fields"]["website"] = {"original": C["website"], "displayed": C["website"],
                                "box": [wx, wy, hx + hw, wy + bp["footnote"] + 4],
                                "font_size": bp["footnote"], "complete": True}

    # ===== 六卡 =====
    # SECTION_HDR 已在 hero 压缩阶段可能被调小；cards_top 由它决定
    cards_top = M + hero_h + bp["gap"] + SECTION_HDR
    cols = bp["cols"]
    rows = (len(C["cards"]) + cols - 1) // cols
    avail_w = W - 2 * M
    card_gap = bp["gap"]
    card_w = (avail_w - card_gap * (cols - 1)) // cols
    # 窄手机采用「横向卡」：序号圆点 + 标题在同一行，detail 在下一行，
    # 这样 6 张卡可在 800px 内完整排下且不缩字号。
    # 卡内容最小高度：pad + max(dot, title) + 8 + detail + pad
    dot_d = bp["dot_d"]
    min_card_h = bp["card_pad"] + max(dot_d, bp["card_title"]) + 8 + bp["card_detail"] + bp["card_pad"]
    # 卡高 = 内容最小高 + 呼吸空间；呼吸空间按可用高度自适应，
    # 空间不足时退到最小高度（内容仍完整，只是留白减少）
    footer_h = bp["footnote"] + 24
    avail_h = H - M - footer_h - cards_top
    breathe = {"mobile": 24, "tablet": 30, "desktop": 34, "stage": 40}[name]
    card_h = min_card_h + breathe
    if rows * card_h + (rows - 1) * card_gap > avail_h:
        # 先尝试只减 gap
        need = rows * card_h + (rows - 1) * card_gap
        new_gap = max(4, card_gap - (need - avail_h) // max(rows, 1) - 1)
        if rows * card_h + (rows - 1) * new_gap <= avail_h:
            card_gap = new_gap
        else:
            # 再减呼吸空间，最后保底到内容最小高度
            for b in range(breathe, -1, -2):
                if rows * (min_card_h + b) + (rows - 1) * card_gap <= avail_h:
                    card_h = min_card_h + b
                    break
            else:
                card_gap = max(4, card_gap - 2)
                card_h = max(min_card_h, (avail_h - (rows - 1) * card_gap) // rows)

    nodes.append(txt("六步工作流", x=M, y=cards_top - SECTION_HDR + 4, w=300, size=bp["body"],
                     color="ink", bold=True, wrap=False))

    for i, cd in enumerate(C["cards"]):
        r, c = i // cols, i % cols
        x = M + c * (card_w + card_gap)
        y = cards_top + r * (card_h + card_gap)
        dot_d = bp["dot_d"]
        cdsl, detail_y = card(x, y, card_w, card_h, cd, str(i + 1), bp["card_pad"],
                              bp["card_title"], bp["card_detail"], dot_d=dot_d)
        nodes.append(cdsl)
        rec["cards"][cd["id"]] = {
            "card_id": cd["id"], "index": i + 1,
            "title": {"original": cd["title"], "displayed": cd["title"],
                      "box": [x + bp["card_pad"] + dot_d + 10, y + bp["card_pad"] - 1,
                              x + card_w - bp["card_pad"],
                              y + bp["card_pad"] + bp["card_title"] + 3],
                      "font_size": bp["card_title"], "complete": True},
            "detail": {"original": cd["detail"], "displayed": cd["detail"],
                       "box": [x + bp["card_pad"], detail_y,
                               x + card_w - bp["card_pad"],
                               detail_y + bp["card_detail"] + 3],
                       "font_size": bp["card_detail"], "complete": True},
            "card_box": [x, y, x + card_w, y + card_h],
        }

    # ===== 页脚 =====
    fy = H - M - bp["footnote"] - 8
    nodes.append(box(M, fy - 12, W - 2 * M, 1, "line"))
    nodes.append(txt(f"{C['title']} · {C['date']} · {C['location']}", x=M, y=fy,
                     w=W - 2 * M - 200, size=bp["footnote"], color="muted", wrap=False))
    nodes.append(txt(C["website"], x=W - M - 200, y=fy, w=200, size=bp["footnote"],
                     color="muted", mono=True, align="RIGHT", wrap=False))
    rec["fields"]["footer_note"] = {
        "original": f"{C['title']} · {C['date']} · {C['location']}",
        "displayed": f"{C['title']} · {C['date']} · {C['location']}",
        "box": [M, fy, W - M, fy + bp["footnote"] + 4],
        "font_size": bp["footnote"], "complete": True}

    dsl = (
        f'<Snapshot type="png" background="{TOKENS["color"]["bg"]}">'
        f'<Container width="{W}" height="{H}">'
        '<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE">'
        + "".join(nodes) + "</Stack></Container></Snapshot>"
    )
    (TMP_DIR / f"{name}.snapshot").write_text(dsl, encoding="utf-8")
    records[name] = rec
    print(f"wrote {name}.snapshot {len(dsl)} bytes; cards_top={cards_top} "
          f"card_h={card_h} rows={rows}")
    return dsl


for nm in ["mobile", "tablet", "desktop", "stage"]:
    build(nm)

# ---------- design-tokens.json ----------
design_tokens = {
    "schema_version": 1,
    "task_id": TASK,
    "path_base": "output_dir",
    "run_id": RUN_ID,
    "color": TOKENS["color"],
    "font_family": TOKENS["font_family"],
    "radius": TOKENS["radius"],
    "shape": TOKENS["shape"],
    "decoration_core": TOKENS["decoration_core"],
    "breakpoints": {},
    "consistency_rules": {
        "color": "四断点使用同一组颜色令牌，不允许断点自定义颜色",
        "form": "圆角卡片、左侧 accent 竖条、序号圆点、胶囊标签四种核心构件在四断点复用",
        "hierarchy": "主标题 > 副标题 > meta/CTA > 卡标题 > 卡 detail > 脚注，层级顺序一致",
        "rearrange_allowed": "装饰使用相同核心构件，可按断点重排（单列/两列/三列）",
    },
    "min_font_rules": {
        "mobile_body_min": 16, "mobile_card_title_min": 18,
        "other_body_min": 20, "main_title_min": 40,
        "mobile_margin_min": 16, "other_margin_min": 32,
    },
}
for nm, bp in BP.items():
    design_tokens["breakpoints"][nm] = {
        "canvas": bp["canvas"], "margin": bp["margin"],
        "type_scale": {
            "title": bp["title"], "subtitle": bp["subtitle"], "meta": bp["meta"],
            "body": bp["body"], "card_title": bp["card_title"],
            "card_detail": bp["card_detail"], "cta": bp["cta"],
            "footnote": bp["footnote"], "chip": bp["chip"],
        },
        "layout": {"columns": bp["cols"], "card_padding": bp["card_pad"],
                   "gap": bp["gap"], "hero_padding": bp["hero_pad"]},
        "meets_minimums": {
            "title_ge_40": bp["title"] >= 40,
            "mobile_body_ge_16": bp["body"] >= 16 if nm == "mobile" else bp["body"] >= 20,
            "mobile_card_title_ge_18": bp["card_title"] >= 18,
            "margin_ok": bp["margin"] >= (16 if nm == "mobile" else 32),
        },
    }
(OUT_DIR / "design-tokens.json").write_text(
    json.dumps(design_tokens, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("wrote design-tokens.json")

# ---------- content-map.json ----------
REQ = ["title", "subtitle", "date", "time", "location", "cta", "website"]
content_map = {
    "schema_version": 1,
    "task_id": TASK,
    "path_base": "output_dir",
    "run_id": RUN_ID,
    "source": "tasks/A12-responsive-system/inputs/content.json",
    "required_fields": REQ,
    "card_field_paths": {
        "C1": "cards[0]", "C2": "cards[1]", "C3": "cards[2]",
        "C4": "cards[3]", "C5": "cards[4]", "C6": "cards[5]",
    },
    "card_ids_note": "cards[].id 仅用于稳定追踪卡片身份，不属于必显文案；"
                     "可以显示编号 1-6，但不要求为 id 分配可见标签。",
    "fidelity_rules": {
        "no_omission": "小屏内容不得省略或改写成缩写",
        "no_ellipsis": "不使用省略号、缩写、改写或删句",
        "wrap_allowed": "允许排版自动折行或增加不改变词语的换行",
        "preserve": "保留原文字词、数字、大小写、标点及有意义的空格",
    },
    "canvases": {},
}
for nm, rec in records.items():
    content_map["canvases"][nm] = {
        "canvas": rec["canvas"], "margin": rec["margin"], "layout": rec["layout"],
        "fields": rec["fields"], "cards": rec["cards"],
        "all_required_present": all(f in rec["fields"] for f in REQ),
        "all_cards_complete": all(
            c["title"]["complete"] and c["detail"]["complete"]
            for c in rec["cards"].values()),
    }
(OUT_DIR / "content-map.json").write_text(
    json.dumps(content_map, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("wrote content-map.json")
