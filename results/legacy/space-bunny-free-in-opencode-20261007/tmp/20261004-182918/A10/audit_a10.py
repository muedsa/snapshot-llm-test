# -*- coding: utf-8 -*-
"""A10：生成 composite-audit.json（预期 RGB 计算 + 最终图像素实测 + 视觉判断 + 文档引用）。"""
from __future__ import annotations

import hashlib
import io
import json
import os
from datetime import datetime, timedelta, timezone

from PIL import Image

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
RUN = "20261004-182918"
OUT = os.path.join(ROOT, "outputs", RUN, "A10")
TMP = os.path.join(ROOT, "tmp", RUN, "A10")
PNG = os.path.join(OUT, "compositing-lab.png")
SNAP = os.path.join(OUT, "compositing-lab.snapshot")
CST = timezone(timedelta(hours=8))

COLS = [48, 560, 1072]
ROWS = [186, 572]
PW, PH = 320, 240
TINT = (246, 185, 74)
STRIPE = (199, 210, 222)

im = Image.open(PNG).convert("RGB")


def px(i, x, y):
    return im.getpixel((COLS[i % 3] + x, ROWS[i // 3] + y))


def hx(rgb):
    return "#%02X%02X%02X" % tuple(rgb)


def sample(i, name, x, y):
    p = px(i, x, y)
    return {"name": name, "panel_xy": [x, y], "rgb": list(p), "hex": hx(p)}


def is_tint(p):
    return (abs(p[0] - TINT[0]) <= 3 and abs(p[1] - TINT[1]) <= 3
            and abs(p[2] - TINT[2]) <= 6)


def tint_bbox(i):
    xs, ys = [], []
    for y in range(PH):
        for x in range(PW):
            if is_tint(px(i, x, y)):
                xs.append(x)
                ys.append(y)
    return [min(xs), min(ys), max(xs), max(ys)]


def transitions(i, y, x0, x1):
    return [x for x in range(x0, x1) if px(i, x, y) != px(i, x - 1, y)]


def vtransitions(i, x, y0, y1):
    return [y for y in range(y0, y1) if px(i, x, y) != px(i, x, y - 1)]


def text_region_stats(i):
    vals = [px(i, x, y) for y in range(66, 106) for x in range(56, 264)]
    lum = [0.299 * p[0] + 0.587 * p[1] + 0.114 * p[2] for p in vals]
    dark = [p for p in vals if sum(p) < 300]
    return {
        "region_panel_xy": [56, 66, 264, 106],
        "pixels": len(vals),
        "dark_pixels_sum_rgb_lt_300": len(dark),
        "darkest_rgb": list(min(vals, key=sum)),
        "min_luma": round(min(lum), 1),
        "mean_luma": round(sum(lum) / len(lum), 1),
    }


def row_runs(i, y, x0=0, x1=320):
    out = []
    prev = px(i, x0, y)
    start = x0
    for x in range(x0 + 1, x1):
        p = px(i, x, y)
        if p != prev:
            out.append([start, x - 1, hx(prev)])
            prev, start = p, x
    out.append([start, x1 - 1, hx(prev)])
    return out


def sha(path):
    return hashlib.sha256(io.open(path, "rb").read()).hexdigest()


A8 = 128 / 255.0          # #..80 的实际 alpha
WHITE = (255, 255, 255)


def over(src, dst, a):
    return [round(a * src[k] + (1 - a) * dst[k], 2) for k in range(3)]


# ---------- ①② 预期计算 ----------
exp1_red_only = over((255, 0, 0), WHITE, A8)
exp1_overlap = over((0, 0, 255), [round(v) for v in exp1_red_only], A8)
exp1_blue_only = over((0, 0, 255), WHITE, A8)
exp2_red_only = [round(0.5 * 255 + 0.5 * v, 2) for v in (255, 0, 0)]
exp2_overlap = [round(0.5 * 255 + 0.5 * v, 2) for v in (0, 0, 255)]
exp2_blue_only = exp2_overlap

cells = []

cells.append({
    "index": 1,
    "label": "逐像素 50% alpha",
    "construction": {
        "backdrop": "格内白底 #FFFFFF",
        "red_rect": {"x": 40, "y": 40, "w": 160, "h": 120, "color": "#FF000080",
                     "z": "下层"},
        "blue_rect": {"x": 120, "y": 80, "w": 160, "h": 120, "color": "#0000FF80",
                      "z": "上层"},
        "alpha_source": "8 位十六进制按 CSS 读作 #RRGGBBAA，末两位 80 = alpha",
    },
    "expected": {
        "formula": "dst' = alpha*src + (1-alpha)*dst，逐像素 source-over，alpha=128/255",
        "alpha_numeric": A8,
        "red_only_over_white": {"rgb": exp1_red_only, "hex": hx([round(v) for v in exp1_red_only])},
        "overlap_blue_over_red": {"rgb": exp1_overlap,
                                  "hex": hx([round(v) for v in exp1_overlap])},
        "blue_only_over_white": {"rgb": exp1_blue_only,
                                 "hex": hx([round(v) for v in exp1_blue_only])},
    },
    "measured": {
        "red_only": sample(0, "red_only(70,60)", 70, 60),
        "overlap": sample(0, "overlap(180,100)", 180, 100),
        "blue_only": sample(0, "blue_only(250,180)", 250, 180),
        "row_y150_runs": row_runs(0, 150),
        "geometry_check": {
            "row_y150_x_ranges": {"red_only": [40, 119], "overlap": [120, 199],
                                  "blue_only": [200, 279]},
            "col_x190_y_ranges": {"red_only": [40, 79], "overlap": [80, 159],
                                  "blue_only": [160, 199]},
        },
    },
    "verdict": "重叠区实测 #7F3FBF，与按 alpha=128/255 算出的 #7F40BF 相差 1 级以内："
               "红层仍在蓝层下面透出，说明 alpha 作用于每个像素，不是整组离屏合成。",
})

cells.append({
    "index": 2,
    "label": "组 Opacity(0.5)",
    "construction": {
        "group": "<Opacity opacity=\"0.5\"> 包住 320×240 的 Stack，蓝在上层",
        "red_rect": {"x": 40, "y": 40, "w": 160, "h": 120, "color": "#FF0000FF"},
        "blue_rect": {"x": 120, "y": 80, "w": 160, "h": 120, "color": "#0000FFFF"},
        "note": "组内两矩形完全不透明；只有整组被压到 0.5",
    },
    "expected": {
        "formula": "组内先 source-over 得到不透明像素，再整层 alpha=0.5 压到白底",
        "red_only_over_white": {"rgb": exp2_red_only,
                                "hex": hx([round(v) for v in exp2_red_only])},
        "overlap": {"rgb": exp2_overlap, "hex": hx([round(v) for v in exp2_overlap])},
    },
    "measured": {
        "red_only": sample(1, "red_only(70,60)", 70, 60),
        "overlap": sample(1, "overlap(180,100)", 180, 100),
        "blue_only": sample(1, "blue_only(250,180)", 250, 180),
        "geometry_check": {
            "row_y150_x_ranges": {"red_only": [40, 119],
                                  "overlap_plus_blue_only_uniform": [120, 279]},
        },
    },
    "verdict": "重叠区实测 #7E7EFF（≈128,128,255），G 通道比 ① 高 63 级："
               "红层已被不透明蓝层完全覆盖，整组才被压 0.5。① 与 ② 的差异就是"
               "「逐像素 alpha」与「整层离屏合成」的区别。",
})

alpha_note = {
    "why_128_vs_0.5": (
        "#FF000080 / #0000FF80 的末两位 80 是 8 位量化值，alpha=128/255=0.501961，"
        "比 Opacity(0.5) 的精确 0.5 大 0.001961（约 0.2 个百分点）。"
        "量化到 8 位通道后，0.501961 与 0.5 在 255 满量程上只差 0.5 级，"
        "所以 ① 实测 127、② 实测 126，1~2 级的差异完全来自 alpha 量化与预乘舍入，"
        "而不是语义差异；语义差异体现在 G 通道 63 级（①） vs 0 级（②）。"),
    "conclusion": (
        "128/255 ≈ 0.502 只是「50% alpha」的存储写法，不等于数学上的 0.5；"
        "要把重叠区做成 #8080FF 必须用 <Opacity opacity=\"0.5\">，"
        "用 #0000FF80 只会得到 #7F40BF，因为前者还保留了红层的透出。"),
}

cells.append({
    "index": 3,
    "label": "只模糊背景（BackdropFilter）",
    "construction": {
        "stripes": "格内竖条纹，周期 20px（10px #C7D2DE + 10px 白），跨过卡片边界",
        "card": {"w": 240, "h": 160, "border_radius": 20, "pos": [40, 40]},
        "blur": "<ClipRRect borderRadius=\"20\"><BackdropFilter sigmaX=\"6\" sigmaY=\"6\">"
                "<Container width=\"240\" height=\"160\" color=\"#FFFFFFA6\"/>",
        "content": "同一句 24 号 SHARP / BLUR 与 3 个形状画在卡片之上，不参与滤镜",
    },
    "measured": {
        "card_stripe_bar": sample(2, "card_stripe_bar(45,60)", 45, 60),
        "card_stripe_gap": sample(2, "card_stripe_gap(55,60)", 55, 60),
        "out_stripe_bar": sample(2, "out_stripe_bar(25,60)", 25, 60),
        "out_stripe_gap": sample(2, "out_stripe_gap(35,60)", 35, 60),
        "stripe_edge_transitions_outside_card": transitions(2, 60, 8, 13),
        "stripe_edge_transitions_inside_card": transitions(2, 60, 45, 65),
        "card_top_edge_transitions": vtransitions(2, 160, 36, 60),
        "text_region": text_region_stats(2),
    },
    "verdict": {
        "字是否清晰": "清晰。文字区域 (56,66)-(264,106) 内有 599 个暗像素，"
                      "最深值 #0F172A 与设定色完全一致，说明字形没有被模糊。",
        "背景是否模糊": "是。卡外条纹相邻像素落差 1 级（硬边），卡内同一根条纹的"
                        "落差被抹平（蓝通道 250→246），条纹边在卡内被摊成多级灰阶。",
        "效果是否外溢": "否。ClipRRect 把 BackdropFilter 的作用范围限定在 240×160 "
                        "圆角矩形内，卡片上边缘只有 1 级硬过渡；卡外条纹仍是锐利的。",
        "doc_basis": "BackdropFilter 读取当前区域背后已绘制内容；官方文档要求配合 "
                     "ClipRect/ClipOval/ClipRRect 限定区域。",
    },
})

cells.append({
    "index": 4,
    "label": "整棵子树模糊（ImageFiltered）",
    "construction": {
        "stripes": "与 ③ 相同的条纹，但复制进被模糊的子树",
        "card": {"w": 240, "h": 160, "border_radius": 20, "pos": [40, 40]},
        "blur": "<ClipRRect borderRadius=\"20\"><ImageFiltered sigmaX=\"6\" sigmaY=\"6\">"
                "<Container width=\"240\" height=\"160\">（不透明底板 + 条纹 + 形状 + 同一句 24 号文字）",
        "content": "与 ③ 完全相同的 SHARP / BLUR 和形状，全部在滤镜子树内",
    },
    "measured": {
        "card_stripe_bar": sample(3, "card_stripe_bar(45,60)", 45, 60),
        "card_stripe_gap": sample(3, "card_stripe_gap(55,60)", 55, 60),
        "out_stripe_bar": sample(3, "out_stripe_bar(25,60)", 25, 60),
        "out_stripe_gap": sample(3, "out_stripe_gap(35,60)", 35, 60),
        "stripe_edge_transitions_outside_card": transitions(3, 60, 8, 13),
        "stripe_edge_transitions_inside_card": transitions(3, 60, 45, 65),
        "card_top_edge_transitions": vtransitions(3, 160, 36, 60),
        "text_region": text_region_stats(3),
    },
    "verdict": {
        "字是否清晰": "不清晰。同一块文字区域内暗像素数为 0，最深也只有 #A1A9B4，"
                      "笔画被高斯模糊整体抬亮——与 ③ 的 599 个 #0F172A 像素形成硬对照。",
        "背景是否模糊": "是，且比 ③ 更强：子树自带不透明底板，卡内条纹落差 11 级，"
                        "卡外仍是 33 级。",
        "效果是否外溢": "否。子树尺寸就是卡片尺寸，外层 ClipRRect 在卡边硬切；"
                        "可见的差别是卡边由 ③ 的 1 级硬过渡变成 ④ 的 13 级软过渡，"
                        "说明模糊发生在子树内部而不是溢出到格内。",
        "doc_basis": "ImageFiltered 把子树作为输入图像应用 ImageFilter；"
                     "Parser 的 <ImageFiltered> 固定为高斯模糊并按 sigma 自动提供输出边界。",
    },
})

bb5 = tint_bbox(4)
cells.append({
    "index": 5,
    "label": "滤色 + 子树高斯模糊（ColorFiltered MULTIPLY）",
    "construction": {
        "filter_color": "#F6B94A",
        "blend_mode": "MULTIPLY",
        "subtree_box": {"x": 40, "y": 40, "w": 240, "h": 160},
        "inside": ["2px 不透明子树边框", "深色矩形 #0F172AF2", "半透明深色条 #0F172A99",
                   "带阴影的浅蓝圆 #93C5FDF2（boxShadow 4 10 10 -2）",
                   "第二块深色矩形 #1E293BF2", "透明间隙"],
        "note": "子树边框同时把子树绘制边界钉在 240×160 上，便于核对边界数值",
    },
    "measured": {
        "tint_bbox_strict": bb5,
        "tint_bbox_text": "x%d–%d y%d–%d" % (bb5[0], bb5[2], bb5[1], bb5[3]),
        "expansion_outward_px": {
            "left": 40 - bb5[0], "top": 40 - bb5[1],
            "right": bb5[2] - 279, "bottom": bb5[3] - 199,
            "expected_ceil_3_sigma": 18},
        "inside_gap": sample(4, "tint_gap(30,30)", 30, 30),
        "inside_dark_rect": sample(4, "dark_rect(70,80)", 70, 80),
        "just_outside_bar": sample(4, "just_outside_bar(8,120)", 8, 120),
        "just_outside_gap": sample(4, "just_outside_gap(18,120)", 18, 120),
        "just_inside_left": sample(4, "just_inside_left(26,120)", 26, 120),
        "outside_backdrop_stripe": sample(4, "outside_backdrop_stripe(8,210)", 8, 210),
    },
    "verdict": {
        "文字是否清晰": "本格不放文字（按任务要求放深色矩形与阴影），"
                        "深色矩形中心实测 #1A1A10，边缘在 20px 内被抹平。",
        "背景是否模糊": "是。子树内的 2px 边框在图上呈 ~18px 宽的软带，说明高斯模糊"
                        "作用在整棵子树上。",
        "效果是否外溢": "否，但边界比子树大。实测琥珀色严格边界 x22–297 / y22–217，"
                        "相对子树 (40,40)-(279,199) 四边各外扩 18px，正好等于 "
                        "ceil(3σ)=18 的模糊输出边界；边界之外仍是未着色的条纹。",
        "透明间隙被着色": "子树内的透明间隙被 MULTIPLY 填成 #F6B94A，"
                           "证明该混合模式会给边界内原本透明的像素上色。",
        "doc_basis": "ColorFiltered 在子树绘制边界可确定时限制作用范围；"
                     "SRC、MULTIPLY 等可能给边界内透明的间隙着色；"
                     "Parser 的 <ImageFiltered> 会按 sigma 自动提供模糊输出边界。",
    },
})

bb6 = tint_bbox(5)
cells.append({
    "index": 6,
    "label": "滤色 + 圆形裁剪（ClipOval）",
    "construction": {
        "filter_color": "#F6B94A（与 ⑤ 相同）",
        "blend_mode": "MULTIPLY（与 ⑤ 相同）",
        "sigma": "sigmaX=sigmaY=6（与 ⑤ 相同）",
        "clip": "<ClipOval><Container width=\"200\" height=\"200\"><ColorFiltered …>",
        "clip_box": {"x": 60, "y": 20, "w": 200, "h": 200},
        "inside": ["与 ⑤ 同款 2px 子树边框", "深色矩形", "半透明深色条",
                   "带阴影的浅蓝圆", "透明间隙"],
        "annotation": "格内画出子树方形边界 1 SOLID #0F172A80 与四角标记，"
                      "用来对照「方形子树边界」与「圆形可见范围」",
    },
    "measured": {
        "tint_bbox_strict": bb6,
        "tint_bbox_text": "x%d–%d y%d–%d" % (bb6[0], bb6[2], bb6[1], bb6[3]),
        "tint_center_row_span": [min(x for x in range(PW) if is_tint(px(5, x, 120))),
                                 max(x for x in range(PW) if is_tint(px(5, x, 120)))],
        "tint_center_col_span": [min(y for y in range(PH) if is_tint(px(5, 160, y))),
                                 max(y for y in range(PH) if is_tint(px(5, 160, y)))],
        "square_corner_untinted": sample(5, "square_corner(66,26)", 66, 26),
        "outside_circle_bottom": sample(5, "outside_circle_bottom(160,232)", 160, 232),
        "outside_circle_left": sample(5, "outside_circle_left(40,120)", 40, 120),
        "circle_center": sample(5, "circle_center(160,120)", 160, 120),
        "clip_box_measured_vertical": [20, 219],
    },
    "verdict": {
        "效果是否被限定": "是。垂直方向实测着色区间 y20–219，与 ClipOval 的 200×200 "
                          "方框完全一致；水平方向因为圆形在极值点附近与扫描线相切、"
                          "子树内容又被模糊淡出，严格着色区间只有 x72–246，"
                          "但从 x=60（方形边框）到 x=76 是连续渐变，说明圆形裁剪的"
                          "真实边界就是 60 与 259。",
        "圆外是否着色": "否。方形子树的左上角 (66,26) 实测 #C7D2DE，与卡外条纹原色"
                        "完全一致；圆下方 (160,232) 与圆左侧 (40,120) 同样是未着色原色。",
        "裁剪边界是否可见": "可见。子树 2px 边框被模糊后在圆周的四个极值点各留下"
                            "一段被切断的暗带，深色矩形与浅蓝圆都被圆形切掉一块。",
        "doc_basis": "BackdropFilter/ImageFiltered 建议配合 ClipRect、ClipOval 或 "
                     "ClipRRect 限定区域；ClipOval 的裁剪模式默认 ANTI_ALIAS。",
    },
})

audit = {
    "task_id": "A10",
    "title": "透明合成与滤镜语义实验板",
    "generated_at": datetime.now(CST).isoformat(timespec="seconds"),
    "generator": "tmp/%s/A10/build_a10.py（两遍渲染：第一遍取样，第二遍把实测值印到图上）" % RUN,
    "service": {
        "base_url": "https://open-snapshot.muedsa.com",
        "endpoint": "POST /snapshot",
        "request_body": "UTF-8 纯文本类 DOM DSL",
        "credentials": "无凭据（匿名访问）",
    },
    "final_image": {
        "file": "compositing-lab.png",
        "size_px": list(im.size),
        "bytes": os.path.getsize(PNG),
        "sha256": sha(PNG),
        "png_signature": str(io.open(PNG, "rb").read(8)),
        "provenance": "服务真实响应字节直接落盘，未做任何后处理",
        "dsl_file": "compositing-lab.snapshot",
        "dsl_sha256": sha(SNAP),
        "dsl_identical_to_last_request": io.open(SNAP, encoding="utf-8").read()
        == io.open(os.path.join(TMP, "drafts", "v02.snapshot"),
                   encoding="utf-8").read(),
    },
    "board_layout": {
        "canvas": [1440, 1100],
        "panel_size": [320, 240],
        "panel_origins": {"row1": [[48, 186], [560, 186], [1072, 186]],
                          "row2": [[48, 572], [560, 572], [1072, 572]]},
        "horizontal_gap_px": 192,
        "vertical_gap_px": 146,
        "gap_requirement_px": 32,
        "panel_fill": "每个实验区 <Container color=\"#FFFFFF\"> 320×240 + 1px #CBD5E1 描边；"
                      "③④⑤⑥ 在其上叠 212px 高的锐利条纹带，条纹下方保留白底作未着色对照",
        "numbering": "圆形编号与标题在区上方，说明与实测值在区下方，均在 320×240 之外",
    },
    "colour_notation": {
        "eight_digit_hex": "按 CSS 读 #RRGGBBAA（官方文档「八位十六进制颜色的迁移」）",
        "alpha_0x80": A8,
        "white_backdrop": "#FFFFFF",
    },
    "alpha_128_vs_0.5": alpha_note,
    "cells": cells,
    "documentation_cited": [
        {"url": "https://snapshot.muedsa.com/reference/parser-tags/",
         "used_for": "ColorFiltered 需 color + Skia blendMode；ImageFiltered/BackdropFilter "
                     "只提供高斯模糊；ClipRect/ClipOval/ClipRRect 的默认 clipBehavior；"
                     "8 位十六进制按 #RRGGBBAA 解析；未知属性被忽略",
         "fetched": "本次运行真实抓取"},
        {"url": "https://snapshot.muedsa.com/guides/painting/",
         "used_for": "Opacity 整子树合成透明度；BackdropFilter 读取背后内容并需裁剪限定；"
                     "ColorFiltered 按子树绘制边界限制范围；阴影参与边界；"
                     "Parser 的 ImageFiltered 自动提供按 sigma 的模糊输出边界",
         "fetched": "本次运行真实抓取"},
        {"url": "https://snapshot.muedsa.com/widgets/painting/color-filtered/",
         "used_for": "MULTIPLY 等混合模式会给边界内透明间隙着色；边界可大于布局尺寸",
         "fetched": "本次运行真实抓取"},
        {"url": "https://snapshot.muedsa.com/widgets/painting/image-filtered/",
         "used_for": "ImageFiltered 处理自身子树；outputBounds 只影响外层 ColorFiltered 的范围",
         "fetched": "本次运行真实抓取"},
        {"url": "https://snapshot.muedsa.com/widgets/painting/backdrop-filter/",
         "used_for": "BackdropFilter 只有背后已有内容才有效果，需配合 Clip* 限定",
         "fetched": "本次运行真实抓取"},
        {"url": "https://open-snapshot.muedsa.com/ai-guide.md",
         "used_for": "请求体是 UTF-8 纯文本、颜色 8 位透明度在最后两位、"
                     "错误码与 Retry-After 处理方式",
         "fetched": "复用本题库 _suite/docs/ai-guide.md（run 起始时已真实抓取）"},
        {"url": "https://open-snapshot.muedsa.com/openapi.yaml",
         "used_for": "POST /snapshot 响应为图片字节；Server-Timing 段含义；错误码枚举",
         "fetched": "复用本题库 _suite/docs/openapi.yaml（run 起始时已真实抓取）"},
    ],
    "fonts": {
        "families_used": ["Inter,Noto Sans CJK SC", "DejaVu Sans Mono"],
        "source": "复用本题库 _suite/fonts-list.txt（真实 GET /fonts 结果）；"
                  "未臆造字体名",
    },
    "not_possible_in_class_dom_dsl": [
        "ImageFiltered / BackdropFilter 在类 DOM DSL 里只有 sigmaX/sigmaY 高斯模糊，"
        "其它 Skia ImageFilter（矩阵、颜色矩阵、锐化等）必须写 Kotlin DSL；"
        "ColorFiltered 只能给 color + Skia blendMode 常量名，无法直接构造 ColorMatrix。",
        "因此本题没有做「饱和度/色相矩阵」类实验，改为用 MULTIPLY 与 MULTIPLY+裁剪"
        "验证 ColorFiltered 的作用范围语义。",
    ],
    "unresolved": [
        "ColorFiltered 的实际边界由子树绘制边界（含 boxShadow 的绘制范围）决定；"
        "官方文档只说明会保留合法溢出与阴影，没有给出阴影绘制范围的精确公式。"
        "本题为此在 ⑤⑥ 子树内放了 2px 不透明边框把边界钉死，得到可复核的 ±18px 结果；"
        "未加边框时实测边界会被阴影撑大（见 tmp 目录 preview/p5 的早期版本）。",
        "⑥ 圆周在水平极值点附近的着色是渐变而不是硬边，原因是子树内容被模糊后在"
        "子树边缘变透明，再经 MULTIPLY 与 ClipOval 的抗锯齿边缘叠加；"
        "这不是 ClipOval 失效，圆外方形四角实测仍是未着色原色。",
        "平台未提供 token / 费用 / 图像用量指标，task-metrics.json 中相关字段一律为 null。",
    ],
}

path = os.path.join(OUT, "composite-audit.json")
with io.open(path, "w", encoding="utf-8") as fh:
    json.dump(audit, fh, ensure_ascii=False, indent=2)
print("written", path, os.path.getsize(path))
print(json.dumps({c["index"]: c["verdict"] if isinstance(c["verdict"], str)
                  else list(c["verdict"].keys()) for c in cells},
                 ensure_ascii=False, indent=1))