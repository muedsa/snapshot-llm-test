# Suite artifacts 对象去重修复

运行：20261002-204314-6f31。修复执行时间：2026-10-03T17:01:29Z 附近。

本次仅修改 `suite.cjs` 中 taskCheckpoint/taskEnd 的 artifacts 合并逻辑。原脚本已完整保存为 `suite-artifact-dedupe-before-000001.cjs`。其他集合仍沿用原字符串/引用 Set 行为，原 API、requests/views/artifacts JSONL、原始响应、最终图片、历史快照不变。

原问题：读取 JSON 状态后，相同 artifact 会成为新的对象；Set 按对象引用而非登记 ID 或文件路径比较，因此重复传入已登记 artifact 会在 suite-state.artifacts 中保留多份。实际 artifacts.jsonl、gallery 与 countsFor 仍按图片路径取最终作品，本问题未产生新的真实作品或 HTTP 请求。

新逻辑保留第一条真实记录；任一登记 ID 相同或规范化绝对 image_path 相同即去重。Windows 文件路径按大小写不敏感比较，slash 差异也规范化。独立路径且独立 ID 的作品保留。对象没有身份字段时保留原引用去重语义，原始值按 Set 去重。

验证脚本：`test-artifact-dedupe-000001.cjs`。验证结果：`artifact-dedupe-verification-000001.json`。隔离夹具：`artifact-dedupe-fixture-000001/`。所有夹具均明确为 synthetic regression only，不算任何真实任务、服务请求、图像或完成证据。

验证覆盖实际 helper 的 taskCheckpoint/taskEnd：空 artifacts 数组清除反序列化克隆重复；末尾合并克隆对象及同图异 ID 记录仍去重；独立图保留；字符串 visual review ID 不变；已有夹具历史快照 SHA-256 不变。全部通过。

本代理未更新真实 suite-state。root 是唯一状态写入者，可在后续真实 checkpoint 中对已重复任务传入 artifacts: [] 清理当前指针；或在一条 root checkpoint mutator 中按相同规则清理所有 task.artifacts。不得修改过去的 state-*.json。

共享修复未增加 HTTP、DSL、看图、作品或视觉迭代统计。
