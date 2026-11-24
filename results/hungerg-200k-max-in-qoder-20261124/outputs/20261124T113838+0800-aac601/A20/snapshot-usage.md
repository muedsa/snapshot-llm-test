# A20 Snapshot 使用与自检报告

- 状态：completed
- 运行 ID：`20261124T113838+0800-aac601`
- 输出根：`outputs/20261124T113838+0800-aac601/A20`（path_base=suite_root）
- 临时根：`tmp/20261124T113838+0800-aac601/A20`（path_base=suite_root）
- 服务基址：https://open-snapshot.muedsa.com

## 文档与工具应用

实际读取服务指南、OpenAPI、Parser 语法、标签与文本属性、示例、字体、布局、绘制、错误处理与数据模板文档；原始响应缓存在 `tmp/20261124T113838+0800-aac601/_suite/shared/`。服务请求使用 UTF-8 纯文本 POST `/snapshot`，依据 HTTP 状态、Content-Type、X-Request-Id 与 Server-Timing 留痕。字体从真实 `/fonts` 响应选择 `Noto Sans CJK SC`。主体、图表、文字和几何均由完整 Snapshot DSL 构造。

## 视觉自检

| 检查项 | 结果与证据 |
|---|---|
| mapping | 24个锚点严格按(280+10.4x,920−7.6y)映射，主图区固定1040×760。 |
| labels | 24个标签均含ID、name、value；正文20px；左右各12个，按锚点纵序排列。 |
| geometry | 标签最小间距12.0px；点重叠失败0；引导线交叉0。 |
| leaders | 24条两段折线从所属圆周连到盒边；不穿任何标签；共线重叠与自交均为0。 |
| visual review | 中心6点与引导线3倍放大、左右标签2倍放大及1600×1100整图均实际查看。 |

## 设计选择

左右标签列与固定gutter弯折线使复杂中心簇保持可追踪；金色点与金框标出value最高3点。

## 问题、修改与验证

v001几何审计通过，但实际查看发现中间y刻度文字被水平引导线压住；v002仅保留0/100端点刻度后重新渲染，整图、左右标签与中心6点复查通过。

## 交付文件

- `outputs/20261124T113838+0800-aac601/A20/annotated-map.png`
- `outputs/20261124T113838+0800-aac601/A20/annotated-map.snapshot`
- `outputs/20261124T113838+0800-aac601/A20/label-layout.json`
- `outputs/20261124T113838+0800-aac601/A20/layout-audit.json`
