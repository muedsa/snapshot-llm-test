"""A21 round-03 提交前无网络干跑门。

不发出任何请求。构造两份浅底 DSL → 断言合法 → 打印元素表 → 逐条校验：
  1. 每行标题的 advance 不超出文本盒宽度（CJK advance = 1em，纯算术，防折行）
  2. 信息栈里赞助方与报名状态牌仍在，位置在网址牌之下（不得消失）
  3. 新增英语短句在网址牌之上、字号 ≥24、advance 不超盒宽
  4. 中文长标题 ≤3 行、字号 ≥48
  5. 上下扩展空间 ≥70
  6. 每个文字元素的墨迹 bbox 不与 orb_core / orb_halo 的填充区域相交
     （保证"实际合成背景"就是页面底或牌子底，而不是球体或辉光叠层）
  7. 全部文字色都是浅色主题的 token 值，没有残留深底的近白文字色
  8. 每个文字色对页面底与纯白牌子底的对比度都 ≥4.5（WCAG 相对亮度公式，
     未舍入判定）——这只是静态预核；最终判定以去文字辅助渲染的实测合成色为准
  9. 必需文案（含第二轮的赞助方、报名状态、日期、讲者、ONLINE LAUNCH、网址）齐全

用法：python a21_dryrun_r3.py
"""
from __future__ import annotations

import pathlib
import sys
import unicodedata

HERE = pathlib.Path(__file__).resolve()
SUITE_ROOT = HERE.parents[4]
RUN_ID = HERE.parents[2].name
TMP = SUITE_ROOT / "tmp" / RUN_ID / "A21"
GEN = HERE.parent
sys.path.insert(0, str(GEN))

import a21_core as K   # noqa: E402
import a21_layouts as L  # noqa: E402

NAMES = {"portrait": "launch-portrait", "wide": "launch-wide"}
MIN_ALL = 24
TITLE_MIN = 48
CONTRAST_MIN = 4.5
MARGIN_MIN = 70
TITLE_FULL = "当所有信息都想成为标题：让复杂信息变得清晰的结构化方法"

# 逐条出现的文案；标题是分行渲染的，另按拼接校验
REQUIRED = [
    ("sponsors", "Northstar Research / 云构工具"),
    ("badge", "免费参加 · 无需报名"),
    ("date", "2026.11.07 19:30"),
    ("kicker", "ONLINE LAUNCH"),
    ("speakers", "讲者：林川 / 苏言"),
    ("url", "layerlight.example.org"),
    ("clarity_en", "Clarity through structure"),
]


def _lin(c8: float) -> float:
    c = c8 / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _lum(hexs: str) -> float:
    h = hexs.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return (0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b))


def contrast(fg: str, bg: str) -> float:
    la, lb = _lum(fg), _lum(bg)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def advance_px(text: str, size: int, spacing: int | None = None) -> int:
    """字宽估算：CJK 全角字 1em，ASCII 按 0.55em；letterSpacing 逐字累加。"""
    total = 0
    for ch in text:
        total += size if unicodedata.east_asian_width(ch) in ("W", "F") \
            else size * 0.55
    if spacing:
        total += spacing * (len(text) - 1)
    return int(round(total))


def overlap(a, b):
    x0, y0 = max(a[0], b[0]), max(a[1], b[1])
    x1, y1 = min(a[2], b[2]), min(a[3], b[3])
    return x0 < x1 and y0 < y1


def main() -> int:
    for st in (sys.stdout, sys.stderr):
        if hasattr(st, "reconfigure"):
            st.reconfigure(encoding="utf-8")

    cfg = L.default_cfg_r3()
    col = cfg["colors"]
    fails = []
    texts_seen: dict[str, list[str]] = {}
    title_lines: dict[str, int] = {}

    for key, builder in L.BUILDERS_R3.items():
        cv = builder(cfg)
        slug = NAMES[key]
        dsl = cv.dsl()
        K.assert_dsl_wellformed(dsl)
        (TMP / "dsl").mkdir(parents=True, exist_ok=True)
        (TMP / "dsl" / ("r03-%s.dryrun.snapshot" % slug)).write_bytes(
            dsl.encode("utf-8"))
        W, H = L.SIZES[key]
        print("== %s  %dx%d  dsl_bytes=%d  elements=%d =="
              % (slug, W, H, len(dsl.encode("utf-8")), len(cv.layout)))

        texts = [e for e in cv.layout if e.get("kind") == "text"]
        shapes = [e for e in cv.layout if e.get("kind") != "text"]
        orb_core = next((e["box"] for e in cv.layout
                         if e.get("kind") == "orb_core"), None)
        orb_halo = next((e["box"] for e in cv.layout
                         if e.get("kind") == "orb_halo"), None)
        plate = next((e["box"] for e in cv.layout
                      if e.get("kind") == "url_plate"), None)

        print("     %-14s %-12s %5s %8s %s" % ("role", "text", "size", "adv/box", "color"))
        for e in cv.layout:
            if e.get("kind") == "text":
                adv = advance_px(e["text"], e["fontSize"], e.get("letterSpacing"))
                boxw = e["box"][2] - e["box"][0]
                print("     %-14s %-14s %5d %6d/%-5d %s"
                      % (e["role"], e["text"][:14], e["fontSize"],
                         adv, boxw, e["color"]))
                if adv > boxw:
                    fails.append("%s %s advance %d > 盒宽 %d（会折行）"
                                 % (slug, e["role"], adv, boxw))
                if e["fontSize"] < MIN_ALL:
                    fails.append("%s %s 字号 %d < %d"
                                 % (slug, e["role"], e["fontSize"], MIN_ALL))
                texts_seen.setdefault(e["text"], []).append(slug)
        print("     形状元素 %d 个：%s"
              % (len(shapes), ", ".join(sorted({e["kind"] for e in shapes}))))

        # ---- 墨迹 bbox（保守估计）与球体填充区域的相交检查 ----
        if orb_core:
            print("     orb_core %s  orb_halo %s" % (orb_core, orb_halo))
        for e in texts:
            box = e["box"]
            size = e["fontSize"]
            text = e["text"]
            # 逐字累加：CJK 全角字 advance 1em、墨迹占 advance 的 0.95；
            # ASCII（数字、拉丁）advance 0.55em、墨迹占 0.98。
            # 混排不能整串乘一个系数，否则日期/网址会被严重高估。
            ink_right = box[0] + 0.5
            for ch in text:
                adv = size if unicodedata.east_asian_width(ch) in ("W", "F") \
                    else size * 0.55
                ink_right += adv * (0.95 if adv == size else 0.98)
            ink = [box[0] + int(size * 0.02),
                   box[1] - int(size * 0.12),
                   int(ink_right),
                   box[1] + int(size * 0.86)]
            for lbl, area in (("orb_core", orb_core), ("orb_halo", orb_halo)):
                if area and overlap(ink, area):
                    fails.append("%s %s 墨迹 %s 与 %s %s 相交"
                                 % (slug, e["role"], ink, lbl, area))

        # ---- 网址牌 / 牌子族与球体填充区域 ----
        for e in shapes:
            if e.get("kind") in ("url_plate", "orb_halo", "orb_core"):
                continue
            if orb_core and e["kind"] == "url_plate" and overlap(e["box"], orb_core):
                fails.append("%s url_plate %s 与 orb_core %s 相交"
                             % (slug, e["box"], orb_core))

        # ---- 信息栈次序：英语短句在网址牌之上、赞助方与状态牌在其下 ----
        def top_of(role):
            hits = [e for e in texts if e["role"] == role]
            return hits[0]["box"][1] if hits else None

        t_clarity = top_of("clarity_en")
        t_spon = top_of("sponsors")
        t_badge = top_of("badge")
        if plate is None or t_clarity is None:
            fails.append("%s 缺网址牌或英语短句" % slug)
        else:
            if not (t_clarity < plate[1] < t_clarity + 600):
                fails.append("%s 英语短句 top=%s 不在网址牌 top=%s 之上"
                             % (slug, t_clarity, plate[1]))
            if t_spon is None:
                fails.append("%s 赞助方消失" % slug)
            elif not t_spon > plate[3]:
                fails.append("%s 赞助方 top=%s 未在网址牌之下 %s"
                             % (slug, t_spon, plate))
            if t_badge is None:
                fails.append("%s 报名状态牌消失" % slug)
            elif not t_badge > plate[3]:
                fails.append("%s 报名状态牌 top=%s 未在网址牌之下"
                             % (slug, t_badge))

        # ---- 标题行数与字号 ----
        tl = [e for e in texts if e["role"].startswith("title_line")]
        tfs = {e["fontSize"] for e in tl}
        if len(tl) > 3:
            fails.append("%s 标题 %d 行 > 3" % (slug, len(tl)))
        if any(fs < TITLE_MIN for fs in tfs):
            fails.append("%s 标题字号 %s < %d" % (slug, tfs, TITLE_MIN))
        joined = "".join(e["text"] for e in sorted(
            tl, key=lambda z: z["box"][1]))
        if joined != TITLE_FULL:
            fails.append("%s 标题分行拼接 %r != 需求整句 %r"
                         % (slug, joined, TITLE_FULL))
        texts_seen.setdefault("title_full", []).append(joined)
        title_lines[slug] = len(tl)

        # ---- 扩展空间 ----
        top = min(e["box"][1] for e in cv.layout if e["kind"] == "text")
        bot = max(e["box"][3] for e in cv.layout if e["kind"] == "text")
        if top < MARGIN_MIN:
            fails.append("%s 顶部空间 %d < %d" % (slug, top, MARGIN_MIN))
        if H - bot < MARGIN_MIN:
            fails.append("%s 底部空间 %d < %d" % (slug, H - bot, MARGIN_MIN))
        print("     扩展空间 上 %d / 下 %d | 标题 %d 行 字号 %s"
              % (top, H - bot, len(tl), sorted(tfs)))

        # ---- 文字色：不得残留深底主题的近白/近青文字色 ----
        for e in texts:
            if e["color"] not in set(col.values()):
                fails.append("%s %s 文字色 %s 不在浅底 token 内"
                             % (slug, e["role"], e["color"]))

    # ---- 静态对比度预核（未舍入）----
    print("\n== 静态对比度预核（对比页面底 %s 与牌子底 %s）=="
          % (col["bg_deep"], col["bg_panel"]))
    roles = {}
    for e in L.BUILDERS_R3["portrait"](cfg).layout:
        if e.get("kind") == "text":
            roles[e["role"]] = e["color"]
    worst = 1e9
    for role, fg in sorted(roles.items()):
        c_page = contrast(fg, col["bg_deep"])
        c_plate = contrast(fg, col["bg_panel"])
        m = min(c_page, c_plate)
        worst = min(worst, m)
        print("     %-14s %-9s  页面底 %7.4f  牌子底 %7.4f" % (role, fg, c_page, c_plate))
    print("     最小值 %.4f（阈值 %.1f）" % (worst, CONTRAST_MIN))
    if worst < CONTRAST_MIN:
        fails.append("静态对比度最小值 %.4f < %.1f" % (worst, CONTRAST_MIN))

    # ---- 必需文案齐全（含标题的分行拼接）----
    print("\n== 必需文案 ==")
    tfs = sorted(set(texts_seen.get("title_full", [])))
    if tfs == [TITLE_FULL]:
        print("     %-12s 竖版 %d 行 / 横版 %d 行，两处分行拼接逐字等于需求整句"
              % ("title_full", title_lines[NAMES["portrait"]],
                 title_lines[NAMES["wide"]]))
    else:
        fails.append("标题分行拼接不符：%s" % tfs)
    for cid, want in REQUIRED:
        got = sorted(set(texts_seen.get(want, [])))
        if not got:
            fails.append("必需文案 %s 未出现" % cid)
        else:
            print("     %-12s -> %s" % (cid, ", ".join(got)))

    print("\n" + ("干跑门通过（%d 项检查，无失败）" % 9
                  if not fails else "干跑门失败："))
    for f in fails:
        print("  ✗ " + f)
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
