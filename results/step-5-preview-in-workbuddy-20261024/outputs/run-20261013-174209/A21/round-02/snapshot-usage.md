# A21 第 2 轮 Snapshot DSL 使用记录（run-20261013-174209）

- 画布：竖版 `1080x1350`、横版 `1440x810`；根结构
  `Snapshot type="png"` -> `Container` 定尺 -> `Stack fit="EXPAND"`，
  其余全部 `Positioned` 绝对定位（根只能有一个子节点）。
- 主题：dark；页面底色 `#0B1020`，卡片 `#151B2E`，卡片边线 `#2A3352`。
- 半透明色用 8 位十六进制 `#RRGGBBAA`（alpha 在末两位）。
- 斜光束用 `Transform matrix="(列主序 4x4)"`，且 **Transform 必须是 Positioned
  的直接子节点**，`alignment="CENTER"` 必须写在 Transform 上，否则整条不渲染或偏移。
- 徽标 5 构件：外环 `CIRCLE` + `border`、中盘/内核 `CIRCLE`、三条层纹圆角矩形、
  斜光束旋转薄矩。
- 字体：中文 `Noto Sans CJK SC`；拉丁 `Inter` 系列
  （字重用 `Inter Black` / `Inter Semi Bold` 字体族名切换）。
- 元信息卡：竖版卡高 154px 增至 196px、横版卡高 164px 增至 200px（新增赞助方一行）。

## 渲染尝试记录（含失败重试）

- `A21-r2-portrait`：ok，http=200，request_id `d36f0fbf-027d-4af6-92c0-da02cd82c06e`，耗时 4.39s，DSL 7348 字节
- `A21-r2-wide`：ok，http=200，request_id `c31cfbe7-16ee-4217-a49e-161e91b71e0a`，耗时 1.734s，DSL 7345 字节
- `A21-r2-portrait`：ok，http=200，request_id `d69f9459-692d-4b77-8f1c-9074c2413bdd`，耗时 2.89s，DSL 7348 字节
- `A21-r2-wide`：ok，http=200，request_id `f15c1fad-5476-4d60-af34-664e76119dea`，耗时 2.875s，DSL 7345 字节
- `A21-r2-portrait`：error，http=None，request_id `-`，耗时 74.172s，DSL 7348 字节，错误 `TimeoutError: The read operation timed out`
- `A21-r2-wide`：ok，http=200，request_id `7c0aa655-c569-4d55-915d-d9fe804b6c63`，耗时 7.985s，DSL 7345 字节
- `A21-r2-portrait`：ok，http=200，request_id `34425705-8f30-4b11-9030-f01b8919e92a`，耗时 7.422s，DSL 7348 字节
- `A21-r2-portrait`：error，http=None，request_id `-`，耗时 66.844s，DSL 7348 字节，错误 `TimeoutError: The read operation timed out`
- `A21-r2-wide`：ok，http=200，request_id `fc735bf5-2ccd-410c-8383-2201779fafaf`，耗时 6.562s，DSL 7345 字节

共 9 次渲染请求，7 次成功，2 次失败（失败均为读取超时，重试后成功；未采用的失败响应不落盘为成品）。

## 成品对应的最终成功渲染

- `launch-portrait.png`：1080x1350，request_id `34425705-8f30-4b11-9030-f01b8919e92a`，status ok，耗时 7.422s
- `launch-wide.png`：1440x810，request_id `fc735bf5-2ccd-410c-8383-2201779fafaf`，status ok，耗时 6.562s

共 9 次渲染请求，7 次成功。
