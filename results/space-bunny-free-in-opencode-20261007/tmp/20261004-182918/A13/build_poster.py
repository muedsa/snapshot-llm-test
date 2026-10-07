# -*- coding: utf-8 -*-
"""A13 - launch-poster.png (1080x1350).

Independent composition (not an enlarged banner): a dark editorial stack -
top bar with the mono mark + OPEN BETA pill, a 420px colour mark whose window
shows the dark ground, the stacked wordmark, a three-column capability row and
a footer card with the mono mark, the URL and the launch date.
"""
import json
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import snapkit  # noqa: E402
import dsllib as D  # noqa: E402
import state as S  # noqa: E402
import layerlight as L  # noqa: E402

TASK = "A13"
OUT = os.path.join(S.OUT_ROOT, TASK)
TMP = os.path.join(S.TMP_ROOT, TASK)
snapkit.configure(TASK, OUT, TMP)

W, H = 1080, 1350
M = 84
CW = W - 2 * M                     # 912
P = L.PALETTE
MARK = L.MARK
CLEAR_RATIO = 1.0 / 9.0

# dark-ground palette additions
CARD = "#151D38FF"
HAIR = "#2A3557FF"
MUT_D = "#AEB9D1FF"
FAINT_D = "#7E8AA6FF"
PAPER = "#F6F7FBFF"

kids = [D.box(0, 0, W, H, color=None,
              gradient={"gradientType": "LINEAR",
                        "gradientColors": "#131D3AFF,#090E1CFF",
                        "gradientStops": "0,1",
                        "gradientBegin": "TOP_CENTER",
                        "gradientEnd": "BOTTOM_CENTER"})]

# ---------------------------------------------------------------- top bar
INK_TOP = 52.0
ox_t, oy_t, kt = L.fitted(MARK, M + INK_TOP / 2.0, 112.0, INK_TOP)
kids += L.emit(MARK, ox_t, oy_t, kt, L.MARK_ROLE_COLOR_ON_DARK)
pill_w, pill_h = 172.0, 38.0
pill_x = W - M - pill_w
kids += [
    D.box(pill_x, 93, pill_w, pill_h, color=P["amber"], radius=pill_h / 2),
    D.text_el("OPEN BETA", x=pill_x, y=93 + (pill_h - 17 * 1.2) / 2, w=pill_w,
              h=26, size=17, style="BOLD", color="#0B1020FF", align="CENTER",
              font=D.LATIN, ls=1.2),
    D.text_el("Layerlight", x=M + INK_TOP + 22, y=112 - 22 * 1.2 / 2, w=320, h=30,
              size=22, color=PAPER, ls=2, font=D.LATIN),
]

# ---------------------------------------------------------------- hero mark
INK_HERO = 420.0
ox, oy, k = L.fitted(MARK, W / 2.0, 400.0, INK_HERO)
kids += L.emit(MARK, ox, oy, k, L.MARK_ROLE_COLOR)

# ---------------------------------------------------------------- type stack
kids += [
    D.hline(M, W - M, 672, HAIR, 1),
    D.text_el("叠光", x=M, y=700, w=400, h=164, size=132, style="BOLD",
              color=PAPER, font=D.CJK, max_lines=1),
    D.text_el("Layerlight", x=M + 6, y=876, w=760, h=62, size=46, color=P["cyan"],
              ls=8, font=D.LATIN, max_lines=1),
    D.text_el("把复杂信息，组织成清晰画面", x=M, y=958, w=760, h=48, size=34,
              color=MUT_D, font=D.CJK, max_lines=1),
]

# ---------------------------------------------------------------- capability row
COLS = [("结构化图层", "STRUCTURED LAYERS", P["amber"]),
        ("可验证几何", "VERIFIABLE GEOMETRY", P["cyan"]),
        ("单色与负形", "MONO + NEGATIVE SPACE", "#8B7BFF")]
col_w = 288.0
for i, (cn, en, accent) in enumerate(COLS):
    cx = M + i * (col_w + 24.0)
    kids += [
        D.box(cx, 1032, 30, 3, color=accent, radius=1.5),
        D.text_el(cn, x=cx, y=1048, w=col_w, h=30, size=21, color="#E6EAF5FF",
                  font=D.CJK, max_lines=1),
        D.text_el(en, x=cx, y=1078, w=col_w, h=22, size=14, color=FAINT_D,
                  ls=1.0, font=D.LATIN, max_lines=1),
    ]

# ---------------------------------------------------------------- footer card
CARD_Y, CARD_H = 1120.0, 146.0
INK_CARD = 96.0
ox_c, oy_c, kc = L.fitted(MARK, M + 40 + INK_CARD / 2.0, CARD_Y + CARD_H / 2.0, INK_CARD)
kids += [
    D.box(M, CARD_Y, CW, CARD_H, color=CARD, radius=22, border="1 SOLID " + HAIR),
]
kids += L.emit(MARK, ox_c, oy_c, kc, L.MARK_ROLE_COLOR_ON_DARK)
TX_C = M + 40 + INK_CARD + 32
kids += [
    D.text_el("layerlight.example.org", x=TX_C, y=CARD_Y + 34, w=CW - 200, h=44,
              size=32, color=PAPER, font=D.LATIN, max_lines=1),
    D.text_el("2026.11.07 · ONLINE", x=TX_C, y=CARD_Y + 82, w=CW - 200, h=32,
              size=22, color=P["amber"], font=D.LATIN, ls=1.2, max_lines=1),
]

dsl = D.snapshot([D.stack(kids, W, H)], W, H, bg="#0B1020FF")
with open(os.path.join(TMP, "drafts", "v12-poster.snapshot"), "w",
          encoding="utf-8", newline="\n") as fh:
    fh.write(dsl)
r = snapkit.render(dsl, "launch-poster.png", "launch-poster.snapshot", final=True)
print("render ok=%s status=%s bytes=%s" % (r.get("ok"), r.get("status"), r.get("bytes")))
if not r.get("ok"):
    print(r.get("error"))
for w in D.warnings():
    print("WARN", w)

geom = {
    "canvas": [W, H], "margin": M, "content_width": CW,
    "marks": {
        "top_bar": {"ink_px": INK_TOP, "scale": round(kt, 6),
                    "ink_box": L.ink_box(MARK, ox_t, oy_t, kt),
                    "clearspace_px": round(INK_TOP * CLEAR_RATIO, 2),
                    "variant": "mono on dark (paper)"},
        "hero": {"ink_px": INK_HERO, "scale": round(k, 6),
                 "ink_box": L.ink_box(MARK, ox, oy, k),
                 "clearspace_px": round(INK_HERO * CLEAR_RATIO, 2),
                 "variant": "colour (indigo + cyan), window shows the dark ground"},
        "footer_card": {"ink_px": INK_CARD, "scale": round(kc, 6),
                        "ink_box": L.ink_box(MARK, ox_c, oy_c, kc),
                        "clearspace_px": round(INK_CARD * CLEAR_RATIO, 2),
                        "variant": "mono on dark (paper)"},
    },
    "required_strings": ["2026.11.07 · ONLINE", "OPEN BETA", "layerlight.example.org"],
    "width_estimates": {
        "叠光@132": round(D.est_width("叠光", 132), 1),
        "Layerlight@46": round(D.est_width("Layerlight", 46), 1),
        "tagline@34": round(D.est_width("把复杂信息，组织成清晰画面", 34), 1),
        "url@32": round(D.est_width("layerlight.example.org", 32), 1),
        "date@22": round(D.est_width("2026.11.07 · ONLINE", 22), 1),
    },
}
with open(os.path.join(TMP, "poster-geometry.json"), "w", encoding="utf-8") as fh:
    json.dump(geom, fh, ensure_ascii=False, indent=2)
print(json.dumps(geom["marks"], ensure_ascii=False, indent=1))