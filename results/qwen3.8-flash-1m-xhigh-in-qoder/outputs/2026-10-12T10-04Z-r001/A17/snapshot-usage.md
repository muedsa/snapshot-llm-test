# A17 使用报告 · 四页可实践的 DSL 入门手册

状态：**completed**（8 件指定交付全部为服务真实响应 + 同名 `.snapshot`，逐图实际看过并通过自检）。

## 1. 交付清单

| 文件 | 尺寸 | 说明 |
|---|---|---|
| `handbook-01.png` / `.snapshot` | 1200×1600 | 第 1 页：真实调用契约 |
| `handbook-02.png` / `.snapshot` | 1200×1600 | 第 2 页：尺寸来自布局 |
| `handbook-03.png` / `.snapshot` | 1200×1600 | 第 3 页：尾部 alpha、CDATA 与富文本 |
| `handbook-04.png` / `.snapshot` | 1200×1600 | 第 4 页：背景滤镜 ≠ 子树滤镜 |
| `example-01…04.png` / `.snapshot` | 400×240 | 每页一例的可运行完整 DSL 与独立渲染 |
| `sources.md` | — | 15 条技术结论 → 实际阅读页面 + 例子 |
| `examples.json` | — | 4 示例的核心子树定位、印刷片段逐字原文、真实响应与自检结果 |
| `task-metrics.json` | — | 请求/迭代/看图/耗时统计 |

过程目录：`../../../tmp/2026-10-12T10-04Z-r001/A17/`（`gen.py`、`examples.py`、`measure.py`、
`fit_audit.py`、`verify.py`、`build_examples_json.py`、`probe_mono.py`、`probe_backdrop.py`、
v001–v007 全部 DSL/PNG、两份探测图、放大检查图、三份 JSONL 日志）。

## 2. 一源三用的做法

`examples.py` 里每页只写一次 `core(i)`：

- **独立示例**：`example_doc(i)` = `Snapshot(Container(core(i), 400×240))` → 真实渲染成 `example-NN.png`；
- **页内插图**：`gen.py` 把**同一个 Node 对象**塞进 `Positioned(core(i), left=64, top=291)`，1:1 画在页面上，不用 `Image` 嵌入任何预渲染图；
- **印刷片段**：`code_text(i)` 直接返回 `example-NN.snapshot` 的行，页面按 1-based 行号引用并原样打印（含缩进）。

因此三者不可能各写一套。`verify.py` 再用两条独立证据核对：把独立示例按 alpha 合成到白底后，
在页面图里做模板搜索并逐像素比对（四页定位都在 `left=64, top=291`，三页 ≥0.9999 一致）；
把页面 DSL 用 ElementTree 解析回来，按顺序在 `example-NN.snapshot` 里匹配每一行印刷文本。

## 3. 真实文档应用

见 `sources.md`。要点：Snapshot 根只接受 `background/debug/type`（parser-tags 180–189 行）、
`Expanded/Flexible/Spacer` 必须是 Flex 的直接子节点（327 行）、Flex 主轴无界时无法分配剩余空间
（guides/layout 90 行）、八位颜色按 `#RRGGBBAA`（87 行）、`Raw` 不 trim 且只能出现在最外层 `Text`
的行内树里（572 行）、`BackdropFilter` 读取子树之外的背景（backdrop-filter 页）。
第 2 页的 flex 结论还用像素反证：三条色块实测 82/164/82 = 1:2:1。

## 4. 用到的标签能力

`Snapshot`、`Container`、`Stack`、`Positioned`、`Row`、`Expanded`、`Spacer`、`Text`、`Raw`（CDATA 与
非 CDATA 两种）、嵌套 `Text` 行内 Span、`ClipRRect`、`BackdropFilter`、`ImageFiltered`、
`border`/`borderRadius`/`color`（含 8 位 alpha）、`textAlign`、`softWrap`、`mainAxisSize`、
`crossAxisAlignment`、`tileMode`、`fontFamily`（Noto Sans CJK SC / Noto Sans Mono CJK SC）。

## 5. 遇到的问题与修复

| 现象 | 原因 | 修复 | 验证 |
|---|---|---|---|
| v001 示例文字越过 400×240、蓝条压住卡片文字 | 字宽靠猜（把 mono 当 0.6em） | 建 `measure.py`（实测 mono 0.486em、CJK 1.00em、行距 1.46em）+ `fit_audit.py` 渲染前遍历同一 Node 树查越界/压字/跨卡 | fit_audit 四页 0 problems；v002 看图 |
| example-02 的 flex 三条色块完全看不见 | `Row` 在只有宽度约束的 `Positioned` 里，交叉轴无界 + `STRETCH` + 无高度 `Container` → 高度塌成 0 | 子 `Container` 给 `height="40"`，`crossAxisAlignment="START"` | v003 量得 82/164/82 |
| 手册第 3 页把我的 `&lt;` 显示成 `&amp;lt;` | 正文走了 `esc()`；解析器不解码实体（正是本页要教的误解） | 含 `& < >` 的正文改用 `Raw`/CDATA 分块 | v004 看图三处均按字面显示 |
| 第 4 页插图与独立示例在卡内差 0.956（max 21） | `BackdropFilter` 读取子树之外的背景，外层画布不同结果就不同（probe-backdrop a/b/c 三次渲染证实：仅换包装就有同样差异） | 独立示例改 `background="#FFFFFF"` 与页内白卡一致；自检允许“差异全部落在滤镜矩形内且 ≤24”，并记录探测证据 | verify：三页 ≥0.9999 完全一致，第 4 页差异 100% 在滤镜矩形内 |
| 印刷片段行号与交付文件对不上 | 之前按 core 相对行统计，而文件里 core 被嵌套两级 | `code_text` 改为直接给出文件行，`RANGES` 用文件 1-based 行号；verify 改成按序在文件里匹配 | 四页 `printed-snippet-verbatim` 通过 |
| 109 字符的源码行被算成一行，面板高度不够 | `wrap_rows` 把空格丢了 | 空格计入原子；同时把面板内边距 20→14、段间距 14→12 | 四页 bottom 1435/1481/1481/1489 ≤ 1498 |
| 插图底部说明压在彩色条纹上 | 条纹铺满 240 高 | 条纹高度改 172，说明落在白底 | v007 看图 |

## 6. 已知残余（不影响交付要求）

1. 第 4 页代码面板里 `example-04.snapshot` 第 38 行长 109 字符，按真实软换行显示成两行；
   文本内容与文件逐字一致，面板高度也按同一模型预留，不会与下一行重叠。
2. 第 4 页插图与独立示例在 `BackdropFilter` 卡内有 ≤21/255 的像素差，成因为文档所述的
   “读取子树之外的背景”，已用三次探测固定为可解释差异而非缺陷。
3. 手册页脚与页码为排版辅助，不构成额外交付项。

## 7. 统计

49 次 A17 请求（45 次渲染 + 4 次探测）全部成功、0 次重试、0 次错误响应；
文档与字体查询复用 `_suite` 共享准备的 61 次请求，未重复抓取。
7 个 DSL 版本、22 次实际看图、5 次完整视觉迭代 + 1 次基线 + 1 次语法修复。
墙钟 19:04→19:52（约 48.3 分钟），请求往返合计 170.7 秒。
