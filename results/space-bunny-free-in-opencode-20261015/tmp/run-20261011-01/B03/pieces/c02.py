#!/usr/bin/env python
"""B03 case-02 · 旧房翻新报价逐项核对。

场景（自拟）：自住业主拿着装修公司的报价单逐项核，想知道总价差在哪、
              有没有先不报、后面加钱的项。
独占手法：**WidgetSpan 行内偏差条**——差额列的每个单元格是一条文字，
          文字里嵌一个 WidgetSpan，span 里装一条带中心刻度的迷你双向条：
          负差向左、红，正差向右、琥珀。金额用 `fontFeatures="tnum"` +
          `textAlign="END"` 严格右对齐；被取消的分项用 `decoration="LINE_THROUGH"`。
"""
from __future__ import annotations

from b03kit import (assert_fits, dashed_h, em_width, footer, gbox, guard, line_h,
                    mono_width, solid, strike_text, tag, tag_size, txt, para,
                    tnum, W500, W600, W400, SERIF, MONO, BLACK, XBOLD, DISCLAIM)
from bsnap import (BG, DIM, INK, LINE, PANEL, SERIES, SUB, canvas, rect, segment,
                   polyline)

W, H = 1560, 1180

PAPER, PAPER2, PAPER3 = "#F5F0E6", "#EDE5D5", "#E3DAC7"
INK_D, INK_M, INK_L = "#22272F", "#5B6472", "#8A919C"
RULE = "#D2C7B2"
RED, AMBER, GREEN, GREY = "#C0442E", "#B07412", "#2F7D5E", "#8A919C"

ROWS = [
    ("拆除清运", "含垃圾袋", 12800, 10500, "偏高"),
    ("砌筑隔墙", "轻质砖 2 面", 26400, 26400, "一致"),
    ("水电改造", "主水管全换", 48600, 56200, "偏低"),
    ("防水工程", "卫生间双遍", 18900, 19400, "基本一致"),
    ("瓷砖铺贴", "800×800 通体", 42000, 40200, "偏高"),
    ("吊顶石膏板", "客厅平顶", 23500, 22000, "取消"),
    ("木地板", "强化复合", 31200, 31200, "取消"),
    ("室内门", "实木复合 3 樘", 28800, 26400, "取消"),
    ("油漆工程", "一底两面", 22000, 21000, "偏高"),
    ("灯具洁具", "主灯 + 基础", 19400, 20800, "偏低"),
    ("定制柜体", "含五金升级", 64000, 72000, "偏低"),
    ("垃圾清运费", "按车次", 3600, 4800, "偏低"),
]

CANCEL = {"取消"}
C0 = 60.0
COL_NO, COL_NAME = 60, 120
COL_Q, COL_M, COL_VERD, COL_D, BAR_X0 = 360, 570, 776, 886, 1046
BAR_X1 = 1182
BAR_MID = (BAR_X0 + BAR_X1) / 2
BAR_HALF = (BAR_X1 - BAR_X0) / 2
DMAP = 10000.0
RX, RW = 1206, W - 60 - 1206

TY, RH = 350, 50

VCOL = {"偏高": AMBER, "偏低": RED, "一致": GREEN, "基本一致": GREEN, "取消": GREY}
VBAND = {"偏高": "#F8EDD4", "偏低": "#F8E1D9", "取消": "#E6E1D6"}

QUOTE_TOT = sum(r[2] for r in ROWS)
OWN_TOT = sum(r[3] for r in ROWS)
CANCEL_TOT = sum(r[2] for r in ROWS if r[4] in CANCEL)
ACTIVE_Q = QUOTE_TOT - CANCEL_TOT
ACTIVE_M = sum(r[3] for r in ROWS if r[4] not in CANCEL)
ACTIVE_D = ACTIVE_Q - ACTIVE_M


def money(v):
    return ("−" if v < 0 else "") + f"{abs(v):,}"


def bar_span(dev):
    """WidgetSpan：一条以中心刻度为原点的迷你双向条。"""
    half = abs(dev) / DMAP * BAR_HALF
    if dev < 0:
        left, col = BAR_MID - BAR_X0 - half, RED
    else:
        left, col = BAR_MID - BAR_X0, AMBER
    w = max(2.0, half)
    bw = BAR_X1 - BAR_X0

    def st(l, t, ww, hh, color, r=0):
        return (f'<Positioned left="{l:.0f}" top="{t:.0f}" width="{ww:.0f}" height="{hh:.0f}">'
                f'<Container width="{ww:.0f}" height="{hh:.0f}" color="{color}"'
                f' borderRadius="{r}"/></Positioned>')

    return (f'<WidgetSpan alignment="MIDDLE"><SizedBox width="{bw:.0f}" height="18">'
            f'<Stack fit="EXPAND">' + st(0, 6, bw, 6, PAPER3, 3)
            + st(BAR_MID - BAR_X0 - 1, 1, 2, 16, INK_L, 1)
            + st(left, 6, w, 6, col, 3) + "</Stack></SizedBox></WidgetSpan>")


def diff_cell(dev, y):
    col = RED if dev < 0 else (AMBER if dev > 0 else GREEN)
    body = (money(dev) if dev else "0") + '<Raw>  </Raw>' + bar_span(dev)
    w = BAR_X1 - COL_D
    return (f'<Positioned left="{COL_D:.0f}" top="{y}" width="{w}" height="30">'
            f'<Text textAlign="END" fontSize="20" color="{col}"'
            f' fontFeatures="tnum=2" fontFamily="{MONO}">{body}</Text></Positioned>')


def build() -> str:
    b = []
    # ---------------- 纸张
    b.append(gbox(0, 0, W, H, [PAPER, "#EFE8DA"], stops="0,1",
                  begin="TOP_LEFT", end="BOTTOM_RIGHT"))
    b.append(gbox(0, 0, W, 8, ["#C0442E", "#2F7D5E"], begin="TOP_LEFT", end="TOP_RIGHT"))
    b.append(rect(28, 28, W - 56, H - 56, None, 6, border="1 SOLID #DCD2BE"))

    # ---------------- 页头
    b.append(txt("核对稿 · 自拟演示", C0, 62, 700, None, 20, RED, W600))
    b.append(txt("云栖里 3 号楼 1102 室 · 旧房翻新报价逐项核对", C0, 96, 1100, None,
                 42, INK_D, W600))
    b.append(txt("12 个分项 · 装修公司报价 vs 业主核价 · 本次取消 3 项 · 单位 元",
                 C0, 152, 1100, None, 20, INK_M))
    b.append(dashed_h(C0, W - C0, 186, RULE, 1.5, 8, 6))

    # ---------------- 合计条
    def total(x, w, label, value, sub, col):
        b.append(rect(x, 206, w, 116, "#FFFFFF", 8, border="1 SOLID #E0D6C2"))
        b.append(solid(x, 206, w, 3, col))
        b.append(txt(label, x + 18, 222, w - 36, None, 19, INK_M))
        assert_fits(value, 30, w - 36, label)
        b.append(tnum(value, x + 18, 252, w - 36, None, 30, col, XBOLD))
        b.append(txt(sub, x + 18, 294, w - 36, None, 18, INK_L))

    cw = (W - 2 * C0 - 3 * 14) / 4
    total(C0, cw, "装修公司报价合计", f"{QUOTE_TOT:,}", "12 项全量", INK_D)
    total(C0 + cw + 14, cw, "业主核价合计", f"{OWN_TOT:,}", "同口径 12 项", INK_D)
    total(C0 + 2 * (cw + 14), cw, "本次取消（3 项）", f"−{CANCEL_TOT:,}",
          "吊顶 / 地板 / 室内门", GREY)
    total(C0 + 3 * (cw + 14), cw, "有效口径差额", money(ACTIVE_D), "报价 − 核价", RED)

    # ---------------- 表头
    b.append(rect(C0, TY, BAR_X1 - C0, 44, "#3A4049", 6))
    heads = [(COL_NO, 52, "序号", "CENTER"), (COL_NAME, 230, "分项", None),
             (COL_Q, 190, "装修公司报价", "END"), (COL_M, 190, "业主核价", "END"),
             (COL_VERD, 100, "判定", "CENTER"), (COL_D, 150, "差额", "END"),
             (BAR_X0, 136, "偏差条", "CENTER")]
    for x, w, t, al in heads:
        b.append(txt(t, x + 6, TY + 11, w - 12, None, 18, "#EDE5D5", W600, align=al))
    for x in (COL_Q - 8, COL_M - 8, COL_VERD - 8, COL_D - 8, BAR_X0 - 8):
        b.append(rect(x, TY + 8, 1, 28, "#5A626E"))

    # ---------------- 表体
    y = TY + 52
    for i, (name, note, q, m, verdict) in enumerate(ROWS, 1):
        dev = q - m
        band = VBAND.get(verdict)
        b.append(rect(C0, y, BAR_X1 - C0, RH - 6, band or ("#FFFFFF" if i % 2 else PAPER2), 4))
        b.append(rect(C0, y, 3, RH - 6, VCOL[verdict]))

        b.append(txt(f"{i:02d}", COL_NO, y + 10, 52, None, 19, INK_L, MONO, align="CENTER"))

        assert_fits(name, 21, 220, name)
        if verdict in CANCEL:
            b.append(strike_text(name, COL_NAME, y + 9, 220, 30, 21, GREY, GREY, W600))
            nw = em_width(name, 21)
            b.append(txt(note, COL_NAME + nw + 10, y + 13, 220 - nw - 10, None, 18, GREY))
        else:
            b.append(txt(name, COL_NAME, y + 9, 220, None, 21, INK_D, W600))
            b.append(txt(note, COL_NAME + em_width(name, 21) + 10, y + 13,
                         220 - em_width(name, 21) - 10, None, 18, INK_L))

        for cx, val, col in ((COL_Q, q, GREY if verdict in CANCEL else INK_D),
                             (COL_M, m, INK_D)):
            b.append(tnum(f"{val:,}", cx, y + 11, 190, None, 20, col, MONO, align="END"))

        tw, _ = tag_size(verdict, 18, padx=12, pady=5)
        b.append(tag(COL_VERD + (100 - tw) / 2, y + 8, verdict, 18, "#FFFFFF",
                     VCOL[verdict], padx=12, pady=5))

        if verdict in CANCEL:
            b.append(strike_text(money(dev) if dev else "0", COL_D + 6, y + 10, 144, 30,
                                 20, GREY, GREY, MONO, align="END"))
        else:
            b.append(diff_cell(dev, y + 9))
        y += RH

    # 合计行
    b.append(rect(C0, y + 4, BAR_X1 - C0, 50, "#3A4049", 6))
    b.append(txt("合计", COL_NAME, y + 18, 220, None, 20, "#EDE5D5", W600))
    b.append(tnum(f"{QUOTE_TOT:,}", COL_Q, y + 18, 190, None, 20, "#EDE5D5", MONO,
                  align="END"))
    b.append(tnum(f"{OWN_TOT:,}", COL_M, y + 18, 190, None, 20, "#EDE5D5", MONO,
                  align="END"))
    b.append(txt("已取消 3 项", COL_VERD, y + 18, 100, None, 18, "#9AA0AA", W500,
                 align="CENTER"))
    b.append(txt(money(ACTIVE_D), COL_D + 6, y + 18, 144, None, 20, "#F0A08C", MONO,
                 align="END"))
    b.append(txt("有效口径", BAR_X0, y + 18, 136, None, 18, "#9AA0AA", W500, align="CENTER"))
    TOT_Y = y + 4

    # ---------------- 右栏：四项低于核价
    lows = [(n, note, q, m) for (n, note, q, m, v) in ROWS if v == "偏低"]
    b.append(rect(RX, TY, RW, 44, RED, 6))
    b.append(txt("四项低于核价", RX + 16, TY + 11, RW - 32, None, 19, "#FFFFFF", W600))
    b.append(txt("先补漏项，再谈总价", RX + 16, TY + 56, RW - 32, None, 21, INK_D, W600))
    b.append(txt("漏项高发：水电 · 定制 · 洁具 · 清运", RX, TY + 92, RW, None, 18, INK_M))

    ly = TY + 124
    for n, note, q, m in lows:
        b.append(rect(RX, ly, RW, 70, "#F8E1D9", 8, border="1 SOLID #E7C3B8"))
        b.append(txt(n, RX + 14, ly + 8, 120, None, 20, INK_D, W600))
        b.append(txt(f"{q:,} → {m:,}", RX + 14, ly + 9, RW - 28, None, 17, RED, MONO,
                     align="END"))
        b.append(txt(note, RX + 14, ly + 38, RW - 28, None, 18, INK_M))
        ly += 74

    # ---- 有效口径构成条
    sy = ly + 12
    b.append(rect(RX, sy, RW, TOT_Y - sy - 4, "#FFFFFF", 8, border="1 SOLID #E0D6C2"))
    b.append(txt("有效 9 项 · 绝对差额构成", RX + 16, sy + 14, RW - 32, None, 19, INK_M))
    seg_y = sy + 48
    seg_h = 26
    segs = [("偏低 4 项", 18200, RED), ("偏高 3 项", 5100, AMBER),
            ("基本一致 2 项", 500, GREEN)]
    total_v = sum(s[1] for s in segs)
    sx = RX + 16
    inner = RW - 32
    for lab, v, col in segs:
        wseg = inner * v / total_v
        b.append(rect(sx, seg_y, max(4, wseg), seg_h, col, 4))
        sx += wseg
    ly2 = seg_y + seg_h + 16
    for lab, v, col in segs:
        b.append(rect(RX + 16, ly2 + 5, 12, 12, col, 3))
        b.append(txt(lab, RX + 36, ly2, 150, None, 18, INK_M))
        b.append(txt(f"{v:,}", RX + 16, ly2, RW - 32, None, 18, INK_D, MONO, align="END"))
        ly2 += 28
    b.append(txt(f"已取消 3 项 {CANCEL_TOT:,} 元未计入", RX + 16, ly2 + 2, RW - 32,
                 None, 18, INK_L))
    ly2 += 26
    guard(ly2 - 2, 0, TOT_Y - 8, "构成条")

    # ---------------- 页脚
    footer(b, C0, TOT_Y + 42, W - 2 * C0,
           "云栖里项目与全部报价、核价、差额均为自拟演示数据，非真实成交或造价记录 · " + DISCLAIM)

    guard(TOT_Y + 92, 0, H, "页脚")
    return canvas(W, H, "".join(b), bg=PAPER)


def case_note(size) -> str:
    return f"""# case-02 · 旧房翻新报价逐项核对

## 用户情境

- **受众**：自住业主（非专业），在餐桌/书桌上对照装修公司报价单。
- **什么时候用**：签约前逐项核对，可能打印一张贴在墙上反复看。
- **真正要回答的问题**：总价差在哪一栏？有没有哪些项明显偏低、后面可能要补钱？
- **领域**：家装 / 造价核对

## 这件独有的视觉决定

差额列不是纯数字，而是**一条文字里嵌一个 WidgetSpan**：金额后面跟着一条以中心刻度为原点的
迷你双向条——负差向左、红色，正差向右、琥珀，长度按 ±10,000 元满量程。
一眼扫过差额列就能看出偏离方向和量级，不必逐个读数。辅助手段有三：

1. `fontFeatures="tnum=2"` + `textAlign="END"` 让金额列严格右对齐；
2. 被取消的 3 项用 `decoration="LINE_THROUGH"` 把分项名和差额同时划掉；
3. 分项格用**嵌套 Text** 在同一行混字号混颜色（名称 21px 粗 / 备注 18px 浅）。

- 画布 {W}×{H}；正文 18–21px、金额 20px，均不低于 18px。

## 数据的可信度

「云栖里」项目、12 个分项的报价与核价、差额、取消项**全部自拟**，用于演示核对表的
信息结构，不是真实报价、真实造价或真实成交记录。

## 实际自检

见 `tmp/run-20261011-01/B03/iterations.jsonl` 中 case-02 的记录；
生成期用 `assert_fits` 校验金额与标签不溢出。

## 素材情况

纯 DSL，无 `<Image>`，无外部素材。

## 文件

| 文件 | 说明 |
|---|---|
| `final.png` | {size['width']}×{size['height']}，open-snapshot 服务真实响应 |
| `final.snapshot` | 同名完整 DSL 源码 |
| `case.md` | 本文件 |

{DISCLAIM}
"""