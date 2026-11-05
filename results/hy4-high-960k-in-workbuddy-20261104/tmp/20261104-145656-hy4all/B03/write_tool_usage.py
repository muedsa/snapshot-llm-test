#!/usr/bin/env python3
"""Write B03 tool-usage.jsonl for the non-HTTP tools actually used.

HTTP render events live in requests.jsonl; this file records other tools and
does NOT count them as additional snapshot requests.
"""
import os
import sys

sys.path.insert(0, os.environ["TOOLS"])
import suite

T = "B03"
rows = [
    ("probe.py + render.py (能力诊断)",
     "在正式作品前验证 RADIAL/SWEEP 渐变、gradientStops/gradientRotation、Transform 旋转矩阵、ImageFiltered 模糊、ClipPath EVEN_ODD 镂空、ClipOval/ClipRRect、富文本 WidgetSpan、8 位颜色与 Opacity 共 10 项能力是否在本服务成立",
     "生成 tmp/<run>/B03/probe.snapshot 并渲染 probe.png；1 次真实服务请求记在 tmp/<run>/B03/probe/requests.jsonl",
     "tmp/20261104-145656-hy4all/B03/probe.py"),
    ("ViewImage (能力诊断图)",
     "打开 probe.png 逐区确认 10 项能力的实际视觉效果与底部说明文字完整性",
     "10 项能力全部真实成立；ImageFiltered 可见生效、BackdropFilter 未使用；文字无裁切",
     "tmp/20261104-145656-hy4all/B03/probe.png"),
    ("build.py (参数化生成)",
     "用 Canvas/渐变/ClipPath/Transform/Opacity/富文本等构造 10 件独立完整 DSL，并生成 portfolio/gallery/technique-notes/case.md/plan.json",
     "10 份 final.snapshot 写入 outputs/<run>/B03/case-XX/，同版备份到 tmp/<run>/B03/v1..v4/",
     "tmp/20261104-145656-hy4all/B03/build.py"),
    ("smooth_closed() 几何计算",
     "Catmull-Rom 转三次贝塞尔生成平滑闭合等高线/年轮/线网路径（case-04/09/10）",
     "12 圈等高线、13 圈年轮、60 圈空心细环均由脚本计算，非手工路径",
     "tmp/20261104-145656-hy4all/B03/build.py"),
    ("render_all.py / render.py / render_rest.py",
     "批量与逐张渲染全部 10 件作品；逐张渲染用于规避服务偶发读超时",
     "全部最终 PNG 为 image/png 真实响应，请求明细见各 case-XX/requests.jsonl；本条不重复计请求数",
     "tmp/20261104-145656-hy4all/_suite/tools/"),
    ("ViewImage (逐图看图)",
     "逐张打开全部 10 张最终 PNG，检查内容、层级、对齐、可读性、遮挡裁切与视觉效果；v1/v3/v4 共多轮",
     "发现并修复 case-01 底部对比不足、case-02 标签偏淡、case-04 海拔标注堆叠、case-05 长标注射位、case-06 月相标签重叠、case-09 第 8 款酒裁切、case-10 方程溢出与线网实心化",
     "outputs/20261104-145656-hy4all/B03/case-XX/final.png"),
    ("Python PNG 头/尺寸/配对检查",
     "读取 10 张 PNG 的 IHDR 校验 89 50 4E 47 与尺寸，核对同名 .snapshot 与 case.md 齐全",
     "10/10 PNG 头有效、尺寸与 DSL 声明一致、根标签为 Snapshot、case.md 齐全",
     "outputs/20261104-145656-hy4all/B03/"),
    ("WebFetch / 文档缓存（B03 未新增）",
     "B03 复用 _suite/docs 已缓存的 ai-guide/parser-tags/parser-text/parser/examples/fonts/openapi 文档；本任务未新增外部 HTTP 文档请求",
     "实际阅读并按文档使用标签；B04 的 WebFetch 研究单独记在 B04 日志，不混入本题",
     "tmp/20261104-145656-hy4all/_suite/docs/"),
]
for tool, purpose, result, source in rows:
    suite.tool_usage(T, tool, purpose, result, source)
print("wrote", len(rows), "tool-usage rows for", T)
