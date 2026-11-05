#!/usr/bin/env python3
"""Fill real view/response evidence into the three audit JSONs after visual review."""
import json, os, sys
from pathlib import Path

ROOT = Path(os.environ["SNAPSHOT_TASK_ROOT"])
RID = os.environ["SNAPSHOT_RUN_ID"]
sys.path.insert(0, os.environ["TOOLS"])
import suite


def save(p, obj):
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


# ---------------------------------------------------------------- A16 findings
p = ROOT / "outputs" / RID / "A16" / "findings.json"
f = json.loads(p.read_text(encoding="utf-8"))
verdicts = {
    "F01": "v2 最终图打开确认：标题为「季度复盘 · Q4 收入与利润均创新高」，由 Q4 收入 180/利润 54 论证，完整可读",
    "F02": "v2 最终图打开确认：重点卡第三行「Q3 收入 128 万较 Q2 的 135 万回落 7 万」单独一行、完整可读",
    "F03": "v2 最终图打开确认：图例蓝=收入、橙=成本；柱顶 120/90/135/108/128/96/180/126 与 source.csv 一致",
    "F04": "v2 最终图打开确认：Y 轴 0/40/80/120/160/200、零线 y=500 加粗，8 柱共用零起点",
    "F05": "v2 最终图打开确认：Q4 最高、Q3 收入柱低于 Q2 收入柱；柱高=数值×1.25px，非仅改标签",
    "F06": "v2 最终图打开确认：利润明细 30/27/32/54 万元，Q4 高亮，四列完整",
    "F07": "v2 最终图打开确认：重点卡改为 Q4，三行文字各占一行、无重叠与裁切",
}
for x in f["findings"]:
    x["final_view_result"] = verdicts[x["id"]]
f["final_review"] = {
    "image": "corrected-report.png",
    "conclusion": "逐张打开 v1 与 v2 实际 PNG；v1 发现重点季度卡文字重叠溢出，v2 修复后复查通过。全部 7 项 findings 的修正均在最终图中可验证，3 项不确定项独立保留，未把审美偏好混作数值错。",
    "viewed_at": suite.now(),
}
save(p, f)
print("A16 findings updated", len(f["findings"]))

# ---------------------------------------------------------------- A17 examples
p = ROOT / "outputs" / RID / "A17" / "examples.json"
e = json.loads(p.read_text(encoding="utf-8"))
log = {}
for rec in suite.read_request_log("A17"):
    label = rec["label"]
    for a in rec["attempts"]:
        if a["success"]:
            log[label] = a
hand_view = {
    "01": "打开 handbook-01.png（v1 发现插图与说明重叠；v2 复查右侧插图/左侧说明不重叠、12 行代码与导语完整）",
    "02": "打开 handbook-02.png（v1 发现导语第二行被裁；v2 复查导语完整、11 行代码与插图完整）",
    "03": "打开 handbook-03.png v2：11 行代码含真实 < > 与 CDATA、插图 a<b && c>d / 左浅右深 / 富文本 Span 与独立示例一致",
    "04": "打开 handbook-04.png v2：12 行代码含 ImageFiltered sigmaX/sigmaY、插图模糊蓝块+锐利文字与独立示例一致",
}
ex_view = {
    "01": "打开 example-01.png：POST /snapshot / text/plain / 200 image/png 完整清晰",
    "02": "打开 example-02.png：蓝橙 2:1 色块、绿圆点、Stack + Positioned 完整",
    "03": "打开 example-03.png：a < b && c > d (CDATA)、半透明/不透明对照、富文本 Span 完整",
    "04": "打开 example-04.png：左侧蓝块高斯模糊、右侧两行文字锐利",
}
for x in e["examples"]:
    pid = x["page_id"]
    a = log.get("example-" + pid, {})
    x["response_evidence"] = {
        "http_status": a.get("http_status"), "content_type": a.get("content_type"),
        "request_id": a.get("request_id"),
        "response_file": a.get("response_file"),
        "dsl_file": "example-%s.snapshot" % pid, "png_file": "example-%s.png" % pid,
    }
    h = log.get("handbook-" + pid, {})
    x["view_evidence"] = {
        "example_png": ex_view[pid], "handbook_png": hand_view[pid],
        "handbook_response": {"http_status": h.get("http_status"),
                              "content_type": h.get("content_type"),
                              "request_id": h.get("request_id")},
        "consistency": "教学页核心子树逐字取自独立示例 DSL 行 %d–%d，1:1 于 400×240 区域；已用 ViewImage 对照确认文字/属性/子节点顺序/效果范围一致" %
                       (x["core_subtree"]["line_range_1based"][0], x["core_subtree"]["line_range_1based"][1]),
    }
e["review_note"] = {
    "viewed_at": suite.now(),
    "text": "4 个独立示例与 4 页手册均实际打开检查。v1 手册页发现教学插图与说明文字重叠、第2页导语换行被裁；v2 改为插图右置/说明左置并加高导语框后重新渲染并逐页复查，缺陷消除。示例 DSL 未改动，两版内容一致。",
}
save(p, e)
print("A17 examples updated", len(e["examples"]))

# ---------------------------------------------------------------- A18 story-audit
p = ROOT / "outputs" / RID / "A18" / "story-audit.json"
s = json.loads(p.read_text(encoding="utf-8"))
s["view_checks"] = [
    {"view": "full 1600x1000", "image": "three-act-story.png", "viewed": True,
     "result": "ViewImage 打开最终图：三幕各 15 圆（5 蓝/5 橙/5 灰，直径 36）与 3 节点完整在各自面板内；幕1 15 条连线全部指向唯一 N01，幕2 40px 紧密队列且连线加深加粗、N01 纵向拉伸 1.30，幕3 三束分流每节点 5 圆且至少两色；连线画在圆与节点下层，未遮圆；除总标题与三个幕名外无其它文字。"},
    {"view": "400px wide thumbnail", "image": "tmp/<run_id>/A18/v2/thumb-400.png", "viewed": True,
     "result": "ViewImage 打开 400px 宽缩略：三个浅色面板与三个幕名仍可辨；幕1 向心汇聚、幕2 紧密队列（与第一幕宽松弧的对比）、幕3 三束分流仍可感知；15 个圆仍可辨为独立圆点，三节点形状（方/菱/六边）仍可分辨；三幕叙事在缩略尺寸下仍可读，仅细连线与颜色计数变弱。"},
]
s["final_review"] = {
    "viewed_at": suite.now(),
    "selected_layout": "A",
    "text": "先制作 preview-A / preview-B 两张 1600×1000 实际预览并打开对比，选构图 A（幕1/幕2 间距对比强烈、三幕无越界）；构图 B 幕3 部分圆越出面板且过载对比弱，未选用。基于预览 A 完善：加深第二幕连线、N01 形变 1.25→1.30、第三幕连线略加深，守恒参数与节点身份不变。最终图与 400px 缩略均已实际打开并通过。",
}
save(p, s)
print("A18 story-audit updated")
