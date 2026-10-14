"""A17 - the four teaching examples, defined exactly once.

`core(i)` returns the single Node tree that is (a) rendered standalone at 400x240,
(b) drawn at 1:1 inside the handbook page, and (c) printed as code. All three come from
the same object, so the printed snippet, the illustration and the standalone render
cannot drift apart. `code_text(i)` returns the exact DSL text of that subtree.

Text positions are computed from measure.py's calibrated advance model instead of being
guessed: fit_audit.py walks this same tree and reports any text box that leaves the
400x240 canvas, crosses a card edge, or lands on another text box.
"""
from __future__ import annotations

import sys
from pathlib import Path

RUN_DIR = Path(__file__).resolve().parents[1]          # tmp/<run_id>/
sys.path.insert(0, str(RUN_DIR / "_suite" / "scripts"))
sys.path.insert(0, str(RUN_DIR / "A17"))

from snap import (  # noqa: E402
    C, BackdropFilter, ClipRRect, Container, Expanded, ImageFiltered, Node, Positioned,
    Raw, Row, Snapshot, Spacer, Stack, Text, num,
)
from measure import text_width  # noqa: E402

SANS = "Noto Sans CJK SC"
MONO = "Noto Sans Mono CJK SC"
INK, INK2, INK3 = "#16233A", "#42536E", "#78879C"
RED = "#B3261E"
BLUE, ORANGE, GREEN, VIOLET = "#2B5BD7", "#E0913B", "#1F8A5F", "#7A4FD3"
PANEL, EDGE = "#F2F5FA", "#D3DBE8"

EX_W, EX_H = 400, 240
PAD = 24


def W(text, size, mono=False):
    return text_width(text, size, mono=mono)


def T(text, size, color, font=SANS, **extra):
    return Node("Text", {"fontSize": num(size), "color": color, "fontFamily": font,
                         **extra}, [], text)


def P(child, x, y, w=None):
    at = {"left": num(x), "top": num(y)}
    if w is not None:
        at["width"] = num(w)
    return Node("Positioned", at, [child])


def box(x, y, w, h, **attrs):
    return P(C(width=num(w), height=num(h), **attrs), x, y)


def sizing():
    return C(width=num(EX_W), height=num(EX_H))


# ---------------------------------------------------------------- example 1
REQ1, REQ2 = "POST /snapshot", "text/plain"
RES1, RES2 = "200 image/png", "响应体就是图片字节"
ERR_LEAD, ERR_BODY = "出错才有", "{code, message, requestId}"
NOTE = "同一份文本：请求体 = .snapshot"
TAIL = "左边发出去，右边拿回来"
CARD_W, CARD_H, CARD_Y = 158, 78, 28


def core_1():
    """请求契约：一段 UTF-8 文本进、一张图片出，只有失败才走 JSON。"""
    lx, rx = PAD, EX_W - PAD - CARD_W
    gap_l, gap_r = lx + CARD_W, rx
    err_x = PAD + W(ERR_LEAD, 16) + 6
    return Stack(
        sizing(),
        box(lx, CARD_Y, CARD_W, CARD_H, color=PANEL, borderRadius="10",
            border=f"1 SOLID {EDGE}"),
        box(rx, CARD_Y, CARD_W, CARD_H, color=PANEL, borderRadius="10",
            border=f"1 SOLID {EDGE}"),
        box(gap_l + 6, CARD_Y + CARD_H / 2 - 4, gap_r - gap_l - 12, 8,
            color=BLUE, borderRadius="4"),
        P(T(REQ1, 18, INK, MONO), lx + 14, CARD_Y + 14),
        P(T(REQ2, 16, INK3, MONO), lx + 14, CARD_Y + 42),
        P(T(RES1, 18, GREEN, MONO), rx + 14, CARD_Y + 14),
        P(T(RES2, 16, INK2, SANS), rx + 14, CARD_Y + 42),
        P(T(ERR_LEAD, 16, RED, SANS), PAD, 132),
        P(T(ERR_BODY, 16, RED, MONO), err_x, 132),
        box(PAD, 162, EX_W - 2 * PAD, 1, color=EDGE),
        P(T(NOTE, 18, INK, SANS), PAD, 176),
        P(T(TAIL, 16, INK3, SANS), PAD, 206),
        alignment="TOP_LEFT", clipBehavior="HARD_EDGE")


# ---------------------------------------------------------------- example 2
ROW_Y, ROW_H, BAR_Y = 96, 40, 158
LAB1, LAB2 = "Expanded 占剩余宽度", "352 里的 1/4"


def core_2():
    """尺寸来自根布局容器，不是 Snapshot 属性；Row + Expanded + Spacer 分配宽度。"""
    inner = EX_W - 2 * PAD
    return Stack(
        sizing(),
        P(T("Snapshot 上没有 width/height", 18, INK, MONO), PAD, 24),
        P(T("尺寸来自下面的 400×240 容器", 16, INK3, SANS), PAD, 52),
        P(Row(Expanded(Container(color=BLUE, borderRadius="8", height=num(ROW_H)),
                        flex=1),
              Container(width="12"),
              Expanded(Container(color=ORANGE, borderRadius="8", height=num(ROW_H)),
                        flex=2),
              Container(width="12"),
              Expanded(Container(color=GREEN, borderRadius="8", height=num(ROW_H)),
                        flex=1),
              mainAxisSize="MAX", crossAxisAlignment="START"), PAD, ROW_Y, inner),
        box(PAD, BAR_Y, inner, 48, color=VIOLET, borderRadius="8"),
        P(Row(Container(width="14"),
              Text(LAB1, fontSize="16", color="#FFFFFF", fontFamily=SANS),
              Spacer(),
              Text(LAB2, fontSize="16", color="#FFFFFF", fontFamily=MONO),
              Container(width="14"),
              mainAxisSize="MAX", crossAxisAlignment="CENTER"), PAD, BAR_Y + 16, inner),
        P(T("flex 1 : 2 : 1", 16, INK2, MONO), PAD, 214),
        alignment="TOP_LEFT", clipBehavior="HARD_EDGE")


# ---------------------------------------------------------------- example 3
SQ, GAP = 96, 28
L1, L2, L3 = "重叠处更深", "两层各 80", "#RRGGBBAA"
RICH_A = "<Row> 与 & 保持原样"
RICH_D = "同一行"
RICH_NOTE = "CDATA 里的尖括号不转义"


def core_3():
    """尾部 alpha、CDATA 与富文本：8 位颜色是 #RRGGBBAA，尖括号不会被解码成实体。"""
    ax, ay = PAD, 22
    bx, by = PAD + GAP, 22 + GAP
    tx = PAD + SQ + GAP + 12
    return Stack(
        sizing(),
        P(C(width=num(SQ), height=num(SQ), color="#E23B3B80", borderRadius="8"), ax, ay),
        P(C(width=num(SQ), height=num(SQ), color="#2B5BD780", borderRadius="8"), bx, by),
        P(T(L1, 16, INK2, SANS), tx, ay + 2),
        P(T(L2, 16, INK2, SANS), tx, ay + 26),
        P(T(L3, 16, BLUE, MONO), tx, ay + 50),
        P(T("alpha 写在末尾", 16, INK, SANS), PAD, 150),
        box(PAD, 174, EX_W - 2 * PAD, 1, color=EDGE),
        P(Node("Text", {"fontSize": "18", "color": INK, "fontFamily": MONO},
               [Raw(RICH_A, cdata=True),
                Node("Text", {"color": GREEN, "fontStyle": "BOLD"}, [], "绿"),
                Raw(" · "),
                Node("Text", {"color": ORANGE, "fontStyle": "BOLD"}, [], "橙"),
                Raw(RICH_D)]), PAD, 184),
        P(T(RICH_NOTE, 16, INK3, SANS), PAD, 212),
        alignment="TOP_LEFT", clipBehavior="HARD_EDGE")


# ---------------------------------------------------------------- example 4
CARD_W2, CARD_H2, CARD_Y2 = 150, 96, 20
STRIPE_H = 172
B_LABEL, B_NOTE = "BackdropFilter", "字清楚，背景糊"
I_LABEL, I_NOTE = "ImageFiltered", "连字一起糊"
CROP_NOTE = "裁剪决定效果停在哪里"


def core_4():
    """背景滤镜糊“已经画好的背景”，子树滤镜糊“子树自己”；范围由裁剪决定。"""
    cols = [BLUE, ORANGE, GREEN, VIOLET, "#D4457A"]
    lx, rx = PAD, EX_W - PAD - CARD_W2

    def card():
        return C(width=num(CARD_W2), height=num(CARD_H2), color="#FFFFFFCC",
                 borderRadius="16", border=f"2 SOLID {INK}")

    return Stack(
        sizing(),
        # stripes stop above the closing note so that line never sits on colour
        *[P(C(width="16", height=num(STRIPE_H), color=cols[i % 5]), num(i * 40), "0")
          for i in range(10)],
        P(ClipRRect(BackdropFilter(card(), sigmaX="6", sigmaY="6", tileMode="CLAMP"),
                    borderRadius="16", clipBehavior="ANTI_ALIAS"), lx, CARD_Y2),
        P(T(B_LABEL, 17, INK, MONO), lx + 14, CARD_Y2 + 26),
        P(T(B_NOTE, 16, INK2, SANS), lx + 14, CARD_Y2 + 50),
        P(ClipRRect(ImageFiltered(
            Stack(C(width=num(CARD_W2), height=num(CARD_H2)),
                  card(),
                  T(I_LABEL, 17, INK, MONO),
                  alignment="CENTER", clipBehavior="NONE"),
            sigmaX="6", sigmaY="6", tileMode="CLAMP"),
            borderRadius="16", clipBehavior="ANTI_ALIAS"), rx, CARD_Y2),
        P(T(I_NOTE, 16, INK2, SANS), rx + 14, CARD_Y2 + CARD_H2 + 12),
        P(T(CROP_NOTE, 18, INK, SANS), PAD, 188),
        alignment="TOP_LEFT", clipBehavior="HARD_EDGE")


CORES = {1: core_1, 2: core_2, 3: core_3, 4: core_4}

# Art-local rectangles where a BackdropFilter reads the layer behind it. Only these can
# paint differently between the standalone example and the page, because the enclosing
# canvas is not the same size; verify.py uses them to bound the allowed difference.
FILTER_REGIONS = {4: [(20, 16, 178, 120)]}

TITLES = {
    1: "真实调用契约：文本进、图片出",
    2: "尺寸来自布局，不是属性",
    3: "尾部 alpha、CDATA 与富文本",
    4: "背景滤镜 ≠ 子树滤镜",
}

PURPOSE = {
    1: "让读者知道一次请求到底发什么、拿什么回来、错了怎么看",
    2: "让读者明白画布尺寸从哪来，以及 Row/Expanded/Spacer 怎样分宽度",
    3: "让读者避开 8 位颜色顺序、实体解码与首尾空格三个常见误解",
    4: "让读者分清两种模糊的作用范围，并养成看图自检的习惯",
}


def core(i):
    return CORES[i]()


def file_lines(i):
    """The exact lines of example-NN.snapshot: the core nested in root + bounded box.

    The handbook prints these lines rather than the level-0 rendering of the core, so
    a reader who opens the delivered .snapshot finds the same text at the same 1-based
    line number the page cites.
    """
    return example_doc(i).render().split("\n")


def code_text(i):
    return file_lines(i)


def example_doc(i):
    """The standalone 400x240 render. The white background is deliberate: on the
    handbook page the same subtree sits on a #FFFFFF card, and a BackdropFilter blurs
    whatever is already painted - a transparent canvas would blur to a different pixel
    value than a white one, which would break the 1:1 illustration identity."""
    return Snapshot(Container(core(i), width=num(EX_W), height=num(EX_H)),
                    type="png", background="#FFFFFF")


if __name__ == "__main__":
    for i in (1, 2, 3, 4):
        ls = code_text(i)
        print(f"=== example {i}: {len(ls)} lines, maxlen "
              f"{max(len(l) for l in ls)} ===")
        for k, l in enumerate(ls, 1):
            print(f"{k:>3}|{len(l):>3}| {l}")
