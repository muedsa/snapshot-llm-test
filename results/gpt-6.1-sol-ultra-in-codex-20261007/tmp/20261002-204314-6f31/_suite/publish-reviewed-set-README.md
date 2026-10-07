# Publish an actually reviewed set

共享准备工具，归属 `shared`，固定复用当前 `20261002-204314-6f31` 运行的 `suite.cjs`。本工具没有制作或完成任何题目；文件预检不能替代真实服务、实际看图或题目审查。

```powershell
node tmp/20261002-204314-6f31/_suite/publish-reviewed-set.cjs A10 path/to/publish-manifest.json --check-only
node tmp/20261002-204314-6f31/_suite/publish-reviewed-set.cjs A10 path/to/publish-manifest.json
```

上面的任务 ID 仅表示参数位置；不是已经执行的记录。任务必须是状态指针内当前 `in_progress` 的题。`--check-only` 只读取来源、当前状态及留痕，输出 JSON 元数据，不写入成品、报告、指标或状态。

Manifest 结构：

```json
{
  "finals": [
    {
      "meta_path": "../requests/TASK-request-000001/render-result.json",
      "stem": "round-01/example",
      "title": "这一张真实审查结果的标题",
      "independent_case": false,
      "details": {}
    }
  ],
  "additional_files": [
    {
      "source": "../geometry-audit-v001.json",
      "relative_output": "round-01/geometry-audit.json"
    }
  ],
  "report_from": "actual-report-v001.md",
  "metrics_extra": {}
}
```

以上是接口示例，不是本次调用或留痕。`finals` 至少一项，`title` 与明确的布尔 `independent_case` 必填。`additional_files`、`metrics_extra`、`details` 可省略。所有来源路径相对 manifest 所在目录解析，也可传绝对路径；目标 stem 与 `relative_output` 必须为任务输出目录内的安全相对路径。stem 不带 `.png`/`.snapshot` 后缀，支持 `round-01/...` 或 `case-01/...` 等目录。

完整预检在任何发布之前进行：

- render metadata 必须是本题临时目录内，与原请求 envelope 同目录的真实 `render-result.json`，HTTP 成功且没有尺寸错误。
- 原服务 PNG、完整 `.snapshot`、实际提交的 input、请求与版本日志相互匹配；记录哈希、实际字节、PNG 尺寸与请求期望尺寸一致。DSL 通过 UTF-8 无损往返检查，以保证 `acceptFinal` 的字符串读取不会改变提交字节。
- 本题 `views.jsonl` 必须已有 `reviewer: "root"`、`tool: "view_image"`、有效时间、非空观察与相同 PNG 哈希的实际查看记录；被查看文件仍存在且字节与记录一致。默认选最后一条匹配记录，`details.root_view_id` 可指定其中一条。工具只核验已有记录，不能证明记录本身是真实操作，也不产生新查看事件。
- `details.case_id`/`round_id` 如存在必须等于原 render metadata；`independent_case: true` 还要求原 metadata 有非空 `case_id`。工具不会从题材或图像推断创作独立性。
- 所有 final/additional 目标没有已有文件或重名，使用 `wx`，且位于本题输出内；拒绝绝对目标、路径穿越、Windows 保留名和重定向目录。追加文件不能占用顶层报告/指标指针；PNG 必须经过 `finals` 发布。
- report source 与每个追加来源必须是非空现存文件；报告是 UTF-8 原文。工具不生成报告文字，也不能核验报告与额外指标说明中的事实是否正确，调用方必须先审查。额外指标照 `suite.cjs` 既有规则处理，不构造 token 或费用估计。

预检通过后，再确认全部来源未发生变化与全部目标仍为空，然后顺序运行 `s.acceptFinal`、`wx` 复制追加文件、`s.report`、`s.writeTaskMetrics`。报告与指标属于允许更新的当前指针，其历史保存在临时目录；最终 PNG/DSL 与追加文件不覆盖。发布的 artifact 记录包含匹配的 `reviewed_view_id`。

工具绝不调用 render、view、iteration、checkpoint、taskEnd、aggregate 或 suiteEnd。任务状态仍为 `in_progress`；root 必须完成剩余内容与文件审查、轮次/用例检查点及关题流程。工具的 JSON 输出只包含路径、ID、尺寸、哈希、字节数与计数，不包含图片数据或报告原文。

发生发布阶段磁盘错误或竞态时不会回滚、清理、删除已写文件。错误 JSON 含已登记成品/追加文件清单与当前阶段；`wx` 可能在已写 PNG、未写 DSL 的时刻中断，此时不能把一套已完整发布作为事实。先核对实际文件和日志，再准备只含未发布条目的新 manifest；不能直接重复原 manifest 覆盖成品。本工具不能排除预检后发生的所有跨进程竞态，仍需 root 单写者约定。

## 接口验证

仅执行 `--help` 验证 CLI，未调用服务、看图、发布或改变任务状态。实际命令：

```powershell
node tmp/20261002-204314-6f31/_suite/publish-reviewed-set.cjs --help
```

真实命令结果：`exit_code: 0`，`wall_time_seconds: 0.1474308`，工具输出块 `981509`。stdout 原文保留如下（没有执行示例 manifest）：

```text
Usage:
  node publish-reviewed-set.cjs TASK manifest.json [--check-only]
  node publish-reviewed-set.cjs --help

Manifest:
  {
    "finals": [{"meta_path":".../render-result.json", "stem":"round-01/example",
      "title":"Actual reviewed result", "independent_case":false, "details":{}}],
    "additional_files": [{"source":".../audit.json", "relative_output":"audit.json"}],
    "report_from":".../actual-report.md",
    "metrics_extra": {}
  }

Source paths resolve relative to the manifest file, or may be absolute.
Stems and relative_output must stay inside the selected task output directory.
All sources, successful request/version evidence, PNG/DSL hashes, actual root
view_image records and unused destinations are checked before any publication.
--check-only reads and reports metadata; it publishes nothing.
Publication preserves source bytes and never overwrites final/additional files.
Only acceptFinal, wx additional-file copies, report and writeTaskMetrics are run.
The helper never renders, views, records iterations or changes suite/task state.
It does not judge report truth, creative independence or visual quality.
```
