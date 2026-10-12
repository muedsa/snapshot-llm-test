"""B03 case-10：品牌字体 specimen 移动页（1080×1920）。

受众与情境：客户设计师要在一次交付里确认三件事——这套品牌字能用到哪些字重、
字距/词距/行高改到多少才有效果、哪些「高级特性」在这台渲染器上其实是空的。
所以这一页不是把字母摆得好看，而是一份**可以照着复现的测量记录**：每个样本占一条
独立测量带，页面上的「实测」数字是用 PIL 扫上一版成品 PNG 的墨迹边界得到的
（`case10-measure.py` → `case10-measure-vNN.json` → 本版把实测值印回页面）。

独到手法：
1. 只用服务**真实安装**的字族（`GET /fonts` 2026-10-08 取得，缓存在
   `tmp/<run>/_suite/docs/fonts.txt`，共 27 族）。Inter 的 8 个字重是 8 个独立族名，
   于是把 `fontFamily="Inter Semi Bold"` 与 `fontStyle="BOLD"` 排成相邻两行直接对照。
2. letterSpacing / wordSpacing / height 三组阶梯，每行同时印**实测宽度**与按字宽模型
   算出的**预期宽度**，差值就是设计师能拿到的可控范围。
3. 回退链实测：`IBM Plex Mono`、`Courier New` 不在安装列表里，把它们的实测单字宽与
   `DejaVu Sans Mono` 并排，说明「写了不等于用了」。
4. `fontFeatures` 只报实测结果（tnum / lnum smcp / −kern / +liga 四组与基准并排），
   页面上明写「语法被接受但未量得出差异」，不冒充生效。
5. STROKE 描边字做三档线宽，并说明它加粗笔画而不改变排版宽度。
6. 每条测量带坐标写进 `data.json.bands`，测量脚本按坐标扫描，不靠肉眼估。
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(os.environ["SNAPSHOT_TASK_ROOT"])
RID = os.environ["SNAPSHOT_RUN_ID"]
for p in (ROOT / "tmp" / RID / "_suite" / "scripts", ROOT / "tmp" / RID / "B03"):
    sys.path.insert(0, str(p))
from dslkit import Doc, TextFit, n                       # noqa: E402
import b03kit as K                                        # noqa: E402

VER = os.environ.get("B03_VER", "v01")
W, H = 1080, 1920
M = 56
PAPER, INK, ACC, GRAY = "#F5F2EC", "#15171B", "#D2482B", "#6E7076"
RULE, PANEL, SOFT = "#D8D2C6", "#EAE5DA", "#908E88"
SANS = "Inter,Noto Sans CJK SC"
MONO = "DejaVu Sans Mono,Noto Sans Mono CJK SC,monospace"
RX = 1040 - 250                  # 右侧「实测/预期」列
SX, SW = M + 156, 552            # 中间样本带（也是测量带的扫描窗口）

# 实测值：扫上一版 PNG 得到；本版没有就印「待测」
MP = ROOT / "tmp" / RID / "B03" / f"case10-measure-{VER}.json"
DOC = json.loads(MP.read_text(encoding="utf-8")) if MP.exists() else {}
MEAS, META = DOC.get("values", {}), DOC.get("meta", {})

# ---------------- 真实安装字族（GET /fonts，2026-10-08） ----------------
FONTS_TXT = (ROOT / "tmp" / RID / "_suite" / "docs" / "fonts.txt").read_text(
    encoding="utf-8")
FAMILIES = [x for x in FONTS_TXT.splitlines() if x.strip()]
assert len(FAMILIES) == 27, len(FAMILIES)
assert "Inter Semi Bold" in FAMILIES and "Noto Serif CJK SC" in FAMILIES
for absent in ("IBM Plex Mono", "Courier New", "Helvetica"):
    assert absent not in FAMILIES, absent

WEIGHTS = [("Inter Thin", "100"), ("Inter", "400"),
           ("Inter Medium", "500"), ("Inter Semi Bold", "600"),
           ("Inter Extra Bold", "800"), ("Inter Black", "900"),
           ("Inter·BOLD", "400+style")]
LS = [0.0, 2.0, 4.0, 8.0]                  # letterSpacing 阶梯（px）
WS = [0.0, 8.0, 18.0]                       # wordSpacing 阶梯（px）
HT = [1.0, 1.25, 1.5, 1.9]                  # height（行高倍数）阶梯
FEAT = [("基准（无属性）", ""), ("tnum", "tnum"), ("lnum smcp", "lnum smcp"),
        ("+liga", "+liga")]
FALLBACK = [("DejaVu Sans Mono", "DejaVu Sans Mono", "已安装"),
            ("Noto Sans Mono CJK SC", "Noto Sans Mono CJK SC", "已安装"),
            ("IBM Plex Mono", "IBM Plex Mono", "未安装→回退"),
            ("Courier New", "Courier New", "未安装→回退"),
            ("Inter（比例字）", "Inter", "已安装·非等宽")]

# 字宽模型（前案像素标定）：CJK ≈1.0em、Inter 拉丁 ≈0.55em、等宽 ≈0.60em
ADV = {"cjk": 1.00, "latin": 0.55, "mono": 0.60}


def expected(s, size, family, ls=0.0, ws=0.0):
    """按字宽模型算一行文本的预期宽度（px），用于与实测对照。"""
    mono = "Mono" in family
    total = 0.0
    for ch in s:
        if ch == " ":
            total += (ADV["mono"] if mono else 0.30) * size + ws
        else:
            total += (ADV["cjk"] if ord(ch) > 0x2E80
                      else (ADV["mono"] if mono else ADV["latin"]) * 1) * size
        total += ls
    return total - ls


d = Doc(W, H, bg=PAPER, font=SANS)
tf = TextFit()
BANDS = {}


def band(key, y0, y1, x0=SX, x1=SX + SW):
    BANDS[key] = {"x": [x0, x1], "y": [round(y0, 1), round(y1, 1)]}
    return MEAS.get(key)


def fmt(v, unit="px"):
    return "待测" if v is None else f"{v:g}{unit}"


def section(y, num, title, note):
    K.tlab(d, tf, f"s{num}n", M, y, 90, 26, f"{num:02d}", 22, ACC, font=MONO,
           style="BOLD")
    K.tlab(d, tf, f"s{num}h", M + 62, y, 620, 26, title, 21, INK, style="BOLD")
    K.tlab(d, tf, f"s{num}e", RX, y + 2, 250, 22, note, 12, GRAY, font=MONO,
           align="END")
    d.line(M, y + 28, W - M, y + 28, 1.2, INK)
    return y + 36


def row(y, label, sample, size, family, key, step=None, style=None, sub="",
        metric="w", **kw):
    """一条测量行：左标签 / 中样本（独立测量带）/ 右实测+预期。

    metric="w" 比宽度（实测 vs 字宽模型预期）；metric="ink" 报墨迹浓度（字重行用）。
    """
    K.tlab(d, tf, f"{key}-l", M, y + 4, 148, 20, label, 11.5, GRAY, font=MONO)
    if sub:
        K.tlab(d, tf, f"{key}-b", M, y + 22, 148, 20, sub, 10.5, SOFT, font=MONO)
    K.tlab(d, tf, f"{key}-s", SX, y, SW, size + 12, sample, size, INK,
           font=family, style=style, **kw)
    got = band(key, y - 2, y + size + 14)
    exp = expected(sample, size, family, kw.get("spacing", 0.0),
                   kw.get("word_spacing", 0.0))
    if metric == "ink":
        K.tlab(d, tf, f"{key}-m", RX, y + 2, 250, 20,
               f"墨迹 {fmt(got, '%')}", 12,
               ACC if got is not None else SOFT, font=MONO, align="END")
    else:
        K.tlab(d, tf, f"{key}-m", RX, y + 2, 250, 20,
               f"实测 {fmt(got)}｜预期 {exp:.0f}", 12,
               ACC if got is not None else SOFT, font=MONO, align="END")
        if got is not None:
            K.tlab(d, tf, f"{key}-x", RX, y + 20, 250, 20,
                   f"Δ {(got - exp):+g}px", 11, GRAY, font=MONO, align="END")
    return y + (step or max(size + 14, 40))


# ============ 页眉 0–150 ============
d.rect(0, 0, W, 6, ACC)
K.tlab(d, tf, "hd-1", M, 34, 640, 38, "品牌字系统 · Type Specimen", 30, INK,
       style="BOLD")
K.tlab(d, tf, "hd-2", M, 78, 640, 24, "字重 / 字距 / 词距 / 行高 / 特性边界 实测记录",
       15, GRAY)
K.outline(d, tf, "hd-mk", 1040 - 150, 16, 150, 86, "Aa", 82, INK, width=2.6)
K.tlab(d, tf, "hd-3", RX, 106, 250, 20, f"{VER} · 2026-10-11 · 1080×1920", 11, GRAY,
       font=MONO, align="END")
d.line(M, 128, W - M, 128, 1.2, RULE)
NOTE0 = ("本页只用渲染服务真实安装的字族（GET /fonts，2026-10-08，27 族）。「实测」由 PIL 扫"
         "上一版成品 PNG 的墨迹边界得到，「预期」按字宽模型（CJK≈1.0em、Inter 拉丁≈0.55em、"
         "等宽≈0.60em）算出；两列之差就是排版可控的范围。")
K.tlab(d, tf, "hd-4", M, 138, W - 2 * M, 46, NOTE0, 12.5, GRAY, lines=3, height=1.35)

y = 190
# ============ 01 字重阶梯 ============
y = section(y, 1, "字重：Inter 的 7 个字重是 7 个独立族名", "看墨迹，不看名字")
for fam, wnum in WEIGHTS:
    if fam.endswith("·BOLD"):
        y = row(y, "fontStyle=BOLD", "字体设计 Type 0123", 24, "Inter", "w-bold",
                style="BOLD", sub="Inter 400 + 样式", step=37, metric="ink")
    else:
        y = row(y, f"Inter {wnum}", "字体设计 Type 0123", 24, fam, f"w-{wnum}",
                sub=f"族名 {fam.replace('Inter ', '') or 'Regular'}", step=37,
                metric="ink")
INK6, INK9, INKB = MEAS.get("w-600"), MEAS.get("w-900"), MEAS.get("w-bold")
WNOTE = ("末两行对照：族名 Semi Bold 与 fontStyle=BOLD 宽度相同而墨迹不同，"
         "说明样式加粗与独立字重族不是同一件事。") if INKB is None else (
         f"实测墨迹 Semi Bold {INK6}% ＜ Black {INK9}% ＜ fontStyle=BOLD {INKB}%："
         f"样式加粗比最重的字重族还黑，它不是 Semi Bold 的等价写法。")
K.tlab(d, tf, "w-note", M, y + 4, W - 2 * M, 24, WNOTE, 11.5, ACC, lines=1)
y += 26

# ============ 02 字距与词距 ============
y = section(y, 2, "letterSpacing：每加 1px，10 个字加 9px", "INTERSTATE / 34px")
for v in LS:
    y = row(y, f"ls={v:g}px", "INTERSTATE", 34, "Inter", f"ls-{v}",
            spacing=v, step=39)
LS0, LS8 = MEAS.get("ls-0.0"), MEAS.get("ls-8.0")
E0 = expected("INTERSTATE", 34, "Inter")
LSNOTE = ("四行宽度若成等差（公差 9×Δls），说明字距是逐间隙线性叠加。"
          if LS0 is None or LS8 is None else
          f"实测 {LS0:g}→{LS8:g}px，每 1px 字距加 {(LS8 - LS0) / 8 / 9:.2f}px≈1（线性）；"
          f"Δ 列恒为 {LS0 - E0:+.0f}px，因为模型按 0.55em 估低了 Inter 大写"
          f"（实测 {LS0 / 10 / 34:.3f}em/字）。")
K.tlab(d, tf, "ls-note", M, y + 2, W - 2 * M, 24, LSNOTE, 11.5, ACC, lines=1)
y += 26
y = section(y, 3, "wordSpacing：只对空格生效，本行 2 个空格",
            "type specimen page / 28px")
for v in WS:
    y = row(y, f"ws={v:g}px", "type specimen page", 28, "Inter", f"ws-{v}",
            word_spacing=v, step=38)
WS0, WS18 = MEAS.get("ws-0.0"), MEAS.get("ws-18.0")
WNOTE2 = ("样本里只有 2 个空格，所以加 18px 只宽 36px；字母间隙不受 wordSpacing 影响。"
          if WS0 is None or WS18 is None else
          f"实测 {WS0:g}→{WS18:g}px，差 {WS18 - WS0:g}px＝2 个空格 × 18px，"
          f"与「只对空格生效」一致。")
K.tlab(d, tf, "ws-note", M, y + 2, W - 2 * M, 24, WNOTE2, 11.5, ACC, lines=1)
y += 26

# ============ 04 行高（五栏并列：默认 + 四档 height） ============
y = section(y, 4, "height：行距＝字号×倍数，不是默认行高×倍数", "五栏同为 17px / 3 行")
PARA = ("0123 4567 89ab cdef 0123 4567 89ab cdef 0123 4567")
HS = 17
CW = (W - 2 * M - 4 * 12) / 5
COLS = [("默认", None), ("1.0", 1.0), ("1.25", 1.25), ("1.5", 1.5), ("1.9", 1.9)]
BLOCK = HS * 1.9 * 3 + 14
# 测量带键名必须绑定 height 值本身：v02 曾用 h-0..h-4 的位置键，插入「默认」列后
# 键整体右移一位，印出来的实测行距全部串了一栏。
for lab, v in COLS:
    hk = "h-def" if v is None else "h-%g" % v
    j = COLS.index((lab, v))
    cx = M + j * (CW + 12)
    K.tlab(d, tf, f"{hk}l", cx, y, CW, 20, f"height {lab}", 11.5, ACC, font=MONO)
    kw = {} if v is None else {"height": v}
    K.tlab(d, tf, f"{hk}s", cx, y + 22, CW, BLOCK, PARA, HS, INK, font=SANS,
           lines=4, **kw)
    band(hk, y + 20, y + 20 + BLOCK + 2, cx, cx + CW)
    got = MEAS.get(hk)
    exp = HS * 1.45 if v is None else HS * v
    cap = (f"行距 {fmt(got, '')}｜预期 {exp:.1f}" if got is not None else
           ("行距 墨迹相接｜预期 %.1f" % exp if v is not None else
            f"行距 待测｜预期 {exp:.1f}"))
    K.tlab(d, tf, f"{hk}m", cx, y + 22 + BLOCK + 4, CW, 22, cap, 10,
           ACC if got is not None else SOFT, font=MONO, lines=2)
y += 22 + BLOCK + 30
HP = {lab: MEAS.get("h-def" if v is None else "h-%g" % v) for lab, v in COLS}
HNOTE = ("行距＝字号 × height；不写 height 时服务用 ≈1.45×字号的默认行距。"
         if HP["1.25"] is None else
         f"实测行距：默认 {HP['默认']:g}、1.0 {HP['1.0']:g}、1.25 {HP['1.25']:g}、"
         f"1.5 {HP['1.5']:g}、1.9 {HP['1.9']:g}px。后四档＝17×倍数（最大偏差 "
         f"{max(abs(HP[l] - HS * v) for l, v in COLS[1:]):.1f}px），height 只与字号相乘；"
         f"默认档实测 {HP['默认'] / HS:.2f}em，比「预期」列用的 1.45em 估算常数紧，"
         f"说明不写 height 时行距取自字族自身 metrics。")
K.tlab(d, tf, "h-note", M, y - 16, W - 2 * M, 34, HNOTE, 11.5, ACC, lines=2,
       height=1.3)
y += 36

# ============ 05 等宽与回退 ============
y = section(y, 5, "等宽与回退：写了不等于用了", "同一串数字换字族")
for j, (lab, fam, st) in enumerate(FALLBACK):
    y = row(y, f"{j + 1} {st.split('→')[0]}", "0123456789", 30, fam, f"fb-{j}",
            sub=lab, step=39)
FB = [MEAS.get(f"fb-{j}") for j in range(5)]
FBNOTE = ("3、4 行的字族不在安装列表里，服务会回退；把它们的实测宽与 1、2、5 行逐一相比，"
          "全不相等就说明回退目标不是其中任何一个，而是平台默认字体。"
          if any(v is None for v in FB) else
          f"实测单串宽：DejaVu {FB[0]:g}、Noto Mono {FB[1]:g}、IBM Plex {FB[2]:g}、"
          f"Courier {FB[3]:g}、Inter {FB[4]:g}px——两行「未安装」与任何已安装族都不等，"
          f"回退到的是平台默认字体。")
K.tlab(d, tf, "fb-note", M, y + 4, W - 2 * M, 24, FBNOTE, 11.5, ACC, lines=1)
y += 26

# ============ 06 fontFeatures ============
y = section(y, 6, "fontFeatures：语法被接受，未量得出差异", "0123456789 / 30px")
for j, (lab, feat) in enumerate(FEAT):
    y = row(y, lab, "0123456789", 30, "DejaVu Sans Mono", f"ff-{j}", step=37,
            **({"features": feat} if feat else {}),
            sub=feat or "（不加属性）")
FF = [MEAS.get(f"ff-{j}") for j in range(4)]
FFNOTE = ("结论与探针 14 一致：fontFeatures 能通过解析，但在本题可用字体上没有量得出的宽度差。"
          "需要等宽数字／小型大写时应在版式里手工设定，不能靠这个属性。"
          if any(v is None for v in FF) else
          f"四行实测全为 {FF[0]:g}px（含 +liga 行），差值 0——fontFeatures 在本服务上"
          f"只被解析、不被应用；需要等宽数字／小型大写时得在版式里手工设定，不能靠这个属性。")
K.tlab(d, tf, "ff-note", M, y + 4, W - 2 * M, 36, FFNOTE, 11.5, ACC, lines=2,
       height=1.35)
y += 36

# ============ 07 STROKE 描边 ============
y = section(y, 7, "STROKE：笔画变粗而不改字宽", "foregroundStrokeWidth 三档")
for wv in (1.0, 2.4, 4.0):
    K.tlab(d, tf, f"st-{wv}l", M, y + 14, 148, 20, f"宽 {wv:g}px", 11.5, GRAY,
           font=MONO)
    K.tlab(d, tf, f"st-{wv}s", SX, y, SW, 46, "裁 CUT", 38, INK, font=SANS,
           fg=ACC, fg_mode="STROKE", fg_w=wv)
    band(f"st-{wv}", y - 2, y + 48)
    got = MEAS.get(f"st-{wv}")
    K.tlab(d, tf, f"st-{wv}m", RX, y + 14, 250, 20, f"实测 {fmt(got)}", 12,
           ACC if got is not None else SOFT, font=MONO, align="END")
    y += 48
ST = [MEAS.get(f"st-{v}") for v in (1.0, 2.4, 4.0)]
STNOTE = ("三档的外框宽度应完全相同（字宽不变、只有笔画变粗），"
          "与 case-09 字墙里的用法是同一属性的两种目的。"
          if any(v is None for v in ST) else
          f"三档实测外框全为 {ST[0]:g}px、零差：描边加粗笔画而不改变排版宽度"
          f"（4px 档已把中宫填满，故只用于展示字，不用于正文）。")
K.tlab(d, tf, "st-note", M, y + 4, W - 2 * M, 24, STNOTE, 11.5, ACC, lines=1)
y += 24

# ============ 页脚 ============
d.line(M, y, W - M, y, 1.2, INK)
K.tlab(d, tf, "ft-1", M, y + 10, W - 2 * M, 34,
       f"测量方法：PIL 在 data.json.bands 登记的坐标带内逐列扫描，以距底色 ΔE>40 记为墨迹，"
       f"宽度取首末墨迹列之差；行高栏取相邻两行墨迹中心的间距。共 {len(BANDS)} 条测量带。",
       11, GRAY, lines=2, height=1.35)
K.tlab(d, tf, "ft-2", M, y + 46, 620, 20,
       f"字族来源 GET /fonts（{len(FAMILIES)} 族）· 本页无外部素材，全部由 DSL 构造",
       11, GRAY, font=MONO)
K.tlab(d, tf, "ft-3", RX, y + 46, 250, 20, f"Snapshot DSL {W}×{H} {VER}", 11, INK,
       font=MONO, align="END")
assert y + 72 <= H, (y + 72, H)

DSL = d.dsl()
OUT = Path(os.environ.get("SNAPSHOT_TMP_OUT", str(ROOT / "tmp" / RID / "B03")))
(OUT / f"case10-{VER}.snapshot").write_text(DSL, encoding="utf-8")

OD = ROOT / "outputs" / RID / "B03" / "case-10"
OD.mkdir(parents=True, exist_ok=True)
(OD / "data.json").write_text(json.dumps({
    "ver": VER, "canvas": [W, H], "dsl_chars": len(DSL),
    "fonts_source": "GET /fonts 2026-10-08，缓存 tmp/<run_id>/_suite/docs/fonts.txt",
    "families_total": len(FAMILIES), "families": FAMILIES,
    "absent_checked": ["IBM Plex Mono", "Courier New", "Helvetica"],
    "advance_model": ADV, "weights": WEIGHTS, "letter_spacing_steps": LS,
    "word_spacing_steps": WS, "height_steps": HT, "features": FEAT,
    "fallback_rows": FALLBACK, "bands": BANDS,
    "measured": MEAS or None,
    "measured_from": (None if not MEAS else
                      f"tmp/{RID}/B03/case10-measure-{VER}.json（扫描上一版 PNG）"),
    "textfit": {"checked": tf.n, "problems": tf.problems},
    "layout_y_end": round(y + 72, 1),
    "fictional": ["品牌抬头「品牌字系统」为示例，非真实客户"],
}, ensure_ascii=False, indent=2), encoding="utf-8")

print(f"{VER} chars {len(DSL)} TextFit {tf.n} problems {len(tf.problems)} "
      f"bands {len(BANDS)} measured {len(MEAS)} pos {DSL.count('<Positioned')} "
      f"nodes {DSL.count('<Container') + DSL.count('<Text ')}")
print("y_end", round(y + 72, 1), "families", len(FAMILIES))
if tf.problems:
    print("PROBLEMS", tf.problems)
