"""A23 · PNG cover + six transparent keyframes + timing/frame data."""
from __future__ import annotations

import json
import math
import os
import random
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = os.environ["SNAPSHOT_RUN_ID"]
TASK = "A23"
TMP = ROOT / "tmp" / RUN / TASK
VERSION = sys.argv[1] if len(sys.argv) > 1 else "v001"
sys.path.insert(0, str(ROOT / "tmp" / RUN / "_suite" / "scripts"))

from dsl import C, Col, Gap, HGap, Pos, Row, SizedBox, Stack, T  # noqa: E402

W, F = 600, 6
BG = "#0B1220"
INK = "#F4F7FB"
MUTED = "#9AA9BD"
CORAL = "#F97362"
COLORS = {"blue": "#3B82F6", "orange": "#F59E0B", "green": "#34D399", "purple": "#8B5CF6"}
SHAPES = ["circle", "square", "ring", "rounded"]
SIZES = [24, 22, 26, 20]
FONT = "Inter,Noto Sans CJK SC"


def unit_defs():
    out = []
    for i in range(12):
        color = list(COLORS)[i % 4]
        shape = SHAPES[i % 4]
        size = SIZES[i % 4]
        out.append({"id": f"U{i+1:02d}", "color": color, "shape": shape, "w": size, "h": size, "alpha": 1.0})
    return out


def shape_c(shape, size, color):
    if shape == "circle":
        return C(width=size, height=size, color=color, borderRadius=size / 2)
    if shape == "square":
        return C(width=size, height=size, color=color)
    if shape == "ring":
        return C(width=size, height=size, color="transparent", border=f"{size/4} SOLID {color}", borderRadius=size / 2)
    return C(width=size, height=size, color=color, borderRadius=size * 0.2)


def rot_matrix(deg):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    return f"({c:.6f},{s:.6f},0,0,{-s:.6f},{c:.6f},0,0,0,0,1,0,0,0,0,1)"


def frame_positions(units):
    final = []
    for i, u in enumerate(units):
        a = math.radians(-90 + i * 30)
        final.append((300 + 190 * math.cos(a), 300 + 190 * math.sin(a)))
    frames = []
    radii = [270, 250, 235, 220, 205, 190]
    for k in range(6):
        t = k / 5
        e = t * t * (3 - 2 * t)
        ps = []
        r = radii[k]
        for i, (f) in enumerate(final):
            ang = math.radians(-90 + i * 30 + 18 * (1 - e))
            p = (300 + r * math.cos(ang), 300 + r * math.sin(ang))
            rot = (i * 37 + (i * 30 + 90 - i * 37) * e) % 360
            ps.append({"x": round(p[0], 2), "y": round(p[1], 2), "rot": round(rot, 2)})
        frames.append(ps)
    scatter = [(p['x'], p['y']) for p in frames[0]]
    return scatter, final, frames


def render_frame(units, ps):
    nodes = [SizedBox(W, W)]
    for u, p in zip(units, ps):
        sz = u["w"]
        child = shape_c(u["shape"], sz, COLORS[u["color"]])
        child = f'<Transform matrix="{rot_matrix(p["rot"])}" alignment="CENTER">{child}</Transform>'
        nodes.append(Pos(p["x"] - sz / 2, p["y"] - sz / 2, child))
    return f'<Snapshot type="png" background="#00000000">\n' + Stack(nodes, width=W, height=W) + "\n</Snapshot>\n"


def cover(units):
    nodes = [SizedBox(1200, 800), Pos(0, 0, C(width=1200, height=800, color=BG)),
             Pos(0, 0, C(width=1200, height=6, gradientType="LINEAR", gradientColors=CORAL + ",#22D3EE,#F5C451",
                         gradientBegin="CENTER_LEFT", gradientEnd="CENTER_RIGHT")),
             Pos(70, 86, T("从结构到画面", size=80, color=INK, weight="BOLD", family=FONT)),
             Pos(74, 190, T("Layerlight · 12 个结构单元汇聚成图像", size=28, color=MUTED, family=FONT)),
             Pos(74, 252, T("STRUCTURE CONVERGES INTO IMAGE", size=18, color=CORAL, weight="BOLD", family=FONT, spacing=3)),
             Pos(74, 650, T("6 帧透明关键帧 · 250ms / frame · 1500ms loop", size=22, color=MUTED, family=FONT))]
    # ring on right, larger but same 12 units
    for i, u in enumerate(units):
        a = math.radians(-90 + i * 30)
        cx, cy = 850 + 260 * math.cos(a), 390 + 260 * math.sin(a)
        sz = 32 if i % 3 else 38
        child = shape_c(u["shape"], sz, COLORS[u["color"]])
        child = f'<Transform matrix="{rot_matrix(math.degrees(a)+90)}" alignment="CENTER">{child}</Transform>'
        nodes.append(Pos(cx - sz / 2, cy - sz / 2, child))
    for r in (260, 220, 180):
        nodes.append(Pos(850 - r, 390 - r, C(width=2 * r, height=2 * r, color="transparent",
                                              border=f"1 SOLID #22344D", borderRadius=r)))
    return f'<Snapshot type="png" background="{BG}">\n' + Stack(nodes, width=1200, height=800) + "\n</Snapshot>\n"


def main() -> int:
    units = unit_defs()
    scatter, final, frames = frame_positions(units)
    (TMP / "dsl").mkdir(parents=True, exist_ok=True)
    (TMP / "renders").mkdir(parents=True, exist_ok=True)
    (TMP / "dsl" / f"cover-{VERSION}.snapshot").write_text(cover(units), encoding="utf-8")
    for i, ps in enumerate(frames, 1):
        (TMP / "dsl" / f"frame-{i:02d}-{VERSION}.snapshot").write_text(render_frame(units, ps), encoding="utf-8")
    allframes = []
    for i, ps in enumerate(frames):
        allframes.append({"frame": i + 1, "t_ms": i * 250, "png": f"frame-{i+1:02d}.png",
                          "dsl": f"frame-{i+1:02d}.snapshot",
                          "units": [{"id": u["id"], "shape": u["shape"], "w": u["w"], "h": u["h"],
                                     "color": u["color"], "alpha": u["alpha"],
                                     "x": p["x"], "y": p["y"], "rotation_deg": p["rot"], "visible": True}
                                    for u, p in zip(units, ps)]})
    # trajectory deltas
    for i in range(6):
        for j, u in enumerate(units):
            cur = allframes[i]["units"][j]
            nxt = allframes[(i + 1) % 6]["units"][j]
            dx = round(nxt["x"] - cur["x"], 3); dy = round(nxt["y"] - cur["y"], 3)
            da = (nxt["rotation_deg"] - cur["rotation_deg"] + 180) % 360 - 180
            cur["next_delta"] = {"dx": dx, "dy": dy, "distance": round(math.hypot(dx, dy), 3),
                                 "rotation_delta_deg": round(da, 3), "interpolation": "easeInOutCubic positions; linear rotation"}
    frame_data = {"schema_version": 1, "task_id": TASK, "path_base": "output_dir", "canvas": [600, 600],
                  "unit_identity": [{"id": u["id"], "shape": u["shape"], "w": u["w"], "h": u["h"],
                                     "color": u["color"], "alpha": u["alpha"]} for u in units],
                  "frames": allframes,
                  "seam": {"from": 6, "to": 1, "t_ms": 1250, "loop_period_ms": 1500,
                           "note": "frame6→frame1 is a 250ms loop seam with a jump; not claimed seamless",
                           "max_displacement": max(math.dist(allframes[5]["units"][j]["__dummy__"] if False else (allframes[5]["units"][j]["x"], allframes[5]["units"][j]["y"]),
                                                           (allframes[0]["units"][j]["x"], allframes[0]["units"][j]["y"])) for j in range(12))}}
    frame_data["seam"]["max_displacement"] = round(frame_data["seam"]["max_displacement"], 3)
    (TMP / "frame-data.json").write_text(json.dumps(frame_data, ensure_ascii=False, indent=2), encoding="utf-8")
    timing = {"schema_version": 1, "task_id": TASK, "frame_count": 6, "frame_duration_ms": 250,
              "times_ms": [0, 250, 500, 750, 1000, 1250], "loop": True, "loop_period_ms": 1500,
              "seam": {"from_frame": 6, "to_frame": 1, "at_ms": 1250, "duration_ms": 250,
                       "behavior": "jump", "seamless": False,
                       "max_translation_px": frame_data["seam"]["max_displacement"]},
              "delivery_note": "6 transparent PNG keyframes + timing metadata; no GIF is synthesized.",
              "frames": [{"frame": i + 1, "t_ms": i * 250, "png": f"frame-{i+1:02d}.png"} for i in range(6)]}
    (TMP / "timing.json").write_text(json.dumps(timing, ensure_ascii=False, indent=2), encoding="utf-8")
    print("A23", VERSION, "built", len(units), "frames", [f["frame"] for f in allframes], "seam_max", frame_data["seam"]["max_displacement"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
