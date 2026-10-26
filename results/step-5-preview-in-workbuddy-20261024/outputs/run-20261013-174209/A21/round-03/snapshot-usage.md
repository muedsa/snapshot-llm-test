# A21 第 3 轮 Snapshot DSL 使用记录（run-20261013-174209）

- 画布：竖版 `1080x1350`、横版 `1440x810`；根结构
  `Snapshot type="png"` -> `Container` 定尺 -> `Stack fit="EXPAND"`，
  其余全部 `Positioned` 绝对定位（根只能有一个子节点）。
- 主题：light；页面底色 `#F6F7FB`，卡片 `#FFFFFF`，卡片边线 `#D7DCEA`。
- 半透明色用 8 位十六进制 `#RRGGBBAA`（alpha 在末两位）。
- 斜光束用 `Transform matrix="(列主序 4x4)"`，且 **Transform 必须是 Positioned
  的直接子节点**，`alignment="CENTER"` 必须写在 Transform 上，否则整条不渲染或偏移。
- 徽标 5 构件：外环 `CIRCLE` + `border`、中盘/内核 `CIRCLE`、三条层纹圆角矩形、
  斜光束旋转薄矩。
- 字体：中文 `Noto Sans CJK SC`；拉丁 `Inter` 系列
  （字重用 `Inter Black` / `Inter Semi Bold` 字体族名切换）。
- 元信息卡：竖版卡高 196px、横版卡高 200px（与第二轮一致；横版卡高由第二轮写死的 164px 改为按行数计算 20 + 各行 size*1.5 + 行距 14 + 20 = 200px，修复赞助方一行文字墨迹探出卡片底边约 16px 的缺陷）。

## 渲染尝试记录（含失败重试）

- `A21-r3-portrait`：ok，http=200，request_id `d5df30bb-10f5-48c3-8cc4-3bb8a5ffc5ba`，耗时 7.0s，DSL 7657 字节
- `A21-r3-portrait-notext`：ok，http=200，request_id `3b01ffad-2188-446b-8798-44d4b891114b`，耗时 2.188s，DSL 3913 字节
- `A21-r3-wide`：ok，http=200，request_id `b616831d-4e74-4fbd-bd0f-1fe16cae9425`，耗时 3.515s，DSL 7655 字节
- `A21-r3-wide-notext`：ok，http=200，request_id `9a7de614-13b8-4cc9-ba8b-a4642dae9313`，耗时 1.937s，DSL 3910 字节
- `A21-r3-portrait`：ok，http=200，request_id `45cc53c7-6115-4c4f-9639-da36df526b03`，耗时 5.656s，DSL 7657 字节
- `A21-r3-portrait-notext`：error，http=None，request_id `-`，耗时 67.109s，DSL 3913 字节，错误 `TimeoutError: The read operation timed out`
- `A21-r3-wide`：ok，http=200，request_id `11f45f75-c718-450f-8b12-28e8c7cc09dc`，耗时 2.907s，DSL 7655 字节
- `A21-r3-wide-notext`：ok，http=200，request_id `8cc6163a-9555-4f0c-b2cc-ab775a3e7eaf`，耗时 2.062s，DSL 3910 字节
- `A21-r3-portrait-notext`：ok，http=200，request_id `b58eb709-8fb2-4b6c-95e4-c18e3170cc35`，耗时 3.406s，DSL 3913 字节
- `A21-r3-wide-notext`：ok，http=200，request_id `4e239ddb-f458-4eb1-8dcb-2fb6230005b9`，耗时 2.735s，DSL 3910 字节

共 10 次渲染请求，9 次成功，1 次失败（失败均为读取超时，重试后成功；未采用的失败响应不落盘为成品）。

## 成品对应的最终成功渲染

- `launch-portrait.png`：1080x1350，request_id `45cc53c7-6115-4c4f-9639-da36df526b03`，status ok，耗时 5.656s
- `launch-wide.png`：1440x810，request_id `11f45f75-c718-450f-8b12-28e8c7cc09dc`，status ok，耗时 2.907s
- `r3-portrait-notext.png`（去文字辅助渲染，对比度审计背景来源）：request_id `b58eb709-8fb2-4b6c-95e4-c18e3170cc35`
- `r3-wide-notext.png`（去文字辅助渲染，对比度审计背景来源）：request_id `4e239ddb-f458-4eb1-8dcb-2fb6230005b9`

共 10 次渲染请求，9 次成功。
