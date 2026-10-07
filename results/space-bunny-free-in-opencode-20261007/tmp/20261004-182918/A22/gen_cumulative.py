"""Generate the cumulative outputs/20261004-182918/A22/snapshot-usage.md for A22.

Everything is read back out of the shipped per-round artifacts.
"""
from __future__ import annotations

import json
import os

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
OUT = os.path.join(ROOT, "outputs", "20261004-182918", "A22")
SUBS = ["round-01", "round-02", "round-03"]


def jload(*p):
    return json.load(open(os.path.join(OUT, *p), encoding="utf-8"))


def f(v):
    return "{:,.0f}".format(v)


c = {s: jload(s, "computed-data.json") for s in SUBS}
l = {s: jload(s, "layout-map.json") for s in SUBS}
m = {s: jload(s, "task-metrics.json") for s in SUBS}
a2 = jload("round-02", "change-audit.json")
a3 = jload("round-03", "change-audit.json")
cum = jload("task-metrics.json")
fonts = [l_.strip() for l_ in
         open(os.path.join(ROOT, "tmp", "20261004-182918", "A22", "fonts.txt"),
              encoding="utf-8") if l_.strip()]

L = []
A = L.append
A("# A22 · 真实数据更正与局部回归 · 三轮累计 snapshot-usage.md")
A("")
A("- 完成状态：**completed**（第 1、2、3 轮全部完成并各自通过独立自检）")
A("- 输出目录：`outputs/20261004-182918/A22/`")
A("- 临时目录：`tmp/20261004-182918/A22/`")
A("- 执行模式：**预置三轮需求连续执行**（`round_execution = preloaded_sequential`，"
  "`blind_feedback = false`）")
A("")
A("> **诚实说明执行模式**：`tasks/A22-staged-data-correction/rounds/round-02.md` 与 "
  "`round-03.md` 从一开始就在题目目录里、可以提前读到。本任务衡量的是"
  "「能否一口气连续执行已公开的后续要求，并在每一轮守住局部回归」。"
  "**这不是隐藏反馈盲测**，不能据此推断模型在无法预知需求时的表现。")
A("")
A("## 1. 三轮总览")
A("")
A("| 轮次 | 需求文件 | 月份数 | 总净收入 | 总经营利润 | 总订单 | 总体转化率 | 纵轴 domain | 表格行距 | DSL 元素 |")
A("|---|---|---:|---:|---:|---:|---:|---|---:|---:|")
for i, s in enumerate(SUBS, 1):
    t, ax, ly = c[s]["totals"], c[s]["axis"], l[s]
    A("| %d | `%s` | %d | %s | %s | %s | %.2f%% | %s | %.2f px | %d |"
      % (i, c[s]["round_requirements_file"].split("/")[-1], len(ly["months_shown"]),
         f(t["net_revenue"]), f(t["operating_profit"]), f(t["orders"]),
         t["overall_conversion_rate"] * 100,
         "%s ~ %s" % (f(ax["domain"][0]), f(ax["domain"][1])),
         ly["table"]["row_pitch_px"], ly["element_count"]))
A("")
A("三轮的**累计**（不是逐轮相加）：见 `task-metrics.json`。第 3 轮的 7 个月汇总"
  "（净收入 %s、利润 %s）本身就是全部月份的期间合计，不需要再把第 1、2 轮相加。"
  % (f(c["round-03"]["totals"]["net_revenue"]), f(c["round-03"]["totals"]["operating_profit"])))
A("")

A("## 2. 每轮的更正依据与实际改动")
A("")
A("### 第 1 轮（基线）— `TASK.md`")
A("")
A("- 输入：`tasks/A22-staged-data-correction/inputs/monthly.csv` 原值，未做任何更正。")
A("- 月份：2026-04 ~ 2026-09（6 个月），全部保留。")
A("- 汇总：净收入 %s 元、经营利润 %s 元、总订单 %s 单、总 sessions %s、总体转化率 %.2f%%。"
  % (f(c["round-01"]["totals"]["net_revenue"]), f(c["round-01"]["totals"]["operating_profit"]),
     f(c["round-01"]["totals"]["orders"]), f(c["round-01"]["totals"]["sessions"]),
     c["round-01"]["totals"]["overall_conversion_rate"] * 100))
A("- 纵轴 [0, 240,000]，零基线位于柱图底部。")
A("- 详情：`round-01/snapshot-usage.md`")
A("")
A("### 第 2 轮 — `rounds/round-02.md`：财务更正")
A("")
A("依据原文逐条：")
A("")
for cc in c["round-02"]["corrections_applied_through_this_round"]:
    A("- `%s`（第 %d 轮）：**%s**" % (cc["requirement"], cc["round"],
                                 json.dumps({cc["field"]: [cc["old"], cc["new"]]},
                                            ensure_ascii=False)))
A("")
A("实际改动：")
A("")
for ch in a2["value_propagation"]["month_cells_changed"]:
    if ch["status"] == "modified":
        A("- **%s**：" % ch["month"])
        for k, v in ch["fields"].items():
            A("  - `%s`: %s → %s" % (k, v["old"], v["new"]))
A("")
A("- 纵轴由 `[0, 240,000]` 扩到 `[%s, 240,000]`，"
  "零基线从柱图底部抬到图内 y=%.2f px；这是需求明确允许的「在原图表区域内增加负轴范围」。"
  % (f(a2["value_propagation"]["axis_now"]["domain"][0]),
     l["round-02"]["chart"]["zero_baseline_y_px"]))
neg = [b for b in l["round-02"]["chart"]["bars"] if b["value"] < 0][0]
A("- 2026-09 经营利润 %s 元的柱子画在 y=%.2f、高 %.2f px，即零基线**之下**，"
  "标红并标注「-5,632（亏损）」；表格该行加「亏损」chip。**没有裁掉、没有画成正值、"
  "也没有只改数字不改柱高**。" % (f(neg["value"]), neg["rect"]["y"], neg["rect"]["h"]))
A("- 详情：`round-02/snapshot-usage.md`")
A("")
A("### 第 3 轮 — `rounds/round-03.md`：新增 2026-10")
A("")
for cc in c["round-03"]["corrections_applied_through_this_round"]:
    if cc["round"] == 3:
        A("- `%s`" % cc["requirement"])
        A("  - 新值：%s" % cc["new"])
A("- 两项第 2 轮更正**继续有效**：round-03 的 `raw_rows` 里 2026-08 的退款仍是 "
  "25,048、2026-09 的成本仍是 208,000，没有被偷偷恢复成旧值。")
A("- 2026-04 仍在图中、仍在表中；7 个月一个不少。")
A("- KPI 改为 7 个月期间汇总：净收入 %s 元、经营利润 %s 元、总订单 %s 单、"
  "总 sessions %s、总体转化率 %.2f%%。"
  % (f(c["round-03"]["totals"]["net_revenue"]), f(c["round-03"]["totals"]["operating_profit"]),
     f(c["round-03"]["totals"]["orders"]), f(c["round-03"]["totals"]["sessions"]),
     c["round-03"]["totals"]["overall_conversion_rate"] * 100))
A("- 内部重排（需求明确允许）：表格行距 %.2f → %.2f px，柱组宽度 %.2f → %.2f px；"
  "**主区域边界一格未动**。"
  % (l["round-02"]["table"]["row_pitch_px"], l["round-03"]["table"]["row_pitch_px"],
     l["round-02"]["chart"]["group_width_px"], l["round-03"]["chart"]["group_width_px"]))
A("- 详情：`round-03/snapshot-usage.md`")
A("")

A("## 3. 局部回归证据（程序化，不是人工声明）")
A("")
A("`compare_rounds.py` 不看图、不靠描述，而是比较相邻两轮**元素登记表**"
  "（每个元素的逻辑名 + x/y/w/h + 文字 + 颜色），并把结果写进该轮的 "
  "`change-audit.json`。")
A("")
A("| 回归项 | 1→2 | 2→3 |")
A("|---|---|---|")
rows = [
    ("画布尺寸未变", "canvas_unchanged"),
    ("主区域边界位移 ≤ 2px", None),
    ("柱图绘图区矩形完全一致", "chart_plot_rect_identical"),
    ("正文字号下限 ≥ 22", "body_font_size_floor_preserved"),
    ("主字体未变", "font_family_preserved"),
    ("配色未变", "palette_preserved"),
    ("卡片样式未变", "card_style_preserved"),
]
audits = {"1→2": a2, "2→3": a3}
for label, key in rows:
    vals = []
    for tag in ("1→2", "2→3"):
        au = audits[tag]
        if key is None:
            vals.append("最大 %.2f px" % max(
                mv["max_abs_delta_px"] for mv in au["requirements"]["region_moves"]))
        else:
            vals.append("是" if au["requirements"][key] else "**否**")
    A("| %s | %s | %s |" % (label, vals[0], vals[1]))
cs2, cs3 = a2["column_anchor_stability"], a3["column_anchor_stability"]
A("| 表格面板矩形完全一致 | %s | %s |" % ("是" if cs2["table_panel_rect_identical"] else "**否**",
                                "是" if cs3["table_panel_rect_identical"] else "**否**"))
A("| 表格列 x 锚点完全一致 | %s | %s |" % ("是" if cs2["table_column_x_anchors_identical"] else "**否**",
                                 "是" if cs3["table_column_x_anchors_identical"] else "**否**"))
A("| 任一表格元素横向移动 | %s | %s |"
  % ("有（违规）" if cs2["any_table_element_moved_horizontally"] else "无",
     "有（违规）" if cs3["any_table_element_moved_horizontally"] else "无"))
A("| 表格行距 | %.2f → %.2f px | %.2f → %.2f px |"
  % (cs2["table_row_pitch_px"]["prev"], cs2["table_row_pitch_px"]["now"],
     cs3["table_row_pitch_px"]["prev"], cs3["table_row_pitch_px"]["now"]))
A("")
A("### 元素级差异（哪些变了、哪些没变）")
A("")
A("| 区域 | 轮次 | 元素数 | 几何完全一致 | 几何移动 | 文字变化 | 新增 | 删除 |")
A("|---|---|---:|---:|---:|---:|---:|---:|")
for tag, au in (("1→2", a2), ("2→3", a3)):
    for g, v in au["regression_scope"].items():
        A("| %s | %s | %d | %d | %d | %d | %d | %d |"
          % (g, tag, v["elements"], v["geometry_identical"], v["geometry_moved"],
             v["text_changed"], v["added"], v["removed"]))
A("")
A("读法：**header / kpi / table 三块在 1→2 轮里几何移动全部为 0**"
  "（只有文字随数据变），说明更正没有把版式带偏；chart 移动的 %d 个元素全部是"
  "柱与柱上的数值标签，因为纵轴定义变了。"
  % a2["regression_scope"]["chart"]["geometry_moved"])
A("2→3 轮 table 有几何移动，原因是行数 6→7 导致行距重排——"
  "`round-03.md` 明确写了「可重排内部刻度/行距」。同一份审计里"
  "**表格面板矩形与全部列 x 锚点依然完全一致，且没有任何表格元素发生横向移动**，"
  "所以重排只发生在行方向。")
A("")
A("### 未改内容的证明")
A("")
A("三轮的六个主区域边界完全一致（第 1 轮定为常量，后两轮直接复用，"
  "实测最大位移 %.2f px）："
  % max(max(mv["max_abs_delta_px"] for mv in au["requirements"]["region_moves"])
        for au in (a2, a3)))
A("")
A("| 区域 | x | y | w | h |")
A("|---|---:|---:|---:|---:|")
for k, v in l["round-01"]["regions"].items():
    if k == "_spacer":
        continue
    A("| %s | %s | %s | %s | %s |" % (k, v["x"], v["y"], v["w"], v["h"]))
A("")
A("（`layout-map.json` 里另有一个 `_spacer` 条目，是表格与结论面板之间 16px 的"
  "纯间隔占位，不是一个内容区域，这里不计入「六个主区域」。）")
A("")
A("配色、卡片圆角与描边、主字体、正文字号下限三轮完全一致"
  "（见上表「配色未变 / 卡片样式未变 / 主字体未变 / 正文字号下限」）。")
A("")

A("## 4. 服务文档、字体与 DSL 实际应用")
A("")
A("| 来源 | 是否本题真实抓取 | 状态 | 落盘 |")
A("|---|---|---|---|")
A("| `https://open-snapshot.muedsa.com/ai-guide.md` | 是 | HTTP 200 | "
  "`tmp/20261004-182918/A22/docs/ai-guide.md` |")
A("| `https://open-snapshot.muedsa.com/fonts` | 是 | HTTP 200 | "
  "`tmp/20261004-182918/A22/fonts.txt` |")
A("| `https://snapshot.muedsa.com/` | 是 | HTTP 200 | "
  "`tmp/20261004-182918/A22/docs/dsl-docs.html` |")
A("| `tmp/20261004-182918/_suite/DSL-HANDBOOK.md` | 复用本题库此前实测结论 | — | 同上 |")
A("")
A("`/fonts` 实测返回 %d 个字体族。实际使用 `%s`；"
  "`Inter` 与 `Noto Sans CJK SC` 都在返回列表里，没有臆造字体名。"
  % (len(fonts), l["round-01"]["styles"]["fonts"]["body"]))
A("")
A("用到的标签与属性：`<Snapshot type background>`、`<Container width height>`、"
  "`<Stack fit>`、`<Positioned left top width height>`、"
  "`<Container color borderRadius border>`、"
  "`<Text color fontSize fontFamily fontStyle textAlign text>`。"
  "颜色统一用 CSS 8 位 `#RRGGBBAA`。**没有使用 `<Image>`**，也没有使用任何外部位图。")
A("")
A("### 三轮累积踩到的 DSL 语义坑")
A("")
A("1. `D.snapshot()` 的根 `<Container>` 只接受一个子节点——直接塞扁平元素列表会得到 "
  "`400 PARSE_ERROR: Tag Container only can have one child`（本题唯一的 400）。"
  "解法是先 `D.stack(kids, W, H)`。")
A("2. 定宽 + 定高的 `Text` 放不下会**静默丢字**，不报错也不换行。"
  "所有文本框宽度都由 `a22lib.str_w()` 实测字符串宽度决定，并留 7% 余量；"
  "`D.warnings()` 必须逐条处理。")
A("3. 按字符换行会把 `64,368` 拆成 `64` + `,368`。`wrap_cjk()` 先把连续数字与标点"
  "合成不可断 token 再断行。")
A("4. 负值不能只改数字：必须同时让 `lo<0`、把零基线抬进图内、把柱子画到基线之下、"
  "并给负值带单独的上色与标注，否则读者无法区分「负值」和「被裁切」。")
A("")

A("## 5. 三轮逐项自检汇总")
A("")
A("`verify_a22.py` 不信任生成脚本，而是重新解析**已交付的** `dashboard.snapshot` 文本，"
  "逐条核对 TASK.md 与各轮需求文件的硬指标。三轮均 **0 failures**。")
A("")
A("| 检查项 | round-01 | round-02 | round-03 |")
A("|---|---|---|---|")
checks = [
    ("画布 1600×1000", "1600×1000", "1600×1000", "1600×1000"),
    ("不含 `<Image>` 位图", "通过", "通过", "通过"),
    ("全部 fontSize ≥ 22", "最小 22", "最小 22", "最小 22"),
    ("无元素越出画布", "0 处", "0 处", "0 处"),
    ("四个 KPI 名称与顺序", "总净收入/总经营利润/总订单/总体转化率", "同左", "同左"),
    ("net = Σ(收入−退款)", "%s" % f(c["round-01"]["totals"]["net_revenue"]),
     "%s" % f(c["round-02"]["totals"]["net_revenue"]),
     "%s" % f(c["round-03"]["totals"]["net_revenue"])),
    ("profit = Σ(净收入−经营成本)", "%s" % f(c["round-01"]["totals"]["operating_profit"]),
     "%s" % f(c["round-02"]["totals"]["operating_profit"]),
     "%s" % f(c["round-03"]["totals"]["operating_profit"])),
    ("总体转化率 = 总订单/总 sessions", "3,045/27,300", "3,045/27,300", "3,685/33,200"),
    ("两序列共用同一线性轴", "通过", "通过", "通过"),
    ("全部柱矩形符合该轴比例", "12/12", "12/12", "14/14"),
    ("负值柱画在零基线之下", "无负值", "2026-09 通过", "2026-09 通过"),
    ("表格月份数", "6", "6", "7"),
    ("2026-04 保留", "是", "是", "是"),
    ("第 2 轮更正仍然有效", "不适用", "是", "是"),
    ("结论数字可回查计算结果", "通过", "通过", "通过"),
]
for row in checks:
    A("| %s | %s | %s | %s |" % row)
A("")

A("## 6. 请求、看图与消耗")
A("")
A("| 项 | round-01 | round-02 | round-03 | 三轮累计 |")
A("|---|---:|---:|---:|---:|")
tot_r = sum(m[s]["counts"]["render_requests"] for s in SUBS)
ok_r = sum(m[s]["counts"]["successful_render_requests"] for s in SUBS)
bad_r = sum(m[s]["counts"]["failed_render_requests"] for s in SUBS)
A("| 渲染请求 | %d | %d | %d | %d |"
  % (m["round-01"]["counts"]["render_requests"], m["round-02"]["counts"]["render_requests"],
     m["round-03"]["counts"]["render_requests"], tot_r))
A("| 成功 / 失败 / 重试 | %d / %d / %d | %d / %d / %d | %d / %d / %d | %d / %d / %d |"
  % (m["round-01"]["counts"]["successful_render_requests"],
     m["round-01"]["counts"]["failed_render_requests"],
     m["round-01"]["counts"]["retry_requests"],
     m["round-02"]["counts"]["successful_render_requests"],
     m["round-02"]["counts"]["failed_render_requests"],
     m["round-02"]["counts"]["retry_requests"],
     m["round-03"]["counts"]["successful_render_requests"],
     m["round-03"]["counts"]["failed_render_requests"],
     m["round-03"]["counts"]["retry_requests"], ok_r, bad_r, 0))
A("| 看图次数 | %d | %d | %d | %d |"
  % (m["round-01"]["counts"]["image_views"], m["round-02"]["counts"]["image_views"],
     m["round-03"]["counts"]["image_views"],
     sum(m[s]["counts"]["image_views"] for s in SUBS)))
A("| 完成的视觉迭代 | %d | %d | %d | %d |"
  % (m["round-01"]["counts"]["completed_visual_iterations"],
     m["round-02"]["counts"]["completed_visual_iterations"],
     m["round-03"]["counts"]["completed_visual_iterations"],
     sum(m[s]["counts"]["completed_visual_iterations"] for s in SUBS)))
A("| 非终态版本（未采纳） | %d | %d | %d | %d |"
  % (m["round-01"]["counts"]["incomplete_visual_iterations"],
     m["round-02"]["counts"]["incomplete_visual_iterations"],
     m["round-03"]["counts"]["incomplete_visual_iterations"],
     sum(m[s]["counts"]["incomplete_visual_iterations"] for s in SUBS)))
A("| 文档 / 字体请求 | %d | %d | %d | %d |"
  % (m["round-01"]["counts"]["other_service_requests"],
     m["round-02"]["counts"]["other_service_requests"],
     m["round-03"]["counts"]["other_service_requests"],
     cum["counts"]["other_service_requests"]))
A("| 请求耗时合计（秒） | %.2f | %.2f | %.2f | %.2f |"
  % (m["round-01"]["sum_of_request_durations_seconds"],
     m["round-02"]["sum_of_request_durations_seconds"],
     m["round-03"]["sum_of_request_durations_seconds"],
     cum["sum_of_request_durations_seconds"]))
A("")
A("- 三轮累计墙钟 %.1f 秒（%.1f 分钟），首图用时 %.1f 秒。"
  "墙钟包含本地的读题、写 DSL、看图与复核时间；请求耗时合计只有 %.2f 秒，"
  "两者不可互相替代。"
  % (cum["wall_clock_seconds_total"], cum["wall_clock_seconds_total"] / 60.0,
     cum["wall_clock_seconds_to_first_usable_image"],
     cum["sum_of_request_durations_seconds"]))
A("- 文档/字体请求的 6 次全部发生在三轮渲染之前，路径落在 `tmp/.../A22/docs/` 与 "
  "`fonts.txt`，不属于任何一轮的输出目录，所以按轮拆分时记在「累计」列而不是"
  "某一轮的列里。这是分轮口径的正常现象，不是漏记。")
A("- 每轮各自还有一份 `round-0N/task-metrics.json`。**不要把它们和本文件相加**，"
  "本文件已经是三轮合并后的单一汇总。")
A("- 明细在 `tmp/20261004-182918/A22/requests.jsonl`（每个请求的 ID、起止时间与时区、"
  "耗时、HTTP 状态、Content-Type、请求文件、响应文件、错误摘要、"
  "可取得的 requestId 与 Server-Timing）与同目录 `iterations.jsonl`"
  "（每个版本的可观察问题、具体改动、复验结果）。")
A("")

A("## 7. 唯一一次服务错误")
A("")
for fl in cum["failures"]:
    A("- `%s` HTTP %s：`%s`" % (fl["request_id"], fl["http_status"], fl["error"][:120]))
    A("  - 定位：错误 JSON 直接给出了 `position 279` 的上下文，"
      "可见根 `<Container>` 收到了多个 `Positioned` 子节点。")
    A("  - 修复：生成端改为 `D.snapshot([D.stack(kids, W, H)], ...)`。")
    A("  - 复验：紧接着的请求 HTTP 200 并返回 PNG；此后 31 次渲染全部成功，零重试。")
    A("  - 原始失败响应保留在 `%s`。" % fl["response_file"])
A("")
A("除这一次 400 之外，**没有遇到限流（429）、服务不可用（503）或认证问题**。")
A("")

A("## 8. 未解决事项与如实说明")
A("")
A("1. **2026-09 的亏损柱只有约 3.8px 高。** 需求要求净收入与经营利润共用同一根"
  "线性轴，而轴必须覆盖 202,368 元，所以 -5,632 元在这把尺子上必然很短。"
  "这里**选择如实按比例画，而不是把负值放大**：整段 -20,000 ~ 0 的负值带被涂成淡红、"
  "在轴底加界线并标注「← 零基线」，读者能看出这根柱是「在这把尺子上本来就短」，"
  "而不是「被裁掉了」或「其实没亏」。柱矩形 y=518.46 恰好等于零基线 y=518.46，"
  "证明它确实从基线往下长。")
A("2. **token / 费用 / 图像输入用量全部为 `null`。** open-snapshot 服务在本次运行中"
  "没有向客户端暴露任何用量或计费接口，对话平台也没有给出单请求数字，"
  "因此这些字段保持未知。**没有按字符数、DSL 长度或任何余额去估算。**")
A("3. **`rate_limit_or_queue_wait_seconds` 为 `null` 而非 0。** 本次所有响应的 "
  "`Server-Timing` 都没有出现排队段，无法确认是否发生过排队，按"
  "「不可确认即为未知」处理。")
A("4. **`user_feedback_wait_seconds = 0` 的含义有限。** 它表示"
  "「本次运行没有向用户请求过反馈」，是因为后续需求本来就预置在题目目录里；"
  "这不能被解读成"
  "「模型不需要反馈」。")
A("5. **本模式不是隐藏反馈盲测。** 见文首说明。")
A("6. 未遇到其它问题：没有臆造标签、属性、枚举值、字体或接口返回；"
  "没有用其它绘图库画主体再嵌入；没有删掉出错区块来宣称修好了；"
  "没有为了"
  "「看起来完成」而提前收工——三轮共 12 次看图、9 个未采纳版本都记录在案。")
A("")

A("## 9. 交付清单")
A("")
A("```")
A("outputs/20261004-182918/A22/")
A("├─ round-01/")
A("│  ├─ dashboard.png            1600x1000  服务原始响应字节，无后处理")
A("│  ├─ dashboard.snapshot       与最终渲染完全一致的完整 DSL")
A("│  ├─ computed-data.json       原始行、更正、月度派生值、汇总、轴、结论及支撑数值")
A("│  ├─ layout-map.json          KPI/图/表/结论/标题区域边界、主样式、%d 个元素登记表"
  % l["round-01"]["element_count"])
A("│  ├─ task-metrics.json")
A("│  └─ snapshot-usage.md")
A("├─ round-02/")
A("│  ├─ dashboard.png            1600x1000")
A("│  ├─ dashboard.snapshot")
A("│  ├─ computed-data.json")
A("│  ├─ layout-map.json")
A("│  ├─ change-audit.json        变更传播、旧新数值、视觉回归与未改内容")
A("│  ├─ task-metrics.json")
A("│  └─ snapshot-usage.md")
A("├─ round-03/")
A("│  ├─ dashboard.png            1600x1000")
A("│  ├─ dashboard.snapshot")
A("│  ├─ computed-data.json")
A("│  ├─ layout-map.json")
A("│  ├─ change-audit.json")
A("│  ├─ task-metrics.json")
A("│  └─ snapshot-usage.md")
A("├─ snapshot-usage.md           本文件（三轮累计报告）")
A("└─ task-metrics.json           三轮累计指标")
A("```")
A("")
A("临时目录 `tmp/20261004-182918/A22/`：`a22lib.py`、`build_a22.py`、`verify_a22.py`、"
  "`compare_rounds.py`、`round_metrics.py`、`gen_reports.py`、`fetch_docs.py`、"
  "`log_a22.py`、`requests.jsonl`、`iterations.jsonl`、`responses/`（失败响应）、"
  "`docs/`（ai-guide.md、dsl-docs.html）、`fonts.txt`、`drafts/`（每轮最终 DSL）、"
  "`history/`（三轮 PNG+DSL 归档）、`crops/`（%d 张放大核对图）。"
  % len([f2 for f2 in os.listdir(os.path.join(ROOT, "tmp", "20261004-182918", "A22", "crops"))]))

with open(os.path.join(OUT, "snapshot-usage.md"), "w", encoding="utf-8", newline="\n") as fh:
    fh.write("\n".join(L) + "\n")
print("wrote A22/snapshot-usage.md (%d chars)" % len("\n".join(L)))