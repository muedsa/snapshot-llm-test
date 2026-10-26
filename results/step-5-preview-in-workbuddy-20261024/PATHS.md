# 可迁移路径约定

涉及文件或目录的配置、DSL、程序脚本、命令、报告和自建日志，都使用有明确基准的相对路径，
或读取直接指向目录的环境变量。不得写死当前机器的盘符、用户名称、用户目录、仓库位置或 UNC 路径。
生成代码也遵循本约定；换机器或整体移动任务目录后，应只需改变启动位置或环境变量。

## 路径基准

| 内容 | 相对路径基准 |
|---|---|
| 总 `run-config.json` 的 `output_root` / `temp_root` | 该配置文件所在目录，即总任务根 |
| 子题 `run-config.json` 的目录参数及 `suite_config` | 该配置文件所在目录；例如 `../../outputs` |
| `catalog.json` 的入口、目录、文件与输出模板 | 总任务根 |
| `task.json` 的 `inputs`、说明文件及轮次要求文件 | 本题输入目录 |
| `task.json` 的 `output_dir_template` / `temp_dir_template` | 总任务根 |
| 题目指定的最终文件名、附加产物名及轮次输出子目录 | 本题输出根；例如 `round-01/final.png` |
| 指标、状态、检查点、请求/迭代/工具日志中的本地路径 | 默认总任务根，记录 `path_base: "suite_root"` |
| `portfolio.json` 的 PNG、DSL、素材和自检证据文件 | 本题输出根，记录 `path_base: "output_dir"` |
| Markdown 的本地链接及图片链接 | 当前 Markdown 文件所在目录 |
| 程序脚本与复现命令 | 明确声明的启动/脚本/配置所在目录，或目录环境变量 |

记录和脚本不能因当前工作目录改变而悄悄变换路径基准。运行时可计算实际目录，保存记录时转换回
相对路径，或保存未展开的目录环境变量表达式。例如 `outputs/<run_id>/A01/`、
`tmp/<run_id>/A01/requests.jsonl`。本题 `OUTPUT_DIR` / `TEMP_DIR` 参数也使用相对路径或目录环境变量。
日志 URL、请求的 HTTP 路径及资料来源链接保留其正常 URL 语义，不当成本地文件路径。

如果指定输出/临时目录位于任务根之外，优先通过 `SNAPSHOT_OUTPUT_ROOT`、`SNAPSHOT_TEMP_ROOT` 等
直接指向目录的环境变量定位；记录保留变量表达式，并注明变量名、用途和路径基准。
复现说明给出变量的设置方式，不抄写当前机器的展开值；不得在记录中暴露凭据。

## 环境变量与代码

| 使用位置 | 用户目录写法 |
|---|---|
| Windows CMD | `%USERPROFILE%` |
| PowerShell | `$env:USERPROFILE` |
| Python | `os.environ["USERPROFILE"]` 或 `Path.home()` |
| POSIX shell | `$HOME` 或 `${HOME}` |

按实际操作系统和语言读取变量。Python 的 `Path("%USERPROFILE%")` 不会自动展开变量；
JSON 中的 `%NAME%`、`${NAME}`、`$NAME` 只是字符串，加载代码必须明确支持所用语法、展开并检查
变量存在。缺少变量时报明确错误，不猜测用户目录，也不回退到写死的机器路径。
目录变量本身可以由运行环境设为实际绝对目录；源码、配置和复现说明保存变量名及相对后缀。

Python 示例（从总任务根启动，或提供直接指向总任务根的 `SNAPSHOT_TASK_ROOT`）：

```python
import os
from pathlib import Path

suite_root = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
run_id = os.environ["SNAPSHOT_RUN_ID"]
output_dir = suite_root / "outputs" / run_id / "A01"
temp_dir = suite_root / "tmp" / run_id / "A01"
user_dir = Path(os.environ["USERPROFILE"]) if os.name == "nt" else Path.home()
# 文件操作可以使用运行时目录；保存到指标/日志时转换回声明的基准。
output_record = output_dir.relative_to(suite_root).as_posix()
```

PowerShell 示例（从总任务根启动）：

```powershell
$snapshotTaskRoot = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { '.' }
if (-not $env:SNAPSHOT_RUN_ID) { throw '请先设置 SNAPSHOT_RUN_ID' }
$snapshotOutputDir = Join-Path $snapshotTaskRoot "outputs/$env:SNAPSHOT_RUN_ID/A01"
$snapshotTempDir = Join-Path $snapshotTaskRoot "tmp/$env:SNAPSHOT_RUN_ID/A01"
$snapshotUserDir = $env:USERPROFILE
```

运行时内部的 `resolve()`、文件 API 或需要绝对路径的图像查看工具参数可以使用计算得到的绝对路径。
不要把这些展开值写回源代码、配置、DSL或自建日志/报告；记录应从实际目录转换成相对路径或变量表达式。
保存过程脚本时注明启动基准，并检查读取、写入、素材、字体、缓存、导出和命令参数中的所有本地路径。

## Markdown 与交付审查

Markdown 渲染器不会展开环境变量，本地图片/文件链接必须是真正的相对路径。
例如输出 `_suite/gallery.md` 链接 `../A01/operations.png`；单题画廊链接 `case-01/final.snapshot`。
报告中的目录说明可以展示环境变量表达式，但不能把它直接放进 Markdown 链接。
从模板生成报告或移动报告后，按实际 Markdown 所在目录重新计算本地链接。

完成前检查生成的配置、DSL、脚本、命令、报告、指标、状态与自建日志中是否残留写死的机器路径，
核对所有基准和变量说明，并检查本地链接实际可访问。作者发布校验仅验证题库契约与模板，
执行模型仍须审查自己生成的文件。

服务/工具的原始响应或原始命令输出按留痕要求保持原始字节；自建记录引用其相对路径即可，
不为改写路径而篡改原始证据。输入中要求逐字排版的路径文本属于内容数据，保持原样，
例如 A11 的 `Path: C:\work\cards\v2`；不要将这种文案用作文件操作路径。

## A21/A22 多轮交付清单

task.json 的 output_path_base 为 output_dir。顶层 required_outputs、
additional_outputs、common_outputs 是全轮次最终交付的完整清单；rounds 中同名字段
仅声明各文件所属轮次，路径仍相对本题输出根。同一路径在两处出现是索引关系，
不表示两份交付。output_subdirectory 不参与二次拼接。
例如 A22 的 round-02/computed-data.json 解析为
outputs/<run_id>/A22/round-02/computed-data.json，不产生双重 round-02/。
任务根 snapshot-usage.md、task-metrics.json 汇总全部轮次；轮次内同名报告只覆盖本轮。
