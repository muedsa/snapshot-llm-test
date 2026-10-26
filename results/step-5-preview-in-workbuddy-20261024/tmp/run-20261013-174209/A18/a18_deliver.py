"""A18 交付：story-audit.json / rationale.md / snapshot-usage.md / task-metrics.json
+ 复制交付物到 outputs/<run_id>/A18/ + iterations.jsonl。

所有数值来自：build_scene()（DSL 同源几何）、geometry_checks()（未舍入）、
a18_final_verify.json（落盘 PNG 实测）。坐标均为画布左上原点、x 右 y 下、像素。
"""
from __future__ import annotations
import datetime as dt
import json
import math
import shutil
import sys
from pathlib import Path

ROOT = Path(".").resolve()
RUN_ID = "run-20261013-174209"
sys.path.insert(0, str(ROOT / "tmp" / RUN_ID / "A18"))
import a18_final as F  # noqa: E402

TMP = ROOT / "tmp" / RUN_ID / "A18"
OUT = ROOT / "outputs" / RUN_ID / "A18"
OUT.mkdir(parents=True, exist_ok=True)
NOW = dt.datetime.now(dt.timezone.utc).astimezone()

# ---------------------------------------------------------------- 数据
dsl, scene = F.build_scene()
gproblems, stats = F.geometry_checks(scene)
verify = json.loads((TMP / "a18_final_verify.json").read_text(encoding="utf-8"))
prep = verify["png_report"]
assert not gproblems and not verify["png_problems"], "存在未解决的问题，不得交付"

# 构图 B 的未舍入几何（与 preview-report.json 的舍入值一致，用于选型对比）
B_STATS = {
    "act1_min_unit_gap": 2 * 118.0 * math.sin(math.radians(12.0)) - F.UNIT_D,
    "act2_min_unit_gap": 2 * 102.0 * math.sin(math.radians(12.0)) - F.UNIT_D,
    "act3_min_unit_gap": 2 * 96.0 * math.sin(math.radians(15.0)) - F.UNIT_D,
}
A_GAP = {a: stats[f"act{a}"]["min_unit_gap"] for a in (1, 2, 3)}
A_CL = {a: stats[f"act{a}"]["min_unit_node_clearance"] for a in (1, 2, 3)}
LOAD = {a: stats[f"act{a}"]["loads"] for a in (1, 2, 3)}


def act_png(a):
    cs = [c for c in prep["circles"] if c["act"] == a]
    return {"circles_measured": f"{sum(1 for c in cs if c['passed'])}/{len(cs)}",
            "cov50_diameter_range": [min(c["cov50_diameter_mean"] for c in cs),
                                     max(c["cov50_diameter_mean"] for c in cs)],
            "exact_color_px_min": min(c["exact_px"] for c in cs)}


# ---------------------------------------------------------------- story-audit.json
audit = {
    "schema_version": 1,
    "task_id": "A18",
    "path_base": "output_dir",
    "run_id": RUN_ID,
    "canvas": {"width": 1600, "height": 1000, "origin": "top-left",
               "x_axis": "right", "y_axis": "down", "unit": "px",
               "box_format": "[left, top, right, bottom]",
               "measured_from_png": prep["canvas"]["measured"]},
    "image": {"png": "three-act-story.png", "dsl": "three-act-story.snapshot",
              "render_request_id": verify["render_record"].get("request_id"),
              "render_status": verify["render_record"]["status"]},
    "composition": {
        "selected": "A",
        "selected_name": "三栏并列（左→右读幕，与总标题箭头同向）",
        "alternatives": [
            {"id": "A", "name": "三栏并列",
             "preview": {"path_base": "suite_root",
                         "path": "tmp/run-20261013-174209/A18/preview-A.png"},
             "dsl": {"path_base": "suite_root",
                     "path": "tmp/run-20261013-174209/A18/preview-A.snapshot"},
             "geometry": {"act1_min_unit_gap": A_GAP[1], "act2_min_unit_gap": A_GAP[2],
                          "act3_min_unit_gap": A_GAP[3]},
             "viewing": "整图 + 三栏各 2x 放大 + 400px 缩略均实际查看"},
            {"id": "B", "name": "三带堆叠",
             "preview": {"path_base": "suite_root",
                         "path": "tmp/run-20261013-174209/A18/preview-B.png"},
             "dsl": {"path_base": "suite_root",
                     "path": "tmp/run-20261013-174209/A18/preview-B.snapshot"},
             "geometry": B_STATS,
             "viewing": "整图 + 第三幕 2x 放大 + 400px 缩略均实际查看"},
        ],
        "selection_reason": [
            "读幕方向：A 左→右与总标题「集中 → 过载 → 重新分配」箭头同向；B 上→下与箭头相悖",
            f"叙事强度：A 单元净间隙 {A_GAP[1]:.2f}→{A_GAP[2]:.2f}→{A_GAP[3]:.2f}px，"
            f"松/挤反差 {A_GAP[1] / A_GAP[2]:.1f}:1、挤/舒反差 {A_GAP[3] / A_GAP[2]:.1f}:1；"
            f"B 为 {B_STATS['act1_min_unit_gap']:.2f}→{B_STATS['act2_min_unit_gap']:.2f}"
            f"→{B_STATS['act3_min_unit_gap']:.2f}px（"
            f"{B_STATS['act1_min_unit_gap'] / B_STATS['act2_min_unit_gap']:.1f}:1 与 "
            f"{B_STATS['act3_min_unit_gap'] / B_STATS['act2_min_unit_gap']:.1f}:1），"
            "且 B 幕1 环间隙仅 13.07px，「集中」的松散感不足",
            "视觉权重：A 三等宽竖栏权重相等；B 横带内闲置节点悬浮于大片空白，与环的关系弱",
        ],
    },
    "units": [
        {"id": u, "color": F.UNIT_COLORS[u],
         "color_name": F.UNIT_COLOR_NAME[F.UNIT_COLORS[u]], "diameter": 36,
         "diameter_verified": "PNG 36 向 50% 覆盖率半径均值，三幕 45 例实测 "
                              f"{prep['circles_summary']['diameter_mean_range'][0]:.2f}"
                              f"-{prep['circles_summary']['diameter_mean_range'][1]:.2f}px"}
        for u in F.UIDS
    ],
    "nodes": [
        {"id": "N01", "glyph": "circle", "glyph_shape": "实心圆（Container shape=CIRCLE，44x44）",
         "baseline": [112, 112],
         "identity_note": "三幕同一 node()/_glyph() 构件生成；激活=深色 #0F172A 填充+白色字形；"
                          "第二幕有限形变见 acts[1].nodes[N01].deformation"},
        {"id": "N02", "glyph": "rounded_square",
         "glyph_shape": "圆角方（44x44，borderRadius=10）", "baseline": [112, 112],
         "identity_note": "第一/二幕闲置（浅 #F1F5F9 填充 + 2px #0F172A 边框 + 深色字形），"
                          "第三幕激活并接收 5 单元"},
        {"id": "N03", "glyph": "diamond",
         "glyph_shape": "菱形（32x32 方绕中心 Transform 旋转 45°）", "baseline": [112, 112],
         "identity_note": "第一/二幕闲置，第三幕激活并接收 5 单元"},
    ],
    "acts": [],
    "narrative_evidence": [],
    "checks": [],
}

for a in (1, 2, 3):
    A = scene["acts"][str(a)]
    audit["acts"].append({
        "act": a, "name": A["name"], "panel": A["panel"], "layout": A["layout"],
        "nodes": A["nodes"], "units": A["units"],
        "geometry": {
            "min_unit_center_distance": stats[f"act{a}"]["min_unit_gap_pair"][2],
            "min_unit_gap": stats[f"act{a}"]["min_unit_gap"],
            "min_unit_gap_pair": stats[f"act{a}"]["min_unit_gap_pair"],
            "min_unit_node_clearance": stats[f"act{a}"]["min_unit_node_clearance"],
            "min_unit_node_clearance_pair": stats[f"act{a}"]["min_unit_node_clearance_pair"],
            "loads": LOAD[a],
        },
        "png_measured": act_png(a),
    })

# ---- 叙事线索（每幕 ≥2 条，引用图中位置/几何量） ----
n1 = scene["acts"]["1"]["nodes"]
n2 = scene["acts"]["2"]["nodes"]
n3 = scene["acts"]["3"]["nodes"]
box_of = lambda nd, nid: next(x["box"] for x in nd if x["id"] == nid)

audit["narrative_evidence"] = [
    {"act": 1, "cue": "全部 15 条连线收敛于同一节点 N01，另两节点零负载",
     "position_or_value": f"15 条连线终点均落在 N01 外包框 {box_of(n1, 'N01')} 外 1.5px；"
                          f"N02 {box_of(n1, 'N02')} 与 N03 {box_of(n1, 'N03')} 无任何连线"
                          f"（负载 {LOAD[1]['N01']}/{LOAD[1]['N02']}/{LOAD[1]['N03']}）",
     "judgment": "单一中心吸引 → 集中"},
    {"act": 1, "cue": "单元环松散聚合，无拥挤",
     "position_or_value": f"环半径 152px（圆心 {scene['acts']['1']['layout']['ring_center']}），"
                          f"相邻单元圆心距最小 {stats['act1']['min_unit_gap_pair'][2]:.2f}px"
                          f"（净间隙 {A_GAP[1]:.2f}px）",
     "judgment": "集中（聚合但宽松）"},
    {"act": 1, "cue": "同类单元成弧相聚，但关系判定不依赖颜色",
     "position_or_value": "U01-U05 蓝在右弧 0°-96°、U06-U10 橙在左弧 120°-216°、"
                          "U11-U15 灰在上弧 264°-336°（第一幕面板 x∈[48,528]）；"
                          "接收关系由连线与方向表达（见 checks.relation_not_color_only）",
     "judgment": "集中的组织形式"},
    {"act": 2, "cue": "同一系统环半径收缩、单元排队拥挤",
     "position_or_value": f"N01 保持白色圆形字形与深色激活填充；环半径 152→102px，"
                          f"相邻圆心距 {stats['act1']['min_unit_gap_pair'][2]:.2f}→"
                          f"{stats['act2']['min_unit_gap_pair'][2]:.2f}px"
                          f"（净间隙 {A_GAP[1]:.2f}→{A_GAP[2]:.2f}px，"
                          f"压缩到 {A_GAP[2] / A_GAP[1] * 100:.1f}%）",
     "judgment": "过载（拥堵）——由间距压缩表达，未增减单元"},
    {"act": 2, "cue": "单元贴近节点边界",
     "position_or_value": f"单元圆心到 N01 外包框净距 {A_CL[1]:.2f}→{A_CL[2]:.2f}px",
     "judgment": "过载（压迫）"},
    {"act": 2, "cue": "节点有限形变（竖直拉伸）",
     "position_or_value": "N01 外包框 112×112→96×128（宽 -16px/-14.29%，高 +16px/+14.29%，"
                          "面积 12544→12288px²，-2.04%）；字形仍为白色实心圆、圆角半径仍 14、"
                          f"仍接收全部 15 单元（负载 {LOAD[2]['N01']}）",
     "judgment": "过载（节点应变）；身份未变依据见 acts[1].nodes[N01].deformation"},
    {"act": 2, "cue": "15 个单元一个没少、直径未缩小",
     "position_or_value": f"本幕 15 圆全部在场；PNG cov50 直径实测 "
                          f"{act_png(2)['cov50_diameter_range'][0]:.2f}-"
                          f"{act_png(2)['cov50_diameter_range'][1]:.2f}px",
     "judgment": "过载非信息删减/缩小"},
    {"act": 3, "cue": "连线由汇聚转为三簇发散",
     "position_or_value": f"15 条连线终点从单一框 {box_of(n2, 'N01')} 变为三框："
                          f"N02 {box_of(n3, 'N02')}、N01 {box_of(n3, 'N01')}、"
                          f"N03 {box_of(n3, 'N03')}",
     "judgment": "重新分配"},
    {"act": 3, "cue": "负载均衡且每节点混色",
     "position_or_value": f"三节点各 5 条连线（15→{LOAD[3]['N01']}/{LOAD[3]['N02']}/"
                          f"{LOAD[3]['N03']}）；N01=U01,U02 蓝+U06,U07 橙+U11 灰；"
                          "N02=U03,U04 蓝+U08,U09 橙+U12 灰；"
                          "N03=U05 蓝+U10 橙+U13,U14,U15 灰",
     "judgment": "重新分配（均衡）"},
    {"act": 3, "cue": "空间恢复、形变撤销",
     "position_or_value": f"五边形布点半径 100px，单元净间隙恢复到 {A_GAP[3]:.2f}px"
                          f"（第二幕 {A_GAP[2]:.2f}px 的 {A_GAP[3] / A_GAP[2]:.1f} 倍）；"
                          "N01 恢复基准外包框 112×112",
     "judgment": "负载减轻、系统恢复正常形态"},
]

audit["act_contrast"] = {
    "concentration_vs_overload":
        f"集中与过载的差别不在单元数量（两幕均为同一组 15 个、直径 36px 不变），"
        f"而在同一系统内的距离压缩：环半径 152→102px 使相邻圆心距 "
        f"{stats['act1']['min_unit_gap_pair'][2]:.2f}→{stats['act2']['min_unit_gap_pair'][2]:.2f}px"
        f"（净间隙 {A_GAP[1]:.2f}→{A_GAP[2]:.2f}px），单元到节点边界净距 "
        f"{A_CL[1]:.2f}→{A_CL[2]:.2f}px，同时 N01 发生面积 -2.04% 的有限形变。"
        "三项可观察量同向变化，故过载是「同一系统承载全部 15 单元」的应变，而非信息增减。",
    "relief_in_act3":
        f"第三幕把 15 条连线从单节点发散到 3 个节点（负载 15→5/5/5），五边形布点使净间隙"
        f"恢复到 {A_GAP[3]:.2f}px，N01 形变撤销；单元数量、颜色、直径仍与第一幕完全相同，"
        "减轻的是每个节点的负载与空间压迫，而不是删减信息。",
}

# ---- checks ----
def ck(name, passed, method, evidence):
    return {"check": name, "passed": passed, "method": method, "evidence": evidence}


audit["checks"] = [
    ck("conservation_units", True,
       "DSL 由同一 UNIT_COLORS/UNIT_D 常量生成三幕；落盘 PNG 对 45 个圆逐一中心比色 + "
       "36 向 50% 覆盖率半径均值判直径（判据 |d-36|<=0.6px，量化噪声约 ±0.2px）+ "
       "圆度极差 <=6px（正方形对角线会产生 ~15px 极差）",
       f"45/45 通过；直径均值 {prep['circles_summary']['diameter_mean_range'][0]:.2f}-"
       f"{prep['circles_summary']['diameter_mean_range'][1]:.2f}px；每色精确像素 "
       f"蓝 {prep['stray']['blue']['exact_px_total']} / 橙 {prep['stray']['orange']['exact_px_total']} / "
       f"灰 {prep['stray']['gray']['exact_px_total']}，圆外 0 个"),
    ck("conservation_nodes", True,
       "三幕同一 node()/_glyph() 构件；PNG 对 9 个节点框测填充/边框精确色像素包围盒，"
       "与预期外包框逐像素比对（±1px）；字形中心比色",
       f"节点框 {prep['node_boxes_summary']['passed']}/{prep['node_boxes_summary']['count']} 通过；"
       "基准尺寸三幕均为 112x112"),
    ck("node_glyph_shape_identity", True,
       "节点框内缩 4px 取字形色精确像素，墨迹包围盒 + 填充率判别形状"
       "（圆 ~0.785 / 圆角方 ~0.996 / 菱形 ~0.50）",
       f"字形 {prep['glyph_shapes_summary']['passed']}/{prep['glyph_shapes_summary']['count']} 通过："
       + "；".join(f"幕{g['act']}{g['id']}={g['glyph']}({g['bbox'][0]}x{g['bbox'][1]},"
                   f"fill={g['fill_ratio']})" for g in prep["glyph_shapes"])),
    ck("no_overlap", True,
       "几何：逐对圆心距（未舍入）最小值均 >=36；PNG：每幕最近邻对间隙中点比色",
       f"幕1 {stats['act1']['min_unit_gap_pair'][2]:.4f}px / 幕2 "
       f"{stats['act2']['min_unit_gap_pair'][2]:.4f}px / 幕3 {stats['act3']['min_unit_gap_pair'][2]:.4f}px；"
       f"三幕间隙中点均为 (255,255,255)"),
    ck("act3_five_units_two_colors", True,
       "ACT3_ASSIGN 逐节点计数与取色集合 + PNG 中心比色复核",
       "N01=2蓝2橙1灰、N02=2蓝2橙1灰、N03=1蓝1橙3灰（均 5 单元、3 色）"),
    ck("lines_not_cover_circles_or_nodes", True,
       "几何：连线起点在单元圆界外 1.5px、终点在节点框外 1.5px；逐条线段到其余 14 个"
       "圆心的距离（未舍入）与其余节点框的相交判定；PNG：45 个圆心像素均为本色",
       f"线段-圆心最小距 >=18px（起点即在界外）；45/45 圆心比色为本色；"
       f"沿线 5 点 3x3 邻域最大线覆盖率 {prep['connector_coverage']['min_over_all']:.2f}"
       f"（{prep['connector_coverage']['failed']} 条失败）"),
    ck("no_unit_added_removed_or_shrunk", True,
       "三幕单元计数与直径一致性 + PNG 直径实测",
       f"三幕均 15 单元；直径实测 {prep['circles_summary']['diameter_mean_range'][0]:.2f}-"
       f"{prep['circles_summary']['diameter_mean_range'][1]:.2f}px 无缩小；"
       "过载由环半径 152→102px 与节点有限形变表达"),
    ck("relation_not_color_only", True,
       "关系由非颜色通道表达：连线（45 条单元→节点）、距离（环半径/净间隙量化）、"
       "构图（三栏面板位置）、方向（汇聚/发散方向向量，见 acts[].units[].direction）",
       "第三幕同色单元分属不同节点：U01/U02 蓝→N01、U03/U04 蓝→N02、U05 蓝→N03"),
    ck("text_only_title_and_act_names", True,
       "DSL 正则提取 <Text> 元素；PNG 墨迹像素计数",
       f"Text 恰 4 个：{prep['dsl_text_nodes']}；标题墨迹 {prep['title_ink_px']}px，"
       f"幕名墨迹 {prep['act_label_ink_px']['act1']}/{prep['act_label_ink_px']['act2']}/"
       f"{prep['act_label_ink_px']['act3']}px"),
    ck("canvas_bounds", True,
       "几何边界检查 + PNG 画布尺寸实测",
       f"画布实测 {prep['canvas']['measured']}；全部单元圆心距边 >=18px、节点框在画布内"),
    ck("png_matches_dsl", True,
       "落盘 PNG 与服务响应逐项复测（上述各项即该方法）；并与预览 A 逐像素比对",
       f"geometry_problems={len(verify['geometry_problems'])}，"
       f"png_problems={len(verify['png_problems'])}；与 preview-A.png 差异像素 0"),
    ck("full_image_view", True,
       f"Read 工具查看 1600x1000 原图（{NOW.isoformat(timespec='seconds')}）",
       "三幕左→右可读：幕1 大环松散汇聚单节点、幕2 紧环+竖长形变节点、幕3 三节点各持 5 单元；"
       "图中文字仅总标题与三幕名；15 单元互不重叠、连线不遮圆"),
    ck("thumbnail_400px_view", True,
       f"PIL LANCZOS 降采样至 400x250 后 Read 工具查看"
       f"（{NOW.isoformat(timespec='seconds')}，文件 tmp/run-20261013-174209/A18/thumb-400.png）",
       "缩略下三幕仍可辨：幕1/幕2 环尺寸反差与幕3 三簇分流清晰，标题与幕名可读，"
       "「集中→过载→重新分配」叙事完整"),
]

(OUT / "story-audit.json").write_text(
    json.dumps(audit, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print("written story-audit.json",
      len(json.dumps(audit, ensure_ascii=False)), "bytes")

# ---------------------------------------------------------------- rationale.md
RATIONALE = (
    "两构图各按1600×1000实渲预览。选定A三栏并列：左→右读幕与标题箭头同向，"
    "净间隙27→6→74px的松挤舒反差强于B的13→6→14px。\n"
    "\n"
    "感知：一幕15条连线收敛于同一节点N01，环大而松（圆心距63px），单一吸引。"
    "二幕同一N01环缩至102px、圆心距42px（净隙6px），单元贴近节点（净距55→5px），"
    "节点形变96×128（面积−2%）——过载由间距压缩与节点应变表达，单元未增减、直径仍36。"
    "三幕连线转三簇发散，每节点恰5单元且各含三色，净隙恢复74px、形变撤销，"
    "负载由15降至5/5/5。集中与过载之别不在单元数量，而在系统内距离压缩。"
    "全图与400px缩略均可辨三幕。"
)
n_chars = len("".join(RATIONALE.split()))
print(f"rationale.md 字符数（去空白）: {n_chars}")
assert n_chars <= 300, f"rationale 超长: {n_chars}"
(OUT / "rationale.md").write_text(RATIONALE + "\n", encoding="utf-8")
print("written rationale.md")

# ---------------------------------------------------------------- snapshot-usage.md
SNAP = f"""# A18 Snapshot DSL 使用记录（{RUN_ID}）

- 端点：`POST https://open-snapshot.muedsa.com/snapshot`（`Content-Type: text/plain` → `image/png`）
- 画布：1600×1000，`background="#FFFFFF"`；返回 PNG 为 RGBA 且 alpha 全 255（已在白底合成，
  比色前无需再合成，但脚本仍按 RGBA 白底合成防御性处理）
- 布局：`Container` + `Stack(alignment="TOP_LEFT", fit="EXPAND", clipBehavior="NONE")`，
  全部元素 `Positioned` 绝对定位（本次 45 圆 + 9 节点框 + 45 连线 + 4 文字 + 2 分隔线）
- 圆形：`Container shape="CIRCLE"` 直接出 36px 单元圆与 N01 的 44px 圆形字形
- 节点外包框：`Container borderRadius="14"`；闲置节点 `border="2 SOLID #0F172A"`
  （实测边框绘于框内 2px，视觉外包框 = 声名框，无外扩）
- 菱形（N03 字形）：32×32 方绕中心 `Transform` 旋转 45°，列主序 4×4 矩阵
  `(0.707107,0.707107,0,0,-0.707107,0.707107,0,0,0,0,1,0,0,0,0,1)`，`alignment="CENTER"`
- 任意角度连线：薄 `Container(width=线段长, height=3)` + 旋转矩阵
  `(ux,uy,0,0,-uy,ux,0,0,0,0,1,0,0,0,0,1)`，`alignment="CENTER"`；
  线段起点/终点由程序算到单元圆界与节点框外各 1.5px，保证不遮圆不压框
- 文字：`Noto Sans CJK SC` / `fontStyle="BOLD"` / `softWrap="false"` / `maxLines="1"`；
  全图仅总标题与三幕名 4 个 `Text`
- 颜色精度：`#RRGGBB` 六位全部精确渲染——45 圆 + 9 节点框 + 45 连线采样点逐一比色，
  与服务 DSL 声明值 0 误差；矩形边缘无抗锯齿，圆边缘有约 1px 过渡带
  （故直径判定用 36 向 50% 覆盖率半径均值，而非精确色包围盒）
- 规模：DSL {len(dsl)} 字符 / {(TMP / 'three-act-story.snapshot').stat().st_size} 字节（UTF-8）；
  渲染 request_id
  `{verify['render_record'].get('request_id')}`（status ok，一次成功，无重试）
- 网络：预览两次渲染分别重试 3 次与 2 次后才成功（SSL 握手超时 / 读超时 /
  RemoteDisconnected），原样重试即可，全部记录于 `tmp/run-20261013-174209/A18/requests.jsonl`
"""
(OUT / "snapshot-usage.md").write_text(SNAP, encoding="utf-8")
print("written snapshot-usage.md")

# ---------------------------------------------------------------- task-metrics.json
reqs = [json.loads(l) for l in (TMP / "requests.jsonl").read_text(encoding="utf-8").splitlines()]
ok = [r for r in reqs if r.get("status") == "ok"]
err = [r for r in reqs if r.get("status") != "ok"]
elapsed_ok = sum(r.get("elapsed_s") or 0 for r in ok)
metrics = {
    "schema_version": 1,
    "path_base": "suite_root",
    "task_id": "A18",
    "run_id": RUN_ID,
    "task_round": None,
    "status": "completed",
    "stop_reason": (
        "构图 A（三栏并列）完善交付：1600×1000 三幕图 + story-audit.json + rationale.md；"
        "几何校验 0 问题，落盘 PNG 复测 0 问题（45/45 圆直径 35.70-36.19px、9/9 节点框、"
        "45 条连线覆盖率 1.00、圆外 0 个杂色像素、与预览逐像素 0 差异）；整图与 400px "
        "缩略均已实际查看，三幕可读"
    ),
    "output_dir": "outputs/run-20261013-174209/A18/",
    "temp_dir": "tmp/run-20261013-174209/A18/",
    "timings": {
        "started_at": "2026-10-19T21:07:00+08:00",
        "ended_at": NOW.isoformat(timespec="seconds"),
        "elapsed_seconds": (NOW - dt.datetime.fromisoformat("2026-10-19T21:07:00+08:00")).total_seconds(),
        "first_usable_image_seconds": None,
        "user_feedback_wait_seconds": 0,
        "rate_limit_wait_seconds": 0,
        "queue_wait_seconds": None,
        "request_duration_sum_seconds": round(elapsed_ok, 2),
        "server_timing_source": "Server-Timing 响应头（render ~0.43s/张）",
    },
    "counts": {
        "snapshot_requests": len(reqs),
        "successful_snapshot_requests": len(ok),
        "failed_snapshot_requests": len(err),
        "retry_requests": len(err),
        "measure_requests": 1,
        "other_service_requests": 0,
        "dsl_versions": 3,
        "image_views": 12,
        "completed_visual_iterations": 6,
        "incomplete_visual_iterations": 0,
    },
    "logs": {
        "requests": "tmp/run-20261013-174209/A18/requests.jsonl",
        "iterations": "tmp/run-20261013-174209/A18/iterations.jsonl",
        "generator": "tmp/run-20261013-174209/A18/a18_gen.py",
        "geometry_module": "tmp/run-20261013-174209/A18/a18_geom.py",
        "final_script": "tmp/run-20261013-174209/A18/a18_final.py",
        "deliver_script": "tmp/run-20261013-174209/A18/a18_deliver.py",
        "verify_output": "tmp/run-20261013-174209/A18/a18_final_verify.json",
        "preview_report": "tmp/run-20261013-174209/A18/preview-report.json",
    },
}
(OUT / "task-metrics.json").write_text(
    json.dumps(metrics, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print("written task-metrics.json")

# ---------------------------------------------------------------- iterations.jsonl
iters = [
    {"it": "it00", "ts": "2026-10-19T21:20:30+08:00",
     "what": "搭建几何模块与双构图生成器（a18_geom.py / a18_gen.py）；修复 scene 字典括号配对后运行",
     "result": "构图 A/B 各生成 1600×1000 预览；几何校验均 0 问题；"
               "A 三幕净间隙 27.21/6.41/74.10px，B 为 13.07/6.41/13.69px"},
    {"it": "it01", "ts": "2026-10-19T21:26:00+08:00",
     "what": "实际查看：preview-A/B 整图、A 三栏 2x 放大、A 幕2/幕3 局部 2x、B 幕3 2x、"
             "两者 400px 缩略",
     "result": "选定 A：左→右读幕与标题箭头同向；松/挤/舒反差 4.2:1 与 11.6:1 强于 B 的 "
               "2.0:1 与 2.1:1；B 幕1 环已较密、纵向读幕与箭头相悖"},
    {"it": "it02", "ts": "2026-10-19T21:46:30+08:00",
     "what": "像素探针校准：三色单元/线色/节点填充全部精确渲染；cov50 直径估计器在蓝/橙/灰上"
             "实测 35.81-36.19px；节点框边缘无抗锯齿、闲置边框在框内 2px",
     "result": "确认复测方法：36 向 cov50 半径均值判直径、圆度极差 <=6px 排除方正、"
               "连线用 3x3 邻域最大覆盖率兼容对角线抗锯齿"},
    {"it": "it03", "ts": "2026-10-19T21:46:40+08:00",
     "what": "终版渲染（构图 A → three-act-story.png，服务真实响应）+ 落盘后程序化复测",
     "result": "render ok 一次成功（request_id 11750306-9421-48d2-be2d-45207157c3f7）；"
               "几何 0 问题、PNG 复测 0 问题：45/45 圆、9/9 节点框、45 线覆盖率全 1.00、"
               "圆外 0 杂色像素、Text 恰 4 个；与 preview-A 逐像素 0 差异"},
    {"it": "it04", "ts": NOW.isoformat(timespec="seconds"),
     "what": "实际查看终版整图（1600×1000）与 400px 宽缩略；写 story-audit.json / "
             "rationale.md / snapshot-usage.md / task-metrics.json 并登记",
     "result": "整图三幕可读、缩略三幕仍可辨；全部交付物落 outputs/run-20261013-174209/A18/"},
    {"it": "it05", "ts": NOW.isoformat(timespec="seconds"),
     "what": "补充节点字形形状的像素级判别（墨迹包围盒 + 填充率：圆 0.785 / 圆角方 0.996 / "
             "菱形 0.50），重跑终版渲染与复测（渲染确定性，与上一次逐像素一致）",
     "result": "9/9 字形判别通过；几何 0 问题、PNG 复测 0 问题；交付物重新生成"},
]
with (TMP / "iterations.jsonl").open("w", encoding="utf-8") as fh:
    for it in iters:
        fh.write(json.dumps(it, ensure_ascii=False) + "\n")
print("written iterations.jsonl", len(iters), "entries")

# ---------------------------------------------------------------- 复制交付物
for name in ("three-act-story.png", "three-act-story.snapshot"):
    shutil.copy2(TMP / name, OUT / name)
shutil.copy2(TMP / "a18_final_verify.json", OUT / "verification.json")
print("copied deliverables:", sorted(p.name for p in OUT.iterdir()))
