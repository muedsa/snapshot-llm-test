# A17 Snapshot 使用与自检报告

- 状态：completed
- 运行 ID：`20261124T113838+0800-aac601`
- 输出根：`outputs/20261124T113838+0800-aac601/A17`（path_base=suite_root）
- 临时根：`tmp/20261124T113838+0800-aac601/A17`（path_base=suite_root）
- 服务基址：https://open-snapshot.muedsa.com

## 文档与工具应用

实际读取服务指南、OpenAPI、Parser 语法、标签与文本属性、示例、字体、布局、绘制、错误处理与数据模板文档；原始响应缓存在 `tmp/20261124T113838+0800-aac601/_suite/shared/`。服务请求使用 UTF-8 纯文本 POST `/snapshot`，依据 HTTP 状态、Content-Type、X-Request-Id 与 Server-Timing 留痕。字体从真实 `/fonts` 响应选择 `Noto Sans CJK SC`。主体、图表、文字和几何均由完整 Snapshot DSL 构造。

## 视觉自检

| 检查项 | 结果与证据 |
|---|---|
| eight final images | 四页1200×1600与四例400×240均由真实服务返回；八张原图实际查看 |
| core subtree equality | 核心源码字节一致；教学页核心矩形与独立示例视觉等价，仅2–4个抗锯齿边缘像素差异并已记录 |
| printed source | 每页实际印出8–18行；1-based行段与逐字文本记录于examples.json |
| typography and margins | 正文与示例文字≥24、代码=20；页面外边距≥48 |
| DSL-only visuals | 八个最终DSL均无Image；教学插图由核心子树直接绘制 |
| reproducibility | 每对最终PNG/DSL匹配真实请求与响应，保留哈希、requestId与原始字节 |

## 设计选择

统一章节条、1:1示例视窗、深色代码卡与三点总结；用固定字体、有限容器和明确坐标保证可复现。

## 问题、修改与验证

v001基线八图查看发现代码卡裁剪、印刷行段不完整、长行换行、第1页标题左裁与第4页模糊文字边界问题；v002修复代码卡和行段，v003修复长行/CDATA核对与滤镜边界，v004标题收紧方案未通过，v005改用外层padding Container修复标题。八张最终原图已直接查看，核心源码字节一致，渲染核心仅记录2–4个抗锯齿边缘像素差异。

## 交付文件

- `outputs/20261124T113838+0800-aac601/A17/example-01.png`
- `outputs/20261124T113838+0800-aac601/A17/example-01.snapshot`
- `outputs/20261124T113838+0800-aac601/A17/example-02.png`
- `outputs/20261124T113838+0800-aac601/A17/example-02.snapshot`
- `outputs/20261124T113838+0800-aac601/A17/example-03.png`
- `outputs/20261124T113838+0800-aac601/A17/example-03.snapshot`
- `outputs/20261124T113838+0800-aac601/A17/example-04.png`
- `outputs/20261124T113838+0800-aac601/A17/example-04.snapshot`
- `outputs/20261124T113838+0800-aac601/A17/handbook-01.png`
- `outputs/20261124T113838+0800-aac601/A17/handbook-01.snapshot`
- `outputs/20261124T113838+0800-aac601/A17/handbook-02.png`
- `outputs/20261124T113838+0800-aac601/A17/handbook-02.snapshot`
- `outputs/20261124T113838+0800-aac601/A17/handbook-03.png`
- `outputs/20261124T113838+0800-aac601/A17/handbook-03.snapshot`
- `outputs/20261124T113838+0800-aac601/A17/handbook-04.png`
- `outputs/20261124T113838+0800-aac601/A17/handbook-04.snapshot`
- `outputs/20261124T113838+0800-aac601/A17/sources.md`
- `outputs/20261124T113838+0800-aac601/A17/examples.json`
