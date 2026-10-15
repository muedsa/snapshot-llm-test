# case-01 · 七月演出海报

## 真实场景

社区爵士酒吧的月度演出海报

## 手法

ClipPath 双轮廓 + fillRule="EVEN_ODD" 挖出方环，镂空处直接放标题

## 文档依据

https://snapshot.muedsa.com/reference/parser-tags/ 的 ClipPath 属性表：fillRule 有 NON_ZERO 与 EVEN_ODD，「EVEN_ODD 使用奇偶规则，可实现镂空」

## 试验与看图证据

首版试了 NON_ZERO：两条同向轮廓在实图上**挖不出孔**，中心仍然是实心的；改 EVEN_ODD 后中心透出海报底色。首版还在方环上盖了三个圆，把镂空盖住了，重做为干净的方环后才一眼看出是透空的。

## 应用价值

演出海报需要「框里有内容」，方环让标题天然成为负形，不用手工描边

## 已确认的边界

EVEN_ODD 依赖轮廓**同向**；反向轮廓在 NON_ZERO 下才是镂空。

## 文件

| 文件 | 说明 |
|---|---|
| `final.png` | open-snapshot 服务真实响应 |
| `final.snapshot` | 同名完整 DSL |
| `case.md` | 本文件 |

场景、品牌与数据均为**自拟示例**，不是真实记录。
