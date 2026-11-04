# -*- coding: utf-8 -*-
"""A13: brand mark - two directions, 512x512 transparent previews."""
from __future__ import annotations

import os
import sys
from pathlib import Path

SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "")
sys.path.insert(0, str(SUITE_ROOT / "tmp" / RUN_ID / "_suite" / "scripts"))
import dslkit as K  # noqa: E402
import snapshot_api as api  # noqa: E402

TASK = "A13"
OUT = SUITE_ROOT / "outputs" / RUN_ID / TASK
TMP = SUITE_ROOT / "tmp" / RUN_ID / TASK
PREV = TMP / "previews"
OUT.mkdir(parents=True, exist_ok=True)
PREV.mkdir(parents=True, exist_ok=True)

STATE = dict(direction="", chosen="")

def alpha_hex(color, a):
    return f"{color}{a:02X}"

def mark_a(x, y, s, mode="color"):
    """diagonal cascade of three rounded squares + core dot (4 components)"""
    def d(v):
        return v * s
    if mode == "color":
        layers = [("#101826", 0.90), ("#2F6BFF", 0.78), ("#FFB020", 0.86)]
        core = "#FFFFFF"
    else:
        layers = [("#000000", 0.90), ("#000000", 0.78), ("#000000", 0.86)]
        core = "#000000"
    out = []
    geo = [(80, 80, 260, 56), (150, 120, 210, 44), (196, 190, 170, 36)]
    for (gx, gy, size, r), (color, a) in zip(geo, layers):
        out.append(K.rect(x + d(gx), y + d(gy), d(size), d(size),
                          color=alpha_hex(color, int(round(a * 255))), radius=d(r)))
    out.append(K.rect(x + d(272), y + d(272), d(56), d(56), color=core, radius=d(28)))
    return "".join(out)

def mark_b(x, y, s, mode="color"):
    """three stacked bars pierced by a vertical light beam (4 components)"""
    def d(v):
        return v * s
    if mode == "color":
        bars = [("#2F6BFF", 0.92), ("#101826", 0.92), ("#FFB020", 0.92)]
        beam = "#FFFFFF"
    else:
        bars = [("#000000", 0.92)] * 3
        beam = "#000000"
    out = []
    geo = [(84, 128, 344, 76), (84, 232, 268, 76), (84, 336, 190, 76)]
    for (gx, gy, w, h), (color, a) in zip(geo, bars):
        out.append(K.rect(x + d(gx), y + d(gy), d(w), d(h),
                          color=alpha_hex(color, int(round(a * 255))), radius=d(14)))
    out.append(K.rect(x + d(300), y + d(84), d(52), d(376), color=beam, radius=d(26)))
    return "".join(out)

W = H = 512
logger = api.TaskLogger(TASK, TMP)
for name, fn in (("preview-a", mark_a), ("preview-b", mark_b)):
    parts = [fn(0, 0, 1.0, "color")]
    dsl = K.document(W, H, parts, background=None)
    snap = PREV / f"{name}.snapshot"
    snap.write_text(dsl, encoding="utf-8")
    rec = logger.render(snap, PREV / f"{name}.png", f"{name}")
    print(name, rec["http_status"], rec["response_bytes"], rec["elapsed_s"],
          api.measure_png(PREV / f"{name}.png"))
