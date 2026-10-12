"""B03 case-06：咖啡馆柜台季节菜单（1080×1350）。

受众与情境：柜台前的顾客平均停留 30 秒，要在一眼之间决定点什么、并确认
「有没有我会过敏的东西」和「这杯咖啡因强不强」。因此：
- 过敏原用行内字母角标（WidgetSpan 内嵌带 Text 的 Container，探针 wschip）
  直接跟在配料说明里，而不是让人去数脚注；
- 咖啡因强度用行内三圆点，点多少由算出来的 mg 决定，不是手填；
- 手冲的产地长句**故意**用 overflow=ELLIPSIS 截断，保证网格不被撑破，
  完整豆卡同时列在页面下方的脚注里（截断不藏信息）。

所有品名、价格、配比、热量都是虚构演示数据（见同目录 data.json）；
咖啡因 mg、萃取比、热量合计、价格统计与季节天数均由脚本计算。
"""
import json
import os
import sys
from datetime import date
from pathlib import Path

ROOT = Path(os.environ["SNAPSHOT_TASK_ROOT"])
RID = os.environ["SNAPSHOT_RUN_ID"]
for p in (ROOT / "tmp" / RID / "_suite" / "scripts", ROOT / "tmp" / RID / "B03"):
    sys.path.insert(0, str(p))
from dslkit import Doc, TextFit, n                      # noqa: E402
import b03kit as K                                       # noqa: E402

VER = os.environ.get("B03_VER", "v01")
W, H = 1080, 1350
BOARD, PANEL, PANEL2 = "#241C17", "#2E241D", "#3A2D24"
CREAM, SOFT, DIM = "#F2E7D5", "#C3B29B", "#6C5B4B"
AMBER, SAGE, CORAL = "#E0A526", "#8FA37E", "#D2694B"
MONO = "IBM Plex Mono,Courier New,monospace"
M = 64
COL_W, GUT = 456, 40
C1, C2 = M, M + COL_W + GUT
BAND, PH = 972.0, 236.0   # 图例带上沿与面板高（栏目底以它为界）
SEASON = (date(2026, 10, 1), date(2026, 11, 30))
DAYS = (SEASON[1] - SEASON[0]).days + 1

# 过敏原：字母与底色列在一起，图例逐条解释
ALLER = {"A": ("乳制品", "#2E5468"), "B": ("坚果", "#7A4A22"),
         "C": ("麸质", "#7A6A1E"), "D": ("蛋", "#5B4A6A")}
# 演示模型：每克咖啡粉约含 10.2mg 咖啡因，进入杯中的比例按器具
CAFF_PER_G = 10.2
YIELD = {"意式": 0.65, "手冲": 0.72, "冷萃": 0.48, "无": 0.0}
# 萃取液量 = 经过咖啡粉的水量；杯量减去它就是要/奶/冰，两者不能混为一谈
BREW_RATIO = {"意式": 2.0, "手冲": None, "冷萃": None, "无": None}
STRENGTH_CUTS = (20, 90, 150)


def drink(name, desc, price, ml, dose, method, allergens=(), veg=True, kcal=None):
    mg = dose * CAFF_PER_G * YIELD[method]
    brew = (dose * BREW_RATIO[method] if BREW_RATIO[method]
            else (ml if dose else 0))
    return {"name": name, "desc": desc, "price": price, "ml": ml, "dose": dose,
            "method": method, "allergens": list(allergens), "veg": veg,
            "kcal": kcal, "mg": mg, "brew_ml": brew,
            "add_ml": (ml - brew) if (ml and dose) else (ml if ml else 0),
            "ratio": (f"1:{brew / dose:.1f}" if dose else "—"),
            "strength": sum(1 for c in STRENGTH_CUTS if mg >= c)}


ESP = [drink("浓缩 Espresso", "18g 粉双份，可可与焦糖尾韵", 22, 36, 18, "意式"),
       drink("澳白 Flat White", "双份 + 微泡牛奶，杯量小茶感重", 30, 160, 18, "意式", "A"),
       drink("燕麦拿铁", "双份 + 燕麦奶，燕麦经同一产线需留意麸质", 34, 240, 18, "意式", "AC"),
       drink("摩卡 Mocha", "单份 + 黑巧酱 + 牛奶 + 榛果碎", 36, 260, 10, "意式", "AB", veg=False),
       drink("冰博客拿铁", "双份浇在冰博克牛奶上，奶味最厚", 38, 280, 18, "意式", "A")]

POUR = [dict(drink("耶加雪菲 科契尔", "水洗 · 茉莉、柑橘、红茶尾", 45, 240, 15, "手冲"),
             origin="埃塞俄比亚 耶加雪菲 科契尔 太阳合作社 水洗 G1 原生种 1950m 花香/柑橘/红茶尾 批次 26-A 烘焙 09/28"),
        dict(drink("洪都拉斯 雪松", "厌氧日晒 · 酒香、荔枝、可可", 52, 240, 15, "手冲"),
             origin="洪都拉斯 马尔卡拉 雪松庄园 厌氧日晒 72h SL28 1700m 酒香/荔枝/黑可可 批次 26-C 烘焙 09/30"),
        dict(drink("云南 保山", "蜜处理 · 话梅、红糖、坚果", 42, 240, 15, "手冲"),
             origin="中国云南 保山 潞江坝 农户联合 半日晒 卡蒂姆 1200m 话梅/红糖/烤坚果 批次 26-B 烘焙 10/02")]

COLD = [drink("冷萃黑咖啡", "16 小时低温慢滴，酸度低、耐放", 32, 300, 36, "冷萃"),
        drink("海盐焦糖冷萃", "冷萃 + 焦糖海盐奶盖", 38, 330, 36, "冷萃", "A"),
        drink("柚子气泡美式", "双份 + 苏打 + 柚子皮，解腻", 30, 350, 18, "意式"),
        drink("抹茶气泡（无咖啡因）", "宇治抹茶 + 苏打，不含咖啡", 28, 320, 0, "无")]

FOOD = [drink("黄油可颂", "法式发酵黄油，两天开酥", 26, None, 0, "无", "CA", kcal=380),
        drink("巴斯克芝士", "重乳酪，表面焦化，冷藏供应", 32, None, 0, "无", "AD", kcal=420),
        drink("香蕉坚果面包", "无添加蔗糖，腰果与核桃", 24, None, 0, "无", "CDB", veg=False, kcal=310),
        drink("米饼（无麸质）", "大米粉制作，配红豆沙", 18, None, 0, "无", kcal=190)]

SECTIONS = [("意式 Espresso Bar", ESP, C1), ("手冲单品 Pour Over", POUR, C1),
            ("冷萃与气泡 Cold", COLD, C2), ("烘焙与点心 Bakery", FOOD, C2)]
ITEMS = ESP + POUR + COLD + FOOD
DRINKS = [it for it in ITEMS if it["ml"]]
assert len(ITEMS) == 16 and len(DRINKS) == 12
PRICES = [it["price"] for it in ITEMS]
DRINK_PRICES = [it["price"] for it in DRINKS]
AVG_DRINK = sum(DRINK_PRICES) / len(DRINK_PRICES)
ALLER_N = {k: sum(1 for it in ITEMS if k in it["allergens"]) for k in ALLER}
KCAL_TOTAL = sum(it["kcal"] or 0 for it in FOOD)
MAX_MG = max(DRINKS, key=lambda it: it["mg"])
MIN_MG = min((it for it in DRINKS if it["mg"] > 0), key=lambda it: it["mg"])
STRENGTH_N = {s: sum(1 for it in DRINKS if it["strength"] == s) for s in range(4)}
assert all(it["mg"] > 0 for it in ESP + POUR + [COLD[0], COLD[1], COLD[2]])
assert DAYS == 61

tf = TextFit()
d = Doc(W, H, bg=BOARD, font="Inter,Noto Sans CJK SC")
d.rect(0, 0, W, H, BOARD)
d.rect(0, 0, W, 176, PANEL)
d.line(M, 176, W - M, 176, 2, AMBER)

# ---------- 抬头 ----------
K.tlab(d, tf, "mast", M, 40, 620, 62, "街角咖啡 · 秋季菜单", 44, CREAM, style="BOLD",
       spacing=2)
K.tlab(d, tf, "mast-en", M, 112, 620, 26, "AUTUMN MENU · 柜台点单 30 秒版", 17, SOFT,
       spacing=3)
K.tlab(d, tf, "win", 660, 44, 356, 30,
       f"{SEASON[0]:%m/%d}–{SEASON[1]:%m/%d} · 共 {DAYS} 天", 20, AMBER, align="END",
       font=MONO)
K.tlab(d, tf, "win2", 660, 80, 356, 24, f"{len(ITEMS)} 个品项 · 4 个分区", 17, SOFT,
       align="END")
K.tlab(d, tf, "win3", 660, 108, 356, 24, "价格含服务费 · 外带 -3 元", 15, DIM,
       align="END")


DOT_ON, DOT_OFF = AMBER, "#8A7358"


def strength_dots(x, yc, n_pts, dia=11, pitch=15):
    """咖啡因强度三圆点：实心＝达档数，暗色＝未达档。"""
    for i in range(3):
        d.dot(x + i * pitch, yc, dia, DOT_ON if i < n_pts else DOT_OFF)


def section(title, items, x0, y):
    K.tlab(d, tf, f"sh-{title}", x0, y, COL_W - 90, 30, title, 22, AMBER, style="BOLD")
    K.tlab(d, tf, f"shn-{title}", x0 + COL_W - 86, y, 86, 28, f"{len(items)} 项", 16,
           DIM, align="END", font=MONO)
    d.line(x0, y + 36, x0 + COL_W, y + 36, 1.5, PANEL2)
    yy = y + 44
    for it in items:
        K.tlab(d, tf, f"nm-{it['name']}", x0, yy, COL_W - 74, 28, it["name"], 21, CREAM)
        if it["ml"]:
            # 强度点用几何圆点画在名字后（WidgetSpan 的行内方块会被顶到基线上方，
            # 且空格宽度不可控）；横向位置按 TextFit 字宽估算，留 12px 间隔。
            dx = x0 + min(COL_W - 74, tf.w(it["name"], 21) + 12)
            assert dx + 45 <= x0 + COL_W - 70, it["name"]
            strength_dots(dx, yy + 14, it["strength"])
        K.tlab(d, tf, f"pr-{it['name']}", x0 + COL_W - 66, yy, 66, 28,
               f"¥{it['price']}", 21, CREAM, align="END", font=MONO)
        desc = [("t", it["desc"] + "  ")]
        for a in it["allergens"]:
            desc.append(("badge", a, ALLER[a][1], "#FFFFFF"))
            desc.append(("t", " "))
        K.inline_runs(d, x0, yy + 30, COL_W, 22, desc, 14, SOFT)
        if it.get("origin"):
            # 故意截断：产地长句比框宽，保证出现省略号而不是悄悄溢出
            assert tf.w(it["origin"], 13) > COL_W - 8, it["name"]
            d.pos(x0, yy + 52, COL_W - 8, 18,
                  f'<Container width="{n(COL_W - 8)}" height="{n(18)}" '
                  f'alignment="CENTER_LEFT">'
                  + K.text_markup(it["origin"], 13, DIM, font=MONO,
                                  soft_wrap="false", overflow="ELLIPSIS")
                  + "</Container>")
            K.tlab(d, tf, f"spec-{it['name']}", x0, yy + 70, COL_W, 18,
                   f"{it['dose']}g 粉 / {it['ml']}ml 水 · 萃取比 {it['ratio']} · "
                   f"咖啡因约 {it['mg']:.0f}mg", 13, SOFT, font=MONO)
            yy += 90
        else:
            if not it["ml"]:
                meta = f"约 {it['kcal']} kcal / 件"
            elif not it["dose"]:
                meta = f"{it['ml']}ml 杯 · 不含咖啡"
            else:
                meta = (f"{it['ml']}ml 杯 / {it['dose']}g 粉 → {it['brew_ml']:.0f}ml 液 "
                        f"{it['ratio']} / 约 {it['mg']:.0f}mg")
            K.tlab(d, tf, f"meta-{it['name']}", x0, yy + 50, COL_W, 18, meta, 13, DIM,
                   font=MONO)
            yy += 72
    return yy


y_left = section(*SECTIONS[0][:2], C1, 208)
y_left = section(*SECTIONS[1][:2], C1, y_left + 10)
y_right = section(*SECTIONS[2][:2], C2, 208)
y_right = section(*SECTIONS[3][:2], C2, y_right + 10)
assert max(y_left, y_right) <= BAND - 20, f"栏目底 {y_left:.0f}/{y_right:.0f} 越出菜单带"

# ---------- 图例与口径 ----------
d.rect(M, BAND, COL_W, PH, PANEL)
d.rect(C2, BAND, COL_W, PH, PANEL)
K.tlab(d, tf, "lg-hd", M + 20, BAND + 14, 300, 26, "过敏原角标", 20, CREAM, style="BOLD")
for i, (k, (nm, col)) in enumerate(ALLER.items()):
    ly = BAND + 48 + i * 30
    K.inline_runs(d, M + 20, ly, 200, 24, [("badge", k, col, "#FFFFFF"),
                                           ("t", " " + nm)], 16, SOFT)
K.tlab(d, tf, "caf-hd", M + 20, BAND + 176, 74, 24, "咖啡因", 16, SOFT)
for i, (cut, lab, lx, lw) in enumerate(
        [(1, "<90mg", 104, 52), (2, "90–150", 205, 62), (3, "≥150mg", 316, 62)]):
    strength_dots(M + lx, BAND + 188, cut)
    K.tlab(d, tf, f"caf{i}", M + lx + 41, BAND + 176, lw, 24, lab, 14, DIM, font=MONO)
    assert M + lx + 41 + lw <= M + COL_W - 20, lab
K.tlab(d, tf, "lg-note", M + 20, BAND + 200, COL_W - 40, 32,
       "角标紧跟配料句；同一产线制作的产品可能残留微量坚果与麸质。", 13, DIM)

K.tlab(d, tf, "st-hd", C2 + 20, BAND + 14, 300, 26, "点单参考", 20, CREAM, style="BOLD")
stats = [("饮品均价 / 区间", f"¥{AVG_DRINK:.0f} · ¥{min(DRINK_PRICES)}–{max(DRINK_PRICES)}"),
         ("全部品项合计", f"{len(ITEMS)} 项 ¥{sum(PRICES)}"),
         ("咖啡因最高", f"{MAX_MG['name']} 约 {MAX_MG['mg']:.0f}mg"),
         ("咖啡因最低（含咖啡）", f"{MIN_MG['name']} 约 {MIN_MG['mg']:.0f}mg"),
         ("强度分布", " · ".join(f"{s}点{STRENGTH_N[s]}" for s in range(4))),
         ("点心热量合计", f"{KCAL_TOTAL} kcal（4 件各一）"),
         ("素食可点", f"{sum(1 for it in ITEMS if it['veg'])} / {len(ITEMS)} 项")]
for i, (k, v) in enumerate(stats):
    sy = BAND + 48 + i * 26
    K.tlab(d, tf, f"stk{i}", C2 + 20, sy, 152, 20, k, 14, SOFT)
    K.tlab(d, tf, f"stv{i}", C2 + 176, sy, COL_W - 196, 20, v, 14, CREAM, align="END",
           font=MONO)
    d.line(C2 + 20, sy + 21, C2 + COL_W - 20, sy + 21, 1, PANEL2)

# ---------- 豆卡脚注 ----------
FOOT = BAND + PH + 16
d.line(M, FOOT - 12, W - M, FOOT - 12, 1.5, PANEL2)
for i, p in enumerate(POUR):
    K.tlab(d, tf, f"po{i}", M, FOOT + i * 22, W - 2 * M, 20,
           f"完整豆卡 {i + 1}　{p['origin']}", 13, SOFT)
K.tlab(d, tf, "foot", M, FOOT + 62, 620, 22, "街角咖啡 · 季节菜单 · 演示数据", 14, DIM)
K.tlab(d, tf, "foot-r", 660, FOOT + 62, 356, 22,
       f"Snapshot DSL · {W}×{H} · {VER}", 14, DIM, align="END", font=MONO)
assert FOOT + 84 <= H - 20, FOOT

out = d.dsl()
tmp = ROOT / "tmp" / RID / "B03"
(tmp / f"case06-{VER}.snapshot").write_text(out, encoding="utf-8")
odata = ROOT / "outputs" / RID / "B03" / "case-06"
odata.mkdir(parents=True, exist_ok=True)
(odata / "data.json").write_text(json.dumps({
    "note": "虚构演示数据：品名、价格、配比、热量均非真实门店数据。咖啡因 mg 用"
            f"「每克咖啡粉 {CAFF_PER_G}mg × 器具萃取比例」模型算出，"
            "强度点数由 mg 阈值 %s 分档，不是手填。" % (STRENGTH_CUTS,),
    "season": {"from": SEASON[0].isoformat(), "to": SEASON[1].isoformat(),
               "days": DAYS},
    "caffeine_model": {"mg_per_dose_gram": CAFF_PER_G, "yield_by_method": YIELD,
                       "strength_thresholds_mg": list(STRENGTH_CUTS),
                       "espresso_yield_ml_per_gram": BREW_RATIO["意式"]},
    "allergens": {k: {"meaning": v[0], "items": ALLER_N[k]} for k, v in ALLER.items()},
    "sections": [{"name": nm, "items": [{"name": it["name"], "price": it["price"],
                                         "ml": it["ml"], "dose_g": it["dose"],
                                         "method": it["method"],
                                         "brewed_coffee_ml": round(it["brew_ml"], 1),
                                         "dilution_ml": round(it["add_ml"], 1),
                                         "brew_ratio": it["ratio"],
                                         "caffeine_mg": round(it["mg"], 1),
                                         "strength_dots": it["strength"],
                                         "allergens": it["allergens"],
                                         "vegetarian": it["veg"],
                                         "kcal": it["kcal"],
                                         "origin_full": it.get("origin")}
                                        for it in items]}
                 for nm, items, _x in SECTIONS],
    "totals": {"items": len(ITEMS), "drinks": len(DRINKS),
               "price_sum": sum(PRICES), "avg_drink_price": round(AVG_DRINK, 2),
               "drink_price_min": min(DRINK_PRICES),
               "drink_price_max": max(DRINK_PRICES),
               "kcal_total_bakery": KCAL_TOTAL,
               "vegetarian": sum(1 for it in ITEMS if it["veg"]),
               "strength_distribution": STRENGTH_N,
               "max_caffeine": {"name": MAX_MG["name"], "mg": round(MAX_MG["mg"], 1)},
               "min_caffeine": {"name": MIN_MG["name"], "mg": round(MIN_MG["mg"], 1)}},
    "ellipsis": {"why": "手冲产地长句宽于栏宽，用 overflow=ELLIPSIS 截断保住网格；"
                         "完整文本同时印在页面脚注，不靠截断隐藏信息。",
                 "lines": [p["origin"] for p in POUR]},
    "render": {"canvas": [W, H], "version": VER, "dsl_chars": len(out),
               "image_nodes": out.count("<Image")},
}, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"{VER} chars {len(out)} TextFit {tf.n} problems {len(tf.problems)} "
      f"Image {out.count('<Image')}")
for p in tf.problems:
    print("  !", p)
print(f"cols bottom {y_left:.0f}/{y_right:.0f} band {BAND:.0f} foot {FOOT:.0f}")
print(f"items {len(ITEMS)} drinks {len(DRINKS)} sum {sum(PRICES)} "
      f"avg {AVG_DRINK:.1f} max_mg {MAX_MG['name']} {MAX_MG['mg']:.0f} "
      f"strength {STRENGTH_N} kcal {KCAL_TOTAL} aller {ALLER_N}")
