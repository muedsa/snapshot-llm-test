"""A21 第三轮：浅色主题 + 对比度审计。

方法：
  1. 渲染带文字的终版图（outputs/round-03/）。
  2. 渲染“去文字辅助图”（保留徽标/卡片/pill/分隔线等全部背景层，仅去掉 Text 节点）
     到临时目录，用于取每段文字下方真实的合成背景。
  3. 对每段文字：在终版图中取其声明盒内“与文字本色接近（排除抗锯齿边缘）”的核心字形像素，
     逐个到辅助图中取该位置背景色，按 WCAG 相对亮度公式算对比度，取最小值（最差位置）。
  4. contrast-audit.json 记录完整文字清单 + 每图至少 6 处详细样本（含最差位置）。
"""
from __future__ import annotations
import json
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "_suite"))

from render import Log, render, suite_root, rel
from a21_core import TOKENS
from a21_layout import build
from a21_run import run_round

RUN_ID = "run-20261013-174209"
ROOT = suite_root()
TMP = ROOT / "tmp" / RUN_ID / "A21"
OUT = ROOT / "outputs" / RUN_ID / "A21"
THRESHOLD = 4.5


def hex_rgb(h):
    h = h.lstrip("#")
    return np.array([int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)])


def lin(c):
    c = c / 255.0
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def lum(rgb):
    l = lin(np.asarray(rgb, dtype=float))
    return float(0.2126 * l[0] + 0.7152 * l[1] + 0.0722 * l[2])


def contrast(fg, bg):
    l1, l2 = lum(fg), lum(bg)
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)


def main():
    # 1) 渲染终版 + 去文字辅助图
    renders = run_round(3, notext=True)
    problems = []

    audit = {
        "schema_version": 1, "task_id": "A21", "path_base": "output_dir",
        "round": 3,
        "formula": {
            "srgb_linearize": "c=c/255; c<=0.04045 ? c/12.92 : ((c+0.055)/1.055)^2.4",
            "relative_luminance": "L = 0.2126*R_lin + 0.7152*G_lin + 0.0722*B_lin",
            "contrast": "(max(L_fg,L_bg)+0.05)/(min(L_fg,L_bg)+0.05)",
            "threshold": THRESHOLD,
            "rounding": "使用未舍入结果判阈值",
            "background_source": ("去文字辅助渲染图（保留全部背景层，仅移除 Text 节点）"
                                  "中同一像素处的实际颜色；文字本体取终版图中与文字"
                                  "名义色相差 <=12 的核心字形像素（排除抗锯齿边缘）"),
        },
        "images": [],
        "evidence": [],
        "visual_regression": (
            "第三轮在第二轮版式上只做主题反转与一处新增：页面/卡片由深色（#0B1020/#151B2E）"
            "改为浅色（#F6F7FB/#FFFFFF），文字由浅色改为深色，品牌 5 构件几何与相对位置不变、"
            "仅色值与不透明度随主题切换（brand_500 #6366F1→#4F46E5 等），并在网址上方新增英语短句"
            "“Clarity through structure”。版式（标题三行、徽标行、元信息卡三行、右栏徽标+网址）"
            "与第二轮一致，因此视觉回归仅限于配色与新增一行英语句；赞助方、日期、讲者、"
            "ONLINE LAUNCH、网址与品牌图形均未消失或移位。"
            "另有一处横版元信息卡修正：第二轮横版卡高写死 164px，新增赞助方一行后该行文字墨迹"
            "会探出卡片底边约 16px（压在页面底色上），第三轮起横版卡高改为按行数计算"
            "（20 + 各行 size*1.5 + 行距 14 + 20 = 200px），卡片向下增高 36px，"
            "右栏英雄徽标与网址随之下移 18px 并重新居中；竖版卡高（196px）本就留足净空，未改动。"),
    }

    for size in ("portrait", "wide"):
        sc = build(3, size)
        real = np.asarray(Image.open(
            OUT / "round-03" / f"launch-{size}.png").convert("RGB")).astype(int)
        aux = np.asarray(Image.open(
            TMP / f"r3-{size}-notext.png").convert("RGB")).astype(int)
        h, w = real.shape[:2]
        tok = TOKENS[3]

        img_entry = {
            "image": f"round-03/launch-{size}.png",
            "size": [w, h],
            "aux_render": {"path_base": "suite_root",
                           "path": f"tmp/{RUN_ID}/A21/r3-{size}-notext.png",
                           "note": "去文字辅助渲染：保留徽标/卡片/pill/分隔线，仅移除 Text 节点"},
            "text_runs": [],
            "detailed_samples": [],
        }

        for t in sc.texts:
            fg = hex_rgb(t["color"])
            x0, y0, x1, y1 = [int(round(v)) for v in t["box"]]
            # 核心字形像素：与文字名义色差 <=12（排除抗锯齿边缘的部分覆盖像素）
            sub = real[max(0, y0 - 2):y1 + 3, max(0, x0 - 2):x1 + 3]
            core = (np.abs(sub - fg).max(axis=2) <= 12)
            ys, xs = np.nonzero(core)
            if len(ys) == 0:
                problems.append(f"{size} {t['id']}: 盒内未找到核心字形像素")
                continue
            # 逐像素取辅助图背景并计算对比度，保留最差
            worst = None
            for yy, xx in zip(ys.tolist(), xs.tolist()):
                by, bx = max(0, y0 - 2) + yy, max(0, x0 - 2) + xx
                bgpx = tuple(int(v) for v in aux[by, bx])
                c = contrast(fg, bgpx)
                if worst is None or c < worst["contrast"]:
                    worst = {"contrast": c, "x": bx, "y": by,
                             "bg": bgpx, "fg": [int(v) for v in fg]}
            run = {
                "id": t["id"], "text": t["text"],
                "box": t["box"], "font_size": t["font_size"],
                "font_family": t["font_family"], "lines": t["lines"],
                "foreground_color": t["color"],
                "declared_background": t["background_color"],
                "core_glyph_px": int(len(ys)),
                "glyph_ink_box": [
                    int(max(0, y0 - 2) + xs.min()), int(max(0, y0 - 2) + ys.min()),
                    int(max(0, y0 - 2) + xs.max()), int(max(0, y0 - 2) + ys.max())],
                "min_contrast": worst["contrast"],
                "min_contrast_sample": worst,
                "method": ("核心字形像素（与名义色差<=12）逐个取去文字辅助图同位置背景，"
                           "按 WCAG 相对亮度公式计算，取最小值"),
                "passed": bool(worst["contrast"] >= THRESHOLD),
            }
            if not run["passed"]:
                problems.append(f"{size} {t['id']}: 最差对比度 "
                                f"{worst['contrast']:.3f} < {THRESHOLD}")
            img_entry["text_runs"].append(run)
            img_entry["detailed_samples"].append({
                "text_id": t["id"], "text": t["text"],
                "sample_type": "worst_position",
                "pixel_xy": [worst["x"], worst["y"]],
                "foreground": worst["fg"], "background": list(worst["bg"]),
                "L_foreground": lum(worst["fg"]), "L_background": lum(worst["bg"]),
                "contrast": worst["contrast"],
                "calculation": (f"L_fg={lum(worst['fg']):.6f}, "
                                f"L_bg={lum(worst['bg']):.6f}, "
                                f"({max(lum(worst['fg']), lum(worst['bg'])) + 0.05:.6f})/"
                                f"({min(lum(worst['fg']), lum(worst['bg'])) + 0.05:.6f})"
                                f" = {worst['contrast']:.4f}"),
                "passed": bool(worst["contrast"] >= THRESHOLD),
            })

        # 汇总
        cr = [r["min_contrast"] for r in img_entry["text_runs"]]
        img_entry["summary"] = {
            "text_run_count": len(img_entry["text_runs"]),
            "min_contrast": min(cr) if cr else None,
            "max_contrast": max(cr) if cr else None,
            "all_passed": all(r["passed"] for r in img_entry["text_runs"]),
            "detailed_sample_count": len(img_entry["detailed_samples"]),
            "threshold": THRESHOLD,
        }
        audit["images"].append(img_entry)
        audit["evidence"].append({
            "path_base": "suite_root",
            "path": f"tmp/{RUN_ID}/A21/r3-{size}-notext.png",
            "role": f"{size} 去文字辅助渲染（真实背景来源）",
            "request_id": next((r["notext_render"]["request_id"] for r in renders
                                if r["size"] == size), None),
        })

    audit["summary"] = {
        "images": len(audit["images"]),
        "total_text_runs": sum(i["summary"]["text_run_count"] for i in audit["images"]),
        "min_contrast_overall": min(i["summary"]["min_contrast"]
                                    for i in audit["images"]),
        "all_passed": all(i["summary"]["all_passed"] for i in audit["images"]),
        "detailed_samples_total": sum(i["summary"]["detailed_sample_count"]
                                      for i in audit["images"]),
        "threshold": THRESHOLD,
        "problems": problems,
    }
    (OUT / "round-03" / "contrast-audit.json").write_text(
        json.dumps(audit, ensure_ascii=False, indent=1), encoding="utf-8")

    print("contrast audit written")
    for i in audit["images"]:
        s = i["summary"]
        print(f"  [{i['image']}] runs={s['text_run_count']} "
              f"min={s['min_contrast']:.3f} max={s['max_contrast']:.3f} "
              f"all_passed={s['all_passed']} samples={s['detailed_sample_count']}")
    print("problems:", len(problems))
    for p in problems:
        print("  !", p)
    return problems


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
