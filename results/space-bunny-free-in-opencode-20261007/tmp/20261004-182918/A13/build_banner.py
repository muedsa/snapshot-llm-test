# -*- coding: utf-8 -*-
"""A13 - brand-banner.png (1200x400).

Left panel carries the mono-on-dark variant of the mark (its window shows the
panel, i.e. the light that comes through the overlap); the right panel carries
the wordmark.  The mark is drawn by layerlight.emit() - the same geometry rules
and the same 4-rect decomposition as the two 512x512 symbols.
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

W, H = 1200, 400
P = L.PALETTE
MARK = L.MARK
CLEAR_RATIO = 1.0 / 9.0          # clearspace = ink / 9 on every side

# ---------------------------------------------------------------- left panel
PANEL_W = 520
kids = [D.box(0, 0, PANEL_W, H, color=None,
              gradient={"gradientType": "LINEAR",
                        "gradientColors": "#3A2FCBFF,#6D5BF5FF",
                        "gradientStops": "0,1",
                        "gradientBegin": "CENTER_LEFT",
                        "gradientEnd": "CENTER_RIGHT"})]
MARK_INK_L = 248.0
ox, oy, k = L.fitted(MARK, PANEL_W / 2.0, H / 2.0, MARK_INK_L)
kids += L.emit(MARK, ox, oy, k, L.MARK_ROLE_COLOR_ON_DARK)

# ---------------------------------------------------------------- right panel
TX = 608                 # text block left
TR = 1112                # text block right
TW = TR - TX
kicker = "结构化视觉工具 · STRUCTURED VISUAL TOOLS"
wordmark = "叠光 Layerlight"
tagline = "把复杂信息，组织成清晰画面"
url = "layerlight.example.org"

kids += [
    D.text_el(kicker, x=TX, y=112, w=TW, h=26, size=17, color=P["faint"],
              ls=1.5, font=D.UI, max_lines=1),
    D.box(TX, 140, 44, 5, color=P["amber"], radius=2.5),
    D.text_el(wordmark, x=TX, y=160, w=TW, h=80, size=56, style="BOLD",
              color=P["ink"], font=D.UI, max_lines=1),
    D.text_el(tagline, x=TX, y=256, w=TW, h=42, size=28, color=P["muted"],
              font=D.CJK, max_lines=1),
    D.hline(TX, TR, 330, P["rule"], 1),
    D.text_el(url, x=TX, y=348, w=TW, h=24, size=17, color=P["faint"],
              font=D.MONO, align="RIGHT", max_lines=1),
]

dsl = D.snapshot([D.stack(kids, W, H)], W, H, bg=P["paper"])
with open(os.path.join(TMP, "drafts", "v11-banner.snapshot"), "w",
          encoding="utf-8", newline="\n") as fh:
    fh.write(dsl)
r = snapkit.render(dsl, "brand-banner.png", "brand-banner.snapshot", final=True)
print("render ok=%s status=%s bytes=%s" % (r.get("ok"), r.get("status"), r.get("bytes")))
if not r.get("ok"):
    print(r.get("error"))
for w in D.warnings():
    print("WARN", w)

geom = {
    "canvas": [W, H],
    "panel_split_x": PANEL_W,
    "mark_ink_px": MARK_INK_L,
    "mark_scale_px_per_grid_unit": round(k, 6),
    "mark_ink_box": L.ink_box(MARK, ox, oy, k),
    "mark_clearspace_px": round(MARK_INK_L * CLEAR_RATIO, 2),
    "mark_left_margin_px": round(L.ink_box(MARK, ox, oy, k)["left"], 2),
    "text_block": {"left": TX, "right": TR, "width": TW},
    "required_strings": {"wordmark": wordmark, "tagline": tagline},
    "measured_width_estimates": {
        "kicker": round(D.est_width(kicker, 17), 1),
        "wordmark": round(D.est_width(wordmark, 56), 1),
        "tagline": round(D.est_width(tagline, 28), 1),
        "url": round(D.est_width(url, 17), 1),
    },
}
with open(os.path.join(TMP, "banner-geometry.json"), "w", encoding="utf-8") as fh:
    json.dump(geom, fh, ensure_ascii=False, indent=2)
print(json.dumps(geom, ensure_ascii=False, indent=1))