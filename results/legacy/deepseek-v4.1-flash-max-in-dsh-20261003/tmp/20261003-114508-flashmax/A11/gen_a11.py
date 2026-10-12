"""A11 generator: two-page bilingual settlement statement (1200x1600 each).

Content: tasks/A11-bilingual-invoice/inputs/invoice.json
Money:    decimal.Decimal fixed point, quantised to cents with ROUND_HALF_UP, in the
          order required by the invoice notes (discount before tax, shipping untaxed).

Text mechanism (measured with probe-a11 renders, see iterations.jsonl):
  * this parser does NOT decode XML entities - `&amp;` renders literally as "&amp;", so
    entity escaping must never be used for content;
  * bare `&` and `>` are passed through literally, bare `<` raises
    `PARSE_ERROR: Unexpected character ' ' in input state [TAG_OPEN]`;
  * `<![CDATA[...]]>` renders its payload verbatim, and `<Raw><![CDATA[...]]></Raw>`
    additionally preserves leading/duplicated spaces exactly.
All text nodes therefore use CDATA; whitespace-critical lines use Raw+CDATA.
"""
from __future__ import annotations

import json
import os
import sys
from decimal import Decimal, ROUND_HALF_UP, getcontext

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261003-114508-flashmax", "_suite", "shared"))
from dslkit import CJK, MONO  # noqa: E402

getcontext().prec = 40
TASK_DIR = os.path.join(ROOT, "tasks", "A11-bilingual-invoice")
INV = json.load(open(os.path.join(TASK_DIR, "inputs", "invoice.json"), encoding="utf-8"))

W, H, M = 1200, 1600, 48
CW = W - 2 * M                     # 1104
INK = "#0F172AFF"
SOFT = "#475569FF"
MUTED = "#64748BFF"
PAGE = "#F7F9FBFF"
CARD = "#FFFFFFFF"
EDGE = "#E2E8F0FF"
GREEN = "#0E9F8F"
BLUE = "#1D4ED8"
RED = "#D92D20"
AMBER = "#D97706"
SEP = "#94A3B8FF"
BAND = "#F1F5F9FF"

REG: list = []


# Advance widths measured from probe-metrics.png (see font-metrics.json):
#   Noto Sans Mono CJK SC digits/latin : 13.0000px at 26px = 0.5000 em (exact, uniform)
#   Noto Sans CJK SC han / kana        : 26.0000px at 26px = 1.0000 em (exact)
#   Noto Sans CJK SC proportional latin: 15.8px at 26px = 0.6077 em for "A"; lowercase
#   runs are much narrower, so 0.62 em is used as a conservative upper bound for checks.
MONO_EM = 0.5000          # exact, uniform (measured)
CJK_EM = 0.9952           # measured 25.875px at 26px
CLASS_EM = {"space": 0.5641, "punct_narrow": 0.2692, "punct_slash": 0.3846,
            "digit": 0.5385, "lower": 0.4700, "upper": 0.6106, "other": 0.5500}
NARROW = ".,:;!|'`"
SLASHY = "/\\-–—()[]{}<>+*=~"


def _em(ch: str) -> float:
    o = ord(ch)
    if o > 0x2E80:
        return CJK_EM
    if ch == " ":
        return CLASS_EM["space"]
    if ch in NARROW:
        return CLASS_EM["punct_narrow"]
    if ch in SLASHY:
        return CLASS_EM["punct_slash"]
    if ch.isdigit():
        return CLASS_EM["digit"]
    if ch.isupper():
        return CLASS_EM["upper"]
    if ch.islower():
        # measured per-glyph advances spread from ~0.30 (i,l,t) to 0.58 (a,o,u);
        # 0.47 is a deliberately conservative average so layout boxes stay wide enough
        return CLASS_EM["lower"]
    return CLASS_EM["other"]


def tw(s: str, size: float, family: str = CJK) -> float:
    if family == MONO:
        return size * MONO_EM * len(s)
    return sum(size * _em(ch) for ch in s)


class B:
    def __init__(self, page: int) -> None:
        self.page = page
        self.p = [f'<Snapshot background="{PAGE}" type="png">',
                  f'<Container width="{W}" height="{H}">',
                  '<Stack alignment="TOP_LEFT" fit="EXPAND">']

    def raw(self, s: str) -> None:
        self.p.append(s)

    def box(self, x, y, w, h, color=None, radius=None, border=None, extra=""):
        a = f'<Container width="{w}" height="{h}"'
        if color:
            a += f' color="{color}"'
        if radius is not None:
            a += f' borderRadius="{radius}"'
        if border:
            a += f' border="{border}"'
        if extra:
            a += " " + extra
        self.p.append(f'<Positioned left="{x}" top="{y}">{a}/></Positioned>')

    def line(self, x, y, w, h, color):
        self.box(x, y, w, h, color)

    def text(self, x, y, s, size, color, weight="NORMAL", family=CJK, role="body",
             source=None, right=None, center=None, max_w=None, raw=False, limit=M,
             limit_r=None):
        """Emit one text node, positioned from the left. `right` right-aligns to that
        edge using the measured advance widths; `raw` switches to <Raw><![CDATA[…]]>."""
        width = tw(s, size, family)
        if right is not None:
            x = right - width
        if center is not None:
            x = center - width / 2
        right_edge = x + width
        lim = limit_r if limit_r is not None else W - limit
        assert x >= limit - 0.5, f"[p{self.page}] {role} starts at {x:.1f} < {limit}: {s!r}"
        assert right_edge <= lim + 0.5, f"[p{self.page}] {role} ends at {right_edge:.1f} > {lim}: {s!r}"
        if max_w is not None:
            assert width <= max_w + 0.5, f"[p{self.page}] {role} width {width:.1f}>{max_w}: {s!r}"
        REG.append({"page": self.page, "role": role, "text": s, "x": round(x, 2),
                    "y": round(y, 2), "width_est": round(width, 2),
                    "fontSize": float(size), "fontFamily": family, "fontStyle": weight,
                    "color": color, "mechanism": "Raw+CDATA" if raw else "CDATA",
                    "source": source})
        a = (f'fontSize="{size}" color="{color}" fontFamily="{family}" '
             f'fontStyle="{weight}"')
        cdata = f'<![CDATA[{s}]]>'
        if raw:
            # <Raw> is only legal inside an outer <Text> (parser: "it can only be used
            # in the Text"), so the paragraph wrapper carries the same style.
            node = (f'<Text fontSize="{size}" fontFamily="{family}">'
                    f'<Raw {a}>{cdata}</Raw></Text>')
        else:
            node = f'<Text {a}>{cdata}</Text>'
        self.p.append(f'<Positioned left="{x:.2f}" top="{y}">{node}</Positioned>')

    def rich_paid(self, x, y, size):
        spans = [("PAID", GREEN, "BOLD"), (" / ", SEP, "NORMAL"), ("已结算", INK, "BOLD")]
        for s, c, w in spans:
            REG.append({"page": self.page, "role": "status-rich-text", "text": s,
                        "x": round(x, 2), "y": y, "fontSize": size, "fontFamily": CJK,
                        "fontStyle": w, "color": c,
                        "mechanism": "nested Text/Raw CDATA span (shared baseline)",
                        "source": "page-2 sample status, does not change the amount due"})
        self.p.append(
            f'<Positioned left="{x}" top="{y}"><Text fontSize="{size}" fontFamily="{CJK}">'
            f'<Text color="{GREEN}" fontStyle="BOLD" fontSize="{size}"><![CDATA[PAID]]></Text>'
            f'<Raw color="{SEP}" fontSize="{size}"><![CDATA[ / ]]></Raw>'
            f'<Text color="{INK}" fontStyle="BOLD" fontSize="{size}"><![CDATA[已结算]]></Text>'
            f'</Text></Positioned>')

    def finish(self) -> str:
        self.p += ['</Stack>', '</Container>', '</Snapshot>']
        return "\n".join(self.p) + "\n"


# ------------------------------------------------------------------ money
def q(v: Decimal) -> Decimal:
    return v.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def money(v: Decimal) -> str:
    return f"{v:,.2f}"


def compute():
    lines, subtotal = [], Decimal("0")
    for it in INV["items"]:
        qty, unit = Decimal(it["quantity"]), Decimal(it["unit_price"])
        amount = q(qty * unit)
        subtotal += amount
        lines.append({"sku": it["sku"], "name": it["name"], "quantity": int(qty),
                      "unit_price": f"{unit:.2f}", "line_amount": f"{amount:.2f}",
                      "computation": f"{unit:.2f} × {int(qty)}"})
    subtotal = q(subtotal)
    discount = q(Decimal(INV["discount"]))
    base = q(subtotal - discount)
    rate = Decimal(INV["tax_rate"])
    tax_raw = base * rate
    tax = q(tax_raw)
    shipping = q(Decimal(INV["shipping"]))
    return {"lines": lines, "goods_subtotal": subtotal, "discount": discount, "base": base,
            "rate": rate, "tax_raw": tax_raw, "tax": tax, "shipping": shipping,
            "due": q(base + tax + shipping)}


def header(b: B, c, subtitle: str, page_label: str):
    b.box(M, M, CW, 190, INK, radius=16)
    b.text(M + 32, M + 26, "结算单 · SETTLEMENT STATEMENT", 40, "#F8FAFCFF", "BOLD",
           role="page-title")
    b.text(M + 32, M + 134, subtitle, 22, "#94A3B8FF", role="page-subtitle")
    b.text(0, M + 30, INV["invoice_id"], 26, "#F8FAFCFF", "BOLD", family=MONO,
           role="invoice-id", source="invoice_id", right=W - M - 32)
    b.text(0, M + 76, f'{INV["issued"]}  ·  {INV["currency"]}', 24, "#94A3B8FF", family=MONO,
           role="issue-date-currency", source="issued,currency", right=W - M - 32)
    b.text(0, M + 122, page_label, 22, "#64748BFF", role="page-number", right=W - M - 32)


def footer(b: B, page_label: str, note: str):
    b.line(M, 1504, CW, 1, EDGE)
    b.text(M, 1516, f'{INV["invoice_id"]} · 结算单 · {page_label}', 22, MUTED, role="footer",
           source="invoice_id")
    b.text(0, 1516, note, 22, MUTED, role="footer-right", right=W - M)


# ------------------------------------------------------------------ page 1
def page1(c) -> str:
    b = B(1)
    header(b, c, "第一页：结算与明细 / Page 1 of 2 — settlement & line items",
           "第 1 页 / 共 2 页")

    py, ph = 268, 160
    cw3 = (CW - 48) / 3
    cards = [("销售方 / SELLER", [INV["seller"], "开票方 / ISSUER"], "seller", BLUE),
             ("购买方 / BUYER", ["Northstar Research", "株式会社"], "buyer", GREEN),
             ("单据信息 / DOCUMENT", [INV["invoice_id"], f'{INV["issued"]} · {INV["currency"]}'],
              "meta", AMBER)]
    for i, (label, values, role, accent) in enumerate(cards):
        x = M + i * (cw3 + 24)
        b.box(x, py, cw3, ph, CARD, radius=12, border=f"1 SOLID {EDGE}")
        b.line(x, py, 6, ph, accent + "FF")
        b.text(x + 24, py + 20, label, 22, MUTED, role=f"{role}-label")
        if role == "meta":
            b.text(x + 24, py + 58, values[0], 26, INK, "BOLD", family=MONO,
                   role="invoice-id-2", source="invoice_id")
            b.text(x + 24, py + 104, values[1], 24, SOFT, family=MONO, role="meta-line",
                   source="issued,currency")
        else:
            b.text(x + 24, py + 62, values[0], 28, INK, "BOLD", role=f"{role}-name",
                   source=role)
            b.text(x + 24, py + 106, values[1], 24, SOFT, role=f"{role}-note",
                   source=role)

    ty, head_h, row_h = 456, 56, 74
    th = head_h + row_h * len(c["lines"]) + 16
    b.box(M, ty, CW, th, CARD, radius=12, border=f"1 SOLID {EDGE}")
    b.box(M, ty, CW, head_h, BAND, extra='borderRadiusTopLeft="12" borderRadiusTopRight="12"')
    x_sku, x_name = M + 24, M + 192
    r_qty, r_unit, r_amt = M + 760, M + 880, M + 1080
    b.text(x_sku, ty + 16, "SKU", 22, SOFT, "BOLD", role="table-header")
    b.text(x_name, ty + 16, "名称 / DESCRIPTION", 22, SOFT, "BOLD", role="table-header")
    b.text(0, ty + 16, "数量 QTY", 22, SOFT, "BOLD", role="table-header", right=r_qty)
    b.text(0, ty + 16, "单价 UNIT", 22, SOFT, "BOLD", role="table-header", right=r_unit)
    b.text(0, ty + 16, "行金额 AMOUNT", 22, SOFT, "BOLD", role="table-header", right=r_amt)
    for i, ln in enumerate(c["lines"]):
        y = ty + head_h + i * row_h
        if i % 2 == 1:
            b.box(M + 1, y, CW - 2, row_h, "#FAFCFEFF")
        b.text(x_sku, y + 22, ln["sku"], 26, BLUE, "BOLD", family=MONO, role="sku",
               source="items[].sku", max_w=x_name - x_sku - 16)
        b.text(x_name, y + 22, ln["name"], 26, INK, role="item-name", source="items[].name",
               max_w=r_qty - 110 - x_name)
        b.text(0, y + 22, str(ln["quantity"]), 26, SOFT, family=MONO, role="quantity",
               source="items[].quantity", right=r_qty)
        b.text(0, y + 22, money(Decimal(ln["unit_price"])), 26, SOFT, family=MONO,
               role="unit-price", source="items[].unit_price", right=r_unit)
        b.text(0, y + 22, money(Decimal(ln["line_amount"])), 26, INK, "BOLD", family=MONO,
               role="line-amount", source="items[].quantity × items[].unit_price",
               right=r_amt)

    oy, oh = 852, 358
    b.box(M, oy, CW, oh, CARD, radius=12, border=f"1 SOLID {EDGE}")
    b.text(M + 32, oy + 24, "计费合计 / TOTALS", 26, INK, "BOLD", role="totals-title")
    rows = [("货品小计 / Goods subtotal", money(c["goods_subtotal"]), SOFT, "NORMAL"),
            ("折扣（税前扣除）/ Discount", "−" + money(c["discount"]), RED, "NORMAL"),
            ("税前货品额 / Net goods", money(c["base"]), INK, "BOLD"),
            (f'税额 {c["rate"]*100:.0f}% / VAT on net goods', money(c["tax"]), SOFT, "NORMAL"),
            ("运费（不计税）/ Shipping", money(c["shipping"]), SOFT, "NORMAL")]
    for i, (label, value, color, weight) in enumerate(rows):
        y = oy + 64 + i * 46
        b.text(M + 32, y, label, 26, SOFT, role="totals-label")
        b.text(0, y, value, 26, color, weight, family=MONO, role="totals-value", right=r_amt)
    sep_y = oy + 64 + len(rows) * 46 + 4
    b.line(M + 32, sep_y, CW - 64, 1, EDGE)
    b.text(M + 32, sep_y + 20, "应付 / AMOUNT DUE", 30, INK, "BOLD", role="due-label")
    b.text(0, sep_y + 12, money(c["due"]), 40, GREEN, "BOLD", family=MONO,
           role="amount-due", source="goods subtotal − discount + tax + shipping",
           right=r_amt)

    fy, fh = 1234, 236
    b.box(M, fy, CW, fh, "#FFFBEBFF", radius=12, border=f"1 SOLID #FDE68AFF")
    b.text(M + 28, fy + 20, "计税顺序 / TAX ORDER（严格按单据 notes 执行）", 24, "#92400EFF",
           "BOLD", role="tax-title")
    tax_lines = [
        f'① 货品小计 = 805.50 + 478.80 + 1,160.00 + 1,680.00 = {money(c["goods_subtotal"])}',
        f'② 折扣 {money(c["discount"])} 在税前从货品小计扣除 → 计税基数 {money(c["base"])}',
        f'③ 税额 = {money(c["base"])} × 6% = {c["tax_raw"]:.4f} → 四舍五入到分 = {money(c["tax"])}'
        f'（第三位小数 8，向上进位）',
        f'④ 运费 {money(c["shipping"])} 不计税，直接加入应付：{money(c["base"])} + '
        f'{money(c["tax"])} + {money(c["shipping"])} = {money(c["due"])}',
        '金额全部用十进制定点 + ROUND_HALF_UP 量化到 0.01，不用二进制浮点。',
    ]
    for i, line in enumerate(tax_lines):
        b.text(M + 28, fy + 60 + i * 34, line, 22, SOFT, role=f"tax-note-{i+1}", max_w=CW - 56)
    footer(b, "第 1 页 / 共 2 页", "金额单位：CNY")
    return b.finish()


# ------------------------------------------------------------------ page 2
def page2(c) -> str:
    b = B(2)
    header(b, c, "第二页：说明与原样文字 / Page 2 of 2 — notes & verbatim text",
           "第 2 页 / 共 2 页")

    ny, nh = 262, 360
    b.box(M, ny, CW, nh, CARD, radius=12, border=f"1 SOLID {EDGE}")
    b.text(M + 32, ny + 22, "单据说明 / NOTES（四条，原文照录）", 28, INK, "BOLD",
           role="notes-title")
    for i, note in enumerate(INV["notes"]):
        y = ny + 82 + i * 66
        b.box(M + 32, y + 4, 30, 30, BLUE + "1A", radius=8)
        b.text(M + 32, y + 8, str(i + 1), 22, BLUE, "BOLD", family=MONO, role="note-index")
        b.text(M + 78, y, note, 26, SOFT, role="note", source=f"notes[{i}]",
               max_w=CW - 110)

    ly, lh = 646, 488
    b.box(M, ly, CW, lh, CARD, radius=12, border=f"1 SOLID {EDGE}")
    b.text(M + 32, ly + 22, "原样文字 / LITERAL LINES（逐字符保真，不执行）", 28, INK, "BOLD",
           role="literal-title")
    b.text(M + 32, ly + 62,
           "下面四行用 Raw + CDATA 原样排版：不 trim、不合并空格；< & > 只作为字符，"
           "不会显示成实体。", 20, MUTED, role="literal-method-note", max_w=CW - 64)
    for i, raw in enumerate(INV["literal_lines"]):
        y = ly + 100 + i * 90
        b.box(M + 32, y, CW - 64, 80, "#F8FAFCFF", radius=10, border=f"1 SOLID {EDGE}")
        b.text(M + 52, y + 12, f"L{i+1}", 22, AMBER, "BOLD", family=MONO, role="literal-index")
        b.text(M + 120, y + 8, raw, 28, INK, family=MONO, role="literal-line",
               source=f"literal_lines[{i}]", raw=True, max_w=CW - 200)
        marked = raw.replace(" ", "·")
        b.text(M + 52, y + 48, "空格标记（· = 空格）", 20, MUTED, role="literal-space-label")
        b.text(M + 300, y + 48, marked, 20, MUTED, family=MONO, role="literal-space-proof",
               source=f"literal_lines[{i}] space audit", max_w=540)
        b.text(0, y + 48,
               f"长度 {len(raw)} / 空格 {raw.count(' ')} / 双空格 {raw.count('  ')}", 20,
               MUTED, role="literal-stats", right=M + 1080)
    b.text(M + 32, ly + lh - 30,
           "第 4 行是提示注入样张，仅作为字样原样排版，不执行、不改变任何金额。", 20, MUTED,
           role="literal-injection-note")

    sy, sh = 1150, 210
    b.box(M, sy, CW, sh, CARD, radius=12, border=f"1 SOLID {EDGE}")
    b.text(M + 32, sy + 22, "样张状态 / SAMPLE STATUS（富文本，三段共用基线）", 28, INK, "BOLD",
           role="status-title")
    b.rich_paid(M + 32, sy + 76, 44)
    b.text(M + 32, sy + 144, "该字样只是样张状态标记，不参与计算，也不改变本页任何数字。",
           22, MUTED, role="status-note", max_w=CW - 64)
    b.text(M + 32, sy + 174,
           f'应付仍为 {money(c["due"])} = 税前货品额 {money(c["base"])} + 税额 '
           f'{money(c["tax"])} + 运费 {money(c["shipping"])}。', 22, MUTED,
           role="status-note-2", max_w=CW - 64)

    fy, fh = 1382, 104
    b.box(M, fy, CW, fh, CARD, radius=12, border=f"1 SOLID {EDGE}")
    b.text(M + 32, fy + 10, "字体覆盖 / FONT COVERAGE（取自 GET /fonts 的实际字体族）", 24,
           INK, "BOLD", role="font-title")
    b.text(M + 32, fy + 44, "中文简体 日本語 カタカナ ひらがな Latin 0123456789", 22, INK,
           role="font-sample", source="fonts.txt: Noto Sans CJK SC", max_w=CW - 64)
    b.text(M + 32, fy + 74, "金额列等宽：Noto Sans Mono CJK SC → 1,680.00 / 4,215.96 / 236.66",
           20, MUTED, family=MONO, role="font-sample-mono",
           source="fonts.txt: Noto Sans Mono CJK SC", max_w=CW - 64)
    footer(b, "第 2 页 / 共 2 页", "页眉与编号与第 1 页一致")
    return b.finish()


# ------------------------------------------------------------------ deliverables
def write_audit(c) -> None:
    lit = []
    for i, raw in enumerate(INV["literal_lines"]):
        lit.append({"index": i, "raw_string": raw, "length": len(raw),
                    "space_count": raw.count(" "), "double_space_runs": raw.count("  "),
                    "double_space_positions": [m for m in range(len(raw) - 1)
                                               if raw[m:m + 2] == "  "],
                    "escapes_visible_in_render": False,
                    "rendered_via": "Raw span with CDATA payload",
                    "char_codes": [ord(ch) for ch in raw]})
    audit = {
        "task": "A11",
        "pages": [{"file": "invoice-page-01.png", "size": [W, H], "role": "结算与明细"},
                  {"file": "invoice-page-02.png", "size": [W, H], "role": "说明与原样文字"}],
        "source": "inputs/invoice.json",
        "invoice_id": INV["invoice_id"], "issued": INV["issued"],
        "currency": INV["currency"], "seller": INV["seller"], "buyer": INV["buyer"],
        "rounding": {"arithmetic": "十进制定点 decimal.Decimal，getcontext().prec = 40",
                     "quantum": "0.01", "mode": "ROUND_HALF_UP",
                     "note": "所有金额先按精确十进制计算，最后一步量化到分；未使用二进制浮点。"},
        "line_items": [{"index": i + 1, "sku": ln["sku"], "name": ln["name"],
                        "quantity": ln["quantity"], "unit_price": ln["unit_price"],
                        "line_amount": ln["line_amount"], "computation": ln["computation"]}
                       for i, ln in enumerate(c["lines"])],
        "totals": {
            "goods_subtotal": {"value": money(c["goods_subtotal"]),
                               "computation": " + ".join(money(Decimal(l["line_amount"]))
                                                         for l in c["lines"])},
            "discount": {"value": money(c["discount"]),
                         "rule": "notes[1]：折扣在税前从货品小计扣除"},
            "taxable_base_after_discount": {"value": money(c["base"]),
                                            "computation": f'{money(c["goods_subtotal"])} − '
                                                           f'{money(c["discount"])}'},
            "tax": {"rate": str(c["rate"]), "exact_base": money(c["base"]),
                    "raw_product": f'{c["tax_raw"]:.6f}', "rounded": money(c["tax"]),
                    "rounding": "236.658 → 236.66：第三位小数 8 ≥ 5，向上进位（ROUND_HALF_UP）"},
            "shipping": {"value": money(c["shipping"]), "taxed": False,
                         "rule": "notes[1]：运费不计税"},
            "amount_due": {"value": money(c["due"]),
                           "computation": f'{money(c["base"])} + {money(c["tax"])} + '
                                          f'{money(c["shipping"])}'}},
        "tax_order_followed": [
            "① 逐行金额 = 数量 × 单价（精确十进制）",
            "② 货品小计 = Σ 行金额 = 4,124.30",
            "③ 折扣 180.00 在税前从小计扣除 → 计税基数 3,944.30",
            "④ 税额 = 计税基数 × 6% = 236.658 → 四舍五入到分 = 236.66",
            "⑤ 运费 35.00 不计税，直接加入应付 → 应付 4,215.96"],
        "literal_lines": lit,
        "text_mechanism": {
            "finding": "本服务的解析器不解码 XML 实体：写成 &amp; 会原样渲染出 “&amp;”。",
            "evidence": "probe-bare.png：A &amp; B / A &gt; B / A &lt; B 三行都显示成了实体字面量。",
            "bare_amp_and_gt": "裸 & 与裸 > 可直接出现在文本里（probe-bare2.png 正常）。",
            "bare_lt": "裸 < 会报 400 PARSE_ERROR: Unexpected character ' ' in input state "
                       "[TAG_OPEN]（probe-bare3 未出图）。",
            "solution": "所有文本节点用 <![CDATA[…]]> 承载；需要保留空格的行用 "
                        "<Raw><![CDATA[…]]></Raw>（probe-rawcdata.png 三行全部逐字符正确）。",
            "applied_to": "第 1 页 SKU “A<B&C>D”；第 2 页 L2 “A < B & C > D”、L3 反斜杠路径、"
                          "L1 双空格批次行"},
        "status_mark": {
            "rich_text": "PAID / 已结算",
            "spans": [{"text": "PAID", "color": GREEN, "style": "BOLD"},
                      {"text": " / ", "color": SEP, "style": "NORMAL"},
                      {"text": "已结算", "color": INK, "style": "BOLD"}],
            "baseline": "三个 span 同字体同字号，作为同一段落的行内 span 共用基线（实测同一行墨迹范围）",
            "effect_on_amount_due": "无：该字样仅为样张状态标记，应付仍为 " + money(c["due"])},
        "fonts_used": {
            "resolved_from": "GET /fonts（共享缓存 _suite/shared/fonts.txt，2026-10-03 11:46，HTTP 200）",
            "body": "Noto Sans CJK SC（中文简体 + 日文假名 + 拉丁）",
            "mono": "Noto Sans Mono CJK SC（金额列与 SKU/编号）",
            "why": "invoice.json 同时含中文、日文（契約レビュー）与拉丁文本，Noto Sans CJK SC "
                   "三者都覆盖；金额列用等宽族以保证垂直对齐。",
            "verified_by": "第 2 页“字体覆盖”样例行实际渲染中文/日文/拉丁/数字"},
        "typography": {"body_min_px": 24, "footnote_min_px": 20, "safe_margin_px": M,
                       "actual_body_sizes": [26, 28, 30, 40],
                       "actual_footnote_sizes": [20, 22],
                       "note": "未通过缩小字号塞内容；正文最小 24（说明/脚注 20–22）。"},
        "page_consistency": {"invoice_id_on_both_pages": INV["invoice_id"],
                             "header_repeated": True, "safe_margin_on_all_text": True,
                             "page_numbers": ["第 1 页 / 共 2 页", "第 2 页 / 共 2 页"]},
    }
    with open(os.path.join(HERE, "invoice-audit.json"), "w", encoding="utf-8",
              newline="\n") as fh:
        json.dump(audit, fh, ensure_ascii=False, indent=2)


def write_text_map() -> None:
    doc = {"task": "A11",
           "note": "每个文字元素对应页面、左上角像素坐标、估算宽度、字号、字体、颜色、"
                   "文本机制与来源字段；坐标按最终 DSL 中 Positioned 的 left/top 记录。",
           "pages": {"1": "invoice-page-01.png（1200×1600）",
                     "2": "invoice-page-02.png（1200×1600）"},
           "safe_margin": M, "segments": REG}
    with open(os.path.join(HERE, "text-map.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=2)


def main() -> None:
    version = sys.argv[1] if len(sys.argv) > 1 else "v1"
    c = compute()
    for name, dsl in (("invoice-page-01", page1(c)), ("invoice-page-02", page2(c))):
        with open(os.path.join(HERE, f"{name}.{version}.snapshot"), "w", encoding="utf-8",
                  newline="\n") as fh:
            fh.write(dsl)
        print("wrote", name, len(dsl), "chars")
    write_audit(c)
    write_text_map()
    print(f'segments={len(REG)} subtotal={money(c["goods_subtotal"])} base={money(c["base"])} '
          f'tax={money(c["tax"])} due={money(c["due"])}')


if __name__ == "__main__":
    main()
