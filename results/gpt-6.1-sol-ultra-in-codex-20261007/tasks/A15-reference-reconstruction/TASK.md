> 全套运行说明：本题由总根入口自动执行。遵循 [总AGENTS.md](../../AGENTS.md)，
> 使用同一run_id的 `outputs/<run_id>/A15/` 和 `tmp/<run_id>/A15/`。
> 单题完成后继续总清单下一题，不等待逐题确认；本题内容要求保持有效。

# A15 · 复杂界面视觉复刻

先完整阅读 [AGENTS.md](AGENTS.md) 的执行、目录、留痕和指标约定；该文件是本任务要求的一部分。

## 任务

inputs/reference.png 是1440×900参考界面，inputs/content.json 仅提供原样文本和
数值以减少OCR歧义，不提供几何坐标。用Snapshot DSL重建参考图的布局、背景、
侧栏、卡片、图表、表格、状态标签和主要装饰。禁止直接嵌入参考图或裁块当素材。
输出尺寸保持1440×900，所有主要结构与信息完整，不改成自己的新设计。
观察原尺寸、缩略与局部放大；主区边界/卡片边界/图表零线/导航选中态等关键
锚点应与参考一致（允许±8像素），颜色可小幅近似，字体从实际服务列表中选择。
重建图表的比例与标记，而不是只放相同数字；表格3行顺序与状态编码准确。
至少记录12个视觉锚点的参考估计坐标和重建坐标，涵盖画布四象限、图表和表格。
交付 reconstruction-audit.json 与 comparison.md：用可测误差及实际视觉说明
残余差异。不要求DSL树与参考来源一致，不必宣称不存在的逐像素完全复刻。

## 输入文件

- [content.json](inputs/content.json)
- [reference.png](inputs/reference.png)

## 指定交付

| PNG与对应DSL | 尺寸 | 用途 |
|---|---|---|
| `reconstructed.png` + `reconstructed.snapshot` | 1440×900 | 参考界面复刻 |

额外文件：`reconstruction-audit.json`、`comparison.md`。

同时交付 `snapshot-usage.md`、`task-metrics.json`，过程日志在临时目录。

完成时依据实际图像自检；所有指定最终PNG都须是服务真实响应且有同名 `.snapshot`。
