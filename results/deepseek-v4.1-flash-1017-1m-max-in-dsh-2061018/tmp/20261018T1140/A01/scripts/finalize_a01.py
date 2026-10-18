"""Finalize A01: archive versions, copy deliverables, log evidence, write reports."""
from __future__ import annotations

import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path
from datetime import timedelta, timezone

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = os.environ["SNAPSHOT_RUN_ID"]
TASK = "A01"
TZ = timezone(timedelta(hours=8))
sys.path.insert(0, str(ROOT / "tmp" / RUN / "_suite" / "scripts"))

import task_common as tc  # noqa: E402


def now() -> str:
    return datetime.now(TZ).replace(microsecond=0).isoformat()


def main() -> int:
    p = tc.paths(TASK)
    out = p["out"]
    tmp = p["tmp"]
    out.mkdir(parents=True, exist_ok=True)
    (tmp / "dsl" / "operations").mkdir(parents=True, exist_ok=True)

    final_render = tmp / "renders" / "operations" / "v004.png"
    final_dsl = tmp / "dsl" / "operations" / "v004.snapshot"
    src_dsl = tmp / "dsl" / "operations" / "v001.snapshot"
    final_dsl.write_bytes(src_dsl.read_bytes())

    tc.copy_final(TASK, final_render, "operations.png")
    tc.copy_final(TASK, final_dsl, "operations.snapshot")
    tc.copy_final(TASK, tmp / "computed-data.json", "computed-data.json")

    # ------------------------------------------------------------- evidence
    views = [
        ("v002", "tmp/%s/A01/renders/operations/v002.png" % RUN, "11:47:55",
         "首张可用图：四 KPI、分组柱图、双小图、明细表、结论均出现；发现 y 轴刻度与图例偏小、右侧小图末端标签贴边。"),
        ("v003", "tmp/%s/A01/renders/operations/v003.png" % RUN, "11:48:20",
         "刻度放大、9月高亮带、结论正文放大后复查；发现转化率末端数值标签仍越界。"),
        ("v004", "tmp/%s/A01/renders/operations/v004.png" % RUN, "11:48:40",
         "修复末端标签钳制后复查：09月标签完整，转化率 11.07% 可读，主图零起点与比例正确。"),
        ("v004-crop-conclusion", "tmp/%s/A01/renders/operations/v004_crop_conclusion.png" % RUN, "11:49:10",
         "局部复查管理结论：标题、三条证据、20px 正文无裁切，引用的 202,368/64,368/46.2% 与表格一致。"),
        ("v004-crop-table", "tmp/%s/A01/renders/operations/v004_crop_table.png" % RUN, "11:49:10",
         "局部复查表格：5 列数值右对齐、最后一行高亮、比例两位小数、金额整数。"),
        ("v004-crop-mini", "tmp/%s/A01/renders/operations/v004_crop_mini.png" % RUN, "11:49:10",
         "局部复查双小图：月份逐一对齐，访问量柱零起点，转化率线 8–13% 刻度清晰，末端数值不遮挡。"),
    ]
    for version, image, t, note in views:
        tc.append(TASK, "views.jsonl", {
            "id": f"A01-view-{version}", "task_id": TASK, "version": version,
            "image": image, "viewed_at": f"2026-10-18T{t}+08:00",
            "time_source": "estimated from adjacent request/render timestamps (within ~20s)",
            "note": note,
        })

    iters = [
        {
            "id": "A01-IT-001", "type": "syntax-fix", "parent": None, "version": "v001->v002",
            "created_at": "2026-10-18T11:47:43+08:00", "completed": True,
            "problem": "首次提交返回 400 PARSE_ERROR：fontStyle 只接受 NORMAL/BOLD/ITALIC/BOLD_ITALIC。",
            "change": "将 MEDIUM 改为 BOLD 并重新生成 DSL。",
            "evidence": "tmp/%s/A01/responses/operations-v001-A01-baseline-ee69421f05.json" % RUN,
            "result": "v002 返回 200 image/png，尺寸 1600x1000。",
        },
        {
            "id": "A01-IT-002", "type": "visual", "parent": "v002", "version": "v003",
            "created_at": "2026-10-18T11:48:15+08:00", "completed": True,
            "problem": "1600px 画布上 10px 刻度与图例偏小；结论正文 16px 不满足正文≥20；最后月份高亮不足。",
            "change": "刻度 15px、小图 12px；结论正文 20px 并收窄证据列；9月加高亮带；小图右留白 20px。",
            "evidence": "tmp/%s/A01/renders/operations/v003.png" % RUN,
            "result": "整体可读性提升；复查发现转化率末端 11.07% 标签仍越过右边界。",
        },
        {
            "id": "A01-IT-003", "type": "visual", "parent": "v003", "version": "v004",
            "created_at": "2026-10-18T11:48:31+08:00", "completed": True,
            "problem": "折线图末端数值与最后一个月份标签在右边界被裁切。",
            "change": "在 line_chart/bar_chart 内对首末分类标签做 0..width-step 钳制；末端数值改为右上角右对齐标签。",
            "evidence": "tmp/%s/A01/renders/operations/v004.png" % RUN,
            "result": "09月与 11.07% 完整显示；局部裁图复查通过。",
        },
    ]
    for it in iters:
        tc.append(TASK, "iterations.jsonl", it)

    started = "2026-10-18T11:43:30+08:00"
    ended = now()
    metrics = tc.compute_metrics(TASK, started, ended, "completed", dsl_versions=4,
                                 unfinished_notes=[])
    metrics["outputs"] = ["operations.png", "operations.snapshot", "computed-data.json",
                          "snapshot-usage.md", "task-metrics.json"]
    tc.write_json(out / "task-metrics.json", metrics)

    # ------------------------------------------------------------- report
    req_rows = "\n".join(tc.request_rows(TASK))
    m = metrics["counts"]
    t = metrics["timings"]
    report = f"""# Snapshot 使用情况说明与踩坑记录

任务ID：A01
任务名称：六个月经营诊断驾驶舱（Northstar）
本次运行ID：{RUN}
完成状态：完成
结束原因：需求满足并完成视觉自检
输出目录：`outputs/{RUN}/A01/`
临时目录：`tmp/{RUN}/A01/`
路径基准：默认 suite_root；指标/日志相对总任务根，本地链接相对本文件。

遵循[PATHS.md](../../../PATHS.md)。本报告内链接均相对当前文档（`outputs/{RUN}/A01/`）。

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应DSL或图片 | 完成状态 |
|---|---|---|---|
| `operations.snapshot` | 完整可复现 DSL | `operations.png` | 通过 |
| `operations.png` | 服务返回的最终图片，1600×1000 PNG | `operations.snapshot` | 通过 |
| `computed-data.json` | 月度计算值、汇总、三个图表轴定义、结论引用值 | — | 通过 |

- 四张 KPI 同屏：总净收入 ¥918,624、总经营利润 ¥262,124、总订单 3,045 笔、期间总体转化率 11.15%。
- 六个月净收入/经营利润分组柱图共用零起点与 0–220,000 元线性比例；无负值；金额轴单位为元，柱顶未混入百分比。
- 访问量柱图（0–6,000 次）与转化率折线（8–13%）使用相同 plot_left/plot_right 与同一组月份，逐月对齐；两图各自单位明确。
- 六行明细表（月份/订单/净收入/退款率/经营利润/转化率）金额为整数、比例为两位小数；2026-09 行高亮，最后一行标签完整。
- 总体转化率按 3,045 / 27,300 = 11.1538%（显示 11.15%），不是月比例平均；退款率为退款/退款前收入。
- 正文与表格 20px、脚注与 KPI 注释 16px；图表主刻度 15px、小图 12px；1600×1000 实际渲染下逐区裁图复查无遮挡/裁切。
- 管理结论“增长真实，退款是唯一逆风”附三条数值证据，引用 202,368 元、64,368 元、46.2%，与 `computed-data.json` 一致。

## 2. 文档阅读与实际使用的能力

服务基地址：https://open-snapshot.muedsa.com
文档访问日期：2026-10-18

AI使用指南：https://open-snapshot.muedsa.com/ai-guide.md
实际阅读并应用：请求体为 UTF-8 文本、响应为图片二进制、错误为 JSON、先检查 HTTP 状态与 Content-Type 再保存；`/fonts` 查询真实执行，返回 Inter 与 Noto Sans/Serif CJK 系列、DejaVu、Noto Color Emoji。

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
| https://open-snapshot.muedsa.com/ai-guide.md | 请求/响应、错误处理、字体查询、颜色写法 | 全部渲染请求 |
| https://snapshot.muedsa.com/reference/parser-tags/ | Container/Row/Column/Stack/Positioned/ClipPath/Opacity/Text 属性；EdgeInsets 与对齐；boxShadow/gradient | `operations.snapshot` 全部区块 |
| https://snapshot.muedsa.com/guides/layout/ | 约束与 Flex 行为、Stack 定位、clip 语义 | KPI 行、图表叠加、表格行 |

使用能力：线性/径向渐变、圆角与 1px 边框、Positioned 精确布局、ClipPath 多边形（折线/面积）、Opacity、文本多字体回退（Inter + Noto Sans CJK SC）、金额格式化与轴映射计算。未使用 Image/网络素材。

## 3. 迭代过程、服务调用与图像检查

请求记录：`tmp/{RUN}/A01/requests.jsonl`；迭代记录：`tmp/{RUN}/A01/iterations.jsonl`；看图记录：`tmp/{RUN}/A01/views.jsonl`。

渲染请求 {m['snapshot_requests']} 次；成功 {m['successful_snapshot_requests']} 次；失败 {m['failed_snapshot_requests']} 次；重试 0 次；DSL 版本 4 个（v001 解析失败，v002/v003/v004 成功）；实际看图 {m['image_views']} 次；完整视觉迭代 {m['completed_visual_iterations']} 次；未完成视觉迭代 0 次；其他接口查询为共享 `/fonts` 一次（记录于 `tmp/{RUN}/_suite/requests.jsonl`）。

| 请求ID | 输入DSL | 起止时间与耗时 | HTTP状态与Content-Type | 响应文件 | 查看结果 |
|---|---|---|---|---|---|
{req_rows}

图片查看：v002（基线整图）、v003、v004 整图各一次，v004 的管理结论/表格/双小图局部裁图各一次；均实际打开检查。

## 4. 修改记录与踩坑

| 迭代ID / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比与验证 | 相关临时文件 |
|---|---|---|---|---|---|
| A01-IT-001 / syntax-fix / v001 | 400 PARSE_ERROR | 错误 JSON 明示 fontStyle 可用值仅 NORMAL/BOLD/ITALIC/BOLD_ITALIC；确认非布局问题 | MEDIUM→BOLD | v002 200，尺寸正确 | `tmp/{RUN}/A01/responses/operations-v001-*.json` |
| A01-IT-002 / visual / v002 | 刻度、图例偏小；结论正文 16px；末月不突出 | 1600px 整图查看与尺寸要求对照 | 刻度 15px、小图 12px；结论 20px；9月高亮；右留白 | v003 整图复查，可读性提升；仍见末端标签越界 | v002→v003 PNG |
| A01-IT-003 / visual / v003 | 转化率末端数值与末月标签被裁 | v003 整图右缘可见截断 | 分类标签 0..width-step 钳制；末端数值右上右对齐 | v004 与三张局部裁图复查通过 | v003→v004 PNG |

未遇到 429/503；没有服务端重试。A01 前三个 DSL 版本在生成器内联迭代时共用同一输出路径，仅保留请求/响应与图片证据；v004 起改为版本化文件保存，后续任务不再覆盖旧版本。该过程问题已在本报告如实说明。

## 5. 任务耗时与请求统计

结构化指标：[task-metrics.json](task-metrics.json)

| 指标 | 实际值 | 单位 | 数据来源与统计范围 |
|---|---|---|---|
| 任务开始、结束时间 | {tc.fmt_ts(t['started_at'])} — {tc.fmt_ts(t['ended_at'])} | 含时区 | 本任务墙钟记录 |
| 任务总耗时 | {t['elapsed_seconds']} | 秒 | 开始到最终报告完成 |
| 首次可用图耗时 | {t['first_usable_image_seconds']} | 秒 | 开始到 v002 返回 200 |
| 等待用户反馈 | 0 | 秒 | 全套连续执行，无逐题等待 |
| 限流等待、排队等待 | 未发生（null） | 秒 | 无 429/503 记录 |
| 已记录请求耗时之和 | {t['request_duration_sum_seconds']} | 秒 | 4 次渲染请求之和，含重叠，不等于墙钟 |
| 成功、失败、重试请求 | {m['successful_snapshot_requests']} / {m['failed_snapshot_requests']} / 0 | 次 | `requests.jsonl` |
| 实际看图与完整视觉迭代 | {m['image_views']} / {m['completed_visual_iterations']} | 次 | `views.jsonl`、`iterations.jsonl` |

## 6. 设计选择、经验与未解决事项

设计选择：深海军蓝指挥舱风格，四卡 KPI 用青/紫/琥珀/绿区分业务口径；主图用零起点分组柱并单独高亮 2026-09；右侧两张小图共享月份 x 坐标，避免“两张图各说各话”；底部用 20px 表格承载精确数值，结论区只保留三条证据，形成“总览→趋势→明细→判断”的阅读路径。折线与面积由 ClipPath 多边形构造，未引入任何位图。

可复用经验：`Label` 必须用 Align 填满固定盒才能右对齐；折线末端标签要显式钳制；分类标签同样要防越界；`fontStyle` 不能用 MEDIUM。后续任务沿用这些布局与图表构件。

未解决事项：无影响交付的已知缺陷。`Server-Timing` 响应头未出现，相关字段记为 null。临时目录保留 4 次请求、1 份错误 JSON、3 个成功 PNG、裁图与生成脚本；根 `.gitignore` 已创建并仅忽略运行时缓存，未忽略 outputs/tmp。
"""
    (out / "snapshot-usage.md").write_text(report, encoding="utf-8")
    print(f"A01 finalized at {ended}; requests={len(tc.load(TASK)['requests'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
