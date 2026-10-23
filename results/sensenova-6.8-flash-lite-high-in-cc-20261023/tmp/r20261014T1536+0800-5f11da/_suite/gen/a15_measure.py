"""A15 参考图量测：从公开 reference.png 提取锚点坐标与颜色采样。

题目只给 1440×900 的 reference.png 与 content.json（纯文本，无几何）。所以
「参考估计坐标」必须自己量：这里用像素扫描把 16 个锚点量出来，不靠目测。
每个锚点记录扫描方法（扫描线/扫描列 + 判据），便于复现。

坐标基准：画布左上原点，x 向右、y 向下，单位像素，框为
[left, top, right, bottom] 外轮廓（含边像素，inclusive）。

用法：python -I tmp/<rid>/_suite/gen/a15_measure.py
输出：tmp/<rid>/A15/gen/ref-anchors.json（参考侧全部量测结果）
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
import suite as S  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

TASK = "A15"
REF = ROOT / "tasks" / "A15-reference-reconstruction" / "inputs" / "reference.png"
OUT, TMP = S.task_dirs(TASK)
TMPGEN = TMP / "gen"
TMPGEN.mkdir(parents=True, exist_ok=True)

IM = Image.open(REF).convert("RGB")
W, H = IM.size
ARR = np.asarray(IM).astype(np.int16)
assert (W, H) == (1440, 900), (W, H)

ANSWERS: list[dict] = []


def rgb(x: int, y: int) -> list[int]:
    return [int(v) for v in ARR[y, x]]


def dist(c1, c2) -> int:
    return max(abs(int(c1[i]) - int(c2[i])) for i in range(3))


def runs(mask) -> list[tuple[int, int]]:
    """一维 bool 数组 → [(start, end)] 闭区间游程。"""
    out, s = [], None
    for i, v in enumerate(mask):
        if v and s is None:
            s = i
        elif not v and s is not None:
            out.append((s, i - 1))
            s = None
    if s is not None:
        out.append((s, len(mask) - 1))
    return out


def white_runs(x0: int, x1: int, y: int, thr: int = 246) -> list[tuple[int, int]]:
    """行 y 上「接近纯白」的游程，用于在白/灰边界上定位卡片左右缘。"""
    row = ARR[y, x0:x1 + 1]
    m = np.all(row >= thr, axis=1)
    return [(s + x0, e + x0) for s, e in runs(m) if e - s + 1 > 40]


def white_v_extent(x: int, y0: int, y1: int, yc: int, thr: int = 246) -> tuple[int, int]:
    """列 x 上包含 y=yc 的那段白色游程的上下缘。"""
    col = ARR[y0:y1 + 1, x]
    m = np.all(col >= thr, axis=1)
    for s, e in runs(m):
        if s <= (yc - y0) <= e:
            return y0 + s, y0 + e
    raise ValueError("列 %d 在 y=%d 处不在白色游程内" % (x, yc))


def bbox(mask) -> tuple[int, int, int, int]:
    ys, xs = np.nonzero(mask)
    return int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())


def sample_name(x: int, y: int, label: str) -> dict:
    """点采样纯色内部，作为颜色判断的辅助证据。"""
    c = rgb(x, y)
    return {"sample": label, "x": x, "y": y, "rgb": c,
            "hex": "#%02X%02X%02X" % tuple(c)}


# ---------------------------------------------------------------- 背景/侧栏
SB_BG = rgb(28, 460)
MAIN_BG = rgb(720, 120)
CARD_BG = rgb(1350, 200)

# 1) 侧栏右边界：行 y=460 上从侧栏底色切换到主背景的 x
_row = ARR[460, 180:400]
_diff = np.array([dist(p, SB_BG) for p in _row])
_sb_x = int(np.flatnonzero(_diff > 24)[0]) + 180
sidebar_right = _sb_x
ANSWERS.append({
    "key": "sidebar_right_edge", "object": "侧栏右边界（深底与浅底的交界列）",
    "type": "line_x", "ref": [_sb_x],
    "measure": "行 y=460（导航下方、工作区卡上方的纯侧栏区域），"
               "从 x=180 起逐列比对侧栏底色 %s，首个色差>24 的列即交界" % SB_BG,
})

# 2) 导航选中态外框：侧栏底色以外的一切像素（含选中底、圆点、文字）
_ry0, _ry1, _rx0, _rx1 = 96, 190, 4, 214
_roi = ARR[_ry0:_ry1 + 1, _rx0:_rx1 + 1]
_mask = np.array([dist(p, SB_BG) > 30 for p in _roi.reshape(-1, 3)]) \
    .reshape(_roi.shape[0], _roi.shape[1])
nav_sel = [int(_rx0 + v) for v in bbox(_mask)]
ANSWERS.append({
    "key": "nav_selected_box", "object": "导航选中态（Overview）外框",
    "type": "rect", "ref": nav_sel,
    "measure": "ROI x=%d..%d y=%d..%d，判据「与侧栏底色色差>30」的像素外接框；"
               "选中底色、绿色圆点与白色文字都在该框内部，外接框即选中态外框"
               % (_rx0, _rx1, _ry0, _ry1),
})

# 3) 主标题可见字形框左上角
_tr = ARR[16:80, 236:760]
_tmask = _tr.sum(axis=2) < 300
tx, ty, _, _ = bbox(_tmask)
title_tl = [int(236 + tx), int(16 + ty)]
ANSWERS.append({
    "key": "title_glyph_topleft", "object": "主标题「Workspace Overview」可见字形框左上角",
    "type": "point_tl", "ref": title_tl,
    "measure": "ROI x=236..760 y=16..80 内三通道和<300 的深色字形像素，"
               "取外接框左上角（字形外轮廓，不是基线也不是盒心）",
})

# 4-6) 三张 KPI 卡外框
kpi_rows = white_runs(240, 1400, 200)
kpi_boxes = []
for (lx, rx) in kpi_rows:
    top, bot = white_v_extent(rx - 12, 120, 320, 200)
    kpi_boxes.append([int(lx), int(top), int(rx), int(bot)])
for i, b in enumerate(kpi_boxes, 1):
    ANSWERS.append({
        "key": "kpi_card_%d_box" % i,
        "object": "第 %d 张 KPI 卡外框（REVENUE / ORDERS / REFUND RATE）" % i,
        "type": "rect", "ref": b,
        "measure": "行 y=200（卡内空白行）取白色游程定左右缘；"
                   "再沿列 x=%d（靠右缘空白列）取含 y=200 的白色游程定上下缘" % (b[2] - 12),
    })

# 7) 净收入图表卡外框
_chart_rows = white_runs(240, 1020, 636)
ch_lx, ch_rx = _chart_rows[-1] if _chart_rows else (0, 0)
ch_top, ch_bot = white_v_extent(ch_rx - 12, 300, 700, 636)
chart_card = [int(ch_lx), int(ch_top), int(ch_rx), int(ch_bot)]
ANSWERS.append({
    "key": "chart_card_box", "object": "净收入（Net revenue）图表卡外框",
    "type": "rect", "ref": chart_card,
    "measure": "行 y=636（图表卡底部空白）取最右白色游程定左右缘；"
               "列 x=%d 取含 y=636 的白色游程定上下缘" % (ch_rx - 12),
})

# 8) 图表零线左端点：绘图区内的浅灰横向网格线，取最下面一条
RULE = rgb(430, 402)
_zero_lines = []
for y in range(330, 575):
    seg = ARR[y, 300:980]
    cnt = sum(1 for p in seg if dist(p, RULE) <= 7)
    if cnt > 400:
        xs = [x for x, p in zip(range(300, 980), seg) if dist(p, RULE) <= 7]
        _zero_lines.append((y, min(xs), max(xs), cnt))
zero_y = int(np.median([l[0] for l in _zero_lines[-3:]])) if _zero_lines else None
zero_x = next(l[1] for l in _zero_lines if l[0] == zero_y) if zero_y else None
ANSWERS.append({
    "key": "chart_zero_line_left", "object": "图表零线（y=0 基线）左端点",
    "type": "point", "ref": [zero_x, zero_y],
    "measure": "在 x=300..980、y=330..575 内逐行统计与网格线色 %s 色差≤7 的像素，"
               "计数>400 的行归为一条网格线；取最下面一条（值 0），"
               "左端点 = 该行首个网格线像素的 (x, y)" % RULE,
})

# 9) 最后一根柱的顶部中心：图表卡内的蓝色柱体
BAR = rgb(896, 430)
_xsb, _ysb = [], []
for y in range(ch_top + 6, ch_bot - 2):
    for x in range(ch_lx + 40, ch_rx - 20):
        p = ARR[y, x]
        if int(p[2]) > 150 and int(p[2]) - int(p[0]) > 60 \
                and int(p[2]) - int(p[1]) > 30:
            _xsb.append(x)
            _ysb.append(y)
bx = np.array(_xsb)
by = np.array(_ysb)
colrun = runs(np.array([bx is not None]))  # 占位
cols = np.unique(bx)
groups, cur = [], [int(cols[0])]
for c in cols[1:]:
    if int(c) - cur[-1] > 4:
        groups.append(cur)
        cur = [int(c)]
    else:
        cur.append(int(c))
groups.append(cur)
last = groups[-1]
bar_xs = by[(bx >= last[0]) & (bx <= last[-1])]
bar_top = int(bar_xs.min())
bar_center_x = int(round((last[0] + last[-1]) / 2))
ANSWERS.append({
    "key": "last_bar_top_center", "object": "最后一根柱（Sep）顶部中心",
    "type": "point", "ref": [bar_center_x, bar_top],
    "measure": "图表卡内部 b>150 且 b-r>60 且 b-g>30 的蓝色柱体像素；"
               "按列号聚成 %d 组柱，取最右一组的列范围 %d..%d，"
               "中心 x 取中点、顶部 y 取该组最小 y"
               % (len(groups), last[0], last[-1]),
})

# 10) 活动卡外框
_act_rows = white_runs(1010, 1410, 612)
a_lx, a_rx = _act_rows[-1] if _act_rows else (0, 0)
a_top, a_bot = white_v_extent(a_rx - 12, 300, 700, 612)
act_card = [int(a_lx), int(a_top), int(a_rx), int(a_bot)]
ANSWERS.append({
    "key": "activity_card_box", "object": "Team activity 活动卡外框",
    "type": "rect", "ref": act_card,
    "measure": "行 y=612（活动卡底部空白）取白色游程定左右缘；"
               "列 x=%d 取含 y=612 的白色游程定上下缘" % (a_rx - 12),
})

# 11) 项目表格卡外框
_tbl_rows = white_runs(240, 1410, 866)
t_lx, t_rx = _tbl_rows[-1] if _tbl_rows else (0, 0)
t_top, t_bot = white_v_extent(t_rx - 12, 640, 900, 866)
tbl_card = [int(t_lx), int(t_top), int(t_rx), int(t_bot)]
ANSWERS.append({
    "key": "table_card_box", "object": "Recent projects 项目表格卡外框",
    "type": "rect", "ref": tbl_card,
    "measure": "行 y=866（表格卡底部空白）取最右白色游程定左右缘；"
               "列 x=%d 取含 y=866 的白色游程定上下缘" % (t_rx - 12),
})

# 12) 最后一行状态标签外框（Done 浅绿胶囊）
_tr0, _ty1, _tx0, _tx1 = 786, 832, 1010, 1230
_roi2 = ARR[_tr0:_ty1 + 1, _tx0:_tx1 + 1].reshape(-1, 3)
_g = (_roi2[:, 1] > _roi2[:, 0] + 8) & (_roi2[:, 1] > _roi2[:, 2] + 8) \
     & (_roi2.mean(axis=1) > 190)
_done = bbox(_g.reshape(_roi2.shape[0], _roi2.shape[1]))
status_done = [int(_tx0 + v) for v in _done]
ANSWERS.append({
    "key": "last_row_status_box", "object": "最后一行状态标签（Done）外框",
    "type": "rect", "ref": status_done,
    "measure": "ROI x=%d..%d y=%d..%d 内 g>r+8 且 g>b+8 且亮度>190 的浅绿胶囊"
               "像素外接框" % (_tx0, _tx1, _tr0, _ty1),
})

# 13) 侧栏底部工作区信息卡外框（左下象限）
_ws0, _ws1, _wx0, _wx1 = 740, 870, 6, 214
_roi3 = ARR[_ws0:_ws1 + 1, _wx0:_wx1 + 1]
_mask3 = np.array([dist(p, SB_BG) > 12 for p in _roi3.reshape(-1, 3)]) \
    .reshape(_roi3.shape[0], _roi3.shape[1])
ws_card = [int(_wx0 + v) for v in bbox(_mask3)]
ANSWERS.append({
    "key": "workspace_card_box", "object": "侧栏底部工作区信息卡外框",
    "type": "rect", "ref": ws_card,
    "measure": "ROI x=%d..%d y=%d..%d 内「与侧栏底色色差>12」的像素外接框；"
               "该卡底色比侧栏略亮，色差阈值必须小，否则漏掉卡体"
               % (_wx0, _wx1, _ws0, _ws1),
})

# 14) 品牌 logo 标记外框（左上象限）
_lm0, _lm1, _lx0, _lx1 = 18, 80, 20, 100
_roi4 = ARR[_lm0:_lm1 + 1, _lx0:_lx1 + 1]
_mask4 = np.array([dist(p, SB_BG) > 40 for p in _roi4.reshape(-1, 3)]) \
    .reshape(_roi4.shape[0], _roi4.shape[1])
logo_box = [int(_lx0 + v) for v in bbox(_mask4)]
ANSWERS.append({
    "key": "logo_box", "object": "侧栏品牌 logo 标记外框",
    "type": "rect", "ref": logo_box,
    "measure": "ROI x=%d..%d y=%d..%d 内「与侧栏底色色差>40」的像素外接框"
               % (_lx0, _lx1, _lm0, _lm1),
})

# 15) 导出按钮外框（右上象限）
_btn0, _btn1, _bx0, _bx1 = 40, 104, 1150, 1410
_roi5 = ARR[_btn0:_btn1 + 1, _bx0:_bx1 + 1]
_mask5 = np.array([dist(p, MAIN_BG) > 40 for p in _roi5.reshape(-1, 3)]) \
    .reshape(_roi5.shape[0], _roi5.shape[1])
btn_box = [int(_bx0 + v) for v in bbox(_mask5)]
ANSWERS.append({
    "key": "export_button_box", "object": "Export report 按钮外框",
    "type": "rect", "ref": btn_box,
    "measure": "ROI x=%d..%d y=%d..%d 内「与主背景色差>40」的像素外接框；"
               "按钮体为饱和蓝，文字为白，都在外接框内"
               % (_bx0, _bx1, _btn0, _btn1),
})

# 16) 表格表头带外框
_hdr0, _hdr1, _hx0, _hx1 = 676, 734, 250, 1400
_roi6 = ARR[_hdr0:_hdr1 + 1, _hx0:_hx1 + 1]
_hdr_col = rgb(300, 706)
_mask6 = np.array([dist(p, CARD_BG) > 6 and dist(p, CARD_BG) <= 26
                   for p in _roi6.reshape(-1, 3)]).reshape(_roi6.shape[0], _roi6.shape[1])
hdr_box = [int(_hx0 + v) for v in bbox(_mask6)]
ANSWERS.append({
    "key": "table_header_band", "object": "表格表头带外框（PROJECT/OWNER/STATUS/DUE 所在行）",
    "type": "rect", "ref": hdr_box,
    "measure": "ROI x=%d..%d y=%d..%d 内「与卡片白底色差在 6..26」的浅灰表头底"
               "像素外接框（色差>26 会命中表头文字）"
               % (_hx0, _hx1, _hdr0, _hdr1),
})

# 17) 活动卡三条记录的时间列左侧圆点位置（图表/列表区域补充锚点）
dots = []
for yy in range(390, 540):
    for xx in range(1040, 1075):
        p = ARR[yy, xx]
        if dist(p, CARD_BG) > 40:
            dots.append((xx, yy, [int(v) for v in p]))
            break
_dot_rows, prev = [], None
for xx, yy, c in dots:
    if prev is None or yy - prev > 6:
        _dot_rows.append([xx, yy, c])
    prev = yy
ANSWERS.append({
    "key": "activity_dots", "object": "活动卡三条记录的指示圆点（左缘/中心行）",
    "type": "points", "ref": _dot_rows,
    "measure": "活动卡内 x=1040..1075 逐行找首个与卡片底色色差>40 的像素，"
               "按行聚成 3 组，取每组首个像素位置与颜色",
})

# ---------------------------------------------------------------- 颜色采样
colors = [
    sample_name(720, 120, "主背景 main_bg"),
    sample_name(28, 460, "侧栏底 sidebar_bg"),
    sample_name(150, 122, "导航选中底 nav_selected_fill"),
    sample_name(1350, 200, "卡片底 card_bg"),
    sample_name(1230, 71, "主蓝色按钮 button_blue"),
    sample_name(896, 430, "图表柱体 bar_blue"),
    sample_name(262, 44, "主标题墨色 title_ink"),
    sample_name(300, 706, "表头底 table_header_bg"),
    sample_name(1120, 813, "状态胶囊 Done 底 status_done_bg"),
    sample_name(1120, 785, "状态胶囊 Review 底 status_review_bg"),
    sample_name(1120, 741, "状态胶囊 In progress 底 status_progress_bg"),
    sample_name(1057, 402, "活动圆点 1 dot_1"),
    sample_name(1057, 463, "活动圆点 2 dot_2"),
    sample_name(1057, 523, "活动圆点 3 dot_3"),
    sample_name(290, 252, "KPI 变化值绿 kpi_change_green"),
    sample_name(48, 46, "logo 绿 logo_green"),
]

payload = {
    "schema_version": 1,
    "task_id": TASK,
    "path_base": "output_dir",
    "source": {"path_base": "suite_root",
               "path": "tasks/A15-reference-reconstruction/inputs/reference.png",
               "width": W, "height": H, "mode": IM.mode,
               "note": "题目提供的公开参考图；无作者源码或标准坐标，"
                       "参考坐标全部由像素扫描量出"},
    "coordinate_convention": "画布左上原点，x 向右 / y 向下，像素；"
                             "矩形为 [left, top, right, bottom] 外轮廓（inclusive）",
    "tolerance_px": 8,
    "anchors": ANSWERS,
    "color_samples": colors,
    "measured_at": S.now_iso(),
    "timezone": S.TZ_NAME,
}

(TMPGEN / "ref-anchors.json").write_text(
    json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print("参考图 %dx%d，锚点 %d 项，颜色采样 %d 项" % (W, H, len(ANSWERS), len(colors)))
for a in ANSWERS:
    print("  %-24s %-6s %s" % (a["key"], a["type"], a["ref"]))
print("\n颜色采样：")
for c in colors:
    print("  %-26s %s  rgb=%s" % (c["sample"], c["hex"], c["rgb"]))
