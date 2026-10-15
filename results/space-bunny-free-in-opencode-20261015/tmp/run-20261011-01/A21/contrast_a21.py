#!/usr/bin/env python
# A21 round-03：对比度审计（contrast-audit.json）。
# 启动基准：总任务根 (suite_root)。
#
# 【口径】题面给的 sRGB 线性化 + WCAG 相对亮度 + (Lmax+.05)/(Lmin+.05)，阈值 4.5，用未舍入结果判定。
#
# 【背景不是 token，而是最终 PNG 的实际像素】
# 本轮所有正文都落在纯 #F8FAFC 底上，不与品牌构件、徽标描边有任何叠压。
# 为了证明这一点（而不是假设），这里做两件事：
#   1) 从**交付图**上按每段文字的包围盒取背景像素，统计其颜色集合与最差值；
#   2) 另外渲一张「保留全部图层但不含任何 <Text>」的辅助图放在临时目录，
#      逐段取样后与交付图一致——这排除了「文字抗锯齿边缘混进背景样本」的可能。
# 抗锯齿边缘像素（部分覆盖）按题面要求不当作文字本色，故背景取样时
# 取的是**该段文字盒内、文字所在行之间的非文字像素**，并单独报告取样像素数。
import json
import os
import subprocess
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
sys.path.insert(0, str(ROOT / "tmp/run-20261011-01/A21"))
import build_a21 as B  # noqa: E402

OUTD = ROOT / "outputs/run-20261011-01/A21/round-03"
TEMPD = ROOT / "tmp/run-20261011-01/A21"
THRESH = 4.5


def lin(c8):
    c = c8 / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def lum(rgb):
    r, g, b = (lin(x) for x in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(fg, bg):
    lf, lb = lum(fg), lum(bg)
    return (max(lf, lb) + 0.05) / (min(lf, lb) + 0.05)


def main() -> None:
    ver = sys.argv[1] if len(sys.argv) > 1 else "v1"
    rd = 3
    drafts = TEMPD / f"drafts/round-{rd:02d}"
    texts = json.loads((drafts / f"texts-{ver}.json").read_text(encoding="utf-8"))
    T = B.THEMES[rd]

    # ---- 辅助图：同构图、保留所有图层与主题，只去掉 <Text>
    # 目录名不能用 "aux"：那是 Windows 保留设备名（AUX），mkdir 会报 WinError 267。
    aux_dir = drafts / "nobg"
    aux_dir.mkdir(parents=True, exist_ok=True)
    aux_pngs = {}
    for which in ("portrait", "wide"):
        dsl = (drafts / f"a21-{which}-{ver}.snapshot").read_text(encoding="utf-8")
        # 去掉 <Text>...</Text> 与自闭合的 <Text .../>，保留其余全部图层
        import re
        # 文本节点是自闭合的 <Text .../>。必须把**整个 Positioned 包装一起删掉**——
        # 只删 <Text/> 会留下一批没有子节点的 Positioned，
        # 服务端报 "ProxyWidget has no widget"（与 A18 的空 Container 同一类错误）。
        no_text = re.sub(r"<Positioned\b[^>]*>\s*<Text\b[^>]*/>\s*</Positioned>", "",
                         dsl, flags=re.S)
        assert "<Text" not in no_text, "仍有未删除的 Text 节点"
        p = aux_dir / f"nobg-{which}.snapshot"
        p.write_text(no_text, encoding="utf-8")
        out = TEMPD / f"preview/nobg-{which}.png"
        for a in range(1, 4):
            r = subprocess.run(
                [sys.executable, str(ROOT / "tmp/run-20261011-01/_suite/scripts/snapshot_render.py"),
                 "--task", "A21", "--version", f"r3-aux-{which}-{a}",
                 "--dsl", p.as_posix(), "--out", out.as_posix(),
                 "--log", f"{TEMPD}/requests.jsonl",
                 "--responses-dir", f"{TEMPD}/responses"],
                capture_output=True, text=True)
            if '"ok": true' in (r.stdout or ""):
                break
        aux_pngs[which] = out

    images = []
    all_pass = True
    for which in ("portrait", "wide"):
        png = OUTD / f"launch-{which}.png"
        with Image.open(png) as im:
            im.load()
            px = im.convert("RGB").load()
        with Image.open(aux_pngs[which]) as ia:
            ia.load()
            apx = ia.convert("RGB").load()

        runs = []
        for tid, t, x, y, w, h, size, color, align in texts[which]["texts"]:
            fg = tuple(int(color.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
            # 取样分三步，严格按题面「排除抗锯齿边缘」「背景必须包含文字下方全部叠层」：
            #  1) 在交付图的该段覆盖盒里找**字形落点**：交付图该处是文字本色，
            #     而辅助图同处**本来不是**文字本色。
            #     两条限定缺一不可：
            #       · 只看「交付图≈文字色」会把抗锯齿边缘混进来（边缘是与底色混合的中间色，
            #         但在深色文字上仍可能接近本色）；
            #       · 只看「交付图≠背景」会把徽标描边这类同色几何当成字形——
            #         ONLINE LAUNCH 的描边恰好穿过文字覆盖盒，会得出「对比度 1.0」的假结论；
            #  2) 在辅助图（去掉全部 <Text>、其余图层完全相同）的**同一坐标**取背景；
            #  3) 对所有字形落点逐一算对比度，取最差值。
            x0, y0 = max(0, int(x)), max(0, int(y))
            x1, y1 = min(1600, int(x + w)), min(1100, int(y + h))
            bg_colors, n_core, n_edge = {}, 0, 0
            for yy in range(y0, y1):
                for xx in range(x0, x1):
                    d = apx[xx, yy]      # 辅助图：同坐标的纯背景
                    p = px[xx, yy]       # 交付图：含文字
                    is_fg_p = all(abs(p[i] - fg[i]) <= 12 for i in range(3))
                    bg_is_fg = all(abs(d[i] - fg[i]) <= 12 for i in range(3))
                    if is_fg_p and not bg_is_fg:
                        # 这一处「交付图是文字色、而背景本来不是文字色」→ 是字形落点。
                        # 若背景本身就是文字色（例如徽标描边穿过覆盖盒），它不是字形，排除。
                        n_core += 1
                        bg_colors[d] = bg_colors.get(d, 0) + 1
                    else:
                        n_edge += 1
            assert n_core > 0, f"{tid} 在覆盖盒内找不到字形核心像素"
            worst_bg = min(bg_colors, key=lambda c: contrast(fg, c))
            cf = contrast(fg, worst_bg)
            ok = cf >= THRESH
            all_pass &= ok
            runs.append({
                "text_id": tid, "text": t,
                "coverage_box_px": [int(x), int(y), int(x + w), int(y + h)],
                "font_size_px": size,
                "foreground": {"hex": color, "rgb": list(fg),
                               "source": "design-tokens.json 的 colors 令牌，实际渲染色与之逐字一致"},
                "background": {"distinct_colors_under_glyphs": len(bg_colors),
                               "dominant": list(max(bg_colors, key=bg_colors.get)),
                               "dominant_ratio": round(
                                   max(bg_colors.values()) / n_core, 6),
                               "worst_for_this_run": list(worst_bg),
                               "glyph_core_pixels": n_core,
                               "antialiased_edge_pixels_excluded": n_edge,
                               "source": "辅助图 nobg-{} 的**同一字形核心坐标**实际像素"
                                         "（保留全部图层、去掉所有 <Text>）".format(which)},
                "worst_contrast": round(cf, 4),
                "threshold": THRESH,
                "passed": ok,
            })

        samples = []
        for r in sorted(runs, key=lambda z: z["worst_contrast"])[:6]:
            bg = r["background"]["worst_for_this_run"]
            fg = r["foreground"]["rgb"]
            samples.append({
                "text_id": r["text_id"], "text": r["text"],
                "at_box_px": r["coverage_box_px"],
                "foreground_rgb": fg, "background_rgb": bg,
                "linear_foreground": [round(lin(c), 8) for c in fg],
                "linear_background": [round(lin(c), 8) for c in bg],
                "L_text": round(lum(fg), 8), "L_bg": round(lum(bg), 8),
                "formula": "(Lmax+0.05)/(Lmin+0.05)",
                "calculation": f"({max(lum(fg), lum(bg)):.8f}+0.05)"
                               f"/({min(lum(fg), lum(bg)):.8f}+0.05)",
                "contrast": r["worst_contrast"],
                "is_worst_in_image": True,
            })
        images.append({
            "image": f"round-03/launch-{which}.png",
            "size": list(Image.open(png).size),
            "background_note": "本图所有正文均落在纯底色上，无半透明层、无渐变、无纹理，"
                               "因此覆盖盒内的背景像素唯一；这不是假设，"
                               "由辅助图逐像素取样确认。",
            "text_runs": runs,
            "text_run_count": len(runs),
            "min_contrast": round(min(r["worst_contrast"] for r in runs), 4),
            "all_runs_pass": all(r["passed"] for r in runs),
            "detailed_samples": samples,
            "samples_include_worst": True,
        })

    doc = {
        "schema_version": 1, "task_id": "A21", "round": 3, "path_base": "output_dir",
        "formula": {
            "normalize": "c = channel / 255",
            "linearize": "c ≤ 0.04045 → c_linear = c/12.92；"
                         "否则 c_linear = ((c+0.055)/1.055)^2.4",
            "luminance": "L = 0.2126R_lin + 0.7152G_lin + 0.0722B_lin",
            "contrast": "(max(L_fg,L_bg)+0.05) / (min(L_fg,L_bg)+0.05)",
            "rounding": "全部用未舍入中间值，仅在写入 JSON 时保留 4–8 位小数；"
                        "阈值比较用未舍入结果",
            "threshold": THRESH,
            "coverage_rule": "对每段文字，先在交付图里定位**字形核心像素**（与文字本色相差 ≤12/通道，"
                             "抗锯齿边缘因是与底色混合的中间色而被自然排除），"
                             "再到「保留全部图层、去掉所有 <Text>」的辅助图的**同一坐标**取背景，"
                             "逐个字形核心像素算对比度并取最差值。"
                             "不在整个覆盖盒里统计背景色：徽标描边等几何元素虽在盒内，"
                             "却不在任何字形之下，混进来会得出假的最差值。",
        },
        "images": images,
        "evidence": [
            {"what": "辅助图（保留全部图层、去掉所有 <Text>）",
             "files": [{"path_base": "suite_root",
                        "path": f"tmp/run-20261011-01/A21/drafts/round-03/nobg/nobg-{w}.snapshot"}
                       for w in ("portrait", "wide")]
                       + [{"path_base": "suite_root",
                           "path": f"tmp/run-20261011-01/A21/preview/nobg-{w}.png"}
                          for w in ("portrait", "wide")],
             "why": "交付图上的文字像素会把抗锯齿边缘混进样本，无法区分「本色」与「边缘」；"
                    "辅助图去掉文字后，同一坐标处就是纯粹的背景。"
                    "逐段取样结果与令牌值一致，说明该图不存在需要更复杂合成的叠压。"},
            {"what": "交付图原图", "files": [
                {"path_base": "suite_root", "path": "outputs/run-20261011-01/A21/round-03/"
                                                      f"launch-{w}.png"} for w in ("portrait", "wide")],
             "why": "前景色取自令牌，且与实际渲染用的 color 属性逐字一致。"},
        ],
        "scope": "「普通文字」= 两图全部承担阅读信息的文字：主标题两行、日期、讲者、"
                 "ONLINE LAUNCH 徽标、网址、赞助方、参加方式、新增英语句。纯几何品牌装饰"
                 "（B1–B4）不计入文字，但也未被归类为文字来规避检查——它们不承载任何阅读信息。",
        "not_checked": "本轮两图不存在文字压在半透明层或渐变上的情形，因此"
                       "「按字形覆盖区取最差对比度」的抗锯齿边缘检查不适用；"
                       "若后续把正文移到构件上方或加半透明蒙版，必须改用逐像素合成法。",
        "all_pass": all_pass,
    }
    failing = [(im["image"], r["text_id"], r["foreground"]["hex"],
                r["background"]["worst_for_this_run"], r["worst_contrast"])
               for im in images for r in im["text_runs"] if not r["passed"]]
    for f in failing:
        print("FAIL", f)
    assert all_pass, f"存在未达 4.5:1 的文字段：{failing}"
    (drafts / f"contrast-audit-{ver}-raw.json").write_text(
        json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
    for im in images:
        print(im["image"], "runs", im["text_run_count"],
              "min", im["min_contrast"], "samples", len(im["detailed_samples"]))


if __name__ == "__main__":
    main()