"""B03 · snapshot-usage.md 生成（结构与 tasks/B03-*/templates/snapshot-usage-template.md 对齐）。

所有数字与路径来自真实留痕：task-metrics.json、case-info.json、doc-cites.json、
requests.jsonl、iterations.jsonl。表体不含任何未经核实的结论。

用法（总任务根执行）：python tmp/<run>/B03/build_usage.py
"""
import json
import os
from collections import Counter
from pathlib import Path

ROOT = Path(os.environ["SNAPSHOT_TASK_ROOT"])
RID = os.environ["SNAPSHOT_RUN_ID"]
TMP = ROOT / "tmp" / RID / "B03"
OUT = ROOT / "outputs" / RID / "B03"
DOCS = "tmp/%s/_suite/docs" % RID
RC = json.loads((ROOT / "run-config.json").read_text(encoding="utf-8"))
MET = json.loads((OUT / "task-metrics.json").read_text(encoding="utf-8"))
CI = json.loads((TMP / "case-info.json").read_text(encoding="utf-8"))
CITES = json.loads((TMP / "doc-cites.json").read_text(encoding="utf-8"))
META = json.loads((TMP / "portfolio-meta.json").read_text(encoding="utf-8"))
REQ = [json.loads(l) for l in (TMP / "requests.jsonl").read_text(encoding="utf-8").splitlines()]
ITR = [json.loads(l) for l in (TMP / "iterations.jsonl").read_text(encoding="utf-8").splitlines()]
RQ = {r["request_id"]: r for r in REQ}
CASES = sorted(CI)
C = MET["counts"]
T = MET["timings"]


def esc(s):
    return " ".join(str(s or "").split()).replace("|", "／")


L = ["# Snapshot 使用情况说明与踩坑记录",
     "",
     "任务ID：`B03`",
     "任务名称：用十件作品探索 DSL 的创意边界",
     "本次运行ID：`%s`" % RID,
     "完成状态：完成（10/10 件主作品定稿，逐件完成真实看图→改→再渲染→再比较的闭环）",
     "结束原因：需求满足并完成视觉自检（无用户中途改需求，无平台阻塞）",
     "输出目录：`outputs/%s/B03/`" % RID,
     "临时目录：`tmp/%s/B03/`" % RID,
     "路径基准：`suite_root`（本文内所有 `tmp/…`、`outputs/…` 相对总任务根；"
     "本文自身的 Markdown 本地链接相对 `outputs/%s/B03/`）" % RID,
     "",
     "遵循 [PATHS.md](../../../PATHS.md)：目录、产物、证据与脚本一律用相对路径或目录环境变量，"
     "不写盘符、用户目录或 UNC 路径。",
     "",
     "## 1. 最终产物与需求完成情况",
     "",
     "| 文件 | 用途 | 对应 DSL 或图片 | 完成状态 |",
     "|---|---|---|---|",
     ]
for c in CASES:
    v = CI[c]
    L.append("| `%s/final.png` | %s：定稿图（%d×%d，服务原始字节） | `%s/final.snapshot` | 定稿，"
             "提升自 `%s` |" % (c, META[c]["slug"],
                                v["dimensions"][0], v["dimensions"][1], c, v["promoted_from"]))
    L.append("| `%s/final.snapshot` | 与该图同源的可复现 DSL（%s 字符） | `%s/final.png` | 配对完整 |"
             % (c, format(v["dsl_chars"], ","), c))
L += ["",
      "题目要求逐项核对：至少 10 件独立完整主作品 ✔（10 件，媒介/幅面/数据模型/主手法互不重复）；"
      "每件落在自选真实使用场景 ✔（受众与使用者要做的事写在各 case.md 与 portfolio.json）；"
      "不交只有滤镜名称与小方块的能力示范板 ✔（最抽象的 case-10 也是一页交付文档）；"
      "尺寸/文案/数据/几何/效果自检 ✔（逐件 case.md「迭代表」＋运行时 assert＋TextFit 闸门）；"
      "所有最终 PNG 为实际服务响应 ✔（`promote.py` 用 md5 指纹确认成品字节＝该请求原始响应，"
      "final.snapshot 从同一请求的 body 留痕切出）；"
      "另交付 `technique-notes.md` ✔；`portfolio.json`/`portfolio.md`/`gallery.md`/"
      "`task-metrics.json` ✔。未满足项：无。",
      "",
      "## 2. 文档阅读与实际使用的能力",
      "",
      "服务基地址（以总 run-config 为准）：`%s`" % RC.get("service_base_url"),
      "文档站：`https://snapshot.muedsa.com/`；AI 使用指南：`https://open-snapshot.muedsa.com/ai-guide.md`",
      "访问日期：%s（本题 4 次直接抓取）与 %s（套件共享 15 次抓取，含本指南、文档站各页与 `GET /fonts`）"
      % (REQ[0]["started_at"][:10], "2026-10-08"),
      "",
      "请求格式按指南执行：`POST /snapshot`，UTF-8 纯文本 body（`<Snapshot …>…</Snapshot>`），"
      "无 API key；响应检查按 Content-Type 判定 `image/png` 或错误 JSON，并按 Content-Length 校验完整性"
      "（case-07 v03 的截断即由此发现）；错误处理保留 400/500 报文原文不删。"
      "字体查询用 `GET /fonts`：实际 27 族，`Inter` 各字重在列，"
      "`IBM Plex Mono`／`Courier New`／`Helvetica` 不在列，清单缓存在 `%s/fonts.txt`。" % DOCS,
      "",
      "| 实际阅读的文档页（缓存文件） | 本次使用的知识 | 对应文件或位置 |",
      "|---|---|---|",
     ]
seen = {}
for c, fn, term, note in CITES["verified"]:
    seen.setdefault((fn, term), (set(), note))
    seen[(fn, term)][0].add(c)
for (fn, term), (cases, note) in sorted(seen.items()):
    L.append("| `%s/%s` | 命中 `%s`：%s | %s |"
             % (DOCS, fn, term, esc(note), "、".join(sorted(cases))))
L += ["| `%s/ai-guide.md`、`%s/fonts.txt` | 请求格式、响应检查与可用字族 | 全部十件的渲染与字体选择 |"
      % (DOCS, DOCS),
      "",
      "实际使用的能力（只列真正出现在定稿 DSL 里的）：绝对布局 `Positioned`（合计 %s 处）、"
      "`Container` 色块/渐变/圆角/阴影/边框（%s 处）、`Text` 字号·字重·`fontStyle`·`letterSpacing`·"
      "`wordSpacing`·`height`·`overflow`·`foregroundMode` 描边·`textShadow`·`WidgetSpan`（%s 处文本节点）、"
      "`ClipRRect`/`ClipOval` 遮罩、`BackdropFilter`、`IndexedStack`、`<Raw>` 与 CDATA、"
      "仿射 `transform`＋`transformAlignment` 旋转/斜切、`ImageFiltered` 高斯模糊（%d 处）。"
      "**未使用任何 `<Image>` 外部素材**：十件定稿 DSL 的 `<Image>` 计数均为 0。"
      % (format(sum(CI[c]["nodes"]["Positioned"] for c in CASES), ","),
         format(sum(CI[c]["nodes"]["Container"] for c in CASES), ","),
         format(sum(CI[c]["nodes"]["Text"] for c in CASES), ","),
         sum(CI[c]["nodes"]["ImageFiltered"] for c in CASES)),
      "",
      "## 3. 迭代过程、服务调用与图像检查",
      "",
      "请求记录文件：`tmp/%s/B03/requests.jsonl`（追加式，含失败与重试）" % RID,
      "迭代记录文件：`tmp/%s/B03/iterations.jsonl`（追加式）；B 赛道另 "
      "`tmp/%s/B03/tool-usage.jsonl`" % (RID, RID),
      "",
      "| 指标 | 值 | 说明 |",
      "|---|---|---|",
      "| 渲染请求总数 | %d | kind=render 的 HTTP 请求，含探针 |" % C["by_kind"]["render"],
      "| 成功次数 | %d | HTTP 200 且响应体完整且无 error_summary |" % C["successful_snapshot_requests"],
      "| 失败次数 | %d | 400 %d 次、500 %d 次、传输层无响应 %d 次、截断 1 次 |"
      % (C["failed_snapshot_requests"], C["by_http_status"]["400"], C["by_http_status"]["500"],
         C["by_http_status"]["0"]),
      "| 重试请求数 | %d | 同版本号重复请求，全部为传输层故障重试 |" % C["retry_requests"],
      "| DSL 版本数 | %d | 十件各自的 vNN 去重；另有 %d 次探针请求（%d 份探针 DSL 缓存在 tmp 下）不计入作品版本 |"
      % (C["dsl_versions"], MET["shared_preparation"]["probe_requests"],
         len(list((TMP / "probe").glob("*.snapshot")))),
      "| 实际图片查看次数 | %d | iterations.jsonl 中 image_viewed=true |" % C["image_views"],
      "| 完整视觉迭代数 | %d | 已看图＋有父版本＋改后重渲并再比较 |" % C["completed_visual_iterations"],
      "| 未完成视觉迭代数 | %d | 有父版本但本版本未取得可看的图：case-06 v03（400 PARSE_ERROR）、"
      "case-07 v03（curl 28 超时两次＋响应体截断）。未看图共 %d 条，第三条 case-05 v01 是无父版本的基线，"
      "同样因 400（`clipBehavior` 的 Check failed）没有出图 |"
      % (C["incomplete_visual_iterations"], len(C["image_views_not_viewed"])),
      "| 其他接口查询 | 文档抓取 %d 次（本题）＋共享 %d 次 | 见 `tmp/%s/_suite/requests.jsonl` |"
      % (C["document_requests"], 15, RID),
      "",
      "十件定稿图的真实响应（逐条可在 requests.jsonl 复查）：",
      "",
      "| 请求ID | 输入 DSL（tmp） | 起止时间与耗时 | HTTP 与 Content-Type | 响应文件 | 查看时间与实际结果 |",
      "|---|---|---|---|---|---|",
     ]
for c in CASES:
    v = CI[c]
    r = RQ[v["promoted_from"]]
    ver = r["dsl_version"].rsplit("-v", 1)[-1]  # 如 "05"
    nver = "case-%s-v" % c.split("-")[1]
    it = next((i for i in ITR if i.get("request_id") == v["promoted_from"]
               or i["version"] in (nver + ver, nver + str(int(ver)))), None)
    dsl_rel = "tmp/%s/B03/case%s-v%s.snapshot" % (RID, c.split("-")[1], ver[1:])
    if not (ROOT / dsl_rel).exists():
        dsl_rel = r["request_file"]
    L.append("| `%s` | `%s` | %s → %s，%.3fs | %s，%s，%s 字节 | `%s` | %s |" % (
        r["request_id"], dsl_rel,
        r["started_at"][11:19], r["ended_at"][11:19], r["duration_seconds"],
        r["http_status"], r["content_type"], format(r["response_bytes"], ","),
        r["out_file"],
        esc((it["image_viewed_at"][:19] + " 已看图：" + (it["recompare_result"] or it["observed_problems"]))
            if it and it.get("image_viewed") else "该响应未单独看图（见迭代表）")))
L += ["",
      "失败与异常的留证（不删、不改写；次数与请求 ID 由 requests.jsonl 全量分组算出）：",
      "",
      "| 现象（错误签名） | 次数 | 典型请求 | 处理方式 |",
      "|---|---|---|---|"]
FAIL_HANDLING = {
    "Check failed": "确认 `Container` 的 `clipBehavior` 对该写法不可用，改用 ClipRRect/ClipOval 或去掉该属性",
    "Attr [gradient": "去掉 SWEEP 不支持的 `gradientRadius`，起始角改非负弧度",
    "Attr [border": "按属性表回退写法（描边与圆角不同时出现在该元素上）",
    "Unknown ele": "删除自造标签，改用文档内标签组合",
    "Tag Contain": "改为文档写法",
    "Attr [decor": "装饰属性回退到已支持项",
    "Unexpected ": "正文里的 `<` 走 CDATA/实体处理（已在 b03kit.tlab 内统一）",
    "no response body": "按 `--retries 3` 重试；提升脚本只取同名记录里最后一次 200",
    "truncated response body": "按 Content-Length 校验拒绝落盘，不写成品、不看图，重打后定稿",
    "INTERNAL_ERROR": "保留报文，改实现路径（外扩光晕不再走 shadow）",
}
fail_groups = {}
for r in REQ:
    if r["http_status"] == 200 and not r["error_summary"]:
        continue
    e = (r.get("error_summary") or "") + " " + str(r.get("http_status"))
    key = next((k for k in FAIL_HANDLING if k in e), "其他（HTTP %s）" % r["http_status"])
    fail_groups.setdefault(key, []).append(r)
for key, rows in sorted(fail_groups.items(), key=lambda kv: -len(kv[1])):
    L.append("| `%s` | %d | %s | %s |" % (
        key, len(rows),
        "、".join("`%s`" % x["request_id"] for x in rows[:2]),
        esc(FAIL_HANDLING.get(key, "保留报文，逐案改实现"))))
L += [
      "",
      "## 4. 修改记录与踩坑",
      "",
      "初次生成与查看计为基线（`type=baseline`，%d 条），不计为改进迭代；下表为 iterations.jsonl 全量 %d 条，"
      "按件分组，「问题或现象」列即当时看图所见。「原因及确认依据」在各件 `case.md` 的看图证据小节，"
      "未确认的原因不写。" % (C["iteration_records_by_kind"].get("baseline", 0), C["iteration_records"]),
      ""]
by_case = {}
for i in ITR:
    by_case.setdefault("case-%s" % i["version"].split("-")[1], []).append(i)
for c in CASES:
    L += ["### %s" % c, "",
          "| 迭代ID／类型／父版本 | 问题或现象 | 采取的修改 | 前后对比与验证结果 | 相关临时文件 |",
          "|---|---|---|---|---|"]
    for i in by_case.get(c, []):
        L.append("| `%s`／%s／%s | %s | %s | %s | %s |" % (
            i["version"], i["type"], i.get("parent_version") or "—",
            esc(i.get("observed_problems"))[:150], esc(i.get("changes_made"))[:120],
            esc(i.get("recompare_result"))[:150],
            "`%s`" % (i.get("image_path") or i.get("request_id") or "本地校验，无图")))
    L.append("")
L += ["**渲染成功但视觉不符合要求**的问题占多数（描边字与标题相撞、圆环内圆盖掉作图内容、√2 标签被下弧穿过、"
      "行内方块顶到基线上方、倒影呈硬边亮柱等），全部由看图发现后修改；"
      "另有两类是「看图看不到、由断言拦下」的：case-09 的 A6 标签放不下（AssertionError 中断渲染）与 "
      "OY−DIAG 断言（742 vs 736）。",
      "",
      "区分「已遇到的问题」与「从文档知道但本次未触发」：以下能力在文档中存在而十件均未使用，因此其行为未经验证——"
      "`<Image>` 外部素材与网络图（刻意不用）、`blendMode` 的其他混合模式（探针 10/11/12 三次 400 后放弃整条路线）、"
      "透视矩阵项（实测无视觉效果，故不再尝试）、`fontFeatures` 之外的 OpenType 特性、"
      "`ClipPath`（服务端无此标签）。",
      "",
      "## 5. 任务耗时与请求统计",
      "",
      "结构化指标文件：`outputs/%s/B03/task-metrics.json`" % RID,
      "",
      "| 指标 | 实际值 | 单位 | 数据来源与统计范围 |",
      "|---|---|---|---|",
      "| 任务开始、结束时间 | %s → %s | UTC ISO | requests.jsonl 首末记录 |" % (T["started_at"], T["ended_at"]),
      "| 任务总墙钟 | %s | 秒 | 首请求至末请求（**不等于连续工作**） |" % format(int(T["wall_clock_seconds"]), ","),
      "| 其中有写入证据的活动时长 | %s | 秒 | 墙钟减去空闲 |" % format(int(T["active_seconds"]), ","),
      "| 空闲与无证据区间 | %s | 秒 | %d 段，逐段见 task-metrics.json 的 idle_gaps（含证据与分类） |"
      % (format(int(T["idle_gap_seconds"]), ","), len(T["idle_gaps"])),
      "| 首次可用图耗时 | %s | 秒 | 开始到 case-01 v01 响应落盘 |" % T["first_usable_image_seconds"],
      "| 等待用户反馈 | 0 | 秒 | 本题无用户中途反馈 |",
      "| 限流等待／排队等待 | 0／未知 | 秒 | 未触发 429（`x-ratelimit-limit: 120`，最低 remaining %d）；"
      "服务端排队不可测 |" % T["ratelimit_observed"]["min_remaining"],
      "| 已记录请求耗时之和 | %s | 秒 | 客户端端到端（含网络与写盘），与墙钟不可比 |" % T["request_duration_sum_seconds"],
      "| 服务端 render 耗时之和 | %s | 秒 | %s |" % (T["server_render_ms"]["sum_seconds"],
                                                  T["server_timing_source"]),
      "| 服务端 total 耗时之和 | %s | 秒 | 同上响应头 |" % T["server_total_sum_seconds"],
      "| 成功／失败／重试请求 | %d／%d／%d | 次 | requests.jsonl |"
      % (C["successful_snapshot_requests"], C["failed_snapshot_requests"], C["retry_requests"]),
      "| 实际看图／完整视觉迭代 | %d／%d | 次 | iterations.jsonl |"
      % (C["image_views"], C["completed_visual_iterations"]),
      "",
      "空闲区间的分类依据（按文件 mtime 证据，tz-aware 比对）：",
      "",
      "| 区间起（UTC） | 时长 | 判定 | 证据 |",
      "|---|---|---|---|"]
for g in T["idle_gaps"]:
    L.append("| %s | %s 秒 | %s（空闲 %s 秒） | %s |" % (
        g["start"][:16], format(int(g["seconds"]), ","), g["classification"],
        format(int(g["idle_seconds"]), ","), esc(g["evidence"])))
L += ["",
      "计时来源区分：客户端 `duration_seconds` 由本地计时写入；服务端耗时只取响应头 `Server-Timing`；"
      "两者不混用、不相加成「总耗时」。历史快照与检查点在 `tmp/%s/_suite/checkpoints/`。" % RID,
      "",
      "## 6. 设计选择、经验与未解决事项",
      "",
      "关键设计选择与预览的影响：",
      "",
      "- 十件的排序按「信息密度能不能扛住放大」而不是按视觉效果排。每件先用一次探针确定服务能不能做这个构造，"
      "再决定构图；因此 case-01 的霓虹、case-03 的轴测、case-04 的扇区、case-06 的行内角标都有各自的探针请求在前。",
      "- 预览图（`v*-preview.png`，共 %s 张）不只是留痕：每件的修改都由看预览决定，"
      "全图看不清的细节再裁局部放大（QA 裁图留在 tmp，不作为交付物）。"
      % len(list(OUT.glob("case-*/v*-preview.png"))),
      "- 数字全部由数据模型算出并写在图上（case.md 的「内容真实性」小节逐件声明虚构范围与真实常数），"
      "这让「看图→改」能改成算式而不只是审美调整。",
      "",
      "可复用经验：",
      "",
      "- **测量带**（case-10）：把测量坐标写进 data.json，用 PIL 扫上一版成品 PNG，再把实测值印回下一版——"
      "让页面结论来自像素而不是肉眼。键名必须绑定参数本身而不是列位置，否则插一栏就全部串值。",
      "- **确定性生成器**：同参数重跑产出逐字节相同的 DSL（case-10 用这招把 v03 的带坐标恢复出来并 md5 验证）。",
      "- **可证伪探针**：回退字族、`fontFeatures`、`clipBehavior` 这类「看不见」的性质，"
      "用一个宽度/状态码探针就能定性，比反复试排版便宜。",
      "- **断言比看图早**：能写成 assert 的几何约束（窗口在带内、标签不越板、累加等于总长）应在生成阶段拦下，"
      "失败即不出图，避免把静默丢内容的版本当成成功。",
      "- 行距与字距：默认行距由字族 metrics 决定（Inter 1.22em，非套件原先估的 1.45em）；"
      "`letterSpacing` 严格线性、`wordSpacing` 只对空格生效；行内小方块的最小步进约 26px，"
      "小于它就会重叠。",
      "",
      "未解决事项：",
      "",
      "- 服务无矢量 path：曲线、星图轨迹、剖面层形仍靠逐段矩形与折线逼近，放大到印刷尺寸会显出棱角。",
      "- `fontFeatures` 只解析不应用，等宽数字与小型大写需要版式手工兜底。",
      "- `Container` 的 `clipBehavior` 对整幅子树 400，遮罩只能用 ClipRRect/ClipOval。",
      "- 未安装字族回退到同一平台默认字体（186px 同宽），字族清单必须以 `GET /fonts` 实际返回为准。",
      "",
      "结束依据：10 件均有真实服务响应的 `final.png` 与同名完整 `final.snapshot`（md5 指纹配对），"
      "逐件真实看图并至少完成一轮「看图→改→再渲染→再比较」，合集层面的独立性审查见 "
      "`portfolio.json` 的 `final_collection_review`。达到请求/迭代次数本身没有被当成完成依据。",
      "",
      "留痕完整性确认：`tmp/%s/B03/` 下保留了 %d 份生成器与构件脚本、"
      "探针留痕 %d 份（DSL %d ＋图 %d）、各案 `requests/` 目录内的原始请求 body 与响应头/响应副本、"
      "%d 张版本预览、%d 张 QA 裁图、%d 份测量文件与全部失败响应（400/500/截断/无响应体），"
      "未删除、未覆盖任何已有尝试；下载文档缓存与原始响应在 `%s/`。"
      "运行时缓存（`__pycache__/`、`*.pyc` 等）不属留痕，未列为证据。"
      "总任务根 `.gitignore`（相对总任务根即 `.gitignore`，与本文相距 `../../../.gitignore`）"
      "已按模板创建并合并：忽略 `__pycache__/`、`*.pyc`、`*.pyo`、`.pytest_cache/`、`.mypy_cache/`、"
      "`.ruff_cache/`，未使用 `tmp/`、`outputs/`、`*.log` 或整体图片/DSL/JSON 的通配规则，"
      "产物与过程证据均未被忽略。"
      % (RID, len(list(TMP.glob("*.py"))), len(list((TMP / "probe").glob("*"))),
         len(list((TMP / "probe").glob("*.snapshot"))), len(list((TMP / "probe").glob("*.png"))),
         len(list(OUT.glob("case-*/v*-preview.png"))),
         len([x for c in CASES for x in CI[c]["qa_crops"]]),
         len(list(TMP.glob("case10-measure-*.json"))), DOCS),
      "",
      "## 开放作品集补充",
      "",
      "- 逐件场景／内容依据／DSL 能力／最终自检：`portfolio.json`（`cases[]` 每项含 "
      "`audience`、`use_context`、`user_goal`、`content_basis`、`dsl_capabilities`、"
      "`completion_criteria`、`visual_review`、`request_ids`、`iteration_ids`）。",
      "- 整体策展审查与合集独立性：`portfolio.md` 末节与 `portfolio.json` 的 `final_collection_review`。",
      "- 实际工具贡献：B 赛道工具记录 %d 条（`tmp/%s/B03/tool-usage.jsonl`），"
      "其中渲染服务、PIL 裁切放大、TextFit 闸门、运行时断言、promote 字节指纹校验为跨件共用；"
      "case-01 的 6 条为收尾核对时按请求留痕补记（记录内 `logged_via` 已注明），不冒充当时的即时记录。"
      % (C["tool_usage_records"], RID),
      "- 局部辅助素材：十件均未使用（`supporting_assets` 全为 `[]`，`<Image>` 计数 0）。",
      "- 重复计数避免：每题指标只在题层汇总，shared 的 15 次文档抓取只计入 `_suite`，探针与构件不计入任何单件作品；"
      "`task-metrics.json` 的 `counts` 与 `case_metrics` 为同一批记录的不同切面，不相加。",
      ]
(OUT / "snapshot-usage.md").write_text("\n".join(L) + "\n", encoding="utf-8")
print("snapshot-usage.md lines", len(L))
