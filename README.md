# Snapshot DSL 模型评测任务

以 [task-suite/](task-suite/README.md) 作为模型任务根目录，一次提交并按顺序完成全部30题：进阶 A01–A24、开放创作 B01–B06，至少124张指定最终图片。A21/A22包含预置三轮要求；每道开放创作题至少10件完整独立作品。

## 使用

1. 将 `task-suite/` 设为模型工作根目录，发送 [START-PROMPT.txt](task-suite/START-PROMPT.txt)。模型需能读取文件、访问官方文档、请求服务并实际查看图片。
2. 模型按 [TASKS.md](task-suite/TASKS.md) 连续完成所有任务，最终 DSL 使用 `.snapshot` 后缀。结果保存在 `outputs/<run_id>/`，过程文件保存在 `tmp/<run_id>/`，不清理过程留痕。

不限制渲染请求或视觉迭代次数。模型应逐件实际看图完善，记录迭代过程、真实耗时和可获取的消耗，并交付 Snapshot 使用情况说明与踩坑记录。详细约定见 [AGENTS.md](task-suite/AGENTS.md)，服务与范围配置见 [run-config.json](task-suite/run-config.json)。

文档：[Snapshot 官方文档](https://snapshot.muedsa.com/) · [Open Snapshot AI 服务指南](https://open-snapshot.muedsa.com/ai-guide.md)。

## 目录

- `task-suite/`：唯一维护的任务源，含30题、输入资料、配置及报告模板，可直接交给模型。
- [evaluation/](evaluation/README.md)：评测端评分材料、参考图作者源码、真实服务记录及发布检查；不要交给被测模型。

两张参考 PNG 已通过真实服务生成并查看；30题尚未整套试跑。发布校验通过只说明任务资料和分发完整，正式跨模型比较前仍需校准工作量与评审一致性。
