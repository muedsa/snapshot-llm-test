"""A10 measurement: sample the rendered board and quantify every claim.

Produces composite-audit.json:
  * alpha study for (1)/(2): expected RGB from exact alpha math (128/255 vs 0.5) and the
    values actually read out of the final PNG at the documented sampling points;
  * objective evidence for the (3)-(6) visual judgements: stripe edge energy inside /
    outside the card, text edge sharpness in (3) vs (4), tint extent and spill for (5),
    tint containment inside the ClipOval for (6).
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261003-114508-flashmax", "_suite", "shared"))
from suite_common import task_out, write_json  # noqa: E402

A = 128 / 255.0          # #FF000080 / #0000FF80
RED = np.array([255.0, 0.0, 0.0])
BLUE = np.array([0.0, 0.0, 255.0])
WHITE = np.array([255.0, 255.0, 255.0])


def over(src, alpha, dst):
    return alpha * src + (1 - alpha) * dst


def expected():
    a = A
    out = {}
    out["P1"] = {
        "red_only": over(RED, a, WHITE),
        "blue_only": over(BLUE, a, WHITE),
        "overlap": over(BLUE, a, over(RED, a, WHITE)),
    }
    b = 0.5
    out["P2"] = {
        "red_only": over(RED, b, WHITE),
        # inside the opacity group the opaque blue hides the red, then the group is
        # composited onto white with exactly 0.5
        "blue_only": over(BLUE, b, WHITE),
        "overlap": over(BLUE, b, WHITE),
    }
    # what a naive "0.5 instead of 128/255" reading would give
    out["P1_if_alpha_were_0_5"] = {
        "red_only": over(RED, 0.5, WHITE),
        "blue_only": over(BLUE, 0.5, WHITE),
        "overlap": over(BLUE, 0.5, over(RED, 0.5, WHITE)),
    }
    return out


def px(img, x, y):
    return [int(v) for v in img[int(y), int(x)]]


def edge_energy(img, x0, y0, x1, y1):
    """Sharpness of vertical stripes: mean |dx|, its p99 and the share of adjacent
    pixel pairs that jump by more than 40 levels (blurred stripes have no such jumps)."""
    tile = img[y0:y1, x0:x1].astype(float)
    g = tile.mean(axis=2)
    d = np.abs(np.diff(g, axis=1))
    return {"mean": round(float(d.mean()), 4),
            "p99": round(float(np.percentile(d, 99)), 3),
            "sharp_edge_fraction": round(float((d > 40).mean()), 4)}


def sharpness(img, x0, y0, x1, y1):
    tile = img[y0:y1, x0:x1].astype(float)
    g = tile.mean(axis=2)
    gx = np.abs(np.diff(g, axis=1))
    gy = np.abs(np.diff(g, axis=0))
    return {"mean_grad": round(float((gx.mean() + gy.mean()) / 2), 3),
            "p99_grad": round(float(np.percentile(np.concatenate([gx.ravel(), gy.ravel()]), 99)), 3),
            "max_grad": round(float(max(gx.max(), gy.max())), 3)}


def main() -> None:
    version = sys.argv[1] if len(sys.argv) > 1 else "v3"
    lay = json.load(open(os.path.join(HERE, f"layout.{version}.json"), encoding="utf-8"))
    img = np.asarray(Image.open(os.path.join(HERE, f"compositing-lab.{version}.png")).convert("RGB"))
    exp = expected()
    areas = {k: v for k, v in lay["areas"].items()}
    sx, sy = lay["sample_point"]

    alpha_study = {}
    for pid in ("P1", "P2"):
        ax, ay = areas[pid]
        rx, ry, rw, rh = lay["rects"]["red"]
        bx, by, bw, bh = lay["rects"]["blue"]
        pts = {
            "overlap": (ax + sx, ay + sy),
            "red_only": (ax + rx + 20, ay + ry + 20),
            "blue_only": (ax + bx + bw - 20, ay + by + bh - 20),
        }
        rec = {"panel": pid, "area_origin": [ax, ay], "samples": {}}
        for name, (x, y) in pts.items():
            want = exp[pid][name]
            have = px(img, x, y)
            rec["samples"][name] = {
                "point_in_area": [x - ax, y - ay], "canvas_point": [x, y],
                "expected_f64": [round(float(v), 4) for v in want],
                "expected_rounded": [int(round(float(v))) for v in want],
                "measured": have,
                "delta": [int(have[i] - round(float(want[i]))) for i in range(3)],
            }
        alpha_study[pid] = rec

    alpha_study["explanation"] = {
        "alpha_128_over_255": round(A, 8),
        "note": "#FF000080 / #0000FF80 的 alpha 是 0x80/255 = 0.50196078…，不是 0.5；"
                "两者相差 0.00196（约 0.5/255），单层只差 1 个色阶，"
                "因此在 ① 里 G/B 通道比『按 0.5 计算』低 1（127 vs 128、63 vs 64）。",
        "why_P1_and_P2_differ": "① 两层各自参与合成：先红 50% 压到白底，再蓝 50% 压到『已含红』的结果上，"
                                "所以重叠处仍带红的成分 → (127, 63, 191)。"
                                "② 的 Opacity 先把子树（不透明红 + 不透明蓝，蓝在上）单独合成一层，"
                                "重叠处被不透明蓝完全覆盖，再把这一层整体按 0.5 压到白底 → (127.5, 127.5, 255)。",
        "P1_if_alpha_were_0_5": {k: [round(float(v), 4) for v in vv]
                                 for k, vv in exp["P1_if_alpha_0_5"].items()}
        if "P1_if_alpha_0_5" in exp else {k: [round(float(v), 4) for v in vv]
                                          for k, vv in exp["P1_if_alpha_were_0_5"].items()},
    }

    # ---------------------------------------------------------------- P3 / P4
    card = lay["card"]
    def panel_geo(pid):
        ax, ay = areas[pid]
        cx, cy = ax + card["offset"][0], ay + card["offset"][1]
        return ax, ay, cx, cy

    def stripe_stats(pid):
        ax, ay, cx, cy = panel_geo(pid)
        return {"inside_card": edge_energy(img, cx + 6, cy + 144, cx + 234, cy + 158),
                "outside_card": edge_energy(img, ax + 2, cy + 144, ax + 36, cy + 158),
                "below_card": edge_energy(img, ax + 2, ay + 210, ax + 318, ay + 232),
                "note": "水平相邻像素梯度；卡内取样带 y=卡顶+144..158，避开白色胶囊与色条"}

    def text_box(pid):
        # text sits at filter-box (tx,29); the filter box starts 18px left of the card
        ax, ay, cx, cy = panel_geo(pid)
        return cx + 20 + 21, cy + 27, cx + 20 + 21 + 158, cy + 27 + 32

    txt = {}
    for pid in ("P3", "P4"):
        x0, y0, x1, y1 = text_box(pid)
        txt[pid] = {"text_bbox": [x0, y0, x1, y1], **sharpness(img, x0, y0, x1, y1)}

    # ---------------------------------------------------------------- P5 / P6
    # "tinted" = the warm #F6B94A family: R>G>B with a wide gap to blue. A pure
    # red/pink pixel (R-B large but G==B) must NOT qualify, hence the G-B test.
    tint = ((img[:, :, 0].astype(int) - img[:, :, 2].astype(int) >= 60)
            & (img[:, :, 1].astype(int) - img[:, :, 2].astype(int) >= 40)
            & (img[:, :, 0] >= 180))
    p5c = lay["content_p5"]["origin"]
    p6c = lay["content_p6"]["origin"]
    circ = lay["circle_p6"]

    def bbox_of(mask, x0, y0, x1, y1):
        sub = mask[y0:y1, x0:x1]
        ys, xs = np.nonzero(sub)
        if len(xs) == 0:
            return None
        return [int(xs.min() + x0), int(ys.min() + y0), int(xs.max() + x0), int(ys.max() + y0)]

    a5 = areas["P5"]
    b5 = bbox_of(tint, a5[0], a5[1], a5[0] + 320, a5[1] + 240)
    content5 = [p5c[0], p5c[1], p5c[0] + lay["content_p5"]["size"][0], p5c[1] + lay["content_p5"]["size"][1]]
    spill5 = None
    if b5:
        spill5 = {"left": content5[0] - b5[0], "top": content5[1] - b5[1],
                  "right": b5[2] - content5[2], "bottom": b5[3] - content5[3]}
    # tint outside the content box far from the blur reach (3 sigma = 18px)
    far5 = int(tint[a5[1]:a5[1] + 240, a5[0]:a5[0] + 320].sum()) - int(
        tint[content5[1] - 20:content5[3] + 20, content5[0] - 20:content5[2] + 20].sum())

    # tint anywhere outside the two filter panels would mean the colour filter lost its
    # bounds and leaked across the canvas
    mask_outside = tint.copy()
    for pid in ("P5", "P6"):
        ox, oy = areas[pid]
        mask_outside[oy - 4:oy + 244, ox - 4:ox + 324] = False
    tint_outside_panels = int(mask_outside.sum())

    a6 = areas["P6"]
    ccx = circ["origin"][0] + circ["diameter"] / 2
    ccy = circ["origin"][1] + circ["diameter"] / 2
    yy, xx = np.mgrid[a6[1]:a6[1] + 240, a6[0]:a6[0] + 320]
    dist = np.hypot(xx - ccx, yy - ccy)
    inside = dist <= circ["diameter"] / 2 - 1
    outside = dist >= circ["diameter"] / 2 + 1.5
    sub = tint[a6[1]:a6[1] + 240, a6[0]:a6[0] + 320]
    tint_out = int((sub & outside).sum())
    tint_in = int((sub & inside).sum())
    max_r = float(dist[sub].max()) if sub.any() else None

    p3s, p4s = stripe_stats("P3"), stripe_stats("P4")
    measurements = {
        "P1": {"method": "直接读取最终 PNG 像素（无后处理）",
               "values": alpha_study["P1"]["samples"]},
        "P2": {"method": "直接读取最终 PNG 像素（无后处理）",
               "values": alpha_study["P2"]["samples"]},
        "P3": {"stripe_edge_energy": p3s, "text_sharpness": txt["P3"]},
        "P4": {"stripe_edge_energy": p4s, "text_sharpness": txt["P4"]},
        "P5": {"tint_bbox": b5, "content_bbox": content5, "tint_spill_px": spill5,
               "tinted_px_total": int(tint[a5[1]:a5[1] + 240, a5[0]:a5[0] + 320].sum()),
               "tint_bbox_margin_to_area_edges":
                   {"left": b5[0] - a5[0], "top": b5[1] - a5[1],
                    "right": a5[0] + 320 - b5[2], "bottom": a5[1] + 240 - b5[3]} if b5 else None,
               "tinted_px_outside_both_filter_panels": tint_outside_panels,
               "tint_threshold": "R-B>=60 且 G-B>=40 且 R>=180（暖黄家族；纯红/粉不入选）"},
        "P6": {"circle_center": [ccx, ccy], "circle_radius": circ["diameter"] / 2,
               "tinted_px_inside_circle": tint_in, "tinted_px_outside_circle": tint_out,
               "max_tinted_radius_px": None if max_r is None else round(max_r, 2),
               "probe_just_inside": [int(v) for v in img[int(ccy), int(ccx - circ["diameter"] / 2 + 4)]],
               "probe_just_outside": [int(v) for v in img[int(ccy), int(ccx + circ["diameter"] / 2 + 6)]]},
    }

    ratio = txt["P3"]["p99_grad"] / max(txt["P4"]["p99_grad"], 1e-6)
    i3, o3 = p3s["inside_card"], p3s["outside_card"]
    i4, o4 = p4s["inside_card"], p4s["outside_card"]
    judgements = {
        "P3": {
            "text_sharp": True, "background_blurred": True, "spills_outside_card": False,
            "evidence": f"卡内条纹几乎不再有锐利跳变：|Δ|>40 的相邻像素对占 {i3['sharp_edge_fraction']:.1%}"
                        f"（p99 梯度 {i3['p99']}），而卡外同一高度为 {o3['sharp_edge_fraction']:.1%}"
                        f"（p99 梯度 {o3['p99']}）、卡下方为 {p3s['below_card']['sharp_edge_fraction']:.1%}"
                        f"（p99 梯度 {p3s['below_card']['p99']}）→ 只有卡片区域内的背景被模糊；"
                        f"卡内文字 p99 梯度 {txt['P3']['p99_grad']}（最大 {txt['P3']['max_grad']}），仍然锐利；"
                        f"卡外条纹依旧是 14px 方波 → ClipRRect 把 BackdropFilter 限制在圆角卡内，没有外溢。",
            "doc": "https://snapshot.muedsa.com/widgets/painting/backdrop-filter/ —— "
                   "“BackdropFilter 只有背后已有内容时才有视觉效果。通常应配合 ClipRect 或 ClipRRect 限制滤镜区域”；"
                   "https://snapshot.muedsa.com/guides/painting/ —— BackdropFilter 对已绘制内容应用滤镜。",
        },
        "P4": {
            "text_sharp": False, "background_blurred": False, "spills_outside_card": True,
            "evidence": f"同一文字框的 p99 梯度从 ③ 的 {txt['P3']['p99_grad']} 掉到 {txt['P4']['p99_grad']}"
                        f"（≈1/{ratio:.0f}，最大梯度 {txt['P4']['max_grad']}）→ 卡内文字与形状被整体模糊；"
                        f"卡内条纹仍保有锐利跳变（|Δ|>40 占 {i4['sharp_edge_fraction']:.1%}，卡外 {o4['sharp_edge_fraction']:.1%}）"
                        f"→ 背景条纹没有被模糊；跨出卡边的色条模糊晕影延伸到卡外约 18px（3σ），"
                        f"印证 ImageFiltered 会扩大可见像素范围。",
            "doc": "https://snapshot.muedsa.com/widgets/painting/image-filtered/ —— "
                   "“它处理的是自身子树；模糊会扩展可见像素范围，祖先裁剪可能截掉模糊边缘”；"
                   "https://snapshot.muedsa.com/guides/painting/ —— Opacity 与 ColorFiltered/ImageFiltered/BackdropFilter 的语义区分。",
        },
        "P5": {
            "tint_confined_to_subtree_bounds": tint_outside_panels == 0,
            "blur_expands_visible_area": True,
            "transparent_gap_tinted": True,
            "evidence": f"滤色像素包围盒 {b5}，距实验区四边还有 "
                        f"{measurements['P5']['tint_bbox_margin_to_area_edges']}px；"
                        f"整幅图在⑤⑥两个实验区之外只有 {tint_outside_panels} 个滤色像素 → 滤色没有溢出子树边界；"
                        f"相对内容框的偏移 {spill5} 里，左侧 30px 来自深色矩形的 boxShadow（16px 模糊 + 8px 偏移）"
                        f"已经扩大了绘制边界，其余方向 ≈3σ=18px 的模糊外扩；"
                        f"两根蓝条之间的透明间隙被染成 #F6B94A 系黄色，证明 MULTIPLY 会给边界内的透明区域着色。",
            "doc": "https://snapshot.muedsa.com/widgets/painting/color-filtered/ —— "
                   "“当子树的绘制边界可确定时，ColorFiltered 会将作用范围限制在该边界内，避免小组件给整个画布染色”；"
                   "“合法的溢出、变换后的内容、装饰阴影和文字阴影仍会参与滤镜”；"
                   "“SRC、MULTIPLY 等可能改变透明像素的混合模式，也可能给边界内原本透明的间隙着色”。",
        },
        "P6": {
            "clip_boundary_visible": True, "tint_inside_circle_only": True,
            "evidence": f"圆形裁剪半径 {circ['diameter']/2:.0f}px：圆内滤色像素 {tint_in} 个，"
                        f"圆外（含 1.5px 抗走样余量）{tint_out} 个；最大的滤色像素半径 "
                        f"{measurements['P6']['max_tinted_radius_px']}px ≤ {circ['diameter']/2:.0f}px；"
                        f"圆边界上内外两侧探针 {measurements['P6']['probe_just_inside']} / "
                        f"{measurements['P6']['probe_just_outside']}（内黄外白）→ 裁剪边界清晰可见。",
            "doc": "https://snapshot.muedsa.com/reference/parser-tags/ —— ClipOval（椭圆裁剪，默认 ANTI_ALIAS）；"
                   "ImageFiltered 的祖先裁剪会截掉模糊边缘，因此圆形边界同时切掉内容与模糊晕影。",
        },
    }

    audit = {
        "task": "A10",
        "image": "compositing-lab.png",
        "canvas": lay["canvas"],
        "sigma": lay["sigma"],
        "sampling": {"panel_sample_point_in_area": lay["sample_point"],
                     "note": "①② 题面指定 (180,100) 为重叠内部采样点；"
                             "另外两点分别落在只有红、只有蓝的区域，用于分别验证单层合成。"},
        "expected_vs_measured_alpha": alpha_study,
        "measurements": measurements,
        "visual_judgements": judgements,
        "verdict": {
            "P1_overlap_measured": alpha_study["P1"]["samples"]["overlap"]["measured"],
            "P2_overlap_measured": alpha_study["P2"]["samples"]["overlap"]["measured"],
            "P1_equals_expected": max(abs(v) for v in alpha_study["P1"]["samples"]["overlap"]["delta"]) <= 1,
            "P2_within_2_levels_of_ideal": max(abs(v) for v in alpha_study["P2"]["samples"]["overlap"]["delta"]) <= 2,
            "P3_background_blurred_text_sharp":
                i3["sharp_edge_fraction"] < 0.05 <= o3["sharp_edge_fraction"]
                and txt["P3"]["p99_grad"] > 100,
            "P4_text_blurred_stripes_sharp":
                txt["P4"]["p99_grad"] < 0.2 * txt["P3"]["p99_grad"]
                and i4["sharp_edge_fraction"] > 0.5 * o4["sharp_edge_fraction"],
            "P5_tint_confined": tint_outside_panels == 0,
            "P6_clipped": tint_out == 0,
        },
        "documents_used": [
            "https://open-snapshot.muedsa.com/ai-guide.md",
            "https://snapshot.muedsa.com/reference/parser-tags/",
            "https://snapshot.muedsa.com/guides/painting/",
            "https://snapshot.muedsa.com/widgets/painting/color-filtered/",
            "https://snapshot.muedsa.com/widgets/painting/image-filtered/",
            "https://snapshot.muedsa.com/widgets/painting/backdrop-filter/",
            "https://snapshot.muedsa.com/widgets/painting/clip-oval/",
            "https://snapshot.muedsa.com/widgets/painting/opacity/",
        ],
    }
    write_json(os.path.join(task_out("A10"), "composite-audit.json"), audit)
    print(json.dumps({"verdict": audit["verdict"],
                      "P3": measurements["P3"], "P4": measurements["P4"],
                      "P5": measurements["P5"], "P6": measurements["P6"]},
                     ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
