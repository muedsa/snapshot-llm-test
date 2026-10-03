"""A04 bookkeeping: iterations + tool usage + task metrics."""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "_suite", "shared"))
from suite_common import append_jsonl_nobom as A, task_tmp, task_out, write_json, build_metrics  # noqa: E402

TASK = "A04"
RUN = "20261003-114508-flashmax"
TMP, OUT = task_tmp(TASK), task_out(TASK)
for f in ("iterations.jsonl", "tool-usage.jsonl"):
    p = os.path.join(TMP, f)
    if os.path.exists(p):
        os.remove(p)

ITERS = [
    dict(version="v1", parent=None, type="baseline", dsl="conversion-story.v1.snapshot", image=None, viewed_at=None,
         issue="首版 DSL 生成完成。", change="三面板 + 核对表 + 结论 + 因果限制的初始版式。",
         result="本地发现 box() 圆角元组写法非法，未发请求。", outcome="superseded"),
    dict(version="v2", parent="v1", type="syntax-fix", dsl="conversion-story.v2.snapshot",
         image="conversion-story.v2.png", viewed_at="2026-10-03T14:40:00+08:00",
         issue="服务 400：Attr [borderRadius] value format error（元组写法）。",
         change="box() 增加元组分支，输出 borderRadiusTopLeft 等四角属性。",
         result="200。看图发现五处重叠：①图例压住 x 轴标签、②两条带的标签互压、③表头与列名互压、结论框正文换行越界、脚注压住加权复核行。",
         outcome="baseline-image"),
    dict(version="v3", parent="v2", type="visual", dsl="conversion-story.v3.snapshot", image=None, viewed_at=None,
         issue="需要重排纵向预算。", change="面板 112–394、结论 410–514、限制 526–650、表 662–842。",
         result="生成后自查发现 v3 又回退了圆角处理，未发请求即修正。", outcome="superseded"),
    dict(version="v4", parent="v3", type="syntax-fix", dsl="conversion-story.v4.snapshot",
         image="conversion-story.v4.png", viewed_at="2026-10-03T14:47:00+08:00",
         issue="同上。", change="恢复元组分支。",
         result="200。看图：①仍图例压轴、②标签仍互压、③表头仍与列名相撞、加权复核行压住脚注。",
         outcome="partial"),
    dict(version="v6", parent="v4", type="visual", dsl="conversion-story.v6.snapshot",
         image="conversion-story.v6.png", viewed_at="2026-10-03T14:53:00+08:00",
         issue="表格列宽与表头未对齐；说明文字两行。",
         change="表格列改成「边界表」一次声明（左/右边缘 + 对齐），表头与单元格共用同一份定义；面板加高到 296。",
         result="表格列对齐；②带标签仍被面板上沿裁切，④标题与说明相撞，加权复核压住脚注。",
         outcome="improved"),
    dict(version="final(v1)", parent="v6", type="visual", dsl="conversion-story.final.snapshot",
         image="conversion-story.final.png", viewed_at="2026-10-03T15:00:00+08:00",
         issue="②带高不足、④表头行拥挤、该期总体率单元格过长被截断。",
         change="面板加高到 320；②改为「前期/后期」标签在带外左侧；④去掉过宽的单元格文本只留总体率；脚注跟随表格底边。",
         result="②仍有 4px 裁切（第一带标签撞上沿）。",
         outcome="partial"),
    dict(version="final(v2..v5)", parent=None, type="visual", dsl="conversion-story.final.snapshot",
         image="conversion-story.final.png", viewed_at="2026-10-03T15:06:00+08:00",
         issue="②带高始终差几像素。",
         change="把「带+标签」改为「带内不再放标签，期名放带外侧，构成百分比合并成面板底部两行」。",
         result="②完全干净（放大核对）；④标题与说明仍相撞。",
         outcome="improved"),
    dict(version="final", parent=None, type="visual", dsl="conversion-story.final.snapshot",
         image="conversion-story.final.png", viewed_at="2026-10-03T15:12:00+08:00",
         issue="④标题行与列头同排相撞。",
         change="表格内容整体下移 24px（HY = TY + 62），列头独占一行。",
         result="最终图：三面板共用 0—40% 尺度、构成带按真实占比、四格核对表列列对齐、结论与因果限制完整；逐项核对无重叠无越界。",
         outcome="accepted"),
]
for r in ITERS:
    A(os.path.join(TMP, "iterations.jsonl"), dict(run_id=RUN, task_id=TASK, **r))

TOOLS = [
    dict(tool="read", purpose="TASK.md、AGENTS.md、task.json、inputs/conversion.csv", count=4),
    dict(tool="python", purpose="精确分数/加权公式/构成分解计算、analysis.json 与 DSL 生成", count=9),
    dict(tool="pwsh+curl.exe", purpose="11 次真实 /snapshot 请求", count=11),
    dict(tool="read_image", purpose="逐版看图 + 2 张局部放大（②面板、④表头）", count=9),
    dict(tool="Pillow", purpose="局部放大核对（zoom-p2.png、zoom-table-header.png）", count=3),
]
for t in TOOLS:
    A(os.path.join(TMP, "tool-usage.jsonl"), dict(run_id=RUN, task_id=TASK, **t))

metrics = build_metrics(
    TASK, title="分组改善与总体下降的数据解释", status="completed",
    started_at="2026-10-03T14:34:00+08:00", ended_at="2026-10-03T15:16:00+08:00",
    outputs=["conversion-story.png", "conversion-story.snapshot", "analysis.json",
             "snapshot-usage.md", "task-metrics.json"],
    final_pngs=1, dsl_versions=9,
    notes=[
        "总体率严格用总成交 ÷ 总访问：2600/10000 = 26.00%，1660/10000 = 16.60%。",
        "渠道比例算术平均 20.00%/23.50% 只在结论里作为反面例子列出，图中所有总体值都不使用它。",
        "构成分解：构成效应 -12.00pp、渠道效应 +4.40pp、交互项 -1.80pp，合计 -9.40pp（可复核）。",
        "三图共用 0—40% 尺度；构成带每期等长 252px，分段按真实份额 80/20 与 20/80。",
    ],
    extra={
        "final_image": {"file": "conversion-story.png", "width": 1600, "height": 1000, "format": "PNG", "viewed": True},
        "key_numbers": {
            "direct_rate_pct": {"前期": 30.00, "后期": 35.00},
            "promo_rate_pct": {"前期": 10.00, "后期": 12.00},
            "overall_rate_pct": {"前期": 26.00, "后期": 16.60},
            "naive_channel_average_pct": {"前期": 20.00, "后期": 23.50},
            "decomposition_pp": {"mix": -12.00, "rate": 4.40, "interaction": -1.80, "total": -9.40},
        },
        "requirements_checked": {
            "channel_grouped_rate_chart": True, "visits_mix_stacked_chart": True,
            "overall_comparison": True, "same_0_100_scale_for_rate_charts": True,
            "mix_bands_equal_length_true_proportion": True,
            "overall_is_total_conversions_over_total_visits": True,
            "no_average_of_channel_rates": True, "no_absolute_counts_as_rates": True,
            "audit_table_with_numerator_denominator": True,
            "data_backed_main_conclusion": True, "causality_limit_statement": True,
            "units_and_period_names_present": True, "body_font_min_22": True,
            "chart_labels_min_18": True, "colour_and_position_link_three_charts": True,
        },
    },
)
write_json(os.path.join(OUT, "task-metrics.json"), metrics)
print("iters", len(ITERS), "req", metrics["requests"], "it", metrics["iterations"])
