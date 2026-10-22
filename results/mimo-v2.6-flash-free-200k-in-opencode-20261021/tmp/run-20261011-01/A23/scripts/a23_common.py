# -*- coding: utf-8 -*-
"""A23 shared: 12-unit camera composition, convergence easing, DSL emit.

Facts established by probe A23-probe-01 (real render, evidence kept in tmp):
- Snapshot background defaults to transparent; explicit "transparent" works;
  returned PNG is RGBA with alpha=0 corners (real transparency).
- Transform matrix tuple (c,s,0,0,-s,c,0,0,0,0,1,0,0,0,0,1) with
  c=cos(rad(theta)), s=sin(rad(theta)) rotates the child CLOCKWISE on screen
  for positive theta (red end cap landed lower-right for +45 deg), matching
  the task's clockwise-degree convention. alignment="CENTER" rotates about
  the child's own center.
No machine paths are stored here; all paths passed from callers are relative
to the suite root.
"""
import math

FONT = "Noto Sans CJK SC"
FRAME = 600                      # animation frame canvas (px)
COVER_W, COVER_H = 1200, 800
EASE_EXP = 1.35                  # s(u) = (1-u)**1.35, ease-out convergence
U_STEP = 0.2                     # 6 keyframes => u = 0,.2,.4,.6,.8,1
MARGIN = 8                       # min canvas margin for rotated bbox

# Final composition = recognizable camera ("从结构到画面": structure->image).
# id, shape, w, h, radius (rect; 0=none; circle => w/2), color, final(cx,cy),
# scattered start (cx,cy,rot). rot degrees clockwise; circles keep rot 0.
UNITS = [
    dict(id="U01", name="body",        shape="rect",    w=340, h=230, radius=18,
         color="#1E293B", fx=300, fy=300, sx=352, sy=356, srot=-24),
    dict(id="U02", name="top_plate",   shape="rect",    w=260, h=34,  radius=8,
         color="#334155", fx=300, fy=168, sx=440, sy=78,  srot=18),
    dict(id="U03", name="viewfinder",  shape="rect",    w=96,  h=40,  radius=6,
         color="#0F172A", fx=380, fy=131, sx=95,  sy=455, srot=-22),
    dict(id="U04", name="flash",       shape="rect",    w=70,  h=26,  radius=4,
         color="#FACC15", fx=190, fy=215, sx=74,  sy=40,  srot=30),
    dict(id="U05", name="led",         shape="circle",  w=18,  h=18,  radius=9,
         color="#EF4444", fx=250, fy=215, sx=36,  sy=120, srot=0),
    dict(id="U06", name="shutter",     shape="circle",  w=34,  h=34,  radius=17,
         color="#22D3EE", fx=270, fy=140, sx=545, sy=225, srot=0),
    dict(id="U07", name="grip",        shape="rect",    w=44,  h=230, radius=8,
         color="#0B1220", fx=450, fy=300, sx=95,  sy=255, srot=-16),
    dict(id="U08", name="lens_outer",  shape="circle",  w=150, h=150, radius=75,
         color="#4F46E5", fx=300, fy=310, sx=150, sy=510, srot=0),
    dict(id="U09", name="lens_inner",  shape="circle",  w=88,  h=88,  radius=44,
         color="#0EA5E9", fx=300, fy=310, sx=470, sy=420, srot=0),
    dict(id="U10", name="lens_detail", shape="circle",  w=30,  h=30,  radius=15,
         color="#F59E0B", fx=272, fy=284, sx=500, sy=545, srot=0),
    dict(id="U11", name="bottom_plate", shape="rect",   w=340, h=26,  radius=6,
         color="#475569", fx=300, fy=428, sx=200, sy=66,  srot=-10),
    dict(id="U12", name="tripod",      shape="circle",  w=20,  h=20,  radius=10,
         color="#A78BFA", fx=300, fy=428, sx=355, sy=545, srot=0),
]


def ease(u):
    """Remaining offset fraction at u in [0,1]; ease-out convergence."""
    return (1.0 - u) ** EASE_EXP


def r2(x):
    """Round to 2 decimals for DSL + JSON consistency."""
    return float("%.2f" % x)


def frame_state(k):
    """Unit params for keyframe k (0..5): dict id -> (cx, cy, rot)."""
    s = ease(k * U_STEP)
    out = {}
    for u in UNITS:
        out[u["id"]] = (r2(u["fx"] + s * (u["sx"] - u["fx"])),
                        r2(u["fy"] + s * (u["sy"] - u["fy"])),
                        r2(u["srot"] * s))
    return out


def rot_matrix(rot):
    """Column-major 16-tuple; positive rot = clockwise (probe-verified)."""
    a = math.radians(rot)
    c, s = math.cos(a), math.sin(a)
    f = lambda v: ("%.8f" % v).rstrip("0").rstrip(".") or "0"
    return "(%s,%s,0,0,%s,%s,0,0,0,0,1,0,0,0,0,1)" % (
        f(c), f(s), f(-s), f(c))


def unit_dsl(u, cx, cy, rot):
    """Positioned (+Transform when rotated) DSL for one unit at pose."""
    w, h = u["w"], u["h"]
    l, t = r2(cx - w / 2.0), r2(cy - h / 2.0)
    inner = ('<SizedBox width="%g" height="%g"><DecoratedBox color="%s"'
             ' borderRadius="%g"/></SizedBox>'
             % (w, h, u["color"], u["radius"]))
    if abs(rot) > 0.01:
        inner = ('<Transform matrix="%s" alignment="CENTER">%s</Transform>'
                 % (rot_matrix(rot), inner))
    return ('<Positioned left="%g" top="%g" width="%g" height="%g">%s'
            '</Positioned>' % (l, t, w, h, inner))


def frame_dsl(k):
    """Full transparent 600x600 DSL for keyframe k (units in U01..U12 order)."""
    st = frame_state(k)
    body = "".join(unit_dsl(u, *st[u["id"]]) for u in UNITS)
    return ('<Snapshot type="png" background="transparent">'
            '<SizedBox width="%d" height="%d"><Stack alignment="TOP_LEFT"'
            ' clipBehavior="NONE">%s</Stack></SizedBox></Snapshot>'
            % (FRAME, FRAME, body))


def bbox_half(w, h, rot):
    """Rotated bbox half-size (superset formula valid for circles too)."""
    a = math.radians(abs(rot))
    c, s = math.cos(a), math.sin(a)
    return (w * c + h * s) / 2.0, (w * s + h * c) / 2.0


def check_bounds():
    """Assert every unit at every keyframe keeps its rotated bbox in canvas."""
    errs = []
    for k in range(6):
        st = frame_state(k)
        for u in UNITS:
            cx, cy, rot = st[u["id"]]
            hw, hh = bbox_half(u["w"], u["h"], rot)
            if (cx - hw < MARGIN or cx + hw > FRAME - MARGIN
                    or cy - hh < MARGIN or cy + hh > FRAME - MARGIN):
                errs.append("F%d %s bbox x[%.1f,%.1f] y[%.1f,%.1f]"
                            % (k + 1, u["id"], cx - hw, cx + hw,
                               cy - hh, cy + hh))
    return errs


def trajectories():
    """Per-ID adjacent-frame displacement / rotation deltas (rounded poses)."""
    frames = [frame_state(k) for k in range(6)]
    out = []
    for u in UNITS:
        steps = []
        for k in range(5):
            x0, y0, r0 = frames[k][u["id"]]
            x1, y1, r1 = frames[k + 1][u["id"]]
            steps.append(dict(
                from_frame=k + 1, to_frame=k + 2,
                dx=r2(x1 - x0), dy=r2(y1 - y0),
                displacement_px=r2(math.hypot(x1 - x0, y1 - y0)),
                d_rotation_deg=r2(r1 - r0)))
        out.append(dict(id=u["id"], steps=steps))
    return out


def seam_rows():
    """F6 -> F1 loop seam deltas per ID (round values, shortest rotation)."""
    f1, f6 = frame_state(0), frame_state(5)
    rows = []
    for u in UNITS:
        x1, y1, r1 = f1[u["id"]]
        x6, y6, r6 = f6[u["id"]]
        drot = (r1 - r6) % 360.0
        if drot > 180.0:
            drot -= 360.0
        step56 = math.hypot(x1 - x6, y1 - y6)  # F5->F6 actual
        x5, y5, r5 = frame_state(4)[u["id"]]
        step56 = math.hypot(x6 - x5, y6 - y5)
        rows.append(dict(
            id=u["id"],
            displacement_px=r2(math.hypot(x1 - x6, y1 - y6)),
            rotation_diff_deg=r2(drot),
            last_step_px=r2(step56),
            ratio_vs_last_step=r2(math.hypot(x1 - x6, y1 - y6) / step56
                                  if step56 else 0.0)))
    return rows


# ---------------- cover (1200x800 RGB, opaque) ----------------
COVER_BG = "#0B1220"
K = 0.78                          # composition scale on cover
CO_CENTER = (905.0, 390.0)


def cover_unit(u):
    """Scaled final-pose placement of unit u on the cover canvas."""
    cx = CO_CENTER[0] + (u["fx"] - 300) * K
    cy = CO_CENTER[1] + (u["fy"] - 300) * K
    return cx, cy, r2(u["w"] * K), r2(u["h"] * K), r2(u["radius"] * K)


def _text_el(l, t, w, h, text, size, color, bold=False, align="LEFT"):
    wt = ' fontStyle="BOLD"' if bold else ""
    return ('<Positioned left="%g" top="%g" width="%g" height="%g">'
            '<Text fontSize="%g" fontFamily="%s" color="%s" textAlign="%s"%s'
            ' lineHeight="1.28" text="%s"/></Positioned>'
            % (l, t, w, h, size, FONT, color, align, wt, text))


def _rect_at(l, t, w, h, fill, radius=0):
    return ('<Positioned left="%g" top="%g" width="%g" height="%g">'
            '<SizedBox width="%g" height="%g"><DecoratedBox color="%s"'
            ' borderRadius="%g"/></SizedBox></Positioned>'
            % (l, t, w, h, w, h, fill, radius))


def _ghost_el(cx, cy, w, h, fill, rad, op, rot=0.0):
    """Faint cover-only element. NOTE: Positioned must stay a direct Stack
    child (render error 'must be StackParentData'), so Opacity/Transform
    wrap the inner box, never the Positioned."""
    inner = ('<Opacity opacity="%g"><SizedBox width="%g" height="%g">'
             '<DecoratedBox color="%s" borderRadius="%g"/></SizedBox>'
             '</Opacity>' % (op, w, h, fill, rad))
    if abs(rot) > 0.01:
        inner = ('<Transform matrix="%s" alignment="CENTER">%s</Transform>'
                 % (rot_matrix(rot), inner))
    return ('<Positioned left="%g" top="%g" width="%g" height="%g">%s'
            '</Positioned>' % (r2(cx - w / 2), r2(cy - h / 2), w, h, inner))


def cover_dsl():
    els = [
        _rect_at(0, 0, COVER_W, COVER_H, COVER_BG),
        # left text block
        _text_el(80, 140, 560, 34, "OPEN-SNAPSHOT · 动画分镜交付", 24,
                 "#A5B4FC"),
        _rect_at(80, 190, 72, 6, "#6366F1", 3),
        _text_el(80, 206, 620, 118, "从结构到画面", 84, "#FFFFFF", bold=True),
        _text_el(80, 352, 620, 40, "12 个几何单元 · 6 帧透明关键帧", 26,
                 "#94A3B8"),
        _text_el(80, 396, 620, 40, "250ms/帧 · 循环周期 1500ms", 26,
                 "#94A3B8"),
        _text_el(80, 452, 660, 36, "主题：结构汇聚成图像 · 末帧构成相机图形",
                 24, "#64748B"),
        _text_el(80, 690, 560, 32, "Snapshot 类 DOM DSL 原生渲染", 22,
                 "#475569"),
        _text_el(80, 724, 620, 32,
                 "播放参数：timing.json / frame-data.json", 22, "#475569"),
    ]
    # right: the same 12-unit camera composition, scaled, rotation 0
    for u in UNITS:
        cx, cy, w, h, rad = cover_unit(u)
        els.append(_rect_at(r2(cx - w / 2), r2(cy - h / 2), w, h,
                            u["color"], rad))
    # ghost copies + trajectory dashes: dispersed "structure" converging in
    ghosts = [
        dict(u="U06", x=700.0, y=206.0, op=0.25, rot=0, tx=880, ty=270),
        dict(u="U12", x=1122.0, y=178.0, op=0.25, rot=0, tx=1010, ty=300),
        dict(u="U05", x=686.0, y=566.0, op=0.25, rot=0, tx=800, ty=440),
        dict(u="U10", x=1096.0, y=596.0, op=0.25, rot=0, tx=990, ty=470),
        dict(u="U04", x=722.0, y=648.0, op=0.22, rot=24, tx=840, ty=380),
    ]
    by_id = {u["id"]: u for u in UNITS}
    for g in ghosts:
        u = by_id[g["u"]]
        w, h, rad = r2(u["w"] * K), r2(u["h"] * K), r2(u["radius"] * K)
        els.append(_ghost_el(g["x"], g["y"], w, h, u["color"], rad,
                             g["op"], g["rot"]))
        # short dash pointing from ghost toward the composition
        dx, dy = g["tx"] - g["x"], g["ty"] - g["y"]
        ang = math.degrees(math.atan2(dy, dx))
        px = g["x"] + 0.62 * dx
        py = g["y"] + 0.62 * dy
        els.append(_ghost_el(px, py, 48, 3, "#64748B", 1.5, 0.55, ang))
    body = "".join(els)
    return ('<Snapshot type="png" background="%s">'
            '<SizedBox width="%d" height="%d"><Stack alignment="TOP_LEFT"'
            ' clipBehavior="NONE">%s</Stack></SizedBox></Snapshot>'
            % (COVER_BG, COVER_W, COVER_H, body))
