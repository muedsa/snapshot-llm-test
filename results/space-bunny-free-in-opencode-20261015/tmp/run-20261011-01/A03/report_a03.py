#!/usr/bin/env python
"""生成 A03 的 snapshot-usage.md。启动基准：总任务根。"""
from __future__ import annotations

import json
import sys

sys.path.insert(0, "tmp/run-20261011-01/_suite/scripts")
import finalize_task as ft  # noqa: E402
import report_gen as rg  # noqa: E402
import suite_log as sl  # noqa: E402

TASK = "A03"
OUT, TEMP = "outputs/run-20261011-01/A03", "tmp/run-20261011-01/A03"

req_items = """
| 文件 | 用途 | 对应 DSL 或图片 | 完成状态 |
|---|---|---|---|
| `system-pulse.snapshot` | 1280×800 监控卡定稿 DSL | `system-pulse.png` | 已完成，不含任何文档未列出的属性 |
| `system-pulse.png` | 服务返回的最终图片 | `system-pulse.snapshot` | 已完成，服务原始响应 |
| `repair-log.json` | 逐项修复台账 | — | 已完成，含 10 条 issue + 7 个版本 + 4 次探针 |
| `snapshot-usage.md` / `task-metrics.json` | 报告与指标 | — | 已完成 |

需求逐项核对（依据最终图整屏 + 说明卡与 REVIEW 标签两处放大局部**实际查看**）：

| 题目要求 | 满足情况 | 证据 |
|---|---|---|
| 先原样提交一次真实服务并保存响应 | 满足 | 请求 `A03-original-unmodified-2c37559f`，HTTP 400，原始 JSON 存于 `tmp/…/A03/responses/`，输入未被修改 |
| 1280×800 | 满足 | 服务 `image_info` = 1280×800 |
| 深底 #0B1220 | 满足 | 根 Container `color="#0B1220"` |
| 安全边距 32 | 满足 | 标题 x=32、LIVE 右边界 1248、页脚 y=744 |
| 44 字号标题 | 满足 | `fontSize="44"`，图中与 28px 指标文案比例正确 |
| 第一行三个等宽指标卡 | 满足 | 每张 392×186，间距 20，总宽 1216 = 1280−64 |
| 指标文案 USAGE 72% / LATENCY 148 ms / SUCCESS 99.2% | 满足 | 三卡文案逐字一致，均为 28px |
| LIVE 标签 96×36 | 满足 | 盒子 [1152,34]–[1248,70]，恰为 96×36 |
| LIVE 不盖住标题 | 满足 | 标题盒 [32,26]–[652,86] 与 LIVE 盒矩形不相交（`live_overlaps_title=false`，几何判定已写入 repair-log） |
| REVIEW 标签 160×56 | 满足 | 盒子 [1088,676]–[1248,732] |
| REVIEW 视觉逆时针 8° | 满足 | `rot_matrix(-8)` + `Transform alignment="CENTER"`；放大图可见右端高于左端 |
| REVIEW 白底不透明度 20% | 满足 | `#FFFFFF33`（#RRGGBBAA 末位 0x33 = 20%） |
| REVIEW 文字不透明、字号 24 | 满足 | `#FFFFFF`（无 alpha）、`fontSize="24"`，放大图中清晰锐利 |
| 中央说明卡 500×150、圆角 24 | 满足 | 盒子 [390,396]–[890,546]，`ClipRRect borderRadius="24"` |
| 彩色细条同时穿过说明卡两侧边界 | 满足 | 细条 x=330..950，卡片 x=390..890，左右各外伸 60px；图中卡外锐利、卡内模糊 |
| 只模糊卡内背景，文字清晰 | 满足 | `BackdropFilter σ=12` 只包裹背景层；文字为其后的兄弟节点，放大图中文字完全清晰 |
| 说明卡显示 "Background-only blur" 28px | 满足 | 放大图逐字可读 |
| 各元素完整可见 | 满足 | 整屏与两处放大局部查看，无裁切、无溢出画布 |
| 区分真实报错/静默忽略/仅视觉暴露 | 满足 | `repair-log.json` 中每条 issue 标注 `error_class`，并附探针或图片证据 |
| 保留逐次失败稿和图片 | 满足 | r0–r4 的 DSL 与全部 400 响应 JSON 全部保留在临时目录 |
| 不把未知属性原样留在源码里 | 满足 | 定稿 DSL 已无 `font-size` / `rotate` / `Snapshot width/height`；见 `artifact_integrity` |
| 不删除出错区块 | 满足 | 出错区块逐项修复并保留在 versions 链路 r1→r4 中，非删除 |
"""

docs_rows = """
| https://open-snapshot.muedsa.com/ai-guide.md | `POST /snapshot` 纯文本 DSL；错误响应为含 `code`/`message`/`requestId` 的 JSON；按 `Content-Type` 区分成功与失败 | `_suite/scripts/snapshot_render.py` |
| https://snapshot.muedsa.com/reference/parser-tags/ · 开篇 | 「标签名和属性名区分大小写，未知属性会被忽略」 | 判定 I05（font-size）、I04（Snapshot width/height）为静默忽略类问题的直接依据 |
| 同上 · EdgeInsets | `"12"` / `"(8,16)"` / `"(8,12,16,20)"`，括号与逗号是语法的一部分 | 判定 I01 |
| 同上 · Transform | `matrix` 必填（16 个 Float、列主序、外层有括号且无空格），另有 `origin`/`alignment` | 判定 I02 |
| 同上 · Positioned | 必须是 `Stack`/`IndexedStack` 的直接子节点 | 判定 I03 |
| 同上 · 颜色 | 8 位颜色按 `#RRGGBBAA`；并特别提示旧 `#AARRGGBB` 写法会改变颜色 | 判定 I06 |
| 同上 · Snapshot | 仅 `background`/`debug`/`type`；画布尺寸由布局决定 | 判定 I04 |
| 同上 · Expanded / Container | Expanded 强制填满主轴；Container 不提供默认内边距 | 判定 I08、I09 |
| 同上 · BackdropFilter | 「读取已有背景，仍建议配合 ClipRect、ClipOval 或 ClipRRect 限定区域」 | 判定 I07 的修复方案 |
"""

capabilities = (
    "画布：`Snapshot background` + 显式根 `Container` 定尺寸。"
    "布局：`Stack(fit=EXPAND)` + `Positioned`（全部元素绝对定位）、`ClipRRect` 圆角裁剪、`Expanded` 的紧约束语义。"
    "文本：`Text` 的 `fontFamily`/`fontSize`/`textAlign`/`fontStyle`。"
    "颜色与透明度：`#RRGGBBAA`（白色 20% = `#FFFFFF33`）、`Opacity`。"
    "滤镜：`BackdropFilter`（sigmaX/sigmaY/tileMode）实现**仅背景**模糊；`ImageFiltered` 已按语义改为背景层使用。"
    "变换：`Transform` 的列主序 4×4 旋转矩阵 + `alignment=\"CENTER\"` 实现逆时针 8°。"
    "装饰：`border`、`borderRadius`、四角圆角。图片标签：未使用（纯 DSL）。"
)

request_rows = """
| 请求ID | 输入 DSL | 耗时 | HTTP | 响应 | 查看与实际结果 |
|---|---|---|---|---|---|
| A03-original-unmodified-2c37559f | tasks/…/inputs/broken.snapshot（原样） | 1.59s | 400 application/json | responses/A03-original-unmodified-2c37559f.error.json | 无图；读错误 JSON：`PARSE_ERROR Attr [padding] value format error at position 92` |
| A03-r1-padding-format-ad7c45b6 | drafts/a03-r1-padding-format.snapshot | 1.38s | 400 | responses/…r1….error.json | 无图；I01 已消，改报 `Attr [matrix] must not be null at position 475` |
| A03-r2-positioned-parent-1b88e0b6 | drafts/a03-r2-positioned-parent.snapshot | 1.66s | 400 | responses/…r2….error.json | 无图；仍是 matrix 空 |
| A03-r3-canvas-size-b109e94b | drafts/a03-r3-canvas-size.snapshot | 0.84s | 400 | responses/…r3….error.json | 无图；仍是 matrix 空 |
| A03-r4-attr-alpha-transform-f8f856b1 | drafts/a03-r4-….snapshot | 2.60s | 200 image/png | preview/a03-r4-attr-alpha-transform.png | **首次出图并实际打开**：时间轴与午休之外的问题集中暴露——指标卡被 Expanded 撑满整行、文字贴角、REVIEW 为不透明浅蓝且旋转矩阵行列式 0.34 导致文字镜像压缩、说明卡文字被模糊到不可读 |
| A03-probe-positioned-row-1e7a7993 | drafts/probe-positioned-in-row.snapshot | 16.66s | 400 | responses/A03-probe-positioned-row-….error.json | 专项探针：`RENDER_ERROR renderBox.parentData must be StackParentData`，确认 I03 是真实报错且发生在渲染期而非解析期 |
| A03-probe-backdrop-blur-a9beab27 | drafts/probe-backdrop-blur.snapshot | 2.95s | 200 image/png | preview/probe-b.png | 探针图已打开：彩色条卡外锐利卡内模糊、文字清晰、REVIEW 逆时针 8°，验证 I07/I02 的修复方案可行 |
| A03-probe-snapshot-size-837b083f | drafts/probe-snapshot-size.snapshot | 3.62s | 200 image/png | preview/probe-d.png | 探针实测输出 300×120，证明 `Snapshot width/height` 被静默忽略（I04） |
| A03-probe-fontsize-104ed42e | drafts/probe-fontsize.snapshot | 3.43s | 200 image/png | preview/probe-c.png | 探针图并排显示 `font-size` 为默认小字号、`fontSize` 为 44px（I05） |
| A03-v1-a5280f99 | drafts/a03-v1.snapshot | 2.74s | 200 image/png | preview/a03-v1.png | 已打开整屏：结构齐全；σ 说明文字与第三条彩色条重叠、脉冲条右端与 REVIEW 标签相接 |
| A03-v2-fbda825a | drafts/a03-v2.snapshot | 2.84s | 200 image/png | preview/a03-v2.png | 已打开（整屏 + 说明卡、REVIEW 放大局部）：两处缺陷消除 |
| A03-final-d1f0627f | outputs/…/system-pulse.snapshot | 2.53s | 200 image/png | outputs/…/system-pulse.png | 已打开复查，1280×800，无重叠无裁切 |
"""

change_rows = """
| 迭代 / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 修改 | 复验结果 | 文件 |
|---|---|---|---|---|---|
| r0 · baseline · — | 原样提交 400 | 服务响应 JSON | 不修改，取证 | 定位 I01 | `responses/A03-original-unmodified-2c37559f.error.json` |
| r1 · syntax-fix · r0 | `padding` 格式错误 | EdgeInsets 文档要求括号+逗号 | `padding="(24,32)"` | I01 消失，暴露 I02 | `a03-r1-padding-format.snapshot` |
| r2 · syntax-fix · r1 | Positioned 位于 Row 内 | Positioned 文档要求直接子节点为 Stack | LIVE 改由 Stack+Positioned 承载 | 服务仍先报 I02（探针已单独确认 I03 为 RENDER_ERROR） | `a03-r2-positioned-parent.snapshot` |
| r3 · syntax-fix · r2 | `Snapshot width/height` 无效 | Snapshot 属性表只有 background/debug/type；探针实测画布随布局 | 改用根 Container 显式 1280×800 | 服务仍报 I02 | `a03-r3-canvas-size.snapshot` |
| r4 · syntax-fix · r3 | `matrix` 为空（连续三次） | Transform 的 matrix 必填，且无 `rotate` 属性 | 给出合法列主序旋转矩阵 | 200 出图 | `a03-r4-attr-alpha-transform.snapshot` |
| r4 观察 · visual · r4 | 7 类静默/视觉问题（I04–I10） | 实际打开图片 + 属性表比对 + 4 次专项探针 | 见 repair-log.json 逐条 fix | — | `preview/a03-r4-attr-alpha-transform.png` |
| v1 · visual · r4 | 元素缺失、REVIEW 镜像压缩、文字被模糊 | 旋转矩阵行列式 0.34（不是旋转而是反射缩放）；ImageFiltered 包住了文字 | 用 `rot_matrix(-8)` + `alignment="CENTER"`；背景层改 BackdropFilter、文字层移出子树；补齐三卡/圆角/彩色条 | 首图结构完整 | `a03-v1.snapshot` |
| v2 · visual · v1 | σ 说明文字压在彩色条上；脉冲条与 REVIEW 相接 | 排版碰撞 | 说明文字移到卡外；脉冲条右端缩至 x=1030 | 整屏与两处放大局部通过 | `a03-v2.snapshot` |
"""

design_notes = """
**关键设计选择**

1. *先证伪再断言*。本题最容易出错的地方是把「看起来像 bug」的东西写成结论。
   因此对 I03（Positioned 父节点）、I04（Snapshot 尺寸）、I05（font-size）、
   I07（背景模糊方案）各做了一次**独立探针渲染**，用服务真实响应与实际图片确认，
   再写进 repair-log.json；探针的请求 ID 与图片路径都保留在日志中可复核。
2. *错误分类有定义*。`repair-log.json` 先给出三类定义（explicit_error / silent_ignore /
   visual_only），每条 issue 必须归入其一并附证据，避免「都算报错」或「都算视觉问题」。
3. *背景模糊用 BackdropFilter 而不是 ImageFiltered*。`ImageFiltered` 会模糊整个子树，
   文字必然跟着糊；`BackdropFilter` 只读取已绘制背景，把文字放到它之后的兄弟节点，
   才能同时满足「只模糊背景」与「文字清晰」。
4. *旋转用真实正交矩阵*。第一版修复随手写的矩阵行列式为 0.34，实际是反射+缩放，
   文字被镜像压缩——这正是「渲染成功但视觉不对」的典型。最终用 cos/sin 构造，
   屏幕坐标 y 向下时负角即视觉逆时针。
5. *LIVE 不遮标题用几何判定而非目测*。把标题盒与 LIVE 盒写进审计 JSON 做矩形相交判断，
   结论 `live_overlaps_title=false` 可被第三方复算。

**可复用经验**

- `Snapshot` 不能设宽高，画布尺寸完全由布局决定；需要固定画布时用带尺寸的根 `Container`。
- 属性名大小写与连字符敏感：`font-size` 会被静默忽略，没有任何报错。
- 8 位颜色是 `#RRGGBBAA`；想要「白色 20%」必须写 `#FFFFFF33`，`#33FFFFFF` 是不透明的浅蓝。
- `Positioned` 放在非 `Stack` 父节点下会在**渲染期**报 `renderBox.parentData must be StackParentData`，
   而不是解析期，排查时容易误判成布局问题。
- `Expanded` 是 TIGHT 约束，子节点自带 `width` 会被父约束覆盖，看起来像「宽度没生效」。
- 旋转必须同时给 `alignment="CENTER"`，否则绕子节点左上角旋转。

**结束依据**：最终图经整屏与两处放大局部实际查看，画布、颜色、边距、字号、旋转、
透明度、滤镜作用域逐项核对并写入 `repair-log.json.requirement_check`；
修复链路 r0→r4→v1→v2 的每一步都有真实响应或实际看图记录；未以「渲染成功」作为完成依据。
"""

unresolved = (
    "- 未发现影响交付的未解决问题。\n"
    "- 指标卡内的进度条与脉冲条为**演示用示意数据**（USAGE 72%、LATENCY 148 ms、SUCCESS 99.2% "
    "取自题面给定的指标文案），卡内已标注标尺，图脚也标明「数据为演示用示意值」。\n"
    "- `opacity` 属性在 `Container` 上用于脉冲条的明暗变化，属文档已列属性；"
    "若后续需要更精确的逐柱 alpha，可改用带 alpha 的颜色常量。"
)

retention = (
    "- 原始输入副本 `a03-r0-original.snapshot`、r1–r4 全部失败稿、4 次探针 DSL、"
    "全部 400 响应 JSON、成功预览与两张放大裁切图均已保留在 `tmp/run-20261011-01/A03/` 下，未删除或覆盖。\n"
    "- `tasks/A03-semantic-debugging/inputs/` 未被修改（副本按字节复制）。\n"
    "- 未保存密钥。\n"
    "- 总任务根 `.gitignore` 仅排除运行时缓存，过程证据不受影响（共享规则见 `_suite/snapshot-usage.md`）。"
)


def main():
    r = ft.root()
    m = json.loads((r / f"{OUT}/task-metrics.json").read_text(encoding="utf-8"))
    t, c = m["timings"], m["counts"]
    metrics_rows = f"""
| 指标 | 实际值 | 单位 | 数据来源与统计范围 |
|---|---|---|---|
| 任务开始 / 结束时间 | {t['started_at']} / {t['ended_at']} | ISO8601 带时区 | 计时记录 |
| 任务总耗时 | {t['elapsed_seconds']} | 秒 | 墙钟时间，含读稿、渐进修复、4 次探针、渲染与看图 |
| 首次可用图耗时 | {t['first_usable_image_seconds']} | 秒 | 从开始到 r4 首次 `200 image/png` 为止的全部请求耗时之和（串行） |
| 等待用户反馈 | 0.0 | 秒 | 单轮任务 |
| 限流等待 | 0.0 | 秒 | 全程未出现 429 |
| 排队等待 | null | 秒 | 服务未提供该指标 |
| 已记录请求耗时之和 | {t['request_duration_sum_seconds']} | 秒 | `requests.jsonl` 全部请求耗时之和；串行不重叠 |
| 成功 / 失败 / 重试请求 | {c['successful_snapshot_requests']} / {c['failed_snapshot_requests']} / {c['retry_requests']} | 次 | 5 次失败（1 原稿 + 3 渐进修复 + 1 探针）均为不同 DSL，非重试 |
| 看图 / 完整视觉迭代 | {c['image_views']} / {c['completed_visual_iterations']} | 次 | 实际打开 6 张图（r4、v1、v2、final、probe-b、probe-c）+ 2 张放大裁切 |
| DSL 版本数 | {c['dsl_versions']} | 个 | 含 4 个探针 DSL |
| Server-Timing | null | — | 服务未返回该响应头 |
"""

    md = rg.render(
        task_id=TASK, title="多层语义故障恢复", run_id=ft.run_id(),
        status="完成", stop_reason="需求满足并完成逐图视觉自检（含修复链路与探针取证）",
        out_dir=OUT, temp_dir=TEMP,
        req_items=req_items, docs_rows=docs_rows, capabilities=capabilities,
        counts={"other_queries": "字体查询与文档读取为 run 级共享准备；A03 范围内另有 4 次 DSL 语义探针（已在表 3 与 repair-log.probes 中单列）"},
        request_rows=request_rows, change_rows=change_rows, metrics_rows=metrics_rows,
        design_notes=design_notes, unresolved=unresolved, retention=retention,
    )
    print(ft.write_usage(TASK, md))


if __name__ == "__main__":
    main()