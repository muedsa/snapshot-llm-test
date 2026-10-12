"""A14 · 八张讲座宣传卡 — 参数化排版规则（一套规则，八条数据）。

设计约束来自 TASK.md：
  * 统一主色 / 标题区域 / 日期 2026.11.07 / 品牌 Structure \/ Vision / 状态体系；
  * 标题 >=36pt 且最多 3 行，讲者 >=22pt（长讲者允许两行）；
  * 状态用「颜色 + 文字/符号」共同区分：开放、满额、候补、取消；
  * 取消卡保留完整标题与时间，并另注明「本场取消」；
  * 安全边距 40，标题不得与状态徽标碰撞；
  * 不允许通过全局缩小整图来适配长标题 —— 长度只能触发字号档位或网格切换。

这里的所有尺寸/行数都先经过 dslkit.TextFit 的宽度估算（Snapshot 裁切文字不加省略号，
盒小了就静默丢字），再把每张卡实际采用的档位、盒位置写进 tmp/<run_id>/A14/layout.json，
供 check_a14.py 与交付的 batch-audit.json 使用。
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RID = os.environ["SNAPSHOT_RUN_ID"]
sys.path.insert(0, str(ROOT / "tmp" / RID / "_suite" / "scripts"))
from dslkit import Doc, TextFit, n, esc  # noqa: E402

TEMP = ROOT / "tmp" / RID / "A14"
OUT = ROOT / "outputs" / RID / "A14"
SRC = ROOT / "tasks" / "A14-content-stress-batch" / "inputs" / "cards.json"

W, H, M = 1200, 630, 40
DATE = "2026.11.07"
BRAND = "Structure / Vision"

P = {
    "primary": "#1B3A6B",     # 统一主色：所有卡共用
    "primary2": "#2F5FA8",
    "ink": "#101826",
    "muted": "#54637A",
    "paper": "#F2F5F9",
    "card": "#FFFFFF",
    "rule": "#D8E0EA",
    "rail": "#E7EDF5",
}
FONT = "Inter,Noto Sans CJK SC"

# 状态体系：颜色 + 几何符号 + 原文字，三者共同编码（色觉不可辨时仍靠符号与文字区分）
STATUS = {
    "开放": {"color": "#1F7A4D", "tint": "#E4F2EA", "symbol": "disc"},
    "满额": {"color": "#B3261E", "tint": "#FBE9E7", "symbol": "square"},
    "候补": {"color": "#A15C07", "tint": "#FBEEDC", "symbol": "diamond"},
    "取消": {"color": "#74191F", "tint": "#EFEAE9", "symbol": "ring"},
}
TITLE_SIZES = [72, 60, 48, 40, 36]     # 下限 36，低于 36 不用
SPEAKER_SIZES = [30, 26, 22]           # 下限 22


class Fit(TextFit):
    """A14 re-calibration of the shared text-width model.

    v01 pixel evidence: K02's 12-character title fits ONE 72pt line inside the 896px box
    (12 x 73.4 = 881 > 896*0.96 = 860, so the shared model predicted two), and K08's first
    line holds 16 glyphs measured at 886 estimated / 896 available. Noto Sans CJK SC
    advances at 1.00em and the renderer uses the whole box width, so the shared
    1.02em + 0.96 slack double-counts ~6 % — harmless for a clipping check, but it made the
    title box reserve a line it never rendered and left a visible hole above the speaker.
    Subclassed, so the estimate A01-A13 were built with stays as it is.
    """

    def w(self, s, size):
        t = 0.0
        for c in s:
            o = ord(c)
            if c == " ":
                t += size * 0.30
            elif o >= 0x2E80 or 0x2190 <= o <= 0x24FF or 0x25A0 <= o <= 0x25FF \
                    or c in "·＝—°／→×":
                t += size * 1.00
            elif c.isalpha():
                t += size * 0.60          # bold Inter runs wider than the regular 0.58
            elif c.isdigit():
                t += size * 0.58
            else:
                t += size * 0.50
        return t

    def lines(self, s, size, bw):
        return len(self.wrap(s, size, bw))


FIT = Fit()


def hh(size, lines=1):
    """line box = 1.45em (A12 measurement) plus a descender allowance."""
    return round(size * 1.45 * lines) + 2


def pick_size(s, sizes, box_w, max_lines, max_h=None):
    """Largest size from the scale that still fits max_lines AND max_h. Never returns a
    size below the scale floor — a title that cannot fit the floor changes grid instead.

    The height limit matters as much as the line count: Snapshot clips text to its box, so
    a 3-line title at the top of the scale is only legal while the stack above the footer
    still holds it. Without this gate the title box quietly grew through the rule line.
    """
    for size in sizes:
        nl = FIT.lines(s, size, box_w)
        if nl <= max_lines and (max_h is None or hh(size, nl) <= max_h):
            return size, nl
    return sizes[-1], FIT.lines(s, sizes[-1], box_w)


def symbol(doc, cx, cy, d, kind, color):
    """Status glyph built from Container geometry only (no font glyph, no image)."""
    if kind == "disc":
        doc.rect(cx - d / 2, cy - d / 2, d, d, color, radius=d / 2)
    elif kind == "square":
        doc.rect(cx - d / 2, cy - d / 2, d, d, color, radius=2)
    elif kind == "diamond":
        seg = ('<Transform matrix="(0.707107,0.707107,0,0,-0.707107,0.707107,0,0,'
               '0,0,1,0,0,0,0,1)" alignment="CENTER">'
               + doc.box(d * 0.78, d * 0.78, color=color, radius=2) + "</Transform>")
        doc.pos(cx - d / 2, cy - d / 2, d, d, seg)
    elif kind == "ring":
        doc.pos(cx - d / 2, cy - d / 2, d, d,
                doc.box(d, d, radius=d / 2, border=f"3 SOLID {color}"))
        doc.line(cx - d * 0.30, cy + d * 0.30, cx + d * 0.30, cy - d * 0.30, 3, color,
                 radius=1.5)


def bars(doc, x, y, idx, color=P["primary"]):
    """The 'Structure' motif: idx stacked bars, one per session number, all derived from data."""
    for i in range(idx):
        doc.rect(x, y + i * 14, 46 + i * 12, 8, color if i == 0 else P["rule"], radius=4)


def bars_h(doc, x, y, idx, color=P["primary"]):
    """Same motif, rotated into a horizontal row for grid B, whose top strip has no
    vertical room for the stacked form."""
    for i in range(idx):
        doc.rect(x + i * 14, y + (34 - (10 + i * 3)) / 2, 8, 10 + i * 3,
                 color if i == 0 else P["rule"], radius=4)


def card(c, idx):
    """Grid A: left rail (index / date / time) + main column.
    Grid B: rail becomes a top strip and the title takes the full content width —
    used only when the title cannot fit grid A's column at the 36pt floor."""
    status = STATUS[c["status"]]
    cx0, cx1 = M, W - M
    doc = Doc(W, H, bg=P["paper"], font=FONT)
    doc.rect(0, 0, W, H, P["paper"])
    doc.rect(cx0, cx0, cx1 - cx0, H - 2 * M, P["card"], radius=18)

    rail_w, gap = 190, 34
    main_x = cx0 + rail_w + gap
    main_w = cx1 - main_x
    badge_w = round(FIT.w(c["status"], 24) / FIT.SLACK) + 62
    badge_h = 52
    badge = (cx1 - 24 - badge_w, cx0 + 24, badge_w, badge_h)

    foot_y = H - M - 74
    content_bottom = foot_y - 20          # the rule line, plus breathing room
    sp = c["speaker"]
    ssize, slines = pick_size(sp, SPEAKER_SIZES, main_w, 2)
    sp_h = hh(ssize, slines)

    title, grid = c["title"], "A"
    # Grid trigger is width-driven: only a title that cannot reach 3 lines at the 36pt
    # floor inside grid A's narrower column earns the full-width grid B column.
    tsize, tlines = pick_size(title, TITLE_SIZES, main_w, 3)
    if FIT.lines(title, TITLE_SIZES[-1], main_w) > 3:
        grid = "B"
        rail_w, gap = 0, 0
        main_x = cx0 + 34
        main_w = cx1 - main_x - 34
        ssize, slines = pick_size(sp, SPEAKER_SIZES, main_w, 2)
        sp_h = hh(ssize, slines)
        tsize, tlines = pick_size(title, TITLE_SIZES, main_w, 3)

    # ---- rail (grid A) or top strip (grid B) -------------------------------------------
    # The badge is placed first and everything else is laid out around it, so a long title
    # can never run under it: the title's top edge starts below the badge row.
    bx, by, bw, bh = badge
    if grid == "A":
        doc.rect(cx0, cx0, rail_w, H - 2 * M, P["rail"], radius=18)
        doc.label(cx0, 78, rail_w, 60, c["id"], P["primary"], 44, "BOLD", align="CENTER")
        doc.label(cx0, 140, rail_w, 30, DATE, P["muted"], 20, align="CENTER")
        doc.line(cx0 + 46, 186, cx0 + rail_w - 46, 186, 2, P["rule"])
        doc.label(cx0, 202, rail_w, 44, c["time"], P["ink"], 32, "BOLD", align="CENTER")
        doc.label(cx0, 246, rail_w, 26, "开始时间", P["muted"], 17, align="CENTER")
        bars(doc, cx0 + 46, 300, idx)
        title_y = by + bh + 22
    else:
        doc.rect(cx0, cx0, cx1 - cx0, 96, P["rail"], radius=18)
        doc.label(cx0 + 34, cx0 + 22, 120, 52, c["id"], P["primary"], 38, "BOLD")
        doc.label(cx0 + 154, cx0 + 30, 240, 36, DATE, P["muted"], 22)
        doc.label(bx - 300, cx0 + 22, 266, 52, c["time"], P["ink"], 34, "BOLD",
                  align="END")
        bars_h(doc, 520, cx0 + 30, idx)
        title_y = cx0 + 118

    # ---- status badge ------------------------------------------------------------------
    doc.rect(bx, by, bw, bh, status["tint"], radius=bh / 2)
    symbol(doc, bx + 26, by + bh / 2, 18, status["symbol"], status["color"])
    doc.label(bx + 44, by, bw - 52, bh, c["status"], status["color"], 24, "BOLD",
              align="CENTER")

    # ---- title -------------------------------------------------------------------------
    # Height budget, bottom-up: what is left above the speaker block and the rule line.
    top = title_y
    max_h = content_bottom - top - 22 - sp_h
    tsize, tlines = pick_size(title, TITLE_SIZES, main_w, 3, max_h)
    title_h = hh(tsize, tlines)
    # Vertically centre title+speaker in the free band. Anchoring both to the top left a
    # 200px hole under the short titles (K01/K02), which reads as leftover space rather
    # than as a layout; the badge, rail and footer stay pinned, only the block moves.
    block_h = title_h + 22 + sp_h
    title_y = round(top + max(0, (content_bottom - top - block_h) / 2))
    doc.pos(main_x, title_y, main_w, title_h,
            doc.box(main_w, title_h,
                    inner=doc.text(title, P["ink"], tsize, "BOLD", maxlines=3),
                    align="CENTER_LEFT"))
    # ---- speaker -----------------------------------------------------------------------
    sp_y = title_y + title_h + 22
    doc.label(main_x, sp_y, main_w, sp_h, "讲者  " + sp, P["muted"], ssize)
    # ---- footer ------------------------------------------------------------------------
    doc.line(cx0 + 34, foot_y, cx1 - 34, foot_y, 2, P["rule"])
    doc.label(cx0 + 34, foot_y + 14, 420, 40, BRAND, P["primary"], 26, "BOLD")
    note = "本场取消" if c["status"] == "取消" else "讲座日程 · Lecture Series"
    doc.label(cx1 - 634, foot_y + 20, 600, 32, note,
              status["color"] if c["status"] == "取消" else P["muted"], 20,
              "BOLD" if c["status"] == "取消" else None, align="END")
    # measure every fixed box we just emitted; Snapshot clips silently, so a box that is
    # one glyph too narrow loses text without any error
    FIT.check(f"{c['id']}-title", title, tsize, main_w, title_h, 3)
    FIT.check(f"{c['id']}-speaker", "讲者  " + sp, ssize, main_w, sp_h, 2)
    FIT.check(f"{c['id']}-note", note, 20, 600, 32)
    FIT.check(f"{c['id']}-brand", BRAND, 26, 420, 40)
    FIT.check(f"{c['id']}-badge", c["status"], 24, bw - 52, bh)

    boxes = {"badge": [bx, by, bw, bh],
             "title": [main_x, title_y, main_w, title_h],
             "speaker": [main_x, sp_y, main_w, sp_h],
             "footer_note": [cx1 - 634, foot_y + 14, 600, 40]}
    geo = {"id": c["id"], "grid": grid, "title_size": tsize, "title_lines": tlines,
           "title_est_width": round(FIT.w(title, tsize)), "title_height_budget": max_h,
           "band": [top, content_bottom],
           "speaker_size": ssize, "speaker_lines": slines, "status": c["status"],
           "status_symbol": status["symbol"], "status_color": status["color"],
           "content_bottom": content_bottom, "boxes": boxes, "safe_margin": M}
    return doc, geo


def overlap(a, b):
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return ax < bx + bw and bx < ax + aw and ay < by + bh and by < ay + ah


def main():
    cards = json.loads(SRC.read_text(encoding="utf-8"))
    OUT.mkdir(parents=True, exist_ok=True)
    TEMP.mkdir(parents=True, exist_ok=True)
    geos, problems = [], []
    for i, c in enumerate(cards, start=1):
        doc, geo = card(c, i)
        dsl = doc.dsl()
        (OUT / f"card-{c['id']}.snapshot").write_text(dsl, encoding="utf-8")
        (TEMP / f"card-{c['id']}.snapshot").write_text(dsl, encoding="utf-8")
        # collision gate: the badge is the box a long title would run into
        for k in ("title", "speaker"):
            if overlap(geo["boxes"]["badge"], geo["boxes"][k]):
                problems.append(f"{c['id']}: badge overlaps {k}")
        if geo["title_size"] < 36 or geo["title_lines"] > 3:
            problems.append(f"{c['id']}: title floor breached "
                            f"{geo['title_size']}pt/{geo['title_lines']}line")
        if geo["speaker_size"] < 22 or geo["speaker_lines"] > 2:
            problems.append(f"{c['id']}: speaker floor breached")
        tb = geo["boxes"]["title"][1] + geo["boxes"]["title"][3]
        sb = geo["boxes"]["speaker"][1] + geo["boxes"]["speaker"][3]
        if tb > geo["content_bottom"] or sb > geo["content_bottom"]:
            problems.append(f"{c['id']}: stack bottom {max(tb, sb)} > "
                            f"content bottom {geo['content_bottom']}")
        for b in geo["boxes"].values():
            if b[0] < M or b[1] < M or b[0] + b[2] > W - M or b[1] + b[3] > H - M:
                problems.append(f"{c['id']}: box {b} outside the 40px safe margin")
        geo["text"] = {"title": c["title"], "speaker": c["speaker"], "time": c["time"],
                       "status": c["status"]}
        geos.append(geo)
    (TEMP / "layout.json").write_text(json.dumps({"cards": geos, "problems": problems,
                                                 "fit_warnings": FIT.problems},
                                                 ensure_ascii=False, indent=1),
                                      encoding="utf-8")
    print(json.dumps({"cards": len(geos), "problems": problems,
                      "grids": {g["id"]: g["grid"] for g in geos},
                      "title_sizes": {g["id"]: [g["title_size"], g["title_lines"]]
                                      for g in geos}},
                     ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
