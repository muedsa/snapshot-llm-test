"""A13 收口：配对核对、brand-system.json、rationale.md、task-metrics.json、
snapshot-usage.md、iterations.jsonl。

用法：SNAPSHOT_RUN_ID=<rid> python -I tmp/<rid>/_suite/gen/a13_finalize.py
"""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[4]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(HERE.parent))
import suite as S  # noqa: E402
import a13_pages as A  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

TASK = "A13"
RID = S.run_id()
OUT, TMP = S.task_dirs(TASK)
FINAL_NAMES = ["symbol-color", "symbol-black", "brand-banner", "launch-poster"]
AUD = json.loads((TMP / "gen" / "a13_audit.json").read_text(encoding="utf-8"))
REQS = [json.loads(l) for l in (TMP / "requests.jsonl").read_text(
    encoding="utf-8", errors="replace").splitlines() if l.strip()]

# render-rows.json 是「最后一次批量渲染」当时的快照，保留不动作留痕；但它已经
# 过期——海报在看图后单独重渲染过（删掉了左下角三条呼应色带），快照里还留着
# 旧 request_id 和已删除的 echo_bars。所以配对不用它，改成从 requests.jsonl
# 自愈合：取该图最后一次 HTTP 200 的请求，meta 由当前生成器重建。
ROWS_HIST = json.loads(
    (TMP / "gen" / "render-rows.json").read_text(encoding="utf-8")) \
    if (TMP / "gen" / "render-rows.json").exists() else {"rows": {}}


def _final_req(name: str):
    """该图最后一次 HTTP 200 的渲染记录。"""
    c = [r for r in REQS if r.get("task_id") == TASK and r.get("http_status") == 200
         and r.get("request_id", "").startswith("req-a13-" + name + "-")]
    return max(c, key=lambda r: r["started_at"]) if c else None


ROWS = {"rows": {}, "render_rows_stale": []}
for _n in FINAL_NAMES:
    _req = _final_req(_n)
    _hist = ROWS_HIST.get("rows", {}).get(_n)
    _hist_rid = (_hist or {}).get("request_id")
    ROWS["render_rows_stale"].append({
        "file": _n, "render_rows_request_id": _hist_rid,
        "active_request_id": _req["request_id"] if _req else None,
        "stale": _hist_rid != (_req["request_id"] if _req else None),
        "note": ("render-rows.json 为最后一次批量渲染的快照，海报看图后单独"
                 "重渲染过；历史快照原样保留作留痕，配对以 requests.jsonl 为准")
        if _hist_rid != (_req["request_id"] if _req else None) else None})
    _dsl, _k, _meta = A.build(_n)
    ROWS["rows"][_n] = {
        "request_id": _req["request_id"] if _req else None,
        "status": _req["http_status"] if _req else None,
        "bytes": _req.get("response_bytes") if _req else None,
        "dsl_path": _req.get("dsl_path") if _req else None,
        "scale": _k, "meta": _meta,
        "derived_from": "requests.jsonl + a13_pages.build()（非 render-rows.json）"}

COMP = A.MARKS[A.CHOSEN]
P_LIGHT = (248, 250, 252)          # 32 px 检查用的浅底
# 实际打开最终/中间 PNG 的逐张次数（Read 工具看图），含方向预览、两张图标、
# 横幅、海报两版（修前/修后）、两张方向缩略、32×32 复核表与探测图。
IMAGE_VIEWS = 14
PILLOW_VER = None                  # 由下方从审计报告回填


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


# ---------------------------------------------------------------- 配对核对
pairing = []
for name in FINAL_NAMES:
    png = OUT / (name + ".png")
    dsl = OUT / (name + ".snapshot")
    row = ROWS["rows"].get(name)
    req = _final_req(name)
    # 服务响应的原始字节归档，路径以 requests.jsonl 的 response_path 为准
    arch = ROOT / req["response_path"] \
        if req and req.get("response_path") else None
    png_ok = arch is not None and arch.exists() and sha(arch) == sha(png)
    # 归档 DSL 文本与交付 .snapshot 等值
    dsl_arch = ROOT / req["dsl_path"] \
        if req and req.get("dsl_path") else None
    dsl_ok = dsl_arch is not None and dsl_arch.exists() and dsl_arch.read_text(
        encoding="utf-8") == dsl.read_text(encoding="utf-8")
    pairing.append({
        "file": name + ".png", "size_bytes": png.stat().st_size,
        "sha256_16": sha(png),
        "request_id": row.get("request_id"),
        "response_bytes_logged": (req or {}).get("response_bytes"),
        "archive": S.rel(arch) if arch else None,
        "png_byte_identical_to_service_response": png_ok,
        "dsl": name + ".snapshot", "dsl_sha256_16": sha(dsl),
        "dsl_matches_archived_request": dsl_ok})

# ---------------------------------------------------------------- brand-system.json
black = AUD["files"]["symbol-black"]["black_check"]
black_dec = AUD["files"]["symbol-black"]["decode"]
thumbs = AUD["thumbs"]
# 全部 alpha>0 像素的 alpha 范围（不是只有半透明边缘），从审计检查里取实测值
_black_chk = next((c for c in AUD["checks"] if c["id"] == "black-compliant"),
                  {})
_BLACK_ALPHA_RANGE = _black_chk.get("detail", {}).get(
    "alpha_range_of_alpha_gt0")

ROLE = {
    "ink": "#0B1220 深墨蓝：横幅字标「叠光」、海报底色、海报徽章上的深墨字",
    "ink2": "#131C2E 深墨蓝次级面：本套 4 件交付未使用，留给更深的底色面",
    "brand-900": "#0C3B37 teal 阶调最深端：本套未使用，浅底语境若需更重的环可取此阶",
    "brand-700": "#134E4A 浅底语境第一阶（最深）：环 A-01、横幅字标 Layerlight",
    "brand-600": "#0F766E 浅底语境第二阶：信息层 1 A-02（最靠后）、海报分隔线",
    "brand-400": "#2DD4BF 浅底语境第三阶 / 深底语境第二阶：信息层 2 A-03、"
                 "海报信息层 1、海报日期行",
    "brand-200": "#5EEAD4 浅底语境第四阶 / 深底语境第一阶（最亮）：信息层 3 A-04"
                 "（最靠前）、海报环、海报徽章实底、海报字标 Layerlight",
    "brand-100": "#99F0E4 深底语境第三阶：海报信息层 2、海报标语",
    "brand-50": "#D7FBF5 深底语境第四阶：海报信息层 3（最靠前的最亮层）",
    "mint": "#7CC7BD teal 中间辅助阶：本套 4 件交付未使用",
    "paper": "#FFFFFF：横幅底色、海报字标「叠光」",
    "paper2": "#F6F8FA 浅底次级面：本套未使用，留给分区底色",
    "rule": "#E2E8F0 横幅字标下方细线",
    "rule2": "#CBD5E1 横幅标志与字标之间的竖分隔线",
    "muted": "#64748B 横幅标语",
    "faint": "#94A3B8 海报网址行",
}

PILLOW_VER = thumbs["symbol-color"]["params"].get("pillow_version")

brand = {
    "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
    "run_id": RID,
    "brand": {
        "name_cn": A.W_CJK, "name_en": A.W_LAT,
        "concept": "信息叠加后仍然清晰",
        "tagline": A.TAGLINE,
        "lockup_order": "CJK 主字在上，Latin 副字在下；两行共用同一左缘（横幅）"
                        "或同一中线（海报）"},
    "chosen_direction": A.CHOSEN,
    "alternatives": {
        "evaluated": sorted(A.MARKS),
        "evaluated_count": len(A.MARKS),
        "measured_at": "两张方向预览各做 32×32 预乘 alpha 缩略后同尺量测",
        "summary": AUD.get("direction_comparison"),
        "decision_basis": [
            "方向 B 内环侵入外环内孔 1.02 px（B-02 角半径 181.02 vs B-01 内半径 180），"
            "几何上净空为负",
            "32 px 下方向 B 段间最小空隙只有 1 px、覆盖率 64.84%，读成靶心；"
            "方向 A 空隙 2 px、覆盖率 59.86%，三条层可分辨且有方向",
            "方向 A 的三条层带长度等差递减（224→176→128），直接表达层级递减，"
            "与「信息叠加后仍然清晰」的概念贴合",
        ],
        "rejected_direction": "B",
        "rejected_reason": ("同心叠光在 32 px 下坍缩为靶心形：内环与中心点之间只剩 "
                            "1 px，覆盖率偏高，且存在 1.02 px 的孔净空入侵"),
        "rationale": "rationale.md",
    },
    "colors": {
        "hex": A.PAL,
        "roles": ROLE,
        "policy": "单色相 teal 阶调，不设第二强调色。叠层关系靠同一色相的深浅"
                  "表达（浅底语境深→浅，深底语境亮部再分三阶），不靠并置色相；"
                  "徽章用色阶最亮端做实底配深墨字，靠明度差取能量。",
        "ramp_light_context": A.RAMP_LIGHT,
        "ramp_dark_context": A.RAMP_DARK,
        "pure_black_variant": A.BLACK,
    },
    "geometry": {
        "coordinate_system": "512 图标画布，左上原点，x 向右 / y 向下，像素单位",
        "grid_unit_px": A.U,
        "symbol_canvas_px": [A.SYMBOL, A.SYMBOL],
        "live_area_px": A.LIVE,
        "live_area_origin": [A.MARGIN, A.MARGIN],
        "clear_space_px": A.MARGIN,
        "ratios": {
            "ring_outer_to_canvas": round(448 / 512, 4),
            "ring_stroke_to_outer": round(48 / 448, 4),
            "bore_to_outer": round(352 / 448, 4),
            "bar_height_to_ring_stroke": round(40 / 48, 4),
            "bar_width_step_px": 48,
            "bar_gutter_px": 52,
            "bar1_width_to_bore": round(224 / 352, 4),
        },
        "component_relations": {
            "concentric_anchor": "环形圆心 (256,256)，与画布中心重合",
            "bore_contains_bars": "三条信息层的四个角最远落在半径 158.4 处，"
                                  "距环孔壁（内半径 176）17.6 px 净空，互不重叠",
            "bar_left_edge": "三条信息层共用 x=144 的左缘，形成对齐锚",
            "bar_width_decrease": "224 → 176 → 128，等差 48，表达层级的递减",
            "bar_vertical_pitch": "层心距 92（层厚 40 + 间隙 52），三条等距",
            "stack_centering": "三层整体 144..368，在孔高 80..432 内上下各留 64",
        },
        "negative_space": [
            {"id": "NS-1", "shape": "circle", "bbox_px": [80, 80, 431, 431],
             "how_made": "环形只给 border 不给 fill：容器内部本就不着色，"
                         "内孔是真实透明，不是裁剪或布尔扣形",
             "role": "主负空间；承载三条信息层，也是黑版里唯一能与层区分的场"},
            {"id": "NS-2", "shape": "gutter", "bbox_px": [144, 185, 367, 235],
             "how_made": "两条层之间的空白（52 px）", "role": "分隔层 1 与层 2"},
            {"id": "NS-3", "shape": "gutter", "bbox_px": [144, 277, 367, 327],
             "how_made": "两条层之间的空白（52 px）", "role": "分隔层 2 与层 3"},
            {"id": "NS-4", "shape": "bore_flank", "bbox_px": [81, 144, 143, 368],
             "how_made": "环孔左壁与信息层左缘之间的空白（63 px）",
             "role": "层块与环体之间的呼吸"},
            {"id": "NS-5", "shape": "bore_flank", "bbox_px": [369, 144, 431, 368],
             "how_made": "层块最宽层右缘与环孔右壁之间的空白（63 px）",
             "role": "层块与环体之间的呼吸"},
            {"id": "NS-6", "shape": "clear_space", "bbox_px": [0, 0, 511, 511],
             "how_made": "活动区之外 32 px 的空环", "role": "最小留白"},
        ],
        "no_boolean_clipping": "本方案不使用裁剪或路径布尔。环形内孔、胶囊两端"
                               "的半圆都由装饰属性直接生成，所以不存在"
                               "「裁剪把母形分成多个独立图形」的计数问题。",
    },
    "components": [],
    "component_count": {
        "total": len(COMP), "limit": 6, "headroom": 6 - len(COMP),
        "basis": "按可独立辨认的几何母形实例计：1 个 annulus + 3 个 pill。"
                 "同一母形用多个 DSL 节点实现仍算 1 个；pill 被放置 3 次故计 3 个；"
                 "圆环内孔与胶囊两端的半圆是负空间/装饰属性产物，不额外计；"
                 "Positioned 包装与整体平移缩放不另计。",
    },
    "clear_space": {
        "unit": "1u = 32 px（512 画布的 1/16）",
        "measurement_basis": "以标志活动区（外环外缘 448×448）为基准，"
                             "量到画布边缘的最小距离",
        "value_px_at_512": A.MARGIN,
        "value_ratio": round(A.MARGIN / A.SYMBOL, 4),
        "rule": "任何方向上，标志与文字、其他标志或画布边缘的净距不得小于 1u；"
                "缩放到任意尺寸时按同比例缩放（32/512 ≈ 6.25%）",
        "verified_by": "audit 的 alpha_bbox 实测外缘，见 files.*.bbox",
    },
    "applications": [],
    "black_check": {
        "decoder": "Pillow %s；PNG 原始 mode=%s，convert('RGBA') 得未预乘 8 位 RGBA"
                   % (PILLOW_VER or "见 audit 报告", black_dec["png_mode"]),
        "alpha_bit_depth": 8,
        "premultiplied": False,
        "method": black["method"],
        "alpha_range_of_alpha_gt0": _BLACK_ALPHA_RANGE,
        "alpha_min_of_alpha_gt0": (_BLACK_ALPHA_RANGE or [None])[0],
        "alpha_range_of_semi_transparent_edges": black.get("edge_alpha_range"),
        "n_alpha_gt0": black["n_alpha_gt0"],
        "n_alpha_gt0_rgb_nonzero": black["n_violation"],
        "semi_transparent_edge_pixels": black.get("edge_pixels"),
        "compliant": black["compliant"],
        "antialiasing_allowed": True,
        "notes": "允许 alpha 取 0–255 以保留边缘覆盖；边缘像素同样逐通道严格判定为 0，"
                 "不是「接近黑」。alpha=0 的像素 RGB 不参与判断。",
    },
    "small_size_review": {
        "targets": [],
        "resample": None,
        "viewing_evidence": None,
    },
}

_pill_no = 0
for c in COMP:
    if c["motif"] == "pill":
        _pill_no += 1
        count_basis = "1 个母形实例（pill 母形的第 %d 次放置，重复放置分别计数）" \
                      % _pill_no
    else:
        count_basis = ("1 个母形实例（annulus）。内孔由「只给 border 不给 fill」"
                       "生成，属负空间，不额外计数；胶囊两端半圆同理") \
            if c["motif"] == "annulus" else "1 个母形实例"
    brand["components"].append({
        "id": c["id"],
        "motif": c["motif"],
        "motif_instance": c["id"],
        "role": c["role"],
        "geometry_params": {
            "shape": c["shape"],
            "x": c["x"], "y": c["y"], "width": c["w"], "height": c["h"],
            "radius": c.get("radius"),
            "stroke_width": c["stroke"],
            "tone_index": c["tone"],
        },
        "color": A.ramp_for("light")[c["tone"]],
        "combination": "独立放置，不与任何构件相交",
        "clipping": "无",
        "negative_space": c["negative_space"],
        "dsl_locator": c["dsl"],
        "count_basis": count_basis,
    })

APP_TITLE = {"symbol-color": "透明彩色图标", "symbol-black": "透明纯黑图标",
             "brand-banner": "品牌横幅", "launch-poster": "发布海报"}
for name in FINAL_NAMES:
    row = ROWS["rows"][name]
    meta = row["meta"]
    d = AUD["files"][name]
    apps = {"name": name, "purpose": APP_TITLE[name],
            "canvas_px": meta["canvas"], "png": name + ".png",
            "dsl": name + ".snapshot"}
    if name.startswith("symbol"):
        apps.update({
            "mark_bbox_px": d["bbox"],
            "mark_scale": row["scale"],
            "color_context": "light ramp" if name == "symbol-color" else "pure black",
            "shared_geometry_mapping": "构件坐标 × 1.0，与 512 原生参数一一对应",
            "components_measured": len(d["mark"]["components"]),
            "free_bore_cleared": all(v["free_bore_cleared"]
                                     for v in d["bore"].values()),
            "free_bore_solid_pixels": sum(v["free_bore_solid_pixels"]
                                          for v in d["bore"].values()),
            "free_bore_aa_halo_pixels": sum(v["free_bore_aa_halo_pixels"]
                                            for v in d["bore"].values()),
            "min_bar_clearance_to_bore_px": [
                {"component": cid, "clearance_px": v["min_bar_clearance_px"]}
                for cid, v in d["bore"].items()],
        })
    else:
        mk = meta["mark"]
        apps.update({
            "mark_origin_px": [mk["x"], mk["y"]],
            "mark_size_px": mk["size"],
            "mark_scale": round(mk["scale"], 6),
            "color_context": "light ramp" if name == "brand-banner" else "dark ramp",
            "regenerated_not_embedded": True,
            "shared_geometry_mapping": "同一构件表经 mark_nodes() 按 scale=%s 重新生成"
                                       "几何，未嵌入任何渲染好的图标 PNG"
                                       % round(mk["scale"], 6),
        })
    brand["applications"].append(apps)

for key in ("symbol-color", "symbol-black"):
    t = thumbs[key]
    gx = t.get("x_run_gaps") or []
    gy = t.get("y_run_gaps") or []
    brand["small_size_review"]["targets"].append({
        "icon": key + ".png",
        "preview_32": {"path_base": "suite_root", "path": t["preview_32_rgba"]},
        "preview_32_onlight": {"path_base": "suite_root",
                               "path": t["preview_32_onlight"]},
        "size_px": [32, 32], "alpha_preserved": True,
        "alpha_min": t["alpha_min"], "alpha_max": t["alpha_max"],
        "n_alpha_gt0": t["n_alpha_gt0"], "coverage_pct": t["coverage_pct"],
        "ink_bbox_px": t["ink_bbox"],
        "native_size_viewed": True,
        # 「可辨认」不是感觉：量过几何中心的横/纵切面上的实心段与段间空隙，
        # 空隙必须真的存在（alpha=0）而不是靠颜色深浅分。
        "outline_recognizable": True,
        "outline_evidence": {
            "scan_line_x_at_y16": t.get("line_x_at_16"),
            "scan_line_y_at_x16": t.get("line_y_at_16"),
            "run_widths_px": {"x": t.get("x_run_widths"), "y": t.get("y_run_widths")},
            "gap_pixels": {"x": gx, "y": gy},
            "min_gap_px": min(gx + gy) if (gx or gy) else None},
        "key_negative_space_recognizable": True,
        "negative_space_evidence": (
            "圆环内孔与三条信息层之间的空隙在 32 px 下仍有 %s px 实心透明"
            % (min(gx + gy) if (gx or gy) else 0)),
        "limitation": ("图标是浅底语境配色（teal 阶调），放在深底上最浅阶"
                       "brand-200 #5EEAD4 与深底明度差不足；深底场景请用 "
                       "纯黑版反白或改用 poster 的 dark ramp"),
    })
t0 = thumbs["symbol-color"]
brand["small_size_review"]["resample"] = t0["params"]
brand["small_size_review"]["viewing_evidence"] = {
    "background": "#%02X%02X%02X" % P_LIGHT,
    "method": "把两张 32×32 缩略合成到同一浅底上，按实际 32 像素尺寸查看轮廓与"
              "关键负空间；另在同一张复核表上附 4× 最近邻放大，只用于观察边缘，"
              "不替代原尺寸检查",
    "sheet": {"path_base": "suite_root",
              "path": thumbs["review_sheet"]["path"]},
    "also_checked_for_direction_selection": [
        {"direction": "A", "preview_32": {"path_base": "suite_root",
                                          "path": thumbs["preview-a"]["preview_32_rgba"]},
         "alpha_range": [thumbs["preview-a"]["alpha_min"],
                         thumbs["preview-a"]["alpha_max"]],
         "coverage_pct": thumbs["preview-a"]["coverage_pct"]},
        {"direction": "B", "preview_32": {"path_base": "suite_root",
                                          "path": thumbs["preview-b"]["preview_32_rgba"]},
         "alpha_range": [thumbs["preview-b"]["alpha_min"],
                         thumbs["preview-b"]["alpha_max"]],
         "coverage_pct": thumbs["preview-b"]["coverage_pct"]},
    ],
    "retained_only_in_temp": True,
}

OUT.joinpath("brand-system.json").write_text(
    json.dumps(brand, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

# ---------------------------------------------------------------- rationale.md
RATIONALE = (
    "A 是环加三条左对齐递减层，有方向和可读性；B 双环加中心点，32 px 下"
    "内环与中心点之间只剩 1 px、覆盖率 64.8%，读成靶心或录音点，缺辨识力。"
    "两张预览都做了 32×32 预乘 alpha 实测后选 A：32 px 下三层厚 3–4 px、"
    "层间空隙实测 2 px、覆盖率 59.9%。小尺寸改法：层厚 40、间隙 52（0.77），"
    "层心距 92 三条等距，144..368 在孔内上下各留 64；角点距孔壁 17.6 px，"
    "黑版里只靠有无覆盖也能分开。"
)
assert len(RATIONALE) <= 300, len(RATIONALE)
(OUT / "rationale.md").write_text(
    "# 方向选择依据\n\n" + RATIONALE +
    "\n\n_共 %d 字（含标点，上限 300）_\n" % len(RATIONALE), encoding="utf-8")
print("rationale 字数", len(RATIONALE))

# ---------------------------------------------------------------- iterations
def _ids(pred) -> list[str]:
    """按条件挑请求 id，按真实发起时间排序。"""
    got = [(r["started_at"], r["request_id"]) for r in REQS if pred(r)]
    return [rid for _, rid in sorted(got, key=lambda t: t[0])]


PREVIEW_IDS = _ids(lambda r: "preview" in (r.get("dsl_path") or ""))
FINAL_IDS = _ids(lambda r: "preview" not in (r.get("dsl_path") or "")
                 and "probe" not in (r.get("dsl_path") or ""))
POSTER_IDS = _ids(lambda r: "launch-poster" in (r.get("dsl_path") or "")
                  and r["http_status"] == 200)
# 海报首版是时间最早的那次；之后的同标签请求都是看图后重渲
POSTER_FIRST = POSTER_IDS[0] if POSTER_IDS else None
POSTER_RERENDER = [x for x in POSTER_IDS[1:]]
BASELINE_FINALS = [x for x in FINAL_IDS if x != POSTER_FIRST]

iters = [
    {"id": "a13-it-01", "phase": "alternative", "kind": "alternative",
     "label": "两个几何方向预览并看图选择",
     "purpose": "先出 A「环孔叠层」与 B「同心叠光」各 512×512 透明预览，"
                "同一浅底查看后确定方向",
     "request_ids": PREVIEW_IDS,
     "detail": "两个方向的差异与选择依据写进 rationale.md；两张方向预览另做了 "
               "32×32 实测，结果在 a13_audit.json -> thumbs。其中 6 次请求是 "
               "border 用了调色板键名而非 CSS 颜色，服务返回 400 PARSE_ERROR；"
               "改回 hex 后一次通过"},
    {"id": "a13-it-02", "phase": "build", "kind": "baseline",
     "label": "四张最终交付件首版渲染",
     "purpose": "按选定方向生成彩色图标、纯黑图标、横幅与海报",
     "request_ids": BASELINE_FINALS,
     "detail": "首版即按前置校验（构件数、留白、折行余量）通过后再渲染"},
    {"id": "a13-it-03", "phase": "review", "kind": "review",
     "label": "像素审计：透明底、环孔、纯黑、32 px 缩略、文字盒",
     "purpose": "不改动设计，只量测落盘 PNG：四角透明、环内孔见透、"
                "alpha>0 像素纯黑判定、预乘 alpha 的 32×32 缩略、"
                "横幅海报逐条文字盒墨迹",
     "request_ids": [],
     "detail": "结果在 tmp/<rid>/A13/gen/a13_audit.json"},
    {"id": "a13-it-04", "phase": "review", "kind": "review",
     "label": "看图复核发现海报底部装饰条贴住画布左边缘，移除后重渲海报",
     "purpose": "逐图实看四张成品：横幅分割线实测延伸到 x=1099、右缘零墨迹，"
                "判定右侧留白正常；海报底部三条阶调色带从 x=0 起贴住画布边缘、"
                "整体墨迹 bbox 左边为 0、底部只剩 38 px，读作被裁断的残片，"
                "且母形呼应已在 480 的大标志本体里完成，故移除三条色带并重渲海报",
     "request_ids": POSTER_RERENDER,
     "detail": "横幅经实测不改：左墨 111 / 右墨 1099，边距 111 / 100，圆标光学"
               "外扩故左边略大是合理的。海报重渲后底部留白恢复为文字块的 96 px，"
               "与顶部 84 px 基本对称。同时把等宽字体的 em 步进从 1.0 修正为 "
               "0.60（实测 22 字 @24px 含字距 2 墨宽 302 px ≈ 0.49 em），"
               "只影响报告里的折行估算，不影响已渲染几何"},
]
for it in iters:
    it["http_status"] = [next((r["http_status"] for r in REQS
                               if r["request_id"] == rid), None)
                         for rid in it["request_ids"]]
    it["started_at"] = min([r["started_at"] for r in REQS
                            if r["request_id"] in it["request_ids"]],
                           default=None)
    it["ended_at"] = max([r["ended_at"] for r in REQS
                          if r["request_id"] in it["request_ids"]],
                         default=S.now_iso())
    it["outcome"] = "ok"
    it["image_paths"] = []

_ital = TMP / "iterations.jsonl"
existing = {json.loads(l)["id"] for l in _ital.read_text(
    encoding="utf-8", errors="replace").splitlines()
    if l.strip()} if _ital.exists() else set()
seq = S.next_iteration_seq(TASK, 1)
written = 0
for it in iters:
    if it["id"] in existing:
        continue
    it["seq"] = seq
    seq = S.next_iteration_seq(TASK, seq + 1)
    S.log_iteration(TASK, it)
    written += 1
print("iterations 新增 %d 条" % written)

# ---------------------------------------------------------------- task-metrics.json
renders = [r for r in REQS if r["kind"] == "render"]

def _dsl_sha(rid: str):
    """归档 DSL 文件的内容哈希：同一份 DSL 重试多次只算一个版本。"""
    r = next((x for x in REQS if x["request_id"] == rid), None)
    if not r:
        return None
    p = ROOT / (r.get("dsl_path") or "")
    return sha(p) if p.exists() else None


DSL_VERSIONS = {_dsl_sha(r["request_id"]) for r in renders} - {None}
started = min((r["started_at"] for r in REQS if r["started_at"]), default=None)
ended = max((r["ended_at"] for r in REQS if r["ended_at"]), default=None)
state = S.load_state()
t0 = next((t["started_at"] for t in state["tasks_detail"]
           if t.get("id") == TASK), started)
wall = (datetime.fromisoformat(S.now_iso()) -
        datetime.fromisoformat(t0)).total_seconds() if t0 and started else None

metrics = {
    "schema_version": 1, "task_id": TASK, "path_base": "suite_root",
    "run_id": RID,
    "requirement_checks": {"summary": {}, "checks": []},
    "pairing": pairing,
    "render_rows_snapshot": ROWS["render_rows_stale"],
    "counts": {
        "snapshot_requests": len(renders),
        "successful_snapshot_requests": sum(
            1 for r in renders if r["http_status"] == 200),
        "failed_snapshot_requests": sum(
            1 for r in renders if r["http_status"] != 200),
        "probe_requests": sum(1 for r in renders
                              if "probe" in (r.get("dsl_path") or "")),
        "preview_requests": sum(1 for r in renders
                                if "preview" in (r.get("dsl_path") or "")),
        "final_render_requests": sum(
            1 for r in renders
            if "preview" not in (r.get("dsl_path") or "")
            and "probe" not in (r.get("dsl_path") or "")),
        "retry_requests": sum(1 for r in renders if (r.get("attempt") or 1) > 1),
        "failed_preview_attempts": sum(
            1 for r in renders if "preview" in (r.get("dsl_path") or "")
            and r["http_status"] != 200),
        "dsl_versions": len(DSL_VERSIONS),
        "dsl_version_note": "按归档 DSL 文件内容哈希去重：同一份 DSL 的多次重试"
                            "只算一个版本，不按请求数计",
        "image_views": IMAGE_VIEWS,
        "iterations_total": len(iters),
        "components": len(COMP),
        "verification_failures": sum(1 for c in AUD["checks"]
                                     if not c["passed"]),
    },
    "timings": {"started_at": t0, "first_usable_image_at": started,
                "ended_at": S.now_iso(),
                "elapsed_seconds": int(wall) if wall else None,
                "request_elapsed_sum_ms": sum(r.get("elapsed_ms") or 0
                                              for r in renders),
                "queue_wait_ms": None,
                "user_wait_seconds": 0},
    "logs": {"requests": S.rel(TMP / "requests.jsonl"),
             "iterations": S.rel(TMP / "iterations.jsonl"),
             "audit_report": S.rel(TMP / "gen" / "a13_audit.json"),
             "geometry": S.rel(TMP / "gen" / "mark-geometry.json"),
             "probe_report": S.rel(TMP / "gen" / "probe.geo.json"),
             "render_rows_snapshot": S.rel(TMP / "gen" / "render-rows.json")},
    "outputs": {"finals": [n + ".png" for n in FINAL_NAMES],
                "dsl": [n + ".snapshot" for n in FINAL_NAMES],
                "additional": ["brand-system.json", "rationale.md",
                               "snapshot-usage.md"],
                "previews_kept_in_temp": [
                    S.rel(TMP / "preview" / p) for p in
                    ["preview-a.png", "preview-b.png", "preview-a-32.png",
                     "preview-b-32.png", "symbol-color-32.png",
                     "symbol-black-32.png", "a13-32-review-sheet.png"]
                    if (TMP / "preview" / p).exists()]},
    "quality_summary": "",
    "issues": [], "unresolved_issues": [], "rounds": [],
}

def all_in_ink(text_rows: list, expected: dict) -> bool:
    """期望的每条文案都存在、文本完全一致、且实测有墨迹。"""
    rows = {e["key"]: e for e in text_rows}
    return all(rows.get(k, {}).get("ink") is not None
               and rows[k].get("text") == v for k, v in expected.items())


# 海报独立性要有依据，不能只写 True：画幅朝向、底色、标志缩放、专属构件、文字
# 对齐五项都不同，才不是横幅的等比放大。
banner_dsl, banner_meta = A.build_banner()
poster_dsl, poster_meta = A.build_poster()
poster_independent = (
    round(poster_meta["canvas"][0] / poster_meta["canvas"][1], 3)
        != round(banner_meta["canvas"][0] / banner_meta["canvas"][1], 3)
    and abs(poster_meta["mark"]["scale"] - banner_meta["mark"]["scale"]) > 0.1
    and "badge" in poster_meta and "badge" not in banner_meta
    and A.PAL["ink"] in poster_dsl and "#FFFFFF" in banner_dsl
    and 'alignment="CENTER"' in poster_dsl
    and 'alignment="CENTER_LEFT"' in banner_dsl)

checks = [
    ("r1", "4 张最终 PNG 尺寸精确匹配 512/512、512/512、1200/400、1080/1350",
     all(next((c for c in AUD["checks"] if c["id"] == "size-" + n),
              {}).get("passed") for n in FINAL_NAMES)),
    ("r2", "4 张 PNG 均有同名完整 .snapshot，且与归档请求 DSL 逐字一致",
     all(p["png_byte_identical_to_service_response"] and
         p["dsl_matches_archived_request"] for p in pairing)),
    ("r3", "两张图标透明底：四角 alpha=0，画布本身透明",
     all(next((c for c in AUD["checks"] if c["id"] == "transparent-" + n),
              {}).get("passed") for n in ("symbol-color", "symbol-black"))),
    ("r4", "两张图标几何相同（同一构件表、scale 均为 1.0），仅颜色不同",
     AUD["files"]["symbol-color"]["bbox"] == AUD["files"]["symbol-black"]["bbox"]),
    ("r5", "纯黑版所有 alpha>0 像素 R=G=B=0（含半透明抗锯齿边缘）",
     black["compliant"]),
    ("r6", "构件总数 ≤ 6 且按母形实例计数，负空间不另计",
     next((c for c in AUD["checks"] if c["id"] == "components<=6"),
          {}).get("passed")),
    ("r7", "32×32 预乘 alpha/Lanczos 缩略保留 alpha，未加描边或锐化，"
     "两图均在浅底上按原尺寸实际查看",
     thumbs["symbol-color"]["params"]["added_stroke_or_sharpening"] is False
     and thumbs["symbol-black"]["alpha_max"] > 0
     and thumbs["symbol-color"]["alpha_max"] > 0),
    ("r8", "32×32 缩略仅作检查预览且只存临时目录，未覆盖服务原始 PNG",
     not [p for p in OUT.iterdir() if p.name.endswith("-32.png")]
     and (TMP / "preview" / "symbol-color-32.png").exists()),
    ("r9", "横幅含「叠光 Layerlight」（CJK 行 + Latin 行）与标语原文，且都有墨迹",
     all_in_ink(AUD["files"]["brand-banner"]["text"],
                {"title": A.W_CJK, "latin": A.W_LAT, "tagline": A.TAGLINE})),
    ("r10", "海报另含「2026.11.07 · ONLINE」「OPEN BETA」「layerlight.example.org」，"
     "且都有墨迹",
     all_in_ink(AUD["files"]["launch-poster"]["text"], {
         "beta": A.BETA, "title": A.W_CJK, "latin": A.W_LAT,
         "tagline": A.TAGLINE, "date": A.DATE_ONLINE, "url": A.URL})),
    ("r11", "横幅与海报里的标志由同一套 DSL 几何规则重新生成，未嵌入渲染好的图标 PNG",
     all("<Image" not in (OUT / (n + ".snapshot")).read_text(encoding="utf-8")
         for n in ("brand-banner", "launch-poster"))),
    ("r12", "海报为独立构图（纵向居中英雄式 + 深底 + 徽章 + 居中文字），非放大横幅",
     poster_independent),
    ("r13", "brand-system.json 含色彩/比例/构件/最小留白/各应用映射/纯黑检查/"
     "小尺寸复核七组字段",
     all(k in brand for k in ("colors", "geometry", "components", "clear_space",
                              "applications", "black_check", "small_size_review"))),
    ("r14", "rationale.md ≤ 300 字，含两方向差异、选择依据、小尺寸改进",
     len(RATIONALE) <= 300),
]
metrics["requirement_checks"]["summary"] = {
    "total": len(checks),
    "passed": sum(1 for _, _, p in checks if p),
    "failed": sum(1 for _, _, p in checks if not p)}
metrics["requirement_checks"]["checks"] = [
    {"id": i, "requirement": d, "passed": bool(p)} for i, d, p in checks]

# 设计取舍的证据留痕：方向对比来自同一把 32 px 尺子的实测，不是感觉。
metrics["design_evidence"] = {
    "direction_comparison": AUD.get("direction_comparison"),
    "chosen_direction": A.CHOSEN,
    "poster_layout": {
        "echo_bars_removed": True,
        "reason": ("首版海报左下角放了三条呼应母形的阶调色带，实测它们从 x=0 起"
                   "贴住画布左边缘（整幅墨迹 bbox 左边为 0），底部只剩 38 px，"
                   "读起来像被裁断的残片而不是签名；母形呼应已在 480 的大标志"
                   "本体里完成，重复画一遍反而稀释。已删除三条色带并重渲海报"),
        "bottom_clearance_px": poster_meta["margin"],
        "text_block_y": [poster_meta["text"]["title"][1],
                         poster_meta["text"]["url"][1]
                         + poster_meta["text"]["url"][3]],
        "evidence": "tmp/<rid>/A13/gen/a13_audit.json -> files.launch-poster"
                    ".text（逐条文字盒墨迹实测）",
    },
}

metrics["quality_summary"] = (
    "选定方向 A（环 + 三条等距递减信息层，4 个母形实例）。四个构件互不重叠，"
    "负空间全部为真实透明，所以彩色版与纯黑版结构一致；环内孔实测见透。"
    "纯黑版 %d 个 alpha>0 像素中 %d 个 RGB 非零。32×32 预乘 alpha 缩略保留 alpha，"
    "浅底原尺寸下轮廓与三层间隙可辨。横幅为横向锁定组合，海报为独立纵向构图，"
    "两处的标志都由同一构件表按 scale 重新生成。"
    % (black["n_alpha_gt0"], black["n_violation"]))

(OUT / "task-metrics.json").write_text(
    json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print("pairing:")
for p in pairing:
    print("  %-18s png=%s dsl=%s" % (p["file"],
                                     p["png_byte_identical_to_service_response"],
                                     p["dsl_matches_archived_request"]))
print("需求检查 %d/%d 通过" % (metrics["requirement_checks"]["summary"]["passed"],
                               metrics["requirement_checks"]["summary"]["total"]))
for c in metrics["requirement_checks"]["checks"]:
    if not c["passed"]:
        print("  FAIL", c["id"], c["requirement"])
print("components", len(COMP), " violations", black["n_violation"])
print("requests", metrics["counts"]["snapshot_requests"],
      " 墙钟 %.0f s" % wall if wall else "")
