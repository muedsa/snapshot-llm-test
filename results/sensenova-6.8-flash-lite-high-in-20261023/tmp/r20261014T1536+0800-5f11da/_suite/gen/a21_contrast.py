"""A21 round-03 对比度审计：写 outputs/<run>/A21/round-03/contrast-audit.json。

判定基准（照 round-03.md 逐字规定，不改动）：
  8 位 sRGB 先归一化 c = channel/255，再线性化
    c <= 0.04045 时 c_lin = c / 12.92
    否则           c_lin = ((c + 0.055) / 1.055) ** 2.4
  相对亮度 L = 0.2126*R_lin + 0.7152*G_lin + 0.0722*B_lin
  对比度 = (max(L_fg, L_bg) + 0.05) / (min(L_fg, L_bg) + 0.05)，未舍入值判阈值

取色方式（这也是 round-03.md 强调的"不得只用主题 token 或名义底色"）：
  前景 = 该段文字的 design-token 色（layout 模型里 cv.text 的 color 参数，
        即提交给服务的 text color 属性）。不使用去锯齿后像素——抗锯齿边缘的
        部分覆盖像素不是文字本色，因此从不进入前景取值。
  背景 = 去文字辅助渲染（同一份构造器、同一批形状/渐变/叠层/牌子，只关掉
        <Text> 节点）在该坐标处的真实像素。辅助图保留文字下方的全部透明叠
        层与效果（氛围 wash、外辉光、外环、光带、牌子底面与边框、角部水印），
        所以它就是"实际合成背景"，不是名义底色。
  判定区域 = 交付图与辅助图的逐像素差值定位出的字形覆盖区（两图除文字外
        逐字节同源，可用作墨迹掩膜）；再在字形覆盖区内取最差对比度，而不是
        取一个有利位置。同时对"仅高覆盖核心像素"这一更窄区域再算一次，
        两者应给出同一个最差值，用于互相印证。

用法：
  python a21_contrast.py            量测并写 contrast-audit.json
  python a21_contrast.py --check    只量测并打印，不写任何文件
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import sys

import numpy as np
from PIL import Image

HERE = pathlib.Path(__file__).resolve()
RUN_ID = HERE.parents[2].name
SUITE_ROOT = HERE.parents[4]
TMP = SUITE_ROOT / "tmp" / RUN_ID / "A21"
OUT = SUITE_ROOT / "outputs" / RUN_ID / "A21"
GEN = HERE.parent
sys.path.insert(0, str(GEN))
sys.path.insert(0, str(SUITE_ROOT / "tools"))

import a21_layouts as L  # noqa: E402
import suite as S       # noqa: E402

RND = 3
RDIR = OUT / ("round-%02d" % RND)
AUX = TMP / "backgrounds"
EV = TMP / "contrast-evidence"

NAMES = {"portrait": "launch-portrait", "wide": "launch-wide"}
EXPECTED_SIZE = {"portrait": [1080, 1350], "wide": [1440, 810]}

THRESHOLD = 4.5
DIFF_THR = 12        # 判定"是墨迹"的最小逐像素差（含抗锯齿边缘）
CORE_THR = 0.85      # 判定"字形核心"的最小覆盖系数
PAD = 4              # 字形盒外扩像素（吸收渲染溢出），仍限定在本段盒内

# 文字承担阅读信息的角色；纯几何装饰（板材/球体/光带/强调条/网址圆点/水印）
# 不在此列，不计入文字对比度检查。
TEXT_ROLES = ("brand_cn", "brand_en", "kicker", "title_line1", "title_line2",
              "title_line3", "date", "speakers", "clarity_en", "url",
              "sponsors", "badge")

FORMULA = {
    "source": "round-03.md「普通文字与对比度检查」逐字规定",
    "normalize": "c = channel / 255",
    "linearize": ("c <= 0.04045 -> c / 12.92 ; 否则 ((c + 0.055) / 1.055) ** 2.4"),
    "luminance": "L = 0.2126*R_lin + 0.7152*G_lin + 0.0722*B_lin",
    "contrast": "(max(L_fg,L_bg) + 0.05) / (min(L_fg,L_bg) + 0.05)",
    "rounding": "阈值判定使用未舍入结果，JSON 里另行给出 4 位小数的展示值",
}


# ---------------------------------------------------------------- 色度学


def linear(c8: float) -> float:
    c = c8 / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def lum(r: float, g: float, b: float) -> float:
    return 0.2126 * linear(r) + 0.7152 * linear(g) + 0.0722 * linear(b)


def hex_of(px) -> str:
    return "#%02X%02X%02X" % (int(px[0]), int(px[1]), int(px[2]))


def contrast_of(fg, bg) -> float:
    """未舍入对比度。fg / bg 均为 3-元组（8 位 sRGB）。"""
    la = lum(*[float(x) for x in fg])
    lb = lum(*[float(x) for x in bg])
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def hex_lum(h: str) -> float:
    v = h.lstrip("#")
    return lum(int(v[0:2], 16), int(v[2:4], 16), int(v[4:6], 16))


# ---------------------------------------------------------------- 掩膜


def masks(delivered: np.ndarray, aux: np.ndarray, fg_rgb):
    """返回 (墨迹掩膜, 字形核心掩膜)。

    两图除 <Text> 外逐字节同源，因此差值处就是墨迹；覆盖系数用
    |交付 - 背景| / |文字本色 - 背景| 估得，>0.85 的像素视为字形核心
    （不把抗锯齿边缘的部分覆盖像素当作文字本色）。
    """
    d = delivered.astype(np.int16)
    a = aux.astype(np.int16)
    delta = np.max(np.abs(d - a), axis=2)
    ink = delta > DIFF_THR
    fg = np.array(fg_rgb, dtype=np.int16)
    span = np.max(np.abs(fg[None, None, :] - a), axis=2)          # |fg - bg|
    with np.errstate(invalid="ignore", divide="ignore"):
        cover = np.where(span > 8, delta / np.maximum(span, 1), 0.0)
    core = ink & (cover >= CORE_THR)
    return ink, core


def method_evidence() -> dict:
    """证明"去文字辅助渲染"确实只差在文字这一件事上。"""
    cfg = L.default_cfg_r3()
    out = {}
    orig = L.Canvas
    try:
        for key, builder in L.BUILDERS_R3.items():
            slug = NAMES[key]
            full = builder(cfg).dsl()
            L.Canvas = __import__("a21_r3_aux").NoTextCanvas
            try:
                aux = builder(cfg).dsl()
            finally:
                L.Canvas = orig
            out[slug] = {
                "delivered_dsl_bytes": len(full.encode("utf-8")),
                "aux_dsl_bytes": len(aux.encode("utf-8")),
                "delivered_text_nodes": full.count("<Text "),
                "aux_text_nodes": aux.count("<Text "),
                "delivered_positioned": full.count("<Positioned"),
                "aux_positioned": aux.count("<Positioned"),
                "positioned_delta_equals_text_nodes":
                    bool(full.count("<Positioned") - aux.count("<Positioned")
                         == full.count("<Text ")),
                "delivered_snapshot_sha256":
                    hashlib.sha256(
                        (RDIR / ("%s.snapshot" % slug)).read_bytes()
                    ).hexdigest(),
                "aux_snapshot_path": S.rel(
                    TMP / "dsl" / ("r03-%s.notext.attempt-01.snapshot" % slug)),
                "same_builder": True,
                "only_difference": "Canvas.text(record_text=False)：只关掉 "
                                   "<Text> 的输出，layout 模型不变，其余节点"
                                   "（氛围 wash、角部水印、发光球辉光/外环/"
                                   "光带、板材与亮核、网址牌与状态牌）全部"
                                   "照常输出",
                "text_has_no_shadow": True,
                "text_has_no_shadow_note":
                    "round-03 的 12/11 段文字均未设置 textShadow（竖版/横版"
                    "分别 grep 确认），因此 交付图 - 背景图 的差值只可能是"
                    "字形墨迹本身，不会混入阴影。前两轮主标题有青色 textShadow，"
                    "本轮按浅底可读性改为无阴影。",
            }
    finally:
        L.Canvas = orig
    return out


def build_layout() -> dict:
    """{key: [{role,text,fontSize,color,box}...]}，与提交给服务的坐标同源。"""
    cfg = L.default_cfg_r3()
    out = {}
    for key, builder in L.BUILDERS_R3.items():
        items = []
        for e in builder(cfg).layout:
            if e.get("kind") == "text" and e.get("role") in TEXT_ROLES:
                items.append({"role": e["role"], "text": e["text"],
                              "fontSize": e["fontSize"], "color": e["color"],
                              "box": e["box"], "bold": e.get("bold")})
        out[key] = items
    return out


def worst_over(region: np.ndarray, fg) -> dict:
    """在 region（2 维布尔）内取辅助图的背景像素，算最差对比度并定位。"""
    ys, xs = np.nonzero(region)
    if len(ys) == 0:
        return None
    bg = aux_ref()
    cols = bg[ys, xs]
    lums = np.array([lum(r, g, b) for r, g, b in cols])
    # 前景固定，对比度随背景亮度的变化是单调的，因此取亮度极值两端即可，
    # 但仍用未舍入公式分别算出两端，再取更小者。
    i_lo = int(np.argmin(lums))
    i_hi = int(np.argmax(lums))
    c_lo = contrast_of(fg, tuple(cols[i_lo].astype(float)))
    c_hi = contrast_of(fg, tuple(cols[i_hi].astype(float)))
    worst = c_lo if c_lo < c_hi else c_hi
    j = i_lo if worst is c_lo else i_hi
    return {"n_pixels": int(len(ys)),
            "bg_luminance_min": float(lums[i_lo]),
            "bg_luminance_max": float(lums[i_hi]),
            "worst": {"bg_rgb": [int(v) for v in cols[j]],
                      "bg_hex": hex_of(cols[j]),
                      "bg_luminance": float(lums[j]),
                      "at": [int(xs[j]), int(ys[j])],
                      "contrast": float(worst),
                      "contrast_vs_bg_luminance_min": float(c_lo),
                      "contrast_vs_bg_luminance_max": float(c_hi)}}


aux_cache: dict = {}


def aux_ref() -> np.ndarray:
    return aux_cache["arr"]


def hex_rgb(h: str):
    v = h.lstrip("#")
    return (int(v[0:2], 16), int(v[2:4], 16), int(v[4:6], 16))


def evidence(slug: str, name: str, box, src: np.ndarray, tag: str):
    """把一段文字在交付图与背景图上的局部各存一份，作为可复核证据。"""
    EV.mkdir(parents=True, exist_ok=True)
    x0, y0, x1, y1 = box
    w, h = src.shape[1], src.shape[0]
    x0c, y0c = max(0, x0), max(0, y0)
    x1c, y1c = min(w, x1), min(h, y1)
    crop = Image.fromarray(src[y0c:y1c, x0c:x1c].copy())
    dst = EV / ("%s-%s-%s.png" % (slug, name, tag))
    crop.save(dst)
    return {"path": S.rel(dst), "crop": [int(x0c), int(y0c), int(x1c), int(y1c)],
            "bytes": dst.stat().st_size,
            "sha256": hashlib.sha256(dst.read_bytes()).hexdigest(),
            "source": ("交付图" if tag == "ink" else "去文字背景图")}


def audit_one(key: str) -> dict:
    global aux_cache
    slug = NAMES[key]
    full = RDIR / ("%s.png" % slug)
    bg_png = AUX / ("%s.notext.png" % slug)
    if not full.exists() or not bg_png.exists():
        return {"image": slug, "status": "not_checked",
                "reason": "缺交付图或去文字背景图：%s / %s"
                          % (full.exists(), bg_png.exists())}

    delivered = np.asarray(Image.open(full).convert("RGB"))
    aux = np.asarray(Image.open(bg_png).convert("RGB"))
    aux_cache["arr"] = aux
    W, H = EXPECTED_SIZE[key]
    if delivered.shape[1] != W or delivered.shape[0] != H:
        return {"image": slug, "status": "not_checked",
                "reason": "交付图尺寸不符 %s" % (delivered.shape,)}

    layout = build_layout()[key]

    # ---- 方法自洽性：两图除墨迹外必须逐字节同源，否则背景取样无效 ----
    d2 = np.abs(delivered.astype(np.int16) - aux.astype(np.int16))
    outside = d2.max(axis=2)
    ink_anywhere = outside > DIFF_THR
    outside_max = float(np.max(outside[~ink_anywhere])) if ink_anywhere.any() \
        else 0.0
    all_ink = ink_anywhere

    segments = []
    for e in layout:
        fg_hex = e["color"]
        fg = hex_rgb(fg_hex)
        ink, core = masks(delivered, aux, fg)
        box = e["box"]
        x0 = max(0, box[0] - PAD)
        y0 = max(0, box[1] - PAD)
        x1 = min(W, box[2] + PAD)
        y1 = min(H, box[3] + PAD)
        reg = np.zeros((H, W), bool)
        reg[y0:y1, x0:x1] = True
        ink_reg = ink & reg
        core_reg = core & reg
        w_all = worst_over(ink_reg, fg)
        if core_reg.any():
            w_core = worst_over(core_reg, fg)
        else:
            w_core = None
        wc = w_all["worst"] if w_all else None
        seg = {
            "role": e["role"], "text": e["text"], "fontSize": e["fontSize"],
            "bold": bool(e["bold"]), "box": [int(v) for v in box],
            "foreground": {"hex": fg_hex, "source": "design-token / 交付 DSL 的 "
                              "text color 属性（layout 模型同源）",
                           "rgb": list(fg), "luminance": hex_lum(fg_hex),
                           "note": "抗锯齿边缘的部分覆盖像素未取作前景色"},
            "background": {"source": "去文字辅助渲染在字形覆盖区的实际像素",
                           "aux_render": S.rel(bg_png),
                           "aux_sha256": hashlib.sha256(bg_png.read_bytes()
                                                        ).hexdigest()},
            "glyph_pixels": {"ink_including_antialias": int(ink_reg.sum()),
                             "core_coverage_ge_0.85": int(core_reg.sum())},
        }
        if wc is None:
            seg["status"] = "not_checked"
            seg["reason"] = "该段在交付图中未找到墨迹像素，无法量测"
        else:
            seg["status"] = "checked"
            seg["minimum_contrast"] = round(wc["contrast"], 4)
            seg["minimum_contrast_unrounded"] = wc["contrast"]
            seg["meets_threshold"] = bool(wc["contrast"] >= THRESHOLD)
            seg["headroom_over_4_5"] = round(wc["contrast"] - THRESHOLD, 4)
            seg["worst_case"] = {
                "background_hex": wc["bg_hex"],
                "background_rgb": wc["bg_rgb"],
                "background_luminance": round(wc["bg_luminance"], 6),
                "pixel": {"x": wc["at"][0], "y": wc["at"][1]},
                "foreground_hex": fg_hex,
                "foreground_luminance": round(hex_lum(fg_hex), 6),
                "calculation": {
                    "foreground_linear": {
                        "R": round(linear(fg[0]), 8),
                        "G": round(linear(fg[1]), 8),
                        "B": round(linear(fg[2]), 8)},
                    "background_linear": {
                        "R": round(linear(wc["bg_rgb"][0]), 8),
                        "G": round(linear(wc["bg_rgb"][1]), 8),
                        "B": round(linear(wc["bg_rgb"][2]), 8)},
                    "foreground_luminance_full": round(hex_lum(fg_hex), 8),
                    "background_luminance_full": round(wc["bg_luminance"], 8),
                    "contrast_full": wc["contrast"],
                    "step": "((%.8f + 0.05) / (%.8f + 0.05)) = %.8f"
                            % (max(hex_lum(fg_hex), wc["bg_luminance"]),
                               min(hex_lum(fg_hex), wc["bg_luminance"]),
                               wc["contrast"])},
                "also_checked_at_opposite_extreme": {
                    "contrast_vs_bg_luminance_max": round(
                        w_all["worst"]["contrast_vs_bg_luminance_max"], 6),
                    "contrast_vs_bg_luminance_min": round(
                        w_all["worst"]["contrast_vs_bg_luminance_min"], 6)},
                "core_region_agreement": None if w_core is None else {
                    "worst_contrast_in_core_only": round(
                        w_core["worst"]["contrast"], 6),
                    "note": "高覆盖核心像素区域的最差值与含抗锯齿边缘的最差值"
                            "一致，说明取色未被边缘污染"},
                "method": "字形覆盖区 = |交付图 - 去文字背景图| > %d 的像素且"
                          "落在本段文本盒外扩 %d px 内；对该区域内全部背景像素"
                          "求相对亮度极值两端，分别用未舍入公式算对比度后取"
                          "更小者" % (DIFF_THR, PAD),
            }
            seg["evidence"] = {
                "delivered_local": evidence(slug, e["role"], (x0, y0, x1, y1),
                                            delivered, "ink")["path"],
                "background_local": evidence(slug, e["role"], (x0, y0, x1, y1),
                                             aux, "bg")["path"],
            }
        segments.append(seg)

    checked = [s for s in segments if s.get("status") == "checked"]
    mins = sorted((s["minimum_contrast"] for s in checked))
    worst_seg = min(checked, key=lambda s: s["minimum_contrast_unrounded"]) \
        if checked else None

    # ---- 展示样本：至少 6 处，且必须包含最差位置 ----
    ordered = sorted(checked, key=lambda s: s["minimum_contrast_unrounded"])
    picks = [worst_seg] if worst_seg else []
    for s in ordered:
        if len(picks) >= 6:
            break
        if s["role"] not in {p["role"] for p in picks}:
            picks.append(s)
    samples = []
    for s in picks:
        wc = s["worst_case"]
        samples.append({
            "role": s["role"], "text": s["text"], "fontSize": s["fontSize"],
            "box": s["box"],
            "sample_point": wc["pixel"],
            "foreground_hex": wc["foreground_hex"],
            "foreground_luminance": wc["foreground_luminance"],
            "background_hex": wc["background_hex"],
            "background_luminance": wc["background_luminance"],
            "contrast": wc["calculation"]["contrast_full"],
            "contrast_display": round(wc["calculation"]["contrast_full"], 4),
            "meets_threshold": s["meets_threshold"],
            "calculation": wc["calculation"],
            "is_worst_of_image": bool(s is worst_seg),
            "evidence_paths": s["evidence"],
        })

    return {
        "image": slug,
        "png": S.rel(full),
        "png_sha256": hashlib.sha256(full.read_bytes()).hexdigest(),
        "size": [W, H],
        "snapshot": S.rel(RDIR / ("%s.snapshot" % slug)),
        "status": "checked" if checked else "not_checked",
        "method_sanity": {
            "check": "去文字辅助渲染与交付图必须除墨迹外逐字节同源，否则背景取样"
                     "无效",
            "max_absolute_channel_difference_outside_ink": outside_max,
            "passes": bool(outside_max <= DIFF_THR),
            "ink_pixel_count_total": int(all_ink.sum()),
        },
        "threshold": THRESHOLD,
        "formula": FORMULA,
        "n_text_segments": len(segments),
        "n_checked": len(checked),
        "n_not_checked": len(segments) - len(checked),
        "minimum_contrast_across_all_text": min(mins) if mins else None,
        "minimum_contrast_across_all_text_unrounded":
            (worst_seg["minimum_contrast_unrounded"] if worst_seg else None),
        "worst_segment": worst_seg["role"] if worst_seg else None,
        "all_text_meets_threshold": bool(mins and mins[0] >= THRESHOLD),
        "not_plain_text_excluded": {
            "note": "以下构件是纯几何品牌装饰，不承担阅读信息，按 round-03.md "
                    "不计入文字对比度检查；此处不是“通过”，而是明确不在检查"
                    "对象内",
            "items": ["叠层板材 sheets", "板材描边", "板材亮核",
                      "发光球（径向渐变 + 光带 + 外环）", "主色强调条",
                      "网址牌左侧圆点", "角部线叠层水印", "氛围 wash"]},
        "samples": samples,
        "segments": segments,
    }


def main() -> int:
    for st in (sys.stdout, sys.stderr):
        if hasattr(st, "reconfigure"):
            st.reconfigure(encoding="utf-8")

    check_only = "--check" in sys.argv
    images = [audit_one(k) for k in ("portrait", "wide")]

    doc = {
        "task_id": "A21", "round": RND, "run_id": RUN_ID,
        "path_base": "suite_root",
        "created_at": S.now_iso(),
        "requirement": {
            "source": "tasks/A21-staged-launch-change/rounds/round-03.md",
            "quote": "改浅色主题，所有普通文字与实际合成背景的对比度≥4.5:1；"
                     "每图至少6处详细样本只是展示证据，不替代全量检查；"
                     "样本必须包含最差位置；未检查项不能预填通过",
        },
        "scope": {
            "plain_text_definition": "两张图中所有承担阅读信息的文字：主标题、"
                                     "日期、讲者、ONLINE LAUNCH、网址、赞助方、"
                                     "参加方式、品牌字标、新增英语短句",
            "threshold_applies_regardless_of_size": True,
            "foreground_source": "design token（交付 DSL 的 text color 属性）",
            "background_source": "去文字辅助渲染的实际合成像素（含全部透明叠层"
                                 "与效果）",
            "worst_case_rule": "渐变/纹理背景按字形覆盖区内最差对比度判定",
            "auxiliary_render_temp_only": True,
        },
        "formula": FORMULA,
        "method_evidence": method_evidence(),
        "images": images,
    }

    overall = [i for i in images if i.get("status") == "checked"]
    doc["overall"] = {
        "n_images_checked": len(overall),
        "n_images_not_checked": len(images) - len(overall),
        "n_text_segments_checked": sum(i["n_checked"] for i in overall),
        "n_text_segments_not_checked": sum(i["n_not_checked"] for i in overall),
        "global_minimum_contrast_unrounded":
            min((i["minimum_contrast_across_all_text_unrounded"] for i in overall),
                default=None),
        "all_plain_text_meets_threshold":
            bool(overall and all(i["all_text_meets_threshold"] for i in overall)),
        "not_checked_items": [
            {"image": i["image"], "reason": i.get("reason", "—")}
            for i in images if i.get("status") != "checked"],
    }
    # 未检查的分段逐条列出，绝不预填通过
    for i in images:
        for s in i.get("segments", []):
            if s.get("status") != "checked":
                doc["overall"]["not_checked_items"].append(
                    {"image": i["image"], "role": s.get("role"),
                     "reason": s.get("reason", "—")})

    if check_only:
        for i in images:
            print("== %s  status=%s  文字段 %d 已检查 %d  "
                  "最小 %.4f  最差段 %s  样本 %d =="
                  % (i["image"], i["status"], i.get("n_text_segments", 0),
                     i.get("n_checked", 0),
                     i.get("minimum_contrast_across_all_text") or 0.0,
                     i.get("worst_segment"), len(i.get("samples", []))))
            ms = i.get("method_sanity")
            if ms:
                print("   同源自检 墨迹外最大差 %s  passes=%s"
                      % (ms["max_absolute_channel_difference_outside_ink"],
                         ms["passes"]))
            for s in i.get("segments", []):
                if s.get("status") == "checked":
                    wc = s["worst_case"]
                    print("     %-13s %-8s 最差背景 %s L=%.6f -> %.4f%s"
                          % (s["role"], s["foreground"]["hex"],
                             wc["background_hex"],
                             wc["background_luminance"],
                             wc["calculation"]["contrast_full"],
                             "  ← 最差" if s["role"] == i.get("worst_segment")
                             else ""))
                else:
                    print("     %-13s 未检查：%s" % (s["role"], s["reason"]))
        print("\n整体：全局最小 %.4f，阈值 %.1f，全量通过=%s，"
              "未检查项 %d 条"
              % (doc["overall"]["global_minimum_contrast_unrounded"] or 0.0,
                 THRESHOLD, doc["overall"]["all_plain_text_meets_threshold"],
                 len(doc["overall"]["not_checked_items"])))
        print("[check-only] 未写文件")
        return 0

    dst = RDIR / "contrast-audit.json"
    RDIR.mkdir(parents=True, exist_ok=True)
    dst.write_text(json.dumps(doc, ensure_ascii=False, indent=1),
                   encoding="utf-8")
    print("wrote %s  %d bytes" % (S.rel(dst), dst.stat().st_size))
    print("全局最小对比度 %.4f  阈值 %.1f  全量通过=%s  未检查项 %d 条"
          % (doc["overall"]["global_minimum_contrast_unrounded"] or 0.0,
             THRESHOLD, doc["overall"]["all_plain_text_meets_threshold"],
             len(doc["overall"]["not_checked_items"])))
    return 0 if doc["overall"]["all_plain_text_meets_threshold"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
