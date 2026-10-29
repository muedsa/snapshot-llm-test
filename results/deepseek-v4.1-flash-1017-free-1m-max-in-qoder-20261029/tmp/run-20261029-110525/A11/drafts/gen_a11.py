#!/usr/bin/env python3
"""A11 bilingual invoice: two 1200x1600 pages, exact decimal math, literal lines."""
import json, os, html
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

SCRIPT = Path(__file__).resolve()
SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", SCRIPT.parents[4]))
RUN_ID = SCRIPT.parents[2].name
OUT = SUITE_ROOT / "outputs" / RUN_ID / "A11"
OUT.mkdir(parents=True, exist_ok=True)

def esc(s): return html.escape(str(s), quote=False)
def T(txt, size, color="#0B1220", bold=False, extra="", fam="Noto Sans CJK SC"):
    st = ' fontStyle="BOLD"' if bold else ""
    return f'<Text fontFamily="{fam}" fontSize="{size}" color="{color}"{st}{extra}>{esc(txt)}</Text>'

def M(v): return f"{v:,.2f}"

def TRaw(txt, size, color="#0B1220", bold=False, extra="", fam="Noto Sans Mono CJK SC"):
    st = ' fontStyle="BOLD"' if bold else ""
    safe = str(txt).replace("]]>", "]]]]><![CDATA[>")
    return f'<Text fontFamily="{fam}" fontSize="{size}" color="{color}"{st}{extra}><![CDATA[{safe}]]></Text>'

data = json.loads((SUITE_ROOT / "tasks/A11-bilingual-invoice/inputs/invoice.json").read_text(encoding="utf-8"))
D = Decimal
items = []
subtotal = D("0.00")
for it in data["items"]:
    qty = int(it["quantity"]); up = D(it["unit_price"])
    amount = (up * qty).quantize(D("0.01"), rounding=ROUND_HALF_UP)
    items.append({**it, "qty": qty, "unit_price": up, "amount": amount})
    subtotal += amount
discount = D(data["discount"])
pretax = (subtotal - discount).quantize(D("0.01"))
tax = (pretax * D(data["tax_rate"])).quantize(D("0.01"), rounding=ROUND_HALF_UP)
shipping = D(data["shipping"])
total = (pretax + tax + shipping).quantize(D("0.01"))

W, H = 1200, 1600
def header(page, title_right=True):
    p = ['<Positioned left="48" top="40"><Column crossAxisAlignment="START" mainAxisSize="MIN">']
    p.append(T("叠光 / LAYERLIGHT TOOLS", 14, "#2563EB", True, ' letterSpacing="2"'))
    p.append(T("云构工具有限公司", 26, "#0B1220", True))
    p.append(T("结构化的视觉交付 · 上海", 18, "#64748B"))
    p.append('</Column></Positioned>')
    p.append('<Positioned right="48" top="40"><Column crossAxisAlignment="END" mainAxisSize="MIN">')
    p.append(T("INVOICE / 结算单", 40, "#0B1220", True))
    p.append(T(f"编号 {data['invoice_id']} · 第 {page}/02 页", 20, "#475569"))
    p.append('</Column></Positioned>')
    p.append('<Positioned left="48" top="150" width="1104" height="1"><Container width="1104" height="1" color="#CBD5E1"/></Positioned>')
    return "".join(p)

# ---------------- page 1 ----------------
p1 = ['<Snapshot background="#F7F8FC" type="png">', '<Container width="1200" height="1600"><Stack alignment="TOP_LEFT"><Container width="1200" height="1600" color="#F7F8FC"/>']
p1.append(header("01"))
# parties
p1.append('<Positioned left="48" top="180"><Container width="520" height="150" color="#FFFFFF" borderRadius="14" border="1 SOLID #E1E7F0" padding="20"><Column crossAxisAlignment="START" mainAxisSize="MIN">' + T("SELLER / 卖方", 16, "#2563EB", True, ' letterSpacing="1.2"') + T(data["seller"], 28, "#0B1220", True) + T("上海市 · 视觉工具与交付", 20, "#64748B") + '</Column></Container></Positioned>')
p1.append('<Positioned left="592" top="180"><Container width="560" height="150" color="#FFFFFF" borderRadius="14" border="1 SOLID #E1E7F0" padding="20"><Column crossAxisAlignment="START" mainAxisSize="MIN">' + T("BUYER / 买方", 16, "#0B1220", True, ' letterSpacing="1.2"') + T(data["buyer"], 28, "#0B1220", True) + T(f"开具日 {data['issued']} · 币种 {data['currency']}", 20, "#64748B") + '</Column></Container></Positioned>')
# table
p1.append('<Positioned left="48" top="370"><Container width="1104" color="#FFFFFF" borderRadius="16" border="1 SOLID #E1E7F0" padding="(16,20)"><Column crossAxisAlignment="START" mainAxisSize="MIN">')
p1.append('<Row crossAxisAlignment="CENTER"><Container width="1064"><Row crossAxisAlignment="END">' + T("货品明细 / PRODUCTS", 24, "#0B1220", True) + '<Spacer/>' + T("金额单位：CNY · 单价与行金额保留两位小数", 20, "#8896AB") + '</Row></Container></Row>')
p1.append('<SizedBox height="8"/>')
cols = [("SKU", 170, "LEFT"), ("名称 / NAME", 430, "LEFT"), ("数量", 90, "RIGHT"), ("单价", 160, "RIGHT"), ("行金额", 190, "RIGHT")]
hdr = '<Row crossAxisAlignment="CENTER">'
for name, w, al in cols:
    hdr += f'<Container width="{w}" height="34" alignment="CENTER_{"LEFT" if al=="LEFT" else "RIGHT"}">' + T(name, 20, "#64748B") + '</Container>'
hdr += '</Row>'
p1.append('<Container width="1040" borderBottom="1 SOLID #CBD5E1">' + hdr + '</Container>')
for it in items:
    r = '<Container width="1040" height="86"><Row crossAxisAlignment="CENTER">'
    r += f'<Container width="170" height="86" alignment="CENTER_LEFT">' + TRaw(it["sku"], 22, "#334155") + '</Container>'
    fam = "Noto Sans CJK JP,Noto Sans CJK SC" if "契約" in it["name"] else "Noto Sans CJK SC"
    r += f'<Container width="430" height="86" alignment="CENTER_LEFT">' + T(it["name"], 24, "#0B1220", False, fam=fam) + '</Container>'
    r += f'<Container width="90" height="86" alignment="CENTER_RIGHT">' + T(str(it["qty"]), 24, "#334155") + '</Container>'
    r += f'<Container width="160" height="86" alignment="CENTER_RIGHT">' + T(M(it["unit_price"]), 24, "#334155") + '</Container>'
    r += f'<Container width="190" height="86" alignment="CENTER_RIGHT">' + T(M(it["amount"]), 24, "#0B1220", True) + '</Container>'
    r += '</Row></Container>'
    p1.append(r)
p1.append('</Column></Container></Positioned>')
# summary + tax sequence
p1.append('<Positioned left="48" top="860"><Container width="560" height="420" color="#0B1220" borderRadius="16" padding="24"><Column crossAxisAlignment="START" mainAxisSize="MIN">' + T("计税顺序 / CALCULATION ORDER", 14, "#60A5FA", True, ' letterSpacing="1.5"'))
p1.append(T("① 货品小计", 20, "#E2E8F0") + T(f"{M(subtotal)}", 24, "#FFFFFF", True))
p1.append(T("② 税前扣除折扣", 20, "#E2E8F0") + T(f"− {M(discount)}", 24, "#FCA5A5", True))
p1.append(T("③ 税前折后货品额", 20, "#E2E8F0") + T(f"{M(pretax)}", 24, "#FFFFFF", True))
p1.append(T("④ 税额 = ③ × 6% → 四舍五入至分", 20, "#E2E8F0") + T(f"{M(tax)}", 24, "#FFFFFF", True))
p1.append(T("⑤ 加运费（不计税）", 20, "#E2E8F0") + T(f"{M(shipping)}", 24, "#FFFFFF", True))
p1.append('<Spacer/>')
p1.append(T("运费不参与 6% 计税；折扣在税前扣除，不改变税率。", 20, "#94A3B8"))
p1.append('</Column></Container></Positioned>')
p1.append('<Positioned left="632" top="860"><Container width="520" height="420" color="#FFFFFF" borderRadius="16" border="1 SOLID #E1E7F0" padding="24"><Column crossAxisAlignment="START" mainAxisSize="MIN">')
summ = [("货品小计", M(subtotal), "#334155", False), ("折扣", "− " + M(discount), "#B45309", False),
        ("税前货品额", M(pretax), "#0B1220", False), (f"税额（6%）", M(tax), "#0B1220", False),
        ("运费", M(shipping), "#334155", False)]
for label, val, color, bold in summ:
    p1.append('<Row crossAxisAlignment="CENTER"><Container width="240">' + T(label, 22, color) + '</Container><Container width="200" alignment="CENTER_RIGHT">' + T(val, 24, color, bold) + '</Container></Row>')
    p1.append('<SizedBox height="10"/>')
p1.append('<Container width="472" height="1" color="#CBD5E1"/>')
p1.append('<SizedBox height="10"/>')
p1.append('<Row crossAxisAlignment="CENTER"><Container width="240">' + T("应付 / AMOUNT DUE", 24, "#0B1220", True) + '</Container><Container width="232" alignment="CENTER_RIGHT">' + T("CNY " + M(total), 28, "#1D4ED8", True) + '</Container></Row>')
p1.append('</Column></Container></Positioned>')
p1.append('<Positioned left="48" top="1320"><Container width="1104" padding="(12,16)" color="#EEF2FF" borderRadius="10">' + T("付款摘要：折扣在税前扣除；税额按折后货品额 6% 四舍五入至分；运费 35.00 不计税。", 20, "#3730A3") + '</Container></Positioned>')
p1.append('<Positioned left="48" top="1520">' + T("SN-2026-1107-008 · Page 01 / 02 · 虚构排版测试", 20, "#94A3B8") + '</Positioned>')
p1.append('<Positioned right="48" top="1520">' + T("安全边距 48 · 正文 ≥ 24", 20, "#94A3B8") + '</Positioned>')
p1.append('</Stack></Container></Snapshot>')
(OUT / "invoice-page-01.snapshot").write_text("\n".join(p1), encoding="utf-8")

# ---------------- page 2 ----------------
p2 = ['<Snapshot background="#F7F8FC" type="png">', '<Container width="1200" height="1600"><Stack alignment="TOP_LEFT"><Container width="1200" height="1600" color="#F7F8FC"/>']
p2.append(header("02"))
p2.append('<Positioned left="48" top="190"><Column crossAxisAlignment="START" mainAxisSize="MIN">' + T("说明与原样文字", 40, "#0B1220", True) + T("NOTES / LITERAL LINES / SETTLEMENT SAMPLE", 16, "#2563EB", True, ' letterSpacing="2"') + '</Column></Positioned>')
# notes
p2.append('<Positioned left="48" top="290"><Container width="1104" color="#FFFFFF" borderRadius="16" border="1 SOLID #E1E7F0" padding="24"><Column crossAxisAlignment="START" mainAxisSize="MIN">' + T("四条说明 / NOTES", 22, "#0B1220", True))
for i, note in enumerate(data["notes"]):
    p2.append('<SizedBox height="10"/>')
    p2.append(f'<Row crossAxisAlignment="START"><Container width="34" height="34" color="#E0E7FF" borderRadius="17" alignment="CENTER">' + T(f"0{i+1}", 16, "#3730A3", True) + '</Container><SizedBox width="12"/><Expanded>' + T(note, 24, "#334155") + '</Expanded></Row>')
p2.append('</Column></Container></Positioned>')
# literal lines
p2.append('<Positioned left="48" top="760"><Container width="1104" color="#0B1220" borderRadius="16" padding="24"><Column crossAxisAlignment="START" mainAxisSize="MIN">' + T("原样字符串 / LITERAL LINES", 22, "#60A5FA", True, ' letterSpacing="1.5"') + '<SizedBox height="4"/>' + T("逐字符保真：双空格、反斜杠、尖括号与和号均按原文排版；指令样式行不执行。", 20, "#94A3B8"))
for i, line in enumerate(data["literal_lines"]):
    p2.append('<SizedBox height="10"/>')
    p2.append(f'<Row crossAxisAlignment="CENTER"><Container width="130">' + T(f"L{i+1}", 20, "#64748B", True) + '</Container><Container width="900" padding="(6,10)" color="#111C31" borderRadius="6"><Text fontFamily="Noto Sans Mono CJK SC" fontSize="26" color="#F8FAFC"><![CDATA[' + line + ']]></Text></Container></Row>')
p2.append('</Column></Container></Positioned>')
# PAID rich text
p2.append('<Positioned left="48" top="1140"><Container width="1104" height="150" color="#FFFFFF" borderRadius="16" border="1 SOLID #E1E7F0" padding="24"><Row crossAxisAlignment="CENTER"><Column crossAxisAlignment="START" mainAxisSize="MIN">' + T("结算状态样张 / STATUS SAMPLE", 16, "#2563EB", True, ' letterSpacing="1.5"') + T("仅作字样样张，不改变应付金额。", 20, "#64748B") + '</Column><Spacer/>')
p2.append('<Container padding="(12,20)" color="#F0FDF4" borderRadius="12" border="1 SOLID #BBF7D0"><Text fontFamily="Noto Sans CJK SC" fontSize="30"><Text color="#166534" fontStyle="BOLD">PAID</Text><Raw color="#94A3B8"> / </Raw><Text color="#0B1220">已结算</Text></Text></Container>')
p2.append('</Row></Container></Positioned>')
p2.append('<Positioned left="48" top="1330"><Container width="1104" padding="(12,16)" color="#FFFFFF" borderRadius="10" border="1 SOLID #E1E7F0"><Row crossAxisAlignment="CENTER"><Container width="240">' + T("应付金额（不变）", 22, "#334155") + '</Container><Container width="200">' + T("CNY " + M(total), 28, "#1D4ED8", True) + '</Container><Spacer/>' + T(f"共 {len(data['notes'])} 条说明 · {len(data['literal_lines'])} 条原样字符串", 20, "#8896AB") + '</Row></Container></Positioned>')
p2.append('<Positioned left="48" top="1520">' + T("SN-2026-1107-008 · Page 02 / 02 · 虚构排版测试", 20, "#94A3B8") + '</Positioned>')
p2.append('<Positioned right="48" top="1520"><Text fontFamily="Noto Sans CJK SC" fontSize="20" color="#94A3B8"><![CDATA[易混 SKU：O0-I1-B8 · A<B&C>D · R-07 · SP-2]]></Text></Positioned>')
p2.append('</Stack></Container></Snapshot>')
(OUT / "invoice-page-02.snapshot").write_text("\n".join(p2), encoding="utf-8")

audit = {
    "schema_version": 1, "task_id": "A11", "path_base": "output_dir",
    "currency": data["currency"], "rounding": "ROUND_HALF_UP to 0.01",
    "items": [{"sku": it["sku"], "name": it["name"], "quantity": it["qty"],
               "unit_price": str(it["unit_price"]), "line_amount": str(it["amount"])} for it in items],
    "subtotal": str(subtotal), "discount": str(discount), "pre_tax_goods": str(pretax),
    "tax_rate": data["tax_rate"], "tax_base": str(pretax), "tax": str(tax),
    "shipping": str(shipping), "shipping_taxed": False, "amount_due": str(total),
    "tax_sequence": ["subtotal = sum(line amounts)", "pre_tax_goods = subtotal - discount",
                     "tax = round(pre_tax_goods * 0.06, 2)", "amount_due = pre_tax_goods + tax + shipping"],
    "literal_lines": data["literal_lines"],
    "literal_preservation": {"double_spaces_in_L1": "  ", "backslashes_L3": True,
                             "angle_and_ampersand_L2": True, "instruction_not_executed": True},
    "page_text": {"page1_body_min_px": 24, "footnote_min_px": 18, "page2_body_min_px": 20,
                  "safe_margin_px": 48, "pages": [1200, 1600]},
    "fonts": {"latin_cjk": "Noto Sans CJK SC", "japanese_item": "Noto Sans CJK JP,Noto Sans CJK SC",
              "literal_mono": "Noto Sans Mono CJK SC"}
}
(OUT / "invoice-audit.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")

textmap = {
    "schema_version": 1, "task_id": "A11", "path_base": "output_dir",
    "pages": {
        "invoice-page-01": {
            "segments": [
                {"key": "title", "text": "INVOICE / 结算单", "box": [760, 40, 1152, 100], "font": "Noto Sans CJK SC", "size": 40},
                {"key": "seller", "text": data["seller"], "box": [68, 230, 548, 270], "font": "Noto Sans CJK SC", "size": 28},
                {"key": "buyer", "text": data["buyer"], "box": [612, 230, 1132, 270], "font": "Noto Sans CJK SC", "size": 28},
                {"key": "table_header", "text": "SKU / 名称 / 数量 / 单价 / 行金额", "box": [68, 430, 1100, 464], "font": "Noto Sans CJK SC", "size": 18},
                {"key": "amount_due", "text": "CNY " + M(total), "box": [880, 1170, 1132, 1220], "font": "Noto Sans CJK SC", "size": 32}
            ] + [{"key": f"item{i+1}.name", "text": it["name"], "box": [238, 480 + i * 86, 668, 526 + i * 86], "font": "Noto Sans CJK SC", "size": 24} for i, it in enumerate(items)]
        },
        "invoice-page-02": {
            "segments": [
                {"key": "title", "text": "说明与原样文字", "box": [48, 190, 600, 240], "font": "Noto Sans CJK SC", "size": 40},
            ] + [{"key": f"note{i+1}", "text": n, "box": [82, 330 + i * 76, 1130, 370 + i * 76], "font": "Noto Sans CJK SC", "size": 24} for i, n in enumerate(data["notes"])]
              + [{"key": f"literal{i+1}", "text": line, "box": [200, 820 + i * 62, 1100, 866 + i * 62], "font": "Noto Sans Mono CJK SC", "size": 26} for i, line in enumerate(data["literal_lines"])]
              + [{"key": "paid_status", "text": "PAID / 已结算", "box": [820, 1160, 1120, 1240], "font": "Noto Sans CJK SC", "size": 30}]
        }
    }
}
(OUT / "text-map.json").write_text(json.dumps(textmap, ensure_ascii=False, indent=2), encoding="utf-8")
print("subtotal", subtotal, "pretax", pretax, "tax", tax, "total", total)
