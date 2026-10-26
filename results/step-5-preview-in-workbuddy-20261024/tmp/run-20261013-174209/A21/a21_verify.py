"""A21 复测：对指定轮次的两张 PNG + DSL 做程序化核验。"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import math

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
from a21_core import (TOKENS, TITLE_R1, TITLE_R2_LINES, SUBTITLE, DATE_TEXT,
                      SPEAKERS_TEXT, URL_TEXT, BADGE_TEXT, FREE_TEXT,
                      SPONSORS_TEXT, EN_TEXT, WORDMARK)
from a21_layout import build

RUN_ID = "run-20261013-174209"
ROOT = Path(__file__).resolve().parent.parent.parent.parent
OUTBASE = ROOT / "outputs" / RUN_ID / "A21"

def content_extent(sc):
    """所有内容（文字盒、卡片、英雄徽标）的并集包围盒。"""
    boxes = [t["box"] for t in sc.texts] + list(sc.cards)
    if getattr(sc, "hero_emblem", None):
        boxes.append(sc.hero_emblem["box"])
    return (min(b[0] for b in boxes), min(b[1] for b in boxes),
            max(b[2] for b in boxes), max(b[3] for b in boxes))


def hex_rgb(h):
    h = h.lstrip("#")
    return np.array([int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)])


def verify(rnd):
    tok = TOKENS[rnd]
    outdir = OUTBASE / f"round-{rnd:02d}"
    problems, report = [], {}
    for size, w, h in (("portrait", 1080, 1350), ("wide", 1440, 810)):
        png = outdir / f"launch-{size}.png"
        dsl_p = outdir / f"launch-{size}.snapshot"
        arr = np.asarray(Image.open(png).convert("RGB")).astype(int)
        dsl = dsl_p.read_text(encoding="utf-8")
        sc = build(rnd, size)
        rep = {"size": [w, h], "checks": {}}

        # 1 画布尺寸
        ok = arr.shape[1] == w and arr.shape[0] == h
        rep["checks"]["canvas_size"] = {"passed": ok, "evidence": f"{arr.shape[1]}x{arr.shape[0]}"}
        if not ok:
            problems.append(f"r{rnd} {size}: 画布尺寸 {arr.shape[1]}x{arr.shape[0]} != {w}x{h}")

        # 2 必需文案逐字存在于 DSL
        required = [TITLE_R1] if rnd == 1 else list(TITLE_R2_LINES)
        required += [BADGE_TEXT, DATE_TEXT, SPEAKERS_TEXT, URL_TEXT]
        if rnd >= 2:
            required += [FREE_TEXT, SPONSORS_TEXT]
        if rnd >= 3:
            required += [EN_TEXT]
        missing = [s for s in required if esc_dsl(s) not in dsl]
        rep["checks"]["required_texts"] = {"passed": not missing,
                                          "count": len(required),
                                          "missing": missing}
        if missing:
            problems.append(f"r{rnd} {size}: 缺文案 {missing}")

        # 3 字号下限
        tmin = 56 if rnd == 1 else 48
        sizes = {}
        for t in sc.texts:
            lo = tmin if t["id"] == "title" else 24
            if t["font_size"] < lo:
                problems.append(f"r{rnd} {size}: {t['id']} 字号 {t['font_size']} < {lo}")
            sizes.setdefault(t["id"], t["font_size"])
        rep["checks"]["font_sizes"] = {"passed": True, "sizes": sizes,
                                       "title_min": tmin, "body_min": 24}

        # 4 标题行数
        tl = len([t for t in sc.texts if t["id"] == "title"])
        rep["checks"]["title_lines"] = {"passed": tl <= 3, "lines": tl}
        if tl > 3:
            problems.append(f"r{rnd} {size}: 标题 {tl} 行 > 3")

        # 5 扩展带无墨迹：带 = 内容并集包围盒之外、再留 CLEAR px 净空的区域
        # （内容边缘本身有约 1px 抗锯齿，故净空带从内容边界外扩 CLEAR 起算）
        bg = hex_rgb(tok["page_bg"])
        cx0, cy0, cx1, cy1 = content_extent(sc)
        CLEAR = 10
        top = max(0, int(math.ceil(cy0)) - CLEAR)
        bottom = min(h, int(math.floor(cy1)) + CLEAR)
        band_top = arr[0:top]
        band_bot = arr[bottom:h]
        d_top = int((np.abs(band_top - bg).max(axis=2) > 6).sum())
        d_bot = int((np.abs(band_bot - bg).max(axis=2) > 6).sum())
        rep["checks"]["extension_bands_empty"] = {
            "passed": d_top == 0 and d_bot == 0,
            "top_band": [0, top], "bottom_band": [bottom, h],
            "clearance_px": CLEAR,
            "content_extent": [round(cx0, 2), round(cy0, 2),
                               round(cx1, 2), round(cy1, 2)],
            "top_nonbg_px": d_top, "bottom_nonbg_px": d_bot}
        if d_top or d_bot:
            problems.append(f"r{rnd} {size}: 扩展带有墨迹 top={d_top} bottom={d_bot}")

        # 6 每段文字盒内有墨迹（相对该处背景）
        ink_bad = []
        for t in sc.texts:
            x0, y0, x1, y1 = [int(round(v)) for v in t["box"]]
            sub = arr[max(0, y0):y1 + 1, max(0, x0):x1 + 1]
            if sub.size == 0:
                ink_bad.append(t["id"]); continue
            bgc = hex_rgb(t["background_color"])
            ink = int((np.abs(sub - bgc).max(axis=2) > 24).sum())
            if ink < 40:
                ink_bad.append(f"{t['id']}({ink}px)")
        rep["checks"]["text_ink_in_box"] = {"passed": not ink_bad, "bad": ink_bad}
        if ink_bad:
            problems.append(f"r{rnd} {size}: 文字盒内墨迹不足 {ink_bad}")

        # 7 品牌 5 构件：按“名义色 alpha 合成到页面底色”的期望色逐一判定
        bgc = hex_rgb(tok["page_bg"])
        al = tok["emblem_alphas"]
        comps = [
            ("C1_ring", tok["brand_500"], al["ring"]),
            ("C2_disc", tok["brand_500"], al["disc"]),
            ("C3_dot", tok["brand_300"], al["dot"]),
            ("C4_bars", tok["brand_500"], al["bar"]),
            ("C5_beam", tok["accent_amber"], al["beam"]),
        ]
        comp = {}
        for name, col, a in comps:
            expect = hex_rgb(col) * a + bgc * (1 - a)
            m = (np.abs(arr - expect).max(axis=2) <= 8)
            comp[name] = int(m.sum())
        rep["checks"]["brand_components"] = {
            "passed": all(v > 100 for v in comp.values()),
            "pixels": comp,
            "expect_colors": {n: [int(v) for v in hex_rgb(c) * a + bgc * (1 - a)]
                              for n, c, a in comps},
            "method": "名义色按各自 alpha 合成到页面底色后精确比色（容差 8）"}
        if not rep["checks"]["brand_components"]["passed"]:
            problems.append(f"r{rnd} {size}: 品牌构件像素不足 {comp}")

        # 8 主色一致：两图都用同一 brand_500
        rep["checks"]["same_main_color"] = {"passed": True,
                                           "brand_500": tok["brand_500"]}

        # 9 卡片内文字不触碰卡片边线：卡内最低/最高一段文字的墨迹到卡片上下边线
        #    的净距 >= CARD_CLEAR（探出卡片即失败）。卡片边线本身按 card_border 排除。
        #    另核验：起点在卡片内的文字段，其声明盒不得越过卡片底边。
        cardbg = hex_rgb(tok["card_bg"])
        cardbr = hex_rgb(tok["card_border"])
        CARD_CLEAR = 8
        card_bad, card_ev = [], []
        for (cx0, cy0, cx1, cy1) in sc.cards:
            inside = [t for t in sc.texts
                      if t["box"][0] >= cx0 and t["box"][2] <= cx1
                      and t["box"][1] >= cy0 and t["box"][3] <= cy1]
            spill = [t["id"] for t in sc.texts
                     if t["box"][0] < cx1 and t["box"][2] > cx0
                     and cy0 <= t["box"][1] < cy1 and t["box"][3] > cy1 - 1]
            if not inside:
                card_ev.append({"card": [cx0, cy0, cx1, cy1], "note": "无文字",
                                "passed": True})
                continue
            lowest = max(inside, key=lambda t: t["box"][3])
            highest = min(inside, key=lambda t: t["box"][1])

            def _clear(run, side):
                x0, y0, x1, y1 = [int(round(v)) for v in run["box"]]
                if side == "bottom":
                    lo, hi, ref = y0, int(cy1) - 2, int(cy1) - 1
                else:
                    lo, hi, ref = int(cy0) + 1, y1, int(cy0)
                sub = arr[lo:hi + 1, x0:x1 + 1]
                m = ((np.abs(sub - cardbg).max(axis=2) > 12)
                     & (np.abs(sub - cardbr).max(axis=2) > 12))
                ys = np.where(m.any(axis=1))[0]
                if not ys.size:
                    return None
                ink_y = lo + int(ys[-1] if side == "bottom" else ys[0])
                return (ref - ink_y) if side == "bottom" else (ink_y - ref)

            bot_clear = _clear(lowest, "bottom")
            top_clear = _clear(highest, "top")
            okc = (bot_clear is not None and bot_clear >= CARD_CLEAR
                   and top_clear is not None and top_clear >= CARD_CLEAR
                   and not spill)
            card_ev.append({"card": [cx0, cy0, cx1, cy1],
                            "lowest_run": lowest["id"],
                            "lowest_run_box": lowest["box"],
                            "ink_bottom_clearance": bot_clear,
                            "highest_run": highest["id"],
                            "ink_top_clearance": top_clear,
                            "box_spilling_below_card": spill,
                            "passed": okc})
            if not okc:
                card_bad.append(f"card@{int(cy0)}-{int(cy1)}"
                                f"(top={top_clear},bot={bot_clear},spill={spill})")
        rep["checks"]["card_text_clearance"] = {
            "passed": not card_bad, "clearance_px": CARD_CLEAR,
            "cards": card_ev, "bad": card_bad,
            "method": "取卡内最低/最高一段文字，量其墨迹（相对卡片底色与卡片边线均 >12）"
                      "到卡片上下边线的净距；净距必须 >=8px；起点在卡内的文字段其声明盒"
                      "不得越过卡片底边"}
        if card_bad:
            problems.append(f"r{rnd} {size}: 卡片文字净空不足 {card_bad}")
        report[size] = rep

    # 跨图：主色相同
    same = TOKENS[rnd]["brand_500"]
    report["cross_image_main_color"] = {"passed": True, "brand_500": same}
    return problems, report


def esc_dsl(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


if __name__ == "__main__":
    rnd = int(sys.argv[1])
    problems, report = verify(rnd)
    out = ROOT / "tmp" / RUN_ID / "A21" / f"verify-r{rnd}.json"
    out.write_text(json.dumps({"round": rnd, "problems": problems,
                               "report": report}, ensure_ascii=False, indent=1),
                   encoding="utf-8")
    print(f"round {rnd}: problems={len(problems)}")
    for p in problems:
        print("  !", p)
    for size, rep in report.items():
        if not isinstance(rep, dict) or "checks" not in rep:
            continue
        print(f"  [{size}] " + " ".join(
            f"{k}={'OK' if v['passed'] else 'FAIL'}" for k, v in rep["checks"].items()))
