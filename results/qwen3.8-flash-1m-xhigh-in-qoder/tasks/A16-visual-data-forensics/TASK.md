> 全套运行说明：本题由总根入口自动执行。遵循 [总AGENTS.md](../../AGENTS.md)，
> 使用同一run_id的 `outputs/<run_id>/A16/` 和 `tmp/<run_id>/A16/`。
> 单题完成后继续总清单下一题，不等待逐题确认；本题内容要求保持有效。

# A16 · 从错误图表恢复可信叙事

先完整阅读 [AGENTS.md](AGENTS.md) 的执行、目录、留痕和指标约定；该文件是本任务要求的一部分。

## 任务

inputs/flawed-report.png 是同事制作的1280×900经营图，inputs/source.csv 为唯一
可信原始数据；图片与源码不是标准答案。只通过图片和数据找出视觉/数值/叙事
问题，不提供旧DSL。先实际查看图，逐项给出可观察证据，别按常见错误凭空列坑。
将它重制为1280×900可信报告：四季收入/成本分组柱图（共同零起点）、利润明细、
一条有数据依据的标题、图例、单位“万元”、全部季度。保持“季度复盘”的主题，
风格允许改进。柱高对应数值，不能只修数字标签；重点季度由数据论证。
附 findings.json，每项问题包含图片位置、现象、源数据核对、影响、修正及最终
查看结果；未确认是否错误的部分独立记录为不确定，避免把审美偏好混作数值错。
附 corrected-data.json 的计算与轴定义。正文≥22、标注≥18，无外部图像。

## 专用审计JSON字段

本题指定的专用JSON须遵循[最小字段约定](templates/audit-fields.json)，可增加字段；
该文件只解释结构、单位、坐标/路径基准及证据要求，不是已完成答案。多轮任务复用
同名文件的字段约定，仍按task.json各轮完整路径交付；不要在输出根增加重复文件。

## 输入文件

- [source.csv](inputs/source.csv)
- [flawed-report.png](inputs/flawed-report.png)

## 指定交付

| PNG与对应DSL | 尺寸 | 用途 |
|---|---|---|
| `corrected-report.png` + `corrected-report.snapshot` | 1280×900 | 修正后的可信报告 |

额外文件：`findings.json`、`corrected-data.json`。

同时交付 `snapshot-usage.md`、`task-metrics.json`，过程日志在临时目录。

完成时依据实际图像自检；所有指定最终PNG都须是服务真实响应且有同名 `.snapshot`。
