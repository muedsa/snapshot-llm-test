"""A17: emit the four 1200x1600 handbook pages.

Every printed code line is read back from the real example DSL files in
tmp/<run_id>/A17/examples/, so a handbook page cannot print a different document from
the one that renders example-0N.png. Long physical lines are wrapped for display and
the continuation is marked with a "↳" gutter arrow.

Usage: python tmp/<run_id>/A17/gen_handbook.py
"""
import os
import re
import sys
from pathlib import Path

root = Path(os.environ["SNAPSHOT_TASK_ROOT"])
run_id = os.environ["SNAPSHOT_RUN_ID"]
sys.path.insert(0, str(root / "tmp" / run_id / "_suite" / "scripts"))
from dslkit import Doc  # noqa: E402

_LABEL = Doc.label


def _label(self, x, y, w, h, s, *a, **kw):
    """dslkit.Doc.label has no per-call font argument; swap the doc default.

    A Container tighter than the text line box clips the glyphs, so grow the box
    to fit every wrapped line at the requested font size."""
    font, old = kw.pop("font", None), self.font
    if font:
        self.font = font
    size = kw.get("size", 20)
    line_h = int(round(size * 1.42)) + 1
    est = est_w(str(s), size, font == MONO)
    lines = max(1, -(-int(est) // max(int(w or 1), 1)))
    h = max(h, line_h * lines)
    try:
        _LABEL(self, x, y, w, h, s, *a, **kw)
    finally:
        self.font = old


Doc.label = _label


def panel(d, x, y, w, h, fill, radius=16, border=None):
    d.pos(x, y, w, h, d.box(w, h, color=fill, radius=radius, border=border))

EX_DIR = root / "tmp" / run_id / "A17" / "examples"
OUT = root / "tmp" / run_id / "A17" / "handbook"
OUT.mkdir(parents=True, exist_ok=True)

W, H, M = 1200, 1600, 48
CW = W - 2 * M
MONO = "DejaVu Sans Mono,Noto Sans Mono CJK SC"
BODY = "Inter,Noto Sans CJK SC"
BODY_B = "Inter Semi Bold,Noto Sans CJK SC"

INK, MUT, SOFT = "#101A2E", "#48587A", "#6B7C97"
CARD, LINE, ACC = "#FFFFFF", "#DDE4EF", "#1F4FD8"
CODE_BG, CODE_FG = "#0E1729", "#DCE6F5"
CODE_CM, CODE_MK, CODE_NUM = "#8093AE", "#FBBF24", "#5B6C88"

BODY_SIZE, CODE_SIZE = 24, 20
BODY_PITCH, CODE_PITCH = 32, 29


def est_w(s, size, mono=False):
    return sum(size * (0.61 if mono else 0.53) if ord(c) < 0x2E80 else size * 1.03
               for c in s)


def wrap(s, size, maxw, mono=False):
    cur, out = "", []
    for ch in s:
        if cur and est_w(cur + ch, size, mono) > maxw:
            out.append(cur)
            cur = ch
        else:
            cur += ch
    out.append(cur or "")
    return out


def code_tokens(s):
    """Split a source line only at break points that never cut a token:
    after '>' , after a run of spaces, and before '<' when it is not tag-start."""
    toks, cur = [], ""
    for i, ch in enumerate(s):
        cur += ch
        nxt = s[i + 1] if i + 1 < len(s) else ""
        if ch == ">" or (ch == " " and nxt not in ("", " ")) or \
           (ch == "<" and len(cur) > 1 and cur[-2] not in " >/"):
            if cur[-1] in "<" and len(cur) > 1:
                toks.append(cur[:-1])
                cur = "<"
            else:
                toks.append(cur)
                cur = ""
    if cur:
        toks.append(cur)
    return toks


def wrap_code(s, size, maxw):
    """Greedy line pack over code_tokens(); continuation rows carry a ↳ gutter."""
    toks, out, cur = code_tokens(s), [], ""
    while toks:
        prefix = "" if not out else "↳ "
        room = maxw - est_w(prefix, size, True)
        while toks and (not cur or est_w(cur + toks[0], size, True) <= room):
            cur += toks.pop(0)
        out.append(cur.rstrip())
        cur = ""
    return out


def code_spans(line, base=None):
    """One source line as inline <Raw> spans. ']]>' prints as ']]' + '>' so the
    quoted CDATA terminator survives the handbook page's own CDATA nesting."""
    spans = []
    for p in re.split(r"(!\[CDATA\[|\]\]>|<!--.*?-->)", line):
        if not p:
            continue
        col = CODE_MK if p in ("<![CDATA[", "]]>") else (
            CODE_CM if p.startswith("<!--") else (base or CODE_FG))
        if p == "]]>":
            spans.append(f'<Raw color="{CODE_MK}">]]</Raw>')
            spans.append(f'<Raw color="{CODE_MK}"><![CDATA[>]]></Raw>')
            continue
        body = f"<![CDATA[{p}]]>" if ("<" in p or ">" in p or p != p.strip()) else p
        spans.append(f'<Raw color="{col}">{body}</Raw>')
    return "".join(spans)


class Page:
    def __init__(self, title, subtitle, kicker):
        self.d = Doc(W, H, bg="#F4F6FB", font=BODY)
        self.y = M
        d = self.d
        d.rect(M, self.y, 6, 78, ACC)
        d.label(M + 22, self.y - 2, CW - 22, 28, kicker, color=SOFT, size=24,
                font=BODY, valign="TOP")
        d.label(M + 22, self.y + 26, CW - 22, 52, title, color=INK, size=38,
                style="BOLD", font=BODY_B, valign="TOP")
        d.label(M + 22, self.y + 82, CW - 22, 30, subtitle, color=MUT, size=24,
                font=BODY, valign="TOP")
        self.y += 126
        d.rect(M, self.y, CW, 1, LINE)
        self.y += 24

    def section(self, heading, bullets):
        d = self.d
        d.label(M, self.y, CW, 30, heading, color=ACC, size=26, style="BOLD",
                font=BODY_B, valign="TOP")
        self.y += 38
        for b in bullets:
            lines = len(wrap(b, BODY_SIZE, CW - 40))
            d.dot(M + 9, self.y + 15, 7, ACC)
            d.label(M + 30, self.y, CW - 30, BODY_PITCH * lines, b, color=INK,
                    size=BODY_SIZE, font=BODY, valign="TOP")
            self.y += BODY_PITCH * lines
        self.y += 12

    def code_panel(self, ex_name, ranges, note, total_lines):
        d = self.d
        src = (EX_DIR / f"{ex_name}.snapshot").read_text(encoding="utf-8").split("\n")
        rows = []
        for i, (a, b) in enumerate(ranges):
            if i:
                rows.append((None, "…"))
            for ln in range(a, b + 1):
                text = src[ln - 1].rstrip()
                cells = wrap_code(text, CODE_SIZE, CW - 52 - 54)
                if len(cells) > 1:
                    print(f"  wrap {ex_name}:{ln} -> {len(cells)} rows")
                rows.append((ln, cells[0]))
                for c in cells[1:]:
                    rows.append((None, "↳ " + c.lstrip()))
        panel_h = 46 + len(rows) * CODE_PITCH + 16
        d.rect(M, self.y, CW, panel_h, CODE_BG, radius=16)
        d.label(M + 26, self.y + 12, CW - 320, 28,
                f"{ex_name}.snapshot · 与独立渲染结果同一份 DSL", color="#9FB4D4",
                size=22, font=BODY_B, valign="TOP")
        d.label(W - M - 300, self.y + 12, 274, 28,
                f"印刷第 {ranges[0][0]}–{ranges[-1][1]} 行 / 全 {total_lines} 行",
                color=CODE_MK, size=22, font=BODY, align="END", valign="TOP")
        yy = self.y + 46
        for ln, txt in rows:
            if ln is None and txt == "…":
                d.label(M + 78, yy, CW - 130, CODE_PITCH,
                        "⋮  省略若干行，完整内容见同名 .snapshot", color=CODE_NUM,
                        size=CODE_SIZE, font=MONO, valign="TOP")
            elif ln is None:
                d.pos(M + 78, yy, CW - 104, CODE_PITCH,
                      f'<Text fontSize="{CODE_SIZE}" fontFamily="{MONO}">'
                      f'{code_spans(txt, base="#A9BAD6")}</Text>')
            else:
                d.pos(M + 26, yy, 46, CODE_PITCH,
                      f'<Text fontSize="{CODE_SIZE}" fontFamily="{MONO}">'
                      f'<Raw color="{CODE_NUM}">{ln:>3}</Raw></Text>')
                d.pos(M + 78, yy, CW - 104, CODE_PITCH,
                      f'<Text fontSize="{CODE_SIZE}" fontFamily="{MONO}">'
                      f'{code_spans(txt)}</Text>')
            yy += CODE_PITCH
        self.y += panel_h + 10
        full = "⋮ 省略的行 · ↳ 续行 · " + note
        if est_w(full, 22) > CW:
            print(f"  NOTE TOO LONG {ex_name}: {est_w(full, 22):.0f} > {CW}")
        d.label(M, self.y, CW, 26, full, color=SOFT, size=22, font=BODY, valign="TOP")
        self.y += 38

    def footer(self, right):
        d = self.d
        d.rect(M, H - M - 32, CW, 1, LINE)
        d.label(M, H - M - 26, CW - 260, 24, "Snapshot DSL 入门手册 · 从文字到图片",
                color=SOFT, size=22, font=BODY, valign="TOP")
        d.label(W - M - 260, H - M - 26, 260, 24, right, color=ACC, size=22,
                font=BODY_B, align="END", valign="TOP")

    def save(self, name):
        if self.y > H - M - 36:
            raise SystemExit(f"{name}: overflow, content bottom y={self.y:.0f}")
        dsl = self.d.dsl() + "\n"
        (OUT / f"{name}.snapshot").write_text(dsl, encoding="utf-8")
        print(name, "content bottom y =", round(self.y, 1), "bytes =",
              len(dsl.encode("utf-8")))


# ============================================================== page 1
p = Page("一次请求，一张图片", "请求体、响应头与错误体：先把契约读清楚",
         "第 1 页 / 共 4 页 · 调用契约")
p.section("请求：纯文本，不是 JSON", [
    "端点 POST /snapshot，请求体是 UTF-8 纯文本，Content-Type 用 text/plain。",
    "<Snapshot> 必须是第一个开始标签、只出现一次，且只有一个根 Widget 子节点。",
    "type 决定 png / jpg / webp，响应 Content-Type 必须与编码一致。",
    "根标签没有宽高：画布尺寸由布局决定（见第 2 页）。",
])
p.section("成功：图片字节 + 四个可核对的响应头", [
    "X-Request-Id 每个响应都有，传入合法值会被沿用，否则服务生成 UUID。",
    "Server-Timing 分段：queue、render、image、cache;desc=hit、total，单位毫秒。",
    "X-Snapshot-Cache 取 hit 或 miss；X-Snapshot-Image-Count 给出图片数量。",
])
p.section("失败：JSON 而不是图片", [
    "错误体统一为 {code, message, requestId}，按 code 分支而不是猜文案。",
    "400：EMPTY_REQUEST、PARSE_ERROR、RENDER_ERROR、IMAGE_LOAD_ERROR。",
    "PARSE_ERROR 的 message 带位置，如 Pos[3:18]~72: Attr [color] unsupported CSS color。",
    "401 未授权、413 体积超限、429 限流（带 Retry-After）、503 队列满、504 渲染超时。",
    "?errorImage=png 让解析失败返回高亮图，状态码仍是 400。",
    "curl 失败也会把 JSON 写进 result.png：用文件前先查 HTTP 状态与 Content-Type。",
])
p.code_panel("example-01", [(1, 13)],
             "断开点只在标签边界；本片段逐行原样，第 14–19 行是 ERROR 段与收尾。", 19)

d = p.d
iy = p.y
panel(d, M, iy, CW, 224, CARD, border=f"1 SOLID {LINE}")
d.label(M + 26, iy + 14, CW - 52, 26, "本页构件直接绘制的流程图（Container + Row + Text，非贴图）",
        color=SOFT, size=22, font=BODY, valign="TOP")
steps = [("请求", "UTF-8 纯文本 DSL", "text/plain", ACC),
         ("解析", "Parser → Widget 树", "出错即 400", "#7C3AED"),
         ("渲染", "JVM + Skia 离线出图", "确定性", "#0F766E"),
         ("响应", "image/png 字节", "四个响应头", "#B45309")]
bw = (CW - 52 - 3 * 22) / 4
for i, (t, s1, s2, c) in enumerate(steps):
    x = M + 26 + i * (bw + 22)
    d.rect(x, iy + 50, bw, 112, "#EEF2FA", radius=12)
    d.rect(x, iy + 50, bw, 6, c)
    d.label(x + 14, iy + 64, bw - 28, 26, t, color=INK, size=24, style="BOLD",
            font=BODY_B, valign="TOP")
    d.label(x + 14, iy + 96, bw - 28, 22, s1, color=MUT, size=20, font=BODY, valign="TOP")
    d.label(x + 14, iy + 124, bw - 28, 22, s2, color=SOFT, size=20, font=BODY, valign="TOP")
    if i < 3:
        d.line(x + bw + 3, iy + 100, x + bw + 19, iy + 100, 3, "#9AAAC4")
d.rect(M + 26, iy + 172, CW - 52, 32, "#FDECEC", radius=8)
d.label(M + 40, iy + 176, CW - 80, 24,
        "任一阶段失败都不产出图片：400 解析错误 / 413 体积超限 / 429 限流 / 504 渲染超时",
        color="#A32B2B", size=20, font=BODY, valign="TOP")
p.y += 224 + 16
p.footer("主题：契约与错误")
p.save("handbook-01")

# ============================================================== page 2
p = Page("尺寸来自布局，不是 CSS", "BoxConstraints、有界主轴与 Stack 定位规则",
         "第 2 页 / 共 4 页 · 布局")
p.section("Box 布局协议", [
    "父传 BoxConstraints（默认 0 到无穷），子在其中选定尺寸，父再决定位置。",
    "Container 的 width/height 是收紧约束，父级更严格的约束仍然生效。",
])
p.section("根尺寸从哪里来", [
    "Snapshot 不接受单独的画布宽高，固定画布要用根 Container 或 SizedBox 表达。",
    "Surface 取根 RenderBox 的布局尺寸并向上取整为像素。",
    "根尺寸为 0 → layout size is empty；无限 → layout size is infinite。",
    "更大的 Surface 不会放大内容，只会多出右侧与底部的背景。",
])
p.section("Row / Column / Expanded", [
    "Row、Column 都是 Flex 的特化；Expanded 等价于 Flexible(fit = TIGHT)。",
    "三者只能是 Flex、Row 或 Column 的直接子节点，否则 parentData 类型不匹配。",
    "主轴无限就没有剩余空间可分配，先用外层容器给出有限主轴。",
    "flex 是正整数权重；允许子节点小于份额时改用 Flexible 或 Spacer。",
])
p.section("Stack 与 Positioned", [
    "Stack 先布局非 Positioned 子节点，由它们决定 Stack 尺寸。",
    "同一轴 left、right、width 最多给两项：两边推尺寸，一边加尺寸推另一侧。",
    "Stack 的 clipBehavior 默认 HARD_EDGE，要显示溢出或阴影需显式写 NONE。",
])
p.code_panel("example-02", [(4, 13)],
             "第 1–3 行根标签与内边距，第 14–24 行 Stack 块与收尾。", 24)

d = p.d
iy = p.y
panel(d, M, iy, CW, 218, CARD, border=f"1 SOLID {LINE}")
d.label(M + 26, iy + 14, CW - 52, 26, "本页构件直接绘制：flex 份额与 Positioned 两种写法",
        color=SOFT, size=22, font=BODY, valign="TOP")
row = d.row([d.exp(d.box(200, 44, color="#1F4FD8", radius=8), 3),
             d.exp(d.box(200, 44, color="#7C3AED", radius=8), 2),
             d.exp(d.box(200, 44, color="#0F766E", radius=8), 1)], align="START")
d.pos(M + 26, iy + 48, CW - 52, 44, row)
acc = 0
for frac, col in [(3, "#1F4FD8"), (2, "#7C3AED"), (1, "#0F766E")]:
    seg = (CW - 52) * frac / 6
    d.label(M + 26 + acc + 12, iy + 98, seg - 20, 22,
            f"flex {frac} ≈ {frac / 6 * 100:.0f}%", color=col, size=20, font=BODY_B,
            valign="TOP")
    acc += seg
d.rect(M + 26, iy + 128, CW - 52, 78, "#EEF2FA", radius=12)
d.rect(M + 40, iy + 138, CW - 80, 22, "#FBBF24", radius=6)
d.label(M + 40, iy + 166, 400, 24, "left + right ⇒ 宽度由两边推导", color="#8A5A00",
        size=20, font=BODY, valign="TOP")
d.rect(M + 452, iy + 166, 190, 22, "#1F4FD8", radius=6)
d.label(M + 656, iy + 166, 400, 24, "left + width ⇒ 另一侧被推出", color=MUT,
        size=20, font=BODY, valign="TOP")
p.y += 218 + 16
p.footer("主题：布局与定位")
p.save("handbook-02")

# ============================================================== page 3
p = Page("文本、转义与颜色", "Text 与 RichText、CDATA 与 Raw、#RRGGBBAA 的尾部 alpha",
         "第 3 页 / 共 4 页 · 文本与颜色")
p.section("Text 与 RichText", [
    "Text 是 RichText 的便捷封装：字符串加可选 TextStyle 包成根 TextSpan。",
    "Text 可嵌套 Text、Raw、Emoji、WidgetSpan；嵌套的 Text 只作行内 Span。",
    "textAlign、softWrap、overflow、maxLines 只作用于最外层 Text。",
    "overflow 取 CLIP（默认）、FADE、ELLIPSIS、VISIBLE；盒子太小会静默丢字。",
])
p.section("转义三条规则", [
    "解析器不做 HTML 实体解码，&amp; 原样保留，不会变成 &。",
    "文本要出现 < 或 > 时使用 CDATA；CDATA 内的注释样式字符也按原文保留。",
    "Text 会裁剪首尾空白，需要保留空白改用 Raw；Raw 只能出现在 Text 的行内树里。",
])
p.section("颜色：最后一组才是 alpha", [
    "十六进制支持 3、4、6、8 位，按 CSS #RRGGBBAA 解析，最后一组是透明度。",
    "旧版按 #AARRGGBB 解析：迁移时 #80FF0000 要写成 #FF000080，否则颜色会变。",
    "Kotlin DSL 的颜色 Int 仍是 0xAARRGGBB，不受这条变更影响。",
    "另外支持命名色与 rgb()、hsl() 等函数写法，不支持 currentColor 与 lab()。",
])
p.section("属性写法里的小坑", [
    '布尔属性必须显式写值：debug="true"；只写 <Snapshot debug> 会回落默认值。',
    "标签名与属性名大小写敏感，未知属性被忽略而不是报错。",
    'fontFamily 多字体用逗号且不加空格："A, B" 会让第二个名字带前导空格。',
])
p.code_panel("example-03", [(6, 8), (18, 22)],
             "第 1–5 行标题，第 9–17 行行内 Span，第 23–29 行色块。", 29)

d = p.d
iy = p.y
panel(d, M, iy, CW, 214, CARD, border=f"1 SOLID {LINE}")
d.label(M + 26, iy + 14, 520, 26, "同一句文本：Text 与 Raw 的差别", color=SOFT,
        size=22, font=BODY, valign="TOP")
d.rect(M + 26, iy + 46, 500, 62, "#EEF2FA", radius=10)
d.label(M + 40, iy + 54, 470, 22, "首尾空白被裁剪", color=INK, size=22, font=BODY_B,
        valign="TOP")
d.label(M + 40, iy + 80, 470, 20, "<Text> 普通文本节点：trim", color=SOFT, size=18,
        font=MONO, valign="TOP")
d.rect(M + 578, iy + 46, 500, 62, "#EEF2FA", radius=10)
d.label(M + 592, iy + 54, 470, 22, "··首尾空格与换行都保留··", color=INK, size=22,
        font=BODY_B, valign="TOP")
d.label(M + 592, iy + 80, 470, 20, "<Raw> 行内节点：不 trim", color=SOFT, size=18,
        font=MONO, valign="TOP")
d.label(M + 26, iy + 116, 700, 24, "#FF0000 的后两位控制透明度（色块叠在深色底上）",
        color=MUT, size=22, font=BODY, valign="TOP")
for i, (a, lab) in enumerate([("FF", "不透明"), ("80", "约 50%"), ("1A", "约 10%")]):
    x = M + 26 + i * 176
    d.rect(x, iy + 148, 164, 50, "#101A2E", radius=10)
    d.rect(x + 10, iy + 157, 56, 32, f"#FF0000{a}", radius=6)
    d.label(x + 74, iy + 160, 86, 26, lab, color="#C6D3E8", size=20, font=BODY,
            valign="TOP")
p.y += 214 + 18
p.footer("主题：文本与颜色")
p.save("handbook-03")

# ============================================================== page 4
p = Page("滤镜、自检与可复现交付", "子树滤镜与背景滤镜、四层验证、图片与 DSL 成对交付",
         "第 4 页 / 共 4 页 · 效果与交付")
p.section("两种滤镜的方向不同", [
    "ImageFiltered 把自身子树当输入图像应用滤镜。",
    "BackdropFilter 读取已经画在它背后的内容再按 BlendMode 合成，典型用途是毛玻璃。",
    "BackdropFilter 只有背后有内容时才可见，应配 ClipRect、ClipOval 或 ClipRRect 限定区域。",
])
p.section("Parser 能写到什么程度", [
    "ImageFiltered 与 BackdropFilter 要求有限非负的 sigmaX、sigmaY，可设 tileMode（默认 CLAMP）。",
    "ColorFiltered 要求 color 与 Skia blendMode；BackdropFilter 另支持 blendMode（默认 SRC_OVER）。",
    "这两个图片滤镜标签只构造高斯模糊，复杂 Skia 滤镜仍需 Kotlin DSL。",
    "Kotlin 里图片滤镜要显式给 outputBounds，模糊按 ceil(3×sigma) 外扩；Parser 自动补。",
])
p.section("视觉自检：四层，越靠前越稳", [
    "推荐顺序：布局与数值断言 → 像素采样 → Golden 逐像素 → artifact 人工检视。",
    "能用布局断言证明的不要升到 Golden；跨节点绘制、裁剪、滤镜、渐变才升级到像素。",
    "artifact 只是落盘给人看的证据，不是断言：“看过图”与“通过校验”要分开记录。",
])
p.code_panel("example-04", [(19, 26)],
             "第 1–18 行彩色背景条，第 27–33 行 ImageFiltered 块。", 33)

d = p.d
iy = p.y
panel(d, M, iy, CW, 212, "#0E1729")
d.label(M + 26, iy + 12, CW - 52, 24, "同一页构件直接绘制的对照：左为原样叠加，右为 ClipRRect + BackdropFilter",
        color="#9FB4D4", size=22, font=BODY, valign="TOP")
stripes = ["#1F4FD8", "#7C3AED", "#0F766E", "#B45309", "#BE123C", "#2563EB",
           "#7C3AED", "#0F766E"]
sw = (CW - 52) / len(stripes)
for i, c in enumerate(stripes):
    d.rect(M + 26 + i * sw, iy + 44, sw, 128, c)
d.rect(M + 26, iy + 44, (CW - 52) / 2 - 14, 128, "#FFFFFF1F", radius=12)
d.label(M + 44, iy + 92, (CW - 52) / 2 - 60, 40, "未加滤镜：身后的条纹原样可见",
        color="#F8FAFC", size=22, font=BODY_B, valign="TOP")
d.pos(M + 26 + (CW - 52) / 2 + 14, iy + 44, (CW - 52) / 2 - 14, 128,
      '<ClipRRect borderRadius="12" clipBehavior="ANTI_ALIAS">'
      '<BackdropFilter sigmaX="12" sigmaY="12" tileMode="CLAMP">'
      f'<Container width="{CW - 52:.0f}" height="128" color="#FFFFFF1F">'
      '<Text fontSize="22" fontFamily="Inter,Noto Sans CJK SC" color="#F8FAFC" '
      'fontStyle="BOLD">BackdropFilter：模糊的是身后像素</Text></Container>'
      "</BackdropFilter></ClipRRect>")
d.label(M + 26, iy + 176, CW - 52, 24,
        "sigma 从 12 降到 2 就是轻微柔化；超出裁剪区域的模糊边缘会被 ClipRRect 截掉",
        color="#8093AE", size=20, font=BODY, valign="TOP")
p.y += 212 + 14

d = p.d
iy = p.y
panel(d, M, iy, CW, 116, CARD, border=f"1 SOLID {LINE}")
d.label(M + 26, iy + 12, CW - 52, 26, "可复现交付清单", color=ACC, size=26,
        style="BOLD", font=BODY_B, valign="TOP")
d.label(M + 26, iy + 50, CW - 52, 24,
        "图片与产生它的完整 DSL 同名成对保存 · 相同请求可能命中缓存（X-Snapshot-Cache 取 hit/miss）",
        color=INK, size=22, font=BODY, valign="TOP")
d.label(M + 26, iy + 78, CW - 52, 24,
        "渲染是 JVM + Skia 的确定性离线过程，不经过浏览器 · 用 X-Request-Id 把图片与服务日志对应",
        color=INK, size=22, font=BODY, valign="TOP")
p.y += 116 + 14
p.footer("主题：滤镜与交付")
p.save("handbook-04")
