# 独立轮次指标归档工具

`archive-round-metrics.cjs` 是当前 `20261002-204314-6f31` 的 shared 准备工具。没有读取任何未来任务/轮次文件，也没有生成 A21/A22 轮次执行事实。这里只核对现有共享代码，并以已完成 A11 页面与 A12 用例做只读接口验证；页面/用例不会改称轮次。

## 现有代码的范围

`suite.cjs` 的 request、render、saveVersion、view、iteration、waitRecord、artifact 均可以记录 `round_id`。`countsFor(task,{round_id})` 先严格过滤，再按 version_id 取最新迭代、按 image_path 取当前成品；所有 raw 追加记录仍保留。view、iteration、waits 的轮次标签需要调用方真实传入，不会由图片文件名或 version_id 自动补齐。

`writeTaskMetrics` 始终读取本题全部日志并写题级 `OUTPUT_DIR/task-metrics.json`，其起止是题级状态时间；`rounds`/`case_metrics` 是明细容器，不会生成或核验每轮指标。`report` 始终写题级 `snapshot-usage.md`。套件 aggregate 只加 shared 和题级顶层，不能再把轮次明细加进去。

现有 `publish-reviewed-set.cjs` 支持 `round-01/...` 成品 stem 及追加文件的相对路径，并保留原 render metadata 的 round_id。其 `report_from` 仍调用题级 report，`metrics_extra` 仍刷新题级指标；它不会自动写每轮报告。调用方可以用追加文件把真正审查好的轮报告 `wx` 复制到轮目录；每轮指标用本工具另归档。

`root-review-close.cjs` 是整题关闭工具：声明必须覆盖本题全部 current finals 的哈希，preclose 会核对所有要求、轮文件与 completed_rounds，然后 taskEnd。不能在第一或第二轮用它代替轮归档。最后整题关闭时可复用已经实际登记的 `existing_view_id`，避免把一次物理查看重复登记；若真实又看了图，则应诚实计入新查看并处理此前轮指标是否需要新版本。这些判断来自代码阅读，尚未执行真正的多轮题目。

## 真实轮次使用方式

真实开始一轮时，root 在实际发生的时刻按现有流程记下边界，例如：

```javascript
s.taskCheckpoint(task, {event_type:'round-start', round_id:roundId});
```

完成本轮实际渲染、查看、必要修改、成品/报告留存和源数据审查后，再按真实时刻记录：

```javascript
s.taskCheckpoint(task, {event_type:'round-completed', round_id:roundId,
  completed_rounds:[roundId]});
```

上述是接口示例，不是已发生的事件。本工具不调用 checkpoint，也不替 root 声明完成。各轮 request/version/view/iteration/wait/artifact 必须使用本题及本轮真实标签；版本/请求/查看 ID 仍须全套唯一，前轮资产、报告和指标归档后才执行下一轮。前后比较可以引用上一轮的真实 before-view，其查看数仍留在原轮，不挪入新轮。

```powershell
node tmp/20261002-204314-6f31/_suite/archive-round-metrics.cjs TASK round-01 --check-only
node tmp/20261002-204314-6f31/_suite/archive-round-metrics.cjs TASK round-01
```

默认要求本题本轮恰有一个 `round-start`/`round-started` 与一个 `round-complete`/`round-completed` 事件。恢复过程中如果有多个边界，用 `--start-event ID --end-event ID` 明确引用已有真实事件；不接受裸起止字符串，不能用首请求或最后一次看图猜测整轮开始/完成时间。所有已标本轮的实际记录时间必须落在选定边界内，否则拒绝归档。

归档只生成两份相同字节的指标：`OUTPUT_DIR/<round_id>/task-metrics.json` 和 `TEMP_DIR/<round_id>/metrics/round-metrics-000001.json`（历史编号递增）。两个目标都 `wx`，不会覆盖前轮或现存同轮指标。指标保存真实边界 ID、起止/墙钟、请求耗时、已记录等待、全部过滤后的 records/ID/日志哈希、当前及历史 artifact、实际版本/查看/迭代计数、文件字节和未知消耗。token/图像输入/费用不能从顶层分摊或估造，保持 null。未测量 queue 时间为 null；没有 wait 记录只是没有记录，不足以隔离平台中断。

工具核对真实源文件哈希、请求/版本/成品关联、实际查看文件及完整 visual 记录；每个待归档当前成品还要求本轮已有相同字节的 root view_image 记录。历史查看如果打开的是后来被更新的交付指针，可以用本题仍保留的同 SHA 原响应证明原字节仍在；解析记录单列，不登记另一次查看。若相关版本的 view/iteration/artifact 漏标本轮，拒绝自动推断，root 应核对实际操作后追加诚实修正。最终数量、数据/几何/视觉质量及内容是否满足本题仍需 root 审查，本工具不能从文件/HTTP/查看记录推断。

归档前复核日志哈希未改变，并拒绝越界或重定向目标目录。磁盘错误可能只写入临时历史而没有完成输出，错误 JSON 保留具体进度；不回滚、不清理、不删除。已经存在的轮指标不会自动覆盖，需要按实际恢复方案保留/审查，再由 root 决定如何交付修订，不能直接重复命令覆盖。工具不写状态、报告、题级/套件指标，也不调用 render/view/iteration/taskEnd/aggregate/suiteEnd。

## 只读验证与局限

```powershell
node tmp/20261002-204314-6f31/_suite/archive-round-metrics.cjs --help
node tmp/20261002-204314-6f31/_suite/archive-round-metrics.cjs --inspect-case A11 page-01
node tmp/20261002-204314-6f31/_suite/archive-round-metrics.cjs --inspect-case A11 page-02
node tmp/20261002-204314-6f31/_suite/archive-round-metrics.cjs --inspect-case A12 mobile
node tmp/20261002-204314-6f31/_suite/archive-round-metrics.cjs --inspect-case A12 tablet
node tmp/20261002-204314-6f31/_suite/archive-round-metrics.cjs --inspect-case A12 desktop
node tmp/20261002-204314-6f31/_suite/archive-round-metrics.cjs --inspect-case A12 stage
```

`--inspect-case` 明确输出 `case_readonly_inspection`、`round_id:null`，真实 case 边界未知，起止/墙钟保持 null；另列实际日志首末时间，仅称 observed span。它不会写任何题目产物、报告、指标或轮文件。stdout 仅元数据，没有图片字节或报告原文。真实命令结果另存 `round-metrics-readonly-validation-v001.json`；本准备阶段不运行任何真正 round 归档或伪造 round fixture。

真实验证已结束：首批与静态修订后各执行一次 help 及上述六个 case，共14条命令均退出0；没有运行 round 归档。静态修订补足了历史交付指针查看的原字节解析，并修正了返回状态字段顺序；因此重复接口检查有实际代码变化依据。最终六个 case 的过滤结果如下，均没有漏标/冲突的 case 标签，当前成品哈希及已有 root 查看证据通过：

|已有范围|render 成功/失败|版本|真实查看事件|当前最终图|
|---|---:|---:|---:|---:|
|A11 page-01|2/0|2|7|1|
|A11 page-02|1/0|1|5|1|
|A12 mobile|1/0|1|3|1|
|A12 tablet|1/0|1|3|1|
|A12 desktop|1/3|4|3|1|
|A12 stage|2/3|5|7|1|

A11 两个 page 范围不包含其2条题级文档请求，A12 四个成品 layout 范围不包含2条 diagnostic 请求/版本，因此表格不是再次声明整题总量。A11/A12 题级报告与指标相对上一份真实源指纹保持相同；`suite.cjs`、publisher 和 root-close 未修改。辅助源指纹读取有1次本地命令语法失败，随后改用 here-string 输入成功，原错误与恢复命令保留在[验证记录](round-metrics-readonly-validation-v001.json)；没有服务、图片或状态变更。真实多轮事件选择、墙钟与 `wx` 归档分支尚未运行，不能把这些 case 检查称为多轮任务实测通过。
