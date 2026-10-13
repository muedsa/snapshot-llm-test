# case-03 · 黄昏港两色网印试印张（ColorFiltered + backgroundBlendMode）

- 场景：丝网印刷店给诗集封面选墨序/网版的试印张；客户据此决定闪干与套准
- 画布：1000 × 1400，PNG 607 KB，服务请求 `B03-case03-v7`（3 149 元素 / 245 KB DSL）
- 主能力：`ColorFiltered blendMode="SRC_ATOP"` 给整棵网点子树上色 ＋
  `backgroundBlendMode="MULTIPLY"` 让朱墨真正叠印 ＋ 亮度函数驱动的程序化网点

## 手法

A 面是 45° 点阵上的黑点，半径 r = 0.60·间距·(1−L)^0.78，L 来自解析的黄昏港亮度函数
（地平线亮、日轮最亮、水面波光、船体近黑）；整棵子树用 ColorFiltered 一次染成藏青，
所以"一版墨色"是真的一个滤镜，而不是逐个填色。B 面只有两个元素：日轮与水面波光的
径向渐变方块，各自 `backgroundBlendMode="MULTIPLY"`，压过 A 面时得到第三个色值——
这正是两色网印的物理：四阶色梯以外不可能有别的值。船体用 ClipPath 实色剪影重新压回画面，
避免网点把主体吃掉。

## 文档依据与实测

- ColorFiltered 只作用于子树绘制边界，`SRC_ATOP` 会替换不透明像素颜色
  （`widget_painting_color-filtered.txt`；`B03-p2-filter2` 采样确认文字被染成 #FF5500）
- backgroundBlendMode 与 Container 背景合成（`reference_parser-tags.txt` 装饰属性表）
- 叠印色可复算：#1B3A5C × #D9552F = #171311；渲染图实测最深像素 (23,22,24)=#171618
  位于 (618,830)，与预测一致
- **4096 元素上限**：`B03-probe-nodes4000` 返回 `Document contains more than 4096 elements`，
  2000 元素仅 607ms 渲染 → 网点间距从 14px 被迫定为 20px（1 506 点 = 3 149 元素）
  已在 `bkit.Sheet.finish()` 前加 elements 计数守卫
- `Positioned` 只能是 `Stack` 的直接子节点：放进 ColorFiltered 内会 400
  `renderBox.parentData must be StackParentData`（`B03-case03-v1`）
- Stack 全 Positioned 子节点 → `Layout size is infinite`（`B03-case03-v1d`，同 `B03-misc`）

## 看图与自检

- `v1`（双网点分色版，case03_screen.py 保留为草稿）：两层各 1 300 点，画面读作"点阵"
  而不是港口，且元素数超限 → 改为"一层网点 + 一层透明叠印"
- `v2`：朱色溢出印区、天空过黑（A 覆盖 77.1%）→ 渐变方块按印区边界算尺寸，
  色调曲线指数 0.46→0.78，覆盖率 47.4%
- `v3`：水面叠印带用 LINEAR 渐变，上下出现硬边 → 改径向渐变（其色标只沿 x 衰减）
- `v4`：色梯写"叠印 27.2%"但 B 面是 90% 透明墨，实测纯 B 面积 0% → 色梯改为
  满墨/满压值并注明，覆盖率改称"墨量（面积加权）"
- `v7`：桅杆 7px 被网点吞掉 → 加粗到 11px
- audit：`overlap_n=0 outside_n=0 below_min_font_n=0`
- 实测色调面积（对最终响应逐 2px 采样）：纸 23.9% · A 35.2% · B 染与网点边缘 40.7% ·
  满压叠印 0.1%，与几何预测同一量级；数据留在 `case03-data.json`

## 边界与取舍

两版满版网点在这个画布尺寸下不可能（元素上限），所以 B 面被设计成"透明叠印洗色"而不是
第二套网点——这是服务限制改变了实现，而不是用后处理冒充。叠印只占 0.1% 面积是真实结果，
写在图版与本报告里，不靠调高墨量伪造更深的暗部。
