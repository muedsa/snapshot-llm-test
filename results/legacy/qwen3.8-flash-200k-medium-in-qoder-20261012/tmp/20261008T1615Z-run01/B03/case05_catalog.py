"""B03 case-05：独立书店月度书单目录页（1200×1600）。

受众：店里翻月度书单的读者；情境：站在书架旁的阅读椅上，手里拿着这期书单，
要在两分钟内找到「哪个栏目、第几页、多少钱、现在能不能买到」。
用户要做的事：按类目定位页码 + 核对价格与库存。

独到手法：**引导线的线型本身就是信息**——点线＝现货、虚线＝需预订、双线＝已停印，
读者顺着线找页码时，手指经过的那条线已经把「能不能买到」说完了，不需要再读一遍小字。
已停印的书名另加 LINE_THROUGH + DOUBLE 删除线（探针 through3 实测该组合成立，
STRIKE_THROUGH 会被枚举拒绝），停印在版面上是「划掉」的直觉。
引导线本身用几何节点程序化绘制：纯空格的 <Text> 一个像素都不画，而带 clipBehavior 的
<Container> 一律 400（探针 l/m/f 与 k/n/o/p 的原始响应都留着），所以装饰线裁不出线长。

书目、作者、出版社、价格、页码全部是虚构演示数据（见同目录 data.json）；
页码由「评论版面页数」从刊首起累加算出，不是手填。
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(os.environ["SNAPSHOT_TASK_ROOT"])
RID = os.environ["SNAPSHOT_RUN_ID"]
for p in (ROOT / "tmp" / RID / "_suite" / "scripts", ROOT / "tmp" / RID / "B03"):
    sys.path.insert(0, str(p))
from dslkit import Doc, TextFit, n           # noqa: E402
import b03kit as K                            # noqa: E402

VER = os.environ.get("B03_VER", "v01")
W, H = 1200, 1600
PAPER, CARD = "#F4F1EA", "#EBE6DA"
INK, SOFT, RULE = "#1E1C18", "#6B6558", "#C9C2B2"
ACC, ACC2, WARN = "#9A3B2A", "#2E5468", "#7A6A1E"
MONO = "IBM Plex Mono,Courier New,monospace"
M = 72
COL_W, GUT = 504, 48
C1, C2 = M, M + COL_W + GUT
TOP = 336.0
ISSUE_PAGES = 96
P0 = 14          # 第一条书评所在页（前面是刊首语与栏目导览）

# 引导线线型＝库存状态（几何绘制，见 b03kit.rule_leader 的探针结论）
STOCK = {"现货": ("DOTTED", "4,9", ACC2), "需预订": ("DASHED", "11,7", WARN),
         "已停印": ("DOUBLE", "", SOFT)}

# (书名, 作者, 出版社, 年, 页数, 定价, 装帧, 库存, 评论版面页数)
CATS = [
    ("A", "文学 · 小说", [
        ("潮信", "沈寄舟", "岭上文艺", 2026, 388, 68, "平装", "现货", 2),
        ("夜航的鲸", "何未晞", "南海出版部", 2026, 256, 52, "平装", "现货", 1),
        ("墙内开花", "陈绿", "海岸线", 2025, 410, 78, "精装", "需预订", 2),
        ("第七个冬天", "A. Lark", "Northgate", 1998, 302, 128, "精装", "已停印", 1)]),
    ("B", "非虚构 · 田野", [
        ("盐井纪事", "罗一鸣", "山川", 2026, 342, 66, "平装", "现货", 2),
        ("夜班", "柯凉", "城市观察", 2026, 228, 45, "平装", "现货", 1),
        ("渡口的人", "苏眉", "云杉小社", 2019, 276, 88, "精装", "需预订", 1),
        ("采石场", "周迟", "人民长流", 2026, 402, 92, "平装", "现货", 2)]),
    ("C", "历史 · 传记", [
        ("驿路千年", "林声远", "方志阁", 2025, 512, 118, "精装", "现货", 2),
        ("米价与盐税", "何未晞", "方志阁", 2024, 356, 86, "平装", "已停印", 1),
        ("一个图书馆员的 1937", "罗一鸣", "城市观察", 2026, 298, 62, "平装", "现货", 2),
        ("海图上的名字", "柯凉", "南海出版部", 2026, 330, 74, "平装", "需预订", 1)]),
    ("D", "艺术 · 影像", [
        ("银盐时代", "陈绿", "光合", 2026, 216, 168, "精装", "现货", 2),
        ("街头钢琴", "A. Lark", "Northgate", 2003, 144, 138, "精装", "已停印", 1),
        ("山的十二种画法", "周迟", "岭上文艺", 2025, 204, 98, "平装", "现货", 1),
        ("暗房笔记", "苏眉", "光合", 2022, 188, 58, "平装", "需预订", 2)]),
    ("E", "思想 · 社科", [
        ("注意力的价格", "柯凉", "断面", 2026, 286, 64, "平装", "现货", 2),
        ("规则的缝隙", "林声远", "人民长流", 2026, 340, 72, "平装", "现货", 1),
        ("论沉默", "何未晞", "断面", 2021, 172, 42, "平装", "已停印", 1),
        ("城市如何失败", "罗一鸣", "城市观察", 2026, 424, 106, "精装", "需预订", 2)]),
    ("F", "童书 · 绘本", [
        ("月亮借我", "白鹿 绘", "童盟", 2026, 40, 39, "精装", "现货", 1),
        ("一粒米的旅行", "沈寄舟", "山川", 2025, 48, 42, "平装", "现货", 1),
        ("爷爷的收音机", "岑树 绘", "童盟", 2024, 36, 46, "精装", "已停印", 2),
        ("出发，小蓝船", "白鹿", "南海出版部", 2026, 32, 36, "平装", "需预订", 1)]),
]

# 页码计划：按栏目顺序、条目顺序，从 P0 起按评论版面页数累加
plan, cur = {}, P0
for ci, (_tag, _name, books) in enumerate(CATS):
    start = cur
    for bi, b in enumerate(books):
        plan[(ci, bi)] = cur
        cur += b[8]
    plan[(ci, "span")] = (start, cur - 1)
LAST_PAGE = cur - 1
BOOKS = [b for _t, _n, bs in CATS for b in bs]
PRICES = [b[5] for b in BOOKS]
AVG_PRICE = sum(PRICES) / len(PRICES)
_S = sorted(PRICES)
# 24 种是偶数样本，中位数取中间两项的均值，不能只取第 13 项
MEDIAN_PRICE = (_S[11] + _S[12]) / 2
MED_TXT = f"¥{MEDIAN_PRICE:g}"
HARDCOVER = sum(1 for b in BOOKS if b[6] == "精装")
STOCK_N = {k: sum(1 for b in BOOKS if b[7] == k) for k in STOCK}
REV_PAGES = sum(b[8] for b in BOOKS)
PUB_N = {}
for b in BOOKS:
    PUB_N[b[2]] = PUB_N.get(b[2], 0) + 1
TOP_PUB = max(PUB_N.items(), key=lambda kv: (kv[1], kv[0]))

assert len(BOOKS) == 24 and REV_PAGES == LAST_PAGE - P0 + 1
assert LAST_PAGE <= ISSUE_PAGES, f"书评页 {LAST_PAGE} 超出全刊 {ISSUE_PAGES}"

tf = TextFit()
d = Doc(W, H, bg=PAPER, font="Inter,Noto Sans CJK SC")
d.rect(0, 0, W, H, PAPER)

# ---------- 刊头 ----------
K.tlab(d, tf, "mast", M, 84, 620, 92, "月度书单", 78, INK, style="BOLD", spacing=6)
K.tlab(d, tf, "mast-sub", M, 178, 620, 26, "目录 / CONTENTS · 2026 年 10 月号 · 第 4 期",
       18, SOFT, spacing=1.2)
K.tlab(d, tf, "shop", 700, 88, 428, 30, "街角书店 · 选书部", 22, ACC, style="BOLD",
       align="END")
K.tlab(d, tf, "issue", 700, 124, 428, 24, f"全刊 {ISSUE_PAGES} 页 · 本月 {len(BOOKS)} 种",
       18, INK, align="END", font=MONO)
K.tlab(d, tf, "issue2", 700, 152, 428, 24, f"书评占 {REV_PAGES} 页 · 第 {P0}–{LAST_PAGE} 页",
       17, SOFT, align="END", font=MONO)
d.line(M, 216, W - M, 216, 2.5, INK)
d.line(M, 222, W - M, 222, 1, RULE)

# ---------- 导语条 ----------
K.tlab(d, tf, "lead", M, 240, 700, 26,
       f"均价 {K.money(AVG_PRICE)} · 最高 {K.money(max(PRICES))} · 最低 {K.money(min(PRICES))}"
       f" · 精装 {HARDCOVER} 种", 18, INK)
K.tlab(d, tf, "lead2", M, 270, 760, 24,
       "选书口径：只收当月新印与值得再版的旧书；页码＝该条评论起始页。", 16, SOFT)
K.tlab(d, tf, "lead3", 700, 240, 428, 26,
       f"出现最多：{TOP_PUB[0]}（{TOP_PUB[1]} 种）", 17, SOFT, align="END")
K.tlab(d, tf, "lead4", 700, 270, 428, 24, "线型＝库存：点线现货 / 虚线预订 / 双线停印",
       16, SOFT, align="END")
d.line(M, 312, W - M, 312, 1, RULE)

# ---------- 双栏目录 ----------
ENTRY_P, HEAD_H, SUB_H = 60.0, 46.0, 20.0
TITLE_W = 250.0
col_bottom = {}
for c, items in enumerate((CATS[0:3], CATS[3:6])):
    x0 = C1 if c == 0 else C2
    y = TOP
    for ci, (tag, name, books) in enumerate(items if c == 0 else CATS[3:6]):
        gci = ci if c == 0 else ci + 3
        p0, p1 = plan[(gci, "span")]
        d.rect(x0, y + 30, COL_W, 1.5, RULE)
        K.tlab(d, tf, f"ch{gci}", x0, y, 30, 30, tag, 22, ACC, style="BOLD")
        K.tlab(d, tf, f"chn{gci}", x0 + 36, y, 300, 30, name, 22, INK, style="BOLD")
        K.tlab(d, tf, f"chp{gci}", x0 + COL_W - 190, y, 190, 28,
               f"第 {p0}–{p1} 页 · {len(books)} 种", 16, SOFT, align="END", font=MONO)
        y += HEAD_H
        for bi, b in enumerate(books):
            sty, gaps, scol = STOCK[b[7]]
            page = plan[(gci, bi)]
            out_of_print = b[7] == "已停印"
            K.tlab(d, tf, f"t{gci}{bi}", x0, y, TITLE_W, 26, b[0], 19, INK,
                   **({"deco": "LINE_THROUGH", "deco_style": "DOUBLE",
                       "deco_color": SOFT, "deco_th": 1.0} if out_of_print else {}))
            # 引导线紧跟书名：宽度由 TextFit 的字宽估算得出（估算偏保守，再留 10% 余量），
            # 超过 TITLE_W 的长书名回落到固定列，避免与页码相碰。
            est = min(TITLE_W, tf.w(b[0], 19) * 1.10 + 8)
            # 停印书名的删除线也是双细线，紧跟其后会被读成「一条超长删除线」（v03 看图），
            # 所以这一类退回固定列，用空白把两个元素分开。
            lx = x0 + (TITLE_W if out_of_print else est)
            lw = (x0 + COL_W - 96 - 14) - lx
            assert lw >= 40, f"{b[0]} 引导线只剩 {lw:.0f}px"
            K.rule_leader(d, lx, y, lw, 26, style=sty, color=scol,
                          gaps=gaps or "2,7")
            K.tlab(d, tf, f"p{gci}{bi}", x0 + COL_W - 84, y, 84, 26, str(page), 19, INK,
                   align="END", font=MONO)
            rest = f"{b[4]}p·{b[6]}"
            if out_of_print:
                # 停印已由删除线与双线说完，这里让位给更长的西文条目名
                sub = f"{b[1]} · {b[2]} · {b[3]} · {rest}"
            else:
                sub = f"{b[1]} · {b[2]} · {b[3]} · {rest} · {b[7]}"
            K.tlab(d, tf, f"s{gci}{bi}", x0, y + 28, COL_W - 104, SUB_H, sub, 14, SOFT)
            K.tlab(d, tf, f"pr{gci}{bi}", x0 + COL_W - 96, y + 26, 96, 24,
                   K.money(b[5]), 17, ACC if b[6] == "精装" else INK, align="END",
                   font=MONO)
            y += ENTRY_P
        y += 16
    col_bottom[c] = y - 16
    assert col_bottom[c] <= 1244, f"第 {c + 1} 栏底部 {col_bottom[c]:.0f} 越出中带"

# ---------- 底带：图例与口径 ----------
BAND_T = 1264.0
d.line(M, BAND_T - 18, W - M, BAND_T - 18, 1, RULE)
K.tlab(d, tf, "lg-hd", M, BAND_T, 300, 26, "引导线图例", 19, INK, style="BOLD")
for i, (k, (sty, gaps, scol)) in enumerate(STOCK.items()):
    ly = BAND_T + 34 + i * 30
    K.tlab(d, tf, f"lg{k}", M, ly, 74, 24, k, 17, INK)
    K.rule_leader(d, M + 82, ly, 150, 24, style=sty, color=scol, gaps=gaps or "2,7")
    note = {"现货": "在架，可直接买", "需预订": "4–7 个工作日到",
            "已停印": "仅二手或库存尾数"}[k]
    K.tlab(d, tf, f"lgn{k}", M + 244, ly, 250, 24, note, 15, SOFT)
K.tlab(d, tf, "lg-note", M, BAND_T + 132, 494, 46,
       f"停印 {STOCK_N['已停印']} 种仍留在书单上，因为它们值得被读到；"
       "线型换成双线，提醒不要按新书价购买。", 15, SOFT, lines=2, valign="TOP")
K.tlab(d, tf, "lg-note2", M, BAND_T + 186, 494, 24,
       f"价格标红＝精装 {HARDCOVER} 种；黑色为平装 {len(BOOKS) - HARDCOVER} 种。",
       15, SOFT)

K.tlab(d, tf, "st-hd", C2, BAND_T, 300, 26, "本期统计", 19, INK, style="BOLD")
stats = [("书目", f"{len(BOOKS)} 种 / {len(CATS)} 栏目"),
         ("评论页数", f"{REV_PAGES} 页（第 {P0}–{LAST_PAGE} 页）"),
         ("码洋合计", K.money(sum(PRICES))),
         ("均价 / 中位价", f"{K.money(AVG_PRICE)} / {MED_TXT}"),
         ("装帧", f"精装 {HARDCOVER} 种 · 平装 {len(BOOKS) - HARDCOVER} 种"),
         ("库存", f"现货 {STOCK_N['现货']} · 预订 {STOCK_N['需预订']} · 停印 {STOCK_N['已停印']}")]
for i, (k, v) in enumerate(stats):
    sy = BAND_T + 34 + i * 26
    K.tlab(d, tf, f"stk{i}", C2, sy, 130, 24, k, 16, SOFT)
    K.tlab(d, tf, f"stv{i}", C2 + 134, sy, COL_W - 134, 24, v, 16, INK, align="END",
           font=MONO)
    d.line(C2, sy + 25, C2 + COL_W, sy + 25, 1, RULE)
K.tlab(d, tf, "st-foot", C2, BAND_T + 196, COL_W, 24,
       "以上数字由 data.json 累加得出；书目与价格为虚构演示数据。", 15, SOFT)
assert BAND_T + 220 <= H - 60

# ---------- 页脚 ----------
d.line(M, H - 64, W - M, H - 64, 2.5, INK)
K.tlab(d, tf, "ft-l", M, H - 52, 620, 24, "街角书店 · 月度书单目录 · 演示数据", 15, SOFT)
K.tlab(d, tf, "ft-r", 700, H - 52, 428, 24,
       f"Snapshot DSL 纯文本渲染 · {W}×{H} · {VER}", 15, SOFT, align="END", font=MONO)

out = d.dsl()
tmp = ROOT / "tmp" / RID / "B03"
(tmp / f"case05-{VER}.snapshot").write_text(out, encoding="utf-8")
odata = ROOT / "outputs" / RID / "B03" / "case-05"
odata.mkdir(parents=True, exist_ok=True)
(odata / "data.json").write_text(json.dumps({
    "note": "虚构演示数据：书名、作者、出版社、年份、页数、定价、库存状态均非真实书目；"
            "页码由「评论版面页数」从第 14 页起累加得出。",
    "issue": {"pages": ISSUE_PAGES, "first_review_page": P0,
              "last_review_page": LAST_PAGE, "review_pages": REV_PAGES},
    "leader_style_means": {k: v[0] for k, v in STOCK.items()},
    "leader_rendering": "引导线为几何节点程序化绘制（圆点/短横/双细线），"
                        "已停印书名叠加 LINE_THROUGH+DOUBLE 删除线",
    "categories": [{"tag": t, "name": nm, "page_span": list(plan[(i, "span")]),
                    "books": [{"title": b[0], "author": b[1], "publisher": b[2],
                               "year": b[3], "pages": b[4], "price": b[5],
                               "binding": b[6], "stock": b[7], "review_pages": b[8],
                               "catalog_page": plan[(i, j)]}
                              for j, b in enumerate(bs)]}
                   for i, (t, nm, bs) in enumerate(CATS)],
    "totals": {"titles": len(BOOKS), "categories": len(CATS),
               "price_sum": sum(PRICES), "avg_price": round(AVG_PRICE, 2),
               "median_price": MEDIAN_PRICE, "min_price": min(PRICES),
               "max_price": max(PRICES), "hardcover": HARDCOVER,
               "stock_counts": STOCK_N,
               "publisher_counts": PUB_N,
               "top_publisher": {"name": TOP_PUB[0], "titles": TOP_PUB[1]}},
    "render": {"canvas": [W, H], "version": VER, "dsl_chars": len(out),
               "image_nodes": out.count("<Image")},
}, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"{VER} chars {len(out)} TextFit {tf.n} problems {len(tf.problems)} "
      f"Image {out.count('<Image')}")
for p in tf.problems:
    print("  !", p)
print(f"pages {P0}-{LAST_PAGE} rev {REV_PAGES} col_bottom "
      f"{col_bottom[0]:.0f}/{col_bottom[1]:.0f}")
print(f"prices sum {sum(PRICES)} avg {AVG_PRICE:.1f} med {MEDIAN_PRICE:g} "
      f"hc {HARDCOVER} stock {STOCK_N} top {TOP_PUB}")
