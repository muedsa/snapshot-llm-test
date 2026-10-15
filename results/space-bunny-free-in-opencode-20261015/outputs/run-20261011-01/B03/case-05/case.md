# case-05 · 降水强度浮层

## 真实场景

天气 App 的分区降水浮层

## 手法

ImageFiltered 高斯模糊作用在**同一份 DSL 里真实存在的底层图元**上，换数据时模糊自动跟着变

## 文档依据

https://snapshot.muedsa.com/reference/parser-tags/ 的 ColorFiltered/ImageFiltered 段：「这两个图片滤镜标签只构造高斯模糊；其他滤镜仍需 Kotlin DSL」；ImageFiltered 要求有限非负的 sigmaX/sigmaY

## 试验与看图证据

首版渲染出来背景圆是**清晰的，完全没模糊**：`ImageFiltered` 里裹的是一个 color="#1B2A4500" 的全透明 Container，而那 26 个圆是它的**兄弟节点不是子节点**，滤镜子树里根本没有可模糊的内容。重做：把 26 个圆作为 ImageFiltered 的子节点放进去，模糊才成立。另外两处纯排版错也是看图才发现的：「接下来 12 小时」排在 y=366 而卡片底边 380，字高 26，悬在卡片外；数值列 txt("68mm", w=64) 装不下 5 个字符，**溢出被静默裁掉**，图上显示成「68m」，和「81mm」不一致。

## 应用价值

天气类界面需要把背景图压暗让文字可读，毛玻璃比纯色块更有层次

## 已确认的边界

**滤镜只作用于自身子树**——想模糊的图元必须是子节点，放在外面等于没写。另外 ImageFiltered **只支持高斯模糊**，其它滤镜 Parser 里没有。

## 文件

| 文件 | 说明 |
|---|---|
| `final.png` | open-snapshot 服务真实响应 |
| `final.snapshot` | 同名完整 DSL |
| `case.md` | 本文件 |

场景、品牌与数据均为**自拟示例**，不是真实记录。
