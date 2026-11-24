# A03 Snapshot 使用与自检报告

- 状态：completed
- 运行 ID：`20261124T113838+0800-aac601`
- 输出根：`outputs/20261124T113838+0800-aac601/A03`（path_base=suite_root）
- 临时根：`tmp/20261124T113838+0800-aac601/A03`（path_base=suite_root）
- 服务基址：https://open-snapshot.muedsa.com

## 文档与工具应用

实际读取服务指南、OpenAPI、Parser 语法、标签与文本属性、示例、字体、布局、绘制、错误处理与数据模板文档；原始响应缓存在 `tmp/20261124T113838+0800-aac601/_suite/shared/`。服务请求使用 UTF-8 纯文本 POST `/snapshot`，依据 HTTP 状态、Content-Type、X-Request-Id 与 Server-Timing 留痕。字体从真实 `/fonts` 响应选择 `Noto Sans CJK SC`。主体、图表、文字和几何均由完整 Snapshot DSL 构造。

## 视觉自检

| 检查项 | 结果与证据 |
|---|---|
| 原稿真实提交 | 通过；未改 DSL 首次请求 400 PARSE_ERROR，原请求/响应与错误诊断保留 |
| 显式错误恢复 | 通过；Transform matrix、Positioned 父级、有界 Stack 全部修复，无删除功能区块 |
| 静默属性 | 通过；移除 Snapshot 未知 width/height；font-size 改 fontSize；根 Container 控制 1280×800 |
| alpha 语义 | 通过；REVIEW 背景 #FFFFFF33 为白色 20%，兄弟文字 #FFFFFF 不透明 |
| 三指标卡 | 通过；USAGE 72%、LATENCY 148 ms、SUCCESS 99.2%，字号 28，宽 394/395/395 |
| 中央背景模糊 | 通过；500×150、圆角 24；彩条穿过左右边界，卡内 BackdropFilter sigma=10，卡外锐利、文字清晰 |
| 标签与安全区 | 通过；标题 44；LIVE 96×36 不盖标题；REVIEW 160×56 逆时针 8°；所有元素在 32 安全边距内 |
| repair-log.json | 通过；7 类问题均对应原稿行、依据、修改与验证；逐版本 DSL/响应/PNG 路径齐全 |

## 设计选择

深色监控卡使用有限根画布与绝对定位保证几何精确。三张等宽指标卡形成第一阅读层；中央卡片用 BackdropFilter 隔离背景模糊，文字置于滤镜之外；LIVE 与 REVIEW 作为状态标签保持在安全区。

## 问题、修改与验证

原样提交得到 Transform matrix 必填错误；继续修复时暴露 Positioned 父级错误，并通过五个最小探针定位。v005 实际查看发现八位色 alpha 顺序导致 REVIEW 青色不透明，以及 ImageFiltered 连文字一起模糊。最终改为 #FFFFFF33、BackdropFilter+ClipRRect，文字与滤镜分层。所有失败稿和探针均保留。

## 交付文件

- `system-pulse.png`
- `system-pulse.snapshot`
- `repair-log.json`
- `snapshot-usage.md`
- `task-metrics.json`
