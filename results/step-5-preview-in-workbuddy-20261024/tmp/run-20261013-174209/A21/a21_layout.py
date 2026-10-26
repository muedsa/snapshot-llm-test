"""A21 构建：三轮 × 两尺寸的 DSL 生成、真实渲染与场景收集。"""
from __future__ import annotations
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "_suite"))

from a21_core import (EMBLEM, EMBLEM_BBOX, TOKENS, TYPO, TITLE_R1, TITLE_R2_LINES, SUBTITLE, DATE_TEXT,
                      SPEAKERS_TEXT, URL_TEXT, BADGE_TEXT, FREE_TEXT, SPONSORS_TEXT,
                      EN_TEXT, WORDMARK, CJK, LATIN, LATIN_BLACK, LATIN_SEMI,
                      alpha_hex, positioned, rect, circle, text_node, line_seg,
                      emblem_nodes, emblem_extent, content_entries, esc)

RUN_ID = "run-20261013-174209"


class Scene:
    def __init__(self, name, w, h, tok, no_text=False):
        self.name, self.w, self.h, self.tok = name, w, h, tok
        self.nodes = []
        self.texts = []
        self.cards = []
        self.no_text = no_text      # True 时不发射文字节点，仅记录（用于取真实背景）

    def node(self, n):
        if n:
            self.nodes.append(n)

    def text(self, tid, s, left, top, w, h, size, color, family=CJK,
             style="NORMAL", align="LEFT", bg="page", lines=1, role=""):
        if not self.no_text:
            self.node(text_node(s, left, top, w, h, size, color, align, style, family))
        self.texts.append({
            "id": tid, "text": s, "box": [round(left, 3), round(top, 3),
                                          round(left + w, 3), round(top + h, 3)],
            "font_size": size, "color": color, "font_family": family,
            "font_style": style, "lines": lines, "role": role,
            "background_source": bg,
            "background_color": self._bg_color(bg),
        })

    def _bg_color(self, bg):
        t = self.tok
        return {"page": t["page_bg"], "card": t["card_bg"],
                "pill": t["pill_bg"]}.get(bg, t["page_bg"])

    def dsl(self):
        return (f'<Snapshot type="png" background="{self.tok["page_bg"]}">'
                f'<Container width="{self.w}" height="{self.h}">'
                f'<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE">'
                + "\n".join(self.nodes) + "</Stack></Container></Snapshot>")


def header(sc, x, y, mark_s, wm_size, wm_top):
    """品牌锁定：小徽标 + 字标。徽标按真实包围盒定位，使其顶端正好落在 y。"""
    ew, eh = emblem_extent(mark_s)
    bo = EMBLEM_BBOX
    cx = x + ew / 2 - (bo["left"] + bo["right"]) / 2 * mark_s
    cy = y - bo["top"] * mark_s
    sc.node("\n".join(emblem_nodes(cx, cy, mark_s, sc.tok)))
    sc.text("wordmark", WORDMARK, x + ew + 18, wm_top, 460, wm_size * 1.5,
            wm_size, sc.tok["text_primary"], family=CJK, style="BOLD", bg="page")
    return y + eh


def divider(sc, x0, x1, y):
    sc.node(line_seg(x0, y, x1, y, 1.0, alpha_hex(sc.tok["divider"], 0.38)))


def pill(sc, tid, s, left, top, w, h, size, family=LATIN_SEMI):
    t = sc.tok
    sc.node(positioned(left, top, w, h,
                       rect(0, 0, w, h, t["pill_bg"], radius=h / 2,
                            border=f'1.5 SOLID {alpha_hex(t["pill_border"], 0.55)}')))
    sc.text(tid, s, left + 18, top + (h - size * 1.4) / 2, w - 36, size * 1.5,
            size, t["pill_text"], family=family, align="CENTER", bg="pill")


def meta_card(sc, left, top, w, h, rows, tok):
    """rows: [(tid, text, size, color, family, style)]"""
    sc.node(positioned(left, top, w, h,
                       rect(0, 0, w, h, tok["card_bg"], radius=20,
                            border=f'1 SOLID {tok["card_border"]}')))
    sc.cards.append([left, top, left + w, top + h])
    y = top + 20
    for tid, s, size, color, family, style in rows:
        sc.text(tid, s, left + 32, y, w - 64, size * 1.5, size, color,
                family=family, style=style, bg="card")
        y += size * 1.5 + 14


# ================================================================ 竖版 1080x1350
def build_portrait(rnd):
    tok = TOKENS[rnd]
    sc = Scene("launch-portrait", 1080, 1350, tok)
    t = tok
    M, CW = 80, 1080
    IW = CW - 2 * M                       # 920

    # 顶部扩展带 0..96（留空，不写待添加文字）
    header(sc, M, 133, 0.32, 30, 136)     # 徽标 130..177，字标 131..176
    divider(sc, M, CW - M, 214)

    # 徽标行（第2轮起右侧加“免费参加”pill）
    if rnd == 1:
        pill(sc, "badge", BADGE_TEXT, M, 240, 320, 58, 28)
    else:
        pill(sc, "badge", BADGE_TEXT, M, 240, 300, 58, 28)
        pill(sc, "free_entry", FREE_TEXT, M + 320, 240, 340, 58, 28)

    # 主标题
    if rnd == 1:
        lines, size, lh = [TITLE_R1], 88, 124
    else:
        lines, size, lh = TITLE_R2_LINES, 56, 78
    ty = 322
    for i, ln in enumerate(lines):
        sc.text("title", ln, M, ty + i * lh, IW, lh, size,
                t["text_primary"], style="BOLD", bg="page",
                lines=len(lines), role="main_title")
    y = ty + len(lines) * lh

    sc.text("subtitle", SUBTITLE, M, y + 24, IW, 44, 28, t["text_secondary"],
            bg="page")
    y += 24 + 44

    # 元信息卡（第2轮起增赞助方一行，卡增高）
    rows = [("datetime", DATE_TEXT, 36, t["text_primary"], LATIN_BLACK, "NORMAL"),
            ("speakers", SPEAKERS_TEXT, 28, t["text_secondary"], CJK, "NORMAL")]
    if rnd >= 2:
        rows.append(("sponsors", SPONSORS_TEXT, 26, t["text_secondary"],
                     CJK, "NORMAL"))
    card_h = 154 if rnd == 1 else 196
    meta_card(sc, M, y + 26, IW, card_h, rows, t)
    y = y + 26 + card_h

    # 英语短句（第3轮，网址上方）+ 网址
    if rnd >= 3:
        sc.text("en_tagline", EN_TEXT, M, y + 26, IW, 44, 28, t["text_brand"],
                family=LATIN_SEMI, bg="page")
        sc.text("url", URL_TEXT, M, y + 82, IW, 44, 28, t["text_brand"],
                family=LATIN_SEMI, bg="page")
        url_end = y + 82 + 44
    else:
        sc.text("url", URL_TEXT, M, y + 26, IW, 44, 28, t["text_brand"],
                family=LATIN_SEMI, bg="page")
        url_end = y + 26 + 44

    # 英雄徽标：按真实包围盒（含光束上探）定位，避免压到网址
    bo = EMBLEM_BBOX
    gap, bottom_limit = 26.0, 1250.0
    s = min(2.40, (bottom_limit - url_end - gap) / (bo["bottom"] - bo["top"]))
    top = url_end + gap
    cx = 540 - (bo["left"] + bo["right"]) / 2 * s
    cy = top - bo["top"] * s
    sc.node("\n".join(emblem_nodes(cx, cy, s, t)))
    sc.hero_emblem = {"scale": s, "cx": cx, "cy": cy,
                      "box": [cx + bo["left"] * s, cy + bo["top"] * s,
                              cx + bo["right"] * s, cy + bo["bottom"] * s]}
    return sc


# ================================================================ 横版 1440x810
def build_wide(rnd):
    tok = TOKENS[rnd]
    sc = Scene("launch-wide", 1440, 810, tok)
    t = tok
    M = 80
    LW = 820                                # 左栏宽 80..900
    RX, RW = 952, 408                       # 右栏 952..1360

    # 顶部扩展带：第1轮 0..130（内容整体下移平衡底部），第2/3轮 0..90
    hy = 133 if rnd == 1 else 93
    header(sc, M, hy, 0.30, 28, hy + 3)     # 徽标 hy..hy+44
    divider(sc, M, M + LW, hy + 68)

    # 徽标行
    if rnd == 1:
        pill(sc, "badge", BADGE_TEXT, M, hy + 88, 280, 54, 26)
        title_lines, tsize, lh = [TITLE_R1], 88, 130
    else:
        pill(sc, "badge", BADGE_TEXT, M, hy + 88, 280, 50, 26)
        pill(sc, "free_entry", FREE_TEXT, M + 296, hy + 88, 320, 50, 26)
        title_lines, tsize, lh = TITLE_R2_LINES, 54, 72
    ty = hy + 166
    for i, ln in enumerate(title_lines):
        sc.text("title", ln, M, ty + i * lh, LW, lh, tsize,
                t["text_primary"], style="BOLD", bg="page",
                lines=len(title_lines), role="main_title")
    y = ty + len(title_lines) * lh

    sc.text("subtitle", SUBTITLE, M, y + 24, LW, 42, 26, t["text_secondary"],
            bg="page")
    y += 24 + 42

    rows = [("datetime", DATE_TEXT, 34, t["text_primary"], LATIN_BLACK, "NORMAL"),
            ("speakers", SPEAKERS_TEXT, 28, t["text_secondary"], CJK, "NORMAL")]
    if rnd >= 2:
        rows.append(("sponsors", SPONSORS_TEXT, 26, t["text_secondary"],
                     CJK, "NORMAL"))
    # 卡高由行数算出：上 20 + 各行 size*1.5 + 行距 14 + 下 20。
    # 第2轮新增赞助方一行后必须重新算（写死 164 会让第三行探出卡片底边约 16px）。
    card_h = 164 if rnd == 1 else (20 + sum(sz * 1.5 + 14 for _, _, sz, _, _, _ in rows)
                                   - 14 + 20)
    meta_card(sc, M, y + 26, LW, card_h, rows, t)
    left_bottom = y + 26 + 164

    # 右栏：大徽标 + 网址（第3轮英语短句在网址上方）
    bo = EMBLEM_BBOX
    s = 1.50
    cx = RX + RW / 2 - (bo["left"] + bo["right"]) / 2 * s
    cy = (left_bottom + 90) / 2 - (bo["top"] + bo["bottom"]) / 2 * s
    sc.node("\n".join(emblem_nodes(cx, cy, s, t)))
    sc.hero_emblem = {"scale": s, "cx": cx, "cy": cy,
                      "box": [cx + bo["left"] * s, cy + bo["top"] * s,
                              cx + bo["right"] * s, cy + bo["bottom"] * s]}
    eb = sc.hero_emblem["box"]
    if rnd >= 3:
        sc.text("en_tagline", EN_TEXT, RX, eb[3] + 30, RW, 42, 26,
                t["text_brand"], family=LATIN_SEMI, bg="page")
        sc.text("url", URL_TEXT, RX, eb[3] + 84, RW, 42, 26,
                t["text_brand"], family=LATIN_SEMI, bg="page")
    else:
        sc.text("url", URL_TEXT, RX, eb[3] + 30, RW, 42, 26,
                t["text_brand"], family=LATIN_SEMI, bg="page")
    return sc


BUILDERS = {(1, "portrait"): build_portrait, (1, "wide"): build_wide,
            (2, "portrait"): build_portrait, (2, "wide"): build_wide,
            (3, "portrait"): build_portrait, (3, "wide"): build_wide}


def build(rnd, size, no_text=False):
    fn = BUILDERS[(rnd, size)]
    sc = fn(rnd)
    if no_text:
        # 去文字辅助渲染：保留徽标/卡片/pill/分隔线等全部背景层，仅去掉文字节点
        sc2 = Scene(sc.name, sc.w, sc.h, sc.tok, no_text=True)
        sc2.nodes = [n for n in sc.nodes
                     if "<Text " not in n]
        sc2.texts = sc.texts
        sc2.cards = sc.cards
        sc2.hero_emblem = getattr(sc, "hero_emblem", None)
        return sc2
    return sc
