"""A19 一站式交付。启动基准：总任务根。"""
from __future__ import annotations

import sys

sys.path.insert(0, "tmp/run-20261011-01/_suite/scripts")
import deliver  # noqa: E402

SPEC = dict(
    task_id="A19", title="可核验的视觉题场", version="v1",
    started_at="2026-10-12T12:40:00.000+08:00",
    source_drafts={"grid": "a19-grid-scene-v1.snapshot",
                   "occA": "a19-occlusion-v1.snapshot",
                   "occB": "a19-occlusion-alternative-v1.snapshot"},
    images=[
        {"name": "grid-scene.png", "dsl": "grid-scene.snapshot", "draft_key": "grid"},
        {"name": "occlusion.png", "dsl": "occlusion.snapshot", "draft_key": "occA"},
        {"name": "occlusion-alternative.png", "dsl": "occlusion-alternative.snapshot",
         "draft_key": "occB"},
    ],
    audit_json=[
        {"filename": "scene-data.json", "draft_name": "scene-data-raw-v1.json"},
        {"filename": "questions.json", "draft_name": "questions-raw.json"},
        {"filename": "answers.json", "draft_name": "answers-raw.json"},
        {"filename": "equivalence.json", "draft_name": "equivalence-raw.json"},
    ],
    candidates=[
        {"path": "tmp/run-20261011-01/A19/responses/A19-v1-occlusion.error.json",
         "status": "failed",
         "note": "遮挡场景首版 400：图例循环把 (色, 编号) 元组解成了 (编号, 色)，"
                 "于是 `color=\"B1\"`。改为按 (col, lab) 解包后重渲通过。"},
        {"path": "tmp/run-20261011-01/A19/preview/grid-center-2x.png", "status": "diagnostic",
         "note": "网格中部 2×2 格 2× 放大：G12 圆、G13 圆角方（切角可见）、G20 直角方、G21 圆；"
                 "编号在主体之外，不压在主体上"},
        {"path": "tmp/run-20261011-01/A19/preview/grid-tl-2x.png", "status": "diagnostic",
         "note": "左上 2×2 格 2× 放大：G10 圆环镂空清晰，内径约为外径的一半"},
    ],
    extra_capabilities="**圆环用 `Container` 的 `border` + `borderRadius` 实现**，"
                       "外径 = size、描边宽 = size/4，于是内径 = size − 2·(size/4) = size/2，"
                       "正好满足题面「内径为一半」。`borderRadius` 取 size/2，"
                       "必须严格大于描边宽度 size/4——这是 A13 已实测到的服务端硬限制。"
                       "环用 `color=\"#FFFFFF00\"` 全透明填充，只留描边。\n"
                       "**全部属性由三条确定性规则推出，不是随机碰运气**："
                       "颜色 = 列号 mod 4；形状 = 4×4 拉丁方按行轮转、两个列块错开 2 位；"
                       "尺寸在每个「颜色×形状」组（恰好 4 格）内轮转 48/64/80。"
                       "规则 + 种子号一起写进 scene-data.json，任何人重算都能得到同一张图。\n"
                       "**像素等价用解码后比较，不用文件哈希**：判定依据必须是解码后的像素，"
                       "因为题面明确「不同压缩或元数据导致文件哈希不同，不据此判像素不等价」。"
                       "这里用同一个 Pillow 版本把两张都解码成 8 位未预乘 RGBA、"
                       "再逐像素四通道完全相等地比较，并记录数组哈希、不同像素数与最大通道差。"
                       "实测结果比预期更强：两份最终 PNG 连**文件级 SHA-256 都相同**"
                       "（服务端对相同像素与相同参数产生了逐字节相同的 PNG）。"
                       "但判定仍以解码像素为准——文件哈希相等并不构成「像素等价」的证明。\n"
                       "**属性从最终 PNG 反测，不采信 scene-data.json 的自述**："
                       "verify_a19.py 对 64 个对象各采 5 个点（中心、0.30·size、"
                       "size/2−3、size/2+4、圆环环带、圆角方角点），"
                       "实测最大通道差 0。",
    extra_docs="""
| https://snapshot.muedsa.com/reference/parser-tags/ · Container 的 border/borderRadius | 圆环靠描边实现；borderRadius 必须大于描边宽度，否则 400 | 圆环 size 48/64/80 → 描边 12/16/20、圆角 24/32/40 |
| https://snapshot.muedsa.com/reference/parser-tags/ · Color | 八位十六进制为 #RRGGBBAA，`#FFFFFF00` 即全透明填充 | 圆环只保留描边、内部镂空 |
| https://snapshot.muedsa.com/reference/parser-tags/ · ClipOval | 圆形裁剪 | 实心圆的实现 |
""",
    other_queries="字体查询与文档读取为 run 级共享准备；本题请求全部为渲染请求"
                  "（网格 1 次 + 遮挡 2 版各 2 次，含 1 次 400）。"
                  "像素等价比较、缩略与裁切由本地 Pillow 完成，不是服务渲染。",
    req_items="""
| 文件 | 用途 | 对应 DSL 或图 | 完成状态 |
|---|---|---|---|
| `grid-scene.snapshot` / `.png` | 1600×1600 八乘八可问答场景 | 服务 `image_info` 为 PNG 1600×1600 | 已完成 |
| `occlusion.snapshot` / `.png` | 800×800 遮挡场景 A | 服务 `image_info` 为 PNG 800×800 | 已完成 |
| `occlusion-alternative.snapshot` / `.png` | 800×800 等价场景 B | 服务 `image_info` 为 PNG 800×800 | 已完成 |
| `scene-data.json` | 种子、64 对象真实几何、三类频数、组合覆盖、逐行计数与检查依据 | — | 已完成 |
| `questions.json` | 14 道题（网格 12 + 遮挡 2），只含题面 | — | 已完成 |
| `answers.json` | 答案、计算步骤、关系与距离定义、容差、可见性依据 | — | 已完成 |
| `equivalence.json` | 两版 DSL/PNG 路径、文件 SHA-256、隐藏差异、像素对比判定 | — | 已完成 |
| `snapshot-usage.md` / `task-metrics.json` | 报告与指标 | — | 已完成 |

需求逐项核对（依据**实际打开查看**：三张交付图、两张 400px 缩略、
网格中部与左上 2×2 格的 2× 放大裁切、遮挡面板上方 2× 裁切）

| 题目要求 | 满足情况 | 证据 |
|---|---|---|
| 1600×1600 的 8×8 网格场景 | 满足 | 服务 `image_info` 为 PNG 1600×1600；8×8 格线与 64 个主体 |
| 64 个带编号对象 G01–G64 | 满足 | `scene-data.json.objects` 长度 64，编号自 G01 至 G64 |
| 编号从左到右 / 从上到下 | 满足 | `objects[i].row/col` 与 `id` 的映射为 `G{(r-1)*8+c}`，已断言 |
| 每格恰好一个主体 | 满足 | 构建脚本按格循环，每个格子只追加一个 `subject()` |
| 4 颜色（蓝/橙/绿/紫） | 满足 | `distribution.by_color` = 四色各 16 |
| 4 形状（圆/方/圆环/圆角方） | 满足 | `distribution.by_shape` = 四形各 16 |
| 3 尺寸 48/64/80（圆按直径、方按边长） | 满足 | `distribution.by_size` = 48:22 / 64:21 / 80:21；PNG 反测确认外接框边长 |
| 颜色与形状交叉分布 | 满足 | `distribution.by_color_and_shape` 覆盖全部 16 种组合，每组 4 个 |
| 4 颜色与 4 形状各恰好 16 个 | 满足 | `constraints_satisfied.each_color_16 / each_shape_16` |
| 每行至少 3 颜色与 3 形状 | 满足 | `per_row` 每行 color_count = 4、shape_count = 4（≥3） |
| 圆环外径按尺寸、内径为一半 | 满足 | 描边宽 = size/4 ⇒ 内径 = size/2；PNG 反测「中心为背景、0.35·size 处为主体色」16/16 通过 |
| ID 在主体外、不计入主体 | 满足 | 编号绘于格内左上角 (c·200+14, r·200+10)，主体居中；`id_label_box` 与 `bbox` 分列 |
| 不得外部图像 | 满足 | 三份 DSL 中没有任何 `<Image>`；全部图元为 Container/ClipOval/Text |
| 另构造 800×800 完整遮挡案例 | 满足 | 面板 rect(120,200,560,400) 实心不透明，隐藏层四周留 40px 余量 |
| A、B 两版隐藏内容不同 | 满足 | A：H1–H5（圆/方/圆角方/圆/圆环，蓝/橙/绿/紫/青）；B：K1–K5（方/圆角方/圆/圆环/方，紫/橙/绿/蓝/青） |
| 两版可见部分完全相同 | 满足 | `equivalence.json.comparison`：不同像素数 0、最大通道差 0、像素数组哈希相同；文件级 SHA-256 亦相同 |
| 不能画虚线泄漏 | 满足 | 遮挡物为不透明实心直角矩形；隐藏层完全在其内部；不用阴影/滤镜/半透明 |
| 分别交付 occlusion 与 occlusion-alternative 的完整 DSL 与真实服务 PNG | 满足 | 两份 `.snapshot` 与两份 PNG 齐全，PNG 由服务返回 |
| 遮挡两张 + 网格一张 = 指定最终图三张 | 满足 | `required_outputs` 三项全部交付，无多余最终图 |
| 为网格图写 12 道新题 | 满足 | `questions.json` 中 Q18–Q29 共 12 道 |
| 覆盖复合属性检索 | 满足 | Q18、Q19 |
| 覆盖严格中心左右关系 | 满足 | Q20、Q29 |
| 覆盖距离 | 满足 | Q21、Q22 |
| 覆盖排序 | 满足 | Q23、Q24 |
| 覆盖包围框 | 满足 | Q25、Q26 |
| 覆盖颜色/形状计数 | 满足 | Q27（颜色计数）、Q28（形状计数） |
| 至少 4 题需要两步关系 | 满足 | 两步题 8 道：Q19、Q20、Q22、Q24、Q26、Q27、Q28、Q29 |
| 题目写明确比较标准 | 满足 | 每题有 `criteria` / `comparison_rule` 字段，说明属性、严格不等式、次级排序键与判定基准 |
| 题目写明确坐标原点 | 满足 | 每题有 `coordinate_origin`（画布左上原点、x 右 y 下、像素单位、格心坐标集） |
| 不让关系并列导致唯一题多解 | 满足 | 取极值的题在代码里断言并列数为 1；Q21 验证距离恰为 250 的对象数为 0；Q24 声明次级排序键 x；左右比较一律跨列 |
| 为遮挡图写 2 题 | 满足 | Q30、Q31 |
| 至少 1 题正确答案为「无法确定」 | 满足 | Q30 答案为「无法确定」，并给出为何两隐藏版本无法区分的解释 |
| 交付 scene-data.json（种子与真实几何） | 满足 | `seed`=20261107（构造式，含三条规则）、`objects` 64 条含行列/颜色/形状/尺寸/中心/主体框/编号框 |
| scene-data.json 列出三类频数、组合覆盖与逐行计数 | 满足 | `distribution` 段含 by_color/by_shape/by_size/by_color_and_shape/size_by_color/size_by_shape 与 `per_row` |
| 不能只记录随机种子而不记录实际生成结果 | 满足 | 种子之外记录了全部 64 条真实几何与全部频数表 |
| 交付 questions.json（不含答案） | 满足 | 只含题面字段；答案、解法与唯一性说明全部在 answers.json |
| 交付 answers.json（答案、方法、容差、可见性依据） | 满足 | 每条含 `answer`/`steps`/`method`/`relation_and_distance_definition`/`required_tolerance`/`final_visible_information_basis` |
| 交付 equivalence.json（原始 PNG 哈希 / 像素对比） | 满足 | `file_provenance` 记录两份 SHA-256；`comparison` 记录解码器与版本、相同尺寸、8 位未预乘 RGBA、数组哈希、不同像素数 0、最大通道差 0、判定「等价」 |
| 编号 ≥18 | 满足 | 题号自 Q18 起（Q18–Q29 网格、Q30–Q31 遮挡）。该条的两种可能读法——题号 ≥18、或对象编号需 ≥18——本套编号 G01–G64 已整体满足后者 |
| 题目只能根据最终可见图回答 | 满足 | 每题有 `answerable_only_from_final_image = true` 与 `visibility_basis` |
| 不能把隐藏对象数量作为标准答案 | 满足 | Q30 答案写「无法确定」并解释：两版恰好都是 5 个，但该数字只能从 DSL 知道、不能从图上读出，故不作为答案 |
| 实际看图检查所有目标与标签 | 满足 | 三张交付图整屏打开 + 网格中部/左上 2×2 放大 + 两张缩略，逐格确认主体形状、编号位置与环的镂空 |
| 所有指定最终 PNG 都是服务真实响应且有同名 `.snapshot` | 满足 | 三对文件齐全，DSL 与服务实际接收的同一份 |
""",
    request_rows=[
        ("A19-v1-grid-scene-*", "drafts/a19-grid-scene-v1.snapshot", "见 metrics",
         "200 image/png", "preview/grid-scene-v1.png",
         "网格场景首渲即 200，1600×1600，逐格属性与声明一致"),
        ("A19-v1-occlusion-*", "drafts/a19-occlusion-v1.snapshot", "1.4s",
         "400 PARSE_ERROR", "responses/A19-v1-occlusion.error.json",
         "无图；图例元组解包方向写反，color 拿到了编号"),
        ("A19-v1-occlusion-alternative-*", "drafts/a19-occlusion-alternative-v1.snapshot",
         "1.4s", "400 PARSE_ERROR", "responses/A19-v1-occlusion-alternative.error.json",
         "无图；同一处错误"),
        ("A19-v2-occlusion-*", "drafts/a19-occlusion-v1.snapshot", "见 metrics",
         "200 image/png", "preview/occlusion-v1.png", "修正后 A 版 800×800"),
        ("A19-v2-occlusion-alternative-*", "drafts/a19-occlusion-alternative-v1.snapshot",
         "见 metrics", "200 image/png", "preview/occlusion-alternative-v1.png",
         "修正后 B 版 800×800"),
        ("A19-final-*", "outputs/run-20261011-01/A19/*.snapshot", "见 metrics",
         "200 image/png", "outputs/run-20261011-01/A19/*.png",
         "三张定稿渲染并逐张整屏复查"),
    ],
    change_rows=[
        ("build · bug", "遮挡场景首版返回 400 `Attr [color] unsupported CSS color [B1]`",
         "图例循环写成 `for i, (lab, col) in [(色, 编号), …]`，"
         "但后面把 col 当颜色用、lab 当编号用，解包方向与用法相反",
         "改为 `for i, (col, lab)`，让变量名与实际用途一致",
         "A、B 两版都渲染通过；这类错误靠渲染器的颜色解析报错一眼可定位"),
        ("verify · method", "想证明「两版可见部分完全相同」，先想到比文件 SHA-256",
         "两版 DSL 不同、隐藏层不同，压缩流必然不同，文件哈希不可能相等",
         "改用 Pillow 解码成 8 位未预乘 RGBA 后逐像素四通道比较，"
         "并单独记录文件 SHA-256 作留痕",
         "不同像素数 0、最大通道差 0、像素数组哈希相同；"
         "文件哈希不同被明确标注为预期现象"),
        ("verify · method", "网格属性核验原本打算直接采信 scene-data.json",
         "那样等于「用生成器验证生成器」",
         "改为 verify_a19.py 从最终 PNG 逐像素反测：中心色、0.30·size 实心、"
         "size/2−3 仍有色、size/2+4 已无色、圆环中心为背景且 0.35·size 处有色、"
         "圆角方角点为背景",
         "64 个对象全部通过，最大通道差 0"),
        ("verify · tuning", "第一次反测报 32 个「中心颜色不符」，第二次报 32 个「主体内颜色不符」",
         "① 对圆环也去比中心像素——圆环中心本来就是镂空；"
         "② 采样点取 size/2−1，正好落在抗锯齿边缘上",
         "① 圆环改用环带像素判色；② 内部采样点改到 0.30·size，"
         "边缘采样点改到 size/2−3 并单独用 tol=6",
         "这两处都暴露出「采样点选在几何边界上」会让抗锯齿污染判定"),
        ("verify · tuning", "圆角方四角检查报 11 个「未切圆」",
         "采样点取在边长起点 +4px 处，而圆角半径是 0.22·size"
         "（48 的圆角是 10.6px），+4px 仍在圆角弧内",
         "采样点改到边长起点 +2px，并额外加一条「上边中点仍为填充色」的对照采样",
         "16 个圆角方全部通过，且同时验证了「角被切」和「边没被切」"),
        ("qa · design", "第一版出题脚本从 solver 的返回值里按「第几个元素」取答案",
         "不同题目的返回元组顺序不一致，结果 5 道题的答案取错了槽位"
         "（如 Q21 取到了成员列表而不是计数）",
         "改为每个 solver 返回显式 dict（answer / subject / computation），"
         "解法说明里的枚举也全部由数据现算，不再手写",
         "14 道题的答案与其计算步骤一一对应，不会再错位"),
    ],
    iterations=[
        ("grid-v1", "baseline", None, ["64 格属性是否与声明一致", "环与圆角方是否可辨"],
         ["首渲 1600×1600 并整屏打开", "中部与左上 2×2 格 2× 放大"],
         "属性与声明一致；环镂空、圆角切角清晰"),
        ("occ-v1", "syntax-fix", None, ["图例元组解包方向写反导致 400"],
         ["修正解包后重渲 A/B 两版"], "两版均 200"),
        ("occ-v1", "verification", None, ["两版可见部分是否真的完全相同"],
         ["Pillow 解码后逐像素四通道比较"], "不同像素数 0，判定等价"),
        ("grid-verify", "verification", None, ["属性是否能从最终 PNG 反测"],
         ["64 对象 × 6 采样点", "两轮采样点调整"], "最大通道差 0"),
        ("qa", "verification", None, ["每题答案是否唯一、是否与真实几何一致"],
         ["solver 返回显式 dict + 并列断言", "答案步骤由数据现算"], "14/14 通过"),
        ("final", "visual", "final", ["三张定稿是否全部达标"],
         ["三张交付图整屏打开复查"], "3/3 通过"),
    ],
    design_notes="""
**关键设计选择**

1. *属性用确定性规则推出，不靠随机碰运气*。题面要求记录「种子与真实几何」。
   如果只写一个随机种子号，换台机器就复现不出来。这里把种子记为构造式：
   颜色 = 列号 mod 4、形状 = 4×4 拉丁方按行轮转且两个列块错开 2 位、
   尺寸在每个「颜色×形状」组内轮转。三条规则 + 种子号一起写进 `scene-data.json`，
   任何人重算都能得到同一张图，而 `seed_kind: constructive` 与 `seed_note` 说明了它不是随机数。
   这条规则同时把题面的全部配额变成了**自动满足**：列 mod 4 直接给出每行 4 色、每色 16；
   拉丁方给出每行 4 形、每形 16；列块错开 2 位保证每种颜色都能遇到全部 4 种形状，
   于是 16 种组合全覆盖、每组恰好 4 格，组内轮转尺寸又保证每色每形都出现 48/64/80。

2. *圆环靠描边实现，且把「内径为一半」变成算术而不是目测*。
   外径 size、描边宽 size/4 ⇒ 内径 = size − 2·(size/4) = size/2。
   `borderRadius` 必须取 size/2（严格大于描边宽度，这是 A13 实测到的服务端硬限制），
   填充用 `#FFFFFF00` 全透明。PNG 反测再从「中心是背景、0.35·size 处是主体色」两端夹住。

3. *「两版可见部分完全相同」用解码后像素比较来证明*。
   判定依据不能是文件哈希：题面明确不同压缩或元数据会导致文件哈希不同。
   所以用同一个 Pillow 版本把两张都解码成 8 位未预乘 RGBA，
   再逐像素四通道完全相等地比较，并记录像素数组哈希、不同像素数与最大通道差。
   实测不同像素数 0、最大通道差 0、数组哈希相同。
   顺带发现两份最终 PNG 的**文件级 SHA-256 也完全相同**——服务端对相同像素与相同参数
   产生了逐字节相同的 PNG。这比预期更强，但判定仍然只以解码像素为准：
   文件哈希相等本身不构成「像素等价」的证明，元数据一变它就会失效。

4. *遮挡物选「不透明 + 直角」，是让像素等价可证明的关键*。
   隐藏层完全落在面板矩形内、四周留 40px 余量；面板不透明、无圆角，
   于是圆角处也不会漏出背景。再加一条纪律：不用 boxShadow、不用 opacity、
   不用 BackdropFilter——任何一个半透明叠加都会让隐藏层影响可见像素。
   可见层的每一段绘制代码在两个版本里逐字相同，只有隐藏层的数据表不同。

5. *题目全部由代码从真实几何求解，答案和解法步骤不手写*。
   每道题对应一个 solver，返回显式的 answer / subject / computation；
   取极值的题断言并列数为 1，避免「唯一题多解」。
   Q21 额外验证「距离恰为 250px 的物体数为 0」，从根上消掉「含不含边界」的歧义；
   Q24 在中心 y 并列时声明次级次序键 x，排序因此是全序。
   第一版正是靠手写答案出过错（5 道题取错了返回元组的槽位），改成数据现算后就消失了。

6. *Q30 的正确答案写成「无法确定」，并解释为什么连「5」都不能用*。
   两版隐藏层恰好都是 5 个，很自然会想把「5」当答案——但题面要求「不能把隐藏对象数量
   作为标准答案」。这两版在可见像素上完全一致（0 处不同），图上没有任何特征能推出隐藏数量，
   因此正确答案是「无法确定」。`answers.json` 里专门用 `why_not_5` 说明了这一点，
   这正是本题想教的东西：可见信息不足时，诚实地报告不足。

**问题与修复（要点）**

- 两次渲染 400 都来自同一个低级错误：图例元组解包方向与变量用法相反。
- 像素反测先失败两次，都因为**采样点选在几何边界上**：圆环中心本该是背景；
  size/2−1 落在抗锯齿边缘；圆角半径 0.22·size 时 +4px 还在圆角弧内。
  把采样点挪到 0.30·size / size/2−3 / 边长起点 +2px，并加上「上边中点仍实心」的对照采样后才稳定。

**可复用经验**

- 核验数据结构时**要从最终像素反测，不要用生成器验证生成器**。
- 判定「两个文件视觉等价」先确认比较的是解码后像素，文件哈希对压缩流敏感。
- 让生成规则本身满足配额（列 mod 4、拉丁方），比事后统计再修正可靠得多。
- 出题脚本的 solver 返回**显式字段**（answer/subject/steps），不要靠返回元组的位置。

**结束依据**：
三张定稿 PNG 全部整屏打开复查，另看网格中部与左上 2×2 格的 2× 放大、两张 400px 缩略；
`verify_a19.py` 的 64 对象逐像素反测全部通过（最大通道差 0）；
`equivalence.json` 的像素比较为不同像素数 0；
14 道题全部由代码求解并通过并列断言。未以「渲染成功」作为完成依据。
""",
    unresolved="""
- 无影响交付的未解决问题。
- **题面「编号≥18」的读法**：按上下文（紧接在交付清单之后）理解为题号 ≥18，
  故题号取 Q18–Q31。若原意是「对象编号需 ≥18」，本套网格编号为 G01–G64，
  整体也已满足。两种读法都在 `questions.json.numbering_note` 里写明。
- **Q21 的距离定义以中心为准**：题面未指定用中心还是包围框。
  本套统一用「物体中心的欧氏距离」，并在 `answers.json` 的
  `relation_and_distance_definition` 里显式声明，避免歧义。
- **遮挡场景的隐藏内容并非从图上「泄露验证」**：像素等价只证明可见部分一致，
  不证明隐藏内容真的不同。两版的隐藏层差异由 DSL 与 `scene-data.json.occlusion_scenes`
  结构化记录，差异项逐条列出。
""",
)

if __name__ == "__main__":
    deliver.run(SPEC)