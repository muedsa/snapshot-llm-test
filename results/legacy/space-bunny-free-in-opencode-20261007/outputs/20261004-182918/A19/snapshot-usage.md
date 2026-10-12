# A19 · 构造可核验的视觉题场 — 使用报告

## 0. 完成状态与目录

| 项 | 值 |
|---|---|
| 任务 | A19 · 构造可核验的视觉题场 |
| run_id | `20261004-182918` |
| 状态 | **completed**（三张指定 PNG 全部是服务真实响应，118 项 JSON/DSL 复核 + 28 项像素复核全部通过） |
| 输出目录 | `outputs/20261004-182918/A19/` |
| 临时目录 | `tmp/20261004-182918/A19/` |
| 时间 | 2026-10-05T02:09:22+08:00 起，2026-10-05T03:0x:xx+08:00 收口（时区 Asia/Shanghai） |
| 渲染请求 | 24 次 `POST /snapshot`，**0 次失败、0 次重试**；其中 21 次为交付/迭代渲染，3 次为反证实验探针 |
| 文档请求 | 3 次（`GET /ai-guide.md`、`GET /reference/parser-tags/`、`GET /fonts`），全部 200 |

### 交付清单

| 文件 | 尺寸 / 规模 | 说明 |
|---|---|---|
| `grid-scene.png` | 1600×1600 RGBA，176762 B | 8×8 网格、64 个带编号主体 G01–G64 |
| `grid-scene.snapshot` | 38979 B | 与上面 PNG 逐字节对应的完整 DSL（sha256 记在 scene-data.json） |
| `occlusion.png` | 800×800 RGBA，91527 B | 遮挡场景 A（做法 A1 覆盖） |
| `occlusion.snapshot` | 6123 B | A 的完整 DSL |
| `occlusion-alternative.png` | 800×800 RGBA，91527 B | 隐藏内容不同的等价场景 B（做法 B1 裁剪） |
| `occlusion-alternative.snapshot` | 6484 B | B 的完整 DSL |
| `scene-data.json` | 64 个对象的完整几何 + 种子 + 约束核对 | 网格题的唯一答案来源 |
| `questions.json` | 14 题（12 网格 + 2 遮挡），**不含任何答案** | |
| `answers.json` | 14 条答案 + 计算方法 + 容差 + 可见性依据 + 良构性证明 | |
| `equivalence.json` | 两遮挡 PNG 的 sha256 / 字节数 / 逐像素对比 / DSL 差异 | |
| `occlusion-scene-data.json`（附加） | 遮挡场景的可见/部分可见/隐藏几何与防泄露说明 | |
| `verification.json`（附加） | 118 项复核明细 | |
| `snapshot-usage.md` / `task-metrics.json` | 本文件与指标 | |

---

## 1. 实际使用的服务文档与字体

全部为**本题真实抓取**（`tmp/20261004-182918/A19/docs/`、`fonts-list.txt`，请求号 A19-req-001..003），
不是复用本题库其他题的缓存：

1. `GET https://open-snapshot.muedsa.com/ai-guide.md` → 200。确认：请求体是 UTF-8 纯文本 DSL 而非 JSON；
   `<Snapshot type>` 的取值；8 位十六进制按 `#RRGGBBAA` 读；非成功响应是带 `code/message/requestId` 的 JSON；
   错误响应体可能被 `curl` 写成 `.png`，因此必须检查 `Content-Type`（我的 `snapkit.render()` 就是先判
   `Content-Type` 是否以 `image/` 开头再落盘）。
2. `GET https://snapshot.muedsa.com/reference/parser-tags/` → 200。这是本题实际依赖的标签/属性参考，实测用到：
   - `Snapshot`（`type`、`background`）、`Container`（`width/height`、`color`、`borderRadius`、
     `border="宽 样式 色"`、`alignment`）、`Positioned`（`left/top/width/height`）、`Stack`（`fit`、
     `clipBehavior`）、`Text`（`color/fontSize/fontFamily/textAlign/text`）、`ClipRect`（`clipBehavior`）。
   - 文档明确 `BorderStyle` 只有 `NONE/SOLID`，所以虚线只能用短矩形拼接——本题不需要虚线，遮挡物也没有任何
     轮廓线。
   - 文档明确 `ClipRect` 默认 `clipBehavior="HARD_EDGE"`、`Stack` 也支持 `clipBehavior`，这正是 B1 方案的基础。
3. `GET https://open-snapshot.muedsa.com/fonts` → 200，返回 26 个字体族。本题实际用到：

| 字体 | 用途 |
|---|---|
| `DejaVu Sans Mono` | 全部编号 G01–G64、C1–C8、R1–R8、遮挡场景的 V1–V4/P1 |
| `DejaVu Serif, Noto Serif CJK SC` | 两张图的主标题 |
| `Inter, Noto Sans CJK SC` | 遮挡物上的文字（`遮挡物 1/2`、`后方内容：不可判定`） |
| `Noto Sans CJK SC` | 说明文字、图例、页脚、页内注释 |

没有臆造任何字体名。

---

## 2. 实际用到的标签与属性

整张图都是**全绝对定位**：唯一根 `<Container width height>` 定画布，内部一个
`<Stack fit="EXPAND">`，每个元素都是 `Positioned` 给出精确 `left/top/width/height`。
DSL 里的坐标就是 `scene-data.json` 里的坐标，可以逐字符核对。

- **主体几何**（本题的核心技巧）
  - 圆：`Container borderRadius = 尺寸/2`，实心。
  - 方：`Container borderRadius = 0`，实心。
  - 圆角方：`Container borderRadius = 0.22 × 尺寸`。
  - 圆环：**不用 alpha**。发一个 `尺寸 × 尺寸`、`borderRadius = 尺寸/2` 的 Container，
    `border="尺寸/4 SOLID 颜色"`，容器自身 `color` 填**格子底色 `#FFFFFF`**。
    Flutter 的边框向内绘制，所以外径＝尺寸、内径＝尺寸−2×(尺寸/4)＝尺寸/2，正是 TASK.md 要求的
    「外径按尺寸、内径为一半」；内圈用格子底色而不是半透明，是为了不引入任何 alpha 泄漏，
    也让 28 项像素复核可以直接断言「内圈中心是纯白」。
- **遮挡的两种做法**（题目要求「另一种遮挡方案」）
  - **A1 覆盖（`occlusion.snapshot`）**：隐藏主体是 `Stack` 的普通兄弟节点、排在最前被真实绘制；
    随后两块不透明深色矩形作为最后两层画上去把它们盖住。
  - **B1 裁剪（`occlusion-alternative.snapshot`）**：可见主体与遮挡矩形的绘制顺序与 A1 完全一致；
    隐藏主体排在**遮挡物之后**，但被放进
    `Positioned(0,0,700,800) > ClipRect(clipBehavior=HARD_EDGE) > Container(700,800) > Stack(fit=EXPAND, clipBehavior=NONE)`，
    发射位置 x=706 起，落在 700px 宽的裁剪盒之外，**在光栅化之前整体移除**。
    注意内层 `Stack` 显式写了 `clipBehavior="NONE"`，这样真正执行裁剪的是 `ClipRect` 本身而不是 Stack，
    机制归属清晰、便于反证。
- **防泄露**：遮挡矩形只写 `color`，不写 `opacity`、不用带 alpha 的颜色；全图没有虚线、半透明或残影。

### 本题踩到的 / 主动规避的 DSL 语义坑

| 坑 | 处理 |
|---|---|
| `Text` 在过窄/过矮的固定框里会**静默丢弃**整段文字（不报错） | 每次渲染都打印 `D.warnings()`，本次共修掉 2 条：`可见证据清单` 第三行原为「· P1 右侧 42 px 被遮挡物 2 压住」，估算宽度 192.5px > 盒宽 186px，改写为「· P1 被遮挡物 2 压住 42 px」后归零 |
| `crop.py` 的 box 顺序是 `(left, upper, right, lower)`，我用 `(x,y,w,h)` 传导致 `Coordinate 'lower' is less than 'upper'` | 改为自己按 `(left, top, right, bottom)` 裁剪并另存到 `A19/crops/` |
| 8 位 hex 的 alpha 在**最后**两位 | 需要透明的场合一律改成「用不透明底色挖洞」，本题因此完全没有 alpha 颜色 |
| `BorderStyle` 无 DASHED | 遮挡物不给任何描边，避免出现「像虚线轮廓」的错觉 |
| 用「画了再盖」的做法 B 时若把遮挡物排在可见主体**之前**，被遮挡的部分（P1）会反而盖在遮挡物上 | 反证实验 N1/N2 就是靠这一差异暴露问题的；见第 5 节 |

---

## 3. 逐项自检表（TASK.md 每条硬指标 → 实际值 → 结论）

### 3.1 grid-scene.png

| TASK.md 要求 | 实际值 | 结论 |
|---|---|---|
| 1600×1600 | PIL 读出 `(1600, 1600)`；DSL 根 `width="1600" height="1600"` | ✅ |
| 8×8 网格 | `grid.rows=8`、`grid.cols=8`；DSL 里恰好 64 个 190×172 圆角格子 | ✅ |
| 64 个带编号对象 G01–G64 | `objects` 长度 64，id 严格等于 `G01..G64`；DSL 里 64 个 `fontSize=20 / DejaVu Sans Mono / textAlign=CENTER` 文本 | ✅ |
| 编号从左到右 / 从上到下 | `gid(r,c)="G%02d"%(r*8+c+1)`，复核脚本逐项比对通过 | ✅ |
| 每格恰好一个主体 | 64 个主体 bbox 全部落在各自 cell bbox 内，且 64 个 (row,col) 互不重复 | ✅ |
| 4 颜色（蓝/橙/绿/紫） | `#2563EB/#EA580C/#16A34A/#7C3AED` | ✅ |
| 4 形状（圆/方/圆环/圆角方） | circle / square / ring / rounded_square | ✅ |
| 3 尺寸 48/64/80 | 计数 22 / 21 / 21 | ✅ |
| 圆按直径、方按边长 | 圆：容器宽高＝尺寸且 `borderRadius=尺寸/2`；方/圆角方：容器宽高＝尺寸 | ✅ |
| 交叉分布 | 16 种「颜色×形状」组合全部出现，每种 2–6 个（见 scene-data.json `counts.by_color_shape`） | ✅ |
| **4 颜色各恰好 16 个** | `{blue:16, orange:16, green:16, purple:16}` | ✅ |
| **4 形状各恰好 16 个** | `{circle:16, square:16, ring:16, rounded_square:16}` | ✅ |
| **每行至少 3 颜色与 3 形状** | 8 行的 distinct_colors / distinct_shapes 全部 ≥3（实际每行都是 4 颜色 4 形状） | ✅ |
| **圆环外径按尺寸、内径为一半** | 像素实测 16 个圆环：outer/inner = 80/40、64/32、48/24，误差 ≤2px | ✅ |
| **ID 在主体外、不计入主体** | 64 个主体的 `bbox.y_max` 均 ≤ `id_label.bbox.y_min`；像素复核确认标签带内没有任何主体颜色像素 | ✅ |
| 不得外部图像 | DSL 中无 `<Image>`、无 `dataUri`、无 `url` | ✅ |

### 3.2 遮挡场景（两张图）

| TASK.md 要求 | 实际值 | 结论 |
|---|---|---|
| 800×800 专用遮挡场景 | 两张均 `(800, 800)` | ✅ |
| 展示**至少两个**不同隐藏内容却得到同一最终图片的完整遮挡案例 | 一张图里同时有两块遮挡物（遮挡物 1、遮挡物 2），每块后面都有各自的隐藏内容；再加上两份交付 DSL 各自整体不同，构成多个完整案例 | ✅ |
| 只给观众可见部分 | 图中只有 V1–V4（完整）与 P1（被压住 42px）可见；两块遮挡物内部只有填充色与自己的标题文字 | ✅ |
| **不能画虚线泄漏** | 全图 `DASHED`/虚线出现 0 次；遮挡物不写 `opacity`，不用带 alpha 的颜色 | ✅ |
| 另交付两份**隐藏内容不同的完整 DSL** 和真实服务 PNG | A 有 5 个隐藏主体、B 有 6 个；每处位置的形状、尺寸、颜色与名义坐标都不同 | ✅ |
| 证明像素等价 | 两份 PNG 的 sha256 完全相同（`8599c180709c8d18…`），`ImageChops.difference` 的 bbox 为 `None`，差异像素 0 / 640000，最大通道差 0 | ✅ |
| 其中一图命名 `occlusion` | `occlusion.png` / `occlusion.snapshot` | ✅ |

### 3.3 题目与答案

| TASK.md 要求 | 实际值 | 结论 |
|---|---|---|
| 为网格图写 **12 道新题** | Q18–Q29，共 12 题 | ✅ |
| 覆盖复合属性检索 | Q18、Q19 | ✅ |
| 覆盖严格中心左右关系 | Q20、Q21（都写明「严格」「中心 x 相同即并列」） | ✅ |
| 覆盖距离 | Q22、Q23 | ✅ |
| 覆盖排序 | Q24、Q25 | ✅ |
| 覆盖包围盒 | Q26、Q27 | ✅ |
| 覆盖颜色/形状计数 | Q28（颜色）、Q29（形状） | ✅ |
| **至少 4 题需要两步关系** | 7 题标 `steps=2`：Q19、Q21、Q23、Q25、Q27、Q28、Q29 | ✅ |
| 题目写明确比较标准 | 每题都有 `comparison_criteria`（中心定义、外接框定义、并集定义、排序键、距离度量） | ✅ |
| 题目写明确坐标原点 | `global_conventions.coordinate_origin`：「每张图的左上角为原点 (0,0)，x 向右为正，y 向下为正」；两图页面上也印了同一句 | ✅ |
| **不让关系并列导致唯一题多解** | 7 道「最前/最小/最近」类题全部带唯一性断言与 margin：Q20 四个候选 center.x 互不相同；Q21 margin 950px；Q22 margin 25.39px；Q23 margin 84.29px；Q24 同列 8 个 center.y 互不相同；Q25 用 (x,y,id) 全序键；Q29 阈值 900 与最近列中心 915 相距 15px | ✅ |
| 为遮挡图写 **2 题** | Q30、Q31 | ✅ |
| **至少 1 题正确答案为「无法确定」** | Q31 的答案就是字面字符串「无法确定」 | ✅ |
| 交付 `scene-data.json`（种子与真实几何） | `seed=20261004`，64 个对象各有 cell_bbox / center / bbox / geometry / id_label | ✅ |
| 交付 `questions.json`（**题目不含答案**） | 逐项扫描确认没有 `answer`/`correct`/`solution`/`answer_type` 字段，也不含任何隐藏内容提示 | ✅ |
| 交付 `answers.json`（答案、计算方法、坐标容差、可见性依据） | 14 条各含 `answer`、`answer_type`、`computation_method`、`derived_from`、`coordinate_tolerance`、`visibility_basis`、`well_posedness` | ✅ |
| 交付 `equivalence.json`（两遮挡原始 PNG 哈希/像素对比） | 含两组 sha256 + 字节数 + `pixel_comparison` + `dsl_difference` | ✅ |
| **编号 ≥18** | 题号从 **Q18** 起编到 Q31（题面文字里明确写了「编号≥18」，故从 18 开始编号） | ✅ |
| **答案能从 scene-data.json 程序化推导并校验** | `verify_a19.py` 完全不读生成器内存状态，只读 4 份交付 JSON 重新算 14 条答案，全部一致；`scene-data.json` 里还记了 `generator.reproducible` | ✅ |
| **equivalence 的等价关系也能复核** | 除 sha256 与逐像素 diff 外，另有 3 个反证探针（见第 5 节）证明这个相等关系是有约束力的 | ✅ |
| **题目只能根据最终可见图回答** | 14 题的 `scope` 都排除了图例/行列标/标题/页脚；遮挡题明确排除隐藏内容 | ✅ |
| **不能把隐藏对象数量作为标准答案** | 隐藏数量 5 / 6 只出现在审计说明（`occlusion-scene-data.json`、`equivalence.json`）里，**没有出现在任何题目的标准答案中**；Q31 的答案恰恰是「无法确定」 | ✅ |
| 实际看图检查所有目标与标签 | 见第 4 节，共 13 次实际读图 | ✅ |

---

## 4. 实际看图记录（渲染次数 / 看图次数 / 改了什么）

渲染 24 次，其中交付相关 21 次 + 反证探针 3 次。看图 13 次：

| # | 看的图 | 看到的问题 | 改动 |
|---|---|---|---|
| 1 | `outputs/.../grid-scene.png`（v1，A19-req-004） | 首版整体成立：64 格、编号、图例、行列标、四色四形三档都清楚；网格右侧留白 20px 与左侧 60px 不对称，但不影响读数 | 保留；仅记录 |
| 2 | `crops/crop-legend.png`（2× 放大图例带） | 图例 4 个色块 + 4 个形状 + 尺寸说明齐全，`尺寸` 后面的说明文字挤在 x=876 处但没压字 | 保留 |
| 3 | `crops/crop-col8.png`（2× 放大 C8 列） | C8 列 4 格形状/编号清晰，圆环内圈是纯白 | 保留 |
| 4 | `crops/crop-bottom.png`（1.6× 放大 R8 行与页脚） | R8 行 8 个主体与 G57–G64 编号完整，页脚未与最后一格打架 | 保留 |
| 5 | `outputs/.../occlusion.png`（v1，A19-req-005/008） | **左下角大片空白**，构图不平衡；且没有任何「部分被遮挡」的主体，「完全可见」这个判据太容易 | 重排：工作区卡片 40,126,720,512；两块遮挡物 350,168 / 350,404，各 278×222；新增 P1（橙色圆环，右侧 42px 被遮挡物 2 压住）；左下新增「可见证据清单」小卡 |
| 6 | `outputs/.../occlusion.png`（v2，A19-req-011） | **P1 越界**：clip 变体里我把遮挡物排在可见主体之前，导致 P1 的右半截画在了遮挡物**上面**，像素对比出现 2801 个差异像素、bbox `(350,458,390,548)` | 改成两个变体都是「可见主体 → 遮挡物」在最后；隐藏主体仍排在遮挡物**之后**（B1 的证明力反而更强） |
| 7 | `outputs/.../occlusion.png`（v3，A19-req-014） | `D.warnings()` 报 2 条文字溢出（第三行证据清单 192.5px > 盒宽 186px） | 改写为「· P1 被遮挡物 2 压住 42 px」，告警归零 |
| 8 | `outputs/.../occlusion.png`（v4，最终，A19-req-017/020/023） | 构图平衡：V1/V2、V3/V4 两排可见主体、证据清单、P1 与遮挡物 2 的交界都清楚；页内无虚线、无半透明 | 定稿 |
| 9 | `outputs/.../occlusion-alternative.png`（最终，A19-req-018/021/024） | 与 occlusion.png 肉眼完全一致 | 定稿 |
| 10 | `crops/crop-p1.png`（3× 放大 P1 交界） | P1 的橙色圆环被遮挡物 2 干净利落地切断，交界处无残影、无半透明边 | 保留 |
| 11 | `preview/negative-control/n1-cover-shrunk.png` | 遮挡物 1 宽度减少 40px 后，隐藏主体 H2/H3 的蓝色/紫色**露了出来** —— 证明覆盖确实是 load-bearing 的 | 该图只作反证，不交付 |
| 12 | `preview/negative-control/n2-clip-widened.png` | ClipRect 放宽到 800px 后，6 个隐藏主体全部**画在遮挡物右侧空白处** —— 证明 ClipRect 确实在裁剪 | 该图只作反证，不交付 |
| 13 | `thumbs/grid-scene-800px.png`（800px 缩略图） | 缩到 800px 后 64 个编号仍全部可读，四色四形仍可区分 | 保留 |

---

## 5. 问题与修复表

| 现象 | 定位方式 | 修复方式 | 复验结果 |
|---|---|---|---|
| 遮挡场景左下大片空白；「完全可见」判据太容易 | 看图 #5 | 重排布局并新增部分遮挡主体 P1 | 看图 #8 通过 |
| clip 变体像素不等，2801 个差异像素、bbox `(350,458,390,548)` | `equivalence.json` 的 `pixel_comparison` 直接报出差异 bbox，指向 P1 区域 | 把遮挡物改为两变体都在最后绘制；隐藏主体仍排在遮挡物之后 | 差异像素 0、sha256 相同 |
| `D.warnings()` 报 2 条「文字需要 ~2 行但盒高只放 1 行」 | 每次渲染后打印 `D.warnings()` | 把「· P1 右侧 42 px 被遮挡物 2 压住」改写为「· P1 被遮挡物 2 压住 42 px」 | 告警归零 |
| `crop.py` 报 `Coordinate 'lower' is less than 'upper'` | 直接读 Python traceback | 该工具按 `(left,upper,right,lower)` 取 box，我按 `(x,y,w,h)` 传了；改为自写裁剪并存到 `A19/crops/` | 4 张放大图都成功生成 |
| `a19_scene.py` 一处隐式字符串拼接多了一个 `)`，`SyntaxError` 报在 617 行 | `ast.parse` 定位 | 删掉多余的 `)` | 解析通过 |
| 复核脚本最初 4 条 FAIL（DSL 文本匹配假设错误） | `verify_a19.py` 打印 FAIL 明细 | 发现 `dsllib` 的数字格式是 `round(v,2)`（整数保持 int）、正方形圆角输出 `borderRadius="0.0"`；按真实格式重写匹配，并按「每种尺寸的圆环各出现几次」来计数，避免 5px 的图例描边干扰 | 118/118 通过 |
| 像素复核最初 3 条 FAIL | `pixel_audit.py` | 圆环探针点原来退到 `size/4+2`（已进内圈），改到 `size/8`（描边正中）；遮挡物内部的文字抗锯齿像素用「到 fill/标题/副标题任一连线段的距离 ≤26」判定，而不是三角形判定 | 28/28 通过 |

### 反证实验：像素等价证明是有约束力的，不是巧合

`equivalence.json` 声称「A 与 B 逐字节相同 ⇒ 覆盖完整且裁剪生效」。为了证明这句话不是空话，
`negative_control.py` 又渲染了 3 张真实服务响应（只落在临时目录，不交付）：

| 探针 | 做法 | 与交付 `occlusion.png` 的差异 bbox | 结论 |
|---|---|---|---|
| N1 | 把 A1 的遮挡物 1 宽度减少 40px | `(402,168,628,390)` —— 隐藏主体露了出来 | 覆盖不完整时图会变，说明交付图的覆盖确实完整 |
| N2 | 把 B1 的 ClipRect 从 700px 放宽到 800px | `(705,196,795,612)` —— 6 个隐藏主体全被画出来 | 裁剪不生效时图会变，说明交付图里隐藏主体确实被裁掉了 |
| N3 | 用与交付 A1 **完全相同**的 DSL 再渲染一次 | 无差异 | 服务渲染是确定性的，「两图相等」不是因为偶然 |

同时 `a19_scene.occ_geometry_check()` 在 N1 那种残缺几何上**直接抛 AssertionError**，
这本身就是「覆盖必须完整」这条约束被代码强制执行的证据（记录在 `negative-control.json` 的
`geometry_check_rejected_this_layout: true`）。

---

## 6. 「可核验」是怎么做到的（不是手填答案）

1. **生成即断言**：`gen_objects()` 里 `check_objects()` 对 TASK.md 的每条分布规则做硬断言
   （64 个、id 顺序、4×16、4×16、每行 ≥3 色 ≥3 形、圆环外径/内径、id 标签在主体外、主体在格内）。
   任何一条不满足就直接抛异常，不会产出图。
2. **种子可复现**：`scene-data.json.seed = 20261004`，并写明算法（三个独立打乱的 64 元列表 +
   罚函数驱动的随机对换）。重跑 `gen_objects(20261004)` 得到完全相同的对象表。
3. **答案独立重算**：`verify_a19.py` 不导入生成器的任何内存状态，只读
   `scene-data.json` / `questions.json` / `answers.json` / `equivalence.json`，
   用自己的实现重算 14 条答案并逐条比对——14/14 一致。
4. **题目不泄漏答案**：`questions.json` 的字段扫描确认没有 `answer`/`correct`/`solution`/`answer_type`，
   也不含任何隐藏内容提示。
5. **像素级复核**：`pixel_audit.py` 直接在渲染出来的 PNG 上量——64 个主体的实测 bbox、
   16 个圆环的实测内外径、64 个编号文字的存在与位置、两块遮挡物内部没有任何隐藏主体颜色的像素。
6. **等价关系可复核**：sha256 + 逐像素 diff + 3 个反证探针（见上）。

---

## 7. 未解决事项与如实说明

1. **token / 图像输入量 / 费用：未知（`null`）**。open-snapshot 是匿名 HTTP 服务，没有暴露任何计费或用量
   接口；本次运行也没有从聊天平台拿到任何 per-request 的 token 或费用数字。因此 `task-metrics.json` 里
   `input_tokens`、`output_tokens`、`image_input_usage`、`cost`、`currency` 全部为 `null`，**没有按字符数或
   请求体大小做任何估算**。
2. **限流 / 排队等待：未知（`null`）**。24 次渲染的 `Server-Timing` 都只有 `render;dur=…` 与 `total;dur=…`
   两段，没有出现 queue 段。因为无法确认「确实没有发生排队」，所以记 `null` 而不是 0。
3. **「编号≥18」的理解**。TASK.md 的这句我按「题号从 18 开始编号」执行（Q18–Q31）。另一种可能的理解是
   「至少 18 道题」，但 TASK.md 同时明确写了「为网格图写 12 道新题」和「为遮挡图写 2 题」，共 14 道，
   与 18 冲突；网格对象编号 G01–G64 的末号也远大于 18。两种读法我都满足不了同时，所以选前者并在此说明。
4. **圆环的「内径＝一半」是用不透明底色挖出来的，不是真正的透明镂空**。服务没有「环形路径」或
   `shape=CIRCLE` + 描边的组合可用（`Container` 的 `border` 已经是能拿到的最接近写法）。
   由于格子底色与卡片底色都是纯白、且圆环从不与任何东西重叠，视觉与几何上与真镂空不可区分，
   像素复核也确认内圈中心是纯白。这个取舍在 `scene-data.json.vocabulary.shape_rules` 里写明了。
5. **题目阈值的容差裕度**。Q29 的 x 阈值 900 距最近的列中心 915 只有 15px。列中心是 190px 的整数格点，
   任何合理的测量误差都远小于 15px；但如果评测者用自动抠图测圆心并允许 >15px 的误差，这一题会不稳。
   其余 6 道比较题的裕度分别是 950 / 25.39 / 84.29 / 全异 / 全序键 / 15px。
6. **`occlusion-scene-data.json` 与 `verification.json` 是 TASK.md 之外多加的两份文件**。
   TASK.md 只点名了 4 份 JSON；这两份是为了让「隐藏内容是什么」「复核跑了什么」可被第三方核对而附上的，
   不替代任何指定交付物。
7. 本题**没有遇到任何服务错误**：24 次渲染全部 200 且 `Content-Type` 为 `image/png`，
   没有 4xx、没有 429、没有需要重试的 503。

---

## 8. 路径

- 输出：`outputs/20261004-182918/A19/`
- 临时：`tmp/20261004-182918/A19/`
  - `a19_scene.py`（场景/题目/答案/遮挡 DSL 的唯一来源）、`build_a19.py`（构建与渲染）、
    `fetch_docs.py`、`verify_a19.py`（118 项复核）、`pixel_audit.py`（28 项像素复核）、
    `negative_control.py`（3 个反证探针）、`thumb.py`、`probe_geometry.py`、`dump_dsl.py`
  - `docs/`（ai-guide.md、parser-tags.html）、`fonts-list.txt`
  - `drafts/`（每版 DSL 留档）、`preview/negative-control/`（反证图）、`crops/`（放大核对）、
    `thumbs/`（缩略图）
  - `requests.jsonl`、`iterations.jsonl`
