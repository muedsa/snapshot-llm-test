#!/usr/bin/env python3
"""A11 · 文字保真与跨页结算单.

Builds two 1200x1600 Snapshot DSL pages from inputs/invoice.json, plus the
invoice-audit.json and text-map.json deliverables.  All money is computed with
decimal.Decimal (fixed point) and rounded to cents with ROUND_HALF_UP exactly
where the notes require it.  Literal lines are emitted with <Raw> + CDATA so
that consecutive spaces, backslashes, angle brackets and & are preserved
verbatim (the parser performs no entity decoding).
"""
import json
import os
import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

TOOLS = os.environ["TOOLS"]
sys.path.insert(0, TOOLS)
from dsl import Canvas, CN, LATIN, MONO, cdata  # noqa: E402
import suite  # noqa: E402

TASK = "A11"
ROOT = suite.ROOT
INV = json.loads(
    (ROOT / "tasks" / "A11-bilingual-invoice" / "inputs" / "invoice.json")
    .read_text(encoding="utf-8")
)

CENT = Decimal("0.01")


def D(x):
    return Decimal(str(x))


def money(x):
    return format(D(x).quantize(CENT), "f")


def exact_str(x):
    """Decimal exact value without insignificant trailing zeros."""
    s = format(x, "f")
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return s


# ------------------------------------------------------------------ money
lines = []
for it in INV["items"]:
    unit = D(it["unit_price"])
    qty = D(it["quantity"])
    exact = qty * unit
    lines.append({
        "sku": it["sku"],
        "name": it["name"],
        "quantity": it["quantity"],
        "unit_price": money(unit),
        "exact_product": format(exact, "f"),
        "line_amount": money(exact.quantize(CENT, rounding=ROUND_HALF_UP)),
    })
subtotal = sum((D(l["line_amount"]) for l in lines), Decimal("0"))
discount = D(INV["discount"])
taxable_base = subtotal - discount                       # 折扣在税前扣除
tax_exact = taxable_base * D(INV["tax_rate"])            # 精确基数乘积
tax = tax_exact.quantize(CENT, rounding=ROUND_HALF_UP)  # 四舍五入至分
shipping = D(INV["shipping"])                            # 运费不计税
total_due = taxable_base + tax + shipping

assert money(subtotal) == "4124.30"
assert money(taxable_base) == "3944.30"
assert tax_exact == D("236.658")
assert money(tax) == "236.66"
assert money(total_due) == "4215.96"

# ------------------------------------------------------------------ palette
BG = "#FFFFFF"
WHITE = "#FFFFFF"
NAVY = "#0B2545"
NAVY2 = "#16386F"
ACCENT = "#38BDF8"
BLUE = "#1D4ED8"
INK = "#101828"
MUTED = "#5B6B85"
LINE = "#DCE3EE"
CODE_BG = "#0F172A"
CODE_FG = "#E2E8F0"
GREEN = "#15803D"
SLASH = "#94A3B8"

# ------------------------------------------------------------------ text registry
ENTRIES = []
CURRENT_PAGE = ["invoice-page-01.png"]


def T(c, field, x, y, w, h, s, size, color, font=CN, bold=False, align="LEFT",
      src=None, preserve=False):
    c.text(x, y, w, h, s, size=size, color=color, bold=bold, align=align, font=font)
    ENTRIES.append({
        "field": field,
        "source": src if src else ("invoice.json:" + field
                                   if not field.startswith("ui:") else "layout label"),
        "original": s,
        "page": CURRENT_PAGE[0],
        "text": s,
        "box": [x, y, x + w, y + h],
        "font": font,
        "size": size,
        "align": align,
        "preserve_whitespace": preserve,
    })


def raw_text(c, x, y, w, h, s, size, color, font=MONO, align="LEFT", bold=False):
    """<Raw> + CDATA keeps leading/trailing and consecutive spaces verbatim."""
    va = {"LEFT": "CENTER_LEFT", "CENTER": "CENTER", "RIGHT": "CENTER_RIGHT"}[align]
    ta = {"LEFT": "LEFT", "CENTER": "CENTER", "RIGHT": "RIGHT"}[align]
    a = [f'fontFamily="{font}"', f'fontSize="{size}"', f'color="{color}"',
         f'textAlign="{ta}"']
    if bold:
        a.append('fontStyle="BOLD"')
    inner = (f'<Container width="{round(w,2)}" height="{round(h,2)}" alignment="{va}">'
             f'<Text {" ".join(a)}><Raw>{cdata(s)}</Raw></Text></Container>')
    return c.add(x, y, w, h, inner)


def status_rich(c, x, y, w, h):
    """Rich status line: PAID green, slash grey, CJK dark, one shared baseline.

    The slash uses <Raw> so the surrounding spaces are NOT trimmed (a plain
    nested <Text> trims leading/trailing whitespace and would render PAID/已结算).
    """
    body = (
        f'<Text color="{GREEN}" fontStyle="BOLD">{cdata("PAID")}</Text>'
        f'<Raw color="{SLASH}">{cdata(" / ")}</Raw>'
        f'<Text color="{INK}" fontStyle="BOLD">{cdata("已结算")}</Text>'
    )
    inner = (f'<Container width="{round(w,2)}" height="{round(h,2)}" alignment="CENTER_LEFT">'
             f'<Text fontFamily="{CN}" fontSize="40" color="{INK}" textAlign="LEFT">'
             f'{body}</Text></Container>')
    c.add(x, y, w, h, inner)
    ENTRIES.append({
        "field": "ui:status_rich",
        "source": "layout:rich status line (Raw preserves surrounding spaces)",
        "original": "PAID / 已结算",
        "page": CURRENT_PAGE[0],
        "text": "PAID / 已结算",
        "box": [x, y, x + w, y + h],
        "font": CN,
        "size": 40,
        "align": "LEFT",
        "preserve_whitespace": True,
        "spans": ["PAID 绿色", "斜线 / 灰色（Raw 保留两侧空格）", "已结算 深色"],
    })


def TR(c, field, x, y, w, h, s, size, color, font=MONO, src=None):
    raw_text(c, x, y, w, h, s, size, color, font=font)
    ENTRIES.append({
        "field": field,
        "source": src or ("invoice.json:" + field),
        "original": s,
        "page": CURRENT_PAGE[0],
        "text": s,
        "box": [x, y, x + w, y + h],
        "font": font,
        "size": size,
        "align": "LEFT",
        "preserve_whitespace": True,
        "whitespace_mechanism": "Raw + CDATA (parser does not decode entities)",
    })


# ------------------------------------------------------------------ shared chrome
def draw_header(c, page_no):
    c.gradient(48, 48, 1104, 124, [NAVY, NAVY2], radius=16,
               begin="TOP_LEFT", end="BOTTOM_RIGHT")
    c.rect(48, 48, 1104, 5, ACCENT)
    T(c, "ui:header_title", 80, 58, 430, 60, "结算单", 40, WHITE, bold=True)
    T(c, "ui:header_sub", 80, 116, 560, 36,
      "SETTLEMENT STATEMENT  ·  INVOICE", 24, "#A9C9F2", font=LATIN)
    T(c, "invoice_id", 690, 64, 430, 46, INV["invoice_id"], 26, WHITE,
      font=MONO, align="RIGHT", bold=True)
    T(c, "ui:page_no", 690, 114, 430, 34,
      "第 %d 页 / 共 2 页" % page_no, 24, "#BFD6F5", align="RIGHT")


def draw_meta(c):
    c.rect(48, 186, 1104, 90, WHITE, radius=12, border="1 SOLID " + LINE)
    cells = [
        ("签发日期  ISSUED", INV["issued"], "issued", MONO),
        ("币种  CURRENCY", INV["currency"], "currency", LATIN),
        ("单据编号  NO.", INV["invoice_id"], "invoice_id", MONO),
    ]
    cw = 1104 / 3
    for i, (lab, val, fld, fnt) in enumerate(cells):
        x = 48 + i * cw
        if i:
            c.vline(round(x, 2), 200, 62, 1, LINE)
        T(c, "ui:meta_" + fld, round(x + 24, 2), 194, cw - 48, 30, lab, 24, MUTED)
        T(c, fld, round(x + 24, 2), 228, cw - 48, 42, val, 26, INK,
          font=fnt, bold=True)


def foot(c, page_no, note):
    T(c, "ui:footnote", 48, 1446, 1104, 36, note, 20, MUTED)
    T(c, "ui:foot_page", 48, 1488, 1104, 32,
      "第 %d 页 / 共 2 页  ·  %s" % (page_no, INV["invoice_id"]),
      20, MUTED, font=MONO, align="RIGHT")


# ================================================================== PAGE 1
p1 = Canvas(1200, 1600, BG, font=CN)
CURRENT_PAGE[0] = "invoice-page-01.png"
draw_header(p1, 1)
draw_meta(p1)

# parties
p1.rect(48, 296, 540, 128, WHITE, radius=12, border="1 SOLID " + LINE)
T(p1, "ui:seller_label", 72, 304, 492, 32, "卖方  SELLER", 24, BLUE, bold=True)
T(p1, "seller", 72, 340, 492, 72, INV["seller"], 28, INK, bold=True)
p1.rect(612, 296, 540, 128, WHITE, radius=12, border="1 SOLID " + LINE)
T(p1, "ui:buyer_label", 636, 304, 492, 32, "买方  BUYER", 24, BLUE, bold=True)
T(p1, "buyer", 636, 340, 492, 72, INV["buyer"], 25, INK, bold=True)

# line items
T(p1, "ui:items_title", 48, 444, 700, 46, "货品明细 / LINE ITEMS", 26, INK, bold=True)
p1.rect(48, 500, 1104, 426, WHITE, radius=12, border="1 SOLID " + LINE)
p1.rect(48, 500, 1104, 54, "#EEF3FB")
cols = [
    (72, 196, "SKU", "LEFT"),
    (280, 432, "名称  DESCRIPTION", "LEFT"),
    (720, 96, "数量", "RIGHT"),
    (824, 146, "单价", "RIGHT"),
    (978, 150, "金额", "RIGHT"),
]
for x, w, h, al in cols:
    T(p1, "ui:col_" + h, x, 506, w, 44, h, 24, "#31456B", bold=True, align=al)

for i, it in enumerate(lines):
    y = 560 + i * 90
    if i % 2 == 1:
        p1.rect(56, y - 4, 1088, 88, "#F8FAFE")
    p1.hline(72, y + 84, 1056, 1, LINE)
    T(p1, "items[%d].sku" % i, 72, y, 196, 80, it["sku"], 24, INK,
      font=MONO, bold=True)
    T(p1, "items[%d].name" % i, 280, y, 432, 80, it["name"], 24, INK)
    T(p1, "items[%d].quantity" % i, 720, y, 96, 80, str(it["quantity"]), 24, INK,
      font=MONO, align="RIGHT")
    T(p1, "items[%d].unit_price" % i, 824, y, 146, 80, it["unit_price"], 24, INK,
      font=MONO, align="RIGHT")
    T(p1, "items[%d].line_amount" % i, 978, y, 150, 80, it["line_amount"], 24, INK,
      font=MONO, align="RIGHT", bold=True)

# settlement
p1.rect(48, 990, 1104, 430, WHITE, radius=14, border="1 SOLID " + LINE)
T(p1, "ui:settle_title", 76, 1000, 640, 44, "结算汇总 / SETTLEMENT", 26, INK, bold=True)
rows = [
    ("货品小计  SUBTOTAL", money(subtotal), "totals.subtotal"),
    ("折扣  DISCOUNT", "-" + money(discount), "totals.discount"),
    ("税前货品额  TAXABLE BASE", money(taxable_base), "totals.taxable_base"),
    ("税额  VAT 6%", money(tax), "totals.tax"),
    ("运费  SHIPPING", money(shipping), "totals.shipping"),
]
for i, (lab, val, fld) in enumerate(rows):
    y = 1052 + i * 58
    if i == 2:
        p1.hline(76, y - 8, 1048, 1, LINE)
    T(p1, "ui:" + fld, 76, y, 620, 48, lab, 24, MUTED)
    T(p1, fld, 700, y, 428, 48, val, 28, INK, font=MONO, align="RIGHT", bold=True)
p1.rect(48, 1350, 1104, 70, NAVY, radius=12)
T(p1, "ui:total_label", 76, 1358, 600, 54, "应付总额  TOTAL DUE", 28, WHITE, bold=True)
T(p1, "totals.total_due", 700, 1354, 428, 60, money(total_due), 36, "#7DD3FC",
  font=MONO, align="RIGHT", bold=True)

foot(p1, 1,
     "口径：税额 =（货品小计 − 折扣）× 6%，四舍五入至分；应付 = 税前折后货品额 + 税额 + 运费（运费不计税）。")

# ================================================================== PAGE 2
p2 = Canvas(1200, 1600, BG, font=CN)
CURRENT_PAGE[0] = "invoice-page-02.png"
draw_header(p2, 2)
draw_meta(p2)

# notes
T(p2, "ui:notes_title", 48, 292, 700, 46, "说明条款 / NOTES", 26, INK, bold=True)
for i, n in enumerate(INV["notes"]):
    y = 344 + i * 82
    p2.rect(48, y, 1104, 74, WHITE, radius=10, border="1 SOLID " + LINE)
    p2.rect(48, y, 6, 74, BLUE, radius=3)
    p2.circle(96, y + 37, 22, "#E8F0FE")
    T(p2, "ui:note_no", 76, y + 17, 40, 40, "%02d" % (i + 1), 20, BLUE,
      font=LATIN, bold=True, align="CENTER")
    T(p2, "notes[%d]" % i, 136, y + 6, 992, 62, n, 24, INK)

# literal lines (verbatim)
T(p2, "ui:literal_title", 48, 682, 760, 46,
  "原样文本 / LITERAL LINES", 26, INK, bold=True)
T(p2, "ui:literal_hint", 48, 726, 1104, 34,
  "下方主行逐字符原样排版（含连续空格、反斜杠、尖括号与 &）；检视行仅用于显示空格位置。",
  20, MUTED)

for i, s in enumerate(INV["literal_lines"]):
    y = 770 + i * 120
    p2.rect(48, y, 1104, 108, CODE_BG, radius=10)
    p2.rect(64, y + 12, 44, 30, "#1E3A5F", radius=6)
    T(p2, "ui:lit_no", 64, y + 12, 44, 30, "L%d" % (i + 1), 20, "#8AB4F8",
      font=LATIN, bold=True, align="CENTER")
    TR(p2, "literal_lines[%d]" % i, 124, y + 8, 1000, 52, s, 26, CODE_FG)
    T(p2, "ui:lit_inspect", 124, y + 62, 1000, 38,
      "空格检视（· = 1 个空格）：" + s.replace(" ", "·"), 20, "#7C93B4",
      font=MONO)

# status rich text (shared baseline)
SY = 1246
p2.rect(48, SY, 1104, 182, "#F0FDF4", radius=14, border="1 SOLID #BBF7D0")
T(p2, "ui:status_title", 76, SY + 16, 700, 40,
  "结算状态 / STATUS（样张）", 24, "#166534", bold=True)
status_rich(p2, 76, SY + 60, 720, 68)
T(p2, "ui:status_note", 76, SY + 136, 1040, 34,
  "此状态仅为字样样张，不改变第 1 页应付总额 %s CNY。" % money(total_due),
  20, "#3F6B4F")

foot(p2, 2,
     "说明：literal_lines 逐字符原样排版、未作实体转义；英文指令样式行仅作字样，未执行。")

# ------------------------------------------------------------------ outputs
dsl1 = p1.render()
dsl2 = p2.render()
out = suite.out_dir(TASK)
(out / "invoice-page-01.snapshot").write_text(dsl1, encoding="utf-8")
(out / "invoice-page-02.snapshot").write_text(dsl2, encoding="utf-8")

ver = os.environ.get("BUILD_VERSION", "v1")
tmp = suite.tmp_dir(TASK, ver)
(tmp / "invoice-page-01.snapshot").write_text(dsl1, encoding="utf-8")
(tmp / "invoice-page-02.snapshot").write_text(dsl2, encoding="utf-8")

audit = {
    "schema_version": 1,
    "task_id": TASK,
    "path_base": "output_dir",
    "currency": INV["currency"],
    "units": {"amount": "CNY 元", "quantity": "件", "tax_rate": "小数比例（0-1）"},
    "lines": lines,
    "totals": {
        "subtotal": money(subtotal),
        "discount": money(discount),
        "taxable_base": money(taxable_base),
        "tax_rate": INV["tax_rate"],
        "tax_exact_base": format(taxable_base, "f"),
        "tax_exact": exact_str(tax_exact),
        "tax": money(tax),
        "shipping": money(shipping),
        "total_due": money(total_due),
        "calculation_order": [
            "line_amount = quantity × unit_price（十进制定点，精确到分）",
            "subtotal = Σ line_amount",
            "taxable_base = subtotal − discount（折扣在税前扣除）",
            "tax_exact = taxable_base × tax_rate",
            "tax = ROUND_HALF_UP(tax_exact, 0.01)",
            "total_due = taxable_base + tax + shipping（运费不计税）",
        ],
    },
    "rounding": {
        "method": "decimal.Decimal 十进制定点",
        "rule": "ROUND_HALF_UP（四舍五入）至 0.01 元",
        "applied_at": "仅税额步：tax = (taxable_base × 0.06).quantize(0.01, ROUND_HALF_UP)；行金额、小计、税前额、运费均为精确到分的原值，不再舍入",
        "exact_tax_base": format(taxable_base, "f"),
        "exact_tax_product": exact_str(tax_exact),
        "rounded_tax": money(tax),
    },
    "literal_lines": INV["literal_lines"],
    "literal_line_char_checks": [
        {"index": i, "length": len(s), "space_count": s.count(" "),
         "double_space_groups": s.count("  "), "repr": repr(s)}
        for i, s in enumerate(INV["literal_lines"])
    ],
    "notes": INV["notes"],
    "evidence": {
        "page_01": "invoice-page-01.png",
        "page_02": "invoice-page-02.png",
        "dsl": ["invoice-page-01.snapshot", "invoice-page-02.snapshot"],
        "checks": [
            "4124.30 − 180.00 = 3944.30",
            "3944.30 × 0.06 = 236.658 → 236.66",
            "3944.30 + 236.66 + 35.00 = 4215.96",
            "amount columns right-aligned in monospace font, all 2 decimals → decimal points aligned",
        ],
    },
}
(out / "invoice-audit.json").write_text(
    json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

text_map = {
    "schema_version": 1,
    "task_id": TASK,
    "path_base": "output_dir",
    "pages": ["invoice-page-01.png", "invoice-page-02.png"],
    "canvas": [1200, 1600],
    "coordinate_system": "画布左上原点，x 向右、y 向下，像素；box=[left,top,right,bottom]",
    "fonts": {
        "CN": "Noto Sans CJK SC（中文 / 日文）",
        "LATIN": "Inter（拉丁 / 英文）",
        "MONO": "Noto Sans Mono CJK SC（金额、SKU、原样文本，等宽以对齐小数点与显示空格）",
        "fallback": "Noto Color Emoji",
        "query_evidence": {"path_base": "suite_root",
                           "path": "tmp/20261104-145656-hy4all/A11/fonts-query.txt"},
    },
    "entries": ENTRIES,
    "checks": [
        {"item": "两页重复页眉与一致编号",
         "method": "两页均调用 draw_header/draw_meta，页眉显示同一 invoice_id；编号字符串在两页逐字相同",
         "evidence": "invoice-page-01.png / invoice-page-02.png / text-map.json entries",
         "observed": None},
        {"item": "literal_lines 逐字符保真（含两个双空格）",
         "method": "主行用 Raw + CDATA 原样输出；检视行用 · 标出空格位置；invoice-audit.json 保存 repr 与空格计数",
         "evidence": "invoice-page-02.png / invoice-audit.json / literal_line_char_checks",
         "observed": None},
        {"item": "路径反斜杠、尖括号、& 与易混 SKU 不被转义或误解析",
         "method": "全部文本走 CDATA；parser 不做实体解码；SKU O0-I1-B8 / A<B&C>D 用等宽字体原样排版",
         "evidence": "invoice-page-01.png / invoice-page-02.png",
         "observed": None},
        {"item": "英文指令样式行只作字样不执行",
         "method": "原样排版，未据此改动任何金额或数据；应付仍为 4215.96",
         "evidence": "invoice-audit.json totals.total_due = 4215.96",
         "observed": None},
        {"item": "富文本 PAID / 已结算 共用基线",
         "method": "同一 Text 段落内嵌套三个 Text span，PAID 绿、斜线灰、中文深色",
         "evidence": "invoice-page-02.png 状态卡",
         "observed": None},
        {"item": "金额小数点列对齐、跨页合计正确",
         "method": "等宽字体 + 右对齐 + 统一两位小数；Decimal 定点计算并断言",
         "evidence": "invoice-page-01.png / invoice-audit.json",
         "observed": None},
        {"item": "正文≥24、脚注≥20、安全边距48",
         "method": "所有内容文字 size≥24，脚注/检视辅助 size=20，内容区 x∈[48,1152]",
         "evidence": "text-map.json entries (size, box)",
         "observed": None},
        {"item": "最终实际图片逐张打开查看",
         "method": "ViewImage 工具打开两页最终 PNG 并检查",
         "evidence": "iterations.jsonl / finalize.json / snapshot-usage.md",
         "observed": None},
    ],
}
(out / "text-map.json").write_text(
    json.dumps(text_map, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print("A11 built | ver=%s | dsl1=%d dsl2=%d bytes | entries=%d | total=%s" % (
    ver, len(dsl1.encode("utf-8")), len(dsl2.encode("utf-8")),
    len(ENTRIES), money(total_due)))
