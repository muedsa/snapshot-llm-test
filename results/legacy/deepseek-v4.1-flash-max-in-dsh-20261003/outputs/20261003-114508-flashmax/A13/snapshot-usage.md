# A13 · snapshot-usage.md

任务ID：A13 · 品牌标志到完整活动应用（虚构品牌「叠光 / Layerlight」）
运行ID：`20261003-114508-flashmax`
输出目录：`D:\workspaces\deepseek-v4.1-flash-max-in-dsh\outputs\20261003-114508-flashmax\A13\`
临时目录：`D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A13\`
完成状态：**completed**（4 张最终 PNG 全部由服务真实 200 响应取得，并已逐张 `read_image` 打开核对）
结束原因：需求满足并完成视觉自检（含真实 32×32 缩略检查）

## 1. 最终产物与需求完成情况

| 文件 | 尺寸 | 用途 | 对应DSL | 状态 |
|---|---|---|---|---|
| `symbol-color.png` | 512×512 | 透明彩色图标 | `symbol-color.snapshot` | 完成（10674 B，200 image/png） |
| `symbol-black.png` | 512×512 | 透明纯黑图标 | `symbol-black.snapshot` | 完成（7298 B，200 image/png） |
| `brand-banner.png` | 1200×400 | 品牌横幅 | `brand-banner.snapshot` | 完成（36470 B，200 image/png） |
| `launch-poster.png` | 1080×1350 | 发布海报 | `launch-poster.snapshot` | 完成（92809 B，200 image/png） |
| `brand-system.json` | — | 色彩/比例/构件/留白/应用映射 | — | 完成 |
| `rationale.md` | — | 方向差异、选择依据、小尺寸改进（288 字 ≤ 300） | — | 完成 |
| `task-metrics.json` / `snapshot-usage.md` | — | 指标与本报告 | — | 完成 |

### 逐项需求核对（依据 `tmp/.../A13/verify.json` 的真实像素统计）

| TASK.md 要求 | 实际值 | 判定 |
|---|---|---|
| 先做两个**真正不同几何方向**的 512×512 透明预览并保留临时目录 | A「层窗」正交同心方框 / B「聚光」斜向 V 形叠层；`dsl/preview-A.pane-stack.v1.snapshot`、`dsl/preview-B.converge.v1.snapshot`，PNG 在 `preview/` | 满足 |
| 看图选择后完善同一方案 | 两张都实际打开；B 被否决（见 §4），A 继续完善到 v2a 收敛 | 满足 |
| 512×512 透明彩色图标 | 尺寸 512×512；四角 alpha=0；实心范围 `[64,64,448,448]` | 满足 |
| 512×512 透明纯黑图标 | 尺寸 512×512；四角 alpha=0；**84767 个可见像素中 0 个 RGB 非零**；非零处仅边缘抗锯齿 alpha | 满足 |
| 两图标几何相同，抗锯齿 alpha 允许 | 255 实心像素两边同为 **83315**，几何差异 **0**，仅 276 个抗锯齿像素 alpha 差 1/255 | 满足 |
| 图标最多 6 个主要几何构件 | **3 个**：外环 384×384 r88 b48、内环 196×196 r46 b32、核心 76×76 r18 | 满足 |
| 32×32 仍能识别轮廓与关键负空间 | 真实渲染 32×32（`preview/check.symbol-32.v1.png`）与 32/48/64/96/128 检查表（`preview/check.size-ladder.v3.png`）；两道间隔在 32px 下为 2.9px / 1.75px，均可见 | 满足 |
| 横幅含「叠光 Layerlight」 | DSL 文本核对 + 看图（60px BOLD，x=316，未换行未裁切） | 满足 |
| 横幅含「把复杂信息，组织成清晰画面」 | DSL 文本核对 + 看图（28px，x=316） | 满足 |
| 海报另含「2026.11.07 · ONLINE」 | 60px 等宽，信息卡内（144,1072） | 满足 |
| 海报另含「OPEN BETA」 | 两处 chip：页头右上 22px、信息卡内 22px | 满足 |
| 海报另含「layerlight.example.org」 | 22px 等宽，（144,1124） | 满足 |
| 不能用品牌图标的渲染 PNG 嵌到两应用 | 横幅/海报里的标志由同一个 `emit_mark(cx,cy,size,palette)` 重新生成（缩放 208/384、360/384、64/384、152/384），DSL 中没有任何 `<Image>` | 满足 |
| 海报有独立构图，非放大横幅 | 海报为纵向 1080×1350：上 70% 深色英雄区（主标+巨型中文+英文），下 30% 浅色信息卡；横幅为 1200×400 横向左标右文锁排 | 满足 |
| 大图与 32×32 缩略均实际查看 | 20 次 `read_image`，含 4 张最终图与 32×32 缩略、五档尺寸检查表 | 满足 |
| 禁用现成标志、文字整体当图标、外部图片 | 全部几何为圆角方框/环；无外部素材、无 `<Image>`；文案只作排版元素 | 满足 |

## 2. 文档阅读与实际使用的能力

服务基地址：`https://open-snapshot.muedsa.com`（与 `run-config.json` 一致）

| 实际阅读的文档 | 本次使用的知识 | 对应位置 |
|---|---|---|
| `https://open-snapshot.muedsa.com/ai-guide.md`（本次实读，HTTP 200） | `POST /snapshot`、请求体为 UTF-8 纯文本、成功体为图片二进制、失败体为含 `code/message/requestId` 的 JSON、`type` 可选 `png/jpg/webp`、颜色 `#RRGGBBAA` 的 alpha 在后两位、`/fonts` 为 `text/plain` | 全部 4 个 DSL 的根标签与请求 |
| `https://snapshot.muedsa.com/reference/parser-tags/`（本次实读，HTTP 200） | `Snapshot background` 默认 `transparent`（**本题透明图标的关键依据**）；`Container` 的 `border` 与 `borderRadius`；`borderRadius` 只接受单值、四角要分写；`EdgeInsets` 用 `"(a,b)"`；`Transform.matrix` 列主序 4×4；`Stack/Positioned` 语义 | `symbol-*.snapshot`（透明画布）、`brand-banner.snapshot` / `launch-poster.snapshot`（`boxShadow="0 10 30 0 #0F172A1F NORMAL"`、`border="2 SOLID #0E9F8F99"`） |
| A01 已取得并保存在 `_suite/shared/fonts.txt` 的 `/fonts` 结果（复用，未重复请求） | 本次只使用 `Noto Sans CJK SC`（正文/字标）、`Noto Sans Mono CJK SC`（日期、网址、眉标） | 全部文字节点 |

**本次新确立的知识（可复用）**：

1. `Snapshot background` 的默认值就是 `transparent`，写 `<Snapshot type="png">` 即可得到带 alpha 的透明 PNG，不需要任何额外属性。
2. **只有 `border`、没有 `color` 的 `Container` 内部是真透明**（`BoxDecoration` 只画边框）。这是本次做出「负空间」的唯一手段：外环与内环都是 `border=...` 的空心方框，两道间隔的 alpha 实测为 0。
3. `dslkit.rotated()` 的矩阵把旋转写在了单位矩阵上（只有平移生效）。本题自建 `rot_box()/rot_bar()`，把 `(cos,sin,0,0,-sin,cos,0,0,...)` 放进前四位，旋转才真正生效；最终交付里虽未使用旋转，但方向 B 的三道 V 形完全依赖它。

## 3. 迭代过程、服务调用与图像检查

请求记录：`tmp/20261003-114508-flashmax/A13/requests.jsonl`（追加式，21 行）
迭代记录：`tmp/20261003-114508-flashmax/A13/iterations.jsonl`（8 行）
看图记录：`tmp/20261003-114508-flashmax/A13/image-views.jsonl`（20 行）

渲染请求总数 **21**，成功 **21**，失败 **0**，重试 **0**（无 429、无 5xx、无 `Retry-After`）
DSL 版本数 **12**，实际图片查看次数 **20**，完整视觉迭代 **4**，未完成视觉迭代 **0**
其他接口查询：本次 **0**（指南与标签参考用 `web_fetch` 读取，字体结论复用 A01 的真实 `/fonts` 响应）

| 请求ID | 输入DSL | 耗时 | HTTP / Content-Type | 响应文件 | 查看结果 |
|---|---|---|---|---|---|
| A13-REQ-0001 | `dsl/preview-A.pane-stack.v1.snapshot` | 1.3 s | 200 / image/png | `preview/preview-A.pane-stack.v1.png` | 已看：方向 A 成立 |
| A13-REQ-0002 | `dsl/preview-B.converge.v1.snapshot` | 1.3 s | 200 / image/png | `preview/preview-B.converge.v1.png` | 已看：方向 B 否决 |
| A13-REQ-0003…0006 | `dsl/symbol-color.v2{a,b,c,d}-*.snapshot` | 各 1.2–1.6 s | 200 / image/png | `png/symbol-color.v2{a,b,c,d}-*.png` | 4 张全看：三种叠块都被否决 |
| A13-REQ-0007 | `dsl/check.symbol-32.v1.snapshot` | 1.2 s | 200 / image/png | `preview/check.symbol-32.v1.png` | 已看：32px 轮廓与间隔可辨 |
| A13-REQ-0008 | `dsl/check.size-ladder.v1.snapshot` | 1.4 s | 200 / image/png | `preview/check.size-ladder.v1.png` | 已看：**页头标题被右边缘裁切** |
| A13-REQ-0009…0012 | `dsl/final/*.snapshot` | 各 1.2–3.4 s | 200 / image/png | `png/final.*.v1.png` | 4 张全看：横幅装饰环浑浊、海报英雄区读成靶心 |
| A13-REQ-0013/0014 | `dsl/final/brand-banner.snapshot`、`launch-poster.snapshot` | 1.5 / 3.2 s | 200 / image/png | `png/final.*.v2.png` | 已看：两处问题均已修正 |
| A13-REQ-0015 | `dsl/check.symbol-32.v1.snapshot` | 1.2 s | 200 / image/png | `preview/check.symbol-32.v2.png` | 已看：同几何，非最终图 |
| A13-REQ-0016/0017 | `dsl/check.size-ladder.v1.snapshot` | 1.3 / 1.4 s | 200 / image/png | `preview/check.size-ladder.v2/v3.png` | 均看：v2 仍截断、v3 完整 |
| A13-REQ-0018…0021 | 已定稿的 4 个 `dsl/final/*.snapshot` | 各 1.2–3.2 s | 200 / image/png | **`outputs/.../A13/*.png`（最终图）** | 4 张全看：定稿确认 |

说明：`-REQ-0018…0021` 是把已通过视觉验收的同一份 DSL 重新 POST 到服务，让输出目录里的最终 PNG 本身就是 curl 的响应体（而不是从临时目录搬运的文件）；服务对相同 DSL 返回相同字节，两次渲染的 `content_type` 都是 `image/png`。

## 4. 修改记录与踩坑

| 迭代ID / 类型 | 问题或现象 | 原因及确认依据 | 采取的修改 | 验证结果 |
|---|---|---|---|---|
| A13-IT-0002 / 方案探索 | 方向 B 的三道 V 形互相遮挡，青/蓝只剩圆头端点；顶点处两条 bar 叠成疙瘩；整体像通用「>」箭头 | 看图（`preview-B.converge.v1.png`）：三道层只有最前面那道完整可见 | 否决 B，不做进一步修改 | A 与 B 并排比较后选定 A |
| A13-IT-0003 / 方案探索 | 核心后加半透明叠块表示「叠」，三种颜色（青/蓝/琥珀）在 512 下都读作脏影子或褪色残留 | 看图（`symbol-color.v2b/c/d*.png`）：叠块与核心的边界产生一层灰调，像重影 | 删除 ghost 构件，收敛为 3 个干净构件（v2a） | `symbol-color.v2a-noghost.png` 最干净；`brand-system.json` 记录 `component_count: 3` |
| A13-IT-0004 / 视觉 | 尺寸检查表页头标题与页脚说明超出 624px 画布，右侧被裁切 | 看图（`check.size-ladder.v1.png`）：标题最后一个字被切 | 缩短文案并加宽画布 | v2 仍轻微越界 |
| A13-IT-0005 / 视觉 | 仅按估算字宽排版不可靠 | 看图（`check.size-ladder.v2.png`）：标题仍被切 | 标题降到 22px、去掉长括号说明，画布 624→760 并留 136px 空档 | v3 文字完整，五档图标均可辨 |
| A13-IT-0006 / 视觉 | 横幅右侧三个装饰环中的琥珀环（`#F59E0B29`）叠在 `#0F172A` 上呈浑浊橄榄色，被画布切断后像脏块 | 看图（`final.brand-banner.v1.png`） | 删除琥珀环，只留青/蓝两环，边框 32/28→30/24、alpha→`0x1F`/`0x26`，中心右移到 x=1120 | v2 右半部安静，字标成为唯一焦点 |
| A13-IT-0007 / 视觉 | 海报英雄区同时出现 2 个装饰环 + 标志自身的 2 道环 = 四层同心方框，读成靶心；主标仅 306 且与「叠光」大字挤在一起 | 看图（`final.launch-poster.v1.png`） | 装饰改为两个**对角偏移**的光环；主标 306→360、y 336→360；大字 y 512→580；深色区 880→940；信息卡整体下移 | v2 由「同心靶心」变为有纵深的层叠主体 |
| A13-IT-0008 / 需求核对 | 需要机器确认黑版纯度与两图标几何一致性 | `verify.json` 逐像素统计 | 无修改 | 84767 可见像素 0 个 RGB 非零；几何差异 0 |

**「渲染成功但视觉不符合要求」的情况**：A13-IT-0002/0003/0006/0007 全部是 HTTP 200、图片可打开但视觉不达标，靠看图发现而不是靠状态码。

**从文档了解到、本次未触发**：`413 REQUEST_TOO_LARGE`（本题最大请求体 5107 B）、`?errorImage=png`（未使用，保持 JSON 错误体可读）、`429/503 + Retry-After`（21 次请求未遇到）。

## 5. 任务耗时与资源消耗

结构化指标：`outputs/20261003-114508-flashmax/A13/task-metrics.json`

| 指标 | 实际值 | 单位 | 来源与范围 |
|---|---|---|---|
| 任务开始 / 结束 | 2026-10-03T12:51:24+08:00 / 2026-10-03T12:55:59+08:00 | ISO8601 +08:00 | 开始取 `tmp/<run>/A13` 目录创建时间；结束取最后一次请求的 `ended_at` |
| 任务总耗时（墙钟） | 275.0 | 秒 | 上述两时间之差 |
| 首次可用图耗时 | 约 84 | 秒 | 从目录创建到 `A13-REQ-0001` 成功结束（12:52:48） |
| 等待用户反馈 | 0 | 秒 | 单轮任务，未等待 |
| 限流等待 | 未确认（null） | — | 未发生 429，无 `Retry-After` 可测 |
| 排队等待 | 未确认（null） | — | 服务端未返回排队时长，不可测 |
| 已记录请求耗时之和 | 34.396 | 秒 | `requests.jsonl` 21 条 `duration_ms` 求和；含网络往返，不等于任务墙钟 |
| 输入 / 输出 / 总 token | 未确认（null） | token | 平台未提供，不用字数估算 |
| 图像输入使用量 | 未确认（null） | — | 平台未提供 |
| 任务费用 | 未确认（null） | — | 平台未提供计费数据 |

## 6. 设计选择、经验与未解决事项

**关键设计选择**

1. **标志概念**：把「信息叠加后仍然清晰」直接做成几何——外青、内蓝两道**空心环**构成两层窗格，两道环之间是**完全透明的间隔**（alpha 实测为 0），中央琥珀方块是叠加之后仍然清晰的核心。三个构件的圆角比例都约 23%（88/384、46/196、18/76），所以三个形状看起来同族。
2. **负空间的实现**：只在 `Container` 上给 `border`、不给 `color`，内部即为真透明。这比用背景色画「假洞」更正确——把图标放到任何底色上，间隔都会透出底色。
3. **四个应用同源**：`emit_mark(cx, cy, size, palette)` 是唯一的几何来源，四个交付物都调用它，因此不存在「把图标 PNG 贴到横幅上」的问题；缩放系数 1.0 / 1.0 / 0.542 / 0.938（海报英雄）全部记录在 `brand-system.json`。
4. **最小留白**：512 画布下四边各 64px，等于标志外框边长的 16.7%，由 alpha 包围盒实测得出，写进 `brand-system.json.ratios.clear_space`。
5. **海报独立构图**：纵向 1080×1350，上 70% 深色英雄区、下 30% 浅色信息卡；横幅是横向左标右文。二者共享色板与几何，但版式完全不同。

**可复用经验**

- 透明画布无需额外属性；`#RRGGBBAA` 的 alpha 在最后两位。
- 空心 `Container`（只给 `border`）= 真负空间，是画「窗/环/洞」的最省事做法。
- 低 alpha 的暖色（琥珀）叠在深蓝底上会变成浑浊的橄榄色；深底装饰只用青/蓝两色更稳。
- 需要真实旋转时必须自建矩阵；`dslkit.rotated()` 只平移。
- 排一行文字前先按 `1.0×CJK / 0.6×等宽 / 0.55×拉丁` 估算并留 15% 余量；尺寸检查表第一版就是按估算排的，仍然越界，最后靠降字号 + 加宽画布解决。

**未解决事项**

- 32px 下第二道间隔只有 1.75px，靠抗锯齿仍可辨但已接近极限；`brand-system.json` 因此把最小可用尺寸定为 24px 并注明不建议更小。
- 横幅右侧装饰环在 1200×400 之外继续延伸，属于有意的出血；如果将来需要方形或更窄的横幅裁切版本，需要重新定位装饰环。
- 两图标的 alpha 通道并非逐字节相同（276 个抗锯齿像素差 1/255）；实心几何完全一致。TASK.md 明确允许抗锯齿 alpha 差异，因此按允许处理，未做后处理强行对齐。

**留痕确认**：所有 DSL 版本（12 个）、每次渲染的 PNG（21 张，含 4 张最终图）、4 个只差核心的候选、方向 B 的否决件、尺寸检查表 v1/v2/v3、`requests.jsonl`、`iterations.jsonl`、`image-views.jsonl`、`tool-usage.jsonl` 全部保留在 `tmp/20261003-114508-flashmax/A13/`，未删除、未覆盖。`finalize.py` 首次运行曾把三个 jsonl 重复追加一次，重复内容已归档到 `tmp/.../A13/logs-archive/*.duplicated-2runs`，当前日志为重建后的干净记录。
