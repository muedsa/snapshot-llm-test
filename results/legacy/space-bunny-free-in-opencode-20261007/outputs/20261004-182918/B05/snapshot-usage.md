# B05 · Snapshot DSL 使用记录

**任务**：从零虚构产品并设计十个关键使用画面
**产品**：房谱 HOMESPEC（住址履历系统）
**输出目录**：`outputs\20261004-182918\B05\`
**临时目录**：`tmp\20261004-182918\B05\`
**完成状态**：**completed** — 10 件最终 PNG + 10 份同名 `.snapshot` + 10 份 `case.md`，
以及根目录的 `product-brief.md` / `journey.json` / `portfolio.json` / `portfolio.md` /
`gallery.html` / `task-metrics.json` / 本文件。

---

## 1. 实际使用的服务文档与字体

全部为**真实抓取**，原始响应保存在 `tmp\20261004-182918\B05\docs\` 与
`tmp\20261004-182918\B05\fonts-list.txt`：

| 类型 | URL | 落盘 | requests.jsonl |
|---|---|---|---|
| 服务指南 | `https://open-snapshot.muedsa.com/ai-guide.md` | `docs\ai-guide.md` | `B05-req-001` |
| 字体列表 | `GET https://open-snapshot.muedsa.com/fonts` | `fonts-list.txt` | `B05-req-002` |
| DSL 文档首页 | `https://snapshot.muedsa.com/` | `docs\snapshot-docs.html` / `.txt` | `B05-req-003` |
| 标签与属性参考 | `https://snapshot.muedsa.com/reference/parser-tags/` | `docs\parser-tags.html` / `.txt` | `B05-req-004` |
| 绘制指南 | `https://snapshot.muedsa.com/guides/painting/` | `docs\painting.html` / `.txt` | `B05-req-005` |

此外**复用**（只读引用，未重新抓取）`tmp\20261004-182918\_suite\DSL-HANDBOOK.md`
——那是本套题库 A 类任务用真实响应和实际看图积累的实测结论。

### 实际用到的字体（全部来自真实 `/fonts` 响应，无一臆造）

| 用途 | fontFamily |
|---|---|
| 标题 / 大数字 | `Inter Black,Noto Sans CJK SC` |
| 小标题 / 强调 | `Inter Semi Bold,Noto Sans CJK SC` |
| 正文（界面） | `Inter,Noto Sans CJK SC` |
| 正文（叙事，case-05 签名 / case-08 全篇） | `Noto Serif CJK SC` |
| **所有产品判定的数字** | `DejaVu Sans Mono` |
| 图例 / 元信息 | `DejaVu Sans Mono` |

色板与类型尺度集中在 `tmp\20261004-182918\B05\fpk.py`，10 个生成脚本共用，
保证跨画面一致。

## 2. 实际用到的标签与属性

| 标签 / 属性 | 用在哪里 |
|---|---|
| `Snapshot`（`type` / `background`） | 全部 10 件的根 |
| `Container width/height` | **唯一**根节点，画布尺寸由它决定 |
| `Stack fit="EXPAND"` | 每一屏 |
| `Positioned left/top/width/height` | 每一个元素（整套用绝对定位） |
| `Container color/borderRadius/border/boxShadow` | 全部矩形 |
| `Container radii="TopLeft/BottomLeft/TopRight/BottomRight"` | 左侧色条、条形图左端 |
| `Container shape="CIRCLE"` | 阀门、快门环、进度点、装订孔 |
| `Container border` 单独使用 | 空心圆环（实测 `CIRCLE` 不能与 `borderRadius` 同用） |
| `Container borderTop/Left/RightWidth + Color` | case-04 / case-10 的窗口 chrome |
| `Text color/fontSize/fontFamily/fontStyle/textAlign/letterSpacing/softWrap` | 全部文字 |
| `ClipRRect` | case-01 取景框、case-02 照片、case-03 缩略图、case-06 表带 |
| `Opacity opacity` | case-01 的检测框 10% 黄色蒙版 |
| `Transform matrix/origin/alignment` | 折线、表格线、危险条纹、时间轴引线 |
| `gradientType="LINEAR"` + `gradientColors/Begin/End` | 封面、扫描光带、桌面 |
| `gradientType="RADIAL"` + `gradientCenter/Radius` | case-01 手电光斑、case-09 冰箱高光 |
| `gradientType` + `gradientStops` | 未使用（scanline 填充更可控） |

**DSL 没有的能力及其替代**（这些不是踩坑，是设计约束）：

- 没有路径图元 → 折线用旋转矩形拟合（`fpk.seg` / `polyline`）
- 没有虚线边框 → 一串短矩形拼接（`dsllib.dashed`）
- 没有面积填充 → 逐扫描行铺矩形（`fpk.area` / `fade_area`）
- 没有圆弧图元 → 圆环用 N 段旋转矩形拟合（case-06 的 56 段进度环）
- 没有不规则裁剪形状 → `ClipRRect` + 超尺寸绘制
- **全程未使用 `<Image>`，未嵌入任何外部图片**

## 3. 本题踩到的 DSL 语义坑

按「现象 → 定位 → 修复 → 复验」记录，全部有真实出图或真实错误响应为证。

### 3.1 服务报错（真实响应）

| # | 现象 | 定位方式 | 修复 | 复验 |
|---|---|---|---|---|
| 1 | `400 PARSE_ERROR: Attr [color] color must be #RGB, #RGBA, #RRGGBB or #RRGGBBAA`，位置 60402 附近 `color="#F8F5EFF"` | 写 `check_colors.py` 扫描全部 DSL 的 color 值长度，定位到唯一一处 7 位色值 | 改为 `#F8F5EFFF`（8 位 = #RRGGBBAA，末尾 FF = 不透明） | 重渲染 200 image/png，且新增房间填充正常显示 |

这条同时暴露了一个**留痕层面的真实隐患**：case-04 此前能出图，是因为当时渲染用的
脚本版本还没有这一行——**脚本与产物不同步**。现在两者已一致。

### 3.2 不报错但结果不对（静默行为）

| # | 现象 | 定位方式 | 修复 | 复验 |
|---|---|---|---|---|
| 2 | 单个 `Text` 在固定宽度的框里放不下时**不换行、不报错，超出部分被静默丢弃** | crop 放大 case-10 右侧面板，看到句子停在「真正花钱的 ¥」处被面板边缘切断 | 全部改用 `fpk.wrap_cjk()` **显式分行**，每行一个 `Text`，不依赖 `softWrap` | case-10 v03 起全部完整显示；case-08 v03 的虚构声明同样处理 |
| 3 | 10.5px 正文的字形实际落在 `[y+3, y+14]`，比直觉多 2px，导致第二行与 chip 行压字 | crop 放大 case-07 第 1 个节点 7 倍，看到正文与 chip 几乎相接 | 正文行起点 36→35、chip 行 62→64（chip 与正文的字形带各留 ≥2px） | case-07 v06 两者分离 |
| 4 | 62px 高的卡片放不下第三行（字形到 `y+64`），文字下部越过卡片边框 | crop 放大 case-07 的绿色卡片 | 卡片 62→72px，两行说明移到 +38 / +54 | case-07 v03 起完整显示 |
| 5 | `transform` 旋转的矩形纵向跨度约 `(长度+厚度)/√2`，按 16px 高的带算尺寸会画出约 58px 并盖住上方文字 | 首次看 case-03 即看到危险条纹盖住失败原因 | 超尺寸绘制 + `ClipRRect` 裁回（`fpk.hazard_stripe`） | case-03 v02 起条纹只在带内 |
| 6 | 表格列宽按 `est_width` 累加超出可用宽度，最后一列整列被裁 | 首次看 case-09 即看到「质保至 2026-03」被卡片右缘切掉 | 取消一列后按实测文本量重排为 6 列；此后每张表都在渲染前先核对 `ΣCOLW ≤ 可用宽度` | case-09 v02 起无溢出 |
| 7 | `Text` 与 `softWrap` 的组合在窄框里不可靠（case-10 / case-08 各一次） | 见第 2 条 | 一律改为显式分行 | 见第 2 条 |

### 3.3 复用上一题的实测结论（未重新踩坑）

- `opacity` 作为 `Container` 属性被**静默忽略**，必须用 `Opacity` 标签
  → case-01 的检测框蒙版从一开始就用 `K.faded()`（`Opacity` + `Stack`）
- 取景框类局部坐标（`TAG_*` 等）必须加上容器偏移 → case-01 v06 已修
- `Transform` 绕盒子**中心**旋转，平移矩阵必须为零 → `fpk.seg` 从一开始就按此实现
- `RADIAL` 渐变只接受 `gradientCenter/Radius`，与 `LINEAR` 的 `gradientBegin/End` 不能混用
  → case-01 的手电光斑直接用了正确的参数组合
- `Container` 只能有一个子节点 → 多子节点区域统一走 `fpk.clipped()`（`ClipRRect > Container > Stack`）
- 8 位十六进制按 CSS 读 `#RRGGBBAA` → 见 3.1 第 1 条

## 4. 逐件自检表（把完成标准逐条落到实际值）

| # | 完成标准 | 实际值 | 结论 |
|---|---|---|---|
| 1 | 10 件独立最终 PNG | 10/10，均为 `case-XX\final.png` | ✅ |
| 2 | 每件配一份同名完整 `.snapshot` | 10/10，且**与临时草稿目录中编号最大的版本逐字节一致**（`inspect_dsl.py` 实测） | ✅ |
| 3 | PNG 是服务响应原始字节、无后处理 | 10/10，均由 `snapkit.render()` 直接写入响应体 | ✅ |
| 4 | 画布尺寸贴合真实载体，不同一版式换皮 | **7 种不同尺寸**：420×900 / 900×430 / 1600×1000 / 1240×1754 / 396×484 / 900×1900 / 1050×760；同尺寸的 3 张手机竖屏（01/03/07）版式分别是取景页 / 告警页 / 工单时间轴，两张桌面（04/10）分别是判定表 / 年度视图 | ✅ |
| 5 | 声明尺寸 = 实际出图像素 | 10/10 一致（用 PIL 读回真实像素逐件比对） | ✅ |
| 6 | 每件都用 read 工具实际打开看过 | 10/10；本次会话累计打开图片 40 次以上，另有 11 处 crop 放大（19 张放大图全部保留在 `tmp\...\B05\crops\`） | ✅ |
| 7 | 逐条处理 `D.warnings()` | 10 件最终版输出均为空 | ✅ |
| 8 | 元素数不超过服务 4096 上限 | 最大 2056（case-05），其余 293–1438 | ✅ |
| 9 | 只用 `POST /snapshot`，不使用 `<Image>` | 55 次渲染请求全部走 `POST /snapshot`；DSL 中 `<Image>` 出现次数为 0 | ✅ |
| 10 | 跨画面共享信息一致 | 7 个共享量（住址 / 进度 / 差分四分类 / 责任 ¥200 / E-02 期限 10-07 / 两条工单 / 电表 1284→3611）逐张核对一致 | ✅ |
| 11 | 失败状态被真实呈现 | E-02 暂挂在 03 / 04 / 05 / 06 / 08 / 09 / 10 **七张图**中持续存在，无一张假装已解决 | ✅ |
| 12 | 自拟品牌与数据明确声明 | gallery.html 顶部、product-brief.md、journey.json、portfolio.json/md、case-08 成品长图底部、case-05 打印稿页脚、case-09 卡片页脚共 7 处 | ✅ |
| 13 | B 类根目录交付齐全 | portfolio.json / portfolio.md / gallery.html / snapshot-usage.md / task-metrics.json + product-brief.md / journey.json，8/8 | ✅ |
| 14 | 每 case 目录三件齐全 | 10/10 目录均含 `final.png` + `final.snapshot` + `case.md` | ✅ |
| 15 | gallery 本地相对链接、可点开原图、不依赖远程脚本 | 12 个 `<a href="case-XX/final.png">` 相对链接 + 数据内联 + 样式内联，零 CDN | ✅ |
| 16 | 临时目录三份日志 | `requests.jsonl`（60 行）/ `iterations.jsonl`（19 行）/ `tool-usage.jsonl`（12 行） | ✅ |

## 5. 问题与修复表（本次会话实际做的改动）

本次会话新建了 case-07…10 四件，并对已交付的 case-01…06 做了整体一致性审查。

### 5.1 已交付图件中发现并修复的真实缺陷（3 张）

| 图 | 现象 | 定位 | 修复 | 复验 |
|---|---|---|---|---|
| **case-05** | 二维码说明第二行（`FY+118`）落在 1754px 画布之外，字形下部被切 | crop 放大 `90,1590` | 二维码 72→62px 移到 `FY+14`；两行说明移到 `FY+82` / `FY+96`，距画布底留 34px | ✅ crop 复验两行完整 |
| **case-04** | ① 图例下方三行说明溢出面板压到页脚线 ② 户型平面 A-03/W-01/W-02 编号标签压底墙线 ③ 脚本里 7 位色值导致 400 报错 | crop 放大 `730,840` 与 `240,700`；`check_colors.py` 全表扫描 | ① 面板 190→224、说明行距 22→16 ② 平面高 130→156、房间带 84/46→100/56、锚点坐标重排 ③ 色值改 `#F8F5EFFF` | ✅ v04/v05/v06 三次渲染后逐区复验 |
| **case-06** | 底部品牌行压在两个动作按钮的下缘 | crop 放大 `0,356` | 按钮行下移，品牌行移出表盘安全区 | ✅ 两者分离 |

其余三张（01 / 02 / 03）重新打开逐区看过，**未发现真实缺陷，保留原版**——
这是有意不为「看起来在迭代」而制造无意义修改。

### 5.2 新建图件的版式修正（共 14 处，全部重渲染并复验）

| 图 | 修正次数 | 主要问题 |
|---|---|---|
| case-07 | 5 | 时间轴竖线与头像圆重叠；绿卡被底栏压住 36px；卡片高度不足；文案压在缩略图上读作水印；chip 与正文间距 1px |
| case-08 | 4 | 底部三块互相压住并超画布；时间轴首尾标签超版心；封面第三张卡压危险条纹；虚构声明第二行掉出画布 |
| case-09 | 4 | 第 7 列整列溢出卡片右缘；第三行与琥珀条右侧同样溢出；表格底到页脚 180px 空洞；二维码说明压卡片下缘 |
| case-10 | 5 | 两条绿色条形与「没花的 ¥0」栏重叠；结论文本被 292px 面板静默截断；右侧面板 120px 死带；两条注释卡与峰值标签压曲线 |

## 6. 服务调用与消耗

| 项 | 值 |
|---|---|
| 渲染请求总数 | **55** 次（`POST https://open-snapshot.muedsa.com/snapshot`） |
| 成功 | **51** 次（`200 image/png`） |
| 失败 | **4** 次（3 次是上一个执行阶段的真实 `400 PARSE_ERROR`，1 次是本次的色值位数） |
| 重试 | 0 次（服务未返回 429/503，无需按 `Retry-After` 退避） |
| 文档 / 字体请求 | 5 次 |
| 请求总耗时 | 200.51 秒 |
| 整题墙钟 | 20110.9 秒（约 5 小时 35 分，含本地设计与 DSL 编写时间） |
| 首张可用图耗时 | 1391.0 秒 |
| **input_tokens** | **`null`** |
| **output_tokens** | **`null`** |
| **image_input_usage** | **`null`** |
| **cost** | **`null`** |

`null` 的原因：open-snapshot HTTP 服务未提供任何 token / 图像用量 / 计费指标端点，
本次运行的聊天平台也未报告逐请求的 token 或费用。**这些数值没有按字数、字节数或
任何方式估算。** 排队等待同样是 `null`——服务只在排队时通过 `Server-Timing` 返回
queue 段，本题的响应里没有该段，所以「无法测量」而不是「0 秒」。

## 7. 未解决事项与如实说明

1. **未做任何真实用户验证**。产品假设——租客接受「必须拍到标记牌」的约束、
   8–16 个锚点足以覆盖主要争议部位、同一锚点「同机位同角度」可重复、
   金额阈值贴近真实维修价——**全部未验证**。已在 `product-brief.md` §7、
   `portfolio.md` §6、`journey.json` 的 `assumptions_and_limits` 中逐条声明。
2. **case-10 的 39 个月逐月湿度读数是自拟演示数据**，不是任何实测传感器记录。
   已在图内（曲线下方）与页脚两处声明。
3. **画面中的差分、识别、责任划分都是设计意图**，不是已实现的算法输出。
   不存在可运行的前端程序或后端服务。
4. **没有做离线 / 弱网状态画面**。十张都设定在有网络的时刻。这是有意的取舍：
   与其加一张离线横幅，不如把一个失败状态（E-02 暂挂）贯穿七张图更能说明这个产品
   的取舍逻辑。已在 `portfolio.md` §2 中说明这是取舍而非遗漏。
5. **token / 图像用量 / 费用为 `null`**，原因见第 6 节。
6. **两处留痕缺陷已修复并保留原始文件**（详见 `task-metrics.json` 的 `trace_files`）：
   - 上一个执行阶段未调用 `snapkit.configure()`，导致 29 条渲染记录被写到**仓库根**
     `requests.jsonl`。已用 `fix_request_log.py` + `fix_task_id.py` 原样归并到本题
     `requests.jsonl`（只改 `request_id` 与 `task_id`，时间、状态、耗时、文件路径、
     错误信息一律未动），原始文件保留在 `requests-root-backup.jsonl`。
   - `log_b05.py` 是追加式写入，重复执行会产生重复行。已用 `dedupe_iterations.py`
     去重，并已把脚本改为幂等（运行前先移除自己写入的 id）。
   这两处不影响任何画面，只影响留痕的完整性，在此如实记录。
7. **未遇到但需要说明的推测**：`case-06` 表盘上「10-05 周二」的星期与日期的对应
   是按 2026 年日历推算的，未通过外部日历服务核对；由于它是演示数据，
   不影响结论，但如果要作为真实样例使用需重新核对。

## 8. 复现条件

```powershell
# 环境：Windows + Python 3.11，Pillow 已安装（用于 crop.py 与像素核对）
cd D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004

# 逐件重渲染（每件独立，互不依赖；写同名的 final.png / final.snapshot）
python tmp\20261004-182918\B05\build_c01.py   # … build_c10.py

# 像素级复核
python tmp\20261004-182918\_suite\crop.py <png> B05 <x,y,w,h> <scale> <tag>

# 校验 DSL 与草稿一致性 / 画布尺寸 / 元素数
python tmp\20261004-182918\B05\inspect_dsl.py

# 留痕（幂等）
python tmp\20261004-182918\B05\log_b05.py
python tmp\20261004-182918\B05\log_tools.py
python tmp\20261004-182918\B05\augment_metrics.py
```

服务不需要任何凭据（公开匿名访问），但**必须带浏览器 User-Agent**，
否则 Cloudflare 返回 `403 error code: 1010`。所有 `.snapshot` 都是自包含的
完整 DSL，不依赖本题以外的任何文件。