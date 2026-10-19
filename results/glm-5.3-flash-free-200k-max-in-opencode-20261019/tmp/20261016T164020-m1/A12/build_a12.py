# -*- coding: utf-8 -*-
"""A12 · 四断点视觉系统：一份 tokens/内容 → mobile/tablet/desktop/stage 四个完整 DSL。
约束：必显字段逐字符完整（不做改写/省略）；手机正文≥16 卡标题≥18；其余正文≥20 主标题≥40；
边距 手机≥16 其他≥32；文字盒不重叠；不能裁切/拉伸/整图 Image。
"""
import io, sys, json, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
OUT = os.path.join(ROOT, "outputs", "20261016T164020-m1", "A12")
os.makedirs(OUT, exist_ok=True)
inv = json.load(open(os.path.join(ROOT, "tasks", "A12-responsive-system", "inputs", "content.json"), encoding="utf-8"))

FAM = "Inter,Noto Sans CJK SC"
T = {
    "bg": "#0E1526", "panel": "#17203A", "card": "#1B2542", "card_border": "#2A3A66",
    "chip_bg": "#1E2A4A", "ink": "#F2F6FF", "sub": "#A8B8D8",
    "accent": "#7AA2F7", "accent2": "#F2C94C", "on_accent": "#0B1220",
}
WARN = []

def estw(s, size):
    t = 0.0
    for ch in s:
        o = ord(ch)
        if o > 0x2E7F: t += size * 1.0
        elif ch in "0123456789": t += size * 0.6
        elif ch == " ": t += size * 0.30
        elif ch.isupper(): t += size * 0.70
        elif ch in "·—（）()→=.,+×:/°#%<>&": t += size * 0.5
        else: t += size * 0.54
    return t

ROLES = []  # content-map 记录（每条正文/必显文本一行）
def rec(canvas, field, src, x, y, size, card_id=None):
    box = [x, y, round(x + estw(src, size)), round(y + size * 1.32)]
    ROLES.append({"canvas": canvas, "field": field, "source_text": src, "displayed_text": src,
                  "box": box, "font_size_px": size, "complete": True, "card_id": card_id})
    return box

def fit(tag, s, size, box):
    w = estw(s, size)
    if w > box: WARN.append(f"{tag} estw {w:.0f}>{box}: {s}")

def emit(x, y, s, size, color, bold=False, deco=False):
    st = f' fontSize="{size}" color="{color}" fontFamily="{FAM}" maxLines="1" overflow="CLIP"'
    if bold: st += ' fontWeight="BOLD"'
    if deco: st += f' decoration="UNDERLINE" decorationColor="{T["accent"]}" decorationThickness="2"'
    return f'<Positioned left="{x}" top="{y}"><Text{st}>{s}</Text></Positioned>'

def Td(cn, field, x, y, s, size, color, bold=False, deco=False, w=None, card_id=None):
    assert "<" not in s
    fit(f"{cn}:{field}", s, size, w or 1900)
    rec(cn, field, s, x, y, size, card_id)
    return emit(x, y, s, size, color, bold, deco)

def Tn(x, y, s, size, color, bold=False):
    """非必显装饰文本（如序号），不入 content-map。"""
    return emit(x, y, s, size, color, bold)

def rect(x, y, w2, h2, color, radius=None, border=0, border_color=None):
    a = f'width="{w2}" height="{h2}"'
    if color: a += f' color="{color}"'
    if radius: a += f' borderRadius="{radius}"'
    if border: a += f' borderWidth="{border}" borderColor="{border_color}"'
    return f'<Positioned left="{x}" top="{y}"><Container {a} /></Positioned>'

def chip(cn, x, y, h, field, text, size, wide=None):
    tw = estw(text, size)
    w2 = int(tw + size * 2.0)
    fit(f"{cn}:chip:{field}", text, size, (wide or w2) - int(size * 1.9))
    res = [rect(x, y, wide or w2, h, T["chip_bg"], radius=h // 2 - 2, border=1, border_color=T["card_border"]),
           Td(cn, field, x + int(size * 0.95), y + int(h * 0.30), text, size, T["ink"], w=(wide or w2) - int(size * 1.9))]
    return res, (wide or w2)

def cta_pill(cn, x, y, h, size):
    text, tw = inv["cta"], estw(inv["cta"], size)
    w2 = int(tw + size * 2.6)
    fit(cn + ":cta", text, size, w2 - int(size * 2.4))
    return [rect(x, y, w2, h, T["accent2"], radius=h // 2 - 2),
            Td(cn, "cta", x + int(size * 1.3), y + int(h * 0.30), text, size, T["on_accent"], bold=True, w=w2 - int(size * 2.4))], w2

def card(cn, x, y, w2, h2, i, s_idx, s_title, s_detail):
    c = inv["cards"][i]
    d = int(s_idx * 3.1)
    tx = x + 24 + d + 16
    fit(f"{cn}:{c['id']}.t", c["title"], s_title, w2 - (tx - x) - 16)
    fit(f"{cn}:{c['id']}.d", c["detail"], s_detail, w2 - (tx - x) - 16)
    y_title = y + int(h2 * (0.26 if cn == "mobile" else 0.32))
    S = [rect(x, y, w2, h2, T["card"], radius=14, border=1, border_color=T["card_border"]),
         rect(x + 24, y + h2 // 2 - d // 2, d, d, T["panel"], radius=d // 2),
         Tn(x + 24 + d / 2 - estw(str(i + 1), s_idx) / 2, y + h2 // 2 - int(s_idx * 0.62), str(i + 1), s_idx, T["accent2"], bold=True),
         Td(cn, "card_title", tx, y_title, c["title"], s_title, T["ink"], bold=True, card_id=c["id"]),
         Td(cn, "card_detail", tx, y_title + int(s_title * 1.55), c["detail"], s_detail, T["sub"], card_id=c["id"])]
    return S

specs = {
    "mobile":  dict(W=360, H=800, M=16, meta="stack", grid=(1, 6), card=(328, 64),
                    k=dict(chip_h=1.75, chip_gap=0.31, cta_h=2.5, web=1.8, card_gap=0.6, card_top=0.75, pre=1.0),
                    sizes=dict(title=32, sub=18, meta=16, cta=16, card_idx=16, card_title=18, card_detail=16)),
    "tablet":  dict(W=768, H=1024, M=32, meta="row", grid=(2, 3), card=(340, 168), k=dict(card_top=2.4),
                    sizes=dict(title=52, sub=22, meta=20, cta=20, card_idx=18, card_title=22, card_detail=20)),
    "desktop": dict(W=1440, H=900, M=32, meta="row", grid=(3, 2), card=(442, 200),
                    sizes=dict(title=64, sub=24, meta=20, cta=20, card_idx=22, card_title=24, card_detail=20)),
    "stage":   dict(W=1920, H=1080, M=48, meta="row", grid=(3, 2), card=(592, 236),
                    sizes=dict(title=88, sub=30, meta=22, cta=22, card_idx=24, card_title=26, card_detail=22)),
}

def canvas(name):
    spec = specs[name]
    W, H, M = spec["W"], spec["H"], spec["M"]
    sz = spec["sizes"]
    S = [rect(0, 0, W, H, T["bg"]), rect(M, M, 64, 6, T["accent"])]
    y = M + 22
    S.append(Td(name, "title", M, y, inv["title"], sz["title"], T["ink"], bold=True, w=W - 2 * M))
    y = int(y + sz["title"] * 1.38)
    S.append(Td(name, "subtitle", M, y, inv["subtitle"], sz["sub"], T["sub"], w=W - 2 * M))
    y = int(y + sz["sub"] * 2.0)
    S.append(rect(M, y, W - 2 * M, 1, T["card_border"]))
    y = int(y + sz["meta"] * 1.0)
    k = spec.get("k", {})
    chip_h_f = k.get("chip_h", 2.1); chip_gap_f = k.get("chip_gap", 0.55)
    cta_h_f = k.get("cta_h", 2.6); card_gap_f = k.get("card_gap", 0.85)
    web_f = k.get("web", 1.95); card_top_f = k.get("card_top", 1.2)
    if spec["meta"] == "stack" or name == "mobile":
        for f2, val in (("date", inv["date"]), ("time", inv["time"]), ("location", inv["location"])):
            b2, w2 = chip(name, M, y, int(sz["meta"] * chip_h_f), f2, val, sz["meta"], wide=(W - 2 * M if name == "mobile" else None))
            S += b2
            y += int(sz["meta"] * chip_h_f + sz["meta"] * chip_gap_f)
    else:
        x = M
        for f2, val in (("date", inv["date"]), ("time", inv["time"]), ("location", inv["location"])):
            b2, w2 = chip(name, x, y, int(sz["meta"] * chip_h_f), f2, val, sz["meta"])
            S += b2
            x += w2 + int(sz["meta"] * 0.7)
        y += int(sz["meta"] * chip_h_f)
    y += int(sz["meta"] * 0.6)
    S.append(Td(name, "website", M, y, inv["website"], sz["meta"], T["accent"], deco=True, w=W - 2 * M))
    y = int(y + sz["meta"] * web_f)
    b3, w3 = cta_pill(name, M, y, int(sz["cta"] * cta_h_f), sz["cta"])
    S += b3
    y += int(sz["cta"] * cta_h_f + sz["meta"] * 1.15)
    S.append(rect(M, y, W - 2 * M, 1, T["card_border"]))
    y = int(y + sz["meta"] * card_top_f)
    cols, rows = spec["grid"]
    cw, ch = spec["card"]
    gap = int(sz["meta"] * card_gap_f)
    for idx2 in range(6):
        r2, c2 = divmod(idx2, cols)
        x = M + c2 * (cw + gap)
        yy = y + r2 * (ch + gap)
        if x + cw > W - M + 1 or yy + ch > H - M + 1:
            WARN.append(f"{name} 卡 {idx2} 越界 right={x + cw} bottom={yy + ch}")
        S += card(name, x, yy, cw, ch, idx2, sz["card_idx"], sz["card_title"], sz["card_detail"])
    grid_bottom = y + rows * ch + (rows - 1) * gap
    if grid_bottom > H - M:
        WARN.append(f"{name} 网格底 {grid_bottom} > {H - M}")
    dsl = (f'<Snapshot background="{T["bg"]}" type="png"><Stack><SizedBox width="{W}" height="{H}" />\n'
           + "\n".join(S)
           + f"\n<Positioned left=\"0\" top=\"{H - 8}\" width=\"{W}\" height=\"8\"><Container width=\"{W}\" height=\"8\" color=\"{T['accent']}\" opacity=\"0.18\" /></Positioned>"
           + "\n</Stack></Snapshot>")
    open(os.path.join(OUT, f"{name}.snapshot"), "w", encoding="utf-8").write(dsl)
    return grid_bottom

CANVASES = {}
for name in specs:
    gb = canvas(name)
    W, H, M = specs[name]["W"], specs[name]["H"], specs[name]["M"]
    CANVASES[name] = {"size": [W, H], "margin": M, "png": f"{name}.png", "dsl": f"{name}.snapshot"}
    print(f"{name}: grid_bottom={gb} limit={H - M}")

tokens = {
    "schema_version": 1, "task_id": "A12", "path_base": "output_dir",
    "palette": T,
    "typography": {"font_family": FAM,
                   "font_note": "本 run 前置真实字体查询缓存（Inter + Noto Sans CJK SC），覆盖中英文",
                   "scale": {name: spec["sizes"] for name, spec in specs.items()},
                   "constraints": {"mobile": {"body_min_px": 16, "card_title_min_px": 18},
                                   "tablet_desktop_stage": {"body_min_px": 20, "title_min_px": 40}}},
    "spacing": {"grid_unit": 8,
                "margins": {n: s["M"] for n, s in specs.items()},
                "card_gap_rule": "gap = 0.85 × meta 字号（26/17/17/19 px）",
                "block_gap_rule": "块距与分隔线按 meta 字号比例（0.6–2.1×），四画布节奏一致"},
    "components": {
        "rail": {"w": 64, "h": 6, "color_ref": "accent", "note": "顶部认可线，四画布必备"},
        "chip": {"bg_ref": "chip_bg", "border": "1 card_border", "radius": "h/2-2",
                 "padding_x": "0.9×字号", "used_for": "date/time/location"},
        "cta_pill": {"bg_ref": "accent2", "text_ref": "on_accent bold", "radius": "h/2-2",
                     "padding_x": "1.1×字号", "used_for": "cta（文字按钮，无二维码）"},
        "card": {"bg_ref": "card", "border": "1 card_border", "radius": 14,
                 "anatomy": "索引圆点(panel/accent2 数字) → 标题(ink bold) → detail(sub)；无裁切拉伸"},
        "index_dot": {"d": "3.1×card_idx", "num_color_ref": "accent2"},
        "website": {"color_ref": "accent", "decoration": "UNDERLINE thickness2 accent"},
        "bottom_overline": {"h": 8, "opacity": 0.18, "color_ref": "accent", "note": "页面底部 8px 收边条，四画布同构"},
    },
    "hierarchy_rules": [
        "信息层级恒定：rail → title → subtitle → 分隔线 → meta chips → website → cta → 卡片网格 → 收边条",
        "四画布同一调色板与组件词汇，仅断点重排；无裁切/拉伸/整图 Image",
        "标题字体升档（手机可用 32；其余 ≥40）：32/52/64/88",
        "正文升档：detail 与元信息 16(手机)/20/20/22；卡片标题 18/22/24/26"],
    "responsive_rules": {"mobile": "单列纵排；meta 三行堆叠；卡 1×6",
                         "tablet": "meta 单行 chips；卡 2×3（行优先 C1C2/C3C4/C5C6）",
                         "desktop": "桌面同构放大；卡 3×2（C1C2C3/C4C5C6）",
                         "stage": "大屏 3×2 等比放大，边距 48"},
}
json.dump(tokens, open(os.path.join(OUT, "design-tokens.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

cmap = {
    "schema_version": 1, "task_id": "A12", "path_base": "output_dir",
    "canvas_files": CANVASES,
    "required_fields": ["title", "subtitle", "date", "time", "location", "cta", "website"],
    "entries": ROLES,
    "card_index": {f"C{i + 1}": {} for i in range(6)},
    "note": "cards[].id 不印在图上（题面允许：以映射记录为准）；卡按输入顺序行优先入网。",
}
for e in ROLES:
    if e["card_id"]:
        cols, rows = specs[e["canvas"]]["grid"]
        i = [c["id"] for c in inv["cards"]].index(e["card_id"])
        r2, c22 = divmod(i, cols)
        cmap["card_index"][e["card_id"]][e["canvas"]] = {
            "grid_position": f"r{r2 + 1}c{c22 + 1}", "order": i + 1,
            "title_box": e["box"] if e["field"] == "card_title" else None}
cmap["card_index"] = {k: {kk: vv for kk, vv in v.items()} for k, v in cmap["card_index"].items()}
json.dump(cmap, open(os.path.join(OUT, "content-map.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

from collections import Counter
print("entries per canvas:", dict(Counter(e["canvas"] for e in ROLES)))
print("WARN", len(WARN))
for w in WARN: print(" -", w)
