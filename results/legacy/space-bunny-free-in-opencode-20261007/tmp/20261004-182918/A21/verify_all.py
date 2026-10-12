# -*- coding: utf-8 -*-
"""Final gate for A21: verify all six delivered images against all three rounds'
requirements, re-running the pixel audits against each round's own text-free
reference render, and checking PNG/DSL pairing.

Run after every render; prints one PASS/FAIL line per check.
"""
import json
import os
import sys
import xml.etree.ElementTree as ET

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
RUN = "20261004-182918"
sys.path.insert(0, os.path.join(ROOT, "tmp", RUN, "_suite"))
sys.path.insert(0, os.path.join(ROOT, "tmp", RUN, "A21"))
import dsllib as D  # noqa: E402
import brandkit as B  # noqa: E402
import audit as A  # noqa: E402
from PIL import Image  # noqa: E402

OUT = os.path.join(ROOT, "outputs", RUN, "A21")
PREV = os.path.join(ROOT, "tmp", RUN, "A21", "preview")
SIZES = {"launch-portrait": (1080, 1350), "launch-wide": (1440, 810)}
MODULES = {"round-01": "build_round01", "round-02": "build_round02",
           "round-03": "build_round03"}
C = B.COPY
TITLE_FULL = C["long_title_a"] + C["long_title_b"]
fails = []


def check(name, ok, detail=""):
    print("%-4s %-62s %s" % ("PASS" if ok else "FAIL", name, detail))
    if not ok:
        fails.append(name)


def main():
    import importlib
    for rnd, modname in MODULES.items():
        mod = importlib.import_module(modname)
        d = os.path.join(OUT, rnd)
        for img, (w, h) in SIZES.items():
            png = os.path.join(d, img + ".png")
            dsl = os.path.join(d, img + ".snapshot")
            check("%s %s PNG exists" % (rnd, img), os.path.exists(png))
            im = Image.open(png)
            check("%s %s size %dx%d" % (rnd, img, w, h), im.size == (w, h),
                  "actual %dx%d" % im.size)
            check("%s %s is PNG" % (rnd, img),
                  open(png, "rb").read(8) == b"\x89PNG\r\n\x1a\n")
            check("%s %s DSL paired" % (rnd, img), os.path.exists(dsl))
            text = open(dsl, encoding="utf-8").read()
            try:
                root = ET.fromstring(text)
                wellformed = root.tag == "Snapshot"
            except ET.ParseError as e:
                wellformed = False
                print("   parse error:", e)
            check("%s %s DSL well-formed, root <Snapshot>" % (rnd, img), wellformed)
            check("%s %s no <Image> tag" % (rnd, img), "<Image" not in text)
            check("%s %s no remote/data URI" % (rnd, img),
                  "http://" not in text and "https://" not in text
                  and "dataUri" not in text)

            built = getattr(mod, "build_" + img.replace("launch-", ""))()
            L = built[0]
            bands = built[1]
            ref = os.path.join(PREV, "%s-notext-r%s.png" % (img, rnd.split("-")[1]))
            check("%s %s text-free reference exists" % (rnd, img),
                  os.path.exists(ref), os.path.basename(ref))
            ia = A.ink_audit(png, ref, L.texts, verbose=False)
            check("%s %s ink containment" % (rnd, img), ia["violations"] == 0,
                  "violations=%d unattributed=%d" %
                  (ia["violations"], ia["unattributed_changed_px"]))
            coll = A.pair_collisions(ia["rows"], verbose=False)
            check("%s %s no text-on-text collision" % (rnd, img), not coll,
                  "collisions=%d" % len(coll))
            sa = A.check_safe_areas(png, bands)
            check("%s %s reserved bands empty" % (rnd, img),
                  all(s["empty"] for s in sa))
            ca = A.contrast_audit(png, ref, L.texts, verbose=False)
            check("%s %s all text >= 4.5:1" % (rnd, img), ca["all_pass"],
                  "worst=%.2f:1 over %d elements" %
                  (ca["worst_contrast"], len(ca["rows"])))
            texts = [t["text"] for t in L.texts]
            joined_title = "".join(t["text"] for t in L.texts
                                  if t["role"] == "main-title")
            minsize = A.min_fontsize(L.texts)
            main_sizes = [t["fontSize"] for t in L.texts
                          if t["role"] == "main-title"]
            title_lines = len([t for t in L.texts if t["role"] == "main-title"])
            if rnd == "round-01":
                check("%s %s main title >= 56" % (rnd, img), min(main_sizes) >= 56,
                      str(main_sizes))
                check("%s %s tagline present" % (rnd, img), C["tagline"] in texts)
            else:
                check("%s %s title >= 48" % (rnd, img), min(main_sizes) >= 48,
                      str(main_sizes))
                check("%s %s title lines <= 3" % (rnd, img), title_lines <= 3,
                      "lines=%d" % title_lines)
                check("%s %s title text intact" % (rnd, img),
                      joined_title == TITLE_FULL)
                check("%s %s sponsor present" % (rnd, img),
                      C["sponsor"] in texts)
                check("%s %s free-entry present" % (rnd, img), C["free"] in texts)
            if rnd == "round-03":
                check("%s %s english line present" % (rnd, img),
                      C["clarity_en"] in texts)
                esize = [t["fontSize"] for t in L.texts
                         if t["text"] == C["clarity_en"]][0]
                check("%s %s english line >= 24" % (rnd, img), esize >= 24,
                      "%dpx" % esize)
                ca_file = os.path.join(d, "contrast-audit-%s.json" % img)
                check("%s %s contrast-audit file exists" % (rnd, img),
                      os.path.exists(ca_file))
                if os.path.exists(ca_file):
                    aj = json.load(open(ca_file, encoding="utf-8"))
                    check("%s %s contrast-audit >= 6 samples" % (rnd, img),
                          len(aj["elements"]) >= 6,
                          "%d samples" % len(aj["elements"]))
            for need in (C["datetime"], C["online"], C["speakers"], C["url"]):
                check("%s %s contains %r" % (rnd, img, need), need in texts)
            check("%s %s smallest font >= 24" % (rnd, img), minsize >= 24,
                  "%dpx" % minsize)
            check("%s %s brand mark has 6 components" % (rnd, img),
                  len([s for s in L.shapes if s.get("kind") == "mark-component"
                       or s.get("id") in ("plate-base", "plate-mid", "plate-top",
                                          "beam", "spark-dot", "spark-ring")]) >= 6)
    print("\n%d checks failed" % len(fails))
    for f in fails:
        print("  FAILED:", f)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())