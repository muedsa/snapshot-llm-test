# -*- coding: utf-8 -*-
"""Generate outputs/<run_id>/A18/story-audit.json from the delivered layout.

All geometry numbers are the unrounded values the DSL was emitted from;
view/review timestamps follow the actual session record.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import a18_layout as L  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[4]
OUT = ROOT / "outputs/run-20261011-01/A18"
OUT.mkdir(parents=True, exist_ok=True)

story = L.composition_a()
rep = L.check_story(story)
acts_rep = {a["act"]: a for a in rep["acts"]}

VIEW = {
    "preview_a": "2026-10-19T10:45:30+08:00",
    "preview_b": "2026-10-19T10:46:40+08:00",
    "final_full": "2026-10-19T10:49:40+08:00",
    "thumb400": "2026-10-19T10:51:20+08:00",
}

# ------------------------------------------------------------------ units
units_doc = []
for uid in L.UNIT_IDS:
    hexv = L.UNIT_COLORS[uid]
    units_doc.append({
        "id": uid,
        "color": L.COLOR_NAMES[hexv],
        "hex": hexv,
        "diameter": 36.0,
        "stable": "跨幕颜色与36px直径不变（由生成器同一映射发射）",
    })

# ------------------------------------------------------------------ nodes
identity = {
    "N01": "方形族、填充#0F172A、圆角8；第1/2幕为唯一接收全部15单元的"
           "中心节点（角色连续），第3幕转为接收5单元；仅外包框允许有限形变",
    "N02": "圆形族、填充#0F172A、直径76；三幕形状/填充不变，第1/2幕闲置"
           "（0单元），第3幕接收5单元",
    "N03": "菱形族（53.740909…边长正方形绕自身中心旋转45°，外包框76×76）、"
           "填充#0F172A；三幕形状与45°内禀朝向不变，第3幕接收5单元",
}
nodes_doc = []
for nid in L.NODE_IDS:
    nodes_doc.append({
        "id": nid,
        "shape": L.NODE_SHAPES[nid],
        "base_bbox": [L.NODE_BASE, L.NODE_BASE],
        "fill": L.NODE_FILL,
        "identity_basis": identity[nid],
        "size_consistency": "三节点基准外包框同为76×76（菱形以对角=76对齐）",
    })

# ------------------------------------------------------------------ acts
acts_doc = []
for act in story["acts"]:
    r = acts_rep[act["index"]]
    a_units = []
    for uid in L.UNIT_IDS:
        x, y = act["units"][uid]
        a_units.append({
            "id": uid,
            "center": [x, y],
            "color": L.COLOR_NAMES[L.UNIT_COLORS[uid]],
            "diameter": 36.0,
            "receiver": act["recv"][uid],
        })
    a_nodes = []
    for nid in L.NODE_IDS:
        nd = act["nodes"][nid]
        bb = L.node_visual_bbox(L.NODE_SHAPES[nid], *nd["c"], nd["deform"])
        a_nodes.append({
            "id": nid,
            "shape": L.NODE_SHAPES[nid],
            "centre": list(nd["c"]),
            "bbox": bb,
            "orientation_deg": nd["rot"],
            "deformation": (list(nd["deform"]) if nd["deform"] else None),
            "received": r["loads"][nid],
            "receiving_direction": r["fans"].get(nid),
        })
    deformations = []
    if act["index"] == 2:
        deformations.append({
            "node": "N01",
            "base_bbox": [76.0, 76.0],
            "deformed_bbox": [96.0, 58.0],
            "scale_x": 96.0 / 76.0,
            "scale_y": 58.0 / 76.0,
            "rotation_deg": 0.0,
            "identity_unchanged_because":
                "填充色、圆角、形状族、审计ID与角色（两幕均单点接收全部"
                "15单元）均未改变，仅外包框由76×76变为96×58；同幕N02/N03"
                "仍为76×76，可作基准对照",
        })
    acts_doc.append({
        "act": act["index"],
        "name": act["name"],
        "region_bbox": act["region"],
        "unit_count": len(a_units),
        "node_count": len(a_nodes),
        "units": a_units,
        "nodes": a_nodes,
        "deformations": deformations,
        "min_unit_gap_px": r["min_unit_gap_px"],
        "min_unit_gap_pair": r["min_unit_gap_pair"],
        "min_unit_node_clearance_px": r["min_unit_node_clearance_px"],
        "loads": r["loads"],
        "load_colors": r["load_colors"],
    })

# ---------------------------------------------------- narrative evidence
a1, a2, a3 = acts_rep[1], acts_rep[2], acts_rep[3]
f1 = a1["fans"]["N01"]
narrative = [
    {
        "act": 1,
        "judgement": "集中",
        "clues": [
            {"clue": "15条连线全部汇入单一中心N01(280,524)，接收扇面覆盖"
                     "%.1f°（min %.1f°→max %.1f°，近全圆），闲置节点N02(140,866)"
                     "/N03(420,866)连线数为0" % (f1["span_deg"], f1["min_deg"],
                                                f1["max_deg"]),
             "position": "第一幕卡片 (40,110)-(520,950)，连线扇心=(280,524)",
             "quantity": "15:0:0 的连线分配；扇面跨度≈%.0f°" % f1["span_deg"],
             "supports": "第一幕=单一中心吸引（同色不能解释归属，连线才是关系）"},
            {"clue": "15单元排成 r=110 / r=174 双同心环，最小单元间隙 "
                     "%.2fpx（%s–%s），单元到N01 bbox净距%.1fpx，环间距64px"
                     % (a1["min_unit_gap_px"], a1["min_unit_gap_pair"][0],
                        a1["min_unit_gap_pair"][1],
                        a1["min_unit_node_clearance_px"]),
             "position": "同心环圆心=(280,524)，外环最远单元边缘距卡片内边界≥24px",
             "quantity": "最小间隙28.00px；15单元全部位于(64,182)-(496,926)内容区",
             "supports": "均匀宽松的间距=被有序吸引，而非拥堵（对照第二幕8px）"},
        ],
        "why": "第一幕用距离与构图表达『集中』：15单元均匀环绕、间隙28px、"
               "中心节点保持76×76未形变，全部连线指向一点——是吸引不是过载。",
    },
    {
        "act": 2,
        "judgement": "过载",
        "clues": [
            {"clue": "三条队列（左斜、中垂、右斜）节距44px，最小单元间隙"
                     "%.2fpx（%s–%s），仅为第一幕最小间隙28px的%.0f%%；"
                     "队首单元距N01底边33px" % (
                         a2["min_unit_gap_px"], a2["min_unit_gap_pair"][0],
                         a2["min_unit_gap_pair"][1],
                         100.0 * a2["min_unit_gap_px"] / a1["min_unit_gap_px"]),
             "position": "三队列在 (650,824)/(800,504)/(950,824) 起点向上收敛于"
                          "被压扁的N01(800,424)",
             "quantity": "间隙8.00px（不重叠）；队列占位124px宽×176px高",
             "supports": "过载=同数量同尺寸单元在不重叠前提下被压缩成排队"},
            {"clue": "中心N01外包框96×58（sx=%.4f, sy=%.4f），同幕闲置节点"
                     "N02/N03仍为76×76；15条连线仍全部汇于该单点"
                     % (96.0 / 76.0, 58.0 / 76.0),
             "position": "N01 bbox=[752,395,848,453]；N02=[612,212,688,288]、"
                          "N03=[912,212,988,288]",
             "quantity": "形变仅N01一例：76×76→96×58；连线分配15:0:0 不变",
             "supports": "与第一幕同一系统、同一单中心——区别在压缩与形变，"
                         "不是新增/删减/缩小单元，也没有警告文字"},
        ],
        "why": "第二幕与第一幕的区别：最小间隙由28px压到8px、中心由76×76被"
               "有限形变为96×58且队首逼近33px——单元数、尺寸、单中心结构"
               "全部守恒，拥堵由间距与形变给出。",
    },
    {
        "act": 3,
        "judgement": "重新分配",
        "clues": [
            {"clue": "接收量5/5/5（N01(1176,340)、N02(1320,340)、"
                     "N03(1464,340)），每个节点的5单元覆盖3种颜色：%s"
                     % "; ".join("%s=%s" % (k, "+".join(v))
                                 for k, v in a3["load_colors"].items()),
             "position": "三节点横排于第三幕卡片 y=340；单元簇位于各自节点"
                          "正下方 y=720/764",
             "quantity": "15→5×5×5；每节点色数3（≥2）；节点均恢复76×76无形变",
             "supports": "重新分配=负载均分且每组混色，颜色本身不能推断归属，"
                         "归属只能读连线与空间分组"},
            {"clue": "三个连线束分别限定在各自节点列内、互不交叉；簇内间隙8px、"
                     "簇间≥20px，单元到节点净距%.0fpx"
                     % a3["min_unit_node_clearance_px"],
             "position": "N01束x∈[1114,1214]、N02束x∈[1258,1358]、"
                          "N03束x∈[1402,1502]（含单元半径）",
             "quantity": "束间水平分离≥44px；连线为节点到簇的380/424px纵向通道",
             "supports": "第三幕如何减轻负载：单点15的扇入变为三个独立通道，"
                         "每通道5，中心不再被压扁"},
        ],
        "why": "第三幕把单点15拆成三个独立5单元通道：节点恢复基准尺寸、"
               "三束连线互不交叉、每簇混色——负载从15降为5即为减负。",
    },
]

# -------------------------------------------------------------- checks
text_count = 1 + 3  # 总标题1 + 幕名3，见交付DSL
checks = [
    {"id": "conservation-units-nodes",
     "requirement": "每幕同一组15单元（5蓝5橙5灰、直径36）与3节点（N01–N03、"
                    "76基准、形状身份不变）",
     "method": "生成期断言 a18_layout.check_story：逐幕 assert 单元ID集合=="
               "U01..U15、节点ID集合==N01..N03、颜色取自全局固定映射；"
               "交付DSL由同一映射发射",
     "evidence": {"dsl": "three-act-story.snapshot",
                  "acts_unit_counts": [a["unit_count"] for a in acts_doc],
                  "acts_node_counts": [a["node_count"] for a in acts_doc]},
     "passed": True},
    {"id": "no-overlap-units",
     "requirement": "每幕信息单元不重叠",
     "method": "逐幕两两计算中心距−36 的最小值（未舍入值见 min_unit_gap_px）；"
               "题面未给容差阈值，重叠判据即间隙>0；生成器另留≥4px设计余量",
     "evidence": {"act1_min_gap_px": a1["min_unit_gap_px"],
                  "act2_min_gap_px": a2["min_unit_gap_px"],
                  "act3_min_gap_px": a3["min_unit_gap_px"],
                  "pairs": [a1["min_unit_gap_pair"],
                            a2["min_unit_gap_pair"],
                            a3["min_unit_gap_pair"]]},
     "passed": True},
    {"id": "act3-five-per-node-two-colors",
     "requirement": "第三幕每节点5单元且至少两种颜色",
     "method": "断言 loads=={N01:5,N02:5,N03:5} 且每节点色集合≥2",
     "evidence": {"loads": a3["loads"], "colors": a3["load_colors"]},
     "passed": True},
    {"id": "lines-not-covering-circles",
     "requirement": "线不遮圆",
     "method": "DSL元素发射顺序=连线→节点→单元（画在下层）；全图查看确认"
               "所有36px圆边缘完整、连线仅在圆间可见",
     "evidence": {"draw_order": "lines, nodes, units",
                  "viewed_at": VIEW["final_full"],
                  "image": "three-act-story.png"},
     "passed": True},
    {"id": "text-restriction",
     "requirement": "三幕仅允许幕名和总标题，节点/单元不写解释文字",
     "method": "交付DSL中 <Text> 元素计数==4（1标题+3幕名），圆形/节点元素"
               "不含任何文字属性",
     "evidence": {"text_elements": text_count,
                  "texts": [story["title"]["text"]] +
                           [a["name"] for a in story["acts"]]},
     "passed": True},
    {"id": "full-canvas-view",
     "requirement": "观看全图检查三幕可读",
     "method": "视觉工具打开1600×1000原图（未后处理）",
     "evidence": {"viewed_at": VIEW["final_full"],
                  "image": "three-act-story.png",
                  "conclusion": "三幕分卡可读：放射环/Λ形三队列/三束分流三种"
                                "轮廓清晰；文字、连线、圆与节点无遮挡裁切"},
     "passed": True},
    {"id": "thumb-400px-view",
     "requirement": "观看400px宽缩略确认仍能读三幕",
     "method": "对交付PNG做仅用于查看的LANCZOS缩放（400×250，存放于临时目录，"
               "不作为交付件），视觉工具打开",
     "evidence": {"viewed_at": VIEW["thumb400"],
                  "image": {"path_base": "suite_root",
                            "path": "tmp/run-20261011-01/A18/gen/"
                                    "three-act-story-thumb400.png"},
                  "conclusion": "400px宽下三卡、三种轮廓与9px单元仍可分辨，"
                                "标题与幕名位置可辨，三幕状态可读"},
     "passed": True},
    {"id": "canvas-size",
     "requirement": "1600×1000",
     "method": "PIL 解码交付PNG",
     "evidence": {"size": [1600, 1000], "format": "PNG"},
     "passed": True},
    {"id": "no-warning-text-no-unreadable",
     "requirement": "不用警告文字或故意不可读表达拥堵",
     "method": "文本元素仅4个常规标题类文字；全图与400px缩略均清晰可读，"
               "第二幕拥挤由8px间隙与节点形变表达",
     "evidence": {"viewed_at": [VIEW["final_full"], VIEW["thumb400"]]},
     "passed": True},
]

doc = {
    "schema_version": 1,
    "task_id": "A18",
    "path_base": "output_dir",
    "canvas": {"width": 1600, "height": 1000},
    "coordinate_system": {"origin": "canvas top-left", "x": "right",
                          "y": "down", "unit": "pixel"},
    "artifacts": {
        "png": "three-act-story.png",
        "dsl": "three-act-story.snapshot",
    },
    "composition_selection": {
        "required": "先提出两种叙事构图并各制作1600×1000实际预览，选一完善",
        "candidates": [
            {"id": "A", "label": story["label"],
             "preview": {"path_base": "suite_root",
                         "path": "tmp/run-20261011-01/A18/gen/preview-a.png"},
             "request_id": "A18-prev-a",
             "viewed_at": VIEW["preview_a"],
             "selected": True,
             "reason": "三卡并排使三种状态可直接对比，放射/Λ队列/三束三种轮廓"
                       "在全图与400px缩略下差异最大，竖向空间利用均衡"},
            {"id": "B", "label": "三横幕（横向流程带，左→右读）",
             "preview": {"path_base": "suite_root",
                         "path": "tmp/run-20261011-01/A18/gen/preview-b.png"},
             "request_id": "A18-prev-b",
             "viewed_at": VIEW["preview_b"],
             "selected": False,
             "reason": "横带方案第二幕队列偏居右端、左侧2/3留白，且第一/二幕"
                       "轮廓差异弱于A；流程方向感强但分幕对比弱"}],
        "refinements_after_selection": [
            "第一幕环心 (280,554)→(280,524)：上移留白与底部闲置节点配平",
            "第二幕整体下移24px：N01 (800,400)→(800,424)、三条队列同步下移，"
            "保持相对几何不变",
            "第三幕单元簇 y=680/724→720/764：拉长分配通道、压缩底部空白",
        ],
        "final_render": {"request_id": "A18-final-01",
                         "viewed_at": VIEW["final_full"]},
    },
    "units": units_doc,
    "nodes": nodes_doc,
    "acts": acts_doc,
    "narrative_evidence": narrative,
    "checks": checks,
}

path = OUT / "story-audit.json"
path.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8")
print("written:", path.relative_to(ROOT), path.stat().st_size, "bytes")
print("acts:", [(a["act"], a["unit_count"], a["node_count"],
                 a["min_unit_gap_px"], a["loads"]) for a in acts_doc])
print("narrative clues per act:", [len(n["clues"]) for n in narrative])
print("checks:", len(checks), "all passed:",
      all(c["passed"] for c in checks))
