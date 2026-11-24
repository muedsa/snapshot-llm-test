# A19 Snapshot 使用与自检报告

- 状态：completed
- 运行 ID：`20261124T113838+0800-aac601`
- 输出根：`outputs/20261124T113838+0800-aac601/A19`（path_base=suite_root）
- 临时根：`tmp/20261124T113838+0800-aac601/A19`（path_base=suite_root）
- 服务基址：https://open-snapshot.muedsa.com

## 文档与工具应用

实际读取服务指南、OpenAPI、Parser 语法、标签与文本属性、示例、字体、布局、绘制、错误处理与数据模板文档；原始响应缓存在 `tmp/20261124T113838+0800-aac601/_suite/shared/`。服务请求使用 UTF-8 纯文本 POST `/snapshot`，依据 HTTP 状态、Content-Type、X-Request-Id 与 Server-Timing 留痕。字体从真实 `/fonts` 响应选择 `Noto Sans CJK SC`。主体、图表、文字和几何均由完整 Snapshot DSL 构造。

## 视觉自检

| 检查项 | 结果与证据 |
|---|---|
| grid coverage | 64对象按行优先编号；4色各16、4形各16、全部16种颜色×形状组合各4；每种颜色×形状均覆盖48/64/80。 |
| row constraints | 每行至少3色3形，scene-data.json记录实际频数、组合覆盖和逐行计数。 |
| questions | 12道网格题+2道遮挡题；至少4道两步关系；questions.json不含答案。 |
| occlusion equivalence | A/B原始PNG保留；Pillow解码8位未预乘RGBA后不同像素0、最大通道差0。 |
| visual review | 三张最终PNG实际查看；网格另以四个象限放大检查全部64主体与编号。 |

## 设计选择

固定种子生成受约束网格，题目从实际几何计算；遮挡案例用不透明前景保证隐藏差异不可见。

## 问题、修改与验证

首次渲染后完成静态覆盖检查、三图查看、四象限标签复核和RGBA逐像素等价检查；未发现需修改的交付缺陷。

## 交付文件

- `outputs/20261124T113838+0800-aac601/A19/grid-scene.png`
- `outputs/20261124T113838+0800-aac601/A19/grid-scene.snapshot`
- `outputs/20261124T113838+0800-aac601/A19/occlusion.png`
- `outputs/20261124T113838+0800-aac601/A19/occlusion.snapshot`
- `outputs/20261124T113838+0800-aac601/A19/occlusion-alternative.png`
- `outputs/20261124T113838+0800-aac601/A19/occlusion-alternative.snapshot`
- `outputs/20261124T113838+0800-aac601/A19/scene-data.json`
- `outputs/20261124T113838+0800-aac601/A19/questions.json`
- `outputs/20261124T113838+0800-aac601/A19/answers.json`
- `outputs/20261124T113838+0800-aac601/A19/equivalence.json`
