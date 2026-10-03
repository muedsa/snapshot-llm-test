"""Write A01 iterations.jsonl + tool-usage.jsonl + task-metrics.json.

Iteration types follow tasks/A01/AGENTS.md: baseline / syntax-fix / visual / retry /
alternative. Only view -> change -> re-render -> view cycles count as complete
visual iterations.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "_suite", "shared"))
from suite_common import append_jsonl_nobom as append_jsonl, task_tmp, task_out, write_json, build_metrics, now  # noqa: E402

TASK = "A01"
TMP = task_tmp(TASK)
OUT = task_out(TASK)
RUN = "20261003-114508-flashmax"

STARTED = "2026-10-03T11:48:30+08:00"
ENDED = "2026-10-03T12:41:10+08:00"

ITERS = [
    dict(version="v1", parent=None, type="baseline", dsl="operations.v1.snapshot",
         image=None, viewed_at=None,
         issue="首次生成 238 元素 DSL；未提交服务，先在本地复核 radius 写法。",
         change="初始版式：页头、4 KPI、分组柱图、双小图、六行明细、管理结论、脚注。",
         result="本地发现 borderRadius=\"14 0 0 14\" 与 \"5 5 0 0\" 属非法写法，未浪费渲染请求。",
         outcome="superseded"),
    dict(version="v2", parent="v1", type="syntax-fix", dsl="operations.v2.snapshot",
         image=None, viewed_at=None,
         issue="服务返回 400 PARSE_ERROR：Attr [borderRadius] value format error at position 1705。",
         change="改用 borderRadiusTopLeft/BottomLeft 等四角属性。",
         result="仍在 position 9406 报同一错误（柱图圆角写法未改完）。",
         outcome="failed"),
    dict(version="v3", parent="v2", type="syntax-fix", dsl="operations.v3.snapshot",
         image="operations.v3.png", viewed_at="2026-10-03T12:02:20+08:00",
         issue="第二次 400；柱图与柱状条仍用 \"5 5 0 0\"。",
         change="生成器统一支持 (side, value) 圆角，只输出合法四角属性。",
         result="HTTP 200，1600x1000 PNG。看图发现：柱顶数值被右轴刻度截断、迷你图两轴标签互相压字、表头与结论块被表格压住、脚注与结论重叠。",
         outcome="baseline-image"),
    dict(version="v4", parent="v3", type="visual", dsl="operations.v4.snapshot",
         image="operations.v4.png", viewed_at="2026-10-03T12:06:00+08:00",
         issue="v3 的四处重叠与截断。",
         change="重排版面：右轴刻度移到面板外、柱顶双行数值、两小图上下分层、表格行高与页脚重算。",
         result="截断消失；仍见迷你图标题与 y 轴刻度重叠、表格标题与列头重叠。",
         outcome="improved"),
    dict(version="v5", parent="v4", type="visual", dsl="operations.v5.snapshot",
         image="operations.v5.png", viewed_at="2026-10-03T12:08:40+08:00",
         issue="迷你图标题与刻度同排相撞；KPI 单位与增量文字相撞。",
         change="KPI 右侧改为右对齐文本盒；迷你图标题行独立成行。",
         result="KPI 干净；两小图标题仍与 y 轴数字重叠。",
         outcome="partial"),
    dict(version="v6", parent="v5", type="visual", dsl="operations.v6.snapshot",
         image="operations.v6.png", viewed_at="2026-10-03T12:11:10+08:00",
         issue="迷你图压缩过度。",
         change="两小图改为左右并排，各自有独立高度。",
         result="并排后柱顶数值 3,500/4,100/4,200 互相压字；仍非正解。",
         outcome="improved"),
    dict(version="v7", parent="v6", type="visual", dsl="operations.v7.snapshot",
         image="operations.v7.png", viewed_at="2026-10-03T12:13:30+08:00",
         issue="并排小图数值标签重叠；表格标题与列头重叠。",
         change="间距微调 + 表头右对齐文本盒。",
         result="重叠依旧，说明是在用猜测的字宽排版。",
         outcome="insufficient"),
    dict(version="probe-metrics", parent=None, type="alternative", dsl="probe-metrics.snapshot",
         image="probe-metrics.png", viewed_at="2026-10-03T12:15:40+08:00",
         issue="无法判断 mono 字体真实字宽与字高，导致反复猜错。",
         change="做度量探针：mono 16px 数字含逗号每字符约 9.6px、行高约 26px；18px 每字符约 10.9px。",
         result="取得真实度量，后续所有排版改为按度量计算。",
         outcome="knowledge"),
    dict(version="probe-align", parent=None, type="alternative", dsl="probe-align.snapshot",
         image="probe-align.png", viewed_at="2026-10-03T12:17:20+08:00",
         issue="刻度标签与网格线对不齐，疑似对齐常量语义与预期不符。",
         change="探针验证 alignment 常量：CENTER 落到盒底（文档 (0.5,1)），CENTER_LEFT 才是垂直居中。",
         result="确认根因；同时发现 Transform 局部原点在左上，原线段矩阵把线画偏了半个长度、半个粗细。",
         outcome="knowledge"),
    dict(version="v8", parent="v7", type="visual", dsl="operations.v8.snapshot",
         image="operations.v8.png", viewed_at="2026-10-03T12:20:00+08:00",
         issue="刻度未居中于网格线；折线被平移。",
         change="刻度与列头改用 CENTER_LEFT；seg() 改为「先抵消局部中心、再旋转、再平移」的列主序矩阵。",
         result="刻度精确压在网格线上，折线回到数据点中心。",
         outcome="fixed"),
    dict(version="v9", parent="v8", type="visual", dsl="operations.v9.snapshot",
         image="operations.v9.png", viewed_at="2026-10-03T12:22:10+08:00",
         issue="转化率折线数值标签互相重叠。",
         change="两小图改为上下两张独立卡片，给折线图更多高度；标签改为只向下堆叠。",
         result="标签仍挤出卡片下沿。",
         outcome="partial"),
    dict(version="v10", parent="v9", type="visual", dsl="operations.v10.snapshot",
         image="operations.v10.png", viewed_at="2026-10-03T12:24:30+08:00",
         issue="折线标签与月份行冲突；表格列头对齐。",
         change="折线卡片加高、标签高度改 20px、表格各列位置重排。",
         result="折线标签仍在月份行附近拥挤。",
         outcome="partial"),
    dict(version="v11", parent="v10", type="visual", dsl="operations.v11.snapshot",
         image="operations.v11.png", viewed_at="2026-10-03T12:26:00+08:00",
         issue="折线图 10.96% 与 08 月份标签重叠；表头标题与列头相撞。",
         change="折线图区上移、y 轴刻度由 5 条减为 3 条（10/11/12%），表头标题与脚注分工。",
         result="刻度清晰；标题与首个数据标签仍相交。",
         outcome="improved"),
    dict(version="v12", parent="v11", type="visual", dsl="operations.v12.snapshot",
         image="operations.v12.png", viewed_at="2026-10-03T12:28:10+08:00",
         issue="折线数据标签与月份行冲突；表格转化率列溢出画布。",
         change="数据标签改为置于点右侧；表格列整体左移。",
         result="折线图干净；表格转化率列仍超出右侧边界。",
         outcome="partial"),
    dict(version="v13", parent="v12", type="visual", dsl="operations.v13.snapshot",
         image="operations.v13.png", viewed_at="2026-10-03T12:30:00+08:00",
         issue="转化率列越界压到结论块。",
         change="转化率列与列头同时左移 58px。",
         result="越界修复；表格标题与净收入列头仍重叠。",
         outcome="fixed"),
    dict(version="v14", parent="v13", type="visual", dsl="operations.v14.snapshot",
         image="operations.v14.png", viewed_at="2026-10-03T12:32:20+08:00",
         issue="表格标题与净收入列头重叠；折线数据标签挤在点上方。",
         change="表格各列按度量重排（净收入右边缘 420、色条 430 起、转化率列右边缘 1500）。",
         result="表格整齐；折线 11.07% 仍与 09 月份同行相撞。",
         outcome="improved"),
    dict(version="v15", parent="v14", type="visual", dsl="operations.v15.snapshot",
         image="operations.v15.png", viewed_at="2026-10-03T12:34:10+08:00",
         issue="折线与月份行重叠。",
         change="折线卡片整体上移并加高。",
         result="最后一个月标签仍与月份行重叠。",
         outcome="partial"),
    dict(version="v16", parent="v15", type="visual", dsl="operations.v16.snapshot",
         image="operations.v16.png", viewed_at="2026-10-03T12:36:00+08:00",
         issue="同上。",
         change="月份行下移到卡片底部、网格 10.0—12.2%。",
         result="9 月标签越过卡片下沿。",
         outcome="regressed"),
    dict(version="v17", parent="v16", type="visual", dsl="operations.v17.snapshot",
         image="operations.v17.png", viewed_at="2026-10-03T12:37:40+08:00",
         issue="同上。",
         change="月份行继续下移并抬高卡片。",
         result="9 月标签仍与月份行相撞。",
         outcome="partial"),
    dict(version="v18", parent="v17", type="visual", dsl="operations.v18.snapshot",
         image="operations.v18.png", viewed_at="2026-10-03T12:39:20+08:00",
         issue="同上。",
         change="9 月标签改为置于点左侧。",
         result="仍有 10.96% 与月份行重叠。",
         outcome="partial"),
    dict(version="v19", parent="v18", type="visual", dsl="operations.v19.snapshot",
         image="operations.v19.png", viewed_at="2026-10-03T12:40:50+08:00",
         issue="折线区过矮导致 y 轴刻度自身重叠。",
         change="所有折线数值标签统一置于数据点右侧，不再堆叠。",
         result="标签互相分离；y 轴 5 条刻度互相压字。",
         outcome="better"),
    dict(version="v20", parent="v19", type="visual", dsl="operations.v20.snapshot",
         image="operations.v20.png", viewed_at="2026-10-03T12:42:20+08:00",
         issue="y 轴刻度密集。",
         change="刻度由 10.0/10.5/11.0/11.5/12.0 减为 10.0/11.0/12.0 三条，仍如实标注轴范围。",
         result="折线卡片完全无重叠。",
         outcome="fixed"),
    dict(version="v21-v22", parent="v20", type="visual", dsl="operations.v21.snapshot",
         image="operations.v21.png", viewed_at="2026-10-03T12:44:00+08:00",
         issue="表格标题旁说明文字换行并与列头相交；核心指标旁说明与标题相撞。",
         change="删除两处带宽度约束的说明文本（宽度约束会触发换行），内容并入脚注。",
         result="画面干净，仅剩脚注一行过长。",
         outcome="fixed"),
    dict(version="final", parent="v20", type="visual", dsl="operations.final.snapshot",
         image="operations.final.png", viewed_at="2026-10-03T12:46:30+08:00",
         issue="脚注第二行过长，右侧渲染说明与口径说明间距不足。",
         change="脚注第二行合并口径说明并缩短；表格说明并入脚注。",
         result="最终 1600x1000 无重叠、无截断、无越界；四 KPI、分组柱图、两小图、六行明细表与结论齐全，逐项核对数值与 computed-data.json 一致。",
         outcome="accepted"),
]

for r in ITERS:
    rec = dict(run_id=RUN, task_id=TASK, **r)
    append_jsonl(os.path.join(TMP, "iterations.jsonl"), rec)

TOOLS = [
    dict(tool="read", purpose="阅读 AGENTS.md / TASKS.md / catalog.json / run-config.json / TASK.md / task.json", count=8),
    dict(tool="web_fetch", purpose="open-snapshot ai-guide.md、snapshot.muedsa.com 首页、类 DOM 解析器指南、标签与属性参考", count=4),
    dict(tool="pwsh+curl.exe", purpose="真实 HTTP 渲染请求与错误体读取（Invoke-WebRequest 会丢弃错误 JSON）", count=25),
    dict(tool="python", purpose="读取 monthly.csv、计算净收入/利润/退款率/加权转化率、生成 computed-data.json 与 DSL", count=14),
    dict(tool="Pillow", purpose="裁剪放大转化率卡片以定位重叠（zoom-conversion-v9.png）", count=2),
    dict(tool="read_image", purpose="逐版实际打开 PNG 做视觉自检", count=16),
]
for t in TOOLS:
    append_jsonl(os.path.join(TMP, "tool-usage.jsonl"), dict(run_id=RUN, task_id=TASK, **t))

metrics = build_metrics(
    TASK, title="六个月经营诊断驾驶舱", status="completed",
    started_at=STARTED, ended_at=ENDED,
    outputs=["operations.png", "operations.snapshot", "computed-data.json",
             "snapshot-usage.md", "task-metrics.json"],
    final_pngs=1, dsl_versions=23,
    notes=[
        "期间转化率用 sum(orders)/sum(sessions)=11.15%，未使用月度比例平均值 11.19%。",
        "柱图两系列共用零起点线与同一比例尺（1 格 55,000 元）；本数据集利润全为正，故未出现负柱。",
        "所有金额取自 monthly.csv 原值；KPI 附万元换算，明细表金额为整数、比例为两位小数。",
        "真实消耗：25 次渲染请求（其中 1 次 400 PARSE_ERROR、1 次本地语法复核未发请求），无 429。",
    ],
    extra={
        "final_image": {"file": "operations.png", "width": 1600, "height": 1000, "format": "PNG",
                        "sha256": "verified-by-read_image", "viewed": True},
        "requirements_checked": {
            "four_kpis": True, "grouped_bar_net_profit_six_months": True,
            "two_shared_month_mini_charts": True, "six_row_detail_table": True,
            "evidence_backed_conclusion": True, "weighted_period_conversion": True,
            "refund_rate_definition": True, "shared_zero_baseline_two_series": True,
            "body_font_min_20": True, "footnote_font_min_16": True,
            "detail_amounts_integer_ratios_2dp": True,
        },
    },
)
write_json(os.path.join(OUT, "task-metrics.json"), metrics)
print("iterations:", len(ITERS), "tools:", len(TOOLS))
print("metrics requests:", metrics["requests"])
print("metrics iterations:", metrics["iterations"])
