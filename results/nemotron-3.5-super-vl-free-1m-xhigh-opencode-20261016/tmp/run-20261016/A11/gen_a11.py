import json
from decimal import Decimal, ROUND_HALF_UP

with open("tasks/A11-bilingual-invoice/inputs/invoice.json", encoding="utf-8") as f:
    inv = json.load(f)

CUR = inv["currency"]
TAX = Decimal(inv["tax_rate"])
DISC = Decimal(inv["discount"])
SHIP = Decimal(inv["shipping"])

def d2(x):
    return Decimal(x).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

def fmt(x):
    x = Decimal(x)
    sign = "-" if x < 0 else ""
    s = format(abs(x), ",.2f")
    return f"{sign}{s}"

lines = []
subtotal = Decimal("0")
for it in inv["items"]:
    qty = Decimal(it["quantity"])
    up = Decimal(it["unit_price"])
    exact = qty * up
    amt = d2(exact)
    subtotal += amt
    lines.append({
        "sku": it["sku"],
        "name": it["name"],
        "qty": str(it["quantity"]),
        "unit": fmt(up),
        "exact": str(exact),
        "amount": fmt(amt),
    })

pre_tax = d2(subtotal - DISC)
tax = d2(pre_tax * TAX)
payable = d2(pre_tax + tax + SHIP)

audit_lines = []
for it, l in zip(inv["items"], lines):
    audit_lines.append({
        "sku": l["sku"],
        "name": l["name"],
        "quantity": int(it["quantity"]),
        "unit_price": l["unit"],
        "exact_product": str(l["exact"]),
        "rounded_amount": l["amount"],
    })

audit = {
    "schema_version": 1,
    "task_id": "A11",
    "path_base": "output_dir",
    "source": "inputs/invoice.json",
    "currency": CUR,
    "tax_rate": str(TAX),
    "rounding": "十进制定点，Decimal ROUND_HALF_UP，逐行金额先四舍五入至分，税额在税前折后货品金额上乘税率后再四舍五入至分，最终应付＝税前额＋税额＋运费",
    "lines": audit_lines,
    "totals": {
        "subtotal": fmt(subtotal),
        "discount": fmt(DISC),
        "pre_tax_amount": fmt(pre_tax),
        "tax_amount": fmt(tax),
        "shipping": fmt(SHIP),
        "payable": fmt(payable),
        "tax_basis": fmt(pre_tax),
        "calculation_order": ["货品小计＝各行金额之和", "税前货品额＝小计－折扣", "税额＝税前货品额×税率（四舍五入至分）", "应付＝税前货品额＋税额＋运费"],
    },
    "payable": fmt(payable),
    "literal_lines": inv["literal_lines"],
    "notes": inv["notes"],
    "note_calculation_order": "严格按 notes：折扣在税前从货品小计扣除，运费不计税；税额以税前折后货品金额乘 6%，四舍五入至分；最终应付再加运费。",
}
with open("tmp/run-20261016/A11/invoice-audit.v1.json", "w", encoding="utf-8") as f:
    json.dump(audit, f, ensure_ascii=False, indent=2)
print("subtotal", subtotal, "pre_tax", pre_tax, "tax", tax, "payable", payable)
for l in lines:
    print(l)

# ---------------- DSL generator ----------------
W, H = 1200, 1600
M = 48  # safety margin
FONT_CJK = "Noto Sans CJK SC,Inter"

def esc_for_dsl(s):
    # Parser 不做 HTML 实体解码，直接写原文即可；仅防止解析器把 '<' 当标签开头时使用 CDATA
    if "<" in s or ">" in s or "&" in s:
        return "<![CDATA[" + s + "]]>"
    return s

def T(text, x, y, w=None, size="20", color="#111827", bold=False, align="START", font=FONT_CJK, leading=None):
    b = ' fontStyle="BOLD"' if bold else ""
    a = f' textAlign="{align}"' if align != "START" else ""
    l = f' height="{leading}"' if leading else ""
    wd = f' width="{w}"' if w else ""
    return f'<Positioned left="{x}" top="{y}"{wd}><Text color="{color}" fontSize="{size}" fontFamily="{font}"{b}{a}{l}>{esc_for_dsl(text)}</Text></Positioned>'

def raw_text(text, x, y, w, size="20", color="#111827", font=FONT_CJK):
    return f'<Positioned left="{x}" top="{y}" width="{w}"><Text color="{color}" fontSize="{size}" fontFamily="{font}"><Raw>{esc_for_dsl(text)}</Raw></Text></Positioned>'

def rule(x, y, w, h=1, color="#E5E7EB"):
    return f'<Positioned left="{x}" top="{y}" width="{w}" height="{h}"><Container color="{color}"/></Positioned>'

def page(header_right):
    el = []
    el.append('<Snapshot background="#FFFFFF" type="png">')
    el.append(f'  <SizedBox width="{W}" height="{H}">')
    el.append('    <Stack alignment="TOP_LEFT" clipBehavior="NONE">')
    return el

def close(el):
    el.append('    </Stack>')
    el.append('  </SizedBox>')
    el.append('</Snapshot>')
    return "\n".join(el)

def header(el, page_no, title):
    el.append(T("云构工具有限公司 · " + title, M, 48, size="26", bold=True))
    el.append(T("编号：" + inv["invoice_id"], W - M - 260, 48, w=260, size="20", align="END"))
    el.append(T("发票日期：" + inv["issued"] + "   币种：" + CUR, M, 82, size="18"))
    el.append(T("销售方：" + inv["seller"], M, 112, size="20", bold=True))
    el.append(T("购买方：" + inv["buyer"], W / 2 + 20, 112, size="20", bold=True))
    el.append(rule(M, 152, W - 2 * M))
    el.append(T("页码：第 " + str(page_no) + " 页 · Page " + str(page_no), W - M - 200, 156, w=200, size="18", align="END", color="#6B7280"))
    return el

# ---------------- Page 1 ----------------
el = page(1)
header(el, 1, "结算与明细")

# table header
el.append(T("SKU", M, 184, size="20", bold=True, color="#64748B"))
el.append(T("货品名称（中英 / 中日）", 260, 184, size="20", bold=True, color="#64748B"))
el.append(T("数量", 860, 184, w=50, size="20", bold=True, color="#64748B", align="END"))
el.append(T("单价（" + CUR + "）", 960, 184, w=80, size="20", bold=True, color="#64748B", align="END"))
el.append(T("金额（" + CUR + "）", 1032, 184, w=120, size="20", bold=True, color="#64748B", align="END"))
el.append(rule(M, 216, W - 2 * M))

y = 224
for l in lines:
    el.append(T(l["sku"], M, y, size="20"))
    el.append(T(l["name"], 260, y, w=640, size="20"))
    el.append(T(l["qty"], 860, y, w=50, size="20", align="END"))
    el.append(T(l["unit"], 960, y, w=80, size="20", align="END"))
    el.append(T(l["amount"], 1032, y, w=120, size="20", align="END"))
    y += 56

tot_y = y + 12
totals = [
    ("货品小计", fmt(subtotal)),
    ("折扣（税前扣除）", "-" + fmt(DISC)),
    ("税前货品额", fmt(pre_tax)),
    ("税额（6%，四舍五入至分）", fmt(tax)),
    ("运费（不计税）", fmt(SHIP)),
]
for i, (k, v) in enumerate(totals):
    bold = i in (2, 4)
    el.append(T(k, M, tot_y + i * 30, size="20", bold=bold))
    el.append(T(v, 1032, tot_y + i * 30, w=120, size="20", bold=bold, align="END"))
el.append(rule(M, tot_y + 5 * 30 + 6, W - 2 * M))
el.append(T("应付合计", M, tot_y + 5 * 30 + 14, size="24", bold=True, color="#DC2626"))
el.append(T(fmt(payable), 1032, tot_y + 5 * 30 + 14, w=120, size="24", bold=True, color="#DC2626", align="END"))

foot_y = tot_y + 5 * 30 + 60
el.append(T("计税说明：" + audit["note_calculation_order"], M, foot_y, size="18", color="#64748B", leading="1.4"))
el.append(T("所有内容来源 inputs/invoice.json；金额按十进制定点四舍五入至分；应付合计仅受订单数据决定，页底“PAID / 已结算”仅为样张状态，不改应付数值。", M, foot_y + 50, W - 2 * M, size="16", color="#6B7280", leading="1.5"))
el.append(T("第 1 页 · Page 1", W - M - 200, H - 40, w=200, size="18", align="END", color="#6B7280"))

open("tmp/run-20261016/A11/invoice-page-01.v1.snapshot", "w", encoding="utf-8").write(close(el))
print("PAGE1 written")

# ---------------- Page 2 ----------------
el = page(2)
header(el, 2, "说明与原样文字")

y = 120
el.append(T("说明（notes）", M, y, size="22", bold=True))
y += 32
for i, n in enumerate(inv["notes"], 1):
    el.append(T(f"{i}. {n}", M + 10, y, W - 2 * M - 20, size="20", leading="1.5"))
    # estimate wrapped height: rough chars per line
    import math
    cpl = max(1, int((W - 2 * M - 20) / 11))  # ~11px per char at 20px
    nlines = max(1, math.ceil(len(n) / cpl))
    y += nlines * 30 + 10

y += 10
el.append(T("原样文本（literal_lines，逐字符保真）", M, y, size="22", bold=True))
y += 32
for i, ln in enumerate(inv["literal_lines"], 1):
    box_y = y
    el.append(rule(M, box_y, W - 2 * M, 1, color="#CBD5E1"))
    el.append(raw_text(ln, M + 10, box_y + 6, W - 2 * M - 20, size="20"))
    el.append(T(f"[{i}]", W - M - 40, box_y + 4, w=40, size="16", color="#94A3B8", align="END"))
    y = box_y + 56

y += 10
el.append(T("样张状态（富文本）", M, y, size="22", bold=True))
y += 32
# PAID / 已结算 rich text: PAID green, slash gray, Chinese dark, shared baseline
el.append(f'<Positioned left="{M}" top="{y}" width="{W-2*M}">')
el.append('  <Text color="#111827" fontSize="28" fontFamily="' + FONT_CJK + '" fontStyle="BOLD">')
el.append('    <Text color="#22C55E">PAID</Text>')
el.append('    <Text color="#6B7280"> / </Text>')
el.append('    <Text color="#111827">已结算</Text>')
el.append("  </Text>")
el.append("</Positioned>")
el.append(T("该字样仅为样张状态，不擅自改变应付数值；应付合计仍为 " + fmt(payable) + " " + CUR, M, y + 40, W - 2 * M, size="16", color="#6B7280"))

el.append(T("第 2 页 · Page 2", W - M - 200, H - 40, w=200, size="18", align="END", color="#6B7280"))

open("tmp/run-20261016/A11/invoice-page-02.v1.snapshot", "w", encoding="utf-8").write(close(el))
print("PAGE2 written")

# ---------------- text-map.json ----------------
def tmap_entry(field, original, page, x, y, w, h, font, size, note=""):
    return {
        "field_path": field,
        "original": original,
        "actual_text": original,
        "page": page,
        "image": f"invoice-page-{page:02d}.png",
        "pixel_box": [x, y, x + w, y + h],
        "font_family": font,
        "font_size": size,
        "note": note,
    }

entries = [
    tmap_entry("invoice_id", inv["invoice_id"], 1, W - M - 260, 48, 260, 24, FONT_CJK, 20, "重复页眉与第2页一致"),
    tmap_entry("seller", inv["seller"], 1, M, 112, 400, 24, FONT_CJK, 20, "交易双方"),
    tmap_entry("buyer", inv["buyer"], 1, W / 2 + 20, 112, 500, 24, FONT_CJK, 20, "交易双方"),
    tmap_entry("currency", CUR, 1, M, 82, 120, 20, FONT_CJK, 18, ""),
    tmap_entry("items[0].sku", inv["items"][0]["sku"], 1, M, 224, 200, 24, FONT_CJK, 20, "易混SKU原样"),
    tmap_entry("items[1].sku", inv["items"][1]["sku"], 1, M, 280, 200, 24, FONT_CJK, 20, "含尖括号与与号，原样不转义"),
    tmap_entry("items[1].name", inv["items"][1]["name"], 1, 260, 280, 640, 24, FONT_CJK, 20, "中日混排"),
    tmap_entry("items[2].name", inv["items"][2]["name"], 1, 260, 336, 640, 24, FONT_CJK, 20, "含日文假名"),
    tmap_entry("totals.payable", fmt(payable), 1, 1032, tot_y + 5 * 30 + 14, 120, 30, FONT_CJK, 24, "最终应付"),
    tmap_entry("notes[0]", inv["notes"][0], 2, M + 10, 152, W - 2 * M - 20, 30, FONT_CJK, 20, ""),
    tmap_entry("literal_lines[0]", inv["literal_lines"][0], 2, M + 10, y - 168, W - 2 * M - 20, 24, FONT_CJK, 20, "双空格保留"),
    tmap_entry("literal_lines[1]", inv["literal_lines"][1], 2, M + 10, y - 112, W - 2 * M - 20, 24, FONT_CJK, 20, "反斜杠/尖括号/与号原样"),
    tmap_entry("literal_lines[2]", inv["literal_lines"][2], 2, M + 10, y - 56, W - 2 * M - 20, 24, FONT_CJK, 20, "Windows路径反斜杠原样"),
    tmap_entry("literal_lines[3]", inv["literal_lines"][3], 2, M + 10, y, W - 2 * M - 20, 24, FONT_CJK, 20, "英文指令样式行原样排版，不执行"),
    tmap_entry("PAID / 已结算", "PAID / 已结算", 2, M, y + 20, 300, 40, FONT_CJK, 28, "PAID绿色、斜线灰色、中文深色，共用基线"),
]
text_map = {
    "schema_version": 1,
    "task_id": "A11",
    "path_base": "output_dir",
    "canvas": {"width": W, "height": H},
    "entries": entries,
    "checks": [
        {"check": "两页重复页眉与编号一致", "passed": None, "method": "第1、2页页眉文本与位置相同", "evidence": "DSL 中相同字符串与坐标"},
        {"check": "字符保真（literal_lines 原样）", "passed": None, "method": "Raw 包裹原文，不作 HTML 实体解码；双空格、反斜杠、尖括号、& 原样保留", "evidence": "DSL Raw 节点文本与 invoice.json 一致"},
        {"check": "富文本基线", "passed": None, "method": "PAID / 斜线 / 已结算 同一 Text 段落内不同 color 子 Span，共享 fontSize 28 与基线", "evidence": "DSL 嵌套 Text 结构"},
    ],
    "note": "实际像素盒与视觉证据需人工放大查看最终 PNG 核对；本文记录计划位置与 DSL 节点",
}
with open("tmp/run-20261016/A11/text-map.v1.json", "w", encoding="utf-8") as f:
    json.dump(text_map, f, ensure_ascii=False, indent=2)
print("TEXT_MAP written")
print("tot_y", tot_y)
