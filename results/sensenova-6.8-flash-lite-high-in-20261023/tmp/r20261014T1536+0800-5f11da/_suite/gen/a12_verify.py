"""A12 四张最终图的真实像素核验：逐条声明文字盒量测实际墨迹。

与 a12_measure.py 的区别：这里不手写量测窗口，直接以 content-map.json 里登记的
box 作为量测窗口。依据是探针 2 确立的裁切契约——文字超出盒会被裁进盒内，不会
溢出到盒外——所以盒内的墨迹就是该条目的全部墨迹，不必额外扩窗去探溢出。

判据（第一版把「墨迹贴左边」当裁切，误报了 108 项，已按下列理由改正）：
  对齐的墨迹天然贴一侧边——左对齐的 CJK 首字左字腔≈0，所以 ink_left == box_left
  是常态而非裁切。真正会丢字的裁切是纵向的：文字先按宽度折行，行数超出盒高时
  多余行被切掉。而且被切的那一版在几何上看不出来——一行 72 px 的墨高本来就
  小于 104 px 的盒高——所以必须靠两条独立证据：
    (a) 折行能力：按墨宽估算（留 8 % 余量）推折行数，与盒高能容纳的行数对照；
    (b) 墨宽÷字号一致性：同一字符串在四个断点上该比值近似恒定，丢字会让它塌陷。
  字号一致性只对 ink_w ≥ 40 px 的条目生效：两位小数字符如「C1」的墨宽是十几到
  几十的整数，四舍五入就能造成 9 % 的相对离散，那只是量化噪声不是缺陷。

核验项：
  1 墨迹存在   文字真的渲染出来了，不是空白
  2 出盒       墨迹越过声明盒边界（违反裁切契约，说明登记坐标错了）
  3 纵向裁切   墨迹贴住盒顶/盒底，或折行能力不足
  4 安全边距   实际墨迹是否越出画布安全边距
  5 墨迹重叠   非装饰文字墨迹两两相交；装饰序号另计
  6 字号下限   各断点 body / card_title / main_title 下限
  7 字号一致   ink_w ÷ font_size 跨断点离散 < 4 %（ink_w ≥ 40）

用法：SNAPSHOT_RUN_ID=<rid> python -I tmp/<rid>/_suite/gen/a12_verify.py
"""

from __future__ import annotations

import json
import math
import sys
from collections import defaultdict
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve()
ROOT = HERE.parents[4]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(HERE.parent))
import suite as S  # noqa: E402
import a12_measure as M  # noqa: E402
from a12_pages import MONO, build_tokens, est_w, lh  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

TASK = "A12"
OUT, TMP = S.task_dirs(TASK)
CM = OUT / "content-map.json"

WRAP_SLACK = 0.92      # 折行估算的盒宽系数，与 a12_pages.check() 一致
RATIO_MIN_INK = 40     # 墨宽低于此值不判字号一致性（整数量化噪声）
RATIO_SPREAD_MAX = 4.0  # ink_w÷字号 的允许相对离散（%）
FLOORS = build_tokens()["typography"]["floors"]


def floor_for(canvas: str, field: str) -> int | None:
    """该字段在该断点的字号下限；装饰文字不设下限。"""
    f = FLOORS[canvas]
    if field == "title":
        return f.get("main_title")
    if field == "cards[].title":
        return f.get("card_title")
    return f.get("body")


def est_lines(text: str, size: int, mono: bool, box_w: int) -> int:
    """按实测字宽估算这条文字在盒宽内需折几行（留 8 % 余量）。"""
    return max(1, math.ceil(est_w(text, size, mono) / (box_w * WRAP_SLACK)))


def main() -> int:
    cm = json.loads(CM.read_text(encoding="utf-8"))
    png_paths = {c["id"]: OUT / c["output_png"] for c in cm["canvases"]}

    failures: list[str] = []
    warnings: list[str] = []
    per_canvas: dict[str, dict] = {}
    spans: dict[str, list[tuple[str, int, int]]] = defaultdict(list)

    for cvid, img_path in png_paths.items():
        im = Image.open(img_path).convert("RGB")
        cv_entries = [e for e in cm["entries"] if e["canvas"] == cvid]
        cv_margin = next(c["margin"] for c in cm["canvases"] if c["id"] == cvid)
        W, H = im.width, im.height

        measured: list[dict] = []
        for e in cv_entries:
            l, t, r, b = e["box"]
            w, h = r - l, b - t
            ink = M.ink_bbox(im, [l, t, w, h])
            mono = e["family"] == MONO
            lines = est_lines(e["original"], e["font_size"], mono, w)
            capable = max(1, h // lh(e["font_size"]))
            rec = {"tag": e["tag"], "field": e["field"], "text": e["original"],
                   "box": [l, t, w, h], "font_size": e["font_size"],
                   "align": e["align"], "decorative": e["decorative"],
                   "ink": ink, "est_lines": lines, "capable_lines": capable}
            if ink is None:
                failures.append(f"{cvid} {e['tag']}「{e['original']}」无墨迹（未渲染）")
                measured.append(rec)
                continue
            clear = {"left": ink[0] - l, "right": r - ink[2],
                     "top": ink[1] - t, "bottom": b - ink[3]}
            rec.update({"ink_w": ink[2] - ink[0] + 1, "ink_h": ink[3] - ink[1] + 1,
                        "clear": clear})
            # 2 出盒
            for side, d in clear.items():
                if d < 0:
                    failures.append(f"{cvid} {e['tag']} 墨迹 {ink} 越过声明盒 {e['box']} "
                                    f"（{side} {d:.0f}px）")
            # 3 纵向裁切
            if clear["top"] < 1 or clear["bottom"] < 1:
                failures.append(f"{cvid} {e['tag']}「{e['original']}」墨迹贴盒"
                                f"{'顶' if clear['top'] < 1 else ''}"
                                f"{'底' if clear['bottom'] < 1 else ''}"
                                f"（clear top={clear['top']:.0f} bottom="
                                f"{clear['bottom']:.0f}）→ 纵向裁切")
            if lines > capable:
                failures.append(f"{cvid} {e['tag']}「{e['original']}」需 {lines} 行，"
                                f"盒高 {h} 只容 {capable} 行（lh={lh(e['font_size'])}）"
                                f"→ 折行后会被裁")
            if 0 < clear["bottom"] < 3 or 0 < clear["right"] < 3:
                warnings.append(f"{cvid} {e['tag']} 墨迹贴近"
                                f"{'底' if 0 < clear['bottom'] < 3 else '右'}边"
                                f" {min(clear['bottom'], clear['right']) if 0 < clear['right'] < 3 else clear['bottom']:.0f}px")
            # 4 安全边距
            if (ink[0] < cv_margin - 1 or ink[2] > W - cv_margin + 1
                    or ink[1] < cv_margin - 1 or ink[3] > H - cv_margin + 1):
                failures.append(f"{cvid} {e['tag']} 墨迹 {ink} 越出安全边距 {cv_margin}"
                                f"（画布 {W}x{H}）")
            # 6 字号下限
            fl = floor_for(cvid, e["field"])
            if not e["decorative"] and fl is not None and e["font_size"] < fl:
                failures.append(f"{cvid} {e['tag']} 字号 {e['font_size']} 低于下限 {fl}"
                                f"（field={e['field']}）")
            # 7 取样
            if not e["decorative"] and rec["ink_w"] >= RATIO_MIN_INK:
                spans[e["original"]].append((cvid, rec["ink_w"], e["font_size"]))
            measured.append(rec)

        # 5 墨迹重叠
        nd = [(m["tag"], m["ink"]) for m in measured
              if not m["decorative"] and m["ink"] is not None]
        dec = [(m["tag"], m["ink"]) for m in measured
               if m["decorative"] and m["ink"] is not None]
        for i in range(len(nd)):
            for j in range(i + 1, len(nd)):
                ov = M.overlap(nd[i][1], nd[j][1])
                if ov:
                    failures.append(f"{cvid} 文字墨迹重叠 {nd[i][0]} × {nd[j][0]} 区域 {ov}")
        for i in range(len(nd)):
            for _, di in dec:
                ov = M.overlap(nd[i][1], di)
                if ov:
                    failures.append(f"{cvid} 文字与装饰序号墨迹重叠 {nd[i][0]} × 装饰 区域 {ov}")

        worst = min((v for m in measured if "clear" in m
                     for k, v in m["clear"].items()
                     for _ in [0] if k in ("top", "bottom")), default=None)
        per_canvas[cvid] = {"png": str(img_path), "size_px": [W, H],
                            "margin": cv_margin, "entries": len(cv_entries),
                            "measured": len(measured),
                            "min_vertical_clearance_px": worst,
                            "measured_entries": measured}
        print("%-8s %dx%d entries=%-3d 测得=%-3d 纵向最小余量=%s" % (
            cvid, W, H, len(cv_entries), len(measured),
            ("%.0f px" % worst) if worst is not None else "-"))

    # 7 字号一致性
    print("\n同一字符串跨断点的 ink_w ÷ 字号（应近似恒定；ink_w ≥ %d）：" % RATIO_MIN_INK)
    for text, rows in sorted(spans.items(), key=lambda kv: -max(w for _, w, _ in kv[1])):
        if len(rows) < 4:
            continue
        ratios = [(c, round(w / s, 3)) for c, w, s in rows]
        rs = [r for _, r in ratios]
        spread = (max(rs) - min(rs)) / (sum(rs) / len(rs)) * 100
        bad = spread > RATIO_SPREAD_MAX
        print("  %-24s %s  离散 %5.1f%%%s" % (
            text, " ".join("%s:%s" % rr for rr in ratios), spread,
            "  ← 异常" if bad else ""))
        if bad:
            failures.append(f"字号一致性异常：{text!r} 的 ink_w÷字号 离散 "
                            f"{spread:.1f}% > {RATIO_SPREAD_MAX}%（可能折行或丢字）")

    report = {"schema_version": 1, "task_id": TASK, "path_base": "output_dir",
              "run_id": S.run_id(), "source_content_map": "content-map.json",
              "method": {
                  "window": "以 content-map.json 登记的 box 为量测窗口；依据裁切契约"
                            "（文字超出盒会被裁进盒内），盒内墨迹即该条目全部墨迹",
                  "ink_threshold": "与区域众数色的欧氏距离 > 40",
                  "wrap_slack": WRAP_SLACK,
                  "ratio_min_ink_px": RATIO_MIN_INK,
                  "ratio_spread_max_pct": RATIO_SPREAD_MAX,
                  "line_height_ratio": 1.45,
                  "note": "对齐墨迹贴一侧边是常态（CJK 首字左字腔≈0），不作裁切判据；"
                          "裁切判定改用纵向余量 + 折行能力 + 跨断点墨宽比值三条独立证据",
                  "limits": "像素量测只确认墨迹几何，无法逐字识别字形；文字保真由 "
                            "a12_pages.check() 的逐字段原文串比对承担",
              },
              "canvases": per_canvas,
              "ratio_check": {t: [{"canvas": c, "ink_w": w, "font_size": s,
                                   "ratio": round(w / s, 3)}
                                  for c, w, s in rows]
                              for t, rows in sorted(spans.items(),
                                                    key=lambda kv: -max(w for _, w, _ in kv[1]))
                              if len(rows) >= 4},
              "failures": failures, "warnings": warnings}
    outp = TMP / "gen" / "a12_verify.json"
    outp.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8")

    print("\n失败 %d 项，警告 %d 项" % (len(failures), len(warnings)))
    for f in failures:
        print("  FAIL", f)
    print("out", S.rel(outp))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
