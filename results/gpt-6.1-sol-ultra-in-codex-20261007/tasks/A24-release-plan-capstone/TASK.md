> 全套运行说明：本题由总根入口自动执行。遵循 [总AGENTS.md](../../AGENTS.md)，
> 使用同一run_id的 `outputs/<run_id>/A24/` 和 `tmp/<run_id>/A24/`。
> 单题完成后继续总清单下一题，不等待逐题确认；本题内容要求保持有效。

# A24 · 双团队约束下的发布作战计划

先完整阅读 [AGENTS.md](AGENTS.md) 的执行、目录、留痕和指标约定；该文件是本任务要求的一部分。

## 任务

根据 inputs/release.json，制作1920×1080执行泳道、1200×1600决策简报、
720×1280手机行动卡。发布日09:00开工，16:00截止。design与engineering各只有
一个团队，同团队不可并行，不可抢占；tasks.teams列可选择的执行团队，
如有两项表示任选其一，不是占用两团队。任务必须完整执行时长、先决完成后
才能开始，不得擅自改依赖、缩时或删除检查环节。团队切换无额外耗时。

自行计算一个满足约束且尽早完成的排程；给忽略资源约束的关键路径时长和
总工作量/两团队的下界。不要求证明全局最优，但不能把未证明的最好方案称为
最优；若提供可核验最优证明可注明。图中真实时间按同尺度绘制，任务块起止/
团队/编号/标签能读；依赖可以用编号索引表达，不要画满交叉线盖住时间块。
执行图展示空档与截止线，简报展示依赖概览、总工时、完成时间、剩余缓冲、
三风险/对策和排程依据；手机卡按时间序给12任务、团队、起止及风险提醒。
三图不得互相矛盾；横屏正文≥20、竖页≥24、手机≥20。品牌“叠光 · 发布演练”。
附 schedule.json（精确起止/团队/依赖）、schedule-audit.json（资源冲突/依赖/
时长/下界/缓冲）与 content-map.json。实际看三图，尤其短任务与长中文标签。

## 输入文件

- [release.json](inputs/release.json)

## 指定交付

| PNG与对应DSL | 尺寸 | 用途 |
|---|---|---|
| `execution-board.png` + `execution-board.snapshot` | 1920×1080 | 团队泳道执行图 |
| `decision-brief.png` + `decision-brief.snapshot` | 1200×1600 | 决策简报 |
| `action-card.png` + `action-card.snapshot` | 720×1280 | 手机行动卡 |

额外文件：`schedule.json`、`schedule-audit.json`、`content-map.json`。

同时交付 `snapshot-usage.md`、`task-metrics.json`，过程日志在临时目录。

完成时依据实际图像自检；所有指定最终PNG都须是服务真实响应且有同名 `.snapshot`。
