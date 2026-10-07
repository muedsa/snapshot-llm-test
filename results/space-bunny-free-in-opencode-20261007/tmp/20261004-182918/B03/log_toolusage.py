"""B03 · tool-usage.jsonl (B-track extra log). Real calls only; HTTP renders are
already in requests.jsonl and are NOT counted a second time here."""
from __future__ import annotations

import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = "20261004-182918"
ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
NOTE = ("HTTP renders are recorded in requests.jsonl and are NOT counted again here")

E = []


def add(tool, purpose, inputs, outputs, affects, detail=None):
    E.append({"task_id": "B03", "run_id": RUN, "tool": tool, "purpose": purpose,
              "inputs": inputs, "outputs": outputs, "affects_cases": affects,
              "detail": detail, "note": NOTE})


add("read", "读取套件实测 DSL 手册，取得本库已验证的结论，避免重复踩已修过的语法错误",
    "tmp/%s/_suite/DSL-HANDBOOK.md" % RUN, [], "all",
    "手册第 3 节「未知属性被静默忽略」后来在 case-08（Container opacity）与 case-09"
    "（fontFeatures=zzzz）上再次应验；第 2 节「矩形永远包在 Positioned 里」的根因在 "
    "case-10 被 probe-c09f 定位到 Stack fit=EXPAND")
add("read", "读取单题执行清单，确认输出/临时目录、留痕与 wrapup 调用的硬要求",
    "tmp/%s/_suite/WORK-ORDER.md" % RUN, [], "all")
add("read", "读取 B03 的 task.json 与 TASK.md，确认 B 类交付结构与 10 件下限",
    "tasks/B03-dsl-creative-frontier/task.json; TASK.md", [], "all",
    "case_artifacts = final.png/final.snapshot/case.md；common_outputs = portfolio.json/"
    "portfolio.md/gallery.html/snapshot-usage.md/task-metrics.json；"
    "additional_outputs = technique-notes.md；log_files 含 tool-usage.jsonl")
add("read", "读取交付模板，确认 portfolio/task-metrics/snapshot-usage 的字段结构",
    "tasks/B03-dsl-creative-frontier/templates/*", [], "all")
add("bash(python)", "列出 B03 输出目录，摸清中断时已交付 8 个 case",
    "outputs/%s/B03/" % RUN, "控制台输出", "all",
    "case-01..case-08 各有 final.png+final.snapshot+case.md；根目录缺 2 件与 6 个文件")
add("read", "读取中断前留下的 8 件 case.md，复用已实测的语义与迭代记录，避免重复实验",
    "outputs/%s/B03/case-0{1..8}/case.md" % RUN, [], "case-01..case-08")
add("read", "读取 8 张已有 final.png 做整体审查（每张单独打开）",
    "outputs/%s/B03/case-0{1..8}/final.png" % RUN, "看图结论 8 条", "case-01..case-08",
    "确认画幅/底色基调互不重复、每张都有可复述的核心数字；未发现需要回炉的既成品")
add("read", "读取中断前的计划与脚本，复用探针与共享库",
    "tmp/%s/B03/plan.md; wlib.py; probe_lib.py; build_c0*.py" % RUN, [],
    "case-09, case-10",
    "plan.md 里已写好的『16 组里只有 ss01/ss02 可能生效』的预判在 case-09 被探针证实；"
    "wlib.Frame/chip/hatch/ring/polar/seg/dim_v 直接复用")
add("bash", "读取已抓取的官方文档，取出 Text/WidgetSpan/Raw/渐变/Clip*/枚举的权威属性表",
    "tmp/%s/B03/docs/reference_parser-tags.html; reference_enums.html; guides_media-text.html" % RUN,
    "控制台提取的纯文本", "case-09, case-10",
    "从 Text 属性表拿到 foregroundMode/decoration*/fontFeatures/strut*/textHeightMode 的"
    "完整清单；从枚举页确认 PaintStrokeCap/Join/PaintStrokeJoin 未收录，只能实测")
add("write", "编写 case-09 的三张能力探针（fontFeatures×fontFamily / 前景画笔与装饰线 / 行内组合）",
    "tmp/%s/B03/probe_c09.py" % RUN, "probes/probe-c09a-fontfeat.png 等", "case-09")
add("bash(python)", "运行 probe_c09.py 并逐张打开探针图",
    "probe_c09.py", "probe-c09a/b/c 三张 PNG + 控制台告警", "case-09",
    "首轮 400 两处：foregroundStrokeCap=BEVEL 无此枚举、text= 属性里含裸双引号")
add("write", "编写枚举/格式逐项探测脚本（每个取值一次独立请求，互不影响）",
    "tmp/%s/B03/probe_c09_enum.py" % RUN, "accepted/rejected 清单", "case-09",
    "两轮穷举：textHeightMode 与 fontEdging 的所有候选全部 400；"
    "fontFeatures=\"zzzz\" 被接受")
add("bash(python)", "运行枚举探测并读结果", "probe_c09_enum.py",
    "tmp/%s/B03/probe_c09_enum.py 控制台输出" % RUN, "case-09")
add("write", "编写 line-height / strut 的隔离诊断探针（浅底白卡，14→21 格）",
    "tmp/%s/B03/probe_c09e.py" % RUN, "probes/probe-c09e-lineheight.png", "case-09",
    "第一次跑整张图几乎全白，定位到 14 个非定位 Container 被 Stack fit=EXPAND 拉满")
add("write", "编写 Stack fit 的对照探针（EXPAND/LOOSE/PASSTHROUGH）",
    "probe_c09e.py 内 dsl2", "probes/probe-c09f-stackfit.png", "case-09, case-10",
    "结论直接成为 case-10 页面底部六条边界的第一条")
add("write", "编写 Raw 空白的逐项隔离探针（8 格 + 左对齐基准线）",
    "tmp/%s/B03/probe_c09g.py" % RUN, "probes/probe-c09g-rawspace.png", "case-09")
add("bash(python)", "运行 probe_c09e/g 并打开三张探针图逐一核对",
    "probe_c09e.py; probe_c09g.py", "三张 PNG + 控制台", "case-09")
add("crop", "局部放大核对 ss02 斜杠零、Raw 缩进、softWrap、CDATA 对照",
    "tmp/%s/B03/crops/*.png" % RUN, "5 张裁切图", "case-09",
    "由 tmp/%s/_suite/crop.py 生成（LANCZOS 重采样，仅用于观察，不进入交付）" % RUN)
add("write", "编写 case-09 正式作品生成脚本（5 版迭代）",
    "tmp/%s/B03/build_c09.py" % RUN, "outputs/.../case-09/final.png + final.snapshot",
    "case-09")
add("bash(python)", "渲染 case-09 并逐版打开看图、打 warnings", "build_c09.py",
    "5 次渲染 + 2 次 400", "case-09",
    "400 修掉 3 处：9 位 hex、6 位 hex、>90° 的 borderRadius 拼接")
add("write", "编写 case-10 的能力探针，并在同一脚本里用 PIL 从返回 PNG 读回像素",
    "tmp/%s/B03/probe_c10.py" % RUN,
    "probes/probe-c10-flex.png + probe-c10-readback.txt", "case-10",
    "这是十件里唯一一份「渲染后从像素反查布局算术」的证据：8 组读回值全部与预测一致")
add("bash(python)", "运行 case-10 探针并读回像素", "probe_c10.py",
    "probe-c10-flex.png + 读回报告", "case-10")
add("write", "编写 case-10 正式作品生成脚本（5 版迭代），含 Cooper 赤纬与标准时角公式",
    "tmp/%s/B03/build_c10.py" % RUN,
    "outputs/.../case-10/final.png + final.snapshot", "case-10")
add("bash(python)", "渲染 case-10 并逐版打开看图", "build_c10.py",
    "11 次请求（1 次成功 + 10 次 400/500 修复）", "case-10",
    "修掉：漏 degrees()、月柱下界、FSB 缺 Flexible 包装、7 位 hex、8 位 hex、"
    "borderRadius 拼接格式、wlib.seg 返回 list 却用 append")
add("crop", "局部放大核对剖面比例、进深条长度、三张日轨缩略图",
    "tmp/%s/B03/crops/final-c10-*.png" % RUN, "3 张裁切图", "case-10")
add("bash(python)", "统计十件 PNG 真实画幅/字节数与 final.snapshot 的元素数",
    "tmp/%s/B03/_stats.py" % RUN, "控制台 10 行", "all",
    "画幅与 elements 全部从交付文件读回，不是手填")
add("write", "编写 portfolio.json / portfolio.md / gallery.html 生成器（字段全部读回真实产物）",
    "tmp/%s/B03/build_portfolio.py" % RUN, "输出根三个文件", "all")
add("bash(python)", "生成三份根目录文件", "build_portfolio.py",
    "portfolio.json / portfolio.md / gallery.html", "all")
add("write", "本文件（tool-usage.jsonl）与 log_b03.py（调 wrapup）",
    "tmp/%s/B03/tool-usage.jsonl; log_b03.py" % RUN, [], "all")
add("write", "编写 technique-notes.md（逐件手法 / 探针证据 / 已确认边界）",
    "outputs/%s/B03/technique-notes.md" % RUN, [], "all",
    "所有「已确认的边界」都能指到 probes/ 下的一张图或 responses/ 下的一次真实响应")
add("write", "编写 snapshot-usage.md（文档依据 / 请求与迭代计数 / 逐图自检 / 踩坑表）",
    "outputs/%s/B03/snapshot-usage.md" % RUN, [], "all")
add("wrapup", "记录迭代、生成 task-metrics.json、更新套件进度",
    "tmp/%s/B03/log_b03.py" % RUN, "outputs/.../task-metrics.json + suite-state.json",
    "all")

if __name__ == "__main__":
    p = os.path.join(HERE, "tool-usage.jsonl")
    with io.open(p, "w", encoding="utf-8", newline="\n") as fh:
        for e in E:
            fh.write(json.dumps(e, ensure_ascii=False) + "\n")
    print(p, len(E), "entries")