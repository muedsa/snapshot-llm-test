# -*- coding: utf-8 -*-
"""A21 round-01: the original brief.

Two launch assets for 叠光 Layerlight, built from one shared kit:
  round-01/launch-portrait.png   1080x1350
  round-01/launch-wide.png      1440x810
Both keep the same primary colour, the same type scale and the same six
component brand mark, but they are composed differently (stacked vs two column).
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
ROUND = "round-01"
OUT = os.path.join(S.OUT_ROOT, TASK, ROUND)
TMP = os.path.join(S.TMP_ROOT, TASK)
snapkit.configure(TASK, OUT, TMP)
REF = "r01"
os.makedirs(TMP, exist_ok=True)

C = B.COPY
TF = B.tokens("dark")
SF = TF["surface"]

REQUIRED = [
    ("\u8ba9\u590d\u6742\u4fe1\u606f\u53d8\u5f97\u6e05\u6670", "TASK.md \u5fc5\u987b\u5305\u542b\u7684\u4e3b\u8bed"),
    ("2026.11.07 19:30", "TASK.md \u5fc5\u987b\u5305\u542b\u7684\u65e5\u671f\u65f6\u95f4"),
    ("ONLINE LAUNCH", "TASK.md \u5fc5\u987b\u5305\u542b\u7684\u53d1\u5e03\u5f62\u5f0f"),
    ("\u8bb2\u8005\uff1a\u6797\u5ddd / \u82cf\u8a00", "TASK.md \u5fc5\u987b\u5305\u542b\u7684\u8bb2\u8005"),
    ("layerlight.example.org", "TASK.md \u5fc5\u987b\u5305\u542b\u7684\u7f51\u5740"),
]


def build_portrait():
    W, H = 1080, 1350
    M = 84
    CR = M + (W - 2 * M)
    L = B.Layout(W, H, SF["bg_top"], SF["bg_bottom"], SF)
    bands = {"safe-top": (0, 0, W, 88), "safe-bottom": (0, H - 88, W, H)}

    # header ---------------------------------------------------------------
    mk, mk_rects = B.mark(M, 114, 44, SF, glow=False)
    L.mid.extend(mk)
    L.shapes.extend(mk_rects)
    L.text(C["brand_latin"], M + 44 + 16, 126, 24, style="BOLD", ls=2,
           font=B.DISPLAY, role="brand-wordmark", key="p-wordmark")
    chip = L.chip(C["online"], CR, 114, 24, padx=22, padh=25, style="BOLD", ls=2,
                  role="online-launch-chip", key="p-chip")

    # hero mark ------------------------------------------------------------
    S_M = 380
    mk2, mk2_rects = B.mark(350, 228, S_M, SF)
    L.mid.extend(mk2)
    L.shapes.extend(mk2_rects)

    # title lockup ---------------------------------------------------------
    L.text(C["brand_cjk"], M, 720, 108, style="BOLD", ls=2, font=B.DISPLAY,
           role="main-title", key="p-title-cjk")
    L.text(C["brand_latin"], 323, 760, 64, style="BOLD", ls=1, font=B.DISPLAY,
           role="main-title", key="p-title-latin")
    L.bar(M, 866, 4, 34, radius=2, color=SF["tick"], _id="tagline-tick")
    L.text(C["tagline"], 112, 866, 36, ls=3, color=SF["ink"],
           role="tagline", key="p-tagline")
    L.rule(M, CR, 950, SF["hairline"], 2)

    # info card ------------------------------------------------------------
    CY, CH = 980, 220
    L.rect("mid", M, CY, CR - M, CH, radius=26, color=SF["panel"],
           border="1 SOLID " + SF["panel_border"], _id="info-card")
    L.bar(M, CY, 6, CH, radius=3, color=SF["tick"], _id="card-accent")
    L.text(C["datetime"], CR - 40 - 237, 1020, 28, style="BOLD", ls=0.5,
           color=SF["ink"], role="datetime", key="p-datetime")
    L.rule(M + 40, CR - 40, 1070, SF["hairline"], 2)
    L.text(C["speakers"], M + 40, 1120, 28, ls=1, color=SF["ink"],
           role="speakers", key="p-speakers")
    L.text(C["url"], CR - 40 - 297, 1120, 26, style="BOLD", ls=0.5,
           color=SF["accent_ink"], role="url", key="p-url")
    return L, bands, chip


def build_wide():
    W, H = 1440, 810
    M = 88
    CR = M + (W - 2 * M)
    L = B.Layout(W, H, SF["bg_top"], SF["bg_bottom"], SF)
    bands = {"safe-top": (0, 0, W, 72), "safe-bottom": (0, H - 72, W, H)}

    # header ---------------------------------------------------------------
    mk, mk_rects = B.mark(M, 96, 44, SF, glow=False)
    L.mid.extend(mk)
    L.shapes.extend(mk_rects)
    L.text(C["brand_latin"], M + 44 + 16, 106, 24, style="BOLD", ls=2,
           font=B.DISPLAY, role="brand-wordmark", key="w-wordmark")
    chip = L.chip(C["online"], CR, 95, 24, padx=22, padh=25, style="BOLD", ls=2,
                  role="online-launch-chip", key="w-chip")

    # right column: the brand mark fills the full height of the banner -------
    S_M = 360
    mk2, mk2_rects = B.mark(900, 240, S_M, SF)
    L.mid.extend(mk2)
    L.shapes.extend(mk2_rects)

    # left column: type ------------------------------------------------------
    L.text(C["brand_cjk"], M, 176, 108, style="BOLD", ls=2, font=B.DISPLAY,
           role="main-title", key="w-title-cjk")
    L.text(C["brand_latin"], 327, 216, 64, style="BOLD", ls=1, font=B.DISPLAY,
           role="main-title", key="w-title-latin")
    L.bar(M, 332, 4, 34, radius=2, color=SF["tick"], _id="tagline-tick")
    L.text(C["tagline"], 116, 332, 36, ls=3, color=SF["ink"],
           role="tagline", key="w-tagline")
    L.rule(M, 716, 424, SF["hairline"], 2)

    # bottom strip: the three facts as a full-width row ----------------------
    L.rule(M, CR, 600, SF["hairline"], 2)
    strip = [("w-datetime", C["datetime"], 28, "BOLD", 0.5, 88, SF["ink"]),
             ("w-speakers", C["speakers"], 28, "NORMAL", 1, 560, SF["ink"]),
             ("w-url", C["url"], 26, "BOLD", 0.5, 1020, SF["accent_ink"])]
    for key, txt, size, style, ls, x, col in strip:
        L.bar(x, 650, 4, size, radius=2,
              color=SF["accent_ink"] if key == "w-url" else SF["tick"],
              _id="row-tick-%s" % key)
        L.text(txt, x + 28, 650, size, style=style, ls=ls, color=col,
               role=key.split("-")[1], key=key)
    return L, bands, chip


def main():
    os.makedirs(OUT, exist_ok=True)
    img_meta = {}
    for name, (builder, size) in {
            "launch-portrait": (build_portrait, (1080, 1350)),
            "launch-wide": (build_wide, (1440, 810))}.items():
        L, bands, chip = builder()
        dsl = L.snapshot_dsl()
        r = snapkit.render(dsl, name + ".png", name + ".snapshot", final=True,
                           out_dir=OUT)
        print("%s render ok=%s status=%s bytes=%s" % (name, r.get("ok"),
                                                     r.get("status"), r.get("bytes")))
        for w in D.warnings():
            print("WARN", name, w)
        if not r.get("ok"):
            raise SystemExit("render failed: %s" % r)
        png = os.path.join(OUT, name + ".png")
        # identical composition without the Text layer: the audit reference
        rn = snapkit.render(L.snapshot_dsl(include_text=False),
                            "%s-notext-%s.png" % (name, REF),
                            "%s-notext-%s.snapshot" % (name, REF),
                            final=False)
        print("%s-notext render ok=%s" % (name, rn.get("ok")))
        if not rn.get("ok"):
            raise SystemExit("reference render failed: %s" % rn)
        png_notext = rn["image"]
        ia = A.ink_audit(png, png_notext, L.texts)
        sa = A.check_safe_areas(png, bands)
        ca = A.contrast_audit(png, png_notext, L.texts)
        ia["measured_ink_collisions"] = A.pair_collisions(ia["rows"])
        img_meta[name] = {"layout": L, "bands": bands, "ink": ia,
                          "safe": sa, "contrast": ca}
        A.dump(os.path.join(TMP, "audits", "%s-ink.json" % name), ia)
        A.dump(os.path.join(TMP, "audits", "%s-safe.json" % name),
               {"png": name + ".png", "bands": sa})
        A.dump(os.path.join(TMP, "audits", "%s-contrast.json" % name), ca)

    # design tokens + content map ------------------------------------------
    tk = B.tokens("dark")
    tk["round"] = ROUND
    tk["layout_grids"] = {
        "launch-portrait": {"size": [1080, 1350], "margin": 84,
                            "reserved_extension_bands": {"top": [0, 0, 1080, 88],
                                                         "bottom": [0, 1262, 1080, 88]},
                            "composition": "vertical stack: header / hero mark / "
                                           "title lockup / tagline / rule / info card"},
        "launch-wide": {"size": [1440, 810], "margin": 88,
                        "reserved_extension_bands": {"top": [0, 0, 1440, 72],
                                                     "bottom": [0, 738, 1440, 72]},
                        "composition": "two column: type + rule-separated fact "
                                       "list on the left, hero mark on the right"},
    }
    A.dump(os.path.join(OUT, "design-tokens.json"), tk)

    cm = {"round": ROUND,
          "requirements_source": "tasks/A21-staged-launch-change/TASK.md",
          "execution_mode": "preloaded_sequential (requirements for round-02/03 "
                            "are readable in the task folder up front; this is "
                            "not blind hidden-feedback testing)",
          "theme": "dark",
          "brand_components": ["plate-base", "plate-mid", "plate-top", "beam",
                               "spark-dot", "spark-ring"],
          "images": {}, "required_copy": []}
    for name, meta in img_meta.items():
        L = meta["layout"]
        present = [t["text"] for t in L.texts]
        cm["images"][name] = {
            "size": [L.w, L.h],
            "reserved_extension_bands": {k: list(v) for k, v in meta["bands"].items()},
            "reserved_band_note": "left intentionally empty: real room for a "
                                  "future partner logo bar (top) and a future "
                                  "ticket QR / footer note (bottom); no "
                                  "placeholder text is written there",
            "elements": [{"id": s["id"], "layer": s.get("layer", s.get("kind")),
                          "rect": s["rect"]}
                         for s in L.shapes] + L.texts,
            "texts": L.texts,
        }
    for want, why in REQUIRED:
        hits = {}
        for name, meta in img_meta.items():
            ids = [t["id"] for t in meta["layout"].texts if t["text"] == want]
            if ids:
                hits[name] = ids
        cm["required_copy"].append({"text": want, "requirement": why,
                                    "present": sorted(hits.keys()), "elements": hits})
    A.dump(os.path.join(OUT, "content-map.json"), cm)

    ok = all(len(v["present"]) == 2 for v in cm["required_copy"])
    print("required copy present in both images:", ok)
    print("ink violations:", {k: v["ink"]["violations"] for k, v in img_meta.items()})
    print("min fontSize:", {k: A.min_fontsize(v["layout"].texts)
                            for k, v in img_meta.items()})
    print("worst contrast:", {k: v["contrast"]["worst_contrast"]
                             for k, v in img_meta.items()})


if __name__ == "__main__":
    main()