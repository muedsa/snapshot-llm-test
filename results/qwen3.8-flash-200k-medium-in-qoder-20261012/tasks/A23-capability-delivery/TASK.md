> 全套运行说明：本题由总根入口自动执行。遵循 [总AGENTS.md](../../AGENTS.md)，
> 使用同一run_id的 `outputs/<run_id>/A23/` 和 `tmp/<run_id>/A23/`。
> 单题完成后继续总清单下一题，不等待逐题确认；本题内容要求保持有效。

# A23 · 格式边界下的动画分镜交付

先完整阅读 [AGENTS.md](AGENTS.md) 的执行、目录、留痕和指标约定；该文件是本任务要求的一部分。

## 任务

客户希望获得“文字可编辑SVG、CMYK印刷稿、6帧透明GIF动画和PNG封面”，主题
为“结构汇聚成图像”，只准Snapshot类DOM DSL和open-snapshot服务作图。
先依据实际文档/接口判定哪些原生支持，别编造动画、路径、SVG、CMYK参数。
本题已授权以下替代，无需再次询问：交付1200×800 RGB PNG封面，以及6张
600×600透明PNG关键帧，分别保存完整DSL；用 timing.json 表达250ms/帧、
循环播放和帧序。无需合成GIF、矢量化、转换CMYK或创建假的目标格式文件。
文字“从结构到画面”在封面可读；动画帧不含文字，包含始终存在的12个几何
单元，由分散逐步汇聚，末帧构成可识别图形。各帧主体颜色/数量/尺度一致，
单元轨迹连续、无突然消失，透明背景真实。可复用参数生成DSL，不嵌预渲染帧。
6帧首尾若不连续，可在timing说明循环会跳变，不要宣称无缝；可设计闭合轨迹
实现无缝，但要给对应证据。逐帧和接触表看图检查。附 limitations.md（逐项
请求/支持情况/依据/替代/仍需外部后续工作）、frame-data.json 与 timing.json。
这里考察完整替代交付，不能仅写“不支持”而结束，也不要求额外工具导出格式。

## 输入文件

无附加输入；文案和数值均在任务说明中。

## 指定交付

| PNG与对应DSL | 尺寸 | 用途 |
|---|---|---|
| `cover.png` + `cover.snapshot` | 1200×800 | RGB封面 |
| `frame-01.png` + `frame-01.snapshot` | 600×600 | 透明关键帧1 |
| `frame-02.png` + `frame-02.snapshot` | 600×600 | 透明关键帧2 |
| `frame-03.png` + `frame-03.snapshot` | 600×600 | 透明关键帧3 |
| `frame-04.png` + `frame-04.snapshot` | 600×600 | 透明关键帧4 |
| `frame-05.png` + `frame-05.snapshot` | 600×600 | 透明关键帧5 |
| `frame-06.png` + `frame-06.snapshot` | 600×600 | 透明关键帧6 |

额外文件：`limitations.md`、`frame-data.json`、`timing.json`。

同时交付 `snapshot-usage.md`、`task-metrics.json`，过程日志在临时目录。

完成时依据实际图像自检；所有指定最终PNG都须是服务真实响应且有同名 `.snapshot`。
