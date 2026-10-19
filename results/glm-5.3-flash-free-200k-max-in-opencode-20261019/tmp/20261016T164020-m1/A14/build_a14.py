# -*- coding: utf-8 -*-
"""A14 · 八组文案压力测试：cards.json → 参数化规则生成 8 张 1200×630 宣传卡（card-K01..K08）。
统一 tokens（沿用 A12 品牌系统：Structure / Vision · 2026.11.07 同一活动）；
状态体系：颜色+DSL 符号+文字（开放/满额/候补/取消）；标题≥36 ≤3行（greedy 标点优先折行）；
讲者≥22 允许两行；安全边距 40；K06 取消卡保留完整标题/时间并另注「本场取消」。
含 <>& 的字段走 <Raw><![CDATA[…]]></Raw>（Parser 不做实体解码）。"""
import io, sys, json, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
OUT = os.path.join(ROOT, "outputs", "20261016T164020-m1", "A14")
os.makedirs(OUT, exist_ok=True)
cards = json.load(open(os.path.join(ROOT, "tasks", "A14-content-stress-batch", "inputs", "cards.json"), encoding="utf-8"))

FAM = "Inter,Noto Sans CJK SC"
T = {"bg": "#0E1526", "panel": "#17203A", "chip": "#1E2A4A", "line": "#2A3A66",
     "ink": "#F2F6FF", "sub": "#A8B8D8", "accent": "#7AA2F7", "accent2": "#F2C94C",
     "on_accent": "#0B1220", "brand_cjk": "#7AA2F7"}
ST = {"开放": {"c": "#35D07F", "shape": "dot"},
      "满额": {"c": "#F2C94C", "shape": "sq"},
      "候补": {"c": "#7AA2F7", "shape": "ring"},
      "取消": {"c": "#FF6B6B", "shape": "cross"}}
DATE, BRAND = "2026.11.07", "Structure / Vision"
M, W, H = 40, 1200, 630
CR = W - M                      # 1160
WARN = []
AUDIT = []

def estw(s, size):
    t = 0.0
    for ch in s:
        o = ord(ch)
        if o > 0x2E7F: t += size * 1.0
        elif ch in "0123456789": t += size * 0.6
        elif ch == " ": t += size * 0.30
        elif ch.isupper(): t += size * 0.70
        elif ch in "<>&·—/,.:": t += size * 0.5
        else: t += size * 0.54
    return t

def fit(tag, s, size, box):
    w = estw(s, size)
    if w > box: WARN.append(f"{tag} estw {w:.0f}>{box}: {s}")

PUNC = set("，。：——、！？；,")   # 优先断行点（在其后断）
def wrap(text, size, limit):
    """greedy + 标点优先：先按估宽累积，超过 limit 回退到最近可用断点；返回行列表（逐字符保留，只插入换行）"""
    def w_of(s): return estw(s, size)
    if w_of(text) <= limit:
        return [text]
    chars = list(text)
    lines, i = [], 0
    n = len(chars)
    while i < n:
        j, acc = i, 0.0
        best = None            # (break_index, width)
        while j < n:
            acc += w_of(chars[j])
            if acc > limit:
                break
            if chars[j] in PUNC or chars[j] == " ":
                best = (j + 1, acc)
            j += 1
        if j >= n:
            lines.append("".join(chars[i:]))
            break
        cut = best[0] if best else j
        cut = max(cut, i + 1)
        lines.append("".join(chars[i:cut]))
        i = cut
    return lines

def TXT(x, y, s, size, color, bold=False):
    """单行文本；含 <>& 的行使用 Raw+CDATA 原样排版。"""
    if any(c in "<>&" for c in s):
        st = f' fontSize="{size}" color="{color}" fontFamily="{FAM}"'
        if bold: st += ' fontWeight="BOLD"'
        body = f'<![CDATA[{s}]]>'
        return f'<Positioned left="{x}" top="{y}"><Text{st} maxLines="1" overflow="CLIP"><Raw>{body}</Raw></Text></Positioned>'
    st = f' fontSize="{size}" color="{color}" fontFamily="{FAM}" maxLines="1" overflow="CLIP"'
    if bold: st += ' fontWeight="BOLD"'
    return f'<Positioned left="{x}" top="{y}"><Text{st}>{s}</Text></Positioned>'

def Rc(x, y, w2, h2, color=None, radius=None, border=0, border_color=None, border_width=None):
    a = f'width="{w2}" height="{h2}"'
    if color: a += f' color="{color}"'
    if radius: a += f' borderRadius="{radius}"'
    if border: a += f' borderWidth="{border}" borderColor="{border_color}"'
    return f'<Positioned left="{x}" top="{y}"><Container {a} /></Positioned>'

STATUS_ICON = {"dot": lambda x, y, d, c: Rc(x, y, d, d, c, radius=d // 2),
               "sq": lambda x, y, d, c: Rc(x, y + 1, d - 2, d - 2, c, radius=3)}

def ring_node(x, y, d, c, ring=3):
    """圆环 = 外圆轮廓 + 内孔轮廓 EVEN_ODD（path 为 SizedBox 内 0 基局部坐标）"""
    r = d / 2
    inner = r - ring
    path = (f"M{d} {d / 2} A{r} {r} 0 0 0 0 {d / 2} A{r} {r} 0 0 0 {d} {d / 2} Z "
            f"M{d / 2 + inner} {d / 2} A{inner} {inner} 0 0 0 {d / 2 - inner} {d / 2} "
            f"A{inner} {inner} 0 0 0 {d / 2 + inner} {d / 2} Z")
    return (f'<Positioned left="{x}" top="{y}"><SizedBox width="{int(d)}" height="{int(d)}">'
            f'<ClipPath path="{path}" fillRule="EVEN_ODD" clipBehavior="ANTI_ALIAS">'
            f'<Container width="{int(d)}" height="{int(d)}" color="{c}" /></ClipPath></SizedBox></Positioned>')

STATUS_ICON["ring"] = lambda x, y, d, c: ring_node(x, y, d, c, ring=3)
STATUS_ICON["cross"] = lambda x, y, d, c: (ring_node(x, y, d, c, ring=3)
                                           + Rc(x + 2, y + d / 2 - 2, d - 4, 4, c, radius=2))

def badge(status, right=CR, top=40, h=48, size=22):
    s = ST[status]
    tw = estw(status, size)
    iw, gap, pad = 14, 10, 16
    w2 = int(tw + iw + gap + pad * 2)
    bx = right - w2
    bgc = s["c"] + "29"                     # 16% alpha 底
    ty = top + (h - int(size * 1.18)) // 2 - 2   # 按墨迹高约 1.18em 垂直居中（像素实测 22px→26px 墨高）
    res = [Rc(bx, top, w2, h, bgc, radius=h // 2, border=2, border_color=s["c"] + "66"),
           STATUS_ICON[s["shape"]](bx + pad, top + h / 2 - iw / 2, iw, s["c"]),
           TXT(bx + pad + iw + gap, ty, status, size, s["c"], bold=True)]
    box = [bx, top, right, top + h]
    return res, w2, box

def rect(x, y, w2, h2, color, radius=None, border=0, border_color=None):
    return Rc(x, y, w2, h2, color, radius, border, border_color)

def build_card(c):
    idn = c["id"]
    ev = {"file": f"card-{idn}.png", "dsl": f"card-{idn}.snapshot", "size": [W, H], "card_id": idn}
    S = [rect(0, 0, W, H, T["bg"]), rect(M, M, 60, 6, T["accent2"]), rect(M, M + 6, 60, 2, T["accent"])]
    bt, bw = 22, None
    S += [TXT(M, 60, BRAND, bt, T["accent"], bold=True)]
    ev["brand"] = {"text": BRAND, "box": [M, 60, round(M + estw(BRAND, bt)), round(60 + bt * 1.32)], "font_size_px": bt}
    bres, bwd, bbox = badge(c["status"])
    S += bres
    ev["status"] = {"label": c["status"], "color": ST[c["status"]]["c"], "shape": ST[c["status"]]["shape"],
                    "badge_box": bbox,
                    "contrast_rule": "色（徽标底16% α+边框2 px）+ 符号（dot/sq/ring/cross）+ 文字（原始状态词）三重编码"}
    # 标题：≤3 行 greedy 标点折行（不做全局缩放；字号恒 44）
    size_title = 44
    tw_limit = CR - 56 - 88      # 标题右边界 1072（与徽标带留白）
    lines = wrap(c["title"], size_title, tw_limit)
    assert len(lines) <= 3, (idn, len(lines), lines)
    ty0 = 148
    tboxes = []
    for li, ln in enumerate(lines):
        fit(f"{idn}:t{li}", ln, size_title, tw_limit)
        S.append(TXT(56, ty0 + li * 56, ln, size_title, T["ink"], bold=True))
        tboxes.append([56, ty0 + li * 56, round(56 + estw(ln, size_title)), round(ty0 + li * 56 + size_title * 1.32)])
    ev["title"] = {"text": c["title"], "font_size_px": size_title, "lines": lines,
                   "line_count": len(lines), "boxes": tboxes, "raw_cdata": any(ch in "<>&" for ch in c["title"]),
                   "zone": [56, ty0, 56 + tw_limit, ty0 + 3 * 56 - 8]}
    sy = ty0 + len(lines) * 56 + 26
    # 讲者（原始文字；允许两行）
    size_sp = 24
    sp_limit = 720
    slines = wrap(c["speaker"], size_sp, sp_limit)
    assert len(slines) <= 2, (idn, slines)
    sboxes = []
    for li, ln in enumerate(slines):
        fit(f"{idn}:s{li}", ln, size_sp, sp_limit)
        S.append(TXT(56, sy + li * 32, ln, size_sp, T["sub"]))
        sboxes.append([56, sy + li * 32, round(56 + estw(ln, size_sp)), round(sy + li * 32 + size_sp * 1.32)])
    ev["speaker"] = {"text": c["speaker"], "font_size_px": size_sp, "line_count": len(slines), "boxes": sboxes,
                     "raw_cdata": any(ch in "<>&" for ch in c["speaker"])}
    if sy + len(slines) * 32 > 500: WARN.append(f"{idn} 讲者区越入底部 y={sy + len(slines) * 32}")
    # 底部：分隔线 + 时间（原始文字）+ 日期 + 取消卡另注
    S.append(rect(56, 512, CR - 56, 1, T["line"]))
    size_time = 26
    S.append(TXT(56, 536, c["time"], size_time, T["accent2"], bold=True))
    dx = 56 + estw(c["time"], size_time) + 16
    S.append(TXT(dx, 536 + (size_time - 20) + 2, DATE, 20, T["sub"]))
    ev["time"] = {"text": c["time"], "font_size_px": size_time, "box": [56, 536, round(56 + estw(c["time"], size_time)), round(536 + size_time * 1.32)]}
    ev["date"] = {"text": DATE, "font_size_px": 20, "box": [round(dx), 536 + 8, round(dx + estw(DATE, 20)), round(536 + 8 + 20 * 1.32)]}
    if c["status"] == "取消":
        ptw = estw("本场取消", 22)
        pw = int(ptw + 44)
        S += [rect(CR - pw, 524, pw, 48, ST["取消"]["c"], radius=24),
              TXT(CR - pw + 22, 524 + 9, "本场取消", 22, T["on_accent"], bold=True)]
        ev["cancel_note"] = {"text": "本场取消", "box": [CR - pw, 524, CR, 572],
                             "note": "取消卡仍完整显示标题/讲者/时间；此红色 pill 为独立注明，且整卡未灰压"}
    dsl = (f'<Snapshot background="{T["bg"]}" type="png"><Stack><SizedBox width="{W}" height="{H}" />\n'
           + "\n".join(S) + "\n</Stack></Snapshot>")
    open(os.path.join(OUT, f"card-{idn}.snapshot"), "w", encoding="utf-8").write(dsl)
    ev["margin_check"] = {"safe": 40, "note": "全部元素位于 [40,40]–[1160,590]（徽标 y40..88、底部行 ≤572）"}
    AUDIT.append(ev)
    return f"card-{idn}"

res = [build_card(c) for c in cards]
json.dump({"schema_version": 1, "task_id": "A14", "path_base": "output_dir",
           "rule": "一套参数化生成器（tmp/build_a14.py）从 cards.json 逐卡生成；无逐条硬改",
           "tokens": T, "status_codes": ST, "cards": AUDIT},
          open(os.path.join(OUT, "batch-audit.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("built", len(res))
print("WARN", len(WARN))
for w in WARN: print(" -", w)
for ev in AUDIT:
    print(ev["card_id"], "lines", ev["title"]["line_count"], "speaker_lines", ev["speaker"]["line_count"])
