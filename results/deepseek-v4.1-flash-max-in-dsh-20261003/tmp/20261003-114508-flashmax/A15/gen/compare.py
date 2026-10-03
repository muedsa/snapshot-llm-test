"""A15 · anchor-by-anchor comparison between the reference and the reconstruction.

Both images are measured with the same functions (gen/measure.py) so the deltas are
like-for-like. Writes reconstruction-audit.json.
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from measure import measure  # noqa: E402

ROOT = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh"
TMP = os.path.join(ROOT, "tmp", "20261003-114508-flashmax", "A15")
OUT = os.path.join(ROOT, "outputs", "20261003-114508-flashmax", "A15")
REF = os.path.join(ROOT, "tasks", "A15-reference-reconstruction", "inputs", "reference.png")

TOL = 8

# (id, label, quadrant, metric-key, index-or-None, axis-of-interest)
ANCHORS = [
    ("A01", "侧栏右边界（画布左上象限的外框）", "canvas", "sidebar_right_edge_x", None, "x"),
    ("A02", "页面背景起点 / 主区左边界", "canvas", "sidebar_right_edge_x", None, "x"),
    ("A03", "主标题 Workspace Overview 文字块", "top-left", "title_ink", None, "box"),
    ("A04", "副标题文字块", "top-left", "subtitle_ink", None, "box"),
    ("A05", "Export report 按钮", "top-right", "export_button", None, "box"),
    ("A06", "KPI 卡片 1 边界", "top-left", "kpi_cards_x", 0, "span"),
    ("A07", "KPI 卡片 2 边界", "top-center", "kpi_cards_x", 1, "span"),
    ("A08", "KPI 卡片 3 边界", "top-right", "kpi_cards_x", 2, "span"),
    ("A09", "KPI 卡片行上下边界", "top-left", "kpi_card1_y", None, "span"),
    ("A10", "图表卡片边界", "bottom-left", "chart_card_box", None, "box"),
    ("A11", "图表零线（0 刻度网格线）", "chart", "chart_gridlines_y", -1, "y"),
    ("A12", "图表 120 刻度网格线", "chart", "chart_gridlines_y", 0, "y"),
    ("A13", "图表柱：Apr", "chart", "chart_bars", 0, "span"),
    ("A14", "图表柱：Sep", "chart", "chart_bars", 5, "span"),
    ("A15", "图表柱：Apr 柱顶高度", "chart", "chart_bars", 0, "top"),
    ("A16", "图表柱：Sep 柱顶高度", "chart", "chart_bars", 5, "top"),
    ("A17", "图表月份标签行", "chart", "chart_month_labels", None, "box"),
    ("A18", "活动卡片边界", "bottom-right", "activity_card_box", None, "box"),
    ("A19", "活动条目圆点列", "bottom-right", "activity_dots", None, "box"),
    ("A20", "表格卡片边界", "bottom-left", "table_card_box", None, "box"),
    ("A21", "表头色带", "table", "table_header_band", None, "box"),
    ("A22", "表格状态胶囊区", "table", "table_status_pills", None, "box"),
    ("A23", "侧栏选中态胶囊", "nav", "nav_selected", None, "box"),
    ("A24", "侧栏 logo 方块", "nav", "logo_mark", None, "box"),
    ("A25", "工作区信息面板", "nav", "workspace_panel", None, "box"),
    ("A26", "页脚文字块", "canvas", "footer_ink", None, "box"),
]


def get(d: dict, key: str, idx):
    if key == "activity_card_box":
        v = d.get("activity_card_y")
        if not v:
            return None
        rows = [r[0] for r in v] + [r[1] for r in v]
        return [d["row2_cards_x"][-1][0], min(rows), d["row2_cards_x"][-1][1], max(rows)]
    v = d.get(key)
    if v is None:
        return None
    if idx is None:
        # normalise "list of runs" into a single [min, max] span
        if isinstance(v, list) and v and isinstance(v[0], list):
            return [min(r[0] for r in v), max(r[1] for r in v)]
        if isinstance(v, int):
            return [v, v]
        return v
    return v[idx] if isinstance(v, list) and len(v) > abs(idx) else None


def delta(ref, new, axis):
    if ref is None or new is None:
        return None
    if axis in ("x", "y"):
        r = ref[0] if isinstance(ref, list) else ref
        n = new[0] if isinstance(new, list) else new
        return n - r
    if axis == "top":
        return new[2] - ref[2] if len(ref) > 2 and len(new) > 2 else None
    if len(ref) != len(new):
        return None
    return max(abs(a - b) for a, b in zip(ref, new))


def main() -> None:
    new_png = sys.argv[1] if len(sys.argv) > 1 else os.path.join(TMP, "png", "reconstructed.v1.png")
    ref = measure(REF)
    new = measure(new_png)
    json.dump(ref, open(os.path.join(TMP, "measure-reference.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    json.dump(new, open(os.path.join(TMP, "measure-reconstructed.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)

    rows, worst, fails = [], 0, []
    for aid, label, quad, key, idx, axis in ANCHORS:
        r = get(ref, key, idx)
        n = get(new, key, idx)
        d = delta(r, n, axis)
        ok = d is not None and d <= TOL
        if d is None:
            ok = False
        else:
            worst = max(worst, abs(d))
        if not ok:
            fails.append(aid)
        rows.append(dict(anchor=aid, label=label, quadrant=quad, metric=key,
                         index=idx, axis=axis, reference=r, reconstructed=n,
                         delta=d, tolerance=TOL, within_tolerance=ok))
    print(f"{'id':4s} {'metric':22s} {'ref':>26s} {'new':>26s} {'d':>6s} ok")
    for r in rows:
        print(f"{r['anchor']:4s} {r['metric']:22s} {str(r['reference']):>26s} "
              f"{str(r['reconstructed']):>26s} {str(r['delta']):>6s} "
              f"{'OK' if r['within_tolerance'] else 'XX'}")
    print(f"\nanchors={len(rows)} within_tolerance={sum(1 for r in rows if r['within_tolerance'])}"
          f" worst_abs_delta={worst} fails={fails}")
    json.dump(dict(anchors=rows, tol=TOL, worst=worst, fails=fails),
              open(os.path.join(TMP, "anchor-compare.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
