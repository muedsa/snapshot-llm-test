# case-08 · 本周骑行成就章

## 真实场景

共享单车的周成就卡

## 手法

ClipPath 用带 Q/C 命令的**曲线轮廓** + EVEN_ODD 挖出四瓣花形章面

## 文档依据

https://snapshot.muedsa.com/reference/parser-tags/：「path 使用 SVG 的 d 属性语法，支持 M/L/H/V/Z、Q/T、C/S、A 命令」

## 试验与看图证据

实图确认曲线轮廓能渲染成非圆角形状，四个花瓣是镂空而非填充。首版柱高按「占 420px」算，最高的周六柱到 y≈310，穿过了右上角章面；改成每公里 8px（最高 34.2 → 274px）并把章面上移到 100–390 后互不相交

## 应用价值

成就章需要有机形状，圆角矩形做不到

## 已确认的边界

ClipPath 的坐标在本地坐标系，**没有布局作用**——必须自己给 SizedBox/父盒子定尺寸（这里靠外层 Positioned 的 width/height）。

## 文件

| 文件 | 说明 |
|---|---|
| `final.png` | open-snapshot 服务真实响应 |
| `final.snapshot` | 同名完整 DSL |
| `case.md` | 本文件 |

场景、品牌与数据均为**自拟示例**，不是真实记录。
