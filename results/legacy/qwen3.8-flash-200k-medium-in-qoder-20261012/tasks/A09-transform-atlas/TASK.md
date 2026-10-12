> 全套运行说明：本题由总根入口自动执行。遵循 [总AGENTS.md](../../AGENTS.md)，
> 使用同一run_id的 `outputs/<run_id>/A09/` 和 `tmp/<run_id>/A09/`。
> 单题完成后继续总清单下一题，不等待逐题确认；本题内容要求保持有效。

# A09 · 十二个非对称图形变换标本

先完整阅读 [AGENTS.md](AGENTS.md) 的执行、目录、留痕和指标约定；该文件是本任务要求的一部分。

## 任务

制作1600×1200变换图谱，4列×3行，每格300×250，格间32；整体居中，格外
保留标题与图例。inputs/stamp.json 定义一个120×120透明印章：3个彩色矩形与
一个黑圆点。所有局部坐标从印章左上角算，矩形之间部分相邻，用圆点消除对称。
inputs/transforms.json 给12个从左到右、从上到下的变换列表；操作按列表顺序，
每步围绕局部(60,60)进行。像素坐标x向右、y向下，因此“顺时针”按图像方向。
mirror_horizontal 表示左右镜像，mirror_vertical 表示上下镜像。最终局部中心
放到每格中心。图中编号、操作短名与刻度辅助线齐全；不裁切变换后的主体。
各格主体必须用Transform.matrix表示最终组合变换，不能直接手改形状坐标
冒充使用矩阵；圆点随同变换。T07与T08要显示操作顺序差异。
附 geometry-audit.json：列主序4×4矩阵、每矩形四角、圆点中心、最终外接框，
以及±1.5像素的视觉/像素核对方法（反走样边缘例外）。标签≥20。

## 输入文件

- [stamp.json](inputs/stamp.json)
- [transforms.json](inputs/transforms.json)

## 指定交付

| PNG与对应DSL | 尺寸 | 用途 |
|---|---|---|
| `transform-atlas.png` + `transform-atlas.snapshot` | 1600×1200 | 十二变换标本 |

额外文件：`geometry-audit.json`。

同时交付 `snapshot-usage.md`、`task-metrics.json`，过程日志在临时目录。

完成时依据实际图像自检；所有指定最终PNG都须是服务真实响应且有同名 `.snapshot`。
