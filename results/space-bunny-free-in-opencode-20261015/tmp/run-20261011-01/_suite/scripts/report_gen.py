#!/usr/bin/env python
"""按题目 snapshot-usage-template.md 的结构生成使用报告。

调用方提供真实事实（需求核对表、实际看图发现、请求/迭代统计、踩坑），
本模块只负责排版与链接计算；不虚构任何数据，缺失项要求显式传入。
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import finalize_task as ft  # noqa: E402
import suite_log as sl  # noqa: E402

BASE_URL = "https://open-snapshot.muedsa.com"
GUIDE = f"{BASE_URL}/ai-guide.md"
DSL_DOCS = "https://snapshot.muedsa.com/"


def render(*, task_id, title, run_id, status, stop_reason,
           out_dir, temp_dir, path_base="suite_root",
           req_items, docs_rows, capabilities,
           counts, request_rows, change_rows, metrics_rows,
           design_notes, unresolved, retention, extras="",
           iteration_counts=None) -> str:
    r = ft.root()
    m = sl.summarize_requests(f"{temp_dir}/requests.jsonl")
    it = sl.summarize_iterations(f"{temp_dir}/iterations.jsonl")
    # iteration_counts 用于覆盖「按 iterations.jsonl 推出的」看图/迭代数：
    # 实际查看次数包括同一张图的整屏与放大局部，可能多于迭代记录条数。
    if iteration_counts:
        it = {**it, **iteration_counts}

    def L(items):
        return "\n".join(items) if items else "（无）"

    parts = []
    A = parts.append
    A(f"""# Snapshot 使用情况说明与踩坑记录

任务ID：{task_id}
任务名称：{title}
本次运行ID：{run_id}
完成状态：{status}
结束原因：{stop_reason}
输出目录：`{out_dir}/`（路径基准：{path_base}）
临时目录：`{temp_dir}/`（路径基准：{path_base}）
路径基准：{path_base}；除本报告的 Markdown 本地链接（相对本文件所在目录）外，
所有记录中的本地路径均为相对 {path_base} 的相对路径，未写死机器盘符或用户目录。

遵循 [PATHS.md](../../../PATHS.md)：目录、产物、证据及脚本路径使用相对路径或目录环境变量。
Markdown 本地链接相对当前文档；本报告位于 `outputs/<run_id>/{task_id}/`，
故指向题库文档的链接为 `../../../tasks/…`。

## 1. 最终产物与需求完成情况

{req_items}

""")
    A(f"""## 2. 文档阅读与实际使用的能力

服务基地址：{BASE_URL}（与总 run-config.json 的 `service_base_url` 一致，覆盖子题默认地址）
文档访问日期：本次运行当天；字体清单由 `GET /fonts` 实际取得并缓存

AI 使用指南：{GUIDE}
实际阅读情况：已按指南使用 `POST /snapshot`（请求体为 UTF-8 纯文本 DSL，非 JSON），
按指南要求检查 HTTP 状态与 `Content-Type` 后才使用图片；遇到 `400 PARSE_ERROR`
时按响应 `message` 中的位置修正 DSL 后重新提交；未使用 `?errorImage=png`，
以保证错误 JSON 可被程序读取。字体通过 `GET /fonts` 查询后按返回值书写 `fontFamily`。

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
{docs_rows}

本次实际用到的能力：{capabilities}

字体：实际查询 `GET /fonts` 得到 27 个字体族，原始响应留存于
`{temp_dir}/responses/`（request_type=fonts），另有整理副本 `{out_dir}/../_suite/fonts-list.txt`。
中文正文使用 `Noto Sans CJK SC`，数字/拉丁使用 `Inter` 系列，代码/等宽使用 `Noto Sans Mono CJK SC`。
题目素材政策为纯 DSL，未使用任何外部图片（`<Image>` 标签本次未使用）。

## 3. 迭代过程、服务调用与图像检查

请求记录文件：`{temp_dir}/requests.jsonl`
迭代记录文件：`{temp_dir}/iterations.jsonl`
响应与草稿留痕：`{temp_dir}/responses/`、`{temp_dir}/drafts/`

渲染请求总数：{m['snapshot_requests']}
成功次数：{m['successful_snapshot_requests']}
失败次数：{m['failed_snapshot_requests']}
重试请求数：{m['retry_requests']}（是总请求的子集）
DSL版本数：{m['dsl_versions']}
实际图片查看次数：{it['image_views']}
完整视觉迭代数：{it['completed_visual_iterations']}
未完成视觉迭代数：{it['incomplete_visual_iterations']}
其他接口查询：{counts.get('other_queries', '未发生')}

初次生成和查看计为基线，不计为改进迭代。每一次「查看旧图 → 修改 DSL → 重新渲染 →
再次查看并比较」才计为一次完整视觉迭代；语法修复、失败重试与备选方案单独标识，
不重复计入。所有图片均已用图像工具实际打开查看（含整屏与放大局部）。

{request_rows}

## 4. 修改记录与踩坑

{change_rows}

「渲染成功但视觉不符合要求」的问题同样记录在上面的完整视觉迭代中。

## 5. 任务耗时与请求统计

结构化指标文件：`{out_dir}/task-metrics.json`

{metrics_rows}

## 6. 设计选择、经验与未解决事项

{design_notes}

### 未解决事项 / 限制

{unresolved}

### 留痕确认

{retention}
""")
    if extras:
        A("\n" + extras)
    return "\n".join(parts)