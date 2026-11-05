#!/usr/bin/env python3
"""Write B04 tool-usage.jsonl for the non-render tools actually used."""
import os
import sys

sys.path.insert(0, os.environ["TOOLS"])
import suite

T = "B04"
rows = [
    ("WebFetch (S1)",
     "实际读取 NASA NSSDCA《Planetary Fact Sheet - Metric》完整表格，取得 8 颗行星 × 20 参数的原始数值、列顺序、作者与更新日期",
     "取得表头/10 列数值/页脚 Last Updated: 18 March 2025, DRW；摘录到 tmp/<run>/B04/research/nasa-facts.json",
     "https://nssdc.gsfc.nasa.gov/planetary/factsheet/"),
    ("WebFetch (S2)",
     "实际读取《Planetary Fact Sheet Notes》，取得每个字段的精确定义（半长轴、逆行、1 bar 层面、IAU 卫星数、平均温度口径）",
     "取得字段定义正文与 Last Updated: 20 December 2021, DRW；用于图中口径脚注与 sources.json 的 locators",
     "https://nssdc.gsfc.nasa.gov/planetary/factsheet/planetfact_notes.html"),
    ("WebFetch (S3)",
     "实际读取 NASA《About the Planets》，取得八颗行星清单、Inner/Outer 分组与 gas/ice giants 分类原文",
     "取得可逐字引用的分类句；页面无确认更新日期，如实记为 null",
     "https://science.nasa.gov/solar-system/planets/"),
    ("数据整理 / research 存档",
     "把 WebFetch 结果按「参数行 × 行星列」转成结构化 JSON，明确排除 Moon 与 Pluto 列，并记录 S2 与 S3 的 terrestrial 定义差异",
     "tmp/<run>/B04/research/nasa-facts.json（8 行星 × 20 字段 + 3 来源元数据 + 字段定义 + 口径冲突记录）",
     "tmp/20261104-145656-hy4all/B04/research/nasa-facts.json"),
    ("Python 数值计算与校验",
     "从研究存档复算直径比例、AU、地球年、对数刻度映射、卫星合计与温度色带定位，校验图中数值未被改动",
     "tmp/<run>/B04/data-check.json 记录逐项断言结果；build.py 所有数值均由该 JSON 计算",
     "tmp/20261104-145656-hy4all/B04/verify_data.py"),
    ("build.py (参数化生成)",
     "用 Canvas/渐变/ClipPath/程序化刻度/富文本构造 10 件连贯视觉特辑，并生成 portfolio/gallery/sources/editorial-note/case.md/plan.json",
     "10 份 final.snapshot 写入 outputs/<run>/B04/case-XX/，同版备份到 tmp/<run>/B04/v1/",
     "tmp/20261104-145656-hy4all/B04/build.py"),
    ("B03 已验证 DSL 能力复用",
     "复用 B03 probe.png 已在本服务验证成立的能力（RADIAL 渐变、ImageFiltered、8 位色、富文本 Raw/WidgetSpan、渐变条等），不重复做能力试验请求",
     "未新增本题的能力诊断 HTTP 请求；probe.png 证据见 tmp/<run>/B03/",
     "tmp/20261104-145656-hy4all/B03/probe.png"),
    ("render_all.py / render.py",
     "批量渲染 10 件作品；请求明细见各 case-XX/requests.jsonl，本条不重复计入渲染请求数",
     "全部最终 PNG 为 image/png 真实响应",
     "tmp/20261104-145656-hy4all/_suite/tools/render_all.py"),
    ("ViewImage (逐图看图)",
     "逐张打开全部 10 张最终 PNG，检查数值、单位、口径、层级、对齐、可读性、遮挡裁切与视觉表达",
     "逐图结论记在各 case.md、portfolio.json 与 snapshot-usage.md；发现缺陷则改 build.py 重渲染复查",
     "outputs/20261104-145656-hy4all/B04/case-XX/final.png"),
    ("Python PNG 头/尺寸/配对检查",
     "读取 10 张 PNG 的 IHDR 校验 89 50 4E 47 与尺寸，核对同名 .snapshot、case.md 与 gallery 链接",
     "10/10 PNG 头有效、尺寸与 DSL 声明一致（含 1600×1200 总表）、交付文件齐全",
     "outputs/20261104-145656-hy4all/B04/"),
]
for tool, purpose, result, source in rows:
    suite.tool_usage(T, tool, purpose, result, source)
print("wrote", len(rows), "tool-usage rows for", T)
