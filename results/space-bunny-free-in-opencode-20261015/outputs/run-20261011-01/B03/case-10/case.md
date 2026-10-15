# case-10 · 年度十佳展陈主视觉

## 真实场景

独立书店的年度书单展陈

## 手法

同一句话用四层 STROKE（不同粗细、透明度）叠出层次，并把最底层整体旋转 6°，做出丝印的套版错位

## 文档依据

https://snapshot.muedsa.com/reference/parser-tags/ 的 Text 属性表：foregroundMode / foregroundStrokeWidth / foregroundColor；Transform 的 matrix 与 alignment

## 试验与看图证据

实图确认四层描边的错位效果成立，层次清楚；同时发现 3px 描边对中文细笔画会粘连（第 02 件的问题在这里被放大），所以底层描边给到 26px 后才干净

## 应用价值

书店展陈需要「印刷感」，纯 DSL 用描边错位是最省事且最像丝印的做法

## 已确认的边界

描边宽度是绝对像素，不会随画布缩放；同一句话叠四层意味着四份 Text，字号或位置改一处要同步改四处。

## 文件

| 文件 | 说明 |
|---|---|
| `final.png` | open-snapshot 服务真实响应 |
| `final.snapshot` | 同名完整 DSL |
| `case.md` | 本文件 |

场景、品牌与数据均为**自拟示例**，不是真实记录。
