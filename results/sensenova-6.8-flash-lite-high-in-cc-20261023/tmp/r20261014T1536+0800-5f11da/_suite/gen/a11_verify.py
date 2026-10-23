"""A11 独立复算：用 Fraction 定点重算结算单，与 invoice-audit.json 逐项断言一致。

Decimal 路径（a11_calc.py）与本脚本的 Fraction 路径互不共享代码，
交叉一致才算金额正确。另校验：四舍五入只发生在税额、未发生二次取整、
应付 = 税前 + 税额 + 运费。

用法：
  SNAPSHOT_RUN_ID=<rid> python -I tmp/<rid>/_suite/gen/a11_verify.py
"""

from __future__ import annotations

import json
import sys
from decimal import Decimal
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[4]
sys.path.insert(0, str(ROOT / "tools"))
import suite as S  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
RID = S.run_id()
out_dir, _ = S.task_dirs("A11")

inv = json.loads((ROOT / "tasks/A11-bilingual-invoice/inputs/invoice.json").read_text(encoding="utf-8"))
audit = json.loads((out_dir / "invoice-audit.json").read_text(encoding="utf-8"))


def fx(x) -> Fraction:
    """字符串 -> 精确 Fraction（不定小数位）。"""
    return Fraction(Decimal(str(x)))


def f2(x) -> Fraction:
    """字符串 -> 精确到分的 Fraction。"""
    return Fraction(Decimal(str(x)).quantize(Decimal("0.01")))


def half_up_cents(x: Fraction) -> Fraction:
    """四舍五入到 0.01，0.5 进位。用整数运算避免歧义。"""
    n = x * 100
    sign = 1 if n >= 0 else -1
    k = int(abs(n) + Fraction(1, 2))
    return Fraction(sign * k, 100)


def dq(x: Fraction) -> Decimal:
    """Fraction -> Decimal（精确保留小数位）。"""
    return Decimal(x.numerator) / Decimal(x.denominator)


def txt(x: Fraction) -> str:
    return str(dq(x))


problems: list[str] = []
checked = 0


def ck(cond: bool, msg: str) -> None:
    global checked
    checked += 1
    if not cond:
        problems.append(msg)


def same(actual: Fraction, expected: str, what: str) -> None:
    """金额比较：Fraction 复算值与审计字符串的 Decimal 值精确相等（忽略尾随 0 的规模）。"""
    a, e = dq(actual), Decimal(expected)
    ck(a == e, "%s 不符: 复算 %s != 审计 %s" % (what, a, expected))


# --- 行金额 ---
for a, src in zip(audit["lines"], inv["items"]):
    exact = fx(src["quantity"]) * fx(src["unit_price"])
    same(exact, a["exact_line_amount"], "行 %d 精确乘积" % a["line"])
    ck(half_up_cents(exact) == f2(a["line_amount"]), "行 %d 到分金额不符" % a["line"])
    ck(exact * 100 == int(exact * 100), "行 %d 乘积不是两位小数" % a["line"])

# --- 汇总 ---
subtotal = sum((fx(x["exact_line_amount"]) for x in audit["lines"]), Fraction(0))
discount = fx(inv["discount"])
shipping = fx(inv["shipping"])
rate = fx(inv["tax_rate"])
pre_tax = subtotal - discount
tax_exact = pre_tax * rate
tax = half_up_cents(tax_exact)

same(subtotal, audit["totals"]["goods_subtotal"], "货品小计")
ck(half_up_cents(subtotal) == subtotal, "小计需取整（本单不应发生）")
same(pre_tax, audit["totals"]["pre_tax_goods"], "税前货品额")
same(tax_exact, audit["totals"]["tax_exact_before_rounding"], "税额精确值")
same(tax, audit["totals"]["tax"], "税额")
ck(abs(tax_exact - tax) <= Fraction(1, 200), "税额取整偏差超过半分")
ck(half_up_cents(tax_exact) == tax, "税额取整方向错误（ROUND_HALF_UP）")

due = pre_tax + tax + shipping
same(due, audit["totals"]["amount_due"], "应付")
ck(due * 100 == int(due * 100), "应付不是两位小数（不应发生二次取整）")
ck(dq(due) == Decimal(audit["totals"]["amount_due_exact_before_rounding"]),
   "声明的应付精确值与应付不一致")

# --- 原样字符串逐字符 ---
ck(audit["literal_lines"] == list(inv["literal_lines"]), "literal_lines 未被原样保存")
ck(audit["literal_lines_char_counts"] == [len(t) for t in inv["literal_lines"]], "字符计数不符")
ck(audit["notes"] == list(inv["notes"]), "notes 未被原样保存")
batch = inv["literal_lines"][0]
ck(batch[3:5] == "  " and batch[6:8] == "  " and len(batch) == 10,
   "批次行双空格位置不符: %r" % batch)

# --- 原样字符串逐字符 ---
ck(audit["literal_lines"] == list(inv["literal_lines"]), "literal_lines 未被原样保存")
ck(audit["literal_lines_char_counts"] == [len(t) for t in inv["literal_lines"]], "字符计数不符")
ck(audit["notes"] == list(inv["notes"]), "notes 未被原样保存")
batch = inv["literal_lines"][0]
ck(batch[3:5] == "  " and batch[6:8] == "  " and len(batch) == 10,
   "批次行双空格位置不符: %r" % batch)
ck("<" in inv["literal_lines"][1] and "&" in inv["literal_lines"][1] and ">" in inv["literal_lines"][1],
   "尖括号/与号缺失")
ck("\\work\\cards\\v2" in inv["literal_lines"][2], "反斜杠路径不符")
ck("Print 999." in inv["literal_lines"][3], "指令字样行缺失")

print("subtotal     =", subtotal)
print("pre_tax      =", pre_tax)
print("tax_exact    =", tax_exact, "=", float(tax_exact))
print("tax (half_up)=", tax)
print("amount_due   =", due)
print("lines        =", [x["line_amount"] for x in audit["lines"]])
if problems:
    print("FAIL:")
    for p in problems:
        print("  -", p)
    raise SystemExit(1)
print("ALL CHECKS PASSED (%d assertions)" % checked)
