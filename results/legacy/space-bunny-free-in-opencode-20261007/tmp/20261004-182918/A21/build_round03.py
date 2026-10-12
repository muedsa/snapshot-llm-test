# -*- coding: utf-8 -*-
"""A21 round-03: light theme on top of round-02.

rounds/round-03.md asks for:
  * switch to a light theme where every piece of normal text reaches at least
    4.5:1 against the *actually composited* background;
  * keep all round-02 copy and the brand graphic (the sponsor in particular);
  * add the English line "Clarity through structure" above the URL, >= 24px;
  * same two sizes, Chinese long title still <= 3 lines and >= 48px;
  * do not fake the theme by recolouring two values - the surfaces, the alpha
    plates, the panel, the chip, the beam and the glow are all recomposed;
  * ship round-03/ with a contrast-audit.json per image carrying at least six
    body-text contrast measurements taken from the final composited pixels.
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
ROUND = "round-03"
OUT = os.path.join(S.OUT_ROOT, TASK, ROUND)
TMP = os.path.join(S.TMP_ROOT, TASK)
snapkit.configure(TASK, OUT, TMP)
REF = "r03"
os.makedirs(OUT, exist_ok=True)

C = B.COPY
TF = B.tokens("light")
SF = TF["surface"]
EN_SIZE = 28
TITLE_SIZE_WIDE = 48

THEME_CHANGES = [
    "page background: #0A0F24->#141034 gradient replaced by #FBFAFF->#EDE9FB",
    "info panel: translucent #FFFFFF0F on dark replaced by solid #FFFFFF with a "
    "violet hairline border #6D4AFF33, so the card now needs its own edge",
    "brand plates: dark-theme alphas (#3A1FB0B3 / #6D4AFF8C) replaced by opaque "
    "light violets (#D7CCFF / #B7A2FF) with stronger borders, because a 70% "
    "alpha plate over a light page would wash out",
    "light beam: #4BE3C8F2 (mint, meant for a dark page) replaced by #0E9E86E6 "
    "so it still reads as light on white",
    "spark: white dot kept (it sits on the violet top plate), ring changed from "
    "mint to #0E9E86",
    "chip: #6D4AFF -> #5B2BE0 and the pill stays white-on-violet",
    "accents: tick/accent ink #7FE9D6 -> #5326E8, muted ink #B7BEE0 -> #4B4478, "
    "body ink #F5F4FF -> #1B1440",
    "aura glow: #6D4AFF59 (additive-looking on dark) -> #6D4AFF33 radial",
    "header rules and panel dividers: #FFFFFF26 -> #6D4AFF3D",
]


def build_portrait():
    W, H = 1080, 1350
    M = 84
    CR = M + (W - 2 * M)
    L = B.Layout(W, H, SF["bg_top"], SF["bg_bottom"], SF)
    bands = {"safe-top": (0, 0, W, 88), "safe-bottom": (0, H - 88, W, H)}

    mk, mk_rects = B.mark(M, 114, 44, SF, glow=False)
    L.mid.extend(mk)
    L.shapes.extend(mk_rects)
    L.text(C["brand_latin"], M + 44 + 16, 126, 24, style="BOLD", ls=2,
           font=B.DISPLAY, role="brand-wordmark", key="p3-wordmark")
    L.chip(C["online"], CR, 114, 24, padx=22, padh=25, style="BOLD", ls=2,
           role="online-launch-chip", key="p3-chip")

    S_M = 320
    mk2, mk2_rects = B.mark(380, 210, S_M, SF)
    L.mid.extend(mk2)
    L.shapes.extend(mk2_rects)

    L.text(C["brand_cjk"], M, 664, 32, style="BOLD", ls=2, font=B.DISPLAY,
           role="brand-kicker", key="p3-kicker-cjk")
    L.text(C["brand_latin"], 169, 664, 32, style="BOLD", ls=2, font=B.DISPLAY,
           role="brand-kicker", key="p3-kicker-latin")

    L.text(C["long_title_a"], M, 720, 52, style="BOLD", ls=0, font=B.DISPLAY,
           role="main-title", key="p3-title-l1")
    L.text(C["long_title_b"], M, 780, 52, style="BOLD", ls=0, font=B.DISPLAY,
           role="main-title", key="p3-title-l2")
    L.rule(M, CR, 878, SF["hairline"], 2)

    CY, CH = 906, 336
    L.rect("mid", M, CY, CR - M, CH, radius=26, color=SF["panel"],
           border="1 SOLID " + SF["panel_border"], _id="info-card")
    L.bar(M, CY, 6, CH, radius=3, color=SF["tick"], _id="card-accent")
    L.bar(M + 40, 946, 4, 28, radius=2, color=SF["tick"], _id="tick-datetime")
    L.text(C["datetime"], M + 64, 946, 28, style="BOLD", ls=0.5,
           color=SF["ink"], role="datetime", key="p3-datetime")
    L.text(C["free"], CR - 40 - 235, 946, 26, ls=1,
           color=SF["accent_ink"], role="free-entry", key="p3-free")
    L.rule(M + 40, CR - 40, 986, SF["hairline"], 2)
    L.bar(M + 40, 1026, 4, 28, radius=2, color=SF["tick"], _id="tick-speakers")
    L.text(C["speakers"], M + 64, 1026, 28, ls=1, color=SF["ink"],
           role="speakers", key="p3-speakers")
    L.text(C["sponsor"], CR - 40 - 378, 1026, 26, ls=0.5,
           color=SF["ink_muted"], role="sponsor", key="p3-sponsor")
    L.rule(M + 40, CR - 40, 1066, SF["hairline"], 2)
    L.bar(M + 40, 1106, 4, EN_SIZE, radius=2, color=SF["accent_ink"],
          _id="tick-clarity-en")
    L.text(C["clarity_en"], M + 64, 1106, EN_SIZE, ls=1,
           color=SF["accent_ink"], role="clarity-en", key="p3-clarity-en")
    L.rule(M + 40, CR - 40, 1146, SF["hairline"], 2)
    L.bar(M + 40, 1176, 4, 26, radius=2, color=SF["accent_ink"], _id="tick-url")
    L.text(C["url"], M + 64, 1176, 26, style="BOLD", ls=0.5,
           color=SF["accent_ink"], role="url", key="p3-url")
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
           font=B.DISPLAY, role="brand-wordmark", key="w3-wordmark")
    L.chip(C["online"], CR, 95, 24, padx=22, padh=25, style="BOLD", ls=2,
           role="online-launch-chip", key="w3-chip")

    S_M = 320
    mk2, mk2_rects = B.mark(940, 246, S_M, SF)
    L.mid.extend(mk2)
    L.shapes.extend(mk2_rects)

    L.text(C["brand_cjk"], M, 170, 32, style="BOLD", ls=2, font=B.DISPLAY,
           role="brand-kicker", key="w3-kicker-cjk")
    L.text(C["brand_latin"], 173, 170, 32, style="BOLD", ls=2, font=B.DISPLAY,
           role="brand-kicker", key="w3-kicker-latin")

    for i, line in enumerate([C["long_title_a"],
                              "\u8ba9\u590d\u6742\u4fe1\u606f\u53d8\u5f97\u6e05\u6670",
                              "\u7684\u7ed3\u6784\u5316\u65b9\u6cd5"]):
        L.text(line, M, 222 + i * 60, TITLE_SIZE_WIDE, style="BOLD", ls=0,
               font=B.DISPLAY, role="main-title", key="w3-title-l%d" % (i + 1))
    L.rule(M, 716, 420, SF["hairline"], 2)
    L.bar(M, 452, 4, 26, radius=2, color=SF["tick"], _id="tick-sponsor")
    L.text(C["sponsor"], M + 24, 452, 26, ls=0.5, color=SF["ink_muted"],
           role="sponsor", key="w3-sponsor")
    L.bar(M, 502, 4, 26, radius=2, color=SF["accent_ink"], _id="tick-free")
    L.text(C["free"], M + 24, 502, 26, ls=1, color=SF["accent_ink"],
           role="free-entry", key="w3-free")
    L.rule(M, CR, 600, SF["hairline"], 2)

    strip = [("w3-datetime", C["datetime"], 28, "BOLD", 0.5, 88, SF["ink"], 676),
             ("w3-speakers", C["speakers"], 28, "NORMAL", 1, 560, SF["ink"], 676),
             ("w3-url", C["url"], 26, "BOLD", 0.5, 968, SF["accent_ink"], 676)]
    for key, txt, size, style, ls, x, col, top in strip:
        L.bar(x, top, 4, size, radius=2,
              color=SF["accent_ink"] if key == "w3-url" else SF["tick"],
              _id="row-tick-%s" % key)
        L.text(txt, x + 28, top, size, style=style, ls=ls, color=col,
               role=key.split("-")[1], key=key)
    # the new English line sits directly above the URL in the same column
    L.bar(968, 630, 4, EN_SIZE, radius=2, color=SF["accent_ink"],
          _id="tick-clarity-en")
    L.text(C["clarity_en"], 996, 630, EN_SIZE, ls=1, color=SF["accent_ink"],
           role="clarity-en", key="w3-clarity-en")
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
        ia["measured_ink_collisions"] = A.pair_collisions(ia["rows"])
        sa = A.check_safe_areas(png, bands, tol=10)
        ca = A.contrast_audit(png, rn["image"], L.texts, threshold=4.5)
        img_meta[name] = {"layout": L, "bands": bands, "ink": ia, "safe": sa,
                          "contrast": ca}
        A.dump(os.path.join(TMP, "audits", "%s-r03-ink.json" % name), ia)
        A.dump(os.path.join(TMP, "audits", "%s-r03-safe.json" % name),
               {"png": name + ".png", "bands": sa})
        A.dump(os.path.join(TMP, "audits", "%s-r03-contrast.json" % name), ca)
        # per-image contrast-audit.json deliverable (task.json also lists one
        # combined file, written below)
        A.dump(os.path.join(OUT, "contrast-audit-%s.json" % name), {
            "image": "%s.png" % name, "size": [L.w, L.h],
            "round": ROUND, "theme": "light",
            "requirement": "rounds/round-03.md: every piece of normal text must "
                           "reach >= 4.5:1 against the actual composited "
                           "background; at least six body-text samples per image",
            "how_background_was_obtained": "the identical composition was "
                                           "rendered a second time with the whole "
                                           "Text layer removed; the background "
                                           "tone under each glyph group is read "
                                           "from those already-composited pixels "
                                           "(page gradient, radial glow, light "
                                           "plates, light beam, panel and chip "
                                           "fill all included - no hand-picked "
                                           "colour and no arithmetic guess)",
            "ratio_definition": "WCAG 2.1 relative luminance contrast, "
                                "(L1+0.05)/(L2+0.05)",
            "threshold": 4.5,
            "worst_contrast": ca["worst_contrast"],
            "all_pass": ca["all_pass"],
            "measured_text_elements": len(ca["rows"]),
            "elements": ca["rows"],
        })

    combined = {
        "round": ROUND, "run_id": RUN, "task_id": TASK,
        "threshold": 4.5, "theme": "light",
        "method": "each image has its own contrast-audit-<name>.json; both come "
                  "from the same procedure: diff-free sampling of a text-free "
                  "render of the identical composition",
        "images": {n: {"file": "contrast-audit-%s.json" % n,
                       "worst_contrast": m["contrast"]["worst_contrast"],
                       "all_pass": m["contrast"]["all_pass"],
                       "elements": len(m["contrast"]["rows"])}
                   for n, m in img_meta.items()},
        "all_pass": all(m["contrast"]["all_pass"] for m in img_meta.values()),
    }
    A.dump(os.path.join(OUT, "contrast-audit.json"), combined)

    tk = B.tokens("light")
    tk["round"] = ROUND
    tk["changed_vs_round_02"] = THEME_CHANGES
    tk["added_in_round_03"] = {
        "clarity-en": {"text": C["clarity_en"], "size": EN_SIZE,
                       "position": "portrait: card row 3, directly above the URL "
                                   "row; wide: bottom strip third column, "
                                   "directly above the URL",
                       "requirement": "English line >= 24px, above the URL"},
    }
    tk["layout_grids"] = {
        "launch-portrait": {"size": [1080, 1350], "margin": 84,
                            "reserved_extension_bands": {"top": [0, 0, 1080, 88],
                                                         "bottom": [0, 1262, 1080, 88]},
                            "composition": "vertical stack: header / hero mark / "
                                           "brand kicker / 2-line title / rule / "
                                           "4-row info card"},
        "launch-wide": {"size": [1440, 810], "margin": 88,
                        "reserved_extension_bands": {"top": [0, 0, 1440, 72],
                                                     "bottom": [0, 738, 1440, 72]},
                        "composition": "two column: kicker + 3-line title + "
                                       "sponsor/free on the left, hero mark on "
                                       "the right, full width fact strip with a "
                                       "two line third column at the bottom"},
    }
    A.dump(os.path.join(OUT, "design-tokens.json"), tk)

    REQUIRED = [
        ("Clarity through structure", "round-03 \u65b0\u589e\u82f1\u8bed\u77ed\u53e5"),
        ("2026.11.07 19:30", "\u4fdd\u7559\u65e5\u671f\u65f6\u95f4"),
        ("ONLINE LAUNCH", "\u4fdd\u7559\u53d1\u5e03\u5f62\u5f0f"),
        ("\u8bb2\u8005\uff1a\u6797\u5ddd / \u82cf\u8a00", "\u4fdd\u7559\u8bb2\u8005"),
        ("layerlight.example.org", "\u4fdd\u7559\u7f51\u5740"),
        ("Northstar Research / \u4e91\u6784\u5de5\u5177", "\u8d5e\u52a9\u65b9\u4e0d\u5f97\u6d88\u5931"),
        ("\u514d\u8d39\u53c2\u52a0 \u00b7 \u65e0\u9700\u62a5\u540d", "\u4fdd\u7559\u53c2\u4e0e\u4fe1\u606f"),
        ("\u5f53\u6240\u6709\u4fe1\u606f\u90fd\u60f3\u6210\u4e3a\u6807\u9898\uff1a"
         "\u8ba9\u590d\u6742\u4fe1\u606f\u53d8\u5f97\u6e05\u6670\u7684\u7ed3\u6784\u5316\u65b9\u6cd5",
         "\u4e2d\u6587\u957f\u6807\u9898\u4e0d\u5f97\u6d88\u5931"),
        ("\u8ba9\u590d\u6742\u4fe1\u606f\u53d8\u5f97\u6e05\u6670", "round-01 \u4e3b\u8bed\uff0c\u5df2\u5e76\u5165\u4e3b\u6807\u9898"),
        ("\u53e0\u5149", "\u54c1\u724c\u540d\u4ecd\u5728\uff08\u9875\u5c3e\u5b57\u6807 + \u5c0f\u6807\uff09"),
        ("Layerlight", "\u54c1\u724c\u540d\u4ecd\u5728"),
    ]
    cm = {"round": ROUND,
          "requirements_source": "tasks/A21-staged-launch-change/rounds/round-03.md",
          "execution_mode": "preloaded_sequential - the round-03 file was read "
                            "only after round-02 was archived",
          "parent_round": "round-02",
          "theme": "light",
          "theme_changes": THEME_CHANGES,
          "brand_components": ["plate-base", "plate-mid", "plate-top", "beam",
                               "spark-dot", "spark-ring"],
          "brand_component_count": 6,
          "brand_geometry_changed": False,
          "images": {}, "required_copy": []}
    for name, meta in img_meta.items():
        L = meta["layout"]
        cm["images"][name] = {
            "size": [L.w, L.h],
            "reserved_extension_bands": {k: list(v) for k, v in meta["bands"].items()},
            "contrast_audit_file": "contrast-audit-%s.json" % name,
            "worst_contrast": meta["contrast"]["worst_contrast"],
            "all_text_pass_4_5_1": meta["contrast"]["all_pass"],
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
            if ids or want in joined:
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
    print("all text >= 4.5:1:", {k: v["contrast"]["all_pass"]
                                 for k, v in img_meta.items()})


if __name__ == "__main__":
    main()