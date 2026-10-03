# 评测端材料

被测模型只接收 `task-suite/`，不要将本目录或整个仓库作为其工作根目录。通过实际文件权限隔离评分检查点、参考答案与作者源码。

- [进阶评分说明](task-pack-v2/README.md)：A01–A24检查点、计算/路线参照及A15/A16参考图生成留痕。
- [开放创作评分说明](task-pack-creative/README.md)：B01–B06检查点与评分权重。
- [全套发布检查](task-suite/authoring-validation.json)：当前任务源和完整ZIP的校验结果，不代表模型完成情况。

现有子目录名保留以保持原始参考图服务记录中的路径可追溯。旧分发目录和单题压缩包已移除；全部题目只在 `task-suite/` 维护。A21/A22后续轮要求只保留在任务根的对应 `rounds/` 中，按预置连续执行模式评测。

参考生成记录中的 `published_input` 是当时发布路径；现在对应输入在 `task-suite/tasks/A15-reference-reconstruction/inputs/reference.png` 与 `task-suite/tasks/A16-visual-data-forensics/inputs/flawed-report.png`，图片字节保持不变。
