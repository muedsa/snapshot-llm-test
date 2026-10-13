"""A23 - "结构汇聚成画面": one unit table, six transparent frames, one RGB cover.

Everything the frames and the cover draw comes from UNITS below, so a unit's geometry,
colour and alpha are identical in all six frames by construction - only position and
rotation are interpolated, along an explicit spiral easing that is written into
frame-data.json rather than eyeballed.

Transparency, rotation and output types were checked against the service docs first:
Snapshot.background defaults to transparent, type accepts png/jpg/webp only, Container
shape is RECTANGLE|CIRCLE, and rotation needs Transform.matrix (there is no `rotate`
attribute in the documented parser).

Run:  python tmp/<run_id>/A23/kit.py            # writes all seven DSLs + frame-data
"""
from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
sys.path.insert(0, str(ROOT / "tmp" / RUN / "_suite" / "scripts"))
from snap import (C, Container, Node, Positioned, Snapshot, Stack, Transform,  # noqa: E402
                  matrix2d, num)

TMP = ROOT / "tmp" / RUN / "A23"
SANS, MONO = "Noto Sans CJK SC", "Noto Sans Mono CJK SC"
FRAME = 600
COVER = (1200, 800)
CENTRE = (300.0, 300.0)
FRAMES = 6
STEP_MS = 250
PERIOD_MS = 1500
MARGIN = 8.0

# id, shape, w, h, colour, alpha, slot (x, y), slot rotation (deg, clockwise),
# swirl: extra radius, extra angle.
# Colours are pairwise >100 apart in sum-abs so the audit can count each unit's own
# pixels even where one unit is drawn on top of another.
UNITS = [
    ("U01", "RECT", 160, 38, "#1B4FBF", 1.00, 240.0, 195.0, -33.0, 96.0, -118.0),
    ("U02", "RECT", 160, 38, "#D84F6B", 1.00, 360.0, 195.0, 33.0, 96.0, 118.0),
    ("U03", "RECT", 34, 84, "#C97415", 1.00, 400.0, 160.0, 0.0, 70.0, 64.0),
    ("U04", "RECT", 116, 110, "#7B4FBF", 1.00, 243.0, 300.0, 0.0, 58.0, -74.0),
    ("U05", "RECT", 116, 110, "#1F9E9E", 1.00, 357.0, 300.0, 0.0, 58.0, 96.0),
    ("U06", "RECT", 116, 110, "#2E7D5B", 1.00, 243.0, 410.0, 0.0, 62.0, 132.0),
    ("U07", "RECT", 116, 110, "#5B8CFF", 1.00, 357.0, 410.0, 0.0, 62.0, -140.0),
    ("U08", "RECT", 54, 104, "#F2A03D", 1.00, 243.0, 415.0, 0.0, 88.0, 40.0),
    ("U09", "RECT", 62, 62, "#8A4B08", 1.00, 357.0, 300.0, 0.0, 96.0, -52.0),
    ("U10", "CIRCLE", 72, 72, "#FFD166", 1.00, 462.0, 150.0, 0.0, 34.0, 96.0),
    ("U11", "RECT", 26, 74, "#3F3D56", 1.00, 128.0, 380.0, 0.0, 74.0, 150.0),
    ("U12", "CIRCLE", 92, 92, "#16A34A", 1.00, 128.0, 300.0, 0.0, 46.0, -96.0),
]


def half_diag(shape, w, h):
    return (w / 2.0) if shape == "CIRCLE" else math.hypot(w / 2.0, h / 2.0)


def ease(tau):
    """smoothstep: starts and settles gently, so all six frames stay distinguishable."""
    return tau * tau * (3.0 - 2.0 * tau)


def slot_of(u):
    _id, shape, w, h, col, alpha, x, y, rot, extra_r, extra_a = u
    dx, dy = x - CENTRE[0], y - CENTRE[1]
    return {"id": _id, "shape": shape, "w": w, "h": h, "colour": col, "alpha": alpha,
            "x": x, "y": y, "rot": rot, "r": math.hypot(dx, dy),
            "phi": math.degrees(math.atan2(dy, dx)), "reach": half_diag(shape, w, h),
            "extra_r": extra_r, "extra_a": extra_a}


def dispersed(s):
    r = s["r"] + s["extra_r"]
    a = math.radians(s["phi"] + s["extra_a"])
    return (CENTRE[0] + r * math.cos(a), CENTRE[1] + r * math.sin(a))


def path_state(s, tau):
    """Any point on a unit's spiral: tau=0 is the dispersed swirl, tau=1 the slot."""
    e = ease(tau)
    x0, y0 = dispersed(s)
    r0 = math.hypot(x0 - CENTRE[0], y0 - CENTRE[1])
    a0 = math.degrees(math.atan2(y0 - CENTRE[1], x0 - CENTRE[0]))
    r = r0 + (s["r"] - r0) * e
    a = a0 + (s["phi"] - a0) * e
    rot = s["start_rot"] + (s["rot"] - s["start_rot"]) * e
    return {"x": CENTRE[0] + r * math.cos(math.radians(a)),
            "y": CENTRE[1] + r * math.sin(math.radians(a)),
            "rot": rot, "r": r, "a": a, "tau": tau, "e": e}


def frame_state(s, n):
    """n = 1..6; frame 6 is the assembled picture, frame 1 the dispersed swirl."""
    return path_state(s, (n - 1) / (FRAMES - 1))


def build_units():
    out = []
    for u in UNITS:
        s = slot_of(u)
        s["start_rot"] = s["rot"] + s["extra_a"] * 0.6
        budget = FRAME / 2.0 - MARGIN - s["reach"]
        # keep the whole swept path inside the canvas: the farthest point of the unit
        # from the canvas centre is r + reach
        max_r = budget
        want = s["r"] + s["extra_r"]
        if want > max_r:
            s["extra_r"] = max(0.0, max_r - s["r"])
        s["frames"] = [frame_state(s, n) for n in range(1, FRAMES + 1)]
        s["max_reach"] = max(f["r"] for f in s["frames"]) + s["reach"]
        out.append(s)
    return out


def unit_node(s, st):
    shape = "CIRCLE" if s["shape"] == "CIRCLE" else None
    a = {"width": num(s["w"]), "height": num(s["h"]), "color": s["colour"]}
    if shape:
        a["shape"] = shape
    else:
        a["borderRadius"] = num(min(10.0, s["w"], s["h"]) * 0.12)
    rad = math.radians(st["rot"])
    tf = Transform(Container(**a), matrix=matrix2d(math.cos(rad), math.sin(rad)),
                   alignment="CENTER")
    return Positioned(tf, left=num(st["x"] - s["w"] / 2), top=num(st["y"] - s["h"] / 2),
                      width=num(s["w"]), height=num(s["h"]))


def frame_doc(units, n):
    """Transparent 600x600 frame: no background attribute at all (docs: default
    transparent), no text."""
    nodes = []
    for s in units:
        nodes.append(unit_node(s, s["frames"][n - 1]))
    root = Stack(C(width=num(FRAME), height=num(FRAME)), *nodes,
                 a={"clipBehavior": "NONE"})
    return Snapshot(root, type="png").render()


def trail_nodes(units, tau, centre=(300.0, 300.0), scale=1.0):
    """Dotted guide arcs: where each unit has come from, sampled along its own path."""
    out = []
    for s in units:
        for k in range(18):
            st = path_state(s, k / 17.0 * tau)
            x = centre[0] + (st["x"] - CENTRE[0]) * scale
            y = centre[1] + (st["y"] - CENTRE[1]) * scale
            d = 5.0
            out.append(Positioned(C(width=num(d), height=num(d), color="#B9C6E2",
                                    shape="CIRCLE"),
                                  left=num(x - d / 2), top=num(y - d / 2)))
    return out


def txt(nodes, s, x, y, size, colour, font=SANS, bold=False, right=None):
    if right is not None:
        x = right - tw(s, size, font == MONO)
    a = {"fontSize": num(size), "color": colour, "fontFamily": font}
    if bold:
        a["fontStyle"] = "BOLD"
    nodes.append(Positioned(Node("Text", a, [], s), left=num(x), top=num(y),
                            width=num(tw(s, size, font == MONO) + 6)))


def tw(t, size, mono=False):
    return sum(size * (1.0 if ord(c) > 0x2E80 else (0.52 if mono else 0.62)) for c in t)


def cover_doc(units):
    """1200x800 opaque RGB cover: left = structure mid-flight, right = the image."""
    W, H = COVER
    bg = "#F5F7FC"
    nodes = [C(width=num(W), height=num(H), color=bg)]
    # type block across the top
    txt(nodes, "从结构到画面", 48, 40, 70, "#111C36", SANS, bold=True)
    txt(nodes, "STRUCTURE CONVERGES INTO AN IMAGE", 52, 128, 26, "#41537A", MONO)
    txt(nodes, "12 个守恒几何单元 · 6 帧 600×600 透明 PNG · 250 ms/帧 · 周期 1500 ms",
        52, 168, 24, "#2C3B5C")
    # right panel: the assembled picture from frame 6, enlarged
    px, py, sc = 888.0, 455.0, 1.15
    nodes.append(Positioned(C(width=528, height=490, color="#FFFFFF", borderRadius=18),
                            left=624, top=210))
    for s in units:
        st = s["frames"][-1]
        nodes.append(unit_node_scaled(s, px + (st["x"] - CENTRE[0]) * sc,
                                      py + (st["y"] - CENTRE[1]) * sc, st["rot"], sc))
    # left panel: the same 12 units caught early on their spirals, with dotted trails
    nodes.append(Positioned(C(width=552, height=490, color="#EDF1FA", borderRadius=18),
                            left=48, top=210))
    tau = 0.10
    nodes += trail_nodes(units, 1.0, (324.0, 455.0), 0.72)
    for s in units:
        st = path_state(s, tau)
        nodes.append(unit_node_scaled(s, 324.0 + (st["x"] - CENTRE[0]) * 0.72,
                                      455.0 + (st["y"] - CENTRE[1]) * 0.72,
                                      st["rot"], 0.72))
    # footer
    nodes.append(Positioned(C(width=1104, height=1, color="#B9C6E2"), left=48, top=724))
    txt(nodes, f"左：汇聚途中（τ={tau:.2f}，t={int(tau * 1250)} ms）· "
               f"右：第 6 帧定格的画面", 52, 740, 24, "#41537A")
    txt(nodes, "open-snapshot · Snapshot DSL", 0, 740, 24, "#41537A", MONO, right=1152)
    return Snapshot(Stack(C(width=num(W), height=num(H)), *nodes),
                    background=bg, type="png").render()


def unit_node_scaled(s, x, y, rot, sc):
    a = {"width": num(s["w"] * sc), "height": num(s["h"] * sc), "color": s["colour"]}
    if s["shape"] == "CIRCLE":
        a["shape"] = "CIRCLE"
    else:
        a["borderRadius"] = num(min(10.0, s["w"], s["h"]) * 0.12 * sc)
    rad = math.radians(rot)
    return Positioned(Transform(Container(**a),
                                matrix=matrix2d(math.cos(rad), math.sin(rad)),
                                alignment="CENTER"),
                      left=num(x - s["w"] * sc / 2), top=num(y - s["h"] * sc / 2),
                      width=num(s["w"] * sc), height=num(s["h"] * sc))


def main():
    TMP.mkdir(parents=True, exist_ok=True)
    units = build_units()
    docs = {}
    for n in range(1, FRAMES + 1):
        docs[f"frame-{n:02d}"] = frame_doc(units, n)
    docs["cover"] = cover_doc(units)
    for name, body in docs.items():
        (TMP / f"{name}.snapshot").write_text(body + "\n", encoding="utf-8")
    data = {
        "schema_version": 1, "task_id": "A23", "path_base": "output_dir",
        "canvas": {"frame": [FRAME, FRAME], "cover": list(COVER), "unit": "px",
                   "origin": "top-left", "position_meaning": "几何中心 (x,y)"},
        "rotation_convention": "以自身中心为原点、顺时针度数；未旋转宽高记录在 w/h",
        "easing": {"rule": "位置沿螺旋插值：r(τ)=r0+(r_slot-r0)·e(τ)，"
                           "θ(τ)=θ0+(φ_slot-θ0)·e(τ)，rot(τ)=rot0+(rot_slot-rot0)·e(τ)",
                   "easing": "e(τ)=τ²(3-2τ)（smoothstep，起止缓和）",
                   "tau": "τ=(frame-1)/5，第 6 帧 τ=1 即定格位置"},
        "conservation": "跨帧只改变 x/y/rot；shape、w、h、colour、alpha 每帧相同",
        "units": [{
            "id": s["id"], "shape": s["shape"], "w": s["w"], "h": s["h"],
            "colour": s["colour"], "alpha": s["alpha"],
            "slot": {"x": s["x"], "y": s["y"], "rot": s["rot"]},
            "dispersed_start": {"x": round(dispersed(s)[0], 2),
                                "y": round(dispersed(s)[1], 2),
                                "rot": round(s["start_rot"], 2)},
            "reach_px": round(s["reach"], 2),
            "max_centre_radius_px": round(max(f["r"] for f in s["frames"]), 2),
            "max_reach_from_centre_px": round(s["max_reach"], 2),
            "frames": [{"frame": n, "t_ms": (n - 1) * STEP_MS,
                        "x": round(f["x"], 2), "y": round(f["y"], 2),
                        "rot": round(f["rot"], 2), "r": round(f["r"], 2),
                        "theta": round(f["a"], 2), "tau": round(f["tau"], 3),
                        "ease": round(f["e"], 4),
                        "png": f"frame-{n:02d}.png",
                        "dsl": f"frame-{n:02d}.snapshot"}
                       for n, f in enumerate(s["frames"], 1)],
            "steps": [],
        } for s in units],
    }
    for u in data["units"]:
        fs = u["frames"]
        for i in range(len(fs) - 1):
            a, b = fs[i], fs[i + 1]
            u["steps"].append({
                "from_frame": a["frame"], "to_frame": b["frame"],
                "dt_ms": STEP_MS, "dx": round(b["x"] - a["x"], 2),
                "dy": round(b["y"] - a["y"], 2),
                "displacement_px": round(math.hypot(b["x"] - a["x"], b["y"] - a["y"]), 2),
                "rotation_delta_deg": round(b["rot"] - a["rot"], 2),
                "direction_deg": round(math.degrees(
                    math.atan2(b["y"] - a["y"], b["x"] - a["x"])), 1)})
        a, b = fs[-1], fs[0]
        u["seam_step"] = {
            "from_frame": 6, "to_frame": 1, "dt_ms": STEP_MS,
            "dx": round(b["x"] - a["x"], 2), "dy": round(b["y"] - a["y"], 2),
            "displacement_px": round(math.hypot(b["x"] - a["x"], b["y"] - a["y"]), 2),
            "rotation_delta_deg": round(((b["rot"] - a["rot"] + 180) % 360) - 180, 2),
            "direction_deg": round(math.degrees(
                math.atan2(b["y"] - a["y"], b["x"] - a["x"])), 1)}
    (TMP / "frame-data.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({
        "units": len(units),
        "max_reach": round(max(u["max_reach"] for u in units), 2),
        "dispersion_by_frame": [round(sum(math.hypot(
            s["frames"][n]["x"] - s["x"], s["frames"][n]["y"] - s["y"])
            for s in units) / 12, 1) for n in range(FRAMES)],
        "seam_disp": round(sum(u["seam_step"]["displacement_px"]
                               for u in data["units"]) / 12, 1),
        "docs": sorted(docs)}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
