> 全套运行说明：本题由总根入口自动执行。遵循 [总AGENTS.md](../../AGENTS.md)，
> 使用同一run_id的 `outputs/<run_id>/B06/` 和 `tmp/<run_id>/B06/`。
> 单题完成后继续总清单下一题，不等待逐题确认；本题内容要求保持有效。

# B06 · 把十个日常信息难题变成惊艳而好用的作品

先完整阅读 [AGENTS.md](AGENTS.md) 与 [run-config.json](run-config.json)，其中的实际执行、输出、留痕和消耗要求也是本题要求。

## 创作任务

自主观察现实生活中信息难理解、难比较、难找到或难采取行动的场景，
选择至少10个值得重新设计的问题，用Snapshot制作十件完整作品。
你自己发现问题、定义使用者与使用环境、研究内容并提出设计方案；
不给行业/媒介名单、版式答案或审美方向。

每件要能说清用户原本卡在哪里、新作品如何让信息更容易被理解/使用。
可以用实际资料，也可以根据可观察的问题建立自拟但合理的案例；对应
标明资料与假设，不声称做过不存在的现场调研或用户实验。原材料或问题
证据只作为输入研究，不需要交十张故意丑化的“之前”图来凑数量。

大胆重构信息、尝试视觉隐喻、程序化几何或新的阅读组织，同时保证关键
内容完整、准确、能读。漂亮与实用都要从实际画面中成立。自主使用各种
可用工具研究、计算、构建、放大/缩小查看和对比，持续改进十件最终图。
另交付problem-evidence.json与design-review.md：每个问题的实际来源/
假设、场景要求、重构选择和根据最终图判断的改进；区分可观察的可读性
改善与未经用户实验验证的效果。交付至少十件主作品及各DSL、作品画廊、
使用说明、临时留痕与消耗记录。

## 交付

至少10件独立完整主作品，尺寸、场景、内容和风格由你决定。每件在输出目录的 `case-01/` 等子目录交付 `final.png`、`final.snapshot` 与 `case.md`。所有最终PNG必须是实际服务响应。

输出根同时交付 `portfolio.json`、`portfolio.md`、`gallery.html`、`snapshot-usage.md` 和 `task-metrics.json`。本题另要求 `problem-evidence.json`、`design-review.md`。

参考格式在 [templates/portfolio-template.json](templates/portfolio-template.json)、[templates/task-metrics-template.json](templates/task-metrics-template.json) 与 [templates/snapshot-usage-template.md](templates/snapshot-usage-template.md)。模板仅解释结构，完成时填真实数据并删去说明字段。

草稿、研究、素材、脚本、每次响应/预览和追加日志全部写入临时目录，不删除、不覆盖。以逐件和整体实际视觉审查判断完成，不设置固定调用/迭代上限。
