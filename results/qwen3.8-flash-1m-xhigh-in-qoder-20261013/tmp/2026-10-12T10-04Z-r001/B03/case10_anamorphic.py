"""B03 case-10 站台预变形地贴 - anamorphic decals with a measured residual.

Real use: a metro platform floor decal that has to read straight to a passenger walking
the last 6 m. Perspective cannot be expressed by a 2D affine matrix, so each glyph gets
its own affine fitted (least squares) to the exact ray-plane projection of its corners;
the plate prints the worst-case residual in millimetres instead of claiming perfection.

Run: python tmp/<run_id>/B03/case10_anamorphic.py
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
from bkit import Sheet, MONO, tw, f, num  # noqa: E402
from snap import C, Node, Positioned, Text, Transform  # noqa: E402

TMP = ROOT / "tmp" / RUN / "B03"
W, H = 1000, 1000
INK, INK2, INK3 = "#141C22", "#41505A", "#75838C"
PAPER = "#F1EFE9"
FLOOR = "#DCD8CE"
TAPE = "#F2C14E"
DARK = "#12202B"
LINE = "#B7B0A2"

EYE_H = 1.65            # metres, passenger eye height
EYE_D = 6.0             # metres along the floor from the decal centre
FOCAL = 900.0           # px, a 55 mm-equivalent eye model
PRINT_MM_PER_M = 320.0  # the plate prints the decal at 1 : 3.125

TEXT_TARGET = "换乘 3 号线"
GLYPH_M = 0.18                # what one character should appear to be, metres tall
MAG = 2.5                     # magnification of the "as seen" panel, stated on the plate


def camera_basis():
    """Right/up/forward for an eye at (0, EYE_H, EYE_D) looking at the decal centre."""
    tgt = (0.0, 0.0, 0.0)
    c = (0.0, EYE_H, EYE_D)
    fv = (tgt[0] - c[0], tgt[1] - c[1], tgt[2] - c[2])
    L = math.sqrt(sum(v * v for v in fv))
    fwd = tuple(v / L for v in fv)
    right = (1.0, 0.0, 0.0)
    up = (fwd[1] * right[2] - fwd[2] * right[1],
          fwd[2] * right[0] - fwd[0] * right[2],
          fwd[0] * right[1] - fwd[1] * right[0])
    up = tuple(-v for v in up)
    return c, right, up, fwd


CAM, R, U, FW = camera_basis()


def project(p):
    """World point -> eye-panel pixel (origin at the panel centre)."""
    v = (p[0] - CAM[0], p[1] - CAM[1], p[2] - CAM[2])
    z = sum(a * b for a, b in zip(v, FW))
    if z <= 1e-6:
        return None
    x = sum(a * b for a, b in zip(v, R)) / z * FOCAL
    y = -sum(a * b for a, b in zip(v, U)) / z * FOCAL
    return x, y


def unproject(px, py, plane_y=0.0):
    """Eye-panel pixel -> point on the floor plane (ray-plane intersection)."""
    d = (R[0] * px / FOCAL - U[0] * py / FOCAL + FW[0],
         R[1] * px / FOCAL - U[1] * py / FOCAL + FW[1],
         R[2] * px / FOCAL - U[2] * py / FOCAL + FW[2])
    t = (plane_y - CAM[1]) / d[1]
    return (CAM[0] + t * d[0], plane_y, CAM[2] + t * d[2])


def fit_affine(src, dst):
    """Least-squares affine from source corners to destination points (2D)."""
    # solve [a b; c d] [x;y] + [e;f] = u by normal equations over the corner set
    n = len(src)
    Sx = sum(p[0] for p in src) / n
    Sy = sum(p[1] for p in src) / n
    Su = sum(p[0] for p in dst) / n
    Sv = sum(p[1] for p in dst) / n
    mxx = sum((p[0] - Sx) ** 2 for p in src) / n
    myy = sum((p[1] - Sy) ** 2 for p in src) / n
    mxy = sum((p[0] - Sx) * (p[1] - Sy) for p in src) / n
    bxu = sum((p[0] - Sx) * (q[0] - Su) for p, q in zip(src, dst)) / n
    byu = sum((p[1] - Sy) * (q[0] - Su) for p, q in zip(src, dst)) / n
    bxv = sum((p[0] - Sx) * (q[1] - Sv) for p, q in zip(src, dst)) / n
    byv = sum((p[1] - Sy) * (q[1] - Sv) for p, q in zip(src, dst)) / n
    det = mxx * myy - mxy * mxy
    a = (myy * bxu - mxy * byu) / det
    b = (mxx * byu - mxy * bxu) / det
    c = (myy * bxv - mxy * byv) / det
    d = (mxx * byv - mxy * bxv) / det
    e = Su - a * Sx - b * Sy
    ff = Sv - c * Sx - d * Sy
    return (a, b, c, d, e, ff)


def apply_affine(m, p):
    a, b, c, d, e, ff = m
    return (a * p[0] + b * p[1] + e, c * p[0] + d * p[1] + ff)


# --- target layout in the eye panel: the text a passenger should see, undistorted
def target_layout():
    size = GLYPH_M / EYE_D * FOCAL     # px in the eye panel: 0.18 m at 6 m
    glyphs = list(TEXT_TARGET)
    widths = [tw(g, size) for g in glyphs]
    total = sum(widths)
    out, x = [], -total / 2
    for g, w in zip(glyphs, widths):
        out.append((g, x + w / 2, 0.0, w, size))
        x += w
    return out, size


TARGETS, TSIZE = target_layout()
DECAL_SCALE = PRINT_MM_PER_M / 1000.0 * 900.0     # metres -> plate px for the print view

# --- solve each glyph: exact floor corners, then the affine that best prints them
plan, residuals = [], []
for g, cx, cy, gw, gh in TARGETS:
    src = [(0.0, 0.0), (gw, 0.0), (gw, gh), (0.0, gh)]
    floor_pts = []
    for sx, sy in src:
        p = unproject(cx + sx, cy + sy)
        floor_pts.append(p)
    # print view: floor metres -> plate px (top-down), y grows towards the viewer
    # decal-space px, centred on the decal: depth is measured from the eye's ground
    # point, so a floor-lying glyph comes out elongated towards the viewer
    dst = [(q[0] * DECAL_SCALE, -q[2] * DECAL_SCALE) for q in floor_pts]
    m = fit_affine(src, dst)
    worst = 0.0
    for (sx, sy), q in zip(src, dst):
        got = apply_affine(m, (sx, sy))
        worst = max(worst, math.hypot(got[0] - q[0], got[1] - q[1]))
    plan.append({"glyph": g, "matrix": m, "src": src, "dst": dst,
                 "floor": floor_pts, "w": gw, "h": gh})
    residuals.append(worst / DECAL_SCALE * 1000.0)     # mm on the real decal

WORST_MM = max(residuals)
assert WORST_MM < 25.0, residuals          # the fit must stay inside a printable tolerance
assert all(p["dst"][0][0] < p["dst"][1][0] for p in plan)

s = Sheet(W, H, min_font=16, bg=PAPER)
s.rect(0, 0, W, H, PAPER)
s.text("hdr", "站台预变形地贴", 48, 44, 40, INK, bold=True)
s.text("hdr", f"观察点：眼高 {EYE_H} m · 距地贴中心 {EYE_D:.0f} m · 视场 {FOCAL:.0f}px"
              f" · 目标字高 {GLYPH_M * 1000:.0f} mm", 50, 98, 20, INK2)
s.text("hdr", "每字单独拟合仿射矩阵；下方为按 1:3.125 打印的实际形状", 50, 126, 18,
       INK3)

# --- panel A: the decal as printed (top-down), each glyph drawn through its own matrix
AX, AY, AW, AH = 50, 176, 900, 420
s.rect(AX, AY, AW, AH, FLOOR, radius=8)
s.rect(AX, AY, AW, AH, "#00000000", border=f"2 SOLID {LINE}", radius=8)
for k in range(1, 10):
    s.line(AX + k * AW / 10, AY, AX + k * AW / 10, AY + AH, "#00000012", 1.0)
for k in range(1, 5):
    s.line(AX, AY + k * AH / 5, AX + AW, AY + k * AH / 5, "#00000012", 1.0)
cx0 = AX + AW / 2
cy0 = AY + AH * 0.62
for p in plan:
    a, b, c, d, e, ff = p["matrix"]
    m = (f"({num(a)},{num(c)},0,0,{num(b)},{num(d)},0,0,0,0,1,0,"
         f"{num(e)},{num(ff)},0,1)")
    tf = Transform(Text(p["glyph"], fontSize=f(TSIZE), color=DARK,
                        fontFamily=MONO, fontStyle="BOLD"),
                   matrix=m, alignment="TOP_LEFT")
    s.nodes.append(Positioned(tf, left=f(cx0), top=f(cy0)))
# the printed bounding frame of the decal, from the solved corners
xs = [q[0] for p in plan for q in p["dst"]]
ys = [q[1] for p in plan for q in p["dst"]]
s.rect(cx0 + min(xs) - 18, cy0 + min(ys) - 18, (max(xs) - min(xs)) + 36,
       (max(ys) - min(ys)) + 36, "#00000000", border=f"2 SOLID {TAPE}", radius=4)
s.text("panel", "打印形状（俯视，含每字仿射矩阵）", AX + 16, AY + AH - 30, 17, INK3)

# --- panel B: the same geometry pushed back through the camera = what the eye receives
BX, BY, BW, BH = 50, 626, 900, 208
s.rect(BX, BY, BW, BH, DARK, radius=8)
ox, oy = BX + BW / 2, BY + 78
for p in plan:
    # exact perspective image of the printed corners, drawn as a filled quad per glyph
    pts = []
    for fp in p["floor"]:
        pr = project((fp[0], 0.0, fp[2]))
        pts.append((ox + pr[0] * MAG, oy + pr[1] * MAG))
    # the clip path is in the child's own space, so it must be localised to the box
    ox0, oy0 = min(q[0] for q in pts), min(q[1] for q in pts)
    local = [(a - ox0, b - oy0) for a, b in pts]
    d = "M " + " L ".join(f"{f(a)} {f(b)}" for a, b in local) + " Z"
    s.nodes.append(Positioned(Node("ClipPath", {"path": d},
                                   [C(width=f(max(1, max(q[0] for q in local))),
                                      height=f(max(1, max(q[1] for q in local))),
                                      color=TAPE)]),
                              left=f(ox0), top=f(oy0)))
    if not p["glyph"].strip():
        continue
    # the glyph is drawn at the size of its own reconstructed footprint, so the tape
    # quad and the letter are the same measurement, not two approximations
    qh = max(q[1] for q in pts) - min(q[1] for q in pts)
    qc = (sum(q[0] for q in pts) / 4, sum(q[1] for q in pts) / 4)
    s.text("panel", p["glyph"], qc[0], qc[1] - qh * 0.5, max(16, int(qh)), DARK,
           align="center", bold=True, font=MONO)
s.text("panel", f"乘客实际看到的像（同一相机模型反投影，放大 {MAG}× 便于阅读）",
       BX, BY + BH + 8, 17, INK3)

# --- readout strip: the numbers a fabricator needs
rows = [("字形数", f"{len(plan)}"), ("单字仿射参数", "6 × " + str(len(plan))),
        ("最大拟合残差", f"{WORST_MM:.1f} mm"), ("允许公差", "±25 mm"),
        ("打印比例", "1:3.125"), ("地贴实际宽度",
                             f"{(max(xs) - min(xs)) / DECAL_SCALE:.2f} m")]
for i, (k, v) in enumerate(rows):
    x = 50 + (i % 3) * 306
    y = 878 + (i // 3) * 32
    s.text("spec", k, x, y, 17, INK3)
    s.text("spec", v, x + 128, y, 17, INK, font=MONO)

audit = s.audit()
print(json.dumps(audit, ensure_ascii=False))
assert audit["overlap_n"] == 0 and audit["outside_n"] == 0, audit
assert audit["below_min_font_n"] == 0, audit["below_min_font"]
dsl = s.dsl() + "\n"
(TMP / "case10-anamorphic.snapshot").write_text(dsl, encoding="utf-8")
(TMP / "case10-data.json").write_text(json.dumps(
    {"eye_height_m": EYE_H, "eye_distance_m": EYE_D, "focal_px": FOCAL,
     "print_scale_mm_per_m": PRINT_MM_PER_M, "target_text": TEXT_TARGET,
     "glyphs": [{"glyph": p["glyph"], "matrix": [round(v, 5) for v in p["matrix"]],
                 "residual_mm": round(r, 2),
                 "floor_corners_m": [[round(c, 4) for c in pt] for pt in p["floor"]]}
                for p, r in zip(plan, residuals)],
     "worst_residual_mm": round(WORST_MM, 2), "decal_width_m":
     round((max(xs) - min(xs)) / DECAL_SCALE, 3), "elements": s.elements()},
    ensure_ascii=False, indent=2), encoding="utf-8")
print("residuals mm", [round(r, 2) for r in residuals], "worst", round(WORST_MM, 2),
      "decal width m", round((max(xs) - min(xs)) / DECAL_SCALE, 3),
      "elements", s.elements())
