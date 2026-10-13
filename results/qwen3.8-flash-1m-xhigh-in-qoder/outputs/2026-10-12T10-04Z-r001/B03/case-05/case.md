# case-05 · 《潮汐》凸版诗句页（压印与文字微距控制）

- 场景：小型凸版工坊的诗集样张，客户据此决定压痕深度、行距与字距
- 画布：820 × 1280，PNG 170 KB，服务请求 `B03-case05-v2`（47 段文字 / 5 图形）
- 主能力：`textShadow` 双向压印、`letterSpacing`、`height` 行距倍率、
  `WidgetSpan` 行内规则线、`Raw` 保留缩进、`fontFeatures="tnum"` 行号列

## 手法

压印不是发光：一条 `-3 -3 0 #FFFFFF` 的高光在左上、一条 `2 3 0 #3A342B55` 的暗部在右下，
两条都是零模糊的硬边，全页只用这一个方向（放大图可见字缘的白色受压面）。
行距对照用同四行诗并列两栏，只有 `height` 1.0 与 1.75 不同；
"其三·终" 前的红线是 `WidgetSpan(alignment=BASELINE, baseline=IDEOGRAPHIC)`，
它排在基线上而不是块与块之间；页脚"排版记录"用 `Raw` 段保留三空格缩进。

## 文档依据与实测

- `textShadow="x y [blur] [color]"` 逗号分隔多条、`fontFeatures` 空白分隔、
  `height`/`letterSpacing`/`wordSpacing` 为文本样式属性（`reference_parser-tags.txt` 文本段）
- 实测：`B03-p2-textab` 红影 1 426 px、双影蓝 729 px；`letterSpacing=6` 使 8 字宽
  160→202px；`wordSpacing=14` 使 167→195px；`height` 只在**换行后**改变行距
  （`B03-p4-lineheight` 行距 22→53px），故本件对照栏用固定宽度自然换行
- `WidgetSpan` 必须恰有一个普通子 Widget 且只能是 `Text` 的子节点
  （`reference_parser-tags.txt` WidgetSpan 段）；`B03-p4-decorun` 实测基线盒 20×20 落在
  (132,113)–(151,132)
- `Raw` 保留首尾空格但**不继承** fontSize（`B03-p8-rawstyle`），因此该段自带字号；
  本件回读渲染像素：三空格间隙 29/30px，普通单空格 11–13px → 缩进真实存在
- `tnum` 使 10 位数字宽 176→186px（`B03-p2-textab`），行号列因此对齐；
  `smcp` 实测 0 像素变化（`B03-p4-smallcaps`），故未使用

## 看图与自检

- `v1`：页脚超出纸框、压印高光不可见 → 画布 1160→1280，高光改纯白零模糊、暗部偏移收紧
- 首版 hairline 边框 `border="1 SOLID" radius=0` 被 bkit 守卫拦下
  （服务对 border>borderRadius 返回 500，`B03-case09` 实测），改为不给圆角
- audit：`overlap_n=0 outside_n=0 below_min_font_n=0`；两栏行距差 12.6px 由断言保证
- 放大图 `zoom-c05-title.png` 检查压痕方向一致；`zoom-c05-raw.png` 检查缩进空格

## 数据自洽

八行诗每行 6–8 字，行距 = 34×1.0×1.46 与 21×{1.0,1.75}×1.46 均由同一公式给出，
`case05-data.json` 记录两种倍率的实际像素间距；colophon 8 条与页面文字一一对应。

## 边界与取舍

凸版的"纸张纹理/凹陷"不可能由 DSL 真实呈现，这里只用双向硬边阴影表达压痕方向，
不假称有实体凹凸，也不引入扫描素材。
