# 单题执行清单（所有子任务通用）

配合 `DSL-HANDBOOK.md` 一起读。你被指派的是某一个具体题目（见任务提示里的 TASK_ID 与题目目录）。

## 目录约定（run_id 固定为 20261004-182918，不要自己另建 run_id）

- 输出：`outputs/20261004-182918/<TASK_ID>/`
- 临时：`tmp/20261004-182918/<TASK_ID>/`
- 共享工具：`tmp/20261004-182918/_suite/`（`snapkit.py` `dsllib.py` `state.py` `finalize.py` `wrapup.py` `crop.py`）

## 步骤

1. 读 `tmp/20261004-182918/_suite/DSL-HANDBOOK.md`（实测 DSL 结论，必读）。
2. 读你的题目：`tasks/<目录>/TASK.md`（**从第 5 行开始**，前 4 行是重复的套件说明）、
   `task.json`（看 `required_outputs` / `additional_outputs` 的精确文件名与尺寸）、
   `inputs/` 下所有输入文件（CSV/JSON/TXT 全部读完）。
   再看一眼 `tasks/<目录>/AGENTS.md` 确认没有额外硬约束。
3. 写 `tmp/20261004-182918/<TASK_ID>/build_<id>.py`：读输入 → 计算 → 用 `dsllib` 拼 DSL →
   `snapkit.render(...)` → 写附加 JSON → 打印 `D.warnings()`。
   把每次的 DSL 也存一份带序号的副本到临时目录（`drafts/vNN.snapshot`），便于追溯。
4. **渲染后必须用 read 工具真的打开 PNG 看**。同时逐条处理 `D.warnings()`。
   细节看不清用 `crop.py` 放大。改 → 重渲染 → 再看，循环到满足 TASK.md 每一条要求。
   没有迭代次数上限，也不要为了"看起来完成"而提前收工。
5. 最终产物写入输出目录：TASK.md 指定的每张 PNG（**服务真实响应的原始字节，不许后处理**）
   + 同名 `.snapshot`（与最终渲染完全一致的完整 DSL）+ 附加 JSON + `snapshot-usage.md` + `task-metrics.json`。
6. 写 `tmp/20261004-182918/<TASK_ID>/log_<id>.py`，调用 `wrapup.wrapup(...)` 写入迭代记录、
   生成 `task-metrics.json`、更新套件状态。**必须执行。**

## `snapshot-usage.md` 至少包含

- 完成状态、输出/临时目录路径
- 实际使用的服务文档与字体（写清是真实抓取还是复用本题库已有抓取）
- 实际用到的标签与属性，以及本题踩到的 DSL 语义坑
- 逐图/逐项自检表：把 TASK.md 的每条硬指标列出来，逐条写"实际值 + 结论"
- 问题与修复表：问题现象 / 定位方式 / 修复方式 / 复验结果
- 未解决事项与如实说明（没遇到错误就写"未遇到"；推测要标明；token/费用等平台未提供的
  计量一律 `null`，**绝不允许按字数或余额估算**）

## 绝对禁止

- 用别的绘图库画主体再 `<Image>` 嵌入；用外部图片。
- 臆造标签、属性、枚举值、字体、接口返回。
- 删掉出错区块来宣称"修好了"。
- 把 `token`/`cost`/`input_tokens` 之类填成估算数字。
- 用 PowerShell 的 `Get-Content`/`Set-Content` 改写 UTF-8 源文件（会破坏中文编码）。
  改文件请用编辑工具，或在 Python 里 `open(..., encoding='utf-8')`。

## 返回总结的格式

(a) 交付文件清单与尺寸；(b) TASK.md 逐条满足情况；(c) 渲染次数/看图次数/改了什么；
(d) 服务错误与修复；(e) 未解决事项。全程中文。