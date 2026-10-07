# -*- coding: utf-8 -*-
"""Record B01's real tool usage into tmp/.../B01/tool-usage.jsonl.

Only tools that were actually used are logged, with the paths they touched.
HTTP renders live in requests.jsonl and are referenced here by request id
rather than counted a second time.
"""
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
TMP = HERE
OUT = os.path.join(ROOT, "outputs", "20261004-182918", "B01")
PATH = os.path.join(TMP, "tool-usage.jsonl")

RECS = [
    # ---------------------------------------------------------- shared prep
    ("read", "读取套件实测 DSL 手册，取得本库已验证的标签/属性/坑位结论，"
             "避免重复踩已修过的语法错误",
     "tmp/20261004-182918/_suite/DSL-HANDBOOK.md", [], "all",
     "手册第 3 节列出 8 位 hex 按 CSS #RRGGBBAA 读、第 4 节 Positioned 只能作 Stack 子节点、"
     "第 6 节列出共享工具，全部按此执行"),
    ("read", "读取单题执行清单，确认输出/临时目录、留痕与 wrapup 调用的硬要求",
     "tmp/20261004-182918/_suite/WORK-ORDER.md", [], "all", None),
    ("read", "读取 B01 的 task.json 与 TASK.md，确认 B 类交付结构"
             "（每 case 一个目录 + 根目录五个文件）与 minimum_independent_cases=10",
     "tasks/B01-ten-real-world-showcases/task.json; TASK.md; AGENTS.md", [], "all",
     "fixed_canvas_dimensions 为 null，画布尺寸由每件自行决定"),
    ("read", "读取 run-config.json 确认 service_base_url 与 asset_policy",
     "run-config.json", [], "all",
     "资产政策为 dsl_primary_with_supporting_assets，但十件均无需要照片之处，"
     "因此未引入任何外部素材、未使用 <Image>"),
    ("read", "读取上一段执行留下的 atelier.py/run.py/build_c0*.py，复用令牌与构件",
     "tmp/20261004-182918/B01/*.py", [], "case-01..case-09", None),

    # ---------------------------------------------------------- per case work
    ("python (stdlib)", "列出 B01 输出目录，摸清中断时已交付 8 个 case",
     "outputs/20261004-182918/B01/", "控制台输出", "all",
     "case-01..case-08 存在且各有 final.png + final.snapshot，case-04 另有 case.md"),
    ("python (PIL)", "逐张打开已交付的 8 张 final.png 做整体审查，"
     "不依赖像素统计代替视觉判断",
     "outputs/20261004-182918/B01/case-0{1..8}/final.png",
     "8 次图像查看结论（见 snapshot-usage.md 审查表）", "case-01..case-08",
     "发现 case-04 时间轴与阶段名整体右移、case-06「剩余时长」不在环心、"
     "case-08 印章文字被红框切掉且「2026」偏右"),
    ("python (PIL crop)", "放大核对上述可疑区域，区分真实缺陷与抗锯齿噪声",
     "tmp/20261004-182918/B01/crops/chk0*.png",
     ["chk04-axis", "chk04-ph", "chk06-ring", "chk06-pill", "chk08-ring", "chk08-seal2"],
     "case-04; case-06; case-08",
     "确认是真实几何偏移，不是渲染噪声"),
    ("python (grep 审计)", "写 audit_center.py 静态扫描全部 build_c*.py，"
     "找出所有把 align=\"CENTER\" 与 w= 混用的调用点",
     "tmp/20261004-182918/B01/build_c*.py",
     "tmp/20261004-182918/B01/audit_center.py", "case-03; case-04; case-06; case-08",
     "命中 10 处，根因是 textAlign 在框内居中而 one_line 把框左边缘放在 x，"
     "字形因此右移 w/2；改用 A.ctr 后全部归位"),
    ("python (PIL crop)", "复核 case-03 警戒条与 case-06 队列状态胶囊的居中结果",
     "tmp/20261004-182918/B01/crops/fin03-pill.png; fin06-pill.png; fin06-ring.png",
     [], "case-03; case-06",
     "首次复核发现 case-06 的「剩余时长」x 参照值取错(NX+660 而非环心 CX)，"
     "第二次修正后归位"),
    ("python (PIL crop)", "复核 case-09 页眉、编目表列距与探坑平面脚注",
     "tmp/20261004-182918/B01/crops/chk09-hdr.png; chk09-hdr2.png; chk09-cat.png; "
     "chk09-cat2.png; chk09-plan.png; fin09-foot.png",
     [], "case-09",
     "定位三个独立缺陷：等宽字宽按字符数估算导致混排中文串尾巴被丢弃、"
     "深度列与网格列间距不足、「探照灯」标签被右侧编目面板覆盖"),
    ("python (字体度量)", "修正 atelier.tw 的 mono 分支为逐字符度量，"
     "并让 one_line 在字体为等宽栈时自动启用",
     "tmp/20261004-182918/B01/atelier.py", [], "case-09（影响全部件的 mono 文本框宽）",
     "DejaVu Sans Mono 的 ASCII 前进宽恒为 0.6021em，但中文回退字形仍是 1em；"
     "混排串按字符数估算会低估约 6%，服务随即静默丢弃溢出部分"),
    ("python (自检)", "10 件全部构建脚本跑通后由 run.emit 打印元素数与全部 "
     "dsllib.warnings()，逐条处理",
     "tmp/20261004-182918/B01/build_c*.py", "控制台输出", "all",
     "最终十件的 warnings 均为 0；元素数区间 348–3377，全部在 4096 上限内"),
    ("python (PIL)", "为新写的 case-10 生成预览后打开查看，发现并修正四处问题",
     "tmp/20261004-182918/B01/preview/case-10.png; crops/chk10-hdr.png; "
     "chk10-hdr2.png; chk10-wall.png",
     [], "case-10",
     "①「在场」标签出现乱码字符 ②难度色带与路线/墙面用的是等级数字而非色带索引，"
     "整体错位一档 ③空闲/占用计数写死为 6/3，实际布尔标记给出 5/4 改为从数据算出 "
     "④教练的话右侧「38 人」压穿段落第二行"),
]

with io.open(PATH, "w", encoding="utf-8", newline="\n") as fh:
    for name, purpose, inputs, outputs, affects, detail in RECS:
        fh.write(json.dumps({
            "task_id": "B01",
            "run_id": "20261004-182918",
            "tool": name,
            "purpose": purpose,
            "inputs": inputs,
            "outputs": outputs,
            "affects_cases": affects,
            "detail": detail,
            "note": "HTTP renders are recorded in requests.jsonl and are NOT counted again here",
        }, ensure_ascii=False) + "\n")
print("wrote", PATH, "records:", len(RECS))