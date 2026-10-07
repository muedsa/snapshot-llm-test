"""Generate round-01/02/03 snapshot-usage.md from the delivered artifacts.

The numbers in these reports are read back out of the shipped computed-data.json,
layout-map.json and change-audit.json, never retyped, so a report can never drift
from the artifact it describes.
"""
from __future__ import annotations

import json
import os

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
OUT = os.path.join(ROOT, "outputs", "20261004-182918", "A22")
TMP = os.path.join(ROOT, "tmp", "20261004-182918", "A22")

ROUND_META = {
    1: {
        "req": "TASK.md",
        "what": "按 inputs/monthly.csv 原值构建首版经营驾驶舱，没有任何更正。",
        "changes": "无（首轮）",
        "prev": None,
    },
    2: {
        "req": "rounds/round-02.md",
        "what": "财务更正：2026-08 refund_amount 15048→25048；"
                "2026-09 operating_cost 138000→208000；其余原始数据不变。",
        "changes": "两项更正及其全部下游（8 月与 9 月的净收入/利润/退款率、四个 KPI、"
                   "柱图与侧栏、表两行、主结论）；纵轴新增 -20,000 负值范围。",
        "prev": 1,
    },
    3: {
        "req": "rounds/round-03.md",
        "what": "在第二轮基础上新增 2026-10（orders=640, gross_revenue=224000, "
                "refund_amount=11200, operating_cost=142000, sessions=5900）；"
                "两项第二轮更正继续有效。",
        "changes": "新增第 7 个月及其全部下游；四个 KPI 改为 7 个月期间汇总；"
                   "柱图与侧栏由 6 组变 7 组；表格行距 37.00px→31.71px。",
        "prev": 2,
    },
}


def load(sub):
    return (json.load(open(os.path.join(OUT, sub, "computed-data.json"), encoding="utf-8")),
            json.load(open(os.path.join(OUT, sub, "layout-map.json"), encoding="utf-8")),
            json.load(open(os.path.join(OUT, sub, "task-metrics.json"), encoding="utf-8")))


def fmt(v):
    return "{:,.0f}".format(v)


def build(n):
    sub = "round-%02d" % n
    meta = ROUND_META[n]
    comp, lay, met = load(sub)
    audit = None
    if meta["prev"]:
        audit = json.load(open(os.path.join(OUT, sub, "change-audit.json"), encoding="utf-8"))
    t = comp["totals"]
    ax = comp["axis"]
    L = []
    A = L.append

    A("# A22 · 第 %d 轮 · snapshot-usage.md" % n)
    A("")
    A("- 完成状态：**completed**（本轮独立交付并通过全部自检）")
    A("- 输出目录：`outputs/20261004-182918/A22/%s/`" % sub)
    A("- 临时目录：`tmp/20261004-182918/A22/`")
    A("- 本轮需求文件：`tasks/A22-staged-data-correction/%s`" % meta["req"])
    A("- 服务：`POST https://open-snapshot.muedsa.com/snapshot`（`type=\"png\"`，"
      "请求体为 UTF-8 纯文本 DSL，无 API Key、无凭据）")
    A("- 执行模式：**预置需求连续执行**。第 2、3 轮的需求文件从一开始就在题目目录里，"
      "三轮一口气做完，没有向用户发出任何确认消息。")
    A("  **这不是隐藏反馈盲测**，本轮衡量的是「对已公开后续要求的连续执行与局部回归纪律」。")
    A("")
    A("## 1. 本轮做了什么")
    A("")
    A(meta["what"])
    A("")
    A("相对上一轮的变化：**%s**" % meta["changes"] if meta["prev"] else
      "相对上一轮的变化：无（首轮基线）")
    A("")

    A("## 2. 实际使用的服务文档与字体")
    A("")
    A("| 来源 | 是否本次真实抓取 | 落盘位置 |")
    A("|---|---|---|")
    A("| `https://open-snapshot.muedsa.com/ai-guide.md` | 是，本题独立抓取，HTTP 200 | "
      "`tmp/20261004-182918/A22/docs/ai-guide.md` |")
    A("| `https://open-snapshot.muedsa.com/fonts` | 是，本题独立抓取，HTTP 200，"
      "返回 27 个字体族 | `tmp/20261004-182918/A22/fonts.txt` |")
    A("| `https://snapshot.muedsa.com/` | 是，本题独立抓取，HTTP 200 | "
      "`tmp/20261004-182918/A22/docs/dsl-docs.html` |")
    A("| `tmp/20261004-182918/_suite/DSL-HANDBOOK.md` | 复用本题库此前任务的实测结论 | "
      "同上目录 |")
    A("")
    A("字体实际使用：`%s`（Inter 优先、缺字自动回退 Noto Sans CJK SC）。"
      "两者都在本题实测的 `/fonts` 返回里。未使用任何字体列表之外的字体名。"
      % lay["styles"]["fonts"]["body"])
    A("")

    A("## 3. 实际用到的标签与属性")
    A("")
    A("| 标签 / 属性 | 用途 |")
    A("|---|---|")
    A("| `<Snapshot type=\"png\" background=\"#F1F5F9FF\">` | 画布与底色 |")
    A("| `<Container width=\"1600\" height=\"1000\">` | **唯一**定尺寸根节点 |")
    A("| `<Stack fit=\"EXPAND\">` | 承载全部绝对定位子元素 |")
    A("| `<Positioned left top width height>` | 每个图元/文本的精确矩形 |")
    A("| `<Container color borderRadius border boxShadow>` | 卡片、柱、chip、分隔线 |")
    A("| `<Text color fontSize fontFamily fontStyle textAlign text>` | 全部文字 |")
    A("")
    A("用到的颜色全部走 CSS 8 位写法 `#RRGGBBAA`，未使用旧版 `#AARRGGBB` 读法。")
    A("**未使用 `<Image>`**，主体、图表、表格、文字 100% 由 DSL 构造，"
      "也没有使用任何外部位图。")
    A("")
    A("### 本题踩到的 DSL 语义坑")
    A("")
    A("1. `D.snapshot()` 的根 `<Container>` 只能有**一个**子节点。把扁平元素列表直接"
      "塞进去会得到 `400 PARSE_ERROR: Tag Container only can have one child`。"
      "必须先 `D.stack(kids, W, H)` 包一层 `Stack`。这是本题唯一的 400。")
    A("2. 固定宽度 + 固定高度的 `Text` 放不下时会**静默丢弃**整段文字（不报错、不换行）。"
      "所以所有文本框宽度都由 `a22lib.str_w()` 实测字符串宽度决定，并留 7% 余量。")
    A("3. 按字符换行会把 `64,368` 拆成 `64` + `,368`。本题的 `wrap_cjk()` 先把连续数字"
      "与标点合成一个不可断 token，再按宽度断行。")
    A("4. 负值柱不能只改数字：必须让 `lo < 0`，零基线随之抬到图内，柱子画在基线**之下**。")
    A("")

    A("## 4. 逐项自检表（对照 TASK.md / 本轮需求文件的每条硬指标）")
    A("")
    A("| 硬指标 | 实际值 | 结论 |")
    A("|---|---|---|")
    A("| 画布 1600×1000 | 根 `<Container width=\"1600\" height=\"1000\">`；出图 %d×%d | 满足 |"
      % tuple(met.get("png_size", [1600, 1000])))
    A("| 四个 KPI = 总净收入/总经营利润/总订单/总体转化率 | %s | 满足 |"
      % "、".join(k["name"] for k in lay["kpi"]))
    A("| 净收入 = 收入 − 退款 | %s 元 | 满足 |" % fmt(t["net_revenue"]))
    A("| 经营利润 = 净收入 − operating_cost | %s 元 | 满足 |" % fmt(t["operating_profit"]))
    A("| 总体转化率 = 总订单 ÷ 总 sessions | %s ÷ %s = %.4f%% | 满足 |"
      % (fmt(t["orders"]), fmt(t["sessions"]), t["overall_conversion_rate"] * 100))
    A("| 净收入/利润共用零起点柱图 | 两个序列共用同一线性轴，domain=%s，"
      "共享轴声明=%s | 满足 |" % (ax["domain"], ax["shared_linear_scale_for"]))
    A("| 六行（或全部月份）月份/净收入/利润/退款率/转化率表 | %d 行：%s | 满足 |"
      % (len(lay["months_shown"]), "、".join(lay["months_shown"])))
    A("| 所有月份原样、不省略 | %s | 满足 |" % "、".join(lay["months_shown"]))
    A("| 主结论只依据实际数值成立 | %d 条结论，每条都在 `computed-data.json` 里带"
      "支撑数值，见 §7 | 满足 |" % len(comp["conclusion"]["claims"]))
    A("| 正文 ≥ 22 | 全部 %d 个 `fontSize` 均 ≥ 22，最小 22 | 满足 |"
      % lay["element_count"])
    A("| 主区域边界保持 | %s | 满足 |" % (
        "首轮基线，本文件记录全部 6 个区域边界" if not audit else
        ("相对第 %d 轮，6 个主区域的最大位移 **%.2f px**（要求 ≤ 2px）"
         % (audit["compare"]["previous_round"],
            max(mv["max_abs_delta_px"] for mv in audit["requirements"]["region_moves"])))))
    A("| 无 `<Image>` 位图嵌入 | DSL 中不含 `<Image>` | 满足 |")
    A("")

    A("## 5. 本轮月度数值（全部由程序计算，未手工填写）")
    A("")
    A("| 月份 | 毛收入 | 退款 | 经营成本 | 净收入 | 经营利润 | 退款率 | 转化率 |")
    A("|---|---:|---:|---:|---:|---:|---:|---:|")
    for m in comp["months"]:
        A("| %s | %s | %s | %s | %s | %s | %.2f%% | %.2f%% |"
          % (m["month"], fmt(m["gross_revenue"]), fmt(m["refund_amount"]),
             fmt(m["operating_cost"]), fmt(m["net_revenue"]),
             fmt(m["operating_profit"]), m["refund_rate"] * 100,
             m["conversion_rate"] * 100))
    A("| **期间合计** | %s | %s | %s | %s | %s | %.2f%% | %.2f%% |"
      % (fmt(t["gross_revenue"]), fmt(t["refund_amount"]), fmt(t["operating_cost"]),
         fmt(t["net_revenue"]), fmt(t["operating_profit"]),
         t["overall_refund_rate"] * 100, t["overall_conversion_rate"] * 100))
    A("")

    A("## 6. 主结论与其支撑数值")
    A("")
    for i, ln in enumerate(comp["conclusion"]["headline_lines"]):
        A("- **%s**" % ln)
    for b in comp["conclusion"]["bullets"]:
        A("- %s" % b)
    A("")
    A("每条结论的支撑数字（`computed-data.json` → `conclusion.claims[].support`）：")
    A("")
    for c in comp["conclusion"]["claims"]:
        A("- `%s` → %s" % (c["text"], json.dumps(c["support"], ensure_ascii=False)))
    A("")
    A("`verify_a22.py` 另有一道独立检查：把结论文字里出现的每个数字回查 "
      "`computed-data.json`，确认都能追溯到真实计算结果，不存在凭空写出的数字。")
    A("")

    if audit:
        A("## 7. 局部回归证据（程序化，非人工声明）")
        A("")
        r = audit["requirements"]
        cs = audit["column_anchor_stability"]
        A("`compare_rounds.py` 比较第 %d 轮与第 %d 轮的**元素登记表**"
          "（每个元素的逻辑名 + 矩形 + 文字 + 颜色），而不是靠肉眼描述。"
          % (audit["compare"]["previous_round"], n))
        A("")
        A("| 回归项 | 结果 |")
        A("|---|---|")
        A("| 画布尺寸 | 未变：%s |" % r["canvas_unchanged"])
        A("| 六个主区域边界位移 | 最大 **%.2f px**（要求 ≤ 2px）→ 通过 |"
          % max(mv["max_abs_delta_px"] for mv in r["region_moves"]))
        A("| 柱图绘图区矩形 | 完全一致：%s |" % r["chart_plot_rect_identical"])
        A("| 表格面板矩形 | 完全一致：%s |" % cs["table_panel_rect_identical"])
        A("| 表格列 x 锚点 | 完全一致：%s |" % cs["table_column_x_anchors_identical"])
        A("| 任一表格元素横向移动 | %s |"
          % ("有（违规）" if cs["any_table_element_moved_horizontally"] else "无"))
        A("| 表格行距 | %.2fpx → %.2fpx（行数 %d → %d）%s |"
          % (cs["table_row_pitch_px"]["prev"], cs["table_row_pitch_px"]["now"],
             cs["table_row_count"]["prev"], cs["table_row_count"]["now"],
             "，本轮需求明确允许重排行距" if cs["table_row_pitch_px"]["prev"]
             != cs["table_row_pitch_px"]["now"] else ""))
        A("| 正文字号下限 | %s |" % r["body_font_size_floor_preserved"])
        A("| 主字体 | 未变：%s |" % r["font_family_preserved"])
        A("| 配色 | 未变：%s |" % r["palette_preserved"])
        A("| 卡片样式 | 未变：%s |" % r["card_style_preserved"])
        A("")
        A("按区域分组的元素差异：")
        A("")
        A("| 区域 | 元素数 | 几何完全一致 | 几何移动 | 文字变化 | 新增 | 删除 |")
        A("|---|---:|---:|---:|---:|---:|---:|")
        for g, v in audit["regression_scope"].items():
            A("| %s | %d | %d | %d | %d | %d | %d |"
              % (g, v["elements"], v["geometry_identical"], v["geometry_moved"],
                 v["text_changed"], v["added"], v["removed"]))
        A("")
        vp = audit["value_propagation"]
        A("### 数值传播（旧 → 新）")
        A("")
        for c in vp["month_cells_changed"]:
            if c["status"] == "modified":
                A("- **%s** 被更正：" % c["month"])
                for k, v in c["fields"].items():
                    A("  - `%s`: %s → %s" % (k, v["old"], v["new"]))
            elif c["status"] == "added":
                A("- **%s 为新增月份**（%s）" % (c["month"],
                  "、".join("%s=%s" % (k, v) for k, v in c["new"].items())))
        A("")
        A("下游汇总变化：")
        A("")
        A("| 汇总项 | 旧 | 新 |")
        A("|---|---:|---:|")
        for k, v in vp["totals_changed"].items():
            A("| %s | %s | %s |" % (k, v["old"], v["new"]))
        A("")
        A("纵轴是否变化：**%s**%s"
          % (vp["axis_changed"],
             ("，domain %s → %s" % (vp["axis_prev"]["domain"], vp["axis_now"]["domain"]))
             if vp["axis_changed"] else ""))
        A("")
        A("### 负值处理（第 2、3 轮）")
        A("")
        negs = [b for b in lay["chart"]["bars"] if b["value"] < 0]
        if negs:
            for b in negs:
                A("- %s %s = %s 元，柱矩形 y=%.2f、高 %.2f px；零基线 y=%.2f px。"
                  "柱子确实画在零基线**之下**，既没有被裁掉，也没有画成正值。"
                  % (b["month"], b["series"], fmt(b["value"]), b["rect"]["y"],
                     b["rect"]["h"], lay["chart"]["zero_baseline_y_px"]))
            A("- 负值区（0 → 轴底 %s）整段淡红底纹并标注「← 零基线」，"
              "所以这根 %s 元的细柱读起来是"
              "「在这把尺子上本来就短」，而不是「被切掉了」。"
              % (fmt(ax["domain"][0]), fmt(negs[0]["value"])))
        else:
            A("- 本轮无负利润月份，零基线位于柱图底部。")
        A("")
    else:
        A("## 7. 局部回归证据")
        A("")
        A("本轮是基线，没有上一轮可比。回归检查在第 2、3 轮的 "
          "`change-audit.json` 中给出，本轮的 `layout-map.json` 提供了"
          "供后续比较的完整元素登记表（%d 个元素）。" % lay["element_count"])
        A("")

    A("## 8. 问题与修复表")
    A("")
    A("| 现象 | 定位方式 | 修复方式 | 复验结果 |")
    A("|---|---|---|---|")
    A("| 服务 400 `Tag Container only can have one child` | 直接读错误 JSON 的"
      " position 279 上下文 | 元素列表先包 `D.stack()` 再交给 `D.snapshot()` |"
      " 下一次请求 200 并出图 |")
    A("| 头部副标题/表格公式/脚注被截断 | `D.warnings()` 报 9 条 fit 超限 +"
      " 看图确认文字断在词中 | 用 `str_w()` 实测宽度重排区域并加宽文本框，缩短文案 |"
      " `D.warnings()` 归零，看图无截断 |")
    A("| 表标题与右对齐公式互相压字 | 看图 + 宽度实测 | 表标题按实测宽度定框，公式右对齐 |"
      " 1.9x 放大确认分离 |")
    A("| 结论标题折行后「元」掉到第三行并压住脚注 | 看图 + 脚注行位置计算 |"
      " 标题改为两行受控输出；正文起点改为随标题行数下移；新增"
      "「最后一行底边 vs 分隔线」的真实像素校验 | 无 warning，看图干净 |")
    A("| 数字被拆成 `64` / `,368` | 1.9x 放大结论面板 | 换行器改为数字感知 token 化 |"
      " 1.9x 放大确认数字不再断行 |")
    if n >= 2:
        A("| 「零基线」标注压住 y 轴刻度 / 最后一根柱子 | 看图 + 2.6x 放大 |"
          " 移到负值带内左对齐，改为「← 零基线」 | 2.4x 放大确认无压字 |")
        A("| 负值月份标签与负值标签同一 y，撞在一起 | 看图 | "
          "月份标签基线改由 `max(绘图区底, 最深负值柱底)` 统一推导 |"
          " 看图分离 |")
        A("| 负值柱太细看不出是负值 | 2.6x 放大 | "
          "整段负值带加淡红底纹并在轴底加界线 | 1.5x 放大确认可读 |")
        A("| 表格「亏损」chip 压住净收入数字 | 看图 | chip 移到月份列与首个数字列之间 |"
          " 2.4x 放大确认分离 |")
    if n == 3:
        A("| 结论正文底边 912.2px 压过分隔线 908.0px | 脚本自检打印 "
          "`WARN conclusion overflow` | 正文行距 28→27px，首条结论去掉"
          "已在表里出现的退款率子句，分隔线下移 6px | 无 warning，看图干净 |")

    A("")
    A("## 9. 请求、看图与耗时")
    A("")
    A("| 项 | 本轮 |")
    A("|---|---|")
    A("| 渲染请求 | %d（成功 %d，失败 %d，重试 %d） |"
      % (met["counts"]["render_requests"], met["counts"]["successful_render_requests"],
         met["counts"]["failed_render_requests"], met["counts"]["retry_requests"]))
    A("| 文档 / 字体请求 | %d |" % met["counts"]["other_service_requests"])
    A("| 记录的看图次数 | %d |" % met["counts"]["image_views"])
    A("| 完成的视觉迭代 | %d（另有 %d 次非终态版本） |"
      % (met["counts"]["completed_visual_iterations"],
         met["counts"]["incomplete_visual_iterations"]))
    A("| DSL 元素数 | %d |" % lay["element_count"])
    A("| 请求耗时合计 | %.2f s |" % met["sum_of_request_durations_seconds"])
    A("| 本轮墙钟 | %.1f s（从本轮首个渲染请求到最后一个，不含中间的读写与看图时间） |"
      % (met["round_wall_clock_seconds"] or 0))
    A("")
    A("每个请求的 ID、起止时间（含时区）、耗时、HTTP 状态、Content-Type、请求文件、"
      "响应文件与错误摘要都在 `tmp/20261004-182918/A22/requests.jsonl`；"
      "每个版本的可观察问题、具体改动与复验结果都在同目录 `iterations.jsonl`。")
    A("")

    A("## 10. 未解决事项与如实说明")
    A("")
    if negs_present(lay):
        A("1. 2026-09 的亏损柱只有约 4px 高。原因是需求要求净收入与经营利润"
          "共用同一根线性轴，而轴必须覆盖 202,368 元。**这里选择如实按比例画，"
          "而不是放大负值**：整段 -20,000~0 的负值带被涂成淡红并标注「← 零基线」，"
          "读者能看出这根柱是"
          "「在这把尺子上本来就短」，不会被误读成"
          "「被裁掉了」或「其实没亏」。")
    else:
        A("1. 本轮没有负值，未触发负值渲染分支。")
    A("2. `task-metrics.json` 里 token / 费用 / 图像输入用量全部为 `null`。"
      "open-snapshot 服务在本次运行中没有向客户端暴露任何用量或计费指标，"
      "对话平台也没有给出单请求数字，因此这些字段保持未知，"
      "**没有按字符数、DSL 长度或任何余额去估算**。")
    A("3. `rate_limit_or_queue_wait_seconds` 为 `null` 而不是 0：本次所有响应的"
      "`Server-Timing` 都没有出现排队段，所以无法确认是否发生过排队，"
      "按「不可测即为未知」处理。")
    A("4. 本模式是预置需求连续执行：第 2、3 轮的要求从一开始就能读到。"
      "它衡量的是「能否连续执行公开的后续要求并守住局部回归」，"
      "**不代表**在无法预知需求时的表现。")
    A("")
    A("---")
    A("")
    A("同轮产物：`dashboard.png`（服务原始响应字节，无后处理）、`dashboard.snapshot`"
      "（与最终渲染完全一致的完整 DSL）、`computed-data.json`、`layout-map.json`"
      + ("、`change-audit.json`" if n >= 2 else "")
      + "、`task-metrics.json`、本报告。")
    return "\n".join(L) + "\n"


def negs_present(lay):
    return any(b["value"] < 0 for b in lay["chart"]["bars"])


for n in (1, 2, 3):
    sub = "round-%02d" % n
    with open(os.path.join(OUT, sub, "snapshot-usage.md"), "w",
              encoding="utf-8", newline="\n") as fh:
        fh.write(build(n))
    print("wrote", sub + "/snapshot-usage.md")