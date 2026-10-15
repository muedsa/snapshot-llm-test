# case-06 · 丝网印刷套色校样

## 真实场景

独立书店海报的印刷校样

## 手法

ColorFiltered + Skia blendMode="MULTIPLY" 模拟油墨叠印，交叠处自然变深

## 文档依据

https://snapshot.muedsa.com/reference/parser-tags/：「ColorFiltered 要求 color 和 Skia blendMode」

## 试验与看图证据

两次踩坑：① 滤镜套在整张画布的 Stack 上，滤镜把画布底一起染了，第二版变成一整块红底；② 把「已是画布绝对坐标」的图元塞进带偏移的 Positioned 里，等于偏移两次，第二版画到了版外看不见。改成图元一律用版内相对坐标、两个版本各自装进自己的 Positioned 后正常。最后把文案改成如实描述「整版上墨」，因为满版红本来就是 MULTIPLY 的正确结果。

## 应用价值

印刷打样要在屏幕上预演叠色，纯 CSS 式混合做不到油墨的压深关系

## 已确认的边界

blendMode 在**滤镜自身边界内**与背板混合，所以整块版区都会上色——这恰好等于丝印的整版上墨；只想让图元变暗则必须让滤镜边界等于图元包围盒。

## 文件

| 文件 | 说明 |
|---|---|
| `final.png` | open-snapshot 服务真实响应 |
| `final.snapshot` | 同名完整 DSL |
| `case.md` | 本文件 |

场景、品牌与数据均为**自拟示例**，不是真实记录。
