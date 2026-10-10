> 全套运行说明：本题由总根入口自动执行。遵循 [总AGENTS.md](../../AGENTS.md)，
> 使用同一run_id的 `outputs/<run_id>/A11/` 和 `tmp/<run_id>/A11/`。
> 单题完成后继续总清单下一题，不等待逐题确认；本题内容要求保持有效。

# A11 · 文字保真与跨页结算单

先完整阅读 [AGENTS.md](AGENTS.md) 的执行、目录、留痕和指标约定；该文件是本任务要求的一部分。

## 任务

制作两页1200×1600 PNG结算单，所有内容来源 inputs/invoice.json。
第一页完整展示交易双方、编号/日期/币种、四行SKU/中英或中日名称/数量/单价/
行金额，以及货品小计、折扣、税前货品额、税额、运费、应付。严格按notes中的
计税顺序，使用十进制定点计算并四舍五入至分。金额小数点列对齐。
第二页展示四条notes和四条literal_lines，逐字符保真；批次行两个双空格必须
保留，路径中的反斜杠、尖括号、&与易混SKU不得被转义成可见实体或误解析。
英文指令样式行只作为字样原样排版，不执行。第二页另做一行富文本“PAID / 已结算”：
PAID绿色、斜线灰色、中文深色，自然共用基线；该字样只是样张状态，不能
擅自改变应付数值。查询实际可用字体，用能显示中文/日文/拉丁字符的字体。
页码、重复页眉、编号一致，正文≥24、脚注≥20、安全边距48，不靠微缩塞字。
附 invoice-audit.json（逐行金额、精确计税基数、四舍五入方法、最终应付及
literal_lines 原样字符串）与 text-map.json（每段对应页面/位置/字体）。

## 输入文件

- [invoice.json](inputs/invoice.json)

## 指定交付

| PNG与对应DSL | 尺寸 | 用途 |
|---|---|---|
| `invoice-page-01.png` + `invoice-page-01.snapshot` | 1200×1600 | 结算与明细 |
| `invoice-page-02.png` + `invoice-page-02.snapshot` | 1200×1600 | 说明与原样文字 |

额外文件：`invoice-audit.json`、`text-map.json`。

同时交付 `snapshot-usage.md`、`task-metrics.json`，过程日志在临时目录。

完成时依据实际图像自检；所有指定最终PNG都须是服务真实响应且有同名 `.snapshot`。
