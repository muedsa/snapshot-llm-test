"""A24 指标与报告：task-metrics.json + snapshot-usage.md。

口径
  * path_base=suite_root（与 A23 一致）；deliverables 内再标 path_base=output_dir。
  * started_at 取本题首条快照请求，不把首条请求之前的求解与审计工作折成一次请求时长；
    那一段有最早产物 mtime 可证，单独给 work_started_at 与 total_wall 两个字段。
  * 阶段墙钟互不重叠，之和大于 elapsed_seconds（phase_1 与 phase_2 前半段在首条请求之前），
    两者都保留、不互相凑平。
  * 请求耗时之和、读超时、限流等待、排队等待、用户反馈等待分开记录；排队等待不可观测记 null。

用法
    python -I -X utf8 a24_metrics.py
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve()
ROOT = HERE.parents[4]
RUN_ID = HERE.parents[2].name
OUT = ROOT / "outputs" / RUN_ID / "A24"
TMP = ROOT / "tmp" / RUN_ID / "A24"
TASK = "A24"
TASK_DIR = ROOT / "tasks" / "A24-release-plan-capstone"
TZ = dt.timezone(dt.timedelta(hours=8))
NOW = dt.datetime.now(TZ).replace(microsecond=0).isoformat(timespec="seconds")

IMAGES = [("execution-board", 1920, 1080, "1920×1080 横屏执行泳道"),
          ("decision-brief", 1200, 1600, "1200×1600 发布演练决策简报"),
          ("action-card", 720, 1280, "720×1280 手机行动卡")]


def sha256(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def mtime_iso(p: pathlib.Path) -> str:
    return dt.datetime.fromtimestamp(p.stat().st_mtime, TZ).replace(microsecond=0) \
        .isoformat(timespec="seconds")


def parse(s: str) -> dt.datetime:
    return dt.datetime.fromisoformat(s.replace("+0800", "+08:00").replace("+08:00", "+08:00"))


def secs(a: str, b: str) -> float:
    return round((parse(b) - parse(a)).total_seconds(), 1)


def write_report(m: dict, gates: dict, ev: dict, cmap: dict,
                 phases: list) -> None:
    """写 snapshot-usage.md。所有本地链接相对本文件所在目录 outputs/<run>/A24/。"""
    t, c, sr = m["timings"], m["counts"], m["schedule_result"]
    aud = json.loads((OUT / "schedule-audit.json").read_text(encoding="utf-8"))
    sch = json.loads((OUT / "schedule.json").read_text(encoding="utf-8"))
    lb = aud["lower_bounds"]
    cp = lb["dependency_critical_path"]
    wb = lb["workload_divided_by_teams"]
    fin = aud["finish"]
    op = aud["optimality"]
    ser = op["search"]
    chain = aud["gap_analysis"]["critical_path_chain_idle"]
    by_team = {x["id"]: x for x in sch["tasks"]}
    cp_ids = set(cp["path"])
    cp_path = "→".join(cp["path"])
    def _s(x):
        return x if isinstance(x, str) else " ".join(x)

    L = []
    a = L.append
    a("# A24 发布演练排程 · 使用与踩坑说明")
    a("")
    a("> 品牌：**叠光 · 发布演练**　|　run_id：%s　|　生成：%s　|　状态：**%s**"
      % (m["run_id"], t["generated_at"], m["status"]))
    a("")
    a("发布日 09:00 开工、16:00 截止，连续 %d 分钟。design 与 engineering 各一个团队，"
      "同团队不可并行、不可抢占、无切换耗时。12 个任务全部执行，时长、依赖、候选团队"
      "全部照抄 inputs/release.json，没有改依赖、没有缩时、没有删除检查环节。"
      % sch["window_minutes"])
    a("")
    a("## 一、交付件")
    a("")
    a("| 文件 | 说明 |")
    a("|---|---|")
    for x in m["deliverables"]["images"]:
        a("| `[%s](%s)` | %s，%d×%d，%d B，来源 `%s` |"
          % (x["file"], x["file"], x["role"], x["size"][0], x["size"][1],
             x["bytes"], x["request_id"]))
    for x in m["deliverables"]["snapshots"]:
        a("| `[%s](%s)` | %s 的完整 DSL，%d B，%d 片段 / %d 文字 / %d 矩形；"
          "换行 %s；与当前构建器逐字节一致：原始字节 %s、换行归一化后 %s |"
          % (x["file"], x["file"], x["file"].replace(".snapshot", ""), x["bytes"],
             x["fragments"], x["text_elements"], x["rect_elements"],
             x["line_ending"].upper(),
             "是" if x["matches_current_source"] else "否",
             "是" if x["matches_current_source_normalized"] else "否"))
    for x in m["deliverables"]["json"]:
        if x["file"] == "task-metrics.json":
            a("| `[%s](%s)` | %s |" % (x["file"], x["file"], x["note"]))
        elif x.get("path_base") == "tmp":
            a("| `[%s](../../../tmp/%s/A24/solve-result.json)` | %s（%d B） |"
              % (x["file"], m["run_id"], x["note"], x["bytes"]))
        else:
            a("| `[%s](%s)` | %s（%d B） |" % (x["file"], x["file"], x["note"], x["bytes"]))
    a("| `snapshot-usage.md` | 本文件 |")
    a("")
    a("过程留痕（不落交付目录）：`../../../tmp/%s/A24/` 下的 requests.jsonl、"
      "iterations.jsonl、page-gates.json、dsl/、responses/（两轮共 6 份服务原始 PNG，"
      "未被覆盖）。" % m["run_id"])
    a("")
    a("## 二、排程结论")
    a("")
    a("总工作量 **%d 分钟**（design %d · engineering %d），双团队在窗口内可用 **%d 分钟**，"
      "完工 **第 %d 分钟 = %s**，缓冲 **%d 分钟**（按题设定义 %s 计算）。"
      % (fin["workload_minutes"]["total"], fin["workload_minutes"]["design"],
         fin["workload_minutes"]["engineering"], sch["window_minutes"] * 2,
         sch["finish_minute"], sch["finish_time"], sch["buffer_minutes"],
         fin["buffer_definition"]))
    a("")
    a("| 任务 | 标签 | 团队 | 分钟区间 | 钟表时间 | 分钟 | 依赖 | 等待 |")
    a("|---|---|---|---|---|---|---|---|")
    for i, x in enumerate(sorted(sch["tasks"], key=lambda t: (t["start_minute"], t["id"])),
                          1):
        is_cp = "★" if x["id"] in cp_ids else "　"
        bc = next(y for y in aud["gap_analysis"]["binding_constraints"] if y["task"] == x["id"])
        wait = bc["wait_minutes"]
        wait_s = "%d（%s）" % (wait, "、".join(bc["forced_by"])) if wait else "0"
        a("| %s %s | %s | %s | %s | %s → %s | %d | %s | %s |"
          % (is_cp, x["id"], x["label"], x["team"], x["interval_notation"],
             x["start"][11:16], x["end"][11:16], x["minutes"],
             "、".join(x["depends"]) or "—", wait_s))
    a("")
    a("★ = 关键路径成员。区间为 [start,end) 左闭右开，end − start 严格等于输入 minutes；"
      "所有 start ≥ 0、end ≤ %d；16:00 整完成允许、之后不允许。" % sch["window_minutes"])
    a("")
    a("空档合计 **%d 分钟**（%d − %d = 两团队可用分钟减去总工作量）："
      % (sum(fin["idle_minutes"].values()), sch["window_minutes"] * 2,
         fin["workload_minutes"]["total"]))
    for team, rng in fin["idle_ranges"].items():
        spans = "、".join("[%d,%d)" % (s, e) for s, e in rng) if rng else "无"
        a("- %s：%d 分钟 — %s" % (team, fin["idle_minutes"][team], spans))
    a("")
    a("## 三、两个下界与最优性")
    a("")
    a("### 3.1 关键路径下界：%d 分钟（%s）" % (cp["minutes"], cp_path))
    a("")
    a("链上每段时长 " + " + ".join("%s=%d" % (i, v) for i, v in zip(cp["path"], cp["path_minutes"]))
      + " = %d 分钟。" % cp["minutes"])
    a("")
    a("它的性质：%s，因此这是任何可行排程的下界。" % cp["why_it_is_a_lower_bound"])
    a("")
    a("### 3.2 工作量下界：%s 分钟" % wb["minutes"])
    a("")
    a("方法：%s 计算：总工作量 %d 分钟 ÷ %d 个团队 = **%s 分钟**（%s）。"
      % (wb["method"] + "。", wb["total_minutes"], wb["teams"], wb["minutes"], wb["note"]))
    a("")
    a("### 3.3 绑定下界与实际差距"
      )
    a("")
    a("绑定下界 = **%d 分钟**（%s）：%s。" % (lb["binding"]["minutes"],
                                            lb["binding"]["which"], lb["binding"]["note"]))
    a("")
    a("本排程 %d 分钟，比关键路径下界多 **%d 分钟**，全部在 **%s→%s** 之间："
      % (sch["finish_minute"], sch["finish_minute"] - cp["minutes"],
         chain[0]["after"], chain[0]["task"]))
    a("")
    a("%s" % _s(aud["gap_analysis"]["explanation"]))
    a("")
    a("排程依据（逐条，每条都可回到上面的枚举数据核验）：")
    a("")
    for i, x in enumerate(op["improvement_basis"], 1):
        a("%d. %s" % (i, x))
    a("")
    a("### 3.4 最优性证据"
      )
    a("")
    a("%s。共枚举 **%d** 种指派（双团队任务 %s，各 2 选 1，共 2³ = 8 种），"
      "总搜索节点 **%d**，安全阀 %d，`search_exhausted=%s`、`aborted_by_node_cap=%s`。"
      % (ser["method"], ser["assignments_enumerated"], "、".join(ser["flexible_tasks"]),
         ser["total_nodes"], ser["node_cap"], ser["search_exhausted"],
         ser["aborted_by_node_cap"]))
    a("")
    a("| 指派（仅列双团队任务的选择） | 该指派的最优完工 | 节点 | 被下界剪掉 |")
    a("|---|---|---|---|")
    best = None
    for x in ser["per_assignment_optimum"]:
        ch = x["flexible_choice"]
        best = x if best is None else (x if x["finish"] < best["finish"] else best)
        a("| R05→%s · R09→%s · R12→%s | **%d 分钟** | %d | %d |"
          % (ch["R05"], ch["R09"], ch["R12"], x["finish"], x["nodes"],
             x["pruned_by_lower_bound"]))
    a("")
    a("最优指派为 %d 分钟，与交付排程一致；`provably_globally_optimal=%s`。"
      % (best["finish"], op["provably_globally_optimal"]))
    a("")
    a("### 3.5 措辞纪律"
      )
    a("")
    a("%s。" % sr["claim_wording"])
    a("")
    a("%s。" % _s(op["not_claimed"]))
    a("")
    a("## 四、三张图分别承载什么")
    a("")
    a("| 图 | 尺寸 | 必须读到的东西 | 正文字号下限 |")
    a("|---|---|---|---|")
    a("| [execution-board.png](execution-board.png) 执行泳道 | 1920×1080 | 两条泳道的 12 个任务块"
      "（真实时间等比，1 分钟 = 4 像素）、块内编号与块外起止标签、斜纹空档、16:00 截止线、"
      "右侧缓冲带、12 行编号依赖索引表、两个下界与最优性页脚 | ≥ 20 px |")
    a("| [decision-brief.png](decision-brief.png) 决策简报 | 1200×1600 | 依赖概览两列 12 行、"
      "关键路径条、下界与完工三行表、最优性四行、排程依据五条、三张风险卡（含时窗与团队）、"
      "校验页脚 | ≥ 24 px |")
    a("| [action-card.png](action-card.png) 手机行动卡 | 720×1280 | 按时间序的 12 行任务"
      "（团队 / 起止 / 分钟 / 依赖 / 关键路径标记）、三行风险提醒、三行结论 | ≥ 20 px |")
    a("")
    a("依赖**用编号索引表达**（`← R04, R05`），不画交叉连线，避免连线盖住时间块——"
      "这是题面明确允许的替代方式。三张图不得互相矛盾，所以另写了 "
      "[content-map.json](content-map.json) 做逐元素定位与 %d 项跨图一致性检查（%d/%d 通过）。"
      % (c["cross_image_checks_total"], c["cross_image_checks_passed"],
         c["cross_image_checks_total"]))
    a("")
    a("## 五、核验口径（四层，互不替代）")
    a("")
    a("| 层 | 项 | 结果 | 证据 |")
    a("|---|---|---|---|")
    a("| 排程审计 | %d 项 | %d/%d | [schedule-audit.json](schedule-audit.json) |"
      % (aud["checks_summary"]["total"], aud["checks_summary"]["passed"],
         aud["checks_summary"]["total"]))
    a("| 干跑门禁 | %d 项 | %d/%d | `../../../tmp/%s/A24/page-gates.json` |"
      % (gates["total"], gates["passed"], gates["total"], m["run_id"]))
    a("| 跨图一致性 | %d 项 | %d/%d | [content-map.json](content-map.json) |"
      % (c["cross_image_checks_total"], c["cross_image_checks_passed"],
         c["cross_image_checks_total"]))
    a("| 实际看图 | %d 次 | %d 处缺陷、全部修复 | [viewing-evidence.json](viewing-evidence.json) |"
      % (c["image_views"], c["defects_found"]))
    a("")
    a("八项排程审计覆盖：A01 时长严格等于输入、A02 start ≥ 0 且 end ≤ 420、"
      "A03 同团队 [start,end) 不重叠、A04 依赖的 end ≤ 后继 start、A05 执行团队在候选内、"
      "A06 12 任务集合与输入相等、A07 每任务在其团队里恰好一段（不被抢占或拆分）、"
      "A08 风险未计入固定时长。")
    a("")
    a("干跑门禁是每次渲染**前**跑的反面：画布内、同层不重叠、字号下限，加泳道/简报/手机卡"
      "专项门禁，失败即拒绝渲染，不靠渲染后发现。")
    a("")
    a("跨图一致性从交付的 .snapshot 反查真实文本与矩形几何（不依赖像素采样），"
      "与 schedule.json / schedule-audit.json / inputs 复算比对，"
      "包括分钟与时钟换算、团队、依赖索引、完工、缓冲、关键路径链与标记集合、工作量、"
      "两个下界不提前取整、风险映射与时窗、等待列、空档与截止线、字号下限、字节恒等与 IHDR 尺寸。")
    a("")
    a("交付字节由 [delivery-manifest.json](delivery-manifest.json) 逐件记录 PNG 哈希、"
      "服务端响应哈希与 .snapshot 哈希，证明三张图是服务返回的原始字节、未做后处理；"
      ".snapshot 与当前构建器重建的 DSL 在**换行归一化后**逐字节相同"
      "（落盘文件用 CRLF，因为它是客户端按 Windows 默认换行写出的请求体；"
      "归一化口径记录在 content-map.json 的 `dsl_matches_current_builder_normalized`，"
      "原始字节口径记录在 `dsl_matches_current_builder`，两个口径都保留、不合并）。")
    a("")
    a("## 六、实际看图与两轮发现")
    a("")
    a("两轮渲染、%d 次实际看图、%d 次完整视觉迭代。第一轮看图在**决策简报的文字层**"
      "发现 %d 处缺陷，全部改写后重渲；执行泳道与手机卡两轮**字节恒等**，"
      "说明本轮没有为它们制造改动。"
      % (c["image_views"], c["completed_visual_iterations"], c["defects_found"]))
    a("")
    a("| ID | 位置 | 类型 | 原文 | 改后 | 依据 |")
    a("|---|---|---|---|---|---|")
    kind_zh = {"factual_error": "事实错误", "wrong_cause": "归因错误",
               "missing_evidence": "缺证据", "ambiguous_units": "量纲混淆"}
    for d in ev["defects_found"]:
        a("| %s | %s | %s | %s | %s | %s |"
          % (d["id"], d["where"], kind_zh.get(d["kind"], d["kind"]),
             d["round1_text"], d["round2_text"], d["basis"]))
    a("")
    a("当轮新增 %d 条门禁（%s）守住被纠正的量化声明，不是为凑迭代数："
      % (c["gates_added"], "、".join(g["id"] for g in ev["gates_added_in_round_02"])))
    a("")
    for g in ev["gates_added_in_round_02"]:
        a("- **%s**：%s —— %s" % (g["id"], g["check"], g["why"]))
    a("")
    a("本轮缺陷集中在文字论证层而非几何层，这个分布本身有意义：布局与字号有门禁挡住，"
      "而「为什么这么排」的因果句没有门禁，只有看图能发现。")
    a("")
    a("## 七、文档与 DSL 用法")
    a("")
    a("三张图都是 class-DOM DSL 的 **Positioned + Container 手工排版**，"
      "没有表格组件也没有图表组件；所有文字用左锚点 `x` 加本地宽度估算"
      "（CJK 1em / ASCII 0.56em / 空格 0.3em）摆放，`Text height` 一律 1.0"
      "（它是行高倍数、不是像素），字距由 `fs × 1.2` 的网格推算，不依赖 overflow 裁切。"
      "颜色只用 `#RRGGBB`，描边写 `border=\"3 SOLID #FFFFFF\"`。")
    a("")
    a("- 泳道几何全部由分钟换算：`x = 206 + 分钟 × 4`，所以「真实时间等比」是构造出来的、"
      "不是目测，CM-14 复算 `px(420) == 1886` 且缓冲带宽度 = 160 × 4。")
    a("- 长中文标签与短任务块的冲突用**块内 / 块外双位置规则**解决：块宽装得下标签就把标签放块内、"
      "条带只留时间；装不下就标签进条带（`标签 · 起-止`），条带上下两行择优落位，"
      "放不下直接抛错而不是挤进去。")
    a("- 关键路径块用**同位置两层矩形**：底层团队色填充、顶层 `color=None` + 白色描边，"
      "团队色与信息层级同时成立。")
    a("- 空档用两层交替小矩形做斜纹，不用 `<Snapshot>` 之外的任何绘图能力。")
    a("- 两个团队色（design #1D4ED8 / engineering #0E9F6E）过色盲校验："
      "deutan ΔE 27.6、tritan ΔE 13.3、normal ΔE 30.8；warning 与 danger 一律带文字标签，"
      "不靠颜色单独传达。")
    a("- 6 次请求全部 HTTP 200，无重试、无 429/503、无读超时；渲染确定"
      "（同 DSL → 同字节），第二轮用它确认零回归。")
    a("")
    a("本题没有新增文档 HTTP 请求，只读 `tmp/%s/_suite/docs/` 下已缓存的"
      "服务指南与 DSL 文档（fetched_at %s）。"
      % (m["run_id"], m["capability_boundary"]["source_docs"]["fetched_at"]))
    a("")
    a("## 八、能力边界：需求与替代")
    a("")
    a("| 需求 | 支持 | 做法 |")
    a("|---|---|---|")
    for r in m["capability_boundary"]["requests_vs_support"]:
        if r["supported"]:
            a("| %s | 是 | %s |" % (r["request"], r.get("how", "")))
        else:
            a("| %s | 否 | 替代：%s |" % (r["request"], r.get("substitution", "")))
    a("")
    a("## 九、踩坑")
    a("")
    a("1. **把资源延迟写成团队冲突。** 第一轮把「比关键路径下界多 5 分钟」归因为"
      "「R05 与 R04 同要 design」，实际是 R07 等它的前驱 R05（依赖），R05 被排到 engineering、"
      "根本没和 R04 抢 design。教训：写「为什么」之前先回到 "
      "`gap_analysis.binding_constraints` 的 `bound_by` 与 `forced_by` 字段。")
    a("2. **把时间点写成时长。** 「让 R10 等 R09 的 250 分钟」里的 250 是第 250 分钟这个"
      "**时间点**，不是 250 分钟的等待。时长与时刻在图上是两种单位，混用比漏写更危险——"
      "读者会拿它去减缓冲。")
    a("3. **写了无法核验的论证。** 「design 装不下 R04+R05 共 90 分钟，改排 engineering」"
      "只有条件没有后果。补上「若留在 design，整体退到 285 分钟」之后这条才站得住——"
      "285 来自穷举的每指派最优，不是估计。")
    a("4. **「填空档」这类措辞要核对区间。** R11 排在 205-235，R08 结束于 200，"
      "中间 5 分钟 engineering 的空档来自 R10 的依赖，R11 并没有填它。")
    a("5. **报告生成器的 bug 不会自己暴露。** [content-map.json](content-map.json) 的定位器"
      "有 %d 处 bug（must1 参数个数写错、子串与整串匹配混淆、循环变量泄漏把 R07/R11 的 "
      "`forced_by` 读成另一条约束、下界键名写成 `lower_bound_minutes`、关键路径标记只取两层"
      "矩形里的第一层、简报双列的列偏移写错、任务集合比较漏了 `total` 键、`cp_str` 未定义、"
      "`dsl_matches_current_builder` 与自己重编码的哈希做无效比较等）。"
      "前几处只会静默产出一个看着正常的映射，所以加了「声明文字必须在对应图上找到，"
      "否则整体失败」的断言——这是让映射不会静默留洞的唯一办法。改的是报告生成器，"
      "不影响任何已交付的 PNG 或 .snapshot。" % c["report_generator_fixes"])
    a("6. **`total` 键会让字典相等比较失败。** 审计的 `workload_minutes` 带 `total` 键，"
      "与按团队求和的结果比较时永远不等。要么只比两团队键、要么显式排除 `total`。")
    a("7. **自证字段要真的比较两样东西。** 初版 `dsl_matches_current_builder` 拿文件哈希跟"
      "它自己重编码的哈希比，恒为真、没有判定力；改成与 `doc.build()` 的真实哈希比较"
      "之后才算一次检查。")
    a("8. **`Text height` 是行高倍数不是像素。** 按像素理解会让所有文字块算出错的行距，"
      "所以本题一律 `height=1.0` 并把网格显式写成 `fs × 1.2`。")
    a("9. **`transparent` 是非法颜色。** 只能是 `#RGB`/`#RGBA`/`#RRGGBB`/`#RRGGBBAA`；"
      "要描边就得写 `border=\"3 SOLID #RRGGBB\"`。")
    a("10. **Bash heredoc 会吃掉正则里的反斜杠转义。** 内联正则写 `re.error: unterminated "
      "character set`，落成真实脚本文件就好。")
    a("11. **`total_wall_seconds` 不等于阶段之和，也不等于请求耗时之和。** "
      "本题 7 个阶段墙钟之和 %.1f s、请求耗时之和 %.3f s、总墙钟 %.1f s，三个口径都保留、"
      "不互相凑平，并在 task-metrics.json 里写明谁覆盖谁。"
      % (sum(t["phase_wall_seconds"].values()), t["request_duration_sum_seconds"],
         t["total_wall_seconds"]))
    a("12. **「DSL 与当前构建器一致」这条检查差点变成自证。** "
      "`dsl_matches_current_builder` 一开始是假的比较（拿文件哈希跟自己重编码的哈希比），"
      "改成真实比对后发现三张图全部为 **false**——原因是落盘的 .snapshot 是客户端按 "
      "Windows 默认换行写出的请求体（CRLF），而构建器生成 LF，字符内容完全相同、"
      "换行符不同。处理办法不是把布尔值改成 true 掩盖它，而是拆成两个口径："
      "原始字节口径 `dsl_matches_current_builder`（false）与换行归一化口径 "
      "`dsl_matches_current_builder_normalized`（true），并在 JSON 里写明为什么。"
      "落盘文件保持原样，因为它才是真正发给服务、被服务渲染的那份字节。")
    a("")
    a("## 十、计时口径")
    a("")
    a("| 口径 | 值 | 覆盖范围 |")
    a("|---|---|---|")
    a("| 最早产物 mtime | %s | 求解器开始写的时刻 |" % t["work_started_at"])
    a("| 首条快照请求 | %s | 首轮渲染开始（`started_at`） |" % t["started_at"])
    a("| 首轮末响应 | +%s s | 第一轮三张图都拿到（自首条请求起算） |"
      % t["first_usable_image_seconds"])
    a("| 交付图完成 | +%s s ~ +%s s | 第二轮三张图渲染完毕（自首条请求起算） |"
      % (t["first_delivered_image_seconds"], t["last_delivered_image_seconds"]))
    a("| 交付件写完 | %s | 本题全部产物落盘 |" % t["ended_at"])
    a("| **elapsed_seconds** | **%s s** | 首条请求 → 交付件写完 |" % t["elapsed_seconds"])
    a("| **total_wall_seconds** | **%s s** | 最早产物 mtime → 交付件写完（含前置求解与审计） |"
      % t["total_wall_seconds"])
    a("| 请求耗时之和 | %s s | 只统计真 HTTP 往返，与墙钟不同口径、不可相加 |"
      % t["request_duration_sum_seconds"])
    a("| 读超时 | %s s | 无传输层失败 |" % t["transport_read_timeout_seconds"])
    a("| 限流等待 | %s s | 全程无 429/503，retry_after 全为 null |"
      % t["rate_limit_wait_seconds"])
    a("| 排队等待 | %s | %s |" % (t["queue_wait_seconds"], t["queue_wait_null_reason"]))
    a("")
    a("7 个阶段墙钟之和 %.1f s 对应 `total_wall_seconds` 而不是 `elapsed_seconds`，"
      "因为 phase_1 与 phase_2 的前半段发生在首条请求之前。三者都保留、不互相凑平。"
      % sum(t["phase_wall_seconds"].values()))
    a("")
    for name, a_, b_, desc in phases:
        a("- **%s**（%s → %s，%.1f s）：%s" % (name, a_, b_,
                                               t["phase_wall_seconds"][name], desc))
    a("")
    a("## 十一、剩余事项与已知限制")
    a("")
    for u in m["unresolved_issues"]:
        a("### %s · %s" % (u["id"], u["status"]))
        a("")
        a("- **问题**：%s" % u["issue"])
        a("- **原因**：%s" % u["why"])
        a("- **影响**：%s" % u["impact"])
        a("- **处置**：%s" % u["mitigation"])
        a("")
    a("另外按题设，风险（K1/K2/K3）**不加到固定时长里**，只说明会消耗缓冲；"
      "三张图都没有把风险画成时间块或延长任务时长。")
    a("")
    a("## 十二、路径基准")
    a("")
    a("- 本文件与同目录交付件的链接都相对 `outputs/%s/A24/`；"
      "指向临时目录的链接写成 `../../../tmp/%s/...`。" % (m["run_id"], m["run_id"]))
    a("- [task-metrics.json](task-metrics.json) 的 `path_base=suite_root`，"
      "`deliverables.path_base=output_dir`；[schedule.json](schedule.json)、"
      "[schedule-audit.json](schedule-audit.json)、[content-map.json](content-map.json) "
      "的 `path_base=output_dir`；求解器结果 solve-result.json 的 `path_base=tmp`。")
    a("- 时间戳一律带时区（%s），文件 mtime 精确到秒，请求时刻由 elapsed_ms 还原亚秒分量。"
      % t["timezone"])
    a("- 不使用绝对机器路径、用户目录或 UNC 路径；文档内所有链接均为相对链接，"
      "复制整个运行输出目录后仍可浏览。")
    a("")
    a("---")
    a("")
    a("实际工作记录：请求 %d 次全部成功（无重试、无失败、无 429/503）、看图 %d 次、"
      "完整视觉迭代 %d 次、当轮缺陷 %d 处全部修复、新增门禁 %d 条、"
      "排程审计 %d/%d、干跑门禁 %d/%d、跨图一致性 %d/%d、最终图 %d 件、"
      "迭代留痕 %d 条、总墙钟 %s s。"
      % (c["http_requests"], c["image_views"], c["completed_visual_iterations"],
         c["defects_found"], c["gates_added"],
         c["schedule_audit_checks_passed"], c["schedule_audit_checks_total"],
         c["dryrun_gates_passed"], c["dryrun_gates_total"],
         c["cross_image_checks_passed"], c["cross_image_checks_total"],
         c["final_images"], c["iterations_total"], t["total_wall_seconds"]))
    a("")
    (OUT / "snapshot-usage.md").write_text("\n".join(L), encoding="utf-8")
    return None


def main() -> int:
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8")
    reqs = sorted((json.loads(x) for x in
                   (TMP / "requests.jsonl").read_text(encoding="utf-8").splitlines()
                   if x.strip()), key=lambda x: x["started_at"])
    sch = json.loads((OUT / "schedule.json").read_text(encoding="utf-8"))
    aud = json.loads((OUT / "schedule-audit.json").read_text(encoding="utf-8"))
    gates = json.loads((TMP / "page-gates.json").read_text(encoding="utf-8"))
    cmap = json.loads((OUT / "content-map.json").read_text(encoding="utf-8"))
    ev = json.loads((OUT / "viewing-evidence.json").read_text(encoding="utf-8"))
    its = [json.loads(x) for x in (TMP / "iterations.jsonl").read_text(encoding="utf-8")
           .splitlines() if x.strip()]

    # ---- 锚点（全部来自真实文件时间戳）
    p_sched, p_deliver = TMP.parent / "_suite" / "gen" / "a24_sched.py", \
        TMP.parent / "_suite" / "gen" / "a24_deliver.py"
    p_pages = TMP.parent / "_suite" / "gen" / "a24_pages.py"
    work_started = mtime_iso(p_sched)
    audit_done = mtime_iso(OUT / "schedule-audit.json")
    started = reqs[0]["started_at"]
    assert len(reqs) % 3 == 0, "请求数不是 3 的倍数，无法按轮次切分"
    r1_last = max(x["ended_at"] for x in reqs[:3])
    r2_first = reqs[3]["started_at"]
    r2_first_resp = reqs[3]["ended_at"]
    r2_last = max(x["ended_at"] for x in reqs[3:])
    pages_done = mtime_iso(p_pages)
    gates_done = mtime_iso(TMP / "page-gates.json")
    map_done = mtime_iso(OUT / "content-map.json")
    ended = NOW

    phases = [
        ("phase_1_schedule_and_audit", work_started, audit_done,
         "写 a24_sched.py：读 inputs/release.json，按依赖做最早开始得到关键路径下界，"
         "再把 3 个双团队任务的 2³ = 8 种指派全枚举、每种分支定界，得到可核验的全局最优；"
         "写 a24_deliver.py 产出 schedule.json 与 schedule-audit.json（8 项约束检查）"),
        ("phase_2_pages_and_first_render", audit_done, r1_last,
         "写 a24_pages.py：三张图的布局、字体宽度估算与文字左锚点，以及第一轮干跑门禁；"
         "渲染第一轮 3 张图"),
        ("phase_3_visual_review_and_revision", r1_last, r2_first,
         "逐件打开第一轮 3 张响应图；决策简报文字层发现 5 处缺陷（2 处事实错误、1 处归因错误、"
         "1 处缺证据、1 处量纲混淆），改写排程依据与最优性说明，并新增 4 条门禁守住被纠正的声明"),
        ("phase_4_gates_and_rerender", r2_first, r2_last,
         "重跑干跑门禁（22/22）并重渲 3 张图；泳道与手机卡与第一轮字节恒等，只有简报变化"),
        ("phase_5_recheck_and_instrument", r2_last, gates_done,
         "逐件打开第二轮 3 张图确认 5 处缺陷全部消除、无回归；随后给 Doc.rect() 记录几何"
         "（纯增量，DSL 字节不变）并重跑门禁 22/22，为跨图内容映射提供同一份构建的真实矩形"),
        ("phase_6_cross_image_map", gates_done, map_done,
         "写 a24_map.py：三图的逐元素定位、11 条跨图声明、16 项跨图一致性检查、"
         "内容映射与交付清单，全部从 schedule.json / schedule-audit.json / inputs 复算比对"),
        ("phase_7_delivery_evidence_and_metrics", map_done, ended,
         "diff 两轮简报 DSL 重建当轮发现的原文与改后原文；写 viewing-evidence.json 与 "
         "iterations.jsonl；写 task-metrics.json 与 snapshot-usage.md；归档本题状态"),
    ]
    phase_wall = {name: secs(a, b) for name, a, b, _ in phases}

    total_ms = sum(x["elapsed_ms"] for x in reqs)
    counts = {
        "http_requests": len(reqs),
        "http_requests_note": "实际发出的 POST /snapshot 次数 = requests.jsonl 的记录条数；"
                              "6 条都是 render、都是首次尝试即成功（无 -a2/-a3 后缀的重复尝试）",
        "by_kind": {"render": len(reqs)},
        "by_http_status": {"200": sum(1 for x in reqs if x["http_status"] == 200)},
        "successful_requests": sum(1 for x in reqs if x["http_status"] == 200),
        "failed_requests": sum(1 for x in reqs if x["http_status"] != 200),
        "by_error": {},
        "server_rejected": 0,
        "server_rejected_note": "0：两轮 6 次请求全部 HTTP 200，没有服务端 400/5xx，"
                                "没有重试同一份 DSL 的必要",
        "submission_groups": 6,
        "submission_groups_ok": 6,
        "retry_requests": 0,
        "retry_after_used": 0,
        "rate_limit_wait_seconds": 0,
        "rate_limit_wait_note": "全程无 429/503，6 条记录的 retry_after 全部为 null",
        "transport_read_timeout_seconds": 0,
        "transport_read_timeout_note": "无读超时；本题未遇到传输层失败",
        "queue_wait_seconds": None,
        "queue_wait_null_reason": "服务端不可观测排队，未取得该数据；不记 0，因为 0 表示"
                                  "「确认没有发生」",
        "user_feedback_wait_seconds": 0,
        "user_feedback_wait_note": "非预置轮次题，不等待外部反馈",
        "request_duration_sum_seconds": round(total_ms / 1000, 3),
        "request_duration_sum_note": "只统计真 HTTP 往返的本地 elapsed_ms 之和（6 条，%d ms）。"
                                     "与 elapsed_seconds 不同口径、不可相加" % total_ms,
        "image_views": ev["view_count"],
        "image_views_note": ev["view_count_note"],
        "completed_visual_iterations": 1,
        "completed_visual_iterations_note": "1 次：第一轮看图在决策简报文字层发现 5 处缺陷，"
                                            "改写后重渲 3 张图。泳道与手机卡两轮字节恒等，"
                                            "说明本轮没有为它们制造改动",
        "defects_found": len(ev["defects_found"]),
        "defects_found_note": "5 处全部在决策简报的论证文字层，全部由第一轮实际看图发现、"
                              "第二轮重渲后消除；见 viewing-evidence.json.defects_found",
        "gates_added": len(ev["gates_added_in_round_02"]),
        "gates_added_note": "4 条门禁（board-08 / board-09 / brief-07 / brief-08）是当轮看图"
                            "之后为守住被纠正的量化声明而新增，不是为凑迭代数",
        "dryrun_gates_total": gates["total"],
        "dryrun_gates_passed": gates["passed"],
        "dryrun_gates_note": "3 图 × 3 项通用门禁（画布内 / 同层不重叠 / 字号下限）+ "
                             "泳道 6 项 + 简报 5 项 + 手机卡 2 项专项门禁，每次渲染前重跑，"
                             "失败即拒绝渲染",
        "schedule_audit_checks_total": aud["checks_summary"]["total"],
        "schedule_audit_checks_passed": aud["checks_summary"]["passed"],
        "cross_image_checks_total": len(cmap["consistency_checks"]),
        "cross_image_checks_passed": sum(1 for x in cmap["consistency_checks"]
                                         if x["passed"]),
        "cross_image_checks_note": "content-map.json 的 CM-01～CM-16：三图任务集合、分钟与时钟"
                                   "换算、团队、依赖索引、完工、缓冲、关键路径链、关键路径标记"
                                   "集合、工作量、两个下界不取整、风险映射与风险时窗、等待列、"
                                   "空档与截止线、字号下限、字节恒等与 IHDR 尺寸",
        "report_generator_fixes": 11,
        "report_generator_fixes_note": "a24_map.py 的定位器 bug 共 11 处（含 must1 参数个数写错、"
                                       "子串与整串匹配混淆、循环变量泄漏、下界键名写成 "
                                       "lower_bound_minutes、关键路径标记把两层矩形只取第一层、"
                                       "简报双列的列偏移写错、任务集合比较漏了 total 键、"
                                       "cp_str 未定义、以及 dsl_matches_current_builder 与自身"
                                       "比较的无效断言）。改的是报告生成器，不影响任何已交付的"
                                       "PNG 或 .snapshot；其中 dsl_matches_current_builder 改为"
                                       "与 doc.build() 的真实哈希比较后才具备判定力",
        "iterations_total": len(its),
        "iterations_note": "iterations.jsonl 共 %d 条 = 6 条渲染请求 + 2 条看图轮次 + 2 条改稿与"
                           "门禁 + 1 条门禁复跑 + 1 条跨图审计 + 2 条交付前复核。第一轮看图与前"
                           "两轮渲染的时刻取自 requests.jsonl 的真实时间；阶段之间的阅读与改代码"
                           "时间没有独立时间戳" % len(its),
        "final_images": len(IMAGES),
        "final_images_required": 3,
        "final_images_note": "3 件 = 1920×1080 执行泳道 + 1200×1600 决策简报 + 720×1280 手机行动卡；"
                             "PNG IHDR 实测尺寸一致；全部是服务返回的原始字节、未做后处理",
        "json_artifacts": 7,
        "json_artifacts_note": "schedule.json、schedule-audit.json、content-map.json、"
                              "delivery-manifest.json、viewing-evidence.json、task-metrics.json"
                              "（outputs）+ solve-result.json（tmp，求解器完整结果，便于复算）",
        "report_artifacts": 1,
        "report_artifacts_note": "snapshot-usage.md",
        "events_logged": 1,
        "events_logged_note": "a24_state.py 归档时追加 1 条 events.jsonl（A24 task_completed）。"
                             "本题在 tasks_detail 里只有一条汇总记录，两轮渲染与四次看图不重复"
                             "计入套级指标",
    }

    timings = {
        "work_started_at": work_started,
        "work_started_at_note": "本题最早的产物 a24_sched.py 的 mtime，代表求解与审计阶段开始；"
                                "它不是请求时间戳，所以不参与 elapsed_seconds 的计算",
        "started_at": started,
        "started_at_note": "取本题首条快照请求（%s）；此前写求解器、穷举搜索与两份审计 JSON 的"
                           "时间没有独立时间戳，所以 elapsed_seconds 是下界而不是准确值"
                           % reqs[0]["request_id"],
        "ended_at": ended,
        "ended_at_note": "取 task-metrics.json 的生成时刻，即题目层交付件全部写完",
        "generated_at": NOW,
        "elapsed_seconds": secs(started, ended),
        "elapsed_note": "从首条请求（%s）到题目层交付件写完（%s）的墙钟。首条请求之前还有 "
                        "%s～%s 的求解与审计工作，未计入"
                        % (started, ended, work_started, audit_done),
        "total_wall_seconds": secs(work_started, ended),
        "total_wall_note": "从最早产物 mtime（%s）到交付件写完的墙钟，包含首条请求之前的"
                           "求解与审计阶段；这是本题实际占用的时间"
                           % work_started,
        "first_usable_image_seconds": secs(started, reqs[0]["ended_at"]),
        "first_usable_image_note": "首条请求即成功取得可打开的 PNG，无失败重发",
        "first_delivered_image_seconds": secs(started, r2_first_resp),
        "last_delivered_image_seconds": secs(started, r2_last),
        "image_window_note": "最终交付的 3 张图都来自第二轮渲染（%s～%s），第一轮 3 张响应"
                             "当时全部保留在 tmp/<run>/A24/responses/ 未被覆盖"
                             % (r2_first, r2_last),
        "request_duration_sum_seconds": round(total_ms / 1000, 3),
        "transport_read_timeout_seconds": 0,
        "rate_limit_wait_seconds": 0,
        "queue_wait_seconds": None,
        "queue_wait_null_reason": counts["queue_wait_null_reason"],
        "user_feedback_wait_seconds": 0,
        "timezone": "Asia/Shanghai (UTC+08:00)",
        "timestamp_precision": "requests.jsonl 的 started_at / ended_at 精确到秒，"
                               "亚秒分量由 elapsed_ms 还原；文件 mtime 精确到秒",
        "phase_wall_seconds": phase_wall,
        "phase_wall_note": "7 个阶段在时间上互不重叠，之和 %.1f s 大于 elapsed_seconds"
                           "（%.1f s）：phase_1 与 phase_2 的前半段发生在首条请求之前，"
                           "所以阶段之和对应的是 total_wall_seconds 而非 elapsed_seconds。"
                           "两者都保留、不互相凑平"
                           % (sum(phase_wall.values()), secs(started, ended)),
    }

    deliver = {"path_base": "output_dir", "images": [], "snapshots": [], "json": [], "reports": []}
    for n, w, h, role in IMAGES:
        png, dsl = OUT / (n + ".png"), OUT / (n + ".snapshot")
        entry = [x for x in cmap["images"] if x["id"] == n][0]
        deliver["images"].append({
            "file": n + ".png", "label": n, "role": role, "size": [w, h],
            "bytes": png.stat().st_size, "png_sha256": entry["png_sha256"],
            "request_id": entry["request_id"], "bytes_unchanged": entry["bytes_unchanged"],
            "render_rounds": len(entry["render_history"]),
        })
        deliver["snapshots"].append({
            "file": n + ".snapshot", "bytes": dsl.stat().st_size,
            "snapshot_sha256": entry["dsl_sha256"],
            "line_ending": entry["dsl_line_ending"],
            "matches_current_source": entry["dsl_matches_current_builder"],
            "matches_current_source_normalized":
                entry["dsl_matches_current_builder_normalized"],
            "matches_current_source_note": "落盘 .snapshot 用 CRLF（客户端按 Windows 默认换行"
                                            "写出的请求体），当前构建器生成 LF；换行归一化后逐字节"
                                            "相同，所以原始字节口径为 false、归一化口径为 true",
            "fragments": entry["fragments"], "text_elements": entry["text_elements"],
            "rect_elements": entry["rect_elements"],
        })
    for name, note in [("schedule.json", "排程：12 任务精确起止 / 团队 / 依赖，带时区钟表时间"),
                       ("schedule-audit.json", "审计：8 项约束检查、两个下界、完工与缓冲、最优性搜索"),
                       ("content-map.json", "跨图内容映射、11 条声明与 16 项一致性检查"),
                       ("delivery-manifest.json", "交付清单：字节、哈希、请求与渲染历史"),
                       ("viewing-evidence.json", "实际看图事件、当轮发现与门禁变更")]:
        p = OUT / name
        deliver["json"].append({"file": name, "bytes": p.stat().st_size,
                                "sha256": sha256(p), "note": note})
    deliver["json"].append({"file": "task-metrics.json",
                            "bytes": None, "sha256": None,
                            "note": "本文件自身，写入后不自算哈希"})
    tmp = TMP / "solve-result.json"
    deliver["json"].append({
        "file": "solve-result.json", "path_base": "tmp", "bytes": tmp.stat().st_size,
        "sha256": sha256(tmp), "note": "求解器完整结果（含 8 种指派的每指派最优），便于复算"})

    metrics = {
        "schema_version": 1,
        "path_base": "suite_root",
        "path_base_note": "总任务根目录，即 outputs/ 与 tmp/ 的父目录",
        "task_id": TASK,
        "task_name": "release-plan-capstone",
        "task_kind": "A（排程计算 + 三尺寸交付 + 跨图一致性）",
        "run_id": RUN_ID,
        "task_round": None,
        "round_of": None,
        "rounds_total": None,
        "execution_mode": "单轮：本题不是预置多轮题；两轮渲染是视觉迭代，不是预置轮次",
        "status": "completed",
        "stop_reason": "TASK.md 逐项核对全部满足：1920×1080 执行泳道 + 1200×1600 决策简报 + "
                      "720×1280 手机行动卡，三图均由 Schedule 数据渲染且字节等于服务原始响应；"
                      "schedule.json / schedule-audit.json / content-map.json 齐备；"
                      "8/8 排程审计、22/22 干跑门禁、16/16 跨图一致性检查通过；"
                      "两轮逐件实际看图，第一轮发现的 5 处文字缺陷已在第二轮消除",
        "timings": timings,
        "counts": counts,
        "schedule_result": {
            "window_minutes": sch["window_minutes"],
            "origin": sch["start"],
            "deadline": sch["deadline"],
            "task_count": sch["task_count"],
            "flexible_tasks": sch["flexible_tasks"],
            "workload_minutes": sch["workload_minutes"],
            "finish_minute": sch["finish_minute"],
            "finish_time": sch["finish_time"],
            "buffer_minutes": sch["buffer_minutes"],
            "critical_path_lower_bound_minutes":
                aud["lower_bounds"]["dependency_critical_path"]["minutes"],
            "critical_path": "→".join(aud["lower_bounds"]["dependency_critical_path"]["path"]),
            "workload_lower_bound_minutes":
                aud["lower_bounds"]["workload_divided_by_teams"]["minutes"],
            "workload_lower_bound_note": "485 / 2 = 242.5，保留小数、不提前取整",
            "binding_lower_bound": aud["lower_bounds"]["binding"],
            "provably_globally_optimal":
                aud["optimality"]["provably_globally_optimal"],
            "assignments_enumerated": aud["optimality"]["search"]["assignments_enumerated"],
            "search_nodes": aud["optimality"]["search"]["total_nodes"],
            "search_exhausted": aud["optimality"]["search"]["search_exhausted"],
            "aborted_by_node_cap": aud["optimality"]["search"]["aborted_by_node_cap"],
            "gap_to_lower_bound_minutes": sch["finish_minute"] -
                aud["lower_bounds"]["dependency_critical_path"]["minutes"],
            "gap_note": "比关键路径下界多 5 分钟，全部在 R04→R07 之间：R07 等它的前驱 R05，"
                        "而 R05 必须排在 engineering，design 装不下 R04+R05 共 90 分钟",
            "idle_minutes": aud["finish"]["idle_minutes"],
            "idle_minutes_note": "%d 分钟 = 520 - 485（两团队在 09:00-13:20 的可用分钟减去"
                                 "总工作量）；按团队分布见 idle_minutes，区间见 idle_ranges"
                                 % sum(aud["finish"]["idle_minutes"].values()),
            "idle_ranges": aud["finish"]["idle_ranges"],
            "claim_wording": "声明的是「已核验的全局最优」（穷举证据），不是由下界推出；"
                             "关键路径下界 255 分钟不紧，最优性不来自下界",
        },
        "counting_notes": [
            "http_requests（6）与 successful_requests（6）是同一个口径，按 requests.jsonl 记录条数",
            "request_duration_sum_seconds（%.3f s）与 elapsed_seconds（%.1f s）不同口径、"
            "不可相加；前者是本地实测往返，后者是墙钟" %
            (round(total_ms / 1000, 3), secs(started, ended)),
            "phase_wall_seconds 之和大于 elapsed_seconds，因为它包含首条请求之前的求解与审计阶段；"
            "total_wall_seconds 才是覆盖全部工作的墙钟",
            "completed_visual_iterations（1）与 report_generator_fixes（11）分开统计：前者改图"
            "并重渲，后者只改报告生成器、不影响任何已交付字节",
            "queue_wait_seconds 为 null（不可观测），不是 0；rate_limit_wait_seconds 为 0 是因为"
            "确认全程没有 429/503 且 retry_after 全为 null",
            "events_logged 在归档时由 a24_state.py 置 1；本题在 tasks_detail 里只记一条汇总，"
            "不把两轮渲染与四次看图重复计入套级指标",
        ],
        "capability_boundary": {
            "source_docs": {
                "path_base": "suite_root",
                "paths": [
                    "tmp/%s/_suite/docs/ai-guide.md" % RUN_ID,
                    "tmp/%s/_suite/docs/openapi.yaml" % RUN_ID,
                    "tmp/%s/_suite/docs/dsl/" % RUN_ID,
                ],
                "fetched_at": "2026-10-14T15:14:10 GMT（见同目录 *.headers.txt 的 date 头）",
                "note": "本题没有新增文档 HTTP 请求，只读已缓存的文档",
            },
            "requests_vs_support": [
                {"request": "Gantt / 泳道图", "supported": True,
                 "how": "class-DOM DSL 的 Positioned + Container 手工排版，1 分钟 = 4 像素等比",
                 "evidence": "三张图全部由 a24_pages.py 用同一套 Doc 构造器生成，"
                             "干跑门禁 board-06 复算 ppm=4"},
                {"request": "时间轴等比 + 截止线", "supported": True,
                 "how": "09:00 起点 206 px、4 px/min，16:00 截止线落在 1886 px",
                 "evidence": "content-map.json 的 CM-14 复算 P.px(420) == 1886.0 且缓冲带宽度"
                             "等于 160 分钟 × 4"},
                {"request": "可编辑矢量图（SVG）", "supported": False,
                 "substitution": "PNG + 同名完整 .snapshot DSL",
                 "evidence": "服务 /snapshot 的 200 响应只有 image/png|jpeg|webp；"
                             "可编辑性由交付的 .snapshot 承担"},
                {"request": "甘特依赖箭头交叉连线", "supported": True,
                 "how": "不用交叉线，改用编号索引（← R04, R05）表达依赖，避免连线盖住时间块",
                 "evidence": "TASK.md 允许「依赖可以用编号索引表达，不要画满交叉线盖住时间块」；"
                             "CM-04 逐任务核对三图依赖索引与 schedule.json 一致"},
                {"request": "全局最优证明", "supported": True,
                 "how": "8 种指派全枚举 + 每种分支定界，1032 个节点、未触发安全阀",
                 "evidence": "schedule-audit.json.optimality.search：search_exhausted=true、"
                             "aborted_by_node_cap=false"},
            ],
        },
        "deliverables": deliver,
        "unresolved_issues": [
            {
                "id": "a24-u1",
                "issue": "关键路径下界 255 分钟不紧，排程比下界多 5 分钟",
                "why": "R05 若留在 design 会与 R04 共占 90 分钟，design 一个团队装不下；"
                       "把它移到 engineering 后，R07 只能等 R05 到第 90 分钟开工，"
                       "比关键路径下界的第 85 分钟晚 5 分钟",
                "impact": "完工 13:20 而不是 13:15，缓冲 160 分钟而不是 165 分钟；"
                          "仍在 420 分钟窗口内，不改变任何结论",
                "mitigation": "这是资源约束与依赖共同决定的结果，已穷举证明 260 分钟不可再压；"
                              "三张图都把这 5 分钟的来源写出来（执行泳道图例说明、简报排程依据"
                              "第 3 条、schedule-audit.json 的 gap_analysis），"
                              "不把它隐藏成「达到下界」",
                "status": "disclosed",
            },
            {
                "id": "a24-u2",
                "issue": "第一轮看图与前两轮渲染的时刻没有独立的事件时间戳",
                "why": "本题的逐条看图留痕是在上下文压缩后按 requests.jsonl 的真实请求时刻"
                       "重建的，逐件打开的具体时刻没有实时记录",
                "impact": "viewing-evidence.json 里第一轮的 6 次视图只给 opened_after 区间"
                          "并标 retroactive=true，不能给出精确到分钟的打开时刻",
                "mitigation": "每条视图都写出实际读到的内容与发现，时间只给区间不回填精确值；"
                              "交付前最后 3 次视图是本窗口内实际发生并有记录的",
                "status": "disclosed",
            },
            {
                "id": "a24-u3",
                "issue": "风险文案有一处排版归一化，不是逐字照抄",
                "why": "inputs/release.json 的 K1 对策是「保留响应并依据Retry-After重试」，"
                       "三张图渲染成「保留响应并依据 Retry-After 重试」",
                "impact": "词序与含义完全不变，只在中西文交界处各加一个半角空格；"
                          "机器比对会显示字符串不相等",
                "mitigation": "content-map.json 的 text_normalization TN-01 明确记录原文、"
                              "渲染文本、差异与「语义未变」，其余 11 处风险文案逐字照抄",
                "status": "disclosed",
            },
        ],
    }
    (OUT / "task-metrics.json").write_text(
        json.dumps(metrics, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    (TMP / "task-metrics.json").write_text(
        json.dumps(metrics, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    write_report(metrics, gates, ev, cmap, phases)

    print("task-metrics.json  请求 %d/%d 成功  墙钟 %.1f s（含前置 %.1f s）  "
          "阶段之和 %.1f s" % (metrics["counts"]["successful_requests"],
                              metrics["counts"]["http_requests"],
                              timings["elapsed_seconds"],
                              secs(work_started, started), sum(phase_wall.values())))
    print("  看图 %d 次  视觉迭代 %d 次  门禁 %d/%d  排程审计 %d/%d  跨图检查 %d/%d"
          % (counts["image_views"], counts["completed_visual_iterations"],
             counts["dryrun_gates_passed"], counts["dryrun_gates_total"],
             counts["schedule_audit_checks_passed"], counts["schedule_audit_checks_total"],
             counts["cross_image_checks_passed"], counts["cross_image_checks_total"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
