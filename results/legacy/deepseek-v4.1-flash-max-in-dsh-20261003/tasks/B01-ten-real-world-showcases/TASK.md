> 全套运行说明：本题由总根入口自动执行。遵循 [总AGENTS.md](../../AGENTS.md)，
> 使用同一run_id的 `outputs/<run_id>/B01/` 和 `tmp/<run_id>/B01/`。
> 单题完成后继续总清单下一题，不等待逐题确认；本题内容要求保持有效。

# B01 · 十张真实场景的炫酷用例

先完整阅读 [AGENTS.md](AGENTS.md) 与 [run-config.json](run-config.json)，其中的实际执行、输出、留痕和消耗要求也是本题要求。

## 创作任务

你是Snapshot的首席创意设计师。请直接构造至少10张完整、炫酷、结合真实
使用场景的用例图片，展示你能把结构化DSL带到什么程度。

不给你行业名单、指定文案、配色、尺寸或构图模板。自主寻找值得设计的
场景，确定受众与具体需求，补齐可信内容，选择恰当媒介和视觉语言。
十张应体现实质不同的使用任务与视觉想法，充分展现广度；每张既能成为
令人愿意停下观看的作品，也能帮助某个真实用户完成一件事。自拟品牌和
示例数据允许，但需说明，不宣称是实际部署的客户作品。

你可以研究优秀用例、探索Snapshot文档、计算几何与数据、写生成程序、
利用各种实际可用工具辅助创作。通过真实服务渲染，用视觉能力逐件审查、
修正和完善；在整个作品集完成前持续工作，不只列点子或展示一张通用卡片。
最后策展：指出各用例为何适合场景、最有辨识度的视觉选择是什么，给出
逐件最终图与完整DSL，以及整体画廊、使用说明、过程与消耗记录。

## 交付

至少10件独立完整主作品，尺寸、场景、内容和风格由你决定。每件在输出目录的 `case-01/` 等子目录交付 `final.png`、`final.snapshot` 与 `case.md`。所有最终PNG必须是实际服务响应。

输出根同时交付 `portfolio.json`、`portfolio.md`、`gallery.html`、`snapshot-usage.md` 和 `task-metrics.json`。

参考格式在 [templates/portfolio-template.json](templates/portfolio-template.json)、[templates/task-metrics-template.json](templates/task-metrics-template.json) 与 [templates/snapshot-usage-template.md](templates/snapshot-usage-template.md)。模板仅解释结构，完成时填真实数据并删去说明字段。

草稿、研究、素材、脚本、每次响应/预览和追加日志全部写入临时目录，不删除、不覆盖。以逐件和整体实际视觉审查判断完成，不设置固定调用/迭代上限。
