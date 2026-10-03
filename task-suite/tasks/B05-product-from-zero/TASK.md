> 全套运行说明：本题由总根入口自动执行。遵循 [总AGENTS.md](../../AGENTS.md)，
> 使用同一run_id的 `outputs/<run_id>/B05/` 和 `tmp/<run_id>/B05/`。
> 单题完成后继续总清单下一题，不等待逐题确认；本题内容要求保持有效。

# B05 · 从零构想产品并设计十个关键使用画面

先完整阅读 [AGENTS.md](AGENTS.md) 与 [run-config.json](run-config.json)，其中的实际执行、输出、留痕和消耗要求也是本题要求。

## 创作任务

找一个现实中值得解决的问题，自主构想一款产品或服务，用至少10张
完整静态界面/使用画面，让人理解它如何帮助真实用户。你决定受众、
产品机制、设备、状态、流程、内容、视觉语言和每张图的尺寸；不预设
登录页、仪表盘或某类App，也不要求实现前端运行程序。

画面组合要支持一个可信使用过程：每件反映不同真实需求、决策、状态
或结果。既要有令人记住的视觉概念，也要让功能、信息与操作意图合理。
用具体而可信的样例内容，不停留在骨架框或满屏lorem ipsum；不把装饰
成操作按钮后又无法解释作用。跨画面共用信息保持一致，必要状态有
合理反馈。你自行判断哪些情境值得呈现，不按固定界面清单凑十页。

运用研究、规划、内容生成、计算、代码/布局工具和视觉判断，用Snapshot
DSL完成全部画面。逐张检查，再按实际旅程整体审查；发现跳步、矛盾、
不可读或形态不适合设备时继续改进。真实用户验证若未做，不声称做过。
另交付product-brief.md与journey.json，解释用户问题、产品方案、每张
画面及其前后关系、假设与验证边界。交付十张主图/DSL及通用画廊、留痕、
使用与消耗记录。

## 交付

至少10件独立完整主作品，尺寸、场景、内容和风格由你决定。每件在输出目录的 `case-01/` 等子目录交付 `final.png`、`final.snapshot` 与 `case.md`。所有最终PNG必须是实际服务响应。

输出根同时交付 `portfolio.json`、`portfolio.md`、`gallery.html`、`snapshot-usage.md` 和 `task-metrics.json`。本题另要求 `product-brief.md`、`journey.json`。

参考格式在 [templates/portfolio-template.json](templates/portfolio-template.json)、[templates/task-metrics-template.json](templates/task-metrics-template.json) 与 [templates/snapshot-usage-template.md](templates/snapshot-usage-template.md)。模板仅解释结构，完成时填真实数据并删去说明字段。

草稿、研究、素材、脚本、每次响应/预览和追加日志全部写入临时目录，不删除、不覆盖。以逐件和整体实际视觉审查判断完成，不设置固定调用/迭代上限。
