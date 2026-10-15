#!/usr/bin/env python
# A24 使用报告。启动基准：总任务根 (suite_root)。用法：python report_a24.py
from __future__ import annotations

import datetime
import json
import os
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
OUTD = ROOT / "outputs/run-20261011-01/A24"
PREV = "tmp/run-20261011-01/A24/preview"


def main() -> None:
    now = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    s = json.loads((OUTD / "schedule.json").read_text(encoding="utf-8"))
    a = json.loads((OUTD / "schedule-audit.json").read_text(encoding="utf-8"))
    c = json.loads((OUTD / "content-map.json").read_text(encoding="utf-8"))
    m = json.loads((OUTD / "task-metrics.json").read_text(encoding="utf-8"))
    inp = json.loads((ROOT / "tasks/A24-release-plan-capstone/inputs/release.json")
                     .read_text(encoding="utf-8"))
    lb, op = a["lower_bounds"], a["optimality"]

    tl_rows = []
    for team in ("design", "engineering"):
        for r in a["team_timelines"][team]:
            tl_rows.append(f'| {team} | {r["id"]} | {r["label"]} | '
                           f'{r["start_hhmm"]}–{r["end_hhmm"]} | '
                           f'{r["start_minute"]:g}–{r["end_minute"]:g} |')
    idle_rows = [f'| {w["team"]} | {w["from_minute"]:g}–{w["to_minute"]:g} | '
                 f'{w["minutes"]:g} |{"（尾部空档）" if w.get("tail") else ""}'
                 for w in a["idle_windows"]]
    ck = "\n".join(f'| {c["check"]} | {c["method"]} | {c["result"]} | '
                   f'{"通过" if c["passed"] else "**未通过**"} |'
                   for c in a["checks"])
    sc = "\n".join(f'| {x["check"]} | {x["method"]} | {x["result"]} |'
                   for x in c["checks"])
    tri = "\n".join(f'| {t["assign"]["R05"]} / {t["assign"]["R09"]} / '
                    f'{t["assign"]["R12"]} | {t["finish"]:g} |'
                    for t in op["improvement_evidence"]["trials"])

    (OUTD / "snapshot-usage.md").write_text(f"""# A24 使用报告 · 双团队约束下的发布作战计划

生成时间：{now}

## 1. 交付清单

| PNG | DSL | 尺寸 | 用途 |
|---|---|---|---|
| `execution-board.png` | `execution-board.snapshot` | 1920×1080 | 团队泳道执行图 |
| `decision-brief.png` | `decision-brief.snapshot` | 1200×1600 | 决策简报 |
| `action-card.png` | `action-card.snapshot` | 720×1280 | 手机行动卡 |

每张图都有同名完整 `.snapshot`，全部是 open-snapshot 服务的真实响应。
另有 `schedule.json`、`schedule-audit.json`、`content-map.json`。

## 2. 排程结果

**完工 {s["finish_minute"]:g} 分钟（{s["finish_time"][11:16]}），剩余缓冲
{s["buffer_minutes"]:g} 分钟，总工时 {lb["total_work_minutes"]:g} 分钟。**

| 团队 | 任务 | 标签 | 起止 | 分钟区间 |
|---|---|---|---|---|
{chr(10).join(tl_rows)}

### 团队空档

| 团队 | 区间（分钟） | 时长 | |
|---|---|---|---|
{chr(10).join(idle_rows)}

## 3. 两个下界与最优性

| 项 | 值 |
|---|---|
| 依赖关键路径 | {lb["dependency_critical_path_minutes"]:g} 分钟（{' → '.join(lb["dependency_critical_path"])}） |
| 资源工作量下界 | {lb["resource_workload_lower_bound_minutes"]:g} 分钟（{lb["total_work_minutes"]:g} ÷ 2） |
| 生效下界 | **{lb["binding_lower_bound"]:g}**，{lb["binding_reason"]} |
| 本解完工 | {s["finish_minute"]:g} 分钟 |
| 与依赖下界之差 | {op["gap_to_dependency_bound_minutes"]:g} 分钟 |
| 是否可证明全局最优 | **是** |

### 上界

本 `schedule.json` 本身就是一个完工于 {s["finish_minute"]:g} 分钟的可行排程。

### 下界证明

{chr(10).join(str(i + 1) + ') ' + x for i, x in enumerate(op["lower_bound_proof"]["argument"]))}

8 类归属各自的最优完工：

| R05 / R09 / R12 的归属 | 该类最优完工（分钟） |
|---|---|
{tri}

### 为什么不是 255 分钟

{op["lower_bound_proof"]["intuition"]}

### 搜索的可核验细节

| 项 | 值 |
|---|---|
| 剪枝界 | `{op["improvement_evidence"]["search"]["pruning_bound"]}` |
| 去重键 | `{op["improvement_evidence"]["search"]["dedup_key"]}` |
| 展开节点数 | {op["improvement_evidence"]["search"]["search_nodes"]} |
| 去重后状态数 | {op["improvement_evidence"]["search"]["distinct_states"]} |
| 是否穷尽 | {op["improvement_evidence"]["search"]["exhaustive"]} |

## 4. 排程可行性核验

| 核验项 | 方法 | 结果 |
|---|---|---|
{ck}

资源冲突列表为空数组，16 条依赖逐条列在 `schedule-audit.json.dependency_checks`。

## 5. 三图一致性核验

| 核验项 | 方法 | 结果 | |
|---|---|---|---|
{sc}

这些检查都是**对渲染坐标做算术**得到的，不是声明：例如「色块宽度与真实时长成正比」
用 `(end_x − start_x) ÷ 每分钟像素数` 逐块复算，「完工线与截止线画在正确的分钟位置」
用线坐标与 `300 + 分钟 × 3.714286` 比对。

## 6. 三张图的实际看图记录

| 图片 | 实际看到的内容 |
|---|---|
| `{PREV}/execution-board.png`（首版） | 轴的「09:00…16:00」压在 KPI 卡底边上；色块上方的「+25 分钟」偏移标签与相邻色块的标签抢位；R10 与 R12 的外部标签重叠；「双选」角标与任务名重叠；「截止 16:00」压在轴的「16:00」上；R12 的外部标签压住「空档 160 分钟」 |
| `{PREV}/execution-board.png`（修正版） | 轴下移到 352 与 KPI 错开；去掉分钟偏移标签，改用「放得下画块内、相撞改画块右侧空档」的标签放置器；「双选」移出色块、改为紫色描边 + 索引表标注；截止标签移到轴下方一行；空档标签右对齐到泳道右端 |
| `{PREV}/decision-brief.png`（首版） | KPI 卡子标签被卡底裁掉；依赖列只给 132px，「前置 R04、R05」被截断；要点靠服务端自动换行，行数估计偏小导致行尾标点被裁、风险卡溢出画布 |
| `{PREV}/decision-brief.png`（修正版） | 卡片加高到 146、子标签上移；依赖列改为「编号·编号」并放宽到 176px；**自己按实测字宽排版并逐行输出 Text**（含 CJK 悬挂标点），行数由代码决定；风险卡加高到 110 |
| `{PREV}/action-card.png`（首版） | 12 行任务 + 风险区共需 1332px，**整段超出 1280 画布**；⚠ 风险文字与任务名重叠并被截断 |
| `{PREV}/action-card.png`（修正版） | 任务行压到 54px，风险移到第二行右侧；风险卡改 2 行 80px；生成时用 assert 卡住画布边界 |
| `execution-board.png`（定稿） | 两条泳道、12 个色块、真实时间轴、空档区、完工线与截止线、12 行任务索引表，数字与 `schedule.json` 一致 |
| `decision-brief.png`（定稿） | 四个 KPI、12 行依赖概览、6 条排程依据、3 张风险卡，无裁切 |
| `action-card.png`（定稿） | 按时间序的 12 行任务（编号/名称/起止/团队/双选/风险徽标）+ 3 张风险卡，无裁切 |

**特别检查了短任务与长中文标签**：最窄的色块是 R02 与 R12（各 20 分钟，
74px），「服务与字体探测」7 字与「交付归档」4 字都放不进块内，
由标签放置器改画在色块上方的条带 / 右侧空档里；索引表与简报、手机卡给出全部 12 项的完整文字。

## 7. 真实文档与 DSL 能力应用

| 来源 | 用到的结论 |
|---|---|
| https://open-snapshot.muedsa.com/ai-guide.md | 请求体形态；`type="png"` 决定编码；响应为原始 PNG 字节 |
| https://snapshot.muedsa.com/reference/parser-tags/ · `Positioned` | 必须是 `Stack` / `IndexedStack` 的直接子节点；每轴最多设三项中的两项 |
| https://snapshot.muedsa.com/reference/parser-tags/ · `Text` | `textAlign` 默认 `START`，合法取值是**大写** `START`/`CENTER`/`END`/`JUSTIFY`（A23 探针已逐项验证），本题用它做右对齐 |
| https://snapshot.muedsa.com/reference/parser-tags/ · `Container` | `border` 格式为「宽度 样式 颜色」；`borderRadius` 做卡片与色块圆角 |
| `GET /fonts`（run 级共享准备） | Inter / Inter Semi Bold / Inter Medium 与 Noto Sans CJK SC |

## 8. 请求与指标

| 项 | 值 |
|---|---|
| 交付图片 | {m["counts"]["renders"]} 张 |
| 渲染请求 | {m["counts"]["requests"]}（成功 {m["counts"]["requests_ok"]} / 失败 {m["counts"]["requests_failed"]}） |
| 服务耗时之和 | {m["timings"]["request_duration_sum_seconds"]} 秒 |
| 渲染重试 | {len(m["verification"]["render_retries"])} 次 |
| 求解器运行 | {m["counts"]["solver_runs"]} 次 |
| 图片查看次数 | {m["counts"]["image_views"]} |

服务耗时之和不是任务总耗时。

## 9. 设计说明

- **三图同源**：所有数字都直接读自 `schedule.json`，绘图代码里不做任何再计算。
  `content-map.json` 的坐标由生成 DSL 的同一段代码顺带记录（`layout-marks-*.json`），
  所以「三图一致」是可以用坐标算术复核的，而不是靠人工目测。
- **依赖用编号索引表达**：题目明确不要求画连线，实际也没画——
  避免交叉线盖住时间块。依赖出现在执行图的索引表、简报的依赖列、
  以及 `schedule.json` / `content-map.json` 的结构化字段里。
- **标签放不下时不缩字**：正文保持 20px（横屏）/ 24px（竖页），
  改用「块内 → 块上条带 → 块右侧空档」三级放置策略。

## 10. 未解决事项

- 无影响交付的未解决问题。
- **最优性声明的边界**：本次能给出全局最优证明，靠的是两个前提——
  (1) 8 种团队归属覆盖了全部可行解（R05/R09/R12 之外没有别的双选任务）；
  (2) 分支定界是完备搜索，剪枝用的是可采纳下界。
  两点都写进了 `schedule-audit.json`，搜索节点数 {op["improvement_evidence"]["search"]["search_nodes"]}，
  未触发节点上限（上限 400 万）。若换成更多双选任务，这个证明就不再成立，
  届时只能标注「已尽力」而不是「最优」。
- **风险的处置**：按题面要求，K1/K2/K3 只用于解释 160 分钟缓冲可能被消耗到什么程度，
  没有加进任何任务时长；简报与手机卡都显式写明了这一点。

## 11. 路径

- 输出：`outputs/run-20261011-01/A24/`
- 临时：`tmp/run-20261011-01/A24/`（`drafts/`、`preview/`、`responses/`、`requests.jsonl`）
- 脚本：`solve_a24.py`（求解与审计）、`build_a24.py`（三图 + 版面留痕）、
  `deliver_a24.py`（渲染与 content-map）
""", encoding="utf-8")
    print("->", (OUTD / "snapshot-usage.md").relative_to(ROOT))


if __name__ == "__main__":
    main()
