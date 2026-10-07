#!/usr/bin/env python
"""写入 B05 的 tool-usage.jsonl：记录本次实际用到的辅助工具与研究动作。

只记录真实发生的事：文档抓取、字体查询、局部放大、图像观察、颜色/尺寸校验脚本。
HTTP 事件引用 requests.jsonl 里的 request_id，不重复计为请求消耗。
"""
import io
import json
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
TMP = os.path.join(ROOT, "tmp", "20261004-182918", "B05")

sys.path.insert(0, TMP)
import bk  # noqa: E402

bk.log_tool(
    "web/document fetch",
    "读取服务使用指南，确认请求体格式、UA 要求与尺寸约束",
    ["https://open-snapshot.muedsa.com/ai-guide.md"],
    ["tmp/20261004-182918/B05/docs/ai-guide.md"],
    affects="全部 10 件",
    note="引用 requests.jsonl 的 B05-req-001，不重复计为请求")
bk.log_tool(
    "HTTP GET /fonts",
    "取得服务真实字体列表，避免臆造字体名",
    ["https://open-snapshot.muedsa.com/fonts"],
    ["tmp/20261004-182918/B05/fonts-list.txt"],
    affects="全部 10 件",
    note="实测到的字体被 fpk.py 的 DISPLAY/SEMI/MED/UI/MONO/SERIF 直接引用；"
         "引用 requests.jsonl 的 B05-req-002")
bk.log_tool(
    "web/document fetch",
    "查 DSL 官方文档首页与 parser-tags 参考，确认标签与属性白名单",
    ["https://snapshot.muedsa.com/",
     "https://snapshot.muedsa.com/reference/parser-tags/",
     "https://snapshot.muedsa.com/guides/painting/"],
    ["tmp/20261004-182918/B05/docs/snapshot-docs.txt",
     "tmp/20261004-182918/B05/docs/parser-tags.txt",
     "tmp/20261004-182918/B05/docs/painting.txt"],
    affects="全部 10 件",
    note="引用 requests.jsonl 的 B05-req-003 / 004 / 005，不重复计为请求")
bk.log_tool(
    "shared DSL handbook",
    "复用上一题的实测结论（Color/Opacity/Transform/ClipRRect/元素上限），不重复踩坑",
    ["tmp/20261004-182918/_suite/DSL-HANDBOOK.md"],
    ["（只读引用，未修改）"],
    affects="全部 10 件",
    note="其中「未知属性被静默忽略」一条直接决定了本任务用 Opacity 标签而非 "
         "Container.opacity 做半透明蒙版")
bk.log_tool(
    "image observation (read tool)",
    "逐张打开成品 PNG 做视觉判断，并在需要时放大局部",
    ["outputs/20261004-182918/B05/case-01..10/final.png"],
    ["（无新文件）"],
    affects="全部 10 件",
    note="本次会话打开图片 40 次以上；整图判断 + 11 处 crop 放大")
bk.log_tool(
    "crop.py (shared)",
    "放大核对 11 处细节：c01 底部、c02 事实行、c03 缩略图标题、c04 平面与图例、"
    "c05 页脚二维码、c06 进度环与按钮、c07 事件行与卡片、c08 时间轴与页脚、"
    "c09 页脚、c10 曲线与右侧面板",
    ["tmp/20261004-182918/_suite/crop.py"],
    ["tmp/20261004-182918/B05/crops/*.png（19 张放大图，全部保留）"],
    affects="case-01..10",
    note="所有放大图按 case 与用途命名，未覆盖")
bk.log_tool(
    "parametric layout scripts",
    "用脚本计算几何而不是手填坐标，保证 DSL 里的坐标等于算出的坐标",
    ["tmp/20261004-182918/B05/fpk.py", "bk.py",
     "build_c01..c06.py", "build_c07..c10.py"],
    ["outputs/20261004-182918/B05/case-01..10/final.snapshot"],
    affects="全部 10 件",
    note="元件库 fpk.py 集中管理调色板、类型尺度、标记牌、危险条纹、"
         "折线/面积/圆弧等构件，10 个脚本共用")
bk.log_tool(
    "inspect_dsl.py (custom)",
    "校验每个 final.snapshot 的画布尺寸、元素数、文本数，并确认它与临时草稿"
    "目录里编号最大的那一版逐字节一致",
    ["outputs/20261004-182918/B05/case-*/final.snapshot",
     "tmp/20261004-182918/B05/drafts/*.snapshot"],
    ["（无新文件，控制台输出）"],
    affects="全部 10 件",
    note="实测 10/10 的 final.snapshot 都与草稿目录中编号最大的版本一致")
bk.log_tool(
    "check_colors.py (custom)",
    "扫描 DSL 里所有 color 值的长度，定位 case-04 的 7 位色值 #F8F5EFF "
    "（该值触发服务 400 PARSE_ERROR）",
    ["tmp/20261004-182918/B05/drafts/case-04-v03.snapshot"],
    ["（无新文件，控制台输出）"],
    affects="case-04",
    note="先用 build_colors 全表扫描定位到唯一一处，再用编辑工具改为 #F8F5EFFF")
bk.log_tool(
    "PIL image inspection",
    "读回每张 PNG 的真实像素尺寸，与 DSL 里声明的画布尺寸逐件比对，"
    "确认没有出现「声明 1600×1000 实际出图 400×200」这类静默失败",
    ["outputs/20261004-182918/B05/case-*/final.png"],
    ["（无新文件，结果写入 task-metrics.json 的 per_case）"],
    affects="全部 10 件",
    note="实测 10/10 的实际像素与 DSL 声明完全一致；这也复核了共享手册里"
         "「画布尺寸由布局决定，不由 Snapshot 决定」这一条")
bk.log_tool(
    "trace log repair scripts",
    "修复两处留痕缺陷：①上一个执行阶段未调用 snapkit.configure()，"
    "29 条渲染记录被写到仓库根 requests.jsonl；②log_b05.py 重复执行导致 "
    "iterations.jsonl 出现重复行",
    ["requests.jsonl（仓库根）",
     "tmp/20261004-182918/B05/requests.jsonl",
     "tmp/20261004-182918/B05/iterations.jsonl"],
    ["tmp/20261004-182918/B05/requests-root-backup.jsonl"],
    affects="（不影响画面，只影响留痕完整性）",
    note="原始文件完整保留；归并只改 request_id 与 task_id，不改任何时间、"
         "状态、耗时、文件路径或错误信息；log_b05.py 现已幂等")
bk.log_tool(
    "local HTML gallery",
    "写本地相对链接的 gallery.html，索引全部 10 件并可点开原图与同名 DSL",
    ["outputs/20261004-182918/B05/case-*/final.png",
     "outputs/20261004-182918/B05/case-*/final.snapshot"],
    ["outputs/20261004-182918/B05/gallery.html"],
    affects="全部 10 件",
    note="数据内联在 <script> 中、样式全部内联，不引用任何 CDN 或远程脚本")

with io.open(os.path.join(TMP, "tool-usage.jsonl"), encoding="utf-8") as fh:
    n = sum(1 for _ in fh)
print("tool-usage.jsonl rows:", n)