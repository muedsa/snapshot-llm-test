# A21 round-02 Snapshot 使用与自检报告

- 状态：completed
- 运行 ID：`20261124T113838+0800-aac601`
- 输出根：`outputs/20261124T113838+0800-aac601/A21`（path_base=suite_root）
- 临时根：`tmp/20261124T113838+0800-aac601/A21`（path_base=suite_root）
- 服务基址：https://open-snapshot.muedsa.com

## 文档与工具应用

实际读取服务指南、OpenAPI、Parser 语法、标签与文本属性、示例、字体、布局、绘制、错误处理与数据模板文档；原始响应缓存在 `tmp/20261124T113838+0800-aac601/_suite/shared/`。服务请求使用 UTF-8 纯文本 POST `/snapshot`，依据 HTTP 状态、Content-Type、X-Request-Id 与 Server-Timing 留痕。字体从真实 `/fonts` 响应选择 `Noto Sans CJK SC`。主体、图表、文字和几何均由完整 Snapshot DSL 构造。

## 视觉自检

| 检查项 | 结果与证据 |
|---|---|
| copy | 两图必需文案完整，标题与新增信息分带排版，文字盒无碰撞。 |
| brand | 四类品牌构件跨图、跨轮保持可识别形态。 |
| visual | 两张最终服务PNG均已实际查看，尺寸、层级、留白与文字可读性通过。 |
| long_title | 三行长标题字号52/50，未使用变形压窄；赞助方与参加方式独立显示。 |

## 设计选择

统一紫色品牌体系与四构件图形，竖版纵向叙事、横版左右分区；顶部/底部保留扩展留白。

## 问题、修改与验证

相对round-01替换为三行长标题，新增独立赞助/参加信息带；品牌构件仅缩放移动，日期、讲者、ONLINE LAUNCH与网址完整保留。

## 交付文件

- `round-02/launch-portrait.png`
- `round-02/launch-portrait.snapshot`
- `round-02/launch-wide.png`
- `round-02/launch-wide.snapshot`
- `round-02/design-tokens.json`
- `round-02/content-map.json`
