# -*- coding: utf-8 -*-
"""A23: cover + 6 transparent keyframes of 12 units converging."""
from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path

SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "")
sys.path.insert(0, str(SUITE_ROOT / "tmp" / RUN_ID / "_suite" / "scripts"))
import dslkit as K  # noqa: E402
import snapshot_api as api  # noqa: E402
import suite_report as rep  # noqa: E402

TASK = "A23"
OUT = SUITE_ROOT / "outputs" / RUN_ID / TASK
TMP = SUITE_ROOT / "tmp" / RUN_ID / TASK
OUT.mkdir(parents=True, exist_ok=True)
clock = rep.TaskClock(TASK)

COLORS = ["#2F6BFF", "#E8892B", "#16A34A", "#7C3AED"]
SHAPES = ["square", "circle", "triangle", "ring"]
SIZE = {"square": 34, "circle": 30, "triangle": 32, "ring": 36}

units = []
grid = [(300 + (c - 1.5) * 82, 300 + (r - 1) * 82) for r in range(3) for c in range(4)]
for i in range(12):
    shape = SHAPES[i % 4]
    ang = math.radians(-90 + i * 30 + (i % 3) * 7)
    r0 = 250 + (i % 4) * 14
    sx, sy = 300 + r0 * math.cos(ang), 300 + r0 * math.sin(ang)
    ex, ey = grid[i]
    rot0 = 0.0
    rot1 = 90.0 if shape == "triangle" else 0.0
    units.append({"id": f"U{i+1:02d}", "shape": shape, "w": SIZE[shape], "h": SIZE[shape],
                  "color": COLORS[i % 4], "alpha": 1.0,
                  "start": [round(sx, 2), round(sy, 2)], "end": [round(ex, 2), round(ey, 2)],
                  "rot0": rot0, "rot1": rot1,
                  "arc": (1 if i % 2 == 0 else -1) * (26 + (i % 5) * 6)})

TIMES = [0, 250, 500, 750, 1000, 1250]
PERIOD = 1500
def ease(t):
    return 0.5 - 0.5 * math.cos(math.pi * t)

frames = []
for k, t in enumerate(TIMES):
    f = t / (PERIOD - 250)
    e = ease(f)
    rows = []
    for u in units:
        sx, sy = u["start"]; ex, ey = u["end"]
        dx, dy = ex - sx, ey - sy
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        off = u["arc"] * math.sin(math.pi * f)
        px = sx + dx * e + nx * off
        py = sy + dy * e + ny * off
        rot = u["rot0"] + (u["rot1"] - u["rot0"]) * f
        rows.append({"id": u["id"], "shape": u["shape"], "x": round(px, 2), "y": round(py, 2),
                     "w": u["w"], "h": u["h"], "rotation": round(rot, 2),
                     "color": u["color"], "alpha": u["alpha"]})
    frames.append({"index": k + 1, "t_ms": t, "units": rows})

def raw_shape(shape, s, color):
    if shape == "circle":
        return f'<Container width="{s:g}" height="{s:g}" color="{color}" borderRadius="{s/2:g}"/>'
    if shape == "square":
        return f'<Container width="{s:g}" height="{s:g}" color="{color}" borderRadius="{4*s/34:g}"/>'
    if shape == "ring":
        r, ir = s / 2, s / 4
        path = (f"M{r:g} {r:g} m{-r:g} 0 a{r:g} {r:g} 0 1 0 {2*r:g} 0 a{r:g} {r:g} 0 1 0 {-2*r:g} 0 "
                f"M{r:g} {r:g} m{-ir:g} 0 a{ir:g} {ir:g} 0 1 1 {2*ir:g} 0 a{ir:g} {ir:g} 0 1 1 {-2*ir:g} 0 Z")
        return (f'<ClipPath path="{path}" fillRule="EVEN_ODD" clipBehavior="ANTI_ALIAS">'
                f'<Container width="{s:g}" height="{s:g}" color="{color}"/></ClipPath>')
    path = f"M{s/2:g} 0 L{s:g} {s:g} L0 {s:g} Z"
    return (f'<ClipPath path="{path}" fillRule="NON_ZERO" clipBehavior="ANTI_ALIAS">'
            f'<Container width="{s:g}" height="{s:g}" color="{color}"/></ClipPath>')

def unit_dsl(rec, dx=0.0, dy=0.0, scale=1.0):
    s = rec["w"] * scale
    cx, cy = rec["x"] * scale + dx, rec["y"] * scale + dy
    inner = raw_shape(rec["shape"], s, rec["color"])
    if abs(rec["rotation"]) < 0.01:
        return f'<Positioned left="{cx - s/2:g}" top="{cy - s/2:g}">{inner}</Positioned>'
    ang = math.radians(rec["rotation"])
    co, sn = math.cos(ang), math.sin(ang)
    h = s / 2
    tx = h - (co * h - sn * h)
    ty = h - (sn * h + co * h)
    return (f'<Positioned left="{cx - s/2:g}" top="{cy - s/2:g}">'
            f'<Transform matrix="({co:.6f},{sn:.6f},0,0,{-sn:.6f},{co:.6f},0,0,0,0,1,0,{tx:.4f},{ty:.4f},0,1)" '
            f'alignment="TOP_LEFT">{inner}</Transform></Positioned>')
logger = api.TaskLogger(TASK, TMP)
for k, fr in enumerate(frames):
    p = [unit_dsl(rec) for rec in fr["units"]]
    dsl = K.document(600, 600, p, background=None)
    snap = OUT / f"frame-{k+1:02d}.snapshot"
    snap.write_text(dsl, encoding="utf-8")
    rec = logger.render(snap, OUT / f"frame-{k+1:02d}.png", f"frame {k+1}")
    print(f"frame{k+1}: {rec['http_status']} {rec['response_bytes']}B {rec['elapsed_s']}s")
    if rec["http_status"] != 200:
        print((TMP / "responses" / f"{rec['id']}.bin").read_text(encoding="utf-8", errors="replace")[:800])
        raise SystemExit(1)

# cover 1200x800
last = frames[-1]
cov = [K.rect(0, 0, 1200, 800, color="#0B1220")]
cov.append(K.rect(0, 0, 1200, 6, color="#2F6BFF"))
for rec in last["units"]:
    cov.append(unit_dsl(rec, dx=600 - 300 * 1.15, dy=330 - 300 * 1.15, scale=1.15))
cov.append(K.text(80, 640, "从结构到画面", size=64, color="#FFFFFF", bold=True, width=600))
cov.append(K.text(80, 726, "12 个单元，6 帧汇聚 · Structure / Vision", size=24, color="#93A4BC",
                  width=900))
cov.append(K.text(860, 726, "layerlight.example.org", size=24, color="#93A4BC", width=280,
                  align="RIGHT"))
dsl = K.document(1200, 800, cov, background="#0B1220")
(OUT / "cover.snapshot").write_text(dsl, encoding="utf-8")
rec = logger.render(OUT / "cover.snapshot", OUT / "cover.png", "cover")
print("cover:", rec["http_status"], rec["response_bytes"], rec["elapsed_s"])

# ---------------------------------------------------------------- data
per_unit = []
for i, u in enumerate(units):
    steps = []
    for k in range(5):
        a, b = frames[k]["units"][i], frames[k + 1]["units"][i]
        steps.append({"from": k + 1, "to": k + 2,
                      "distance_px": round(math.hypot(b["x"] - a["x"], b["y"] - a["y"]), 2),
                      "rotation_delta_deg": round(b["rotation"] - a["rotation"], 2)})
    seam_a, seam_b = frames[5]["units"][i], frames[0]["units"][i]
    per_unit.append({
        "id": u["id"], "shape": u["shape"], "width_px": u["w"], "height_px": u["h"],
        "color": u["color"], "alpha": u["alpha"],
        "frames": [{"frame": f["index"], "t_ms": f["t_ms"], "x": f["units"][i]["x"],
                    "y": f["units"][i]["y"], "rotation": f["units"][i]["rotation"]}
                   for f in frames],
        "steps": steps,
        "seam_6_to_1": {"distance_px": round(math.hypot(seam_b["x"] - seam_a["x"],
                                                        seam_b["y"] - seam_a["y"]), 2),
                        "rotation_delta_deg": round(((seam_b["rotation"] - seam_a["rotation"]) % 360), 2)},
        "interpolation": "位置 = 起点 + (终点−起点)·(0.5−0.5cos(πt)) + 法向弧偏移·sin(πt)，"
                         "t = (t_ms)/(1250)；旋转线性插值",
    })
api.write_json(OUT / "frame-data.json", {
    "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
    "canvas": [600, 600], "transparent": True,
    "coordinate_system": "画布左上为原点，x 向右、y 向下；位置为几何中心；旋转以自身中心为原点、顺时针度数",
    "units": per_unit,
    "frames": [{"index": f["index"], "t_ms": f["t_ms"], "png": f"frame-{f['index']:02d}.png",
                "dsl": f"frame-{f['index']:02d}.snapshot"} for f in frames],
    "invariants": {"unit_count_per_frame": 12, "geometry_type_constant": True,
                   "width_height_constant": True, "color_constant": True, "alpha_constant": True,
                   "only_position_and_rotation_change": True,
                   "all_units_inside_canvas": all(0 <= r["x"] <= 600 and 0 <= r["y"] <= 600
                                                  for f in frames for r in f["units"])},
})
seam = [p["seam_6_to_1"]["distance_px"] for p in per_unit]
normal = [s["distance_px"] for p in per_unit for s in p["steps"]]
api.write_json(OUT / "timing.json", {
    "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
    "frame_duration_ms": 250, "frame_count": 6, "loop_period_ms": 1500,
    "loop": True, "frames": [{"index": f["index"], "t_ms": f["t_ms"],
                              "file": f"frame-{f['index']:02d}.png"} for f in frames],
    "seam": {"from_frame": 6, "to_frame": 1, "seamless": False,
             "mean_displacement_px": round(sum(seam) / len(seam), 2),
             "max_displacement_px": max(seam), "min_displacement_px": min(seam),
             "normal_step_mean_px": round(sum(normal) / len(normal), 2),
             "normal_step_max_px": max(normal),
             "rotation_delta_deg": [p["seam_6_to_1"]["rotation_delta_deg"] for p in per_unit],
             "note": "第 6 帧→第 1 帧是硬切：末帧已汇聚成 4×3 网格，首帧是散开状态，"
                     "两者位置差远大于正常步长，循环播放会看到一次跳变。未声明无缝。"},
    "interpolation": "缓动 0.5−0.5cos(πt) + 法向弧偏移；中间帧未渲染，仅 6 张关键帧。",
})
print("seam mean", round(sum(seam) / len(seam), 2), "normal mean", round(sum(normal) / len(normal), 2))
