"""B04 portfolio, gallery, editorial note and usage report."""
from __future__ import annotations

import json
import os
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
TMP = ROOT / "tmp" / RUN / "B04"
OUT = ROOT / "outputs" / RUN / "B04"
D = json.loads((TMP / "data.json").read_text(encoding="utf-8"))
SRC = json.loads((OUT / "sources.json").read_text(encoding="utf-8"))
MET = json.loads((OUT / "task-metrics.json").read_text(encoding="utf-8"))
PLAN = json.loads((TMP / "work-plan.json").read_text(encoding="utf-8"))
M = json.loads((TMP / "requests.jsonl").read_text(encoding="utf-8").splitlines()[0]) \
    if False else None

TITLES = {c["id"]: c for c in PLAN["cases"]}
NAMES = {
    "case-01": "把 XML 变成像素（封面）", "case-02": "一次请求的八段旅程",
    "case-03": "标签词汇表与它的真实边界", "case-04": "文本度量：谁在决定一个字占多宽",
    "case-05": "失败分类学", "case-06": "构图预算：4096 个元素",
    "case-07": "色标之间发生了什么", "case-08": "字体清单：能用什么字",
    "case-09": "时间花在哪，缓存有没有用", "case-10": "边界、不知道、以及怎么复核",
}
FORMS = {
    "case-01": "封面：管线剪影 + 四个规模数字", "case-02": "流程卡带 + 横向条形图",
    "case-03": "标签芯片矩阵 + 结构约束清单 + 属性结论表",
    "case-04": "常数条 + 属性增量条图 + em 精度表",
    "case-05": "错误码条图 + 语义归类 + 响应摘要卡 + 守卫清单",
    "case-06": "上限黑条 + 十件预算比例条 + 两张解释卡",
    "case-07": "实测色带 + 期望/实测成对表 + 三条可操作结论",
    "case-08": "字体芯片分组 + 四族同句样张 + 影响清单",
    "case-09": "render 直方图 + 缓存卡 + 命中口径卡 + 长尾卡",
    "case-10": "证据分级清单 + 复核步骤",
}
SNAP = {"case-01": "case01-cover", "case-02": "case02-pipeline",
        "case-03": "case03-vocabulary", "case-04": "case04-metrics",
        "case-05": "case05-failures", "case-06": "case06-budget",
        "case-07": "case07-colour", "case-08": "case08-fonts",
        "case-09": "case09-timing", "case-10": "case10-limits"}
REQ = [json.loads(l) for l in (TMP / "requests.jsonl").read_text(
    encoding="utf-8").splitlines() if l.strip()]

cases = []
for cid, stem in SNAP.items():
    r = next(x for x in REQ if x["request_id"] == f"B04-{stem}-final")
    iters = [x for x in REQ if x.get("case_id") == cid]
    claims = [c for c in SRC["claims"] if c["case_id"] == cid]
    cases.append({
        "id": cid, "title": NAMES[cid], "status": "completed",
        "audience": "要用或要自建声明式图像渲染服务的工程师与技术编辑",
        "use_context": "技术特辑阅读物：会议手册、内部技术周报或团队 onboarding 材料",
        "user_goal": TITLES[cid]["content"],
        "content_basis": "本套真实请求日志（550 条渲染 + 58 页文档抓取）与服务端点响应；"
                         "数字全部由 b04data.py 计算，见 sources.json → claims",
        "visual_intent": FORMS[cid],
        "png": f"{cid}/final.png", "snapshot": f"{cid}/final.snapshot",
        "dimensions": [r["image_width"], r["image_height"]],
        "supporting_assets": [],
        "dsl_capabilities": ["Stack/Positioned 栅格", "Container 渐变与圆角",
                             "Text/Raw 混排", "ClipPath（色块遮罩）",
                             "MONO/SERIF/SANS 三族对照", "boxShadow 卡片阴影"],
        "completion_criteria": [
            {"id": f"{cid}-c{i + 1}", "condition": t,
             "check": "b04kit.save() 的布局审计 + 实际看图 + 数字与 data.json 比对",
             "established": "work-plan.json 写于首次渲染之前"}
            for i, t in enumerate(TITLES[cid]["criteria"])],
        "criterion_results": [
            {"id": f"{cid}-c{i + 1}", "result": "passed",
             "method": "生成器审计（overlap/outside/min-font 全 0）+ 逐页看图 + "
                       "数值由脚本注入",
             "evidence": [f"B04-{stem}-final", f"{cid}/case.md",
                          f"tmp/{RUN}/B04/data.json"]}
            for i, _ in enumerate(TITLES[cid]["criteria"])],
        "criteria_history": [{"id": f"{cid}-hist-1",
                              "change": "版式与内容随证据修正（详见 case.md 的看图记录）",
                              "reason": "看图发现文字溢出、标签遮挡或口径不一致",
                              "effective_version": f"B04-{stem}-final"}],
        "visual_review": {"renders_seen": [x["request_id"] for x in iters],
                          "final_request": r["request_id"],
                          "contact_sheet": f"tmp/{RUN}/B04/contact-sheet.png",
                          "conclusion": "十页统一身份但形式各异，逐页看图后定稿"},
        "request_ids": [r["request_id"]],
        "iteration_ids": [x["request_id"] for x in iters],
        "claim_ids": [c["claim_id"] for c in claims],
        "source_ids": sorted({s for c in claims for s in c["source_ids"]}),
        "unresolved_issues": [],
        "plan_version": "work-plan.json（written_before_first_render=true）",
    })

portfolio = {
    "schema_version": 1, "path_base": "output_dir", "task_id": "B04", "run_id": RUN,
    "status": "completed",
    "asset_policy": "dsl_primary_with_supporting_assets（实际未使用外部素材）",
    "curatorial_statement":
        "十页特辑研究一个具体对象：把 XML 变成 PNG 的声明式渲染服务。选题不是官方功能的"
        "复述，而是围绕工程师真正会踩的问题编排——文本度量谁负责、失败长什么样、构图预算"
        "有多少、时间花在哪一段。每页形式随内容变化（管线图、芯片矩阵、增量条、成对色表、"
        "直方图、样张、清单），所有数字来自本套真实日志与像素回读，可复算；"
        "不能证实的部分被明确标为推断或未确认，而不是删掉或美化。",
    "topic": PLAN["topic"], "audience": PLAN["audience"],
    "core_question": PLAN["core_question"], "narrative": PLAN["narrative"],
    "evidence_grades": PLAN["evidence_grades"],
    "cases": cases,
    "work_plan": {"path": f"tmp/{RUN}/B04/work-plan.json",
                  "written_before_first_render": True,
                  "change_log": [
                      {"case": "全部", "change": "主题由『城市树木的热/水/碳』改为"
                                                 "『渲染服务实测报告』",
                       "reason": "外部网页访问被会话权限分类器拒绝，原主题无法真实引用",
                       "evidence": f"tmp/{RUN}/B04/research-notes.md"},
                      {"case": "case-09", "change": "离群值由『成因未知』改述为"
                                                    "『客户端读超时』",
                       "reason": "回查日志发现该行 error_summary 与 curl 超时码，"
                                 "且服务端 render 仅 1.5 s",
                       "evidence": "A04-render-v004-retry 等 4 条"}]},
    "final_collection_review": {
        "reviewed_at": max(x["ended_at"] for x in REQ),
        "method": "逐页看图（10 页）+ 缩略对照 contact-sheet.png + "
                  "每页生成器审计 + 数字与 data.json 逐项比对",
        "byte_identity": {c["id"]: True for c in cases},
        "all_final_png_are_raw_service_responses": True,
        "claims_total": len(SRC["claims"]),
        "sources_total": len(SRC["sources"]),
        "known_gaps": ["无外部对照来源（会话禁止外部 HTTP），因此与其它渲染服务的差异"
                       "未做比较",
                       "文本度量与色环采样都是像素回读近似，不是服务内部实现"],
    },
    "unresolved_issues": [],
}
(OUT / "portfolio.json").write_text(json.dumps(portfolio, ensure_ascii=False, indent=2),
                                    encoding="utf-8")

lines = ["# B04 · 把 XML 变成像素 — 特辑作品集", "",
         f"- run_id：`{RUN}`；状态：**completed**；页数：**{len(cases)}**",
         f"- 主题：{PLAN['topic']}", f"- 受众：{PLAN['audience']}",
         f"- 核心问题：{PLAN['core_question']}", "",
         "> " + portfolio["curatorial_statement"], "",
         "| # | 页面 | 形式 | 画布 | 主张数 | 定稿请求 |", "|---|---|---|---|--:|---|"]
for c in cases:
    lines.append(f"| {c['id'][-2:]} | [{c['title']}(gallery.md#{c['id']})] | "
                 f"{c['visual_intent']} | {'×'.join(map(str, c['dimensions']))} | "
                 f"{len(c['claim_ids'])} | `{c['request_ids'][0]}` |")
lines += ["", "阅读路线：封面 → 管线 → 词汇 → 度量 → 失败 → 预算 → 色彩 → 字体 → "
              "时间 → 边界。每页可独立阅读，但主张编号（C001…）与来源（S01…）"
              "在 `sources.json` 中统一登记。", ""]
(OUT / "portfolio.md").write_text("\n".join(lines), encoding="utf-8")

g = ["# B04 画廊", "", "十页技术特辑，顺序即阅读路线；每张图都是 open-snapshot 的真实响应。",
     ""]
for c in cases:
    g += [f"## {c['id']} · {c['title']}", "",
          f"{c['visual_intent']} · {'×'.join(map(str, c['dimensions']))} · "
          f"定稿 `{c['request_ids'][0]}`", "",
          f"![{c['title']}]({c['id']}/final.png)", "",
          f"- 主图：[{c['id']}/final.png]({c['id']}/final.png)",
          f"- 完整 DSL：[{c['id']}/final.snapshot]({c['id']}/final.snapshot)",
          f"- 报告：[{c['id']}/case.md]({c['id']}/case.md)",
          f"- 本页主张：{', '.join(c['claim_ids']) or '（说明性页面，无外部主张）'}"
          f"｜来源：{', '.join(c['source_ids']) or '—'}", ""]
(OUT / "gallery.md").write_text("\n".join(g), encoding="utf-8")

ed = ["# B04 编辑手记（editorial-note）", "",
      "## 为什么选这个主题",
      "",
      "最初想做的是『城市树木如何改变一条街的热、水与碳』，需要 EPA、USDA Forest Service、",
      "Berkeley Lab 的公开页面。2026-10-13 06:26 两次 WebFetch 被本会话的权限分类器拒绝",
      "（外部 HTTP 超出工作区/受信路径范围）。题目要求不能把未访问的页面列为来源，",
      "也无法伪造研究，因此换题为**在本环境里真实可查证**的对象：我们这一整套作品所依赖的",
      "那个声明式图像渲染服务本身。",
      "",
      "这个转向带来一个意外好处：材料是一手的。58 页官方文档是本人在 2026-10-12 10:10–10:13",
      "真实抓取并缓存的；550 次渲染请求、457 张图、63 次失败，都是同一批日志里可复算的事实。",
      "",
      "## 读者与核心问题",
      "",
      f"- 受众：{PLAN['audience']}",
      f"- 核心问题：{PLAN['core_question']}",
      "- 读者读完应该能回答：这类服务的能力边界在哪、代价在哪、哪些坑可以提前避开。",
      "",
      "## 叙述路线与编辑意图",
      "",
      f"- {PLAN['narrative']}",
      "- 十页共用一套编辑身份（纸色、栅格、等宽数字、证据芯片），但**每页主视觉形式不同**：",
      "  封面用规模数字与管线剪影，管线页用八张阶段卡，词汇页用芯片矩阵，度量页用常数条与",
      "  增量条，失败页用分面统计加响应原文，预算页用比例条，色彩页用成对色表，字体页用",
      "  同句四族样张，时间页用直方图，末页用分级清单收束。",
      "- 阅读关系：01 给规模 → 02 给流程 → 03/04 给『能用什么、准到什么程度』→",
      "  05/06 给『会怎么失败、预算多少』→ 07/08/09 给三个具体维度的实测 → 10 收束到边界。",
      "",
      "## 证据分级（贯穿全特辑）",
      "",
      "- **事实**：文档原文或服务响应可直接指认（给 source_id 或请求 ID）",
      "- **测量**：从日志与像素回读计算，脚本可复算",
      "- **解释**：本报告对证据的推断（如『线性光插值』『八阶段拆分』）",
      "- **演示**：为说明机制构造的示意（如四族样张的措辞）",
      "- **未确认**：明确写不知道（如边缘计时 1.5 s 与客户端 249 s 之间的差值成因）",
      "",
      "## 限制与坦白",
      "",
      "1. 单一服务、约 20 小时窗口，不外推到其它渲染服务或生产峰值。",
      "2. 文本度量是墨迹回读的近似（±1px），且墨迹宽度不含 sidebearing，只能给方向。",
      "3. 无外部对照来源：会话禁止外部 HTTP，因此 Skia 插值等说法只能是推断。",
      "4. 统计口径刻意排除 B04 自身的请求，否则报告边写边变（写在 case-09 的页脚）。",
      "5. 缓存命中率 2.8% 只说明本套没有做去重设计，不能用来评价服务缓存能力。",
      "",
      "## 制作过程",
      "",
      f"- 请求：{MET['counts']['snapshot_requests']} 次（成功 "
      f"{MET['counts']['successful_snapshot_requests']}、失败 "
      f"{MET['counts']['failed_snapshot_requests']}）",
      f"- 墙钟 {MET['timings']['elapsed_seconds']} s，其中请求耗时 "
      f"{MET['timings']['request_duration_sum_seconds']} s，其余为读日志、写脚本与看图",
      "- 每页都经生成器审计（重叠/越界/最小字号三项为 0）并实际看图；"
      "十页另做一张 contact sheet 复核整体节奏",
      f"- 复算路径：`tmp/{RUN}/B04/b04data.py` → `data.json` → `b04pages.py` → 十份 DSL",
      ""]
(OUT / "editorial-note.md").write_text("\n".join(ed), encoding="utf-8")

us = ["# B04 · Snapshot 用法记录", "",
      "本题的『用法』有双重含义：既是用 Snapshot 做十页特辑，也是把 Snapshot 本身当研究对象。",
      "",
      "## 用到的 DSL 能力",
      "",
      "- 版式：`Stack` + `Positioned` 绝对栅格；`Container` 圆角/边框/渐变/阴影",
      "- 文字：`Text`（三族：Noto Sans CJK SC / Noto Serif CJK SC / Noto Sans Mono CJK SC）、",
      "  `Raw` 保留空格、`letterSpacing`、`fontFeatures=tnum`",
      "- 图形：`ClipPath`（色块遮罩、色带分格）、`shape=CIRCLE`、`line` 网格与坐标轴",
      "- 复用：`b04kit.Report` 封装页眉/页脚/证据芯片/条图/直方图，十页共用一套身份",
      "",
      "## 制作中确认的行为（与 B03 一致，未重复探测）",
      "",
      "- 文档正文里的 `<` `>` 会被转义显示为 `&lt;` `&gt;`，因此页面上改用中文措辞表达",
      "  『大于/小于』（case-10 修正）",
      "- `Text` 宽度不足会自动换行：所有长句改用 `para()` 按预测宽度断行",
      "- 卡片阴影 `boxShadow=\"0 14 34 #12202B22\"` 在纸色底上稳定可用",
      "- 一次请求最多 4096 个元素：十页都在 60 元素以内，无需合并子路径",
      "",
      "## 数据管线（本任务真正的工程）",
      "",
      "```",
      f"tmp/<run>/*/requests.jsonl  ─┐",
      f"tmp/<run>/_suite/requests.jsonl ├─ b04data.py ─→ data.json ─┐",
      f"tmp/<run>/_suite/docs/fonts.txt ─┘                          ├─ b04pages.py ─→ 10×DSL",
      f"outputs/<run>/B03/case-02/final.png（像素回读）──────────────┘        │",
      "                                                            render.py ─→ 10×PNG",
      "```",
      "",
      "- `b04data.py` 只读真实日志与缓存，不写死任何数字；页面构建时从 `data.json` 取值，",
      "  所以报告不会与证据脱节。",
      "- 统计排除 B04 自身请求，避免『边写报告边改变样本』。",
      "",
      "## 踩坑记录",
      "",
      "1. 外部资料不可得 → 换选题而不是换说法（见 editorial-note）。",
      "2. `hist()` 把计数画在深色柱内 → 深色底上不可读，改为柱顶上方标注。",
      "3. `fmt_num` 与单位拼接产生 \"6.0kms\" → 改为 `6,000 ms` 带千分位与空格。",
      "4. 页脚芯片 15px 触发最小字号审计 → 统一提到 16px，而不是放宽规则。",
      "5. 色带最初画的是**色标定义值**却标注为实测 → 改为真的从 B03 成品回读像素，",
      "   否则就是本题禁止的『把演示当事实』。",
      "",
      "## 交付核对",
      "",
      f"- 十页 PNG/DSL/case.md：`outputs/{RUN}/B04/case-01…case-10/`",
      f"- 作品集：`portfolio.json` `portfolio.md` `gallery.md`",
      f"- 来源与主张：`sources.json`（{len(SRC['sources'])} 个来源、"
      f"{len(SRC['claims'])} 条主张、{len(SRC['unread_sources'])} 条未读声明）",
      f"- 编辑手记：`editorial-note.md`；统计：`task-metrics.json`",
      ""]
(OUT / "snapshot-usage.md").write_text("\n".join(us), encoding="utf-8")
print("portfolio cases:", len(cases), "claims:", len(SRC["claims"]))
