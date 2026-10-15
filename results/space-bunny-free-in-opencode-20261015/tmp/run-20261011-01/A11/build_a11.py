#!/usr/bin/env python
"""A11 文字保真与跨页结算单 —— 两页 1200×1600。

启动基准：总任务根 (suite_root)。输入 tasks/A11-bilingual-invoice/inputs/invoice.json 只读。

服务端的文本语义（由 tmp/run-20261011-01/A11/probe_a11.py 与 probe_a11b.py 实测，
出图见 preview/probe-text.png / probe-text2.png / preview/ent*-*.png）：
  * `Text` 子文本内容与 `text` 属性都**不解码 XML 实体**：`&lt;` 会被画成 "&lt;"。
  * 子文本内容里裸写 `<` 会被 XML 解析器拒绝（HTTP 400）；裸写 `&` 与 `>` 可以。
  * **`text` 属性里裸写 `<`、`&`、`>` 可以正确渲染**；属性值内的双空格也保留。
  * 嵌套 `Text` 的文本节点会被 trim，因此富文本里的空格要用 `<Raw> </Raw>` 承载。
  * `Row crossAxisAlignment="BASELINE"` 缺 `textBaseline` 会 400（BASELINE 只在文本对齐时可用）。
  * `Positioned` 只接受一个子节点。
因此：literal_lines 与含尖括号/& 的字符串一律用 `text="..."` + 裸字符写出，
并在 emit 前断言字符串里不含双引号（本套输入确实不含）。
"""
from __future__ import annotations

import json
import os
import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

sys.path.insert(0, "tmp/run-20261011-01/_suite/scripts")
import snapkit as sk  # noqa: E402

TASK = "A11"
BASE = "tasks/A11-bilingual-invoice"
INVOICE_IN = f"{BASE}/inputs/invoice.json"
DRAFTS = f"tmp/run-20261011-01/{TASK}/drafts"

W, H = 1200, 1600
MARGIN = 48                       # 安全边距
CW = W - 2 * MARGIN               # 1104 内容宽

F_HEAD = "Inter Semi Bold"        # 拉丁半粗（实际返回为 Inter Semi Bold）
F_NUM = "Inter Medium"
F_LATIN = "Inter"
F_SC = "Noto Sans CJK SC"
F_JP = "Noto Sans CJK JP"
F_MONO = "DejaVu Sans Mono"

# 中日英混排：拉丁走 Inter，汉字走 SC，kana 走 JP
F_MIX = f"{F_LATIN},{F_SC},{F_JP}"
F_TITLE = f"{F_HEAD},{F_SC},{F_JP}"

INK = "#0F172A"
INK2 = "#1E293B"
MUTED = "#64748B"
FAINT = "#94A3B8"
LINE = "#E2E8F0"
GREEN = "#059669"
SLATE_GRAY = "#94A3B8"
BRAND = "#1D4ED8"

BODY = 26          # 正文字号（题面要求 ≥24）
BODY_SM = 24       # 次级正文
FOOT = 20          # 脚注（题面要求 ≥20）
LIT = 30           # literal_lines 字号
MONO_W = 7         # DejaVu Sans Mono 在 30px 下的近似字宽（用于定位，非排版依据）

TEXTS: list[dict] = []             # text-map 的来源


# ---------------------------------------------------------------- 金额（十进制定点）
def q2(v: Decimal) -> Decimal:
    return v.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def thousands(d: Decimal) -> str:
    s = f"{d:,.2f}"
    return s


def compute(inv: dict) -> dict:
    lines = []
    for it in inv["items"]:
        qty = int(it["quantity"])
        unit = Decimal(str(it["unit_price"]))
        amount = q2(Decimal(qty) * unit)
        lines.append({"sku": it["sku"], "name": it["name"], "quantity": qty,
                      "unit_price": unit, "line_amount": amount})
    subtotal = q2(sum((l["line_amount"] for l in lines), Decimal("0")))
    discount = q2(Decimal(str(inv["discount"])))
    taxable = q2(subtotal - discount)                       # 税前折后货品额
    rate = Decimal(str(inv["tax_rate"]))
    tax_exact = taxable * rate
    tax = q2(tax_exact)                                     # 四舍五入至分
    shipping = q2(Decimal(str(inv["shipping"])))
    total = q2(taxable + tax + shipping)
    return {
        "lines": lines, "subtotal": subtotal, "discount": discount, "taxable": taxable,
        "rate": rate, "tax_exact": tax_exact, "tax": tax, "shipping": shipping, "total": total,
    }


# ---------------------------------------------------------------- 文本发射器
def q(s: str) -> str:
    """把字面量直接放进属性值的引号之间。

    本服务的解析器不解码 XML 实体，所以这里**不能**调用 XML 转义：
    一旦转义成 `&lt;` 就会在图上显示成 "&lt;"（题面明确禁止）。
    调用方在 `T()` 里断言字符串不含双引号。
    """
    return '"' + s + '"'


def T(page: int, role: str, text: str, *, x: float, y: float, w: float, h: float,
      size: int, family: str, color: str = INK2, align: str | None = None,
      raw: bool = False) -> str:
    """发射一个 Text 并登记到 text-map。

    一律用 `text="…"` 属性承载字面量：实测本服务的解析器**不解码 XML 实体**
    （`&lt;` 会被画成 "&lt;"），而属性里裸写 `<`、`&`、`>` 可以正确渲染，
    且属性值能原样保留内部连续空格。调用方保证字符串中不含双引号。
    """
    assert '"' not in text, f"text 属性无法承载双引号：{text!r}"
    attrs = (f' fontSize="{size}" color="{color}" fontFamily="{family}"'
             + (f' textAlign="{align}"' if align else ""))
    node = f"<Text{attrs} text={q(text)}/>"
    TEXTS.append({
        "page": page, "id": f"p{page}-t{len(TEXTS) + 1:03d}", "role": role, "text": text,
        "x": round(x, 2), "y": round(y, 2), "width": round(w, 2), "height": round(h, 2),
        "font_family": family, "font_size": size, "color": color,
        "text_align": align or "START", "size_unit": "px", "path_base": "canvas",
        "placement": "text 属性（裸字符，不做实体转义）",
    })
    return (f'<Positioned left="{round(x, 2)}" top="{round(y, 2)}" '
            f'width="{round(w, 2)}" height="{round(h, 2)}">{node}</Positioned>')


def raw_node(x, y, w, h, node):
    return (f'<Positioned left="{round(x, 2)}" top="{round(y, 2)}" '
            f'width="{round(w, 2)}" height="{round(h, 2)}">{node}</Positioned>')


# ---------------------------------------------------------------- 定点金额（三段式，小数点列对齐）
DOT_W, FRAC_W = 9, 44


def money(page: int, role: str, value: Decimal, *, x_dec: float, y: float, h: float,
          int_w: int, size: int = BODY, color: str = INK2, bold: bool = False) -> str:
    """把金额画成「整数部分右对齐 | 小数点居中于 x_dec | 小数部分左对齐」三段。

    这样同一列的所有小数点严格落在 x_dec 这一条竖线上（题面要求「金额小数点列对齐」）。
    """
    s = f"{value:,.2f}"
    int_part, frac_part = s.split(".")
    fam = F_NUM if not bold else f"{F_HEAD},{F_NUM}"
    out = [
        T(page, role + ".整数部分", int_part, x=x_dec - DOT_W - int_w, y=y, w=int_w, h=h,
          size=size, family=fam, color=color, align="RIGHT"),
        T(page, role + ".小数点", ".", x=x_dec - DOT_W, y=y, w=2 * DOT_W, h=h,
          size=size, family=fam, color=color, align="CENTER"),
        T(page, role + ".小数部分", frac_part, x=x_dec + DOT_W, y=y, w=FRAC_W, h=h,
          size=size, family=fam, color=color, align="LEFT"),
    ]
    TEXTS.append({
        "page": page, "id": f"p{page}-t{len(TEXTS) + 1:03d}", "role": role + "（整体）",
        "text": s, "x": round(x_dec, 2), "y": round(y, 2),
        "width": round(int_w + 2 * DOT_W + FRAC_W, 2), "height": round(h, 2),
        "font_family": fam, "font_size": size, "color": color, "text_align": "RIGHT",
        "size_unit": "px", "path_base": "canvas",
        "decimal_point_x": round(x_dec, 2),
        "placement": "整数右对齐 + 小数点居中于 x + 小数左对齐，三段合读",
    })
    return "".join(out)


# ---------------------------------------------------------------- 公共版式
HDR_CARD = (72, 156)             # 页眉卡 (y, h)
FOOT_Y1, FOOT_Y2, FOOT_RULE = 1496, 1522, 1486


def header(page: int, inv: dict) -> str:
    """两页完全一致的重复页眉（编号一致）。"""
    P = []
    A = P.append
    hy, hh = HDR_CARD
    A(f'<Positioned left="{MARGIN}" top="{MARGIN}" width="{CW}" height="8">'
      f'<Container width="{CW}" height="8" color="{BRAND}" borderRadius="4"/></Positioned>')
    A(f'<Positioned left="{MARGIN}" top="{hy}" width="{CW}" height="{hh}">'
      f'<Container width="{CW}" height="{hh}" color="#FFFFFF" borderRadius="14" '
      f'border="1.5 SOLID #CBD5E1"/></Positioned>')
    A(T(page, "页眉.标题", "结算单 / SETTLEMENT INVOICE",
        x=MARGIN + 32, y=hy + 14, w=640, h=48, size=36, family=F_TITLE, color=INK))
    A(T(page, "页眉.单号", inv["invoice_id"],
        x=700, y=hy + 20, w=420, h=40, size=30, family=f"{F_HEAD},{F_MONO}",
        color=BRAND, align="RIGHT"))
    A(f'<Positioned left="{MARGIN + 32}" top="{hy + 70}" width="{CW - 64}" height="1.4">'
      f'<Container width="{CW - 64}" height="1.4" color="{LINE}"/></Positioned>')
    fields = [("卖方 SELLER", inv["seller"], 0, 290, F_SC),
              ("买方 BUYER", inv["buyer"], 312, 420, F_MIX),
              ("开票日期 ISSUED", inv["issued"], 756, 150, F_NUM),
              ("币种 CCY", inv["currency"], 926, 114, F_NUM)]
    for label, value, dx, fw, fam in fields:
        A(T(page, "页眉.字段标签", label, x=MARGIN + 32 + dx, y=hy + 80, w=fw, h=24,
            size=FOOT, family=f"{F_LATIN},{F_SC}", color=MUTED))
        A(T(page, "页眉.字段值", value, x=MARGIN + 32 + dx, y=hy + 104, w=fw, h=32,
            size=BODY_SM, family=fam, color=INK))
    return "".join(P)


def footer(page: int, inv: dict, total: Decimal) -> str:
    P = []
    A = P.append
    A(f'<Positioned left="{MARGIN}" top="{FOOT_RULE}" width="{CW}" height="1.4">'
      f'<Container width="{CW}" height="1.4" color="{LINE}"/></Positioned>')
    A(T(page, "页脚.页码", f"第 {page} 页 / 共 2 页", x=MARGIN, y=FOOT_Y1, w=260, h=FOOT + 6,
        size=FOOT, family=f"{F_LATIN},{F_SC}", color=MUTED))
    A(T(page, "页脚.单号", f"{inv['invoice_id']} · {inv['issued']} · {inv['currency']}",
        x=380, y=FOOT_Y1, w=440, h=FOOT + 6, size=FOOT, family=f"{F_LATIN},{F_SC}",
        color=MUTED, align="CENTER"))
    A(T(page, "页脚.应付", f"应付合计 {total:,.2f} {inv['currency']}",
        x=852, y=FOOT_Y1, w=CW - 804, h=FOOT + 6, size=FOOT,
        family=f"{F_NUM},{F_SC}", color=INK, align="RIGHT"))
    A(T(page, "页脚.排印",
        f"两页页眉与单号一致 · 安全边距 {MARGIN}px · 正文 {BODY}px / 次级 {BODY_SM}px / "
        f"脚注 {FOOT}px / 原样文字 {LIT}px，均 ≥ 题面下限",
        x=MARGIN, y=FOOT_Y2, w=CW, h=FOOT + 4, size=FOOT, family=F_MIX, color=FAINT))
    return "".join(P)


def section(page: int, title: str, sub: str, y: int) -> str:
    P = []
    A = P.append
    A(f'<Positioned left="{MARGIN}" top="{y + 4}" width="6" height="30">'
      f'<Container width="6" height="30" color="{BRAND}" borderRadius="3"/></Positioned>')
    A(T(page, "小节标题", title, x=MARGIN + 18, y=y, w=760, h=36, size=30,
        family=F_TITLE, color=INK))
    A(T(page, "小节副题", sub, x=MARGIN + 18, y=y + 36, w=1000, h=26, size=FOOT,
        family=F_MIX, color=MUTED))
    return "".join(P)


def card(x, y, w, h, *, bg="#FFFFFF", border="#CBD5E1", radius=14, accent=None):
    out = [f'<Positioned left="{x}" top="{y}" width="{w}" height="{h}">'
           f'<Container width="{w}" height="{h}" color="{bg}" borderRadius="{radius}" '
           f'border="1.5 SOLID {border}"/></Positioned>']
    if accent:
        out.append(f'<Positioned left="{x}" top="{y}" width="6" height="{h}">'
                   f'<Container width="6" height="{h}" color="{accent}" borderRadius="3"/></Positioned>')
    return "".join(out)


# ---------------------------------------------------------------- 第 1 页
COL_SKU = (104, 164)
COL_NAME = (280, 360)
QTY_R = 708
XDEC_UNIT, INTW_UNIT = 900, 170
XDEC_AMT, INTW_AMT = 1098, 130
ROW_H = 88
TBL_TOP = 330
HDR_H = 48


def page1(inv: dict, m: dict) -> str:
    P = []
    A = P.append
    A(f'<Container width="{W}" height="{H}" color="#F5F7FA"><Stack fit="EXPAND">')
    A(header(1, inv))
    A(section(1, "明细 ITEMS", "四行 SKU · 中英或中日名称 · 数量 · 单价 · 行金额；同一列金额的小数点严格对齐", 252))

    # 表头
    hy = TBL_TOP
    A(f'<Positioned left="{MARGIN}" top="{hy}" width="{CW}" height="{HDR_H}">'
      f'<Container width="{CW}" height="{HDR_H}" color="#EFF4FB" borderRadius="8"/></Positioned>')
    A(T(1, "表头.序号", "序号", x=MARGIN, y=hy + 9, w=48, h=32, size=FOOT + 2,
        family=f"{F_HEAD},{F_SC}", color=INK2))
    A(T(1, "表头.SKU", "SKU", x=COL_SKU[0], y=hy + 9, w=COL_SKU[1], h=32, size=FOOT + 2,
        family=F_HEAD, color=INK2))
    A(T(1, "表头.名称", "名称（中 / 英 · 日）", x=COL_NAME[0], y=hy + 9, w=COL_NAME[1], h=32,
        size=FOOT + 2, family=f"{F_HEAD},{F_SC}", color=INK2))
    A(T(1, "表头.数量", "数量", x=QTY_R - 100, y=hy + 9, w=100, h=32, size=FOOT + 2,
        family=f"{F_HEAD},{F_SC}", color=INK2, align="RIGHT"))
    A(T(1, "表头.单价", f"单价 {inv['currency']}", x=XDEC_UNIT - DOT_W - INTW_UNIT, y=hy + 9,
        w=INTW_UNIT + DOT_W + FRAC_W + 60, h=32, size=FOOT + 2,
        family=f"{F_HEAD},{F_SC}", color=INK2, align="RIGHT"))
    A(T(1, "表头.行金额", f"行金额 {inv['currency']}", x=XDEC_AMT - DOT_W - INTW_AMT, y=hy + 9,
        w=INTW_AMT + DOT_W + FRAC_W + 20, h=32, size=FOOT + 2,
        family=f"{F_HEAD},{F_SC}", color=INK2, align="RIGHT"))

    # 四行明细
    for i, ln in enumerate(m["lines"]):
        ry = TBL_TOP + HDR_H + i * ROW_H
        A(f'<Positioned left="{MARGIN}" top="{ry}" width="{CW}" height="{ROW_H}">'
          f'<Container width="{CW}" height="{ROW_H}" '
          f'color="{"#FFFFFF" if i % 2 == 0 else "#FAFBFD"}"/>'
          f'</Positioned>')
        A(f'<Positioned left="{MARGIN}" top="{ry + ROW_H - 1}" width="{CW}" height="1">'
          f'<Container width="{CW}" height="1" color="{LINE}"/></Positioned>')
        A(T(1, f"明细{i + 1}.序号", f"{i + 1:02d}", x=MARGIN, y=ry + 32, w=48, h=30,
            size=BODY, family=F_NUM, color=FAINT))
        A(T(1, f"明细{i + 1}.SKU", ln["sku"], x=COL_SKU[0], y=ry + 30, w=COL_SKU[1], h=34,
            size=BODY, family=f"{F_HEAD},{F_NUM}", color=INK))
        A(T(1, f"明细{i + 1}.名称", ln["name"], x=COL_NAME[0], y=ry + 6, w=COL_NAME[1], h=76,
            size=BODY, family=F_MIX, color=INK2))
        A(T(1, f"明细{i + 1}.数量", f"{ln['quantity']}", x=QTY_R - 100, y=ry + 30, w=100, h=34,
            size=BODY, family=F_NUM, color=INK2, align="RIGHT"))
        A(money(1, f"明细{i + 1}.单价", ln["unit_price"], x_dec=XDEC_UNIT, y=ry + 28,
                h=38, int_w=INTW_UNIT, size=BODY, color=INK2))
        A(money(1, f"明细{i + 1}.行金额", ln["line_amount"], x_dec=XDEC_AMT, y=ry + 28,
                h=38, int_w=INTW_AMT, size=BODY, color=INK, bold=True))

    # ---- 左卡：计税顺序与定点计算
    lx, ly, lw, lh = MARGIN, 754, 552, 588
    A(card(lx, ly, lw, lh, accent=BRAND))
    A(T(1, "计税卡.标题", "计税顺序与定点计算", x=lx + 24, y=ly + 20, w=lw - 48, h=34,
        size=26, family=F_TITLE, color=INK))
    A(T(1, "计税卡.副题", "严格按 invoice.json 的 notes 所述顺序，逐步给出中间值",
        x=lx + 24, y=ly + 56, w=lw - 48, h=26, size=FOOT, family=F_SC, color=MUTED))
    line_sum = " + ".join(f"{l['line_amount']:,.2f}" for l in m["lines"])
    steps = [
        "1  逐行金额 = 数量 × 单价（定点）",
        f"2  货品小计 = {line_sum}",
        f"3  折扣在税前扣除：{m['subtotal']:,.2f} − {m['discount']:,.2f}",
        f"     = {m['taxable']:,.2f}",
        f"4  税额 = {m['taxable']:,.2f} × 税率 {m['rate']} = {m['tax_exact']}（未取整）",
        f"5  四舍五入至分 ROUND_HALF_UP → {m['tax']:,.2f}",
        f"6  运费不计税，直接相加：{m['shipping']:,.2f}",
        f"7  应付 = {m['taxable']:,.2f} + {m['tax']:,.2f} + {m['shipping']:,.2f}",
        f"     = {m['total']:,.2f} {inv['currency']}",
    ]
    yy = ly + 92
    for i, s in enumerate(steps):
        n = sk.est_lines(s, lw - 48, BODY_SM)
        h = n * 34
        A(T(1, f"计税步骤{i + 1}", s, x=lx + 24, y=yy, w=lw - 48, h=h,
            size=BODY_SM, family=f"{F_NUM},{F_SC}", color=INK2))
        yy += h + 2

    # ---- 右卡：金额汇总
    rx, rw = 624, W - MARGIN - 624
    ry0 = ly
    A(card(rx, ry0, rw, lh, accent=GREEN))
    A(T(1, "汇总卡.标题", "金额汇总", x=rx + 24, y=ry0 + 20, w=rw - 48, h=34,
        size=26, family=F_TITLE, color=INK))
    A(T(1, "汇总卡.表头", f"项目（{inv['currency']}）", x=rx + 24, y=ry0 + 64, w=240, h=26,
        size=FOOT, family=f"{F_HEAD},{F_SC}", color=MUTED))
    A(T(1, "汇总卡.表头右", "金额", x=rx + 264, y=ry0 + 64, w=rw - 288, h=26, size=FOOT,
        family=f"{F_HEAD},{F_SC}", color=MUTED, align="RIGHT"))
    summary = [
        ("货品小计 Subtotal", "", m["subtotal"], INK2, False),
        ("折扣 Discount", "税前扣除", -m["discount"], INK2, False),
        ("税前货品额 Taxable goods", "计税基数", m["taxable"], INK, True),
        (f"税额 Tax @ {m['rate'] * 100:g}%", "不含运费", m["tax"], INK2, False),
        ("运费 Shipping", "不计税", m["shipping"], INK2, False),
    ]
    yy = ry0 + 98
    for i, (label, tag, val, col, bold) in enumerate(summary):
        A(T(1, f"汇总{i + 1}.项目", label, x=rx + 24, y=yy + 5, w=236, h=34,
            size=BODY_SM, family=f"{F_NUM},{F_SC}", color=INK2))
        A(T(1, f"汇总{i + 1}.标注", tag, x=rx + 266, y=yy + 10, w=100, h=28,
            size=FOOT, family=F_SC, color=BRAND))
        A(money(1, f"汇总{i + 1}.金额", val, x_dec=rx + rw - 24 - FRAC_W, y=yy + 4, h=38,
                int_w=120, size=BODY_SM, color=col, bold=bold))
        yy += 52
    A(f'<Positioned left="{rx + 24}" top="{yy + 8}" width="{rw - 48}" height="1.4">'
      f'<Container width="{rw - 48}" height="1.4" color="#94A3B8"/></Positioned>')
    A(T(1, "汇总.应付标签", "应付 Total due", x=rx + 24, y=yy + 26, w=280, h=50,
        size=32, family=F_TITLE, color=INK))
    A(money(1, "汇总.应付金额", m["total"], x_dec=rx + rw - 24 - FRAC_W, y=yy + 26, h=52,
            int_w=170, size=34, color=GREEN, bold=True))
    A(T(1, "汇总.应付脚注",
        f"折扣在税前从货品小计扣除、运费不计税（依 notes 第 2、3 条）；"
        f"计税基数为折后货品额 {m['taxable']:,.2f}，运费 {m['shipping']:,.2f} 另计。",
        x=rx + 24, y=yy + 92, w=rw - 48, h=90, size=FOOT, family=F_SC, color=MUTED))

    # ---- 本页口径条
    by = 1354
    A(card(MARGIN, by, CW, 120, bg="#EFF6FF", border="#BFDBFE", radius=12))
    A(f'<Positioned left="{MARGIN + 20}" top="{by + 42}" width="118" height="36">'
      f'<Container width="118" height="36" color="{BRAND}" borderRadius="18" alignment="CENTER">'
      f'<Text fontSize="20" color="#FFFFFF" fontFamily="{F_HEAD},{F_SC}">本页口径</Text>'
      f'</Container></Positioned>')
    A(T(1, "说明条.正文",
        "折扣在税前从货品小计扣除；运费不计税；税额 = 税前折后货品金额 × 6%，"
        "以 ROUND_HALF_UP 四舍五入至分；最终应付再加运费。本单为虚构排版测试，不是实际发票。",
        x=MARGIN + 150, y=by + 10, w=CW - 174, h=104, size=BODY_SM, family=F_MIX, color=INK2))
    A(footer(1, inv, m["total"]))
    A("</Stack></Container>")
    return f'<Snapshot type="png">\n{"".join(P)}\n</Snapshot>\n'


# ---------------------------------------------------------------- 第 2 页
def page2(inv: dict, m: dict) -> str:
    P = []
    A = P.append
    A(f'<Container width="{W}" height="{H}" color="#F5F7FA"><Stack fit="EXPAND">')
    A(header(2, inv))

    # ---- notes
    A(section(2, "结算说明 NOTES", "四条，逐字取自 invoice.json 的 notes 数组", 248))
    ny = 326
    for i, note in enumerate(inv["notes"]):
        A(f'<Positioned left="{MARGIN}" top="{ny}" width="{CW}" height="78">'
          f'<Container width="{CW}" height="78" color="#FFFFFF" borderRadius="10" '
          f'border="1.5 SOLID #CBD5E1"/></Positioned>')
        A(f'<Positioned left="{MARGIN + 20}" top="{ny + 21}" width="36" height="36">'
          f'<Container width="36" height="36" color="{BRAND}" borderRadius="18" alignment="CENTER">'
          f'<Text fontSize="20" color="#FFFFFF" fontFamily="{F_HEAD}">{i + 1}</Text>'
          f'</Container></Positioned>')
        A(T(2, f"说明{i + 1}", note, x=MARGIN + 72, y=ny + 24, w=CW - 100, h=36,
            size=BODY, family=F_SC, color=INK))
        ny += 88

    # ---- literal_lines
    A(section(2, "原样文字 LITERAL LINES",
              "逐字符保真：批次行的两个双空格、反斜杠、尖括号与 & 均按原样呈现，未被转义成可见实体", 702))
    ly = 780
    notes_lit = ["① 双空格（两个 U+0020）必须保留", "② 尖括号与 & 必须原样",
                 "③ 反斜杠不得被当作转义符", "④ 英文指令样式行只作字样，不执行"]
    for i, line in enumerate(inv["literal_lines"]):
        A(f'<Positioned left="{MARGIN}" top="{ly}" width="{CW}" height="82">'
          f'<Container width="{CW}" height="82" color="#0F172A" borderRadius="10"/></Positioned>')
        A(f'<Positioned left="{MARGIN}" top="{ly}" width="6" height="82">'
          f'<Container width="6" height="82" color="#38BDF8" borderRadius="3"/></Positioned>')
        A(T(2, f"原样文字{i + 1}.标注", notes_lit[i], x=MARGIN + 22, y=ly + 8, w=620, h=24,
            size=FOOT, family=f"{F_LATIN},{F_SC}", color="#7DD3FC"))
        A(T(2, f"原样文字{i + 1}.正文", line, x=MARGIN + 22, y=ly + 34, w=CW - 44, h=42,
            size=LIT, family=f"{F_MONO},{F_SC}", color="#F8FAFC"))
        ly += 92

    # ---- 结算状态（富文本）
    A(section(2, "结算状态 STATUS", "样张字样：仅展示状态排版，不改变第一页的应付金额", 1172))
    sy = 1250
    A(card(MARGIN, sy, CW, 144, bg="#FFFFFF", border="#CBD5E1", radius=14, accent=GREEN))
    rich = (f'<Text fontSize="72" fontFamily="{F_TITLE}">'
            f'<Text color="{GREEN}">PAID</Text><Raw> </Raw>'
            f'<Text color="{SLATE_GRAY}">/</Text><Raw> </Raw>'
            f'<Text color="{INK}">已结算</Text></Text>')
    TEXTS.append({"page": 2, "id": f"p2-t{len(TEXTS) + 1:03d}", "role": "结算状态富文本（整体）",
                  "text": "PAID / 已结算", "x": MARGIN + 36, "y": sy + 24,
                  "width": 560, "height": 88, "font_family": F_TITLE, "font_size": 72,
                  "color": "分段着色", "text_align": "START", "size_unit": "px",
                  "path_base": "canvas",
                  "placement": "单个 Text 内嵌套三个带色 Text，空格由 <Raw> </Raw> 承载，共用同一段落基线"})
    for seg, col, fam, note in (("PAID", GREEN, F_HEAD, "绿色段"),
                                (" / ", SLATE_GRAY, F_HEAD, "斜线与两侧空格为灰色段"),
                                ("已结算", INK, F_SC, "深色中文段")):
        TEXTS.append({"page": 2, "id": f"p2-t{len(TEXTS) + 1:03d}",
                      "role": f"结算状态富文本.{note}", "text": seg,
                      "x": MARGIN + 36, "y": sy + 24, "width": 560, "height": 88,
                      "font_family": fam, "font_size": 72, "color": col,
                      "text_align": "START", "size_unit": "px", "path_base": "canvas",
                      "placement": "嵌套 Text span"})
    A(raw_node(MARGIN + 36, sy + 24, 560, 88, rich))
    A(T(2, "结算状态.声明",
        f"该字样只表示样张的排印状态；第一页计算出的应付金额 {m['total']:,.2f} {inv['currency']} "
        f"未因本字样发生任何改变。",
        x=MARGIN + 620, y=sy + 30, w=CW - 656, h=100, size=BODY_SM, family=F_MIX, color=INK2))

    # ---- 排印约定
    A(card(MARGIN, 1406, CW, 74, bg="#FFFFFF", border="#CBD5E1", radius=12))
    A(T(2, "排印.字号",
        f"正文 {BODY}px / 次级 {BODY_SM}px / 脚注与说明 {FOOT}px（原样文字 {LIT}px），均 ≥ 题面下限；"
        f"安全边距 {MARGIN}px，不靠微缩塞字。",
        x=MARGIN + 24, y=1414, w=CW - 48, h=26, size=FOOT, family=F_MIX, color=INK2))
    A(T(2, "排印.字体",
        "拉丁 Inter Semi Bold / Medium；中文 Noto Sans CJK SC；"
        "日文 CJK JP；原样文字 DejaVu Sans Mono。",
        x=MARGIN + 24, y=1442, w=CW - 48, h=26, size=FOOT, family=F_MIX, color=MUTED))
    A(footer(2, inv, m["total"]))
    A("</Stack></Container>")
    return f'<Snapshot type="png">\n{"".join(P)}\n</Snapshot>\n'


# ---------------------------------------------------------------- 审计
def audit(inv: dict, m: dict) -> dict:
    return {
        "schema_version": 1, "task_id": TASK, "path_base": "output_dir", "round": "round-01",
        "title": "文字保真与跨页结算单",
        "source": {"invoice": "inputs/invoice.json", "modified": False,
                   "note": "全部字段原样读取；页面上的每一段文字都可在 text-map.json 中回溯到源数组"},
        "money_policy": {
            "arithmetic": "十进制定点（Python decimal.Decimal），不使用二进制浮点",
            "rounding": "ROUND_HALF_UP（四舍五入），仅在入账时执行一次",
            "round_to": "分（两位小数）",
            "intermediate_kept": "中间值（如税额未取整的精确值）在页面与本审计中同时给出",
            "tax_order": ["逐行金额 = 数量 × 单价", "货品小计 = 各行金额之和",
                          "折扣在税前从货品小计扣除 → 税前货品额",
                          "税额 = 税前货品额 × 税率", "税额四舍五入至分",
                          "运费不计税", "应付 = 税前货品额 + 税额 + 运费"],
        },
        "invoice_id": inv["invoice_id"], "issued": inv["issued"], "currency": inv["currency"],
        "seller": inv["seller"], "buyer": inv["buyer"],
        "tax_rate": inv["tax_rate"],
        "lines": [{
            "index": i + 1, "sku": l["sku"], "name": l["name"],
            "quantity": l["quantity"], "unit_price": str(l["unit_price"]),
            "formula": f"{l['quantity']} × {l['unit_price']}",
            "line_amount": f"{l['line_amount']:.2f}",
            "line_amount_decimal": str(l["line_amount"]),
        } for i, l in enumerate(m["lines"])],
        "totals": {
            "subtotal": f"{m['subtotal']:.2f}",
            "subtotal_formula": " + ".join(f"{l['line_amount']:.2f}" for l in m["lines"]),
            "discount": f"{m['discount']:.2f}",
            "discount_applied": "税前，从货品小计扣除",
            "taxable_goods_amount": f"{m['taxable']:.2f}",
            "taxable_exact_formula": f"{m['subtotal']:.2f} - {m['discount']:.2f} = {m['taxable']:.2f}",
            "tax_base_exact": f"{m['taxable']:.2f}",
            "tax_rate": str(m["rate"]),
            "tax_exact_before_rounding": f"{m['tax_exact']}",
            "tax_rounded": f"{m['tax']:.2f}",
            "tax_rounding_method": "ROUND_HALF_UP to 0.01",
            "shipping": f"{m['shipping']:.2f}",
            "shipping_taxable": False,
            "total_due": f"{m['total']:.2f}",
            "total_formula": (f"{m['taxable']:.2f} + {m['tax']:.2f} + {m['shipping']:.2f}"
                              f" = {m['total']:.2f}"),
        },
        "literal_lines": {
            "requirement": "逐字符保真；批次行的两个双空格必须保留；反斜杠、尖括号、& 不得被转义成可见实体",
            "count": len(inv["literal_lines"]),
            "lines": [{"index": i + 1, "verbatim": s, "codepoints": [f"U+{ord(c):04X}" for c in s],
                       "length": len(s), "double_space_count": s.count("  "),
                       "contains_backslash": "\\" in s,
                       "contains_angle_bracket": ("<" in s) or (">" in s),
                       "contains_ampersand": "&" in s}
                      for i, s in enumerate(inv["literal_lines"])],
        },
        "confusable_sku": {
            "values": [i["sku"] for i in inv["items"]],
            "risk": "O0-I1-B8 同时含字母 O 与数字 0、字母 I 与数字 1；A<B&C>D 含尖括号与 &",
            "handling": "全部 SKU 用 Inter Semi Bold + Inter Medium 排印（该组合下 O/0、I/1 字形可分）；"
                        "逐字符保真依靠 text 属性写裸字符，实测见 report 与 probe 出图",
        },
        "parser_finding": {
            "claim": "Text 的子文本与 text 属性都不解码 XML 实体；子文本中的裸 < 会被 XML 解析器拒绝",
            "evidence": ["tmp/run-20261011-01/A11/preview/probe-text.png（&lt; 被画成 &lt;）",
                         "tmp/run-20261011-01/A11/preview/ent-bare-amp-literal.png（子文本裸 & 正常）",
                         "tmp/run-20261011-01/A11/responses/A11-ent-bare-lt-literal-f66893a7.error.json（裸 < 400）",
                         "tmp/run-20261011-01/A11/preview/ent2-attr-bare.png（text 属性裸字符正常）",
                         "tmp/run-20261011-01/A11/preview/ent2-cdata.png（CDATA 亦可，但本页统一用 text 属性）"],
            "mitigation": "literal_lines、含尖括号/& 的 SKU 一律写成 text=\"…\" 且属性内放裸字符；"
                          "构建器断言字符串不含双引号（本套输入确实不含）",
        },
        "rich_text": {
            "requirement": "PAID 绿色、斜线灰色、中文深色、自然共用基线；只是样张状态，不能改变应付数值",
            "implementation": "单个 <Text fontSize=\"72\"> 内嵌套三个带色 <Text>，空格由 <Raw> </Raw> 承载"
                              "（嵌套 Text 的文本节点会被 trim）",
            "colors": {"PAID": GREEN, "slash_and_spaces": SLATE_GRAY, "已结算": INK},
            "affects_total_due": False,
        },
        "layout": {"canvas": [W, H], "safe_margin": MARGIN, "content_width": CW,
                   "body_px": BODY, "secondary_px": BODY_SM, "footnote_px": FOOT,
                   "literal_px": LIT,
                   "min_required": "正文 ≥24，脚注 ≥20，安全边距 48",
                   "repeated_header": "两页页眉完全一致（标题、单号、卖方、买方、日期、币种）",
                   "page_numbers": ["第 1 页 / 共 2 页", "第 2 页 / 共 2 页"]},
        "outputs": [{"kind": "png", "filename": "invoice-page-01.png",
                     "dsl": "invoice-page-01.snapshot", "width": W, "height": H},
                    {"kind": "png", "filename": "invoice-page-02.png",
                     "dsl": "invoice-page-02.snapshot", "width": W, "height": H},
                    {"kind": "json", "filename": "invoice-audit.json"},
                    {"kind": "json", "filename": "text-map.json"}],
    }


def main() -> None:
    ver = sys.argv[1] if len(sys.argv) > 1 else "v1"
    base = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
    inv = json.loads((base / INVOICE_IN).read_text(encoding="utf-8"))
    m = compute(inv)

    d = base / DRAFTS
    d.mkdir(parents=True, exist_ok=True)
    dsl1 = page1(inv, m)
    p1_texts = len(TEXTS)
    dsl2 = page2(inv, m)
    (d / f"a11-p1-{ver}.snapshot").write_text(dsl1, encoding="utf-8")
    (d / f"a11-p2-{ver}.snapshot").write_text(dsl2, encoding="utf-8")

    text_map = {
        "schema_version": 1, "task_id": TASK, "path_base": "output_dir", "round": "round-01",
        "canvas": {"width": W, "height": H, "pages": 2, "origin": "top-left",
                   "x_direction": "right", "y_direction": "down", "unit": "px"},
        "font_sources": {"query": "GET /fonts", "families_available": 27,
                         "used": {"Inter": "拉丁与数字", "Inter Semi Bold": "标题与 SKU",
                                  "Inter Medium": "金额",
                                  "Noto Sans CJK SC": "简体中文",
                                  "Noto Sans CJK JP": "日文假名与汉字",
                                  "DejaVu Sans Mono": "原样文字与路径"}},
        "counts": {"page_1_segments": p1_texts, "page_2_segments": len(TEXTS) - p1_texts,
                   "total_segments": len(TEXTS)},
        "segments": TEXTS,
    }
    (d / "text-map-raw.json").write_text(json.dumps(text_map, ensure_ascii=False, indent=2),
                                         encoding="utf-8")
    (d / "invoice-audit-raw.json").write_text(json.dumps(audit(inv, m), ensure_ascii=False,
                                                         indent=2), encoding="utf-8")

    print(f"subtotal={m['subtotal']} discount={m['discount']} taxable={m['taxable']} "
          f"tax_exact={m['tax_exact']} tax={m['tax']} shipping={m['shipping']} total={m['total']}")
    for ln in m["lines"]:
        print("  ", ln["sku"], ln["quantity"], "x", ln["unit_price"], "=", ln["line_amount"])
    print("p1 bytes:", len(dsl1.encode()), "| p2 bytes:", len(dsl2.encode()),
          "| text segments:", len(TEXTS))


if __name__ == "__main__":
    main()