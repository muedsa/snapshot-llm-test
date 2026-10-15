#!/usr/bin/env python
"""A17 四页 DSL 入门手册 + 4 个可独立运行的示例。

启动基准：总任务根 (suite_root)。无附加输入，文案与数值写在 PAGES 里。

**一致性设计（本题最关键的一条）**
  每个页面内容由 `CORE[i]`（一个 Python 字符串，8–18 行）唯一决定：
    * 独立示例 DSL = 3 行外层包装（Snapshot / 400×240 Container / Stack）
      + CORE[i] 原样 + 3 行收尾；
    * 教学页把**同一份 CORE[i] 原文**放进一个 400×240 的有界容器里，
      坐标不缩放、不改字号、不换滤镜参数 —— 1:1 展示；
    * 手册印刷的代码片段 = 独立 DSL 的第 4 行到第 3+len(CORE) 行，
      逐字相同（示例脚本会断言这一点）。
  因此"印刷的是一套、跑的是另一套"在结构上不可能发生。

**印刷转义**：页面上直接印裸字符 `<` 与 `&`（服务端 `text=` 属性不解码实体，
照印实体反而会显示成 "&lt;"）；`examples.json` 同时给出 XML 转义形式，
并断言 unescape(xml_escaped) == 印刷原文。
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

BASE = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
DRAFTS = "tmp/run-20261011-01/A17/drafts"
OUT = "outputs/run-20261011-01/A17"

FH = "Inter Semi Bold,Noto Sans CJK SC"
FM = "Inter Medium,Noto Sans CJK SC"
FB = "Inter,Noto Sans CJK SC"
FMONO = "DejaVu Sans Mono"

C = {
    "page": "#FFFFFF", "band": "#F8FAFC", "card": "#FFFFFF", "edge": "#E2E8F0",
    "codebg": "#0F172A", "codefg": "#E2E8F0", "codehl": "#7DD3FC", "codecmt": "#64748B",
    "ink": "#0F172A", "body": "#334155", "muted": "#64748B", "faint": "#94A3B8",
    "accent": "#1D4ED8", "green": "#15803D", "red": "#B91C1C",
}

W, H = 1200, 1600
M = 48
CODE_X, CODE_W = M, W - 2 * M          # 48 .. 1152
CODE_PITCH = 27
ILL_X, ILL_W, ILL_H = 96, 400, 240
BULLET_PITCH_1, BULLET_PITCH_2 = 40, 66
FOOTER_RULE = 1496


def est_w(text: str, size: float) -> float:
    """字面宽估算（系数沿用 A14 对本服务实测标定出的 em 表）。"""
    _NARROW = "iljft.,;'`|"
    _MED = "rsz"
    _WIDE = "mw"
    _HEAVY = "<>&@"
    tot = 0.0
    for ch in text:
        o = ord(ch)
        if (0x1100 <= o <= 0x115F or 0x2E80 <= o <= 0x303E or 0x3041 <= o <= 0x33FF
                or 0x3400 <= o <= 0x4DBF or 0x4E00 <= o <= 0x9FFF
                or 0xAC00 <= o <= 0xD7A3 or 0xF900 <= o <= 0xFAFF
                or 0xFE10 <= o <= 0xFE4F or 0xFF00 <= o <= 0xFF60 or 0xFFE0 <= o <= 0xFFE6
                or ch in "—…·“”"):
            tot += 1.0
        elif ch == " ":
            tot += 0.28
        elif ch in _NARROW:
            tot += 0.30
        elif ch in _MED:
            tot += 0.40
        elif ch in _WIDE:
            tot += 0.85
        elif ch in _HEAVY:
            tot += 0.66
        elif ch in ":;":
            tot += 0.42
        elif ch == "/":
            tot += 0.40
        elif ch.isdigit():
            tot += 0.53
        elif ch.isupper():
            tot += 0.70
        elif ch.isalpha():
            tot += 0.60
        else:
            tot += 0.32
    return tot * size


def n_lines(text: str, size: float, box_w: float) -> int:
    return max(1, -(-int(est_w(text, size) * 100) // int(box_w * 100)))

# ================================================================ 核心示例（8–18 行）
CORE = {}

CORE["01"] = "\n".join([
    '<Positioned left="24" top="22" width="352" height="196">',
    '<Container width="352" height="196" color="#FFFFFF" borderRadius="12"/>',
    '</Positioned>',
    '<Positioned left="44" top="40" width="200" height="26">',
    '<Text fontSize="17" color="#0F172A" fontFamily="Inter Semi Bold" text="请求"/>',
    '</Positioned>',
    '<Positioned left="44" top="70" width="240" height="22">',
    '<Text fontSize="15" color="#475569" text="POST /render"/>',
    '</Positioned>',
    '<Positioned left="44" top="106" width="240" height="22">',
    '<Text fontSize="15" color="#15803D" text="200  image/png"/>',
    '</Positioned>',
    '<Positioned left="44" top="142" width="240" height="22">',
    '<Text fontSize="15" color="#B91C1C" text="400  PARSE_ERROR"/>',
    '</Positioned>',
    '<Positioned left="44" top="178" width="290" height="22">',
    '<Text fontSize="14" color="#64748B" text="根标签 type 决定编码"/>',
    '</Positioned>',
])

CORE["02"] = "\n".join([
    '<Positioned left="24" top="24" width="352" height="80">',
    '<Row crossAxisAlignment="CENTER">',
    '<Expanded flex="2">',
    '<Container width="213" height="48" color="#1D4ED8" borderRadius="10"/>',
    '</Expanded>',
    '<Expanded flex="1">',
    '<Container width="107" height="48" color="#93C5FD" borderRadius="10"/>',
    '</Expanded>',
    '</Row>',
    '</Positioned>',
    '<Positioned left="24" top="122" width="352" height="80">',
    '<Stack fit="EXPAND">',
    '<Positioned left="16" top="24" width="320" height="32">',
    '<Container width="320" height="32" color="#0F172A" borderRadius="8"/>',
    '</Positioned>',
    '</Stack>',
    '</Positioned>',
])

CORE["03"] = "\n".join([
    '<Positioned left="24" top="20" width="352" height="156">',
    '<Container width="352" height="156" color="#FFFFFF" borderRadius="12"/>',
    '</Positioned>',
    '<Positioned left="44" top="36" width="320" height="26">',
    '<Text fontSize="17" color="#0F172A" fontFamily="Inter Semi Bold">',
    '<Text color="#15803D">PAID</Text><Raw> </Raw><Text color="#94A3B8">/</Text>',
    '<Raw> </Raw><Text color="#0F172A">已结算</Text>',
    '</Text>',
    '</Positioned>',
    '<Positioned left="44" top="84" width="320" height="26">',
    '<Text fontSize="17" color="#0F172A" fontFamily="Inter Semi Bold">',
    '<Raw><![CDATA[A < B & C > D]]></Raw>',
    '</Text>',
    '</Positioned>',
    '<Positioned left="44" top="128" width="40" height="28">',
    '<Container width="40" height="28" color="#0F172A80" borderRadius="6"/>',
    '</Positioned>',
])

CORE["04"] = "\n".join([
    '<Positioned left="24" top="20" width="352" height="160">',
    '<Container width="352" height="160" color="#FFFFFF" borderRadius="12"/>',
    '</Positioned>',
    '<Positioned left="44" top="40" width="120" height="120">',
    '<ColorFiltered color="#1D4ED8" blendMode="MULTIPLY">',
    '<Container width="120" height="120" color="#F97316" borderRadius="14"/>',
    '</ColorFiltered>',
    '</Positioned>',
    '<Positioned left="184" top="40" width="120" height="120">',
    '<ImageFiltered sigmaX="5" sigmaY="5" tileMode="CLAMP">',
    '<Container width="120" height="120" color="#22C55E" borderRadius="14"/>',
    '</ImageFiltered>',
    '</Positioned>',
    '<Positioned left="324" top="40" width="40" height="120">',
    '<Container width="40" height="120" color="#1D4ED8" borderRadius="14"/>',
    '</Positioned>',
])

# 独立示例的固定三行外层包装与三行收尾
EX_HEAD = ['<Snapshot type="png">',
           '<Container width="400" height="240" color="#F8FAFC">',
           '<Stack fit="EXPAND">']
EX_TAIL = ['</Stack>', '</Container>', '</Snapshot>']
OMISSION_MARK = "……省略外层包装……"

# ================================================================ 页面内容
PAGES = [
    {
        "id": "01", "section": "01 · 调用契约",
        "title": "把 DSL 文本变成一张图片",
        "lead": "Snapshot 不是浏览器：它把一段类 DOM 文本编译成一棵 Widget 树，"
                "再把根节点快照成图片。请求只有一次往返，响应要么是图片字节，"
                "要么是一段说明失败原因的 JSON。",
        "bullets": [
            "根标签只能是 Snapshot，且必须是文档的第一个标签；它只带一个根 Widget 子节点。",
            "响应的编码由根标签的 type 决定（png / jpg / webp），不要一律当 image/png 处理。",
            "结构或属性错误抛 ParseException，服务端映射为 400；布局参数非法映射为 422。",
            "错误消息带 Pos[行:列]~偏移，能直接定位到出错的属性值，不必整篇二分排查。",
        ],
        "core": "01",
        "aside": ["输出尺寸 = 根 Widget 的 width / height",
                  "响应二选一：图片字节 或 失败 JSON",
                  "错误消息自带行列与偏移"],
    },
    {
        "id": "02", "section": "02 · 布局",
        "title": "尺寸来自布局，不是来自视口",
        "lead": "输出画布的像素尺寸完全由布局决定：根 Widget 的宽高就是画布宽高，"
                "没有“视口”“屏幕宽度”“百分比”这类浏览器概念。"
                "在一个显式给了 width / height 的 Container 里，Row 会把主轴切成有界的份额。",
        "bullets": [
            "下面两块的画布都是 400×240，因为它就是 example-02 的根 Container 尺寸。",
            "上半块用 Row + Expanded 按 flex 份额切分；下半块用 Stack + Positioned 直接落坐标。",
            "Expanded / Flexible / Spacer 必须是 Flex、Row 或 Column 的直接子节点。",
            "Expanded 固定使用 TIGHT，不接受 fit 属性；只有 Flexible 才有 fit=\"LOOSE\"。",
            "Stack 的 fit 默认 LOOSE，clipBehavior 默认 HARD_EDGE；Positioned 只能挂在 Stack 下。",
        ],
        "core": "02",
        "aside": ["有界 Flex：份额由布局算", "Stack：坐标由你给",
                  "两者都受父约束限制"],
    },
    {
        "id": "03", "section": "03 · 文本与颜色",
        "title": "看不见的空白，转不掉的尖括号",
        "lead": "文本里最容易被吃掉的是空白，最容易被误解的是尖括号与 &。"
                "颜色还有一类：八位十六进制里，alpha 写在尾部而不是开头。",
        "bullets": [
            "<Text> 里的普通文本节点会被 trim；<Raw> 原样保留首尾空格与换行。",
            "解析器不做 HTML 实体解码：写 &amp; 会被原样显示成「&amp;」这几个字符。",
            "文本里需要 < 或 > 时用 CDATA，例如 <Raw><![CDATA[A < B]]></Raw>。",
            "多字体字符串不会逐项 trim，「A, B」会保留前导空格，要写成「A,B」。",
            "八位十六进制按 CSS 的 #RRGGBBAA 解析：alpha 在尾部，不在开头。",
        ],
        "core": "03",
        "aside": ["Raw 保住空格", "CDATA 保住 < 与 &",
                  "#0F172A80 的 80 是尾部 alpha"],
    },
    {
        "id": "04", "section": "04 · 效果与交付",
        "title": "滤镜的作用范围，以及什么叫完成",
        "lead": "滤镜分两类：BackdropFilter 读取已经画好的背景，"
                "ImageFiltered 与 ColorFiltered 作用在自己的子树上。"
                "解析器只提供高斯模糊，其它滤镜要走 Kotlin DSL。",
        "bullets": [
            "ColorFiltered 需要 color 与 blendMode，并把着色限制在子树的绘制边界内。",
            "ImageFiltered / BackdropFilter 需要非负有限的 sigmaX / sigmaY。",
            "BackdropFilter 读的是已绘制背景，建议配合 ClipRect / ClipOval / ClipRRect 限定范围。",
            "Opacity 取值 0 到 1，作用在整棵子树上。",
            "渲染成功只说明能出图，不代表画面对——必须实际打开每张图逐张看。",
            "可复现交付 = 保留真实 DSL、真实请求体、真实响应字节与逐图查看记录。",
        ],
        "core": "04",
        "aside": ["ColorFiltered：子树着色", "ImageFiltered：子树高斯模糊",
                  "看不到就等于没做"],
    },
]


# ---------------------------------------------------------------- 图元
def rect(x, y, w, h, color, radius=0, border=None):
    b = f' border="1 SOLID {border}"' if border else ""
    return (f'<Positioned left="{round(x, 2)}" top="{round(y, 2)}" width="{round(w, 2)}" '
            f'height="{round(h, 2)}"><Container width="{round(w, 2)}" height="{round(h, 2)}" '
            f'color="{color}" borderRadius="{radius}"{b}/></Positioned>')


def txt(t, x, y, w, h, size, color, family=FB, align=None, spacing=None):
    # 印刷的代码行里同时含 " 与 < / &。实测本服务：
    #   · text= 用双引号包裹时，内容不能含 "；
    #   · 改用**单引号**包裹（XML 允许）时，裸 " < > & 甚至 ]]> 都能原样渲染。
    # 因此印刷行一律走单引号；普通文案不含 " 时仍用双引号，避免无谓转义。
    if '"' in t:
        assert "'" not in t, f'文本同时含单引号与双引号，无法作为属性值: {t!r}'
        q = "'"
    else:
        q = '"'
    at = f' fontSize="{size}" color="{color}" fontFamily="{family}"'
    if align:
        at += f' textAlign="{align}"'
    if spacing:
        at += f' letterSpacing="{spacing}"'
    return (f'<Positioned left="{round(x, 2)}" top="{round(y, 2)}" width="{round(w, 2)}" '
            f'height="{round(h, 2)}"><Text{at} text={q}{t}{q}/></Positioned>')


# ---------------------------------------------------------------- 独立示例 DSL
def example_dsl(idx: str) -> list[str]:
    lines = EX_HEAD + CORE[idx].split("\n") + EX_TAIL
    assert 8 <= len(CORE[idx].split("\n")) <= 18, idx
    for ln in CORE[idx].split("\n"):
        assert len(ln) <= 88, f"第 {idx} 页示例有超过 88 字符的行，印刷会溢出: {ln}"
    return lines


# ---------------------------------------------------------------- 手册页
def page_dsl(p: dict) -> str:
    core = CORE[p["core"]]
    core_lines = core.split("\n")
    n_core = len(core_lines)
    printed = [OMISSION_MARK] + core_lines + [OMISSION_MARK]
    code_h = len(printed) * CODE_PITCH + 24

    b = [rect(0, 0, W, H, C["page"])]
    b.append(rect(0, 0, W, 8, C["accent"]))
    # 页眉
    b.append(txt("Snapshot DSL 入门手册", M, M + 8, 600, 40, 28, C["ink"], FH))
    b.append(txt(f"第 {int(p['id'])} 页 / 共 4 页", W - M - 320, M + 12, 320, 36, 24,
                 C["muted"], FM, align="RIGHT"))
    b.append(txt("面向首次接触 Snapshot 的程序员", W - M - 420, M + 48, 420, 28, 22,
                 C["faint"], FB, align="RIGHT"))
    b.append(rect(M, 132, W - 2 * M, 2, C["edge"]))
    # 章节与导语
    b.append(txt(p["section"], M, 152, 400, 30, 24, C["accent"], FM, spacing="1.5"))
    b.append(txt(p["title"], M, 186, W - 2 * M, 48, 34, C["ink"], FH))
    lead_box_w = W - 2 * M
    lead_n = n_lines(p["lead"], 24, lead_box_w)
    b.append(txt(p["lead"], M, 248, lead_box_w, lead_n * 34, 24, C["body"], FB))

    # 要点：按估算行数动态排，避免与插图标题相撞
    y = 248 + lead_n * 34 + 20
    bullet_w = W - 2 * M - 28
    for s in p["bullets"]:
        nl = n_lines(s, 24, bullet_w)
        b.append(rect(M + 2, y + 9, 10, 10, C["accent"], 3))
        b.append(txt(s, M + 28, y, bullet_w, nl * 34, 24, C["body"], FB))
        y += BULLET_PITCH_1 if nl == 1 else BULLET_PITCH_2

    # 教学插图：同一份 CORE，400×240，1:1
    ill_y = y + 46
    # 标签底沿必须高于插图卡的上描边（ill_y-12），否则描边会横穿文字（v2 就是这样）
    b.append(txt("教学插图 · 与下方代码同源", ILL_X, ill_y - 46, 460, 26, 24, C["ink"], FH))
    b.append(rect(ILL_X - 12, ill_y - 12, ILL_W + 24, ILL_H + 24, C["band"], 16, C["edge"]))
    b.append(f'<Positioned left="{ILL_X}" top="{ill_y}" width="{ILL_W}" height="{ILL_H}">'
             f'<Container width="{ILL_W}" height="{ILL_H}" color="#F8FAFC">'
             f'<Stack fit="EXPAND">{core}</Stack></Container></Positioned>')
    # 图注：框宽给到插图与右栏之间，否则长说明会折行、被 26px 的框高裁掉第二行
    b.append(txt(f"插图与 example-{p['id']}.png 同一坐标、同一比例",
                 ILL_X, ill_y + ILL_H + 4, 600, 28, 22, C["muted"], FB))
    # 右侧说明
    ax = 620
    b.append(rect(ax, ill_y - 12, W - M - ax + 12, ILL_H + 24, C["band"], 16, C["edge"]))
    b.append(txt("这一页的示例", ax + 24, ill_y + 6, W - M - ax - 48, 32, 26, C["ink"], FH))
    ay = ill_y + 52
    for s in p["aside"]:
        b.append(txt(s, ax + 24, ay, W - M - ax - 48, 40, 24, C["body"], FB))
        ay += 46
    b.append(txt(f"核心子树 {n_core} 行 · 完整示例第 4–{3 + n_core} 行",
                 ax + 24, ay + 6, W - M - ax - 48, 32, 22, C["faint"], FB))
    # 代码块
    cy = ill_y + ILL_H + 80
    b.append(txt(f"示例代码 · 印刷 {n_core} 行 = 完整 DSL 的第 4–{3 + n_core} 行"
                 f"，省略的 6 行为 Snapshot 根与 400×240 外层容器",
                 CODE_X, cy - 42, CODE_W, 30, 24, C["ink"], FH))
    b.append(rect(CODE_X, cy, CODE_W, code_h, C["codebg"], 12))
    for i, ln in enumerate(printed):
        col = C["codecmt"] if ln == OMISSION_MARK else C["codefg"]
        b.append(txt(ln, CODE_X + 20, cy + 12 + i * CODE_PITCH, CODE_W - 40, CODE_PITCH,
                     20, col, FMONO))
    b.append(rect(CODE_X, cy, 6, code_h, C["accent"]))
    # 页脚
    b.append(rect(M, FOOTER_RULE, W - 2 * M, 1, C["edge"]))
    b.append(txt("Snapshot DSL 入门手册", M, FOOTER_RULE + 16, 500, 30, 22, C["faint"], FB))
    b.append(txt(f"{p['section']}", W - M - 500, FOOTER_RULE + 16, 500, 30, 22, C["faint"],
                 FB, align="RIGHT"))
    return (f'<Snapshot type="png">\n<Container width="{W}" height="{H}" color="{C["page"]}">'
            f'<Stack fit="EXPAND">{"".join(b)}</Stack></Container>\n</Snapshot>\n')


def xml_escape(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def xml_unescape(s: str) -> str:
    return s.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")


def main() -> None:
    ver = sys.argv[1] if len(sys.argv) > 1 else "v1"
    d = BASE / DRAFTS
    d.mkdir(parents=True, exist_ok=True)
    meta = []
    for i in ("01", "02", "03", "04"):
        lines = example_dsl(i)
        dsl = "\n".join(lines) + "\n"
        (d / f"a17-example-{i}-{ver}.snapshot").write_text(dsl, encoding="utf-8")
        core_lines = CORE[i].split("\n")
        meta.append({
            "example_id": f"example-{i}",
            "page": f"handbook-{i}",
            "complete_dsl": f"example-{i}.snapshot",
            "lines_total": len(lines),
            "core_line_range_1based": [4, 3 + len(core_lines)],
            "core_line_count": len(core_lines),
            "printed_line_count": len(core_lines),
            "omission_marker": OMISSION_MARK,
        })
        print(f"example-{i}: total {len(lines)} lines, core lines 4-{3 + len(core_lines)}")

    for p in PAGES:
        dsl = page_dsl(p)
        (d / f"a17-handbook-{p['id']}-{ver}.snapshot").write_text(dsl, encoding="utf-8")
        print(f"handbook-{p['id']} bytes={len(dsl.encode())}")

    # 排版自检：正文/标注是否单行放得下、代码块是否越过页脚
    for p in PAGES:
        core_lines = len(CORE[p["core"]].split("\n"))
        printed = core_lines + 2
        y = 248 + n_lines(p["lead"], 24, W - 2 * M) * 34 + 20
        bw = W - 2 * M - 28
        for s in p["bullets"]:
            nl = n_lines(s, 24, bw)
            assert nl == 1, f"第 {p['id']} 页要点需 {nl} 行，请缩短：{s[:30]}…"
            y += BULLET_PITCH_1
        ill_y = y + 46
        cy = ill_y + ILL_H + 80
        code_h = printed * CODE_PITCH + 24
        assert cy + code_h <= FOOTER_RULE - 12, (
            f"第 {p['id']} 页代码块底部 {cy + code_h} 越过页脚 {FOOTER_RULE}")
        print(f"  第 {p['id']} 页：要点到 {y}，插图 {ill_y}–{ill_y + ILL_H}，"
              f"代码 {cy}–{cy + code_h}（{printed} 行）")

    (d / f"examples-meta-{ver}.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2),
                                                 encoding="utf-8")


if __name__ == "__main__":
    main()