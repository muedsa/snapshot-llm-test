# -*- coding: utf-8 -*-
"""B03 case-04 · 摩尔纹科普展板 (1000x1400).

user_goal: 看见干涉条纹并理解成因——线距相同+微小错角=粗大条纹。
technique: 两层等距细线栅(6px线距)以不同角度叠放, ClipRect限定演示窗,
           组内按窗中心旋转(motif_rot矩阵); 条纹间距 D=p/sin(dtheta) 计算并标注。
数据: 主窗错角0.5°(D≈687.5px, 窗内<1周期), 对照窗10°(D≈34.6px);
      线距/线数/条纹间距均由脚本计算并断言。
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b03_common as C  # noqa: E402

W, H = 1000, 1400

NAVY = "#14213D"
PAPER = "#F2EDE0"
INK = "#23232B"
MAROON = "#8B1E2D"
PITCH = 6.0        # line pitch px (both grids identical)
THICK = 1.6        # line thickness px

MAIN_WIN = (40, 180, 920, 560)
CTRL_WIN = (40, 838, 920, 260)
THETA_MAIN = 0.5
THETA_CTRL = 10.0


def fringe(theta_deg):
    """moire fringe spacing for equal pitches: D = p / sin(dtheta)."""
    return PITCH / math.sin(math.radians(theta_deg))


def grid_lines(lx, ly, lw, lh, thick=THICK, color=INK):
    """horizontal parallel lines, LOCAL coords, pitch=PITCH.
    extent covers the local box; count = floor(lh/pitch)+1."""
    els = []
    n = int(lh / PITCH) + 1
    y = ly
    for _ in range(n):
        els.append(C.box(lx, y, lw, thick, color))
        y += PITCH
    return "".join(els), n


def facts():
    d_main = fringe(THETA_MAIN)
    d_ctrl = fringe(THETA_CTRL)
    assert abs(d_main - 687.5) < 0.1, d_main          # 6/sin0.5deg
    assert abs(d_ctrl - 34.56) < 0.05, d_ctrl          # 6/sin10deg
    assert d_ctrl * 18 < d_main                        # contrast is the lesson
    n_main, n_ctrl = None, None
    g_main, n_main = grid_lines(-90, -70, 1100, 700)
    g_ctrl, n_ctrl = grid_lines(-90, -110, 1100, 480)
    assert n_main == 117 and n_ctrl == 81, (n_main, n_ctrl)
    # window sizes vs fringe periods (honest captions)
    assert d_main > MAIN_WIN[3]                        # <1 period in main win
    periods_ctrl = CTRL_WIN[3] / d_ctrl
    assert 7.0 < periods_ctrl < 8.0, periods_ctrl       # ~7.5 periods visible
    return dict(d_main=d_main, d_ctrl=d_ctrl, n_main=n_main, n_ctrl=n_ctrl,
                periods_ctrl=periods_ctrl, g_main=g_main, g_ctrl=g_ctrl)


def window(x, y, w, h, theta, g_body, g_body2, title, params):
    """clip window: two grids rotated +-theta/2 about window center (local)."""
    cx, cy = w / 2.0, h / 2.0
    inner = (C.motif_rot(cx, cy, 0.0, [g_body], w, h)
             + C.motif_rot(cx, cy, theta, [g_body2], w, h))
    els = [C.box(x - 6, y - 6, w + 12, h + 12, "#FFFFFF", radius=10,
                 border="#C9BFA6", border_w=2)]
    els.append(C.clip_rect(x, y, w, h, inner))
    els.append(C.text(x, y - 40, w, 30, title, 21, NAVY, bold=True))
    els.append(C.text(x, y + h + 12, w, 26, params, 15, "#6B6355"))
    return "".join(els)


def main():
    f = facts()
    els = [C.box(0, 0, W, H, PAPER)]
    # header
    els.append(C.box(0, 0, W, 90, NAVY))
    els.append(C.text(48, 14, 700, 44, "摩尔纹：两组细线的干涉", 34, "#F6F3EA",
                      bold=True))
    els.append(C.text(48, 56, 800, 26,
                      "线距完全相同（6px），只错开一点角度，就长出粗大条纹",
                      18, "#A9BBD8"))
    els.append(C.text(48, 110, 904, 28,
                      "科技馆『光与错觉』展区 · 立板演示（虚构展项）", 16,
                      "#6B6355"))

    # main demo window: 0.5 deg offset
    wx, wy, ww, wh = MAIN_WIN
    els.append(window(wx, wy, ww, wh, THETA_MAIN, f["g_main"], f["g_main"],
                      "主演示：错角仅 0.5°",
                      "两层线距均 6px · 错角 0.5° · 条纹间距 ≈ %.0fpx "
                      "（= 6px ÷ sin0.5°）· 窗内不足 1 个条纹周期"
                      % f["d_main"]))
    # grid A/B chips
    els.append(C.box(wx, wy + wh - 34, 130, 26, "#FFFFFFE8", radius=8))
    els.append(C.text(wx + 10, wy + wh - 32, 130, 24,
                      "下层 栅A(0°)", 14, INK))
    els.append(C.box(wx + 142, wy + wh - 34, 150, 26, "#FFFFFFE8", radius=8))
    els.append(C.text(wx + 152, wy + wh - 32, 150, 24,
                      "上层 栅B(+0.5°)", 14, MAROON))

    # control window: 10 deg offset
    cx0, cy0, cw, ch = CTRL_WIN
    els.append(window(cx0, cy0, cw, ch, THETA_CTRL, f["g_ctrl"], f["g_ctrl"],
                      "对照：错角放大到 10°",
                      "同样 6px 线距 · 错角 10° · 条纹间距 ≈ %.1fpx "
                      "（= 6px ÷ sin10°）· 窗内约 %.1f 个周期"
                      % (f["d_ctrl"], f["periods_ctrl"])))

    # three-step explanation (grammar lesson: \n renders literally in the
    # text attribute — split lines into separate Text widgets)
    ey = 1180
    steps = [
        ("① 铺两组线", "栅A与栅B各自等距平行，", "线距都是 6px"),
        ("② 错开一点角", "把栅B转 θ 叠到栅A上，", "θ 越小条纹越粗"),
        ("③ 放大成条纹", "间距差沿垂直方向累积，", "粗条纹 = 6px ÷ sinθ"),
    ]
    for i, (t1, t2a, t2b) in enumerate(steps):
        x0 = 40 + i * 312
        els.append(C.box(x0, ey, 296, 110, "#FFFFFF", radius=12,
                         border="#C9BFA6"))
        els.append(C.text(x0 + 18, ey + 12, 260, 28, t1, 19, NAVY, bold=True))
        els.append(C.text(x0 + 18, ey + 46, 264, 26, t2a, 15, "#4A4438"))
        els.append(C.text(x0 + 18, ey + 74, 264, 26, t2b, 15, "#4A4438"))

    # interaction hint + footer
    els.append(C.box(40, 1306, 920, 40, "#E8EFD8", radius=10))
    els.append(C.text(56, 1314, 890, 28,
                      "动手试：用一张纸片盖住上层栅再松开——条纹随之出现与消失，"
                      "说明条纹来自两层的叠合而非印刷瑕疵。",
                      16, "#2E5A38", bold=True))
    els.append(C.footnote(40, 1356, 920,
                          "展项为虚构演示；条纹间距按理想等距线栅的几何关系估算，"
                          "实际观感随显示介质与观看距离变化",
                          align="CENTER"))

    body = "".join(els)
    ver = sys.argv[1] if len(sys.argv) > 1 else "v1"
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                       "drafts", "case-04-%s.snapshot" % ver)
    C.emit(os.path.normpath(out), body, W, H, bg=PAPER)
    print("facts ok: D(0.5deg)=%.1fpx D(10deg)=%.2fpx lines %d+%d"
          % (f["d_main"], f["d_ctrl"], f["n_main"], f["n_ctrl"]))


if __name__ == "__main__":
    main()
