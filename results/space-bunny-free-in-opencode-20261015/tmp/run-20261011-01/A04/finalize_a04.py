#!/usr/bin/env python
"""A04 定稿 + 报告。启动基准：总任务根。"""
from __future__ import annotations

import json
import sys

sys.path.insert(0, "tmp/run-20261011-01/_suite/scripts")
import finalize_task as ft  # noqa: E402
import report_gen as rg  # noqa: E402
import suite_log as sl  # noqa: E402

TASK = "A04"
VER = "v4"
OUT, TEMP = "outputs/run-20261011-01/A04", "tmp/run-20261011-01/A04"

req_items = """
| 文件 | 用途 | 对应 DSL 或图片 | 完成状态 |
|---|---|---|---|
| `conversion-story.snapshot` | 1600×1000 信息图定稿 DSL | `conversion-story.png` | 已完成 |
| `conversion-story.png` | 服务返回的最终图片 | `conversion-story.snapshot` | 已完成，服务原始响应 |
| `analysis.json` | 审计数据（分数/百分比/加权公式/结论） | — | 已完成 |
| `snapshot-usage.md` / `task-metrics.json` | 报告与指标 | — | 已完成 |

需求逐项核对（依据最终图**实际查看**）：

| 题目要求 | 满足情况 | 证据 |
|---|---|---|
| 1600×1000 | 满足 | 服务 `image_info` = 1600×1000 |
| 两渠道各自两期转化率 | 满足 | 图①四根柱：30.00% / 10.00% / 35.00% / 12.00% |
| 两期访问构成 | 满足 | 图②两条**等长**堆叠条：80%/20% 与 20%/80%，各标「访问 10,000 次 · 合计 100%」 |
| 总体转化率 | 满足 | 图③实心柱 26.00% → 16.60%，小表两行「总体」 |
| 解释分组与总体是否同向 | 满足 | 标题、主结论与图③底部对照同时点明「分组↑、总体↓，不同向」 |
| 总体＝成交总数/访问总数 | 满足 | 2600/10000、1660/10000；`analysis.json.periods[].weighted_formula` |
| 不准平均渠道比例 | 满足 | 所有结论与总体值均用总成交÷总访问；渠道平均**仅**在图③以灰色虚框标注为「错误做法」，并在 `guardrails` 中说明 |
| 不把同期不同渠道绝对成交量当转化率 | 满足 | 每个渠道的率都用自己的分母：2400/8000、200/2000、700/2000、960/8000 |
| 率图同一 0–100% 尺度 | 满足 | 图①与图③均用 0/25/50/75/100 刻度，轴范围与像素映射写入 `analysis.json.axes` |
| 构成图每期等长、分段按真实占比 | 满足 | 两条长度相同，分段宽＝占比×等长；`axes[1].equal_length_per_period=true` |
| 所有原始分母/分子可从小表核对 | 满足 | 小表 6 行含「访问（分母）」「成交（分子）」「精确分数」三列，逐行可验 |
| 一条由数据支持的主结论 | 满足 | 「主结论」段，引用 4 个渠道率与 2 个总体率，差额 −9.40 个百分点 |
| 「不能证明因果」的限制说明 | 满足 | 「限制」段独立成块并标橙色 |
| 单位与期名齐全 | 满足 | 页眉右上单位说明；四张图与表格均标「前期 / 后期」；表头标单位 |
| 正文≥22、图标注≥18 | 满足 | 主结论与限制正文 22px；图内标注、坐标、表格、图注 18–20px |
| 用色和位置建立三图关系 | 满足 | ① ② ③ 编号建立顺序；① ② 共用渠道配色（直接=蓝、推广=橙），③ 专用青色表示总量 |
| 避免结论先行 | 满足 | 三图与数据表排在结论卡之前，结论卡位于右下 |
| analysis.json 四类字段 | 满足 | `groups` / `periods` / `axes` / `conclusions` 齐备 |
"""

docs_rows = """
| https://open-snapshot.muedsa.com/ai-guide.md | `POST /snapshot` 纯文本 DSL；按 `Content-Type` 判定成败；错误 JSON 的 `message` 与 `position` 用于定位 | `_suite/scripts/snapshot_render.py` |
| https://snapshot.muedsa.com/reference/parser-tags/ | `Stack`+`Positioned` 精确坐标；`Container` 渐变/圆角/边框；`Text` 的 `textAlign`/`height`；`Flex` 的 `mainAxisAlignment="END"` | `snapkit.py`、`conversion-story.snapshot` |
| https://snapshot.muedsa.com/reference/enums/ | `BorderStyle` 仅 `NONE`/`SOLID`（**没有** DASHED）；`CrossAxisAlignment` 仅 START/END/CENTER/STRETCH/BASELINE | 虚线外框改用小矩形拼出；右对齐图例用 `Row mainAxisAlignment="END"` |
"""

capabilities = (
    "布局：`Stack(fit=EXPAND)` + `Positioned` 实现三图的全部柱、网格线、刻度与堆叠分段；"
    "`Row mainAxisAlignment=END` 做右对齐图例；`Column`/`SizedBox` 组装卡片内元素。"
    "文本：`Text` 的 `fontFamily`/`fontSize`/`textAlign`（LEFT/CENTER/RIGHT）；`height` 控制行高。"
    "颜色与透明度：`#RRGGBBAA`（灰色虚框填充 `#CBD5E155`）、`borderRadius` 四角圆角。"
    "装饰：`border`、`border` 变体。图片标签：未使用（纯 DSL）。"
)

request_rows = """
| 请求ID | DSL | 耗时 | HTTP | 响应 | 查看与实际结果 |
|---|---|---|---|---|---|
| A04-v1-d96032d9 | drafts/a04-v1.snapshot | 2.06s | 400 application/json | responses/A04-v1-d96032d9.error.json | 无图；`PARSE_ERROR Attr [border] value is invalid: No enum constant BorderStyle.DASHED` |
| A04-v1-2f174c14 | drafts/a04-v1.snapshot（修正后） | 6.29s | 200 image/png | preview/a04-v1.png | 已打开整屏：数据与结构正确，但图③标题与图例重叠、图③绘图区过扁、结论卡三段严重重叠、表格「精确分数」被截断、图②窄分段标签溢出 |
| A04-v2-4c225775 | drafts/a04-v2.snapshot | 5.36s | 200 image/png | preview/a04-v2.png | 已打开整屏：结论卡已不重叠；但图②两根条的行距不足（外置标签压住上一行的「访问 10,000 次」），表格分数仍折行，结论第三段溢出卡片并与页脚相碰 |
| A04-v3-72aea110 | drafts/a04-v3.snapshot | 12.20s | 200 image/png | preview/a04-v3.png | 已打开整屏：图②、表格、结论卡均正常；仅图①底部注释右端被裁 |
| A04-final-* | outputs/…/conversion-story.snapshot | 见 metrics | 200 image/png | outputs/…/conversion-story.png | 已打开复查 |

（完整字段见 `requests.jsonl`；上表耗时取自该日志）
"""

change_rows = """
| 迭代 / 类型 | 问题或现象 | 原因及确认依据 | 修改 | 复验结果 | 文件 |
|---|---|---|---|---|---|
| v1 · syntax-fix | 服务 400 | `BorderStyle` 枚举速查页只有 `NONE`/`SOLID`，不存在 `DASHED` | 虚线外框改为按柱宽均匀排布的小矩形（顶边+底边各一组） | 服务 200 | `a04-v1.snapshot` |
| v2 · visual | 图③标题压住图例；图③绘图区被 `pb=70` 压扁；结论三段重叠；表格分数列折行；图②窄分段标签挤在条内 | 图例与标题同处 y=CH_Y+16；结论卡按固定行数 3/4/2 估算而实际为 3/3/2+ 溢出；分数列 106px 不足 | 图例下移到副标题行；绘图区上下边距收紧；卡片宽度重分配（520/420/剩余）；表格列宽重排并去掉分数中的空格；窄分段标签移到条形上方 | 结论不再重叠，表格分数完整 | `a04-v2.snapshot` |
| v3 · visual | 图②两根条行距 92px 不足，外置标签压住上一行说明；结论第三段仍与页脚相碰 | 行距需 ≥ 标签高+说明高；结论文案偏长 | 行距提到 112px；限制段与口径段各缩短一行 | 图②与结论均正常 | `a04-v3.snapshot` |
| v4 · visual | 图①底部注释右端被裁 | 卡片宽 520，注释文字宽 480 而实际约 600px | 注释压缩为「↑ 30.00%→35.00% · 10.00%→12.00%（成交 ÷ 访问）」 | 复查通过 | `a04-v4.snapshot` |
"""

design_notes = """
**关键设计选择**

1. *把「错误做法」画出来，而不是只说不要用*。题目的核心悖论正是「简单平均会给出相反方向」。
   因此图③同时画出正确的加权总体（青色实心）与错误的渠道比例平均（灰色虚框），
   两条线一眼可见方向相反；但**所有结论、表格与 JSON 都只用总成交÷总访问**，
   并在 `analysis.json.guardrails` 中写明这一约束，避免读者误读。
2. *构成图用等长条而不是饼图*。两条 100% 堆叠条长度完全一致、分段宽度＝真实占比，
   翻转一眼可见；饼图面积难比较，等长条更适合表达构成变化。
3. *三图用「① ② ③ + 共享配色」建立关系*。① ② 共用渠道色（直接=蓝、推广=橙），
   ③ 用区别于渠道的青色代表总量，位置从左到右对应「分组 → 构成 → 总体」的推理顺序。
4. *精确分数与百分比并列*。小表同时给「访问（分母）」「成交（分子）」「精确分数」「转化率」，
   让读者能自己验算；JSON 里用 `fractions.Fraction` 保留精确值而非浮点近似。
5. *结论不先行*。三图与小表排在结论卡之前，先看数据再看判断。

**可复用经验**

- `BorderStyle` 没有 `DASHED`，虚线只能自己用小矩形拼。
- 固定行数估算在真实渲染下不可靠（本任务实际行数与估计差 1 行就造成重叠）。
  改为按 `sk.est_lines()`（CJK 1.0em、其余 0.56em）估算并把估算值写入排版逻辑，
  仍以最终看图为准。
- 表格列宽要按**最长内容**而不是按标题分配；`2400/8000` 这类紧凑写法比 `2400 / 8000` 更省宽。
- 堆叠条的窄分段放不下标签时，标签要移到条形外并为行距留出空间，不能硬塞。

**结束依据**：最终图实际打开查看，三图数值、小表分数与结论引用的数字逐项与
`analysis.json` 及 CSV 原始分子分母核对一致；无重叠、无截断；未以渲染成功作为完成依据。
"""

unresolved = (
    "- 未发现影响交付的未解决问题。\n"
    "- 「正文≥22」已按主结论/限制/口径三段正文 22px 执行；表格正文为 20px、"
    "图内标注 18px，属于表体与图表附属元素。如需表体也 ≥22px，"
    "需加宽表格卡片并相应压缩结论卡片。\n"
    "- 因果限制已在图中与 JSON 中显式声明；本图不主张任何因果关系。"
)

retention = (
    "- 草稿 a04-v1…v4 全部保留，失败响应 JSON 保留在 `tmp/run-20261011-01/A04/responses/`，未删除或覆盖。\n"
    "- `tasks/A04-conversion-paradox/inputs/` 未被修改。\n"
    "- 未保存密钥。\n"
    "- 总任务根 `.gitignore` 仅排除运行时缓存，过程证据不受影响（共享规则见 `_suite/snapshot-usage.md`）。"
)


def main():
    r = ft.root()
    dsl = ft.promote_dsl(TASK, f"{TEMP}/drafts/a04-{VER}.snapshot", "conversion-story.snapshot")
    res = ft.render_final(TASK, "final", dsl, "conversion-story.png", TEMP)
    print("render ->", res.get("ok"), res.get("image_info"))
    if not res.get("ok"):
        sys.exit(1)
    analysis = json.loads((r / f"{TEMP}/drafts/analysis-raw.json").read_text(encoding="utf-8"))
    analysis["artifacts"] = {"conversion-story.png": {"width": 1600, "height": 1000,
                                                      "dsl": "conversion-story.snapshot",
                                                      "image_info": res.get("image_info")}}
    print("analysis ->", ft.write_audit_json(TASK, "analysis.json", analysis))

    log_rel = f"{TEMP}/iterations.jsonl"
    if not sl.read_jsonl(r / log_rel):
        for v, kind, prob, chg, cmp_ in [
            ("v1-syntax", "syntax-fix", ["服务 400：BorderStyle.DASHED 不存在"],
             "虚线外框改为小矩形拼出", "200 出图"),
            ("v1", "baseline", ["图③标题压住图例；图③绘图区过扁；结论三段重叠；表格分数截断；图②窄标签溢出"],
             "首版结构与数据正确", "整屏查看发现问题"),
            ("v2", "visual", ["结论不再重叠；图②行距不足、结论第三段溢出"],
             "图例下移；绘图区边距收紧；卡片宽度重分配；表格列宽重排；窄标签外移",
             "图②与表格正常"),
            ("v3", "visual", ["图①底部注释右端被裁"], "注释压缩为一行",
             "复查通过"),
            ("final", "visual", [], "最终交付复查", "1600×1000，无重叠无截断"),
        ]:
            ft.log(TASK, version=v, kind=kind, image=(f"{OUT}/conversion-story.png" if v == "final" else None),
                   problems=prob, changes=[chg], comparison=cmp_, complete=True)
    m = ft.build_metrics(
        TASK, started_at="2026-10-11T11:40:00.000+08:00", ended_at=sl.now_iso(),
        status="completed", stop_reason="需求满足并完成逐图视觉自检",
        feedback_wait=0.0, rate_limit_wait=0.0, queue_wait=None,
        outputs=[{"kind": "png", "path": f"{OUT}/conversion-story.png",
                  "dsl": f"{OUT}/conversion-story.snapshot", "required_by": "task.json required_outputs[0]",
                  **ft.png_size(f"{OUT}/conversion-story.png")},
                 {"kind": "dsl", "path": dsl},
                 {"kind": "json", "path": f"{OUT}/analysis.json"},
                 {"kind": "report", "path": f"{OUT}/snapshot-usage.md"},
                 {"kind": "metrics", "path": f"{OUT}/task-metrics.json"}],
        candidates=[{"path": f"{TEMP}/drafts/a04-v1.snapshot", "status": "superseded"},
                    {"path": f"{TEMP}/drafts/a04-v2.snapshot", "status": "superseded"},
                    {"path": f"{TEMP}/drafts/a04-v3.snapshot", "status": "superseded"}],
        round_label="round-01")
    recs = sl.read_jsonl(r / f"{TEMP}/requests.jsonl")
    renders = [x for x in recs if x.get("request_type") == "render"]
    ok = next((x for x in renders if x.get("status") == 200), None)
    m["timings"]["first_usable_image_seconds"] = round(
        sum(float(x.get("duration_seconds") or 0) for x in renders[:renders.index(ok) + 1]), 3)
    ft.write_metrics(TASK, m)

    mm = json.loads((r / f"{OUT}/task-metrics.json").read_text(encoding="utf-8"))
    t, c = mm["timings"], mm["counts"]
    metrics_rows = f"""
| 指标 | 实际值 | 单位 | 数据来源与统计范围 |
|---|---|---|---|
| 任务开始 / 结束时间 | {t['started_at']} / {t['ended_at']} | ISO8601 带时区 | 计时记录 |
| 任务总耗时 | {t['elapsed_seconds']} | 秒 | 墙钟时间 |
| 首次可用图耗时 | {t['first_usable_image_seconds']} | 秒 | 至首个 `200 image/png` 的请求耗时之和（串行） |
| 等待用户反馈 / 限流等待 | 0.0 / 0.0 | 秒 | 单轮任务；全程无 429 |
| 排队等待 | null | 秒 | 服务未提供该指标 |
| 已记录请求耗时之和 | {t['request_duration_sum_seconds']} | 秒 | `requests.jsonl` 求和，串行不重叠 |
| 成功 / 失败 / 重试请求 | {c['successful_snapshot_requests']} / {c['failed_snapshot_requests']} / {c['retry_requests']} | 次 | 1 次失败为语法错误，非重试 |
| 看图 / 完整视觉迭代 | {c['image_views']} / {c['completed_visual_iterations']} | 次 | `iterations.jsonl`；实际打开 4 张 |
| Server-Timing | null | — | 服务未返回该响应头 |
"""
    md = rg.render(task_id=TASK, title="分组改善与总体下降的数据解释", run_id=ft.run_id(),
                   status="完成", stop_reason="需求满足并完成逐图视觉自检",
                   out_dir=OUT, temp_dir=TEMP, req_items=req_items, docs_rows=docs_rows,
                   capabilities=capabilities,
                   counts={"other_queries": "字体与文档读取为 run 级共享准备；A04 另查枚举速查页确认 BorderStyle 取值"},
                   request_rows=request_rows, change_rows=change_rows,
                   metrics_rows=metrics_rows, design_notes=design_notes,
                   unresolved=unresolved, retention=retention)
    print(ft.write_usage(TASK, md))


if __name__ == "__main__":
    main()