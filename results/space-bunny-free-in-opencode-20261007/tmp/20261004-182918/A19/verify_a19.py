"""A19 verify: independently re-derive every answer from the DELIVERED scene-data.json,
re-check every TASK.md constraint, and re-check the pixel-equality proof.

Nothing here imports the generator's in-memory state: it reads the JSON files that
were actually written into outputs/<run>/A19/ and recomputes from those.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
RUN = "20261004-182918"
TASK = "A19"
OUT = os.path.join(ROOT, "outputs", RUN, TASK)
TMP = os.path.join(ROOT, "tmp", RUN, TASK)

CHECKS = []


def ck(name, ok, detail=""):
    CHECKS.append({"check": name, "pass": bool(ok), "detail": detail})
    print("%-4s %-58s %s" % ("PASS" if ok else "FAIL", name, detail))
    return ok


def load(n):
    with open(os.path.join(OUT, n), encoding="utf-8") as fh:
        return json.load(fh)


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        h.update(fh.read())
    return h.hexdigest()


def main():
    from PIL import Image, ImageChops

    scene = load("scene-data.json")
    occ = load("occlusion-scene-data.json")
    qs = load("questions.json")
    ans = load("answers.json")
    eq = load("equivalence.json")
    objs = scene["objects"]
    by = {o["id"]: o for o in objs}

    print("=== 1. delivered files ===")
    for n in ("grid-scene.png", "grid-scene.snapshot", "occlusion.png",
              "occlusion.snapshot", "occlusion-alternative.png",
              "occlusion-alternative.snapshot", "scene-data.json", "questions.json",
              "answers.json", "equivalence.json"):
        ck("file exists: " + n, os.path.exists(os.path.join(OUT, n)))

    print("\n=== 2. PNG dimensions & pairing ===")
    g = Image.open(os.path.join(OUT, "grid-scene.png"))
    ck("grid-scene.png is 1600x1600", g.size == (1600, 1600), str(g.size))
    for n, dsl in (("grid-scene", "grid-scene.snapshot"),
                   ("occlusion", "occlusion.snapshot"),
                   ("occlusion-alternative", "occlusion-alternative.snapshot")):
        im = Image.open(os.path.join(OUT, n + ".png"))
        ck("%s.png size" % n, im.size == ((1600, 1600) if n == "grid-scene" else (800, 800)),
           str(im.size))
        d = open(os.path.join(OUT, dsl), encoding="utf-8").read()
        ck("%s.snapshot declares %dx%d" % (n, *im.size),
           ('width="%d"' % im.size[0]) in d and ('height="%d"' % im.size[1]) in d)
        ck("%s.snapshot has no <Image>" % n, "<Image" not in d and "dataUri" not in d)
        ck("%s.snapshot root is Snapshot" % n, d.strip().startswith("<Snapshot"))

    print("\n=== 3. grid constraints (re-checked from scene-data.json) ===")
    ck("64 objects", len(objs) == 64, str(len(objs)))
    ck("ids G01..G64 row-major",
       [o["id"] for o in objs] == ["G%02d" % (i + 1) for i in range(64)])
    cc = {}
    cs = {}
    cz = {}
    for o in objs:
        cc[o["color"]] = cc.get(o["color"], 0) + 1
        cs[o["shape"]] = cs.get(o["shape"], 0) + 1
        cz[str(o["size"])] = cz.get(str(o["size"]), 0) + 1
    ck("4 colors", sorted(cc) == ["blue", "green", "orange", "purple"], str(cc))
    ck("each color == 16", all(v == 16 for v in cc.values()), str(cc))
    ck("4 shapes", sorted(cs) == ["circle", "ring", "rounded_square", "square"], str(cs))
    ck("each shape == 16", all(v == 16 for v in cs.values()), str(cs))
    ck("3 sizes 48/64/80", sorted(cz) == ["48", "64", "80"], str(cz))
    ck("seed recorded", scene["seed"] == 20261004, str(scene.get("seed")))
    r_ok_c = r_ok_s = True
    for r in range(8):
        row = objs[r * 8:r * 8 + 8]
        r_ok_c &= len({o["color"] for o in row}) >= 3
        r_ok_s &= len({o["shape"] for o in row}) >= 3
    ck("every row has >=3 colors", r_ok_c)
    ck("every row has >=3 shapes", r_ok_s)
    ck("scene-data row_distribution agrees",
       all(len(r["distinct_colors"]) >= 3 and len(r["distinct_shapes"]) >= 3
           for r in scene["row_distribution"]))

    # geometry: one body per cell, ring rule, label outside body
    cells = set()
    geom_ok = ring_ok = lbl_ok = True
    for o in objs:
        cells.add((o["row"], o["col"]))
        cb, bb, lb = o["cell_bbox"], o["bbox"], o["id_label"]["bbox"]
        if not (cb["x_min"] <= bb["x_min"] and bb["x_max"] <= cb["x_max"]
                and cb["y_min"] <= bb["y_min"] and bb["y_max"] <= cb["y_max"]):
            geom_ok = False
        if abs(bb["x_max"] - bb["x_min"] - o["size"]) > 1e-9 or \
           abs(bb["y_max"] - bb["y_min"] - o["size"]) > 1e-9:
            geom_ok = False
        if lb["y_min"] < bb["y_max"]:
            lbl_ok = False
        if o["shape"] == "ring":
            gm = o["geometry"]
            if not (abs(gm["outer_diameter"] - o["size"]) < 1e-9
                    and abs(gm["inner_diameter"] - o["size"] / 2.0) < 1e-9):
                ring_ok = False
    ck("one body per cell, 64 distinct cells", len(cells) == 64 and geom_ok)
    ck("ring outer==size and inner==size/2", ring_ok)
    ck("every id label is outside its body", lbl_ok)

    print("\n=== 4. geometry re-derived from the rendered DSL ===")
    import re
    dsl = open(os.path.join(OUT, "grid-scene.snapshot"), encoding="utf-8").read()
    ck("exactly 64 cell backgrounds (190x172 rounded white rects)",
       dsl.count('<Container color="#FFFFFF" borderRadius="10.0" '
                 'border="1 SOLID #E2E8F0" width="190" height="172" />') == 64,
       str(dsl.count('<Container color="#FFFFFF" borderRadius="10.0" '
                     'border="1 SOLID #E2E8F0" width="190" height="172" />')))
    ck("64 id labels with fontSize 20 mono",
       dsl.count('fontSize="20.0" fontFamily="DejaVu Sans Mono" textAlign="CENTER"') == 64,
       str(dsl.count('fontSize="20.0" fontFamily="DejaVu Sans Mono" textAlign="CENTER"')))
    ck("8 column headers + 8 row headers",
       len(re.findall(r'fontFamily="DejaVu Sans Mono" textAlign="CENTER" text="C\d"', dsl)) == 8
       and len(re.findall(r'fontFamily="DejaVu Sans Mono" textAlign="RIGHT" text="R\d"',
                          dsl)) == 8)

    # every body must appear at exactly its scene-data bbox, with the right paint attrs
    def num(v):
        """Reproduce dsllib's number formatting exactly (round() keeps int in, int out)."""
        return str(v) if isinstance(v, str) else str(round(v, 2))

    miss = []
    for o in objs:
        bb = o["bbox"]
        s = o["size"]
        hexv = {"blue": "#2563EB", "orange": "#EA580C",
                "green": "#16A34A", "purple": "#7C3AED"}[o["color"]]
        head = ('<Positioned left="%s" top="%s" width="%s" height="%s">\n'
                % (num(bb["x_min"]), num(bb["y_min"]), num(s), num(s)))
        if o["shape"] == "ring":
            frag = (head + '<Container color="#FFFFFF" borderRadius="%s" border="%g SOLID %s"'
                           ' width="%s" height="%s" />'
                    % (num(s / 2.0), s / 4.0, hexv, num(s), num(s)))
        elif o["shape"] == "circle":
            frag = (head + '<Container color="%s" borderRadius="%s" width="%s" height="%s" />'
                    % (hexv, num(s / 2.0), num(s), num(s)))
        elif o["shape"] == "square":
            frag = head + '<Container color="%s" borderRadius="0.0" width="%s" height="%s" />' \
                % (hexv, num(s), num(s))
        else:
            frag = (head + '<Container color="%s" borderRadius="%s" width="%s" height="%s" />'
                    % (hexv, num(round(0.22 * s, 2)), num(s), num(s)))
        if frag not in dsl:
            miss.append(o["id"])
    ck("all 64 bodies appear in the DSL at their scene-data bbox with the right paint",
       not miss, "missing: %s" % miss[:6])

    # the ring stroke really is size/4 in the emitted DSL, counted once per size
    ring_sizes = {}
    n_rings = {}
    for o in objs:
        if o["shape"] != "ring":
            continue
        frag = ('<Container color="#FFFFFF" borderRadius="%s" border="%g SOLID #%s"'
                % (num(o["size"] / 2.0), o["size"] / 4.0,
                   {"blue": "2563EB", "orange": "EA580C",
                    "green": "16A34A", "purple": "7C3AED"}[o["color"]]))
        ring_sizes[frag] = ring_sizes.get(frag, 0) + 1
        n_rings[o["size"]] = n_rings.get(o["size"], 0) + 1
    bad = {k: (dsl.count(k), v) for k, v in ring_sizes.items() if dsl.count(k) != v}
    ck("every ring emits exactly one Container, outer=size and stroke=size/4",
       not bad and sorted(n_rings) == [48, 64, 80],
       "ring sizes %s ; mismatches %s" % (n_rings, list(bad)[:2]))
    ck("ring stroke widths used by bodies are exactly 12/16/20 px",
       all(('border="%g SOLID' % (s / 4.0)) in dsl for s in (48, 64, 80)),
       "the 5 px stroke in the DSL belongs to the 20 px legend chip, not to a body")
    ck("ring hole uses the opaque cell fill, never an alpha colour",
       all('color="#FFFFFF"' in k for k in ring_sizes)
       and not re.search(r'color="#FFFFFF[0-9A-F]{2}"', dsl))
    ck("DSL body block emits no opacity attribute", ' opacity="' not in dsl)
    ck("DSL declares all 4 palette colours",
       all(c in dsl for c in ("#2563EB", "#EA580C", "#16A34A", "#7C3AED")))

    print("\n=== 5. questions ===")
    qlist = qs["questions"]
    ck("14 questions", len(qlist) == 14, str(len(qlist)))
    ck("12 grid + 2 occlusion",
       sum(1 for q in qlist if q["image"] == "grid-scene.png") == 12
       and sum(1 for q in qlist if q["image"] == "occlusion.png") == 2)
    two_step = [q for q in qlist if q["steps"] >= 2]
    ck("at least 4 two-step questions", len(two_step) >= 4,
       "%d two-step: %s" % (len(two_step), [q["q_id"] for q in two_step]))
    kinds = {q["type"] for q in qlist}
    need = {"composite_attribute_retrieval", "strict_center_horizontal_relation",
            "distance", "ordering", "bounding_box", "color_counting", "shape_counting"}
    ck("all required question types covered", need <= kinds, str(sorted(need - kinds)))
    gc = qs["global_conventions"]
    ck("global conventions state the coordinate origin",
       "原点" in gc["coordinate_origin"] and "左上角" in gc["coordinate_origin"],
       gc["coordinate_origin"][:40])
    ck("global conventions state the counting scope",
       "G01" in gc["counting_scope"] and "G64" in gc["counting_scope"])
    ck("global conventions state the tie policy",
       "并列" in gc["tie_policy"] and "严格" in gc["tie_policy"])
    ck("global conventions state the distance metric", "欧氏距离" in gc["distance_metric"])
    ck("every question has comparison criteria + tolerance + visibility basis",
       all(q.get("comparison_criteria") and q.get("coordinate_tolerance")
           and q.get("answer_visibility_basis") for q in qlist))
    ck("every question has a non-empty scope", all(q.get("scope") for q in qlist))
    ck("questions.json contains no answer/correct/solution field",
       not any(k in q for q in qlist
               for k in ("answer", "correct", "solution", "answer_type")))
    ck("questions.json mentions no hidden-body count",
       not any(s in json.dumps(qlist, ensure_ascii=False)
               for s in ("隐藏主体", "H1", "H5", "H6")))
    ck("occlusion question with undeterminable answer exists",
       any(a["answer_type"] == "undeterminable" for a in ans["answers"]))

    print("\n=== 6. answers recomputed from scene-data.json (independent path) ===")
    A = {a["q_id"]: a for a in ans["answers"]}
    ck("14 answers", len(A) == 14, str(len(A)))

    # Q18
    exp = sorted(o["id"] for o in objs if o["color"] == "purple" and o["shape"] == "ring")
    ck("Q18 purple rings", A["Q18"]["answer"] == exp, str(exp))
    # Q19
    exp = sorted(o["id"] for o in objs if o["size"] == 80 and o["color"] == "orange")
    ck("Q19 size80 orange", A["Q19"]["answer"] == exp, str(exp))
    # Q20
    cand = ["G07", "G19", "G12", "G13"]
    xs = {i: by[i]["center"]["x"] for i in cand}
    exp = max(cand, key=lambda i: xs[i])
    ck("Q20 strict max centre x", A["Q20"]["answer"] == exp, exp)
    ck("Q20 unique (no centre-x tie)", len(set(xs.values())) == 4, str(xs))
    # Q21
    sub = [o for o in objs if o["row"] == 3 and o["color"] == "green"]
    gx = {o["id"]: o["center"]["x"] for o in sub}
    exp = min(gx, key=lambda i: gx[i])
    ck("Q21 two-step leftmost green in R3", A["Q21"]["answer"] == exp, exp)
    ck("Q21 unique", len(set(gx.values())) == len(gx), str(gx))
    # Q22
    def d(a, b):
        return math.hypot(a["x"] - b["x"], a["y"] - b["y"])
    dd = {i: d(by[i]["center"], by["G13"]["center"]) for i in ("G16", "G24", "G09", "G17")}
    srt = sorted(dd.values())
    exp = min(dd, key=lambda i: dd[i])
    ck("Q22 nearest to G13", A["Q22"]["answer"] == exp, exp)
    ck("Q22 margin > 2px", srt[1] - srt[0] > 2.0, "%.2f" % (srt[1] - srt[0]))
    # Q23
    rings = [o for o in objs if o["shape"] == "ring"]
    d23 = {o["id"]: d(o["center"], by["G37"]["center"]) for o in rings if o["id"] != "G37"}
    o23 = sorted(d23.values())
    exp = min(d23, key=lambda i: d23[i])
    ck("Q23 nearest ring to G37", A["Q23"]["answer"] == exp, exp)
    ck("Q23 16 rings and unique argmin",
       len(rings) == 16 and o23[0] + 1e-9 < o23[1], "margin %.2f" % (o23[1] - o23[0]))
    # Q24
    col7 = {o["id"]: o["center"]["y"] for o in objs if o["col"] == 7}
    exp = sorted(col7, key=lambda i: (col7[i], i))[:3]
    ck("Q24 first 3 of C7 by centre y", A["Q24"]["answer"] == exp, str(exp))
    ck("Q24 distinct centre y", len(set(col7.values())) == 8)
    # Q25
    sub = [o for o in objs if o["size"] == 64]
    exp = [o["id"] for o in sorted(sub, key=lambda o: (o["center"]["x"], o["center"]["y"],
                                                       o["id"]))[:3]]
    ck("Q25 first 3 of size-64 with tie-break", A["Q25"]["answer"] == exp, str(exp))
    ck("Q25 has %d size-64 bodies" % len(sub), len(sub) == 21)
    # Q26
    bb = by["G23"]["bbox"]
    exp = [bb["x_min"], bb["y_min"], bb["x_max"], bb["y_max"]]
    ck("Q26 G23 bbox", A["Q26"]["answer"] == exp, str(exp))
    # Q27
    sub = [o for o in objs if o["size"] == 80]
    exp = [min(o["bbox"]["x_min"] for o in sub), min(o["bbox"]["y_min"] for o in sub),
           max(o["bbox"]["x_max"] for o in sub), max(o["bbox"]["y_max"] for o in sub)]
    ck("Q27 union bbox of size-80", A["Q27"]["answer"] == exp, str(exp))
    # Q28
    blue = [o for o in objs if o["color"] == "blue"]
    exp = {"blue_total": len(blue),
           "blue_size_48": len([o for o in blue if o["size"] == 48])}
    ck("Q28 blue counts", A["Q28"]["answer"] == exp, str(exp))
    # Q29
    circ = [o for o in objs if o["shape"] == "circle"]
    thr = 900
    exp = {"circle_total": len(circ),
           "circle_centre_x_gt_900": len([o for o in circ if o["center"]["x"] > thr])}
    ck("Q29 circle counts", A["Q29"]["answer"] == exp, str(exp))
    colx = sorted({o["center"]["x"] for o in objs})
    ck("Q29 threshold 900 is clear of every centre x",
       all(abs(v - thr) > 2 for v in colx), str(colx))
    # Q30
    exp = {"fully_visible_bodies": 4, "ids": ["V1", "V2", "V3", "V4"]}
    ck("Q30 fully visible count", A["Q30"]["answer"] == exp, str(exp))
    ck("Q30 matches occlusion-scene-data fully_visible_bodies",
       [b["label"] for b in occ["fully_visible_bodies"]] == exp["ids"])
    ck("Q30 P1 is partially covered and therefore excluded",
       occ["partially_visible_bodies"][0]["covered_px"] > 0)
    # Q31
    ck("Q31 answer is 无法确定", A["Q31"]["answer"] == "无法确定", A["Q31"]["answer"])

    print("\n=== 7. occlusion geometry ===")
    ck("2 opaque covers", len(occ["covers"]) == 2)
    ck("covers declare no alpha", all("不透明" in c["opacity"] for c in occ["covers"]))
    od = open(os.path.join(OUT, "occlusion.snapshot"), encoding="utf-8").read()
    oa = open(os.path.join(OUT, "occlusion-alternative.snapshot"), encoding="utf-8").read()
    ck("A DSL has no opacity/dashed for covers",
       "opacity" not in od and "DASHED" not in od and "dashed" not in od.lower())
    ck("A DSL has no <Image>", "<Image" not in od and "<Image" not in oa)
    ck("A DSL emits the hidden bodies", " 84 " in od or 'width="84"' in od)
    ck("B DSL uses ClipRect", "<ClipRect" in oa, str(oa.count("<ClipRect")))
    ck("B DSL does NOT use ClipRect in A", "<ClipRect" not in od)
    hsetA = occ["hidden_set_A__occlusion_png"]
    hsetB = occ["hidden_set_B__occlusion_alternative_png"]["items"]
    ck("hidden sets have different counts", len(hsetA) != len(hsetB),
       "%d vs %d" % (len(hsetA), len(hsetB)))
    sigA = sorted((b["shape"], b["size"], b["color"]) for b in hsetA)
    sigB = sorted((b["shape"], b["size"], b["color"]) for b in hsetB)
    ck("hidden shapes/sizes/colors differ", sigA != sigB)
    ck("hidden nominal positions differ",
       [b["nominal_bbox"] for b in hsetA] != [b["nominal_bbox"] for b in hsetB])
    # every hidden body is fully inside a cover
    def inside(body):
        for c in occ["covers"]:
            bb2, cb2 = body["nominal_bbox"], c["bbox"]
            if (cb2["x_min"] <= bb2["x_min"] and cb2["y_min"] <= bb2["y_min"]
                    and bb2["x_max"] <= cb2["x_max"] and bb2["y_max"] <= cb2["y_max"]):
                return True
        return False
    ck("all A hidden bodies fully inside a cover", all(inside(b) for b in hsetA),
       str([b["label"] for b in hsetA if not inside(b)]))
    ck("all B hidden bodies fully inside a cover", all(inside(b) for b in hsetB),
       str([b["label"] for b in hsetB if not inside(b)]))
    # B's emitted bodies are outside the clip box
    cbx = occ["clip_box_of_variant_B"]
    ck("B emitted bodies start beyond the clip box",
       all(b["emitted_bbox"]["x_min"] >= cbx["x_max"] for b in hsetB),
       "clip x_max=%d, emitted x_min=%s" % (cbx["x_max"],
                                             min(b["emitted_bbox"]["x_min"] for b in hsetB)))

    print("\n=== 8. pixel equality proof ===")
    pa = os.path.join(OUT, "occlusion.png")
    pb = os.path.join(OUT, "occlusion-alternative.png")
    ba = open(pa, "rb").read()
    bb_ = open(pb, "rb").read()
    ck("raw PNG bytes identical", ba == bb_, "%d bytes" % len(ba))
    ck("sha256 identical", sha(pa) == sha(pb), sha(pa)[:16])
    ia = Image.open(pa).convert("RGB")
    ib = Image.open(pb).convert("RGB")
    d = ImageChops.difference(ia, ib)
    ck("zero differing pixels", d.getbbox() is None, str(d.getbbox()))
    ck("equivalence.json hash matches the file on disk",
       eq["hashes"]["occlusion.png"]["sha256"] == sha(pa))
    ck("equivalence.json reports pixel_identical", eq["pixel_comparison"]["pixel_identical"] is True)
    ck("equivalence.json differing_pixels == 0",
       eq["pixel_comparison"]["differing_pixels"] == 0)
    ck("the two DSLs are NOT identical (proves the mechanism really differs)",
       sha(os.path.join(OUT, "occlusion.snapshot"))
       != sha(os.path.join(OUT, "occlusion-alternative.snapshot")),
       "%d vs %d bytes" % (os.path.getsize(os.path.join(OUT, "occlusion.snapshot")),
                           os.path.getsize(os.path.join(OUT, "occlusion-alternative.snapshot"))))
    ck("scene-data dsl hash matches grid-scene.snapshot",
       scene["dsl"]["sha256"] == sha(os.path.join(OUT, "grid-scene.snapshot")))
    ck("scene-data dsl bytes match grid-scene.snapshot",
       scene["dsl"]["bytes"] == os.path.getsize(os.path.join(OUT, "grid-scene.snapshot")))

    print("\n=== 9. hidden counts are never answers ===")
    a_txt = json.dumps(ans, ensure_ascii=False)
    for a in ans["answers"]:
        if a["q_id"] in ("Q30", "Q31"):
            continue
        ck("%s does not mention a hidden count" % a["q_id"],
           "隐藏主体数量" not in json.dumps(a, ensure_ascii=False)
           or a["q_id"] == "Q31")
    ck("answers.json never states the hidden count as a ground truth",
       '"hidden_count": 5' not in a_txt and '"hidden_count": 6' not in a_txt)

    npass = sum(1 for c in CHECKS if c["pass"])
    print("\n==== %d / %d checks passed ====" % (npass, len(CHECKS)))
    out = {
        "task_id": "A19",
        "checks_total": len(CHECKS),
        "checks_passed": npass,
        "all_passed": npass == len(CHECKS),
        "checks": CHECKS,
    }
    p = os.path.join(OUT, "verification.json")
    with open(p, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    print("wrote", p)
    return 0 if npass == len(CHECKS) else 1


if __name__ == "__main__":
    sys.exit(main())
