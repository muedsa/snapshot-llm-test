> 全套运行说明：本题由总根入口自动执行。遵循 [总AGENTS.md](../../AGENTS.md)，
> 使用同一run_id的 `outputs/<run_id>/A21/` 和 `tmp/<run_id>/A21/`。
> 单题完成后继续总清单下一题，不等待逐题确认；本题内容要求保持有效。

# A21 · 真实需求变更：双尺寸发布物（自动三轮版本）

## 第一轮与执行顺序

本题按预置要求自动执行三轮。先完成第一轮：为“叠光 Layerlight”发布
活动做1080×1350竖海报和1440×810横屏。必须包含“让复杂信息变得清晰”
“2026.11.07 19:30”“ONLINE LAUNCH”“讲者：林川 / 苏言”
“layerlight.example.org”。两图同一主色、字体层级与可识别的3–6构件品牌图形，
分别构图；主标题≥56、其余≥24，不得使用整图嵌入或外部图片。
顶部/底部留有真实可用扩展空间，但不写待添加文字。交付 round-01/ 下
launch-portrait与launch-wide两PNG/DSL，以及 design-tokens.json、content-map.json。
查看两图并归档第一轮后，立即读取rounds/round-02.md完成第二轮，
再读取rounds/round-03.md完成第三轮，不等待用户消息。后续轮必须保留上一轮可比版本、内容映射
与真实变化，按执行约定保存每轮报告/指标。

## 交付路径与轮次归属

本题 task.json 的 required_outputs（PNG/DSL）、additional_outputs（专用审计）、
common_outputs（报告/指标）均使用相对本题输出根的完整路径，顶层列出全部最终交付。
rounds 内的同名字段是顶层清单按轮次划分的子集；output_subdirectory 仅表示归属目录，
不能再次拼接到这些已带 round-XX/ 的路径前。同一个路径只交付一次。
snapshot-usage.md 与 task-metrics.json 位于本题输出根，汇总三轮；每轮另有
round-XX/snapshot-usage.md 与 round-XX/task-metrics.json，只记录该轮。
专用审计仅在清单指定的轮次目录交付，不另在输出根复制一份。

## 专用审计JSON字段

本题指定的专用JSON须遵循[最小字段约定](templates/audit-fields.json)，可增加字段；
该文件只解释结构、单位、坐标/路径基准及证据要求，不是已完成答案。多轮任务复用
同名文件的字段约定，仍按task.json各轮完整路径交付；不要在输出根增加重复文件。

## 后续轮次

第一轮实际完成、看图、保存后，自动读取 [第二轮](rounds/round-02.md)；第二轮归档后自动读取 [第三轮](rounds/round-03.md)。全部需求预置可访问，报告注明连续执行模式。

## 全部最终图片

| PNG与同名DSL | 尺寸 |
|---|---|
| `round-01/launch-portrait.png` + `round-01/launch-portrait.snapshot` | 1080×1350 |
| `round-01/launch-wide.png` + `round-01/launch-wide.snapshot` | 1440×810 |
| `round-02/launch-portrait.png` + `round-02/launch-portrait.snapshot` | 1080×1350 |
| `round-02/launch-wide.png` + `round-02/launch-wide.snapshot` | 1440×810 |
| `round-03/launch-portrait.png` + `round-03/launch-portrait.snapshot` | 1080×1350 |
| `round-03/launch-wide.png` + `round-03/launch-wide.snapshot` | 1440×810 |

各轮额外文件和报告/指标见task.json的rounds。任务输出根另有三轮累计snapshot-usage.md与task-metrics.json。保留所有旧轮，三轮完成后继续总任务下一题。

## 全部审计文件与报告

| 相对本题输出根的路径 | 归属 |
|---|---|
| `round-01/design-tokens.json` | round-01 |
| `round-01/content-map.json` | round-01 |
| `round-02/design-tokens.json` | round-02 |
| `round-02/content-map.json` | round-02 |
| `round-03/design-tokens.json` | round-03 |
| `round-03/content-map.json` | round-03 |
| `round-03/contrast-audit.json` | round-03 |
| `snapshot-usage.md` | 三轮任务汇总 |
| `task-metrics.json` | 三轮任务汇总 |
| `round-01/snapshot-usage.md` | round-01 |
| `round-01/task-metrics.json` | round-01 |
| `round-02/snapshot-usage.md` | round-02 |
| `round-02/task-metrics.json` | round-02 |
| `round-03/snapshot-usage.md` | round-03 |
| `round-03/task-metrics.json` | round-03 |
