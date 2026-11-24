# A18 Snapshot 使用与自检报告

- 状态：completed
- 运行 ID：`20261124T113838+0800-aac601`
- 输出根：`outputs/20261124T113838+0800-aac601/A18`（path_base=suite_root）
- 临时根：`tmp/20261124T113838+0800-aac601/A18`（path_base=suite_root）
- 服务基址：https://open-snapshot.muedsa.com

## 文档与工具应用

实际读取服务指南、OpenAPI、Parser 语法、标签与文本属性、示例、字体、布局、绘制、错误处理与数据模板文档；原始响应缓存在 `tmp/20261124T113838+0800-aac601/_suite/shared/`。服务请求使用 UTF-8 纯文本 POST `/snapshot`，依据 HTTP 状态、Content-Type、X-Request-Id 与 Server-Timing 留痕。字体从真实 `/fonts` 响应选择 `Noto Sans CJK SC`。主体、图表、文字和几何均由完整 Snapshot DSL 构造。

## 视觉自检

| 检查项 | 结果与证据 |
|---|---|
| object conservation | 三幕均15单元、每色5个、直径36；节点N01–N03形状与104×104基准一致 |
| geometry | 单元不重叠；连接线绘制在节点和单元下方，且几何净距计算通过 |
| third act distribution | 三节点各接收5单元，每节点至少蓝/橙/灰中的两种颜色 |
| two concepts | radial与flow两种1600×1000构图均真实渲染并查看，最终选择radial |
| visual review | 最终全图与400px宽缩略实际查看，三幕在两种观看尺寸均可辨 |

## 设计选择

三块纵向舞台保持相同尺度；圆形/菱形/六边形节点提供稳定身份，15个单元用径向连线、间距和压缩形变表达状态。

## 问题、修改与验证

两种预览实际查看后选择向心轨道构图。过载仅通过112px与210px环半径、单元最小边距及N01的1.16×/0.84×有限形变表达，未增减或缩小单元。最终全图和400px缩略复查无遮挡、裁剪或身份歧义。

## 交付文件

- `outputs/20261124T113838+0800-aac601/A18/three-act-story.png`
- `outputs/20261124T113838+0800-aac601/A18/three-act-story.snapshot`
- `outputs/20261124T113838+0800-aac601/A18/story-audit.json`
- `outputs/20261124T113838+0800-aac601/A18/rationale.md`
