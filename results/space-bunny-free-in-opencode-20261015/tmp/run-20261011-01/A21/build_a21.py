#!/usr/bin/env python
# A21 双尺寸发布海报：三轮共用的生成器。
# 启动基准：总任务根 (suite_root)。用法：python build_a21.py <round> [version]
#
# 【设计令牌】同一套令牌驱动两尺寸与三轮，保证「同一主色、字体层级、
# 可识别的 3–6 构件品牌图形」。第 3 轮只换主题与新增英文句，
# 不改品牌构件形态（round-02.md / round-03.md 的硬要求）。
#
# 【构图】竖版与横版分别构图，不是同一张缩放：
#   竖版 1080x1350 —— 纵向堆叠：顶部留白 → 品牌行 → 大构件 → 标题 → 日期 → 徽标 → 讲者 → 网址 → 底部留白
#   横版 1440x810  —— 左右分栏：左栏文字竖向序列，右侧大构件；上下留白带更窄
from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path

BASE = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
OUT = BASE / "outputs/run-20261011-01/A21"
DRAFTS = BASE / "tmp/run-20261011-01/A21/drafts"

PORTRAIT = (1080, 1350)
WIDE = (1440, 810)

# ---------------------------------------------------------------- 字宽（A14 实测标定）
def em_width(s: str, size: float) -> float:
    w = 0.0
    for ch in s:
        if ord(ch) > 0x2E80:
            w += 1.0
        elif ch == " ":
            w += 0.28
        elif ch.isdigit():
            w += 0.53
        elif ch.isupper():
            w += 0.70
        elif ch.islower():
            w += 0.60
        elif ch in ":;":
            w += 0.42
        elif ch in "/.":
            w += 0.40
        elif ch == "-":
            w += 0.50
        else:
            w += 0.45
    return w * size


# ---------------------------------------------------------------- 品牌构件（4 个核心构件）
BAR_DX = (0.0, 30.0, 60.0)      # 三层向右错位，unit = s
BAR_DY = (0.0, 68.0, 136.0)
BAR_W, BAR_H = 380.0, 44.0
DISC_D = 92.0
MARK_W = 456.0                   # BAR_DX[2] + BAR_W + DISC_D/2 - BAR_W/2 之外的实测外接宽
MARK_H = 180.0


def brand_mark(cx, cy, s, layers, disc):
    """3 层圆角条 + 1 枚光斑圆盘 = 4 个构件。

    条的圆角 = 高度的一半，端头为半圆；光斑圆盘叠在第二层条的右端，
    表达「叠在一起的光」。四构件在两尺寸与三轮之间形态完全一致，只做整体缩放与平移。
    """
    # 真实外接框宽 = BAR_DX[1] + BAR_W + DISC_D/2 - BAR_W/2 之右的最大值
    #  = max(BAR_DX[2]+BAR_W, BAR_DX[1]+BAR_W+DISC_D/2) = 456（单位 s）
    # 首版用 (BAR_W + BAR_DX[2])/2 = 440 居中，导致整体右偏 8px（2×1.02）到 10px（×1.30）。
    x0 = cx - MARK_W * s / 2
    y0 = cy - MARK_H * s / 2
    out = []
    for i, (dx, dy) in enumerate(zip(BAR_DX, BAR_DY)):
        out.append(
            f'<Positioned left="{x0 + dx * s:.2f}" top="{y0 + dy * s:.2f}" '
            f'width="{BAR_W * s:.2f}" height="{BAR_H * s:.2f}">'
            f'<Container width="{BAR_W * s:.2f}" height="{BAR_H * s:.2f}" '
            f'color="{layers[i]}" borderRadius="{BAR_H * s / 2:.2f}"/></Positioned>')
    dcx = x0 + BAR_DX[1] * s + BAR_W * s
    dcy = y0 + BAR_DY[1] * s + BAR_H * s / 2
    out.append(
        f'<Positioned left="{dcx - DISC_D * s / 2:.2f}" top="{dcy - DISC_D * s / 2:.2f}" '
        f'width="{DISC_D * s:.2f}" height="{DISC_D * s:.2f}">'
        f'<ClipOval><Container width="{DISC_D * s:.2f}" height="{DISC_D * s:.2f}" '
        f'color="{disc}"/></ClipOval></Positioned>')
    return "".join(out)


# ---------------------------------------------------------------- 主题
THEMES = {
    1: dict(bg="#0B1020", layers=["#4338CA", "#3730A3", "#312E81"], disc="#FBBF24",
            primary="#F8FAFC", secondary="#A5B4FC", accent="#FBBF24",
            rule="#312E81", badge_bg="#FFFFFF00", badge_bd="#4F46E5"),
    2: dict(bg="#0B1020", layers=["#4338CA", "#3730A3", "#312E81"], disc="#FBBF24",
            primary="#F8FAFC", secondary="#A5B4FC", accent="#FBBF24",
            rule="#312E81", badge_bg="#FFFFFF00", badge_bd="#4F46E5"),
    3: dict(bg="#F8FAFC", layers=["#6366F1", "#4F46E5", "#4338CA"], disc="#D97706",
            # accent 用 #9A3412 而非 #B45309：后者在 #F8FAFC 上只有 4.80:1，
            # 虽过 4.5 但余量太薄；前者 6.98:1。
            primary="#1E1B4B", secondary="#3730A3", accent="#9A3412",
            rule="#C7D2FE", badge_bg="#FFFFFF00", badge_bd="#1E1B4B"),
}

FONT_SEMI = "Inter Semi Bold,Noto Sans CJK SC"
FONT_MED = "Inter Medium,Noto Sans CJK SC"
FONT_MONO = "Inter,Noto Sans CJK SC"

# ---------------------------------------------------------------- 内容（三轮变化）
CONTENT = {
    1: dict(
        brand="叠光 Layerlight",
        title_lines=["让复杂信息变得清晰"],
        title_size=68,
        date="2026.11.07 19:30",
        badge="ONLINE LAUNCH",
        speakers="讲者：林川 / 苏言",
        url="layerlight.example.org",
        sponsor=None,
        attend=None,
        english=None,
    ),
    2: dict(
        brand="叠光 Layerlight",
        title_lines=["当所有信息都想成为标题：", "让复杂信息变得清晰的结构化方法"],
        title_size=52,
        date="2026.11.07 19:30",
        badge="ONLINE LAUNCH",
        speakers="讲者：林川 / 苏言",
        url="layerlight.example.org",
        sponsor="Northstar Research / 云构工具",
        attend="免费参加 · 无需报名",
        english=None,
    ),
    3: dict(
        brand="叠光 Layerlight",
        title_lines=["当所有信息都想成为标题：", "让复杂信息变得清晰的结构化方法"],
        title_size=52,
        date="2026.11.07 19:30",
        badge="ONLINE LAUNCH",
        speakers="讲者：林川 / 苏言",
        url="layerlight.example.org",
        sponsor="Northstar Research / 云构工具",
        attend="免费参加 · 无需报名",
        english="Clarity through structure",
    ),
}

REQUIRED_ALL = ("date", "badge", "speakers", "url")
SPONSOR_NOTE = "赞助方与参加方式自 round-02 引入，round-03 不得消失"


# ---------------------------------------------------------------- 图元
def rect(x, y, w, h, color, radius=0, border=None, bw=2):
    b = f' border="{bw} SOLID {border}"' if border else ""
    return (f'<Positioned left="{x:.2f}" top="{y:.2f}" width="{w:.2f}" height="{h:.2f}">'
            f'<Container width="{w:.2f}" height="{h:.2f}" color="{color}" '
            f'borderRadius="{radius}"{b}/></Positioned>')


def txt(t, x, y, w, h, size, color, family=FONT_MED, align=None, spacing=None):
    q = "'" if '"' in t else '"'
    at = f' fontSize="{size}" color="{color}" fontFamily="{family}"'
    # 服务端只接受 center/right/end 等枚举，left 是默认值，**不能**显式写
    # textAlign="left"（A21 首轮实测：Enum constant Alignment.left 不存在 → 400）。
    if align and align != "left":
        at += f' textAlign="{align}"'
    if spacing:
        at += f' letterSpacing="{spacing}"'
    return (f'<Positioned left="{x:.2f}" top="{y:.2f}" width="{w:.2f}" height="{h:.2f}">'
            f'<Text{at} text={q}{t}{q}/></Positioned>')


# ---------------------------------------------------------------- 版式
def build_portrait(rd):
    T = THEMES[rd]
    C = CONTENT[rd]
    W, H = PORTRAIT
    M = 84
    b = [rect(0, 0, W, H, T["bg"])]
    content = W - 2 * M
    texts = []          # (id, text, x, y, w, h, size, color, align)

    # 顶部预留带 0..168：不写任何待补文字，只用一条细分隔线界定可用区
    b.append(rect(M, 168, content, 2, T["rule"]))
    # 品牌行：小构件 + 字标
    ms = 0.30
    b.append(brand_mark(M + MARK_W * ms / 2, 214, ms, T["layers"], T["disc"]))
    bw_txt_x = M + MARK_W * ms + 24
    b.append(txt(C["brand"], bw_txt_x, 196, content - (bw_txt_x - M), 38, 32,
                 T["primary"], FONT_SEMI, spacing=1))
    texts.append(("brand", C["brand"], bw_txt_x, 196, content - (bw_txt_x - M), 38, 32,
                  T["primary"], "left"))

    # 主构件
    hs = 1.02 if rd == 1 else 0.96
    b.append(brand_mark(W / 2, 400, hs, T["layers"], T["disc"]))

    # 主标题
    ty = 560 if rd == 1 else 556
    lh = 1.34
    # 第 1 轮主标题 9 个汉字，76px 会顶到 912px 内容宽的 2/3，放到 68px 更稳
    # （仍是题面要求的 ≥56）。第 2、3 轮第二行 14 字，52px × 14 = 728px < 912。
    for i, line in enumerate(C["title_lines"]):
        y = ty + i * C["title_size"] * lh
        b.append(txt(line, M, y, content, C["title_size"] * lh, C["title_size"],
                     T["primary"], FONT_SEMI, align="CENTER"))
        texts.append((f"title-{i+1}", line, M, y, content, C["title_size"] * lh,
                      C["title_size"], T["primary"], "center"))

    y = ty + len(C["title_lines"]) * C["title_size"] * lh + 34
    b.append(txt(C["date"], M, y, content, 44, 36, T["accent"], FONT_SEMI, align="CENTER",
                 spacing=2))
    texts.append(("date", C["date"], M, y, content, 44, 36, T["accent"], "center"))
    y += 72          # 首版日期盒底与徽标顶只差 12px，实图上几乎粘在一起，放到 28px

    # 徽标 ONLINE LAUNCH
    bw_ = 360
    bh = 62
    bx = (W - bw_) / 2
    b.append(rect(bx, y, bw_, bh, T["badge_bg"], bh / 2, T["badge_bd"], 2))
    b.append(txt(C["badge"], bx, y + 12, bw_, 40, 30, T["primary"], FONT_SEMI,
                 align="CENTER", spacing=6))
    texts.append(("badge", C["badge"], bx, y + 12, bw_, 40, 30, T["primary"], "center"))
    y += bh + 36

    b.append(txt(C["speakers"], M, y, content, 40, 30, T["secondary"], FONT_MED,
                 align="CENTER"))
    texts.append(("speakers", C["speakers"], M, y, content, 40, 30, T["secondary"], "center"))
    y += 52

    if C["sponsor"]:
        b.append(txt(C["sponsor"], M, y, content, 36, 26, T["secondary"], FONT_MED,
                     align="CENTER"))
        texts.append(("sponsor", C["sponsor"], M, y, content, 36, 26, T["secondary"],
                      "center"))
        y += 44
    if C["attend"]:
        b.append(txt(C["attend"], M, y, content, 36, 26, T["accent"], FONT_MED,
                     align="CENTER"))
        texts.append(("attend", C["attend"], M, y, content, 36, 26, T["accent"], "center"))
        y += 44
    if C["english"]:
        b.append(txt(C["english"], M, y, content, 36, 26, T["primary"], FONT_SEMI,
                     align="CENTER", spacing=2))
        texts.append(("english", C["english"], M, y, content, 36, 26, T["primary"],
                      "center"))
        y += 44

    b.append(txt(C["url"], M, y, content, 38, 28, T["primary"], FONT_MONO,
                 align="CENTER", spacing=1))
    texts.append(("url", C["url"], M, y, content, 38, 28, T["primary"], "center"))
    content_bottom = y + 38

    # 底部预留带
    rule_y = max(content_bottom + 36, H - 232)
    b.append(rect(M, rule_y, content, 2, T["rule"]))
    reserve = {"top_px": 168, "bottom_px": H - rule_y,
               "top_note": "分隔线之上的 168px 为真实可用扩展区，未写任何待补文字",
               "bottom_note": "分隔线之下的底部条带为真实可用扩展区，未写任何待补文字"}
    assert reserve["bottom_px"] >= 100, f"底部预留不足：{reserve['bottom_px']}"
    return b, texts, reserve, (M, 168, W - M, rule_y)


def build_wide(rd):
    T = THEMES[rd]
    C = CONTENT[rd]
    W, H = WIDE
    M = 80
    COL = 800          # 780 时第 2 轮标题第二行估算宽度正好 780 = 框宽，余量不足 2px
    b = [rect(0, 0, W, H, T["bg"])]

    TOP, BOT = 96, H - 96
    b.append(rect(M, TOP, W - 2 * M, 2, T["rule"]))

    ms = 0.26
    b.append(brand_mark(M + MARK_W * ms / 2, TOP + 44, ms, T["layers"], T["disc"]))
    bx_txt = M + MARK_W * ms + 22
    b.append(txt(C["brand"], bx_txt, TOP + 26, COL - (bx_txt - M), 36, 30, T["primary"],
                 FONT_SEMI, spacing=1))
    texts = [("brand", C["brand"], bx_txt, TOP + 26, COL - (bx_txt - M), 36, 30,
              T["primary"], "left")]

    # 右栏主构件：放在左栏右缘之外，尺度按「不越过画布 48px 安全边」反推
    hs = min(1.00, (W - 48 - (M + COL + 62)) / MARK_W)
    hcx = (M + COL + 62 + (W - 48)) / 2
    b.append(brand_mark(hcx, 430, hs, T["layers"], T["disc"]))

    y = TOP + 104
    lh = 1.34
    for i, line in enumerate(C["title_lines"]):
        b.append(txt(line, M, y + i * C["title_size"] * lh, COL, C["title_size"] * lh,
                     C["title_size"], T["primary"], FONT_SEMI, align="left"))
        texts.append((f"title-{i+1}", line, M, y + i * C["title_size"] * lh, COL,
                      C["title_size"] * lh, C["title_size"], T["primary"], "left"))
    # 横版左栏的文字段数逐轮增加（6 → 7 → 8），810px 高度下段间距必须随轮次收紧，
    # 否则第 3 轮的底部扩展带会被吃掉。间隔按「盒高（含行距）之外的净空」定义。
    gap = {1: 16, 2: 12, 3: 7}[rd]
    tgap = {1: 20, 2: 14, 3: 10}[rd]
    y += len(C["title_lines"]) * C["title_size"] * lh + tgap

    for key, size, color, fam, sp in (
            ("date", 32, T["accent"], FONT_SEMI, 2),
            ("speakers", 26, T["secondary"], FONT_MED, None),
            ("sponsor", 24, T["secondary"], FONT_MED, None),
            ("attend", 24, T["accent"], FONT_MED, None),
            ("english", 26, T["primary"], FONT_SEMI, 2),
            ("url", 26, T["primary"], FONT_MONO, 1)):
        v = C.get(key)
        if not v:
            continue
        h = size * 1.45
        b.append(txt(v, M, y, COL, h, size, color, fam, align="left", spacing=sp))
        texts.append((key, v, M, y, COL, h, size, color, "left"))
        y += h + gap

    # 徽标放在左栏底部，与右侧构件互不重叠
    bw_, bh = 330, 56
    b.append(rect(M, y, bw_, bh, T["badge_bg"], bh / 2, T["badge_bd"], 2))
    b.append(txt(C["badge"], M, y + 11, bw_, 36, 28, T["primary"], FONT_SEMI,
                 align="CENTER", spacing=6))
    texts.append(("badge", C["badge"], M, y + 11, bw_, 36, 28, T["primary"], "center"))
    content_bottom = y + bh

    rule_y = max(content_bottom + 28, H - 128)
    assert H - rule_y >= 96, f"底部预留不足：{H - rule_y}"
    b.append(rect(M, rule_y, W - 2 * M, 2, T["rule"]))
    reserve = {"top_px": TOP, "bottom_px": H - rule_y,
               "top_note": "分隔线之上的 96px 为真实可用扩展区，未写任何待补文字",
               "bottom_note": "分隔线之下的底部条带为真实可用扩展区，未写任何待补文字"}
    return b, texts, reserve, (M, TOP, W - M, rule_y)


def build(rd, which):
    b, texts, reserve, frame = (build_portrait(rd) if which == "portrait"
                                else build_wide(rd))
    size = PORTRAIT if which == "portrait" else WIDE
    marks = _mark_boxes(rd, which)
    chk = check_texts(texts, which, marks, rd)
    dsl = (f'<Snapshot type="png">\n<Container width="{size[0]}" height="{size[1]}" '
           f'color="{THEMES[rd]["bg"]}"><Stack fit="EXPAND">{"".join(b)}</Stack></Container>'
           f'\n</Snapshot>\n')
    return dsl, texts, reserve, frame, chk


def _mark_boxes(rd, which):
    """按生成时的真实几何算出两处品牌构件的外接框，供碰撞检查使用。"""
    if which == "portrait":
        M, W = 84, PORTRAIT[0]
        ms, hs = 0.30, (1.02 if rd == 1 else 0.96)
        return {"brand-row": (M, 214 - MARK_H * ms / 2, MARK_W * ms, MARK_H * ms),
                "hero": (W / 2 - MARK_W * hs / 2, 400 - MARK_H * hs / 2,
                         MARK_W * hs, MARK_H * hs)}
    M, W, COL = 80, WIDE[0], 800
    ms = 0.26
    hs = min(1.00, (W - 48 - (M + COL + 62)) / MARK_W)
    hcx = (M + COL + 62 + (W - 48)) / 2
    return {"brand-row": (M, 96 + 44 - MARK_H * ms / 2, MARK_W * ms, MARK_H * ms),
            "hero": (hcx - MARK_W * hs / 2, 430 - MARK_H * hs / 2,
                     MARK_W * hs, MARK_H * hs)}


def check_texts(texts, which, marks, rd):
    """断言：正文 ≥24、主标题下限、估算宽度不超框、文字不与品牌构件相撞、
    构件不出画布且离边缘 ≥48px、任意两个文字盒不相交。"""
    W, H = PORTRAIT if which == "portrait" else WIDE
    issues = []

    # 主标题下限：第 1 轮 ≥56；第 2、3 轮按 round-02.md 的 ≥48，且 ≤3 行
    need = 56 if rd == 1 else 48
    title_lines = [t for t in texts if t[0].startswith("title")]
    need = 56 if rd == 1 else 48
    assert len(title_lines) <= 3, f"标题行数 {len(title_lines)} > 3"
    for tid, t, x, y, w, h, sz, color, al in title_lines:
        if sz < need:
            issues.append(f"{tid} 主标题字号 {sz} < {need}")

    boxes = []
    for tid, t, x, y, w, h, sz, color, al in texts:
        if sz < 24:
            issues.append(f"{tid} 字号 {sz} < 24")
        est = em_width(t, sz)
        if est > w - 2:
            issues.append(f"{tid} 估算宽度 {est:.1f} > 框宽 {w:.2f}")
        if x < 0 or x + w > W or y < 0 or y + h > H:
            issues.append(f"{tid} 文字框越出画布")
        boxes.append((tid, [x, y, x + w, y + h]))

    # 文字盒两两不相交
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            a, b = boxes[i][1], boxes[j][1]
            if not (a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1]):
                issues.append(f"{boxes[i][0]} 与 {boxes[j][0]} 文字框相交")

    # 品牌构件：不出画布、离边 ≥48、不与任何文字盒相交
    for name, (mx, my, mw, mh) in marks.items():
        if mx < 48 or my < 48 or mx + mw > W - 48 or my + mh > H - 48:
            issues.append(f"构件 {name} 外接框 [{mx:.1f},{my:.1f},{mx+mw:.1f},{my+mh:.1f}] "
                          f"离画布边 < 48")
        for tid, bx in boxes:
            if not (bx[2] <= mx or mx + mw <= bx[0] or bx[3] <= my or my + mh <= bx[1]):
                issues.append(f"构件 {name} 与文字 {tid} 相交")

    assert not issues, f"{which} 检查失败：{issues}"
    return {"title_min_px": need, "title_lines": len(title_lines),
            "min_body_px": min(b[6] for b in texts if not b[0].startswith("title")),
            "text_boxes": [{"id": b[0], "box": [round(v, 2) for v in b[1]]} for b in boxes],
            "marks": {k: [round(v, 2) for v in b] for k, b in marks.items()}}


def main() -> None:
    rd = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    ver = sys.argv[2] if len(sys.argv) > 2 else "v1"
    d = DRAFTS / f"round-{rd:02d}"
    d.mkdir(parents=True, exist_ok=True)
    out = OUT / f"round-{rd:02d}"
    out.mkdir(parents=True, exist_ok=True)
    all_texts = {}
    for which in ("portrait", "wide"):
        dsl, texts, reserve, frame, chk = build(rd, which)
        (d / f"a21-{which}-{ver}.snapshot").write_text(dsl, encoding="utf-8")
        all_texts[which] = {"texts": texts, "reserve": reserve, "frame": frame,
                            "checks": chk}
        print(f"round{rd} {which}: bytes={len(dsl.encode())} texts={len(texts)} "
              f"reserve top={reserve['top_px']} bottom={reserve['bottom_px']} "
              f"title={chk['title_lines']}行@{chk['title_min_px']}px "
              f"minbody={chk['min_body_px']}px")
    (d / f"texts-{ver}.json").write_text(
        json.dumps(all_texts, ensure_ascii=False, indent=2, default=list),
        encoding="utf-8")


if __name__ == "__main__":
    main()