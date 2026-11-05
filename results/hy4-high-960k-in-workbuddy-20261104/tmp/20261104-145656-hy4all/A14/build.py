#!/usr/bin/env python3
"""A14 · 八组文案压力测试与批量生成.

One parameterised rule reads inputs/cards.json and emits eight independent
1200x630 DSL cards.  Title size/wrapping is chosen from measured text width
(never by shrinking the whole layout).  All source strings are emitted
verbatim via CDATA; the only insertion is layout line breaks.  Status is
encoded by colour + text + a DSL-drawn symbol.  The cancelled card keeps its
full title and time and adds an explicit "本场取消" notice.
"""
import json
import math
import os
import sys

TOOLS = os.environ["TOOLS"]
sys.path.insert(0, TOOLS)
from dsl import Canvas, CN, LATIN, MONO, cdata  # noqa: E402
import suite  # noqa: E402

TASK = "A14"
ROOT = suite.ROOT
CARDS = json.loads(
    (ROOT / "tasks" / "A14-content-stress-batch" / "inputs" / "cards.json")
    .read_text(encoding="utf-8")
)

# ------------------------------------------------------------------ tokens
PAPER = "#F4F7FC"
WHITE = "#FFFFFF"
NAVY = "#0B2545"
NAVY2 = "#16386F"
INK = "#0F172A"
MUTED = "#5B6B85"
LINE = "#DDE5F0"
CYAN = "#38BDF8"
BLUE = "#1D4ED8"
SAFE = 40
DATE = "2026.11.07"
BRAND = "Structure / Vision"

STATUS = {
    "开放": {"code": "OPEN", "color": "#16A34A", "symbol": "circle", "label": "开放"},
    "满额": {"code": "FULL", "color": "#D97706", "symbol": "square", "label": "满额"},
    "候补": {"code": "WAITLIST", "color": "#2563EB", "symbol": "diamond", "label": "候补"},
    "取消": {"code": "CANCELLED", "color": "#DC2626", "symbol": "cross", "label": "取消"},
}

TITLE_X, TITLE_W = 64, 1088
TITLE_Y, TITLE_H = 180, 240
WRAP_W = 1040                      # conservative wrap width (48px slack vs box)
SPEAKER_X, SPEAKER_W = 64, 700
SPEAKER_Y, SPEAKER_H = 516, 68
TIME_X, TIME_W = 900, 260


# ------------------------------------------------------------------ wrapping
def char_w(ch, size):
    if ch == " ":
        return size * 0.30
    if ord(ch) >= 0x2E80:          # CJK / fullwidth punctuation
        return size * 1.0
    return size * 0.55             # latin / digits / ascii punctuation


def wrap(text, size, W):
    lines, cur, w = [], "", 0.0
    for ch in text:
        cw = char_w(ch, size)
        if w + cw > W and cur:
            lines.append(cur)
            cur, w = "", 0.0
        cur += ch
        w += cw
    if cur:
        lines.append(cur)
    return lines


def choose_title(title):
    """Prefer one line at the largest size; never below 36, never above 3 lines."""
    for size in (56, 50, 44, 40, 36):
        lines = wrap(title, size, WRAP_W)
        if len(lines) == 1:
            return size, lines
    size = 40
    lines = wrap(title, size, WRAP_W)
    if len(lines) > 3:
        size = 36
        lines = wrap(title, size, WRAP_W)
    return size, lines


def raw_multiline(c, x, y, w, h, text, size, color, bold=True):
    """Raw + CDATA keeps explicit line breaks and every special character."""
    a = [f'fontFamily="{CN}"', f'fontSize="{size}"', f'color="{color}"',
         'textAlign="LEFT"', 'softWrap="true"']
    if bold:
        a.append('fontStyle="BOLD"')
    inner = (f'<Container width="{round(w,2)}" height="{round(h,2)}" alignment="CENTER_LEFT">'
             f'<Text {" ".join(a)}><Raw>{cdata(text)}</Raw></Text></Container>')
    c.add(x, y, w, h, inner)


# ------------------------------------------------------------------ components
def status_badge(c, x, y, w, h, st):
    col = st["color"]
    c.rect(x, y, w, h, col, radius=h / 2)
    cx, cy = x + 30, y + h / 2
    if st["symbol"] == "circle":
        c.circle(cx, cy, 9, WHITE)
    elif st["symbol"] == "square":
        c.rect(cx - 9, cy - 9, 18, 18, WHITE, radius=4)
    elif st["symbol"] == "diamond":
        c.poly([(cx, cy - 11), (cx + 11, cy), (cx, cy + 11), (cx - 11, cy)], WHITE)
    else:
        c.line(cx - 9, cy - 9, cx + 9, cy + 9, 4, WHITE)
        c.line(cx - 9, cy + 9, cx + 9, cy - 9, 4, WHITE)
    c.text(x + 52, y, w - 64, h, "%s %s" % (st["label"], st["code"]),
           22, WHITE, bold=True, align="LEFT")


def build_card(card):
    cid = card["id"]
    st = STATUS[card["status"]]
    cancelled = st["code"] == "CANCELLED"
    size, lines = choose_title(card["title"])
    display_title = "\n".join(lines)
    assert "".join(lines) == card["title"], "title text must stay verbatim"

    c = Canvas(1200, 630, PAPER, font=CN)
    c.rect(0, 0, 1200, 6, CYAN)
    c.rect(0, 624, 1200, 6, BLUE)

    # header: shared brand + date + status badge
    c.gradient(SAFE, SAFE, 1120, 112, [NAVY, NAVY2], radius=16,
               begin="TOP_LEFT", end="BOTTOM_RIGHT")
    c.text(64, 54, 560, 38, BRAND, 30, WHITE, bold=True, font=LATIN)
    c.text(64, 96, 560, 28, DATE + "  ·  LECTURE SERIES", 20, "#A9C9F2", font=LATIN)
    status_badge(c, 880, 68, 256, 56, st)

    # title: fixed region, parameterised size / explicit wrapping
    c.rect(SAFE, 190, 6, 64, CYAN, radius=3)
    raw_multiline(c, TITLE_X, TITLE_Y, TITLE_W, TITLE_H, display_title, size, INK)

    # session band (cancelled card gets an explicit red notice, never greys out)
    if cancelled:
        c.rect(SAFE, 420, 1120, 46, "#FEE2E2", radius=8)
        c.rect(SAFE, 420, 6, 46, st["color"], radius=3)
        c.text(64, 420, 1088, 46,
               "SESSION %s  ·  本场取消  /  SESSION CANCELLED" % cid,
               22, st["color"], bold=True)
    else:
        c.text(64, 424, 700, 36, "SESSION %s" % cid, 20, MUTED, font=LATIN)

    # footer: speaker (up to two lines) + time
    c.hline(SAFE, 478, 1120, 2, LINE)
    c.text(SPEAKER_X, 488, SPEAKER_W, 26, "讲者  SPEAKER", 18, MUTED)
    c.text(SPEAKER_X, SPEAKER_Y, SPEAKER_W, SPEAKER_H, card["speaker"],
           26, INK, bold=True)
    c.text(TIME_X, 488, TIME_W, 26, "TIME", 18, MUTED, font=LATIN, align="RIGHT")
    c.text(TIME_X, 516, TIME_W, 60, card["time"], 40, INK, bold=True,
           font=MONO, align="RIGHT")
    return c.render(), {
        "title_size": size, "title_lines": lines,
        "title_display": display_title,
        "status": st, "cancelled": cancelled,
    }


# ------------------------------------------------------------------ emit
dsls, metas = {}, {}
for card in CARDS:
    dsl, meta = build_card(card)
    dsls[card["id"]] = dsl
    metas[card["id"]] = meta

out = suite.out_dir(TASK)
ver = os.environ.get("BUILD_VERSION", "v1")
tmp = suite.tmp_dir(TASK, ver)
for cid, dsl in dsls.items():
    (out / ("card-%s.snapshot" % cid)).write_text(dsl, encoding="utf-8")
    (tmp / ("card-%s.snapshot" % cid)).write_text(dsl, encoding="utf-8")

# ------------------------------------------------------------------ batch-audit.json
cards_audit = []
for card in CARDS:
    cid = card["id"]
    m = metas[cid]
    st = m["status"]
    cards_audit.append({
        "id": cid,
        "original": {"title": card["title"], "speaker": card["speaker"],
                     "status": card["status"], "time": card["time"]},
        "display_text": {"title": m["title_display"], "speaker": card["speaker"],
                         "status": st["label"], "status_code": st["code"],
                         "time": card["time"], "brand": BRAND, "date": DATE},
        "png": "card-%s.png" % cid,
        "dsl": "card-%s.snapshot" % cid,
        "title": {"size": m["title_size"], "line_count": len(m["title_lines"]),
                  "lines": m["title_lines"],
                  "box": [TITLE_X, TITLE_Y, TITLE_X + TITLE_W, TITLE_Y + TITLE_H],
                  "wrap_width": WRAP_W, "font": CN, "max_lines": 3},
        "speaker": {"size": 26, "box": [SPEAKER_X, SPEAKER_Y,
                                       SPEAKER_X + SPEAKER_W, SPEAKER_Y + SPEAKER_H],
                    "max_lines": 2, "font": CN},
        "time": {"size": 40, "box": [TIME_X, 516, TIME_X + TIME_W, 576], "font": MONO},
        "status_encoding": {"label": st["label"], "code": st["code"],
                            "color": st["color"], "symbol": st["symbol"],
                            "badge_box": [880, 68, 1136, 124],
                            "channels": ["颜色", "文字/编码", "DSL 几何符号"]},
        "cancelled_card": m["cancelled"],
        "cancelled_notice": ("本场取消 / SESSION CANCELLED（红色横条 y=420..466，标题与时间完整保留）"
                             if m["cancelled"] else None),
        "safe_margin": SAFE,
        "canvas": [1200, 630],
        "image_view": None,
    })

audit = {
    "schema_version": 1,
    "task_id": TASK,
    "path_base": "output_dir",
    "generation": {
        "script": {"path_base": "suite_root",
                   "path": "tmp/20261104-145656-hy4all/A14/build.py"},
        "input": {"path_base": "suite_root",
                  "path": "tasks/A14-content-stress-batch/inputs/cards.json"},
        "method": "一套参数化规则从 cards.json 生成 8 份独立完整 DSL，未逐条硬改输入；仅按文本长度触发标题字号/换行与状态编码",
        "shared": {"canvas": [1200, 630], "safe_margin": SAFE, "brand": BRAND,
                   "date": DATE, "primary": BLUE, "header": [NAVY, NAVY2],
                   "title_region": [TITLE_X, TITLE_Y, TITLE_W, TITLE_H],
                   "title_min_size": 36, "title_max_lines": 3,
                   "speaker_min_size": 22},
        "length_branches": {
            "title": "按加权字符宽（中文/全角=size，拉丁=0.55·size，空格=0.30·size）在保守宽度 1040 分行；从 56/50/44/40/36 中选能单行的最大字号，无单行方案则用 40 号（必要时 36 号）允许 2–3 行；不通过缩小整图适配长标题",
            "speaker": "讲者盒 700×68 支持 2 行 26 号自动折行（题面允许长讲者两行）",
            "status": "4 个状态由颜色 + 文字/编码 + DSL 几何符号共同区分；取消卡保留完整标题与时间并另加红色『本场取消』横条",
            "special_chars": "全部文案经 CDATA 输出，A < B & C > D、&、中文引号、破折号、· 均原样，parser 不做实体解码",
        },
        "preserved_verbatim": "原始 title/speaker/status/time 逐字保留；仅插入不改变词语的排版换行（title_display 记录）",
    },
    "cards": cards_audit,
    "reviews": [
        {"id": c["id"], "png": "card-%s.png" % c["id"], "viewed_at": None,
         "observed": None, "change": None, "final_verdict": None}
        for c in CARDS
    ],
    "contact_sheet": {"note": "接触表仅作一致性辅助证据，不替代八张最终服务原图",
                      "path_base": "suite_root",
                      "path": "tmp/20261104-145656-hy4all/A14/preview/contact-sheet.png"},
    "checks": [
        {"item": "8 张卡内容完整且逐字保真", "observed": None},
        {"item": "标题字号≥36、最多3行、不与状态徽标碰撞、安全边距40", "observed": None},
        {"item": "取消卡保留完整标题与时间并注明本场取消", "observed": None},
        {"item": "八张最终 PNG 逐张实际打开查看", "observed": None},
    ],
}
(out / "batch-audit.json").write_text(
    json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print("A14 built | ver=%s | cards=%d" % (ver, len(dsls)))
for card in CARDS:
    cid = card["id"]
    m = metas[cid]
    print("  %s size=%2d lines=%d status=%-9s bytes=%d" % (
        cid, m["title_size"], len(m["title_lines"]), m["status"]["code"],
        len(dsls[cid].encode("utf-8"))))
