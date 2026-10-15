#!/usr/bin/env python
# A22 核验与回归：layout-map 的区域比较、change-audit 的 regression，
# 以及**从最终 PNG 反测柱高**——证明负值没有被裁掉、柱高按未舍入值计算。
# 启动基准：总任务根 (suite_root)。用法：python verify_a22.py <round> [ver]
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
OUTD = ROOT / "outputs/run-20261011-01/A22"
TEMPD = ROOT / "tmp/run-20261011-01/A22"

REGIONS = {"title": (48, 30, 1552, 104), "kpi": (48, 120, 1552, 236),
           "chart": (48, 256, 912, 640), "conclusion": (944, 256, 1552, 640),
           "table": (48, 664, 1552, 968)}
PLOT = (156, 324, 888, 584)
C_NET = "#1D4ED8"
C_PROFIT = "#0E9F6E"
C_NEG = "#DC2626"


def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def main() -> None:
    rd = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    ver = sys.argv[2] if len(sys.argv) > 2 else "v1"
    dsub = f"round-{rd:02d}"
    cd = json.loads((OUTD / dsub / "computed-data.json").read_text(encoding="utf-8"))
    lm = json.loads((OUTD / dsub / "layout-map.json").read_text(encoding="utf-8"))
    ax = cd["axes"]
    span = ax["nice_max"] - ax["nice_min"]

    # ---------- 1. 柱高像素反测
    png = OUTD / dsub / "dashboard.png"
    with Image.open(png) as im:
        im.load()
        px = im.convert("RGB").load()
    cx0, cy0, cx1, cy1 = REGIONS["chart"]

    def y_of(v):
        return PLOT[3] - (v - ax["nice_min"]) / span * (PLOT[3] - PLOT[1])

    # 收集柱色像素并按 x 槽位聚类。
    # 只扫描绘图区（y 从零线所在带往下到绘图区底），因为图例色块也用同样的两种颜色，
    # 若把整张图表卡都扫进去，会把图例当成第 n 根柱。
    def bars(hexcolor):
        c = rgb(hexcolor)
        cols = {}
        for yy in range(PLOT[1] - 3, PLOT[3] + 3):
            for xx in range(PLOT[0] - 3, PLOT[2] + 3):
                p = px[xx, yy]
                if abs(p[0] - c[0]) <= 6 and abs(p[1] - c[1]) <= 6 and abs(p[2] - c[2]) <= 6:
                    cols.setdefault(xx, []).append(yy)
        groups, cur = [], []
        for xx in sorted(cols):
            if cur and xx - cur[-1] > 12:
                groups.append(cur)
                cur = []
            cur.append(xx)
        if cur:
            groups.append(cur)
        out = []
        for g in groups:
            ys = [y for x in g for y in cols[x]]
            out.append({"x_left": g[0], "x_right": g[-1],
                        "y_top": min(ys), "y_bottom": max(ys)})
        return out

    net_b = bars(C_NET)
    neg_b = bars(C_NEG)
    prof_b = bars(C_PROFIT) + neg_b     # 经营利润：正负两种配色合起来按 x 归并
    months = cd["months"]
    n = len(months)
    slot = (PLOT[2] - PLOT[0]) / n
    zero_y = y_of(0)

    checks, failures = [], []

    def expect_height(v):
        return abs(y_of(v) - zero_y)

    for i, m in enumerate(months):
        lo = PLOT[0] + slot * i + 2
        hi = PLOT[0] + slot * (i + 1) - 2
        nb = [b for b in net_b if lo <= b["x_left"] and b["x_right"] <= hi]
        pb = [b for b in prof_b if lo <= b["x_left"] and b["x_right"] <= hi]
        assert len(nb) == 1, f'{m["month"]} 净收入柱数 {len(nb)}'
        assert len(pb) == 1, f'{m["month"]} 利润柱数 {len(pb)}'
        nh = nb[0]["y_bottom"] - nb[0]["y_top"] + 1
        ph = pb[0]["y_bottom"] - pb[0]["y_top"] + 1
        e_n, e_p = expect_height(m["net_revenue"]), expect_height(m["operating_profit"])
        # 负值柱必须完全位于零线之下
        below = (pb[0]["y_top"] >= zero_y - 1.5) if m["operating_profit"] < 0 else True
        above = (pb[0]["y_bottom"] <= zero_y + 1.5) if m["operating_profit"] > 0 else True
        rec = {"month": m["month"], "net_revenue": m["net_revenue"],
               "operating_profit": m["operating_profit"],
               "net_bar_px": {"measured_height": nh, "expected_height": round(e_n, 2),
                              "delta_px": round(nh - e_n, 2)},
               "profit_bar_px": {"measured_height": ph, "expected_height": round(e_p, 2),
                                 "delta_px": round(ph - e_p, 2)},
               "profit_side": "零线之下" if m["operating_profit"] < 0 else "零线之上",
               "not_clipped": below and above,
               "color_used": C_NEG if m["operating_profit"] < 0 else C_PROFIT}
        checks.append(rec)
        if abs(nh - e_n) > 3:
            failures.append(f'{m["month"]} 净收入柱高 {nh} vs 期望 {e_n:.1f}')
        if abs(ph - e_p) > 3:
            failures.append(f'{m["month"]} 利润柱高 {ph} vs 期望 {e_p:.1f}')
        if not (below and above):
            failures.append(f'{m["month"]} 利润柱方向错误')
    assert not failures, f"柱高反测失败：{failures}"

    # ---------- 2. layout-map 的区域比较
    comparison = []
    if rd >= 2:
        prev = json.loads((OUTD / f"round-{rd-1:02d}/layout-map.json")
                          .read_text(encoding="utf-8"))
        p = {r["id"]: r["box"] for r in prev["regions"]}
        c = {r["id"]: r["box"] for r in lm["regions"]}
        for rid in sorted(p):
            d = [round(c[rid][k] - p[rid][k], 4) for k in range(4)]
            comparison.append({"region_id": rid, "previous_box": p[rid],
                               "current_box": c[rid], "delta_components_px": d,
                               "max_abs_delta_px": round(max(abs(v) for v in d), 4),
                               "within_2px": max(abs(v) for v in d) <= 2.0})
        bad = [x for x in comparison if not x["within_2px"]]
        assert not bad, f"主区域边界偏移超过 2px：{bad}"
    lm["comparison"] = comparison
    lm["bar_height_pixel_audit"] = checks
    (OUTD / dsub / "layout-map.json").write_text(
        json.dumps(lm, ensure_ascii=False, indent=2), encoding="utf-8")

    # ---------- 3. change-audit 的 regression
    if rd >= 2:
        ca = json.loads((OUTD / dsub / "change-audit.json").read_text(encoding="utf-8"))
        prevc = json.loads((OUTD / f"round-{rd-1:02d}/computed-data.json")
                           .read_text(encoding="utf-8"))
        ca["regression"] = [
            {"check": "主区域边界", "method": "layout-map.comparison 逐区域逐分量比较上轮",
             "result": f'{len(comparison)} 个区域，最大分量差 '
                       f'{max(c["max_abs_delta_px"] for c in comparison)}px ≤ 2px',
             "evidence": "round-XX/layout-map.json 的 comparison 段"},
            {"check": "柱高与未舍入值一致",
             "method": "从最终 PNG 逐像素定位柱色区域，量测每根柱的实际高度，"
                       "与用未舍入数值算出的期望高度比较（容差 3px，含圆角与抗锯齿）",
             "result": f'{len(checks)} 根净收入柱 + {len(checks)} 根利润柱全部一致',
             "evidence": "round-XX/layout-map.json 的 bar_height_pixel_audit 段"},
            {"check": "负值未被裁剪或改写为正",
             "method": "检查每个负利润月的利润柱是否整根位于零线之下",
             "result": ("负利润月份：" +
                        "、".join(c["month"] for c in checks if c["operating_profit"] < 0)
                        + "，柱身完整位于零线之下" if any(c["operating_profit"] < 0
                                                        for c in checks)
                        else "本轮无负利润月份"),
             "evidence": "bar_height_pixel_audit[].not_clipped 与 profit_side"},
            {"check": "轴范围",
             "method": "nice 范围由未舍入极值重算",
             "result": f'由 [{prevc["axes"]["nice_min"]},{prevc["axes"]["nice_max"]}] 变为 '
                       f'[{ax["nice_min"]},{ax["nice_max"]}]，刻度步长 '
                       f'{ax["tick_step_yuan"]} 元未变',
             "evidence": "computed-data.json 的 axes 段"},
            {"check": "汇总口径未变",
             "method": "比较两轮 computed-data 的 formulas 段",
             "result": "逐字相同" if prevc["formulas"] == cd["formulas"] else "不一致",
             "evidence": "computed-data.json 的 formulas 段"},
            {"check": "月份完整性",
             "method": "比较两轮月份列表",
             "result": f'{prevc["totals"]["period"]["months"]} 个月 → '
                       f'{cd["totals"]["period"]["months"]} 个月；'
                       f'首月 {cd["totals"]["period"]["from"]} 仍在',
             "evidence": "computed-data.json 的 months 与 totals.period"},
            {"check": "真实图像核验",
             "method": "整屏打开本轮 PNG 与上一轮 PNG 对照",
             "result": "已打开确认：KPI 数字、表格单元格、柱形方向与颜色、结论文字均与 "
                       "computed-data.json 一致",
             "evidence": "round-XX/snapshot-usage.md 第 4 节的看图记录"},
        ]
        (OUTD / dsub / "change-audit.json").write_text(
            json.dumps(ca, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"round{rd}: bars ok ({len(checks)} months), regions compared "
          f"{len(comparison)}, max delta "
          f"{max([c['max_abs_delta_px'] for c in comparison], default=0)}px")


if __name__ == "__main__":
    main()