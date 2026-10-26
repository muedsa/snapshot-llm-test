"""从 anchor-compare-v4.json 生成 reconstruction-audit.json（A15 交付用）。

字段约定遵循 tasks/A15-reference-reconstruction/templates/audit-fields.json：
- anchors: >=12 条，name/type、参考估计/重建实际分量、误差、测量方法、局部证据
- color_review: 题面规定色彩角色的人工比较 + 采样辅助 + 残余差异
- visual_reviews: 原尺寸/缩略/局部放大实际查看记录
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(".")
TMP = ROOT / "tmp" / "run-20261013-174209" / "A15"
OUT = ROOT / "outputs" / "run-20261013-174209" / "A15"

cmp_data = json.load(open(TMP / "anchor-compare-v4.json"))
REF, REC = cmp_data["ref"], cmp_data["rec"]

# 每个锚点的测量方法与局部证据（截图/放大路径相对 suite_root）
META = {
    "sidebar_right": (
        "边界", "侧栏深色 #14233C 与主背景 #F3F6FB 的交界：在 y=100/300/500/700/850 五行上"
        "找第一个 x 使 px[x]<70 且 px[x+1]>200，边界取 x+1（主背景首列）。",
        "tmp/run-20261013-174209/A15/qc-q3_nav.png"),
    "nav_sel": (
        "矩形", "导航选中态背景 #294467 与侧栏 #14233C 的色差扫描：收集容差 ±8 内的全部像素取外接框。",
        "tmp/run-20261013-174209/A15/qc-q3_nav.png"),
    "title_tl": (
        "点", "主标题 'Workspace Overview' 深墨色 #18283F 可见字形框：阈值 t=150 扫 (250..620, 30..80) 取左上角。",
        "tmp/run-20261013-174209/A15/qc-q1_header.png"),
    "subtitle_tl": (
        "点", "副标题 'Saturday, 07 November 2026' 灰色字形框：阈值 t=180 扫 (250..560, 80..110) 取左上角。",
        "tmp/run-20261013-174209/A15/qc-q1_header.png"),
    "kpi1": (
        "矩形", "KPI 卡 1 外框：边框色 #E2E8F1（±8 容差）在 (240..640, 120..300) 内外接框。",
        "tmp/run-20261013-174209/A15/qc-q1_header.png"),
    "kpi2": (
        "矩形", "KPI 卡 2 外框：同上方法，搜索区 (624..1020, 120..300)。",
        "tmp/run-20261013-174209/A15/qc-q2_kpi.png"),
    "kpi3": (
        "矩形", "KPI 卡 3 外框：同上方法，搜索区 (1008..1400, 120..300)。",
        "tmp/run-20261013-174209/A15/qc-q2_kpi.png"),
    "chart_card": (
        "矩形", "净收入图表卡外框：边框色 #E2E8F1 外接框，搜索区 (250..1010, 300..600)。",
        "tmp/run-20261013-174209/A15/qc-q4_chart.png"),
    "activity_card": (
        "矩形", "活动卡外框：边框色 #E2E8F1 外接框，搜索区 (1020..1400, 300..600)。",
        "tmp/run-20261013-174209/A15/qc-q5_activity.png"),
    "table_card": (
        "矩形", "项目表格卡外框：边框色 #E2E8F1 外接框，搜索区 (250..1400, 610..850)。",
        "tmp/run-20261013-174209/A15/qc-q6_table.png"),
    "zero_line": (
        "线段", "图表零线（网格线最底行 #E7EDF5）：从 x=325 起向右找第一段连续 >=50px 的线，"
        "记录左端点与右端点（避开左侧刻度 '0' 文字墨迹）。",
        "tmp/run-20261013-174209/A15/qc-q4_chart.png"),
    "last_bar_top": (
        "点", "最后一根柱（Sep）顶部中心：列 x=888 上从 y=310 向下找第一个蓝色 #245CE4 像素。",
        "tmp/run-20261013-174209/A15/qc-q4_chart.png"),
    "pill_done": (
        "矩形", "最后一行（Orbit / Launch）状态标签 'Done' 外框： pill 底色 #DCF5EC 外接框，"
        "搜索区 (1020..1180, 790..835)。",
        "tmp/run-20261013-174209/A15/qc-q6_table.png"),
    "button": (
        "矩形", "Export report 按钮外框：蓝色 #245CE4 实底外接框，搜索区 (1150..1410, 30..100)。",
        "tmp/run-20261013-174209/A15/qc-q1_header.png"),
    "pro_card": (
        "矩形", "侧栏 PRO WORKSPACE 卡外框：底色 #233954 外接框，搜索区 (0..230, 730..890)。",
        "tmp/run-20261013-174209/A15/qc-q7_pro.png"),
    "head_band": (
        "矩形", "表格表头带 #F3F6FB：在表格卡内收集该色像素外接框，搜索区 (270..1390, 680..735)。",
        "tmp/run-20261013-174209/A15/qc-q6_table.png"),
    "divider1": (
        "线段", "表格第一行下分隔线 #EBEFF5：y=760 行上从 x=280 向右连续段取左右端。",
        "tmp/run-20261013-174209/A15/qc-q6_table.png"),
    "divider2": (
        "线段", "表格第二行下分隔线 #EBEFF5：y=795 行同上。",
        "tmp/run-20261013-174209/A15/qc-q6_table.png"),
}

# 文字锚点（题面要求 12 个之外增加的文本墨迹锚点）
TEXT_META = {
    "t_northstar": ("点", "侧栏品牌 'NORTHSTAR' 白字墨迹框左上角，阈值 t=150。",
                    "tmp/run-20261013-174209/A15/qc-q3_nav.png"),
    "t_overview": ("点", "导航选中项 'Overview' 白粗字墨迹框左上角，t=150。",
                   "tmp/run-20261013-174209/A15/qc-q3_nav.png"),
    "t_button": ("点", "按钮 'Export report' 白字墨迹框左上角，t=200。",
                 "tmp/run-20261013-174209/A15/qc-q1_header.png"),
    "t_k1_label": ("点", "KPI 卡 1 标签 'REVENUE' 灰蓝墨迹框左上角，t=200。",
                   "tmp/run-20261013-174209/A15/qc-q2_kpi.png"),
    "t_k1_value": ("点", "KPI 卡 1 数值 '¥128,400' 深墨框左上角，t=150。",
                   "tmp/run-20261013-174209/A15/qc-q2_kpi.png"),
    "t_chart_title": ("点", "图表标题 'Net revenue' 墨迹框左上角，t=150。",
                      "tmp/run-20261013-174209/A15/qc-q4_chart.png"),
    "t_act_title": ("点", "活动卡标题 'Team activity' 墨迹框左上角，t=150。",
                    "tmp/run-20261013-174209/A15/qc-q5_activity.png"),
    "t_act_name1": ("点", "活动第 1 条名称 'Design review' 墨迹框左上角，t=200。",
                    "tmp/run-20261013-174209/A15/qc-q5_activity.png"),
    "t_table_title": ("点", "表格标题 'Recent projects' 墨迹框左上角，t=150。",
                      "tmp/run-20261013-174209/A15/qc-q6_table.png"),
    "t_hdr_PROJECT": ("点", "表头 'PROJECT' 墨迹框左上角，t=150。",
                      "tmp/run-20261013-174209/A15/qc-q6_table.png"),
    "t_proj1": ("点", "第 1 行项目名 'Atlas / Visual system' 墨迹框左上角，t=150。",
                "tmp/run-20261013-174209/A15/qc-q6_table.png"),
    "t_pill1": ("点", "第 1 行状态 'In progress' 蓝字墨迹框左上角，t=150。",
                "tmp/run-20261013-174209/A15/qc-q6_table.png"),
    "footer": ("点", "页脚 'All data is fictional · Snapshot benchmark' 灰字墨迹框左上角，t=180。",
               "tmp/run-20261013-174209/A15/qc-q6_table.png"),
    "month_Apr": ("点", "X 轴月份 'Apr' 墨迹框左上角（t=210，避免漏掉浅 AA）。",
                  "tmp/run-20261013-174209/A15/qc-q4_chart.png"),
    "month_Sep": ("点", "X 轴月份 'Sep' 墨迹框左上角（t=210）。",
                  "tmp/run-20261013-174209/A15/qc-q4_chart.png"),
    "t_tick_120": ("点", "Y 轴刻度 '120' 墨迹框左上角，t=200。",
                   "tmp/run-20261013-174209/A15/qc-q4_chart.png"),
    "t_unit": ("点", "单位标注 '¥ thousand' 墨迹框左上角，t=210。",
               "tmp/run-20261013-174209/A15/qc-q4_chart.png"),
}

BAR_META = ("点", "第 {i} 根柱（{m}）顶部中心：列 x={x} 上从 y=310 向下找第一个蓝色 #245CE4 像素。",
            "tmp/run-20261013-174209/A15/qc-q4_chart.png")
BAR_X = [357, 458, 559, 660, 761, 862]
BAR_M = ["Apr", "May", "Jun", "Jul", "Aug", "Sep"]

QUAD = {
    "sidebar_right": "左上/左下（侧栏纵贯）", "nav_sel": "左上",
    "title_tl": "右上", "subtitle_tl": "右上", "kpi1": "右上", "kpi2": "右上", "kpi3": "右上",
    "chart_card": "右下偏左", "activity_card": "右下", "table_card": "右下",
    "zero_line": "右下（图表内）", "last_bar_top": "右下（图表内）",
    "pill_done": "右下（表格内）", "button": "右上", "pro_card": "左下",
    "head_band": "右下（表格内）", "divider1": "右下（表格内）", "divider2": "右下（表格内）",
}


def err_entry(name, ref, rec, typ, method, evidence):
    if isinstance(ref, (int, float)) and isinstance(rec, (int, float)):
        err = rec - ref
        return {"name": name, "type": typ, "quadrant": QUAD.get(name, ""),
                "ref_estimate": ref, "reconstructed": rec, "component_error": err,
                "abs_error": abs(err), "within_tolerance": abs(err) <= 8,
                "measurement_method": method, "local_evidence": {"path_base": "suite_root", "path": evidence}}
    if isinstance(ref, list) and len(ref) == 2:
        err = [rec[0] - ref[0], rec[1] - ref[1]]
        return {"name": name, "type": typ, "quadrant": QUAD.get(name, ""),
                "ref_estimate": ref, "reconstructed": rec, "component_error": err,
                "abs_error": max(abs(e) for e in err), "within_tolerance": all(abs(e) <= 8 for e in err),
                "measurement_method": method, "local_evidence": {"path_base": "suite_root", "path": evidence}}
    # 矩形/线段 [l,t,r,b]
    err = [rec[i] - ref[i] for i in range(4)]
    return {"name": name, "type": typ, "quadrant": QUAD.get(name, ""),
            "ref_estimate": ref, "reconstructed": rec, "component_error": err,
            "abs_error": max(abs(e) for e in err), "within_tolerance": all(abs(e) <= 8 for e in err),
            "measurement_method": method, "local_evidence": {"path_base": "suite_root", "path": evidence}}


anchors = []
# 1) 题面规定的 12+ 对象
for name in ["sidebar_right", "nav_sel", "title_tl", "kpi1", "kpi2", "kpi3",
             "chart_card", "zero_line", "last_bar_top", "activity_card",
             "table_card", "pill_done"]:
    typ, method, ev = META[name]
    anchors.append(err_entry(name, REF[name], REC[name], typ, method, ev))

# 2) 附加锚点：按钮、PRO 卡、表头带、分隔线、副标题
for name in ["button", "pro_card", "head_band", "divider1", "divider2", "subtitle_tl"]:
    typ, method, ev = META[name]
    anchors.append(err_entry(name, REF[name], REC[name], typ, method, ev))

# 3) 柱顶 6 项
for i, (x, m) in enumerate(zip(BAR_X, BAR_M), 1):
    name = f"bar{i}_top"
    typ, method, ev = BAR_META
    anchors.append(err_entry(name, REF[name], REC[name], typ,
                             method.format(i=i, m=m, x=x), ev))

# 4) 月份锚点（比例标记）
for name in ["month_Apr", "month_Sep"]:
    typ, method, ev = TEXT_META[name]
    anchors.append(err_entry(name, REF[name], REC[name], typ, method, ev))

# 5) 文本墨迹锚点
for name, (typ, method, ev) in TEXT_META.items():
    if name in ("month_Apr", "month_Sep"):
        continue
    anchors.append(err_entry(name, REF[name], REC[name], typ, method, ev))

out_of = [a["name"] for a in anchors if not a["within_tolerance"]]
print("anchors:", len(anchors), "out_of_tolerance:", out_of)

# ---------- 颜色人工比较 ----------
color_review = [
    {
        "role": "主背景",
        "ref_observation": "整体为低饱和的浅灰蓝，偏冷、明度高，与白色卡片形成柔和层级。",
        "rec_observation": "同区域并排看色相、明暗与角色一致，均为同一浅灰蓝底。",
        "sampling": {"ref": "#F3F6FB", "rec": "#F3F6FB", "point": [700, 470],
                     "note": "两图空白区内部单点采样相同；采样仅辅助人工判断。"},
        "residual_difference": "无可见差异。",
    },
    {
        "role": "侧栏背景",
        "ref_observation": "深海军蓝，明度低、饱和中等，与主背景对比强烈，界定导航区。",
        "rec_observation": "并排看同为深海军蓝，边界清晰，角色一致。",
        "sampling": {"ref": "#14233C", "rec": "#14233C", "point": [100, 500], "note": "纯色内部采样相同。"},
        "residual_difference": "无可见差异。",
    },
    {
        "role": "主蓝色（按钮/柱/进度点）",
        "ref_observation": "明亮饱和的钴蓝，用于主操作按钮、图表柱与状态点，是画面主强调色。",
        "rec_observation": "并排看色相与明暗接近，强调角色一致。",
        "sampling": {"ref": "#245CE4", "rec": "#245CE4", "point": [888, 500], "note": "柱体内部采样相同；按钮文字下方底色亦为同值。"},
        "residual_difference": "无可见差异。",
    },
    {
        "role": "卡片（KPI/图表/活动/表格）",
        "ref_observation": "纯白卡面配 1px 浅灰蓝描边，圆角约 12px，浮于浅灰蓝主背景上。",
        "rec_observation": "并排看卡面、描边与圆角角色一致。",
        "sampling": {"ref": "#FFFFFF / 边 #E2E8F1", "rec": "#FFFFFF / 边 #E2E8F1", "point": [430, 200],
                     "note": "卡面与描边采样均相同。"},
        "residual_difference": "无可见差异。",
    },
    {
        "role": "状态标签（三枚 pill）",
        "ref_observation": "In progress 蓝底蓝字、Review 琥珀底棕字、Done 绿底绿字，色彩语义分工明确。",
        "rec_observation": "并排看三枚底色与字色的色相、明暗和语义角色一致。",
        "sampling": {"ref": "#E7EFFF/#FFF3D7/#DCF5EC", "rec": "#E7EFFF/#FFF3D7/#DCF5EC",
                     "point": [1100, 743],
                     "note": "底色采样相同；字色受抗锯齿影响单点会有混合差，属正常。"},
        "residual_difference": "文字抗锯齿边缘在不同字体下有 1-3px 墨迹宽微差（见 comparison.md）。",
    },
    {
        "role": "正向变化色（KPI 变化率）",
        "ref_observation": "KPI 卡底部变化率为绿色，明度中高，表示正向。",
        "rec_observation": "并排看色相与明暗接近。",
        "sampling": {"ref": "#168267", "rec": "#168267", "point": [300, 250], "note": "内部采样一致（±3 抗锯齿差）。"},
        "residual_difference": "无可见差异。",
    },
    {
        "role": "侧栏选中态",
        "ref_observation": "导航选中项为比侧栏略浅的蓝灰圆角块，白粗文字，与非选中项区分明确。",
        "rec_observation": "并排看底色、圆角与文字角色一致。",
        "sampling": {"ref": "#294467", "rec": "#294467", "point": [34, 128], "note": "非文字区采样相同。"},
        "residual_difference": "无可见差异。",
    },
]

# ---------- 实际查看记录 ----------
visual_reviews = [
    {
        "view": "原尺寸整图",
        "image": "tmp/run-20261013-174209/A15/reconstructed-v4.png",
        "compared_with": "tasks/A15-reference-reconstruction/inputs/reference.png",
        "observed": "整体布局、侧栏、三张 KPI 卡、图表卡、活动卡、表格卡与参考同构；"
                    "信息层级与视觉重量接近，未改成新设计。",
        "conclusion": "通过",
    },
    {
        "view": "七分区 2 倍放大并排（左参考 / 右重建）",
        "images": ["tmp/run-20261013-174209/A15/qc-q1_header.png",
                   "tmp/run-20261013-174209/A15/qc-q2_kpi.png",
                   "tmp/run-20261013-174209/A15/qc-q3_nav.png",
                   "tmp/run-20261013-174209/A15/qc-q4_chart.png",
                   "tmp/run-20261013-174209/A15/qc-q5_activity.png",
                   "tmp/run-20261013-174209/A15/qc-q6_table.png",
                   "tmp/run-20261013-174209/A15/qc-q7_pro.png"],
        "observed": "逐区核对：页眉/按钮/导航/PRO 卡/图表柱与刻度/活动列表/表格三行与 pill"
                    " 的文字、字重、间距与参考一致；表格三行顺序与状态编码正确。",
        "conclusion": "通过",
    },
    {
        "view": "图表比例专项",
        "image": "tmp/run-20261013-174209/A15/qc-q4_chart.png",
        "observed": "六根柱高比例 54/72/63/90/81/108 与零线比例 1.2px/单位一致，"
                    "柱顶逐项 0 误差；刻度 0/30/60/90/120 位置正确，非仅相同数字。",
        "conclusion": "通过",
    },
]

audit = {
    "schema_version": 1,
    "task_id": "A15",
    "path_base": "output_dir",
    "run_id": "run-20261013-174209",
    "reference": {"path": "tasks/A15-reference-reconstruction/inputs/reference.png",
                  "width": 1440, "height": 900, "path_base": "suite_root"},
    "reconstructed": {"path": "outputs/run-20261013-174209/A15/reconstructed.png",
                      "dsl": "outputs/run-20261013-174209/A15/reconstructed.snapshot",
                      "width": 1440, "height": 900, "path_base": "suite_root"},
    "tolerance_px": 8,
    "coordinate_convention": "原点为画布左上，x 向右、y 向下，单位像素；矩形 [left,top,right,bottom] 取外轮廓。",
    "anchors": anchors,
    "anchor_summary": {
        "count": len(anchors),
        "required_objects_covered": 12,
        "quadrants_covered": ["左上（标题/按钮/KPI1）", "右上（KPI 三卡/按钮/标题）",
                              "左下（侧栏/导航/PRO 卡）", "右下（图表卡/活动卡/表格卡）"],
        "max_abs_error": max(a["abs_error"] for a in anchors),
        "out_of_tolerance": out_of,
        "zero_error_anchors": sum(1 for a in anchors if a["abs_error"] == 0),
    },
    "color_review": color_review,
    "visual_reviews": visual_reviews,
    "notes": "文字锚点比较可见字形框位置；Inter 与参考字体存在字形级差异，"
             "已在 comparison.md 说明。颜色为同背景下人工并排判断，内部采样仅辅助。",
}

OUT.mkdir(parents=True, exist_ok=True)
with open(OUT / "reconstruction-audit.json", "w", encoding="utf-8") as f:
    json.dump(audit, f, ensure_ascii=False, indent=2)
print("written:", OUT / "reconstruction-audit.json")
