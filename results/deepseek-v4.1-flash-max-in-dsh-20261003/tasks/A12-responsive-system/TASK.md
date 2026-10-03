> 全套运行说明：本题由总根入口自动执行。遵循 [总AGENTS.md](../../AGENTS.md)，
> 使用同一run_id的 `outputs/<run_id>/A12/` 和 `tmp/<run_id>/A12/`。
> 单题完成后继续总清单下一题，不等待逐题确认；本题内容要求保持有效。

# A12 · 四断点完整内容视觉系统

先完整阅读 [AGENTS.md](AGENTS.md) 的执行、目录、留痕和指标约定；该文件是本任务要求的一部分。

## 任务

使用 inputs/content.json 为同一活动制作四尺寸：360×800、768×1024、1440×900、
1920×1080。每张都要保留全部主信息、网站及六张卡的标题和detail，一字不丢；
CTA是文字，不需要生成二维码。不能用裁切、拉伸或整图Image实现适配。
手机正文≥16、卡标题≥18；其余正文≥20、主标题≥40。留白、安全边距至少
手机16/其他32；实际文字盒不能重叠。自行规划手机单列/平板/桌面组合，所有
尺寸统一色彩、形态与层级，装饰使用相同核心构件但可以重排。
输入title与subtitle都完整可读，信息之间不因缩屏失去联系。可用生成器从
一份内容与设计参数生成四个完整DSL，但每张仍要实际渲染并查看。
交付 design-tokens.json 与 content-map.json：颜色/字号/间距/组件规则、每个
输入字段在四种画布中的坐标区域和保留情况。小屏内容不得省略或改写成缩写。

## 输入文件

- [content.json](inputs/content.json)

## 指定交付

| PNG与对应DSL | 尺寸 | 用途 |
|---|---|---|
| `mobile.png` + `mobile.snapshot` | 360×800 | 窄手机 |
| `tablet.png` + `tablet.snapshot` | 768×1024 | 平板 |
| `desktop.png` + `desktop.snapshot` | 1440×900 | 桌面 |
| `stage.png` + `stage.snapshot` | 1920×1080 | 大屏 |

额外文件：`design-tokens.json`、`content-map.json`。

同时交付 `snapshot-usage.md`、`task-metrics.json`，过程日志在临时目录。

完成时依据实际图像自检；所有指定最终PNG都须是服务真实响应且有同名 `.snapshot`。
