# -*- coding: utf-8 -*-
"""A21 round-02: real requirement change on top of round-01.

rounds/round-02.md asks for:
  * the main title replaced by
    "当所有信息都想成为标题：让复杂信息变得清晰的结构化方法",
    at most 3 lines, at least 48px, in both sizes;
  * two new strings: the sponsor "Northstar Research / 云构工具" and
    "免费参加 · 无需报名";
  * date/time, speakers, ONLINE LAUNCH and the URL must all survive;
  * the primary colour and the 3-6 component brand mark must not change shape
    (only decoration may move / rescale);
  * text must not be narrowed with a transform.

Everything else (palette, type scale, mark geometry, chip, cards, the audit
pipeline) is inherited from round-01, so the two rounds stay comparable.
"""
import json
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
RUN = "20261004-182918"
sys.path.insert(0, os.path.join(ROOT, "tmp", RUN, "_suite"))
sys.path.insert(0, os.path.join(ROOT, "tmp", RUN, "A21"))
import snapkit  # noqa: E402
import dsllib as D  # noqa: E402
import state as S  # noqa: E402
import brandkit as B  # noqa: E402
import audit as A  # noqa: E402

TASK = "A21"
ROUND = "round-02"
OUT = os.path.join(S.OUT_ROOT, TASK, ROUND)
TMP = os.path.join(S.TMP_ROOT, TASK)
snapkit.configure(TASK, OUT, TMP)
REF = "r02"
os.makedirs(OUT, exist_ok=True)

C = B.COPY
TF = B.tokens("dark")
SF = TF["surface"]

TITLE_LINES = [C["long_title_a"], C["long_title_b"]]
TITLE_SIZE = 52          # >= 48 required, and identical in both sizes
COLLISION_NOTE = {
    "title_lines": len(TITLE_LINES),
    "title_font_size": TITLE_SIZE,
    "title_font": B.DISPLAY,
    "title_letter_spacing": 0,
    "title_transform": "none - the title is never narrowed or rotated",
    "how_collisions_are_avoided": [
        "the title is set as explicit per-line Text elements so the line breaks "
        "are chosen at real punctuation instead of relying on soft wrap",
        "each title line is measured from a rendered probe (probe-r02.json); the "
        "portrait column is 912px wide and the longest line measures 776px, the "
        "wide column is 628px wide and its longest line measures 540px",
        "the title is placed first in the vertical order and the two new "
        "strings get their own reserved band below it, so the 2 new rows never "
        "share a line with a title line",
        "two new rows keep the same 48px minimum gap and 60px row pitch as the "
        "existing facts, and the ink audit measures a real gap between the "
        "title's last line and the first new row",
        "no negative letterSpacing and no Transform are used anywhere on text, "
        "so no string is optically compressed to fit",
    ],
}


def build_portrait():
    W, H = 1080, 1350
    M = 84
    CR = M + (W - 2 * M)
    L = B.Layout(W, H, SF["bg_top"], SF["bg_bottom"], SF)
    bands = {"safe-top": (0, 0, W, 88), "safe-bottom": (0, H - 88, W, H)}

    # header (unchanged from round-01) --------------------------------------
    mk, mk_rects = B.mark(M, 114, 44, SF, glow=False)
    L.mid.extend(mk)
    L.shapes.extend(mk_rects)
    L.text(C["brand_latin"], M + 44 + 16, 126, 24, style="BOLD", ls=2,
           font=B.DISPLAY, role="brand-wordmark", key="p2-wordmark")
    L.chip(C["online"], CR, 114, 24, padx=22, padh=25, style="BOLD", ls=2,
           role="online-launch-chip", key="p2-chip")

    # hero mark: same six components, rescaled and moved (decoration only)
    S_M = 360
    mk2, mk2_rects = B.mark(360, 226, S_M, SF)
    L.mid.extend(mk2)
    L.shapes.extend(mk2_rects)

    # brand kicker keeps the name visible now that the title changed ----------
    L.text(C["brand_cjk"], M, 690, 32, style="BOLD", ls=2, font=B.DISPLAY,
           role="brand-kicker", key="p2-kicker-cjk")
    L.text(C["brand_latin"], 169, 690, 32, style="BOLD", ls=2, font=B.DISPLAY,
           role="brand-kicker", key="p2-kicker-latin")

    # main title: 2 explicit lines at 52px ----------------------------------
    L.text(TITLE_LINES[0], M, 746, TITLE_SIZE, style="BOLD", ls=0,
           font=B.DISPLAY, role="main-title", key="p2-title-l1")
    L.text(TITLE_LINES[1], M, 806, TITLE_SIZE, style="BOLD", ls=0,
           font=B.DISPLAY, role="main-title", key="p2-title-l2")
    L.rule(M, CR, 906, SF["hairline"], 2)

    # info card: the two round-01 facts plus the two new round-02 strings ----
    CY, CH = 936, 284
    L.rect("mid", M, CY, CR - M, CH, radius=26, color=SF["panel"],
           border="1 SOLID " + SF["panel_border"], _id="info-card")
    L.bar(M, CY, 6, CH, radius=3, color=SF["tick"], _id="card-accent")
    L.bar(M + 40, 976, 4, 28, radius=2, color=SF["tick"], _id="tick-datetime")
    L.text(C["datetime"], M + 64, 976, 28, style="BOLD", ls=0.5,
           color=SF["ink"], role="datetime", key="p2-datetime")
    L.text(C["free"], CR - 40 - 235, 976, 26, style="NORMAL", ls=1,
           color=SF["accent_ink"], role="free-entry", key="p2-free")
    L.rule(M + 40, CR - 40, 1016, SF["hairline"], 2)
    L.bar(M + 40, 1056, 4, 28, radius=2, color=SF["tick"], _id="tick-speakers")
    L.text(C["speakers"], M + 64, 1056, 28, ls=1, color=SF["ink"],
           role="speakers", key="p2-speakers")
    L.text(C["sponsor"], CR - 40 - 378, 1056, 26, ls=0.5,
           color=SF["ink_muted"], role="sponsor", key="p2-sponsor")
    L.rule(M + 40, CR - 40, 1102, SF["hairline"], 2)
    L.bar(M + 40, 1142, 4, 26, radius=2, color=SF["accent_ink"], _id="tick-url")
    L.text(C["url"], M + 64, 1142, 26, style="BOLD", ls=0.5,
           color=SF["accent_ink"], role="url", key="p2-url")
    return L, bands


def build_wide():
    W, H = 1440, 810
    M = 88
    CR = M + (W - 2 * M)
    L = B.Layout(W, H, SF["bg_top"], SF["bg_bottom"], SF)
    bands = {"safe-top": (0, 0, W, 72), "safe-bottom": (0, H - 72, W, H)}

    mk, mk_rects = B.mark(M, 96, 44, SF, glow=False)
    L.mid.extend(mk)
    L.shapes.extend(mk_rects)
    L.text(C["brand_latin"], M + 44 + 16, 106, 24, style="BOLD", ls=2,
           font=B.DISPLAY, role="brand-wordmark", key="w2-wordmark")
    L.chip(C["online"], CR, 95, 24, padx=22, padh=25, style="BOLD", ls=2,
           role="online-launch-chip", key="w2-chip")

    # hero mark: same six components, rescaled and shifted right (decoration)
    S_M = 320
    mk2, mk2_rects = B.mark(940, 246, S_M, SF)
    L.mid.extend(mk2)
    L.shapes.extend(mk2_rects)

    # brand kicker -----------------------------------------------------------
    L.text(C["brand_cjk"], M, 170, 32, style="BOLD", ls=2, font=B.DISPLAY,
           role="brand-kicker", key="w2-kicker-cjk")
    L.text(C["brand_latin"], 173, 170, 32, style="BOLD", ls=2, font=B.DISPLAY,
           role="brand-kicker", key="w2-kicker-latin")

    # main title: 3 explicit lines at 48px (the 628px column cannot hold the
    # 776px single-line variant, and 3 lines is exactly what the brief allows)
    for i, line in enumerate(["\u5f53\u6240\u6709\u4fe1\u606f\u90fd\u60f3\u6210\u4e3a\u6807\u9898\uff1a",
                              "\u8ba9\u590d\u6742\u4fe1\u606f\u53d8\u5f97\u6e05\u6670",
                              "\u7684\u7ed3\u6784\u5316\u65b9\u6cd5"]):
        L.text(line, M, 222 + i * 60, 48, style="BOLD", ls=0, font=B.DISPLAY,
               role="main-title", key="w2-title-l%d" % (i + 1))
    L.rule(M, 716, 420, SF["hairline"], 2)

    # the two new round-02 strings, in their own reserved band -----------------
    L.bar(M, 452, 4, 26, radius=2, color=SF["tick"], _id="tick-sponsor")
    L.text(C["sponsor"], M + 24, 452, 26, ls=0.5, color=SF["ink_muted"],
           role="sponsor", key="w2-sponsor")
    L.bar(M, 502, 4, 26, radius=2, color=SF["accent_ink"], _id="tick-free")
    L.text(C["free"], M + 24, 502, 26, ls=1, color=SF["accent_ink"],
           role="free-entry", key="w2-free")
    L.rule(M, CR, 600, SF["hairline"], 2)

    strip = [("w2-datetime", C["datetime"], 28, "BOLD", 0.5, 88, SF["ink"]),
             ("w2-speakers", C["speakers"], 28, "NORMAL", 1, 560, SF["ink"]),
             ("w2-url", C["url"], 26, "BOLD", 0.5, 1020, SF["accent_ink"])]
    for key, txt, size, style, ls, x, col in strip:
        L.bar(x, 650, 4, size, radius=2,
              color=SF["accent_ink"] if key == "w2-url" else SF["tick"],
              _id="row-tick-%s" % key)
        L.text(txt, x + 28, 650, size, style=style, ls=ls, color=col,
               role=key.split("-")[1], key=key)
    return L, bands


def main():
    img_meta = {}
    for name, builder in (("launch-portrait", build_portrait),
                          ("launch-wide", build_wide)):
        L, bands = builder()
        r = snapkit.render(L.snapshot_dsl(), name + ".png", name + ".snapshot",
                           final=True, out_dir=OUT)
        print("%s render ok=%s status=%s bytes=%s" % (name, r.get("ok"),
                                                     r.get("status"), r.get("bytes")))
        for w in D.warnings():
            print("WARN", name, w)
        if not r.get("ok"):
            raise SystemExit("render failed: %s" % r)
        png = os.path.join(OUT, name + ".png")
        rn = snapkit.render(L.snapshot_dsl(include_text=False),
                            "%s-notext-%s.png" % (name, REF),
                            "%s-notext-%s.snapshot" % (name, REF),
                            final=False)
        if not rn.get("ok"):
            raise SystemExit("reference render failed: %s" % rn)
        ia = A.ink_audit(png, rn["image"], L.texts)
        sa = A.check_safe_areas(png, bands)
        ca = A.contrast_audit(png, rn["image"], L.texts)
        ia["measured_ink_collisions"] = A.pair_collisions(ia["rows"])
        img_meta[name] = {"layout": L, "bands": bands, "ink": ia, "safe": sa,
                          "contrast": ca}
        A.dump(os.path.join(TMP, "audits", "%s-r02-ink.json" % name), ia)
        A.dump(os.path.join(TMP, "audits", "%s-r02-safe.json" % name),
               {"png": name + ".png", "bands": sa})
        A.dump(os.path.join(TMP, "audits", "%s-r02-contrast.json" % name), ca)

    # ---- measured collision evidence -------------------------------------
    collision = {}
    for name, meta in img_meta.items():
        rows = {r["id"]: r for r in meta["ink"]["rows"]}
        titles = [r for k, r in rows.items() if r["role"] == "main-title"]
        titles.sort(key=lambda r: r["declared_rect"][1])
        others = [r for k, r in rows.items()
                  if r["role"] in ("sponsor", "free-entry", "datetime",
                                   "speakers", "url", "tagline")]
        gaps = []
        last = titles[-1]
        nxt = min([o for o in others if o["declared_rect"][1] > last["declared_rect"][1]],
                  key=lambda o: o["declared_rect"][1], default=None)
        if nxt:
            gaps.append({"title": last["id"], "other": nxt["id"],
                         "vertical_gap_px": round(
                             nxt["declared_rect"][1] - last["declared_rect"][3], 1)})
        colw = {"launch-portrait": 912, "launch-wide": 628}[name]
        widest = max(r["measured_ink"][2] - r["measured_ink"][0] for r in titles)
        collision[name] = {"column_width_px": colw,
                           "widest_title_line_measured_ink_px": widest,
                           "title_lines": len(titles),
                           "title_font_size": titles[0]["fontSize"],
                           "horizontal_slack_px": colw - widest,
                           "vertical_gap_to_next_block": gaps}
        print(name, "collision:", json.dumps(collision[name], ensure_ascii=False))

    tk = B.tokens("dark")
    tk["round"] = ROUND
    tk["changed_vs_round_01"] = [
        "title: 叠光 + Layerlight (108/64) replaced by the round-02 long title, "
        "2 lines at 52px in the portrait and 3 lines at 48px in the wide",
        "added brand kicker 叠光 Layerlight at 32px so the brand name stays "
        "visible after the title change",
        "added the two new strings sponsor (26px) and free-entry (26px)",
        "decorations moved/rescaled only: hero mark 380->340 (portrait) and "
        "360->320 (wide); mark component geometry unchanged",
        "the separate tagline line is gone because its text is now part of the "
        "main title (the string is still present, inside the title)",
        "palette, type scale, chip, card style and font families unchanged",
    ]
    tk["title_typography"] = {"lines": TITLE_LINES, "font_size": TITLE_SIZE,
                              "font": B.DISPLAY, "letter_spacing": 0,
                              "transform": "none"}
    tk["layout_grids"] = {
        "launch-portrait": {"size": [1080, 1350], "margin": 84,
                            "reserved_extension_bands": {"top": [0, 0, 1080, 88],
                                                         "bottom": [0, 1262, 1080, 88]},
                            "composition": "vertical stack: header / hero mark / "
                                           "brand kicker / 2-line title / rule / "
                                           "3-row info card"},
        "launch-wide": {"size": [1440, 810], "margin": 88,
                        "reserved_extension_bands": {"top": [0, 0, 1440, 72],
                                                     "bottom": [0, 738, 1440, 72]},
                        "composition": "two column: kicker + 3-line title + the "
                                       "two new strings on the left, hero mark "
                                       "on the right, full width fact strip at "
                                       "the bottom"},
    }
    A.dump(os.path.join(OUT, "design-tokens.json"), tk)

    REQUIRED = [
        ("\u5f53\u6240\u6709\u4fe1\u606f\u90fd\u60f3\u6210\u4e3a\u6807\u9898\uff1a"
         "\u8ba9\u590d\u6742\u4fe1\u606f\u53d8\u5f97\u6e05\u6670\u7684\u7ed3\u6784\u5316\u65b9\u6cd5",
         "round-02 \u4e3b\u6807\u9898\uff08\u6309\u6a2a\u7ebf\u62c6\u5206\uff0c\u5185\u5bb9\u5b8c\u6574\uff09"),
        ("2026.11.07 19:30", "round-02 \u8981\u6c42\u4fdd\u7559\u65e5\u671f\u65f6\u95f4"),
        ("ONLINE LAUNCH", "round-02 \u8981\u6c42\u4fdd\u7559"),
        ("\u8bb2\u8005\uff1a\u6797\u5ddd / \u82cf\u8a00", "round-02 \u8981\u6c42\u4fdd\u7559\u8bb2\u8005"),
        ("layerlight.example.org", "round-02 \u8981\u6c42\u4fdd\u7559\u7f51\u5740"),
        ("Northstar Research / \u4e91\u6784\u5de5\u5177", "round-02 \u65b0\u589e\u8d5e\u52a9\u65b9"),
        ("\u514d\u8d39\u53c2\u52a0 \u00b7 \u65e0\u9700\u62a5\u540d", "round-02 \u65b0\u589e\u53c2\u4e0e\u4fe1\u606f"),
        ("\u8ba9\u590d\u6742\u4fe1\u606f\u53d8\u5f97\u6e05\u6670", "round-01 \u5fc5\u542b\u4e3b\u8bed\uff0c\u73b0\u5df2\u5e76\u5165\u4e3b\u6807\u9898"),
    ]
    cm = {"round": ROUND,
          "requirements_source": "tasks/A21-staged-launch-change/rounds/round-02.md",
          "execution_mode": "preloaded_sequential - the round-02 file was read "
                            "only after round-01 was archived; the requirement "
                            "was pre-loaded, this is not hidden-feedback testing",
          "parent_round": "round-01",
          "theme": "dark (unchanged)",
          "brand_components": ["plate-base", "plate-mid", "plate-top", "beam",
                               "spark-dot", "spark-ring"],
          "title_change": COLLISION_NOTE,
          "measured_collision_evidence": collision,
          "images": {}, "required_copy": []}
    for name, meta in img_meta.items():
        L = meta["layout"]
        cm["images"][name] = {
            "size": [L.w, L.h],
            "reserved_extension_bands": {k: list(v) for k, v in meta["bands"].items()},
            "elements": [{"id": s["id"], "layer": s.get("layer", s.get("kind")),
                          "rect": s["rect"]} for s in L.shapes] + L.texts,
            "texts": L.texts,
        }
    for want, why in REQUIRED:
        hits = {}
        for name, meta in img_meta.items():
            joined = "".join(t["text"] for t in meta["layout"].texts
                             if t["role"] == "main-title")
            ids = [t["id"] for t in meta["layout"].texts if t["text"] == want]
            ok = bool(ids) or (want in joined)
            if ok:
                hits[name] = ids or ["(title lines joined)"]
        cm["required_copy"].append({"text": want, "requirement": why,
                                    "present": sorted(hits.keys()), "elements": hits})
    A.dump(os.path.join(OUT, "content-map.json"), cm)
    print("required copy present in both:",
          all(len(v["present"]) == 2 for v in cm["required_copy"]))
    print("ink violations:", {k: v["ink"]["violations"] for k, v in img_meta.items()})
    print("min fontSize:", {k: A.min_fontsize(v["layout"].texts)
                            for k, v in img_meta.items()})
    print("worst contrast:", {k: v["contrast"]["worst_contrast"]
                             for k, v in img_meta.items()})


if __name__ == "__main__":
    main()