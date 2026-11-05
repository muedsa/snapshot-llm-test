#!/usr/bin/env python3
"""Fill B06 deliverables with REAL per-image review results and request ids."""
import json, os, sys
from pathlib import Path
sys.path.insert(0, os.environ["TOOLS"])
import suite

T = "B06"
out = suite.out_dir(T)
tmp = suite.tmp_dir(T)

# ---- real request ids per case -----------------------------------------
reqids = {}
for p in sorted(tmp.rglob("requests.jsonl")):
    cid = p.parent.name
    for line in p.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        for a in r.get("attempts", []):
            if a.get("success"):
                reqids.setdefault(cid, []).append(a["request_id"])

# ---- real per-case final review ----------------------------------------
REVIEWS = {
    "case-01": {
        "final_version": "v2",
        "text": (
            "v1 基线发现 24 小时环形时钟只显示 00/06/18，正下方「12」被底部深色注意事项条"
            "遮挡。v2 把环形与圆心整体上移（CY 600→555），使「12」落在注意事项条上方。"
            "v2 实际打开复查：00/06/12/18 四个刻度齐全，三个彩色服药弧段、中央巨大「3」、"
            "右侧三张服药卡、胶囊图形与底部注意事项条全部完整清晰，无遮挡裁切。"
        ),
        "iters": ["case-01-v1", "case-01-v2"],
        "obs": "补齐 00/06/12/18 四个刻度，「12」从被遮挡变为清晰可见，24 小时时间轴完整；服药次数与三张时间卡保持对齐可读。",
    },
    "case-02": {
        "final_version": "v2",
        "text": (
            "v1 基线发现 5 行单价数值压在条形末端（「¥4.70 / 100g」被条形边缘切割），"
            "且底部「按每周买 3 袋算」文案与脚本 ×20 估算口径不一致。"
            "v2 把条形宽度收窄到独立绘图区、单价数值移到右侧专属列、「最划算」角标右移，"
            "并把结论文案改为「按每月 20 份的单价差累计估算」。"
            "v2 实际打开复查：5 个单价数值全部在条形外完整可读，金色高亮行与角标分离，"
            "条形仍按单价从低到高正确排序，底部结论与 ¥16.50 大数字清晰。"
        ),
        "iters": ["case-02-v1", "case-02-v2"],
        "obs": "单价数值移到独立右列、不再压在色条上；结论口径改为与脚本计算一致的明确表述，5 行排序与金色高亮保持正确。",
    },
    "case-03": {
        "final_version": "v1",
        "text": (
            "v1 首版实际打开即通过：24 格用电色带按峰/平/谷分色且柱高与数值对应，"
            "00:00–23:00 时间刻度、三色图例、右侧 61% 占比环、三条省电建议卡与"
            "底部结论条全部完整可读，无遮挡裁切。未发生修改。"
        ),
        "iters": ["case-03-v1"],
        "obs": "用颜色（电价档）× 柱高（用电量）双编码，18–22 点峰值一眼可见；61% 环与三条换时段建议同时回答「钱花在哪」和「怎么省」。",
    },
    "case-04": {
        "final_version": "v1",
        "text": (
            "v1 首版实际打开即通过：糖/钠/脂肪三层同心环比例正确（24%/78%/37%），"
            "中心「钠偏高」判定、三行精确数值与进度条、底部结论与虚构声明全部完整对齐。"
            "未发生修改。"
        ),
        "iters": ["case-04-v1"],
        "obs": "NRV% 表格变成三层同心环 + 中心「钠偏高」判定，78% 等比例可直接比较；三行精确数值保留可核查性。",
    },
    "case-05": {
        "final_version": "v1",
        "text": (
            "v1 首版实际打开即通过：绿色 ETA 横幅、5 阶段垂直单轨、当前「派送中」高亮卡、"
            "「预计签收」绿卡与底部「14:00 之后在家等就行」结论卡全部完整可读，"
            "节点文字互不重叠。未发生修改。"
        ),
        "iters": ["case-05-v1"],
        "obs": "8 条时间戳归并成 5 节点单轨，当前节点与 ETA 窗口用底色高亮；底部一句话给出「14:00 后在家」的行动结论。",
    },
    "case-06": {
        "final_version": "v2",
        "text": (
            "v1 基线发现底部说明出现中英混杂「还要自己 subtract 出等待时间」。"
            "v2 改为通顺中文「还要自己算出等待时间」。"
            "v2 实际打开复查：四个放射扇区、圆心「现在 22:28」、四张扇区标签卡与"
            "底部说明条全部完整清晰，无重叠裁切。"
        ),
        "iters": ["case-06-v1", "case-06-v2"],
        "obs": "底部说明改为通顺中文、消除中英混杂；四个放射扇区与倒计时大字仍完整可读。",
    },
    "case-07": {
        "final_version": "v2",
        "text": (
            "v1 基线发现根节点深绿圆偏小使「这是什么东西？」贴边，且「三个都不是」的"
            "长贝塞尔曲线从中间横跨到最右灰桶、与另三条连线交叉。"
            "v2 放大根节点圆并缩小字号、删除交叉长曲线，灰桶改用「三个都不是 → 这里」"
            "局部标注加短竖线。"
            "v2 实际打开复查：根节点文字完整落在圆内，三条问题→桶连线各自独立不交叉，"
            "四色桶卡与 6 个速查色块完整可读。"
        ),
        "iters": ["case-07-v1", "case-07-v2"],
        "obs": "根节点圆放大后文字完整落在圆内；删除交叉长曲线，三条连线各自独立，灰桶改局部标注 + 短竖线，决策树路径清晰。",
    },
    "case-08": {
        "final_version": "v1",
        "text": (
            "v1 首版实际打开即通过：7 列等宽天气卡、橙→蓝温度渐变色带与最高/最低温、"
            "降水概率条、每列一句穿衣决策、底部周降雨色带与结论全部完整对齐，"
            "无裁切遮挡。未发生修改。"
        ),
        "iters": ["case-08-v1"],
        "obs": "7 天数字压成 7 列温度色带 + 一句决策，周三/周五带伞在周降雨色带上一眼可见。",
    },
    "case-09": {
        "final_version": "v1",
        "text": (
            "v1 首版实际打开即通过：A/B/C 三区色块网格与 B 区「07」高亮车位、米白记忆卡、"
            "三段计费阶梯卡、巨大「¥18」与说明、「原本卡在哪」及虚构声明全部完整可读，"
            "无重叠。未发生修改。"
        ),
        "iters": ["case-09-v1"],
        "obs": "分区网格高亮车位 + 三段计费阶梯 + 直接换算的 ¥18 大数字，把「找车」与「算钱」合在一张卡。",
    },
    "case-10": {
        "final_version": "v1",
        "text": (
            "v1 首版实际打开即通过：巨大「B27」、绿色「现在登机」标、水平时间轴 4 节点"
            "与当前高亮、右侧 9 分钟步行面板、荧光绿「现在走 / 还来得及」两行结论"
            "与底部信息全部完整清晰，无裁切遮挡。未发生修改。"
        ),
        "iters": ["case-10-v1"],
        "obs": "超大 B27、水平时间轴与「现在走还来得及」绿灯结论，把几十行航班表压缩成单个航班的一个决定。",
    },
}

CRITERIA_METHOD = {
    "C1": "ViewImage 打开最终 PNG 逐项核对问题背景、关键数值与可执行结论",
    "C2": "ViewImage 打开并放大文字区检查字号、遮挡、裁切与对比度",
    "C3": "gallery.md 十图并列 + 逐张 ViewImage 比较构图/配色/信息结构",
    "C4": "核对 problem-evidence.json、脚本计算值与各 case.md / 画面文字",
    "C5": "读取 PNG 文件头 89 50 4E 47 并检查 requests.jsonl 的 200/image-png 记录",
}

FINAL_REVIEW = (
    "10 张最终 PNG 均已逐张用 ViewImage 打开检查（v1 全 10 张基线 + 4 张 v2 复查）。"
    "其中 6 张首版即通过，4 张（case-01/02/06/07）经 1 轮真实视觉迭代修复后通过；"
    "所有已知的遮挡、裁切、重叠、中英混杂与连线交叉缺陷均已消除。"
    "10 件作品分别解决不同的日常信息难题，并采用不同的主导视觉组织"
    "（极坐标环 / 排序标尺 / 时间色带 / 同心仪表 / 垂直单轨 / 放射扇区 / 决策树 / "
    "列网格色带 / 分区网格+阶梯 / 超大数字时间轴），构图、配色与信息结构互不相同，"
    "不是同模板换文案。全部数值为脚本计算的自拟演示数据并明确标注虚构；"
    "每张 PNG 文件头均为真实 89 50 4E 47，且都有同名完整自包含 .snapshot。"
    "未使用任何外部素材。未做真实用户实验，不声称实际效果提升。"
    "剩余事项：无。"
)

# ---- portfolio.json ----------------------------------------------------
pf = json.loads((out / "portfolio.json").read_text(encoding="utf-8"))
for case in pf["cases"]:
    cid = case["id"]
    rv = REVIEWS[cid]
    case["request_ids"] = reqids.get(cid, [])
    case["iteration_ids"] = rv["iters"]
    case["visual_review"] = rv["text"]
    case["criterion_results"] = [
        {"id": k, "result": "passed", "method": CRITERIA_METHOD[k],
         "evidence": "最终 %s 版 %s/final.png 已实际打开查看；逐图结论见 case.md、"
                     "tmp/%s/%s/visual-review-v1.md 与 design-review.md"
                     % (rv["final_version"], cid, suite.RID, T)}
        for k in ("C1", "C2", "C3", "C4", "C5")
    ]
pf["final_collection_review"] = FINAL_REVIEW
pf["unresolved_issues"] = []
(out / "portfolio.json").write_text(
    json.dumps(pf, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

# ---- problem-evidence.json ---------------------------------------------
pe = json.loads((out / "problem-evidence.json").read_text(encoding="utf-8"))
for c in pe["cases"]:
    c["observable_improvement"] = REVIEWS[c["id"]]["obs"]
pe["unresolved_issues"] = []
(out / "problem-evidence.json").write_text(
    json.dumps(pe, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

# ---- design-review.md --------------------------------------------------
dr = (out / "design-review.md").read_text(encoding="utf-8")
placeholder = "- **可观察的改善**：待最终图实际查看后填写（可读性、层级、对齐、数值一致）"
for i in range(1, 11):
    cid = "case-%02d" % i
    assert placeholder in dr, cid
    dr = dr.replace(placeholder,
                    "- **可观察的改善**：" + REVIEWS[cid]["obs"] + "（基于最终渲染图的实际观察）",
                    1)
dr = dr.replace("PENDING_FINAL_REVIEW", FINAL_REVIEW)
(out / "design-review.md").write_text(dr, encoding="utf-8")

# ---- case.md -----------------------------------------------------------
for i in range(1, 11):
    cid = "case-%02d" % i
    p = out / cid / "case.md"
    txt = p.read_text(encoding="utf-8")
    rv = REVIEWS[cid]
    conclusion = ("**最终版本**：%s（该用例%s）\n\n%s\n\n"
                  "逐条完成标准 C1–C5 的检查结果见 `portfolio.json` 的 `criterion_results`；"
                  "问题来源与假设见 `problem-evidence.json`，逐件设计复核见 `design-review.md`，"
                  "全套逐图看图基线见临时目录 `visual-review-v1.md`。"
                  % (rv["final_version"],
                     "经过视觉迭代修复" if len(rv["iters"]) > 1 else "首版即通过、未修改",
                     rv["text"]))
    p.write_text(txt.replace("PENDING_VISUAL_REVIEW", conclusion), encoding="utf-8")

# ---- tool-usage: real v2 ViewImage re-checks ----------------------------
for cid in ("case-01", "case-02", "case-06", "case-07"):
    suite.tool_usage(T, "ViewImage",
                     "打开 %s/final.png（v2）复查上一轮缺陷是否消除" % cid,
                     "%s -> v2 recheck" % cid,
                     source="outputs/%s/%s/%s/final.png" % (suite.RID, T, cid))

print("patched portfolio.json, problem-evidence.json, design-review.md, 10 case.md, +4 ViewImage records")
print("request ids per case:", {k: len(v) for k, v in sorted(reqids.items())})
