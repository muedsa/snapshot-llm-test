"""A11 页面生成器：两页 1200x1600 双语发票样张。

硬性要求（TASK.md）：正文 ≥24、脚注 ≥20、安全边距 48、不靠微缩塞字；
金额小数点列对齐；literal_lines 逐字符保真；PAID 富文本自然共用基线。

关键契约（A11 探针 1–4 实测，见 iterations.jsonl）：
  * 类 DOM 解析器不做任何实体解码，子内容里的 &lt; 会被原样显示
  * 子内容里写原样 < 直接 400
  * 只有 text="..." 属性值按字面取用 → 含 < > & 的文本一律走 text 属性
  * Raw 与普通 Text 对内部双空格的保留完全一致（像素级相同）
  * 嵌套 Text 的样式只写在**子内容**形态上生效；写成 <Text text=".." color=".."/>
    属性形态时子级颜色会被外层覆盖（探针 5 证实）
  * Noto Sans Mono CJK SC 为等宽（步进 = fontSize/2），同字体 + 固定宽容器右对齐
    → 小数点列精确对齐；由于右对齐，小数点左侧字形宽度不影响对齐
所有坐标来自本文件常量，text-map.json 的放置盒与最终 PNG 的实测墨迹盒双向对照。

用法：
  SNAPSHOT_RUN_ID=<rid> python -I tmp/<rid>/_suite/gen/a11_pages.py [page1|page2|both]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[4]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(HERE.parent))
import suite as S  # noqa: E402
import a11_client as C  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")
TASK = "A11"
RID = S.run_id()
OUT, TMP = S.task_dirs(TASK)
W, H, M = 1200, 1600, 48
CW = W - 2 * M          # 内容宽 1104
BOTTOM = H - M          # 内容下界 1552

CJK = "Noto Sans CJK SC"
MONO = "Noto Sans Mono CJK SC"
INK = "#0F172A"
INK2 = "#1E293B"
MUTED = "#64748B"
FAINT = "#94A3B8"
RULE = "#CBD5E1"
RULE2 = "#E2E8F0"
ACC = "#0F766E"
ACC2 = "#134E4A"
BAND = "#F1F5F9"
ZEBRA = "#F8FAFC"
AMBER = "#B45309"
GREEN = "#15803D"
PAID_SLASH = "#94A3B8"
PAID_BG = "#F0FDF4"
PAID_BD = "#86EFAC"
MINT = "#A7F3D0"
WHITE = "#FFFFFF"

inv = json.loads((ROOT / "tasks/A11-bilingual-invoice/inputs/invoice.json")
                 .read_text(encoding="utf-8"))
audit = json.loads((OUT / "invoice-audit.json").read_text(encoding="utf-8"))

# --- 金额：一律取自已独立复算通过(33 断言)的 invoice-audit.json -------------
_T = audit["totals"]
SUB = _T["goods_subtotal"]            # 4124.30
DISC = _T["discount"]                 # 180.00
PRE = _T["pre_tax_goods"]             # 3944.30
TAX = _T["tax"]                       # 236.66
SHIP = _T["shipping"]                 # 35.00
DUE = _T["amount_due"]                # 4215.96
TAX_EXACT = _T["tax_exact_before_rounding"]          # 236.6580
DUE_EXACT = _T["amount_due_exact_before_rounding"]   # 4215.96

ITEMS = inv["items"]
NOTES = inv["notes"]
LIT = inv["literal_lines"]
ID_, ISSUED, SELLER, BUYER, CUR = (
    inv["invoice_id"], inv["issued"], inv["seller"], inv["buyer"], inv["currency"])
TAXRATE = int(round(float(inv["tax_rate"]) * 100))
LIT_LEN = audit["literal_lines_char_counts"]


def money(s: str) -> str:
    """4124.30 -> 4,124.30（只加千分位，不动小数部分）。"""
    whole, _, frac = s.partition(".")
    return f"{int(whole):,}.{frac}"


LINE_AMT = [money(l["line_amount"]) for l in audit["lines"]]
UNIT_PRIX = [money(l["unit_price"]) for l in audit["lines"]]
assert LINE_AMT == ["805.50", "478.80", "1,160.00", "1,680.00"], LINE_AMT
assert UNIT_PRIX == ["268.50", "39.90", "580.00", "1,680.00"], UNIT_PRIX
assert money(SUB) == "4,124.30" and money(DUE) == "4,215.96"
assert money(PRE) == "3,944.30" and TAX == "236.66"
assert TAX_EXACT == "236.6580" and DUE_EXACT == "4215.96"
assert [len(x) for x in LIT] == list(LIT_LEN), (LIT_LEN, [len(x) for x in LIT])

ENTRIES: list[dict] = []

# 字号下限：正文 BODY=24，脚注 NOTE=20
BODY = 24
NOTE = 20
CAPS = 21        # 副标题（>脚注下限）
HEAD = 28        # 小节标题
BIG = 56         # 应付金额大字


def pos(x, y, w, h, child: str) -> str:
    return f'<Positioned left="{x}" top="{y}" width="{w}" height="{h}">{child}</Positioned>'


def rect(x, y, w, h, color: str, border: str = "") -> str:
    inner = f'<Container width="{w}" height="{h}" color="{color}" />'
    if border:
        inner = f'<Border border="{border}">{inner}</Border>'
    return pos(x, y, w, h, inner)


def T(eid, page, field, original, x, y, w, h, text, *, family=CJK, size=BODY,
      color=INK, style="", align="CENTER_LEFT", mode="dark", note=""):
    """输出一处文字并登记到 ENTRIES。含 < > & 的文本同样走 text 属性（保真通道）。"""
    st = f' fontStyle="{style}"' if style else ""
    body = (f'<Text fontFamily="{family}" fontSize="{size}" color="{color}"'
            f'{st} text="{text}" />')
    ENTRIES.append({
        "id": eid, "page": page, "field": field, "original": original,
        "rendered": text, "box": [x, y, x + w, y + h],
        "text_rect": [x, y, x + w, y + h], "align": align, "mode": mode,
        "font": {"family": family, "size": size, "color": color,
                 "style": style or "regular"},
        "note": note,
    })
    return (f'<Positioned left="{x}" top="{y}" width="{w}" height="{h}">'
            f'<Container width="{w}" height="{h}" alignment="{align}">{body}</Container>'
            f'</Positioned>')


def note_(x, y, w, h, text, *, family=CJK, size=NOTE, color=MUTED,
          style="", align="CENTER_LEFT"):
    """脚注/说明文字，字号 ≥ NOTE；不计入 text-map 条目。"""
    assert size >= NOTE, size
    st = f' fontStyle="{style}"' if style else ""
    return (f'<Positioned left="{x}" top="{y}" width="{w}" height="{h}">'
            f'<Container width="{w}" height="{h}" alignment="{align}">'
            f'<Text fontFamily="{family}" fontSize="{size}" color="{color}"{st}>'
            f'{text}</Text></Container></Positioned>')


def title(x, y, w, h, text, *, color=INK) -> str:
    """小节标题，字号 ≥ HEAD。"""
    return note_(x, y, w, h, text, size=HEAD, color=color, style="BOLD")


# --- 两页共用的页眉（重复页眉/编号一致性检查的目标）-------------------------
def header(P: int) -> list[str]:
    s = [rect(0, 0, W, 6, ACC),
         rect(M, 30, CW, 156, ZEBRA, "1 SOLID #E2E8F0"),
         rect(M, 30, 6, 156, ACC)]
    s.append(T("h-title", P, "title", "双语发票样张", M + 24, 50, 620, 50,
               "双语发票样张", size=36, style="BOLD"))
    s.append(T("h-sub", P, "title_en", "Bilingual Invoice Specimen", M + 24, 106,
               620, 28, "Bilingual Invoice Specimen", size=CAPS, color=MUTED))
    for i, (lab, val) in enumerate([("发票编号", ID_), ("开票日期", ISSUED),
                                    ("结算币种", CUR)]):
        s.append(T(f"h-meta{i + 1}-lab", P, f"meta[{i}].label", lab, 736, 46 + 40 * i,
                   176, 24, lab, size=NOTE, color=FAINT, align="CENTER_RIGHT"))
        s.append(T(f"h-meta{i + 1}-val", P, f"meta[{i}].value", val, 922, 40 + 40 * i,
                   214, 34, val, family=MONO, size=26, style="BOLD"))
    return s


# =========================================================================
# 第 1 页：结算与明细
# =========================================================================
def build_page1() -> str:
    P = 1
    s = header(P)

    # --- 交易双方 ---------------------------------------------------------
    for cx, who, lab, cap in [(M, SELLER, "卖方 / Seller", "开具方，按 invoice.seller 原样输出"),
                              (612, BUYER, "买方 / Buyer", "购方含日文字形，按 invoice.buyer 原样输出")]:
        s.append(note_(cx, 214, 540, 26, lab, size=NOTE, color=FAINT))
        s.append(T(f"p1-{'seller' if who == SELLER else 'buyer'}", P,
                   "seller" if who == SELLER else "buyer", who, cx, 246, 540, 46,
                   who, size=30, style="BOLD"))
        s.append(rect(cx, 302, 540, 1, RULE2))
        s.append(note_(cx, 316, 540, 26, cap))

    # --- 货品明细表 -------------------------------------------------------
    HY, HH = 360, 56
    s.append(rect(M, HY, CW, HH, ACC))
    cols = [("SKU", M + 16, 190, "CENTER_LEFT"),
            ("名称 / Name", M + 214, 420, "CENTER_LEFT"),
            ("数量", 680, 76, "CENTER_RIGHT"),
            ("单价", 770, 170, "CENTER_RIGHT"),
            ("行金额", 954, 198, "CENTER_RIGHT")]
    for j, (cap, cx, cwid, ca) in enumerate(cols):
        s.append(T(f"tbl-h{j + 1}", P, f"table_header[{j}]", cap, cx, HY + 13, cwid, 30,
                   cap, size=BODY, color=WHITE, style="BOLD", align=ca, mode="light"))

    ROW0, ROW_H = HY + HH, 78
    for i, it in enumerate(ITEMS):
        ry = ROW0 + i * ROW_H
        if i:
            s.append(rect(M, ry, CW, 1, RULE2))
        if i % 2:
            s.append(rect(M, ry, CW, ROW_H, ZEBRA))
        ty = ry + (ROW_H - 32) // 2
        s.append(T(f"r{i + 1}-sku", P, f"items[{i}].sku", it["sku"], M + 16, ty, 190, 32,
                   it["sku"], family=MONO, size=BODY, style="BOLD",
                   note="含 < > & 的 SKU 走 text 属性，原样渲染为字形"))
        s.append(T(f"r{i + 1}-name", P, f"items[{i}].name", it["name"], M + 214, ty, 420, 32,
                   it["name"], size=BODY, color=INK2))
        s.append(T(f"r{i + 1}-qty", P, f"items[{i}].quantity", str(it["quantity"]),
                   680, ty, 76, 32, str(it["quantity"]), family=MONO, size=BODY,
                   align="CENTER_RIGHT"))
        s.append(T(f"r{i + 1}-price", P, f"items[{i}].unit_price", it["unit_price"],
                   770, ty, 170, 32, UNIT_PRIX[i], family=MONO, size=BODY,
                   align="CENTER_RIGHT"))
        s.append(T(f"r{i + 1}-amt", P, f"items[{i}].line_amount", LINE_AMT[i], 954, ty,
                   198, 32, LINE_AMT[i], family=MONO, size=BODY, style="BOLD",
                   align="CENTER_RIGHT",
                   note=f"行金额 = 数量 {it['quantity']} × 单价 {it['unit_price']}"))
    TBL_END = ROW0 + 4 * ROW_H
    s.append(rect(M, TBL_END - 1, CW, 2, RULE))

    # --- 合计 ------------------------------------------------------------
    TY = TBL_END + 34
    s.append(title(M, TY, 700, 36, f"金额合计 / Totals（{CUR}）"))
    s.append(rect(M, TY + 44, CW, 1, RULE2))
    rows = [
        ("货品小计 / Subtotal", money(SUB), False, INK),
        ("折扣 / Discount", "−" + money(DISC), False, AMBER),
        ("税前货品金额 / Pre-tax goods", money(PRE), True, ACC),
        (f"税额 / VAT {TAXRATE}%", money(TAX), False, INK),
        ("运费 / Shipping", money(SHIP), False, INK),
        ("应付金额 / Amount due", money(DUE), True, ACC2),
    ]
    ROWS_Y, ROW_STEP = TY + 58, 60
    for i, (lab, val, strong, col) in enumerate(rows):
        ry = ROWS_Y + i * ROW_STEP
        if strong:
            s.append(rect(M, ry - 6, CW, 52, ZEBRA))
        s.append(T(f"t{i + 1}-lab", P, f"totals_row[{i}].label", lab, M + 8, ry, 520, 34,
                   lab, size=BODY, color=col, style="BOLD" if strong else ""))
        s.append(T(f"t{i + 1}-val", P, f"totals_row[{i}].value", val, 600, ry, 552, 34,
                   val, family=MONO, size=26,
                   style="BOLD" if strong else "", align="CENTER_RIGHT", color=col))
    T_END = ROWS_Y + 6 * ROW_STEP

    # --- 应付金额强调带 ---------------------------------------------------
    BY = T_END + 24
    s.append(rect(M, BY, CW, 156, ACC))
    s.append(rect(M, BY, 8, 156, ACC2))
    s.append(T("due-lab", P, "amount_due_label", "应付金额 / Amount due",
               M + 34, BY + 22, 560, 32, "应付金额 / Amount due", size=BODY,
               color=WHITE, style="BOLD", mode="light"))
    s.append(T("due-sub1", P, "amount_due_breakdown",
               f"税前 {money(PRE)} ＋ 税额 {money(TAX)} ＋ 运费 {money(SHIP)}",
               M + 34, BY + 68, 560, 28,
               f"税前 {money(PRE)} ＋ 税额 {money(TAX)} ＋ 运费 {money(SHIP)}",
               size=NOTE + 1, color=MINT, mode="light"))
    s.append(T("due-sub2", P, "tax_rounding_note",
               f"税额精确值 {TAX_EXACT}，ROUND_HALF_UP 至分",
               M + 34, BY + 106, 560, 28,
               f"税额精确值 {TAX_EXACT}，ROUND_HALF_UP 至分",
               size=NOTE + 1, color=MINT, mode="light"))
    s.append(T("due-big", P, "amount_due", DUE, 600, BY + 30, 518, 100,
               f"{CUR} {money(DUE)}", family=MONO, size=BIG, style="BOLD",
               color=WHITE, align="CENTER_RIGHT", mode="light"))

    s.append(note_(M, BY + 176, CW, 28,
                   "所有金额按 notes 的计税顺序以十进制定点计算，四舍五入至分；"
                   "详见第 2 页金额计算口径。"))
    s.append(rect(M, BOTTOM - 46, CW, 1, RULE2))
    s.append(note_(M, BOTTOM - 32, 760, 28, NOTES[0]))
    s.append(note_(900, BOTTOM - 32, 252, 28, "第 1 / 2 页", color=ACC,
                   style="BOLD", align="CENTER_RIGHT"))
    return close(s)


def close(s: list[str]) -> str:
    return "\n".join(["<Snapshot background=\"#FFFFFF\">",
                      f'<Container width="{W}" height="{H}">',
                      f'<Stack width="{W}" height="{H}">'] + s +
                     ["</Stack>", "</Container>", "</Snapshot>"]) + "\n"


# =========================================================================
# 第 2 页：说明与原样文字
# =========================================================================
def build_page2() -> str:
    P = 2
    s = header(P)

    # --- 附注 ------------------------------------------------------------
    s.append(title(M, 214, 900, 36, "附注 / Notes"))
    for i, nt in enumerate(NOTES):
        ny = 264 + i * 66
        s.append(rect(M, ny, CW, 64, ZEBRA, "1 SOLID #E2E8F0"))
        s.append(rect(M, ny, 4, 64, ACC))
        s.append(T(f"n{i + 1}", P, f"notes[{i}]", nt, M + 26, ny + 10, CW - 52, 44,
                   nt, size=BODY))

    # --- literal_lines 逐字符核对 -----------------------------------------
    LY = 554
    s.append(title(M, LY, 700, 36, "逐字符保真核对 / literal_lines"))
    s.append(note_(852, LY + 8, 300, 24, "等宽字体 · 原样排版", size=NOTE,
                   color=FAINT, align="CENTER_RIGHT"))
    for i, ln in enumerate(LIT):
        cy = 604 + i * 98
        s.append(rect(M, cy, CW, 92, WHITE, "1 SOLID #E2E8F0"))
        s.append(rect(M, cy, 4, 92, ACC))
        s.append(T(f"l{i + 1}-idx", P, f"literal_lines[{i}].index", f"L{i + 1}",
                   M + 26, cy + 10, 60, 26, f"L{i + 1}", family=MONO, size=NOTE,
                   color=FAINT, style="BOLD"))
        s.append(T(f"l{i + 1}-len", P, f"literal_lines[{i}].char_count",
                   f"{LIT_LEN[i]} 字符", 900, cy + 10, 230, 26, f"{LIT_LEN[i]} 字符",
                   size=NOTE, color=FAINT, align="CENTER_RIGHT"))
        s.append(rect(M + 26, cy + 42, CW - 52, 42, ZEBRA, "1 SOLID #E2E8F0"))
        s.append(T(f"l{i + 1}", P, f"literal_lines[{i}]", ln, M + 40, cy + 42,
                   CW - 80, 42, ln, family=MONO, size=BODY))

    # --- 富文本样张状态（PAID 绿色 / 斜线灰色 / 中文深色，共享基线）---------
    SY = 1022
    s.append(title(M, SY, 700, 36, "样张状态 / Specimen status"))
    s.append(rect(M, SY + 48, CW, 156, PAID_BG, f"2 SOLID {PAID_BD}"))
    rich = (f'<Positioned left="{M + 26}" top="{SY + 66}" width="{CW - 52}" height="84">'
            f'<Container width="{CW - 52}" height="84" alignment="CENTER">'
            f'<Text fontFamily="{CJK}" fontSize="48" fontStyle="BOLD" color="{INK}" '
            f'letterSpacing="1"><Text color="{GREEN}">PAID</Text>'
            f'<Raw color="{PAID_SLASH}"> / </Raw>'
            f'<Text color="{INK}">已结算</Text></Text>'
            f'</Container></Positioned>')
    ENTRIES.append({
        "id": "paid", "page": P, "field": "paid_stamp",
        "original": "PAID / 已结算", "rendered": "PAID / 已结算",
        "box": [M + 26, SY + 66, M + 26 + CW - 52, SY + 150],
        "text_rect": [M + 26, SY + 66, M + 26 + CW - 52, SY + 150],
        "align": "CENTER", "mode": "dark",
        "font": {"family": CJK, "size": 48, "color": INK, "style": "BOLD",
                 "segments": [
                     {"text": "PAID", "color": GREEN},
                     {"text": " / ", "color": PAID_SLASH, "whitespace": "Raw"},
                     {"text": "已结算", "color": INK}]},
        "note": "富文本：三段不同颜色共用同一基线，仅样张状态，未改变应付金额"})
    s.append(rich)
    s.append(note_(M + 26, SY + 168, CW - 52, 28,
                   f"样张状态标注，仅示意，不改变应付金额 {money(DUE)}",
                   size=NOTE, color=MUTED, align="CENTER"))

    # --- 金额计算口径 -----------------------------------------------------
    KY = 1240
    s.append(title(M, KY, 900, 36, "金额计算口径 / Tax order"))
    steps = [
        f"货品小计 {money(SUB)} 减去折扣 {money(DISC)}，得税前货品金额 {money(PRE)}",
        f"运费 {money(SHIP)} 不计税，在税额之外单独加回应付金额",
        f"税额 = 税前折后货品金额 {money(PRE)} × {TAXRATE}% = {TAX_EXACT}",
        f"税额四舍五入到分：{TAX_EXACT} → {money(TAX)}（ROUND_HALF_UP，"
        f"舍入误差 +{abs(float(TAX) - float(TAX_EXACT)):.4f}）",
        f"应付金额 = {money(PRE)} ＋ {money(TAX)} ＋ {money(SHIP)} = {money(DUE)}"
        f"（无二次舍入）",
    ]
    for i, st in enumerate(steps):
        sy = 1290 + i * 34
        s.append(rect(M, sy, 28, 28, ACC2))
        s.append(note_(M, sy, 28, 28, str(i + 1), family=MONO, size=NOTE,
                       color=WHITE, style="BOLD", align="CENTER"))
        s.append(T(f"step{i + 1}", P, f"tax_order[{i + 1}]", st, M + 40, sy - 2,
                   1064, 34, st, size=BODY, color=INK2))

    s.append(rect(M, BOTTOM - 46, CW, 1, RULE2))
    s.append(note_(M, BOTTOM - 32, 760, 28, "样张中的发票、公司与金额均为排版演示数据。"))
    s.append(note_(900, BOTTOM - 32, 252, 28, "第 2 / 2 页", color=ACC,
                   style="BOLD", align="CENTER_RIGHT"))
    return close(s)


BUILDERS = {"page1": ("invoice-page-01", build_page1),
            "page2": ("invoice-page-02", build_page2)}

# 迭代编号：a11-it-09/10 是第一版（正文缩到 14–21px，违反「正文≥24、脚注≥20」），
# 已被本版取代，日志保留不删。
ITER = {"page1": (11, 9), "page2": (12, 10)}


def main() -> None:
    which = sys.argv[1] if len(sys.argv) > 1 else "both"
    for key, (stem, fn) in BUILDERS.items():
        if which not in ("both", key):
            continue
        global ENTRIES
        ENTRIES = []
        dsl = fn()
        entries = list(ENTRIES)
        sizes = sorted({e["font"]["size"] for e in entries})
        assert min(sizes) >= NOTE, sizes
        (OUT / (stem + ".snapshot")).write_text(dsl, encoding="utf-8")  # 最终 DSL
        # 尝试副本留在 tmp，不覆盖上一版
        (TMP / "dsl").mkdir(parents=True, exist_ok=True)
        (TMP / "dsl" / ("v2-" + stem + ".snapshot")).write_text(dsl, encoding="utf-8")
        print(f"{stem}: DSL {len(dsl.encode('utf-8'))} B / {len(dsl)} chars, "
              f"{len(entries)} 处审计文字, 字号 {sizes}")
        r = C.render(TASK, dsl, stem, purpose=f"A11 交付页 {stem} 渲染",
                     dsl_name=stem + ".snapshot")
        print("   HTTP %s rid=%s bytes=%s" % (r["status"], r["request_id"],
                                              r["log"].get("response_bytes")))
        if r["status"] == 200:
            (OUT / (stem + ".png")).write_bytes(r["body"])
            (TMP / "preview" / (stem + ".png")).write_bytes(r["body"])
        for e in entries:
            e["page_image"] = stem + ".png"
        (TMP / "gen" / (stem + ".entries.json")).write_text(
            json.dumps(entries, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        spec = {"image": f"tmp/{RID}/A11/preview/{stem}.png", "threshold": 190,
                "bands": [{"label": e["id"], "x0": e["text_rect"][0],
                           "x1": e["text_rect"][2], "y0": e["text_rect"][1],
                           "y1": e["text_rect"][3], "mode": e["mode"]}
                          for e in entries]}
        (TMP / "gen" / (stem + ".measure.json")).write_text(
            json.dumps(spec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        seq, prev = ITER[key]
        seq = S.next_iteration_seq(TASK, seq)
        S.log_iteration(TASK, {
            "id": f"a11-it-{seq:02d}", "seq": seq, "phase": "build", "kind": "page",
            "supersedes": f"a11-it-{prev:02d}",
            "started_at": r["log"].get("started_at"),
            "ended_at": r["log"].get("ended_at"), "label": stem,
            "purpose": f"生成并渲染 {stem}",
            "request_ids": [r["request_id"]], "http_status": [r["status"]],
            "outcome": "done" if r["status"] == 200 else "incomplete",
            "detail": f"第一版（a11-it-{prev:02d}）正文缩到 14–21px，违反「正文≥24、"
                      f"脚注≥20」，已按 ≥24 重排：{len(entries)} 处需登记文字，"
                      f"像素盒清单 tmp/{RID}/A11/gen/{stem}.measure.json",
            "image_path": S.rel(TMP / "preview" / (stem + ".png"))
            if r["status"] == 200 else None,
        })


if __name__ == "__main__":
    main()
