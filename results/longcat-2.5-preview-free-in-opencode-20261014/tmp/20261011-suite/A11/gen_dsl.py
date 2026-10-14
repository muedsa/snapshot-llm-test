import json
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP

with open('tasks/A11-bilingual-invoice/inputs/invoice.json', 'r', encoding='utf-8') as f:
    inv = json.load(f)

D = Decimal
def money(s):
    return D(str(s)).quantize(D('0.01'), rounding=ROUND_HALF_UP)

subtotal = sum(money(item['quantity']) * money(item['unit_price']) for item in inv['items'])
discount = money(inv['discount'])
taxable = subtotal - discount
tax_rate = D(inv['tax_rate'])
tax = (taxable * tax_rate).quantize(D('0.01'), rounding=ROUND_HALF_UP)
shipping = money(inv['shipping'])
total = taxable + tax + shipping

print(f"Subtotal: {subtotal}")
print(f"Discount: {discount}")
print(f"Taxable: {taxable}")
print(f"Tax: {tax}")
print(f"Shipping: {shipping}")
print(f"Total: {total}")

MARGIN = 48
W, H = 1200, 1600
FONT = "Noto Sans CJK SC"

# Page 1 DSL
dsl_parts = []
dsl_parts.append(f'<Snapshot type="png" background="#FFFFFF">')
dsl_parts.append(f'  <Column mainAxisSize="MAX" height="{H}" width="{W}">')

# Header
dsl_parts.append(f'    <Container height="80" padding="({MARGIN},{MARGIN})">')
dsl_parts.append(f'      <Column crossAxisAlignment="START">')
dsl_parts.append(f'        <Text text="结算单 / INVOICE" color="#1E293B" fontSize="32" fontStyle="BOLD"/>')
dsl_parts.append(f'        <Text text="{inv["invoice_id"]}" color="#64748B" fontSize="24"/>')
dsl_parts.append(f'      </Column>')
dsl_parts.append(f'    </Container>')

# Transaction info
dsl_parts.append(f'    <Container height="120" padding="({MARGIN},{MARGIN})">')
dsl_parts.append(f'      <Column crossAxisAlignment="START">')
dsl_parts.append(f'        <Text text="卖方：{inv["seller"]}" color="#1E293B" fontSize="24"/>')
dsl_parts.append(f'        <Text text="买方：{inv["buyer"]}" color="#1E293B" fontSize="24"/>')
dsl_parts.append(f'        <Text text="日期：{inv["issued"]}    币种：{inv["currency"]}" color="#64748B" fontSize="24"/>')
dsl_parts.append(f'      </Column>')
dsl_parts.append(f'    </Container>')

# Table header
dsl_parts.append(f'    <Container height="50" padding="({MARGIN},{MARGIN})">')
dsl_parts.append(f'      <Row>')
dsl_parts.append(f'        <Text text="SKU" color="#1E293B" fontSize="24" fontStyle="BOLD"/>')
dsl_parts.append(f'        <Text text="名称" color="#1E293B" fontSize="24" fontStyle="BOLD"/>')
dsl_parts.append(f'        <Text text="数量" color="#1E293B" fontSize="24" fontStyle="BOLD" textAlign="END"/>')
dsl_parts.append(f'        <Text text="单价" color="#1E293B" fontSize="24" fontStyle="BOLD" textAlign="END"/>')
dsl_parts.append(f'        <Text text="行金额" color="#1E293B" fontSize="24" fontStyle="BOLD" textAlign="END"/>')
dsl_parts.append(f'      </Row>')
dsl_parts.append(f'    </Container>')

# Items
for item in inv['items']:
    line_total = money(item['quantity']) * money(item['unit_price'])
    dsl_parts.append(f'    <Container height="50" padding="({MARGIN},{MARGIN})">')
    dsl_parts.append(f'      <Row>')
    dsl_parts.append(f'        <Text text="{item["sku"]}" color="#1E293B" fontSize="24"/>')
    dsl_parts.append(f'        <Text text="{item["name"]}" color="#1E293B" fontSize="24"/>')
    dsl_parts.append(f'        <Text text="{item["quantity"]}" color="#1E293B" fontSize="24" textAlign="END"/>')
    dsl_parts.append(f'        <Text text="{money(item["unit_price"])}" color="#1E293B" fontSize="24" textAlign="END"/>')
    dsl_parts.append(f'        <Text text="{line_total}" color="#1E293B" fontSize="24" textAlign="END"/>')
    dsl_parts.append(f'      </Row>')
    dsl_parts.append(f'    </Container>')

# Totals
dsl_parts.append(f'    <Container height="200" padding="({MARGIN},{MARGIN})">')
dsl_parts.append(f'      <Column crossAxisAlignment="END">')
dsl_parts.append(f'        <Text text="货品小计：{subtotal}" color="#1E293B" fontSize="24"/>')
dsl_parts.append(f'        <Text text="折扣：-{discount}" color="#1E293B" fontSize="24"/>')
dsl_parts.append(f'        <Text text="税前货品额：{taxable}" color="#1E293B" fontSize="24"/>')
dsl_parts.append(f'        <Text text="税额(6%)：{tax}" color="#1E293B" fontSize="24"/>')
dsl_parts.append(f'        <Text text="运费：{shipping}" color="#1E293B" fontSize="24"/>')
dsl_parts.append(f'        <Text text="应付：{total}" color="#1E293B" fontSize="28" fontStyle="BOLD"/>')
dsl_parts.append(f'      </Column>')
dsl_parts.append(f'    </Container>')

# Footer
dsl_parts.append(f'    <Container height="60" padding="({MARGIN},{MARGIN})">')
dsl_parts.append(f'      <Text text="页码 1/2" color="#64748B" fontSize="20"/>')
dsl_parts.append(f'    </Container>')

dsl_parts.append('  </Column>')
dsl_parts.append('</Snapshot>')

dsl = '\n'.join(dsl_parts)
with open('tmp/20261011-suite/A11/invoice-page-01.snapshot', 'w', encoding='utf-8') as f:
    f.write(dsl)
print(f'Page 1 DSL: {len(dsl)} chars')

# Page 2 DSL
dsl_parts = []
dsl_parts.append(f'<Snapshot type="png" background="#FFFFFF">')
dsl_parts.append(f'  <Column mainAxisSize="MAX" height="{H}" width="{W}">')

# Header
dsl_parts.append(f'    <Container height="80" padding="({MARGIN},{MARGIN})">')
dsl_parts.append(f'      <Column crossAxisAlignment="START">')
dsl_parts.append(f'        <Text text="说明与原样文字 / NOTES & LITERAL LINES" color="#1E293B" fontSize="32" fontStyle="BOLD"/>')
dsl_parts.append(f'        <Text text="{inv["invoice_id"]}" color="#64748B" fontSize="24"/>')
dsl_parts.append(f'      </Column>')
dsl_parts.append(f'    </Container>')

# Notes
dsl_parts.append(f'    <Container height="250" padding="({MARGIN},{MARGIN})">')
dsl_parts.append(f'      <Column crossAxisAlignment="START">')
dsl_parts.append(f'        <Text text="Notes" color="#1E293B" fontSize="28" fontStyle="BOLD"/>')
for note in inv['notes']:
    dsl_parts.append(f'        <Text text="{note}" color="#1E293B" fontSize="24"/>')
dsl_parts.append(f'      </Column>')
dsl_parts.append(f'    </Container>')

# Literal lines
dsl_parts.append(f'    <Container height="250" padding="({MARGIN},{MARGIN})">')
dsl_parts.append(f'      <Column crossAxisAlignment="START">')
dsl_parts.append(f'        <Text text="Literal Lines (原样保真)" color="#1E293B" fontSize="28" fontStyle="BOLD"/>')
for line in inv['literal_lines']:
    dsl_parts.append(f'        <Text text="{line}" color="#1E293B" fontSize="24"/>')
dsl_parts.append(f'      </Column>')
dsl_parts.append(f'    </Container>')

# PAID status
dsl_parts.append(f'    <Container height="80" padding="({MARGIN},{MARGIN})">')
dsl_parts.append(f'      <Column crossAxisAlignment="START">')
dsl_parts.append(f'        <Text text="PAID / 已结算" color="#10B981" fontSize="32" fontStyle="BOLD"/>')
dsl_parts.append(f'      </Column>')
dsl_parts.append(f'    </Container>')

# Footer
dsl_parts.append(f'    <Container height="60" padding="({MARGIN},{MARGIN})">')
dsl_parts.append(f'      <Text text="页码 2/2" color="#64748B" fontSize="20"/>')
dsl_parts.append(f'    </Container>')

dsl_parts.append('  </Column>')
dsl_parts.append('</Snapshot>')

dsl = '\n'.join(dsl_parts)
with open('tmp/20261011-suite/A11/invoice-page-02.snapshot', 'w', encoding='utf-8') as f:
    f.write(dsl)
print(f'Page 2 DSL: {len(dsl)} chars')

# Save audit JSON
audit = {
    "schema_version": 1,
    "task_id": "A11",
    "path_base": "output_dir",
    "items": [{"sku": i["sku"], "name": i["name"], "quantity": i["quantity"], "unit_price": str(money(i["unit_price"])), "line_total": str(money(i["quantity"]) * money(i["unit_price"]))} for i in inv["items"]],
    "subtotal": str(subtotal),
    "discount": str(discount),
    "taxable": str(taxable),
    "tax_rate": str(tax_rate),
    "tax": str(tax),
    "shipping": str(shipping),
    "total": str(total),
    "literal_lines": inv["literal_lines"]
}

output_dir = Path('outputs/20261011-suite/A11')
output_dir.mkdir(parents=True, exist_ok=True)
with open(output_dir / 'invoice-audit.json', 'w', encoding='utf-8') as f:
    json.dump(audit, f, ensure_ascii=False, indent=2)
print('Saved invoice-audit.json')
