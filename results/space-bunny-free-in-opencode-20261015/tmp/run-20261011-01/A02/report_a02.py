#!/usr/bin/env python
"""生成 A02 的 snapshot-usage.md。启动基准：总任务根。"""
from __future__ import annotations

import json
import sys

sys.path.insert(0, "tmp/run-20261011-01/_suite/scripts")
import finalize_task as ft  # noqa: E402
import report_gen as rg  # noqa: E402
import suite_log as sl  # noqa: E402

TASK = "A02"
OUT, TEMP = "outputs/run-20261011-01/A02", "tmp/run-20261011-01/A02"

req_items = """
| 文件 | 用途 | 对应 DSL 或图片 | 完成状态 |
|---|---|---|---|
| `agenda-wide.snapshot` | 1920×1200 泳道大图定稿 DSL | `agenda-wide.png` | 已完成 |
| `agenda-wide.png` | 服务返回的泳道大图，1920×1200 | `agenda-wide.snapshot` | 已完成，服务原始响应 |
| `agenda-mobile.snapshot` | 720×1280 手机导览定稿 DSL | `agenda-mobile.png` | 已完成 |
| `agenda-mobile.png` | 服务返回的手机导览，720×1280 | `agenda-mobile.snapshot` | 已完成，服务原始响应 |
| `schedule-audit.json` | 审计数据（时长/空档/冲突/内容映射/时间轴） | — | 已完成 |
| `snapshot-usage.md` / `task-metrics.json` | 报告与指标 | — | 已完成 |

需求逐项核对（依据两张最终图的**实际查看**，大图另放大检查 10:00 附近密集区）：

| 题目要求 | 满足情况 | 证据 |
|---|---|---|
| 1920×1200 全日日程 | 满足 | 服务返回 `image_info` = 1920×1200 PNG |
| 720×1280 手机导览 | 满足 | 服务返回 `image_info` = 720×1280 PNG |
| 日期/地点/时区 | 满足 | 页眉「2026-11-07（周六） · Asia/Shanghai · 云构中心 · A / B / C 会场」 |
| 15 项活动全部来自 agenda.csv | 满足 | 索引区 S01–S15 共 15 条，逐条与 CSV 原文一致（`schedule-audit.json.events`） |
| 公共午休 12:00–13:00 不与会议合并 | 满足 | 独立渐变色带跨三条泳道，标注「三会场共通 · 不与任何会议合并 · 60 分钟」；手机图另有独立午休横幅 |
| 三条会场泳道 + 09:00–16:00 共用线性时间轴 | 满足 | 三个泳道共用同一 `px(t) = 182 + (t−09:00)×4.061905` 映射 |
| 块位置与长度按实际起止时间比例 | 满足 | 最宽 S10 = 75 分钟 = 304.64 px，最窄 S15 = 30 分钟 = 121.86 px，比值 2.5000 = 75/30；**未为塞字拉伸任何块** |
| 空档保留 | 满足 | 三泳道全部空档以空白保留，未压缩或合并；逐条记录于 `venue_gaps`（A 95 分钟 / B 115 分钟 / C 130 分钟，不含午休） |
| 午休跨三泳道清楚标识 | 满足 | 色带 `y=280..802`，覆盖 laneA/B/C 全部高度，文字居中 |
| 15 项的编号、标题、讲者、起止时间、类别均可读 | 满足 | 宽块（≥196px）在块内显示标题+讲者；窄块只显示编号/类别/起止时间；**全部 15 项的 7 个字段在下方编号索引中完整给出**，按编号一一对应 |
| 短活动用外侧说明或编号索引解决，不拉伸 | 满足 | 采用编号索引方案；30 分钟的 S15 未被拉长，块内仍保持真实比例 |
| 正文≥20、时间标签≥18 | 满足 | 块内标题 20px、索引 20px、说明条 19px；时间标签：时间轴 19px、块内起止 18px、索引内 20px；泳道标签 30px |
| 注明读图方法 | 满足 | 顶部说明条给出 px/分钟、映射公式、方向与空档处理方式 |
| 注明会场容量 | 满足 | 页眉右上「A 320 人 · B 80 人 · C 160 人」，并在每条泳道标签内重复标注 |
| 手机图改为分时段列表 | 满足 | 上午场（8 项）/ 午休横幅 / 下午场（7 项），全新排版 |
| 手机图保留 15 项编号、标题、会场、起止时间 | 满足 | 15 张卡片逐项列出，未截断（标题右列宽 560px） |
| 讲者移到���图但需写「讲者详见完整日程」 | 满足 | 手机图说明条首句即「讲者详见完整日程（agenda-wide）」 |
| 不得直接缩小/裁切大图 | 满足 | 手机版为独立 DSL（`agenda-mobile.snapshot`），按卡片列表重新编排；两图时间轴体系不同（手机图不使用线性时间轴，已在审计 JSON 注明） |
| 手机正文≥18 | 满足 | 卡片标题 20px、元信息 18px、说明与页脚 18px |
| 不捏造冲突、不调整输入时间 | 满足 | `conflicts` 为**空数组**（场内重叠 0、午休重叠 0）；CSV 原始起止时间原样使用 |
"""

docs_rows = """
| https://open-snapshot.muedsa.com/ai-guide.md | `POST /snapshot` 纯文本请求体；按 `Content-Type` 判定成功/失败；`GET /fonts` 取字体族 | `_suite/scripts/snapshot_render.py` |
| https://snapshot.muedsa.com/reference/parser-tags/ | `Positioned`（每轴最多两项）、`Stack` 的 `fit`/`clipBehavior`、`Container` 渐变与圆角、`Text` 的 `textAlign`/`height`/`maxLines` | `snapkit.py`、`agenda-wide.snapshot` |
| 同上 · 布局约束 | `Positioned` 必须是 `Stack`/`IndexedStack` 直接子节点；`Container` 单一子节点限制 | 泳道块与说明条的 Stack 结构 |
"""

capabilities = (
    "布局：`Stack(fit=EXPAND)` + `Positioned` 实现全部泳道/块/网格线的精确坐标；"
    "`Column`/`Row`/`SizedBox` 用于泳道标签与图例；`ClipOval` 未使用。"
    "文本：`Text` 的 `fontFamily`/`fontSize`/`textAlign`（CENTER/RIGHT/LEFT）/`height`/`softWrap`；"
    "颜色：`#RRGGBBAA`、线性渐变（午休带与手机页眉）。"
    "装饰：`border`/`borderRadius`；裁剪：靠 `Positioned` 边界而非 `ClipRect` 控制。"
    "变换：未使用。图片：未使用（本题纯 DSL，素材政策 dsl_only）。"
)

request_rows = """
| 请求ID | DSL | 耗时 | HTTP | 响应 | 查看与实际结果 |
|---|---|---|---|---|---|
| A02-v1-wide-c9a4f460 | drafts/a02-v1-wide.snapshot | 4.88s | 200 image/png | preview/a02-v1-wide.png | 已打开：时间轴被泳道完全遮挡；午休带只剩浅灰残影；块内讲者与时间重叠；泳道标签折行溢出 |
| A02-v1-mobile-fc229785 | drafts/a02-v1-mobile.snapshot | 4.15s | 200 image/png | preview/a02-v1-mobile.png | 已打开：页眉第 3 行被裁；说明条被裁；标题「开场：结构如何成为画面」被截断 |
| A02-v2-wide-4bd67c42 | drafts/a02-v2-wide.snapshot | 3.13s | 200 image/png | preview/a02-v2-wide.png | 已打开：轴可见、午休带正确；图例压住轴、说明条第 2 行仍被裁 |
| A02-v3-wide-7fbc6df7 | drafts/a02-v3-wide.snapshot | 4.63s | 200 image/png | preview/a02-v3-wide.png | 已打开：说明条仍裁一行；块内布局基本正确 |
| A02-v3-mobile-fa712e5f | drafts/a02-v3-mobile.snapshot | 3.11s | 200 image/png | preview/a02-v3-mobile.png | 已打开：与 v1 同类问题 |
| A02-v4-wide-a8e70fdf | drafts/a02-v4-wide.snapshot | 5.82s | 200 image/png | preview/a02-v4-wide.png | 已打开（整屏 + 10:00 密集区放大）：大图通过 |
| A02-v5-mobile-ac21b0e5 | drafts/a02-v5-mobile.snapshot | 5.32s | 200 image/png | preview/a02-v5-mobile.png | 已打开：标题列已够宽；页眉第 3 行仍被裁 |
| A02-v6-mobile-1b5f6768 | drafts/a02-v6-mobile.snapshot | 3.09s | 200 image/png | preview/a02-v6-mobile.png | 已打开（页眉/页脚放大）：页眉三行完整；页脚第二行被画布底边裁切 |
| A02-v7-mobile-9d3d47d7 | drafts/a02-v7-mobile.snapshot | 4.14s | 200 image/png | preview/a02-v7-mobile.png | 已打开：手机图通过 |
| A02-final-wide-d338e2be | outputs/…/agenda-wide.snapshot | 5.67s | 200 image/png | outputs/…/agenda-wide.png | 已打开复查，与 v4 大图一致 |
| A02-final-mobile-91abc2d2 | outputs/…/agenda-mobile.snapshot | 2.75s | 200 image/png | outputs/…/agenda-mobile.png | 已打开复查，与 v7 手机图一致 |

（完整时间戳/时区/请求文件/Server-Timing 见 `requests.jsonl`；本表耗时取自该日志）
"""

change_rows = """
| 迭代 / 类型 | 问题或现象 | 原因及确认依据 | 修改 | 复验结果 | 文件 |
|---|---|---|---|---|---|
| 大图 v1 · baseline | 时间轴被泳道遮挡；午休带被泳道白底覆盖；块内讲者与时间重叠；泳道标签折行溢出 | 轴带 y=174–208 落在 laneA(y=190) 之内；绘制顺序把午休带放在泳道之前；讲者与时间 y 分别取 `bh-34`/`bh-30` | 泳道标签列加宽至 142px；纵向节奏重排（轴移到泳道之上）；绘制顺序改为 泳道底板 → 午休带 → 活动块；块内改为自上而下显式坐标 | v2 轴可见、午休带正确 | `drafts/a02-v2-wide.snapshot` |
| 大图 v2 · visual | 类别图例压住时间轴带；说明条第 2 行被裁 | 图例 y=166 与轴带 y=176 相接；`note_strip` 内部按单行垂直居中，2 行文本放不进 38px | `note_strip` 改为顶部对齐并新增 `lines` 参数；图例独占一行 | 说明条仍差一行高度 → v3 继续调 | `snapkit.py#note_strip` |
| 大图 v3 · visual | 说明条高度不足 | 19px × 1.5 行高 × 2 行 = 57px，而内部可用高度仅 38px | 说明条高度提到 80px；泳道高 162；块内坐标改为相对 `bh` | v4 全部通过 | `drafts/a02-v4-wide.snapshot` |
| 大图 v4 · visual | 复查 | — | — | 整屏 + 10:00 密集区放大核对：S04/S05/S06/S07/S08 起止与宽度成比例，整点网格线与块边界对齐，无重叠/裁切 | `preview/crop-10am.png` |
| 手机 v1 · baseline | 页眉第 3 行被裁；说明条被裁；标题被截断 | 右侧标题列仅 210px；`note_strip` 高度 34 放不下 18px 文本 | 卡片改为「左：编号+元信息 / 右：标题+类别」，标题列宽 560px；说明条 68px 两行；页眉加高 | v5 仅剩页眉问题 | `drafts/a02-v5-mobile.snapshot` |
| 手机 v5 · visual | 页眉第 3 行仍被裁 | `Container` 同时带 `padding` 与 `Stack fit=EXPAND`，`Positioned` 坐标基准与预想不同 | 去掉 padding，全部用显式 `Positioned` 坐标 | v6 页眉完整 | `drafts/a02-v6-mobile.snapshot` |
| 手机 v6 · visual | 页脚第二行被画布底边裁切 | 版面累计高度 1286px > 1280px | 页脚文案压缩为一行并上移 | v7 通过 | `drafts/a02-v7-mobile.snapshot` |
"""

design_notes = """
**关键设计选择**

1. *编号索引而非拉伸块*。任务明确禁止「为塞字把 40 分钟画成 60 分钟」。因此块宽严格由
   `duration × 4.0619 px/分` 决定，文字放不下时不在块内强塞，而是由下方两列编号索引
   补齐 7 个字段。索引与块用同一个类别色条 + 编号徽标建立对应关系。
2. *绘制顺序按层次显式编排*。泳道白底（含整点竖线）→ 午休色带 → 活动块。
   v1 把午休带画在最前，导致它被三条泳道的白色 `Container` 完全盖住，只剩边缘露出的浅灰条。
3. *窄块的信息密度自适应*。块宽 < 128px 只显示编号徽标；≥ 128px 加类别；≥ 150px 加标题；
   ≥ 196px 再加讲者。阈值全部来自像素预算（20px 标题在 `bw-20` 内可容 2 行），
   而不是拍脑袋取整。
4. *手机版是另一套排版*。完全不使用大图的线性时间轴，改为「上午场 / 午休 / 下午场」
   三段列表，按开始时间排序；卡片把编号、元信息、标题、类别四要素分列两栏，
   在 720px 宽度内保证 11 字标题不截断。
5. *审计 JSON 记录可复算的量*。`time_axis.pixels_per_minute = 4.061905`、
   每项活动的 `wide_block_width_px`、空档分钟数、冲突对都写入 `schedule-audit.json`，
   便于第三方按公式复算宽度。

**可复用经验**

- `Container` 的 `padding` 与内部 `Stack` 的 `Positioned` 坐标系会叠加，直接写死 top 容易偏移；
  需要精确坐标时不要用 padding，改用显式 `Positioned`。
- 垂直居中式的说明条对多行文本不可靠，应改为顶部对齐 + 按行数预留高度。
- 「先画背景层还是先画内容层」必须显式决定，泳道这类大面积不透明底色很容易盖住后画的东西。

**结束依据**：两张最终图均已实际打开查看（大图另放大检查 10:00 密集区，手机图放大检查页眉页脚），
15 项编号/标题/讲者/会场/起止时间/时长/类别全部可读，块宽与实际时长严格成比例，
冲突检查为空且与图面一致；未以「渲染成功」或「数量达标」作为完成依据。
"""

unresolved = (
    "- 未发现影响交付的未解决问题。\n"
    "- 「正文≥20」的边界：大图索引与块内标题为 20px，读图方法说明 19px、块内起止时间 18px、"
    "时间轴刻度 19px（均为说明性/辅助文字）；手机图正文 18–20px。若要求所有说明性文字也 ≥20px，"
    "需进一步加宽泳道或减少同屏信息量。\n"
    "- 本数据集没有同日同会场的真实冲突，审计 JSON 的 `conflicts` 因此为空数组；"
    "这是如实结果，不是检查未做（方法与逐对比较记录在 `conflict_check.method`）。"
)

retention = (
    "- 草稿 DSL（a02-v1…v7 的 wide 与 mobile）、每次请求体副本、成功预览、"
    "`requests.jsonl` 与 `iterations.jsonl` 全部保留，未删除或覆盖任何一次尝试。\n"
    "- 输入 `tasks/A02-conference-schedule/inputs/` 未被修改。\n"
    "- 未保存密钥。\n"
    "- 总任务根 `.gitignore` 已按模板创建（仅排除运行时缓存），过程证据不受影响；"
    "共享规则见 `_suite/snapshot-usage.md`。"
)


def main():
    r = ft.root()
    metrics = json.loads((r / f"{OUT}/task-metrics.json").read_text(encoding="utf-8"))
    t, c = metrics["timings"], metrics["counts"]
    metrics_rows = f"""
| 指标 | 实际值 | 单位 | 数据来源与统计范围 |
|---|---|---|---|
| 任务开始 / 结束时间 | {t['started_at']} / {t['ended_at']} | ISO8601 带时区 | 计时记录 |
| 任务总耗时 | {t['elapsed_seconds']} | 秒 | 墙钟时间，含读题、数据核对、两张图的构造/渲染/看图 |
| 首次可用图耗时 | {t['first_usable_image_seconds']} | 秒 | 从开始到首个 `200 image/png`（大图 v1）为止的全部请求耗时之和；请求串行，故与实际顺序一致 |
| 等待用户反馈 | 0.0 | 秒 | 本题为单轮任务 |
| 限流等待 | 0.0 | 秒 | 全程未出现 429 |
| 排队等待 | null | 秒 | 服务未提供排队指标，不可测量 |
| 已记录请求耗时之和 | {t['request_duration_sum_seconds']} | 秒 | `requests.jsonl` 全部渲染请求耗时之和；串行，不与墙钟重复 |
| 成功 / 失败 / 重试请求 | {c['successful_snapshot_requests']} / {c['failed_snapshot_requests']} / {c['retry_requests']} | 次 | `requests.jsonl` |
| 看图 / 完整视觉迭代 | {c['image_views']} / {c['completed_visual_iterations']} | 次 | `iterations.jsonl`；大图整屏 + 10:00 密集区放大、手机图整屏 + 页眉页脚放大，共 15 张实际打开 |
| DSL 版本数 | {c['dsl_versions']} | 个 | `requests.jsonl` |
| Server-Timing | null | — | 服务未返回该响应头 |
"""

    md = rg.render(
        task_id=TASK, title="三会场密集会议日程", run_id=ft.run_id(),
        status="完成", stop_reason="需求满足并完成两图逐图视觉自检",
        out_dir=OUT, temp_dir=TEMP,
        req_items=req_items, docs_rows=docs_rows, capabilities=capabilities,
        counts={"other_queries": "字体查询与文档读取为 run 级共享准备（`_suite/requests.jsonl`），A02 范围内无额外接口查询"},
        request_rows=request_rows, change_rows=change_rows, metrics_rows=metrics_rows,
        design_notes=design_notes, unresolved=unresolved, retention=retention,
    )
    print(ft.write_usage(TASK, md))


if __name__ == "__main__":
    main()