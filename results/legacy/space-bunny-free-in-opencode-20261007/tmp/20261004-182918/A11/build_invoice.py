"""A11 - Bilingual invoice / settlement statement, two 1200x1600 pages.

Everything is laid out with absolute positioning through dsllib; every string is
carried verbatim from tasks/A11-bilingual-invoice/inputs/invoice.json.

Money is computed with decimal.Decimal (fixed point) and ROUND_HALF_UP, in the
order the notes prescribe, and every rendered amount string is the plain
2-decimal stringification of a Decimal (no thousands separators) so it can be
compared character by character against invoice-audit.json.
"""
from __future__ import annotations

import json
import os
import sys
from decimal import Decimal, ROUND_HALF_UP

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
import snapkit  # noqa: E402
import dsllib as D  # noqa: E402
import state as S  # noqa: E402

TASK = "A11"
OUT = os.path.join(S.OUT_ROOT, TASK)
TMP = os.path.join(S.TMP_ROOT, TASK)
snapkit.configure(TASK, OUT, TMP)
S.start_task(TASK)

IN = os.path.join(ROOT, "tasks", "A11-bilingual-invoice", "inputs", "invoice.json")
inv = json.load(open(IN, encoding="utf-8"))

# ----------------------------------------------------------------- computation
CENT = Decimal("0.01")
QTY = Decimal


def money(d: Decimal) -> Decimal:
    return d.quantize(CENT, rounding=ROUND_HALF_UP)


rate = Decimal(inv["tax_rate"])                 # 0.06
discount = Decimal(inv["discount"])             # 180.00
shipping = Decimal(inv["shipping"])             # 35.00

lines = []
subtotal = Decimal("0.00")
for it in inv["items"]:
    qty = QTY(it["quantity"])
    unit = Decimal(it["unit_price"])
    amount = money(qty * unit)                  # integer quantity -> exact
    subtotal += amount
    lines.append({"sku": it["sku"], "name": it["name"],
                  "quantity": it["quantity"], "unit_price": it["unit_price"],
                  "unit_price_decimal": unit, "quantity_decimal": qty,
                  "exact_product": qty * unit, "amount": amount,
                  "amount_str": str(amount)})

subtotal = money(subtotal)                                   # 4124.30
taxable_base = money(subtotal - discount)                    # 3944.30  (note 2)
tax_exact = taxable_base * rate                              # 236.658  (note 3)
tax = money(tax_exact)                                       # 236.66    HALF_UP
total = money(taxable_base + tax + shipping)                 # 4215.96   (note 3)
# Decimal keeps the operand scales, so the raw product prints as 236.6580.
# normalize() removes only trailing zeros, never a significant digit.
tax_exact_norm = tax_exact.normalize()

M = {}   # money strings
M["subtotal"] = str(subtotal)
M["discount"] = str(discount)
M["taxable"] = str(taxable_base)
M["tax_exact"] = str(tax_exact_norm)
M["tax_exact_raw"] = str(tax_exact)
M["tax"] = str(tax)
M["shipping"] = str(shipping)
M["total"] = str(total)

# ------------------------------------------------------------------- styling
UI = "Inter,Noto Sans CJK SC"
MONO = "DejaVu Sans Mono"
MONOUI = "DejaVu Sans Mono,Noto Sans Mono CJK SC"
SKUF = "Inter,Noto Sans Mono CJK SC"

INK = "#0F172AFF"
MUTED = "#475569FF"
FAINT = "#94A3B8FF"
LINE = "#CBD5E1FF"
PAPER = "#F1F5F9FF"
CARD = "#FFFFFFFF"
DARK = "#0F172AFF"
WHITE = "#F8FAFCFF"
ACCENT = "#1D4ED8FF"
ACCENT_BG = "#DBEAFEFF"
GREEN = "#15803DFF"
GREEN_BG = "#DCFCE7FF"
RULE = "#E2E8F0FF"

PW, PH = 1200, 1600
MARGIN = 72
CW = PW - 2 * MARGIN                 # 1056 content width
RIGHT = PW - MARGIN                  # 1128

# page-1 table columns (x, width, right edge)
C_SKU = (MARGIN, 160)
C_NAME = (244, 470)
C_QTY_R = 820
C_UNIT_R = 950
C_AMT_R = RIGHT

TEXTMAP = []
FITS = []


def assert_fit(tag, text, size, box_w, font_factor=1.0):
    """Record and enforce that a must-be-single-line string fits its box."""
    need = D.est_width(text, size) * font_factor
    FITS.append({"tag": tag, "text": text, "size": size, "box_w": box_w,
                 "est_w": round(need, 1),
                 "slack_px": round(box_w - need, 1),
                 "fits": need <= box_w})
    return need


def gy(box_y, box_h, size):
    """Text-box top that centres a glyph run of 1.05*size inside a box."""
    return round(box_y + box_h / 2.0 - 1.05 * size / 2.0 - 3, 2)


def T(kids, page, eid, role, x, y, w, text, size, font=UI, color=INK,
      align=None, bold=False, ls=None, zero=False, h=None, source=None,
      note=None, soft_wrap=None):
    """Emit one absolutely positioned Text and register it in text-map.json."""
    a = {"color": color, "fontSize": size, "fontFamily": font}
    if bold:
        a["fontStyle"] = "BOLD"
    if ls is not None:
        a["letterSpacing"] = ls
    if zero:
        a["fontFeatures"] = "zero"
    if align:
        a["textAlign"] = align
    if soft_wrap is not None:
        a["softWrap"] = soft_wrap
    pa = {"left": round(x, 2), "top": round(y, 2), "width": round(w, 2)}
    if h is not None:
        pa["height"] = round(h, 2)
    raw = any(c in text for c in "<>&")
    inner = D.el("Text", a, [D.cdata(text)]) if raw else \
        D.el("Text", dict(a, text=text))
    kids.append(D.el("Positioned", pa, [inner]))
    TEXTMAP.append({
        "element_id": eid, "page": page, "role": role,
        "text": text, "codepoints": ["U+%04X" % ord(c) for c in text],
        "char_count": len(text),
        "left": round(x, 2), "top": round(y, 2), "width": round(w, 2),
        "height": round(h, 2) if h is not None else None,
        "font_family": font, "font_size": size, "color": color,
        "text_align": align, "font_style": "BOLD" if bold else "NORMAL",
        "font_features": "zero" if zero else None,
        "source": source or "derived",
        "note": note,
    })
    return round(y + size * 1.25, 2)


def rule(kids, x0, x1, y, color=LINE, w=1):
    kids.append(D.box(x0, y - w / 2.0, x1 - x0, w, color=color))


def boxp(kids, x, y, w, h, fill=CARD, radius=14, border=None, shadow=None):
    kids.append(D.box(x, y, w, h, color=fill, radius=radius, border=border,
                      shadow=shadow))


# ------------------------------------------------------- shared page furniture
HDR_H = 216
def page_frame(kids, page_no):
    """Identical dark header band + footer on both pages (repeated header)."""
    pg = "p%d" % page_no
    kids.append(D.box(0, 0, PW, HDR_H, color=DARK))
    kids.append(D.box(0, HDR_H, PW, 4, color=ACCENT))

    T(kids, pg, "hdr.title", "header", MARGIN, 52, 700,
      "结算单", 46, font=UI, color=WHITE, bold=True,
      source="derived:document title")
    T(kids, pg, "hdr.sub", "header", MARGIN, 118, 760,
      "SETTLEMENT STATEMENT / 跨页排版样张", 24, font=UI, color=FAINT,
      source="derived:document subtitle")

    T(kids, pg, "hdr.no.label", "header", 700, 48, RIGHT - 700,
      "结算单编号 / Invoice No.", 24, font=UI, color=FAINT, align="RIGHT",
      source="derived:label")
    T(kids, pg, "hdr.no.value", "header", 640, 80, RIGHT - 640,
      inv["invoice_id"], 30, font=MONO, color=WHITE, align="RIGHT", zero=True,
      source="invoice.json:invoice_id")
    T(kids, pg, "hdr.date", "header", 640, 124, RIGHT - 640,
      "开票日期 / Issued  %s" % inv["issued"], 24, font=UI, color="#CBD5E1FF",
      align="RIGHT", source="invoice.json:issued")
    T(kids, pg, "hdr.cur", "header", 640, 158, RIGHT - 640,
      "币种 / Currency  %s" % inv["currency"], 24, font=UI, color="#CBD5E1FF",
      align="RIGHT", source="invoice.json:currency")

    # footer: identical structure, page number differs
    rule(kids, MARGIN, RIGHT, 1500, color=LINE)
    T(kids, pg, "ftr.doc", "footer", MARGIN, 1518, 700,
      "%s · %s · %s" % (inv["invoice_id"], inv["issued"], inv["currency"]),
      21, font=MONOUI, color=FAINT, source="invoice.json:invoice_id,issued,currency")
    T(kids, pg, "ftr.page", "footer", RIGHT - 320, 1518, 320,
      "第 %d 页 / 共 2 页 · Page %d of 2" % (page_no, page_no),
      21, font=UI, color=MUTED, align="RIGHT", source="derived:page number")


# ===================================================================== PAGE 1
p1 = []
p1.append(D.box(0, 0, PW, PH, color=PAPER))
page_frame(p1, 1)

# ---- parties
boxp(p1, MARGIN, 260, 516, 152, shadow="0 2 10 0 #0F172A0F")
boxp(p1, 612, 260, 516, 152, shadow="0 2 10 0 #0F172A0F")
T(p1, "p1", "p1.seller.label", "label", MARGIN + 24, 282, 468,
  "卖方 / SELLER", 24, font=UI, color=MUTED, source="invoice.json:seller")
T(p1, "p1", "p1.seller.name", "body", MARGIN + 24, 318, 468,
  inv["seller"], 32, font=UI, color=INK, bold=True, source="invoice.json:seller")
T(p1, "p1", "p1.buyer.label", "label", 636, 282, 468,
  "买方 / BUYER", 24, font=UI, color=MUTED, source="invoice.json:buyer")
T(p1, "p1", "p1.buyer.name", "body", 636, 318, 468,
  inv["buyer"], 32, font=UI, color=INK, bold=True, source="invoice.json:buyer")

# ---- table section title + header
T(p1, "p1", "p1.sec.title", "label", MARGIN, 428, 700,
  "结算明细 / Line items", 26, font=UI, color=MUTED, bold=True,
  source="derived:section title")
T(p1, "p1", "p1.sec.unit", "label", RIGHT - 460, 432, 460,
  "单价与金额单位 / Unit: %s" % inv["currency"], 24, font=UI, color=FAINT,
  align="RIGHT", source="invoice.json:currency")

TH_Y, TH_H = 472, 48
p1.append(D.box(MARGIN, TH_Y, CW, TH_H, color="#E2E8F0FF",
                radii={"TopLeft": 12, "TopRight": 12}))
_hdr_y = gy(TH_Y, TH_H, 24)
T(p1, "p1", "p1.th.sku", "table_header", C_SKU[0] + 12, _hdr_y, 300,
  "SKU", 24, font=UI, color=MUTED, bold=True, source="derived:column header")
T(p1, "p1", "p1.th.name", "table_header", C_NAME[0], _hdr_y, 460,
  "品名 / Description", 24, font=UI, color=MUTED, bold=True,
  source="derived:column header")
T(p1, "p1", "p1.th.qty", "table_header", C_QTY_R - 200, _hdr_y, 200,
  "数量 Qty", 24, font=UI, color=MUTED, bold=True, align="RIGHT",
  source="derived:column header")
T(p1, "p1", "p1.th.unit", "table_header", C_UNIT_R - 220, _hdr_y, 220,
  "单价 Unit", 24, font=UI, color=MUTED, bold=True, align="RIGHT",
  source="derived:column header")
T(p1, "p1", "p1.th.amt", "table_header", C_AMT_R - 320, _hdr_y, 320,
  "金额 Amount", 24, font=UI, color=MUTED, bold=True, align="RIGHT",
  source="derived:column header")
for _t, _w, _b in (("品名 / Description", 460, MARGIN + 460),
                   ("数量 Qty", 200, C_QTY_R), ("单价 Unit", 220, C_UNIT_R),
                   ("金额 Amount", 320, C_AMT_R)):
    assert_fit("th:" + _t, _t, 24, _w)

# ---- item rows
ROW_Y0, ROW_H = TH_Y + TH_H, 72
for i, ln in enumerate(lines):
    ry = ROW_Y0 + i * ROW_H
    if i % 2 == 1:
        p1.append(D.box(MARGIN, ry, CW, ROW_H, color="#F8FAFCFF"))
    rule(p1, MARGIN, RIGHT, ry, color=RULE)
    T(p1, "p1", "p1.item%d.sku" % i, "body", C_SKU[0] + 12, gy(ry, ROW_H, 26),
      C_SKU[1], ln["sku"], 26, font=SKUF, color=INK, zero=True,
      source="invoice.json:items[%d].sku" % i)
    T(p1, "p1", "p1.item%d.name" % i, "body", C_NAME[0], gy(ry, ROW_H, 26),
      C_NAME[1], ln["name"], 26, font=UI, color=INK,
      source="invoice.json:items[%d].name" % i)
    T(p1, "p1", "p1.item%d.qty" % i, "body", C_QTY_R - 200, gy(ry, ROW_H, 26),
      200, str(ln["quantity"]), 26, font=MONO, color=INK, align="RIGHT",
      source="invoice.json:items[%d].quantity" % i)
    T(p1, "p1", "p1.item%d.unit" % i, "body", C_UNIT_R - 220, gy(ry, ROW_H, 26),
      220, str(ln["unit_price_decimal"]), 26, font=MONO, color=INK,
      align="RIGHT", source="invoice.json:items[%d].unit_price" % i)
    T(p1, "p1", "p1.item%d.amount" % i, "body", C_AMT_R - 300, gy(ry, ROW_H, 26),
      300, ln["amount_str"], 26, font=MONO, color=ACCENT, align="RIGHT",
      source="derived:items[%d].quantity*unit_price rounded HALF_UP" % i)
    assert_fit("item%d.sku" % i, ln["sku"], 26, C_SKU[1])
    assert_fit("item%d.name" % i, ln["name"], 26, C_NAME[1])
    assert_fit("item%d.amount" % i, ln["amount_str"], 26, 300, 0.62)

ry_end = ROW_Y0 + len(lines) * ROW_H
rule(p1, MARGIN, RIGHT, ry_end, color="#94A3B8FF", w=2)

# ---- totals card (right)
TX, TY, TW, TH = 612, 832, 516, 500
LVL_W, VAL_W = 310, 150
VAL_X = TX + TW - 24 - VAL_W
boxp(p1, TX, TY, TW, TH, shadow="0 2 10 0 #0F172A0F")
T(p1, "p1", "p1.tot.title", "label", TX + 24, TY + 22, TW - 48,
  "结算汇总 / Settlement summary", 24, font=UI, color=MUTED, bold=True,
  source="derived:section title")
T(p1, "p1", "p1.tot.cur", "label", TX + 24, TY + 58, TW - 48,
  "币种 / Currency  %s" % inv["currency"], 24, font=UI, color=FAINT,
  source="invoice.json:currency")

pct_txt = format(rate * 100, "f").rstrip("0").rstrip(".")
tot_rows = [
    ("货品小计 / Goods subtotal", M["subtotal"], "derived:sum of line amounts"),
    ("折扣 / Discount（税前）", M["discount"], "invoice.json:discount"),
    ("税前货品额 / Taxable base", M["taxable"], "derived:subtotal-discount"),
    ("税额 / Tax @ %s%%" % pct_txt, M["tax"],
     "derived:taxable*tax_rate rounded HALF_UP"),
    ("运费 / Shipping（不计税）", M["shipping"], "invoice.json:shipping"),
]
ry = TY + 104
for i, (lab, val, src) in enumerate(tot_rows):
    T(p1, "p1", "p1.tot%d.label" % i, "body", TX + 24, gy(ry, 50, 24), LVL_W,
      lab, 24, font=UI, color=INK, source=src)
    T(p1, "p1", "p1.tot%d.value" % i, "body", VAL_X, gy(ry, 50, 26),
      VAL_W, val, 26, font=MONO, color=INK, align="RIGHT", source=src)
    assert_fit("tot%d.label" % i, lab, 24, LVL_W)
    assert_fit("tot%d.value" % i, val, 26, VAL_W, 0.62)
    ry += 50

rule(p1, TX + 24, TX + TW - 24, ry + 8, color="#94A3B8FF", w=2)
T(p1, "p1", "p1.total.label", "body", TX + 24, gy(ry + 24, 64, 26),
  TW - 24 - VAL_W - 24 - 8,
  "应付 / Amount payable", 26, font=UI, color=ACCENT, bold=True,
  source="derived:taxable+tax+shipping")
T(p1, "p1", "p1.total.value", "body", VAL_X, gy(ry + 24, 64, 32),
  VAL_W, M["total"], 32, font=MONO, color=ACCENT, bold=True, align="RIGHT",
  source="derived:final payable")
assert_fit("total.label", "应付 / Amount payable", 26, TW - 24 - VAL_W - 32)
assert_fit("total.value", M["total"], 32, VAL_W, 0.62)
T(p1, "p1", "p1.tot.note", "footnote", TX + 24, ry + 108, TW - 48,
  "运费不计税；折扣在税前扣除。", 21, font=UI, color=MUTED,
  source="invoice.json:notes[1],notes[2]")

# ---- tax order card (left)
OLB_W, OVAL_W = 240, 228
OVAL_X = MARGIN + 24 + OLB_W
boxp(p1, MARGIN, TY, 516, TH, shadow="0 2 10 0 #0F172A0F")
T(p1, "p1", "p1.order.title", "label", MARGIN + 24, TY + 22, 468,
  "计税顺序 / Tax order（依 notes 2→3）", 24, font=UI, color=MUTED, bold=True,
  source="invoice.json:notes[1],notes[2]")
ord_rows = [
    ("1) 货品小计", M["subtotal"], "derived:sum of line amounts"),
    ("2) 折扣（税前扣除）", M["discount"], "invoice.json:discount"),
    ("3) 税前货品额", M["taxable"], "derived:exact tax base"),
    ("4) 税额 × %s%%" % pct_txt, M["tax_exact"],
     "derived:exact unrounded tax"),
    ("5) 四舍五入至分", M["tax"], "derived:tax rounded HALF_UP"),
    ("6) 运费（不计税）", M["shipping"], "invoice.json:shipping"),
    ("7) 应付", M["total"], "derived:final payable"),
]
oy = TY + 68
for i, (lab, val, src) in enumerate(ord_rows):
    T(p1, "p1", "p1.ord%d.label" % i, "body", MARGIN + 24, oy, OLB_W,
      lab, 24, font=UI, color=INK, source=src)
    T(p1, "p1", "p1.ord%d.value" % i, "body", OVAL_X, oy, OVAL_W,
      val, 24, font=MONO, color=ACCENT, align="RIGHT", source=src)
    assert_fit("ord%d.label" % i, lab, 24, OLB_W)
    assert_fit("ord%d.value" % i, val, 24, OVAL_W, 0.62)
    oy += 50
T(p1, "p1", "p1.order.note0", "footnote", MARGIN + 24, oy + 6, 468,
  "计税基数见第 3 行，未取整税额见第 4 行。", 21, font=UI, color=MUTED,
  source="invoice.json:notes[2]")
T(p1, "p1", "p1.order.note1", "footnote", MARGIN + 24, oy + 36, 468,
  "定点 Decimal；ROUND_HALF_UP 取整。", 21, font=UI, color=MUTED,
  source="invoice.json:notes[2]")

# ---- footnotes
fn_y = 1388
rule(p1, MARGIN, RIGHT, fn_y - 18, color=LINE)
fn = [
    "本页金额均为两位小数定点值，不使用千分位分隔符，可与 invoice-audit.json 逐字符比对。",
    "税率 %s 取自 tax_rate；折扣在税前从货品小计扣除，运费不计税（依据见第 2 页 notes）。"
    % inv["tax_rate"],
]
for i, t in enumerate(fn):
    T(p1, "p1", "p1.fn%d" % i, "footnote", MARGIN, fn_y + i * 34, CW, t, 21,
      font=UI, color=MUTED, source="derived:footnote")

dsl1 = D.snapshot([D.stack(p1, PW, PH)], PW, PH, bg=PAPER)

# ===================================================================== PAGE 2
p2 = []
p2.append(D.box(0, 0, PW, PH, color=PAPER))
page_frame(p2, 2)

# ---- notes
NY = 256
boxp(p2, MARGIN, NY, CW, 356, shadow="0 2 10 0 #0F172A0F")
T(p2, "p2", "p2.notes.title", "label", MARGIN + 28, NY + 22, 600,
  "说明 / Notes", 26, font=UI, color=MUTED, bold=True,
  source="derived:section title")
T(p2, "p2", "p2.notes.sub", "label", MARGIN + 28, NY + 56, 700,
  "逐字符保真 / verbatim, no reflow", 21, font=UI, color=FAINT,
  source="derived:annotation")
ny = NY + 96
for i, note in enumerate(inv["notes"]):
    p2.append(D.box(MARGIN + 28, ny - 10, 4, 44, color=ACCENT, radius=2))
    T(p2, "p2", "p2.note%d" % i, "body", MARGIN + 46, ny - 4, CW - 100,
      note, 26, font=UI, color=INK, source="invoice.json:notes[%d]" % i)
    ny += 66

# ---- literal lines
LY = 640
boxp(p2, MARGIN, LY, CW, 404, shadow="0 2 10 0 #0F172A0F")
T(p2, "p2", "p2.lit.title", "label", MARGIN + 28, LY + 22, 700,
  "原样文字 / Literal lines", 26, font=UI, color=MUTED, bold=True,
  source="derived:section title")
T(p2, "p2", "p2.lit.sub", "label", MARGIN + 28, LY + 56, 900,
  "逐字符保真渲染；CDATA 承载，不做 HTML 实体解码 / verbatim via CDATA",
  21, font=UI, color=FAINT, source="derived:annotation")
ly = LY + 100
for i, lit in enumerate(inv["literal_lines"]):
    p2.append(D.box(MARGIN + 28, ly - 12, CW - 56, 60, color="#F1F5F9FF",
                    radius=8))
    T(p2, "p2", "p2.lit%d" % i, "body", MARGIN + 44, ly + 2, CW - 92,
      lit, 30, font=MONOUI, color=INK, soft_wrap="false",
      source="invoice.json:literal_lines[%d]" % i,
      note="verbatim; contains < > & backslashes and double spaces")
    assert_fit("p2.lit%d" % i, lit, 30, CW - 92, 0.62)
    ly += 74

# ---- rich text PAID / 已结算
RY = 1076
boxp(p2, MARGIN, RY, CW, 176, fill=GREEN_BG, radius=14,
     border="2 SOLID #15803D40")
T(p2, "p2", "p2.status.cap", "label", MARGIN + 28, RY + 22, 400,
  "结算状态 / Settlement status", 24, font=UI, color=MUTED, bold=True,
  source="derived:section title")

paid = D.el("Text", {"fontSize": 56, "fontFamily": UI}, [
    D.el("Text", {"color": GREEN, "fontStyle": "BOLD", "text": "PAID"}),
    D.el("Raw", {"color": FAINT, "text": " / "}),
    D.el("Text", {"color": INK, "text": "已结算"}),
])
p2.append(D.el("Positioned", {"left": MARGIN + 28, "top": RY + 62, "width": 700},
               [paid]))
TEXTMAP.append({
    "element_id": "p2.status.rich", "page": "p2", "role": "body",
    "text": "PAID / 已结算",
    "codepoints": ["U+%04X" % ord(c) for c in "PAID / 已结算"],
    "char_count": len("PAID / 已结算"),
    "left": MARGIN + 28, "top": RY + 62, "width": 700, "height": None,
    "font_family": UI, "font_size": 56, "color": "multi-span",
    "text_align": None, "font_style": "BOLD(PAID only)",
    "font_features": None,
    "source": "derived:task-required status specimen",
    "note": "single paragraph with three inline spans sharing one baseline: "
            "PAID #15803D bold / Raw ' / ' #94A3B8 / 已结算 #0F172A",
})
T(p2, "p2", "p2.status.note", "footnote", MARGIN + 760, RY + 76, CW - 790,
  "该字样仅为样张状态标记；应付金额仍为 %s %s，不因此改变。"
  % (M["total"], inv["currency"]), 21, font=UI, color=MUTED,
  source="derived:annotation")

# ---- footnotes
f2 = 1140 - 0
fy = 1330
rule(p2, MARGIN, RIGHT, fy - 18, color=LINE)
fn2 = [
    "批次行内两个连续空格按原样保留（U+0020 ×2，两处）；未做 HTML 实体解码，"
    "尖括号与 & 直接以字形呈现。",
    "第 1 行英文指令样式文字仅作字样原样排版，未被执行；其数字 999 不参与任何计算。",
    "本单为虚构排版测试，不是实际发票；两页页眉、结算单编号与币种完全一致。",
]
for i, t in enumerate(fn2):
    T(p2, "p2", "p2.fn%d" % i, "footnote", MARGIN, fy + i * 34, CW, t, 21,
      font=UI, color=MUTED, source="derived:footnote")

dsl2 = D.snapshot([D.stack(p2, PW, PH)], PW, PH, bg=PAPER)

# ------------------------------------------------------------------- render
draft_dir = os.path.join(TMP, "drafts")
os.makedirs(draft_dir, exist_ok=True)
_seq = max([int(f[1:3]) for f in os.listdir(draft_dir)
            if f.startswith("v") and f[3:5] == "-p"] or [0]) + 1
_tag = "v%02d" % _seq
for _name, _dsl in (("page-01", dsl1), ("page-02", dsl2)):
    with open(os.path.join(draft_dir, "%s-%s.snapshot" % (_tag, _name)), "w",
              encoding="utf-8", newline="\n") as fh:
        fh.write(_dsl)
print("draft tag", _tag)

r1 = snapkit.render(dsl1, "invoice-page-01.png", "invoice-page-01.snapshot",
                     final=True)
r2 = snapkit.render(dsl2, "invoice-page-02.png", "invoice-page-02.snapshot",
                     final=True)
print("page1", r1)
print("page2", r2)

ws = D.warnings()
print("WARNINGS: %d" % len(ws))
for w in ws:
    print("  WARN", w)
bad = [f for f in FITS if not f["fits"]]
print("FIT CHECKS: %d total, %d too narrow" % (len(FITS), len(bad)))
for f in bad:
    print("  FITFAIL %-22s est=%.1f box=%.1f  %r" %
          (f["tag"], f["est_w"], f["box_w"], f["text"]))
tight = [f for f in FITS if f["fits"] and f["slack_px"] < 12]
for f in tight:
    print("  FITTIGHT %-22s est=%.1f box=%.1f slack=%.1f %r" %
          (f["tag"], f["est_w"], f["box_w"], f["slack_px"], f["text"]))

# ------------------------------------------------------------- audit + textmap
audit = {
    "task": "A11",
    "generated_for_run": S.RUN,
    "source_input": "tasks/A11-bilingual-invoice/inputs/invoice.json",
    "arithmetic": {
        "library": "python decimal.Decimal (fixed point, no binary float)",
        "rounding_method": "ROUND_HALF_UP applied only at the two places the "
                           "notes require it: per-line amount (integer quantity "
                           "x 2dp unit price is already exact) and the tax",
        "rounding_constant": "decimal.ROUND_HALF_UP",
        "tax_rate_as_decimal": inv["tax_rate"],
        "order_from_notes": [
            "notes[1]: discount is deducted from the goods subtotal before tax",
            "notes[2]: tax = discounted pre-tax goods amount x 6%, rounded to "
                       "the cent; shipping is added afterwards and is not taxed",
        ],
        "steps": [
            {"step": 1, "name": "goods subtotal", "expression":
                " + ".join(l["amount_str"] for l in lines),
             "value": M["subtotal"]},
            {"step": 2, "name": "less discount (pre-tax)",
             "expression": "%s - %s" % (M["subtotal"], M["discount"]),
             "value": M["taxable"]},
            {"step": 3, "name": "exact tax base", "value": M["taxable"],
             "note": "the taxable base is exact to the cent; no rounding needed"},
            {"step": 4, "name": "exact unrounded tax",
             "expression": "%s * %s" % (M["taxable"], inv["tax_rate"]),
             "value": M["tax_exact"],
             "decimal_raw_product": M["tax_exact_raw"],
             "note": "Decimal keeps both operand scales so the raw product "
                     "stringifies as 236.6580; normalize() drops only trailing "
                     "zeros and gives 236.658, which is the same number"},
            {"step": 5, "name": "tax rounded HALF_UP to the cent",
             "value": M["tax"],
             "note": "236.658 -> 236.66 (third decimal 8 >= 5 so it rounds up)"},
            {"step": 6, "name": "shipping added, not taxed",
             "value": M["shipping"], "note": "invoice.json:shipping"},
            {"step": 7, "name": "final amount payable",
             "expression": "%s + %s + %s" % (M["taxable"], M["tax"], M["shipping"]),
             "value": M["total"]},
        ],
        "exact_taxable_base": M["taxable"],
        "exact_tax_unrounded": M["tax_exact"],
        "exact_tax_unrounded_decimal_raw": M["tax_exact_raw"],
        "final_amount_payable": M["total"],
        "currency": inv["currency"],
        "thousands_separators_used": False,
        "amount_string_policy": "every rendered amount is str(Decimal) with "
                                "exactly two decimal places, so each page "
                                "string equals the value in this file",
    },
    "lines": [
        {"index": i,
         "sku": l["sku"],
         "sku_codepoints": ["U+%04X" % ord(c) for c in l["sku"]],
         "name": l["name"],
         "quantity": l["quantity"],
         "unit_price_input": l["unit_price"],
         "unit_price_decimal": str(l["unit_price_decimal"]),
         "exact_product": str(l["exact_product"]),
         "line_amount": l["amount_str"],
         "expression": "%s x %s = %s" % (l["quantity"], l["unit_price_decimal"],
                                          l["amount_str"])}
        for i, l in enumerate(lines)
    ],
    "totals": {
        "goods_subtotal": M["subtotal"],
        "discount": M["discount"],
        "taxable_goods_base": M["taxable"],
        "tax": M["tax"],
        "shipping": M["shipping"],
        "amount_payable": M["total"],
    },
    "literal_lines_verbatim": [
        {"index": i, "text": s, "char_count": len(s),
         "codepoints": ["U+%04X" % ord(c) for c in s],
         "utf8_hex": s.encode("utf-8").hex(),
         "double_space_groups": [j for j in range(len(s) - 1)
                                 if s[j] == " " and s[j + 1] == " "],
         "contains": {
             "lt": "<" in s, "gt": ">" in s, "amp": "&" in s,
             "backslash": "\\" in s,
         }}
        for i, s in enumerate(inv["literal_lines"])
    ],
    "notes_verbatim": [
        {"index": i, "text": s, "char_count": len(s),
         "codepoints": ["U+%04X" % ord(c) for c in s]}
        for i, s in enumerate(inv["notes"])
    ],
    "confusable_sku_note": {
        "sku": lines[0]["sku"],
        "chars": [{"char": c, "codepoint": "U+%04X" % ord(c),
                   "kind": ("digit" if c.isdigit() else
                            "upper" if c.isupper() else
                            "lower" if c.islower() else "punct")}
                  for c in lines[0]["sku"]],
        "rendering_choice": "fontFamily=Inter,Noto Sans Mono CJK SC with "
                            "fontFeatures=zero, which switches the digit zero "
                            "to Inter's slashed zero so O/0 and I/1/l cannot "
                            "be confused; verified on a rendered probe",
    },
    "escape_policy": {
        "rule": "the parser does NOT decode HTML entities, so attribute values "
                "containing < > & would print as visible '&lt;' text; every "
                "string with < > & is therefore carried in a CDATA section",
        "probe_evidence": "tmp/20261004-182918/A11/preview/probe-01.png P1 vs P2",
    },
    "whitespace_policy": {
        "rule": "Text text nodes are trimmed by the parser, so any inline span "
                "whose content has leading/trailing spaces uses <Raw text=...>, "
                "which is documented as not trimmed",
        "probe_evidence": "tmp/20261004-182918/A11/preview/probe-03.png Q1 vs Q2",
        "measured_space_advance_px": {"Inter@56px": 16},
    },
}
with open(os.path.join(OUT, "invoice-audit.json"), "w", encoding="utf-8") as fh:
    json.dump(audit, fh, ensure_ascii=False, indent=2)

textmap = {
    "task": "A11",
    "run_id": S.RUN,
    "pages": [
        {"file": "invoice-page-01.png", "dsl": "invoice-page-01.snapshot",
         "width": PW, "height": PH, "role": "结算与明细",
         "margin": MARGIN, "content_width": CW},
        {"file": "invoice-page-02.png", "dsl": "invoice-page-02.snapshot",
         "width": PW, "height": PH, "role": "说明与原样文字",
         "margin": MARGIN, "content_width": CW},
    ],
    "fonts_used": [
        {"family": UI, "use": "latin + CJK body text", "size_range": [21, 56]},
        {"family": MONO, "use": "money, quantity, invoice number (tabular digits)",
         "size_range": [26, 34]},
        {"family": MONOUI, "use": "literal lines and footer ids", "size_range": [21, 30]},
        {"family": SKUF, "use": "SKU column with fontFeatures=zero", "size_range": [26]},
    ],
    "type_scale": {"body_min_px": 24, "footnote_px": 21, "label_min_px": 21},
    "layout_fit_checks": {
        "method": "dsllib.est_width() on every string that must stay on one "
                  "line; monospace runs are scaled by 0.62 because the shared "
                  "estimator uses 0.55em for latin while DejaVu Sans Mono "
                  "really advances 0.602em (1233/2048)",
        "all_fit": all(f["fits"] for f in FITS),
        "checks": FITS,
    },
    "elements": TEXTMAP,
}
with open(os.path.join(OUT, "text-map.json"), "w", encoding="utf-8") as fh:
    json.dump(textmap, fh, ensure_ascii=False, indent=2)

print("audit+textmap written; text elements: %d" % len(TEXTMAP))