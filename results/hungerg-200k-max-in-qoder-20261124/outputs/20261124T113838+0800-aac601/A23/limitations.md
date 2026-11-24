# A23 能力边界与替代交付

- 状态：完整替代交付已完成；未创建伪 SVG、CMYK 或 GIF 文件。
- 判定依据：实际读取并缓存服务 `ai-guide.md`、`openapi.yaml`、`parser-tags.md`、`parser.md`；缓存路径基准为 suite_root：`tmp/20261124T113838+0800-aac601/_suite/shared/`。

| 客户请求 | 实际支持判定 | 依据 | 本题替代 | 仍需外部后续工作 |
|---|---|---|---|---|
| 文字可编辑 SVG | 原生不支持 SVG 文件输出；文字在 PNG 中栅格化 | `Snapshot.type` 仅 png/jpg/webp；OpenAPI 成功响应仅 image/png、image/jpeg、image/webp；Parser 的 SVG path 仅是裁剪路径数据，不是 SVG 文档导出 | `cover.png` 与 `cover.snapshot`；DSL 中保留可编辑文字字符串和参数，但不是 SVG 字形 | 在外部矢量工具中重建文字与图形、指定字体并输出可编辑 SVG |
| CMYK 印刷稿 | 原生不支持 CMYK 参数、ICC 配置或印刷 PDF | 接口与颜色文档只描述 PNG/JPEG/WebP 位图及 CSS/RGBA 颜色，无 CMYK/profile 字段 | 1200×800 RGB PNG 封面 | 按印厂要求转换色彩空间、嵌入 ICC、处理出血与专色，并打样 |
| 6 帧透明 GIF 动画 | 原生不支持 GIF 输出、时间轴、帧合成或循环参数 | `Snapshot.type` 枚举不含 gif；接口每次只接受一份 DSL 并返回一张位图 | 6 张 600×600 透明 PNG、同名 DSL、`timing.json` 与 `frame-data.json` | 用外部动画工具按 250ms/帧组装 GIF 或视频，并验证透明索引与循环 |
| PNG 封面 | 原生支持 | `Snapshot type="png"`；OpenAPI `image/png` 二进制响应 | `cover.png` + `cover.snapshot`，1200×800 RGB | 无 |
| 透明背景与单元 alpha | 原生支持 | `Snapshot.background` 默认 transparent；支持 #RRGGBBAA；实际六帧 RGBA 检查见 `frame-data.json` | 六张真实透明关键帧；四角 alpha=0 | 外部组装时需确认目标格式保留透明度 |
| 汇聚动画与插值 | 服务只渲染静态关键帧，不执行时间轴 | 接口无 duration/loop/frame 参数；Transform 可做单帧旋转 | 明确 smoothstep 设计轨迹，仅渲染 6 个采样点 | 外部播放器/动画工具实现中间帧与缓动 |
| 无缝循环 | 本题未声明无缝 | 末帧是汇聚后的相机，首帧是分散布局；`frame-data.json` 的接缝位移大于所有常规步长 | `loop=true`、`seamless=false`，明确 1250→1500/0ms 跳变 | 增加回散中间帧或重新设计闭合轨迹后才能宣称无缝 |

## 真实执行与核验

七张指定 PNG 均由 `POST /snapshot` 返回的原始字节保存，未使用其他绘图工具生成主体；接触表仅由已渲染关键帧拼成，保存在临时目录用于检查，不是交付图片。逐帧查看确认 U01–U12 均存在、仅位置与旋转变化、画布透明，末帧构成可识别相机图形。循环接缝会从末帧相机快速跳回首帧分散状态，影响是可见回跳；不把 loop 设置误称为无缝。
