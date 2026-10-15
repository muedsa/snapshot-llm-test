#!/usr/bin/env python
"""报告生成的共享默认值：把各题重复的「文档/能力/留痕」段落集中维护。

每个题目只需提供需求核对表、请求表、修改表、指标表、设计说明与未解决事项。
"""

from __future__ import annotations

DOCS_COMMON = """
| https://open-snapshot.muedsa.com/ai-guide.md | `POST /snapshot` 请求体为 UTF-8 纯文本 DSL（非 JSON）；成功返回图片二进制；失败返回含 `code`/`message`/`requestId` 的 JSON，按 `message` 中的 `position` 定位修正；`GET /fonts` 返回 text/plain 字体族列表 | `_suite/scripts/snapshot_render.py` |
| https://snapshot.muedsa.com/reference/parser-tags/ | 38 个标签的完整属性表（`Container`/`Stack`/`Positioned`/`Text`/`Flex`/`ClipOval`/`ClipRRect`/`Transform` 等） | `snapkit.py` 与各题 DSL |
| https://snapshot.muedsa.com/reference/enums/ | 枚举取值（`CrossAxisAlignment`、`BorderStyle`、`FlexFit`、`StackFit` 等）；已确认 `BorderStyle` 仅 `NONE`/`SOLID`、`CrossAxisAlignment` 无 `BOTTOM` | 各题构造器中的枚举取值 |

字体：实际调用 `GET /fonts` 取得 27 个字体族，原始响应留存于
`tmp/<run_id>/_suite/responses/`（`request_type=fonts`），整理副本见 `tmp/<run_id>/_suite/fonts-list.txt`。
中文正文用 `Noto Sans CJK SC`，拉丁与数字用 `Inter` 系列。本套 A 类任务素材政策为 `dsl_only`，
全部主体由 DSL 构造，**未使用 `<Image>` 标签**，未引入任何外部图片素材。
"""

CAPS_COMMON = (
    "布局：`Container`/`Column`/`Row`/`Expanded`/`SizedBox`/`Padding`；"
    "精确定位：`Stack(fit=EXPAND)` + `Positioned`；"
    "文本：`Text` 的 `fontFamily`/`fontSize`/`textAlign`/`height`/`maxLines`/`letterSpacing`；"
    "颜色与透明度：CSS 颜色与 `#RRGGBBAA` 独立 alpha；"
    "装饰：`border`（宽度+样式+颜色）、`borderRadius` 与四角圆角、`boxShadow`；"
    "裁剪：`ClipRRect`/`ClipOval`；变换：`Transform` 的列主序 4×4 矩阵 + `alignment`；"
    "滤镜：`ImageFiltered`（子树模糊）、`BackdropFilter`（仅背景模糊）；"
    "渐变：`gradientType=LINEAR/RADIAL/SWEEP` + `gradientColors`/`gradientStops`。"
    "解析器未提供 `ClipPath`/多边形，所有图形均由矩形、圆角矩形、椭圆与渐变拼装。"
)

RETENTION_COMMON = (
    "- 临时目录中的草稿 DSL、各次请求体副本、成功图片、失败响应 JSON、"
    "放大裁切图与预览全部保留，未删除或覆盖任何一次尝试；日志为追加写入。\n"
    "- `tasks/` 下的输入文件、任务说明与模板均未被修改。\n"
    "- 未保存任何密钥；`SNAPSHOT_API_KEY` 若存在只从环境变量读取，不写入 DSL 或日志。\n"
    "- 总任务根 `.gitignore` 已创建（参考 `templates/gitignore-template.txt`），仅排除 "
    "`__pycache__/`、`*.pyc`、`*.pyo`、`.pytest_cache/`、`.mypy_cache/`、`.ruff_cache/`、"
    "`.ipynb_checkpoints/`、`node_modules/.cache/` 等明确的运行时缓存；"
    "**未**使用 `tmp/`、`outputs/`、`cache/`、`.cache/`、`*.log` 或图片/DSL/JSON 通配规则，"
    "因此本任务的过程证据不会被忽略（共享规则详见 `_suite/snapshot-usage.md`）。\n"
    "- `__pycache__/` 等运行时缓存不作为留痕材料，也不列为产物或自检证据。"
)


def iter_table(rows):
    """把 (版本, 类型, 问题, 修改, 结论) 元组列表渲染成 Markdown 表。"""
    head = ("| 版本 / 类型 | 观察到的实际问题 | 原因及确认依据 | 实际修改 | 复验结果 |\n"
            "|---|---|---|---|---|")
    body = "\n".join(f"| {a} | {b} | {c} | {d} | {e} |" for a, b, c, d, e in rows)
    return head + "\n" + body


def req_table(rows):
    """(请求ID, DSL, 耗时, HTTP, 响应, 查看结果) -> Markdown 表。"""
    head = ("| 请求ID | 输入 DSL | 耗时 | HTTP / Content-Type | 响应文件 | 查看与实际结果 |\n"
            "|---|---|---|---|---|---|")
    body = "\n".join(f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[5]} |" for r in rows)
    return head + "\n" + body


def metrics_table(metrics, *, started_note="计时记录（本地时钟，带时区）"):
    t, c = metrics["timings"], metrics["counts"]
    return f"""
| 指标 | 实际值 | 单位 | 数据来源与统计范围 |
|---|---|---|---|
| 任务开始 / 结束时间 | {t['started_at']} / {t['ended_at']} | ISO8601 带时区 | {started_note} |
| 任务总耗时 | {t['elapsed_seconds']} | 秒 | 墙钟时间（读题 → 计算 → 构造 → 渲染 → 看图 → 修复 → 报告） |
| 首次可用图耗时 | {t['first_usable_image_seconds']} | 秒 | 从开始到首个 `200 image/png` 且能打开的图为止的全部请求耗时之和；本任务请求串行，故与实际顺序一致 |
| 等待用户反馈 | {t['user_feedback_wait_seconds']} | 秒 | 本题为单轮任务，无多轮反馈等待 |
| 限流等待 | {t['rate_limit_wait_seconds']} | 秒 | 全程未出现 `429`（见 `requests.jsonl`） |
| 排队等待 | {t['queue_wait_seconds']} | 秒 | 服务未提供排队指标，不可测量，记 null 而非 0 |
| 已记录请求耗时之和 | {t['request_duration_sum_seconds']} | 秒 | `requests.jsonl` 中 `duration_seconds` 求和；请求串行，不与墙钟重复计入 |
| 成功 / 失败 / 重试请求 | {c['successful_snapshot_requests']} / {c['failed_snapshot_requests']} / {c['retry_requests']} | 次 | `requests.jsonl`；失败均为不同 DSL 的语法修复，非同一请求重试 |
| 看图 / 完整视觉迭代 | {c['image_views']} / {c['completed_visual_iterations']} | 次 | `iterations.jsonl` 与实际图像查看记录 |
| DSL 版本数 | {c['dsl_versions']} | 个 | `requests.jsonl` 去重 |
| Server-Timing | null | — | 服务响应未返回该头，日志中如实记为 null |
"""


def artifact_table(files, purpose_col="用途"):
    head = f"| 文件 | {purpose_col} | 对应 DSL 或图片 | 完成状态 |\n|---|---|---|---|"
    body = "\n".join(f"| `{a}` | {b} | {c} | {d} |" for a, b, c, d in files)
    return head + "\n" + body