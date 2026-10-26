# -*- coding: utf-8 -*-
"""A12 四断点完整内容视觉系统（v2：实测字宽，零截断）。

四个画布：360x800（窄手机单列）、768x1024（平板两列）、1440x900（桌面三列）、
1920x1080（大屏三列）。
全部内容一字不丢：title, subtitle, date, time, location, cta, website,
cards[].title, cards[].detail（C1-C6）。

与 v1 的差别：
- 所有字符串先用真实服务测量墨迹宽度（bm.batch_measure，一次渲染批量测），
  盒子宽度 = 实测 + 内边距，杜绝 ONLII / 详见官网 / example.or 这类截断；
- 主标题/副标题按实测字符宽度贪心折行，maxLines=行数，不再出现丢行；
- 大屏/桌面按可用高度均分卡高，内容垂直居中，消除下半屏空白；
- design-tokens.json / content-map.json 记录实测盒子坐标。
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ["SNAPSHOT_RUN_ID"]
TASK = "A12"
TASK_DIR = ROOT / "tasks" / "A12-responsive-system"
OUT_DIR = ROOT / "outputs" / RUN_ID / TASK
TMP_DIR = ROOT / "tmp" / RUN_ID / TASK
OUT_DIR.mkdir(parents=True, exist_ok=True)
TMP_DIR.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT / "tmp" / RUN_ID / "_suite"))
import bm  # noqa: E402

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
        "description": "圆角卡片 + 左侧 accent 竖条 + 序号圆点 + 胶囊标签；四断点重排不更换构件",
        "elements": ["radius_card", "accent_bar", "index_dot", "chip"],
    },
}

BP = {
    "mobile": {
        "canvas": [360, 800], "margin": 16, "fill": True, "fill_cap": 30,
        "title": 40, "subtitle": 20, "chip": 16, "cta": 18, "footnote": 16,
        "card_title": 18, "card_detail": 16,
        "cols": 1, "card_pad": 8, "gap": 6, "hero_pad": 10, "dot_d": 18,
        "chip_h": 28, "chip_pad": 12, "cta_h": 34, "cta_pad": 14,
        "sec_size": 20,
    },
    "tablet": {
        "canvas": [768, 1024], "margin": 32, "fill": True, "fill_cap": 110,
        "title": 48, "subtitle": 22, "chip": 18, "cta": 20, "footnote": 18,
        "card_title": 20, "card_detail": 20,
        "cols": 2, "card_pad": 18, "gap": 16, "hero_pad": 28, "dot_d": 26,
        "chip_h": 32, "chip_pad": 14, "cta_h": 40, "cta_pad": 16,
        "sec_size": 22,
    },
    "desktop": {
        "canvas": [1440, 900], "margin": 32, "fill": True, "fill_cap": 110,
        "title": 56, "subtitle": 24, "chip": 18, "cta": 22, "footnote": 20,
        "card_title": 22, "card_detail": 20,
        "cols": 3, "card_pad": 20, "gap": 20, "hero_pad": 36, "dot_d": 26,
        "chip_h": 34, "chip_pad": 14, "cta_h": 44, "cta_pad": 16,
        "sec_size": 22,
    },
    "stage": {
        "canvas": [1920, 1080], "margin": 32, "fill": True, "fill_cap": 110,
        "title": 64, "subtitle": 26, "chip": 20, "cta": 24, "footnote": 20,
        "card_title": 24, "card_detail": 22,
        "cols": 3, "card_pad": 24, "gap": 24, "hero_pad": 44, "dot_d": 28,
        "chip_h": 38, "chip_pad": 16, "cta_h": 48, "cta_pad": 18,
        "sec_size": 24,
    },
}

SECTION_TITLE = "六步工作流"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def txt(s, *, x, y, w, size, color="ink", family="primary", bold=False, align="LEFT",
        h=None, wrap=False, max_lines=1, mono=False, record=None, field=None):
    """放置一段文字。盒子宽 = 传入 w；wrap=True 时按 size 折行。"""
    col = TOKENS["color"][color]
    fam = TOKENS["font_family"]["monospace"] if mono else TOKENS["font_family"][family]
    h_attr = f' height="{h:.1f}"' if h else ""
    node = (
        f'<Positioned left="{x:.1f}" top="{y:.1f}" width="{w:.1f}"{h_attr}>'
        f'<Container color="transparent"><Text fontSize="{size}" fontFamily="{fam}"'
        + (' fontStyle="BOLD"' if bold else "")
        + f' color="{col}" textAlign="{align}" softWrap="{"true" if wrap else "false"}"'
        + f' maxLines="{max_lines}">{esc(s)}</Text></Container></Positioned>'
    )
    if record is not None and field is not None:
        record[field] = {
            "original": s, "displayed": s,
            "box": [round(x, 1), round(y, 1), round(x + w, 1), round(y + (h or size), 1)],
            "font_size": size, "complete": True,
        }
    return node


def box(x, y, w, h, color, *, radius=None, border=None):
    col = TOKENS["color"][color] if color in TOKENS["color"] else color
    a = ""
    if radius:
        a += f' borderRadius="{radius}"'
    if border:
        a += f' border="{border}"'
    return f'<Positioned left="{x:.1f}" top="{y:.1f}" width="{w:.1f}" height="{h:.1f}"><Container color="{col}"{a}/></Positioned>'


# ================= 测量阶段 =================
# 先测全串（判断是否放得下、算芯片/按钮/页脚宽度）
full_items = []   # (key, text, size, style, family)
full_keys = []


def add_full(text, size, style="NORMAL", family=SANS, key=None):
    k = key or f"{text}|{size}|{style}|{family}"
    if k not in full_keys:
        full_keys.append(k)
        full_items.append({"text": text, "size": size, "style": style, "family": family})
    return k


for nm, bp in BP.items():
    add_full(C["title"], bp["title"], "BOLD", key=f"title|{nm}")
    add_full(C["subtitle"], bp["subtitle"], key=f"subtitle|{nm}")
    for t in (C["date"], C["time"], C["location"]):
        add_full(t, bp["chip"], key=f"meta|{t}|{nm}")
    add_full(C["cta"], bp["cta"], "BOLD", key=f"cta|{nm}")
    add_full(C["website"], bp["footnote"], family=MONO, key=f"web|{nm}")
    for cd in C["cards"]:
        add_full(cd["title"], bp["card_title"], "BOLD", key=f"ct|{cd['id']}|{nm}")
        add_full(cd["detail"], bp["card_detail"], key=f"cdetail|{cd['id']}|{nm}")
    add_full(f"{C['title']} · {C['date']} · {C['location']}", bp["footnote"],
             key=f"footnote|{nm}")
    add_full(SECTION_TITLE, bp["sec_size"], "BOLD", key=f"sec|{nm}")

full_w = {}
res = bm.batch_measure(full_items, task_id=TASK, label="A12-measure-full")
for k, r in zip(full_keys, res):
    full_w[k] = r["width"]
print("measured full strings:", len(full_keys))

# 再测字符（为折行服务）：只测可能需要折行的字符串的字符。
# 注意：BOLD 文本必须用 BOLD 字形测，否则宽度偏小导致折行误判。
bold_chars, normal_chars = set(), set()
for nm, bp in BP.items():
    bold_chars |= set(C["title"])
    normal_chars |= set(C["subtitle"])
    for cd in C["cards"]:
        bold_chars |= set(cd["title"])
        normal_chars |= set(cd["detail"])
char_items = []
char_keys = []
for nm, bp in BP.items():
    for size, chars, style in ((bp["title"], bold_chars, "BOLD"),
                               (bp["card_title"], bold_chars, "BOLD"),
                               (bp["subtitle"], normal_chars, "NORMAL"),
                               (bp["card_detail"], normal_chars, "NORMAL")):
        for ch in sorted(chars):
            if ch == " ":
                continue
            k = f"{ch}|{size}|{style}"
            if k not in char_keys:
                char_keys.append(k)
                char_items.append({"text": ch, "size": size, "style": style})
char_w = {}
BATCH = 130
for i in range(0, len(char_items), BATCH):
    part = char_items[i:i + BATCH]
    keys = char_keys[i:i + BATCH]
    r = bm.batch_measure(part, task_id=TASK, label=f"A12-measure-chars-{i // BATCH}")
    for k, rr in zip(keys, r):
        char_w[k] = rr["width"] if rr["width"] is not None else 0
# 空格宽度按 0.32em 估
for nm, bp in BP.items():
    for size, style in ((bp["title"], "BOLD"), (bp["card_title"], "BOLD"),
                        (bp["subtitle"], "NORMAL"), (bp["card_detail"], "NORMAL")):
        char_w[f" |{size}|{style}"] = size * 0.32
print("measured chars:", len(char_keys))


def cw(ch, size, style="NORMAL"):
    if ch == " ":
        return char_w.get(f" |{size}|{style}", size * 0.32)
    return char_w.get(f"{ch}|{size}|{style}", size)


def wrap_lines(text, size, maxw, style="NORMAL"):
    """按实测字符宽度折行：优先在空格处断行，CJK 可按字断；
    单个西文词超长时才按字符断。返回行列表。"""
    # 切 token：CJK 单字为 token；西文连续串（含尾随空格）为 token
    tokens: list[str] = []
    buf = ""
    for ch in text:
        if ord(ch) > 0x2E7F:
            if buf:
                tokens.append(buf)
                buf = ""
            tokens.append(ch)
        else:
            buf += ch
            if ch == " ":
                tokens.append(buf)
                buf = ""
    if buf:
        tokens.append(buf)

    def tw(tok: str) -> float:
        return sum(cw(c, size, style) for c in tok)

    lines: list[str] = []
    cur = ""
    cur_w = 0.0
    for tok in tokens:
        w = tw(tok)
        stripped = tok.rstrip()
        if cur and cur_w + w > maxw + 0.5:
            if stripped and tw(stripped) <= maxw:
                # 整词换行
                lines.append(cur.rstrip())
                cur, cur_w = tok, w
            else:
                # 词超长：按字符断
                for c in tok:
                    cwid = cw(c, size, style)
                    if cur and cur_w + cwid > maxw + 0.5:
                        lines.append(cur.rstrip())
                        cur, cur_w = c, cwid
                    else:
                        cur += c
                        cur_w += cwid
        else:
            cur += tok
            cur_w += w
    if cur:
        lines.append(cur.rstrip())
    return lines or [""]


# ================= 生成阶段 =================
records = {}


def build(name):
    bp = BP[name]
    W, H = bp["canvas"]
    M = bp["margin"]
    nodes = [box(0, 0, W, H, "bg")]
    rec = {"canvas": {"width": W, "height": H}, "margin": M,
           "layout": ("mobile_single_column" if bp["cols"] == 1 else
                      "tablet_two_column" if bp["cols"] == 2 else
                      "desktop_or_stage_three_column"),
           "fields": {}, "cards": {}}

    hp = bp["hero_pad"]
    hx = M + hp
    hw = W - 2 * M - 2 * hp

    # ---- 主标题（实测折行）----
    t_lines = wrap_lines(C["title"], bp["title"], hw, "BOLD")
    t_lh = round(bp["title"] * 1.18)
    t_block = len(t_lines) * t_lh
    nodes.append(txt(C["title"], x=hx, y=M + hp, w=hw, size=bp["title"],
                     color="dark_text", bold=True, wrap=True, h=t_block,
                     max_lines=len(t_lines), record=rec["fields"], field="title"))
    rec["fields"]["title"]["lines"] = t_lines
    y = M + hp + t_block + 8

    # ---- 副标题 ----
    s_lines = wrap_lines(C["subtitle"], bp["subtitle"], hw)
    s_lh = round(bp["subtitle"] * 1.22)
    s_block = len(s_lines) * s_lh
    nodes.append(txt(C["subtitle"], x=hx, y=y, w=hw, size=bp["subtitle"],
                     color="dark_muted", wrap=True, h=s_block,
                     max_lines=len(s_lines), record=rec["fields"], field="subtitle"))
    rec["fields"]["subtitle"]["lines"] = s_lines
    y += s_block + 12

    # ---- meta chips（date / time / location）----
    msize = bp["chip"]
    chip_h = bp["chip_h"]
    cpad = bp["chip_pad"]
    meta = [("date", C["date"]), ("time", C["time"]), ("location", C["location"])]
    cx, cy = hx, y
    for fname, mtxt in meta:
        w = full_w[f"meta|{mtxt}|{name}"] + 2 * cpad
        if cx + w > hx + hw and cx > hx:
            cx = hx
            cy += chip_h + 6
        nodes.append(box(cx, cy, w, chip_h, "dark", radius=999, border="1 SOLID #334155"))
        nodes.append(txt(mtxt, x=cx + cpad, y=cy + (chip_h - msize) / 2 - 1,
                         w=w - 2 * cpad, size=msize, color="dark_text",
                         record=rec["fields"], field=fname))
        rec["fields"][fname]["box"] = [round(cx + cpad, 1), round(cy + (chip_h - msize) / 2 - 1, 1),
                                       round(cx + cpad + w - 2 * cpad, 1),
                                       round(cy + (chip_h - msize) / 2 - 1 + msize + 2, 1)]
        cx += w + 6
    y = cy + chip_h + 12

    # ---- CTA 按钮 + website ----
    cta_size = bp["cta"]
    cta_w = full_w[f"cta|{name}"] + 2 * bp["cta_pad"]
    nodes.append(box(hx, y, cta_w, bp["cta_h"], "accent", radius=TOKENS["radius"]["button"]))
    nodes.append(txt(C["cta"], x=hx + bp["cta_pad"],
                     y=y + (bp["cta_h"] - cta_size) / 2 - 1, w=cta_w - 2 * bp["cta_pad"],
                     size=cta_size, color="surface", bold=True,
                     record=rec["fields"], field="cta"))
    rec["fields"]["cta"]["box"] = [round(hx + bp["cta_pad"], 1),
                                   round(y + (bp["cta_h"] - cta_size) / 2 - 1, 1),
                                   round(hx + cta_w - bp["cta_pad"], 1),
                                   round(y + (bp["cta_h"] - cta_size) / 2 - 1 + cta_size + 2, 1)]
    web_w = full_w[f"web|{name}"] + 6
    wx = hx + cta_w + 16
    wy = y + (bp["cta_h"] - bp["footnote"]) / 2
    if wx + web_w > hx + hw:
        wx = hx
        wy = y + bp["cta_h"] + 10
        y = wy + bp["footnote"] + 10
    else:
        y = y + bp["cta_h"] + 12
    nodes.append(txt(C["website"], x=wx, y=wy, w=max(hx + hw - wx, web_w),
                     size=bp["footnote"], color="dark_muted", mono=True,
                     record=rec["fields"], field="website"))
    rec["fields"]["website"]["box"] = [round(wx, 1), round(wy, 1),
                                       round(wx + web_w, 1), round(wy + bp["footnote"] + 3, 1)]
    hero_h = (y + hp) - M
    nodes.append(box(M, M, W - 2 * M, hero_h, "dark", radius=TOKENS["radius"]["hero"]))
    # 重新按正确顺序拼接：hero 背景必须在文字之前——上面 nodes[0] 是 bg，
    # 这里把 hero 背景插到 bg 之后
    nodes.insert(1, nodes.pop())

    # ---- 六卡 ----
    sec_h = bp["sec_size"] + 8
    cards_top = M + hero_h + bp["gap"] + sec_h
    cols = bp["cols"]
    rows = (len(C["cards"]) + cols - 1) // cols
    avail_w = W - 2 * M
    card_gap = bp["gap"]
    card_w = (avail_w - card_gap * (cols - 1)) // cols
    pad = bp["card_pad"]
    dot_d = bp["dot_d"]
    ct, cd = bp["card_title"], bp["card_detail"]
    min_card_h = pad + max(dot_d, ct) + 8 + cd + pad
    footer_h = bp["footnote"] + 30
    avail_h = H - M - footer_h - cards_top
    if bp["fill"]:
        card_h = (avail_h - card_gap * (rows - 1)) / rows
        card_h = min(card_h, min_card_h + bp.get("fill_cap", 110))
        # 剩余空间匀给行间与节标题前
        slack = avail_h - (rows * card_h + card_gap * (rows - 1))
        if slack > 0:
            cards_top += slack * 0.45
            card_gap += slack * 0.55 / max(rows - 1, 1)
    else:
        card_h = min_card_h
        if rows * card_h + (rows - 1) * card_gap > avail_h:
            card_gap = max(4, card_gap - 2)
            card_h = max(min_card_h, (avail_h - (rows - 1) * card_gap) / rows)

    nodes.append(txt(SECTION_TITLE, x=M, y=cards_top - sec_h + 2, w=400, size=bp["sec_size"],
                     color="ink", bold=True, record=rec["fields"], field="section_header"))
    rec["fields"]["section_header"]["box"] = [M, cards_top - sec_h + 2,
                                              M + full_w[f"sec|{name}"],
                                              cards_top - sec_h + 2 + bp["sec_size"] + 2]

    for i, card in enumerate(C["cards"]):
        r, c = i // cols, i % cols
        x = M + c * (card_w + card_gap)
        y0 = cards_top + r * (card_h + card_gap)
        nodes.append(box(x, y0, card_w, card_h, "surface", radius=TOKENS["radius"]["card"],
                         border=TOKENS["shape"]["card_border"]))
        nodes.append(box(x, y0, TOKENS["shape"]["accent_bar_w"], card_h, "accent", radius=2))
        # 内容垂直居中
        content_h = max(dot_d, ct) + 8 + cd
        top = y0 + (card_h - content_h) / 2
        # 序号圆点
        nodes.append(box(x + pad, top, dot_d, dot_d, "accent", radius=dot_d / 2))
        num_size = 14 if dot_d >= 26 else 12
        nodes.append(txt(str(i + 1), x=x + pad, y=top + (dot_d - num_size) / 2 - 1,
                         w=dot_d, size=num_size, color="surface", bold=True, align="CENTER"))
        # 卡标题（与圆点同行；放不下则折行）
        tx = x + pad + dot_d + 10
        tw = card_w - (tx - x) - pad
        tkey = f"ct|{card['id']}|{name}"
        if full_w[tkey] <= tw:
            nodes.append(txt(card["title"], x=tx, y=top + (max(dot_d, ct) - ct) / 2 - 1,
                             w=tw, size=ct, color="ink", bold=True))
            tbox = [round(tx, 1), round(top + (max(dot_d, ct) - ct) / 2 - 1, 1),
                    round(tx + full_w[tkey], 1),
                    round(top + (max(dot_d, ct) - ct) / 2 - 1 + ct + 2, 1)]
            tlines = 1
        else:
            tl = wrap_lines(card["title"], ct, tw, "BOLD")
            tblock = len(tl) * round(ct * 1.2)
            nodes.append(txt(card["title"], x=tx, y=top - (tblock - ct) / 2, w=tw, size=ct,
                             color="ink", bold=True, wrap=True, h=tblock,
                             max_lines=len(tl)))
            tbox = [round(tx, 1), round(top - (tblock - ct) / 2, 1),
                    round(tx + tw, 1), round(top - (tblock - ct) / 2 + tblock, 1)]
            tlines = len(tl)
        # detail
        dy = top + max(dot_d, ct) + 8
        dw = card_w - 2 * pad
        dkey = f"cdetail|{card['id']}|{name}"
        if full_w[dkey] <= dw:
            nodes.append(txt(card["detail"], x=x + pad, y=dy, w=dw, size=cd,
                             color="ink_secondary"))
            dbox = [round(x + pad, 1), round(dy, 1), round(x + pad + full_w[dkey], 1),
                    round(dy + cd + 2, 1)]
            dlines = 1
        else:
            dl = wrap_lines(card["detail"], cd, dw)
            dblock = len(dl) * round(cd * 1.25)
            nodes.append(txt(card["detail"], x=x + pad, y=dy, w=dw, size=cd,
                             color="ink_secondary", wrap=True, h=dblock,
                             max_lines=len(dl)))
            dbox = [round(x + pad, 1), round(dy, 1), round(x + pad + dw, 1),
                    round(dy + dblock, 1)]
            dlines = len(dl)
        rec["cards"][card["id"]] = {
            "card_id": card["id"], "index": i + 1,
            "title": {"original": card["title"], "displayed": card["title"],
                      "box": tbox, "font_size": ct, "complete": True, "lines": tlines},
            "detail": {"original": card["detail"], "displayed": card["detail"],
                       "box": dbox, "font_size": cd, "complete": True, "lines": dlines},
            "card_box": [round(x, 1), round(y0, 1), round(x + card_w, 1),
                         round(y0 + card_h, 1)],
        }

    # ---- 页脚 ----
    fy = H - M - bp["footnote"] - 8
    note = f"{C['title']} · {C['date']} · {C['location']}"
    note_w = full_w[f"footnote|{name}"]
    web_w2 = full_w[f"web|{name}"] + 8
    if note_w + 24 + web_w2 <= W - 2 * M:
        nodes.append(box(M, fy - 12, W - 2 * M, 1, "line"))
        nodes.append(txt(note, x=M, y=fy, w=note_w + 4, size=bp["footnote"],
                         color="muted", record=rec["fields"], field="footer_note"))
        nodes.append(txt(C["website"], x=W - M - web_w2, y=fy, w=web_w2,
                         size=bp["footnote"], color="muted", mono=True, align="RIGHT"))
        rec["fields"]["footer_note"] = {
            "original": note, "displayed": note,
            "box": [M, round(fy, 1), M + note_w + 4, round(fy + bp["footnote"] + 3, 1)],
            "font_size": bp["footnote"], "complete": True}
        rec["fields"]["footer_website"] = {
            "original": C["website"], "displayed": C["website"],
            "box": [round(W - M - web_w2, 1), round(fy, 1), round(W - M, 1),
                    round(fy + bp["footnote"] + 3, 1)],
            "font_size": bp["footnote"], "complete": True}
    else:
        nodes.append(box(M, fy - 12, W - 2 * M, 1, "line"))
        nodes.append(txt(C["website"], x=M, y=fy, w=web_w2, size=bp["footnote"],
                         color="muted", mono=True))
        rec["fields"]["footer_website"] = {
            "original": C["website"], "displayed": C["website"],
            "box": [M, round(fy, 1), M + web_w2, round(fy + bp["footnote"] + 3, 1)],
            "font_size": bp["footnote"], "complete": True}

    dsl = (
        f'<Snapshot type="png" background="{TOKENS["color"]["bg"]}">'
        f'<Container width="{W}" height="{H}">'
        '<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE">'
        + "".join(nodes) + "</Stack></Container></Snapshot>"
    )
    (TMP_DIR / f"{name}.snapshot").write_text(dsl, encoding="utf-8")
    records[name] = rec
    print(f"wrote {name}.snapshot {len(dsl)} bytes; hero_h={hero_h:.0f} "
          f"cards_top={cards_top:.0f} card_h={card_h:.0f} rows={rows} "
          f"title_lines={t_lines}")
    return dsl


for nm in ["mobile", "tablet", "desktop", "stage"]:
    build(nm)

# ---------- design-tokens.json ----------
design_tokens = {
    "schema_version": 2,
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
    "measurement_note": "所有文字盒宽度由 open-snapshot 真实渲染测量（type=measure-batch），"
                        "盒宽 ≥ 实测墨迹宽，保证一字不丢；主标题/副标题按实测字符宽度折行。",
}
for nm, bp in BP.items():
    design_tokens["breakpoints"][nm] = {
        "canvas": bp["canvas"], "margin": bp["margin"],
        "type_scale": {
            "title": bp["title"], "subtitle": bp["subtitle"], "chip": bp["chip"],
            "cta": bp["cta"], "footnote": bp["footnote"],
            "card_title": bp["card_title"], "card_detail": bp["card_detail"],
        },
        "layout": {"columns": bp["cols"], "card_padding": bp["card_pad"],
                   "gap": bp["gap"], "hero_padding": bp["hero_pad"]},
        "meets_minimums": {
            "title_ge_40": bp["title"] >= 40,
            "body_min": bp["card_detail"] >= (16 if nm == "mobile" else 20),
            "card_title_ge_18": bp["card_title"] >= 18,
            "margin_ok": bp["margin"] >= (16 if nm == "mobile" else 32),
        },
    }
(OUT_DIR / "design-tokens.json").write_text(
    json.dumps(design_tokens, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("wrote design-tokens.json")

# ---------- content-map.json ----------
REQ = ["title", "subtitle", "date", "time", "location", "cta", "website"]
content_map = {
    "schema_version": 2,
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
                     "图内显示序号 1-6，不要求为 id 分配可见标签。",
    "fidelity_rules": {
        "no_omission": "小屏内容不得省略或改写成缩写",
        "no_ellipsis": "不使用省略号、缩写、改写或删句",
        "wrap_allowed": "允许排版自动折行或增加不改变词语的换行",
        "preserve": "保留原文字词、数字、大小写、标点及有意义的空格",
    },
    "measurement": "文字盒坐标由实测字宽计算；box 为 [x1,y1,x2,y2]（画布左上原点，像素）",
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
