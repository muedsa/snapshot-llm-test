# B06 · Snapshot DSL 使用记录

服务：open-snapshot（run-config.json 指定），端点 `POST /snapshot`，
Content-Type `image/png`。

## 请求统计

- 总请求：28 次
- 成功：14（HTTP 200；平均 7.12s）
- 失败：14（PARSE_ERROR×3；读超时/SSL×7；RENDER_ERROR×4）
  - PARSE_ERROR ×1：`<Path>` 元素不存在于本 DSL（case-02 斜杠/旗面首版）——
    改写为旋转 Container 条 + 矩形后解决；据此建立「本 DSL 无 Path 元素」边界
  - RENDER_ERROR ×若干：`Transform` 内直接放 `Positioned` 触发
    `renderBox.parentData must be StackParentData`——Transform 内只放 Container
  - 读超时/SSL ×6：服务瞬时排队（200–240s 级），由 b06_net.py 重试层覆盖
    （更长客户端超时 + 读超时重试，每次尝试独立记入 requests.jsonl）

## DSL 能力实际使用范围

| 能力 | 使用情况 |
|---|---|
| Container 定尺/圆角/边框 | 10 件全部（卡片/徽标/胶囊/条） |
| Stack + Positioned 绝对定位 | 10 件全部；坐标脚本计算 |
| 渐变 LINEAR | 纸面底与部分卡头（01/05/07/08） |
| 文本 Text（SERIF/SANS/MONO） | 标题 SERIF、正文 SANS、数据 MONO（02/09） |
| 形状 CIRCLE / borderRadius | 圆点/节点/圆环（ring_segment 拼环）/胶囊 |
| **ClipPath 自定义路径裁剪** | **case-07 五大类洗衣符号（洗涤槽/三角/熨斗异形）** |
| Transform matrix（旋转） | × 叠加斜杠、V 形箭头、阴凉处斜线、圆环分段 |
| polyline（粗折线） | ring_segment 圆环、桶形示意、少量连线 |
| Flex Row/Column | 未使用（全部绝对定位） |
| Image dataUri / 摄影图 | 未使用（纯 DSL） |
| Emoji | 未使用（符号自绘，避免字体依赖） |

## 实测边界与规避

1. **本 DSL 无 `<Path>` 元素**：任意形状（三角/异形）用 `ClipPath` 裁剪
   Container 实现（case-02/07/08 实证；B03 已有 ClipPath 先例）
2. **`Transform` 内只能放 `Container`**：放 `Positioned` 报
   `parentData must be StackParentData`（case-02 实证）
3. **T() 位置参数必须显式**：T(s, left, top, w, h, size, color, align,
   style, family)——错位生成非法属性值（延续 B05 实证）
4. **HTML 实体不被解码**：ASCII `<`/`>` 需用全角 ＜＞（case-03 自检拦截 1 次）
5. **T() 为 softWrap=false maxLines=1**：长文必须拆条或加宽盒
   （case-01 两处窄箱长文拆两行）
6. **圆环无原生弧线**：用 b02 `ring_segment`（旋转小段拼环，端部重叠消缝）
   （case-10 实证）
7. **文本右对齐会被后绘卡片遮挡**：时间轨右对齐文本要预留到卡片的间距
   （case-02 实证：rail_x +130）

## 复用资产

- 共享助手：`tmp/run-20261013-174209/B06/b06_common.py`（调色板/徽标/标签/页头/脚注/
  比例条/圆环/箭头/图元 nodes 包装）
- 逐用例生成器：`tmp/run-20261013-174209/B06/cases/case01_gen.py` … `case10_gen.py`
- 每份最终 `.snapshot` 完整自包含（无外部文件依赖），可独立重新提交渲染
- CRLF 说明：final.snapshot 由 `write_text` 写出（Windows CRLF 换行），
  与请求体仅差换行符
