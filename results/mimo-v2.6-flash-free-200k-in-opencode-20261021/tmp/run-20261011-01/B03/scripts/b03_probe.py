# -*- coding: utf-8 -*-
"""B03 shared capability probes (case_id=null requests, logged with rids
B03-probe-01..03). Validate doc claims before cases rely on them."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b03_common as C  # noqa: E402


def panel_title(x, y, s):
    return C.text(x, y, 420, 30, s, 20, "#222222", bold=True)


def probe1():
    """SWEEP / RADIAL gradients, shape=CIRCLE ring, ClipOval."""
    W, H = 1400, 500
    els = [C.box(0, 0, W, H, "#F4F1EA")]
    # A: SWEEP gradient disc
    els.append(panel_title(30, 24, "A SWEEP gradient (0..2pi)"))
    els.append(C.grad(30, 70, 360, 360,
                      C.col("#1B3A6B", "#E4572E", "#F4B942", "#2E8B57",
                            "#1B3A6B"),
                      gtype="SWEEP", radius=180, start_angle=0,
                      end_angle=6.283185))
    els.append(C.circle(210, 250, 60, "#F4F1EA"))
    # B: RADIAL gradient with focal
    els.append(panel_title(430, 24, "B RADIAL focal"))
    els.append(C.grad(430, 70, 360, 360,
                      C.col("#FFF3BF", "#C1502E", "#3A1D5A"),
                      gtype="RADIAL", radius=180, center="(0.5,0.5)",
                      gradient_radius=0.62, focal="(0.32,0.30)",
                      focal_r=0.2))
    # C: shape=CIRCLE ring (border only)
    els.append(panel_title(830, 24, "C shape=CIRCLE border ring"))
    els.append('<Positioned left="860" top="100" width="220" height="220">'
               '<Container width="220" height="220" shape="CIRCLE"'
               ' color="#00000000" border="6 SOLID #1B6B4D"'
               ' transform="%s"/></Positioned>'
               % C.rot_matrix(10))
    els.append(C.text(840, 330, 260, 30, "Container transform 10°",
                     13, "#555555", align="CENTER"))
    # D: ClipOval over grid (inner coords LOCAL to the clip box)
    els.append(panel_title(1120, 24, "D ClipOval over grid"))
    grid = []
    for i in range(11):
        grid.append(C.box(0, i * 36, 250, 6, "#1B3A6B"))
        grid.append(C.box(i * 25, 0, 6, 360, "#E4572E"))
    els.append(C.clip_oval(1120, 70, 250, 360, "".join(grid)))
    els.append(C.footnote(30, H - 34, 900,
                          "B03 probe-01 · capability validation sheet"))
    return W, H, "".join(els), "#FFFFFF"


def probe2():
    """textShadow RGB split, STROKE outline, letterSpacing, fontFeatures,
    decorationLineStyle probe."""
    W, H = 1400, 520
    els = [C.box(0, 0, W, H, "#101014")]
    els.append(panel_title(30, 24, ""))  # placeholder replaced below
    els[1] = C.text(30, 20, 600, 34, "A chromatic textShadow (±10px)",
                    20, "#F0EDE6", bold=True)
    els.append(C.text(30, 64, 660, 120, "潮汐回声 TIDE ECHO", 64, "#FFFFFF",
                      bold=True, shadow="10 0 3 #FF2D55AA,-10 0 3 #2DE0FFAA",
                      letter_space=6))
    els.append(C.text(30, 196, 640, 60, "letterSpacing=6 · 文字色差重影", 30,
                      "#8CF0D8", letter_space=6))
    els.append(C.text(30, 270, 640, 60, "B foregroundMode=STROKE", 20,
                      "#F0EDE6", bold=True))
    els.append(C.text(30, 306, 640, 90, "空心描边字 OUTLINE", 54, "#00000000",
                      stroke="#F4B942", stroke_w=3, bold=True))
    els.append(C.text(30, 402, 640, 40, "C fontFeatures smcp + tnum", 20,
                      "#F0EDE6", bold=True))
    els.append(C.text(30, 440, 640, 50, "SmallCaps 1234567890", 30,
                      "#F4B942", features="smcp tnum", letter_space=2))
    els.append(C.text(740, 270, 620, 40, "D decoration line style", 20,
                      "#F0EDE6", bold=True))
    # decoration line style probe: DASHED not in decoration enum
    # (allowed: NONE/UNDERLINE/OVERLINE/LINE_THROUGH per service 400);
    # style test via decorationLineStyle on a valid UNDERLINE
    els.append('<Positioned left="740" top="310" width="620" height="60">'
               '<Text fontSize="30" fontFamily="%s" color="#2DE0FF"'
               ' text="decorationLineStyle=DASHED probe" decoration="UNDERLINE"'
               ' decorationLineStyle="DASHED" decorationColor="#2DE0FF"'
               ' decorationThickness="2"/></Positioned>' % C.FONT)
    els.append(C.text(740, 380, 620, 40, "E wordSpacing + maxLines", 20,
                      "#F0EDE6", bold=True))
    els.append(C.text(740, 418, 620, 90,
                      "word  spacing  rhythm · 多行文本 maxHeight", 26,
                      "#CDE0C4", word_space=10, line_h=1.5))
    return W, H, "".join(els), "#101014"


def probe3():
    """ImageFiltered blur, ColorFiltered blend, 45° seg, iso, dash."""
    W, H = 1400, 500
    els = [C.box(0, 0, W, H, "#F4F1EA")]
    els.append(C.text(30, 20, 500, 34, "A ImageFiltered blur (sigma 6)", 20,
                      "#222222", bold=True))
    blobs = "".join(C.circle(60 + i * 55, 100, 40, "#E4572E")
                    for i in range(6))
    els.append(C.clip_rect(30, 64, 420, 220,
                           C.blur(0, 0, 420, 220, blobs, 6),
                           clip="ANTI_ALIAS"))
    els.append(C.text(30, 300, 460, 80,
                      "模糊层：内容仍由 DSL 生成，\n高斯由 ImageFiltered 施加",
                      16, "#555555", line_h=1.5))
    els.append(C.text(500, 20, 500, 34, "B ColorFiltered MULTIPLY", 20,
                      "#222222", bold=True))
    inner = (C.box(0, 0, 420, 220, "#FFFFFF")
             + C.text(16, 20, 390, 40, "白底黑字", 30, "#101014", bold=True)
             + C.circle(120, 136, 60, "#E4572E")
             + C.circle(300, 136, 60, "#1B6B4D"))
    els.append(C.color_filter(500, 64, 420, 220, inner, "#3A1D5A",
                              "MULTIPLY"))
    els.append(C.text(500, 300, 420, 60, "同内容施加混合前后可对照", 16,
                      "#555555"))
    els.append(C.text(970, 20, 400, 34, "C 45° seg / D iso / E dash", 20,
                      "#222222", bold=True))
    els.append(C.seg(980, 90, 1140, 250, 10, "#1B3A6B"))   # exact 45°
    els.append(C.seg(1140, 90, 980, 250, 10, "#E4572E"))
    els.append(C.text(970, 262, 300, 30, "|dx|=|dy| exact 45°", 14,
                      "#555555"))
    # iso mini cube
    o = (1080, 360)
    pts = [C.iso(o[0], o[1], 0, 0, 0, 40), C.iso(o[0], o[1], 3, 0, 0, 40),
           C.iso(o[0], o[1], 3, 2, 0, 40), C.iso(o[0], o[1], 0, 2, 0, 40)]
    els.append(C.poly(pts, 4, "#1B6B4D"))
    els.append(C.poly([pts[0], C.iso(o[0], o[1], 0, 0, 2, 40)], 4, "#1B3A6B"))
    els.append(C.poly([pts[1], C.iso(o[0], o[1], 3, 0, 2, 40)], 4, "#1B3A6B"))
    els.append(C.dash_line(1210, 100, 1360, 260, "#8A4028", dash=10, gap=7,
                           thick=3))
    els.append(C.text(1200, 380, 180, 30, "E 程序化虚线", 14, "#555555"))
    els.append(C.footnote(30, H - 34, 900,
                          "B03 probe-03 · capability validation sheet"))
    return W, H, "".join(els), "#FFFFFF"


PROBES = {1: probe1, 2: probe2, 3: probe3}


def main():
    n = int(sys.argv[1])
    w, h, body, bg = PROBES[n]()
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                       "drafts", "probe-0%d.snapshot" % n)
    C.emit(os.path.normpath(out), body, w, h, bg=bg)


if __name__ == "__main__":
    main()
