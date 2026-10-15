# case-04 · 慢转 33⅓ 唱片封套

## 真实场景

独立厂牌的黑胶唱片封套

## 手法

gradientType="SWEEP" 画扇形色盘 + 同心圆环，模拟黑胶旋转的视觉隐喻

## 文档依据

https://snapshot.muedsa.com/reference/parser-tags/ 的 Container 渐变表：SWEEP 用 gradientStartAngle/gradientEndAngle，角度是弧度，且「起点必须小于终点」

## 试验与看图证据

首版压了一层 #0E0E1244 的暗色，把扇形渐变压成灰扑扑的粉彩，颜色全糊了 → 减到 1A 后鲜艳度回来；另外中心圆半径 150 装不下 "ROTATION"，文字被黑圆边缘切掉 → 放大到 176 并把字缩到 22px

## 应用价值

黑胶的视觉本质就是「一个中心 + 一圈圈旋转的色带」，SWEEP 是最直接的对应

## 已确认的边界

SWEEP 的中心同样只能给对齐常量，所以渐变中心必须与唱片中心重合；`gradientEndAngle` 要大于 `gradientStartAngle`，全周用 6.2832。

## 文件

| 文件 | 说明 |
|---|---|
| `final.png` | open-snapshot 服务真实响应 |
| `final.snapshot` | 同名完整 DSL |
| `case.md` | 本文件 |

场景、品牌与数据均为**自拟示例**，不是真实记录。
