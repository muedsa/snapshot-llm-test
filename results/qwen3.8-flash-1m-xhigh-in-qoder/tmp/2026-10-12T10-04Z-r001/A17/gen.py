"""A17 - four 1200x1600 handbook pages built from the same example nodes.

The illustration on each page embeds core(i) - the very object that produces the
standalone 400x240 example - so the printed snippet, the illustration and the
standalone render all come from one Node tree instead of being re-typed.

Layout is measured, not guessed: every text block reserves the height its wrapped
rows will actually take (advance model calibrated by probe-mono.png: CJK 1.00em,
Latin in the mono body font 0.50em, real line pitch 1.46em), and build_page asserts
the page body ends above the footer rule.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
sys.path.insert(0, str(ROOT / "tmp" / RUN / "_suite" / "scripts"))
sys.path.insert(0, str(ROOT / "tmp" / RUN / "A17"))

from snap import (  # noqa: E402
    C, Node, Positioned, Snapshot, Stack, hline, num,
)
# one metric source for the page, the examples and both audits
from measure import ink_h, text_width, wrap_rows  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "ex", ROOT / "tmp" / RUN / "A17" / "examples.py")
ex = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ex)

TASK = "A17"
TMP_DIR = ROOT / "tmp" / RUN / TASK

W, H, M = 1200, 1600, 48
CW = W - 2 * M                       # 1104 content width
RIGHT = W - M
INK, INK2, INK3 = "#16233A", "#42536E", "#78879C"
PAPER, CARD, EDGE = "#F6F7FA", "#FFFFFF", "#DCE2EC"
CODE_BG, CODE_FG, CODE_CM, CODE_EL = "#16233A", "#E8EEF8", "#8FD3A6", "#93AECF"
BLUE, ORANGE, GREEN, VIOLET = "#2B5BD7", "#C97A22", "#1F8A5F", "#7A4FD3"
SANS = "Noto Sans CJK SC"
MONO = "Noto Sans Mono CJK SC"

EX_W, EX_H = 400, 240
CODE_SIZE, CODE_PITCH = 20, 27
FOOTER_Y = 1512
LIMIT = FOOTER_Y - 14                # body copy must clear the footer rule

FIG_NOTE = "插图由本页 DSL 构件直接画成，未嵌入预渲染整图。"
BOXES: list[dict] = []


# ---------------------------------------------------------------- primitives
def rect(x, y, w, h, *, colour=None, radius=None, border=None, role="rect"):
    BOXES.append({"role": role, "x": x, "y": y, "w": w, "h": h, "size": 0,
                  "text": "", "kind": "rect"})
    a = {"width": num(w), "height": num(h)}
    if colour:
        a["color"] = colour
    if radius is not None:
        a["borderRadius"] = num(radius)
    if border:
        a["border"] = border
    return Positioned(C(**a), left=num(x), top=num(y))


def txt(x, y, w, text, size, colour, *, font=SANS, bold=False, align="LEFT",
        role=""):
    """One absolutely positioned, width-constrained Text; returns (node, ink height).

    Copy that mentions markup characters (& < >) goes out as Raw/CDATA spans: the
    parser does not decode entities, so escaping them here would print "&amp;" on the
    page - exactly the misconception page 3 teaches against.
    """
    rows = wrap_rows(text, size, w, mono=(font == MONO))
    BOXES.append({"role": role, "x": x, "y": y, "w": w, "h": ink_h(rows, size),
                  "size": size, "text": text[:30], "kind": "text", "rows": rows})
    a = {"fontSize": num(size), "color": colour, "fontFamily": font,
         "textAlign": align, "softWrap": "true"}
    if bold:
        a["fontStyle"] = "BOLD"
    if any(ch in text for ch in "&<>"):
        kids = [Node("Raw", [], [], chunk, kind == "cdata")
                for kind, chunk in raw_chunks(text)]
        body = Node("Text", a, kids)
    else:
        body = Node("Text", a, [], text)
    return Node("Positioned", {"left": num(x), "top": num(y), "width": num(w)},
                [body]), ink_h(rows, size)


def raw_chunks(line):
    """Split a source line so no CDATA section ever contains ']]>'."""
    parts = line.split("]]>")
    out = []
    for k, p in enumerate(parts):
        if p:
            out.append(("cdata", p))
        if k < len(parts) - 1:
            out.append(("plain", "]]"))
            out.append(("cdata", ">"))
    return out or [("cdata", "")]


def code_line(x, y, w, line, *, colour=CODE_FG, role="code"):
    """Print one DSL source line verbatim: every chunk goes through Raw/CDATA."""
    rows = wrap_rows(line, CODE_SIZE, w, mono=True)
    BOXES.append({"role": role, "x": x, "y": y, "w": w, "h": ink_h(rows, CODE_SIZE),
                  "size": CODE_SIZE, "text": line[:30], "kind": "code", "rows": rows})
    children = [Node("Raw", [], [], chunk, kind == "cdata")
                for kind, chunk in raw_chunks(line)]
    return Node("Positioned", {"left": num(x), "top": num(y), "width": num(w)},
                [Node("Text", {"fontSize": num(CODE_SIZE), "color": colour,
                               "fontFamily": MONO, "textAlign": "LEFT",
                               "softWrap": "true"}, children)])


def heading_line(x, y, w, numeral, title, colour):
    els = [rect(x, y + 4, 5, 26, colour=colour, radius=2, role="heading-bar")]
    el, _ = txt(x + 17, y, w - 17, f"{numeral}、{title}", 28, INK, bold=True,
                role="heading")
    els.append(el)
    return els


# ---------------------------------------------------------------- snippets
RANGES = {   # 1-based line numbers inside example-NN.snapshot, the delivered file
    1: [(1, 6), (14, 16), (20, 22)],
    2: [(1, 2), (11, 18), (29, 33)],
    3: [(1, 2), (5, 6), (8, 9), (26, 33)],
    4: [(1, 2), (35, 41), (48, 51)],
}


def snippet(i):
    lines = ex.code_text(i)
    out, meta = [], []
    for k, (s, e) in enumerate(RANGES[i]):
        seg = lines[s - 1:e]
        meta.append({"from_line": s, "to_line": e, "verbatim": seg})
        out.extend(("code", l) for l in seg)
        if k + 1 < len(RANGES[i]):
            out.append(("elision", "……省略外层包装……"))
    return out, meta


# ---------------------------------------------------------------- page copy
COPY = {
    1: {
        "goal": "看懂一次真实调用：发出去的是什么，拿回来的是什么，出错了看什么",
        "points": [
            ("请求体是 UTF-8 纯文本，不是 JSON",
             "Content-Type: text/plain; charset=utf-8，把 DSL 原文当字节流发出去"),
            ("200 的响应体直接是图片字节",
             "Content-Type 为 image/png，不要按 JSON 去 parse 它"),
            ("只有失败才返回 JSON",
             "{code, message, requestId}，requestId 用来向服务方定位那一次请求"),
        ],
        "hint": "左框是发出去的，右框是拿回来的，中间蓝杠就是这一次调用。",
        "myths": [
            "把 DSL 当 HTML 写：它不是网页，浏览器标签与 CSS 选择器在这里没有意义。",
            "以为成功响应也带 JSON 外壳：200 时拿到的是图片字节，解析必然报错。",
        ],
        "check": [
            "用 text/plain 发一次，确认落盘文件能被图片查看器打开",
            "故意写错一个标签名，记下返回的 code 与 requestId",
            "把请求体原样存成 .snapshot，再次请求应得到同一张图",
        ],
    },
    2: {
        "goal": "搞清画布尺寸从哪来，以及一行里的宽度按什么规则分",
        "points": [
            ("Snapshot 标签上没有 width / height",
             "根标签只接受 background / debug / type，写别的会被静默忽略"),
            ("画布尺寸来自最外层有界容器",
             "给它 400×240，输出图片就是这个大小"),
            ("Expanded / Spacer 必须是 Flex 的直接子节点",
             "隔一层就失效；flex 数字决定剩余宽度的分配比例"),
        ],
        "hint": "三条色块是同一条 Row 里的 flex 1:2:1，隔两个 12px 容器。",
        "myths": [
            "在 Snapshot 上写宽度后画面塌了：真正缺的是根容器尺寸，不是根标签属性。",
            "把 Expanded 塞进 Container：它不是 Flex 的直接子节点，布局会报错或被忽略。",
        ],
        "check": [
            "删掉根容器的宽高，观察报错或空白",
            "把一个 flex 从 1 改成 3，确认比例随之变化",
            "在 Row 里插入 Spacer，看两段文字是否被推到两端",
        ],
    },
    3: {
        "goal": "避开尾部 alpha、实体解码与首尾空格三个高频误解",
        "points": [
            ("8 位颜色是 #RRGGBBAA，alpha 在末尾",
             "50% 不透明的红是 #FF000080，不是 #80FF0000"),
            ("解析器不解码 HTML 实体",
             "写 &lt; 就原样印出这 4 个字符，要显示尖括号请改用 CDATA"),
            ("普通文本节点会被 trim",
             "要保留首尾空格改用 Raw；嵌套 Text 只作行内 Span，与周围共用基线"),
        ],
        "hint": "两块方块各带 alpha 80，重叠处比任一块都深；最后一行原样印出尖括号。",
        "myths": [
            "把 #33FFFFFF 当成 20% 白：末尾 FF 表示完全不透明，前缀反而不合法。",
            "用 &amp; 转义 &：解析器不解码，屏幕上看到的就是实体名本身。",
        ],
        "check": [
            "把 alpha 从开头移到末尾再渲染，比较透明度",
            "用 CDATA 印一行含 < > & 的文字，确认没有实体残留",
            "行内混排两种颜色的 Text，检查基线是否齐平",
        ],
    },
    4: {
        "goal": "分清两种模糊各自糊什么，并把看图自检变成默认动作",
        "points": [
            ("BackdropFilter 糊已经画好的背景",
             "它自己什么都不画，子节点叠在模糊结果之上，所以文字仍然清晰"),
            ("ImageFiltered 糊整棵子树",
             "子树里的色块、文字、描边会被一起模糊"),
            ("作用范围由外层裁剪决定",
             "Stack 默认 HARD_EDGE，滤镜柔化会外溢，用 ClipRRect / ClipOval 圈住"),
        ],
        "hint": "左卡字清楚、右卡连字一起糊，两张卡的 sigma 都是 6。",
        "myths": [
            "以为 BackdropFilter 会糊自己的子节点：不会，子节点是叠在结果上面的。",
            "以为换滤镜就能自动限定区域：范围只由外层裁剪决定，去掉裁剪就溢出去。",
        ],
        "check": [
            "同一场景分别用两种滤镜渲染，比较文字是否变糊",
            "去掉外层 ClipRRect，观察柔化是否溢到相邻区域",
            "最终图放大看局部、缩略看整体，确认没有遮挡与裁切",
        ],
    },
}


def fig_h_total(i):
    """Card height: 12 pad + label 21 + 8 + art 240 + 12 + hint + 8 + note + 12."""
    c = COPY[i]
    hint_h = ink_h(wrap_rows("看图：" + c["hint"], 20, EX_W, mono=False), 20)
    note_h = ink_h(wrap_rows(FIG_NOTE, 20, EX_W, mono=False), 20)
    return 293 + hint_h + 8 + note_h + 12, hint_h, note_h


def build_page(i):
    c = COPY[i]
    els = []
    els.append(rect(M, M, CW, 128, colour=CARD, radius=16, border=f"1 SOLID {EDGE}",
                    role="header-card"))
    el, _ = txt(M + 24, M + 16, CW - 48, f"Snapshot 入门手册 · 第 {i} 页 / 共 4 页",
                20, INK3, font=MONO, role="page-label")
    els.append(el)
    el, h_t = txt(M + 24, M + 42, CW - 48, ex.TITLES[i], 40, INK, bold=True, role="title")
    els.append(el)
    el, h_g = txt(M + 24, M + 42 + h_t + 6, CW - 48, "本页目标：" + c["goal"], 24,
                  INK2, role="goal")
    els.append(el)
    assert M + 42 + h_t + 6 + h_g <= M + 128, (i, "header text overflows the card")

    y = M + 128 + 34

    # 一、示例渲染结果（左）+ 本页三要点（右）
    els += heading_line(M, y, CW, "一", "示例的实际渲染结果与本页要点", GREEN)
    y += 40
    fig_x, fig_w = M, EX_W + 32
    card_h, hint_h, note_h = fig_h_total(i)
    els.append(rect(fig_x, y, fig_w, card_h, colour=CARD, radius=14,
                    border=f"1 SOLID {EDGE}", role="fig-card"))
    el, _ = txt(fig_x + 16, y + 12, fig_w - 32, f"example-{i:02d}.png · 400×240 · 1:1",
                20, INK3, font=MONO, role="fig-label")
    els.append(el)
    els.append(Positioned(ex.core(i), left=num(fig_x + 16), top=num(y + 41)))
    el, _ = txt(fig_x + 16, y + 293, EX_W, "看图：" + c["hint"], 20, INK2, role="fig-hint")
    els.append(el)
    el, _ = txt(fig_x + 16, y + 293 + hint_h + 8, EX_W, FIG_NOTE, 20, INK3,
                role="fig-note")
    els.append(el)
    del note_h

    rx = fig_x + fig_w + 30
    rw = RIGHT - rx
    yy = y
    for t, d in c["points"]:
        els.append(rect(rx, yy + 4, 4, 24, colour=BLUE, radius=2, role="point-bar"))
        el, ht = txt(rx + 16, yy, rw - 16, t, 26, INK, bold=True, role="point-t")
        els.append(el)
        el, hd = txt(rx + 16, yy + ht + 4, rw - 16, d, 24, INK2, role="point-d")
        els.append(el)
        yy += ht + 4 + hd + 18
    y += max(card_h, yy - y - 18) + 12

    # 二、示例关键片段
    els += heading_line(M, y, CW, "二", "示例关键片段（完整 DSL 见 example-NN.snapshot）",
                        ORANGE)
    y += 40
    lines, meta = snippet(i)
    n_printed = sum(1 for k, _ in lines if k == "code")
    inner_w = CW - 44
    row_h = [wrap_rows(l, CODE_SIZE, inner_w, mono=True) if k == "code" else 1
             for k, l in lines]
    body_h = sum(CODE_PITCH * r for r in row_h)
    els.append(rect(M, y, CW, body_h + 46, colour=CODE_BG, radius=14, role="code-card"))
    el, _ = txt(M + 22, y + 12, inner_w,
                f"example-{i:02d}.snapshot 第 "
                + "、".join(str(m["from_line"]) if m["from_line"] == m["to_line"]
                           else f"{m['from_line']}–{m['to_line']}" for m in meta)
                + f" 行 · 实际印出 {n_printed} 行代码", 20, CODE_CM, font=MONO,
                role="code-cap")
    els.append(el)
    cy = y + 12 + ink_h(1, CODE_SIZE) + 8
    for (kind, l), r in zip(lines, row_h):
        els.append(code_line(M + 22, cy, inner_w, l) if kind == "code" else
                   code_line(M + 22, cy, inner_w, l, colour=CODE_EL, role="elision"))
        cy += CODE_PITCH * r
    y += body_h + 46 + 12

    # 三、常见误解与动手核对（两栏）
    els += heading_line(M, y, CW, "三", "常见误解与动手核对", VIOLET)
    y += 38
    col_w = (CW - 40) / 2
    lx, rxx = M, M + col_w + 40
    el, _ = txt(lx, y, col_w, "容易踩的坑", 24, VIOLET, bold=True, role="col-h")
    els.append(el)
    el, _ = txt(rxx, y, col_w, "动手核对", 24, GREEN, bold=True, role="col-h")
    els.append(el)
    ly = ry = y + 34
    for s in c["myths"]:
        els.append(rect(lx + 2, ly + 9, 10, 10, colour=VIOLET, radius=5, role="bullet"))
        el, hh = txt(lx + 24, ly, col_w - 26, s, 24, INK2, role="myth")
        els.append(el)
        ly += hh + 12
    for s in c["check"]:
        els.append(rect(rxx + 3, ry + 9, 13, 13, colour=None, radius=2,
                        border=f"2 SOLID {GREEN}", role="checkbox"))
        el, hh = txt(rxx + 26, ry, col_w - 26, s, 24, INK2, role="check")
        els.append(el)
        ry += hh + 12
    y = max(ly, ry) - 12 + 6

    els.append(hline(M, RIGHT, FOOTER_Y, 1, EDGE))
    el, _ = txt(M, FOOTER_Y + 10, 760, f"第 {i} 页 · {ex.TITLES[i]}", 20, INK3,
                role="foot-l")
    els.append(el)
    el, _ = txt(RIGHT - 200, FOOTER_Y + 10, 200, f"{i} / 4", 20, INK3, font=MONO,
                align="RIGHT", role="foot-r")
    els.append(el)

    assert 8 <= n_printed <= 18, (i, n_printed)
    assert y <= LIMIT, (i, round(y, 1), LIMIT)
    return els, {"printed_lines": n_printed, "code_rows": sum(row_h),
                 "ranges": [[m["from_line"], m["to_line"]] for m in meta],
                 "body_bottom": round(y, 1)}


def page_doc(els):
    return Snapshot(Stack(C(width=num(W), height=num(H), color=PAPER), *els,
                          alignment="TOP_LEFT", clipBehavior="HARD_EDGE"),
                    background=PAPER, type="png")


ap = argparse.ArgumentParser()
ap.add_argument("--ver", default="v001")
a = ap.parse_args()
TMP_DIR.mkdir(parents=True, exist_ok=True)

info = {}
for i in (1, 2, 3, 4):
    els, meta = build_page(i)
    info[str(i)] = meta
    (TMP_DIR / f"{a.ver}-handbook-{i:02d}.snapshot").write_text(
        page_doc(els).render() + "\n", encoding="utf-8")
    (TMP_DIR / f"{a.ver}-example-{i:02d}.snapshot").write_text(
        ex.example_doc(i).render() + "\n", encoding="utf-8")

print(json.dumps(info, ensure_ascii=False, indent=1))
json.dump({"boxes": BOXES}, (TMP_DIR / f"{a.ver}-boxes.json").open("w",
                                                                  encoding="utf-8"),
          ensure_ascii=False, indent=0)
