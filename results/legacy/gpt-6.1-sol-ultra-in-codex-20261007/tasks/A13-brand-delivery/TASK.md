> 全套运行说明：本题由总根入口自动执行。遵循 [总AGENTS.md](../../AGENTS.md)，
> 使用同一run_id的 `outputs/<run_id>/A13/` 和 `tmp/<run_id>/A13/`。
> 单题完成后继续总清单下一题，不等待逐题确认；本题内容要求保持有效。

# A13 · 品牌标志到完整活动应用

先完整阅读 [AGENTS.md](AGENTS.md) 的执行、目录、留痕和指标约定；该文件是本任务要求的一部分。

## 任务

虚构品牌“叠光 / Layerlight”提供结构化视觉工具，概念是“信息叠加后仍然清晰”。
禁用现成标志、文字整体当图标、外部图片。先用DSL做两个真正不同几何方向
的预览（各512×512透明PNG，保留临时目录），看图选择后完善同一方案。
最终交付：512×512透明彩色图标、512×512透明纯黑图标、1200×400品牌横幅、
1080×1350发布海报。两图标几何相同，抗锯齿alpha允许；非透明黑版RGB必须为0。
图标最多6个主要几何构件，在32×32仍能识别轮廓与关键负空间。
横幅含“叠光 Layerlight”“把复杂信息，组织成清晰画面”。海报另含
“2026.11.07 · ONLINE”“OPEN BETA”“layerlight.example.org”。不能用品牌图标
的渲染PNG嵌到两应用，须用同一DSL几何规则生成。海报有独立构图，非放大横幅。
交付 brand-system.json（色彩、比例、图标构件、最小留白、各应用映射）及
rationale.md≤300字：两个方向差异、实际预览选择依据、小尺寸改进。
大图与32×32缩略均实际查看，缩略仅作检查预览、保存在临时目录。

## 输入文件

无附加输入；文案和数值均在任务说明中。

## 指定交付

| PNG与对应DSL | 尺寸 | 用途 |
|---|---|---|
| `symbol-color.png` + `symbol-color.snapshot` | 512×512 | 透明彩色图标 |
| `symbol-black.png` + `symbol-black.snapshot` | 512×512 | 透明纯黑图标 |
| `brand-banner.png` + `brand-banner.snapshot` | 1200×400 | 品牌横幅 |
| `launch-poster.png` + `launch-poster.snapshot` | 1080×1350 | 发布海报 |

额外文件：`brand-system.json`、`rationale.md`。

同时交付 `snapshot-usage.md`、`task-metrics.json`，过程日志在临时目录。

完成时依据实际图像自检；所有指定最终PNG都须是服务真实响应且有同名 `.snapshot`。
