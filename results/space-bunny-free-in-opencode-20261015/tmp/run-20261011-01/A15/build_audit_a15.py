#!/usr/bin/env python
"""A15 审计生成：锚点（来自 anchor-verify.json）+ 色彩复核 + 实际看图记录。

启动基准：总任务根 (suite_root)。
输出：tmp/run-20261011-01/A15/drafts/reconstruction-audit-raw.json
"""
from __future__ import annotations

import colorsys
import json
import os
import sys
from pathlib import Path

from PIL import Image

BASE = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
REF = BASE / "tasks/A15-reference-reconstruction/inputs/reference.png"
DRAFTS = BASE / "tmp/run-20261011-01/A15/drafts"

# 色彩角色 → 在参考图与重建图上**同一坐标**的采样
# mode=point   : 该点 3×3 邻域中位色（适合大面积纯色）
# mode=darkest : 区域内最暗像素（适合 1px 细线与文字笔画，按固定点取会踩到抗锯齿边）
ROLES = [
    ("主背景", "main_background", "point", (700, 14), "整幅底色，卡片之间的留白",
     "极浅冷灰蓝，明度最高的一档，承担整个界面的空气感"),
    ("侧栏", "sidebar", "point", (110, 450), "左侧导航栏底色",
     "很深的海军蓝，明度最低，与主背景形成最强明暗对比，把导航区从内容区里切出来"),
    ("导航选中态底", "nav_selected", "point", (180, 140), "Overview 项高亮圆角块",
     "比侧栏底色略浅的蓝灰，明度抬高一档用于表达「当前页」而不引入第二种色相"),
    ("主蓝色", "primary_blue", "point", (1296, 52), "导出按钮填充",
     "饱和的钴蓝，是界面唯一的高饱和主色，承担「可操作」语义"),
    ("主蓝色（柱）", "primary_blue_bars", "point", (384, 505), "图表柱体填充",
     "与按钮同色，说明图表沿用同一个品牌主色而不是另立配色"),
    ("卡片填充", "card_fill", "point", (600, 250), "KPI 卡 1 右下空白处",
     "纯白，比主背景亮一档，用明度差而不是描边把卡片托起来"),
    ("卡片填充（图表卡）", "card_fill_chart", "point", (975, 330), "图表卡右上空白处", "同为纯白"),
    ("卡片填充（活动卡）", "card_fill_activity", "point", (1380, 340), "活动卡右上空白处", "同为纯白"),
    ("卡片填充（表格卡）", "card_fill_table", "point", (1360, 665), "表格卡右上空白处", "同为纯白"),
    ("卡片描边", "card_border", "darkest", (330, 133, 470, 142),
     "KPI 卡 1 顶边 1px 描边所在的一行", "比白卡略暗的浅蓝灰，给白卡一个清晰的物理边界"),
    ("图表网格线", "grid_line", "darkest", (335, 546, 352, 553),
     "零线网格线在第一根柱左侧的可见段", "极浅蓝灰，明度接近白卡，只在需要时给出比例参照"),
    ("状态标签底（In progress）", "status_pill_1", "point", (1036, 743), "第一行药丸左侧空白",
     "很浅的蓝，与主蓝同色相但明度大幅抬高，用于「进行中」"),
    ("状态标签字（In progress）", "status_text_1", "darkest", (1066, 735, 1140, 752),
     "药丸内文字笔画的最暗像素", "主蓝原色，与药丸底同色相，高对比可读"),
    ("状态标签底（Review）", "status_pill_2", "point", (1036, 778), "第二行药丸左侧空白",
     "很浅的暖黄，色相从蓝转向琥珀，与第一行形成明显区分"),
    ("状态标签底（Done）", "status_pill_3", "point", (1036, 813), "第三行药丸左侧空白",
     "很浅的青绿，色相转向绿，语义上对应「已完成」"),
    ("品牌标记", "brand_mint", "point", (36, 40), "NORTHSTAR 左侧标记方块",
     "高明度薄荷绿，是侧栏里唯一的亮色点"),
    ("PRO 卡片", "pro_card", "point", (180, 860), "侧栏底部卡片右下空白",
     "比侧栏底色略浅的深蓝灰，用于把升级信息从导航项里分层出来"),
]

VISUAL_REVIEWS = [
    ("原尺寸", "1440×900 全图整屏", "preview/reconstructed-v3.png",
     "整屏打开：布局分块、页眉、KPI 三卡、图表卡 + 活动卡、表格卡、页脚、侧栏五区"
     "全部落在与参考图相同的位置；未发现缺块、错位或越界", "通过"),
    ("并排原尺寸", "参考图与重建图上下并排（各 70%）", "preview/compare-fullsize.png",
     "上下并排逐块比对：块面比例、留白节奏、色块关系一致；"
     "唯一肉眼可辨的系统性差异是字形（见 comparison.md 的字体一节）", "通过"),
    ("缩略", "25% 缩略并排", "preview/compare-thumbnail-25pct.png",
     "缩到 25% 后两图在块面与色彩关系上几乎不可区分，"
     "说明「远看结构」这一层已经复刻到位", "通过"),
    ("局部放大 · 侧栏", "2× 最近邻", "preview/zoom-sidebar-2x.png",
     "品牌标记、四个导航项、选中态圆角块、圆点、PRO 卡三行文字位置一致；"
     "选中态圆点为薄荷绿、未选中为蓝灰，色差关系正确", "通过"),
    ("局部放大 · 页眉", "2× 最近邻", "preview/zoom-header-2x.png",
     "主标题、副标题、导出按钮的文字基线与块面对齐一致；"
     "字形宽度不同（字体替换所致）", "通过"),
    ("局部放大 · KPI", "2× 最近邻", "preview/zoom-kpi-2x.png",
     "三张卡的标签/数值/变化率三段节奏一致，变化率统一为绿色；"
     "第三张卡右边界比另外两行窄 16px 的原图特征也照原样保留", "通过"),
    ("局部放大 · 图表", "2× 最近邻", "preview/zoom-chart-2x.png",
     "六根柱的比例、网格线间距、零线位置、刻度标签右对齐、月份标签居中"
     "全部一致；柱高是按 1.2px/单位算出来的，不是照着数字摆的", "通过"),
    ("局部放大 · 活动卡", "2× 最近邻", "preview/zoom-activity-2x.png",
     "三个活动项的名称与时间两行结构、圆点颜色序列（琥珀/蓝/绿）与参考一致", "通过"),
    ("局部放大 · 表格", "2× 最近邻", "preview/zoom-table-2x.png",
     "表头底带、三行顺序、四个分列、两条行分隔线、三枚状态药丸的配色与圆角一致；"
     "状态编码 In progress / Review / Done 未错位", "通过"),
    ("局部放大 · PRO 卡", "2× 最近邻", "preview/zoom-procard-2x.png",
     "三行文字层级（薄荷绿标签 / 白色正文 / 蓝灰提示）与卡片内边距一致", "通过"),
    ("像素级锚点比对", "24 个锚点，两图同一测量代码", "drafts/anchor-verify.json",
     "24/24 全部落在题面 ±8px 内，最大分量误差 3px（主标题字形框左上角 y 38 vs 35）", "通过"),
]


def hx(c):
    return "#%02X%02X%02X" % (c[0], c[1], c[2])


def hsl(c):
    r, g, b = [v / 255.0 for v in c]
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    return {"hue_deg": round(h * 360, 1), "sat_pct": round(s * 100, 1),
            "light_pct": round(l * 100, 1)}


def patch(px, pt):
    """取该坐标 3×3 邻域的中位色，避免踩在抗锯齿边缘上。"""
    x, y = pt
    vals = []
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            vals.append(px[min(max(x + dx, 0), 1439), min(max(y + dy, 0), 899)][:3])
    vals.sort(key=lambda c: c[0] + c[1] + c[2])
    return vals[len(vals) // 2]


def patch_darkest(px, box):
    """取区域内**最暗**的像素：用于 1px 细线与文字笔画——
    按固定坐标取点会踩在抗锯齿边缘上（首版的状态标签字与卡片描边就是这样误采的）。"""
    x0, y0, x1, y1 = box
    best, bl = None, 10 ** 9
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            c = px[x, y][:3]
            lum = c[0] + c[1] + c[2]
            if lum < bl:
                bl, best = lum, c
    return best


def main() -> None:
    rec_path = BASE / (sys.argv[1] if len(sys.argv) > 1
                       else "outputs/run-20261011-01/A15/reconstructed.png")
    with Image.open(REF) as s:
        s.load()
        rim = s.convert("RGB")
    with Image.open(rec_path) as s:
        s.load()
        sim = s.convert("RGB")
    verify = json.loads((DRAFTS / "anchor-verify.json").read_text(encoding="utf-8"))
    geom = json.loads((DRAFTS / "a15-geometry-v1.json").read_text(encoding="utf-8"))

    color_rows = []
    for name, key, mode, pt, where, role_desc in ROLES:
        if mode == "point":
            rc = patch(rim.load(), pt)
            sc = patch(sim.load(), pt)
            region = [pt[0], pt[1], pt[0], pt[1]]
        else:
            rc = patch_darkest(rim.load(), pt)
            sc = patch_darkest(sim.load(), pt)
            region = list(pt)
        rh, sh = hsl(rc), hsl(sc)
        dist = round(sum((rc[i] - sc[i]) ** 2 for i in range(3)) ** 0.5, 2)
        color_rows.append({
            "role": name, "key": key, "sample_mode": mode,
            "sample_region_xyxy": region, "sampled_from": where,
            "reference_hex": hx(rc), "reconstructed_hex": hx(sc),
            "reference_hsl": rh, "reconstructed_hsl": sh,
            "rgb_distance": dist,
            "hue_delta_deg": round(abs(rh["hue_deg"] - sh["hue_deg"]), 1),
            "lightness_delta_pct": round(abs(rh["light_pct"] - sh["light_pct"]), 1),
            "role_meaning": role_desc,
            "judgment": ("色相、明暗与角色一致；重建用同一区域的纯色，"
                         "逐通道差值很小" if dist <= 8 else
                         "色相/明暗接近但取样值有偏差，见 comparison.md"),
        })

    audit = {
        "schema_version": 1, "task_id": "A15", "round": "round-01", "path_base": "output_dir",
        "reference": {
            "file": "tasks/A15-reference-reconstruction/inputs/reference.png",
            "size": list(rim.size),
            "usage": "仅用于观察与像素测量；未嵌入 DSL、未裁块、未作为输出资产",
        },
        "reconstruction": {
            "png": "reconstructed.png", "dsl": "reconstructed.snapshot",
            "size": list(sim.size), "source_script": {
                "path_base": "suite_root",
                "path": "tmp/run-20261011-01/A15/build_a15.py"},
            "font_choice": {"latin": "Inter / Inter Semi Bold / Inter Medium",
                            "source": "run 级 GET /fonts 的 27 个族",
                            "note": "参考图使用的是几何无衬线（近似 Poppins 一类），"
                                    "服务端未提供该族，改用最接近的 Inter；"
                                    "字形差异在 comparison.md 说明"},
        },
        "coordinate_convention": {
            "origin": "画布左上角", "x": "向右为正", "y": "向下为正", "unit": "px",
            "rect_form": "[left, top, right, bottom]，均为外轮廓",
            "note": "边界项只记 x 或 y；点项记 (x,y)；矩形四边分别比较，不混用文字基线、中心与边界",
        },
        "tolerance": {"value_px": 8,
                      "rule": "对应分量的绝对误差均 ≤8px；矩形四边分别比较，不做平均抵消",
                      "source": "题面规定"},
        "measurement": {
            "method": "参考图与重建图使用**同一套测量函数**（verify_a15.py）："
                      "边界=沿扫描线找颜色跃变；矩形=按纯色/描边色的像素包围盒；"
                      "点=由矩形派生或取字形墨迹包围盒",
            "reference_coordinates_origin": "对公开 reference.png 做像素测量得到；"
                                            "题面未提供作者源码或标准坐标",
            "raw_reference_measurements": [
                "tmp/run-20261011-01/A15/drafts/reference-probe.json",
                "tmp/run-20261011-01/A15/drafts/reference-geometry.json",
                "tmp/run-20261011-01/A15/drafts/reference-geometry-2.json",
                "tmp/run-20261011-01/A15/drafts/reference-geometry-3.json",
                "tmp/run-20261011-01/A15/drafts/reference-geometry-4.json"],
        },
        "chart_proportions": {
            "note": "柱高由刻度反推的比例算出，不是照抄数字",
            "zero_line_y": 549, "top_tick_y": 405, "ticks": [0, 30, 60, 90, 120],
            "px_per_unit": geom["chart"]["px_per_unit"],
            "bar_width_px": geom["chart"]["bar_w"],
            "bar_left_positions": [geom["chart"]["bars"][i]["x_left"] for i in range(6)],
            "bar_top_positions": [geom["chart"]["bars"][i]["y_top"] for i in range(6)],
            "bar_height_formula": "height = value × 1.2；y_top = 549 − height",
            "verified_by_anchor": "A12/A13（第一根与最后一根柱的顶部中心）误差 0px",
        },
        "anchors": verify["anchors"],
        "anchor_summary": {
            "count": verify["anchor_count"], "tolerance_px": verify["tolerance_px"],
            "all_passed": verify["all_passed"],
            "worst_error_px": verify["worst_error_px"],
            "worst_error_anchor": verify["worst_error_anchor"],
            "quadrants_covered": verify["quadrants_covered"],
            "required_anchors_present": {
                "侧栏右边界": "A01", "导航选中态外框": "A02",
                "主标题可见字形框左上角": "A04",
                "三张KPI卡外框": ["A05", "A06", "A07"],
                "净收入图表卡外框": "A09", "图表零线左端点": "A10",
                "最后一根柱的顶部中心": "A12", "活动卡外框": "A14",
                "项目表格卡外框": "A15", "最后一行状态标签外框": "A17"},
            "extra_anchors": "另加 12 个（A03/A08/A11/A13/A16/A18–A24）覆盖四象限与局部细节",
        },
        "color_review": {
            "method": "在参考图与重建图的**同一坐标**取 3×3 邻域中位色（避开抗锯齿边缘），"
                      "换算 HSL 比较色相/饱和/明度，并记录该颜色的角色含义；"
                      "不使用未公开的硬阈值，rgb_distance 仅作辅助解释",
            "rows": color_rows,
            "all_roles_match": all(r["rgb_distance"] <= 8 for r in color_rows),
            "roles_checked": [r["key"] for r in color_rows],
        },
        "visual_reviews": [
            {"mode": m, "zoom": z, "image": {"path_base": "suite_root",
                                             "path": f"tmp/run-20261011-01/A15/{p}"},
             "observed": o, "conclusion": c}
            for m, z, p, o, c in VISUAL_REVIEWS],
        "known_differences": [
            {"item": "字体", "detail": "参考图为几何无衬线（近似 Poppins），服务端 27 个字体族里"
                                        "没有该族，改用 Inter。字宽/字面率不同，"
                                        "因此长标题与长项目名的可见字形右缘会比参考图略短",
             "affects": "全部文字的字形形状与宽度，不影响任何文字块的位置与字号"},
            {"item": "字重观感", "detail": "Inter Semi Bold 的笔画粗细与参考图标题用字略有差异，"
                                          "在 2× 放大下可见",
             "affects": "视觉重量，不影响几何"},
            {"item": "抗锯齿", "detail": "服务端 Skia 渲染的边缘过渡与参考图的生成管线不同",
             "affects": "1px 级别的边缘灰阶，锚点测量已把它计入"},
        ],
        "not_claimed": "不宣称逐像素完全复刻，也不宣称 DSL 树与参考来源一致；"
                       "锚点合格不等于字形一致",
    }
    p = DRAFTS / "reconstruction-audit-raw.json"
    p.write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"anchors": audit["anchor_summary"]["count"],
                      "all_passed": audit["anchor_summary"]["all_passed"],
                      "worst_error_px": audit["anchor_summary"]["worst_error_px"],
                      "color_roles": len(color_rows),
                      "all_roles_match": audit["color_review"]["all_roles_match"]},
                     ensure_ascii=False, indent=2))
    for r in color_rows:
        print(f"  {r['role']:22} ref={r['reference_hex']} rec={r['reconstructed_hex']} "
              f"d={r['rgb_distance']:<6} ΔL={r['lightness_delta_pct']}%")
    print("->", p.as_posix())


if __name__ == "__main__":
    main()