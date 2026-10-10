# snapshot-usage —— B04 应用记录

- 任务：B04（researched visual special）· 运行：`run-20261002-220723-mimo` · 时区：UTC+08:00
- 交付：10 件独立研究型作品（要求 ≥ 10），10 张最终 PNG + 同名 `.snapshot`
- 日志：`tmp/run-20261002-220723-mimo/B04/` 下 `requests.jsonl` / `iterations.jsonl` /
  `tool-usage.jsonl` / `task-metrics.json`

---

## 一、真实取回并使用的文档

B04 的文档抓取是 `type=documentation` 的 HTTP 请求，逐条带 URL、状态码、字节数、
起止时间与服务端 `request_id` 写入 `requests.jsonl`（15 条 + 1 条 `/fonts`）。

### 1.1 命中并实际用于构造 DSL 的文档

| 文档 | 用途 |
|---|---|
| `https://open-snapshot.muedsa.com/ai-guide.md` | 服务整体约束、根标签、能力边界 |
| `snapshot.muedsa.com` → parser-tags | 元素/属性语法（`Snapshot`、`Container`、`Text`、`TextBlock`、`Shape`…） |
| → painting | 填充、渐变、边框、阴影的书写方式 |
| → enums | 对齐、字重等枚举取值（如 `CENTER_LEFT` 而非 `LEFT_CENTER`） |
| → transform | 变换矩阵的写法与限制 |
| → rendering | 渲染顺序、裁剪与堆叠 |
| → decorated-box | `boxShadow` / `border` 的字符串形态 |
| → source-index | 索引页，用来定位正确地址 |
| → faq | 已知边界与常见报错 |
| `https://open-snapshot.muedsa.com/fonts` | 字体清单，确认 `Noto Sans CJK SC` / `Noto Serif CJK SC` / `Noto Sans Mono CJK SC` / `Inter` / `Inter Black` 可用（共 27 种） |

### 1.2 真实的 404（按原样登记，未掩饰）

早期按猜测地址抓取的 6 个文档页返回 **HTTP 404**（响应体是 SPA shell），
登记为 `B04-doc-02` … `B04-doc-07`，原文字节保留在 `tmp/.../B04/docs/`。
从 `B04-doc-08` 起改用 `snapshot.muedsa.com` 的正确地址，9 条全部 200。
**这 6 条失败计入 `failed_snapshot_requests`，不计入成功数。**

---

## 二、真实应用的研究与工具

### 2.1 一手资料（47 条 `type=research`）

- **数据集**：`Leap_Second.dat`（28 行 TAI−UTC 阶跃）→ 解码为
  `Leap_Second.decoded.txt` → 程序化解析为 `leap-seconds-rows.json`（28 行 / 27 次）。
  二进制小数字段按空白切分后逐位转字符，不手抄。
- **公告**：`bulletinc.dat`（Bulletin C 72，巴黎 2026-07-06，"NO leap second ... at the
  end of December 2026"）。
- **说明页**：IERS 闰秒页（0.9 s 门槛、27 s、2012-06-30 的 61 秒、仅用 6/12 月、
  1820 年平太阳日）、常用常数页（0.2 ms/天、Ω_N）、地球自转页、TAI−UTC 历史表
  （1961–1971 的分数频率调整）。
- **决议**：第 27 届 CGPM 决议 4（2035 年前提高 |UT1−UTC| 上限、可能需要首次负闰秒）
  与决议 5（9 192 631 770 Hz、100 倍、2026 审定 / 2030 通过），含 DOI。
- **规范与注册表**：ITU-R TF.460-6、IANA tzdb、RFC 5905、SI 手册 PDF
  （`si_brochure_1.pdf`，5,199,982 B）。
- **旁证**：NIST / NPL / PTB 时间页、BIPM CGPM 议题页。

**失败请求 14 条全部留档**：Wikipedia（中/英/移动版）、wikiwand、Britannica 403、
USNO、`nist.gov` 根、`datacenter.iers.org` DNS 失败、以及 4 个猜错的路径。
`sources.json.unreachable_attempts` 逐条列出 `request_id / url / http_status / error`。
相关事实一律改由 **BIPM / IERS / hpiers / IANA / ITU / NIST / NPL / PTB / RFC**
一手来源交叉覆盖，**没有一条来源是没访问过就写上去的**。

### 2.2 计算与校验

- `27 = 37 − 10`；`16255 ÷ 26 = 625.19 → 625 天`（首末两行日历差 ÷ 间隔数，望远镜式复核）
- `3567 = 2026-10-07 − 2016-12-31`；`3567 − 2557 = 1010 天 ≈ 2 年 9 个月`
- `9 + 6 + 7 + 2 + 3 + 0 = 27`；`11 + 16 = 27`；`26 年 + 1972 的第 2 次 = 27`
- `0.2 ms/d × 4500 d = 0.9 s`（画面标注为量级演算，并说明 UT1−UTC 并不匀速）
- 表格逐格核对：184 / 365 / 366 / 547 / 2 557 / 1 096 / 1 277 / 1 095 / 550 等
  距上次天数与相邻两行日期差一致；MJD 41499 = 生效首日 1972-07-01 的儒略日。

12 条算术检查以 `AC-01 … AC-12` 写入 `sources.json.arithmetic_checks`，
每条带分子、分母、单位、时间范围、来源编号与 `matches_artwork`。

### 2.3 生成与渲染工具链

| 工具 | 作用 |
|---|---|
| `fetch-b04.ps1` / `fetch-bin-b04.ps1` | 真实 GET 研究/文档/字体，逐条写 `requests.jsonl` |
| `lib-b04.ps1` | `Ts`/`TBlock`/`Card`/`HR`/`VR`/`Kicker`/`Tag`/`Bar*`/`Tick*`/`Strip61`/`Steps`/`Masthead`/`SourceLine`/`Page4` + 调色板 + `Get-LeapRows`/`Get-LeapList` |
| `gen-b04-a/b/c/d.ps1` | 分段生成 10 件完整自包含 DSL（a:01-02 b:03-05 c:06-08 d:09-10） |
| `build-b04.ps1` | 按轮次写 `.snapshot` 并跑 **Fit 越界守卫** |
| `render-b04.ps1` / `render-b04-all.ps1` | `POST /snapshot`，全字段写 `requests.jsonl` |
| `mk-logs-b04.ps1` / `mk-metrics-b04.ps1` / `mk-sources-b04.ps1` / `mk-cases-b04.ps1` / `mk-portfolio-b04.ps1` | 从 JSONL 反查生成迭代、指标、来源、说明与画廊，**避免手写数字** |
| `System.Drawing` | 尺寸/哈希/像素指纹核验；生成唯一字节副本以恢复读图 |

**渲染结果**：21 条 `type=render` 全部 **HTTP 200 image/png**，0 失败、0 条 429，
`ratelimit_remaining` 最低 110，单张 6.6 s → 4.5 s 不等（总计 74.686 s）。

---

## 三、DSL 实际用到的能力

- **根结构**：`<Snapshot type="png" background="...">`，画布尺寸由首个内层
  `Container width height` 决定（根标签不写宽高）。
- **形状**：矩形、圆角矩形、圆、以及 `matrix(...)` 旋转/斜切的矩形——
  十件作品里的**时间轴、阶梯、波形、条形图、年份矩阵、梳齿刻度全部由这些画出**，
  没有位图、没有 `<Image>`、没有外部素材。
- **文本**：`Text` 单行与 `TextBlock` 多行，显式给行高与颜色；
  中文断行手工控制（case-02 的卡片正文就是靠重排行解决行首冒号问题）。
- **裁剪与堆叠**：`Stack` + `ClipPath`（Kotlin-only）实现卡片内的裁剪；
  背景整幅用一次 `BackdropFilter`（每文档至多一个、必须被 `Clip` 直接包裹）。
- **渐变**：自定义对齐只允许 `(-1,0)`；深墨与纸色两套底色由线性渐变铺。
- **边框与阴影**：边框串 `WIDTH SOLID #COLOR`（前缀 `BD`）、阴影用
  `ELEVATION_n` 或 `"dx dy blur spread #color"`；`Circle`/`Circ` 的形参顺序是
  颜色在前、边框在后，**不接受阴影参数**。
- **对齐枚举**：`LEFT_CENTER` 无效，用 `CENTER_LEFT`。
- **已知边界（本任务内验证或复用 B03 结论）**：`Positioned` 只能是 `Stack` 的直接
  子节点；变换矩阵外层括号且不能有空格、16 个浮点按列主序；`SizedOverflowBox`
  的宽度是换行约束；`Stack` 裁剪子节点但从不裁剪 `boxShadow`；`maxLines` 被忽略
  （所以断行必须自己控制）；`ClipPath` 仅 Kotlin 侧可用；滤镜仅高斯模糊。

**Fit 守卫**是本次最有价值的自建能力：`build-b04.ps1` 在写每个 `.snapshot` 时
计算所有文本框底边与卡片边界，**任一超出画布即判失败**。r01 由此抓到
case-09 来源行 `675 > 672` 的越界并当场修正；此后 3 轮构建 **30/30 全部通过**。

---

## 四、视觉迭代（读图 → 改 → 再读图）

**读图 33 次**（10 次 r01 首看 + 23 次 r02/r03 验收与复看），
`iterations.jsonl` 21 行中 **11 行为 `type=visual`**，每行都有
`observation`（读图看到什么）与 `view_evidence`（下一轮读图确认了什么）。

r01 被推翻的六类问题（证明读图不是走形式）：

1. **case-01 / case-07 刻度画成递增高度**——视觉上暗示"秒越走越长"，与事实相反。
   r02 改为 60 个等高灰刻度 + 第 61 个琥珀刻度单独加高。
2. **case-07 的 `23:59:59` 标签与它标注的那一秒相差约 320 px**。r02 删除，
   改为位置正确的 `:00 … :50` 刻度标签。
3. **case-03 TAI 线末端有一块突兀的青色实心矩形**（原拟作箭头）；**UT1 波形由
   离散点构成、呈串珠状**。r02 换成 `→` 字形并改为连续曲线。
4. **case-05 的 `9` 轴标签与标题重叠**；年份矩阵没有行区间标签；图例两个圆点
   同色无法区分。r02 三处全改。
5. **case-06 的 0.1 秒梳齿几乎不可见**，caption 提到的"灰色刻度"在画面上读不出来。
   r02 由 2×2 暗点改为 2×14 可见刻度并加轴线。
6. **case-10 的迷你示意图标签掉到面板外**、压住卡片描边。r02 移入面板内。

文案类修正：case-02 卡片小标题"模型频率固定"语义错误（应为"铯频率固定"）、
正文行首出现全角冒号、case-01 的生造词"闰接日"、`-37 s` 用连字符而非真减号 `−`、
case-04 表格 MJD 列未说明对应哪一天（r03 补"MJD 为生效首日"）。

**case-04 是唯一 3 轮的用例**：r02 终审时发现表头 `MJD` 没说清对应哪一天，
补入口径行后单独重渲染 r03，其余 9 件保持 r02（r03 的 DSL 与 r02 逐字节相同）。

---

## 五、踩坑与应对（可复用经验）

1. **`read` 工具的内容哈希缓存会串图。**
   同内容副本、连续读取会返回错图——最严重时连续四次把 case-06 的图返回成
   case-04。应对手法（两步）：
   - 先用 `System.Drawing` 独立核验 **磁盘字节**：20 张 PNG 的画布尺寸 + SHA1、
     `outputs` 与 `tmp` 的 SHA256 一致性（结果全部 `SAME`），
     证明**问题只在读图通道，不在产物**；
   - 再用 `System.Drawing` 改 **1 个角像素**（通道值 ±1，视觉不可察觉）
     生成唯一字节副本，绕开缓存后逐张读。
   33 次调用中 **21 次取得与目标画稿匹配的正确字节**，12 次串图/重复全部留档为
   失败的工具尝试（`tool-usage.jsonl` 的 `tu-08` / `tu-09`）。
   **识别收到的到底是哪张图，靠画内烘焙的 `NN / 10` 报头 + 画幅比例，不靠路径。**
2. **浏览器通道不可用**：`browser.preview` 返回
   `[browser.disconnected] No desktop browser is connected to this session`。
   不重复尝试（"repeating browser actions while disconnected will not help"），
   改走 `read` + 唯一字节副本（`tu-10`）。
3. **PowerShell 5.1 的大小写不敏感**：`mk-cases-b04.ps1` 里循环变量 `$d`
   与字典 `$D` 是同一个变量，第二次迭代就把字典覆盖成 null，
   第三次报 `Cannot index into a null array`，并且**悄悄写出了一个字段全空的
   case-02**。改名为 `$caseMeta` 并加 `if ($null -eq $caseMeta) { throw }` 后重跑。
   → **教训：字典与循环变量绝不共用大小写不同的名字。**
4. **不要把辅助函数命名为 `H`**：`H` 是 `Get-History` 的别名，调用 `H $x` 会
   触发 `Get-History : Cannot bind parameter 'Id'`。改名 `Esc` 后正常。
   （这与 B03 记录的"绝不把路径存进 `$r`"、"绝不让 `$R`/`$Rdir` 与循环变量 `$r`
   并存"是同一类问题。）
5. **`[char]0xNNNN + [char]0xNNNN` 会被当成整数相加**，不是字符串拼接——
   本任务一律在源文件里直接写 CJK 字面量，避免用码点拼字。
6. **`edit` 工具会剥掉 BOM**：PS 5.1 下含中文的 `.ps1` 每次编辑后必须
   重新写 BOM（`UTF8Encoding($true)`），否则中文按 ASCII 误读、脚本直接语法错。
   本次对 `gen-b04-b.ps1`、`mk-logs-b04.ps1`、`mk-metrics-b04.ps1`、
   `mk-sources-b04.ps1`、`mk-cases-b04.ps1`、`mk-portfolio-b04.ps1` 都做了这一步。
7. **`ConvertTo-Json` 里跨行的数组表达式**：`outputs = (@(...) + @(...))` 在
   哈希字面量内跨行会被解析器认为括号未闭合。拆成循环先算好 `$outputsList`
   再赋值即可。
8. **未把外部研究当素材**：47 条 research 的产物（HTML/PDF/TXT）只用于**引用**，
   一张也没有嵌进画面；B04 的 `external_assets_used = 0`，
   资产政策 `dsl_primary_with_supporting_assets` 在实际执行上退化为 `dsl_only`，
   并在 `task-metrics.json.asset_policy` 中如实声明 `actual` 字段。

---

## 六、总审查

| 检查项 | 结果 |
|---|---|
| 作品数（要求 ≥ 10） | **10**，全部独立自包含 DSL |
| 最终图片数 | **10**，服务返回的原始字节，无后处理 |
| PNG ↔ `.snapshot` 配对 | **10 / 10**，同名同目录 |
| 画幅比例 | **10 种互不重复**：0.40 / 0.71 / 0.73 / 0.75 / 1.00 / 1.33 / 1.78 / 2.30 / 2.50 / 4.00 |
| 逐件实际看图 | **21 次正确读图**覆盖 10 件 × 2–3 轮，全部有 `view_evidence` |
| 真实渲染请求 | **21 条 HTTP 200**，0 失败、0 条 429 |
| 一手来源 | **14 个全部真实访问**，访问记录由 `requests.jsonl` 反查生成 |
| 失败请求留档 | 6 条文档 404 + 14 条研究不可达/超时，全部原样保留 |
| 数据正确性 | 12 条算术检查带分子/分母/单位/时间范围，逐条 `matches_artwork = true` |
| 演示内容标记 | 刊名、期号、编辑部署名带 `DEMO`；编辑计算/解释/建议在画面上分别标注 |
| 日志 | `requests.jsonl` 84 行 · `iterations.jsonl` 21 行 · `tool-usage.jsonl` 11 行 |
| token / 费用 | `null`（平台未提供，不以字数或额度猜造） |

### 遗留事项

1. `requests.jsonl` 中 6 条 `documentation` 404 是猜错地址的真实失败，按原样保留；
   正确文档已由 `B04-doc-08` 起取得。
2. 10 条 `research` 网络失败保留原样；相关事实改由其他一手主机交叉覆盖，
   **未以任何未访问页面充当来源**。
3. 浏览器通道不可用，`browser.preview` 无法看图；已用
   "`read` + System.Drawing 唯一字节副本"恢复逐件看图。
4. token / 图像使用量 / 费用平台未提供，`task-metrics.json` 中相关字段为 `null`，
   并在 `unknown_fields_reason` 写明原因与未来的覆盖方式。
5. case-01 / case-05 / case-08 中"至今 / 当前"的天数以 **2026-10-07** 为基准日，
   此后会过期；来源行已写明抓取日期，重新运行时应更新这三处数字。
