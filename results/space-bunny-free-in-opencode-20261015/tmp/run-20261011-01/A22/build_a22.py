#!/usr/bin/env python
# A22 经营驾驶舱：1600x1000，三轮共用生成器。
# 启动基准：总任务根 (suite_root)。用法：python build_a22.py <round> [version]
#
# 【计算口径】全部来自 TASK.md「三轮共同计算与显示显示口径」，不在本文件里另立规则：
#   净收入 = gross_revenue - refund_amount
#   经营利润 = 净收入 - operating_cost
#   退款率 = refund_amount / gross_revenue
#   月转化率 = orders / sessions
#   期间：先分别求和；总体转化率 = 总orders/总sessions（不平均各月百分比）
#   总体退款率 = 总refund/总gross（不平均）
# 计算、汇总、差额与柱高比例全部使用**未按展示精度舍入**的值，只有最后格式化时才舍入。
#
# 【更正不改原 CSV】第 2/3 轮的更正以 applied_changes 记录在 computed-data.json，
# 原 CSV 始终只读、不被覆写。
from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path

BASE = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
TASK = BASE / "tasks/A22-staged-data-correction"
CSV_PATH = TASK / "inputs/monthly.csv"
DRAFTS = BASE / "tmp/run-20261011-01/A22/drafts"

W, H = 1600, 1000

# 主区域边界：三轮保持不变（round-02/03 要求 ±2px）
REGIONS = {
    "title": (48, 30, 1552, 104),
    "kpi": (48, 120, 1552, 236),
    "chart": (48, 256, 912, 640),
    "conclusion": (944, 256, 1552, 640),
    "table": (48, 664, 1552, 968),
}

TICK_STEP = 40000            # 轴刻度步长（元）= 4 万元

# 轮次数据修订（只在这里记录，绝不回写 CSV）
CHANGES = {
    2: [("2026-08", "refund_amount", 15048, 25048,
         "round-02.md 财务更正：2026-08 退款额应为 25048"),
        ("2026-09", "operating_cost", 138000, 208000,
         "round-02.md 财务更正：2026-09 经营成本应为 208000")],
    3: [("2026-10", "NEW", None,
         {"orders": 640, "gross_revenue": 224000, "refund_amount": 11200,
          "operating_cost": 142000, "sessions": 5900},
         "round-03.md 新增月份：2026-10")],
}

# ---------------------------------------------------------------- 展示格式
def fmt_int(v: int) -> str:
    return f"{v:,}"


def fmt_wan(v: int) -> str:
    """元 -> 万元，保留两位小数；恰好半单位时绝对值增大（四舍五入远离零）。"""
    x = v / 10000.0
    return f"{x + 0.0000001:.2f}" if x >= 0 else f"{x - 0.0000001:.2f}"


def fmt_pct(v: float) -> str:
    """比率 -> 百分比两位小数；未舍入值只在这里被舍入。"""
    x = v * 100.0
    return f"{x + 0.0000001:.2f}%" if x >= 0 else f"{x - 0.0000001:.2f}%"


def em_width(s: str, size: float) -> float:
    w = 0.0
    for ch in s:
        if ord(ch) > 0x2E80:
            w += 1.0
        elif ch == " ":
            w += 0.28
        elif ch.isdigit():
            w += 0.53
        elif ch in ",.·":
            w += 0.40
        elif ch in "-−":
            w += 0.56
        elif ch == "%":
            w += 0.90
        elif ch.isupper():
            w += 0.70
        elif ch.islower():
            w += 0.60
        else:
            w += 0.45
    return w * size


# ---------------------------------------------------------------- 计算
def load(rd: int):
    rows = []
    with CSV_PATH.open(encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            rows.append({k: int(v) if k != "month" else v for k, v in r.items()})
    base = {r["month"]: dict(r) for r in rows}
    applied = []
    # 第 rd 轮要**累计应用**第 2..rd 轮的全部更正：
    # round-03.md 明确「两项第二轮更正继续有效」，所以不能只看本轮自己的修订。
    for src_rd in range(2, rd + 1):
        for ch in CHANGES.get(src_rd, []):
            month, field, old, new, why = ch
            if field == "NEW":
                applied.append({"round": src_rd, "month": month, "field": field,
                                "old_value": None, "new_value": new,
                                "source": why, "action": "新增整行"})
                if not any(r["month"] == month for r in rows):
                    rows.append({"month": month, **new})
            else:
                applied.append({"round": src_rd, "month": month, "field": field,
                                "old_value": old, "new_value": new,
                                "source": why, "action": "更正原值"})
                for r in rows:
                    if r["month"] == month:
                        r[field] = new
    return rows, base, applied


def compute(rows, rd):
    months = []
    for r in rows:
        net = r["gross_revenue"] - r["refund_amount"]
        profit = net - r["operating_cost"]
        rr = r["refund_amount"] / r["gross_revenue"]
        cv = r["orders"] / r["sessions"]
        months.append({
            "month": r["month"],
            "raw": {"orders": r["orders"], "gross_revenue": r["gross_revenue"],
                    "refund_amount": r["refund_amount"],
                    "operating_cost": r["operating_cost"], "sessions": r["sessions"]},
            "net_revenue": net,
            "operating_profit": profit,
            "refund_rate": {"numerator": r["refund_amount"],
                            "denominator": r["gross_revenue"],
                            "unrounded": rr, "display": fmt_pct(rr)},
            "conversion_rate": {"numerator": r["orders"], "denominator": r["sessions"],
                                 "unrounded": cv, "display": fmt_pct(cv)},
            "display": {"net_revenue": fmt_int(net),
                        "operating_profit": fmt_int(profit)},
        })
    t = {
        "period": {"from": months[0]["month"], "to": months[-1]["month"],
                   "months": len(months)},
        "gross_revenue": sum(m["raw"]["gross_revenue"] for m in months),
        "refund_amount": sum(m["raw"]["refund_amount"] for m in months),
        "operating_cost": sum(m["raw"]["operating_cost"] for m in months),
        "orders": sum(m["raw"]["orders"] for m in months),
        "sessions": sum(m["raw"]["sessions"] for m in months),
    }
    t["net_revenue"] = t["gross_revenue"] - t["refund_amount"]
    t["operating_profit"] = t["net_revenue"] - t["operating_cost"]
    t["overall_conversion_rate"] = {
        "numerator": t["orders"], "denominator": t["sessions"],
        "unrounded": t["orders"] / t["sessions"],
        "display": fmt_pct(t["orders"] / t["sessions"]),
        "note": "总 orders / 总 sessions，不是各月百分比的平均",
    }
    t["overall_refund_rate"] = {
        "numerator": t["refund_amount"], "denominator": t["gross_revenue"],
        "unrounded": t["refund_amount"] / t["gross_revenue"],
        "display": fmt_pct(t["refund_amount"] / t["gross_revenue"]),
        "note": "总 refund / 总 gross，不是各月百分比的平均",
    }

    # 轴：用未舍入值定 nice 范围
    hi = max(m["net_revenue"] for m in months)
    lo = min(0, min(m["operating_profit"] for m in months))
    nice_hi = -(-hi // TICK_STEP) * TICK_STEP
    nice_lo = (lo // TICK_STEP) * TICK_STEP
    ticks, v = [], int(nice_lo)
    while v <= nice_hi + 1:
        ticks.append(v)
        v += TICK_STEP
    axes = {
        "shared_scale": True,
        "series": ["net_revenue", "operating_profit"],
        "unit": "元",
        "axis_display_unit": "万元",
        "tick_step_yuan": TICK_STEP,
        "nice_min": nice_lo, "nice_max": nice_hi,
        "ticks": ticks,
        "zero_line_yuan": 0,
        "has_negative": nice_lo < 0,
        "note": "净收入与经营利润共用同一比例尺与同一条零线；"
                "存在负利润时负轴在同一图表区域内展开，不裁剪、不改写为正值。",
    }
    return months, t, axes


def conclusion(months, t, rd):
    """主结论只从实际数值推出，不写任何不能由数据支持的判断。"""
    best_net = max(months, key=lambda m: m["net_revenue"])
    worst_profit = min(months, key=lambda m: m["operating_profit"])
    best_profit = max(months, key=lambda m: m["operating_profit"])
    worst_rr = max(months, key=lambda m: m["refund_rate"]["unrounded"])
    best_rr = min(months, key=lambda m: m["refund_rate"]["unrounded"])
    losses = [m for m in months if m["operating_profit"] < 0]

    lines = [
        f'{best_net["month"]} 净收入最高 {fmt_int(best_net["net_revenue"])} 元；'
        f'经营利润最高 {fmt_int(best_profit["operating_profit"])} 元'
        f'（{best_profit["month"]}）。',
        f'期间净收入合计 {fmt_int(t["net_revenue"])} 元，'
        f'经营利润合计 {fmt_int(t["operating_profit"])} 元。',
    ]
    if losses:
        lines.append(
            '经营利润为负：' + "、".join(
                f'{m["month"]}（{fmt_int(m["operating_profit"])} 元）' for m in losses)
            + f'；该月净收入仍有 {fmt_int(losses[0]["net_revenue"])} 元，'
              f'亏损来自经营成本高于净收入。')
    else:
        lines.append(f'各月经营利润均为正；最低为 {worst_profit["month"]} 的 '
                     f'{fmt_int(worst_profit["operating_profit"])} 元。')
    lines.append(
        f'退款率 {best_rr["refund_rate"]["display"]}–'
        f'{worst_rr["refund_rate"]["display"]}，总体 '
        f'{t["overall_refund_rate"]["display"]}；总体转化率 '
        f'{t["overall_conversion_rate"]["display"]}'
        f'（{t["overall_conversion_rate"]["numerator"]} orders / '
        f'{t["overall_conversion_rate"]["denominator"]} sessions）。')
    return {"title": f'主结论（截至 {t["period"]["to"]}）',
            "lines": lines,
            "cited_numbers": {
                "max_net_revenue_month": best_net["month"],
                "max_net_revenue": best_net["net_revenue"],
                "max_profit_month": best_profit["month"],
                "max_profit": best_profit["operating_profit"],
                "loss_months": [m["month"] for m in losses],
                "worst_refund_rate_month": worst_rr["month"],
                "overall_refund_rate": t["overall_refund_rate"]["unrounded"],
                "overall_conversion_rate": t["overall_conversion_rate"]["unrounded"],
            },
            "basis": "每一条都直接引用上表与 KPI 的数值；没有任何超出数据的推断。"}


# ---------------------------------------------------------------- 图元
def rect(x, y, w, h, color, radius=0, border=None, bw=1.5):
    b = f' border="{bw} SOLID {border}"' if border else ""
    return (f'<Positioned left="{x:.2f}" top="{y:.2f}" width="{w:.2f}" height="{h:.2f}">'
            f'<Container width="{w:.2f}" height="{h:.2f}" color="{color}" '
            f'borderRadius="{radius}"{b}/></Positioned>')


def txt(t, x, y, w, h, size, color, family="Inter,Noto Sans CJK SC",
        align=None, weight="Inter Medium"):
    # 本服务实测：`textAlign` 的枚举里连 left / right / center 都不存在，
    # 任何取值都返回 400。因此本文件**完全不输出 textAlign**，
    # 所有对齐都靠 txt_right / txt_center 按实测字宽算出坐标来实现。
    q = "'" if '"' in t else '"'
    at = f' fontSize="{size}" color="{color}" fontFamily="{weight},{family}"'
    return (f'<Positioned left="{x:.2f}" top="{y:.2f}" width="{w:.2f}" height="{h:.2f}">'
            f'<Text{at} text={q}{t}{q}/></Positioned>')


def txt_right(t, right, y, h, size, color, weight="Inter Medium", pad=2):
    """右对齐：按实测字宽系数算出文本宽度，从右边界往左摆。

    余量给到 +40px：服务端会**静默裁掉**超出盒子的文字且仍返回 200，
    字宽系数只是估计，盒子太紧就会在实图上少掉最后一个字符。
    """
    est = em_width(t, size)
    return txt(t, right - est - pad, y, est + pad + 40, h, size, color, weight=weight)


def txt_center(t, cx, y, h, size, color, weight="Inter Medium", pad=6):
    """居中对齐：按实测字宽系数算出宽度，使文本中心落在 cx。盒宽同样留足余量。"""
    est = em_width(t, size)
    return txt(t, cx - (est + 20) / 2, y, est + 20, h, size, color, weight=weight)


# ---------------------------------------------------------------- 配色
C_BG = "#F1F5F9"
C_CARD = "#FFFFFF"
C_EDGE = "#E2E8F0"
C_INK = "#0F172A"
C_MUTED = "#64748B"
C_NET = "#1D4ED8"
C_PROFIT = "#0E9F6E"
C_NEG = "#DC2626"
C_ZERO = "#94A3B8"
C_GRID = "#EEF2F7"
C_ACCENT = "#7C3AED"


def build(rd, ver):
    rows, base, applied = load(rd)
    months, tot, axes = compute(rows, rd)
    concl = conclusion(months, tot, rd)

    x0, y0, x1, y1 = REGIONS["title"]
    b = [rect(0, 0, W, H, C_BG)]

    # ---------------- 标题
    b.append(txt(f'经营驾驶舱 · {tot["period"]["from"]} 至 {tot["period"]["to"]}',
                 x0, y0 + 4, x1 - x0, 44, 34, C_INK, weight="Inter Semi Bold"))
    b.append(txt(f'金额单位：元（KPI 另注万元）· 比率按题面公式由原始数据计算，'
                 f'不修改原始 CSV', x0, y0 + 54, x1 - x0, 30, 22, C_MUTED))
    b.append(rect(x0, y1 - 2, x1 - x0, 2, C_EDGE))

    # ---------------- KPI
    kx0, ky0, kx1, ky1 = REGIONS["kpi"]
    kpis = [
        ("总净收入", f'{fmt_wan(tot["net_revenue"])}', "万元",
         f'{fmt_int(tot["net_revenue"])} 元', C_NET),
        ("总经营利润", f'{fmt_wan(tot["operating_profit"])}', "万元",
         f'{fmt_int(tot["operating_profit"])} 元',
         C_NEG if tot["operating_profit"] < 0 else C_PROFIT),
        ("总订单", fmt_int(tot["orders"]), "笔",
         f'{tot["orders"]} orders', C_ACCENT),
        ("总体转化率", tot["overall_conversion_rate"]["display"], "",
         f'{tot["overall_conversion_rate"]["numerator"]} / '
         f'{tot["overall_conversion_rate"]["denominator"]}', C_PROFIT),
    ]
    gap = 16
    cw = ((kx1 - kx0) - gap * 3) / 4
    for i, (name, val, unit, sub, col) in enumerate(kpis):
        cx = kx0 + i * (cw + gap)
        b.append(rect(cx, ky0, cw, ky1 - ky0, C_CARD, 14, C_EDGE))
        b.append(rect(cx, ky0, 6, ky1 - ky0, col, 3))
        b.append(txt(name, cx + 24, ky0 + 18, cw - 40, 28, 22, C_MUTED))
        b.append(txt(val, cx + 24, ky0 + 48, cw - 40, 46, 40, col,
                     weight="Inter Semi Bold"))
        uy = ky0 + 96
        b.append(txt(unit + "　" + sub, cx + 24, uy, cw - 40, 26, 22, C_MUTED))

    # ---------------- 柱图
    gx0, gy0, gx1, gy1 = REGIONS["chart"]
    b.append(rect(gx0, gy0, gx1 - gx0, gy1 - gy0, C_CARD, 14, C_EDGE))
    b.append(txt("净收入与经营利润（元）", gx0 + 24, gy0 + 18, 500, 32, 24, C_INK,
                 weight="Inter Semi Bold"))
    plx0, ply0 = gx0 + 108, gy0 + 68        # 绘图区
    plx1, ply1 = gx1 - 24, gy1 - 56
    span = axes["nice_max"] - axes["nice_min"]

    def y_of(v):
        return ply1 - (v - axes["nice_min"]) / span * (ply1 - ply0)

    for tv in axes["ticks"]:
        yy = y_of(tv)
        b.append(rect(plx0, yy, plx1 - plx0, 1, C_GRID))
        b.append(txt_right(f'{fmt_wan(tv)}万', gx0 + 96, yy - 14, 28, 22, C_MUTED))
    zy = y_of(0)
    b.append(rect(plx0, zy, plx1 - plx0, 2, C_ZERO))
    # 零线本身已由刻度表里的 0 标注，不再重复画一个 "0"（首版两者叠在一起）

    n = len(months)
    slot = (plx1 - plx0) / n
    bw = min(30, slot * 0.30)
    for i, m in enumerate(months):
        cx = plx0 + slot * (i + 0.5)
        for val, col, off in ((m["net_revenue"], C_NET, -bw - 5),
                              (m["operating_profit"],
                               C_NEG if m["operating_profit"] < 0 else C_PROFIT, 5)):
            yv = y_of(val)
            top = min(zy, yv)
            hgt = abs(zy - yv)
            assert hgt >= 0.5, "柱高为零，请检查数值"
            b.append(rect(cx + off, top, bw, hgt, col, 3))
        b.append(txt_center(m["month"][2:], cx, ply1 + 12, 26, 22, C_MUTED))
    # 图例移到标题行右侧：原先放在图的底部，与月份标签（ply1+12）重叠了。
    lg = [("净收入", C_NET), ("经营利润", C_PROFIT)]
    if any(m["operating_profit"] < 0 for m in months):
        lg.append(("经营利润（负值）", C_NEG))
    lx = gx1 - 24
    for name, col in reversed(lg):
        wdt = em_width(name, 22)
        b.append(txt(name, lx - wdt, gy0 + 14, wdt + 20, 26, 22, C_MUTED))
        lx -= wdt + 26
        b.append(rect(lx + 8, gy0 + 20, 16, 16, col, 3))
        lx -= 4

    # ---------------- 结论
    cx0, cy0, cx1, cy1 = REGIONS["conclusion"]
    b.append(rect(cx0, cy0, cx1 - cx0, cy1 - cy0, C_CARD, 14, C_EDGE))
    b.append(txt(concl["title"], cx0 + 24, cy0 + 18, cx1 - cx0 - 48, 32, 24, C_INK,
                 weight="Inter Semi Bold"))
    # 每条结论允许折成两行，盒高给 64px；条距 74px，4 条正好落在区域内。
    # 首版用 58px 盒高 + 62px 条距，实图上第二行的句号被裁掉了。
    assert len(concl["lines"]) <= 4, "结论条数超过 4，请合并或加大区域"
    yy = cy0 + 56
    for line in concl["lines"]:
        b.append(rect(cx0 + 26, yy + 12, 7, 7, C_ACCENT, 4))
        b.append(txt(line, cx0 + 46, yy, cx1 - cx0 - 76, 64, 22, C_INK))
        yy += 74
    concl_bottom = yy - 74 + 64

    # ---------------- 表格
    tx0, ty0, tx1, ty1 = REGIONS["table"]
    b.append(rect(tx0, ty0, tx1 - tx0, ty1 - ty0, C_CARD, 14, C_EDGE))
    cols = [240, 320, 320, 312, 312]
    heads = ["月份", "净收入（元）", "经营利润（元）", "退款率", "转化率"]
    xs, acc = [], tx0 + 20
    for c in cols:
        xs.append(acc)
        acc += c
    b.append(txt("月度明细", tx0 + 24, ty0 + 14, 300, 30, 24, C_INK,
                 weight="Inter Semi Bold"))
    hy = ty0 + 48
    b.append(rect(tx0 + 20, hy + 32, tx1 - tx0 - 40, 2, C_EDGE))
    for i, hd in enumerate(heads):
        b.append(txt_center(hd, xs[i] + (cols[i] - 16) / 2, hy, 30, 22, C_MUTED))
    # 7 个月（第 3 轮）比 6 个月多一行，行高按轮次收到 25px——
    # round-03.md 明确允许「重排内部刻度/行距」，主区域边界不动。
    rh = 26 if rd <= 2 else 25
    for j, m in enumerate(months):
        ry = hy + 40 + j * rh
        if j % 2 == 1:
            b.append(rect(tx0 + 14, ry - 3, tx1 - tx0 - 28, rh, "#F8FAFC", 6))
        neg = m["operating_profit"] < 0
        b.append(txt(m["month"], xs[0], ry, cols[0] - 16, 28, 22, C_INK))
        b.append(txt_right(m["display"]["net_revenue"], xs[1] + cols[1] - 16,
                           ry, 28, 22, C_INK))
        b.append(txt_right(m["display"]["operating_profit"], xs[2] + cols[2] - 16,
                           ry, 28, 22, C_NEG if neg else C_INK))
        b.append(txt_right(m["refund_rate"]["display"], xs[3] + cols[3] - 16,
                           ry, 28, 22, C_INK))
        b.append(txt_right(m["conversion_rate"]["display"], xs[4] + cols[4] - 16,
                           ry, 28, 22, C_INK))
    fy = hy + 36 + len(months) * rh + 4
    b.append(rect(tx0 + 20, fy - 6, tx1 - tx0 - 40, 2, C_EDGE))
    tr = [("期间合计", f'{fmt_int(tot["net_revenue"])}',
           f'{fmt_int(tot["operating_profit"])}',
           tot["overall_refund_rate"]["display"],
           tot["overall_conversion_rate"]["display"])]
    # 合计行盒高给到 32：22px 字体的行高约 28.6px，盒高 28 会把下缘切掉
    # （7 个月那一版实图上「期间合计」的下沿正好压在区域边界上被裁）。
    for i, (a1, a2, a3, a4, a5) in enumerate(tr):
        b.append(txt(a1, xs[0], fy + 2, cols[0] - 16, 32, 22, C_INK,
                     weight="Inter Semi Bold"))
        b.append(txt_right(a2, xs[1] + cols[1] - 16, fy + 2, 32, 22, C_INK,
                           weight="Inter Semi Bold"))
        b.append(txt_right(a3, xs[2] + cols[2] - 16, fy + 2, 32, 22,
                           C_NEG if tot["operating_profit"] < 0 else C_INK,
                           weight="Inter Semi Bold"))
        b.append(txt_right(a4, xs[3] + cols[3] - 16, fy + 2, 32, 22, C_INK,
                           weight="Inter Semi Bold"))
        b.append(txt_right(a5, xs[4] + cols[4] - 16, fy + 2, 32, 22, C_INK,
                           weight="Inter Semi Bold"))

    dsl = (f'<Snapshot type="png">\n<Container width="{W}" height="{H}" color="{C_BG}">'
           f'<Stack fit="EXPAND">{"".join(b)}</Stack></Container>\n</Snapshot>\n')

    # ---- 布局自检
    issues = []
    if fy + 36 > ty1:
        issues.append(f"表格底部 {fy + 34:.0f} 越出表格区域 {ty1}")
    if concl_bottom > cy1:
        issues.append(f"结论区底部 {concl_bottom:.0f} 越出 {cy1}")
    assert not issues, f"版面检查失败：{issues}"

    computed = {
        "schema_version": 1, "task_id": "A22", "round": rd, "path_base": "output_dir",
        "source_csv": {"path_base": "suite_root",
                       "path": "tasks/A22-staged-data-correction/inputs/monthly.csv",
                       "modified": False,
                       "note": "原始 CSV 全程只读；第 2/3 轮的更正记录在 applied_changes，"
                               "不回写输入文件。"},
        "applied_changes": applied,
        "formulas": {
            "net_revenue": "gross_revenue - refund_amount",
            "operating_profit": "net_revenue - operating_cost",
            "refund_rate": "refund_amount / gross_revenue",
            "conversion_rate": "orders / sessions",
            "totals": "期间各字段先分别求和",
            "overall_conversion_rate": "总 orders / 总 sessions（非各月百分比平均）",
            "overall_refund_rate": "总 refund / 总 gross（非各月百分比平均）",
            "rounding": "计算、汇总、差额与柱高比例全部使用未舍入值；"
                        "百分比与万元金额仅在格式化时按题面精度舍入（四舍五入，绝对值增大）。",
        },
        "units": {"currency": "元", "orders": "笔", "sessions": "次",
                  "kpi_currency_display": "万元（两位小数）",
                  "detail_currency_display": "整数元，带千位分隔",
                  "percent_display": "两位小数"},
        "months": months,
        "totals": tot,
        "axes": axes,
        "conclusion": concl,
    }

    layout = {
        "schema_version": 1, "task_id": "A22", "round": rd, "path_base": "output_dir",
        "canvas": [W, H],
        "coordinate_convention": {"origin": "画布左上角 (0,0)", "x": "向右为正",
                                  "y": "向下为正", "unit": "px"},
        "regions": [
            {"id": "title", "box": list(REGIONS["title"]),
             "fonts": [{"text": "标题", "size_px": 34, "weight": "Inter Semi Bold"},
                       {"text": "副标题", "size_px": 22}],
             "colors": [C_INK, C_MUTED], "axis": None},
            {"id": "kpi", "box": list(REGIONS["kpi"]),
             "fonts": [{"text": "KPI 名", "size_px": 22},
                       {"text": "KPI 值", "size_px": 40, "weight": "Inter Semi Bold"},
                       {"text": "KPI 副注", "size_px": 22}],
             "colors": [C_CARD, C_EDGE, C_NET, C_PROFIT, C_NEG, C_ACCENT], "axis": None,
             "card_count": 4, "card_gap_px": 16},
            {"id": "chart", "box": list(REGIONS["chart"]),
             "fonts": [{"text": "图表标题/刻度/月名/图例", "size_px": 22},
                       {"text": "图表标题", "size_px": 24, "weight": "Inter Semi Bold"}],
             "colors": [C_CARD, C_EDGE, C_NET, C_PROFIT, C_NEG, C_ZERO, C_GRID],
             "axis": {"shared_scale": True, "unit": "元", "display_unit": "万元",
                      "tick_step_yuan": TICK_STEP, "nice_min": axes["nice_min"],
                      "nice_max": axes["nice_max"], "zero_line_yuan": 0,
                      "plot_box": [REGIONS["chart"][0] + 108,
                                   REGIONS["chart"][1] + 68,
                                   REGIONS["chart"][2] - 24,
                                   REGIONS["chart"][3] - 56]}},
            {"id": "conclusion", "box": list(REGIONS["conclusion"]),
             "fonts": [{"text": "标题", "size_px": 24, "weight": "Inter Semi Bold"},
                       {"text": "正文", "size_px": 22}],
             "colors": [C_CARD, C_EDGE, C_INK, C_ACCENT], "axis": None},
            {"id": "table", "box": list(REGIONS["table"]),
             "fonts": [{"text": "表名", "size_px": 24, "weight": "Inter Semi Bold"},
                       {"text": "表头/单元格/合计", "size_px": 22}],
             "colors": [C_CARD, C_EDGE, C_INK, C_MUTED, C_NEG, "#F8FAFC"],
             "axis": None, "row_height_px": rh,
             "column_widths_px": cols},
        ],
        "min_body_px": 22,
        "comparison": [],
    }
    return dsl, computed, layout


def main() -> None:
    rd = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    ver = sys.argv[2] if len(sys.argv) > 2 else "v1"
    d = DRAFTS / f"round-{rd:02d}"
    d.mkdir(parents=True, exist_ok=True)
    dsl, computed, layout = build(rd, ver)
    (d / f"a22-dashboard-{ver}.snapshot").write_text(dsl, encoding="utf-8")
    (d / f"computed-data-{ver}-raw.json").write_text(
        json.dumps(computed, ensure_ascii=False, indent=2), encoding="utf-8")
    (d / f"layout-map-{ver}-raw.json").write_text(
        json.dumps(layout, ensure_ascii=False, indent=2), encoding="utf-8")
    t = computed["totals"]
    print(f"round{rd} bytes={len(dsl.encode())} months={t['period']['months']} "
          f"net={t['net_revenue']} profit={t['operating_profit']} "
          f"orders={t['orders']} conv={t['overall_conversion_rate']['display']} "
          f"axis=[{computed['axes']['nice_min']},{computed['axes']['nice_max']}]")


if __name__ == "__main__":
    main()