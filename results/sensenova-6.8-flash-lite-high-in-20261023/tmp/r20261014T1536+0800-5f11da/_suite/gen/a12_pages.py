"""A12 四断点完整内容视觉系统：一份内容 + 一套设计参数 → 四份完整 DSL。

inputs/content.json 的全部内容在四个画布上一字不丢，只重组结构：
  mobile  360×800   手机竖屏，单列流
  tablet  768×1024  平板，标题区在上、卡片 2×3
  desktop 1440×900  桌面，左侧深色面板 + 右侧卡片 2×3
  stage   1920×1080 大屏，左侧 hero + 右侧卡片 3×2

四条契约由探针 1/2 实测得出（a12_probe1/2.py，量测 probe{1,2}.measure.json）：
  * 文本在固定宽容器里自动折行，CJK 可在任意字符间断行
  * 行距 = 1.45 × 字号（实测饱和行距 1.40–1.44 × 字号，取上界做安全预算）
  * 容器高度小于文字高度时文字**被裁掉**，不是溢出 —— 行数 × 行高必须给足
  * 单行墨迹上缘距盒顶约 0.28 × 字号；盒有余量时垂直居中
  * 子文本里的前导空格会被裁掉 → CTA 不做分色富文本，保真优先于局部着色

补充契约（由最终四图的像素量测补得，见 title.measure.json / a12_verify.py）：
  * 同一字符串的墨宽随字号线性缩放。desktop 56 px 实测「Structure / Vision」墨宽
    473 px，据此线性外推：stage 若用 72 px 则是 608 px > 600 盒宽 → 折成两行，
    而盒只给了一行高，第二行「Vision」被裁掉。这就是初版 stage 图的真实缺陷。
  * Latin 字符的平均墨宽是 0.47 em，不是早先估算用的 0.55 em。
  * check() 据此在「墨宽估算 > 盒宽 × 0.92」时报折行风险，防止再出同类裁切。

用法：SNAPSHOT_RUN_ID=<rid> python -I tmp/<rid>/_suite/gen/a12_pages.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[4]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(HERE.parent))
import suite as S  # noqa: E402
import snap_client as C  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

TASK = "A12"
OUT, TMP = S.task_dirs(TASK)
SRC = ROOT / "tasks" / "A12-responsive-system" / "inputs" / "content.json"
CONTENT = json.loads(SRC.read_text(encoding="utf-8"))

CJK = "Noto Sans CJK SC"
MONO = "Noto Sans Mono CJK SC"

# --- 色彩：四断点共用同一套，不随尺寸改变 ----------------------------------
INK = "#0F172A"       # 主文字
INK2 = "#1E293B"      # 次文字
MUTED = "#64748B"     # 卡片详情等辅助正文
FAINT = "#94A3B8"     # 元信息标签、浅底序号
RULE = "#E2E8F0"      # 分隔线、卡片描边
RULE2 = "#CBD5E1"     # 元信息列分隔
SURFACE = "#FFFFFF"
ZEBRA = "#F8FAFC"     # 元信息表格底色
BAND = "#F1F5F9"
ACCENT = "#0F766E"    # 卡片 ID 徽章、左侧强调条、顶部色条
ACCENT_D = "#134E4A"  # 深主色：CTA 强调带、面板
ACCENT_L = "#5EEAD4"  # 深底副标题与网址
MINT = "#7CC7BD"      # 深底标签
PANEL_RULE = "#2E6A63"
PANEL_NUM = "#2E7E74"  # 深底大序号（与面板色距 > 40 才能被量测到）
DECO = "#D5DDE5"      # 浅底大序号
WHITE = "#FFFFFF"

LEFT, RIGHT, MID = "CENTER_LEFT", "CENTER_RIGHT", "CENTER"


def lh(size: int) -> int:
    """一行文字的最小盒高；小于它会被裁。"""
    return max(1, round(size * 1.45))


LATIN_EM = 0.47  # Latin 平均墨宽（em）；由 desktop 56 px 实测 473 px / 18 字符反推


def est_w(text: str, size: int, mono: bool = False, ls: float = 0) -> float:
    """字宽估算，只用于预判是否折行；真值以像素量测为准。

    系数来源：mono 全宽 1.0 em、CJK 1.0 em 为设计值；Latin 0.47 em 由
    title.measure.json 实测（desktop 56 px「Structure / Vision」墨宽 473 px）。
    量测给的是墨迹盒宽度，略小于排版 advance，故判定时另留 8 % 余量。
    """
    w = 0.0
    for ch in text:
        if ch == " ":
            w += size * (0.5 if mono else 0.33)
        elif ord(ch) > 0x2E80:
            w += size * 1.0
        elif ch == "·":
            w += size * 0.67
        else:
            w += size * (0.5 if mono else LATIN_EM)
    return w + ls * (len(text) - 1)


class Canvas:
    """一个断点：累计 DSL 片段与文字条目，结束时自检边界与重叠。"""

    def __init__(self, name: str, w: int, h: int, margin: int) -> None:
        self.name, self.W, self.H, self.M = name, w, h, margin
        self.parts: list[str] = []
        self.entries: list[dict] = []
        self._n = 0

    def block(self, x: int, y: int, w: int, h: int, color: str,
              border: str = "") -> None:
        inner = f'<Container width="{w}" height="{h}" color="{color}" />'
        if border:
            inner = f'<Border border="{border}">{inner}</Border>'
        self.parts.append(f'<Positioned left="{x}" top="{y}" width="{w}" '
                          f'height="{h}">{inner}</Positioned>')

    def txt(self, field: str, x: int, y: int, w: int, h: int, text: str,
            size: int, *, family: str = CJK, color: str = INK, style: str = "",
            align: str = LEFT, ls: float = 0, card_id: str | None = None,
            decorative: bool = False) -> str:
        self._n += 1
        tag = f"{self.name[:3]}-{self._n:02d}"
        st = f' fontStyle="{style}"' if style else ""
        lsa = f' letterSpacing="{ls}"' if ls else ""
        self.parts.append(
            f'<Positioned left="{x}" top="{y}" width="{w}" height="{h}">'
            f'<Container width="{w}" height="{h}" alignment="{align}">'
            f'<Text fontFamily="{family}" fontSize="{size}" color="{color}"'
            f'{st}{lsa} text="{text}" /></Container></Positioned>')
        self.entries.append({
            "tag": tag, "field": field, "card_id": card_id, "text": text,
            "box": [x, y, w, h], "font_size": size, "family": family,
            "align": align, "letter_spacing": ls or None,
            "decorative": decorative,
        })
        return tag

    def dsl(self) -> str:
        return "\n".join(["<Snapshot background=\"#FFFFFF\">",
                          f'<Container width="{self.W}" height="{self.H}">',
                          f'<Stack width="{self.W}" height="{self.H}">']
                         + self.parts + ["</Stack>", "</Container>",
                                         "</Snapshot>"]) + "\n"

    def check(self) -> dict:
        """边界、折行风险、文字盒两两重叠、以及输入串逐字段保真自检。"""
        problems: list[str] = []
        for e in self.entries:
            x, y, w, h = e["box"]
            if (x < self.M - 1 or y < self.M - 1
                    or x + w > self.W - self.M + 1 or y + h > self.H - self.M + 1):
                problems.append(f"越出安全边距 {self.M}: {e['tag']} {e['box']}")
            # 折行风险：折行后盒高若只够一行，第二行会被裁掉（stage 初版就这样丢了
            # 「Vision」）。墨宽估算超过盒宽 92 % 即报警，留足余量。
            ew = est_w(e["text"], e["font_size"], e["family"] == MONO,
                       e["letter_spacing"] or 0)
            if ew > w * 0.92:
                problems.append(
                    f"预判折行 {e['tag']}「{e['text']}」墨宽≈{ew:.0f} 超过盒宽 {w} "
                    f"的 92%（折行后会被裁）")
        boxes = [(e["tag"], e["box"]) for e in self.entries
                 if not e["decorative"]]
        for i in range(len(boxes)):
            for j in range(i + 1, len(boxes)):
                ta, ba = boxes[i]
                tb, bb = boxes[j]
                if (max(ba[0], bb[0]) < min(ba[0] + ba[2], bb[0] + bb[2]) - 0.5
                        and max(ba[1], bb[1])
                        < min(ba[1] + ba[3], bb[1] + bb[3]) - 0.5):
                    problems.append(f"文字盒重叠 {ta} {ba} × {tb} {bb}")
        texts = [e["text"] for e in self.entries]
        for fld, val in CONTENT.items():
            if fld == "cards":
                for c in val:
                    if c["title"] not in texts:
                        problems.append(f"缺失 {c['id']}.title={c['title']}")
                    if c["detail"] not in texts:
                        problems.append(f"缺失 {c['id']}.detail={c['detail']}")
            elif val not in texts:
                problems.append(f"缺失 {fld}={val}")
        return {"canvas": self.name, "size": [self.W, self.H],
                "margin": self.M, "entries": len(self.entries),
                "problems": problems}


# --- 组件 -----------------------------------------------------------------
def meta_rows(cv: Canvas, x: int, y: int, w: int, items, label_size: int,
              value_size: int, label_w: int, label_color: str,
              value_color: str, step: int) -> None:
    """标签在左、数值右对齐的三行元信息（手机/平板/桌面/大屏统一形态）。"""
    for i, (key, lab, val, mono) in enumerate(items):
        ty = y + i * step
        cv.txt("meta." + key, x, ty, label_w, lh(label_size), lab,
               label_size, color=label_color)
        cv.txt(key, x + label_w + 8, ty, w - label_w - 8, lh(value_size), val,
               value_size, family=MONO if mono else CJK, color=value_color,
               style="BOLD", align=RIGHT)


def section_label(cv: Canvas, x: int, y: int, w: int, size: int,
                  color: str, count_color: str) -> None:
    cv.txt("section.title", x, y, w - 120, lh(size), "六大环节", size,
           color=color, style="BOLD")
    cv.txt("section.count", x + w - 64, y, 64, lh(size), "06", size,
           family=MONO, color=count_color, style="BOLD", align=RIGHT,
           decorative=True)


def card(cv: Canvas, cid: str, title: str, detail: str, idx: str, x: int,
         y: int, w: int, h: int, t_size: int, d_size: int, pad: int,
         badge_w: int, strip: int, badge_gap: int, rule_gap: int,
         show_rule: bool, show_idx: bool, idx_size: int) -> None:
    """卡片：白底 + 描边 + 左侧强调条 + ID 徽章 + 标题 + 分隔 + 详情 [+ 大序号]。"""
    cv.block(x, y, w, h, SURFACE, "1 SOLID " + RULE)
    cv.block(x, y, strip, h, ACCENT)
    cv.txt("cards[].id", x + pad, y + pad, badge_w, lh(d_size), cid, d_size,
           family=MONO, color=ACCENT, style="BOLD", card_id=cid)
    cv.txt("cards[].title", x + pad + badge_w + badge_gap, y + pad,
           w - 2 * pad - badge_w - badge_gap, lh(t_size), title, t_size,
           color=INK, style="BOLD", card_id=cid)
    cy = y + pad + max(lh(t_size), lh(d_size)) + rule_gap
    if show_rule:
        cv.block(x + pad, cy, w - 2 * pad, 1, RULE)
        cy += 1 + rule_gap
    cv.txt("cards[].detail", x + pad, cy, w - 2 * pad, lh(d_size), detail,
           d_size, color=MUTED, card_id=cid)
    if show_idx:
        cv.txt("deco.index", x + pad, y + h - pad - lh(idx_size), 220,
               lh(idx_size), idx, idx_size, family=MONO, color=DECO,
               style="BOLD", decorative=True)


def build_mobile() -> Canvas:
    """360×800，边距 16。单列：标题区 → 元信息 → CTA → 网址 → 六卡纵排。"""
    cv = Canvas("mobile", 360, 800, 16)
    M = 16
    cv.block(M, M, 56, 4, ACCENT)
    cv.txt("title", M, 28, 328, lh(30), CONTENT["title"], 30,
           color=INK, style="BOLD")
    cv.txt("subtitle", M, 80, 328, lh(17), CONTENT["subtitle"], 17, color=INK2)
    cv.block(M, 114, 328, 1, RULE)
    cv.block(M, 122, 328, 88, ZEBRA, "1 SOLID " + RULE)
    meta_rows(cv, M + 18, 132, 292,
              [("date", "日期", CONTENT["date"], True),
               ("time", "时间", CONTENT["time"], True),
               ("location", "地点", CONTENT["location"], False)],
              16, 16, 54, FAINT, INK, 23)
    cv.block(M, 218, 328, 52, ACCENT_D)
    cv.txt("cta", M + 16, 218, 296, 52, CONTENT["cta"], 18, color=WHITE,
           style="BOLD", align=MID)
    cv.block(M, 282, 14, 14, ACCENT)
    cv.txt("website", M + 24, 278, 272, lh(16), CONTENT["website"], 16,
           family=MONO, color=INK2)
    section_label(cv, M, 308, 328, 18, INK, ACCENT)
    for i, c in enumerate(CONTENT["cards"]):
        card(cv, c["id"], c["title"], c["detail"], "%02d" % (i + 1),
             M, 342 + i * 74, 328, 68, 18, 16, 9, 30, 3, 12, 3, False, False, 0)
    return cv


def build_tablet() -> Canvas:
    """768×1024，边距 32。标题区在上，元信息三列，CTA 通栏，卡片 2×3。"""
    cv = Canvas("tablet", 768, 1024, 32)
    M = 32
    cv.block(M, M, 72, 5, ACCENT)
    cv.txt("title", M, 46, 704, lh(46), CONTENT["title"], 46,
           color=INK, style="BOLD")
    cv.txt("subtitle", M, 120, 704, lh(24), CONTENT["subtitle"], 24, color=INK2)
    cv.block(M, 168, 704, 1, RULE)
    cv.block(M, 178, 704, 88, ZEBRA, "1 SOLID " + RULE)
    cv.block(270, 192, 1, 62, RULE2)
    cv.block(498, 192, 1, 62, RULE2)
    for i, (key, lab, val, mono) in enumerate([
            ("date", "日期", CONTENT["date"], True),
            ("time", "时间", CONTENT["time"], True),
            ("location", "地点", CONTENT["location"], False)]):
        x = 52 + i * 228
        cv.txt("meta." + key, x, 190, 120, lh(20), lab, 20, color=FAINT)
        cv.txt(key, x, 224, 208, lh(22), val, 22,
               family=MONO if mono else CJK, color=INK, style="BOLD")
    cv.block(M, 278, 704, 76, ACCENT_D)
    cv.txt("cta", M + 24, 278, 656, 76, CONTENT["cta"], 26, color=WHITE,
           style="BOLD", align=MID)
    cv.block(M, 368, 20, 20, ACCENT)
    cv.txt("website", M + 30, 364, 640, lh(22), CONTENT["website"], 22,
           family=MONO, color=INK2)
    section_label(cv, M, 406, 704, 24, INK, ACCENT)
    for i, c in enumerate(CONTENT["cards"]):
        col, row = i % 2, i // 2
        card(cv, c["id"], c["title"], c["detail"], "%02d" % (i + 1),
             32 + col * 364, 451 + row * 187, 340, 167, 24, 22, 20, 44, 4, 14,
             10, True, False, 0)
    return cv


def build_desktop() -> Canvas:
    """1440×900，边距 32。左侧 600 深底面板放标题/元信息/CTA/网址，右侧卡片 2×3。"""
    cv = Canvas("desktop", 1440, 900, 32)
    M = 32
    cv.block(M, M, 600, 836, ACCENT_D)
    hx = M + 40                                  # 72
    cv.block(hx, M + 40, 72, 6, ACCENT)
    # 标题 50 px：56 px 实测墨宽 473 只比 480 盒宽少 7 px，属折行临界，故下调一档
    cv.txt("title", hx, M + 70, 480, lh(50), CONTENT["title"], 50,
           color=WHITE, style="BOLD")
    cv.txt("subtitle", hx, M + 162, 480, lh(26), CONTENT["subtitle"], 26,
           color=ACCENT_L)
    cv.block(hx, M + 227, 480, 1, PANEL_RULE)
    meta_rows(cv, hx, M + 247, 480,
              [("date", "Date", CONTENT["date"], True),
               ("time", "Time", CONTENT["time"], True),
               ("location", "Location", CONTENT["location"], False)],
              20, 22, 96, MINT, WHITE, 46)
    cv.block(hx, M + 403, 480, 84, WHITE)
    cv.txt("cta", hx + 24, M + 403, 432, 84, CONTENT["cta"], 26,
           color=ACCENT_D, style="BOLD", align=MID)
    cv.block(hx, M + 503, 480, 1, PANEL_RULE)
    cv.txt("website", hx, M + 519, 480, lh(24), CONTENT["website"], 24,
           family=MONO, color=ACCENT_L)
    cv.txt("deco.numeral", hx, M + 599, 340, lh(108), "06", 108, family=MONO,
           color=PANEL_NUM, style="BOLD", decorative=True)
    cv.txt("section.title", hx, M + 768, 340, lh(20), "六大环节", 20,
           color=MINT)
    section_label(cv, 664, M, 744, 24, INK, ACCENT)
    for i, c in enumerate(CONTENT["cards"]):
        col, row = i % 2, i // 2
        card(cv, c["id"], c["title"], c["detail"], "%02d" % (i + 1),
             664 + col * 384, 76 + row * 270, 360, 252, 26, 24, 28, 48, 4, 14,
             14, True, True, 22)
    return cv


def build_stage() -> Canvas:
    """1920×1080，边距 32。左侧 680 hero 面板，右侧卡片 3×2。"""
    cv = Canvas("stage", 1920, 1080, 32)
    M = 32
    cv.block(M, M, 680, 1016, ACCENT_D)
    hx = M + 44                                  # 76
    cv.block(hx, M + 64, 88, 7, ACCENT)
    # 标题 64 px：72 px 实测外推墨宽 608 > 600 盒宽，初版折行丢了「Vision」
    cv.txt("title", hx, M + 100, 600, lh(64), CONTENT["title"], 64,
           color=WHITE, style="BOLD")
    cv.txt("subtitle", hx, M + 215, 600, lh(32), CONTENT["subtitle"], 32,
           color=ACCENT_L)
    cv.block(hx, M + 281, 600, 1, PANEL_RULE)
    meta_rows(cv, hx, M + 309, 600,
              [("date", "Date", CONTENT["date"], True),
               ("time", "Time", CONTENT["time"], True),
               ("location", "Location", CONTENT["location"], False)],
              22, 26, 104, MINT, WHITE, 56)
    cv.block(hx, M + 505, 600, 100, WHITE)
    cv.txt("cta", hx + 32, M + 505, 536, 100, CONTENT["cta"], 32,
           color=ACCENT_D, style="BOLD", align=MID)
    cv.block(hx, M + 621, 600, 1, PANEL_RULE)
    cv.txt("website", hx, M + 641, 600, lh(26), CONTENT["website"], 26,
           family=MONO, color=ACCENT_L)
    cv.txt("deco.numeral", hx, M + 717, 420, lh(132), "06", 132, family=MONO,
           color=PANEL_NUM, style="BOLD", decorative=True)
    cv.txt("section.title", hx, M + 964, 420, lh(22), "六大环节", 22,
           color=MINT)
    section_label(cv, 744, M, 1144, 28, INK, ACCENT)
    for i, c in enumerate(CONTENT["cards"]):
        col, row = i % 3, i // 3
        card(cv, c["id"], c["title"], c["detail"], "%02d" % (i + 1),
             744 + col * 390, 76 + row * 504, 362, 468, 28, 24, 32, 56, 5, 16,
             14, True, True, 150)
    return cv


CANVASES = [build_mobile(), build_tablet(), build_desktop(), build_stage()]

SCALES = {
    "mobile": {"eyebrow": None, "title": 30, "subtitle": 17, "body": 16,
               "meta_label": 16, "meta_value": 16, "cta": 18,
               "card_title": 18, "card_detail": 16, "section": 18},
    "tablet": {"eyebrow": None, "title": 46, "subtitle": 24, "body": 22,
               "meta_label": 20, "meta_value": 22, "cta": 26,
               "card_title": 24, "card_detail": 22, "section": 24},
    "desktop": {"eyebrow": None, "title": 50, "subtitle": 26, "body": 24,
                "meta_label": 20, "meta_value": 22, "cta": 26,
                "card_title": 26, "card_detail": 24, "section": 24},
    "stage": {"eyebrow": None, "title": 64, "subtitle": 32, "body": 26,
              "meta_label": 22, "meta_value": 26, "cta": 32,
              "card_title": 28, "card_detail": 24, "section": 28},
}

SPACING = {
    "margin": {"mobile": 16, "tablet": 32, "desktop": 32, "stage": 32},
    "mobile": {"card_w": 328, "card_h": 68, "card_gap": 6, "card_pad": 9,
               "meta_row_step": 23},
    "tablet": {"card_w": 340, "card_h": 167, "col_gap": 24, "row_gap": 20,
               "card_pad": 20},
    "desktop": {"panel_w": 600, "card_w": 360, "card_h": 252, "col_gap": 24,
                "row_gap": 18, "card_pad": 28},
    "stage": {"panel_w": 680, "card_w": 362, "card_h": 468, "col_gap": 28,
              "row_gap": 36, "card_pad": 32},
}


def build_tokens() -> dict:
    return {
        "schema_version": 1,
        "task_id": TASK,
        "path_base": "output_dir",
        "run_id": S.run_id(),
        "generator": "tmp/" + S.run_id() + "/_suite/gen/a12_pages.py",
        "colors": {
            "ink": {"hex": INK, "use": "主文字"},
            "ink_2": {"hex": INK2, "use": "副标题、网址"},
            "muted": {"hex": MUTED, "use": "卡片详情等辅助正文"},
            "faint": {"hex": FAINT, "use": "元信息标签"},
            "rule": {"hex": RULE, "use": "分隔线、卡片描边"},
            "rule_2": {"hex": RULE2, "use": "元信息列分隔"},
            "surface": {"hex": SURFACE, "use": "页面与卡片底色"},
            "zebra": {"hex": ZEBRA, "use": "元信息表格底色"},
            "band": {"hex": BAND, "use": "浅色分组底"},
            "accent": {"hex": ACCENT, "use": "卡片 ID 徽章、左侧强调条、顶部色条"},
            "accent_dark": {"hex": ACCENT_D, "use": "CTA 强调带、深色面板"},
            "accent_light": {"hex": ACCENT_L, "use": "深底副标题与网址"},
            "mint": {"hex": MINT, "use": "深底标签"},
            "panel_rule": {"hex": PANEL_RULE, "use": "深底分隔线"},
            "panel_numeral": {"hex": PANEL_NUM, "use": "深底大序号"},
            "deco_light": {"hex": DECO, "use": "浅底大序号"},
            "white": {"hex": WHITE, "use": "深底主文字"},
        },
        "typography": {
            "families": [CJK, MONO],
            "monospace_use": "日期、时间、网址、卡片 ID、序号用等宽字体",
            "line_height_ratio": 1.45,
            "line_height_basis": "探针 2 实测同一文本在不同盒高下墨迹跨度，"
                                 "饱和行距为 1.40–1.44 × 字号，取上界 1.45 做安全预算",
            "latin_advance_em": LATIN_EM,
            "latin_advance_basis": "desktop 56 px 标题「Structure / Vision」像素量测"
                                    "墨宽 473 px ÷ 18 字符 ÷ 56 px；初版按 0.55 em 估算"
                                    "偏低，正是它让 stage 72 px 被误判为放得下",
            "title_wrap_slack_pct": {
                "mobile": 22.7, "tablet": 44.8, "desktop": 11.96, "stage": 9.74},
            "title_wrap_slack_note": "各断点标题盒的余量（%），由 desktop 实测墨宽"
                                      "按字号线性外推：mobile 30 px→253 px / 328 盒，"
                                      "tablet 46 px→390 px / 704 盒，desktop 50 px→"
                                      "423 px / 480 盒，stage 64 px→539 px / 600 盒。"
                                      "check() 以墨宽估算 > 盒宽 92 % 为折行风险阈值",
            "scales_by_canvas": SCALES,
            "floors": {
                "mobile": {"body": 16, "card_title": 18},
                "tablet": {"body": 20, "main_title": 40},
                "desktop": {"body": 20, "main_title": 40},
                "stage": {"body": 20, "main_title": 40},
            },
        },
        "spacing": SPACING,
        "components": {
            "top_bar": {"desc": "顶部 accent 色条，宽度随画布缩放",
                        "variants": {"mobile": [56, 4], "tablet": [72, 5],
                                     "desktop": [72, 6], "stage": [88, 7]}},
            "mark": {"desc": "网址行前的方块图标位，纯装饰",
                     "sizes": {"mobile": 14, "tablet": 20}},
            "meta_table": {"desc": "日期/时间/地点三行，标签左对齐、数值右对齐；"
                                   "手机与平板为浅底带描边的整块，桌面与大屏为面板内"
                                   "三行无框；标签文字按断点取中文或英文，数值恒为"
                                   "输入原文", "variant_by_canvas": {
                "mobile": "boxed_left_right", "tablet": "boxed_left_right",
                "desktop": "plain_left_right", "stage": "plain_left_right"}},
            "cta_band": {"desc": "CTA 文本行；手机与平板为 accent_dark 实底白字，"
                                 "桌面与大屏为白底 accent_dark 字（面板已深）",
                         "height": {"mobile": 52, "tablet": 76, "desktop": 84,
                                    "stage": 100}},
            "section_label": {"desc": "「六大环节」+ 右对齐序号 06，卡片分组标题"},
            "card": {"desc": "白底 + 1px rule 描边 + 左侧 accent 强调条 + 等宽 "
                             "C1–C6 徽章 + 粗体标题 + 分隔线 + 辅助色详情 + "
                             "桌面/大屏可选大序号",
                     "parts_order": ["surface", "border", "accent_strip",
                                     "id_badge", "title", "divider", "detail",
                                     "deco_index"],
                     "strip_width": {"mobile": 3, "tablet": 4, "desktop": 4,
                                     "stage": 5}},
            "numeral": {"desc": "面板底部大号 06 数字，呼应六张卡片，纯装饰；"
                                "桌面 108px、大屏 132px",
                        "sizes": {"desktop": 108, "stage": 132}},
        },
    }


def build_content_map(canvases: list[Canvas], checks: list) -> dict:
    return {
        "schema_version": 1,
        "task_id": TASK,
        "path_base": "output_dir",
        "run_id": S.run_id(),
        "source_content": "tasks/A12-responsive-system/inputs/content.json",
        "coordinates": {"origin": "canvas_top_left", "x": "right", "y": "down",
                        "unit": "px", "box": "[left, top, right, bottom]"},
        "canvases": [{"id": c.name, "width": c.W, "height": c.H, "margin": c.M,
                      "output_png": c.name + ".png",
                      "output_dsl": c.name + ".snapshot"} for c in canvases],
        "card_id_map": {c["id"]: c["title"] for c in CONTENT["cards"]},
        "entries": [],
        "checks": checks,
        "notes": {
            "wrapping": "文本在固定宽容器内自动折行；折行只改排版不改文字，"
                        "无省略号、无缩写、无改写、无删句",
            "displayed_equals_original": True,
            "card_id_shown": "卡片 ID C1–C6 以等宽徽章印在图上，同时在此登记",
            "decorative_text": "「六大环节」与序号 06 / 01…06 为设计装饰文字，"
                               "不是输入内容，decorative=true 单独登记，"
                               "不计入「内容一字不丢」核对",
            "box_is_declared": "box 为 DSL 声明盒；实际墨迹盒由量测脚本另行写入",
        },
    }


def main() -> int:
    (TMP / "preview").mkdir(parents=True, exist_ok=True)
    (TMP / "gen").mkdir(parents=True, exist_ok=True)

    results, all_problems = [], []
    for cv in CANVASES:
        rep = cv.check()
        all_problems += rep["problems"]
        dsl = cv.dsl()
        for e in cv.entries:
            for bad in ("<", ">", "&"):
                assert bad not in e["text"], (cv.name, bad, e["text"])
        r = C.render(TASK, dsl, cv.name,
                     purpose="A12 四断点最终图：%s %dx%d" % (cv.name, cv.W, cv.H),
                     kind="render")
        rec = {"canvas": cv.name, "size": [cv.W, cv.H], "margin": cv.M,
               "entries": rep["entries"], "dsl_bytes": len(dsl.encode("utf-8")),
               "problems": rep["problems"], "request_id": r["request_id"],
               "http_status": r["status"]}
        if r["status"] == 200 and r["body"]:
            (OUT / (cv.name + ".png")).write_bytes(r["body"])
            (OUT / (cv.name + ".snapshot")).write_text(dsl, encoding="utf-8")
            (TMP / "preview" / (cv.name + ".png")).write_bytes(r["body"])
            rec.update({"response_bytes": len(r["body"]),
                        "started_at": r["log"].get("started_at"),
                        "ended_at": r["log"].get("ended_at"),
                        "elapsed_ms": r["log"].get("elapsed_ms")})
        else:
            rec["error"] = r["log"].get("error")
        results.append(rec)
        print("%-8s HTTP %-3s bytes=%-8s entries=%-3d problems=%d" % (
            cv.name, r["status"], r["log"].get("response_bytes"), rep["entries"],
            len(rep["problems"])))

    (OUT / "design-tokens.json").write_text(
        json.dumps(build_tokens(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")
    entries = []
    for cv in CANVASES:
        for e in cv.entries:
            entries.append({
                "canvas": cv.name, "field": e["field"], "card_id": e["card_id"],
                "original": e["text"], "displayed": e["text"],
                "box": [e["box"][0], e["box"][1], e["box"][0] + e["box"][2],
                        e["box"][1] + e["box"][3]],
                "box_w": e["box"][2], "box_h": e["box"][3],
                "font_size": e["font_size"], "family": e["family"],
                "align": e["align"], "letter_spacing": e["letter_spacing"],
                "decorative": e["decorative"], "complete": not e["decorative"],
                "est_width_px": round(est_w(e["text"], e["font_size"],
                                            e["family"] == MONO,
                                            e["letter_spacing"] or 0), 1),
                "tag": e["tag"]})
    cm = build_content_map(CANVASES, [])
    cm["entries"] = entries
    (OUT / "content-map.json").write_text(
        json.dumps(cm, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (TMP / "gen" / "a12_pages.json").write_text(
        json.dumps({"results": results, "problems": all_problems},
                   ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print("\nproblems total: %d" % len(all_problems))
    for p in all_problems:
        print("  -", p)
    print("tokens ->", S.rel(OUT / "design-tokens.json"))
    print("map    ->", S.rel(OUT / "content-map.json"))
    return 1 if all_problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
