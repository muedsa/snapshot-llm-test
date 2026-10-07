"""Append this wrap-up session's real tool usage to B03/tool-usage.jsonl.

Entries 1..32 of that file were written by the interrupted run; #31 and #32 there
announced snapshot-usage.md and the wrapup call before the session died, so they
were aspirational at the time. This session actually did that work, and the rows
below record what was really done, in order.
"""
import io
import json
import os
from datetime import datetime, timezone, timedelta

RUN = "20261004-182918"
TMP = os.path.join("tmp", RUN, "B03")
PATH = os.path.join(TMP, "tool-usage.jsonl")
CST = timezone(timedelta(hours=8))


def now():
    return datetime.now(CST).isoformat(timespec="milliseconds")


ENTRIES = [
    ("read", "收尾复审：逐张打开 10 张 final.png 做整体策展审查（每张单独打开，共 10 次）",
     "outputs/%s/B03/case-01..case-10/final.png" % RUN,
     "outputs/%s/B03/（仅观察，未改动）" % RUN, ["case-01", "case-02", "case-03",
     "case-04", "case-05", "case-06", "case-07", "case-08", "case-09", "case-10"]),
    ("bash(python)", "用 check_deliverables.py 确认缺哪三份收尾文件",
     "tmp/%s/_suite/check_deliverables.py" % RUN, None, []),
    ("crop", "3.4× 放大 case-01 月面，发现标签「亏凸月 · 照亮 72%」与画面（约 20% 右侧"
     "蛾眉）矛盾",
     "outputs/%s/B03/case-01/final.png" % RUN,
     "tmp/%s/B03/crops/final-review-c01-moon.png" % RUN, ["case-01"]),
    ("crop", "4.0× 放大 case-04 B 区 05 排，核实那条空心小格是刻意的「本排座位放大条」"
     "而不是错位元素",
     "outputs/%s/B03/case-04/final.png" % RUN,
     "tmp/%s/B03/crops/final-review-c04-row05.png" % RUN, ["case-04"]),
    ("crop", "6× / 8× 放大 case-02 左侧竖排标注，初看像乱码",
     "outputs/%s/B03/case-02/final.png" % RUN,
     "tmp/%s/B03/crops/final-review-c02-vertlabel.png" % RUN, ["case-02"]),
    ("write", "写 rotcheck.py（crop + 旋转），把 case-02 的竖排标注旋正读回，"
     "确认是正常的「346 px」尺寸标注，排除一处疑似缺陷",
     "tmp/%s/B03/rotcheck.py" % RUN,
     "tmp/%s/B03/crops/final-review-c02-vert-rot2.png" % RUN, ["case-02"]),
    ("crop", "2.6× 放大两张取餐牌逐行核金额，发现 B 牌「合计 86 元」与三行 62 元不符；"
     "同时读到票面写着「外带 TAKEAWAY / 堂食」",
     "outputs/%s/B03/case-02/final.png" % RUN,
     "tmp/%s/B03/crops/final-review-c02-cardA.png、final-review-c02-cardB.png" % RUN,
     ["case-02"]),
    ("write", "写 review_audit.py，独立重算 case-01 潮位、case-01 月相（Meeus 第 47 章"
     "低精度级数）、case-10 昼长，用来分辨真实算错与四舍五入假象",
     "tmp/%s/B03/review_audit.py" % RUN, None, ["case-01", "case-10"]),
    ("bash(python)", "跑 review_audit.py：潮位与昼长全部对得上（是四舍五入），"
     "月面对不上（真实值 37.0% 残月，图上是 20% 右侧蛾眉，标签写 72%）",
     "tmp/%s/B03/review_audit.py" % RUN, None, ["case-01", "case-10"]),
    ("crop", "2.6× 放大 case-07 的 K 行交点、3.2× 放大 case-10 的楼层标高、"
     "3.0× 放大 case-10 进深条矩阵，确认没有文字被静默丢弃或比例失真",
     "outputs/%s/B03/case-07|10/final.png" % RUN,
     "tmp/%s/B03/crops/final-review-c07-Krow.png、final-review-c10-depthlabels.png、"
     "final-review-c10-depthrows.png" % RUN, ["case-07", "case-10"]),
    ("bash(python)", "把改渲染前的三张 final.png / final.snapshot 备份到 "
     "pre-final-review/，保证旧版不被覆盖丢失",
     "outputs/%s/B03/case-01|02|09/final.*" % RUN,
     "tmp/%s/B03/pre-final-review/" % RUN, ["case-01", "case-02", "case-09"]),
    ("write", "写 patch_review_c01.py / c02 / c09，修掉复审发现的三处「图与字互相打脸」",
     "tmp/%s/B03/patch_review_c01.py、patch_review_c02.py、patch_review_c09.py" % RUN,
     None, ["case-01", "case-02", "case-09"]),
    ("bash(python)", "在 .orig.py 基线上打补丁并重渲染三张（每张 1 次请求），"
     "全部 HTTP 200 image/png",
     "tmp/%s/B03/build_c01.py、build_c02.py、build_c09.py" % RUN,
     "outputs/%s/B03/case-01|02|09/final.png" % RUN,
     ["case-01", "case-02", "case-09"]),
    ("crop", "3.0× 复验修好的 case-01 月相：左亮右暗、亮面约 37%、标签「残月 · 照亮 37%」"
     "「月龄 23.4 d · 由 D=285.0° 算得」",
     "outputs/%s/B03/case-01/final.png" % RUN,
     "tmp/%s/B03/crops/final-review2-c01-moon.png" % RUN, ["case-01"]),
    ("crop", "2.4× / 2.8× 复验 case-02：副标题「取餐牌 PICKUP / 台号 T-07」、"
     "「合计 62 元」",
     "outputs/%s/B03/case-02/final.png" % RUN,
     "tmp/%s/B03/crops/final-review2-c02-ticketB.png、final-review2-c02-total.png" % RUN,
     ["case-02"]),
    ("crop", "1.8× 复验 case-09 摘要带：印「12 条变更里 2 条破坏性变更、2 条弃用、"
     "3 条新增、5 条修复」",
     "outputs/%s/B03/case-09/final.png" % RUN,
     "tmp/%s/B03/crops/final-review2-c09-summary.png" % RUN, ["case-09"]),
    ("read", "复审后重新完整打开 case-01 的 final.png，确认加 176 个元素后其余版面未受影响",
     "outputs/%s/B03/case-01/final.png" % RUN, None, ["case-01"]),
    ("write", "写 patch_review_portfolio.py，把三处修复与三处排除折进 "
     "portfolio.json / portfolio.md / gallery.html 的数据源",
     "tmp/%s/B03/patch_review_portfolio.py" % RUN, None,
     ["case-01", "case-02", "case-09"]),
    ("bash(python)", "重跑 build_portfolio.py：尺寸/字节/元素数全部从交付文件重新读回",
     "tmp/%s/B03/build_portfolio.py" % RUN,
     "outputs/%s/B03/portfolio.json、portfolio.md、gallery.html" % RUN,
     ["case-01", "case-02", "case-03", "case-04", "case-05", "case-06", "case-07",
      "case-08", "case-09", "case-10"]),
    ("write", "改写 case-01 / case-02 / case-09 的 case.md（新增的复审迭代、"
     "修好的自检项、修正后的遗留），并给 technique-notes.md 补上晨昏线填充手法"
     "与「收尾复审」一节",
     "outputs/%s/B03/case-01|02|09/case.md、technique-notes.md" % RUN, None,
     ["case-01", "case-02", "case-09"]),
    ("write", "写 review_counts.py，从 requests.jsonl 实测汇总请求/渲染/失败/文档计数，"
     "供 snapshot-usage.md 引用（不手填数字）",
     "tmp/%s/B03/review_counts.py" % RUN, None, []),
    ("write", "写 snapshot-usage.md：文档与字体来源、实际标签属性、29 条 DSL 语义坑、"
     "逐件自检表、问题与修复表、未解决事项（token/费用一律 null）",
     "outputs/%s/B03/snapshot-usage.md" % RUN, None, []),
    ("write", "写 log_review.py：由 requests.jsonl + 各 case.md 的迭代记录重建 "
     "iterations.jsonl（63 行），并调用 wrapup.wrapup() 生成 task-metrics.json、"
     "更新套件状态；随后修正 B 类 case 子目录导致的 final_pngs 计数",
     "tmp/%s/B03/log_review.py" % RUN,
     "tmp/%s/B03/iterations.jsonl、outputs/%s/B03/task-metrics.json" % (RUN, RUN), []),
    ("bash(python)", "跑 check_deliverables.py 复核全部交付物齐备", None, None, []),
]

with io.open(PATH, "a", encoding="utf-8", newline="\n") as fh:
    for tool, purpose, inputs, outputs, affects in ENTRIES:
        fh.write(json.dumps({
            "run_id": RUN, "task_id": "B03", "tool": tool, "purpose": purpose,
            "inputs": inputs, "outputs": outputs, "affects_cases": affects,
            "at": now(),
            "note": "收尾复审阶段（被中断的运行恢复后）实际发生的工具调用",
        }, ensure_ascii=False) + "\n")
print("appended", len(ENTRIES), "tool-usage rows")
