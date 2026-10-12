"""Probe 2: exact advance widths, glyph band heights, and the minimum Text box height.

Probe 1 showed the shared dsllib estimator is conservative for Inter/Noto CJK but
UNDER-estimates DejaVu Sans Mono by up to 7%, which is what silently wrapped and
truncated the meta values and ghost numerals. This probe measures, from real
service responses:
  * advance width per character for long mono strings (side bearings removed)
  * ink band top/bottom for a rendered line, to validate the glyph-band model
  * the smallest box height at which a line still renders (truncation threshold)
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np
from PIL import Image

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
import snapkit  # noqa: E402
import dsllib as D  # noqa: E402
import state as S  # noqa: E402

OUT = os.path.join(S.OUT_ROOT, "A12")
TMP = os.path.join(S.TMP_ROOT, "A12")
PROBE = os.path.join(TMP, "probe2")
os.makedirs(PROBE, exist_ok=True)
snapkit.configure("A12", OUT, TMP)

BG, INK, PAD = "#FFFFFFFF", "#000000FF", 60


def render_and_measure(name, kids, w, h):
    dsl = D.snapshot([D.stack(kids, w, h)], w, h, bg=BG)
    with open(os.path.join(PROBE, name + ".snapshot"), "w", encoding="utf-8",
              newline="\n") as fh:
        fh.write(dsl)
    r = snapkit.render(dsl, name + ".png", name + ".snapshot", final=False,
                       out_dir=PROBE)
    if not r.get("ok"):
        return {"error": (r.get("error") or "")[:200]}
    a = np.array(Image.open(r["image"]).convert("L"))
    ink = np.where(a < 128)
    if len(ink[0]) == 0:
        return {"blank": True}
    return {"x0": int(ink[1].min()), "x1": int(ink[1].max()),
            "y0": int(ink[0].min()), "y1": int(ink[0].max())}


out = {"advance": [], "band": [], "minheight": []}

# ---- 1. advance width, long strings so side bearings are negligible --------
LONG = [
    ("mono_zeros20", "00000000000000000000", D.MONO),
    ("mono_m20", "mmmmmmmmmmmmmmmmmmmm", D.MONO),
    ("mono_site22", "structure.example.org", D.MONO),
    ("mono_date10", "2026.11.07", D.MONO),
    ("mono_time11", "09:00–16:00", D.MONO),
    ("mono_ghost", "01", D.MONO),
    ("ui_cjk20", "让模型从读懂文档到完成作品让模型", D.UI),
    ("ui_detail", "图片、DSL与过程留痕", D.UI),
    ("ui_cta", "免费参加 · 扫码方式详见官网", D.UI),
    ("ui_loc", "云构中心 · ONLINE", D.UI),
    ("inter_title", "Structure / Vision", D.LATIN),
]
for key, s, fam in LONG:
    n = len(s)
    for fs in (100,):
        w = int(n * fs * 1.4) + 2 * PAD
        h = int(fs * 2.0)
        m = render_and_measure("adv-%s-%d" % (key, fs),
                               [D.box(0, 0, w, h, color=BG),
                                D.text_el(s, x=PAD, y=40, w=w - 2 * PAD,
                                          h=fs * 1.55, size=fs, color=INK, font=fam)],
                               w, h)
        if "error" in m or m.get("blank"):
            out["advance"].append({"key": key, "chars": n, "size": fs, **m})
            print(key, m)
            continue
        adv = (m["x1"] - m["x0"] + 1) / float(fs)
        out["advance"].append({"key": key, "text": s, "chars": n, "font": fam,
                               "size": fs, "ink_em": round(adv, 4),
                               "em_per_char": round(adv / n, 4),
                               "dsllib_naive_em_per_char":
                                   round(D.est_width(s, fs) / fs / n, 4)})
        print("%-14s n=%2d ink=%.3fem  per_char=%.4f  naive=%.4f  ratio=%.3f"
              % (key, n, adv, adv / n, D.est_width(s, fs) / fs / n,
                 adv / n / (D.est_width(s, fs) / fs / n)))

# ---- 2. glyph band: where do the glyphs actually land inside the box? ------
for fs in (16, 20, 26, 32, 48, 64, 96):
    s = "让模型从读懂文档到完成作品Ag1"
    w = int(D.est_width(s, fs) * 1.6) + 2 * PAD
    h = int(fs * 2.2)
    boxtop = 40
    m = render_and_measure("band-%d" % fs,
                           [D.box(0, 0, w, h, color=BG),
                            D.box(PAD - 6, boxtop - 1, w - 2 * PAD + 12, 1,
                                  color="#FF0000FF"),
                            D.text_el(s, x=PAD, y=boxtop, w=w - 2 * PAD,
                                      h=fs * 1.55, size=fs, color=INK, font=D.UI)],
                           w, h)
    if "error" in m or m.get("blank"):
        out["band"].append({"size": fs, **m})
        print("band", fs, m)
        continue
    rec = {"size": fs, "box_top": boxtop, "box_h": round(fs * 1.55, 2),
           "ink_y0": m["y0"], "ink_y1": m["y1"],
           "glyph_top_from_box_top": m["y0"] - boxtop,
           "glyph_h": m["y1"] - m["y0"] + 1,
           "glyph_h_over_size": round((m["y1"] - m["y0"] + 1) / fs, 4)}
    out["band"].append(rec)
    print("band fs=%2d  glyph_top=%.1f (%.3f em)  glyph_h=%.1f (%.3f em)"
          % (fs, rec["glyph_top_from_box_top"],
             rec["glyph_top_from_box_top"] / fs, rec["glyph_h"],
             rec["glyph_h_over_size"]))

# ---- 3. minimum box height before a single line is silently dropped --------
s = "让模型从读懂文档到完成作品"
for ratio in (1.00, 1.10, 1.18, 1.25, 1.35, 1.45, 1.55, 1.70):
    fs = 40
    w = int(D.est_width(s, fs) * 1.6) + 2 * PAD
    hh = int(fs * ratio)
    m = render_and_measure("minh-%d" % int(ratio * 100),
                           [D.box(0, 0, w, 120, color=BG),
                            D.text_el(s, x=PAD, y=40, w=w - 2 * PAD, h=hh,
                                      size=fs, color=INK, font=D.UI)],
                           w, 120)
    ok = "error" not in m and not m.get("blank")
    out["minheight"].append({"height_ratio": ratio, "height_px": hh,
                             "renders": bool(ok), "detail": m})
    print("minh ratio=%.2f h=%3d renders=%s" % (ratio, hh, ok))

with open(os.path.join(TMP, "font-metrics-2.json"), "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=2)
print("\nsaved", os.path.join(TMP, "font-metrics-2.json"))
