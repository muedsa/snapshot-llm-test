"""Build outputs/<run>/B04/snapshot-usage.md from the real B04 logs.

Run from the suite root:
  python tmp/<run_id>/B04/build_b04_usage.py
"""
import json
import os
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

root = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
rid = os.environ["SNAPSHOT_RUN_ID"]
temp = root / "tmp" / rid / "B04"
out = root / "outputs" / rid / "B04"

jl = lambda p: [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]
M = json.loads((out / "task-metrics.json").read_text(encoding="utf-8"))
P = json.loads((out / "portfolio.json").read_text(encoding="utf-8"))
S = json.loads((out / "sources.json").read_text(encoding="utf-8"))
req = jl(temp / "requests.jsonl")
itn = jl(temp / "iterations.jsonl")
tools = jl(temp / "tool-usage.jsonl")
shared = jl(root / "tmp" / rid / "_suite" / "requests.jsonl")
req_by_id = {r["request_id"]: r for r in req}
CP = re.compile(r"B04/(case-\d\d)/")


def case_of(i):
    m = CP.search(i.get("image_path") or "")
    if m:
        return m.group(1)
    m = re.match(r"case(\d\d)", i.get("version") or "")
    return "case-%s" % m.group(1) if m else None


attrs = Counter()
tags = Counter()
for c in P["cases"]:
    for t in c["dsl_capabilities"]["tags"]:
        tags[t] += 1
    for a in c["dsl_capabilities"]["notable_attributes"]:
        attrs[a] += 1
counts = Counter()
for c in P["cases"]:
    for k, v in c["dsl_capabilities"]["counts"].items():
        counts[k] += v

docs_read = [r for r in shared if str(r.get("request_id", "")).startswith("shared-doc")]
T = M["timings"]
L = []
A = L.append
A("# Snapshot 使用情况说明与踩坑记录 · B04")
A("")
A("任务ID：B04（自主研究一个真实主题并制作十件视觉特辑）")
A("任务名称：《月影手册 · 21 世纪日食特辑》")
A("本次运行ID：%s" % rid)
A("完成状态：完成")
A("结束原因：需求满足并完成视觉自检——十件各有 final.png/final.snapshot/case.md 三件套，"
  "逐件实际看图并按图修改，收尾产物（portfolio.json/md、gallery.md、sources.json、"
  "editorial-note.md、snapshot-usage.md、task-metrics.json）齐备")
A("输出目录：outputs/%s/B04/" % rid)
A("临时目录：tmp/%s/B04/" % rid)
A("路径基准：本文与同目录其它报告里的本地链接相对本文所在的 `outputs/<run>/B04/`；"
  "提到过程文件时写成 `tmp/<run>/B04/...`，其基准是总任务根（suite_root）。"
  "遵循 [PATHS.md](../../../PATHS.md)，全文无盘符、无用户目录、无 UNC 路径。")
A("")
A("## 1. 最终产物与需求完成情况")
A("")
A("十件独立完整主作品（各 1 张最终 PNG + 同名完整 DSL），全部是服务真实响应按字节指纹提升，"
  "无后处理、无占位图：")
A("")
A("| 件 | 主图 | 同名 DSL | 尺寸 | 内容任务（题目要求的“研究→编辑→视觉”落点） | 状态 |")
A("|---|---|---|---|---|---|")
for c in P["cases"]:
    A("| [%s](%s/case.md) | [final.png](%s/final.png)（%s B） | [final.snapshot](%s/final.snapshot)（%s B） | "
      "%d×%d | %s | 完成 |"
      % (c["id"], c["id"], c["id"], f"{c['png_bytes']:,}", c["id"], f"{c['snapshot_bytes']:,}",
         c["dimensions"][0], c["dimensions"][1],
         dict((x["id"], x["user_goal"]) for x in P["cases"])[c["id"]]))
A("")
A("题面逐项核对：")
A("")
A("- “自选真实主题 + 亲自研究资料”：主题为 21 世纪日食（不依赖实时信息，符合题目允许的非新闻题材）；"
  "实际抓取 %d 次文档请求、其中 %d 个 URL 取到正文，全部原页缓存留在 `tmp/%s/B04/sources/`（HTML + headers）。"
  % (S["access_account"]["document_requests"], S["access_account"]["urls_accessed_ok"], rid))
A("- “区分已证实事实／来源结论／你的解释／演示内容”：四级标注写进图内与 case.md；"
  "计数口径在件-10 上如实说明是**自标覆盖率**（已证实 1／来源结论 1／推算 13／演示 0，截至其快照时刻），"
  "不是内容真值率。本辑“演示”为 0 是实情：十件没有编造数据。")
A("- “图表数据/分母/单位/比例/时间范围正确，图示不能为了气势改掉事实”：所有计数由解析脚本从原表派生 "
  "（`research/catalog.json` 224 行逐行解析，失败行进 `unparsed`）；分母在图上写明；"
  "件-04/06/08 的轴按真实数值比例绘制；件-05 把目录 ΔT 74 s 与路径页 ΔT 70.6 s 的 3.4 s 差异并列而不取舍。")
A("- “观点和比喻不能冒充证据”：比喻（如件-03“复读机”）只出现在标题层，数值层一律给来源或算法；"
  "件-08 的“中国经度带 29 个／全食 7 个”在图上写明是按 75°E–135°E 的编辑口径筛点，不是行政边界。")
A("- “不能把未访问页面列为已读来源”：`sources.json` 的 `never_read_pages` 单列 %d 个从未取到正文的 URL"
  "（404 %d 次、超时/传输 %d 次），`accessed:false`，只在件-10 的 D 区作为“失败的一半”展示。"
  % (S["access_account"]["urls_never_read"], S["access_account"]["http_404"],
     S["access_account"]["timeout_or_transport"]))
A("- “充分使用检索、数据/文本处理、编程、视觉检查等工具”：`tool-usage.jsonl` 共 %d 条真实记录 "
  "（抓取 6 轮、解析与调试、派生计算、闸门试算、QA 裁图、提升与留痕），见第 3、4 节。"
  % M["counts"]["tool_usage_records"])
A("- “至少 10 件自足作品 + 有意义的阅读关系 + 编辑意图”：十件各自成立；关系不是口头声称——"
  "件-10 用矩阵给出 15 条由“两份生成器实际读取同一份 `research/*.json`”算出的共享输入边，"
  "并据此排出三条阅读路线（E 区）。")
A("")
A("## 2. 文档阅读与实际使用的能力")
A("")
A("服务基地址：`https://open-snapshot.muedsa.com`（总 run-config 覆盖各单题默认值）")
A("文档访问日期：%s（suite 级共享抓取，B04 复用已下载正文与本仓库解析脚本，未为同一文档重复发请求）"
  % (docs_read[0]["started_at"][:10] if docs_read else "未确认"))
A("")
A("AI 使用指南：https://open-snapshot.muedsa.com/ai-guide.md（`shared-doc-001-guide-ai`，HTTP 200）")
A("实际用到的规则：请求体是 UTF-8 纯文本 DSL、无需 API Key；响应 Content-Type 为 image/png 时按字节保存；"
  "非 200 时保留错误响应文件且不写成成品；`GET /fonts` 用一次即可（B04 的 `B04-fonts-20261011T070651Z`，"
  "返回 27 个字体族，之后十件的 fontFamily 都从中选）。")
A("")
A("| 实际阅读的文档页面 | 本次用到的具体知识 | 对应产物位置 |")
A("|---|---|---|")
for r in docs_read[:12]:
    A("| `%s`（%s） | %s | 全套 DSL 通用（见下行汇总） |"
      % ((r.get("url") or "").replace("https://snapshot.muedsa.com/", "").replace(
          "https://open-snapshot.muedsa.com/", ""), r["http_status"],
          {"shared-doc-001-guide-ai": "请求格式、字体查询、响应检查、错误处理",
           "shared-doc-002-openapi": "接口字段与响应头（Server-Timing、限流头）",
           "shared-doc-003-doc-home": "文档结构与术语",
           "shared-doc-004-doc-parser-tags": "标签与属性写法（XML 属性式）",
           "shared-doc-005-doc-widgets": "可用图元清单",
           "shared-doc-006-doc-container": "Container 的 alignment/color/borderRadius/clipBehavior",
           "shared-doc-007-doc-concepts": "布局概念（盒模型与坐标系）",
           "shared-doc-008-doc-layout": "Positioned/Stack 的定位语义",
           "shared-doc-009-doc-painting": "绘制顺序、裁剪与描边",
           "shared-doc-010-doc-media-text": "Text 的 fontSize/fontFamily/fontStyle/textAlign",
           "shared-doc-011-doc-rendering": "渲染尺寸与 type=png",
           "shared-doc-012-doc-parser": "解析器对未知属性的容错边界"}.get(
              r["request_id"].rsplit("-", 1)[0] if r["request_id"].startswith("shared-doc") else r["request_id"],
              "布局/绘制/文本语义核对")))
A("")
A("实际使用的能力（由 10 份 `final.snapshot` 正则统计，不是“理论上可用”）：")
A("")
A("- 标签：%s（按“出现在几件里”计）。" % "、".join("`%s`×%d 件" % (k, v) for k, v in tags.most_common()))
A("- 属性：%s。" % "、".join("`%s`×%d 件" % (k, v) for k, v in attrs.most_common()))
A("- 元素规模：Container %s、Positioned %s、Text %s、Transform %s、Stack %d；"
  "DSL 合计 %s 字节。"
  % (f"{counts['Container']:,}", f"{counts['Positioned']:,}", f"{counts['Text']:,}",
     f"{counts['Transform']:,}", counts["Stack"], f"{M['counts']['final_dsl_bytes_total']:,}"))
A("- 版面手法：`<Snapshot background=\"#080D1C\" type=\"png\">` 定底；`Stack`+`clipBehavior` 做整页裁剪；"
  "`Positioned` 绝对定位承担“手册骨架”（页眉编号、脚注数据带）；`Container color=` 画实心矩形与色块矩阵；"
  "`borderRadius` 做胶囊与卡片；`Transform matrix=`（4 件、共 %s 次）承担旋转刻度与斜线；"
  "文字一律 `Text` + `fontFamily`（Inter/Noto Sans SC 正文、Noto Sans Mono CJK SC 数字、Noto Serif CJK SC 引文）。"
  % f"{counts['Transform']:,}")
A("- 本辑**没有**用到的能力（与 B01 对比后如实记录）：渐变（gradient*）、阴影（boxShadow/textShadow）、"
  "混合模式、模糊（sigmaX）、OpenType tnum、富文本、`<Image>`。10 份 DSL 的 `<Image>` 标签数均为 0，"
  "所以画面 100% 由上述图元构造，未嵌入任何外部素材或参考图。")
A("- 服务没有矢量 path 图元：圆锥（件-01）、月牙与阶梯（件-03）、曲线（件-06/07）、"
  "地理网格点（件-08）全部由矩形扫描线、圆角矩形与 `Transform` 斜条逼近，放大可见棱角，各件图上已注明。")
A("- 字体查询结果文件：`tmp/%s/B04/fonts/`（含 `/fonts` 响应留痕）；`sources.json` 的 `fonts_query` 记录请求ID。" % rid)
A("")
A("## 3. 迭代过程、服务调用与图像检查")
A("")
A("请求记录文件：`tmp/%s/B04/requests.jsonl`（%d 行，含文档/渲染/字体三类）" % (rid, M["counts"]["http_requests_total"]))
A("构建与闸门记录：`tmp/%s/B04/build-log.jsonl`（每次 TextFit 检查与提交结果一行）" % rid)
A("迭代记录文件：`tmp/%s/B04/iterations.jsonl`（%d 行）" % (rid, M["counts"]["iterations_total"]))
A("工具使用记录：`tmp/%s/B04/tool-usage.jsonl`（%d 行）" % (rid, M["counts"]["tool_usage_records"]))
A("")
A("渲染提交 **%d** 次：HTTP 200 **%d** 次，传输层失败 **%d** 次（件-10 v04 curl(56) 连接重置 39.2 s／0 字节；"
  "v07 响应体截断，只收到 296,737 / 407,170 字节，服务端 Server-Timing 显示 render 已完成 927.1 ms），"
  "两次都按同一 DSL 重发并取到完整响应；400 语法错误 **%d** 次——因为提交前一律过本地 TextFit 与属性自检，"
  "语法与超宽问题在本地就被拦下。"
  % (M["counts"]["render_submissions"], M["counts"]["render_ok"],
     M["counts"]["render_transport_or_truncated"], M["counts"]["render_errors_400"]))
A("")
A("另有 **%d** 次被本地闸门拦下、**未向服务发出任何请求**（`build-log.jsonl` 中 `request_sent:false`：%s），"
  "与渲染失败分开统计；件-04 的 case.md 还自述 1 次拦下，但那次早于该留痕约定、无机器记录，"
  "所以“可核对的拦下数”是 %d，报告口径的总数是 5，差额在 `task-metrics.json` 里写明而不合并。"
  % (M["counts"]["gate_blocked_no_request"],
     "、".join("%s×%d" % (k, v) for k, v in sorted(M["counts"]["gate_blocked_by_case"].items())),
     M["counts"]["gate_blocked_no_request"]))
A("")
A("文档抓取 **%d** 次（200 %d／404 %d／超时或传输 %d），去重后取到正文的页面 **%d** 个；"
  "`GET /fonts` **%d** 次。DSL 版本名 **%d** 个；实际图片查看 **%d** 次；完整视觉迭代 **%d** 次"
  "（baseline %d／syntax-fix %d／retry %d 单列，不计入视觉迭代）。"
  % (M["counts"]["document_requests"], M["counts"]["document_by_status"]["200"],
     M["counts"]["document_by_status"]["404"], M["counts"]["document_by_status"]["timeout_or_transport"],
     M["counts"]["distinct_ok_document_pages"], M["counts"]["fonts_queries"],
     M["counts"]["dsl_versions"], M["counts"]["image_views"],
     M["counts"]["completed_visual_iterations"], M["counts"]["iterations_by_type"]["baseline"],
     M["counts"]["iterations_by_type"]["syntax-fix"], M["counts"]["iterations_by_type"]["retry"]))
A("")
A("初次生成并查看记为 baseline，不算改进；下表“看图后修改”才计为视觉迭代。逐件明细：")
A("")
A("| 件 | 版本数 | 渲染提交 | 失败/截断 | 闸门拦下 | 看图 | 视觉迭代 | 定稿请求 |")
A("|---|---|---|---|---|---|---|---|")
for p in M["case_metrics"]:
    A("| [%s](%s/case.md) | %d | %d | %d | %d | %d | %d | `%s` |"
      % (p["case_id"], p["case_id"], p["dsl_versions"], p["render_submissions"],
         p["transport_failures_or_truncations"], p["gate_blocked_no_request"],
         p["image_views"], p["completed_visual_iterations"], p["promoted_from_request"]))
A("")
A("逐条留痕（请求ID／版本／类型／状态／耗时／看图结论摘录，取自 `iterations.jsonl` 与 `requests.jsonl` 原文）：")
A("")
A("| 迭代ID | 件/版本 | 类型 | 请求ID与状态 | 端到端耗时 | 看图时间与结果（问题→改动） |")
A("|---|---|---|---|---|---|")
for i in itn:
    c = case_of(i) or "—"
    ridm = [r for r in req if r.get("dsl_version") == i.get("version")]
    rr = ridm[-1] if ridm else None
    dur = ("%s s" % rr["duration_seconds"]) if rr else "—"
    st = str(rr["http_status"]) if rr else "未提交"
    prob = (i.get("observed_problems") or "—").replace("\n", " ")[:150]
    chg = (i.get("changes_made") or "—").replace("\n", " ")[:150]
    A("| `%s` | [%s](%s/case.md) `%s` | %s | `%s`（%s） | %s | 看图 %s：%s → %s |"
      % (i["iteration_id"], c, c, i["version"], i["type"],
         (rr["request_id"] if rr else "—"), st, dur,
         (i.get("image_viewed_at") or "未看图")[:19].replace("T", " "), prob, chg))
A("")
A("响应文件位置：每题的原始响应与请求体在 `outputs/%s/B04/<case>/requests/`（含失败那两次的 "
  "`.body.txt`、`.response-headers.txt` 与半截 `.response.bin`），逐版预览在 `outputs/.../<case>/*-preview.png`，"
  "2× 放大裁图在 `tmp/%s/B04/<case>/qa/`（只作观察用，不进交付物）。" % (rid, rid))
A("")
A("## 4. 修改记录与踩坑")
A("")
A("| 迭代ID / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比与剩余问题 | 相关临时文件 |")
A("|---|---|---|---|---|---|")
pitfalls = [
    ("parse_lunar.py / 语法修复", "月食目录首轮只解析出 56 行",
     "正则把月龄列宽写死；`B04-tool-003` 记录了逐轮放宽：56→64（ΔT 列 2 位）→116（QSE 标志列）→178（类型子类）",
     "按页面自述的类型计数与年份分布对账后放宽正则", "最终行数与页面自述一致，对账通过",
     "`tmp/<run>/B04/parse_lunar.py`、`research/` 中间产物"),
    ("parse_path.py / 语法修复", "GE/GD/ΔT 三项全为 None",
     "Greatest Eclipse 与数值之间夹着 `<a>` 标签与 HTML 注释，且 body 起点判断过窄（`B04-tool-007` 两次修正）",
     "先剥标签再匹配，并把注释当作可跳过的空白", "两条路径页全部字段解析成功",
     "`tmp/<run>/B04/parse_path.py`、`research/path-pages.json`"),
    ("derive_duration.py / 口径错误", "第一版把样本限定成“时长与宽度都有”的 142 条",
     "误剔 2 条有时长无宽度的环食（2003-05-31 217 s、2044-02-28），分母被悄悄改变（`B04-tool-010`）",
     "改成按时长取样本、带宽另列，分母在图上写明",
     "分布与极值口径自洽；这是“为了图好看改分母”的反例，已在件-06 case.md 记录",
     "`tmp/<run>/B04/derive_duration.py`、`research/duration.json`"),
    ("b04kit.ring 构件缺陷 / 渲染成功但视觉不符", "件-06 v03 的三个“白圈”画成实心奶油圆点",
     "构件内层矩形尺寸写错，服务照实渲染——不是服务问题（`B04-tool-011` 用 400×200 探针 DSL 定位，未发请求）",
     "修 `ring()` 内径，探针先验证再回到件-06", "v04 起圆环正确；构件层修复惠及件-07/08/09",
     "`tmp/<run>/B04/probe/`、`b04kit.py`"),
    ("件-06 v04x / 操作失误造成的多余请求", "同内容 DSL 被多渲染一次",
     "写 v03 迭代记录的同一命令行里误加 `--version v04x`（`B04-tool-013` 如实记为不该发生的请求）",
     "保留该请求与 `retry` 迭代记录；promote 规则“同版本取最后一次成功响应”使成品指向 v04x",
     "已核对 v04 与 v04x 的 DSL 与 PNG 三方 md5 逐字节相同，成品即看过的那张图",
     "`tmp/<run>/B04/build-log.jsonl`、`case-06/requests/`"),
    ("件-04 / TextFit 闸门拦下 1 次", "长句估宽超出 1500 px 盒",
     "页脚数据带单行文本按 1.45 行距算需 2 行，`est_w > box_w×0.96`",
     "把长句拆成两行并缩短措辞（不缩字号硬塞）", "v03 提交后 0 警；但这次拦下早于 build-log 约定，无机器留痕",
     "`case-04/case.md` 的版本行"),
    ("件-09 / 闸门拦下 1 次（有机器留痕）", "v01 页脚第 2 行超宽",
     "`build-log.jsonl` 中 `request_sent:false` 记录，警告原文一并留档",
     "拆行后重跑闸门再提交", "v01→v05 全部 200；未发出的请求不计入渲染数",
     "`tmp/<run>/B04/build-log.jsonl`"),
    ("件-10 / 闸门拦下 3 次", "v01 两处、v02 一处、v06 一处超宽（最长估宽 1153 px）",
     "元页面要写的口径句天然长；可用宽是 936×0.96=898 px",
     "用 `measure10.py` 逐条试算 `(盒宽, 字号, 文本)`，长句一律拆行或换词（如 final.snapshot→九份 DSL）",
     "v03 起 0 警提交；三次拦下都补记为 `request_sent:false`（事后补记，已注明）",
     "`tmp/<run>/B04/measure10.py`、`measure10.json`"),
    ("件-10 / 传输层失败 2 次", "v04 curl(56) 连接重置（39.2 s，0 字节）；v07 响应截断 296,737/407,170 字节（240.1 s）",
     "客户端链路问题而非 DSL 问题：v07 的响应头已有 Server-Timing（render 927.1 ms）与完整 Content-Length，"
     "说明服务端已画完，只是没传完",
     "同一 DSL 原样重发；`render.py` 按 Content-Length 校验长度，短了就判失败而不是存成成品",
     "两次重发都拿到完整 407,170 字节响应；失败留痕保留在 `case-10/requests/`",
     "`outputs/<run>/B04/case-10/requests/B04-case10-v04-20261011T102717Z.*`、`...v07-20261011T103049Z.response.bin`"),
    ("件-10 / 自指与时间戳缺陷", "`generated_at` 在 v09 交付时是脚本里手写的 “2026-10-11T10:05Z”",
     "元页面只能反映扫描时刻；手写字符串不是真实时钟（件-10 的 case.md 已列为限制）",
     "改为读取真实 UTC 时钟；把件-10 当时所读那份原样冻结为 `research/meta-case10-frozen.json`",
     "重跑后 meta 增长到 http 86／渲染提交 45／迭代 46，与成品 DSL 所印数字的差值已逐条写明",
     "`research/meta.json`、`research/meta-case10-frozen.json`"),
    ("文档抓取 14 次失败", "404×10、超时/传输×4（含 en.wikipedia.org 一次长超时）",
     "候选 URL 是猜的或已迁移；wiki 页族在本环境不稳定",
     "改抓 `solar.html` 链接清单里真实存在的页族（`B04-tool-025`），并改用已抓到的 NASA 事实页做交叉核对"
     "（`B04-tool-008/016` 用 grep 确认常数确实在本地页面里）",
     "14 个 URL 始终没读到正文，全部标 `accessed:false`，未列为来源；件-10 D 区把失败样本原文列在图上",
     "`tmp/<run>/B04/fetch_sources*.py`、`sources.json` 的 `never_read_pages`"),
    ("来源点名缺失（留痕缺陷）", "件-02、件-03 的 case.md 与成品 DSL 里没有任何文件名级来源点名，件-01 只写了裸目录 `sources/`",
     "早期件把“见 sources/ 目录”当成引用；`meta_stats.py` 的 sources_per_case 与件-10 C 区如实计为 0/0/1",
     "不改写历史报告；件-10 D 区整份列出 25 个去重页面作为补救，`sources.json` 按 URL 逐条给出访问记录",
     "缺口在图上可见（件-10 C 区用橙色标注），读图者能自行核对",
     "`outputs/<run>/B04/case-10/case.md`、`sources.json`"),
]
for row in pitfalls:
    A("| %s | %s | %s | %s | %s | %s |" % row)
A("")
A("渲染成功但视觉不符合要求、靠看图发现并改掉的问题（各件 case.md 的版本小节留有逐条对应）：")
for i in itn:
    if i["type"] == "visual" and i.get("observed_problems"):
        A("- `%s`（%s）：%s" % (i["iteration_id"], case_of(i) or "—",
                                str(i["observed_problems"]).replace("\n", " ")[:220]))
A("")
A("## 5. 任务耗时与请求统计")
A("")
A("结构化指标文件：`task-metrics.json`（同目录，含逐用例指标与成品 md5）")
A("")
A("| 指标 | 实际值 | 单位 | 数据来源与统计范围 |")
A("|---|---|---|---|")
A("| 任务开始（最早留痕） | %s | 含时区时间 | `requests.jsonl` 最早一条（文档抓取）|" % T["first_evidence_at"])
A("| 任务结束（最晚留痕） | %s | 含时区时间 | 本报告的生成时刻；过程中各日志末行时间见 `task-metrics.json` |"
  % datetime.now(timezone.utc).isoformat())
A("| 任务总耗时（墙钟） | %d | 秒 | %.2f h，首末留痕之差；不等于持续工作时长 |"
  % (T["wall_clock_seconds"], T["wall_clock_seconds"] / 3600.0))
A("| 其中空闲/无留痕间隔 | %d | 秒 | %d 段相邻留痕间隔 >900 s，逐段列在 `timings.idle_gaps`；"
  "只算经过时间，不算工时 |" % (T["idle_gap_seconds"], len(T["idle_gaps"])))
A("| 有记录的活动时长 | %d | 秒 | 墙钟减空闲间隔，是“有证据的时间上界”，非专注秒表 |"
  % T["active_seconds"])
A("| 首次可用图耗时 | %d | 秒 | 从最早留痕到第一次 HTTP 200 渲染响应（`B04-case01-v01`）|"
  % round((datetime.fromisoformat(min(r["started_at"] for r in req if r["http_status"] == 200))
           - datetime.fromisoformat(T["first_evidence_at"])).total_seconds()))
A("| 等待用户反馈 | 0 | 秒 | 单题一次成稿，无外部反馈等待；A21/A22 才有的预置轮次不适用本题 |")
A("| 限流等待 / 排队等待 | 未发生 / 未知 | 秒 | 响应头 `x-ratelimit-remaining` 始终 ≥119（见 requests 记录），"
  "未出现 429 与 Retry-After；服务端排队不可测，记为未知 |")
A("| 已记录请求耗时之和 | %d | 秒 | %d 次成功渲染的 curl 端到端 `duration_seconds` 之和；"
  "与墙钟重叠，不相加进总耗时 |"
  % (T["request_duration_sum_seconds"], M["counts"]["render_ok"]))
A("| 服务端渲染耗时 | 最大 %s ms | 毫秒 | 响应头 Server-Timing（`render;dur=`），与客户端耗时分列 |"
  % T["server_render_ms_max"])
A("| 成功 / 失败 / 重试 | %d / %d / %d | 次 | 渲染提交 %d 次；文档 %d、字体 %d 另计 |"
  % (M["counts"]["render_ok"], M["counts"]["render_transport_or_truncated"],
     sum(p["retry_requests"] for p in M["case_metrics"]), M["counts"]["render_submissions"],
     M["counts"]["document_requests"], M["counts"]["fonts_queries"]))
A("| 实际看图 / 完整视觉迭代 | %d / %d | 次 | `iterations.jsonl` 的 `image_viewed_at` 与 `type:visual`；"
  "该时间是记录写入时刻（同用例多行可能相同），真实逐版看图以预览与 QA 裁图文件时间交叉印证 |"
  % (M["counts"]["image_views"], M["counts"]["completed_visual_iterations"]))
A("| 闸门拦下（未发请求） | %d | 次 | `build-log.jsonl` 的 `request_sent:false`；报告口径另有件-04 的 1 次无机器记录 |"
  % M["counts"]["gate_blocked_no_request"])
A("")
A("共享准备（suite 级 15 次文档/openapi 抓取）不计入本题请求数，见 `tmp/%s/_suite/requests.jsonl`；"
  "本题的 %d 次文档抓取与 %d 次渲染提交都是自己的。" % (rid, M["counts"]["document_requests"],
                                                        M["counts"]["render_submissions"]))
A("")
A("## 6. 设计选择、经验与未解决事项")
A("")
A("关键设计选择（每一处都有预览/看图依据）：")
A("")
A("- **底色与三色**：深空 `#080D1C` 统一整套手册，强调只用 ember（日/危险）、cyan（几何/月食）、"
  "corona（日冕/高亮），纸面 `#EFE6D3` 只给件-02（“账本”要读起来像印刷纸）。看图依据：件-02 v01 的"
  "主标题完全没显示——`header()` 少传 `paper=True`，纸上浅色压在纸底上等于隐形；补上后纸本配色才成立。")
A("- **版式随内容变**：几何页要有锥（件-01 扫描线）、清点页要能数（件-02 点阵）、时间轴按真实天数比例"
  "（件-04）、档案页保留等宽原文（件-05）、点图保持面积比（件-08）。十件骨架不同但页眉编号与脚注数据带一致。")
A("- **把差异留在图上而不是抹平**：件-05 的两个 ΔT、件-07 的两种算法、件-08 的整数度量化、件-06 的"
  "“最宽不等于最长”，都在版面上并列，让读者看到不一致本身。")
A("- **看图会推翻设计而不是只调字号**：件-01 的 ② 区原本画“放大扫描锥”，v03 的 2× 裁图看出扫描线"
  "露出明显条带、远地点那行的尖端翻到月球左侧，v04 直接把锥体删掉换成从 0 出发的余量条＋三角记号"
  "（轴量的是尖端相对地表的差距，月球并不在该轴的固定位置——语义错误，不是画得不够好）。")
A("- **跨件呼应靠图内标记**：件-08 v03/v04 加的十字标记指回件-05、件-07 逐点分析过的 2024-04-08 与"
  "2027-08-02 两次食甚点；图例文字从“十字 05/07”（读者无法解码的套件内部编号）改成“2024/2027”。")
A("- **件-10 用元页面收束**：与其写一段“编者感想”，不如把关系、分级、来源账与限制做成可核对的表；"
  "矩阵的 15 条边来自“两个生成器实际读同一个 research/*.json”，不是编辑感觉。")
A("")
A("可复用的经验（Snapshot 相关）：")
A("")
A("- 提交前的本地自检比服务报错便宜：TextFit（SLACK 0.96／PITCH 1.45，CJK 1.0 em、空格 0.30 em、"
  "拉丁数字 0.50 em）把“文字压盖/被截”类问题在发请求前拦下，本题 0 次 400 就是这么来的；"
  "被拦下的行一律拆行或换词，不缩字号硬塞。")
A("- 密集版面必须靠 2× 裁图判断：9.5 px 的 URL 清单在整图预览里“看起来没问题”，裁图才看出被切底（件-10 v03→v05）。")
A("- `Container color=` 画矩阵格子时，0 值格要与底衬同色系否则网格消失（件-10 v03→v04 加 `#05080F` 底衬）。")
A("- `Transform matrix=` 是唯一可靠的斜线手段，但小角度下 1 px 线的抗锯齿会闪断；刻度密度要跟着降。")
A("- 服务无 path 图元：任何曲线/圆锥都提前设计成“矩形扫描线 + 圆角”可接受的形态，并在图上注明棱角限制。")
A("- 长渲染（>2 min）用后台任务等完成，不要重发：件-10 v07 那次截断正是等待期，重发前先看 Content-Length 与实际字节。")
A("- 自指型页面（件-10）要预留“快照时刻”语义：所有统计标明截至点、本件自己在表外，交付后差值写进 case.md。")
A("")
A("未解决事项与限制（均为已如实呈现，不是待补工作量）：")
A("")
for k in P["final_collection_review"]["remaining_issues"]:
    A("- " + k)
A("")
A("结束依据：题目要求“逐件实际看图及整体最终审查、完整需求达成”。十件均有 baseline + 按图修改的视觉迭代记录、"
  "定稿请求与字节指纹一致的 final.png/final.snapshot、同名 case.md；整体终审见 `portfolio.json` 的 "
  "`final_collection_review` 与件-10。")
A("")
A("留痕完整性确认：临时目录保留 `PLAN.md`、6 轮抓取脚本与其失败样本、解析脚本的中间修正、派生数据 "
  "（`research/*.json` 14 个，含被 v1 口径淘汰的 `seasons-solar-only-v1.json`）、闸门试算台 `measure10.py/json`、"
  "每件逐版 DSL 与预览、QA 裁图、`build-log.jsonl` 与三份日志、被拦下的 DSL 草稿（`case10-v0draft.py.bak`）。"
  "没有删除或覆盖任何尝试文件；运行时缓存（`__pycache__/`、`*.pyc`）按总任务根 `.gitignore` 排除，"
  "不列为证据。无法取得的留痕：件-04 那次闸门拦下的机器记录（当时未启用 `request_sent:false` 约定）、"
  "14 次失败抓取的页面正文（本就没有取到）。")
A("")
(out / "snapshot-usage.md").write_text("\n".join(L) + "\n", encoding="utf-8")
print((out / "snapshot-usage.md").relative_to(root).as_posix(), len(L), "lines")
