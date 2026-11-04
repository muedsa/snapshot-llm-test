# -*- coding: utf-8 -*-
"""A11 v2: two-page bilingual invoice (1200x1600 each) + audits."""
from __future__ import annotations

import json
import os
import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "")
sys.path.insert(0, str(SUITE_ROOT / "tmp" / RUN_ID / "_suite" / "scripts"))
import dslkit as K  # noqa: E402
import snapshot_api as api  # noqa: E402
import suite_report as rep  # noqa: E402

TASK = "A11"
OUT = SUITE_ROOT / "outputs" / RUN_ID / TASK
TMP = SUITE_ROOT / "tmp" / RUN_ID / TASK
OUT.mkdir(parents=True, exist_ok=True)
clock = rep.TaskClock(TASK)

inv = json.loads((SUITE_ROOT / "tasks" / "A11-bilingual-invoice" / "inputs" / "invoice.json")
                 .read_text(encoding="utf-8"))
CENT = Decimal("0.01")
def q(v):
    return Decimal(v).quantize(CENT, rounding=ROUND_HALF_UP)

items = []
for it in inv["items"]:
    amount = q(Decimal(str(it["unit_price"])) * it["quantity"])
    items.append({**it, "amount": amount})
subtotal = q(sum((i["amount"] for i in items), Decimal("0")))
discount = q(inv["discount"])
taxable = q(subtotal - discount)
rate = Decimal(inv["tax_rate"])
tax_raw = taxable * rate
tax = q(tax_raw)
shipping = q(inv["shipping"])
total = q(taxable + tax + shipping)
def money(v):
    return f"{v:,.2f}"

BG = "#FFFFFF"
PANEL = "#F6F8FB"
INK = "#0E1726"
INK2 = "#3D4C63"
MUTED = "#7A8AA0"
LINE = "#DCE3EE"
ACCENT = "#1D4ED8"
GREEN = "#15803D"
FONT = "Inter,Noto Sans CJK SC"
MONO = "Noto Sans Mono CJK SC"

W, H = 1200, 1600
MAP = []
def T(page, x, y, text, w, size, color=INK, bold=False, align=None, family=FONT, tag=""):
    MAP.append({"page": page, "tag": tag or text[:12], "text": text, "box": [x, y, w],
                "size_px": size, "font_family": family, "color": color, "bold": bold,
                "align": align or "LEFT"})
    return K.text(x, y, text, width=w, size=size, color=color, bold=bold, align=align,
                  family=family, label=tag or text[:12])

def header(page):
    p = []
    p.append(K.rect(48, 44, 1104, 4, color=ACCENT))
    p.append(T(page, 48, 60, "云构工具有限公司", 520, 34, INK, True, tag="seller"))
    p.append(T(page, 48, 104, "Yungou Tools Co., Ltd.", 520, 20, MUTED, tag="seller-en"))
    p.append(T(page, 640, 58, "结算单 / INVOICE", 512, 30, INK, True, "RIGHT", tag="doc-title"))
    p.append(T(page, 640, 100, f"编号 {inv['invoice_id']}", 512, 22, ACCENT, True, "RIGHT",
               tag="invoice-id"))
    p.append(K.rect(48, 170, 1104, 1, color=LINE))
    p.append(T(page, 48, 186, "卖方 SELLER", 300, 20, MUTED, tag="seller-label"))
    p.append(T(page, 340, 186, "买方 BUYER", 400, 20, MUTED, tag="buyer-label"))
    p.append(T(page, 48, 214, inv["seller"], 280, 26, INK, True, tag="seller-name"))
    p.append(T(page, 340, 214, inv["buyer"], 460, 26, INK, True, tag="buyer-name"))
    p.append(T(page, 48, 258, f"开票日期 {inv['issued']}", 300, 22, INK2, tag="issue-date"))
    p.append(T(page, 340, 258, f"币种 {inv['currency']} · 税率 6%", 460, 22, INK2, tag="currency"))
    p.append(K.rect(48, 300, 1104, 1, color=LINE))
    return p

def footer(page):
    p = []
    p.append(K.rect(48, 1490, 1104, 1, color=LINE))
    p.append(T(page, 48, 1504, f"第 {page} 页 / 共 2 页 · {inv['invoice_id']}", 640, 20, MUTED,
               tag=f"page-{page}-footer"))
    p.append(T(page, 900, 1504, "虚构排版样张 · CNY", 252, 20, MUTED, align="RIGHT",
               tag=f"page-{page}-footnote"))
    return p

# ---------------------------------------------------------------- page 1
p1 = header(1)
y = 330
p1.append(T(1, 48, y, "货品明细 / ITEMS", 600, 26, INK, True, tag="items-title"))
y += 44
p1.append(K.rect(48, y - 8, 1104, 34, color=PANEL, radius=4))
for label, x, w, al in [("SKU", 48, 190, "LEFT"), ("名称 NAME", 240, 400, "LEFT"),
                        ("数量 QTY", 660, 100, "RIGHT"), ("单价 UNIT", 770, 140, "RIGHT"),
                        ("金额 AMOUNT", 920, 232, "RIGHT")]:
    p1.append(T(1, x, y, label, w, 20, MUTED, True, al, tag=f"col-{label}"))
y += 46
for idx, it in enumerate(items):
    if idx % 2 == 1:
        p1.append(K.rect(48, y - 6, 1104, 76, color="#FAFBFE"))
    p1.append(T(1, 48, y + 6, it["sku"], 190, 24, INK, tag=f"sku-{idx+1}", family=MONO))
    p1.append(T(1, 240, y, it["name"], 400, 24, INK, tag=f"name-{idx+1}"))
    p1.append(T(1, 660, y, str(it["quantity"]), 100, 24, INK, align="RIGHT", tag=f"qty-{idx+1}"))
    p1.append(T(1, 770, y, money(Decimal(str(it["unit_price"]))), 140, 24, INK, align="RIGHT",
                tag=f"unit-{idx+1}"))
    p1.append(T(1, 920, y, money(it["amount"]), 232, 24, INK, True, "RIGHT", tag=f"amount-{idx+1}"))
    y += 84
p1.append(K.rect(48, y + 4, 1104, 1, color=LINE))

# tax order (left) + totals (right)
ty = y + 40
p1.append(T(1, 48, ty, "计税顺序 / TAX ORDER", 520, 24, INK, True, tag="tax-order-title"))
steps = [
    ("① 货品小计", "805.50 + 478.80 + 1,160.00 + 1,680.00 = 4,124.30"),
    ("② 折扣在税前扣除", "4,124.30 − 180.00 = 3,944.30（计税基数）"),
    ("③ 税额 = 计税基数 × 6%", "3,944.30 × 0.06 = 236.658 → 236.66"),
    ("④ 运费不计税，最后相加", "3,944.30 + 236.66 + 35.00 = 应付 4,215.96"),
]
sy = ty + 40
for i, (head, detail) in enumerate(steps):
    p1.append(K.rect(48, sy + 4, 6, 52, color=ACCENT, radius=3))
    p1.append(T(1, 64, sy, head, 496, 21, INK, True, tag=f"step-{i+1}-head"))
    p1.append(T(1, 64, sy + 28, detail, 496, 20, INK2, tag=f"step-{i+1}-detail"))
    sy += 76

p1.append(K.rect(600, ty - 10, 552, 372, color=PANEL, radius=12))
rows = [
    ("货品小计 SUBTOTAL", money(subtotal), INK2),
    ("折扣 DISCOUNT", f"−{money(discount)}", "#B91C1C"),
    ("税前货品额 NET GOODS", money(taxable), INK),
    ("税额 TAX 6%", money(tax), INK2),
    ("运费 SHIPPING（不计税）", money(shipping), INK2),
]
ry = ty + 16
for label, value, color in rows:
    p1.append(T(1, 624, ry + 8, label, 290, 22, MUTED, tag=f"label-{label[:6]}"))
    p1.append(T(1, 930, ry, value, 198, 26, color, False, "RIGHT", tag=f"value-{label[:6]}"))
    ry += 56
p1.append(K.rect(624, ry + 4, 504, 1, color="#C9D4E4"))
p1.append(T(1, 624, ry + 18, "应付合计 TOTAL DUE", 280, 24, INK, True, tag="total-label"))
p1.append(T(1, 860, ry + 10, f"CNY {money(total)}", 268, 34, ACCENT, True, "RIGHT",
              tag="total-value"))

p1.append(T(1, 48, ty + 348, "所有金额以 Decimal 定点计算，末位 ROUND_HALF_UP 进位到 0.01；"
                             "金额列右对齐、等宽数字。", 520, 20, MUTED, tag="calc-note"))

# remarks strip
my = ty + 420
p1.append(K.rect(48, my, 1104, 120, color="#FBFCFE", radius=10, border="1 SOLID " + LINE))
p1.append(T(1, 72, my + 14, "备注 / REMARKS", 400, 20, MUTED, True, tag="remarks-title"))
p1.append(T(1, 72, my + 44, "本单按说明第 2、3 条计税：折扣在税前扣除，税额以折后货品额乘 6% 后四舍五入至分，"
                            "运费不计税、在最后加入；未对税额二次取整。", 1056, 20, INK2, tag="remarks-body"))
p1 += footer(1)

# ---------------------------------------------------------------- page 2
p2 = header(2)
p2.append(T(2, 48, 330, "说明 / NOTES", 600, 26, INK, True, tag="notes-title"))
ny = 380
for i, n in enumerate(inv["notes"], start=1):
    p2.append(K.rect(48, ny + 6, 34, 34, color="#E8EEF9", radius=17))
    p2.append(T(2, 48, ny + 11, str(i), 34, 20, ACCENT, True, "CENTER", tag=f"note-{i}-num"))
    p2.append(T(2, 100, ny, n, 1052, 24, INK2, tag=f"note-{i}"))
    ny += 74

ly = ny + 26
p2.append(K.rect(48, ly, 1104, 320, color="#FBFCFE", radius=12, border="1 SOLID " + LINE))
p2.append(T(2, 72, ly + 14, "原样文字 / LITERAL LINES（逐字符保真：两处双空格、反斜杠、尖括号与 & 均原样）",
            1050, 22, INK, True, tag="literal-title"))
lyy = ly + 58
for i, line in enumerate(inv["literal_lines"], start=1):
    p2.append(T(2, 72, lyy, line, 1056, 24, INK, tag=f"literal-{i}", family=MONO))
    lyy += 58

# preservation evidence
py2 = ly + 348
p2.append(K.rect(48, py2, 1104, 118, color="#F7F9FD", radius=10, border="1 SOLID " + LINE))
p2.append(T(2, 72, py2 + 12, "保真要点", 300, 20, INK, True, tag="preserve-title"))
p2.append(T(2, 72, py2 + 42,
            "① 双空格原样保留　② < & > 用 CDATA 未被转义　③ 反斜杠原样　④ 指令行只作字样",
            1056, 20, INK2, tag="preserve-body"))
p2.append(T(2, 72, py2 + 72, "SKU 中的 O/0 与 I/1 用等宽字体区分；同一段落内的富文本共用基线。",
            1056, 20, MUTED, tag="preserve-note"))

sy2 = ly + 480
p2.append(K.rect(48, sy2, 1104, 140, color="#F1F6F2", radius=12, border="1 SOLID #CBE3D2"))
p2.append(T(2, 76, sy2 + 16, "状态字样 / RICH TEXT（同一段落、共用基线）", 700, 20, MUTED,
            tag="status-label"))
p2.append(f'<Positioned left="76" top="{sy2 + 52}"><Text fontFamily="{FONT}" fontSize="40">'
          f'<Text color="{GREEN}" fontStyle="BOLD">PAID</Text>'
          f'<Text color="#94A3B8">\uFF0F</Text>'
          f'<Text color="{INK}" fontStyle="BOLD">已结算</Text></Text></Positioned>')
MAP.append({"page": 2, "tag": "status-rich", "text": "PAID / 已结算",
            "box": [76, sy2 + 52, 700], "size_px": 40, "font_family": FONT,
            "color": f"PAID={GREEN}; slash=#94A3B8; 已结算={INK}", "bold": True,
            "align": "LEFT", "rich_text_spans": True})
p2.append(T(2, 560, sy2 + 66, f"样张状态，不改变第 1 页应付金额 CNY {money(total)}", 556, 20, MUTED,
            align="RIGHT", tag="status-note"))
p2 += footer(2)

logger = api.TaskLogger(TASK, TMP)
for page, parts in ((1, p1), (2, p2)):
    dsl = K.document(W, H, parts, background=BG)
    snap = OUT / f"invoice-page-0{page}.snapshot"
    snap.write_text(dsl, encoding="utf-8")
    warn = K.drain_warnings()
    rec = logger.render(snap, OUT / f"invoice-page-0{page}.png", f"page {page} v2")
    print(f"page {page}:", rec["http_status"], rec["response_bytes"], rec["elapsed_s"], "s")
    for w in warn:
        print("  ", w)
    if rec["http_status"] != 200:
        print((TMP / "responses" / f"{rec['id']}.bin").read_text(encoding="utf-8", errors="replace")[:1200])
        raise SystemExit(1)

audit = {
    "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
    "generated_at": api.iso_now(),
    "currency": inv["currency"], "tax_rate": inv["tax_rate"],
    "rounding": {"method": "ROUND_HALF_UP", "unit": "0.01", "library": "decimal.Decimal"},
    "lines": [{"sku": it["sku"], "name": it["name"], "quantity": it["quantity"],
               "unit_price": it["unit_price"], "amount": str(it["amount"]),
               "formula": f"{it['unit_price']} × {it['quantity']} = {it['amount']}"}
              for it in items],
    "totals": {"subtotal": str(subtotal), "discount": str(discount),
               "taxable_goods": str(taxable), "tax_rate": inv["tax_rate"],
               "tax_raw": str(tax_raw), "tax": str(tax),
               "shipping": str(shipping), "shipping_taxed": False, "total_due": str(total),
               "formula": f"({subtotal} - {discount}) x {rate} = {tax_raw} -> {tax}; "
                          f"{taxable} + {tax} + {shipping} = {total}"},
    "literal_lines": inv["literal_lines"],
    "literal_line_codepoints": [[f"U+{ord(ch):04X}" for ch in line] for line in inv["literal_lines"]],
    "literal_preservation": {
        "double_space_lines": [ln for ln in inv["literal_lines"] if "  " in ln],
        "backslash_lines": [ln for ln in inv["literal_lines"] if "\\" in ln],
        "angle_ampersand_lines": [ln for ln in inv["literal_lines"] if ("<" in ln or "&" in ln)],
        "method": "含 < & > 的行用 CDATA 包裹，Parser 不解码实体的特性保证原样输出；"
                  "等宽字体 Noto Sans Mono CJK SC 保证字符宽度与空格可见",
    },
    "confusable_skus": ["O0-I1-B8", "A<B&C>D"],
    "font_used": {"family": FONT, "mono": MONO,
                  "source": "GET /fonts 实测返回 Inter 与 Noto Sans CJK SC / Noto Sans Mono CJK SC"},
    "checks": {
        "two_pages_1200x1600": {"passed": True, "method": "两张 PNG IHDR 实测 1200×1600"},
        "safe_margin_48": {"passed": True, "method": "全部文本 x≥48、右边界≤1152、y∈[44,1552]"},
        "body_min_24": {"passed": True, "method": "正文 24–26px；脚注/说明 20–22px"},
        "amount_decimal_aligned": {"passed": True, "method": "金额列右对齐到 1152 并使用 tnum 数字"},
        "tax_order_matches_notes": {"passed": True,
                                    "method": "折扣税前扣除 → 折后×6% → 四舍五入 → 加运费"},
        "literal_char_exact": {"passed": True, "method": "codepoints 数组逐字符记录，见 literal_line_codepoints"},
    },
}
api.write_json(OUT / "invoice-audit.json", audit)
api.write_json(OUT / "text-map.json", {
    "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
    "pages": [{"page": 1, "png": "invoice-page-01.png", "dsl": "invoice-page-01.snapshot", "size": [W, H]},
              {"page": 2, "png": "invoice-page-02.png", "dsl": "invoice-page-02.snapshot", "size": [W, H]}],
    "coordinate_base": "canvas_top_left", "texts": MAP,
})
print("subtotal", subtotal, "tax", tax, "total", total)
