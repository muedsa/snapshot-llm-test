# B03 · Snapshot DSL 应用记录

## 本题用到的文档

| 文档 | 用途 |
|---|---|
| `https://open-snapshot.muedsa.com/ai-guide.md` | 服务指南：渲染端点、尺寸约定、错误处理、字体查询 |
| `https://snapshot.muedsa.com/reference/parser-tags/` | 标签与属性总表。逐件的手法、参数与踩坑见 `technique-notes.md` |

属性用法不是照抄文档，而是**逐个试出来**的：文档没写的地方（`gradientFocal`
的取值类型、`border` 有没有虚线样式、`textAlign` 有没有垂直居中）都以服务
400 报错为准，记在 `technique-notes.md` 的边界表里。

## 十件各自用到的手法

| 用例 | 手法 | 关键属性 |
|---|---|---|
| case-01 | 偶奇填充挖出方环 | `ClipPath` `fillRule="EVEN_ODD"` |
| case-02 | 空心描边字 + 套色错位 | `Text` `foregroundMode="STROKE"` `foregroundStrokeWidth` |
| case-03 | 极坐标潮位 + 径向柔光 | `gradientType="RADIAL"` `gradientCenter` `gradientFocal` |
| case-04 | 全周扇形色盘 | `gradientType="SWEEP"` `gradientStartAngle/EndAngle` |
| case-05 | 毛玻璃浮层 | `ImageFiltered` `sigmaX/sigmaY` `tileMode` |
| case-06 | 油墨叠印 | `ColorFiltered` `blendMode="MULTIPLY"` |
| case-07 | 太阳方位与影长 | `Transform` `matrix`（16 个 Float 列主序） |
| case-08 | 曲线花形章面 | `ClipPath` `path`（Q/T/C/S/A）+ `EVEN_ODD` |
| case-09 | 6×5 高密度表 | `Positioned` `Stack` `borderRadius` |
| case-10 | 四层描边套版错位 | `Text` 描边 ×4 + `Transform` 旋转 |

## 跨题可复用的结论

1. **渲染成功 ≠ 做对了。** 本题有三处返回 200 但效果完全不对：
   `ImageFiltered` 罩住了空容器（根本没模糊）、渐变 append 在最后（盖住全部数据）、
   `Transform` 角度差 90°（投影与光线垂直）。只有真的打开图才发现得了。
2. **DSL 不排版。** 后画的实心图元直接盖住先画的文字（case-09 的百分比整列被
   徽章切没），x 必须手工算开。
3. **文字溢出被静默裁掉，仍返回 200。** 本题有四处（case-03 图例、case-05 的
   「68mm」、case-06 说明、case-07 提示语）。按 A14 标定的 `char_em` 预算宽度，
   并且**每件都要看图确认**——返回 200 说明不了没被裁。
4. **滤镜只作用于自身子树。** 要模糊/混合的图元必须是子节点，且坐标要相对滤镜盒子，
   用画布绝对坐标会二次偏移（case-06）。
5. **不支持的写法会 400，而不是静默降级。** `border="1 DASHED"`、
   `textAlign="MIDDLE"`、传颜色给 `gradientFocal` 都是直接报错——这点比静默降级好，
   至少不会做出错的图。

## 踩过的坑（跨题复用）

- `s.index('    W, H = 1200, 900')` 这种**用重复字面量定位**的写法差点毁掉整个构建脚本：
  case-03 和 case-07 同尺寸，`index()` 命中第一处，切片把中间四件函数整段删光。
  恢复过程本身也记在 `tmp/run-20261011-01/B03/restore_b03_*.py`。
  结论：**定位锚点必须唯一**（函数名、注释首行），不能靠碰巧不重复的数值。
- `exec()` 一个 fix 脚本来做内存替换时，必须让 `write_text` 落到真实临时文件再读回，
  否则拿不到替换结果（`restore_b03_c03.py` 里踩过）。

## 资产政策

十件**全部纯 DSL**，没有任何 `<Image>` 标签、没有 base64、没有外部素材。
实物照片位置一律用几何占位并在图上写明。

## 文件

- 十件：`case-01/` … `case-10/`（`final.png` + `final.snapshot` + `case.md`）
- 手法与边界：[`technique-notes.md`](technique-notes.md)
- 大图：[`gallery.md`](gallery.md) · 索引：[`portfolio.md`](portfolio.md) · [`portfolio.json`](portfolio.json)
- 指标：`task-metrics.json`
- 过程证据：`tmp/run-20261011-01/B03/`（`drafts/`、`preview/`、`responses/`、
  `requests.jsonl`，以及每轮修正的补丁脚本与事故恢复脚本）
