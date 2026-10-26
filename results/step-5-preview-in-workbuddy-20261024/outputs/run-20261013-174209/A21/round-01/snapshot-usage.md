# A21 第 1 轮 Snapshot DSL 使用记录（run-20261013-174209）

- 画布：竖版 `1080x1350`、横版 `1440x810`；根结构
  `Snapshot type="png"` -> `Container` 定尺 -> `Stack fit="EXPAND"`，
  其余全部 `Positioned` 绝对定位（根只能有一个子节点）。
- 主题：dark；页面底色 `#0B1020`，卡片 `#151B2E`。
- 半透明色用 8 位十六进制 `#RRGGBBAA`（alpha 在末两位）。
- 斜光束用 `Transform matrix="(列主序 4x4)"`，且 **Transform 必须是 Positioned
  的直接子节点**，否则整条不渲染。
- 徽标 5 构件：外环 `CIRCLE` + `border`、中盘/内核 `CIRCLE`、三条层纹圆角矩形、
  斜光束旋转薄矩。
- 字体：中文 `Noto Sans CJK SC`；拉丁 `Inter` 系列
  （字重用 `Inter Black` / `Inter Semi Bold` 字体族名切换）。

## 渲染记录

- `launch-portrait.png`：1080x1350，request_id `fc6441f7-739b-4e2d-a1c3-95639285d402`，status ok，耗时 2.688s，DSL 5891 字节
- `launch-wide.png`：1440x810，request_id `c212969f-cbfb-47af-81de-07e85a69d69a`，status ok，耗时 2.063s，DSL 5891 字节

共 2 次渲染请求，2 次成功。
