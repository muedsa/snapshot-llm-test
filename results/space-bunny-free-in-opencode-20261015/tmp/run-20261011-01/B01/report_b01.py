#!/usr/bin/env python
# B01 使用报告：从交付产物里读真实数据，不用手抄。
# 启动基准：总任务根 (suite_root)。用法：python report_b01.py
from __future__ import annotations

import datetime
import json
import os
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
OUTD = ROOT / "outputs/run-20261011-01/B01"
PREV = "tmp/run-20261011-01/B01/preview"


def main() -> None:
    now = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    pf = json.loads((OUTD / "portfolio.json").read_text(encoding="utf-8"))
    mt = json.loads((OUTD / "task-metrics.json").read_text(encoding="utf-8"))

    tbl = "\n".join(
        f'| {c["id"]} | {c["title"]} | {c["domain"]} | '
        f'{c["size"]["width"]}×{c["size"]["height"]} | {c["dsl"].split("/")[-2]} |'
        for c in pf["cases"])
    picks = "\n\n".join(
        f'### {c["id"]} · {c["title"]}\n\n'
        f'- 受众：{c["audience"]}\n'
        f'- 问题：{c["user_question"]}\n'
        f'- 辨识点：{c["signature_visual_choice"]}'
        for c in pf["cases"])

    (OUTD / "snapshot-usage.md").write_text(f"""# B01 使用报告 · 十张真实场景的炫酷用例

生成时间：{now}

## 1. 完成状态

十件独立完整主作品已交付，全部是 open-snapshot 服务的真实响应，
每件都有同名完整 `.snapshot`。十件的尺寸、场景与图形语汇各不相同：

| 用例 | 主题 | 领域 | 尺寸 | 目录 |
|---|---|---|---|---|
{tbl}

|pf["disclaimer"]|

## 2. 实际看图记录

十件全部整屏打开看过，下面是**每一轮改了什么**的真实记录。

| 轮次 | 涉及 | 实际看到的问题 | 处理 |
|---|---|---|---|
| 1 | 01 | KPI 卡（210–334）与时间轴区（起点 326）重叠，站名「人民广场」压在「时间轴（分钟，23:00 = 0）」上 | 轴线下移到 424，换乘窗口从时间轴挪到左栏文字列 |
| 1 | 03 | 曲线被画成**一串圆点**而不是连线；图例把「浅焙/深焙」各画了两次；KPI 副注压住数值；要点压住 x 轴标签 | 用 `Transform` 旋转长条画实线段；图例移出曲线循环；`kpi_row` 改按字号顺次排布并把卡加高到 124；要点下移 |
| 1 | 04 | 刻度方向反了：标 80% 在左、0% 在右，条子却从右侧长出去；「浇/跳过」按钮被画布右缘切掉；8 行溢出画布 | 改成常规左增右的条形；处置按钮移到固定列 1104；行距 62 并整体上移 |
| 1 | 05 | 「最长等待」与底部「超时预警」自相矛盾（前者全部未超时，后者点名两个等级超时）；预警框压住页脚 | 统一数据（III 级 38>30、IV 级 74>60）；行距 78；预警框压到 92 高 |
| 2 | 04 | 改完方向后数据自相矛盾：44% 与 39% 明明在 35–60 窗口内，备注却写「低于下限 1 个点」，而 KPI 又写「需浇 4/8」 | 备注按同一阈值重写；KPI 由数据现算成「2/8」「平均 48%」「19 L」 |
| 2 | 05 | I 级目标写成「≤ 0 分钟」，0 分钟的时长目标没有意义；平均等待首版写 27 分钟，与按人数加权算出的 67 分钟不符 | 目标改 5 分钟；平均等待改成由数据现算 |
| 3 | 06 | 四条 PR 竖排，900px 画布放不下，最后一条压住页脚；行距 44px 时姓名与副行竖排互相重叠 | 画布加高到 960；PR 清单改两列；姓名与容量并排 |
| 3 | 07 | **极坐标投影与地平线自相矛盾**：星跑到了地平线以下 | 改用直角星图：横轴方位角、纵轴高度角，地平线是底边 |
| 3 | 09 | 六个港口的时窗叠在同一根时间轴上，糊成一条实心带，文字互相盖住；路径带中心固定导致视觉重心偏上；「必须关港 4 个」与图里 0 个红色窗口矛盾 | 每港单独一行；概率带以路径中心线为基准展开；四个短窗口的关港时间改到同一 70h，使 KPI 与图一致 |
| 4 | 10 | 平面图画在 y=288 而 KPI 卡到 334，地图顶栏压在卡片下沿；右侧列表宽 192px，百分比与「在场/容量」两行文字互相盖住 | 地图下移到 348 并给入口标签让出空带；右侧加宽到 260，数字分两行 |
| 4 | 08 | 刻度标签与轴标题同一高度，文字互压；名称与日销竖排，48px 行距下压到下一行 | 标题上移缩短、刻度下移；名称与日销并排 |

第 4 轮之后十件都没有再发现影响可读性或正确性的缺陷。

## 3. 逐件辨识点

{picks}

## 4. 真实文档与 DSL 能力应用

| 来源 | 用到的结论 |
|---|---|
| https://open-snapshot.muedsa.com/ai-guide.md | 请求体与响应形态；`type="png"` 决定编码；响应为原始 PNG 字节 |
| https://snapshot.muedsa.com/reference/parser-tags/ | 39 个标签总表：`Container`/`Positioned`/`Stack`/`Text`/`Transform`/`ClipRRect` 等 |
| 同上 · `Transform` | `matrix` 为列主序 4×4、**16 个**有限 Float、外层带括号且值间无空格。首版写了 17 个值直接 400；改正后用它画折线、斜条与旋转块 |
| 同上 · `Text` | `textAlign` 合法取值是**大写** `START`/`CENTER`/`END`/`JUSTIFY`（A23 探针已验证）；小写一律 400 |
| 同上 · `Container` | `border` 格式为「宽度 样式 颜色」；`borderRadius` 做卡片、槽位与色块圆角 |
| `GET /fonts`（run 级共享准备） | Inter / Inter Semi Bold / Inter Medium 与 Noto Sans CJK SC |

**十件全部没有使用 `<Image>`**：没有外部素材，也没有内嵌任何已渲染图。
每件都是「用参数生成 DSL → 渲染 → 看图 → 改参数 → 重渲染」。

## 5. 一个被推翻的旧结论

本题开工时沿用了本套早先记录的一条「服务行为」：`textAlign` 不可用。
A23 已经用探针证明它只是要求**大写**枚举，B01 全部改用
`textAlign="END"` / `"CENTER"` 做右对齐与居中，不再靠估算字宽手工摆坐标。
更正过程与证据见 `tmp/run-20261011-01/_suite/capability-corrections.md`。

## 6. 请求与指标

| 项 | 值 |
|---|---|
| 作品件数 | {mt["counts"]["cases"]} |
| 最终 PNG | {mt["counts"]["renders"]} 张，尺寸逐件断言通过 |
| 渲染请求 | {mt["counts"]["requests"]}（成功 {mt["counts"]["requests_ok"]} / 失败 {mt["counts"]["requests_failed"]}） |
| 服务耗时之和 | {mt["timings"]["request_duration_sum_seconds"]} 秒 |
| 视觉迭代轮次 | {mt["counts"]["visual_iteration_rounds"]} |
| 图片查看次数 | {mt["counts"]["image_views"]} |
| 最终渲染重试 | {len(mt["verification"]["render_retries"])} 次 |

服务耗时之和不是任务总耗时。失败的请求体与错误响应全部保留在
`{PREV.replace('preview', 'responses')}/`。

## 7. 未解决事项

- 无影响交付的未解决问题。
- **十件的场景与数据都是自拟的**，这一点在 `portfolio.json.disclaimer`、
  每张图的页脚和每份 `case.md` 里都写明了，没有把它们包装成真实客户作品。
- **服务偶发返回 HTTP 200 + 0 字节**：十件的渲染循环都校验了 PNG 字节长度并重试，
  失败响应原样保存在 `tmp/run-20261011-01/B01/responses/`。
- **文字宽度是估算值**：`bsnap.em_width` 用 A14 实测标定的系数判断「放不放得下」，
  多行段落一律自己排版逐行输出（`wrap` + CJK 悬挂标点），
  不依赖服务端自动换行——服务端会把溢出盒子的行**静默裁掉**。
  估算仍可能偏小，所以每个 Text 盒子都留了余量。

## 8. 路径

- 作品：`outputs/run-20261011-01/B01/case-01/` … `case-10/`（各含 `final.png`、`final.snapshot`、`case.md`）
- 作品集：`outputs/run-20261011-01/B01/portfolio.json`、`portfolio.md`、`gallery.md`
- 生成脚本：`tmp/run-20261011-01/B01/build_b01.py`、`cases_b01_b.py`、`deliver_b01.py`
- 共用工具：`tmp/run-20261011-01/_suite/scripts/bsnap.py`
- 过程证据：`tmp/run-20261011-01/B01/`（`drafts/`、`preview/`、`responses/`、`requests.jsonl`、补丁脚本）
""", encoding="utf-8")
    print("->", (OUTD / "snapshot-usage.md").relative_to(ROOT))


if __name__ == "__main__":
    main()