> 全套运行说明：本题由总根入口自动执行。遵循 [总AGENTS.md](../../AGENTS.md)，
> 使用同一run_id的 `outputs/<run_id>/B02/` 和 `tmp/<run_id>/B02/`。
> 单题完成后继续总清单下一题，不等待逐题确认；本题内容要求保持有效。

# B02 · 为一个自选项目设计完整视觉生态

先完整阅读 [AGENTS.md](AGENTS.md) 与 [run-config.json](run-config.json)，其中的实际执行、输出、留痕和统计要求也是本题要求。

## 创作任务

自选一个值得投入的真实业务/文化/社区项目，为它构建一套至少10件完整
图像作品组成的视觉生态。项目可自拟，但服务对象、运作方式和使用需求
必须像真实项目一样清楚。你决定品牌或名称、定位、内容、触点和视觉概念。

自主识别用户在什么地方接触它、如何了解/参与/使用它、如何需要提醒或
获得反馈；设计十件各有实际任务的作品，而不是同一海报的十种颜色。
不指定任何必选媒介，也不要求固定流程页。你的整体设计应让人看出是
同一项目，又让每件适合其内容、观看距离和使用环境。

自行研究、写内容、建立可复用设计规则，以Snapshot DSL制作所有完整
用例。对实际图像反复检查和完善，尤其检验复用组件在不同密度/比例下
是否有效。允许大胆概念、局部辅助素材和工具，但主体工作必须是DSL。
交付至少10件主作品与各自DSL；另附project-brief.md说明你解决了什么
项目问题，design-system.json说明真正用到的系统规则，touchpoint-map.json
映射十件作品与用户情境。整体画廊、留痕、报告与统计按AGENTS执行。

## 交付

至少10件独立完整主作品，尺寸、场景、内容和风格由你决定。每件在输出目录的 `case-01/` 等子目录交付 `final.png`、`final.snapshot` 与 `case.md`。所有最终PNG必须是实际服务响应。

输出根同时交付 `portfolio.json`、`portfolio.md`、`gallery.md`、`snapshot-usage.md` 和 `task-metrics.json`。本题另要求 `project-brief.md`、`design-system.json`、`touchpoint-map.json`。

参考格式在 [templates/portfolio-template.json](templates/portfolio-template.json)、[templates/task-metrics-template.json](templates/task-metrics-template.json) 与 [templates/snapshot-usage-template.md](templates/snapshot-usage-template.md)。模板仅解释结构，完成时填真实数据并删去说明字段。

草稿、研究、素材、脚本、每次响应/预览和追加日志全部写入临时目录，不删除、不覆盖。以逐件和整体实际视觉审查判断完成，不设置固定调用/迭代上限。
