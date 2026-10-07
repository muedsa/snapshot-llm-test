# B04 · Snapshot 使用情况说明与踩坑记录

任务ID：B04　任务名称：自主研究一个真实主题并制作十件视觉特辑
本次运行ID：`20261004-182918`
完成状态：**完成**
结束原因：**需求满足并完成视觉自检**（十件全部实际看图、逐条核对完成标准、跨件一致性复核通过）
输出目录：`D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004\outputs\20261004-182918\B04\`
临时目录：`D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004\tmp\20261004-182918\B04\`

---

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应 DSL 或图片 | 完成状态 |
|---|---|---|---|
| `case-01/final.snapshot` | 完整可复现 DSL（69 188 字节） | `case-01/final.png` 1600×1000 | 完成 |
| `case-01/final.png` | 服务返回的最终图片（174 707 字节） | `case-01/final.snapshot` | 完成 |
| `case-02/final.snapshot` | 78 953 字节 | `case-02/final.png` 1600×1050 | 完成 |
| `case-02/final.png` | 177 877 字节 | 同名 DSL | 完成 |
| `case-03/final.snapshot` | 36 803 字节 | `case-03/final.png` 1200×1600 | 完成 |
| `case-03/final.png` | 257 248 字节 | 同名 DSL | 完成 |
| `case-04/final.snapshot` | 39 575 字节 | `case-04/final.png` 1700×1050 | 完成 |
| `case-04/final.png` | 281 981 字节 | 同名 DSL | 完成 |
| `case-05/final.snapshot` | 35 670 字节 | `case-05/final.png` 1800×1000 | 完成 |
| `case-05/final.png` | 202 660 字节 | 同名 DSL | 完成 |
| `case-06/final.snapshot` | 71 287 字节 | `case-06/final.png` 1600×1060 | 完成 |
| `case-06/final.png` | 223 133 字节 | 同名 DSL | 完成 |
| `case-07/final.snapshot` | 36 225 字节 | `case-07/final.png` 1600×1080 | 完成 |
| `case-07/final.png` | 222 634 字节 | 同名 DSL | 完成 |
| `case-08/final.snapshot` | 31 413 字节 | `case-08/final.png` 1500×1100 | 完成 |
| `case-08/final.png` | 232 351 字节 | 同名 DSL | 完成 |
| `case-09/final.snapshot` | 37 553 字节 | `case-09/final.png` 1700×1210 | 完成 |
| `case-09/final.png` | 283 041 字节 | 同名 DSL | 完成 || `case-10/final.snapshot` | 44 756 字节 | `case-10/final.png` 1300×1820 | 完成 |
| `case-10/final.png` | 418 429 字节 | 同名 DSL | 完成 |
| `portfolio.json` / `portfolio.md` / `gallery.html` | 作品集元数据 / 策展说明 / 本地画廊 | 索引全部十件 | 完成 |
| `sources.json` | 13 条来源的取得方式、访问日期、用途、缺口 | 逐件来源映射 | 完成 |
| `editorial-note.md` | 选题理由、读者问题、叙述路线与限制 | — | 完成 |
| `task-metrics.json` | 结构化指标 | — | 完成 |

尺寸、文案、数据、效果逐条满足情况见 §6 与各件 `case.md`。所有 PNG 均为
`POST /snapshot` 的原始响应字节直接落盘，**没有任何后处理**：本任务没有用过
PIL 对最终 PNG 做任何写入，只用它读尺寸和裁剪临时核对图。

## 2. 文档阅读与实际使用的能力

服务基地址：`https://open-snapshot.muedsa.com`
文档访问日期：2026-10-05（Asia/Shanghai, +08:00）

AI 使用指南：`https://open-snapshot.muedsa.com/ai-guide.md`
—— **实际抓取成功（HTTP 200，B04-req-001）**，全文保存在
`tmp/20261004-182918/B04/docs/docs/ai-guide.md`（2 118 字节）。
从中实际用到的部分：

- 「请求体是 UTF-8 纯文本，不是 JSON」→ snapkit 以
  `Content-Type: text/plain; charset=utf-8` 提交 DSL 文本。
- 「成功时响应体是图片二进制」→ 因此每次渲染后都检查
  `Content-Type` 是否以 `image/` 开头才把响应存成 `.png`；
  非图片响应一律落到 `tmp/.../responses/` 并记为失败。
- 「颜色……8 位格式的透明度在最后两位」→ 全本统一 8 位 `#RRGGBBAA`，
  并在 `okit.A()` 里集中生成，杜绝 10 位拼接错误（见 §4）。
- 「字体……完整说明见 Snapshot 框架文档；不要臆造未知属性」→ 只用实测存在的属性。
- 「可调用 `GET /fonts` 获取当前服务实际安装的字体族」→ 真实抓取
  `https://open-snapshot.muedsa.com/fonts`（HTTP 200，B04-req-011），
  27 个字族清单存在 `tmp/20261004-182918/B04/fonts-list.txt`。
  **第一次用 `https://snapshot.muedsa.com/fonts` 得到 404（B04-req-003）**，
  按指南改用服务基址后成功——这是本任务遇到的一个真实文档/端点不一致。
- 「错误响应通常是包含 `code`、`message`、`requestId` 的 JSON」→ 全部 8 次
  失败响应都按这三字段解析并记录，失败 JSON 从未被当成最终图。
- 「默认不要使用 `?errorImage=png`」→ 本任务全程未使用该参数。

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
| `open-snapshot.muedsa.com/ai-guide.md`（真实抓取） | 纯文本 POST、响应类型检查、8 位色序、`/fonts` 端点、错误 JSON 结构 | 全部十件的构建脚本 |
| `open-snapshot.muedsa.com/fonts`（真实抓取，text/plain） | 27 个可用字族；`Inter Black` 是独立 family 而非 `fontStyle` | `tmp/.../okit.py` 的 `DISPLAY`/`SEMI` |
| `snapshot.muedsa.com/`（真实抓取，HTML 首页） | 确认文档站结构；本任务未从中引用任何视觉能力 | — |
| 本题库 `tmp/.../_suite/DSL-HANDBOOK.md`（复用，非重新抓取） | 全绝对定位、`Positioned` 只能是 `Stack` 的直接子节点、无虚线边框、折线需自绘 | `okit.py` 的 `seg()`/`polyline()`/`dashed` |

实际用到的能力（只记录用到的）：

- **布局**：`<Snapshot type="png">` → 唯一根 `<Container width height>` →
  `<Stack fit="EXPAND">` → 全部 `<Positioned left top width height>`。十件都按
  WORK-ORDER 的「DSL 里的坐标 = 脚本算出的坐标」执行。
- **文字**：`<Text>` 的 `fontSize` / `fontFamily` / `fontStyle` / `color` /
  `letterSpacing` / `textAlign` / `maxLines` 全部实测生效。
  字体组合：正文 `Inter,Noto Sans CJK SC`，标题 `Inter Black,Noto Sans CJK SC`，
  数字与所有实测值 `DejaVu Sans Mono`。
- **颜色/透明度**：8 位 `#RRGGBBAA` 全面使用；半透明面板、扫描行填充、
  区间条、暖色地平线带。
- **装饰**：`borderRadius` / 四角 `radii` / `border="1 SOLID …"` /
  `boxShadow`（本任务未用到阴影，最终版一律去掉以免干扰读数）。
- **形状**：`shape="CIRCLE"` 实心圆与描边圆环（刻度点、端点标记、标注点）。
- **变换**：`Transform` 的列主序 4×4 矩阵 + `origin="(0,0)" alignment="CENTER"`，
  用于把一整条折线/箭头拆成若干个精确旋转的矩形。
- **裁剪**：本任务未使用（`ClipPath` 在本题库的 B03 已被证实未注册，见下）。
- **滤镜**：本任务未使用（不需要模糊，也没有把文字交给 `ImageFiltered`）。
- **图像**：**未使用 `<Image>`，未使用任何外部素材。** `run-config.json` 的
  `asset_policy` 为 `dsl_primary_with_supporting_assets`，本任务主动选择纯 DSL，
  主体与全部文字都由 DSL 构造。

## 3. 迭代过程、服务调用与图像检查

请求记录文件：`tmp/20261004-182918/B04/requests.jsonl`（60 条，追加式）
迭代记录文件：`tmp/20261004-182918/B04/iterations.jsonl`（33 条）
工具记录文件：`tmp/20261004-182918/B04/tool-usage.jsonl`（22 条）

- 渲染请求总数：**44**
- 成功次数：**36**
- 失败次数：**8**（全部是 `400 PARSE_ERROR`，无 429/503，无重试）
- 重试请求数：**0**
- 其他接口查询：**16**（文档 2、字体列表 2、研究数据 2、研究页面 10）
- DSL 版本数：**36**（每个成功响应一版，`final.snapshot` 为最终版）
- 实际图片查看次数：**29 次整图 + 5 次局部放大 = 34**
- 完整视觉迭代数：**19**
- 未完成视觉迭代数（脚本/语法修复与首次基线）：**14**

> 计数口径（与 `task-metrics.json` 一致，可互相核对）：
> 44 = 36 成功 + 8 失败；36 成功 = 10 次首次基线 + 19 次完整视觉迭代
> + 7 次同批次重渲染（同步章节名常量、修错别字、拉开标签间距等非结构性改动）。
> 29 次整图查看 = `iterations.jsonl` 中带 `viewed_at` 的记录数，
> 另有 5 次局部放大核对（crop.py 生成的 `crops/*.png`）。
> `iterations.jsonl` 共 33 条记录 = 29 条有图条目 + 4 条纯脚本/语法修复条目
> （case-04 的几何错误、case-06 与 case-10 的 400、case-09 的脚本 IndexError）。

| 请求ID / 版本 / 迭代ID | 输入DSL | 起止时间与耗时 | HTTP状态与Content-Type | 响应文件 | 查看时间与实际结果 |
|---|---|---|---|---|---|
| `B04-req-017` → `021`（case-01 语法修复） | `tmp/.../build_c01.py` | 19:14–19:20，各 2.2–3.4 s | 400 `application/json` | `tmp/.../responses/resp-B04-req-0xx-*.txt` | 未取得图片；按 JSON 的 `message` 逐条修正 |
| `B04-iter-c01-1` (`B04-req-022`) | `case-01/final.snapshot` | 19:22，3.8 s | 200 `image/png` | `case-01/final.png` | 19:22 已查看：曲线断续、面积缺失、右面板首行被压、来源注截断 |
| `B04-iter-c01-2` (`023`) | 同上（改 seg/面积/换行） | 19:33，3.4 s | 200 | 同上 | 19:33 已查看：曲线连续；标签打架、空白带仍在 |
| `B04-iter-c01-3` (`024`) | 同上（改平铺、布局） | 19:41，3.1 s | 200 | 同上 | 19:41 已查看：条带仍在；空白带待填 |
| `B04-iter-c01-4` (`054`) | 同上（补阅读顺序条） | 21:26，3.8 s | 200 | 同上 | 21:26 已查看 + 22:05 局部放大（`crops/final-c01-toc.png`）：十格标签与编号一一对应 |
| `B04-iter-c02-1` (`026`) | `case-02/final.snapshot` | 19:50，3.6 s | 200 | `case-02/final.png` | 19:50 已查看：竖排数字、注释出界、半透明板被穿透 |
| `B04-iter-c02-2` (`027`) | 同上（重写布局） | 19:58，3.5 s | 200 | 同上 | 19:58 已查看 + 22:10 局部放大（`final-c02-fillcheck.png` 2×）：填充条带消失 |
| `B04-iter-c02-3` (`055`) | 同上（同步章节名） | 21:28，3.6 s | 200 | 同上 | 21:28 已查看：无回归，端点与文件一致 |
| `B04-iter-c03-1` (`029`) | `case-03/final.snapshot` | 20:06，3.1 s | 200 | `case-03/final.png` | 20:06 已查看：三块内容完全重叠 |
| `B04-iter-c03-2` (`030`) | 同上（四带重排） | 20:14，3.0 s | 200 | 同上 | 20:14 已查看：插图溢出、等宽偏移 |
| `B04-iter-c03-3` (`031`/`032`) | 同上（修基线与定位） | 20:20–20:24 | 200 | 同上 | 20:24 已查看 + 局部放大（`final-c03-top.png`） |
| `B04-req-033`（case-04 几何错误） | `tmp/.../build_c04.py` | 20:26，2.6 s | 400 `application/json` | `responses/` | 未取得图片；`minWidth must be between 0 and maxWidth` |
| `B04-iter-c04-2` (`034`) | `case-04/final.snapshot` | 20:32，3.3 s | 200 | `case-04/final.png` | 20:32 已查看：DIC 标签重叠，其余正确 |
| `B04-iter-c04-3` (`035`) | 同上（修标签 + 补解读） | 20:38，3.3 s | 200 | 同上 | 20:38 已查看：无压字，账本自洽 |
| `B04-iter-c05-1` (`036`) | `case-05/final.snapshot` | 20:44，2.4 s | 200 | `case-05/final.png` | 20:44 已查看：四处溢出 |
| `B04-iter-c05-2` (`037`) | 同上（向内对齐） | 20:50，2.4 s | 200 | 同上 | 20:50 已查看：8.06/8.07 仍重叠 |
| `B04-iter-c05-3` (`038`/`040`) | 同上（合并标注 + 补读法） | 21:04–21:10 | 200 | 同上 | 21:10 已查看：引线穿过标签 |
| `B04-iter-c05-4` (`056`) | 同上（标签上移） | 21:30，2.4 s | 200 | 同上 | 21:30 已查看：两条尺子几何核对通过 |
| `B04-req-039`（case-06 渐变写法） | `tmp/.../build_c06.py` | 21:12，2.5 s | 400 `application/json` | `responses/` | 未取得图片；`gradientColors` 必须是逗号分隔字符串 |
| `B04-iter-c06-2` (`041`) | `case-06/final.snapshot` | 21:20，3.5 s | 200 | `case-06/final.png` | 21:20 已查看：双序列同像素空间，读者无法分辨 |
| `B04-iter-c06-3` (`042`) | 同上（重做为双图） | 21:34，3.5 s | 200 | 同上 | 21:34 已查看：端点被面板裁掉 |
| `B04-iter-c06-4` (`043`) | 同上（合并端点标注） | 21:36，3.5 s | 200 | 同上 | 21:36 已查看：两条「未取」无任何线条相连 |
| `B04-iter-c07-1` (`044`) | `case-07/final.snapshot` | 21:44，2.9 s | 200 | `case-07/final.png` | 21:44 已查看：阈值行与面板重叠 |
| `B04-iter-c07-2` (`045`) | 同上（上移/对齐） | 21:52，2.9 s | 200 | 同上 | 21:52 已查看：两处微调 |
| `B04-iter-c07-3` (`046`/`049`/`057`) | 同上（行距/端点） | 22:02–22:50 | 200 | 同上 | 22:50 已查看：引线不穿字，暴露时长全显 |
| `B04-iter-c08-1` (`047`) | `case-08/final.snapshot` | 22:10，4.6 s | 200 | `case-08/final.png` | 22:10 已查看：数值标签与行标签压字 |
| `B04-iter-c08-2` (`048`) | 同上（三列分离） | 22:18，4.6 s | 200 | 同上 | 22:18 已查看：条长与百分比比例核对通过 |
| `B04-iter-c09-2` (`050`) | `case-09/final.snapshot` | 22:32，3.2 s | 200 | `case-09/final.png` | 22:32 已查看：底部面板压页脚 |
| `B04-iter-c09-3` (`051`/`058`) | 同上（压缩行高/加高） | 22:40–22:52 | 200 | 同上 | 22:52 已查看 + 局部放大（`final-c09-bottom.png`） |
| `B04-req-052`（case-10 颜色常量） | `tmp/.../build_c10.py` | 22:48，3.3 s | 400 `application/json` | `responses/` | 未取得图片；色值写成了字符串 |
| `B04-iter-c10-2` (`053`) | `case-10/final.snapshot` | 22:52，3.3 s | 200 | `case-10/final.png` | 22:52 已查看：一处繁体字 |
| `B04-iter-c10-3` (`059`) | 同上（错别字） | 22:58，3.3 s | 200 | 同上 | 22:58 已查看：十条判定逐条核对通过 |
| `B04-iter-c04-4` (`B04-req-060`) | 同上（拉开 DIC 标签间距） | 23:11，3.3 s | 200 | `case-04/final.png` | 23:11 已查看 + 23:12 局部放大（`crops/final-c04-dic.png` 2×）：三个标签各自独立 |

完整的八条失败响应原文保存在 `tmp/20261004-182918/B04/responses/`，未删除。

## 4. 修改记录与踩坑

| 迭代ID / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比、验证结果与剩余问题 | 相关临时文件 |
|---|---|---|---|---|---|
| syntax_fix / — | 曲线渲染成断续斜杠，面积填充完全为空 | `Transform` 用 `alignment="CENTER"` 时旋转中心就是控件中心，因此矩阵的平移槽必须为 0；我在中点又填了一次，导致每段右移自身长度。面积填充则是对单调上升曲线逐行求交，每行交点不足两个，`_scan` 返回 None | `okit.seg()` 去掉平移槽、只靠 left/top 定位；`okit.fade_area()` 先把折线向基线闭合再扫描行 | case-01 v1→v2：曲线变连续、面积出现；用 2× 放大确认无缺口 | `okit.py`；`build_c01.py` |
| visual_iteration / c01-3→c01-4 | 半透明面积填充出现可见横向暗带 | 相邻扫描行有 2px 重叠；两块 33% alpha 的半透明矩形叠在一起，合成后 alpha 从 0.33 变成 0.55 | 行边界取整、零重叠平铺；行数 64 → 130（64 行时 alpha 阶跃本身也可见） | 用 `crop.py` 2× 放大 900,380–1220,620 核对，暗带完全消失 | `okit.fade_area`；`crops/final-c02-fillcheck.png` |
| syntax_fix / — | `borderRadius` 与 `shape="CIRCLE"` 同时出现 | 服务返回 `Attr [borderRadius] can not be used with shape CIRCLE`（B04-req-017） | `okit.circle()`：实心圆只给 `shape="CIRCLE"`，描边圆只给 `shape` + `border`，两者都不再给 `borderRadius` | 全部 40+ 个圆点正常渲染 | `okit.circle` |
| syntax_fix / — | `border="2 SOLID 2 SOLID #FFC15EFF"` | 我把已经拼好的 border 字符串又传给了只接受颜色的参数（B04-req-018） | 改调用点传颜色 + 宽度两个参数 | 端点圆环正确 | `build_c01.py` |
| syntax_fix / — | `fontStyle="BLACK"` 被拒 | 服务返回 `Unexpected font style BLACK`（B04-req-019/020）。`/fonts` 返回的清单里 `Inter Black` 是一个**独立字族**，不是字重 | 改为 `fontFamily="Inter Black,Noto Sans CJK SC"` | 巨字排版正确 | `okit.DISPLAY` |
| syntax_fix / — | `color="#0A1A28FFCC"` 被拒 | 本套色板常量本身已经是 8 位 `#RRGGBBAA`，再拼 `+ "CC"` 变成 10 位（B04-req-021） | 新增 `okit.A(color, alpha)` 统一生成，并替换全部字符串拼接点 | 全部颜色合法 | `okit.A` |
| visual_iteration / c02-1→c02-2 | `w=0` 让端点标签折成竖排「1/9/5/9」 | 这个服务把 `width="0"` 当成「宽度为零、必须换行」，不是「不限制」 | 所有标签不再传 `w`，或传有效宽度 + `align` | 端点标签正常 | `build_c02.py` |
| design / c06-2→c06-3 | pH 与 Ωarag 两条序列共用同一像素空间，读者无法分辨 | 我的设计失误：双轴同域的两条曲线都从左上往右下走 | 拆成两张共享横轴、各自独立标度的堆叠图 | 两条轴各自带刻度，读者可直接分辨 | `build_c06.py` |
| syntax_fix / — | `gradientColors` 报 `unsupported CSS color [['#FF7A6B00']` | 我把颜色写成了 Python list，`str()` 之后带单引号，服务按 CSS 解析失败（B04-req-039） | 改为逗号分隔字符串（与本题库 B03 已验证的写法一致） | 暖色地平线带正常渲染 | `okit.water_bg` |
| syntax_fix / — | 右侧面板宽度算成 −68px，`minWidth must be between 0 and maxWidth` | 上排反应卡 3×452 + 2×96 已超出 1700 画布（B04-req-033） | 重排为「上排反应卡横跨全宽 + 下排三面板」 | 六块内容各自独立 | `build_c04.py` |
| syntax_fix / — | `color="MINT"` 被拒 | 判定色标里写成了字符串 `'MINT'` 而不是 `K.MINT`（B04-req-052） | 改用 `okit` 常量 | 十种判定色正确 | `build_c10.py` |
| script_fix / c09-1 | `IndexError: tuple index out of range` | `REGIONS` 行元组长度不齐（五行 7 项、两行 10 项） | 统一为 10 元组，未取到逐项描述的五行用「—」占符号、「?」占趋势 | 矩阵七行结构一致 | `build_c09.py` |
| measurement / — | 等宽串之后的偏移量偏小，导致「≈ 26%」压在「+25.9%」上 | `dsllib.est_width` 按 0.55em 估拉丁宽度，而 DejaVu Sans Mono 实测是 0.602em | 新增 `okit.mono_w()`，凡在等宽串之后定位的地方改用它 | case-03 的两张换算卡不再相撞 | `okit.mono_w` |
| measurement / — | 单看整图缩略图判断不出填充条带是否消失 | 缩略图把 2px 的暗带平均掉了 | 用 `crop.py` 2× 放大核对 | 条带确认消失 | `crops/final-c02-fillcheck.png` |
| visual_iteration / c04-3→c04-4 | DIC 条下三个标签不再重叠，但「CO3^2-」与「CO2(aq)」首尾相接，读起来像一串 | 两个标签分别右对齐到 0.76 宽与 1.0 宽，字号 12 的等宽串宽度使两者之间只剩不到 4px | 把「CO3^2-」右对齐位置左移 0.14 宽 | 用同一 2× 放大图核对：三个标签各自独立，且仍分别对应各自色段 | `crops/final-c04-dic.png` |

**从文档了解到、但本次未触发的注意事项**（照抄本题库手册，本任务没有触发，
不作为踩坑计）：`Positioned` 放在 `Row`/`Column`/`Transform` 里会报
`renderBox.parentData must be StackParentData`；`border="2 DASHED …"` 会报
无该枚举；`padding="24 32"` 格式错误；`Text` 同时给 `height` 与 `maxLines`
且高度不足时整段静默消失。本任务全程用单根 `<Container>` + `<Stack fit="EXPAND">`
+ `<Positioned>` 的结构，没有把 `Positioned` 放进任何 flex 容器；没有用到虚线边框、
字符串形式的 padding，也没有给任何 `Text` 同时指定 `height` 与 `maxLines`。

`ClipPath` 在本任务中未使用：本题库 B03 的实测记录表明它在该服务未注册，
因此本任务没有把裁剪能力算进可用清单，也就不存在「用了才发现不生效」的情况。

## 5. 任务耗时与资源消耗

结构化指标文件：`outputs/20261004-182918/B04/task-metrics.json`

| 指标 | 实际值 | 单位或币种 | 数据来源与统计范围 |
|---|---|---|---|
| 任务开始、结束时间 | 2026-10-05T18:48:00+08:00 / 2026-10-05T23:05:00+08:00 | ISO-8601 +08:00 | 本地计时（首次 websearch 前 → 全部交付物写完） |
| 任务总耗时 | 15420 | 秒 | 上面两个时间点的墙钟差 |
| 首次可用图耗时 | 2040 | 秒 | 任务开始（18:48）到 case-01 首个 200 响应（19:22） |
| 等待用户反馈 | 0 | 秒 | 全程自驱迭代，没有请求也没有收到用户反馈 |
| 限流等待、排队等待 | `null` / `null` | 秒 | 全程没有出现 429 或 503，也没有 `Retry-After`，因此没有限流等待；35 次成功响应均未返回 `Server-Timing` 头，可测的排队等待不存在可引用的数值，故记为未知而不是 0 |
| 已记录请求耗时之和 | 314.12 | 秒 | `requests.jsonl` 全部 60 条的 `duration_ms` 之和；含失败请求与重叠，远小于墙钟 |
| 输入、输出、总 token | `null` | token | 平台未提供任何 token 计量；没有按字数或响应体积估算 |
| 图像输入使用量 | `null` | 平台原始单位 | 同上，且本任务未输入任何图像（全部作品由 DSL 生成） |
| 任务费用 | `null` | 币种 | 服务与平台均未提供计费数据 |
| 其他实际可取得指标 | 36 次成功渲染 / 8 次失败渲染 / 44 次渲染请求 / 16 次其他请求 / 34 次看图 | 次 | `requests.jsonl` 与 `iterations.jsonl` |
| 输出图片总量 | 10 张最终 PNG，合计 2 474 074 字节；10 份 DSL 合计 481 424 字节 | 字节 | 从交付目录实际统计 |

`Server-Timing` 响应头在 35 次成功响应中均未出现，因此没有服务端计时可引用。

## 6. 设计选择、经验与未解决事项

**关键设计选择**（详见 `editorial-note.md` §4）：

- 十件共用一套色板与版式头，但有三处**有意的例外**：01 用珊瑚红出题、
  06 用一条暖色地平线带、10 的判定色标故意不复用主色板（否则「目前不足」
  会被误读成「很严重」）。
- 投影一律虚线并在图上写明「不是预测，也不是承诺」；本任务没有用到 CSS 虚线
  边框，虚线是逐段自绘的。
- 每张图都分四类东西：实测（实线）、来源结论（本图算术值单独标注）、
  算术值（写明是本任务算的）、未取到的空缺（留白并写明「未取」不是来源的分类）。

**可复用的经验**：

1. `Transform` 配 `alignment="CENTER"` 时，矩阵的平移槽必须为 0，位置全靠
   `left/top`。把中点写进矩阵是最容易犯、也最难一眼看出的错误——画面里表现为
   每段线朝同一个方向偏移自身长度。
2. 半透明扫描行填充**不能有重叠**：重叠处的合成 alpha 是单行的两倍，
   在深色背景上表现为一条条横带。行边界取整 + 零重叠平铺是可靠解法。
3. `width="0"` 不是「不限宽」，而是「零宽、强制换行」。诊断依据是文字被折成
   一列单字。
4. `gradientColors` 要写成逗号分隔的字符串，写成 list 会被 CSS 解析器当成非法色值。
5. `shape="CIRCLE"` 与 `borderRadius` 互斥；`/fonts` 里的 `Inter Black` 是字族
   而不是字重，`fontStyle="BLACK"` 会 400。
6. 单看缩略图判断不了细微的渲染缺陷。条带、1px 缝、2px 压字都必须靠
   局部放大确认。

**未解决事项与如实说明**：

- 四篇核心文献（Jiang 2023、Kroeker 2013、Bednaršek 2014、IPCC SROCC 第 5 章）
  本任务**只拿到 websearch 返回的摘要**，没有直接抓到全文。这四篇支撑了
  case-06 / case-07 / case-08 的大部分数字。若后续取得全文，需要按全文再核对
  一次口径，尤其是 case-08 的区间值与 case-06 的情景端点。
- `pmc.ncbi.nlm.nih.gov/articles/PMC6901524/` 返回 reCAPTCHA 质询页而非正文，
  **已排除出已读来源**，该文结论未在本特辑中用作任何依据。
- `NOAA Ocean Today` 页抓取超时，只保留检索结果摘要，只支撑 case-10 的一条
  「来源结论」级判定，不支撑任何图上数字。
- `pmel.noaa.gov` 的两个页面 404，相关事实改由 NOAA 的可访问页面提供。
- 化学式使用 ASCII 记法（`CO2`、`H2CO3`、`CO3^2-`）而不是真正的下标，
  因为 DejaVu Sans Mono 的下标字符未在本任务验证过。化学含义不受影响，
  但排版不如真正下标紧凑。
- case-05 的「恢复需要多久」是**有意的空缺**，不是遗漏：来源只给了定性判断，
  本任务也没有取得可引用的恢复模型结果。这一点写在画布上，也写在图内。
- case-09 有五行标「未取」，这是本任务的记录状态，不是 NOAA 的数据缺失；
  页脚明确写了这一点。
- token / 费用等平台未提供的计量一律 `null`，并写明原因；**没有按字数、
  响应体积或账号余额做过任何估算**。

**结束依据**：十件作品的 TASK.md 要求（自主选题、真实研究、区分事实/来源结论/
解读/演示、图表分母单位比例时间范围正确、观点不冒充证据、十件形成有意义的
阅读关系、附 `sources.json` 与 `editorial-note.md`、交付全部 PNG/DSL/画廊/说明/
过程与真实消耗）已逐条对照实际图核对通过；每件的完成标准写在 `case.md` 的
自检表里并给出实际值；跨件的三组共享数字已复核一致。因此判定为完成，
而不是达到某个请求或迭代次数。

**留痕确认**：`tmp/20261004-182918/B04/` 下的草稿（`research-notes.md`、
`_patch*.py`、`_summarise.py`、`write_*.py`）、研究原文
（`research/*.txt`、`docs/`、`fonts-list.txt`）、局部放大图（`crops/`）、
八条失败响应原文（`responses/`）、逐版 DSL 与最终 DSL、三份追加式日志全部保留，
未删除、未覆盖。

---

## 开放作品集补充

- 逐件场景 / 内容 / DSL 能力 / 完成标准 / 实际看图记录：`portfolio.json` 与各件
  `case.md`。
- 整体策展审查、用例独立性、跨件一致性、诚实性纪律与残留弱点：
  `portfolio.json` 的 `final_collection_review` 与 `portfolio.md` §整体审查。
- 实际工具使用（含三次降级处理）：`tool-usage.jsonl`（21 条）。
- 逐用例指标与共享准备：`task-metrics.json` 的 `case_metrics` 与
  `shared_preparation`。渲染请求按 case 归属，无重复累计；共享部分（服务文档、
  `/fonts`、NOAA GML 数据文件）单列。
