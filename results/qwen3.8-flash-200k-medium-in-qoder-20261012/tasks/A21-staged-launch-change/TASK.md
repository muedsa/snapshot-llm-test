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
