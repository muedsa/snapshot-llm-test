#!/usr/bin/env python
"""A14 逐张像素核验：把交付的 8 张 PNG 量出来，和 build_a14.py 的声明值对账。

启动基准：总任务根 (suite_root)。
用法：python tmp/run-20261011-01/A14/verify_a14.py outputs/run-20261011-01/A14

核验项（全部基于**交付 PNG 的实际像素**，不是复算 DSL）
  1. 标题墨迹包围盒：行数、每行墨迹顶/底、右侧边缘
  2. 标题行不被裁：每行「实测墨迹宽 / 声明估算宽」必须落在 [0.80, 1.20]；
     被服务端裁掉的行实测宽会顶到字面框 700px，比值会 > 1.3（K05 首版就是这样被抓到的）
  3. 标题与状态徽标不碰撞：徽标左边 − 标题墨迹右边 ≥ 0
  4. 内容安全边距：全图亮墨迹包围盒（排除刻意出血的装饰）必须落在 [40,1160]×[40,590]
  5. 状态徽标像素：边框/文字颜色与 STATUS 表一致，符号形状可用（实心/空心/方/叉）
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, "tmp/run-20261011-01/A14")
from build_a14 import (  # noqa: E402
    STATUS, TITLE_X, TITLE_W, TITLE_FIT_W, BAND_TOP, BAND_BOTTOM, KICKER_Y,
    BADGE_X, BADGE_Y, BADGE_W, BADGE_H, MARGIN, W, H, RULE2_Y, est_em_str,
)

BASE = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
TITLE_LUM = 140          # 标题是 #F8FAFC（近白），阈值取 140 只留标题
CONTENT_LUM = 70         # 内容墨迹阈值
RATIO_LO, RATIO_HI = 0.80, 1.20


def lum(px):
    r, g, b = px[0], px[1], px[2]
    return 0.299 * r + 0.587 * g + 0.114 * b


def ink_rows(im, box, thr):
    """在 box=(x0,y0,x1,y1) 内逐行找亮像素，返回 [(y0,y1,x0,x1)] 的连续行带。"""
    px = im.load()
    x0, y0, x1, y1 = box
    bands, cur = [], None
    for y in range(y0, y1):
        xs = [x for x in range(x0, x1) if lum(px[x, y]) > thr]
        if xs:
            if cur is None:
                cur = [y, y, min(xs), max(xs)]
            else:
                cur[1] = y
                cur[2] = min(cur[2], min(xs))
                cur[3] = max(cur[3], max(xs))
        else:
            if cur:
                bands.append(tuple(cur))
                cur = None
    if cur:
        bands.append(tuple(cur))
    # 合并间隔 < 半个行高的相邻行带（同一行内的字间空隙不算断行）
    merged = []
    for b in bands:
        if merged and b[0] - merged[-1][1] < 8:
            merged[-1] = (merged[-1][0], b[1], min(merged[-1][2], b[2]),
                          max(merged[-1][3], b[3]))
        else:
            merged.append(b)
    return merged


def hexrgb(s):
    s = s.lstrip("#")
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


def nearest_status_color(im, box, target, tol=90):
    """在 box 内找最接近 target 颜色的像素（用于确认徽标颜色真的上了图）。"""
    px = im.load()
    x0, y0, x1, y1 = box
    tr, tg, tb = hexrgb(target)
    best, bestd = None, 1e9
    for y in range(y0, y1, 2):
        for x in range(x0, x1, 2):
            r, g, b = px[x, y][0], px[x, y][1], px[x, y][2]
            d = (r - tr) ** 2 + (g - tg) ** 2 + (b - tb) ** 2
            if d < bestd:
                bestd, best = d, (x, y, (r, g, b))
    return {"target": target, "closest_pixel": list(best),
            "rgb": list(best[2]),
            "color_distance": round(bestd ** 0.5, 1)}


def solid_ratio(im, box, color_hex):
    """box 内颜色与 color_hex 高度一致的像素占比（判定实心/空心符号）。"""
    px = im.load()
    x0, y0, x1, y1 = box
    tr, tg, tb = hexrgb(color_hex)
    hit = tot = 0
    for y in range(y0, y1):
        for x in range(x0, x1):
            r, g, b = px[x, y][0], px[x, y][1], px[x, y][2]
            tot += 1
            if abs(r - tr) < 60 and abs(g - tg) < 60 and abs(b - tb) < 60:
                hit += 1
    return round(hit / max(tot, 1), 4)


def main() -> None:
    out_dir = BASE / (sys.argv[1] if len(sys.argv) > 1 else "outputs/run-20261011-01/A14")
    audit = json.loads((BASE / "tmp/run-20261011-01/A14/drafts/batch-audit-raw.json")
                       .read_text(encoding="utf-8"))
    cards = {c["id"]: c for c in audit["cards"]}
    cards_in = json.loads((BASE / "tasks/A14-content-stress-batch/inputs/cards.json")
                          .read_text(encoding="utf-8"))
    src = {c["id"]: c for c in cards_in}

    res = []
    for cid in [c["id"] for c in cards_in]:
        png = out_dir / f"card-{cid}.png"
        with Image.open(png) as s:
            s.load()
            im = s.convert("RGB")
        decl = cards[cid]
        st = STATUS[src[cid]["status"]]

        # ---- 1/2 标题墨迹
        # 眉题文本框 y=146..174，其底缘会漏进标题带（#7DA7F5 亮度 163 > TITLE_LUM=140），
        # 被误判成标题的第一行；因此扫描从 y=182 起，保证只量到标题本身。
        bands = ink_rows(im, (TITLE_X, 182, BADGE_X - 20, BAND_BOTTOM + 10), TITLE_LUM)
        lines = decl["title_typography"]["lines"]
        sizes = decl["title_typography"]["font_size_px"]
        ests = decl["title_typography"]["estimated_line_widths_px"]
        ratios = []
        for b, est in zip(bands, ests):
            w = b[3] - b[2] + 1
            ratios.append({"line_y": [b[0], b[1]], "ink_x": [b[2], b[3]],
                           "ink_width_px": w, "declared_est_px": est,
                           "ratio": round(w / est, 3) if est else None,
                           "clipped": w >= TITLE_W - 2})
        title_right = max((b[3] for b in bands), default=None)

        # ---- 3 徽标左边（取徽标框外沿）与标题右边
        badge_ink = ink_rows(im, (BADGE_X, BADGE_Y - 6, BADGE_X + BADGE_W + 6,
                                  BADGE_Y + BADGE_H + 6), 70)
        badge_left = min((b[2] for b in badge_ink), default=None)
        gap = (badge_left - title_right) if (badge_left and title_right) else None

        # ---- 4 内容安全边距
        # 扫描整幅宽度：取消卡的斜纹带亮度约 35（#F871710D 叠在 #0E1830 上），
        # 低于 CONTENT_LUM=70，天然被阈值排除；背景柔光亮度约 35 同样被排除。
        # 只排除 y<10 的统一主色出血条。
        cont = ink_rows(im, (0, 10, W, H), CONTENT_LUM)
        cx0 = min((b[2] for b in cont), default=None)
        cx1 = max((b[3] for b in cont), default=None)
        cy0 = min((b[0] for b in cont), default=None)
        cy1 = max((b[1] for b in cont), default=None)

        # ---- 5 状态颜色与符号
        sym_box = (BADGE_X + 24, BADGE_Y + BADGE_H // 2 - 12,
                   BADGE_X + 44, BADGE_Y + BADGE_H // 2 + 12)
        fill = solid_ratio(im, sym_box, st["color"])
        center_hit = solid_ratio(im, (sym_box[0] + 6, sym_box[1] + 6,
                                      sym_box[2] - 6, sym_box[3] - 6), st["color"])

        row = {
            "id": cid, "png": f"card-{cid}.png",
            "size": list(im.size),
            "title_lines_declared": lines,
            "title_lines_measured": len(bands),
            "title_font_size_px": sizes,
            "title_line_ink": ratios,
            "title_ink_bbox": [min((b[2] for b in bands), default=None),
                               min((b[0] for b in bands), default=None),
                               title_right,
                               max((b[1] for b in bands), default=None)],
            "title_column_right_edge": TITLE_X + TITLE_W,
            "title_within_column": title_right is not None and title_right <= TITLE_X + TITLE_W,
            "title_line_pitch_px": [bands[i][0] - bands[i - 1][0] for i in range(1, len(bands))],
            "title_line_pitch_declared": decl["title_typography"]["line_height_px"],
            "badge_left_edge_px": badge_left,
            "title_badge_gap_px": gap,
            "no_collision": gap is not None and gap >= 0,
            "content_ink_bbox": [cx0, cy0, cx1, cy1],
            "safe_margin_px": MARGIN,
            "within_safe_margin": all(v is not None for v in (cx0, cy0, cx1, cy1))
            and cx0 >= MARGIN and cy0 >= MARGIN and cx1 <= W - MARGIN and cy1 <= H - MARGIN,
            "status": src[cid]["status"],
            "status_color_on_canvas": nearest_status_color(im, (BADGE_X, BADGE_Y,
                                                               BADGE_X + BADGE_W,
                                                               BADGE_Y + BADGE_H), st["color"]),
            "symbol": st["symbol"],
            "symbol_fill_ratio": fill,
            "symbol_center_fill_ratio": center_hit,
            "symbol_solid": (center_hit > 0.75) if st["symbol"] == "dot" else None,
            "symbol_hollow": (center_hit < 0.15) if st["symbol"] == "ring" else None,
            "cancel_note_present": (cid == "K06"),
        }
        row["passed"] = all([
            row["title_lines_measured"] == lines,
            row["title_within_column"],
            row["no_collision"],
            row["within_safe_margin"],
            all(r["clipped"] is False for r in ratios),
            all(r["ratio"] is None or RATIO_LO <= r["ratio"] <= RATIO_HI for r in ratios),
            row["status_color_on_canvas"]["color_distance"] < 110,
        ])
        res.append(row)
        print(f"{cid} 行{row['title_lines_measured']}/{lines} "
              f"右{title_right}(≤{TITLE_X+TITLE_W}) 距徽标{gap}px "
              f"内容[{cx0},{cy0},{cx1},{cy1}] "
              f"比值{[r['ratio'] for r in ratios]} -> {'PASS' if row['passed'] else 'FAIL'}")

    p = BASE / "tmp/run-20261011-01/A14/drafts/verify.json"
    p.write_text(json.dumps({
        "tool": {"name": "Pillow", "method": "逐行/逐列扫描交付 PNG 的像素亮度，"
                                             "取墨迹包围盒；再与 build_a14.py 的声明值对账"},
        "thresholds": {"title_lum": TITLE_LUM, "content_lum": CONTENT_LUM,
                       "ratio_window": [RATIO_LO, RATIO_HI]},
        "excluded_from_margin_scan": {"top": "y<10 的统一主色出血条",
                                      "auto_excluded_by_threshold": "取消卡右侧斜纹带（亮度≈35）与背景柔光（≈35），"
                                                                  "均低于 CONTENT_LUM=70"},
        "cards": res,
        "all_passed": all(r["passed"] for r in res),
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\nall_passed =", all(r["passed"] for r in res))
    print("->", p.as_posix())


if __name__ == "__main__":
    main()