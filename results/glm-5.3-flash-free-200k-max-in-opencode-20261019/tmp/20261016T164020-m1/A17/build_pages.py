# -*- coding: utf-8 -*-
"""A17：四页 1200×1600 教学手册。核心子树 1:1 嵌入 + 印刷例源码（行号=完整文件 1-based）。"""
import io, sys, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

D = "outputs/20261016T164020-m1/A17"
EXSRC = {}
for i in range(4):
    EXSRC[i + 1] = open(os.path.join(D, f"example-0{i+1}.snapshot"), encoding="utf-8").read().splitlines()
EXBG = {1: "#F5F3EE", 2: "#F2F4F8", 3: "#101322", 4: "#0E1016"}
ACCENT = {1: "#2F5CD9", 2: "#1F7A5C", 3: "#B3651F", 4: "#4C3AD6"}

def estw(s, fs, mono=False):
    t = 0.0
    for ch in s:
        o = ord(ch)
        if o > 0x2E7F or ch in "，。：；（）·—－、":
            t += fs
        elif ch == " ":
            t += fs * 0.30
        elif ch in "0123456789":
            t += fs * 0.6
        elif ch.isupper():
            t += fs * 0.72
        else:
            t += fs * (0.6 if mono else 0.545)
    return t

CJK = "Noto Sans CJK SC"
MONO = "Noto Sans Mono CJK SC"

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def indent_a0(s):
    n = 0
    for ch in s:
        if ch == " ":
            n += 1
        else:
            break
    return "\u00a0" * n + s[n:]

S = []
def R(x, y, w, h, color=None, radius=None, border=None):
    a = f'width="{w}" height="{h}"'
    if color:
        a += f' color="{color}"'
    if radius:
        a += f' borderRadius="{radius}"'
    if border:
        a += f' border="{border}"'
    S.append(f'<Positioned left="{x}" top="{y}"><Container {a} /></Positioned>')

def cdata_wrap(s):
    if ("<" in s) or (">" in s) or ("&" in s):
        if "]]>" in s:
            s = s.replace("]]>", "]]]]><![CDATA[>")
        return "<![CDATA[" + s + "]]>"
    return s

def TXT(x, y, s, fs, color, bold=False, fam=CJK, ml=1, anchor=None):
    st = f' fontSize="{fs}" color="{color}" fontFamily="{fam}" maxLines="{ml}" overflow="CLIP"'
    if bold:
        st += ' fontStyle="BOLD"'
    if anchor == "right":
        x -= estw(s, fs)
    S.append(f'<Positioned left="{x}" top="{y}"><Text{st}>{cdata_wrap(s)}</Text></Positioned>')

def hair(x, y, w, c="#E2DFD5"):
    R(x, y, w, 1, c)

PAGES = [
 dict(n=1, title="从文字到图片：一次真实调用", sub="向 /snapshot 发送 XML 文本，取回 PNG 字节",
  s1="调用契约（请求 → 响应 → 错误）", ex=1,
  body=[
   "POST /snapshot：请求体是 UTF-8 纯文本 XML（不是 JSON）。",
   "200 响应体即图片字节（image/png）；X-Request-Id 与 Server-Timing 用于排错追踪。",
   "错误时返回 JSON（code/message/requestId）；429/503 先读 Retry-After 再重试。"],
  facts=["根标签必须是 <Snapshot>，type=png/jpg/webp", "画布尺寸由布局树决定，不是属性",
         "GET /fonts 列出实际可用的字体族", "密钥走 X-API-Key 头，不写进 DSL"],
  header="example-01.snapshot · 400×240 · 完整 16 行直印",
  rows=[(i, 1) for i in range(1, 17)],
  tk=[("契约三要素", "POST /snapshot · text/plain · 200 PNG"),
      ("排错抓手", "X-Request-Id 追踪单一请求全链路")]),
 dict(n=2, title="布局：根尺寸来自布局树", sub="有界 Row/Column/Expanded 与 Stack 定位对照",
  s1="约束先有界，flex 才有剩余空间可分", ex=2,
  body=[
   "根尺寸：Snapshot 自身不带宽高，画布 = 布局根的有限尺寸；本图由 400×240 的 SizedBox 决定。",
   "Row/Column 有界才按 flex 分配；Expanded 须是 Flex 直接子节点，上例剩余宽按 2:1 拆分。",
   "Stack 定位：非定位子项先依流排版，Positioned 子项用 left/top 绝对放置，可配宽高限定区域。"],
  facts=["Expanded 只在 Flex 直接子级有意义", "固定子项 + SizedBox 间距可混排",
         "交叉轴默认居中；容器无宽会被拉伸", "调试顺序：根有界 → 中层有界 → 叶子"],
  header="example-02.snapshot · 印刷 15/28 行（行号 9–23）",
  rows=[None] + [(i, 2) for i in range(9, 24)] + [None],
  mk_top="…… 前 8 行省略：Snapshot / Stack / 400×240 与 Column 标题 ……",
  mk_bot="…… 后 5 行省略：Column / Container / Stack / Snapshot 闭合 ……",
  tk=[("根尺寸口诀", "等于根布局的有限、非零宽高"),
      ("flex 三步", "先有界 → 再分剩余 → 只放直接子")]),
 dict(n=3, title="文本：实体不解码与尾部 alpha", sub="Raw / CDATA、行内样式与 #RRGGBBAA",
  s1="让“原样”真正原样", ex=3,
  body=[
   "解析器不做 HTML 实体解码；<、& 收进 CDATA 交给 Text；Raw 段保留原文空白。",
   "行内样式：Text 内嵌 Raw 段带 color/fontStyle；子标签的装饰属性整体替换而非逐字段继承。",
   "8 位颜色 #RRGGBBAA：透明度在末两位；同 RGB 的 #2F5CD966 在深底上比实色更暗。"],
  facts=["Raw = 保留空白的行内 Span", "CDATA 内部不被当作标签解析",
         "段落参数只由最外层 Text 控制", "尾部 alpha：末两位，#2F5CD966 ≈ 40%"],
  header="example-03.snapshot · 印刷 18/23 行（行号 4–21）",
  rows=[None] + [(i, 3) for i in range(4, 22)],
  mk_top="…… 前 3 行省略：Snapshot / Stack / 400×240 包装 ……",
  mk_bot=None,
  tk=[("原样三招", "CDATA 承载标记；Raw 保留空白"),
      ("尾部 alpha", "透明度写末两位，深浅底两端校验")]),
 dict(n=4, title="滤镜与可复现交付", sub="背景滤镜、子树滤镜与自检流程",
  s1="滤镜看作用对象，交付看留痕", ex=4,
  body=[
   "BackdropFilter 只模糊背后已画的内容；配 ClipRRect 限边，面板用低不透明白 #FFFFFF2E。",
   "ImageFiltered 把这棵子树的绘制结果整层高斯；同族还有 Opacity 与 ColorFiltered。",
   "交付：图片与 .snapshot 成对落盘；自检先整图再放大局部，全程留痕。"],
  facts=["BackdropFilter 背后要有内容", "ClipRRect 负责清边（ANTI_ALIAS）",
         "面板色 #FFFFFF2E = 18% 白", "子树模糊同样可被外层裁剪"],
  header="example-04.snapshot · 印刷 17/28 行（行号 4–16、22–25）",
  rows=[None] + [(i, 4) for i in range(4, 17)] + [None] + [(i, 4) for i in range(22, 26)],
  mk_top="…… 前 3 行省略：Snapshot / Stack / 400×240 包装 ……",
  mk_mid="…… 行 17–21 省略：毛玻璃说明标题及上级容器 ……",
  tk=[("两类滤镜", "背景模糊看 Behind；子树模糊看 Own"),
      ("交付自检", "成对留痕 · 整图+放大 · 不后处理")]),
]

def marker_for(pg, idx):
    if idx == 0:
        return pg.get("mk_top") or "…… ……"
    return pg.get("mk_mid") or pg.get("mk_bot") or "…… ……"

for pg in PAGES:
    n = pg["n"]; EX = pg["ex"]; acc = ACCENT[n]
    R(0, 0, 1200, 1600, "#F8F7F3")
    TXT(48, 54, pg["title"], 40, "#171E33", bold=True)
    TXT(1152, 64, f"第 {n} 页 · 共 4 页", 20, "#5C6474", anchor="right")
    TXT(48, 106, pg["sub"], 24, "#5C6474")
    hair(48, 148, 1104)
    R(48, 182, 10, 26, acc, radius=3)
    TXT(70, 178, pg["s1"], 28, "#171E33", bold=True)
    yb = 228
    for ln in pg["body"]:
        w = estw(ln, 24)
        if w > 1090:
            print(f"P{n} WARN body {int(w)}", ln)
        TXT(48, yb, ln, 24, "#3A4152")
        yb += 38
    yI = 352
    R(48, yI, 432, 308, "#FFFFFF", radius=12, border="1 SOLID #E2DFD5")
    TXT(64, yI + 264, "真实渲染 · 400×240", 18, "#5C6474")
    core = "\n".join(EXSRC[EX][3:-2])
    embed = (f'<Positioned left="64" top="{yI + 16}"><Stack><SizedBox width="400" height="240" />'
             f'<Positioned left="0" top="0"><Container width="400" height="240" color="{EXBG[EX]}" /></Positioned>'
             f'{core}</Stack></Positioned>')
    S.append(embed)
    yf = yI + 8
    TXT(512, yf, "本页速览", 22, acc, bold=True)
    yf += 40
    for f in pg["facts"]:
        w = estw(f, 24)
        if w > 610:
            print(f"P{n} WARN fact {int(w)}", f)
        R(512, yf + 9, 6, 6, acc, radius=1)
        TXT(530, yf, f, 24, "#3A4152")
        yf += 38
    yC = 684
    codeH = 46 + 16 + len(pg["rows"]) * 30 + 18
    R(48, yC, 1104, codeH, "#1E2433", radius=14)
    for dx, c in [(0, "#FF5F57"), (18, "#FEBC2E"), (36, "#28C840")]:
        R(48 + 20 + dx, yC + 16, 12, 12, c, radius=6)
    TXT(48 + 76, yC + 12, pg["header"], 18, "#8B94A8", fam=MONO)
    y0 = yC + 46 + 16
    for idx, row in enumerate(pg["rows"]):
        if row is None:
            TXT(48 + 88, y0, marker_for(pg, idx), 20, "#5F6B8A", fam=MONO)
        else:
            ln_no, exi = row
            line = EXSRC[exi][ln_no - 1]
            cw = estw(line, 20, mono=True)
            if cw > 980:
                print(f"P{n} WARN code {ln_no} {int(cw)}")
            TXT(48 + 104, y0, indent_a0(line), 20, "#E8ECF5", fam=MONO)
            TXT(48 + 96, y0, str(ln_no), 20, "#5F6B8A", fam=MONO, anchor="right")
        y0 += 30
    yk = yC + codeH + 30
    if yk + 140 > 1520:
        print(f"P{n} WARN takeaways {yk}")
    for k, (tt, bb) in enumerate(pg["tk"]):
        xx = 48 + (k % 2) * 564
        yy = yk + (k // 2) * 164
        R(xx, yy, 540, 140, "#FFFFFF", radius=12, border="1 SOLID #E2DFD5")
        R(xx + 22, yy + 26, 8, 24, acc, radius=3)
        TXT(xx + 42, yy + 24, tt, 26, "#171E33", bold=True)
        w = estw(bb, 24)
        if w > 500:
            print(f"P{n} WARN tk {int(w)}", bb)
        TXT(xx + 22, yy + 78, bb, 24, "#3A4152", ml=1)
    hair(48, 1528, 1104)
    TXT(48, 1544, "Snapshot DSL 上手手册 · 从文字到图片", 20, "#8A8494")
    TXT(1152, 1544, "A17", 20, "#8A8494", anchor="right")
    dsl = ('<Snapshot background="#F8F7F3" type="png"><Stack>'
           '<SizedBox width="1200" height="1600" />' + "".join(S) + "</Stack></Snapshot>")
    open(os.path.join(D, f"page-0{n}.snapshot"), "w", encoding="utf-8", newline="\n").write(dsl)
    S = []
    print(f"P{n} built rows {len(pg['rows'])} takeawayY {yk}")
print("done")
