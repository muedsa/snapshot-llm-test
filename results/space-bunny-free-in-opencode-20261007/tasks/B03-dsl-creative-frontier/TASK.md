> 全套运行说明：本题由总根入口自动执行。遵循 [总AGENTS.md](../../AGENTS.md)，
> 使用同一run_id的 `outputs/<run_id>/B03/` 和 `tmp/<run_id>/B03/`。
> 单题完成后继续总清单下一题，不等待逐题确认；本题内容要求保持有效。

# B03 · 用十件作品探索DSL的创意边界

先完整阅读 [AGENTS.md](AGENTS.md) 与 [run-config.json](run-config.json)，其中的实际执行、输出、留痕和统计要求也是本题要求。

## 创作任务

把Snapshot当作你的创意材料，探索它能产生怎样令人意外又有用途的视觉
表达。阅读官方文档、实际实验，制作至少10件完整作品，每件都落在你
自选的真实使用场景，不交只有滤镜名称和小方块的能力示范板。

自主挑选值得研究的布局、文字、几何、变换、裁剪、合成、滤镜、程序化
构图或其他已支持能力；不要求凑齐特定标签，也不给视觉参考答案。
用不同创意组合形成自己的视觉手法，让手法服务内容而不是遮住信息。
有想法在服务里不成立时，保留试验依据，改变实现或改用更好的表达，
不靠不存在的标签和后处理冒充实现。

允许编程计算、搜索研究、生成辅助素材、制作放大对比和诊断版本等
实际可用工具；最终文字、布局和主要视觉均由DSL构造。逐件检查实际
效果、阅读性和应用适配，持续完善整个十件合集。
另交付technique-notes.md：每件独到手法、实际文档依据、试验与看图证据、
应用价值和已确认的边界。不要将“使用了复杂标签”本身当作作品完成。
保留至少10件完整PNG/DSL、作品画廊、真实使用/踩坑与统计记录。

## 交付

至少10件独立完整主作品，尺寸、场景、内容和风格由你决定。每件在输出目录的 `case-01/` 等子目录交付 `final.png`、`final.snapshot` 与 `case.md`。所有最终PNG必须是实际服务响应。

输出根同时交付 `portfolio.json`、`portfolio.md`、`gallery.md`、`snapshot-usage.md` 和 `task-metrics.json`。本题另要求 `technique-notes.md`。

参考格式在 [templates/portfolio-template.json](templates/portfolio-template.json)、[templates/task-metrics-template.json](templates/task-metrics-template.json) 与 [templates/snapshot-usage-template.md](templates/snapshot-usage-template.md)。模板仅解释结构，完成时填真实数据并删去说明字段。

草稿、研究、素材、脚本、每次响应/预览和追加日志全部写入临时目录，不删除、不覆盖。以逐件和整体实际视觉审查判断完成，不设置固定调用/迭代上限。
