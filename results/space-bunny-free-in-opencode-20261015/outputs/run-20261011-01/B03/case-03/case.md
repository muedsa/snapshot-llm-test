# case-03 · 潮汐预报卡

## 真实场景

海滨城市的每日潮汐

## 手法

gradientType="RADIAL" 把每小时潮位映射成从中心向外的半径，半径越长潮越高，渐变把高潮与低潮自然分开

## 文档依据

https://snapshot.muedsa.com/reference/parser-tags/ 的 Container 渐变表：gradientType 有 LINEAR/RADIAL/SWEEP；RADIAL 用 gradientCenter + gradientRadius

## 试验与看图证据

首版写 gradientFocal="#9BE8F5" 直接 400：`gradientFocal value format error`，它是 alignment 不是颜色。改 gradientFocal="CENTER" + gradientStops="0,0.22,1" 后正常。**更大的错在绘制顺序**：渐变 Container 是不透明的 840×840 方块，首版 append 在最后，把标题、24 个潮位点、页脚全盖住了，整张图只剩一块青色方块——重做为「先铺柔光底 → 再画基准圈与刻度 → 最后画数据点」。右侧表格还重排过四次：数值列曾与条重叠、24 行曾顶到画布下沿、图例曾压在 08.5/09.0 两行上、图例文字曾被裁成半句。

## 应用价值

潮汐是天然的径向量（离某个时刻越近潮位越极端），径向比折线更贴合语义

## 已确认的边界

渐变 Container **不透明**，必须画在所有数据之前；gradientCenter/gradientFocal 想偏心只能把 Container 缩到想要的大小再摆位（第 04 件就是这么处理的）。

## 文件

| 文件 | 说明 |
|---|---|
| `final.png` | open-snapshot 服务真实响应 |
| `final.snapshot` | 同名完整 DSL |
| `case.md` | 本文件 |

场景、品牌与数据均为**自拟示例**，不是真实记录。
