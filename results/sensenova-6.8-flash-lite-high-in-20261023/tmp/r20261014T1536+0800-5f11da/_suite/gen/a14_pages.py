"""A14 生成器：8 张 1200×630 讲座宣传卡，从 inputs/cards.json 参数化生成。

一套规则，不做逐条硬改
----------------------
所有内容槽位的坐标、字号、颜色都来自本文件的常量表。卡片之间唯一的差异来自
**数据本身触发的参数化规则**：

  1. 标题折行——从 TITLE_STEPS 最大档（48 px）起，按「CJK 逐字 / 拉丁按词」
     切 token 贪心折行，加行首禁则与寡行再平衡；所需行数 > 3 时逐档降到 36 px
     为止。字号只在 [36, 48] 内变，画布、安全边距、徽标、讲者、时间、页脚
     一律不动——题目禁止「通过全局缩小整图适配长标题」，本实现不动画布。
  2. 讲者折行——同一套折行函数，上限 2 行（题目「长讲者允许两行」）。
  3. 状态徽标——按状态表查前景色 / 底色 / 符号 / 文字，四条冗余通道区分。
  4. 取消卡——只在标题盒下方空档放一个注明标签，位置由标题实际行数算出，
     标题与时间照常完整显示，不灰底、不删卡。

三件必须先实测、不能靠假设的事，都靠一次探针渲染确认：

  * **文本里 & < > 怎么写**——K04 标题是 `A < B & C > D：不要把文本当成标签`。
    实测（req-a14-probe-layout-abdd1d 与 req-a14-escape-test-raw-6355ec）结论
    与直觉相反：服务**不解码** XML 实体，`&lt;` 会被原样显示成字面串；而裸
    `<` `>` `&` 直接写进 text 属性是 HTTP 200 且逐字正确的。所以 text 属性
    收原始字符，esc() 是恒等函数。
  * **全角标点宽度**——`“ ” —— ·` 在中日韩字体里按全角排，不是 0.47 em。
    低估会让 K08 的 29 字标题被误判成「一行装得下」，实际渲染溢出盒外被裁。
  * **状态符号不用文字字形**——✕/✓ 这类字形在指定字体里可能缺字，缺字会渲染成
    豆腐块。四个状态符号全部用几何容器画出，形状完全可控、无缺字风险。

折行结果一律「一行一个 `<Text>` 单行盒」输出，不依赖服务自己的自动折行：
每行盒高精确等于该字号的行高，既不裁切也不需要服务的换行行为配合。

用法（run_id 从脚本自身路径 tmp/<rid>/_suite/gen/ 推出，也可显式设
SNAPSHOT_RUN_ID 覆盖）：
  python -I a14_pages.py probe      # 探针渲染，验证不能靠假设的事
  python -I a14_pages.py checks     # 前置校验与转义核验，不发请求
  python -I a14_pages.py finals     # 8 张最终交付件
接触表由 a14_audit.py 生成，只作一致性辅助。
"""

from __future__ import annotations

import json
import os
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[4]
# run_id 可从脚本自身路径推出（tmp/<rid>/_suite/gen/…），无需外部传参；
# 显式设置 SNAPSHOT_RUN_ID 仍然优先。
os.environ.setdefault("SNAPSHOT_RUN_ID", HERE.parents[2].name)
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(HERE.parent))
import suite as S  # noqa: E402
import snap_client as C  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

TASK = "A14"
RID = S.run_id()
OUT, TMP = S.task_dirs(TASK)
CARDS_PATH = ROOT / "tasks" / "A14-content-stress-batch" / "inputs" / "cards.json"

# ---------------------------------------------------------------- 画布与槽位
W, H = 1200, 630          # 题目规定的卡面尺寸
SAFE = 40                 # 题目规定的安全边距
CX0, CX1 = 88, 1112       # 内容栏左右缘（安全边距内再留呼吸）
CW = CX1 - CX0            # 1024

HEADER_Y = 44             # 头部文字顶缘
HDR_SIZE = 20
ACCENT_RULE_W, ACCENT_RULE_H = 44, 3
ACCENT_RULE_GAP = 12
RULE1_Y = 104

TITLE_X = CX0
TITLE_Y = 140
WRAP_SLACK = 0.92        # 折行上限 = 盒宽 × 0.92，剩下的 8% 是估算误差预算
TITLE_W = 888             # 标题盒宽（内容栏减去徽标与 32 px 净距）
# 主动折行上限 = 盒宽 × 余量系数。盒子是 888，但折行点在 817：留出的 71 px 是
# 墨宽估算误差的预算。若折行点等于盒宽，估到 99% 的行只差一点就越界被裁。
TITLE_WRAP_LIMIT = round(TITLE_W * WRAP_SLACK)
TITLE_MAX_LINES = 3
TITLE_STEPS = [48, 46, 44, 42, 40, 38, 36]   # 下限 36：题目「标题字号不小于 36」
TITLE_LS = 1.0

BADGE_H = 48
BADGE_W = 104
BADGE_X = CX1 - BADGE_W   # 1008，右缘对齐内容栏
BADGE_Y0 = TITLE_Y        # 与标题同顶
BADGE_PAD = 18
SYM = 16                  # 徽标内符号尺寸
BADGE_TEXT_SIZE = 20

LABEL_Y = 396
LABEL_SIZE = 14
VALUE_Y = 424
SPEAKER_SIZE = 26
SPEAKER_X = CX0
SPEAKER_W = 888
SPEAKER_WRAP_LIMIT = round(SPEAKER_W * 0.94)   # 讲者同样留出估算余量
SPEAKER_MAX_LINES = 2
TIME_SIZE = 36
TIME_LS = 2.0

NOTE_W, NOTE_H = 168, 48
NOTE_X = CX1 - NOTE_W
NOTE_GAP = 24             # 标签顶缘距标题盒底
LABEL_CLEAR = 8           # 标签底缘距讲者标签行的最小净距

RULE2_Y = 522
FOOT_Y = 534
FOOT_SIZE = 14

# ---------------------------------------------------------------- 字体与度量
CJK = "Noto Sans CJK SC"
MONO = "Noto Sans Mono CJK SC"
LATIN_EM = 0.47      # A12 实测：Noto Sans CJK SC 里拉丁墨宽约 0.47 em
MONO_EM = 0.60       # A13 实测：等宽字 0.49–0.52 em，取 0.60 让盒宽估算偏保守
MONO_EM_TIGHT = 0.50  # 同一实测区间的中值，只用于**定位**（估算偏高会让右列偏左）
SPACE_EM = 0.28
MONO_SPACE_EM = 0.50
MIDDLE_DOT_EM = 0.67  # A13 实测
ORPHAN_RATIO = 0.35  # 末行估算宽度低于折行上限 35% 且行数 >1 时触发再平衡

CJK_RANGES = [(0x3000, 0x303F), (0x3400, 0x4DBF), (0x4E00, 0x9FFF),
              (0xF900, 0xFAFF), (0xFF00, 0xFFEF),
              (0x20000, 0x2A6DF), (0x2E800, 0x2EFFF)]
# 这些拉丁区标点在中日韩字体里按**全角**排。K08 标题含 “ ”（U+201C/201D），
# K07 标题含 ——（U+2014），K07 讲者含 ·（U+00B7）。低估它们会把 K08 的 29 字
# 标题误判成「一行装得下」，渲染时溢出标题盒被裁——这是必须先量出来的失败模式。
WIDE_PUNCT = {0x2010, 0x2011, 0x2012, 0x2013, 0x2014, 0x2015, 0x2018, 0x2019,
              0x201C, 0x201D, 0x201E, 0x201F, 0x2026, 0x2030, 0x2212, 0x2329,
              0x232A, 0x2E30, 0x2E31}
MIDDLE_DOT = {0x00B7, 0x2027}

# 行首禁则 + 标点粘连。本批数据真正会碰到：K03/K08 的「：」、K08 的「”」、
# K07 的「——」与讲者里的「·」。处理方式是「把上一行最后一个 token 挪下来」，
# 不是允许溢出行尾——溢出会撞安全边距，挪 token 只是让上一行短一点。
NO_LINE_START = "，。、；：！？）】》」』”’%》—–－～~…·/"
SP = " "                 # ASCII 空格（显式常量，避免字面量歧义）


def is_cjk(ch: str) -> bool:
    o = ord(ch)
    return any(a <= o <= b for a, b in CJK_RANGES)


def esc(text: str) -> str:
    """原样返回，不做任何转义。

    这是实测结论，不是推断。第一次探针 req-a14-probe-layout-abdd1d 把标题
    写成 `A &lt; B &amp; C &gt; D`，服务**不解码 XML 实体**，画面上就是字面
    `&lt;` `&amp;` `&gt;`；同一张探针里写成裸 `A < B & C > D` 的那条标签也同样
    被写成实体（因为当时走了本函数）。随后 req-a14-escape-test-raw-6355ec
    绕过本函数把裸字符直接写进 text 属性：HTTP 200，渲染为
    `A < B & C > D：不要把文本当成标签`，逐字正确。

    所以 text 属性必须收原始字符。唯一的例外是半角双引号 `"` 会截断属性，
    但本批 8 条文案里没有（K08 的弯引号是 U+201C/U+201D，不是 `"`），故不做
    处理；函数保留原名以免大面积改动调用点。
    """
    return text


def lh(size: float) -> int:
    """行高 = 1.45 × 字号（A12 实测饱和行距 1.40–1.44，取上界做安全预算）。"""
    return int(round(size * 1.45))


def char_em(ch: str, mono: bool = False, tight: bool = False) -> float:
    o = ord(ch)
    if is_cjk(ch) or o in WIDE_PUNCT:
        return 1.0
    if o in MIDDLE_DOT:
        return MIDDLE_DOT_EM
    if ch == " ":
        return MONO_SPACE_EM if mono else SPACE_EM
    if mono:
        return MONO_EM_TIGHT if tight else MONO_EM
    return LATIN_EM


def est_w(text: str, size: float, ls: float = 0.0, mono: bool = False,
          tight: bool = False) -> float:
    """单行墨宽估算。

    mono 默认用 MONO_EM（0.60，保守）——用于**盒宽**，盒越宽越安全。
    tight=True 换成 MONO_EM_TIGHT（0.50，贴近实测 0.49–0.52）——只用于
    **定位**，因为位置错了会让右列整体偏掉。两个口径不能混用。
    """
    return sum(size * char_em(c, mono, tight) + ls for c in text)


def tokenize(text: str) -> list[dict]:
    """折行原子：CJK 逐字，拉丁按词。空格不单独成 token，而是标在需要前置空格
    的 token 上——保证行尾不留空格、行首不吃空格。"""
    out: list[dict] = []
    i, n = 0, len(text)
    while i < n:
        ch = text[i]
        if ch == SP:
            i += 1
            continue
        if is_cjk(ch):
            out.append({"t": ch, "space": i > 0 and text[i - 1] == SP})
            i += 1
            continue
        j = i
        while j < n and not is_cjk(text[j]) and text[j] != " ":
            j += 1
        if j <= i:
            raise RuntimeError("tokenize 无法前进：i=%d ch=%r (U+%04X)"
                               % (i, ch, ord(ch)))
        out.append({"t": text[i:j], "space": i > 0 and text[i - 1] == " "})
        i = j
    return out


def line_w(toks: list[dict], size: float, ls: float) -> float:
    sw = size * SPACE_EM
    w = 0.0
    for k, tk in enumerate(toks):
        w += sum(size * char_em(c) + ls for c in tk["t"])
        if tk["space"] and k > 0:
            w += sw
    return w


def join(toks: list[dict]) -> str:
    out = []
    for k, tk in enumerate(toks):
        if tk["space"] and k > 0:
            out.append(" ")
        out.append(tk["t"])
    return "".join(out)


def greedy(toks: list[dict], size: float, ls: float, limit: float) -> list:
    """贪心折行：能塞下就塞，塞不下就换行。"""
    lines, cur = [], []
    for tk in toks:
        if cur and line_w(cur + [tk], size, ls) > limit:
            lines.append(cur)
            cur = [tk]
        else:
            cur = cur + [tk]
    if cur:
        lines.append(cur)
    return lines


def balanced(toks: list[dict], size: float, ls: float, limit: float,
             n_lines: int) -> list | None:
    """在**恰好 n_lines 行**内重排，最小化最宽行宽度。

    折点处不允许下一行以禁则字符开头。贪心只保证「装得下」，不保证均衡：
    K05 的 2 行分法会让第二行只剩「读性」两个字，这就是孤字尾行。在同一行数
    内枚举全部合规折点取最窄的一版，行末的落差会明显收窄。行数 ≤3、token 数
    ≤40，代价可忽略。找不到合规分法时返回 None。
    """
    if n_lines < 1 or len(toks) < n_lines:
        return None
    best = {"w": None, "lines": None}

    def rec(start: int, left: int, prefix: list, worst: float) -> None:
        if left == 1:
            w = line_w(toks[start:], size, ls)
            if w > limit:
                return
            m = w if w > worst else worst
            if best["w"] is not None and m >= best["w"]:
                return
            best["w"] = m
            best["lines"] = prefix + [list(toks[start:])]
            return
        cur = []
        for j in range(start, len(toks)):
            cur.append(toks[j])
            w = line_w(cur, size, ls)
            if w > limit:
                break
            if best["w"] is not None and w >= best["w"]:
                continue
            nxt = toks[j + 1] if j + 1 < len(toks) else None
            if nxt and nxt["t"] and nxt["t"][0] in NO_LINE_START:
                continue
            rec(j + 1, left - 1, prefix + [list(cur)],
                max(worst, w))

    rec(0, n_lines, [], 0.0)
    return best["lines"]


def no_line_start_fix(lines: list, size: float, ls: float,
                      limit: float) -> list:
    """行首禁则：某行以禁则字符开头时，把上一行最后一个 token 挪下来。"""
    out = [list(x) for x in lines]
    for k in range(1, len(out)):
        if out[k] and out[k - 1] and out[k][0]["t"] and \
                out[k][0]["t"][0] in NO_LINE_START and len(out[k - 1]) > 1:
            out[k] = [out[k - 1].pop()] + out[k]
    return out


def wrap(text: str, size: float, box_w: float, ls: float = 0.0,
         max_lines: int = 1, limit: float = None) -> tuple[list[str], int]:
    """折行主流程：求最少行数 → 在同一行数内取最均衡的折点。

    limit 是**主动折行的宽度上限**，故意小于盒宽 box_w：盒子是容器，折行点
    要提前，留出的差额是墨宽估算误差与安全余量。若把 limit 设成盒宽，估到 99%
    的行只差一点就越界，渲染时会被裁。默认 limit = box_w。

    最少行数下如果末行不足折行上限的 ORPHAN_RATIO（孤字尾行），会尝试多占用
    一行把它摊匀；摊匀不了就退回行数最少的那版。

    返回 (行文本列表, 实际使用的行数)。需要超过 max_lines 时行列表为空，
    由调用方降字号重试。
    """
    if limit is None:
        limit = box_w
    toks = tokenize(text)
    min_lines = len(greedy(toks, size, ls, limit))
    if min_lines > max_lines:
        return ([], min_lines)
    orphan = limit * ORPHAN_RATIO
    cands = [c for n in range(min_lines, max_lines + 1)
             if (c := balanced(toks, size, ls, limit, n)) is not None]
    if cands:
        for cand in cands:                     # 先要「末行不是孤字」
            if line_w(cand[-1], size, ls) >= orphan:
                return ([join(ln) for ln in cand], len(cand))
        return ([join(ln) for ln in cands[0]], len(cands[0]))   # 再要行数最少
    lines = no_line_start_fix(greedy(toks, size, ls, limit),
                              size, ls, box_w)
    return ([join(ln) for ln in lines], len(lines))


def fit_title(text: str) -> dict:
    """标题：从最大档起逐档降，取第一个能在 TITLE_MAX_LINES 内排下的字号。

    画布、安全边距与所有其他槽位都不动——降字号是唯一被允许的适配手段。
    """
    for size in TITLE_STEPS:
        lines, need = wrap(text, size, TITLE_W, TITLE_LS, TITLE_MAX_LINES,
                           TITLE_WRAP_LIMIT)
        if lines:
            widest = max(est_w(ln, size, TITLE_LS) for ln in lines)
            return {"size": size, "lines": lines, "need_at_this_size": need,
                    "lh": lh(size), "widest_line_px": round(widest, 1),
                    "widest_ratio": round(widest / TITLE_W, 4),
                    "wrap_limit_px": TITLE_WRAP_LIMIT,
                    "wrap_slack_vs_box_px": round(TITLE_W - TITLE_WRAP_LIMIT, 1),
                    "steps_tried": TITLE_STEPS[:TITLE_STEPS.index(size) + 1]}
    raise RuntimeError("标题在任何字号下都无法在 %d 行内排下" % TITLE_MAX_LINES)


def fit_speaker(text: str) -> dict:
    """讲者：允许 2 行；仍装不下就按 24 px 再试（题目「讲者字号不小于 22」）。"""
    for size in (SPEAKER_SIZE, 24):
        lines, need = wrap(text, size, SPEAKER_W, 0.0, SPEAKER_MAX_LINES,
                           SPEAKER_WRAP_LIMIT)
        if lines:
            return {"size": size, "lines": lines, "lh": lh(size),
                    "need_at_this_size": need,
                    "widest_line_px": round(
                        max(est_w(ln, size, 0.0) for ln in lines), 1),
                    "steps_tried": [SPEAKER_SIZE] if size == SPEAKER_SIZE
                    else [SPEAKER_SIZE, 24]}
    raise RuntimeError("讲者「%s」装不下" % text)


# ---------------------------------------------------------------- 调色板
PAPER = "#FFFFFF"
INK = "#0F172A"
INK2 = "#1E293B"
MUTED = "#64748B"
FAINT = "#94A3B8"
RULE = "#E2E8F0"
ACCENT = "#4338CA"        # 统一主色（全批唯一强调色）
ACCENT2 = "#6366F1"

# 状态体系：颜色 + 绘制符号 + 中文文字，三条冗余通道。
# 符号一律用几何容器画，不用 ✕/✓ 这类可能缺字的字形。
STATUS = {
    "开放": {"en": "OPEN", "fg": "#15803D", "bg": "#DCFCE7", "sym": "disc",
             "sym_note": "实心圆点：位置可用"},
    "满额": {"en": "FULL", "fg": "#B45309", "bg": "#FEF3C7", "sym": "block",
             "sym_note": "实心方块：额度已满"},
    "候补": {"en": "WAITLIST", "fg": "#1D4ED8", "bg": "#DBEAFE", "sym": "ring",
             "sym_note": "空心圆环：等待递补"},
    "取消": {"en": "CANCELLED", "fg": "#B91C1C", "bg": "#FEE2E2",
             "sym": "strike", "sym_note": "空心圆环加横杠：本场取消"},
}


def sym_nodes(kind: str, x: float, y: float, size: float,
              color: str) -> list[str]:
    """把状态符号画成几何节点，落在 (x,y,size,size) 的盒里。"""
    out = ['<Positioned left="%g" top="%g" width="%g" height="%g">' % (
        x, y, size, size)]
    if kind == "disc":
        out.append('<Container width="%g" height="%g" shape="CIRCLE" '
                   'color="%s" />' % (size, size, color))
    elif kind == "block":
        out.append('<Container width="%g" height="%g" borderRadius="2" '
                   'color="%s" />' % (size, size, color))
    elif kind == "ring":
        out.append('<Container width="%g" height="%g" shape="CIRCLE" '
                   'border="3 SOLID %s" />' % (size, size, color))
    elif kind == "strike":
        # 横杠比圆环略宽，做出「穿过」的感觉
        bw, bh = size + 6, 3
        out.append('<Container width="%g" height="%g" shape="CIRCLE" '
                   'border="3 SOLID %s" />' % (size, size, color))
        out.append('</Positioned>')
        out.append('<Positioned left="%g" top="%g" width="%g" height="%g">'
                   '<Container width="%g" height="%g" borderRadius="1.5" '
                   'color="%s" /></Positioned>' % (
                       x - 3, y + size / 2 - bh / 2, bw, bh, bw, bh, color))
        return out
    else:
        raise ValueError(kind)
    out.append('</Positioned>')
    return out


# ---------------------------------------------------------------- DSL 组件
def text(x, y, w, h, s, size, *, family=CJK, color=INK, style="", ls=0.0,
         align="CENTER_LEFT", mono=False):
    # mono 是「盒宽按等宽步进估」的标记，字体必须跟上来；不一致就会让右锚
    # 元素的整体右缘悄悄偏掉。直接在这里拦住，不留隐患。
    if mono and family != MONO:
        raise ValueError("mono=True 但 family=%s：估算与实际字体口径不一致"
                         % family)
    st = ' fontStyle="%s"' % style if style else ""
    lsa = ' letterSpacing="%g"' % ls if ls else ""
    return ('<Positioned left="%g" top="%g" width="%g" height="%g">'
            '<Container width="%g" height="%g" alignment="%s">'
            '<Text fontFamily="%s" fontSize="%g" color="%s"%s%s '
            'text="%s" /></Container></Positioned>' % (
                x, y, w, h, w, h, align, family, size, color, st, lsa,
                esc(s)))


PAD_X = 40.0  # 文字盒在墨宽之外多留的横向余量（盒透明，宽一点不会裁切）

# 右锚实测修正量（px）。来源不是估计，是**第一版渲染后的像素测量**：
# tmp/<rid>/A14/gen/batch-audit.json 的 right_anchors 给出 8 张卡的墨迹右缘，
# K01–K08 完全一致（date/time/label_time/footer_right 分别 -4/-4/-2/+3），
# 说明偏移只跟「字符串族 + 字号 + 字距」有关，与具体是哪张卡无关。
#
# 偏移的机制是 `text_r` 里 `盒中心 = x_right - ink_est/2`，而真实墨宽和 ink_est
# 差着几像素，这个差会被**减半**传导到锚点（见 text_r 的说明）；等宽字估算偏高、
# 混合串估算偏低，所以四个槽位的符号都不一样。这里直接把测出来的偏差补回去。
ANCHOR_SHIFT = {"date": 4.0, "time": 4.0, "label_time": 2.0, "footer_right": -3.0}


def text_r(x_right, y, h, s, size, ink_est, *, family=CJK, color=INK,
           style="", ls=0.0, pad=PAD_X, mono=False, shift=0.0):
    """墨迹右缘对齐到 x_right 的单行文字。

    探针 req-a14-align-probe-800ada 实测：`alignment="CENTER"` 是**水平居中**
    （同一串 AB、同一个 400 px 盒，CENTER_LEFT 的墨迹贴左边、CENTER 的居中），
    而 `CENTER_LEFT` 是左对齐。所以要右缘对齐就得用 CENTER 并把盒中心放到
    x_right - 墨宽/2：

        盒左 = x_right - ink_est - pad/2，盒宽 = ink_est + pad

    盒比墨宽多 pad 是必须的：实测盒窄于墨宽时服务会**自动把文字折到第二行**，
    而单行盒高会把第二行整行裁掉——页脚右侧的「SESSION」就是这样消失的。
    盒向右多出 pad/2 仍在安全边距内（1112 + 20 = 1132 < 1160）。

    shift 是实测锚点修正（见 ANCHOR_SHIFT）：把它加到盒左就等于把盒心和墨迹一起
    平移 shift 像素，从而把 `real_ink ≠ ink_est` 造成的半个误差补回来。
    """
    w = ink_est + pad
    return text(x_right - ink_est - pad / 2 + shift, y, w, h, s, size,
                family=family, color=color, style=style, ls=ls, align="CENTER",
                mono=mono)


def rbox(x_right, y, h, ink_est, pad=PAD_X, shift=0.0) -> list:
    """text_r 实际发出的盒边界 [l, t, r, b]，供 meta 与几何检查使用。"""
    w = ink_est + pad
    return [x_right - ink_est - pad / 2 + shift, y, x_right + pad / 2 + shift,
            y + h]


def rect(x, y, w, h, *, color=None, border=None, radius=0.0):
    rd = ' borderRadius="%g"' % radius if radius else ""
    bd = ' border="%s"' % border if border else ""
    cd = ' color="%s"' % color if color else ""
    return ('<Positioned left="%g" top="%g" width="%g" height="%g">'
            '<Container width="%g" height="%g"%s%s%s />'
            '</Positioned>' % (x, y, w, h, w, h, rd, bd, cd))


def snapshot(w, h, parts):
    return ('<Snapshot type="png">\n<Container width="%d" height="%d">\n'
            '<Stack width="%d" height="%d">\n' % (w, h, w, h)
            + "\n".join(parts)
            + '\n</Stack>\n</Container>\n</Snapshot>\n')


BRAND = "Structure / Vision"
DATE = "2026.11.07"
FOOT_RIGHT = "讲座系列 · SESSION"


def build_card(card: dict) -> tuple[str, dict]:
    """一张卡的完整 DSL 与排版元数据。

    `<Stack>` 里后写的覆盖先写的，所以节点顺序就是绘制顺序：
    铺底矩形 → 徽标底色 → 徽标符号与文字 → 其余内容。徽标组件先攒成列表再
    整体插到铺底矩形之后。
    """
    p: list[str] = [rect(0, 0, W, H, color=PAPER)]
    sid = card["id"]
    status = STATUS[card["status"]]

    # 头部：品牌 / 主色短线 / 日期 / 分隔线。品牌与日期是纯代码式字符串，
    # 用等宽字；盒宽按保守步进估、渲染也显式 family=MONO，两边口径一致。
    brand_w = est_w(BRAND, HDR_SIZE, 2.0, mono=True)
    date_w = est_w(DATE, HDR_SIZE, 2.0, mono=True, tight=True)
    p.append(text(CX0, HEADER_Y, brand_w + PAD_X, lh(HDR_SIZE), BRAND, HDR_SIZE,
                  color=INK2, style="BOLD", family=MONO, ls=2.0, mono=True))
    p.append(text_r(CX1, HEADER_Y, lh(HDR_SIZE), DATE, HDR_SIZE, date_w,
                    family=MONO, color=MUTED, ls=2.0, mono=True,
                    shift=ANCHOR_SHIFT["date"]))
    p.append(rect(CX0, HEADER_Y + lh(HDR_SIZE) + ACCENT_RULE_GAP,
                  ACCENT_RULE_W, ACCENT_RULE_H, color=ACCENT))
    p.append(rect(CX0, RULE1_Y, CW, 1, color=RULE))

    # 标题先算：字号由参数化折行规则决定
    tf = fit_title(card["title"])
    title_bottom = TITLE_Y + len(tf["lines"]) * tf["lh"]

    # 状态徽标
    btext_h = lh(BADGE_TEXT_SIZE)
    btext_x = BADGE_X + BADGE_PAD + SYM + 10
    btext_w = BADGE_X + BADGE_W - BADGE_PAD - btext_x
    badge = [rect(BADGE_X, BADGE_Y0, BADGE_W, BADGE_H, color=status["bg"],
                  radius=BADGE_H / 2)]
    badge += sym_nodes(status["sym"], BADGE_X + BADGE_PAD,
                       BADGE_Y0 + (BADGE_H - SYM) / 2, SYM, status["fg"])
    badge.append(text(btext_x, BADGE_Y0 + (BADGE_H - btext_h) / 2, btext_w,
                      btext_h, card["status"], BADGE_TEXT_SIZE,
                      color=status["fg"], style="BOLD"))
    p[1:1] = badge

    # 标题：一行一个独立单行盒，不依赖服务的自动折行
    for k, ln in enumerate(tf["lines"]):
        p.append(text(TITLE_X, TITLE_Y + k * tf["lh"], TITLE_W, tf["lh"],
                      ln, tf["size"], style="BOLD", ls=TITLE_LS))

    # 讲者 / 时间
    sf = fit_speaker(card["speaker"])
    # 盒宽一律比墨宽多留 PAD_X，保证不触发服务的自动折行；定位用 tight 口径，
    # 否则右列整体左偏（等宽字实测 0.49–0.52 em，0.60 只适合估盒宽）。
    time_w = est_w(card["time"], TIME_SIZE, TIME_LS, mono=True, tight=True)
    lab_w = est_w("讲者", LABEL_SIZE)
    time_lab_w = est_w("时间", LABEL_SIZE)
    p.append(text(SPEAKER_X, LABEL_Y, lab_w + PAD_X, lh(LABEL_SIZE), "讲者",
                  LABEL_SIZE, color=MUTED, ls=1.5))
    p.append(text_r(CX1, LABEL_Y, lh(LABEL_SIZE), "时间", LABEL_SIZE,
                    time_lab_w, color=MUTED, ls=1.5,
                    shift=ANCHOR_SHIFT["label_time"]))
    for k, ln in enumerate(sf["lines"]):
        p.append(text(SPEAKER_X, VALUE_Y + k * sf["lh"], SPEAKER_W, sf["lh"],
                      ln, sf["size"], color=INK2))
    p.append(text_r(CX1, VALUE_Y, lh(TIME_SIZE), card["time"], TIME_SIZE,
                    time_w, family=MONO, color=INK, style="BOLD", ls=TIME_LS,
                    mono=True, shift=ANCHOR_SHIFT["time"]))

    # 取消卡：额外注明「本场取消」。位置由标题实际行数算出，不逐条硬改。
    cancel_note = None
    if card["status"] == "取消":
        note_y = title_bottom + NOTE_GAP
        note = [rect(NOTE_X, note_y, NOTE_W, NOTE_H, color="#FEE2E2",
                     border="1 SOLID #FCA5A5", radius=6)]
        note += sym_nodes("strike", NOTE_X + 18, note_y + (NOTE_H - 20) / 2,
                          20, "#B91C1C")
        ntext_h = lh(19)
        note.append(text(NOTE_X + 18 + 20 + 10, note_y + (NOTE_H - ntext_h) / 2,
                         NOTE_W - 18 - 20 - 10 - 18, ntext_h, "本场取消", 19,
                         color="#B91C1C", style="BOLD"))
        p += note
        cancel_note = {"box": [NOTE_X, note_y, NOTE_X + NOTE_W,
                               note_y + NOTE_H], "text": "本场取消",
                       "gap_from_title_bottom_px": note_y - title_bottom}

    # 底部
    p.append(rect(CX0, RULE2_Y, CW, 1, color=RULE))
    idw = est_w(sid, FOOT_SIZE, 3.0, mono=True)
    p.append(text(CX0, FOOT_Y, idw + PAD_X, lh(FOOT_SIZE), sid, FOOT_SIZE,
                  color=ACCENT, style="BOLD", family=MONO, mono=True, ls=3.0))
    frw = est_w(FOOT_RIGHT, FOOT_SIZE, 1.5)
    p.append(text_r(CX1, FOOT_Y, lh(FOOT_SIZE), FOOT_RIGHT, FOOT_SIZE, frw,
                    color=FAINT, ls=1.5, shift=ANCHOR_SHIFT["footer_right"]))

    dsl = snapshot(W, H, p)

    meta = {
        "id": sid,
        "canvas": [W, H],
        "safe_margin": SAFE,
        "content_column": [CX0, CX1],
        "raw": {"title": card["title"], "speaker": card["speaker"],
                "time": card["time"], "status": card["status"]},
        "title": {
            "text": card["title"],
            "box": [TITLE_X, TITLE_Y, TITLE_X + TITLE_W, title_bottom],
            "size_px": tf["size"],
            "line_height_px": tf["lh"],
            "lines": tf["lines"],
            "line_count": len(tf["lines"]),
            "line_count_max": TITLE_MAX_LINES,
            "estimated_widest_line_px": tf["widest_line_px"],
            "widest_line_ratio_of_box": tf["widest_ratio"],
            "font_steps_tried": tf["steps_tried"],
            "size_steps_available": TITLE_STEPS,
            "size_floor_px": TITLE_STEPS[-1],
            "bottom_px": title_bottom,
            "wrapped_not_shrunk_canvas": True,
        },
        "speaker": {
            "text": card["speaker"],
            "box": [SPEAKER_X, VALUE_Y, SPEAKER_X + SPEAKER_W,
                    VALUE_Y + SPEAKER_MAX_LINES * sf["lh"]],
            "size_px": sf["size"],
            "line_height_px": sf["lh"],
            "lines": sf["lines"],
            "line_count": len(sf["lines"]),
            "line_count_max": SPEAKER_MAX_LINES,
            "estimated_widest_line_px": sf["widest_line_px"],
            "font_steps_tried": sf["steps_tried"],
            "size_floor_px": 22,
        },
        "time": {"text": card["time"], "size_px": TIME_SIZE,
                 "letter_spacing": TIME_LS,
                 "box": rbox(CX1, VALUE_Y, lh(TIME_SIZE), time_w,
                             shift=ANCHOR_SHIFT["time"]),
                 "estimated_ink_px": round(time_w, 1),
                 "anchor": "ink_right_edge_at_CONTENT_RIGHT",
                 "anchor_shift_px": ANCHOR_SHIFT["time"]},
        "status": {
            "text": card["status"], "code": status["en"],
            "foreground": status["fg"], "background": status["bg"],
            "symbol_kind": status["sym"], "symbol_note": status["sym_note"],
            "symbol_drawn_geometrically": True,
            "box": [BADGE_X, BADGE_Y0, BADGE_X + BADGE_W, BADGE_Y0 + BADGE_H],
        },
        "cancel_note": cancel_note,
        "header": {
            "brand": {"text": BRAND, "size_px": HDR_SIZE,
                      "box": [CX0, HEADER_Y, CX0 + brand_w + PAD_X,
                              HEADER_Y + lh(HDR_SIZE)],
                      "estimated_ink_px": round(brand_w, 1),
                      "anchor": "left_edge_at_CONTENT_LEFT"},
            "date": {"text": DATE, "size_px": HDR_SIZE,
                     "box": rbox(CX1, HEADER_Y, lh(HDR_SIZE), date_w,
                                 shift=ANCHOR_SHIFT["date"]),
                     "estimated_ink_px": round(date_w, 1),
                     "anchor": "ink_right_edge_at_CONTENT_RIGHT",
                     "anchor_shift_px": ANCHOR_SHIFT["date"]},
            "accent_rule": [CX0, HEADER_Y + lh(HDR_SIZE) + ACCENT_RULE_GAP,
                            ACCENT_RULE_W, ACCENT_RULE_H],
            "rule_y": RULE1_Y,
        },
        "labels": {
            "speaker": {"box": [SPEAKER_X, LABEL_Y, SPEAKER_X + lab_w + PAD_X,
                                LABEL_Y + lh(LABEL_SIZE)],
                        "text": "讲者",
                        "estimated_ink_px": round(lab_w, 1)},
            "time": {"box": rbox(CX1, LABEL_Y, lh(LABEL_SIZE), time_lab_w,
                                 shift=ANCHOR_SHIFT["label_time"]),
                     "text": "时间",
                     "estimated_ink_px": round(time_lab_w, 1),
                     "anchor_shift_px": ANCHOR_SHIFT["label_time"]},
        },
        "footer": {
            "rule_y": RULE2_Y, "id": sid, "right_text": FOOT_RIGHT,
            "box": [CX0, FOOT_Y, CX1, FOOT_Y + lh(FOOT_SIZE)],
            "id_box": [CX0, FOOT_Y, CX0 + idw + PAD_X, FOOT_Y + lh(FOOT_SIZE)],
            "right_box": rbox(CX1, FOOT_Y, lh(FOOT_SIZE), frw,
                              shift=ANCHOR_SHIFT["footer_right"]),
            "id_estimated_ink_px": round(idw, 1),
            "right_estimated_ink_px": round(frw, 1),
            "right_anchor_shift_px": ANCHOR_SHIFT["footer_right"],
        },
        "title_badge_gap_px": BADGE_X - (TITLE_X + TITLE_W),
        "xml_escaped_chars": {c: card["title"].count(c) for c in "&<>"
                              if card["title"].count(c)},
    }
    return dsl, meta


# ---------------------------------------------------------------- 探针
def build_probe() -> tuple[str, dict]:
    """探针：一次渲染同时确认三件不能靠假设的事。

    1. XML 转义是否被解回字面字符（而不是显示成实体串）。
    2. 四个状态符号的几何形态是否互不相同且可辨。
    3. 最长标题 / 混合标题在 888 px 盒里的实际排版：行数、是否溢出右缘参照线。
    4. `alignment="CENTER"` 在「宽盒 + 窄文字」下的实际落点，用来核对时间/日期
       右列的真实对齐，而不是信估算。
    """
    p: list[str] = [rect(0, 0, W, H, color=PAPER)]
    long_title = ("从“已经请求成功”到“已经完成作品”：模型工作能力的最后一公里")
    mixed_title = "Color, Alpha & Contrast / 从颜色到可读性"
    angle_title = "A < B & C > D：不要把文本当成标签"

    p.append(text(88, 44, 700, lh(22), "A14 探针 · 转义 / 符号 / 折行 / 对齐", 22,
                  style="BOLD"))

    # 1) XML 转义
    p.append(text(88, 96, 400, lh(LABEL_SIZE), "1 XML 转义（应为字面 < > &）",
                  LABEL_SIZE, color=MUTED, ls=1.5))
    p.append(text(88, 122, TITLE_W, lh(40), angle_title, 40, style="BOLD",
                  ls=TITLE_LS))

    # 2) 四个状态符号
    p.append(text(88, 182, 520, lh(LABEL_SIZE), "2 状态符号（几何绘制，无字形依赖）",
                  LABEL_SIZE, color=MUTED, ls=1.5))
    for k, (name, st) in enumerate(STATUS.items()):
        x = 88 + k * 168
        p.append(rect(x, 208, 152, 60, color=st["bg"], radius=12))
        p += sym_nodes(st["sym"], x + 16, 228, 20, st["fg"])
        p.append(text(x + 16 + 20 + 10, 208 + (60 - lh(22)) / 2, 152 - 16 - 20
                      - 10 - 14, lh(22), name, 22, color=st["fg"],
                      style="BOLD"))

    # 3) 折行：最长标题、混合标题，右缘参照线用于目视确认未溢出
    p.append(text(88, 290, 600, lh(LABEL_SIZE),
                  "3 标题盒宽 %d，字号台阶 %s，字距 %g" % (
                      TITLE_W, TITLE_STEPS, TITLE_LS), LABEL_SIZE,
                  color=MUTED, ls=1.5))
    t1 = fit_title(long_title)
    for k, ln in enumerate(t1["lines"]):
        p.append(text(88, 316 + k * t1["lh"], TITLE_W, t1["lh"], ln, t1["size"],
                      style="BOLD", ls=TITLE_LS))
    y2 = 316 + len(t1["lines"]) * t1["lh"] + 18
    t2 = fit_title(mixed_title)
    for k, ln in enumerate(t2["lines"]):
        p.append(text(88, y2 + k * t2["lh"], TITLE_W, t2["lh"], ln, t2["size"],
                      style="BOLD", ls=TITLE_LS))
    ref_top = 316
    ref_bot = y2 + len(t2["lines"]) * t2["lh"]
    p.append(rect(TITLE_X + TITLE_W, ref_top, 1, ref_bot - ref_top,
                  color=ACCENT2))

    # 4) 对齐：时间/日期右列 + 长讲者
    y3 = ref_bot + 16
    p.append(text(88, y3, 520, lh(LABEL_SIZE), "4 右列对齐（CENTER 在宽盒内）与长讲者",
                  LABEL_SIZE, color=MUTED, ls=1.5))
    tw = est_w("15:00", TIME_SIZE, TIME_LS, mono=True)
    p.append(text(CX1 - tw, y3 + 22, tw, lh(TIME_SIZE), "15:00", TIME_SIZE,
                  color=INK, style="BOLD", align="CENTER", family=MONO,
                  mono=True, ls=TIME_LS))
    dw = est_w(DATE, HDR_SIZE, 2.0, mono=True)
    p.append(text(CX1 - dw, y3 + 22 + lh(TIME_SIZE) + 6, dw, lh(HDR_SIZE),
                  DATE, HDR_SIZE, color=MUTED, align="CENTER", family=MONO,
                  ls=2.0))
    sf = fit_speaker("Northstar Research · 林川")
    p.append(text(88, y3 + 22, 520, sf["lh"], sf["lines"][0], sf["size"],
                  color=INK2))
    p.append(rect(CX1, y3 + 22, 1, lh(TIME_SIZE) + lh(HDR_SIZE) + 6,
                  color=ACCENT2))

    meta = {"probe_items": [
        {"id": "xml-escape", "text": angle_title,
         "expected": "显示字面字符 A < B & C > D：不要把文本当成标签",
         "fail_if": "出现 &lt; &amp; &gt; 字面实体串，或标题缺失"},
        {"id": "status-symbols", "kinds": list(STATUS),
         "expected": "四种符号形状互不相同、均可辨",
         "fail_if": "出现豆腐块、缺字或形状雷同"},
        {"id": "title-wrap", "box_width": TITLE_W,
         "long": {"text": long_title, "size": t1["size"], "lines": t1["lines"],
                  "widest": t1["widest_line_px"]},
         "mixed": {"text": mixed_title, "size": t2["size"], "lines": t2["lines"],
                   "widest": t2["widest_line_px"]},
         "expected": "不超过 %d 行，墨迹不越过右缘参照线" % TITLE_MAX_LINES,
         "fail_if": "墨迹越过参照线或行数超限"},
        {"id": "right-column-align",
         "expected": "时间与日期墨迹右缘基本齐平且接近 x=1112",
         "fail_if": "两者右缘相差明显，或明显离 x=1112 过远"},
        {"id": "long-speaker", "text": "Northstar Research · 林川",
         "size": sf["size"], "lines": sf["lines"]},
    ]}
    return snapshot(W, H, p), meta


CARDS = json.loads(CARDS_PATH.read_text(encoding="utf-8"))


def checks() -> list[str]:
    """前置校验：不发请求，只验排版与硬约束。"""
    probs: list[str] = []
    for c in CARDS:
        dsl, m = build_card(c)
        tf, sf = m["title"], m["speaker"]
        if tf["size_px"] < 36:
            probs.append("%s 标题字号 %s 低于下限 36" % (c["id"], tf["size_px"]))
        if tf["line_count"] > TITLE_MAX_LINES:
            probs.append("%s 标题 %d 行超过上限 %d" % (
                c["id"], tf["line_count"], TITLE_MAX_LINES))
        if tf["widest_line_ratio_of_box"] > WRAP_SLACK:
            probs.append("%s 标题最宽行 %.0f%% 超过折行阈值 %.0f%%" % (
                c["id"], tf["widest_line_ratio_of_box"] * 100,
                WRAP_SLACK * 100))
        # 每行都必须是单行盒：单行墨宽不得超过盒宽（否则会被服务再折一次而裁切）
        for i, ln in enumerate(tf["lines"]):
            ew = est_w(ln, tf["size_px"], TITLE_LS)
            if ew > TITLE_W:
                probs.append("%s 标题第 %d 行墨宽 %.0f 超过盒宽 %d" % (
                    c["id"], i + 1, ew, TITLE_W))
        if sf["size_px"] < 22:
            probs.append("%s 讲者字号 %s 低于下限 22" % (c["id"], sf["size_px"]))
        if sf["line_count"] > SPEAKER_MAX_LINES:
            probs.append("%s 讲者 %d 行超过上限 %d" % (
                c["id"], sf["line_count"], SPEAKER_MAX_LINES))
        for i, ln in enumerate(sf["lines"]):
            if est_w(ln, sf["size_px"]) > SPEAKER_W:
                probs.append("%s 讲者第 %d 行墨宽超盒宽" % (c["id"], i + 1))
        # 安全边距：所有声明盒都必须落在 [SAFE, W-SAFE] × [SAFE, H-SAFE] 内
        boxes = {"title": tf["box"], "speaker": sf["box"],
                 "status": m["status"]["box"], "time": m["time"]["box"],
                 "brand": m["header"]["brand"]["box"],
                 "date": m["header"]["date"]["box"],
                 "label.speaker": m["labels"]["speaker"]["box"],
                 "label.time": m["labels"]["time"]["box"],
                 "footer": m["footer"]["box"],
                 "footer.id": m["footer"]["id_box"],
                 "footer.right": m["footer"]["right_box"]}
        for key, (l, t, r, b) in boxes.items():
            if l < SAFE - 0.5 or t < SAFE - 0.5 or r > W - SAFE + 0.5 \
                    or b > H - SAFE + 0.5:
                probs.append("%s %s 盒 [%s] 越出安全边距 %d" % (
                    c["id"], key, [round(v) for v in (l, t, r, b)], SAFE))
        if m["title_badge_gap_px"] < 16:
            probs.append("%s 标题右缘与徽标净距只有 %s px" % (
                c["id"], m["title_badge_gap_px"]))
        if tf["box"][3] > LABEL_Y - 8:
            probs.append("%s 标题盒底 %s 逼近讲者标签行 %s" % (
                c["id"], tf["box"][3], LABEL_Y))
        if sf["box"][3] > RULE2_Y - 4:
            probs.append("%s 讲者盒底 %s 压到底部分隔线 %s" % (
                c["id"], sf["box"][3], RULE2_Y))
        if c["status"] == "取消":
            if not m["cancel_note"]:
                probs.append("%s 取消卡缺少「本场取消」注明" % c["id"])
            nb = m["cancel_note"]["box"]
            if nb[3] > LABEL_Y - LABEL_CLEAR:
                probs.append("%s 取消注明底缘 %s 与讲者标签行 %s 净距不足" % (
                    c["id"], nb[3], LABEL_Y))
            if not m["time"]["text"] or tf["line_count"] == 0:
                probs.append("%s 取消卡标题或时间被删" % c["id"])
        if not m["status"]["code"] or not m["status"]["foreground"]:
            probs.append("%s 状态编码缺失" % c["id"])
        # 原文必须原样保留
        if m["raw"] != {k: c[k] for k in ("title", "speaker", "time", "status")}:
            probs.append("%s 原始文字未原样保留" % c["id"])
        # 结构完整性：声明了几条文字就该有几个 <Text> 节点。这条专门抓
        # 「写进了 meta 却忘了写进 DSL」的漏发——上一版整个头部（品牌、日期、
        # 主色短线、分隔线）就是这样漏掉的。
        n_expect = (2 + 1 + tf["line_count"] + 2 + sf["line_count"] + 1
                    + (1 if c["status"] == "取消" else 0) + 2)
        n_text = dsl.count('<Text ')
        if n_text != n_expect:
            probs.append("%s <Text> 节点数 %d 与声明的 %d 不符" % (
                c["id"], n_text, n_expect))
        if 'color="%s" />' % ACCENT not in dsl:
            probs.append("%s 主色短线未出现在 DSL" % c["id"])
        # 盒宽必须大于墨宽：实测盒窄于墨宽时服务会自行折到第二行，而单行盒高把
        # 第二行整行裁掉。上一版「讲者」→「讲」、「SESSION」整段消失就是这个根因。
        box_vs_ink = [
            ("时间标签", m["labels"]["time"]["box"][2] - m["labels"]["time"]["box"][0],
             m["labels"]["time"]["estimated_ink_px"]),
            ("讲者标签", m["labels"]["speaker"]["box"][2] - m["labels"]["speaker"]["box"][0],
             m["labels"]["speaker"]["estimated_ink_px"]),
            ("时间", m["time"]["box"][2] - m["time"]["box"][0],
             m["time"]["estimated_ink_px"]),
            ("日期", m["header"]["date"]["box"][2] - m["header"]["date"]["box"][0],
             m["header"]["date"]["estimated_ink_px"]),
            ("品牌", m["header"]["brand"]["box"][2] - m["header"]["brand"]["box"][0],
             m["header"]["brand"]["estimated_ink_px"]),
            ("页脚卡号", m["footer"]["id_box"][2] - m["footer"]["id_box"][0],
             m["footer"]["id_estimated_ink_px"]),
            ("页脚右串", m["footer"]["right_box"][2] - m["footer"]["right_box"][0],
             m["footer"]["right_estimated_ink_px"]),
        ]
        for name, bw, iw in box_vs_ink:
            if bw <= iw:
                probs.append("%s %s 盒宽 %.1f 未超过墨宽估算 %.1f（会被服务折行后"
                             "裁切）" % (c["id"], name, bw, iw))
    if len(CARDS) != 8:
        probs.append("卡片数 %d，应为 8" % len(CARDS))
    if len({c["id"] for c in CARDS}) != 8:
        probs.append("卡片 ID 有重复或缺失")
    ids = sorted(c["id"] for c in CARDS)
    if ids != ["K0%d" % i for i in range(1, 9)]:
        probs.append("卡片 ID 序列异常：%s" % ids)
    # 全批一致性：主色、日期、品牌、关键槽位坐标必须完全一致
    coords = set()
    for c in CARDS:
        _, m = build_card(c)
        coords.add((m["title"]["box"][0], m["title"]["box"][1],
                    m["title"]["box"][2], m["speaker"]["box"][0],
                    m["speaker"]["box"][1], m["status"]["box"][0],
                    m["status"]["box"][1], m["status"]["box"][2],
                    m["time"]["box"][0], m["time"]["box"][2],
                    m["header"]["brand"]["box"][1], m["footer"]["rule_y"]))
    if len(coords) > 1:
        probs.append("各卡关键槽位坐标不统一：%d 种组合" % len(coords))
    for k, st in STATUS.items():
        if not st["fg"] or not st["bg"] or st["fg"] == st["bg"]:
            probs.append("状态「%s」颜色配置无效" % k)
    fgs = {k: st["fg"] for k, st in STATUS.items()}
    if len(set(fgs.values())) != 4:
        probs.append("四个状态前景色未互不相同")
    return probs


def _dsl_of(card: dict) -> str:
    return build_card(card)[0]


# 服务不解码 XML 实体（见 esc() 的实测说明），text 属性里出现实体串即为缺陷
ENT_STRINGS = ("&lt;", "&gt;", "&amp;", "&quot;", "&apos;")


def _diff(exp: Counter, got: Counter) -> str:
    keys = sorted(set(exp) | set(got))
    out = []
    for k in keys:
        if exp[k] != got[k]:
            out.append("%r %d→%d" % (k, exp[k], got[k]))
    return "；".join(out[:8]) or "无差异"


def _escape_check() -> list[str]:
    """逐字核验：原文里的 & < > 必须原样出现在 DSL 的 text 属性里。

    探针实测（见 esc() 说明）确认服务不解码 XML 实体，所以本检查的方向与
    「必须转义」相反：实体串出现即为缺陷，裸字符才是正确形态。
    """
    probs = []
    for c in CARDS:
        dsl = _dsl_of(c)
        vals = [seg.split('"', 1)[0] for seg in dsl.split('text="')[1:]]
        joined = "".join(vals)
        for e in ENT_STRINGS:
            if e in joined:
                probs.append("%s DSL text 属性里出现实体串 %s（服务不解码，"
                             "画面上会显示成字面串）" % (c["id"], e))
        for field in ("title", "speaker", "time", "status"):
            if '"' in c[field]:
                probs.append("%s %s 含半角双引号，会截断 DSL text 属性"
                             % (c["id"], field))
        # 卡上出现的所有文字必须与预期文本集的字符多重集完全一致。多重集
        # 比较同时抓住「折行丢字」「折行多字」「被转义吃掉字符」三类缺陷。
        expected = (c["title"] + c["speaker"] + c["time"] + c["status"]
                    + "讲者" + "时间" + BRAND + DATE + c["id"] + FOOT_RIGHT)
        if c["status"] == "取消":
            expected += "本场取消"
        # 折行点会吃掉一个空格，这是正常排版行为（「Contrast /」换行后下一行
        # 不需要前导空格），不参与多重集比对；空格另有分词器无损校验兜底。
        exp_ns = Counter(ch for ch in expected if ch != SP)
        got_ns = Counter(ch for ch in joined if ch != SP)
        if exp_ns != got_ns:
            probs.append("%s DSL text 字符多重集与预期不符：%s"
                         % (c["id"], _diff(exp_ns, got_ns)))
        # 折行必须是无损重排：各行拼回去应等于原文（去掉空白后）
        _, m = build_card(c)
        for key, field in (("title", "title"), ("speaker", "speaker")):
            back = "".join(m[key]["lines"]).replace(" ", "")
            if back != c[field].replace(" ", ""):
                probs.append("%s %s 折行后字符不一致：拼回「%s」"
                             % (c["id"], key, "".join(m[key]["lines"])))
        # 分词器自身必须无损：把原文切成 token 再拼回去要逐字等于原文。
        # 这条能抓住「CJK 前导空格被吞」「词被切开」这类 token 级缺陷，而
        # 逐行拼接的比对抓不住（它会把空格全去掉）。
        for field in ("title", "speaker"):
            back = join(tokenize(c[field]))
            if back != c[field]:
                probs.append("%s %s 分词拼接有损：原文 %r 拼回 %r"
                             % (c["id"], field, c[field], back))
    return probs


def render_all(to_out: bool) -> dict:
    if to_out:
        OUT.mkdir(parents=True, exist_ok=True)
    rows = {}
    for c in CARDS:
        dsl, m = build_card(c)
        label = "card-" + c["id"]
        r = C.render(TASK, dsl, label, kind="render",
                     purpose="讲座宣传卡 %s「%s」" % (c["id"], c["title"]))
        rows[c["id"]] = {"request_id": r["request_id"], "status": r["status"],
                         "bytes": r["log"].get("response_bytes"),
                         "dsl_path": r["log"]["dsl_path"],
                         "response_path": r["response_path"], "meta": m}
        print("  %-8s HTTP %-3s %7s B  rid=%s" % (
            label, r["status"], r["log"].get("response_bytes"), r["request_id"]))
        if r["status"] != 200:
            print("    错误：", r["log"].get("error"))
            continue
        if to_out:
            (OUT / (label + ".png")).write_bytes(r["body"])
            (OUT / (label + ".snapshot")).write_text(dsl, encoding="utf-8")
            print("    ->", S.rel(OUT / (label + ".png")))
    return rows


def _checks_report() -> tuple[list[str], list[str]]:
    """前置校验报告：返回 (问题列表, 待打印/待归档的行)。

    同时打印与落盘：落盘是为了在 Bash 前台被拦时仍能从仓库内的
    tmp/<rid>/A14/gen/checks.log 读到完整结果。
    """
    probs = checks() + _escape_check()
    lines = ["前置校验 %d 个问题" % len(probs)]
    lines += ["  ! %s" % x for x in probs]
    for c in CARDS:
        _, m = build_card(c)
        lines.append("  %-4s 标题 %2dpx %d行 最宽%.0fpx(%.0f%%) | 讲者 %dpx %d行 | %s%s"
                     % (c["id"], m["title"]["size_px"], m["title"]["line_count"],
                        m["title"]["estimated_widest_line_px"],
                        m["title"]["widest_line_ratio_of_box"] * 100,
                        m["speaker"]["size_px"], m["speaker"]["line_count"],
                        m["status"]["code"],
                        " | 取消注明" if m["cancel_note"] else ""))
        lines.append("       标题行：%s" % " ⏎ ".join(m["title"]["lines"]))
        lines.append("       讲者行：%s" % " ⏎ ".join(m["speaker"]["lines"]))
    return probs, lines


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else "checks"
    if mode == "checks":
        probs, lines = _checks_report()
        (TMP / "gen").mkdir(parents=True, exist_ok=True)
        (TMP / "gen" / "checks.log").write_text("\n".join(lines) + "\n",
                                               encoding="utf-8")
        for x in lines:
            print(x)
        print("->", S.rel(TMP / "gen" / "checks.log"))
        return 1 if probs else 0
    if mode == "probe":
        (TMP / "preview").mkdir(parents=True, exist_ok=True)
        dsl, m = build_probe()
        r = C.render(TASK, dsl, "probe-layout", kind="render",
                     purpose="A14 探针：XML 转义、状态符号几何、标题折行、右列对齐")
        print("探针 HTTP", r["status"], "bytes", r["log"].get("response_bytes"),
              "rid", r["request_id"])
        if r["status"] != 200:
            print("错误：", r["log"].get("error"))
            return 1
        p = TMP / "preview" / "a14-probe.png"
        p.write_bytes(r["body"])
        print("->", S.rel(p))
        (TMP / "gen" / "probe.layout.json").write_text(
            json.dumps(m, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return 0
    if mode == "finals":
        probs = checks() + _escape_check()
        if probs:
            print("前置校验未通过，不渲染：")
            for x in probs:
                print("  !", x)
            return 1
        rows = render_all(to_out=True)
        (TMP / "gen" / "render-rows.json").write_text(
            json.dumps({"mode": "finals", "rows": rows,
                        "checks_problems": probs}, ensure_ascii=False, indent=2)
            + "\n", encoding="utf-8")
        ok = sum(1 for v in rows.values() if v["status"] == 200)
        print("成功 %d/%d" % (ok, len(CARDS)))
        return 0 if ok == len(CARDS) else 1
    raise SystemExit("未知模式 %s" % mode)


if __name__ == "__main__":
    raise SystemExit(main())
