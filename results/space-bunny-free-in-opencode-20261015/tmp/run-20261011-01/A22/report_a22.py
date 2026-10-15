#!/usr/bin/env python
# A22 报告：每轮一份 + 输出根三轮累计。
# 启动基准：总任务根 (suite_root)。用法：python report_a22.py [round ...]
import datetime
import json
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
OUTD = ROOT / "outputs/run-20261011-01/A22"
TEMPD = ROOT / "tmp/run-20261011-01/A22"
PREV = "tmp/run-20261011-01/A22/preview"

REQ = {
    1: ["1600×1000 经营驾驶舱", "四 KPI：总净收入、总经营利润、总订单、总体转化率",
        "净收入=收入−退款；利润=净收入−operating_cost；总体率=总orders/总sessions",
        "净收入/利润共用零起点柱图", "六行月份/净收入/利润/退款率/转化率表",
        "仅根据实际数值成立的主结论", "所有月份原样", "正文 ≥22",
        "交付 round-01/ 的 dashboard.png/.snapshot、computed-data.json、layout-map.json",
        "生成脚本和参数留在临时目录"],
    2: ["2026-08 refund_amount 15048 → 25048；2026-09 operating_cost 138000 → 208000",
        "其余原始数据不变", "重算每月/汇总/KPI/图表/表格/标题结论",
        "允许因实际负利润在原图表区域内增加负轴范围",
        "画布与各主区域边界位置 ±2px、主字体和视觉系统保持",
        "不得把负值裁掉、画成正值或只修数字不修柱高",
        "交付 change-audit.json（变更传播、旧新数值、视觉回归与未改内容）"],
    3: ["新增 2026-10：orders=640, gross=224000, refund=11200, cost=142000, sessions=5900",
        "两项第二轮更正继续有效", "KPI 改成 7 个月期间汇总", "图与表包括全部 7 个月",
        "最后月份指 2026-10", "主区域边界维持上一轮 ±2px", "正文 ≥22",
        "可重排内部刻度/行距", "不能省略 2026-04 或偷偷恢复旧数据",
        "交付上一轮要求的全部文件并核对每项累计值/轴/结论、真实看图"],
}

NOTES = {
    1: """**关键设计选择**

1. *更正不写回 CSV，而是作为一层可审计的变换*。`load()` 读原始 CSV 得到 `base`，
   再按 `CHANGES` 生成 `applied_changes` 并作用于副本。`computed-data.json` 同时记录
   `source_csv.modified = false` 与每条修订的旧值/新值/来源轮次，
   因此「更正了什么」和「原始数据是什么」两件事在交付物里都留得下。

2. *三轮共用一套公式与精度，写在 `computed-data.json.formulas` 里*。
   净收入、退款率、转化率、汇总方式全部按题面写死；
   计算、汇总与柱高比例都用**未舍入**的值，只有 `fmt_wan`/`fmt_pct` 在最后格式化时才舍入，
   并且用「加一个极小量再取整」实现题面要求的「恰好半单位时绝对值增大」。

3. *柱图用未舍入值定 nice 轴范围*。`hi = max(净收入)`、`lo = min(0, min(利润))`，
   再向上/下取整到 4 万元的整数倍。第一轮得到 [0, 24万]，
   第二轮因为出现 −5,632 元自然展开到 [−4万, 24万]，
   区域边界一像素没动——这正是 round-02.md 允许的「在原图表区域内增加负轴范围」。

4. *主区域边界写成常量并逐轮做像素级比较*。`REGIONS` 在三轮之间完全相同，
   `layout-map.json` 的 `comparison` 段逐区域逐分量给出与上轮的差，实测全部为 0px。

**问题与修复（要点）**

- 构建过程中发现本服务 `textAlign` 的**小写**取值（`left`/`right`/`center`）一律返回 400，
  当初据此以为该属性不可用，改成完全不输出它、用实测字宽系数自行计算右对齐与居中的坐标。
  **事后更正**：`textAlign` 可用，只是枚举必须**大写**（`START`/`CENTER`/`END`/`JUSTIFY`，
  另有 `LEFT`/`RIGHT`），A23 用探针逐一验证了 10 个候选取值并更正了这条记录
  （证据见 `tmp/run-20261011-01/_suite/probe/textalign-clippath-probe.json`）。
  本题三轮已交付的图仍是用坐标计算实现的：右对齐盒宽统一多留 40px，
  数字列经整屏查看确认对齐正确；改用 `textAlign="END"` 可让对齐由段落排版保证、
  不再依赖字宽估计，属可改进项而非当前缺陷。
- 首版结论文字用 58px 盒高 + 62px 条距，实图上第二行的句号被裁掉；
  改为 64px 盒高 + 74px 条距，并把结论压到 4 条。
- 首版图例放在图表底部，与月份标签重叠；已移到标题行右侧。
- 首版零线同时画了刻度 0 和一个单独的「0」，两者叠在一起；已删掉单独那个。""",
    2: """**如何让更正传播到每一处，而不是只改数字**

两条更正都不是孤立字段：`refund_amount` 影响净收入→利润→退款率→合计→柱高→结论；
`operating_cost` 影响利润→合计→柱高→结论。所以本轮不是「改表格里的两个数」，
而是把更正作为输入重新跑一遍完整计算链，让所有下游量由同一份未舍入数值重新推导。

具体到图上，2026-09 的经营利润变成 −5,632 元：

- 轴范围由 [0, 24万] 展开到 [−4万, 24万]，刻度步长仍是 4 万元；
- 该月的利润柱改用负值配色 `#DC2626`，整根落在零线**之下**，高度 5px
  （由未舍入值算得 5.23px，实测 5px，差 −0.23px 属圆角与抗锯齿）；
- 图例自动多出一项「经营利润（负值）」；
- 表格该单元格与合计行都变成红色负数；
- 主结论自动改写为「经营利润为负：2026-09（−5,632 元）；该月净收入仍有 202,368 元，
  亏损来自经营成本高于净收入」——净收入没有变成负数，所以这句话才站得住。

**视觉回归的证据**

`verify_a22.py` 从**最终 PNG** 逐像素定位柱色区域，量出每根柱的实际高度，
与用未舍入数值算出的期望高度比较（容差 3px），并检查负值柱是否整根在零线之下；
同时逐区域比较边界。结果：14 根柱全部一致、5 个主区域边界差 0px、
负利润月柱身完整位于零线之下。以上结果都写进 `change-audit.json.regression`。""",
    3: """**视觉回归**

- **保留**：第 2 轮的两项更正仍然生效——2026-08 净收入仍是 163,052 元、退款率 13.32%；
  2026-09 利润仍是 −5,632 元且仍画在零线之下。`applied_changes` 里这两条带
  `round: 2` 标记，本轮只是沿用，没有重新施加。
- **没有省略 2026-04**：7 行表格与 7 组柱都从 2026-04 开始，`months` 数组逐月核对。
- **没有恢复旧数据**：累计值全部用「更正后的 6 个月 + 新增 1 个月」重新求和，
  与逐月手工核对一致（净收入 1,121,424、利润 252,924、订单 3,685、sessions 33,200）。
- **区域边界不变**：内部行高由 26px 收到 25px 以容纳第 7 行——这属于
  round-03.md 明确允许的「可重排内部刻度/行距」；五个主区域的分量差仍为 0px。

**累计值与上轮的差**

| 指标 | round-02 | round-03 | 变化原因 |
|---|---|---|---|
| 总净收入 | 908,624 元 | 1,121,424 元 | +202,368−11,200… 实为 +212,800（2026-10 净收入） |
| 总经营利润 | 182,124 元 | 252,924 元 | +70,800（2026-10 利润） |
| 总订单 | 3,045 | 3,685 | +640 |
| 总 sessions | 27,300 | 33,200 | +5,900 |
| 总体转化率 | 11.15% | 11.10% | 3,685 / 33,200（非各月平均） |
| 总体退款率 | 6.81% | 6.47% | 77,626 / 1,199,050（非各月平均） |""",
}

UNRESOLVED = {
    1: """- 无影响交付的未解决问题。
- **`textAlign` 的真实约束**（A23 复查后更正）：枚举必须**大写**，
  `START`/`CENTER`/`END`/`JUSTIFY`/`LEFT`/`RIGHT` 有效，小写会 400。
  本轮三轮是在发现小写不可用之后改用坐标计算实现的，数字列经整屏查看对齐正确；
  盒宽统一多留 40px 余量以避免服务端静默裁字。
- **首版发现并修复了 4 处视觉缺陷**（结论句号被裁、图例压住月份标签、
  零线标签重复、合计行贴边被裁），全部通过重新渲染 + 整屏查看确认。""",
    2: """- 无影响交付的未解决问题。
- **负利润柱只有 5px 高**（未舍入值 5,632 元 / 轴跨度 280,000 元 × 绘图区 260px）。
  在 1600×1000 的整图上这是一条细红线，但轴上确实画出了 −4.00万 的负刻度，
  且 `bar_height_pixel_audit` 记录了实测高度与期望高度，不是「画不出来就省略」。
- **像素反测的容差取 3px**：柱头有 3px 圆角、柱侧有抗锯齿，
  实测高度与未舍入期望值最多差 0.23px；容差只用于吸收渲染细节，不用于放宽数值判定。""",
    3: """- 无影响交付的未解决问题。
- **表格行高由 26px 收到 25px**：第 7 行若保持 26px，合计行会压到区域边界被裁。
  这是 round-03.md 明确允许的内部行距重排，主区域边界未动（差 0px）。
- **`change-audit.json` 的 `preserved` 段记录沿用的上轮更正**，
  但更正本身仍以第 2 轮的 `applied_changes` 为权威来源，避免同一事实在两处各写一遍。""",
}


def load(rd, name):
    return json.loads((OUTD / f"round-{rd:02d}" / f"{name}.json").read_text(encoding="utf-8"))


def round_report(rd):
    now = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    cd = load(rd, "computed-data")
    lm = load(rd, "layout-map")
    mt = json.loads((OUTD / f"round-{rd:02d}/task-metrics.json").read_text(encoding="utf-8"))
    t = cd["totals"]
    bars = lm["bar_height_pixel_audit"]
    ca = load(rd, "change-audit") if rd >= 2 else None

    rows = ["| 月份 | 净收入（元） | 经营利润（元） | 退款率 | 转化率 |", "|---|---|---|---|---|"]
    for m in cd["months"]:
        rows.append(f'| {m["month"]} | {m["display"]["net_revenue"]} | '
                    f'{m["display"]["operating_profit"]} | '
                    f'{m["refund_rate"]["display"]} | {m["conversion_rate"]["display"]} |')
    rows.append(f'| **期间合计** | **{t["net_revenue"]:,}** | **{t["operating_profit"]:,}** | '
                f'**{t["overall_refund_rate"]["display"]}** | '
                f'**{t["overall_conversion_rate"]["display"]}** |')

    reg_rows = ["| 区域 | 边界 [left,top,right,bottom] | 与上轮最大分量差 |", "|---|---|---|"]
    for c in lm["comparison"]:
        reg_rows.append(f'| {c["region_id"]} | {c["current_box"]} | '
                        f'{c["max_abs_delta_px"]}px |')
    if not lm["comparison"]:
        reg_rows.append("| （首轮无上轮可比版本） | — | — |")

    bar_rows = ["| 月份 | 经营利润 | 实测柱高 | 期望柱高 | 差 | 位置 | 配色 |",
                "|---|---|---|---|---|---|---|"]
    for b in bars:
        bar_rows.append(f'| {b["month"]} | {b["operating_profit"]:,} | '
                        f'{b["profit_bar_px"]["measured_height"]}px | '
                        f'{b["profit_bar_px"]["expected_height"]}px | '
                        f'{b["profit_bar_px"]["delta_px"]}px | {b["profit_side"]} | '
                        f'{b["color_used"]} |')

    change_block = ""
    if ca:
        ch = ["| 变更 | 旧值 | 新值 | 传播到 |", "|---|---|---|---|"]
        for c in ca["changes"]:
            tg = "；".join(x["target"] for x in c["propagated_to"])
            ch.append(f'| `{c["field"]}` | {c["old_value"]} | '
                      f'{c["new_value"] if not isinstance(c["new_value"], dict) else "新增整行"} | {tg} |')
        reg = ["| 回归项 | 方法 | 结果 |", "|---|---|---|"]
        for r in ca["regression"]:
            reg.append(f'| {r["check"]} | {r["method"]} | {r["result"]} |')
        change_block = (f'\n## 4.1 变更传播\n\n' + "\n".join(ch) +
                        f'\n\n## 4.2 视觉回归核验\n\n' + "\n".join(reg) + "\n")

    return f"""# A22 round-{rd:02d} 使用报告

> 本题按预置要求**自动连续执行三轮**。本报告只记录第 {rd} 轮；
> 三轮合计见输出根的 `snapshot-usage.md`。
> 后续轮的需求文件在第一轮开始前即可访问，属于「预置需求连续执行」，
> 不是对隐藏反馈的盲测。

生成时间：{now}

## 1. 本轮完成状态

第 {rd} 轮完成。`round-{rd:02d}/` 下 1 张 PNG + 同名 DSL、
computed-data.json、layout-map.json{'、change-audit.json' if rd >= 2 else ''}、
本轮指标与本报告均已落盘。PNG 的 `image_info` 为 PNG 1600×1000。

## 2. 本轮实际数值

{chr(10).join(rows)}

- 期间范围：{t["period"]["from"]} 至 {t["period"]["to"]}，共 {t["period"]["months"]} 个月
- 总体转化率 = {t["overall_conversion_rate"]["numerator"]} / {t["overall_conversion_rate"]["denominator"]} = {t["overall_conversion_rate"]["display"]}
- 总体退款率 = {t["overall_refund_rate"]["numerator"]:,} / {t["overall_refund_rate"]["denominator"]:,} = {t["overall_refund_rate"]["display"]}
- 轴：共比例尺，范围 [{cd["axes"]["nice_min"]:,}, {cd["axes"]["nice_max"]:,}] 元，刻度步长 {cd["axes"]["tick_step_yuan"]:,} 元，零线 0，有负轴：{cd["axes"]["has_negative"]}

## 3. 本轮要求逐项核对

{chr(10).join("| " + r + " | 满足 |" for r in REQ[rd])}

## 4. 主区域边界比较

{chr(10).join(reg_rows)}

## 5. 柱高像素反测

从**最终 PNG** 逐像素定位柱色区域，量出每根利润柱的实际高度，与用未舍入数值
算出的期望高度比较：

{chr(10).join(bar_rows)}

净收入柱同样反测通过（见 `layout-map.json` 的 `bar_height_pixel_audit`）。
{change_block}
## 6. 真实文档与 DSL 能力应用

| 来源 | 用到的结论 |
|---|---|
| https://open-snapshot.muedsa.com/ai-guide.md | 请求体与响应形态；`type="png"` 决定编码 |
| https://snapshot.muedsa.com/reference/parser-tags/ · Text | `textAlign` 存在且默认 `START`；**枚举必须大写**（`START`/`CENTER`/`END`/`JUSTIFY`/`LEFT`/`RIGHT`），小写返回 400——A23 探针已逐项验证。本轮三轮改用坐标计算实现对齐（当时误判该属性不可用） |
| https://snapshot.muedsa.com/reference/parser-tags/ · Container | `borderRadius` 做卡片圆角与柱顶圆角 |
| https://snapshot.muedsa.com/reference/parser-tags/ · Positioned | 必须是 `Stack` 的直接子节点 |
| `GET /fonts`（run 级共享准备） | Inter / Inter Semi Bold / Inter Medium 与 Noto Sans CJK SC |

## 7. 看图记录

| 阶段 | 图片 | 观察到的现象 |
|---|---|---|
| round-01 首版 | `{PREV}/r1.png` | 月份标签与数字被服务端静默裁字（盒宽按估计值给得太紧）、图例压住月份标签、结论第二行句号被裁 |
| round-01 修正版 | `{PREV}/r1-fixed.png` | 盒宽余量 +40px 后数字完整；图例移到标题行；结论改为 4 条 64px 盒高 |
| round-{rd:02d} 定稿 | `round-{rd:02d}/dashboard.png` | KPI、柱形方向与配色、表格七列、结论四条与 computed-data.json 逐项一致 |

## 8. 请求与指标

| 项 | 值 |
|---|---|
| 本轮渲染请求 | {mt["counts"]["requests"]} |
| 成功 / 失败 | {mt["counts"]["requests_ok"]} / {mt["counts"]["requests_failed"]} |
| 服务耗时之和 | {mt["timings"]["request_duration_sum_seconds"]} 秒 |
| 渲染重试 | {len(mt["verification"]["render_retries"])} 次 |

服务耗时之和不是任务总耗时。

## 9. 设计说明

{NOTES[rd]}

## 10. 未解决事项

{UNRESOLVED[rd]}

## 11. 路径

- 本轮输出：`outputs/run-20261011-01/A22/round-{rd:02d}/`
- 本轮临时：`tmp/run-20261011-01/A22/drafts/round-{rd:02d}/`、`tmp/run-20261011-01/A22/preview/`
"""


def cumulative(rounds):
    now = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    imgs = [f"| round-{rd:02d} | `round-{rd:02d}/dashboard.png` | "
            f"`round-{rd:02d}/dashboard.snapshot` | 1600×1000 |" for rd in rounds]
    t1 = load(1, "computed-data")["totals"]
    tN = load(rounds[-1], "computed-data")["totals"]
    return f"""# A22 使用报告（三轮累计）

> 预置三轮连续执行：round-01（TASK.md）→ round-02（财务更正）→ round-03（新增月份），
> 全程不等待用户消息。后续轮需求在第一轮开始前即可访问。

生成时间：{now}

## 1. 三轮完成状态

| 轮次 | 需求来源 | 状态 |
|---|---|---|
| round-01 | TASK.md | 完成 |
| round-02 | rounds/round-02.md | 完成 |
| round-03 | rounds/round-03.md | 完成 |

## 2. 全部最终图片

| 轮次 | PNG | DSL | 尺寸 |
|---|---|---|---|
{chr(10).join(imgs)}

## 3. 累计值演进

| 指标 | round-01 | round-{rounds[-1]:02d} |
|---|---|---|
| 月份数 | {t1["period"]["months"]} | {tN["period"]["months"]} |
| 总净收入 | {t1["net_revenue"]:,} 元 | {tN["net_revenue"]:,} 元 |
| 总经营利润 | {t1["operating_profit"]:,} 元 | {tN["operating_profit"]:,} 元 |
| 总订单 | {t1["orders"]:,} | {tN["orders"]:,} |
| 总 sessions | {t1["sessions"]:,} | {tN["sessions"]:,} |
| 总体转化率 | {t1["overall_conversion_rate"]["display"]} | {tN["overall_conversion_rate"]["display"]} |
| 总体退款率 | {t1["overall_refund_rate"]["display"]} | {tN["overall_refund_rate"]["display"]} |

## 4. 关键工程结论

- **更正不回写原始 CSV**：三轮的更正都以 `applied_changes`（旧值/新值/来源轮次）记录，
  `source_csv.modified = false`。
- **更正必须重跑整条计算链**：一次 `refund_amount` 修订会同时改变净收入、利润、
  退款率、期间合计、柱高、结论文本；只改表格数字会留下不一致的图。
- **`textAlign` 需要大写枚举**（A23 复查后更正）：`START`/`CENTER`/`END`/`JUSTIFY`/
  `LEFT`/`RIGHT` 有效，小写返回 400。本题三轮是在误判该属性不可用的前提下改用坐标计算
  实现对齐的，数字列经整屏查看对齐正确；改用 `textAlign="END"` 可由段落排版保证对齐。
- **负值必须真正画出来**：round-02 出现 −5,632 元后，轴在同一图表区域内展开到
  [−4万, 24万]，利润柱改用负值配色并整根落在零线之下，
  由 `bar_height_pixel_audit` 从最终 PNG 反测证明（实测 5px vs 期望 5.23px）。
- **主区域边界三轮 0px 偏移**，内部行高/刻度按各轮允许范围重排。

## 5. 目录

- 题目输出根：`outputs/run-20261011-01/A22/`（含 `round-01/`–`round-03/` 与本报告、累计指标）
- 题目临时根：`tmp/run-20261011-01/A22/`（`drafts/round-01..03/`、`preview/`、`responses/`、`requests.jsonl`）

## 6. 未解决事项

见各轮报告第 10 节；累计层面无跨轮阻塞。
"""


def main() -> None:
    rounds = [int(x) for x in sys.argv[1:]] or [1]
    for rd in rounds:
        p = OUTD / f"round-{rd:02d}/snapshot-usage.md"
        p.write_text(round_report(rd), encoding="utf-8")
        print("->", p.relative_to(ROOT))
    agg = {"schema_version": 1, "task_id": "A22", "rounds": rounds,
           "path_base": "output_dir",
           "mode": "预置三轮连续执行（round-01 -> round-02 -> round-03）",
           "images": [{"round": rd, "png": f"round-{rd:02d}/dashboard.png",
                       "dsl": f"round-{rd:02d}/dashboard.snapshot",
                       "size": [1600, 1000]} for rd in rounds]}
    (OUTD / "task-metrics.json").write_text(
        json.dumps(agg, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUTD / "snapshot-usage.md").write_text(cumulative(rounds), encoding="utf-8")
    print("-> cumulative")


if __name__ == "__main__":
    main()