> 全套运行说明：本题由总根入口自动执行。遵循 [总AGENTS.md](../../AGENTS.md)，
> 使用同一run_id的 `outputs/<run_id>/B04/` 和 `tmp/<run_id>/B04/`。
> 单题完成后继续总清单下一题，不等待逐题确认；本题内容要求保持有效。

# B04 · 自主研究一个真实主题并制作十件视觉特辑

先完整阅读 [AGENTS.md](AGENTS.md) 与 [run-config.json](run-config.json)，其中的实际执行、输出、留痕和统计要求也是本题要求。

## 创作任务

自选一个你认为值得公众或专业读者理解的真实主题，亲自研究资料，编辑
成至少10件完整的视觉特辑作品。主题、受众、核心问题、叙述方式、作品
类型和风格全部由你决定；目标是既有原创视觉吸引力，又让读者获得准确
且有价值的理解，而不是把十段摘要贴在同一种卡片里。

实际读取资料，区分已证实事实、来源结论、你的解释和演示内容。图表
数据/分母/单位/比例/时间范围正确，图示不能为了气势改掉事实；观点和
比喻不能冒充证据。可选不依赖最新实时信息的主题，也可用环境中实际
可访问的本地公开资料，不要求实时联网新闻。不能把未访问页面列为
已读来源，无法取得材料时调整到可查证主题，仍不能伪造研究。

充分使用检索、数据/文本处理、编程、视觉检查等工具。以Snapshot DSL
制作十件自足作品，同时让特辑形成有意义的阅读关系；风格可统一或
因内容变化，但要有编辑意图。实际看图、复核事实并持续修改。
另附sources.json（实际来源/访问记录/各作品引用/演示或不确定信息）、
editorial-note.md（主题选择、读者问题、叙述路线与限制）。交付全部
PNG/DSL、作品画廊、使用说明、过程与请求/迭代/耗时统计。

## 交付

至少10件独立完整主作品，尺寸、场景、内容和风格由你决定。每件在输出目录的 `case-01/` 等子目录交付 `final.png`、`final.snapshot` 与 `case.md`。所有最终PNG必须是实际服务响应。

输出根同时交付 `portfolio.json`、`portfolio.md`、`gallery.html`、`snapshot-usage.md` 和 `task-metrics.json`。本题另要求 `sources.json`、`editorial-note.md`。

参考格式在 [templates/portfolio-template.json](templates/portfolio-template.json)、[templates/task-metrics-template.json](templates/task-metrics-template.json) 与 [templates/snapshot-usage-template.md](templates/snapshot-usage-template.md)。模板仅解释结构，完成时填真实数据并删去说明字段。

草稿、研究、素材、脚本、每次响应/预览和追加日志全部写入临时目录，不删除、不覆盖。以逐件和整体实际视觉审查判断完成，不设置固定调用/迭代上限。
