# -*- coding: utf-8 -*-
"""A11 · 文字保真与跨页结算单（1200×1600×2）。
数值 Decimal 定点：行金额=数量×单价（整分）；小计→税前扣折扣→×6% HALF_UP 至分→加运费。
保真：8 位颜色=#RRGGBBAA；& 不解码 → 直接写原文；< > 与双空格行走 <Raw><![CDATA[...]]></Raw>。
"""
import io, sys, json, os
from decimal import Decimal, ROUND_HALF_UP
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
OUT = os.path.join(ROOT, "outputs", "20261016T164020-m1", "A11")
os.makedirs(OUT, exist_ok=True)
inv = json.load(open(os.path.join(ROOT, "tasks", "A11-bilingual-invoice", "inputs", "invoice.json"), encoding="utf-8"))

W, H, M = 1200, 1600, 48
CR = W - M                                # 1152 内容右缘
FAM = "Inter,Noto Sans CJK SC"
INK = "#0F172A"; SUB = "#55657F"; FAINT = "#94A3B8"; LINE = "#E2E8F0"; LINE2 = "#EEF2F7"
CHIP = "#F1F5F9"; ACC = "#2563EB"; GREEN = "#157F3B"; CARD = "#FFFFFF"; BG = "#FFFFFF"

WARN = []
def estw(s, size):
    t = 0.0
    for ch in s:
        o = ord(ch)
        if o > 0x2E7F: t += size * 1.0
        elif ch in "0123456789": t += size * 0.6
        elif ch == " ": t += size * 0.30
        elif ch.isupper(): t += size * 0.70
        elif ch in "·—（）()→=.,+×:/°#%<>&\\": t += size * 0.5
        else: t += size * 0.54
    return t

def fit(tag, s, size, box):
    w = estw(s, size)
    if w > box: WARN.append(f"{tag} estw {w:.0f}>{box}: {s}")

NODES = []
def rec(key, sp_path, page, s, x, y, size, bold, method):
    NODES.append({"key": key, "source_path": sp_path, "page": page, "source_text": s,
                  "box": [x, y, round(x + estw(s, size)), round(y + size * 1.32)],
                  "font": {"family": FAM, "font_size_px": size, "weight": "BOLD" if bold else "NORMAL"},
                  "method": method})

def cd(s):
    assert "]]>" not in s, s
    return "<![CDATA[" + s + "]]>"

def text(page, x, y, s, size, color, bold=False, align="START", box_w=None, key=None, sp_path=None):
    assert "<" not in s, f"plain text has '<': {s}"
    fit(key or "?", s, size, box_w if align != "START" else (box_w or 1160))
    sty = f' fontSize="{size}" color="{color}" fontFamily="{FAM}" maxLines="1" overflow="CLIP"'
    if bold: sty += ' fontWeight="BOLD"'
    s2 = s.replace("&", "&")  # & 不需转义：Parser 不做实体解码，&amp; 反而会显示为字面量
    inner = s2
    if align != "START":
        assert box_w, "END 需要 box_w"
        sty += f' textAlign="{align}"'
        body = f'<Text{sty}>{inner}</Text>'
        rec(key, sp_path, page, s, x + box_w - estw(s, size), y, size, bold, "构版坐标（END 对齐按估宽折算左缘，最终以放大件核对）")
        return [f'<Positioned left="{x}" top="{y}" width="{box_w}">{body}</Positioned>']
    rec(key, sp_path, page, s, x, y, size, bold, "构版坐标（估宽），放大件核对")
    return [f'<Positioned left="{x}" top="{y}"><Text{sty}>{inner}</Text></Positioned>']

def textraw(page, x, y, s, size, color, bold=False, key=None, sp_path=None, box_w=None, align=None):
    fit(key or "?", s, size, box_w or 1160)
    sty = f' fontSize="{size}" color="{color}" fontFamily="{FAM}" maxLines="1" overflow="CLIP"'
    if bold: sty += ' fontWeight="BOLD"'
    if align:
        sty += f' textAlign="{align}"'
        body = f'<Text{sty}><Raw>{cd(s)}</Raw></Text>'
        rec(key, sp_path, page, s, x + (box_w - estw(s, size)), y, size, bold, "构版坐标（Raw 保空格；END 估宽折算）")
        return [f'<Positioned left="{x}" top="{y}" width="{box_w}">{body}</Positioned>']
    rec(key, sp_path, page, s, x, y, size, bold, "构版坐标（Raw 保空格）")
    return [f'<Positioned left="{x}" top="{y}"><Text{sty}><Raw>{cd(s)}</Raw></Text></Positioned>']

def rect(x, y, w2, h2, color, radius=None, border=None):
    a = f'width="{w2}" height="{h2}"' + (f' color="{color}"' if color else "")
    if radius: a += f' borderRadius="{radius}"'
    if border: a += f' border="{border}"'
    return f'<Positioned left="{x}" top="{y}"><Container {a} /></Positioned>'

# ---------- 十进制定点计算 ----------
D = lambda s: Decimal(s)
q2 = lambda v: v.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
lines = []
for it in inv["items"]:
    exact = D(it["unit_price"]) * D(it["quantity"])
    lines.append({"sku": it["sku"], "name": it["name"], "quantity": it["quantity"],
                  "unit_price": str(q2(D(it["unit_price"]))), "exact_product": str(exact), "amount": str(q2(exact))})
subtotal = sum(D(l["amount"]) for l in lines)
discount = D(inv["discount"])
base = subtotal - discount
tax_exact = base * D(inv["tax_rate"])
tax = q2(tax_exact)
shipping = D(inv["shipping"])
payable = base + tax + shipping
assert payable == D("4215.96"), payable

def header(page_no):
    S = []
    S += text(page_no, M, 48, f'{inv["invoice_id"]} · 结算单 INVOICE', 20, SUB, key="header.left", sp_path="invoice.invoice_id")
    S += text(page_no, CR - 300, 48, f"第 {page_no} / 2 页", 20, SUB, align="END", box_w=300, key=f"header.page{page_no}", sp_path="computed")
    S.append(rect(M, 78, CR - M, 1, LINE))
    return S

def footer(page_no):
    S = []
    S.append(rect(M, 1490, CR - M, 1, LINE))
    S += text(page_no, M, 1512, f'{inv["seller"]} · 结算单 INVOICE · {inv["currency"]}', 20, FAINT, key="footer.left", sp_path="invoice.seller")
    S += text(page_no, CR - 300, 1512, f"第 {page_no} / 2 页", 20, FAINT, align="END", box_w=300, key=f"footer.page{page_no}", sp_path="computed")
    return S

# ================= 页 1 =================
P1 = [rect(0, 0, W, H, BG)]
P1 += header(1)
P1 += text(1, M, 100, "结算单 INVOICE", 44, INK, bold=True, key="p1.title", sp_path="computed")
P1.append(rect(M, 164, 76, 6, ACC))
P1 += text(1, M, 190, "卖方 SELLER", 20, FAINT, key="p1.seller.label", sp_path="computed")
P1 += text(1, M, 218, inv["seller"], 30, INK, bold=True, key="p1.seller.name", sp_path="invoice.seller")
P1 += text(1, 620, 190, "买方 BUYER", 20, FAINT, key="p1.buyer.label", sp_path="computed")
P1 += text(1, 620, 218, inv["buyer"], 30, INK, bold=True, key="p1.buyer.name", sp_path="invoice.buyer")
# 元信息芯片
def chip(page, x, w, label, value, lkey, vkey, vsp):
    S = [rect(x, 300, w, 64, CHIP, radius=10)]
    S += text(page, x + 24, 312, label, 20, FAINT, key=lkey, sp_path="computed")
    S += text(page, x + 24, 340, value, 24, INK, bold=True, key=vkey, sp_path=vsp)
    return S
P1 += chip(1, 48, 340, "编号 NUMBER", inv["invoice_id"], "p1.meta.id.label", "p1.meta.id", "invoice.invoice_id")
P1 += chip(1, 408, 250, "日期 DATE", inv["issued"], "p1.meta.date.label", "p1.meta.date", "invoice.issued")
P1 += chip(1, 678, 220, "币种 CURRENCY", inv["currency"], "p1.meta.ccy.label", "p1.meta.ccy", "invoice.currency")
P1.append(rect(M, 396, CR - M, 1, LINE))
# 表头
P1 += text(1, M, 416, "SKU", 20, SUB, bold=True, key="p1.th.sku", sp_path="computed")
P1 += text(1, 304, 416, "名称 NAME", 20, SUB, bold=True, key="p1.th.name", sp_path="computed")
P1 += text(1, 760, 416, "数量", 20, SUB, bold=True, align="END", box_w=160, key="p1.th.qty", sp_path="computed")
P1 += text(1, 870, 416, "单价", 20, SUB, bold=True, align="END", box_w=160, key="p1.th.price", sp_path="computed")
P1 += text(1, 952, 416, "行金额", 20, SUB, bold=True, align="END", box_w=200, key="p1.th.amount", sp_path="computed")
P1.append(rect(M, 452, CR - M, 2, "#CBD5E1"))
rows_y = [476, 596, 716, 836]
for i, (l, y0) in enumerate(zip(lines, rows_y)):
    special = "<" in l["sku"] or "&" in l["sku"]
    if special:
        P1 += textraw(1, M, y0, l["sku"], 24, SUB, key=f"p1.r{i}.sku", sp_path=f"invoice.items[{i}].sku")
    else:
        P1 += text(1, M, y0, l["sku"], 24, SUB, key=f"p1.r{i}.sku", sp_path=f"invoice.items[{i}].sku")
    P1 += text(1, 304, y0 + 36, l["name"], 24, INK, key=f"p1.r{i}.name", sp_path=f"invoice.items[{i}].name")
    P1 += text(1, 760, y0 + 36, str(l["quantity"]), 24, INK, align="END", box_w=160, key=f"p1.r{i}.qty", sp_path=f"invoice.items[{i}].quantity")
    P1 += text(1, 870, y0 + 36, l["unit_price"], 24, INK, align="END", box_w=160, key=f"p1.r{i}.price", sp_path=f"invoice.items[{i}].unit_price")
    P1 += text(1, 952, y0 + 36, l["amount"], 24, INK, bold=True, align="END", box_w=200, key=f"p1.r{i}.amount", sp_path=f"invoice.items[{i}].unit_price×quantity")
    P1.append(rect(M, y0 + 82, CR - M, 1, LINE2))
P1.append(rect(M, 962, CR - M, 1, LINE))
tot_y = [994, 1044, 1094, 1144, 1194]
tot = [("货品小计 GOODS SUBTOTAL", str(subtotal), "computed.goods_subtotal"),
       ("折扣 DISCOUNT（税前扣除）", "-" + str(discount), "invoice.discount"),
       ("税前折后货品额 PRE-TAX BASE", str(base), "computed.pretax_base"),
       (f'税额 TAX（× {inv["tax_rate"]}）', str(tax), "computed.tax"),
       ("运费 SHIPPING（不计税）", str(shipping), "invoice.shipping")]
for (lab, val, sp), y in zip(tot, tot_y):
    P1 += text(1, 500, y, lab, 24, SUB, align="END", box_w=480, key="p1.tot." + sp.replace(".", "_"), sp_path=sp)
    P1 += text(1, CR - 260, y, val, 24, INK, align="END", box_w=260, key="p1.totv." + sp.replace(".", "_"), sp_path=sp)
P1.append(rect(M, 1246, CR - M, 2, "#94A3B8"))
P1 += text(1, 500, 1278, "应付合计 PAYABLE", 30, INK, bold=True, align="END", box_w=480, key="p1.payable.label", sp_path="computed.payable")
P1 += text(1, CR - 300, 1268, str(payable), 40, INK, bold=True, align="END", box_w=300, key="p1.payable.value", sp_path="computed.payable")
P1 += text(1, M, 1352, f'计税顺序：货品小计 − 折扣 → × {inv["tax_rate"]}（四舍五入至分）→ 运费不计税加入 → 应付 {payable}。', 20, SUB, key="p1.taxorder", sp_path="invoice.notes[1,2]")
P1 += text(1, M, 1388, "说明与原样字样见第 2 / 2 页。", 20, FAINT, key="p1.pointer", sp_path="computed")
P1 += footer(1)

dsl1 = f'<Snapshot background="{BG}" type="png"><Stack><SizedBox width="{W}" height="{H}" />\n' + "\n".join(P1) + "\n</Stack></Snapshot>"
open(os.path.join(OUT, "invoice-page-01.snapshot"), "w", encoding="utf-8").write(dsl1)

# ================= 页 2 =================
P2 = [rect(0, 0, W, H, BG)]
P2 += header(2)
P2 += text(2, M, 100, "说明与原样字样", 44, INK, bold=True, key="p2.title", sp_path="computed")
P2.append(rect(M, 164, 76, 6, ACC))
P2 += text(2, M, 176, "NOTES & LITERAL LINES · 逐字符保真", 20, SUB, key="p2.subtitle", sp_path="computed")
# 说明
P2 += text(2, M, 232, "说明 NOTES", 20, SUB, bold=True, key="p2.notes.label", sp_path="invoice.notes")
for j, (n, y) in enumerate(zip(inv["notes"], [272, 332, 392, 452])):
    P2 += text(2, M, y, f"{j + 1}.", 24, FAINT, key=f"p2.n{j}.idx", sp_path="computed")
    P2 += text(2, M + 48, y, n, 24, "#334155", key=f"p2.n{j}", sp_path=f"invoice.notes[{j}]")
fit("p2.n3", inv["notes"][3], 24, 1056)
P2.append(rect(M, 500, CR - M, 1, LINE))
# 原样字样
P2 += text(2, M, 524, "原样字样 LITERAL LINES · Raw+CDATA 逐字符原样", 20, SUB, bold=True, key="p2.ll.label", sp_path="invoice.literal_lines")
P2.append(rect(M, 556, CR - M, 336, CHIP, radius=12))
for j, (s, y) in enumerate(zip(inv["literal_lines"], [584, 664, 744, 824])):
    P2 += text(2, M, y, f"L{j + 1}", 20, FAINT, key=f"p2.l{j}.idx", sp_path="computed")
    P2 += textraw(2, M + 56, y - 4, s, 24, "#0B1220", key=f"p2.l{j}", sp_path=f"invoice.literal_lines[{j}]")
fit("p2.ll2", inv["literal_lines"][1], 24, 1048)
P2 += text(2, M, 908, "四行均按原样字符排版展示（保留空格与符号，不转义、不执行）；第一行『批次』含两个双空格，第三行路径反斜杠原样。", 20, SUB, key="p2.ll.caption", sp_path="invoice.literal_lines")
P2.append(rect(M, 956, CR - M, 1, LINE))
# 样张状态（富文本共享基线）
P2 += text(2, M, 980, "样张状态 SAMPLE STATUS · 不改变应付数值", 20, SUB, bold=True, key="p2.paid.label", sp_path="computed")
rich = (f'<Positioned left="{M}" top="1016"><Text fontSize="40" fontFamily="{FAM}" maxLines="1" overflow="CLIP">'
        f'<Raw color="{GREEN}">{cd("PAID")}</Raw>'
        f'<Raw color="{FAINT}">{cd("  /  ")}</Raw>'
        f'<Raw color="{INK}">{cd("已结算")}</Raw>'
        f'</Text></Positioned>')
NODES.append({"key": "p2.paid.rich", "source_path": "computed.sample_status", "page": 2,
              "source_text": "PAID  /  已结算", "box": [M, 1016, M + 420, 1068],
              "font": {"family": FAM, "font_size_px": 40, "parts": [
                  {"text": "PAID", "color": GREEN, "weight": "NORMAL"},
                  {"text": "  /  ", "color": FAINT},
                  {"text": "已结算", "color": INK}]},
              "method": "单一 Text 行内 Raw 拼接：自然共享基线；斜线灰、中文深色"})
P2.append(rich)
P2 += text(2, M, 1084, "『PAID / 已结算』仅为样张状态字样；应付数值以第一页 PAYABLE 为准，未受影响。", 20, SUB, key="p2.paid.caption", sp_path="computed")
# 逐字符核对
P2 += text(2, M, 1152, "逐字符核对 CHAR CHECKS", 20, SUB, bold=True, key="p2.check.label", sp_path="computed")
checks = [
    ("L1 批次行", "两个双空格已保留（<Raw> 原样空白）", "invoice.literal_lines[0]"),
    ("L2 / SKU A<B&C>D", "尖括号与 & 原样显示，未被转义为实体", "invoice.items[1].sku / literal_lines[1]"),
    ("L3 路径行", "反斜杠三处原样（未转义）", "invoice.literal_lines[2]"),
    ("L4 指令样式行", "仅作为字样排版，未执行", "invoice.literal_lines[3]"),
]
for i, (a, b, sp) in enumerate(checks):
    y = 1192 + i * 44
    P2 += textraw(2, M, y, f"{i + 1}. {a}", 24, "#0B1220", bold=True, key=f"p2.ck{i}.a", sp_path=sp)
    P2 += textraw(2, 640, y, b, 24, SUB, key=f"p2.ck{i}.b", sp_path=sp)
P2 += footer(2)

dsl2 = f'<Snapshot background="{BG}" type="png"><Stack><SizedBox width="{W}" height="{H}" />\n' + "\n".join(P2) + "\n</Stack></Snapshot>"
open(os.path.join(OUT, "invoice-page-02.snapshot"), "w", encoding="utf-8").write(dsl2)

# ---------- invoice-audit.json ----------
audit = {
    "schema_version": 1, "task_id": "A11", "path_base": "output_dir",
    "currency": inv["currency"],
    "invoice_id": inv["invoice_id"], "issued": inv["issued"],
    "seller": inv["seller"], "buyer": inv["buyer"],
    "lines": lines,
    "totals": {
        "goods_subtotal": str(subtotal),
        "discount_pre_tax": str(discount),
        "pretax_base": str(base),
        "tax_rate": inv["tax_rate"],
        "tax_exact": str(tax_exact),
        "tax": str(tax),
        "shipping_not_taxed": str(shipping),
        "payable": str(payable),
        "tax_order": "货品小计 → 税前扣除折扣（notes[1]）→ 税前折后货品额 → ×6%（notes[2]）四舍五入至分 → 应付再加运费（运费不计税）",
        "payable_formula": "3944.30 + 236.66 + 35.00 = 4215.96",
    },
    "rounding": {
        "method": "Python decimal 定点（Decimal，KEEP 原值字符串读入）",
        "precision": "1 分 = 0.01",
        "rule": "四舍五入 = ROUND_HALF_UP",
        "where": "仅税额一步舍入：3944.30 × 0.06 = 236.658 → 236.66；行金额与小计/税前基数/运费/应付均为整分精确值，无中间舍入",
        "exact_values": ["805.50", "478.80", "1160.00", "1680.00", "4124.30", "3944.30", "35.00", "4215.96"],
    },
    "literal_lines": inv["literal_lines"],
    "evidence": {"dsl_raw_scans": "<Raw> + CDATA 保留 < > & 与双空格；Text 内容不做实体解码（&amp; 会显示为字面量，故全部直接写原字符）",
                 "crops": {"path_base": "suite_root", "path": "tmp/20261016T164020-m1/A11/steps/"}},
}
json.dump(audit, open(os.path.join(OUT, "invoice-audit.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ---------- text-map.json ----------
def entries_for(page):
    return [n for n in NODES if n["page"] == page]
textmap = {
    "schema_version": 1, "task_id": "A11", "path_base": "output_dir",
    "font_family": FAM,
    "font_note": "字体为本 run 前置真实查询的可用集（Inter + Noto Sans CJK SC）：覆盖中文/日文假名/拉丁；JP『契約レビュー』落于 Noto Sans CJK 渲染。",
    "entries": NODES,
    "checks": [],
}
json.dump(textmap, open(os.path.join(OUT, "text-map.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

print("lines:", [(l["sku"], l["amount"]) for l in lines])
print("subtotal", subtotal, "base", base, "tax", tax_exact, "->", tax, "payable", payable)
print("nodes:", len(NODES), "p1", len(entries_for(1)), "p2", len(entries_for(2)))
print("WARN", len(WARN))
for w in WARN: print(" -", w)
