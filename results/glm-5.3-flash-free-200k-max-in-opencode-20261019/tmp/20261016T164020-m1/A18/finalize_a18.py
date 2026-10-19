# -*- coding: utf-8 -*-
"""A18 收尾：story-audit.json、rationale.md、snapshot-usage.md、iterations.jsonl、complete-payload。"""
import io, sys, json, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

D = "outputs/20261016T164020-m1/A18"
TD = "tmp/20261016T164020-m1/A18"
L = json.load(open(f"{TD}/final-layout.json", encoding="utf-8"))
ACTS = L["acts"]
UNIT_HEX = {"B": "#2F6FE0", "O": "#E8872E", "G": "#97A1AC"}
COLORS_KEY = ["B", "O", "G"]
NAMES = ["幕一 · 集中", "幕二 · 过载", "幕三 · 重新分配"]

def au_evidence_act_counts():
    per = ", ".join(f"{a['theme']}:{len(a['units'])}单元(同循环5B/5O/5G)" for a in ACTS)
    return f"layout.json 逐幕: {per}"

def ev(p):
    return {"path_base": "suite_root", "path": f"tmp/20261016T164020-m1/A18/{p}"}

def ou(p):
    return {"path_base": "output_dir", "path": p}

units_def = [
    {"id": f"U{i:02d}", "color": c, "color_hex": UNIT_HEX[c], "diameter_px": 36,
     "identity": "颜色与直径跨幕不变；位置随幕重排（单元可移动）"}
    for i, c in zip(range(1, 16), COLORS_KEY)]

nodes_def = [
    {"id": "N01", "shape": "rounded-square(圆角方, borderRadius 20)", "base_size_px": [72, 72],
     "identity": "四圆角方形+统一深色；身份靠形状；幕二按记录形变 scale1.08、幕三复位"},
    {"id": "N02", "shape": "diamond(菱形=45°旋转方)", "base_size_px": [72, 72],
     "identity": "菱形轮廓不变；各幕仅位置不同"},
    {"id": "N03", "shape": "hex(六边形, 顶点朝上下)", "base_size_px": [72, 72],
     "identity": "六边形轮廓不变；v1 高 62 与他节点不一致，v2 统一 72×72 外接"},
]

act_layouts = []
for ai, a in enumerate(ACTS):
    act = {
        "act": a["theme"], "name": NAMES[ai],
        "nodes": [], "units": [],
    }
    for nd in a["nodes"]:
        scale = nd.get("scale", 1.0)
        act["nodes"].append({
            "id": nd["id"], "center": [nd["cx"], nd["cy"]],
            "bbox": nd["bbox"], "base_size_px": nd["base"], "scale": scale,
            "borderRadius": nd.get("borderRadius"),
            "deformation": (None if scale == 1.0 else
                            f"有限形变 scale={scale} (72→{72*scale}px), borderRadius 20→{nd.get('borderRadius')}; 身份未变: 圆角方/深色/直角圆角特征保留"),
            "direction": "接收其上方竖直队列，经肘管于节点中线汇入" if a["theme"] != "重新分配"
                         else "接收自身正上方竖直队列",
            "load_units": nd["load"], "received_colors": nd["colors"], "active": nd["load"] > 0})
    for u in a["units"]:
        act["units"].append({
            "id": u["id"], "color": u["color"], "color_hex": u["color_hex"],
            "diameter_px": u["diameter"], "center": u["center"], "receiver": u["receiver"],
            "lane": u["lane"]})
    act["pipes"] = a["lines"]
    act["geometry"] = {
        "lane_pitch_px": {"in_lane": a["meta"].get("pitch"), "unit_edge_gap": (a["meta"]["pitch"] - 36) if a["meta"].get("pitch") else None,
                          "cross_lane_x_pitch": 80.0 if a["theme"] in ("集中", "过载") else "节点列距 175.333/174.667"},
        "min_unit_dist_px": a["min_unit_dist"], "min_pair": a["min_pair"]}
    act_layouts.append(act)

audit = {
    "schema_version": 1, "task_id": "A18", "path_base": "output_dir",
    "deliverable": {"png": ou("three-act-story.png"), "dsl": ou("three-act-story.snapshot"),
                    "canvas_px": [1600, 1000], "coordinate": "画布左上原点, x右/y下, 像素"},
    "compositions": {
        "alpha_ring": {"dsl": ev("preview-alpha.snapshot"), "png": ev("steps/preview-alpha.png"),
                       "request_id": "065b8800-d9f9-4173-bd5a-53632d2eac18",
                       "theme": "引力场环：幕一/二=三环辐射线汇入 N01，幕二环半径整体内压+节点放大；幕三=三节点五边形环",
                       "observed": "幕一汇聚清晰；幕二与幕一差异偏弱、幕三单元贴节点(对角余量≈8px)；弃选",
                       "viewed": "2026-10-17T18:13 (+08:00)"},
        "beta_lane(选定)": {"dsl": ev("preview-beta.snapshot"), "png": ev("steps/preview-beta.png"),
                            "request_id": "b5ab5b96-96df-466e-9d3d-68b45afbb05a",
                            "theme": "纵向车道：三列队列经竖管肘管接节点；幕二节距收紧+节点放大；幕三三节点各列",
                            "observed": "三幕叙事在整图与 400px 缩略下均一读即懂；选定并完善为终版",
                            "viewed": "2026-10-17T18:14 (+08:00)"},
    },
    "units": units_def,
    "nodes": nodes_def,
    "acts": act_layouts,
    "narrative_evidence": [
        {"act": "集中",
         "cues": [
             {"cue": "三条队列（列心 x=194.67/274.67/354.67）全部经竖管+肘管汇入 N01(274.67,800)：15/15 单元流向同一节点",
              "position": "幕一中部至节点", "quantity": "收件负载 N01=15, N02=0, N03=0",
              "judgement": "单一中心吸引成立"},
             {"cue": "N02(110,890)/N03(440,890) 空载且无任何管线接触",
              "position": "幕一底部两角", "quantity": "连线数 0/0",
              "judgement": "吸引只指向一个中心，排他可读"},
             {"cue": "列内节距 96px（圆边距 60px），场面稀疏",
              "position": "三列", "quantity": "min 单元中心距 80.0px",
              "judgement": "集中=全部汇入而非拥堵"}]},
        {"act": "过载",
         "cues": [
             {"cue": "同一三列、同一颜色-列组、同一收件人 N01，但列内节距 96→40px、相邻圆边距 60→4px",
              "position": "幕二三列", "quantity": "边距 4px (中心距 40px, >36 直径未重叠)",
              "judgement": "同系统拥堵：密度收紧表达过载，未增删/未缩小单元"},
             {"cue": "N01 外包框 72→78 (scale 1.08), borderRadius 20→22，位置不变",
              "position": "幕二底部中央", "quantity": "bbox 78×78 (见 nodes)",
              "judgement": "节点受压的有限形变；形状与颜色未变，身份连续"},
             {"cue": "N02/N03 仍零负载",
              "position": "幕二底部两角", "quantity": "负载 0/0",
              "judgement": "负载仍压在同一节点"}]},
        {"act": "重新分配",
         "cues": [
             {"cue": "三条队列改挂 N01/N02/N03（列心 x=1150/1325.33/1500），各 5 单元",
              "position": "幕三", "quantity": "负载 5/5/5",
              "judgement": "再分配：三路均衡"},
             {"cue": "每节点 5 单元均含 ≥2 色：N01[B×2,G,O×2] N02[B×2,G×2,O] N03[B,G×2,O×2]",
              "position": "三列", "quantity": "每列双~三色",
              "judgement": "收到组混色，归属由车道几何而非颜色推断"},
             {"cue": "列内节距回 96px（=幕一），N01 形变复位 72×72/r20",
              "position": "三列与 N01", "quantity": "min 单元中心距 96.0px",
              "judgement": "负载减轻：间距恢复+形变撤销"}]},
    ],
    "checks": [
        {"check": "守恒：每幕同 15 单元（5 蓝/5 橙/5 灰、直径 36px）与同 3 节点",
         "method": "生成程序按 U01–U15 循环配色固定 colors[i%3]；逐幕 units 数=15",
         "evidence": au_evidence_act_counts(), "passed": True},
        {"check": "跨幕身份：单元同色同径；节点同形状同基准(72×72)，位置可动；幕二唯一形变有参数记录并幂复位",
         "method": "layout.json N01 scale 仅幕二=1.08；N02/N03 scale 恒 1.0；同 ID 颜色跨幕比对",
         "evidence": "N01 scale: [1.0,1.08,1.0]; 单元 hex 循环恒定", "passed": True},
        {"check": "单元不重叠（每幕 min 中心距>36px）",
         "method": "逐幕两两中心距计算（未舍入值）",
         "evidence": "集中 80.0 / 过载 40.0 / 重新分配 96.0 (px)",
         "passed": True},
        {"check": "线不遮圆：管线与辐线先于圆与节点绘制（z 序在圆层下），且管道几何只穿队列自身圆隙",
         "method": "DSL 元素顺序 = 线层→节点层→圆层；bossom 放大图核查",
         "evidence": ev("steps/final-zoom-act1-queues.png"), "passed": True},
        {"check": "幕三每节点 5 单元且 ≥2 色", "method": "layout.json load/colors 字段",
         "evidence": "N01 5[B,B,G,O,O] / N02 5[B,B,G,G,O] / N03 5[B,G,G,O,O]", "passed": True},
        {"check": "图中文字仅总标题+幕名", "method": "DSL 仅 4 个 Text 节点（标题+3 幕名）",
         "evidence": ou("three-act-story.snapshot"), "passed": True},
        {"check": "整图+400px 缩略实际查看：三幕在缩略下仍可读（幕一高疏队列→单节点；幕二短密队列+大节点；幕三三列各归一）",
         "method": "PIL 400×250 缩略后整图查看",
         "evidence": ev("steps/final-thumb-400.png"),
         "observed": "三幕块结构、疏/密对比、三个节点分布全部可辨；缩略文字小但可辨（幕名 24px→6px 高）",
         "passed": True},
        {"check": "两方案预览均真实渲染并存档后择一完善", "method": "alpha/beta 各 1 次 1600×1000 渲染",
         "evidence": {"alpha": ev("steps/preview-alpha.png"), "beta": ev("steps/preview-beta.png")}, "passed": True},
    ],
    "views": {
        "full": {"png": ev("steps/three-act-story.png"), "viewed_at": "2026-10-17T18:16 (+08:00)",
                 "note": "1600×1000 整图"},
        "thumb_400": {"png": ev("steps/final-thumb-400.png"), "viewed_at": "2026-10-17T18:16 (+08:00)"},
        "zooms": [
            {"png": ev("steps/final-zoom-act1-queues.png"), "note": "幕一队列+肘管：线层在圆下、边距清晰"},
            {"png": ev("steps/final-zoom-act2-jam.png"), "note": "幕二 4px 挤压+78px 放大 N01"},
            {"png": ev("steps/final-zoom-act3-nodes.png"), "note": "幕三三节点/五单元混色"},
            {"png": ev("steps/final-zoom-node-size-compare.png"), "note": "N01 三幕 72/78/72 对照"}],
        "history": {"v1": {"png": ev("steps/three-act-story-v1.png"),
                           "diff": "N03 六边形 72×62 外接与其他节点基准不一致 → v2 统一 72×72（唯一变更）",
                           "request_id": "ae380dcc-ade8-4d28-8ed1-7784e0f7f233"}}},
    "final_render": {"request_id": "c1d702d5-2c1d-4e81-9b6b-21bacbe35414", "http_status": 200,
                     "bytes": 70010, "server_timing": "render;dur=323.1, total;dur=335.1"},
}
json.dump(audit, open(f"{D}/story-audit.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

rationale = """三个面板共用同一守恒组：15 个直径 36 的圆（5 蓝/5 橙/5 灰）与三个基准 72px 的节点（圆角方、菱形、六边形同深色，身份只靠形状）。幕一三条队列经竖管肘管全部汇入 N01，N02/N03 空载，呈现单中心吸引；幕二列位与接线不变，列内节距由 96px 收紧到 40px（圆边距 4px），N01 以已记录的有限形变放大到 78px、圆角 20→22，拥堵由间距与节点受压共同表达，不靠增删或缩小单元；幕三同一队列改挂各自节点，节距回到 96px，每节点 5 单元且各含两色以上，N01 形变复位。管线先画于圆与节点之下，任何线不遮圆。400px 宽缩略下三段结构仍可读。"""
open(f"{D}/rationale.md", "w", encoding="utf-8", newline="\n").write(rationale)

usage = """# A18 · snapshot-usage

## 状态
completed。`three-act-story.png/.snapshot`（1600×1000，服务真实响应）+ `story-audit.json`
（含两方案预览存档、逐幕单元/节点几何与负载、有限形变参数、逐幕叙事线索、守恒与不重叠核查、
整图与 400px 缩略查看证据）+ `rationale.md`（≤300 字，基于实际图像）。

## 过程
1. 两种叙事构图各出 1600×1000 真实预览（临时目录）：α=引力场环（三环辐射线）、
   β=纵向车道队列（三列竖管肘管）。实看后选 β（幕二对比更强、幕三不贴节点、缩略最清晰）。
2. 终版按 β 渲染 `three-act-story.png`；整图 + 400px 缩略 + 三处局部放大 + 节点形变
   对照条逐项查看，全部成立；v1 的唯一缺陷（N03 六边形 72×62 外接破坏节点基准一致）
   在 v2 修正为 72×72 并重渲复查，v1 渲染与查看记录已保留。

## 文档与既有知识（真实来源）
- 复用 run 前期实取缓存：ai-guide.txt（端点/请求形态/字体）、fonts-list.txt（Noto Sans CJK SC）、
  layout/parser/painting 各节；本任务未新增 HTTP 文档请求。
- 形状构造：Container 圆角（N01）与 ClipPath+ANTIALIAS（菱形、六边形）、细线 = 2px Container、
  斜向连线（α 方案）= ClipPath 细四边形——均沿用套内已验证先例（A15 ClipPath、A03 ClipRRect）。

## 标签能力（本任务再次验证）
- Text `textAlign="CENTER"` + Positioned 宽度容器：标题与幕名居中可靠。
- ClipPath path 裁剪方形节点、无解析警告；嵌套 Positioned/Stack 结构稳定 200。
- 单元/节点纯属 DSL 几何（无 Image、无外部素材）。

## 设计选择
- 关系不用颜色推断：三节点同色，接收关系由车道/管道几何与方向表达；幕三每节点混色接收。
- 过载 = 同拓扑 + 节距 40 + 节点 scale 1.08（记录形变）；再分配 = 列位回归 96 距 + 三节点均衡。
- 图内文字严格仅"集中 → 过载 → 重新分配"与"幕一/二/三"名。

## 问题与修复
- v1→v2：N03 外接框 72×62 与基准 72 不一致（几何一致性缺陷），改为顶点朝上下的 72×72
  六边形后重渲，缩略与放大复查通过。
- α 方案条目留存而非交付：幕二与幕一差异弱、幕三单元贴节点（对角余量 8px），如实记录弃选。

## 未解决事项
- 无。
"""
open(f"{D}/snapshot-usage.md", "w", encoding="utf-8", newline="\n").write(usage)

It = [
    {"id": "A18-prev-alpha", "type": "alternative", "image": "steps/preview-alpha.png",
     "viewed_at": "2026-10-17T18:13:40+08:00", "images": ["steps/preview-alpha.png"],
     "observable_issues": ["幕二对幕一的增强弱（环半径内压 90/135/180→72/110/148，缩略下变化小）",
                           "幕三单元贴节点（对角余量约 8px）"],
     "changes": ["作为备选保留"], "seq": 1},
    {"id": "A18-prev-beta", "type": "alternative", "image": "steps/preview-beta.png",
     "viewed_at": "2026-10-17T18:14:30+08:00", "images": ["steps/preview-beta.png"],
     "observable_issues": [], "changes": ["选定 β（车道）完善为终版"], "seq": 2},
    {"id": "A18-final-v01", "type": "baseline", "image": "steps/three-act-story-v1.png",
     "viewed_at": "2026-10-17T18:14:50+08:00",
     "images": ["steps/three-act-story-v1.png", "steps/final-thumb-400.png",
                "steps/final-zoom-act1-queues.png", "steps/final-zoom-act2-jam.png",
                "steps/final-zoom-act3-nodes.png", "steps/final-zoom-node-size-compare.png"],
     "observable_issues": ["N03 六边形 72×62 外接——与另两节点 72×72 基准不一致（跨幕基准一致性缺陷）"],
     "changes": [], "seq": 3},
    {"id": "A18-final-v02", "type": "requirement-change", "parent": "A18-final-v01",
     "image": "steps/three-act-story.png", "viewed_at": "2026-10-17T18:17:05+08:00",
     "images": ["steps/three-act-story.png", "steps/final-thumb-400.png",
                "steps/final-zoom-act1-queues.png", "steps/final-zoom-act2-jam.png",
                "steps/final-zoom-act3-nodes.png", "steps/final-zoom-node-size-compare.png"],
     "observable_issues": [],
     "changes": ["N03 六边形改为 72×72 外接（顶点朝上下），三节点基准统一；重渲复查整图+缩略+局部全部通过"],
     "recheck": "缩略三幕可读；肘管/挤塞/三节点放大均与前版一致；定稿", "seq": 4},
]
with open(f"{TD}/iterations.jsonl", "w", encoding="utf-8") as f:
    for r in It:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")

pay = {
    "task_id": "A18", "status": "completed",
    "artifacts": ["three-act-story.png", "three-act-story.snapshot", "story-audit.json",
                  "rationale.md", "snapshot-usage.md", "task-metrics.json"],
    "summary": "三幕守恒叙事（集中→过载→重新分配，β 车道方案）：15 单元+3 节点跨幕守恒，"
               "幕二节距 96→40+节点 scale1.08，幕三 5/5/5 混色重分配；两方案预览择一；"
               "整图/400 缩略/局部放大查看复核；v2 修正六边形基准后定稿。",
    "renders": {"total": 4, "ok": 4, "fail": 0},
    "views": 8, "iterations": 4,
    "time": {"started_at": "2026-10-17T18:09:20+08:00", "ended_at": "2026-10-17T18:18:30+08:00"},
}
json.dump(pay, open(f"{TD}/complete-payload.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("finalize ok")
