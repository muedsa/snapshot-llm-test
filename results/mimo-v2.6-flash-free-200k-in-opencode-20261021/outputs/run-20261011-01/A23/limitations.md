# A23 · 能力边界与替代交付说明（limitations.md）

逐项列明客户原始请求、本服务（Snapshot DSL + open-snapshot `/snapshot` 接口）的实际支持
情况、判定依据（真实文档/实测响应，不臆造）、已授权的替代交付，以及仍需外部后续工作的地方。
依据均指向本 run 已真实取得并缓存的文档或真实服务响应（`tmp/run-20261011-01/_suite/docs/`、
`tmp/run-20261011-01/A23/requests.jsonl`）。

判定方法：先读 ai-guide/DSL 标签文档，再用**真实探针渲染**（`A23-probe-01`）实测透明背景与
旋转方向，不用臆测参数。所有"不支持"结论均来自接口文档（`type` 只有 `png`/`jpg`/`webp`、
无 SVG/CMYK/多帧/动画参数）或实测响应，不编造参数。

| # | 客户原始请求 | 支持情况 | 判定依据（真实） | 本题替代交付 | 仍需外部后续工作 |
|---|---|---|---|---|---|
| 1 | 文字可编辑 **SVG** 矢量稿 | **不支持**（服务只出位图） | ai-guide.md：`type` 可为 `png`/`jpg`/`webp`，无 `svg`；`/snapshot` 响应为位图字节（本题 7 图 `Content-Type: image/png`） | **1200×800 RGB PNG 封面**（`cover.png`）+ 同名完整 `cover.snapshot`；标题文字"从结构到画面"用 `Text` 标签，改 `text=`/`fontSize=` 重渲染即可编辑，非描边转曲 | 如必须 `.svg`：用 Inkscape/Illustrator 按各单元几何（见 `frame-data.json`）重描，或等待服务提供 SVG 输出 |
| 2 | **CMYK** 印刷稿 | **不支持**（无 CMYK 色彩空间/ICC 参数） | ai-guide.md 仅列 RGB/CSS 颜色语法（`#RRGGBBAA`/`rgb()` 等）；`type` 无 CMYK 项；接口不返回色彩配置文件 | **RGB PNG 封面** + 12 单元精确色值清单（`frame-data.json` 的 `units[].color_rgb`）+ 透明关键帧 | 印前用 Adobe/Affinity/Ghostscript 按目标 ICC（如 Japan Color 2001 Coated）转 CMYK 并打样校色 |
| 3 | **6 帧透明 GIF** 动画 | **不支持**（接口单次单图，无 GIF/多帧/时间轴） | ai-guide.md：一次 `POST /snapshot` 返回一张图；`type` 无 `gif`；DSL 标签总表无动画/时间轴标签（不臆造） | **6 张 600×600 透明 PNG 关键帧**（`frame-01..06.png`，各配完整 `.snapshot`）+ `timing.json`（250ms/帧、循环 1500ms、帧序 1→6、插值规则、循环跳变说明） | 用 ffmpeg / ImageMagick / GIF 编码器按 `timing.json` 合成 GIF/APNG/动画 WebP；如需更流畅按 `frame-data.json` 轨迹补中间帧 |
| 4 | **PNG 封面** | **原生支持** ✓ | `type="png"`；`background` 非 transparent 即不透明底；实测 `cover.png` 1200×800 全像素 alpha=255 | 交付 `cover.png`（83265 字节，md5 `760df51f…`）+ `cover.snapshot` | 无 |
| 5 | **透明背景** | **原生支持** ✓ | `background` 默认 `transparent`（parser 文档）；颜色支持 `#RRGGBBAA`/`transparent`；**探针 `A23-probe-01` 与 6 帧实测**：`type=png` 返回 RGBA、四角 alpha=0、透明面积占比 0.62–0.74 | 6 张关键帧即为透明 PNG；`frame-data.json` 记录逐帧透明度实测值 | 无 |
| 6 | 单元**旋转/位移**动画 | **原生支持** ✓（仅关键帧） | `Transform` 有 `matrix`（列主序 4×4、16 有限浮点、无空格）；`origin`/`alignment` 控制变换原点。**探针实测**：矩阵正角使端点标记落到右下 → 正角=顺时针，与题目约定一致；`alignment="CENTER"` 绕自身中心 | 每帧由同一参数化 DSL 生成（`a23_common.py`），非嵌预渲染帧；12 单元仅 `x,y`（中心坐标）与 `rotation_deg` 变化，宽高/颜色/alpha 守恒 | 如需中间帧：按 `frame-data.json` 的缓动公式 `s(u)=(1−u)^1.35` 采样生成 DSL 后逐帧渲染 |
| 7 | 无缝循环 | **不支持默认无缝**（汇聚主题使首尾天然不闭合） | `frame-data.json#/seam`：接缝步位移为常规末步约 8.78 倍、方向由汇聚反转为发散；接触表实看确认循环回跳明显 | **如实记录跳变**：`timing.json` `loop.seamless=false`、`frame-data.json` `seam.closed=false`，附 12 单元接缝位移/旋转差值与实看结论，**不宣称无缝** | 如必须无缝：改 ping-pong 播放（1→6→1），或重新设计闭合轨迹并给出 t=1500ms 位移=0 的证据 |
| 8 | 封面/帧内文字 | 封面文字**原生支持**；动画帧**按要求不含文字** | `Text` 标签（内容在 `text=` 属性）；探针/帧实测无文字渲染问题 | 封面标题"从结构到画面"+ 副标题/页脚；6 张关键帧只含 12 个几何单元、无任何文字 | 无 |

## 结论

4 项原始请求中 2 项原生支持（PNG 封面、透明背景），2 项不支持（SVG、CMYK），GIF 动画部分
以"透明 PNG 关键帧 + timing.json"替代。已按授权交付**完整可执行替代包**：封面 + 6 帧透明
关键帧 + 逐单元轨迹数据 + 播放/循环时序 + 本说明，而非仅回复"不支持"。矢量/印刷/动画编码
三项的最终文件仍需外部工具按上表完成。
