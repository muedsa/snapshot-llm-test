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
必显字段在四种画布中的坐标区域和保留情况，以及卡片ID对应关系。小屏内容不得省略或改写成缩写。

## 必显文案与追踪字段

四种尺寸均须完整显示title、subtitle、date、time、location、cta、website，
以及cards中每张卡的title和detail。cards[].id仅用于稳定追踪卡片身份，
不属于“一字不丢”的必显文案；可以显示ID，但不要求为它分配可见标签。
content-map.json以C1–C6和字段路径关联每张卡，逐画布记录必显字段的原文、
实际显示文本、文字盒、字号和是否完整；ID记录在映射中，不能因未印在图上判缺字。
允许排版自动折行或增加不改变词语的换行，保留原文字词、数字、大小写、标点及
有意义的空格；不使用省略号、缩写、改写或删句。字段坐标不代替实际看图核对。

## 专用审计JSON字段

本题指定的专用JSON须遵循[最小字段约定](templates/audit-fields.json)，可增加字段；
该文件只解释结构、单位、坐标/路径基准及证据要求，不是已完成答案。多轮任务复用
同名文件的字段约定，仍按task.json各轮完整路径交付；不要在输出根增加重复文件。

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
