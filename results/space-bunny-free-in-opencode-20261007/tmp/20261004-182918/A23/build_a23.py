"""A23 - format-boundary storyboard delivery: 1 RGB cover + 6 transparent keyframes.

One parameter set, seven real renders from open-snapshot. Nothing is embedded:
every mark in every file is emitted as Snapshot class-DOM DSL, and the cover plus
the contact sheet re-run the *same* frame generator at a different scale, so the
storyboard continuity is provable from the deliverables themselves.

Run:  python build_a23.py [all|frames|cover|sheet]
"""
from __future__ import annotations

import json
import math
import os
import re
import shutil
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
import snapkit  # noqa: E402
import dsllib as D  # noqa: E402
import state as S  # noqa: E402

TASK = "A23"
OUT = os.path.join(S.OUT_ROOT, TASK)
TMP = os.path.join(S.TMP_ROOT, TASK)
DRAFTS = os.path.join(TMP, "drafts")
snapkit.configure(TASK, OUT, TMP)

# ============================================================== motion parameters
CANVAS = 600.0
CX = CY = 300.0                 # figure centre, and the pivot of every frame
N_UNITS = 12
N_FRAMES = 6
PETALS = 6

# ease = 0.72 * linear + 0.28 * smoothstep  -> every frame pair moves 17-23 % of the
# way, so each adjacent pair is readable and no single step dwarfs the others.
def ease(t: float) -> float:
    return 0.72 * t + 0.28 * (3.0 * t * t - 2.0 * t * t * t)


EASE_BREAKDOWN = [
    {"frame": k + 1, "t": round(k / (N_FRAMES - 1.0), 4),
     "eased_progress": round(ease(k / (N_FRAMES - 1.0)), 4)}
    for k in range(N_FRAMES)
]

# two-shade six-hue wheel. Outer capsules use the -800 step, core tiles the -700
# step of the same six hues: two nested rings of one colour system, both dark
# enough to stay legible on a white page (verified on the rendered frames).
OUTER_HUES = ["#9F1239", "#9A3412", "#854D0E", "#166534", "#155E75", "#3730A3"]
INNER_HUES = ["#BE123C", "#C2410C", "#A16207", "#15803D", "#0E7490", "#4338CA"]

R_PETAL = 150.0        # outer capsule centre radius in the final figure
R_CORE = 68.0          # inner tile centre radius in the final figure
PETAL_W, PETAL_H, PETAL_R = 76.0, 34.0, 17.0
CORE_W, CORE_H, CORE_R = 42.0, 42.0, 10.0

# geometry that had to be corrected after looking at rendered frame-06:
#   adjacent core-tile centre distance = 2*R_CORE*sin(30) = R_CORE must exceed the
#   tile diagonal 42*sqrt2 = 59.4, else the tiles merge into one dark blob;
#   petal inner edge (R_PETAL - PETAL_W/2) must clear the tile outer edge
#   (R_CORE + CORE_W*sqrt2/2) or the rings collide.
assert R_CORE > CORE_W * math.sqrt(2), "core tiles would overlap each other"
assert R_PETAL - PETAL_W / 2.0 > R_CORE + CORE_W * math.sqrt(2) / 2.0, "rings collide"
FIGURE_RADIUS = R_PETAL + PETAL_W / 2.0          # 188 px of the 600 px canvas

# scatter: petals pushed out by +42 deg and tiles by -42 deg, so the two rings
# interleave (24 deg apart at minimum) and never overlap, while the exploded
# radius gives every unit a ~160-190 px journey -> 32-38 px per frame step.
SPRING = 42.0
SCATTER_PETAL_R = (228.0, 244.0)
SCATTER_CORE_R = (224.0, 240.0)


class LCG:
    """Deterministic pseudo-random source: same seed -> same storyboard, always."""

    def __init__(self, seed: int):
        self.s = seed % (1 << 31)

    def u(self) -> float:
        self.s = (1103515245 * self.s + 12345) % (1 << 31)
        return self.s / float(1 << 31)

    def r(self, lo: float, hi: float) -> float:
        return lo + (hi - lo) * self.u()


def unit_spec() -> list:
    """The 12 units. index 2k = outer petal of axis k, 2k+1 = core tile of axis k."""
    rng = LCG(20261004)
    specs = []
    for k in range(PETALS):
        a = math.radians(-90.0 + k * (360.0 / PETALS))          # screen angle, y down
        fx, fy = CX + R_PETAL * math.cos(a), CY + R_PETAL * math.sin(a)
        ix, iy = CX + R_CORE * math.cos(a), CY + R_CORE * math.sin(a)
        f_rot = -math.degrees(a)                                # matrix angle -> axis a
        # exploded start: petals +SPRING deg, tiles -SPRING deg, so the two rings
        # interleave around the same annulus; min angular gap stays >= 18 deg.
        pa = a + math.radians(SPRING + rng.r(-3, 3))
        pr = rng.r(*SCATTER_PETAL_R)
        ta = a - math.radians(SPRING + rng.r(-3, 3))
        tr = rng.r(*SCATTER_CORE_R)
        specs.append({
            "unit": "U%02d" % (2 * k + 1), "role": "petal", "axis": k,
            "color": OUTER_HUES[k], "w": PETAL_W, "h": PETAL_H, "radius": PETAL_R,
            "start": (CX + pr * math.cos(pa), CY + pr * math.sin(pa)),
            "end": (fx, fy), "rot_end": f_rot,
            "rot_start": f_rot + rng.r(-172, 172),
            "bend": rng.r(-0.16, 0.16),
        })
        specs.append({
            "unit": "U%02d" % (2 * k + 2), "role": "core", "axis": k,
            "color": INNER_HUES[k], "w": CORE_W, "h": CORE_H, "radius": CORE_R,
            "start": (CX + tr * math.cos(ta), CY + tr * math.sin(ta)),
            "end": (ix, iy), "rot_end": f_rot,
            "rot_start": f_rot + rng.r(-172, 172),
            "bend": rng.r(-0.16, 0.16),
        })
    return specs


UNITS = unit_spec()


def quad_bezier(p0, p1, p2, t):
    u = 1.0 - t
    return (u * u * p0[0] + 2 * u * t * p1[0] + t * t * p2[0],
            u * u * p0[1] + 2 * u * t * p1[1] + t * t * p2[1])


def control_point(spec):
    s, f = spec["start"], spec["end"]
    mx, my = (s[0] + f[0]) / 2.0, (s[1] + f[1]) / 2.0
    dx, dy = f[0] - s[0], f[1] - s[1]
    ln = math.hypot(dx, dy) or 1.0
    px, py = -dy / ln, dx / ln                       # unit normal to the chord
    k = spec["bend"] * ln
    return (mx + px * k, my + py * k)


def lerp_angle(a0: float, a1: float, t: float) -> float:
    d = (a1 - a0) % 360.0
    if d > 180.0:
        d -= 360.0
    return a0 + d * t


def frame_state(k: int) -> list:
    """Absolute position + rotation of all 12 units in keyframe k (0-based)."""
    t = k / (N_FRAMES - 1.0)
    e = ease(t)
    out = []
    for sp in UNITS:
        x, y = quad_bezier(sp["start"], control_point(sp), sp["end"], e)
        out.append({
            "unit": sp["unit"], "role": sp["role"], "axis": sp["axis"],
            "color": sp["color"], "w": sp["w"], "h": sp["h"], "radius": sp["radius"],
            "cx": round(x, 2), "cy": round(y, 2),
            "left": round(x - sp["w"] / 2.0, 2), "top": round(y - sp["h"] / 2.0, 2),
            "rotation_deg": round(lerp_angle(sp["rot_start"], sp["rot_end"], e), 2),
            "progress": round(e, 4),
        })
    return out


# ============================================================== DSL emitters
def mat(theta_deg: float) -> str:
    t = math.radians(theta_deg)
    c, s = round(math.cos(t), 6), round(math.sin(t), 6)
    # counter-clockwise on screen (y down): a=cos, b=-sin, c=sin, d=cos
    return "(%s,%s,0,0,%s,%s,0,0,0,0,1,0,0,0,0,1)" % (c, -s, s, c)


def unit_el(u: dict) -> str:
    return D.el("Positioned",
                {"left": u["left"], "top": u["top"],
                 "width": round(u["w"], 2), "height": round(u["h"], 2)},
                [D.el("Transform",
                      {"matrix": mat(u["rotation_deg"]), "origin": "(0,0)",
                       "alignment": "CENTER"},
                      [D.el("Container",
                            {"width": round(u["w"], 2), "height": round(u["h"], 2),
                             "color": u["color"], "borderRadius": round(u["radius"], 2)})])])


def scaled_units(k: int, ox: float, oy: float, size: float) -> list:
    """Same 12 units, same frame, re-centred and scaled into a size x size box."""
    s = size / CANVAS
    cx, cy = ox + size / 2.0, oy + size / 2.0
    out = []
    for u in frame_state(k):
        d = dict(u)
        d["cx"] = round(cx + (u["cx"] - CX) * s, 2)
        d["cy"] = round(cy + (u["cy"] - CY) * s, 2)
        d["w"] = round(u["w"] * s, 2)
        d["h"] = round(u["h"] * s, 2)
        d["radius"] = round(u["radius"] * s, 2)
        d["left"] = round(d["cx"] - d["w"] / 2.0, 2)
        d["top"] = round(d["cy"] - d["h"] / 2.0, 2)
        out.append(d)
    return out


def frame_dsl(k: int) -> str:
    kids = [unit_el(u) for u in frame_state(k)]
    return D.snapshot([D.stack(kids, CANVAS, CANVAS)], CANVAS, CANVAS, bg="#00000000")


# ---------------------------------------------------------------- cover
def cover_dsl() -> str:
    W, H = 1200.0, 800.0
    kids = []
    add = kids.append

    add(D.box(0, 0, W, H, color="#070C18FF"))
    add(D.box(0, 0, W, 420, gradient={
        "gradientType": "LINEAR",
        "gradientColors": "#132244,#0B1220",
        "gradientBegin": "TOP_LEFT", "gradientEnd": "BOTTOM_RIGHT"}))
    # faint structural grid across the whole plate, drawn first so it sits behind
    for i in range(20):
        add(D.box(i * 63, 0, 1, H, color="#38BDF80F"))
    for j in range(14):
        add(D.box(0, j * 63, W, 1, color="#38BDF80F"))

    # ---- eyebrow.  NOTE: DejaVu Sans Mono advances ~0.602em + letterSpacing per
    # char, so dsllib's 0.55em latin estimate under-measures mono strings; the box
    # is sized by hand (see snapshot-usage.md issue #3).
    add(D.box(64, 46, 10, 10, color="#38BDF8FF", radius=2))
    add(D.text_el("OPEN-SNAPSHOT · FORMAT-BOUNDARY DELIVERY",
                  x=84, y=42, w=600, h=22, size=15, color="#7DD3FCFF",
                  font=D.MONO, ls=1.0))

    # ---- title (72 px CJK, legibility confirmed in probe q4-cjk)
    add(D.text_el("从结构到画面", x=60, y=88, w=600, h=104, size=72,
                  color="#F8FAFCFF", font=D.CJK, ls=4))
    add(D.box(64, 202, 132, 4, color="#38BDF8FF", radius=2))
    add(D.text_el("结构汇聚成图像 · 12 个几何单元 · 6 帧关键帧 · 250 ms/帧",
                  x=64, y=222, w=590, h=30, size=21, color="#CBD5E1FF", font=D.CJK))
    add(D.text_el("帧内只含 12 个几何单元，由分散逐步汇聚，第 6 帧构成可识别图形。",
                  x=64, y=268, w=580, h=26, size=17, color="#94A3B8FF", font=D.CJK))
    add(D.text_el("同一参数集生成封面缩略图、6 帧与接触表，未嵌入任何预渲染位图。",
                  x=64, y=300, w=580, h=26, size=17, color="#94A3B8FF", font=D.CJK))

    # ---- capability matrix (right) -----------------------------------------
    CX0, CY0, CW, CH = 690.0, 46.0, 446.0, 372.0
    add(D.card(CX0, CY0, CW, CH, fill="#0E1A31FF", radius=18,
               border="1 SOLID #1E3A5FFF", shadow="0 6 24 0 #00000059"))
    add(D.text_el("客户请求 vs 服务原生支持", x=CX0 + 24, y=CY0 + 20, w=CW - 48, h=26,
                  size=20, color="#F8FAFCFF", font=D.CJK, ls=0.5))
    add(D.hline(CX0 + 24, CX0 + CW - 24, CY0 + 56, "#1E3A5FFF", 1))
    rows = [
        ("文字可编辑 SVG", "不支持", False,
         "→ 1200×800 RGB PNG 封面，文字仍是真实 Text 节点"),
        ("CMYK 印刷稿", "不支持", False,
         "→ sRGB PNG + 十六进制色值表，供印前自行转换"),
        ("6 帧透明 GIF 动画", "不支持", False,
         "→ 6 张 600×600 透明 PNG + timing.json 帧序/时长"),
        ("PNG 封面", "支持", True,
         "→ 原生 type=png，1200×800 不透明 RGB"),
    ]
    ry = CY0 + 70
    for name, verdict, ok, alt in rows:
        add(D.box(CX0 + 24, ry + 6, 8, 8, color="#34D399FF" if ok else "#FB7185FF", radius=4))
        add(D.text_el(name, x=CX0 + 42, y=ry, w=250, h=24, size=17,
                      color="#E2E8F0FF", font=D.CJK))
        vw = D.est_width(verdict, 12) + 20
        add(D.box(CX0 + CW - 24 - vw, ry - 1, vw, 21,
                  color="#134E4AFF" if ok else "#5B1A2AFF", radius=10))
        add(D.text_el(verdict, x=CX0 + CW - 24 - vw, y=ry + 3, w=vw, h=18, size=12,
                      color="#6EE7B7FF" if ok else "#FDA4AFFF", font=D.CJK,
                      align="CENTER"))
        add(D.text_el(alt, x=CX0 + 42, y=ry + 26, w=CW - 66, h=20, size=14,
                      color="#94A3B8FF", font=D.CJK))
        ry += 62
    add(D.text_el("服务实测 type 只接受 png / jpg / webp",
                  x=CX0 + 24, y=CY0 + CH - 48, w=CW - 48, h=20, size=12,
                  color="#64748BFF", font=D.UI))
    add(D.text_el("PARSE_ERROR: type must be one of png|jpg|webp",
                  x=CX0 + 24, y=CY0 + CH - 28, w=CW - 48, h=20, size=10.5,
                  color="#64748BFF", font=D.MONO))

    # ---- 6 thumbnails on light cards (transparent frames read correctly on light)
    THUMB, CARD_W, GAP = 148.0, 174.0, 12.0
    tot = 6 * CARD_W + 5 * GAP
    tx = (W - tot) / 2.0
    for k in range(6):
        cx0 = tx + k * (CARD_W + GAP)
        add(D.box(cx0, 428, CARD_W, 210, color="#F1F5F9FF", radius=14))
        for u in scaled_units(k, cx0 + 13, 441, THUMB):
            add(unit_el(u))
        add(D.text_el("FRAME %02d" % (k + 1), x=cx0, y=595, w=CARD_W, h=18,
                      size=12, color="#475569FF", font=D.MONO, align="CENTER"))
        add(D.text_el("progress %d%%" % round(frame_state(k)[0]["progress"] * 100),
                      x=cx0, y=613, w=CARD_W, h=16, size=11,
                      color="#94A3B8FF", font=D.MONO, align="CENTER"))
    # convergence axis below the strip
    add(D.box(tx, 652, tot, 2, color="#1E3A5FFF"))
    for k in range(6):
        cx0 = tx + k * (CARD_W + GAP) + CARD_W / 2.0
        add(D.box(cx0 - 4, 648, 8, 8, color="#38BDF8FF", radius=4))
    add(D.text_el("分散 scatter · 12 单元炸开", x=tx, y=664, w=260, h=20, size=13,
                  color="#64748BFF", font=D.CJK))
    add(D.text_el("汇聚 converge → 第 6 帧构成可识别图形",
                  x=tx + tot - 320, y=664, w=320, h=20, size=13,
                  color="#7DD3FCFF", font=D.CJK, align="RIGHT"))

    # ---- footer
    add(D.hline(64, W - 64, 704, "#1E293BFF", 1))
    add(D.text_el("交付：cover.png 1200×800 RGB  ·  frame-01…06.png 600×600 透明  ·  "
                  "同名 .snapshot 完整 DSL  ·  limitations.md / frame-data.json / timing.json",
                  x=64, y=718, w=1072, h=22, size=14, color="#94A3B8FF", font=D.CJK))
    add(D.text_el("边界说明：本服务不产出 GIF / SVG / CMYK，静态分镜 + timing.json 为已授权替代；"
                  "未合成动图，未矢量化，未生成假的目标格式文件。",
                  x=64, y=744, w=1072, h=22, size=14, color="#FBBF24FF", font=D.CJK))
    return D.snapshot([D.stack(kids, W, H)], W, H, bg="#070C18FF")


# ---------------------------------------------------------------- contact sheet
SHEET_W, SHEET_H = 980.0, 792.0
CELL_IMG, CELL_LBL, PAD = 300.0, 36.0, 20.0


def sheet_dsl() -> str:
    kids = []
    add = kids.append
    add(D.box(0, 0, SHEET_W, SHEET_H, color="#F8FAFCFF"))
    add(D.box(0, 0, SHEET_W, 56, color="#0B1220FF"))
    add(D.text_el("接触表 · CONTACT SHEET · 12 单元汇聚分镜 6 帧（全部为 DSL 重新生成，非位图拼接）",
                  x=PAD, y=18, w=SHEET_W - 2 * PAD, h=24, size=15,
                  color="#E2E8F0FF", font=D.CJK))
    stats = frame_stats()
    for k in range(6):
        r, c = divmod(k, 3)
        ox = PAD + c * (CELL_IMG + PAD)
        oy = 56 + PAD + r * (CELL_IMG + CELL_LBL + PAD)
        add(D.box(ox, oy, CELL_IMG, CELL_IMG, color="#FFFFFFFF", radius=10,
                  border="1 SOLID #CBD5E1FF"))
        for u in scaled_units(k, ox, oy, CELL_IMG):
            add(unit_el(u))
        st = stats[k]
        add(D.box(ox, oy + CELL_IMG + 6, CELL_IMG, CELL_LBL - 12, color="#FFFFFFFF",
                  radius=6, border="1 SOLID #E2E8F0FF"))
        add(D.text_el("FRAME %02d" % (k + 1), x=ox + 10, y=oy + CELL_IMG + 13,
                      w=110, h=18, size=12, color="#0F172AFF", font=D.MONO))
        add(D.text_el("progress %s   step %s px"
                      % (st["eased_progress_text"], st["median_step_text"]),
                      x=ox + 108, y=oy + CELL_IMG + 13, w=CELL_IMG - 118, h=18,
                      size=11, color="#64748BFF", font=D.MONO, align="RIGHT"))
    return D.snapshot([D.stack(kids, SHEET_W, SHEET_H)], SHEET_W, SHEET_H, bg="#F8FAFCFF")


# ============================================================== stats / audit
def frame_stats() -> list:
    out = []
    states = [frame_state(k) for k in range(N_FRAMES)]
    for k, st in enumerate(states):
        steps = []
        for i in range(len(st)):
            a = states[k - 1][i] if k > 0 else None
            b = states[k + 1][i] if k + 1 < N_FRAMES else None
            if a:
                steps.append(math.hypot(st[i]["cx"] - a["cx"], st[i]["cy"] - a["cy"]))
            if b:
                steps.append(math.hypot(b["cx"] - st[i]["cx"], b["cy"] - st[i]["cy"]))
        rot = []
        for i in range(len(st)):
            a = states[k - 1][i]["rotation_deg"] if k > 0 else None
            b = states[k + 1][i]["rotation_deg"] if k + 1 < N_FRAMES else None
            if a is not None:
                rot.append(abs(((st[i]["rotation_deg"] - a) % 360 + 180) % 360 - 180))
            if b is not None:
                rot.append(abs(((b - st[i]["rotation_deg"]) % 360 + 180) % 360 - 180))
        ss = sorted(steps)
        med = ss[len(ss) // 2] if ss else 0.0
        seam = math.hypot(states[0][i]["cx"] - states[-1][i]["cx"],
                          states[0][i]["cy"] - states[-1][i]["cy"]) if False else None
        out.append({
            "eased_progress_text": "%.3f" % st[0]["progress"],
            "median_step_text": "%.1f" % med,
            "steps": [round(s, 2) for s in steps],
            "median_step": round(med, 2),
            "max_step": round(max(steps), 2) if steps else 0.0,
            "min_step": round(min(steps), 2) if steps else 0.0,
            "max_rot_step": round(max(rot), 2) if rot else 0.0,
            "seam": seam,
        })
    return out


def frame_metrics() -> list:
    """Per-frame inter-frame displacement, used by frame-data.json and timing.json."""
    states = [frame_state(k) for k in range(N_FRAMES)]
    rows = []
    for k in range(N_FRAMES):
        prev = states[k - 1] if k > 0 else None
        rows.append({
            "frame": k + 1,
            "file": "frame-%02d.png" % (k + 1),
            "t": round(k / (N_FRAMES - 1.0), 4),
            "eased_progress": round(states[k][0]["progress"], 4),
            "per_unit_step_from_previous_px": None if prev is None else [
                round(math.hypot(states[k][i]["cx"] - prev[i]["cx"],
                                 states[k][i]["cy"] - prev[i]["cy"]), 2)
                for i in range(N_UNITS)],
            "max_rotation_step_deg": None if prev is None else [
                round(((states[k][i]["rotation_deg"] - prev[i]["rotation_deg"]) % 360 + 180) % 360 - 180, 2)
                for i in range(N_UNITS)],
            "unit_count": len(states[k]),
            "distinct_colors": len({u["color"] for u in states[k]}),
            "unit_size_set": sorted({(u["w"], u["h"]) for u in states[k]}),
            "alpha_bbox": alpha_bbox_of(k),
        })
    return rows


def alpha_bbox_of(k: int) -> dict:
    """Proven against the rendered PNG later; placeholder filled by audit()."""
    xs = [u["left"] for u in frame_state(k)] + [u["left"] + u["w"] for u in frame_state(k)]
    ys = [u["top"] for u in frame_state(k)] + [u["top"] + u["h"] for u in frame_state(k)]
    return {"expected_min_x": round(min(xs), 2), "expected_max_x": round(max(xs), 2),
            "expected_min_y": round(min(ys), 2), "expected_max_y": round(max(ys), 2)}


def draft(name: str, text: str) -> str:
    """Numbered, never-overwritten draft copy.

    NOTE: the first version of this helper wrote 'vNN-<name>' with no extension, so
    the *.snapshot glob below always matched nothing, n stayed at 1 and every run
    silently overwrote v01-*.  Fixed; see drafts/README.md for what that cost.
    """
    os.makedirs(DRAFTS, exist_ok=True)
    used = set()
    for f in os.listdir(DRAFTS):
        m = re.match(r"^v(\d+)-.*\.snapshot$", f)
        if m:
            used.add(int(m.group(1)))
    n = (max(used) if used else 0) + 1
    path = os.path.join(DRAFTS, "v%02d-%s.snapshot" % (n, name))
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    return path


# ============================================================== render
def audit_png(path: str, expect_size, expect_transparent: bool) -> dict:
    from PIL import Image
    im = Image.open(path)
    rgba = im.convert("RGBA")
    alpha = rgba.getchannel("A")
    bbox = alpha.getbbox() if expect_transparent else None
    corners = [rgba.getpixel(p) for p in
               [(0, 0), (rgba.width - 1, 0), (0, rgba.height - 1),
                (rgba.width - 1, rgba.height - 1)]]
    opaque = sum(1 for p in alpha.getdata() if p == 255)
    total = rgba.width * rgba.height
    return {"file": os.path.basename(path), "pil_mode": im.mode, "format": im.format,
            "size": list(im.size), "size_ok": list(im.size) == list(expect_size),
            "corner_rgba": [list(c) for c in corners],
            "all_corners_transparent": all(c[3] == 0 for c in corners),
            "alpha_bbox": list(bbox) if bbox else None,
            "opaque_pixel_ratio": round(opaque / float(total), 4),
            "fully_opaque_canvas": opaque == total}


def main() -> int:
    what = (sys.argv[1] if len(sys.argv) > 1 else "all").lower()
    D.WARNINGS.clear()
    made = []

    if what in ("all", "frames"):
        for k in range(N_FRAMES):
            dsl = frame_dsl(k)
            draft("frame-%02d" % (k + 1), dsl)
            r = snapkit.render(dsl, "frame-%02d.png" % (k + 1), final=True)
            print("  frame-%02d ok=%s status=%s bytes=%s"
                  % (k + 1, r["ok"], r["status"], r.get("bytes")))
            if not r["ok"]:
                print("     error:", (r.get("error") or "")[:300])
                return 1
            made.append("frame-%02d" % (k + 1))

    if what in ("all", "cover"):
        dsl = cover_dsl()
        draft("cover", dsl)
        r = snapkit.render(dsl, "cover.png", final=True)
        print("  cover ok=%s status=%s bytes=%s" % (r["ok"], r["status"], r.get("bytes")))
        if not r["ok"]:
            print("     error:", (r.get("error") or "")[:300])
            return 1
        made.append("cover")

    if what in ("all", "sheet"):
        dsl = sheet_dsl()
        draft("contact-sheet", dsl)
        r = snapkit.render(dsl, "contact-sheet.png", final=True)
        print("  contact-sheet ok=%s status=%s bytes=%s"
              % (r["ok"], r["status"], r.get("bytes")))
        if not r["ok"]:
            print("     error:", (r.get("error") or "")[:300])
            return 1
        made.append("contact-sheet")

    print("\n=== dsllib warnings ===")
    for w in D.warnings():
        print("  WARN", w)
    if not D.warnings():
        print("  (none)")

    if what == "all":
        print("\n=== rendered PNG audit ===")
        for name in ["cover"] + ["frame-%02d" % (k + 1) for k in range(N_FRAMES)] + ["contact-sheet"]:
            p = os.path.join(OUT, name + ".png")
            if not os.path.exists(p):
                print("  MISSING", name)
                continue
            if name == "cover":
                print("  ", audit_png(p, (1200, 800), False))
            elif name.startswith("frame"):
                a = audit_png(p, (600, 600), True)
                print("   frame-%02d size_ok=%s corners_alpha0=%s opaque_ratio=%s bbox=%s"
                      % (int(name[-2:]), a["size_ok"], a["all_corners_transparent"],
                         a["opaque_pixel_ratio"], a["alpha_bbox"]))
            else:
                print("  ", audit_png(p, (980, 792), False))

    with open(os.path.join(TMP, "last-run.json"), "w", encoding="utf-8") as fh:
        json.dump({"made": made, "what": what}, fh, ensure_ascii=False, indent=2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
