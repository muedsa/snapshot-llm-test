"""A10 data layer: layout table + the compositing arithmetic the picture will be checked
against. Nothing here touches the renderer; generate_a10.py draws from this file and
check_a10.py measures the delivered PNG against it, so a caption can never disagree with
a pixel.

Arithmetic conventions (documented in composite-audit.json):
  * 8-bit channel values are the service's, so a hex alpha of 80 is 128/255 = 0.501961,
    not 0.5; both are computed so the size of the difference is measured, not asserted.
  * source-over: out = src*a + dst*(1-a), per channel, rounded to nearest integer.
  * group Opacity(0.5): the subtree is flattened first (blue hides red in the overlap),
    then that single layer is composited at 0.5 over white.
  * ColorFiltered(MULTIPLY, c): per channel out = dst * c / 255 -- and where the layer is
    transparent, MULTIPLY leaves the *source* colour, so the filter's bounds turn solid c.
"""
import json
import math
import os
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RID = os.environ["SNAPSHOT_RUN_ID"]
TASK = "A10"
TEMP = ROOT / "tmp" / RID / TASK
OUT = ROOT / "outputs" / RID / TASK
TEMP.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)

W, H = 1440, 1100
AREA_W, AREA_H = 320, 240
SLOT_W, SLOT_H = 440, 420
COL_X = [40, 500, 960]
ROW_Y = [152, 584]
AREA_DX, AREA_DY = 60, 40           # white experiment area inside its slot
SIGMA = 6.0
CARD = [40, 40, 240, 160]           # area-local, radius 20
CARD_R = 20
STRIPE_PITCH, STRIPE_W = 16, 8
RED = "#FF0000"
BLUE = "#0000FF"
WHITE = "#FFFFFF"
AMBER = "#F6B94A"
DARK = "#1E293B"
DARKER = "#0F172A"
CYAN = "#22D3EE"
STRIPE = "#1D4ED8"


def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def over(src, sa, dst):
    """source-over with src alpha sa (0..1), src/dst as 0..255 tuples, rounded"""
    return tuple(round(src[i] * sa + dst[i] * (1 - sa)) for i in range(3))


def multiply(dst, c):
    return tuple(round(dst[i] * c[i] / 255) for i in range(3))


A80 = 128 / 255.0                    # what "#FF000080" actually means
WHITE_T = rgb(WHITE)

# ------------------------------------------------------------------ ① / ② overlap maths
c1_exact = over(rgb(BLUE), 0.5, over(rgb(RED), 0.5, WHITE_T))          # if alpha were 0.5
c1_real = over(rgb(BLUE), A80, over(rgb(RED), A80, WHITE_T))           # hex 80 = 128/255
c1_red_only = over(rgb(RED), A80, WHITE_T)
c1_blue_only = over(rgb(BLUE), A80, WHITE_T)

flat_blue = rgb(BLUE)                    # group is flattened: opaque blue wins the overlap
flat_red = rgb(RED)
c2_exact = over(flat_blue, 0.5, WHITE_T)
c2_red_only = over(flat_red, 0.5, WHITE_T)
c2_blue_only = c2_exact                  # both are the same single layer at 0.5

# ------------------------------------------------------------------ ⑤ / ⑥ multiply maths
m_dark = multiply(rgb(DARK), rgb(AMBER))
m_darker = multiply(rgb(DARKER), rgb(AMBER))
m_cyan = multiply(rgb(CYAN), rgb(AMBER))
m_white = multiply(WHITE_T, rgb(AMBER))          # == the filter colour itself

# ------------------------------------------------------------------ blur expectations
# Gaussian step edge: 10%..90% rise distance = 2*erf_inv(0.8)*sigma = 2.5631*sigma
RISE_PREDICTED = round(2 * 1.28155 * SIGMA, 2)


def phi(z):
    """standard normal CDF (0.5*erfc(-z/sqrt 2)), used for blurred step edges"""
    return 0.5 * math.erfc(-z / math.sqrt(2.0))


# A 50%-duty square wave of period P blurred by sigma keeps only its fundamental:
# amplitude factor exp(-2*pi^2*sigma^2/P^2), peak-to-peak = 2*(2/pi)*that.
RIPPLE_PP = 2 * (2 / math.pi) * math.exp(-2 * math.pi ** 2 * SIGMA ** 2 / STRIPE_PITCH ** 2)
STRIPE_RGB, WHITE_RGB = rgb(STRIPE), rgb(WHITE)
STRIPE_MEAN = tuple((STRIPE_RGB[i] + WHITE_RGB[i]) / 2 for i in range(3))     # blurred field
CARD_TINT_A = 0x1A / 255.0            # ③ card overlay #FFFFFF1A
CARD_FILL_A = 0xB3 / 255.0            # ④ card overlay #FFFFFFB3
C3_INSIDE_MEAN = tuple(round(CARD_TINT_A * 255 + (1 - CARD_TINT_A) * STRIPE_MEAN[i])
                       for i in range(3))
C3_INSIDE_RIPPLE = tuple(round((1 - CARD_TINT_A) * RIPPLE_PP * (WHITE_RGB[i] - STRIPE_RGB[i]), 1)
                         for i in range(3))
C4_INSIDE_RIPPLE = tuple(round((1 - CARD_FILL_A) * (WHITE_RGB[i] - STRIPE_RGB[i]), 1)
                         for i in range(3))
OUTSIDE_RIPPLE = tuple(round(WHITE_RGB[i] - STRIPE_RGB[i], 1) for i in range(3))

# ⑤: the filter layer is opaque amber across its 200x150 bounds, so ImageFiltered bleeds
# amber past the violet box. The naive model (a Gaussian step centred on the box edge,
# value at distance d = phi(-d/sigma)*amber + (1-)*white) is what BLEED_NAIVE below holds --
# probe_a10.py measured the real response and rejected it: the decay is Gaussian (sigma ~5.2)
# but centred ~15px OUTSIDE the box edge, so the audit asserts the shape of the halo
# (still amber at 6px, white by 30px, 10-90% rise ~ sigma*2.56) instead of that model.
AMBER_RGB, GAP = rgb(AMBER), rgb(WHITE)
BLEED_NAIVE = {str(d): [round(phi(-d / SIGMA) * AMBER_RGB[i] + (1 - phi(-d / SIGMA)) * GAP[i], 1)
                        for i in range(3)] for d in (6, 12, 30)}
# the 7px cyan ring blurred by sigma=6 keeps only erf(3.5/(sigma*sqrt2)) of its own colour
RING_STROKE = 7.0
RING_RET = math.erf((RING_STROKE / 2) / (SIGMA * math.sqrt(2.0)))
RING_BLURRED = [round(RING_RET * m_cyan[i] + (1 - RING_RET) * AMBER_RGB[i]) for i in range(3)]

CONTENT_ORIGIN, CONTENT_SIZE = [60, 45], [200, 150]      # area-local, as drawn
CIRCLE_C = [CONTENT_ORIGIN[0] + CONTENT_SIZE[0] / 2, CONTENT_ORIGIN[1] + CONTENT_SIZE[1] / 2]
CIRCLE_R = 100


def canvas_point(cell_no, content_xy):
    """content-box-local -> canvas pixel, for cells 5/6 which share the content box"""
    c = next(x for x in cells if x["number"] == cell_no)
    return [c["area_origin"][0] + CONTENT_ORIGIN[0] + content_xy[0],
            c["area_origin"][1] + CONTENT_ORIGIN[1] + content_xy[1]]


def on_ring(content_xy):
    """how far a content-local point sits from the ring band centre (stroke 7 inside r22)"""
    return abs(math.hypot(content_xy[0] - 172, content_xy[1] - 22) - 18.5)


cells = []
for idx, (row, col, num, name) in enumerate([
        (0, 0, "①", "两个矩形各带 50% alpha"),
        (0, 1, "②", "不透明矩形放进 Opacity(0.5) 组"),
        (0, 2, "③", "圆角卡：只有背景被模糊"),
        (1, 0, "④", "圆角卡：文字与形状一起子树模糊"),
        (1, 1, "⑤", "MULTIPLY 之后再做子树高斯模糊"),
        (1, 2, "⑥", "⑤ 的效果限定在圆形裁剪区内")]):
    sx, sy = COL_X[col], ROW_Y[row]
    cells.append({
        "index": idx, "number": num, "name": name,
        "slot_rect": [sx, sy, SLOT_W, SLOT_H],
        "area_origin": [sx + AREA_DX, sy + AREA_DY],
        "area_size": [AREA_W, AREA_H],
    })

SAMPLE_LOCAL = [180, 100]
for c in cells:
    ax, ay = c["area_origin"]
    c["sample_canvas"] = [ax + SAMPLE_LOCAL[0], ay + SAMPLE_LOCAL[1]]

SAMPLES = [
    # cell, label, canvas point, expected, tolerance, what it proves
    ("①", "overlap", cells[0]["sample_canvas"], list(c1_real), 2,
     "两层各带 hex 80，逐层 source-over"),
    ("①", "red_only", [cells[0]["area_origin"][0] + 60, cells[0]["area_origin"][1] + 60],
     list(c1_red_only), 2, "单层 50% 红压在白底上"),
    ("①", "blue_only", [cells[0]["area_origin"][0] + 250, cells[0]["area_origin"][1] + 180],
     list(c1_blue_only), 2, "单层 50% 蓝压在白底上"),
    ("②", "overlap", cells[1]["sample_canvas"], list(c2_exact), 2,
     "组内先拍平，只剩纯蓝按 0.5 合成"),
    ("②", "red_only", [cells[1]["area_origin"][0] + 60, cells[1]["area_origin"][1] + 60],
     list(c2_red_only), 2, "拍平后红侧与①相差 1 级（hex 80 与 0.5 之差）"),
    ("②", "blue_only", [cells[1]["area_origin"][0] + 250, cells[1]["area_origin"][1] + 180],
     list(c2_blue_only), 2, "蓝侧即整层 0.5 的结果"),
    ("⑤", "dark_rect", canvas_point("⑤", [60, 45]), list(m_dark), 3,
     "MULTIPLY 后再模糊，离边 >=40px 处即精确值"),
    ("⑤", "amber_gap", canvas_point("⑤", [160, 64]), list(m_white), 3,
     "透明间隙被 MULTIPLY 染成实心滤色"),
    ("⑤", "ring_blurred", canvas_point("⑤", [157, 33]), RING_BLURRED, 12,
     "7px 青环经 sigma=6 后的保留值（含色相旋转）"),
    ("⑥", "unfiltered_dark", canvas_point("⑥", [15, 10]), list(rgb(DARK)), 2,
     "圆外是完全未滤镜的原图"),
    ("⑥", "unfiltered_ring", canvas_point("⑥", [187, 11]), list(rgb(CYAN)), 3,
     "青环跨圆界：界外仍是纯青 (34,211,238)"),
    ("⑥", "filtered_dark", canvas_point("⑥", [60, 45]), list(m_dark), 3,
     "圆内与⑤同点同值：裁剪只限定作用范围"),
]
# the two ring samples must sit on the stroke centre line; the ⑥ one must also be clear of
# the clip circle, otherwise it measures the filtered copy and the check proves nothing
assert on_ring([157, 33]) < 1.0 and on_ring([187, 11]) < 1.0
assert math.hypot(187 - (CIRCLE_C[0] - CONTENT_ORIGIN[0]),
                  11 - (CIRCLE_C[1] - CONTENT_ORIGIN[1])) > CIRCLE_R + 4

AX = {c["number"]: c["area_origin"] for c in cells}
_TY = CARD[1] + CARD[3] / 2 - 24          # where generate_a10.py puts the card caption
TEXT_BAND = [CARD[0], _TY, CARD[0] + CARD[2], _TY + 36]
HALO_CONTENT_X = 135
BOX_TOP_CANVAS_Y = cells[4]["area_origin"][1] + CONTENT_ORIGIN[1]
MEAS = {
    "note": "所有坐标由本文件常量推出，check_a10.py 不自带任何像素位置；"
            "expected 值与图上印的期望值同源",
    "samples": [{"cell": s[0], "label": s[1], "canvas": s[2], "expected": s[3],
                 "tolerance": s[4], "claim": s[5]} for s in SAMPLES],
    "area_geometry": [{"cell": c["number"], "expected_bbox": c["area_origin"] + c["area_size"]}
                      for c in cells],
    "area_geometry_method": {"lum_bright": 60, "row_fraction_min": 0.9,
                             "col_fraction_min": 0.9, "search_margin_px": 10,
                             "tolerance_px": 2,
                             "note": "整行/整列亮占比 >=0.9 才算实验区边缘，"
                                     "避免把区头上方的说明文字当成边界"},
    "ripple": {"channel": "R",
               "outside": {"cells": ["③", "④"], "row_area_y": 20, "x_range": [8, 32],
                           "expected_p2p": {"③": OUTSIDE_RIPPLE[0], "④": OUTSIDE_RIPPLE[0]}},
               "inside": {"cells": ["③", "④"], "row_area_y": 70, "x_range": [64, 96],
                          "expected_p2p": {"③": C3_INSIDE_RIPPLE[0],
                                           "④": C4_INSIDE_RIPPLE[0]}}},
    "card_edge": {"cell_3_rim": {"row_area_y": 70, "x_range": [30, 50], "lum_max_dark": 40,
                                 "expected_columns": [CARD[0], CARD[0] + 1],
                                 "tolerance_px": 1.5},
                  "cell_4_profile": {
                      # profiled along y across the card's TOP edge: the stripes oscillate
                      # along x, so averaging over whole 16px periods (x 64..256) is what
                      # makes the feather measurable at all
                      "col_range_area_x": [64, 256], "y_range": [10, 80],
                      "edge_area_y": CARD[1], "channel": "R",
                      "expected_rise_10_90_px": RISE_PREDICTED, "rise_tol_px": 2.5,
                      "plateau_outside_mean_R": round(STRIPE_MEAN[0]),
                      "plateau_inside_mean_R": round(
                          CARD_FILL_A * 255 + (1 - CARD_FILL_A) * STRIPE_MEAN[0])}},
    "text_band_gradient": {"area_rect": TEXT_BAND, "channel": "B", "rule": "③ / ④ >= 2.5",
                           "sharp_edge_counts_expected": {"③": "> 0", "④": "0"}},
    "arc_profile": {"cell": "⑥", "angle_deg": 220, "r_range": [88, 109],
                    "plateau_samples": 5, "channel": "B",
                    "step_window_r": [98, 106],
                    "inside": list(m_dark), "outside": list(rgb(DARK)),
                    "expected_rise_10_90_px_max": 3.0,
                    "note": "半径 88..100 段内值缓升（19→25）本身就是证据：模糊发生在裁剪"
                            "之前，滤镜场自己的梯度一直延续到圆界；台阶宽度只在紧邻边界的 "
                            "98..106 窗口内测",
                    "claim": "ClipOval 在滤镜之后裁剪：边界是硬边，不是 15px 羽化"},
    "filter_halo_profile": {
        "cell": "⑤", "content_x": HALO_CONTENT_X,
        "canvas_x": cells[4]["area_origin"][0] + CONTENT_ORIGIN[0] + HALO_CONTENT_X,
        "y_range": [BOX_TOP_CANVAS_Y - 39, BOX_TOP_CANVAS_Y - 2], "channel": "B",
        "box_top_canvas_y": BOX_TOP_CANVAS_Y, "amber_B": m_white[2], "white_B": 255,
        "assertions": {"B_at_minus_6_max": 100, "B_at_minus_30_min": 250,
                       "midpoint_offset_px_range": [8, 22]},
        "naive_step_model_rejected": BLEED_NAIVE,
        "claim": "ImageFiltered 的晕染越过滤镜盒外沿：6px 处仍是琥珀，30px 处回到白"},
}

plan = {
    "schema_version": 1, "path_base": "suite_root", "task_id": TASK, "run_id": RID,
    "canvas": [W, H],
    "layout": {"area": [AREA_W, AREA_H], "columns": 3, "rows": 2,
               "col_x": COL_X, "row_y": ROW_Y, "slot": [SLOT_W, SLOT_H],
               "area_origin_in_slot": [AREA_DX, AREA_DY],
               "min_gap_between_areas": COL_X[1] - (COL_X[0] + AREA_DX + AREA_W),
               "background": "#0A1120", "area_background": WHITE},
    "filters": {"sigmaX": SIGMA, "sigmaY": SIGMA, "tileMode": "CLAMP",
                "predicted_step_edge_rise_10_90_px": RISE_PREDICTED,
                "card": {"rect_in_area": CARD, "radius": CARD_R,
                         "text": "SHARP / BLUR", "text_font_size": 24},
                "stripe": {"pitch": STRIPE_PITCH, "width": STRIPE_W, "color": STRIPE,
                           "direction": "vertical", "spans_whole_area": True},
                "circle": {"center_area": CIRCLE_C, "radius": CIRCLE_R,
                           "clip_behavior": "ANTI_ALIAS"}},
    "shapes": {"red": {"xywh_in_area": [40, 40, 160, 120], "color": RED},
               "blue": {"xywh_in_area": [120, 80, 160, 120], "color": BLUE, "z": "above red"},
               "sample_point_in_area": SAMPLE_LOCAL,
               "content_box": {"xywh_in_area": CONTENT_ORIGIN + CONTENT_SIZE,
                               "used_by": ["⑤", "⑥"]},
               "content_rects": {"dark": {"xywh_in_content": [0, 5, 120, 80], "color": DARK,
                                          "shadow": "0 6 14 0 #00000066 NORMAL"},
                                 "darker": {"xywh_in_content": [95, 85, 105, 60],
                                            "color": DARKER},
                                 "ring": {"xywh_in_content": [150, 0, 44, 44], "color": CYAN,
                                          "border_px": 7, "band_radius": [15, 22]}}},
    "cells": cells,
    "measurements": MEAS,
    "predicted": {
        "note": "全部为按上面公式算出的期望值，check_a10.py 会在最终 PNG 上取同一点实测",
        "c1_alpha_meaning": {"hex_alpha": "80", "as_fraction": round(A80, 6),
                             "vs_half": round(A80 - 0.5, 6),
                             "percent_error": round((A80 - 0.5) / 0.5 * 100, 3)},
        "cell1_overlap": {"if_alpha_were_0.5": list(c1_exact),
                          "with_hex_80": list(c1_real),
                          "delta_levels": [c1_real[i] - c1_exact[i] for i in range(3)]},
        "cell1_red_only": list(c1_red_only),
        "cell1_blue_only": list(c1_blue_only),
        "cell2_overlap": list(c2_exact),
        "cell2_red_only": list(c2_red_only),
        "cell2_blue_only": list(c2_blue_only),
        "cell1_vs_cell2_overlap": [c2_exact[i] - c1_real[i] for i in range(3)],
        "multiply": {"filter_color": AMBER, "dark_rect": list(m_dark),
                     "darker_rect": list(m_darker), "cyan_ring": list(m_cyan),
                     "cyan_ring_after_sigma6": RING_BLURRED,
                     "cyan_ring_retention": round(RING_RET, 4),
                     "bleed_outside_box_naive_step_model": BLEED_NAIVE,
                     "white_or_gap": list(m_white),
                     "gap_rule": "MULTIPLY 在图层透明处留下源色，因此滤镜边界内的透明间隙"
                                 "会变成实心 #F6B94A（文档：部分混合模式也会给边界内的"
                                 "透明间隙着色）"},
    },
}
(TEMP / "plan_a10.json").write_text(json.dumps(plan, ensure_ascii=False, indent=1),
                                    encoding="utf-8")
(OUT / "composite-audit.json").write_text(json.dumps(plan, ensure_ascii=False, indent=1),
                                          encoding="utf-8")
print(json.dumps({"cells": len(cells), "min_gap": plan["layout"]["min_gap_between_areas"],
                  "c1_overlap_hex80": c1_real, "c1_overlap_half": c1_exact,
                  "c2_overlap": c2_exact, "c1_vs_c2": plan["predicted"]["cell1_vs_cell2_overlap"],
                  "rise_px": RISE_PREDICTED, "ripple_pp_factor": round(RIPPLE_PP, 4),
                  "inside_3_mean": list(C3_INSIDE_MEAN), "inside_3_ripple": C3_INSIDE_RIPPLE[0],
                  "inside_4_ripple": C4_INSIDE_RIPPLE[0], "outside_ripple": OUTSIDE_RIPPLE[0],
                  "ring_blurred": RING_BLURRED, "naive_bleed_6": BLEED_NAIVE["6"],
                  "multiply": {"dark": m_dark, "darker": m_darker, "cyan": m_cyan,
                               "gap": m_white}}, ensure_ascii=False))
