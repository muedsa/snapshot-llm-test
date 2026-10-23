"""A15 审计：同一套扫描例程量参考图与重建图，逐锚点算四项误差。

设计要点
--------
* 参考图与重建图走**完全相同**的测量函数，误差才可比。方法写在每个锚点的
  `method` 字段里，任何人能重跑复核。
* 矩形四边**分开**比较，不用中心平均去抵消误差（题目要求）。
* 字形框用「ROI 内最大色差 × 0.5」的自适应阈值（≈50% 覆盖率），去掉抗锯齿晕影。
  诊断 V 用固定 tol=40（≈1% 覆盖率）会把晕影算进墨迹，字高系统性偏大 3–6 px，
  所以首版字号是拿宽松口径反推的，这里改成严格口径复核。
* 容差 ±8 px 指**每个分量**的绝对误差都 ≤ 8，不取平均。
* 不生成 RGB / ΔE 硬阈值；颜色只做同底并排的人眼判断，采样值只作佐证。

用法：
  python -I a15_audit.py            # 测量 + 出审计报告数据
  python -I a15_audit.py --crops    # 额外导出原尺寸 / 缩略 / 局部放大
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve()
ROOT = HERE.parents[4]
os.environ.setdefault("SNAPSHOT_RUN_ID", HERE.parents[2].name)
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(HERE.parent))
import suite as S  # noqa: E402
import a15_pages as P  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

TASK = P.TASK
RID = S.run_id()
OUT, TMP = S.task_dirs(TASK)
REF = ROOT / "tasks" / "A15-reference-reconstruction" / "inputs" / "reference.png"
MINE = OUT / "reconstructed.png"

TOL_PX = 8.0


# ---------------------------------------------------------------- 扫描原语
def load(p: Path) -> np.ndarray:
    return np.asarray(Image.open(p).convert("RGB")).astype(np.int16)


def bbox_color(arr, roi, ref, tol=14):
    """ROI 内与 ref 色差 ≤ tol 的像素外接框。ROI = (x0,y0,x1,y1) 含端点。"""
    x0, y0, x1, y1 = roi
    seg = arr[y0:y1 + 1, x0:x1 + 1]
    m = np.abs(seg - ref).max(axis=2) <= tol
    ys, xs = np.nonzero(m)
    if not len(xs):
        return None
    return [int(xs.min()) + x0, int(ys.min()) + y0,
            int(xs.max()) + x0, int(ys.max()) + y0]


def bbox_ink(arr, roi, bg, frac=0.5):
    """ROI 内相对 bg 的墨迹框，阈值 = ROI 最大色差 × frac（去晕影）。"""
    x0, y0, x1, y1 = roi
    seg = arr[y0:y1 + 1, x0:x1 + 1]
    d = np.abs(seg - bg).max(axis=2)
    dm = int(d.max())
    if dm < 4:
        return None
    m = d > dm * frac
    ys, xs = np.nonzero(m)
    if not len(xs):
        return None
    return [int(xs.min()) + x0, int(ys.min()) + y0,
            int(xs.max()) + x0, int(ys.max()) + y0]


def bbox_notbg(arr, roi, bg, thr=8):
    """ROI 内与 bg 色差 > thr 的像素外接框——用来量浅色卡片边框。"""
    x0, y0, x1, y1 = roi
    seg = arr[y0:y1 + 1, x0:x1 + 1]
    m = np.abs(seg - bg).max(axis=2) > thr
    ys, xs = np.nonzero(m)
    if not len(xs):
        return None
    return [int(xs.min()) + x0, int(ys.min()) + y0,
            int(xs.max()) + x0, int(ys.max()) + y0]


def first_diff_x(arr, y, x0, x1, ref, tol=8):
    """行 y 上第一个与 ref 色差 > tol 的列——侧栏右边界。"""
    d = np.abs(arr[y, x0:x1] - ref).max(axis=1)
    xs = np.flatnonzero(d > tol)
    return int(xs[0]) + x0 if len(xs) else None


def line_extent(arr, y, x0, x1, white, lo=6, hi=48):
    """行 y 上「比白色暗一点点」的像素范围——网格线。"""
    d = np.abs(arr[y, x0:x1 + 1] - white).max(axis=1)
    xs = np.flatnonzero((d > lo) & (d < hi))
    return (int(xs[0]) + x0, int(xs[-1]) + x0, int(len(xs))) if len(xs) else None


def bar_geom(arr, x0, x1, y0, y1, ref, tol=34):
    """柱体几何：中心 x 与顶缘 y。"""
    seg = arr[y0:y1 + 1, x0:x1 + 1]
    m = np.abs(seg - ref).max(axis=2) <= tol
    ys, xs = np.nonzero(m)
    if not len(xs):
        return None
    return [round((int(xs.min()) + int(xs.max()) + 2 * x0) / 2, 1),
            int(ys.min()) + y0,
            int(xs.min()) + x0, int(xs.max()) + x0,
            int(ys.max()) + y0]


def band_geom(arr, x0, x1, y0, y1, band, tol=6, fill_ratio=0.6):
    """表格表头浅色带的四条边界（按整行填充率判定，不用外接框）。

    带的填充色与页面底色同为 (243,246,251)，两个坑都来自这一点：
    1. 窗口必须严格落在表格卡内部——卡外的页面底色会命中同一个掩码。首版用
       窗口 (270,680)-(1408,730) 就把卡右缘外的 x 1400–1408 整列算成了带，
       top/bottom/right 三个分量都顶到窗口边界，量出的 0 误差是窗口自证。
    2. 窗口内也不能直接取外接框：标题文字与正文的抗锯齿晕影有不少像素落在
       带色 ±6 内，散在 y 645–665 与 745 附近，会把 top/bottom 拉出去 25 px。
       所以先按「整行带色像素数 ≥ 60% 行宽」筛出带所在行，再在这些行里取列范围。
    窗口纵向也不能进 y 760 附近的行分隔线（(235,239,245) 与带色差 8，tol 6 内可分）。
    """
    seg = arr[y0:y1 + 1, x0:x1 + 1]
    m = np.abs(seg - band).max(axis=2) <= tol
    width = x1 - x0 + 1
    rows = np.flatnonzero(m.sum(axis=1) >= fill_ratio * width)
    if not len(rows):
        return None
    top, bottom = int(rows.min()), int(rows.max())
    cols = np.flatnonzero(m[top:bottom + 1].sum(axis=0))
    return [int(cols.min()) + x0, top + y0, int(cols.max()) + x0, bottom + y0]


def sample(arr, x, y):
    p = arr[y, x]
    return [int(v) for v in p]


def dom(arr, roi):
    """ROI 内最饱和（或最深）像素，作纯色角色的采样佐证。"""
    x0, y0, x1, y1 = roi
    reg = arr[y0:y1 + 1, x0:x1 + 1].reshape(-1, 3)
    s = reg.max(axis=1) - reg.min(axis=1)
    p = reg[int(np.argmax(s))]
    return [int(v) for v in p]


def core(arr, x0, y0, x1, y1, bg):
    """文字真色：取 ROI 内与底色通道和差最大处。

    满覆盖率的文字体素差值最大，抗锯齿混色像素差值最小，所以这一处最接近
    文字真实色。直接取「最深/最饱和像素」会命中混色边缘——例如真实
    #168267 会被量成 #0E7F67。
    """
    bg = np.asarray(bg, dtype=np.int16)
    reg = arr[y0:y1 + 1, x0:x1 + 1].reshape(-1, 3)
    p = reg[int(np.argmax(np.abs(reg - bg).sum(axis=1)))]
    return [int(v) for v in p]


# ---------------------------------------------------------------- 锚点定义
# roi 是搜索窗口，比目标大几像素，保证外轮廓不被窗口切到。
def measure(arr, bg, white, sb):
    a: dict = {}
    # 1 侧栏右边界：在纯空白段取行扫描
    a["sidebar_right"] = {"value": first_diff_x(arr, 500, 180, 320, sb, 8),
                          "roi": [180, 500, 320, 500]}
    # 2 导航选中底。窗口 y 上下都收紧：下界 186 要切在第 2 行「Projects」文字
    # （墨迹顶 191）之前——否则宽窗口会把该行抗锯齿混色算成选中底，实测会框到
    # y=205；上界 108 在底框顶 116 上方留 8 px，保证外轮廓不被窗口切到。
    a["nav_selected_box"] = {"value": bbox_color(arr, (4, 108, 218, 186),
                                                 np.array([41, 68, 103]), 16),
                             "roi": [4, 108, 218, 186]}
    # 3 主标题墨迹左上角
    tb = bbox_ink(arr, (236, 16, 780, 82), bg)
    a["title_ink"] = {"value": tb, "roi": [236, 16, 780, 82]}
    # 4-6 三张 KPI 卡
    for i, x in enumerate(P.KPI_XS):
        a["kpi_card_%d" % (i + 1)] = {
            "value": bbox_notbg(arr, (x - 10, P.KPI_Y - 10,
                                      x + P.KPI_W + 9, P.KPI_Y + P.KPI_H + 9),
                                bg, 8),
            "roi": [x - 10, P.KPI_Y - 10, x + P.KPI_W + 9,
                    P.KPI_Y + P.KPI_H + 9]}
    # 7 图表卡
    a["chart_card"] = {"value": bbox_notbg(arr, (250, 300, 1010, 605), bg, 8),
                       "roi": [250, 300, 1010, 605]}
    # 8 零线左端点
    le = line_extent(arr, P.ZERO_Y, 300, 1000, white)
    a["zero_line"] = {"value": [le[0], P.ZERO_Y] if le else None, "roi": le}
    # 9 最后一根柱
    last = P.BAR_CENTERS[-1]
    a["last_bar"] = {"value": bar_geom(arr, int(last - 40), int(last + 40),
                                       400, P.ZERO_Y + 4,
                                       np.array([36, 92, 228]), 40),
                     "roi": [int(last - 40), 400, int(last + 40), P.ZERO_Y + 4]}
    # 10 活动卡
    a["activity_card"] = {"value": bbox_notbg(arr, (1020, 300, 1409, 605), bg, 8),
                          "roi": [1020, 300, 1409, 605]}
    # 11 表格卡
    a["table_card"] = {"value": bbox_notbg(arr, (250, 614, 1409, 851), bg, 8),
                       "roi": [250, 614, 1409, 851]}
    # 12 末行状态标签（Done，绿底）
    a["last_pill"] = {"value": bbox_color(arr, (1012, 790, 1192, 836),
                                          np.array([220, 245, 236]), 20),
                      "roi": [1012, 790, 1192, 836]}
    # 13 导出按钮
    a["export_button"] = {"value": bbox_color(arr, (1140, 30, 1420, 110),
                                              np.array([36, 92, 228]), 40),
                          "roi": [1140, 30, 1420, 110]}
    # 14 侧栏工作区卡
    a["workspace_card"] = {"value": bbox_color(arr, (6, 700, 218, 884),
                                               np.array([35, 57, 84]), 18),
                           "roi": [6, 700, 218, 884]}
    # 15 页脚墨迹左上角
    a["footer_ink"] = {"value": bbox_ink(arr, (240, 856, 820, 890), bg),
                       "roi": [240, 856, 820, 890]}
    # 16 表头带（浅色带，在白色卡片上）。窗口严格落在卡片内部
    # （卡 [260,624,1399,841]，x 262..1398 在内边距内，y 640..755 远离四个圆角
    # 与 y≈760 的行分隔线），否则卡外的页面底色会命中同一个带色掩码。
    a["header_band"] = {"value": band_geom(arr, 262, 1398, 640, 755,
                                           np.array([243, 246, 251])),
                        "roi": [262, 640, 1398, 755]}
    # 17 两条行分隔线。与表头带同宽是这次修正的重点，所以单独各量一条确认。
    # 窗口纵向夹在两行文字墨迹之间（第 1/2 行墨迹底 749/784，第 3 行墨迹顶 805）。
    a["divider_1"] = {"value": bbox_color(arr, (262, 754, 1398, 766),
                                          np.array([235, 239, 245]), 10),
                      "roi": [262, 754, 1398, 766]}
    a["divider_2"] = {"value": bbox_color(arr, (262, 789, 1398, 801),
                                          np.array([235, 239, 245]), 10),
                      "roi": [262, 789, 1398, 801]}
    # 17 logo 圆环：直接匹配 mint 描边色，避开紧邻的白色品牌文字
    a["logo_ring"] = {"value": bbox_color(arr, (20, 24, 80, 70),
                                          np.array([100, 219, 182]), 40),
                      "roi": [20, 24, 80, 70]}
    return a


# 辅助字形框：不是锚点，但用于说明排版是否落在该落的位置。
# 每项附「该元素的字号与期望墨迹左上角」，报告里据此把偏差归到字号或位置。
GLYPH_ROIS = [
    ("subtitle", (236, 82, 760, 114), "bg", 18.0, (261, 85)),
    ("kpi1_label", (278, 154, 400, 186), "card", 14.0, (285, 161)),
    ("kpi1_value", (278, 186, 480, 232), "card", 32.0, (285, 199)),
    ("kpi1_delta", (278, 232, 400, 270), "card", 16.0, (285, 246)),
    ("kpi2_value", (662, 186, 780, 232), "card", 32.0, (669, 199)),
    ("kpi3_value", (1046, 186, 1240, 232), "card", 32.0, (1053, 199)),
    ("kpi3_delta", (1046, 232, 1240, 270), "card", 16.0, (1053, 246)),
    ("chart_title", (278, 330, 470, 374), "card", 22.0, (286, 336)),
    ("chart_period", (880, 330, 1010, 374), "card", 17.0, (900, 338)),
    ("chart_unit", (278, 374, 400, 394), "card", 13.2, (288, 376)),
    ("tick_120", (262, 394, 330, 418), "card", 13.0, (300, 398)),
    ("tick_0", (262, 538, 330, 562), "card", 13.0, (314, 543)),
    ("month_apr", (340, 552, 430, 584), "card", 13.5, (373, 561)),
    ("month_sep", (852, 552, 930, 584), "card", 13.5, (877, 561)),
    ("activity_title", (1046, 330, 1260, 374), "card", 22.0, (1055, 335)),
    ("activity1", (1068, 386, 1300, 416), "card", 17.0, (1078, 395)),
    ("activity1_time", (1068, 414, 1300, 442), "card", 14.0, (1078, 423)),
    ("activity3", (1068, 508, 1300, 540), "card", 17.0, (1078, 516)),
    ("activity3_time", (1068, 536, 1300, 562), "card", 14.0, (1078, 543)),
    ("table_title", (278, 636, 520, 672), "card", 22.0, (286, 645)),
    ("tbl_hdr_project", (280, 686, 400, 718), "card", 12.5, (299, 699)),
    ("tbl_hdr_due", (1220, 686, 1300, 718), "card", 12.5, (1231, 699)),
    ("row1_name", (280, 724, 620, 758), "card", 16.2, (299, 735)),
    ("row1_owner", (740, 724, 900, 758), "card", 16.0, (783, 735)),
    ("row1_due", (1200, 724, 1330, 758), "card", 16.0, (1231, 735)),
    ("row3_name", (280, 796, 620, 828), "card", 16.2, (299, 805)),
    ("brand", (72, 26, 216, 68), "sb", 19.0, (73, 38)),
    ("nav_overview", (54, 120, 216, 160), "navsel", 19.0, (62.5, 126)),
    ("nav_projects", (54, 184, 216, 220), "sb", 19.0, (62.5, 191)),
    ("nav_settings", (54, 312, 216, 348), "sb", 19.0, (62.5, 319)),
    ("ws_tag", (30, 764, 214, 792), "ws", 13.0, (38.5, 770)),
    ("ws_main", (30, 796, 214, 826), "ws", 16.0, (38.5, 804)),
    ("ws_sub", (30, 828, 214, 858), "ws", 14.0, (38.5, 836)),
    ("pill_inprogress", (1024, 729, 1180, 756), "pillb", 13.0, None),
    ("pill_review", (1024, 764, 1180, 791), "pilla", 13.0, None),
    ("pill_done", (1024, 799, 1180, 826), "pillg", 13.0, None),
]


def glyphs(arr, bg, white, sb, navsel):
    out = {}
    for tag, roi, kind, _size, _exp in GLYPH_ROIS:
        bgrnd = {"bg": bg, "card": white, "sb": sb, "navsel": navsel,
                 "ws": np.array([35, 57, 84]),
                 "pillb": np.array([231, 239, 255]),
                 "pilla": np.array([255, 243, 215]),
                 "pillg": np.array([220, 245, 236])}[kind]
        out[tag] = bbox_ink(arr, roi, bgrnd)
    return out


# ---------------------------------------------------------------- 颜色采样
# "fill"：纯色角色，取窗口中心的像素。
# "text"：文字角色，取窗口内 |像素−底色| 通道和最大处（满覆盖率文字体素，
#         避开抗锯齿混色）——直接取单点会把真色 #168267 量成混色 #0E7F67。
FILL_ROIS = [
    ("主背景", (720, 120), "主背景铺底"),
    ("侧栏底", (28, 460), "侧栏铺底"),
    ("卡片底", (1360, 200), "KPI 卡内空白"),
    ("卡片边框", (260, 200), "卡片 1 px 描边"),
    # 采样点必须落在纯色填充里，不能压到按钮上的白色文字：(1330,71) 在重建图里正好
    # 落在白色字形上，会把主蓝量成 (247,249,254)。改到按钮内缘 (1200,71)，参考与重建
    # 都是 (36,92,228)。柱体单独取样验证「按钮=柱体」这一说法，而不是只写备注。
    ("主蓝（导出按钮）", (1200, 71), "导出按钮填充"),
    ("柱体填充", (888, 500), "图表最后一根柱体内（顶缘 y=420 与零线 y=549 之间），"
                            "应与按钮同为主蓝"),
    ("网格线", (400, 549), "0 刻度网格线"),
    ("行分隔线", (900, 760), "表格行间分隔"),
    ("表头带底", (900, 690), "表格表头浅底带"),
    ("导航选中底", (150, 139), "选中态外框填充"),
    ("侧栏工作区卡", (120, 800), "侧栏底部卡片填充"),
    ("胶囊 In progress 底", (1036, 742), "进行中状态底"),
    ("胶囊 Review 底", (1036, 777), "待评审状态底"),
    ("胶囊 Done 底", (1036, 812), "已完成状态底"),
    ("logo 描边", (33, 46), "品牌标记描边"),
    ("导航圆点 选中", (39, 133), "选中态圆点（取圆心，避开圆点下缘与底色的混色）"),
    ("导航圆点 未选", (39, 200), "未选圆点"),
    ("活动圆点 1", (1058, 401), "琥珀"),
    ("活动圆点 3", (1058, 521), "绿"),
]
TEXT_ROIS = [
    ("主标题", (261, 38, 594, 69), "bg", "页头主标题"),
    ("副标题", (261, 85, 506, 102), "bg", "页头次级信息"),
    ("KPI 标签", (285, 161, 348, 170), "card", "指标名"),
    ("KPI 数值", (285, 199, 432, 228), "card", "指标值"),
    ("KPI 变化", (285, 246, 341, 258), "card", "环比变化（含 −0.8 pp，同色）"),
    ("图表标题", (286, 336, 413, 351), "card", "图表区块标题"),
    ("图表周期", (900, 338, 972, 352), "card", "统计区间"),
    ("图表单位", (288, 376, 355, 384), "card", "纵轴单位"),
    ("y 轴刻度", (299, 398, 320, 407), "card", "数值刻度"),
    ("月份标签", (373, 561, 394, 573), "card", "横轴分类"),
    ("活动标题", (1055, 335, 1198, 355), "card", "活动区块标题"),
    ("活动条目", (1078, 395, 1194, 410), "card", "动态正文"),
    ("活动时间", (1078, 423, 1115, 432), "card", "动态时间"),
    ("表格标题", (286, 645, 452, 665), "card", "表格区块标题"),
    ("表头文字", (299, 699, 353, 707), "card", "列名"),
    ("行项目名", (299, 735, 459, 749), "card", "行主字段"),
    ("行负责人", (783, 735, 855, 746), "card", "行次级字段"),
    ("页脚", (260, 867, 516, 879), "bg", "页脚说明"),
    ("品牌名", (73, 38, 188, 51), "sb", "侧栏品牌"),
    ("导航选中文字", (62, 126, 149, 140), "navsel", "当前页"),
    ("导航未选文字", (62, 191, 134, 208), "sb", "非当前页"),
    ("PRO WORKSPACE", (38, 770, 150, 779), "ws", "工作区标签"),
    ("团队成员数", (38, 804, 172, 815), "ws", "工作区主行"),
    ("管理入口", (38, 836, 160, 848), "ws", "工作区次行"),
    ("按钮文字", (1196, 60, 1387, 82), "btn", "导出按钮"),
    ("胶囊 In progress 字", (1035, 729, 1170, 755), "pillb", "进行中"),
    ("胶囊 Review 字", (1035, 764, 1170, 790), "pilla", "待评审"),
    ("胶囊 Done 字", (1035, 799, 1170, 825), "pillg", "已完成"),
]
_CBGS = {"bg": (243, 246, 251), "card": (255, 255, 255), "sb": (20, 35, 60),
         "navsel": (41, 68, 103), "ws": (35, 57, 84), "btn": (36, 92, 228),
         "pillb": (231, 239, 255), "pilla": (255, 243, 215),
         "pillg": (220, 245, 236)}


def colors(arr):
    """填充色与文字色分开量，方法不同，报告里也分开记。"""
    out = []
    for tag, (x, y), note in FILL_ROIS:
        out.append({"role": tag, "sample_kind": "fill", "roi": [x, y],
                    "note": note, "sample_rgb": sample(arr, x, y)})
    for tag, (x0, y0, x1, y1), bgkey, note in TEXT_ROIS:
        out.append({"role": tag, "sample_kind": "text_core",
                    "roi": [x0, y0, x1, y1], "note": note,
                    "sample_rgb": core(arr, x0, y0, x1, y1, _CBGS[bgkey])})
    return out


# ---------------------------------------------------------------- 颜色人工比较
# 同一个 RGB 值在参考图里往往承担多个视觉角色（例如 (22,130,103) 既是 KPI 变化的
# 文字色，也是胶囊 Done 的文字色）。按 token 分组记一条，roles 里列出它实际覆盖的
# 角色，避免 47 条判断互相重复；残余差异单列，不只写“颜色一致”。
TOKEN_JUDGE = {
    (243, 246, 251): "主背景与表格表头浅底带。参考与重建并排看：都是同一支偏冷的极浅灰蓝，"
                     "明度相同、饱和度相同，卡片浮在这层底上时对比关系一致。",
    (20, 35, 60): "侧栏铺底。深海军蓝，蓝相一致、明度一致；侧栏内文字与卡片的层次没有变。",
    (255, 255, 255): "卡片底、品牌名、导航选中文字、工作区主行、按钮文字。白底与反白文字"
                     "均逐位相同；侧栏里白字在深蓝上的可读性关系不变。",
    (226, 232, 241): "卡片 1 px 描边。浅灰蓝描边，参考与重建在同一卡片边缘上粗细与深浅一致，"
                     "卡片没有被描边压重或压淡。",
    (36, 92, 228): "主蓝。导出按钮填充与图表最后一根柱体各自单独取样，都是 (36,92,228)；"
                   "并排看按钮和柱体的蓝相、明度一致，与胶囊 In progress 的文字色也是同一支蓝。",
    (231, 237, 245): "0 刻度网格线。极浅灰蓝细线，与背景只差一层，参考与重建一致，"
                     "网格没有变黑成实线也没有淡到看不见。",
    (235, 239, 245): "表格行间分隔线。与网格线同一族但更淡一档；并排看两条线在同一图里"
                     "的相对深浅关系保持一致。",
    (41, 68, 103): "导航选中态外框填充。比侧栏底亮一档、偏蓝一档，选中项因此可辨；"
                   "参考与重建的选中框在同一行上位置和明暗都一致。",
    (35, 57, 84): "侧栏底部工作区卡填充。落在侧栏底与选中底之间的一档，卡片边界清楚；"
                   "并排看两图工作区卡的明暗相对关系一致。",
    (231, 239, 255): "胶囊 In progress 底。极浅蓝，配主蓝字；两图并排底色深浅一致。",
    (255, 243, 215): "胶囊 Review 底。极浅琥珀，配琥珀字；两图并排底色深浅一致。",
    (220, 245, 236): "胶囊 Done 底。极浅绿，配绿字；两图并排底色深浅一致。",
    (100, 219, 182): "薄荷绿。logo 描边、导航选中圆点、PRO WORKSPACE 文字三处共用；"
                     "采样逐位相同，并排看三处绿是同支薄荷绿，明度一致。",
    (119, 145, 179): "未选导航圆点。中灰蓝，明显比选中绿圆点点缀更弱；两图并排圆点深浅一致。",
    (234, 175, 64): "活动圆点（琥珀）。活动流第 1 条圆点；两图并排同一颗圆点的色相与明度一致。",
    (22, 130, 103): "深绿。KPI 变化文字与胶囊 Done 文字共用；采样取的是满覆盖文字体素，"
                    "逐位相同，不是抗锯齿混色。",
    (24, 40, 63): "主要墨色。主标题、KPI 数值、三个区块标题、活动条目、行项目名共用；"
                  "深蓝黑，比侧栏底更暗更冷。并排看正文墨色的浓淡关系一致。",
    (99, 116, 143): "次要墨色。副标题、KPI 标签、图表周期/单位、y 轴刻度、活动时间、"
                    "表头文字、行负责人共用；中等灰蓝。并排看次级文字与主墨色的层级关系一致。",
    (123, 139, 163): "页脚墨色。比次要墨色更淡一档；两图页脚行的明度接近，"
                     "仍可读但不抢正文。",
    (190, 202, 221): "未选导航文字。在深蓝侧栏上属于低对比灰白；并排看与选中态白字的"
                     "强弱对比一致。",
    (184, 202, 221): "工作区次行（管理入口）。比同卡主行白字更淡一档；两图一致。",
    (157, 102, 19): "胶囊 Review 文字。深琥珀，压在浅琥珀底上；并排看两图这枚胶囊的"
                    "字色与底色对比度一致。",
}


def color_review(cols_r, cols_m):
    """按 RGB token 分组输出人工并排判断；每组列出它覆盖的全部角色。"""
    groups = {}
    for cr in cols_r:
        groups.setdefault(tuple(cr["sample_rgb"]), []).append(cr)
    mine_by_role = {c["role"]: c["sample_rgb"] for c in cols_m}
    out = []
    for rgb, rows in groups.items():
        # 每个角色各自记双侧采样与差值：同一 token 组若只取第一个角色的差值，
        # 会把这个 token 下别的角色（例如 y 轴刻度）的残余差藏掉。
        role_rows = []
        worst = [0, 0, 0]
        for r in rows:
            m = mine_by_role[r["role"]]
            dd = [m[i] - r["sample_rgb"][i] for i in range(3)]
            worst = [max(worst[i], abs(dd[i])) for i in range(3)]
            role_rows.append({
                "role": r["role"], "role_in_layout": r["note"],
                "sample_point_or_roi": r["roi"],
                "reference_sample_rgb": r["sample_rgb"],
                "reconstructed_sample_rgb": m,
                "delta_rgb": dd,
                "exact": dd == [0, 0, 0],
            })
        out.append({
            "path_base": "output_dir",
            "token_rgb": list(rgb),
            "token_hex": "#%02X%02X%02X" % rgb,
            "sample_kind": rows[0]["sample_kind"],
            "roles": role_rows,
            "roles_count": len(role_rows),
            "delta_rgb_max_abs": worst,
            "manual_side_by_side_review": (
                "review/01-page-pair.png（整页并排）+ 对应区块对照图"),
            "judgement": TOKEN_JUDGE.get(rgb, None),
            "residual_difference": (
                "无（该 token 下 %d 个角色采样三通道逐位相同）" % len(role_rows)
                if all(v == 0 for v in worst)
                else "该 token 下有角色的采样三通道最大差 %s，见 residual_roles"
                     % worst),
        })
    # 残余差异集中说明：只出现在小字号文字的采样点上
    for e in out:
        if e["delta_rgb_max_abs"] != [0, 0, 0]:
            resid = [{"role": r["role"], "delta_rgb": r["delta_rgb"]}
                     for r in e["roles"] if r["delta_rgb"] != [0, 0, 0]]
            e["residual_roles"] = resid
            e["residual_difference"] = (
                "三通道最大差 %s，只出现在：%s。这些角色的文字是 13 px 级小字号，"
                "笔画只有 1–2 px 宽，窗口内取到的「核心像素」会掺进抗锯齿混色，"
                "量出来的不是纯 token 值而是 token 与底色的过渡色。并排看两图这几处"
                "文字色相与明暗一致，差值来自采样口径；同一 token 下 17 px 以上的"
                "角色（副标题、KPI 标签等）采样逐位相同。"
                % (e["delta_rgb_max_abs"], "、".join(r["role"] for r in resid)))
    return out


# ---------------------------------------------------------------- 看图记录
# 每一条都对应一次实际打开过 review/ 里的对照图（不是预设清单）。pair 图上半是参考、
# 下半是重建，所以结论里可以直接说「上下对比」。
VISUAL_REVIEWS = [
    ("review/00-thumbnail.png", "缩略（720×450）",
     "整体版面对得上：深蓝侧栏 + 浅色主区、上排三张 KPI 卡、下方左大图右活动流、"
     "底部通栏表格，比例与页边距在缩略尺度下没有可辨差异；没有明显缺块或多出的装饰。"),
    ("review/01-page-pair.png", "原尺寸整页并排（1440×900）",
     "区块边界、卡片圆角、行高节奏一致。并排逐区看下来没有遮挡、裁切或文字溢出版心；"
     "侧栏与主区分界、表格通栏右缘对齐都一致。"),
    ("review/02-kpi-row-pair.png", "KPI 行并排",
     "三张卡等宽等高、间距一致；标签—数值—变化的垂直节奏一致，数值基线对齐；"
     "第三个变化值前的负号与单位排布一致，绿色变化文字位置一致。"),
    ("review/03-chart-pair.png", "图表卡并排",
     "纵轴刻度自上而下 120→0、柱底都落在零线上、柱宽与柱间距一致、横轴月份标签居中对齐柱；"
     "「¥ thousand」单位在左上、「Apr – Sep」在右上，与标题在同一水平带。"),
    ("review/04-activity-pair.png", "活动流并排",
     "三条动态的圆点—正文—时间结构一致，圆点垂直居中于首行文字，时间缩进一致；"
     "第 2 条圆点为蓝、第 1、3 条为琥珀与绿，与参考的角色分配一致。"),
    ("review/05-table-pair.png", "表格卡并排",
     "表头浅底带两端都内缩（参考 [284,688,1373,721]，比卡片内容右缘 1398 短 25 px，"
     "并不是贯通卡宽——首版按贯通卡宽画成 1399，1× 并排看不出，收紧审计窗口后才露出），"
     "两条行分隔线与带同宽；四列表位置一致；五行行高一致；"
     "胶囊在最后一列右对齐、垂直居中于行内。"),
    ("review/06-sidebar-pair.png", "侧栏并排（含 logo 与工作区卡）",
     "logo 是同心圆环而不是矩形环，外缘与内孔比例一致；品牌名与其右侧对齐一致；"
     "四项导航的行距与圆点位置一致，选中态只有 Overview 有底框；底部工作区卡三行层级一致。"),
    ("review/07-title-pair.png", "页头标题 2× 放大",
     "主标题与副标题的字号、字重、颜色层级一致；主标题下沿与副标题上沿的间距一致；"
     "两行左缘同对齐线。"),
    ("review/08-bars-pair.png", "柱体 1.5× 放大",
     "柱体填充色、柱宽、柱间距、柱底基线一致；6 根柱的高度比例与参考一致。"),
    ("review/09-bar-top-pair.png", "单根柱 4× 放大",
     "柱顶左右两角都是圆角、柱底为直角，两图一致——圆角只作用在顶部；"
     "圆角半径目测量级相同，没有把整条柱做成胶囊形。"),
    ("review/10-yaxis-pair.png", "纵轴 3× 放大",
     "刻度顺序自上而下 120、90、60、30、0，两图一致；刻度文字右对齐、贴左留白一致；"
     "0 刻度与网格线重合，柱底也压在同一根零线上。"),
]


def visual_reviews():
    return [{"path_base": "output_dir", "path": p, "view": v, "conclusion": c}
            for p, v, c in VISUAL_REVIEWS]


# ---------------------------------------------------------------- 误差
def err_point(r, m):
    if not r or not m:
        return None
    return [round(m[0] - r[0], 2), round(m[1] - r[1], 2)]


def err_rect(r, m):
    if not r or not m:
        return None
    d = [round(m[i] - r[i], 2) for i in range(4)]
    return {"left": d[0], "top": d[1], "right": d[2], "bottom": d[3],
            "max_abs": max(abs(v) for v in d)}


def err_line(r, m):
    if r is None or m is None:
        return None
    return round(m - r, 2)


ANCHOR_SPECS = [
    # key, 名称, 类型, 象限/覆盖说明
    ("sidebar_right", "侧栏右边界", "line", "纵向贯通，Q1–Q3 分界"),
    ("nav_selected_box", "导航选中态外框", "rect", "左上象限"),
    ("title_ink", "主标题可见字形框左上角", "point", "左上象限（取左上角点）"),
    ("kpi_card_1", "KPI 卡①外框（收入）", "rect", "上中左"),
    ("kpi_card_2", "KPI 卡②外框（订单）", "rect", "上中右"),
    ("kpi_card_3", "KPI 卡③外框（退款率）", "rect", "右上象限"),
    ("chart_card", "净收入图表卡外框", "rect", "图表区 + 左下"),
    ("zero_line", "图表零线左端点", "point", "图表区"),
    ("last_bar", "最后一根柱的顶部中心", "point", "图表区（取顶缘中点）"),
    ("activity_card", "活动卡外框", "rect", "右上 / 右中"),
    ("table_card", "项目表格卡外框", "rect", "下沿，Q3–Q4"),
    ("last_pill", "最后一行状态标签外框", "rect", "右下象限"),
    ("export_button", "导出按钮外框", "rect", "右上象限"),
    ("workspace_card", "侧栏工作区卡外框", "rect", "左下象限"),
    ("footer_ink", "页脚说明字形框左上角", "point", "左下象限"),
    ("header_band", "表格表头浅色带外框", "rect", "下沿左侧，Q3"),
    ("divider_1", "表格第 1 条行分隔线外框", "rect", "下沿，Q3–Q4"),
    ("divider_2", "表格第 2 条行分隔线外框", "rect", "下沿，Q4"),
    ("logo_ring", "侧栏品牌标记圆环", "rect", "左上象限"),
]

METHODS = {
    "sidebar_right": "行 y=500 从 x=180 向右扫，取第一个与侧栏底色 (20,35,60) "
                     "色差 > 8 的列",
    "nav_selected_box": "窗口 (4,108)-(218,186) 内与选中底色 (41,68,103) 色差 ≤ 16 "
                        "的像素外接框；窗口切在第 2 行文字之前，避免抗锯齿混色被计入",
    "title_ink": "窗口 (236,16)-(780,82) 内相对页面底色 (243,246,251) 的墨迹框，"
                 "阈值取窗口最大色差的 50%（≈50% 覆盖率，去抗锯齿晕影）；取左上角",
    "kpi_card_1": "窗口 = 卡外扩 10 px；窗口内与页面底色色差 > 8 的像素外接框"
                  "（1 px 边框对底色差 17，可辨）",
    "kpi_card_2": "同 kpi_card_1，窗口随卡②平移",
    "kpi_card_3": "同 kpi_card_1，窗口随卡③平移",
    "chart_card": "窗口 (250,300)-(1010,605) 内与页面底色色差 > 8 的像素外接框",
    "zero_line": "行 y=549 上「比卡片白暗一点点」（与白差 6–48）的像素最左列，"
                 "端点 y 取网格线行号 549",
    "last_bar": "窗口 x 848–928、y 400–553 内与柱体蓝 (36,92,228) 色差 ≤ 40 的"
                "像素；中心 x = (最左列+最右列)/2，顶部 y = 最上排",
    "activity_card": "窗口 (1020,300)-(1409,605) 内与页面底色色差 > 8 的像素外接框",
    "table_card": "窗口 (250,614)-(1409,851) 内与页面底色色差 > 8 的像素外接框",
    "last_pill": "窗口 (1012,790)-(1192,836) 内与 Done 底色 (220,245,236) 色差 "
                 "≤ 20 的像素外接框",
    "export_button": "窗口 (1140,30)-(1420,110) 内与主蓝 (36,92,228) 色差 ≤ 40 的"
                     "像素外接框",
    "workspace_card": "窗口 (6,700)-(218,884) 内与工作区卡底色 (35,57,84) 色差 "
                      "≤ 18 的像素外接框",
    "footer_ink": "窗口 (240,856)-(820,890) 内相对页面底色的墨迹框，阈值同"
                  " title_ink；取左上角",
    "header_band": "窗口 (262,640)-(1398,755) 严格落在表格卡内部；取与带色 "
                   "(243,246,251) 色差 ≤ 6 的像素，先按「整行命中数 ≥ 60% 行宽」"
                   "筛出带所在行再取列范围，不用外接框。两点必要：窗口不能出卡"
                   "（卡外页面底色与带同色，首版窗口右界 1408 越过卡右缘 1399 "
                   "后把整列卡外底色算成带，top/bottom/right 都顶到窗口边界，"
                   "0 误差是窗口自证）；也不能直接取外接框（标题与正文的抗锯齿"
                   "晕影有不少像素落在带色 ±6 内，散在 y 645–665 与 745 附近，"
                   "会把 top 拉早 25 px）。窗口纵向避开卡圆角与 y≈760 的行"
                   "分隔线（(235,239,245) 与带色差 8，tol 6 内可分开）",
    "divider_1": "窗口 (262,754)-(1398,766) 内与分隔线色 (235,239,245) 色差 "
                 "≤ 10 的像素外接框；窗口夹在第 1 行墨迹底 749 与第 2 行墨迹顶 "
                 "770 之间，只含这一条线",
    "divider_2": "窗口 (262,789)-(1398,801) 内与分隔线色 (235,239,245) 色差 "
                 "≤ 10 的像素外接框；窗口夹在第 2 行墨迹底 784 与第 3 行墨迹顶 "
                 "805 之间，只含这一条线",
    "logo_ring": "窗口 (20,24)-(80,70) 内与描边色 (100,219,182) 色差 ≤ 40 的像素"
                 "外接框；窗口右界 80 切在品牌文字之前，避免白色文字被计入围框",
}


def build_audit() -> dict:
    if not REF.exists():
        raise SystemExit("找不到参考图 %s" % REF)
    if not MINE.exists():
        raise SystemExit("重建图尚未生成：%s" % MINE)
    arr_r = load(REF)
    arr_m = load(MINE)
    bg = np.array([243, 246, 251])
    white = np.array([255, 255, 255])
    sb = np.array([20, 35, 60])
    navsel = np.array([41, 68, 103])

    mr = measure(arr_r, bg, white, sb)
    mm = measure(arr_m, bg, white, sb)
    gr = glyphs(arr_r, bg, white, sb, navsel)
    gm = glyphs(arr_m, bg, white, sb, navsel)

    anchors = []
    for key, name, kind, cover in ANCHOR_SPECS:
        rv, mv = mr[key]["value"], mm[key]["value"]
        if key == "sidebar_right":
            ref, rec, err = rv, mv, err_line(rv, mv)
            detail = "x=%s vs x=%s" % (rv, mv)
        elif key == "title_ink" or key == "footer_ink":
            # 点项只比左上角；整框留在 local_evidence 里给宽度/字高的残余差异看
            ref, rec, err = rv[:2], mv[:2], err_point(rv, mv)
            detail = "[%s,%s,%s,%s] vs [%s,%s,%s,%s]，取左上角" % tuple(rv + mv)
        elif key == "zero_line":
            ref, rec, err = rv, mv, err_point(rv, mv)
            detail = "(%s,%s) vs (%s,%s)" % (rv[0], rv[1], mv[0], mv[1])
        elif key == "last_bar":
            ref, rec, err = [rv[0], rv[1]], [mv[0], mv[1]], err_point(rv, mv)
            detail = "顶缘中点 (%s,%s) vs (%s,%s)" % (rv[0], rv[1], mv[0], mv[1])
        else:
            ref, rec = rv, mv
            er = err_rect(rv, mv)
            err = er["max_abs"] if er else None
            detail = ( "[%s,%s,%s,%s]" % tuple(rv) if rv else "未检出"
                        + " vs " + ("[%s,%s,%s,%s]" % tuple(mv) if mv else "未检出")
                        + ("（四边误差 左%+.1f 上%+.1f 右%+.1f 下%+.1f）"
                           % (er["left"], er["top"], er["right"], er["bottom"])
                           if er else ""))
        ok = (err is not None and abs(err) <= TOL_PX) if not isinstance(err, list) \
            else (err is not None
                  and all(abs(v) <= TOL_PX for v in err))
        anchors.append({
            "anchor_id": key,
            "name": name,
            "type": kind,
            "covers": cover,
            "reference_estimated": ref,
            "reconstructed": rec,
            "error": err,
            "tolerance_px": TOL_PX,
            "pass": bool(ok),
            "measurement_method": METHODS[key],
            "local_evidence": detail,
        })

    glyph_report = []
    for tag, roi, kind, size, exp in GLYPH_ROIS:
        r, m = gr[tag], gm[tag]
        rec = {"element": tag, "font_size_px": size,
               "expected_ink_top_left": list(exp) if exp else None,
               "reference": r, "reconstructed": m,
               "measure_method": "与 title_ink 同一阈值：ROI 内相对该元素底色"
                                 "最大色差的 50%"}
        if not r or not m:
            rec["note"] = "有一侧未检出"
            glyph_report.append(rec)
            continue
        e = [round(m[i] - r[i], 1) for i in range(4)]
        rec.update({"delta": {"left": e[0], "top": e[1],
                              "right": e[2], "bottom": e[3]},
                    "ink_h": [r[3] - r[1] + 1, m[3] - m[1] + 1],
                    "ink_w": [r[2] - r[0] + 1, m[2] - m[0] + 1]})
        # 墨迹相对该元素理论墨迹左上角的偏移，两侧同算：
        # 偏移一致说明位置对了；只有一侧偏说明是渲染字号/基线差异。
        if exp:
            rec["offset_vs_expected"] = {
                "reference": [round(r[0] - exp[0], 1), round(r[1] - exp[1], 1)],
                "reconstructed": [round(m[0] - exp[0], 1),
                                  round(m[1] - exp[1], 1)]}
        # 由墨迹高度反推的「墨迹顶距字面框顶」比值，与 EM_INK_TOP=0.32 对照
        rec["ink_top_over_em"] = [round((r[3] - r[1] + 1) / size, 3),
                                  round((m[3] - m[1] + 1) / size, 3)]
        glyph_report.append(rec)

    n_ok = sum(1 for a in anchors if a["pass"])
    return {
        "schema_version": 1,
        "task_id": TASK,
        "path_base": "output_dir",
        "reference_image": {"path_base": "task_input_root",
                            "path": "tasks/A15-reference-reconstruction/inputs/"
                                    "reference.png"},
        "reconstructed_image": {
            "path_base": "output_dir", "path": "reconstructed.png"},
        "reconstructed_dsl": {"path_base": "output_dir",
                              "path": "reconstructed.snapshot"},
        "tolerance_px_per_component": TOL_PX,
        "anchors_checked": len(anchors),
        "anchors_pass": n_ok,
        "anchors": anchors,
        "glyph_boxes": glyph_report,
        "color_review": [],
        "visual_reviews": visual_reviews(),
    }, colors(arr_r), colors(arr_m), arr_r, arr_m


# ---------------------------------------------------------------- 局部放大
def crops(audit, cols_r, cols_m) -> list[str]:
    dirs = [OUT / "review", TMP / "gen" / "crops"]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
    im_r = Image.open(REF).convert("RGB")
    im_m = Image.open(MINE).convert("RGB")
    names = []
    specs = [
        ("01-page", (0, 0, 1440, 900), 1.0),
        ("02-kpi-row", (240, 120, 1412, 300), 1.0),
        ("03-chart", (244, 296, 1016, 610), 1.0),
        ("04-activity", (1016, 296, 1412, 610), 1.0),
        ("05-table", (244, 610, 1412, 862), 1.0),
        ("06-sidebar", (0, 0, 240, 900), 1.0),
        ("07-title", (244, 20, 700, 116), 2.0),
        ("08-bars", (270, 392, 1006, 590), 1.5),
        # 柱顶圆角只有 6 px，1.5× 看不准，单独裁一根柱到 4× 看顶/底角
        ("09-bar-top", (352, 470, 470, 558), 4.0),
        # y 轴刻度与柱底的关系：刻度是否自上而下 120→0、柱底是否落在零线上
        ("10-yaxis", (276, 392, 360, 578), 3.0),
    ]
    for tag, box, scale in specs:
        cr = im_r.crop(box)
        cm = im_m.crop(box)
        if scale != 1.0:
            cr = cr.resize((int(cr.width * scale), int(cr.height * scale)),
                           Image.NEAREST)
            cm = cm.resize((int(cm.width * scale), int(cm.height * scale)),
                           Image.NEAREST)
        pair = Image.new("RGB", (cr.width, cr.height * 2 + 12), (255, 255, 255))
        pair.paste(cr, (0, 0))
        pair.paste(cm, (0, cr.height + 12))
        fn = "%s-pair.png" % tag
        pair.save(OUT / "review" / fn)
        names.append(fn)
        cr.save(TMP / "gen" / "crops" / ("%s-ref.png" % tag))
        cm.save(TMP / "gen" / "crops" / ("%s-mine.png" % tag))
    # 缩略图：整体缩到 720×450 看整体关系
    im_m.resize((720, 450), Image.LANCZOS).save(OUT / "review" / "00-thumbnail.png")
    im_r.resize((720, 450), Image.LANCZOS).save(OUT / "review" / "00-thumbnail-ref.png")
    names.append("00-thumbnail.png")
    return names


def main() -> int:
    audit, cols_r, cols_m, arr_r, arr_m = build_audit()

    # 颜色：题面要求给「主背景、侧栏、主蓝、卡片、状态标签」等色彩角色做人工并排
    # 判断，采样只能当佐证。这里按 token 分组，每组列出它覆盖的角色、双侧采样值与
    # 人工判断；残余差异单独写原因，不只写「颜色一致」。
    crs = color_review(cols_r, cols_m)
    audit["color_review"] = crs
    n_roles = sum(g["roles_count"] for g in crs)
    n_exact_roles = sum(1 for g in crs for r in g["roles"] if r["exact"])
    audit["color_review_summary"] = {
        "path_base": "output_dir",
        "roles_sampled": n_roles,
        "roles_exact_on_both_sides": n_exact_roles,
        "roles_with_residual_delta": n_roles - n_exact_roles,
        "fill_roles": sum(1 for c in cols_r if c["sample_kind"] == "fill"),
        "text_roles": sum(1 for c in cols_r if c["sample_kind"] == "text_core"),
        "tokens_grouped": len(crs),
        "tokens_exact_on_both_sides": sum(
            1 for g in crs if g["delta_rgb_max_abs"] == [0, 0, 0]),
        "tokens_with_residual_delta": [
            {"token_rgb": g["token_rgb"], "delta_rgb_max_abs": g["delta_rgb_max_abs"],
             "residual_roles": [r["role"] for r in g["residual_roles"]]}
            for g in crs if g["delta_rgb_max_abs"] != [0, 0, 0]],
        "required_roles_covered": [
            "主背景", "侧栏底", "主蓝（导出按钮）", "柱体填充", "卡片底", "卡片边框",
            "胶囊 In progress 底", "胶囊 Review 底", "胶囊 Done 底",
            "胶囊 In progress 字", "胶囊 Review 字", "胶囊 Done 字",
            "导航选中底", "导航圆点 选中", "logo 描边", "侧栏工作区卡"],
        "method_note": "填充色取窗口中心单像素；文字色取窗口内相对底色 |像素−底色| "
                       "通道和最大处的核心像素，避开抗锯齿混色。题面未公开 RGB/色差"
                       "硬阈值，这里只记录采样与人工判断，不据此判定合格。",
    }

    n_ok = audit["anchors_pass"]
    print("锚点：%d/%d 在 ±%d px 内" % (n_ok, audit["anchors_checked"], TOL_PX))
    for a in audit["anchors"]:
        flag = "OK " if a["pass"] else "FAIL"
        print("  %-3s %-24s 误差 %s" % (flag, a["anchor_id"], a["error"]))

    worst = max(audit["glyph_boxes"],
                key=lambda g: max(abs(g["delta"]["left"]), abs(g["delta"]["top"]),
                                  abs(g["delta"]["right"]), abs(g["delta"]["bottom"]))
                if "delta" in g else -1)
    print("\n字形框（严格阈值）偏差最大的元素：%s %s" % (worst["element"], worst))

    names = crops(audit, cols_r, cols_m)
    print("\n导出对照放大图 %d 张 ->" % len(names), S.rel(OUT / "review"))

    (OUT / "reconstruction-audit.json").write_text(
        json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("->", S.rel(OUT / "reconstruction-audit.json"))
    (TMP / "gen" / "color-samples.json").write_text(
        json.dumps({"reference": cols_r, "reconstructed": cols_m},
                   ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("->", S.rel(TMP / "gen" / "color-samples.json"))
    return 0 if n_ok == audit["anchors_checked"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
