"""A17 log: record the visual iterations, write task-metrics.json and update the
suite state.  Must be executed; see WORK-ORDER.md step 6.
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
RUN = "20261004-182918"
TASK = "A17"
OUT = os.path.join(ROOT, "outputs", RUN, TASK)
TMP = os.path.join(ROOT, "tmp", RUN, TASK)
sys.path.insert(0, os.path.join(ROOT, "tmp", RUN, "_suite"))
import wrapup  # noqa: E402

STARTED = "2026-10-05T00:23:02.756+08:00"
FIRST_IMAGE = "2026-10-05T00:24:31.402+08:00"   # first successful render (calib probe)
ENDED = "2026-10-05T01:52:40.115+08:00"

# (version, parent, kind, dsl, image, viewed_at, observed, changes, complete)
ITERATIONS = [
    ("A17-v01", None, "baseline",
     "tmp/20261004-182918/A17/probe/calib.snapshot",
     "tmp/20261004-182918/A17/probe/calib.png",
     "2026-10-05T00:25:10.000+08:00",
     "第一个探针图：30 行文字墨迹条。用于测 advance 的单行扫描在中线取样，"
     "所以 '.' ',' '|' 这类低位字符量不到，宽度数据不完整。",
     "建立 calib 探针：深色底 + 浅色字，按行扫描墨迹包围盒。",
     True),
    ("A17-v02", "A17-v01", "visual",
     "tmp/20261004-182918/A17/probe/glyphs.snapshot",
     "tmp/20261004-182918/A17/probe/glyphs.png",
     "2026-10-05T00:31:20.000+08:00",
     "359 个汉字 advance 全部实测为 1.000 em；86 个拉丁字符得到 advance，"
     "但 9 个低位/标点字符缺失。",
     "改为整行扫描墨迹（probe_glyphs.py），并追加 20 次重复行反推 advance。",
     True),
    ("A17-v03", "A17-v02", "syntax-fix",
     "tmp/20261004-182918/A17/probe/adv-00.snapshot",
     "tmp/20261004-182918/A17/probe/adv-00.png",
     "2026-10-05T00:38:00.000+08:00",
     "mono advance 全部量成 0.038 em——明显错误：2400px 画布放不下 30×10 个 "
     "100px 字形，行被截断了。",
     "修正 probe_metrics2.py：改为 single 行 + 20 次重复行配对，重复数按实测 "
     "advance 反算，保证行宽不触边。",
     True),
    ("A17-v04", "A17-v03", "visual",
     "tmp/20261004-182918/A17/probe/mono-00.snapshot",
     "tmp/20261004-182918/A17/probe/mono-00.png",
     "2026-10-05T00:41:40.000+08:00",
     "DejaVu Sans Mono advance 30 个字符全部 0.60000 em，极差 0.00000。"
     "代码块的列宽因此可以是精确值。",
     "记录为版式常量 MONO_ADV=0.600，代码块列距 0.6022*size（留字距余量）。",
     True),
    ("A17-v05", "A17-v04", "syntax-fix",
     "tmp/20261004-182918/A17/probe/space.snapshot",
     "tmp/20261004-182918/A17/probe/space.png",
     "2026-10-05T00:45:05.000+08:00",
     "前一次空格对比用了 40 个字形 × 0.68em × 100px = 2720px > 2360px 文本框，"
     "文本换行导致差值算成负数（-0.056 em）。",
     "probe_space.py 把重复数降到 8 行，行宽 1088px，实测 Inter 空格 0.28 em、"
     "mono 空格 0.60 em。",
     True),
    ("A17-v06", None, "baseline",
     "outputs/20261004-182918/A17/example-01.snapshot",
     "outputs/20261004-182918/A17/example-01.png",
     "2026-10-05T01:02:00.000+08:00",
     "四个 400×240 示例首版全部 200。打开看：example-01/02/03/04 内容正确，"
     "但 example-01 的箭头用两个矩形拼出来，是个空心方框，不像箭头。",
     "箭头改成文本 '→'（Inter,Noto Sans CJK SC，26px）。",
     True),
    ("A17-v07", "A17-v06", "visual",
     "outputs/20261004-182918/A17/example-03.snapshot",
     "outputs/20261004-182918/A17/example-03.png",
     "2026-10-05T01:12:30.000+08:00",
     "example-03 行内富文本 '限制条件：Stack 与 Positioned' 三段贴在一起，"
     "'与' 紧贴 Stack，没有空格——因为普通 Text 会 trim 首尾空白。",
     "分隔处改用 <Raw><![CDATA[ 与 ]]></Raw>，正好同时演示 Raw 保留空白的用途。",
     True),
    ("A17-v08", "A17-v07", "visual",
     "outputs/20261004-182918/A17/example-04.snapshot",
     "outputs/20261004-182918/A17/example-04.png",
     "2026-10-05T01:20:15.000+08:00",
     "example-04 右块的 ImageFiltered 只包了文字，底板没进去，"
     "对比不像'整棵子树一起糊'。",
     "把 ImageFiltered 上提，包住底板 + Stack + 文字的整棵子树。",
     True),
    ("A17-v09", None, "baseline",
     "outputs/20261004-182918/A17/handbook-01.snapshot",
     "outputs/20261004-182918/A17/handbook-01.png",
     "2026-10-05T01:31:00.000+08:00",
     "手册首版结构成立，但打开看发现四个真问题："
     "(1) 正文把 Content-Type 拆成 'Content-T / ype'、'mess / age'，"
     "因为换行器逐字符断行；(2) 插图标题与面板标题重叠在同一基线；"
     "(3) 页脚左文字与右侧页码重叠；(4) standfirst 里的 '49 行' 与实际 63 行不符。",
     "hb.wrap 改成词感知贪心（拉丁/数字/'-' 粘在一起，CJK 任意断，加避头尾规则）；"
     "插图标题移到插图下方并加 check_fit；页脚右对齐两段各留 280/804px；"
     "改写 standfirst。",
     True),
    ("A17-v10", "A17-v09", "syntax-fix",
     "outputs/20261004-182918/A17/handbook-01.snapshot",
     "outputs/20261004-182918/A17/handbook-01.png",
     "2026-10-05T01:38:20.000+08:00",
     "打开裁切放大后发现省略行那一栏 '；完整文档见' 有一簇字叠在一起。"
     "查 DSL 源码定位：省略行的 note 被当成代码 token 化，再用 0.6022em 的"
     "mono 列距逐 token 定位——中文被按半角列宽硬塞，必然重叠。"
     "（单独渲染同一串文字是正常的，所以问题在调用路径不在服务。）",
     "code_block 的行协议从 2 元组改成 3 元组 (行号, 代码或 None, 省略说明)；"
     "text 为 None 时整行用 UI 字体渲染，不再 token 化。",
     True),
    ("A17-v11", "A17-v10", "visual",
     "outputs/20261004-182918/A17/handbook-02.snapshot",
     "outputs/20261004-182918/A17/handbook-02.png",
     "2026-10-05T01:44:00.000+08:00",
     "右栏四条红色条目连成一片，分不清是四条还是八条；插图 caption 折行后"
     "第二行掉到面板外面。",
     "notes_box 改成条目级排版：续行缩进对齐首行、只在首行画色块标记；"
     "caption 加 check_fit 并缩短措辞；CHAPTER 04 的 kicker 也超宽，改短。",
     True),
    ("A17-v12", "A17-v11", "visual",
     "outputs/20261004-182918/A17/handbook-02.snapshot",
     "outputs/20261004-182918/A17/handbook-02.png",
     "2026-10-05T01:49:30.000+08:00",
     "把插图裁出来与 example-02.png 逐像素比对，发现 Row 里的两个 Expanded "
     "被画成了 103px/35px 加一个 14px 间隔；实测 example-02.png 是 "
     "16–124 与 138–192，即 108px/54px。插图几何与示例不一致。",
     "按 example-02.png 的实测像素改 EX2_ART 的三个矩形："
     "[16,16,108,120]、[124,16,14,120]、[138,16,54,120]。",
     True),
    ("A17-v13", "A17-v12", "visual",
     "outputs/20261004-182918/A17/handbook-03.snapshot",
     "outputs/20261004-182918/A17/handbook-03.png",
     "2026-10-05T01:51:00.000+08:00",
     "与 example-03.png 比对发现插图给三行文字各加了一块 #0B1220FF 底板，"
     "而示例本身没有——插图成了'装饰过的重画'而不是同一构件。",
     "去掉三块底板，插图改用示例自身的颜色与盒子；行内富文本的三个 span "
     "各自定位到实测基线（156/236/272），并在 examples.py 里注明这一行"
     "由页侧重排、字形 x 与服务内联排版有几像素差异。",
     True),
]

ARTIFACTS = [
    "handbook-01.png", "handbook-01.snapshot",
    "handbook-02.png", "handbook-02.snapshot",
    "handbook-03.png", "handbook-03.snapshot",
    "handbook-04.png", "handbook-04.snapshot",
    "example-01.png", "example-01.snapshot",
    "example-02.png", "example-02.snapshot",
    "example-03.png", "example-03.snapshot",
    "example-04.png", "example-04.snapshot",
    "sources.md", "examples.json",
    "snapshot-usage.md", "task-metrics.json",
]

VISUAL_EVIDENCE = [
    {"artifact": "handbook-01.png", "viewed": True,
     "viewed_at": "2026-10-05T01:52:00+08:00",
     "checks": ["1200x1600 与 PNG 签名", "页眉/页码/色板统一",
                "正文 24px 不断词（Content-Type 完整）",
                "代码块 13 行 + 1 处省略标记，省略说明不再叠字",
                "插图与 example-01.png 同构图",
                "右栏错误码与真实响应一致"]},
    {"artifact": "handbook-02.png", "viewed": True,
     "viewed_at": "2026-10-05T01:52:10+08:00",
     "checks": ["1200x1600", "Row/Expanded 段代码可读",
                "右栏四条条目各自成段（续行缩进）",
                "插图 Row 几何已按 example-02.png 实测像素修正"]},
    {"artifact": "handbook-03.png", "viewed": True,
     "viewed_at": "2026-10-05T01:52:20+08:00",
     "checks": ["1200x1600", "CDATA/Raw 两段代码印刷正确",
                "两个色块与 example-03.png 同一坐标与同一颜色",
                "右栏解释了 #80FF0000 为什么透明"]},
    {"artifact": "handbook-04.png", "viewed": True,
     "viewed_at": "2026-10-05T01:52:30+08:00",
     "checks": ["1200x1600", "BackdropFilter/ImageFiltered 两段代码印刷正确",
                "插图左侧背景糊而文字清晰、右侧文字一起糊（真滤镜）",
                "kicker 不再折行压线"]},
    {"artifact": "example-01.png", "viewed": True,
     "viewed_at": "2026-10-05T01:02:30+08:00",
     "checks": ["400x240", "请求/响应/错误三块都在", "箭头改为 '→' 后正确"]},
    {"artifact": "example-02.png", "viewed": True,
     "viewed_at": "2026-10-05T01:03:00+08:00",
     "checks": ["400x240", "Row 2:1 与 Stack 定位都在", "像素扫描确认 108/54 分配"]},
    {"artifact": "example-03.png", "viewed": True,
     "viewed_at": "2026-10-05T01:12:40+08:00",
     "checks": ["400x240", "CDATA 尖括号正常显示", "Raw 保留首尾空格",
                "行内富文本三色正确", "#80FF0000 完全透明只剩描边"]},
    {"artifact": "example-04.png", "viewed": True,
     "viewed_at": "2026-10-05T01:20:25+08:00",
     "checks": ["400x240", "左块背景模糊/文字清晰", "右块文字连同底板一起模糊"]},
]

UNRESOLVED = [
    "服务画布高度上限 4096px：字符探针因此必须分批渲染，已按此实现；"
    "手册本身 1600px 不受影响。",
    "413 REQUEST_TOO_LARGE 与 429/503 未在本题触发实测（会浪费配额或需要构造"
    "超限请求体），手册只把它们作为 openapi.yaml 的枚举事实陈述，"
    "sources.md 已注明这一点。",
    "行内富文本那一行在页面插图里是三个独立 Text 逐段定位，字形 x 与服务自己的"
    "内联排版有几像素差异；其余所有元素都与示例逐像素对齐"
    "（probe/art-compare.json 记录了比对数据）。",
]

m = wrapup.wrapup(
    TASK, STARTED, FIRST_IMAGE, ENDED, ITERATIONS, ARTIFACTS,
    VISUAL_EVIDENCE, UNRESOLVED,
    notes="四页手册 + 4 个可运行示例，全部为服务真实响应；印刷代码由 hb.excerpt() "
          "从已渲染的 example-0N.snapshot 逐行切出并 assert；插图全部由页面 DSL "
          "重绘，无 <Image> 嵌入；排版列距基于实测 mono advance 0.600 em。",
    rounds=["round-01"],
    cases=["handbook-01", "handbook-02", "handbook-03", "handbook-04",
           "example-01", "example-02", "example-03", "example-04"])

print("task-metrics.json written")
print("render requests:", m["counts"]["render_requests"],
      "ok:", m["counts"]["successful_render_requests"],
      "failed:", m["counts"]["failed_render_requests"],
      "docs:", m["counts"]["document_requests"])
print("views:", m["counts"]["image_views"],
      "visual iterations:", m["counts"]["completed_visual_iterations"])
print("final pngs:", m["counts"]["final_pngs"])
print("wall clock s:", m["wall_clock_seconds_total"])
print("usage:", m["usage"]["input_tokens"], m["usage"]["cost"])