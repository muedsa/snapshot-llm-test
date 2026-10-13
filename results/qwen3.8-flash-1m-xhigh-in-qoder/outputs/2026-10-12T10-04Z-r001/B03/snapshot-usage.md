# B03 · Snapshot 用法记录（创意边界探索）

本题的目标不是"多用标签"，而是把此前 A/B 各题没有真正用过的能力推到可用为止。
下面记录实际读过的文档、真实请求得到的结论、踩到的坑，以及它们如何改变了作品。

## 一、文档依据（真实读取）

全部来自 `_suite/docs-cache/` 的抓取副本（本任务复用共享缓存，未新增 HTTP 请求，
`task-metrics.json → counts.document_requests = 0`），逐页读过并保留原文：

| 文档 | 用途 |
|---|---|
| `reference_parser-tags.txt` | 标签白名单、渐变/装饰/文本属性格式、WidgetSpan 约束 |
| `reference_enums.txt` | ClipBehavior、BoxShape、BlendMode、TileMode 取值 |
| `widget_painting_backdrop-filter.txt` | BackdropFilter 签名与"必须配合裁剪"的官方建议 |
| `widget_painting_color-filtered.txt` | 子树绘制边界、SRC_ATOP/MULTIPLY 语义 |
| `widget_painting_clip-path.txt` | path 语法与裁剪边界 |
| `widget_layout_transform.txt` | matrix/origin/alignment 三者关系 |
| `widget_text_text.txt` | 文本样式属性全集（height、letterSpacing、fontFeatures…） |
| `widget_text_rich-text.txt` / `widget_text_widget-span.txt` | 行内 Span 树与占位对齐 |
| `guides_painting.txt` | 渐变与混合的整体模型 |

## 二、六轮能力探测（74 次请求）与结论

探测脚本：`probe.py` `probe2.py` `probe3.py` `probe4.py` `probe5.py` `probe6.py`
`probe7.py` `probe8.py` `probe8b`；像素证据：`probe-evidence.json`
`probe-evidence2.json` `probe-evidence4.json`；看图：`montage-A…H`。

**已确认可用**

- `BackdropFilter sigmaX/sigmaY(+tileMode/blendMode)`：12px 棋盘上 sigma 6 把 9 次跳变
  压到 0 次（`B03-probe2-blur2`）
- `gradientType="SWEEP"`：四方向采样 4 个不同颜色，0 弧度在 3 点钟方向、顺时针增大
- `RADIAL + gradientTileMode`：CLAMP 1 环、REPEAT 5 环、MIRROR 3 环、DECAL 环外不画
- `ColorFiltered color+blendMode`：SRC_ATOP 把黑字整棵子树染成 #FF5500
- `backgroundBlendMode="MULTIPLY"`：Container 背景与身后像素相乘（网印叠印）
- `boxShadow`：ELEVATION_0…24 单调变暗；**自定义 `"x y blur color"` 字符串同样有效**
- `textShadow`：`"4 5 2 #E53935,-4 0 0 #0D47A1"` 双影分别 1 426 / 729 像素
- `letterSpacing=6` 8 字宽 160→202；`wordSpacing=14` 167→195；`height=2.4` 使换行行距
  22→53 px（必须真的发生换行）
- `WidgetSpan`：20×20 色块按 BASELINE/MIDDLE 正确入行
- `decorationLineStyle`：SOLID/DOTTED/DASHED/DOUBLE/WAVY 可用（DOTTED 64 段 vs
  DASHED 28 段），`DOUBLE_SOLID` 非法
- `ClipPath` 反向子路径成孔、`A/a` 弧段、单路径多子形状求并
- `Emoji` 作为 `Text` 行内 Span，`dataUri` 接受完整 `data:image/png;base64,…`

**已确认不成立 / 有边界**

| 结论 | 证据 |
|---|---|
| 文档级 **4096 元素上限** | `B03-probe-nodes4000` → `Document contains more than 4096 elements`；2000 元素仅 607 ms |
| **未裁剪的 BackdropFilter 会把先前半透明内容重新合成为不透明** | `B03-p6-bottom-only`（复现）/ `B03-p6-clipped-backdrop`（修复）/ `B03-p7-*`（小画布未复现）→ 一律经 `bkit.Sheet.glass()` 加裁剪 |
| LINEAR 渐变的 REPEAT/MIRROR 在轴向铺满自身画框时**不可见** | `B03-p2-tile2` 四种模式转次数均为 0；只有 RADIAL（半径即周期）能平铺 |
| `gradientRotation` 在同时给出 begin/end 时无效果 | `B03-p2-gradrot` 采样完全相同 |
| SWEEP 不接受 `gradientRadius/Center` | `B03-case02-v1` → `Attr [gradientRadius] is not supported by this gradient type` |
| `fontFeatures="smcp"` 零像素变化（字体不支持小型大写） | `B03-p4-smallcaps` changed_px=0 |
| `Transform origin` 只接受 `"(x,y)"` | `B03-origin1` 200；`B03-origin0/2` 400 格式错误 |
| `border` 宽 > `borderRadius` → 500 INTERNAL_ERROR | 早期实测，已在 `bkit.rect()` 加抛错守卫 |
| Stack 的子节点全为 Positioned → 400 `Layout size is infinite` | `B03-misc` |
| `Positioned` 只能是 Stack 的直接子节点 | 放进 ColorFiltered → 400 `renderBox.parentData must be StackParentData` |
| `Raw` Span 不继承父级 fontSize | `B03-p8-rawstyle`（行高不同） |
| `Emoji` 不能作为独立 Widget | `B03-p8-emoji-fix` → `cant not buildWidget` |
| Java `trim()` 会吃掉 U+3000 全角空格 | `B03-case01-v2` 标题粘连 |
| 渐变色标之间 Skia 按线性光插值 | 日轮 8 点回读，色标处精确、中点偏亮 55–69 |

## 三、这些结论怎样改变了作品

1. **case-03 从"两层网点"改成"一层网点 + 一层透明叠印"**：4096 上限使满版双分色不可能；
   同时 LINEAR 无法平铺，所以叠印用 `backgroundBlendMode` 的透明洗色实现。
2. **case-07 的布面不再宣称用 gradientTileMode 生成**：实测 LINEAR 平铺不可见，
   于是布面按浮长线几何分色，平铺只用在 RADIAL 纱纹上，并在卡片脚注写明原因。
3. **case-02 的色环反算**：因为 Skia 线性光插值，只在色标位置给硬承诺，
   中点色改为"回读比对"而不是"公式预测"。
4. **case-06 的漏失孔**：第一版内环与外框同向 → 像素回读仍是层色；改反向环后回读为纸色。
5. **case-10 的逐字仿射**：整句共用仿射残差 38–61 mm 不可接受；改为每字 6 参数拟合，
   残差 4.6 mm，并把公差 ±25 mm 印在图上。
6. **case-08 的等时圈口径**：按车速时圆环大于图幅，改为步行 5 km/h（AED 响应链的真实约束）。
7. **共享工具**：`bkit` 新增 `glass/rich/shear/filter_rect/elements` 与 border、元素数守卫，
   使这些边界在后续题目里不可能再被无意踩到。

## 四、跨题经验

- 绝对定位画布上"先算后画"比"画了再看"省一半迭代：本题 10 件共 49 次成功视觉迭代，
  其中约一半由生成器内 assert 在渲染前就拦下。
- 像素回读是 DSL 作品最有效的自检：case-06/07/09/10 都用它替代了"看起来对"。
- 服务的原始响应字节必须原样进交付目录：本题 10 件全部经 sha256 与 `requests.jsonl`
  的 `response_file` 比对一致（`portfolio.json → final_collection_review.byte_identity`）。

## 五、剩余事项

- `BackdropFilter` 在 460×180 小画布上未复现"压平半透明"的现象，边界条件（画布尺寸/
  滤镜区域推断）未完全定位；作品层面已用"一律加裁剪"规避。
- `foregroundGradient*` 只在 case-01 的面板上用过一次，其 begin/end 方向语义未单独探测。
- 本题未使用任何外部素材或后处理：所有最终 PNG 都是服务响应，缩放检查只作用于副本。
