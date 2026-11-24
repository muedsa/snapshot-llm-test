# A23 Snapshot 使用与自检报告

- 状态：completed
- 运行 ID：`20261124T113838+0800-aac601`
- 输出根：`outputs/20261124T113838+0800-aac601/A23`（path_base=suite_root）
- 临时根：`tmp/20261124T113838+0800-aac601/A23`（path_base=suite_root）
- 服务基址：https://open-snapshot.muedsa.com

## 文档与工具应用

实际读取服务指南、OpenAPI、Parser 语法、标签与文本属性、示例、字体、布局、绘制、错误处理与数据模板文档；原始响应缓存在 `tmp/20261124T113838+0800-aac601/_suite/shared/`。服务请求使用 UTF-8 纯文本 POST `/snapshot`，依据 HTTP 状态、Content-Type、X-Request-Id 与 Server-Timing 留痕。字体从真实 `/fonts` 响应选择 `Noto Sans CJK SC`。主体、图表、文字和几何均由完整 Snapshot DSL 构造。

## 视觉自检

| 检查项 | 结果与证据 |
|---|---|
| formats | 依据实际指南/OpenAPI判定原生仅输出静态位图；未编造SVG、CMYK、GIF或时间轴参数。 |
| cover | 1200×800 RGB PNG封面；‘从结构到画面’可读；服务原始响应与DSL匹配。 |
| frames | 六张600×600透明PNG均实际查看；四角alpha=0，U01–U12逐帧存在且可见。 |
| conservation | 12单元几何、未旋转宽高、RGB与自身alpha跨帧守恒；只改变位置和旋转。 |
| trajectory | smoothstep设计轨迹、逐单元位移/角差与1250→1500/0ms接缝均记录；明确非无缝。 |
| contact_sheet | 透明棋盘接触表仅存临时目录，已实际查看并与六张原图逐一核对。 |

## 设计选择

深色封面与高对比相机图形；关键帧从分散的12个构件汇聚成相机，透明背景便于外部合成。

## 问题、修改与验证

依据真实接口提供完整PNG替代，未制作伪目标格式；循环保留但接缝跳变已明确记录。

## 交付文件

- `cover.png`
- `cover.snapshot`
- `frame-01.png`
- `frame-01.snapshot`
- `frame-02.png`
- `frame-02.snapshot`
- `frame-03.png`
- `frame-03.snapshot`
- `frame-04.png`
- `frame-04.snapshot`
- `frame-05.png`
- `frame-05.snapshot`
- `frame-06.png`
- `frame-06.snapshot`
- `limitations.md`
- `frame-data.json`
- `timing.json`
