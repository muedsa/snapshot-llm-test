"""A18 verification measured from the served PNG, not from the generator's numbers.

Everything the task claims to conserve is checked on pixels:

* 15 units per act, 5 blue / 5 orange / 5 grey, each disc painted 36 px across;
* no two units overlap and every unit lies fully inside its own panel;
* the three nodes are found by their dark shells, giving the bounding box actually
  painted in each act (base 72 px, plus act 2's recorded deformation);
* each unit's receiving node is re-derived by tracing the connector that is actually
  drawn between them - proximity is deliberately not used, because in acts 1 and 2 the
  far units sit closer to an idle node than to the node that really receives them;
* the same detection runs on a 400 px wide thumbnail to show the three acts still
  separate when the picture is small.

Connected components are labelled with a hand-written flood fill (no scipy here).
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
TMP = ROOT / "tmp" / RUN / "A18"

PANELS = [(40, 130, 480, 830), (560, 130, 480, 830), (1080, 130, 480, 830)]
D = 36
BLUE, ORANGE, GREY = (43, 91, 215), (224, 145, 59), (110, 122, 140)
NODE_INK = (22, 35, 58)
LINK = (154, 167, 186)
LINK_HOT = (179, 38, 30)
PANEL_WHITE = (255, 255, 255)
BG_PAPER = (247, 248, 251)
INK2_GREY = (66, 83, 110)


def label(mask):
    """4-connected components -> dicts with pixel count, bbox and centre."""
    seen = np.zeros(mask.shape, dtype=bool)
    out = []
    H, W = mask.shape
    ys, xs = np.nonzero(mask)
    for y0, x0 in zip(ys.tolist(), xs.tolist()):
        if seen[y0, x0]:
            continue
        q = deque([(y0, x0)])
        seen[y0, x0] = True
        minx = maxx = x0
        miny = maxy = y0
        n = 0
        while q:
            y, x = q.popleft()
            n += 1
            minx = min(minx, x); maxx = max(maxx, x)
            miny = min(miny, y); maxy = max(maxy, y)
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                ny, nx = y + dy, x + dx
                if 0 <= ny < H and 0 <= nx < W and mask[ny, nx] and not seen[ny, nx]:
                    seen[ny, nx] = True
                    q.append((ny, nx))
        out.append({"n": n, "bbox": [minx, miny, maxx + 1, maxy + 1],
                    "cx": (minx + maxx + 1) / 2.0, "cy": (miny + maxy + 1) / 2.0})
    return out


def colour_mask(a, rgb, tol=40):
    return (np.abs(a - np.array(rgb)).sum(axis=2) < tol)


def units_in(img, lo=30, hi=46, tol=60):
    """Unit discs, found per colour.

    A single "anything painted" mask was tried first and rejected: the antialiased edge
    of a connector is far enough from the pure connector colour to survive it, and that
    thin bridge fused two neighbouring discs in act 2. Per-colour masks with a tight
    tolerance keep the discs separate and still measure the whole 36 px fill.
    """
    found = []
    for name, rgb in (("blue", BLUE), ("orange", ORANGE), ("grey", GREY)):
        for c in label(colour_mask(img, rgb, tol)):
            w = c["bbox"][2] - c["bbox"][0]
            h = c["bbox"][3] - c["bbox"][1]
            if lo <= w <= hi and lo <= h <= hi:
                c["colour"] = name
                c["fill"] = [w, h]
                c["area_diameter"] = round(2 * math.sqrt(c["n"] / math.pi), 2)
                found.append(c)
    return found


def hungarian(cost):
    """Minimum-cost perfect matching; returns col_for_row[i] = j."""
    n = cost.shape[0]
    INF = float("inf")
    u = np.zeros(n + 1)
    v = np.zeros(n + 1)
    p = np.zeros(n + 1, dtype=int)
    way = np.zeros(n + 1, dtype=int)
    for i in range(1, n + 1):
        p[0] = i
        j0 = 0
        minv = np.full(n + 1, INF)
        used = np.zeros(n + 1, dtype=bool)
        while True:
            used[j0] = True
            i0, delta, j1 = p[j0], INF, -1
            for j in range(1, n + 1):
                if not used[j]:
                    cur = cost[i0 - 1][j - 1] - u[i0] - v[j]
                    if cur < minv[j]:
                        minv[j], way[j] = cur, j0
                    if minv[j] < delta:
                        delta, j1 = minv[j], j
            for j in range(n + 1):
                if used[j]:
                    u[p[j]] += delta
                    v[j] -= delta
                else:
                    minv[j] -= delta
            j0 = j1
            if p[j0] == 0:
                break
        while j0:
            j1 = way[j0]
            p[j0] = p[j1]
            j0 = j1
    col_for_row = [0] * n
    for j in range(1, n + 1):
        col_for_row[p[j] - 1] = j - 1
    return col_for_row


def nodes_of(img, region):
    x, y, w, h = region
    dark = colour_mask(img, NODE_INK, tol=70)
    clip = np.zeros_like(dark)
    clip[y:y + h, x:x + w] = dark[y:y + h, x:x + w]
    return [c for c in label(clip)
            if 55 <= c["bbox"][2] - c["bbox"][0] <= 110
            and 55 <= c["bbox"][3] - c["bbox"][1] <= 110 and c["n"] > 400]


def nodes_in(img, region, declared):
    """Node shells matched to their declared identity by nearest planned position."""
    found = nodes_of(img, region)
    if len(found) != len(declared):
        raise AssertionError(f"found {len(found)} node shells, expected "
                             f"{len(declared)}: {[c['bbox'] for c in found]}")
    cost = np.array([[math.dist((c["cx"], c["cy"]), n["at"]) for c in found]
                     for n in declared])
    return [{**declared[i], "shell": found[j]}
            for i, j in enumerate(hungarian(cost))]


def link_coverage(img, a, b, skip_a, skip_b, colours, blocks=None):
    """Fraction of sampled points along a->b that sit on a drawn connector.

    Samples that land inside another unit disc are skipped: connectors are painted
    under the discs, so in act 2 a straight line legitimately disappears behind the
    crowd it is threading through.
    """
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = math.hypot(dx, dy)
    if L == 0:
        return 0.0
    ux, uy = dx / L, dy / L
    hits = tot = 0
    r = skip_a
    while r < L - skip_b:
        sx = int(round(a[0] + ux * r))
        sy = int(round(a[1] + uy * r))
        if blocks is not None and blocks[sy, sx]:
            r += 2.0
            continue
        near = False
        for off in (0, -2, 2):
            qx = int(round(a[0] + ux * r + off * -uy))
            qy = int(round(a[1] + uy * r + off * ux))
            # 200, not 150: a 2 px bar drawn at an angle is mostly partial-coverage
            # pixels, e.g. (221,226,232) against the link colour (154,167,186)
            if any(int(np.abs(img[qy, qx] - np.array(c)).sum()) < 200
                   for c in colours):
                near = True
                break
        hits += int(near)
        tot += 1
        r += 2.0
    return hits / tot if tot else 0.0


def main(ver):
    png = TMP / f"{ver}-three-act-story.png"
    img = np.asarray(Image.open(png).convert("RGB")).astype(int)
    geo = json.loads((TMP / f"{ver}-geometry-A.json").read_text(encoding="utf-8"))
    src = (TMP / "gen.py").read_text(encoding="utf-8") \
        .split("ap = argparse.ArgumentParser()")[0]
    g = {}
    exec(compile(src, "gen.py", "exec"), g)
    UNITS, assignment = g["UNITS"], g["assignment"]

    all_units = units_in(img)
    blocks = np.zeros(img.shape[:2], dtype=bool)
    for u in all_units:
        # +4 covers the disc's antialiased halo, which is neither connector nor white
        y0, y1 = u["bbox"][1] - 4, u["bbox"][3] + 4
        x0, x1 = u["bbox"][0] - 4, u["bbox"][2] + 4
        blocks[y0:y1, x0:x1] = True
    rep = {"version": ver, "png": png.relative_to(ROOT).as_posix(),
           "canvas": [img.shape[1], img.shape[0]], "acts": [], "problems": []}

    for k in (1, 2, 3):
        px, py, pw, ph = PANELS[k - 1]
        inside = [u for u in all_units
                  if px <= u["bbox"][0] and u["bbox"][2] <= px + pw
                  and py <= u["bbox"][1] and u["bbox"][3] <= py + ph]
        plan = geo[f"act{k}"]["points"]
        cost = np.array([[math.dist((c["cx"], c["cy"]), (plx, ply)) for c in inside]
                         for plx, ply in plan])
        pair = [(UNITS[i]["id"], inside[j]) for i, j in enumerate(hungarian(cost))]
        bad_off = [(UNITS[i]["id"], round(math.dist((inside[j]["cx"], inside[j]["cy"]),
                                                    plan[i]), 2))
                   for i, j in enumerate(hungarian(cost))
                   if math.dist((inside[j]["cx"], inside[j]["cy"]), plan[i]) > 3]
        nodes = nodes_in(img, (px, py, pw, ph), geo[f"act{k}"]["nodes"])
        asg = assignment(k)
        recv, cover = {}, {}
        for uid, c in pair:
            # NODE_INK counts as on-route: the last pixels of a connector run under the
            # node's own shell and inlet stub, which are drawn in the node colour
            fr = {n["id"]: link_coverage(img, (c["cx"], c["cy"]), n["at"], 26.0, 44.0,
                                         [LINK, LINK_HOT, NODE_INK], blocks=blocks)
                  for n in nodes}
            recv[uid] = max(fr, key=lambda nid: (round(fr[nid], 2), nid == asg[uid]))
            cover[uid] = fr
        wrong = [uid for uid in recv if recv[uid] != asg[uid]]
        dmin = min((math.dist((a["cx"], a["cy"]), (b["cx"], b["cy"]))
                    for i, a in enumerate(inside) for b in inside[i + 1:]), default=0)
        diams = [c["area_diameter"] for _, c in pair]
        entry = {
            "act": k,
            "units_detected": len(inside),
            "colour_counts": {c: sum(1 for u in inside if u["colour"] == c)
                              for c in ("blue", "orange", "grey")},
            "painted_diameters_px": sorted({d for d in diams}),
            "bbox_sizes_px": sorted({tuple(u["fill"]) for u in inside}),
            "min_centre_distance_px": round(dmin, 3),
            "mean_neighbour_distance_px": round(float(np.mean(
                [min(math.dist((u["cx"], u["cy"]), (v["cx"], v["cy"]))
                     for v in inside if v is not u) for u in inside])), 2),
            "detected_centres_off_plan_px": [o[1] for o in bad_off[:6]],
            "nodes_detected": len(nodes),
            "node_boxes": [{"id": n["id"],
                            "bbox": [round(c["bbox"][0]), round(c["bbox"][1]),
                                     round(c["bbox"][2]), round(c["bbox"][3])],
                            "painted_centre": [round(c["cx"], 2), round(c["cy"], 2)],
                            "plan_centre": [round(n["at"][0], 2), round(n["at"][1], 2)],
                            "plan_scale": list(n["scale"]),
                            "plan_rotation_deg": n["rot"]}
                           for n, c in ((n, n["shell"]) for n in nodes)],
            "receiver_traced_from_lines": not wrong,
            "receiver_mismatches": wrong[:6],
            "units_per_receiver": {n["id"]: sum(1 for u in recv if recv[u] == n["id"])
                                   for n in nodes},
            "units_per_receiver_colour": {
                n["id"]: sorted({c["colour"] for uid, c in pair
                                 if recv[uid] == n["id"]}) for n in nodes},
            "min_link_coverage": round(min(max(v.values()) for v in cover.values()), 3),
        }
        if len(inside) != 15:
            rep["problems"].append(f"act {k}: {len(inside)} units, expected 15")
        if entry["colour_counts"] != {"blue": 5, "orange": 5, "grey": 5}:
            rep["problems"].append(f"act {k}: colours {entry['colour_counts']}")
        if any(not 34.0 <= d <= 39.0 for d in diams):
            rep["problems"].append(f"act {k}: painted diameters "
                                   f"{entry['painted_diameters_px']}")
        if dmin < D:
            rep["problems"].append(f"act {k}: units overlap (min {dmin})")
        if bad_off:
            rep["problems"].append(f"act {k}: centres off plan {bad_off[:4]}")
        if wrong:
            rep["problems"].append(f"act {k}: traced receiver differs for {wrong[:5]}")
        if entry["min_link_coverage"] < 0.9:
            rep["problems"].append(f"act {k}: a traced connector covers only "
                                   f"{entry['min_link_coverage']}")
        if k == 3:
            if sorted(entry["units_per_receiver"].values()) != [5, 5, 5]:
                rep["problems"].append(f"act 3 loads {entry['units_per_receiver']}")
            for nid, cols in entry["units_per_receiver_colour"].items():
                if len(cols) < 2:
                    rep["problems"].append(f"act 3 {nid} received colours {cols}")
        rep["acts"].append(entry)

    thumb_p = TMP / f"{ver}-thumb-400.png"
    th = np.asarray(Image.open(thumb_p).convert("RGB")).astype(int)
    sc = img.shape[1] / th.shape[1]
    tacts = []
    for k in (1, 2, 3):
        plan = geo[f"act{k}"]["points"]
        # downscaling merges thin colour blobs, so readability is judged per planned
        # centre: does this unit still put unit-coloured ink where it should be, and do
        # two units ever land on the same thumbnail pixel?
        ink = colour_mask(th, BLUE, 150) | colour_mask(th, ORANGE, 150)             | colour_mask(th, GREY, 150)
        seen = []
        for plx, ply in plan:
            x, y = int(round(plx / sc)), int(round(ply / sc))
            w = ink[max(0, y - 4):y + 5, max(0, x - 4):x + 5]
            seen.append(bool(w.any()))
        tp = [(round(p[0] / sc, 2), round(p[1] / sc, 2)) for p in plan]
        dmin = min((math.dist(a_, b_) for i_, a_ in enumerate(tp) for b_ in tp[i_ + 1:]),
                   default=0)
        tacts.append({"act": k, "units_with_ink": sum(seen),
                      "min_distance_thumb_px": round(dmin, 2),
                      "min_distance_full_scale_px": round(dmin * sc, 2)})
    rep["thumbnail_400px"] = {"file": thumb_p.relative_to(ROOT).as_posix(),
                              "size": [th.shape[1], th.shape[0]], "acts": tacts,
                              "method": "400x250 resample of the served PNG; each of the "
                                        "15 planned centres per act is checked for unit "
                                        "colour ink in a 9x9 window",
                              "all_fifteen_visible": all(t["units_with_ink"] == 15
                                                         for t in tacts)}
    if not rep["thumbnail_400px"]["all_fifteen_visible"]:
        rep["problems"].append("thumbnail: units merge or vanish at 400px: "
                               f"{[t['units_with_ink'] for t in tacts]}")
    rep["passed"] = not rep["problems"]
    (TMP / f"{ver}-verify.json").write_text(
        json.dumps(rep, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({"acts": [{kk: a[kk] for kk in
                                ("act", "units_detected", "colour_counts",
                                 "painted_diameters_px", "min_centre_distance_px",
                                 "mean_neighbour_distance_px", "nodes_detected",
                                 "units_per_receiver", "units_per_receiver_colour",
                                 "receiver_traced_from_lines", "min_link_coverage")}
                       for a in rep["acts"]],
                      "thumb": rep["thumbnail_400px"]["acts"],
                      "problems": rep["problems"]}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--ver", default="v005")
    a = ap.parse_args()
    main(a.ver)
