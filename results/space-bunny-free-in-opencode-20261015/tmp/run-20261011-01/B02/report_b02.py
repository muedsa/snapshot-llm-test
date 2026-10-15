#!/usr/bin/env python
# B02 使用报告：从交付产物读真实数据。
# 启动基准：总任务根 (suite_root)。用法：python report_b02.py
from __future__ import annotations

import datetime
import json
import os
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
OUTD = ROOT / "outputs/run-20261011-01/B02"
PREV = "tmp/run-20261011-01/B02/preview"


def main() -> None:
    now = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    pf = json.loads((OUTD / "portfolio.json").read_text(encoding="utf-8"))
    ds = json.loads((OUTD / "design-system.json").read_text(encoding="utf-8"))
    tm = json.loads((OUTD / "touchpoint-map.json").read_text(encoding="utf-8"))
    mt = json.loads((OUTD / "task-metrics.json").read_text(encoding="utf-8"))

    tbl = "\n".join(f'| {c["id"]} | {c["title"]} | {c["touchpoint"]} | '
                    f'{c["size"]["width"]}×{c["size"]["height"]} | '
                    f'{c["min_body_font_px"]}px |' for c in pf["cases"])
    fixlist = "\n".join(f'{i}. {x}' for i, x in
                        enumerate(ds["density_stress_test"]["found_and_fixed"], 1))

    (OUTD / "snapshot-usage.md").write_text(f"""# B02 使用报告 · 为「旧物仓」构建的视觉生态

生成时间：{now}

## 1. 完成状态

十件独立完整主作品已交付，全部是 open-snapshot 服务的真实响应，各有同名 `.snapshot`：

| 用例 | 标题 | 触点 | 尺寸 | 正文最小字号 |
|---|---|---|---|---|
{tbl}

另交付 `project-brief.md`（项目问题分析）、`design-system.json`（系统规则）、
`touchpoint-map.json`（触点与旅程映射）、`portfolio.json` / `portfolio.md` /
`gallery.md` 与本报告。

## 2. 项目与视觉系统

项目：**旧物仓 · 邻里共享**——社区共享物品站，无押金 + 6 件信用额度。
十件覆盖九段旅程（见 `touchpoint-map.json`），每件对应一个**互不重复**的用户情境。

系统规则五条，全部写在 `design-system.json`：

1. 每件都有**标签条**（编号 + 分类徽标 + 状态点）；
2. **状态只有五种**，颜色是唯一编码，跨十件不出现第二套状态色；
3. **分类色与状态色互不重叠**，分别编码「是什么」和「怎么样」；
4. **页脚统一署名**与示例数据说明；
5. **只用圆角矩形、细分割线与状态色块**，不引入插画、不使用 `<Image>`。

## 3. 密度与比例的压力测试

同一套组件在**字号 16px–96px（跨度 6 倍）**与 4 列高密度下都成立。
`case-04`（工具墙目录，4×9=36 格）是密度最高的一件，`case-06`（560px 宽推送）
是最窄的一件，`case-01`（门头 96px 标题）是字号最大的一件。

实际看图后发现并修掉的问题：

{fixlist}

## 4. 逐件看图记录

| 图片 | 实际看到的问题 | 处理 |
|---|---|---|
| `preview/tp-03.png` | 首轮即通过：六条规则、逾期时间条、页脚均正常 | 直接采用 |
| `preview/tp-06.png` | 最窄的一件：560px 下标签条与胶囊都成立，但**页脚说明行掉出画布底边**（竖排两行占 59px） | 页脚组件改同排，整条只占 35px；十件同时受益 |
| `preview/tp-04.png` | 状态圆点压在状态文字上；底部汇总条溢出 1980 | 圆点移到 CW−92、文字限宽 60；行高 176→160、汇总条改 68px |
| `preview/tp-09.png` | 首轮即通过；「有 3 项不合格」与表内勾选一一对应 | 直接采用 |
| `preview/tp-05.png` | 参数两列按 200+120 算宽度，正好顶到列距 330，值与右侧键名相接、附件值被截断 | 改为键名 126 + 值 188 |
| `preview/tp-10.png` | 活动班次的第三行（时段）掉出色块底部 | 行高 92→112、色块高 66→90 |
| `preview/tp-07.png` | 首轮即通过：四张可撕标签的撕线、标签条、编号对齐 | 直接采用 |
| `preview/tp-01/02/08.png` | 首轮即通过 | 直接采用 |

## 5. 真实文档与 DSL 能力应用

| 来源 | 用到的结论 |
|---|---|
| https://open-snapshot.muedsa.com/ai-guide.md | 请求体与响应形态；`type="png"` 决定编码 |
| https://snapshot.muedsa.com/reference/parser-tags/ | 39 个标签：`Container`/`Positioned`/`Stack`/`Text`/`ClipRRect` 等 |
| 同上 · `Text` | `textAlign` 取**大写**枚举 `START`/`CENTER`/`END`（A23 探针已验证） |
| 同上 · `Container` | `border` 为「宽度 样式 颜色」；`borderRadius` 做卡片与胶囊圆角 |
| `GET /fonts`（run 级共享准备） | Inter / Inter Semi Bold / Inter Medium + Noto Sans CJK SC |

## 6. 请求与指标

| 项 | 值 |
|---|---|
| 作品件数 | {mt["counts"]["cases"]} |
| 最终 PNG | {mt["counts"]["renders"]} 张，尺寸逐件断言通过 |
| 渲染请求 | {mt["counts"]["requests"]}（成功 {mt["counts"]["requests_ok"]} / 失败 {mt["counts"]["requests_failed"]}） |
| 服务耗时之和 | {mt["timings"]["request_duration_sum_seconds"]} 秒 |
| 视觉迭代轮次 | {mt["counts"]["visual_iteration_rounds"]} |
| 最终渲染重试 | {len(mt["verification"]["render_retries"])} 次 |

服务耗时之和不是任务总耗时。失败响应全部保留在 `tmp/run-20261011-01/B02/responses/`。

## 7. 未解决事项

- 无影响交付的未解决问题。
- **项目、数据、姓名、日期、班次全部自拟**，在 `design-system.json.disclaimer`、
  `portfolio.json.disclaimer`、`project-brief.md` 与每件 `case.md` 里都写明，
  每张图的页脚也写了。
- **无实物照片**：`case-05` 的商品大图位与 `case-04` 的缩略位用几何占位，
  并在图上明写「无实物照片 · 图为占位」，没有用外部素材或 `<Image>` 冒充。
- **字号下限在密集件降到 16px**：低于正文下限的 18px 的是表格内的编号与图例文字，
  不是叙述性正文；`design-system.json.typography.rule` 里写明了这条例外及其原因。

## 8. 路径

- 作品：`outputs/run-20261011-01/B02/case-01/` … `case-10/`
- 系统与映射：`outputs/run-20261011-01/B02/design-system.json`、`touchpoint-map.json`
- 项目说明：`outputs/run-20261011-01/B02/project-brief.md`
- 生成脚本：`tmp/run-20261011-01/B02/b02kit.py`、`cases_b02_a.py`、`cases_b02_b.py`、`build_b02.py`、`deliver_b02.py`
- 过程证据：`tmp/run-20261011-01/B02/`（`drafts/`、`preview/`、`responses/`、`requests.jsonl`、补丁脚本）
""", encoding="utf-8")
    print("->", (OUTD / "snapshot-usage.md").relative_to(ROOT))


if __name__ == "__main__":
    main()