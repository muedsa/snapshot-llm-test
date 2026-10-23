"""A21 round-03 看图证据补记。

把本次会话中实际打开过的 round-03 交付图、裁切视图、去文字背景辅助图与
对比度局部证据图逐条追加进 tmp/<run>/A21/viewing-evidence.json 的
rounds["3"]，只追加本轮，不改写第一、二轮的既有记录。

时间精度：本会话内实际打开，记到分钟级，不做秒级补造。
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve()
RUN_ID = HERE.parents[2].name
SUITE_ROOT = HERE.parents[4]
TASK = SUITE_ROOT / "outputs" / RUN_ID / "A21"
TMP = SUITE_ROOT / "tmp" / RUN_ID / "A21"
R = TASK / "round-03"
PV = TMP / "preview" / "round-03"
AU = TMP / "backgrounds"
EV = TMP / "contrast-evidence"
DOC = TMP / "viewing-evidence.json"


def rec(eid, phase, artifact, rel, view_type, ts, obs):
    p = SUITE_ROOT / rel
    return {"event_id": eid, "round": 3, "phase": phase, "artifact": artifact,
            "image": {"path": rel,
                      "sha256": hashlib.sha256(p.read_bytes()).hexdigest()},
            "view_type": view_type,
            "viewed_at": ts,
            "viewed_at_precision": "minute-level（本次会话内实际打开）",
            "observed": obs}


EVENTS = [
    rec("ev-a21-029", "delivery", "launch-portrait",
        "outputs/%s/A21/round-03/launch-portrait.png" % RUN_ID,
        "whole-1to1", "2026-10-20T09:49+08:00",
        "整图 1:1 首次查看。浅底主题落地：页面为极浅蓝灰 #F5F8FC，无暗场噪点。"
        "三行长标题 #0B1B33 深藏蓝、无发光阴影，边缘干净；眉标 ONLINE LAUNCH "
        "深青蓝 + 橙色竖条；日期橙红 #C2410C；讲者与赞助方中灰蓝；新增英语短句 "
        "Clarity through structure 在讲者与网址牌之间，深青蓝、字高明显低于日期。"
        "网址牌与报名状态牌为纯白底、圆角收口完整。发光球移到右侧标题与信息之间的"
        "空区，浅蓝辉光外环很淡，未压到任何一行文字。上下左右都有余量。"),
    rec("ev-a21-030", "delivery", "launch-wide",
        "outputs/%s/A21/round-03/launch-wide.png" % RUN_ID,
        "whole-1to1", "2026-10-20T09:50+08:00",
        "整图 1:1 首次查看。左栏品牌行 + 眉标 + 两行长标题（15 字行）排满，"
        "底部信息竖排为日期 → 讲者 → 英语短句 → 网址牌 → 赞助方 → 报名状态牌六行，"
        "收口在底部扩展空间内。右栏发光球占整栏中部，浅蓝外辉光与球体轮廓清楚。"
        "浅底上六个品牌构件（叠层主标记、亮核、球、光带、强调条、牌子族）都在，"
        "无深底主题残留。"),
    rec("ev-a21-031", "delivery", "launch-portrait",
        "tmp/%s/A21/preview/round-03/launch-portrait-info.png" % RUN_ID,
        "crop-info-1.5x", "2026-10-20T09:50+08:00",
        "信息栈 1.5x 放大。强调条 → 日期 → 讲者 → Clarity through structure → "
        "网址牌五档层级清楚：日期 56px 橙红最重，讲者与赞助方中灰蓝次级，"
        "英语短句 28px 深青蓝独立成档，网址牌内 layerlight.example.org 深青蓝。"
        "四行文字全部落在页面底纯色上，无辉光、无渐变干扰，字边缘锐利可读。"
        "发光球的浅蓝外环在最右侧，与文字之间留有可见间隙。"),
    rec("ev-a21-032", "delivery", "launch-portrait",
        "tmp/%s/A21/preview/round-03/launch-portrait-footer.png" % RUN_ID,
        "crop-footer-1.5x", "2026-10-20T09:50+08:00",
        "页脚 1.5x 放大。赞助方 Northstar Research / 云构工具 保留，中灰蓝可读；"
        "报名状态牌「免费参加 · 无需报名」纯白底 + 深青蓝边框，文字 #0B1B33，"
        "圆角收口完整无锯齿。第二条 round-03.md 硬约束「不得让赞助方消失」确认"
        "满足。"),
    rec("ev-a21-033", "delivery", "launch-portrait",
        "tmp/%s/A21/preview/round-03/launch-portrait-header.png" % RUN_ID,
        "crop-header-1.6x", "2026-10-20T09:51+08:00",
        "顶部品牌行 1.6x 放大。叠层主标记三段蓝由暗到亮，亮核为近白青色、"
        "压在最亮板材上仍读得出边界——浅底上亮核未变成一团白。字标「叠光」"
        "深青蓝、「Layerlight」中灰蓝。右上角部线叠层水印为浅蓝描边无填充，"
        "与左上实心主标记区分清楚，未与文字相撞。"),
    rec("ev-a21-034", "delivery", "launch-wide",
        "tmp/%s/A21/preview/round-03/launch-wide-info.png" % RUN_ID,
        "crop-info-2.0x", "2026-10-20T09:51+08:00",
        "横版信息栈 2.0x 放大。日期橙红 44px、讲者中灰蓝、英语短句深青蓝 26px、"
        "网址牌内网址深青蓝，四档颜色不混淆。网址牌左右内边距均匀，左侧主色圆点"
        "与文字基线对齐。最右缘可见发光球外环的极淡浅蓝，未压到任何字形。"),
    rec("ev-a21-035", "contrast", "launch-portrait",
        "tmp/%s/A21/contrast-evidence/launch-portrait-date-bg.png" % RUN_ID,
        "contrast-evidence-background", "2026-10-20T09:52+08:00",
        "对比度证据图：日期所在区域的去文字背景局部。整片为均匀的 #F5F8FC 页面底，"
        "无氛围 wash、无辉光叠层——证实全图最差对比度段（date）测到的背景就是"
        "页面底名义色本身，而不是某个不利的渐变叠层。发光球外环在框外右侧，"
        "未进入取样区。"),
    rec("ev-a21-036", "delivery", "launch-portrait",
        "tmp/%s/A21/preview/round-03/launch-portrait-title.png" % RUN_ID,
        "crop-title-1.3x", "2026-10-20T09:52+08:00",
        "标题 1.3x 放大。三行 66px 加粗，27 字长标题完整、行距 1.30em 不挤不撞；"
        "确认已取消前两轮的青色发光阴影，字边缘在浅底上无半透明光晕。"
        "裁切框右下角刚露出发光球辉光的起点，与第三行字墨迹之间有明显浅色间隙。"),
    rec("ev-a21-037", "delivery", "launch-portrait",
        "tmp/%s/A21/preview/round-03/launch-portrait-orb.png" % RUN_ID,
        "crop-orb-1.5x", "2026-10-20T09:53+08:00",
        "竖版发光球 1.5x 放大。径向渐变由中上亮蓝过渡到边缘深藏蓝，立体感到位；"
        "外环细线主色蓝；外辉光在浅底上收成一圈极淡的冷色，边缘自然消失不显脏。"
        "球内光带为近白青色圆头条。左上角的标题墨迹属于相邻文字段，与球体不相交。"),
    rec("ev-a21-038", "delivery", "launch-wide",
        "tmp/%s/A21/preview/round-03/launch-wide-orb.png" % RUN_ID,
        "crop-orb-1.4x", "2026-10-20T09:53+08:00",
        "横版发光球 1.4x 放大。三条光带自上而下宽度与亮度递减（0.90 / 0.58 / 0.34）"
        "关系保留，圆头收口完整；球体轮廓在浅底上由辉光与外环共同勾勒，"
        "边界清楚不糊。品牌图形在浅底主题下的形制与前两轮一致。"),
    rec("ev-a21-039", "delivery", "launch-wide",
        "tmp/%s/A21/preview/round-03/launch-wide-footer.png" % RUN_ID,
        "crop-footer-2.0x", "2026-10-20T09:54+08:00",
        "横版页脚 2.0x 放大。赞助方与报名状态牌均在，层级低于网址牌；"
        "状态牌边框为主色深青蓝，与网址牌的中性浅蓝边框区分语义。"),
    rec("ev-a21-040", "delivery", "launch-wide",
        "tmp/%s/A21/preview/round-03/launch-wide-header.png" % RUN_ID,
        "crop-header-1.8x", "2026-10-20T09:54+08:00",
        "横版品牌行 1.8x 放大。主标记亮核与板材层级清楚；字标两色可读；"
        "眉标橙竖条 + 深青蓝 ONLINE LAUNCH，字距均匀。"),
    rec("ev-a21-041", "delivery", "launch-wide",
        "tmp/%s/A21/preview/round-03/launch-wide-title.png" % RUN_ID,
        "crop-title-1.5x", "2026-10-20T09:55+08:00",
        "横版标题 1.5x 放大。两行 52px，15 字行排满不折行、不压窄；"
        "确认 <Text> 无 transform 属性，字形比例正常。底部露出的橙色为日期顶部。"),
    rec("ev-a21-042", "contrast", "launch-portrait",
        "tmp/%s/A21/backgrounds/launch-portrait.notext.png" % RUN_ID,
        "auxiliary-notext-1to1", "2026-10-20T09:56+08:00",
        "去文字辅助背景图整图 1:1。所有非文字层齐全：叠层主标记与亮核、眉标橙竖条、"
        "主色强调条、网址牌与报名状态牌（含左侧主色圆点）、角部线叠层水印、"
        "发光球（辉光 + 外环 + 球体 + 三条光带）、左下氛围 wash；画面中无任何文字。"
        "确认该渲染与交付图只差在 <Text> 节点，因此可作为文字下方实际合成背景的"
        "取样源。此图仅存临时目录，不进入交付。"),
    rec("ev-a21-043", "contrast", "launch-wide",
        "tmp/%s/A21/backgrounds/launch-wide.notext.png" % RUN_ID,
        "auxiliary-notext-1to1", "2026-10-20T09:56+08:00",
        "去文字辅助背景图整图 1:1。左栏除文字外的品牌行、眉标竖条、网址牌与报名"
        "状态牌齐全，右栏发光球完整（辉光、外环、球体、三条光带），左上氛围 wash"
        "可见。无任何文字。与交付横版只差在 <Text> 节点。仅存临时目录。"),
]

CONCLUSION = (
    "两图通过实际看图验收：浅底主题落地干净，页面为极浅蓝灰 #F5F8FC、牌子为纯白；"
    "9 条文案全部保留（含第二轮新增的赞助方与报名状态牌，以及本轮新增的英语短句"
    "「Clarity through structure」）；主标题取消发光阴影后字边缘在浅底上锐利，"
    "三行/两行不折不挤；6 个品牌构件的形态、层数与递减关系未变，只换色带；"
    "发光球移到右列空区、辉光收敛后，未压到任何一行文字，"
    "赞助方与报名状态牌仍在网址牌之下。对比度用去文字辅助渲染量取实际合成背景，"
    "两图 23 段普通文字全量检查，全局最小 4.8616（阈值 4.5），"
    "最差段为竖版日期 #C2410C 对页面底 #F5F8FC，证据见 "
    "round-03/contrast-audit.json。本轮首版即通过，未产生改进迭代。"
)


def main() -> int:
    for st in (sys.stdout, sys.stderr):
        if hasattr(st, "reconfigure"):
            st.reconfigure(encoding="utf-8")
    doc = json.loads(DOC.read_text(encoding="utf-8"))
    before = len(doc.get("rounds", {}).get("2", {}).get("image_open_events", []))
    for e in EVENTS:
        p = SUITE_ROOT / e["image"]["path"]
        if not p.exists():
            raise SystemExit("证据文件不存在: %s" % p)
    doc.setdefault("rounds", {})["3"] = {
        "conclusion": CONCLUSION,
        "image_open_events": EVENTS,
        "note": "辅助去文字背景图（ev-a21-042 / ev-a21-043）只作对比度取样的"
                "临时证据，不属于交付作品；其 PNG 与 DSL 均在临时目录，"
                "交付目录内没有对应文件",
    }
    doc["updated_at"] = "2026-10-20T09:57+08:00"
    DOC.write_text(json.dumps(doc, ensure_ascii=False, indent=1),
                   encoding="utf-8")
    print("round-02 事件数（未改动）: %d" % before)
    print("round-03 事件数: %d" % len(EVENTS))
    print("wrote", DOC.relative_to(SUITE_ROOT).as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
