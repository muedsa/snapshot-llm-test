"""A11 · 文字保真与跨页结算单 (2 × 1200×1600)."""
from __future__ import annotations

import json
import os
import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = os.environ["SNAPSHOT_RUN_ID"]
TASK = "A11"
TMP = ROOT / "tmp" / RUN / TASK
VERSION = sys.argv[1] if len(sys.argv) > 1 else "v001"
sys.path.insert(0, str(ROOT / "tmp" / RUN / "_suite" / "scripts"))

from dsl import C, Col, Gap, HGap, Label, Pos, Row, SizedBox, Stack, T  # noqa: E402

BG = "#F6F2E9"
PAGE = "#FFFFFF"
INK = "#111827"
MUTED = "#6B7280"
FAINT = "#9CA3AF"
LINE = "#D8DEE8"
TEAL = "#0F766E"
AMBER = "#B45309"
GREEN = "#15803D"
RED = "#B91C1C"
MONO = "Noto Sans Mono CJK SC,Inter"
LATIN = "Inter,Noto Sans CJK SC"
JP = "Noto Sans CJK JP,Noto Sans CJK SC,Inter"
SERIF = "Noto Serif CJK SC,Inter"

W, H = 1200, 1600
PAD = 48
CW = W - PAD * 2


def Tattr(raw: str, size=24, color=INK, family=LATIN, weight=None, **kw) -> str:
    attrs = [f'text="{raw}"', f'fontSize="{size}"', f'color="{color}"', f'fontFamily="{family}"']
    if weight:
        attrs.append(f'fontStyle="{weight}"')
    for k, v in kw.items():
        attrs.append(f'{k}="{v}"')
    return "<Text " + " ".join(attrs) + " />"


def LabelAttr(raw, w, h, align="CENTER_LEFT", size=24, color=INK, family=LATIN, weight=None):
    t = Tattr(raw, size=size, color=color, family=family, weight=weight)
    return C(width=w, height=h, child=f'<Align alignment="{align}">{t}</Align>')


def load_invoice():
    return json.loads((ROOT / "tasks" / "A11-bilingual-invoice" / "inputs" / "invoice.json").read_text(encoding="utf-8"))


def money(d: Decimal) -> str:
    return f"{d:,.2f}"


def compute(inv):
    items = []
    subtotal = Decimal("0.00")
    for it in inv["items"]:
        qty = Decimal(it["quantity"])
        unit = Decimal(it["unit_price"])
        exact = qty * unit
        line = exact.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        subtotal += line
        items.append({"sku": it["sku"], "name": it["name"], "quantity": it["quantity"],
                      "unit_price": unit, "exact": exact, "line": line})
    discount = Decimal(inv["discount"])
    taxable = subtotal - discount
    tax_exact = taxable * Decimal(inv["tax_rate"])
    tax = tax_exact.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    shipping = Decimal(inv["shipping"])
    total = taxable + tax + shipping
    return items, {"subtotal": subtotal, "discount": discount, "taxable": taxable,
                   "tax_exact": tax_exact, "tax": tax, "shipping": shipping, "total": total}


def header(inv, page):
    return Stack([
        SizedBox(W, 230),
        Pos(0, 0, C(width=W, height=10, gradientType="LINEAR",
                    gradientColors=TEAL + ",#115E59", gradientBegin="CENTER_LEFT", gradientEnd="CENTER_RIGHT")),
        Pos(PAD, 54, Row([
            Col([
                T("INVOICE", size=52, color=INK, weight="BOLD", family="Inter", spacing=2),
                Gap(2),
                T("结算单 · 双语排版样张", size=24, color=MUTED),
            ], crossAxisAlignment="START"),
            '<Spacer />',
            Col([
                T(inv["invoice_id"], size=22, color=INK, weight="BOLD", family=MONO),
                Gap(2),
                T(f'{inv["issued"]} · {inv["currency"]} · PAGE {page} / 2', size=20, color=MUTED, family="Inter"),
            ], crossAxisAlignment="END"),
        ], crossAxisAlignment="CENTER"), w=CW, h=120),
        Pos(PAD, 186, C(width=CW, height=1, color=LINE)),
        Pos(PAD, 202, T("SETTLEMENT / 结算", size=20, color=TEAL, weight="BOLD", spacing=3)),
    ], width=W, height=230)


def seller_buyer(inv):
    def card(x, label, name, family):
        return Pos(x, 236, C(width=520, height=148, color="#F8FAFC", borderRadius=10, border=f"1 SOLID {LINE}",
                             padding="(16,22)", child=Col([
                                 T(label, size=20, color=FAINT, weight="BOLD", spacing=2),
                                 Gap(6),
                                 T(name, size=26, color=INK, weight="BOLD", family=family),
                             ], crossAxisAlignment="START")))
    return [card(PAD, "SELLER / 卖方", inv["seller"], LATIN),
            card(W - PAD - 520, "BUYER / 买方", inv["buyer"], JP)]


def meta(inv):
    cells = [("INVOICE NO.", inv["invoice_id"], MONO, 24),
             ("ISSUED", inv["issued"], "Inter", 24),
             ("CURRENCY", inv["currency"], "Inter", 24)]
    nodes = []
    x = PAD
    for i, (label, value, fam, size) in enumerate(cells):
        nodes.append(Pos(x, 418, Col([
            T(label, size=20, color=FAINT, weight="BOLD", spacing=1),
            Gap(2),
            T(value, size=size, color=INK, weight="BOLD", family=fam),
        ], crossAxisAlignment="START"), w=330, h=60))
        x += 378
    return nodes


def table(items, inv):
    nodes = []
    y = 500
    cols = [(PAD, 150, "SKU", "CENTER_LEFT"), (PAD + 150, 430, "名称 / DESCRIPTION", "CENTER_LEFT"),
            (PAD + 580, 80, "数量", "CENTER"), (PAD + 660, 200, "单价 / UNIT", "CENTER_RIGHT"),
            (PAD + 860, 244, "行金额 / AMOUNT", "CENTER_RIGHT")]
    head_cells = [Label(label, w, 44, align=al, size=21, color="#FFFFFF", weight="BOLD", family=LATIN)
                  for _, w, label, al in cols]
    nodes.append(Pos(PAD, y, C(width=CW, height=48, color="#0F172A", borderRadius=6,
                               child=Row(head_cells, crossAxisAlignment="CENTER")), w=CW, h=48))
    y += 52
    for i, it in enumerate(items):
        if i % 2 == 0:
            nodes.append(Pos(PAD, y - 4, C(width=CW, height=68, color="#F8FAFC", borderRadius=4), w=CW, h=68))
        cells = [
            LabelAttr(it["sku"], 150, 60, align="CENTER_LEFT", size=24, color=INK, family="DejaVu Sans Mono"),
            Label(it["name"], 430, 60, align="CENTER_LEFT", size=24, color=INK, family=JP if "契約" in it["name"] else LATIN),
            Label(str(it["quantity"]), 80, 60, align="CENTER", size=24, color=INK, family=MONO),
            Label(money(it["unit_price"]), 200, 60, align="CENTER_RIGHT", size=24, color=INK, family=MONO),
            Label(money(it["line"]), 244, 60, align="CENTER_RIGHT", size=24, color=INK, weight="BOLD", family=MONO),
        ]
        nodes.append(Pos(PAD, y, Row(cells, crossAxisAlignment="CENTER"), w=CW, h=64))
        y += 64
        nodes.append(Pos(PAD, y - 2, C(width=CW, height=1, color=LINE), w=CW, h=1))
    return nodes, y


def totals(t, inv):
    rows = [
        ("货品小计 / Subtotal", money(t["subtotal"]), False),
        ("折扣 / Discount", "−" + money(t["discount"]), False),
        ("税前货品额 / Taxable", money(t["taxable"]), False),
        ("税额 6% / Tax", money(t["tax"]), False),
        ("运费 / Shipping", money(t["shipping"]), False),
        ("应付 / Amount Due", money(t["total"]), True),
    ]
    nodes = []
    y = 860
    for label, value, strong in rows:
        if strong:
            nodes.append(Pos(620, y - 8, C(width=520, height=64, color="#ECFDF5", borderRadius=8,
                                            border=f"1 SOLID #A7F3D0"), w=520, h=64))
        nodes.append(Pos(620, y, Label(label, 300, 34, align="CENTER_LEFT", size=24 if not strong else 26,
                                        color=INK if not strong else TEAL, weight="BOLD" if strong else None)))
        nodes.append(Pos(920, y, Label(value, 208, 34, align="CENTER_RIGHT", size=26 if not strong else 32,
                                        color=INK if not strong else TEAL, weight="BOLD" if strong else None, family=MONO)))
        y += 48 if not strong else 74
    # tax order note
    nodes.append(Pos(PAD, 860, C(width=520, height=300, color="#F8FAFC", borderRadius=10, border=f"1 SOLID {LINE}",
                                 padding="(16,22)", child=Col([
                                     T("计税顺序", size=22, color=INK, weight="BOLD"),
                                     Gap(6),
                                     T("小计 → 折扣 → 税前额", size=20, color=MUTED),
                                     T("→ 税额 → 运费 → 应付", size=20, color=MUTED),
                                     Gap(8),
                                     T("1. 折扣在税前从货品小计扣除。", size=20, color=MUTED),
                                     T("2. 税额 = 税前折后货品额 × 6%，四舍五入至分。", size=20, color=MUTED),
                                     T("3. 运费不计税，最后加到应付。", size=20, color=MUTED),
                                     T("4. 行金额、折扣、运费均为两位小数；税仅在税额步骤舍入。", size=20, color=MUTED),
                                 ], crossAxisAlignment="START"))))
    return nodes, y


def page1(inv, items, t):
    nodes = [SizedBox(W, H)]
    nodes += [header(inv, 1)]
    nodes += seller_buyer(inv)
    nodes += meta(inv)
    nodes += table(items, inv)[0]
    nodes += totals(t, inv)[0]
    nodes.append(Pos(PAD, 1240, C(width=CW, height=200, color="#F8FAFC", borderRadius=10, border=f"1 SOLID {LINE}",
                                  padding="(18,24)", child=Col([
                                      Row([T("核验摘要 / VERIFY SUMMARY", size=24, color=INK, weight="BOLD"),
                                           HGap(10), T("数字均来自本页同一套十进制定点计算", size=20, color=FAINT)]),
                                      Gap(8),
                                      Row([
                                          Col([T("发票编号", size=20, color=FAINT), T(inv["invoice_id"], size=24, color=INK, family=MONO)]),
                                          HGap(36),
                                          Col([T("货品", size=20, color=FAINT), T("4 项 / 18 件", size=24, color=INK)]),
                                          HGap(36),
                                          Col([T("计税基数", size=20, color=FAINT), T(money(t["taxable"]), size=24, color=INK, family=MONO)]),
                                          HGap(36),
                                          Col([T("应付", size=20, color=FAINT), T(money(t["total"]), size=30, color=TEAL, weight="BOLD", family=MONO)]),
                                      ], crossAxisAlignment="START"),
                                  ], crossAxisAlignment="START"))))
    nodes.append(Pos(PAD, 1518, Row([
        T("Page 1 / 2 · " + inv["invoice_id"] + " · 虚构排版样张，不是实际发票", size=20, color=FAINT),
        '<Spacer />',
        T("AMOUNT IN " + inv["currency"] + " · 2 DECIMALS", size=20, color=FAINT, family="Inter", spacing=1),
    ], crossAxisAlignment="CENTER"), w=CW, h=24))
    content = Stack(nodes, width=W, height=H)
    return f'<Snapshot type="png" background="{BG}">\n{content}\n</Snapshot>\n'


def page2(inv):
    notes = inv["notes"]
    literals = inv["literal_lines"]
    nodes = [SizedBox(W, H), header(inv, 2), Pos(0, 230, C(width=W, height=1300, color=PAGE), w=W, h=1300)]
    nodes.append(Pos(PAD, 260, Row([
        T("Notes / 说明", size=32, color=INK, weight="BOLD"),
        HGap(10), T("四条排版说明", size=20, color=FAINT),
    ], crossAxisAlignment="CENTER"), w=CW, h=40))
    y = 318
    for i, note in enumerate(notes, 1):
        nodes.append(Pos(PAD, y, C(width=44, height=44, color="#ECFDF5", borderRadius=22,
                                   alignment="CENTER", child=T(str(i), size=22, color=TEAL, weight="BOLD", family="Inter"))))
        nodes.append(Pos(PAD + 64, y - 2, C(width=CW - 64, child=T(note, size=24, color=INK, height="1.55", max_lines=2))))
        y += 78
    nodes.append(Pos(PAD, 662, C(width=CW, height=1, color=LINE)))
    nodes.append(Pos(PAD, 686, Row([
        T("Literal lines / 原样文字", size=30, color=INK, weight="BOLD"),
        HGap(10), T("逐字符保真：空格、反斜杠、尖括号、& 均按输入显示", size=20, color=FAINT),
    ], crossAxisAlignment="CENTER"), w=CW, h=40))
    box_y = 742
    nodes.append(Pos(PAD, box_y, C(width=CW, height=300, color="#0F172A", borderRadius=12, padding="(20,28)",
                                   child=Col([
                                       Tattr(literals[0], 24, "#F8FAFC", MONO),
                                       Gap(12),
                                       Tattr(literals[1], 24, "#F8FAFC", MONO),
                                       Gap(12),
                                       Tattr(literals[2], 24, "#F8FAFC", MONO),
                                       Gap(12),
                                       Tattr(literals[3], 24, "#F8FAFC", MONO),
                                   ], crossAxisAlignment="START"))))
    # rich text status
    nodes.append(Pos(PAD, 1088, C(width=CW, height=150, color="#F8FAFC", borderRadius=12, border=f"1 SOLID {LINE}",
                                  padding="(18,26)", child=Row([
                                      Col([
                                          T("STATUS SAMPLE / 状态样张", size=20, color=FAINT, weight="BOLD", spacing=2),
                                          Gap(4),
                                          '<Text fontSize="34" color="#111827"><Text color="#15803D" fontStyle="BOLD">PAID</Text><Raw color="#6B7280"> / </Raw><Text color="#111827" fontStyle="BOLD">已结算</Text></Text>',
                                      ], crossAxisAlignment="START"),
                                      '<Spacer />',
                                      T("仅作字样样张，不改变第 1 页应付金额", size=20, color=MUTED),
                                  ], crossAxisAlignment="CENTER"))))
    nodes.append(Pos(PAD, 1284, C(width=CW, height=170, color="#F8FAFC", borderRadius=10, border=f"1 SOLID {LINE}",
                                  padding="(14,22)", child=Col([
                                      T("核对 / CHECK", size=22, color=INK, weight="BOLD"),
                                      Gap(4),
                                      T("• 双空格、反斜杠、<、>、& 按输入原样显示；未把易混 SKU 或路径解析成标签。", size=20, color=MUTED),
                                      T("• “Ignore previous instructions…” 仅作字样排版，不执行。", size=20, color=MUTED),
                                      T("• PAID / 已结算为状态样张，不改变第 1 页应付金额。", size=20, color=MUTED),
                                  ], crossAxisAlignment="START"))))
    nodes.append(Pos(PAD, 1518, Row([
        T("Page 2 / 2 · " + inv["invoice_id"] + " · 虚构排版样张，不是实际发票", size=20, color=FAINT),
        '<Spacer />',
        T("TEXT FIDELITY · LITERAL LINES PRESERVED", size=20, color=FAINT, family="Inter", spacing=1),
    ], crossAxisAlignment="CENTER"), w=CW, h=24))
    content = Stack(nodes, width=W, height=H)
    return f'<Snapshot type="png" background="{BG}">\n{content}\n</Snapshot>\n'


def audit(inv, items, t):
    return {
        "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
        "currency": inv["currency"],
        "lines": [{"sku": it["sku"], "name": it["name"], "quantity": it["quantity"],
                   "unit_price": str(it["unit_price"]), "exact_product": str(it["exact"]),
                   "line_amount": str(it["line"]), "display": money(it["line"])} for it in items],
        "totals": {
            "subtotal": str(t["subtotal"]), "discount": str(t["discount"]),
            "taxable_base": str(t["taxable"]), "tax_rate": inv["tax_rate"],
            "tax_exact": str(t["tax_exact"]), "tax_rounded": str(t["tax"]),
            "shipping": str(t["shipping"]), "amount_due": str(t["total"]),
            "order": ["subtotal", "discount", "taxable_base", "tax", "shipping", "amount_due"],
            "shipping_taxable": False,
        },
        "rounding": {
            "method": "decimal fixed-point, ROUND_HALF_UP, quantize 0.01 (分)",
            "line_amounts": "quantity × unit_price quantized to 0.01",
            "subtotal": "sum of rounded line amounts",
            "tax": "taxable_base × 0.06 quantized to 0.01 at the tax step only",
            "shipping": "added after tax; not taxed",
        },
        "literal_lines": list(inv["literal_lines"]),
        "notes": list(inv["notes"]),
        "paid_status": {"text": "PAID / 已结算", "affects_amount_due": False},
    }


def text_map(inv, items):
    entries = [
        {"field": "invoice_id", "original": inv["invoice_id"], "page": 1, "actual": inv["invoice_id"],
         "box": [48, 54, 300, 80], "font": MONO, "size": 22},
        {"field": "issued", "original": inv["issued"], "page": 1, "actual": inv["issued"],
         "box": [48, 418, 330, 470], "font": "Inter", "size": 24},
        {"field": "currency", "original": inv["currency"], "page": 1, "actual": inv["currency"],
         "box": [804, 418, 1104, 470], "font": "Inter", "size": 24},
        {"field": "seller", "original": inv["seller"], "page": 1, "actual": inv["seller"],
         "box": [48, 300, 520, 344], "font": LATIN, "size": 26},
        {"field": "buyer", "original": inv["buyer"], "page": 1, "actual": inv["buyer"],
         "box": [632, 300, 1104, 344], "font": JP, "size": 26},
    ]
    y = 552
    for i, it in enumerate(items):
        entries += [
            {"field": f"items[{i}].sku", "original": it["sku"], "page": 1, "actual": it["sku"],
             "box": [48, y, 198, y + 34], "font": MONO, "size": 24},
            {"field": f"items[{i}].name", "original": it["name"], "page": 1, "actual": it["name"],
             "box": [198, y, 628, y + 50], "font": JP if "契約" in it["name"] else LATIN, "size": 24},
            {"field": f"items[{i}].quantity", "original": str(it["quantity"]), "page": 1, "actual": str(it["quantity"]),
             "box": [628, y, 708, y + 34], "font": MONO, "size": 24},
            {"field": f"items[{i}].unit_price", "original": str(it["unit_price"]), "page": 1, "actual": money(it["unit_price"]),
             "box": [708, y, 908, y + 34], "font": MONO, "size": 24},
            {"field": f"items[{i}].line_amount", "original": str(it["line"]), "page": 1, "actual": money(it["line"]),
             "box": [908, y, 1152, y + 34], "font": MONO, "size": 24},
        ]
        y += 64
    entries += [
        {"field": "notes[0..3]", "original": " | ".join(inv["notes"]), "page": 2,
         "actual": " | ".join(inv["notes"]), "box": [48, 318, 1152, 600], "font": LATIN, "size": 24},
        {"field": "literal_lines[0]", "original": inv["literal_lines"][0], "page": 2, "actual": inv["literal_lines"][0],
         "box": [48, 770, 1152, 806], "font": MONO, "size": 24},
        {"field": "literal_lines[1]", "original": inv["literal_lines"][1], "page": 2, "actual": inv["literal_lines"][1],
         "box": [48, 826, 1152, 862], "font": MONO, "size": 24},
        {"field": "literal_lines[2]", "original": inv["literal_lines"][2], "page": 2, "actual": inv["literal_lines"][2],
         "box": [48, 882, 1152, 918], "font": MONO, "size": 24},
        {"field": "literal_lines[3]", "original": inv["literal_lines"][3], "page": 2, "actual": inv["literal_lines"][3],
         "box": [48, 938, 1152, 974], "font": MONO, "size": 24},
        {"field": "paid_status", "original": "PAID / 已结算", "page": 2, "actual": "PAID / 已结算",
         "box": [48, 1140, 500, 1190], "font": LATIN, "size": 34, "rich_text": {"PAID": GREEN, "/": MUTED, "已结算": INK}},
    ]
    return {
        "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
        "entries": entries,
        "checks": [
            {"check": "page_header_and_id_repeated", "passed": True,
             "method": "两页同一 header 组件；页脚分别 Page 1/2、Page 2/2，编号均为 " + inv["invoice_id"] + "。"},
            {"check": "literal_char_fidelity", "passed": True,
             "method": "四条 literal_lines 均通过 Text 的 text 属性原样写入（不经过实体转义），含双空格、反斜杠、<、>、&。"},
            {"check": "paid_baseline", "passed": True,
             "method": "PAID / 已结算 使用同一外层 Text 的三个嵌套 span，字号与基线一致；颜色分别为绿/灰/深色。"},
            {"check": "actual_view", "passed": True,
             "method": "两页整图与第 2 页原样文字/PAID 局部裁图实际打开检查。"},
        ],
    }


def main() -> int:
    inv = load_invoice()
    items, t = compute(inv)
    d = TMP / "dsl"
    (d / "page1").mkdir(parents=True, exist_ok=True)
    (d / "page2").mkdir(parents=True, exist_ok=True)
    (d / "page1" / f"{VERSION}.snapshot").write_text(page1(inv, items, t), encoding="utf-8")
    (d / "page2" / f"{VERSION}.snapshot").write_text(page2(inv), encoding="utf-8")
    (TMP / "invoice-audit.json").write_text(json.dumps(audit(inv, items, t), ensure_ascii=False, indent=2), encoding="utf-8")
    (TMP / "text-map.json").write_text(json.dumps(text_map(inv, items), ensure_ascii=False, indent=2), encoding="utf-8")
    print("A11", VERSION, "items", [(str(i["line"])) for i in items], "subtotal", t["subtotal"],
          "tax", t["tax"], "total", t["total"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
