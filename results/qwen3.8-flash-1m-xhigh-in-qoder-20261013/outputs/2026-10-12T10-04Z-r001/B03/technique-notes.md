# B03 · technique-notes — 十件作品的独到手法、依据、证据与边界

约定：每件列"独到手法 / 文档依据 / 试验与看图证据 / 应用价值 / 已确认边界"。
所有请求 ID 可在 `tmp/2026-10-12T10-04Z-r001/B03/requests.jsonl` 逐条查到；
所有结论只声称渲染结果被实际验证过的部分。

---

## case-01 门诊候诊屏（1600×900，`B03-case01-v3`）

- **独到手法**：玻璃面板下面真的画出"科室色带 + 超大首字母水印 + 39px 栅格线"三层，
  `BackdropFilter sigma=16` 把三层一起糊成柔和色块，于是**色相留下、细节消失**：
  患者仍能按颜色认区，但水印不再与真实叫号数字抢读。数字画在玻璃之上，锐度不受影响。
- **文档依据**：`widget_painting_backdrop-filter.txt`（需 imageFilter/sigma，官方建议
  配 ClipRect/ClipRRect 限定区域）；`reference_parser-tags.txt` 装饰段（boxShadow、
  backgroundBlendMode、clipBehavior）。
- **试验与看图证据**：`B03-probe2-blur2` 棋盘 9 次跳变→玻璃下 0 次；
  `B03-p6-bottom-only` 与 `B03-p6-clipped-backdrop` 证明未裁剪时半透明被压平；
  `B03-p4-shadowscan` 证明 `boxShadow="6 8 14 #00000066"` 为真实方向性投影
  （卡下采样 180→248 连续衰减）；`B03-p2-textab` 证明 tnum 改变数字前进宽度。
  看图：`case01-v1/v2/v3` + `zoom-c01-header.png`、`zoom-c01-card.png`。
- **应用价值**：同一套玻璃层级可直接搬到车站/银行/政务大厅；数字全部 tnum，
  30 秒刷新时不会左右跳动。
- **已确认边界**：毛玻璃在纯平底色上完全无效（`B03-p2-filter2` 采样＝纸色），
  所以底纹必须真实绘制，文件因此 387 KB；未裁剪的 BackdropFilter 会毁掉半透明层。

## case-02 城市电网一日负荷轮（1200×1420，`B03-case02-v4`）

- **独到手法**：把 24 小时做成真正的日轮，最外层 SWEEP 渐变**就是昼夜**——色标按
  `p = 1/4 + h/24` 排布，正午在正上方、子正在正下方；往里依次是光伏环（donut 扇形半径＝
  出力/日内最大）、负荷条、碳强度折线、时刻刻度；RADIAL+REPEAT 只作纹理并压到 05/15 透明。
- **文档依据**：`reference_parser-tags.txt` 渐变表（SWEEP 用 start/endAngle；
  不同类型专用参数不可混用）；`reference_enums.txt` GradientTileMode。
- **试验与看图证据**：`B03-probe-sweep` 四方向采样确认 0 弧度在 3 点钟、顺时针；
  `B03-case02-v1` 报 `gradientRadius is not supported by this gradient type`；
  反算 8 个时刻环色回读：00 时精确命中 #0B3954，06/21 时偏差 55–69 →
  证明**色标之间按线性光插值**，sRGB 手算中点偏暗；`B03-p4-radialtile*` 四模式对比。
  看图 `case02-v1b…v4`。
- **应用价值**：晨会投影片只需换数据数组，角度映射与色标顺序自动保持；
  昼夜环同时充当"时间刻度"，减少一层标注。
- **已确认边界**：SWEEP 不接受 radius/center；LINEAR 平铺不可见，故同心场只能用 RADIAL；
  方形画布放不下标题带，改竖幅（已记入 work_plan.change_log）。

## case-03 黄昏港两色网印试印张（1000×1400，`B03-case03-v7`）

- **独到手法**：A 面是 45° 点阵上的**黑点**，整棵子树用 `ColorFiltered SRC_ATOP` 一次染成
  藏青（"一版墨色＝一个滤镜"）；B 面只有两个元素——日轮与水面波光的透明朱墨，
  `backgroundBlendMode="MULTIPLY"` 让它真正叠印在 A 上，于是画面只可能出现四个值，
  与网印物理一致；船体用 ClipPath 实色剪影压回主体。
- **文档依据**：`widget_painting_color-filtered.txt`（作用于子树绘制边界、
  混合模式语义由 Skia 定义）；`reference_parser-tags.txt` 的 backgroundBlendMode。
- **试验与看图证据**：`B03-p2-filter2` SRC_ATOP 染字为 #FF5500；
  `B03-probe-nodes4000` → 4096 元素上限，迫使网点从 14px 定为 20px（1 506 点＝3 149 元素）；
  `B03-case03-v1` 报 `renderBox.parentData must be StackParentData`（Positioned 嵌在
  ColorFiltered 内）；叠印预测 #171311 vs 实测最深像素 #171618；
  色调面积回读：纸 23.9% / A 35.2% / 边缘与朱染 40.7% / 满压 0.1%。
  看图 `case03-v1…v7`。
- **应用价值**：客户能直接从图上判断墨序与闪干；四阶色梯就是可交付的色彩上限。
- **已确认边界**：两版满版网点在该画幅下不可能；B 面是 90% 透明墨，
  所以"纯 B"面积接近 0，色梯改标"满墨/满压"并注明，不伪造暗部。

## case-04 云脊纵走路书海报（900×1300，`B03-case04-v5`）

- **独到手法**：标题的**基线**就是它宣传的那条山脊。19 个 (km, m) 采样经 Catmull-Rom
  生成 115 点曲线与累计弧长表，每字按弧长定位、旋转角取该点切线、并沿法线抬起
  `h/2 − 0.26·size` 使基线贴线；脊顶处弧长松弛（≤400 轮 ×3px）直到旋转矩形互不相交。
- **文档依据**：`widget_layout_transform.txt`（matrix 列主序 + alignment 必填）；
  `reference_parser-tags.txt` textShadow 格式。
- **试验与看图证据**：`B03-origin*` 确认 origin 只接受 `"(x,y)"`；
  `B03-case04-v1` 报 path 解析失败（`M 0 96 860` 一条命令多坐标）；
  轴对齐盒检测在陡坡必然误报 → 改分离轴测试（`obb_hit`）；
  反向子路径山口孔在该处落在山脊线之上、读作浮板 → 撤掉并保留结论。
  看图 `case04-v1…v5`。
- **应用价值**：换路线只需替换 profile 数组；同一函数还生成刻度与标注位置。
- **已确认边界**：服务不提供文本度量，字距靠 em 模型 + 1.14 粗体余量估算，
  再用 OBB 断言与看图兜底；中点符号"·"在斜切后读作杂点，故标题去分隔符。

## case-05 《潮汐》凸版诗句页（820×1280，`B03-case05-v2`）

- **独到手法**：压痕用**两条零模糊硬边**阴影表达（左上白高光 + 右下暗部），全页同一方向；
  行距倍率用同四行并列两栏对照；"其三·终"前的红线是 `WidgetSpan` 排在基线上的行内规则；
  页脚缩进用 `Raw` 段保留。
- **文档依据**：`reference_parser-tags.txt` 文本段（textShadow 逗号分隔多条、
  fontFeatures 空白分隔、height/letterSpacing/wordSpacing）；
  `widget_text_widget-span.txt`（alignment/baseline 语义）。
- **试验与看图证据**：`B03-p2-textab` 红影 1 426 px、双影蓝 729 px、letterSpacing
  160→202、wordSpacing 167→195；`B03-p4-lineheight` 证明 height 只在换行后改变行距
  22→53 px；`B03-p4-decorun` 基线盒 (132,113)–(151,132)；`B03-p8-rawstyle` 证明 Raw
  不继承字号；`B03-p4-smallcaps` smcp 0 像素变化故不用。
  回读渲染：三空格间隙 29/30 px vs 单空格 11–13 px → 缩进真实存在
  （`zoom-c05-title.png`、`zoom-c05-raw.png`）。
- **应用价值**：客户按图选压痕深浅与行距；行号 tnum 保证 01…08 成列。
- **已确认边界**：纸张凹陷与材质无法由 DSL 呈现，只表达压痕方向；
  `border 1 SOLID` 配 `radius=0` 会被服务判 500，故 hairline 边框不给圆角。

## case-06 ZK-14 钻孔柱状图（960×2000，`B03-case06-v3`）

- **独到手法**：岩芯**漏失井段是真孔**——同一条 ClipPath 内用逆时针内环把层带挖通到纸面，
  而不是画白色矩形；岩性花纹（点/横线/砖缝/三角/溶隙/碎屑）画在同一层的裁剪内，绝不跨层。
- **文档依据**：`widget_painting_clip-path.txt` 与 `reference_parser-tags.txt`
  （解析器忽略 fillType、保持非零环绕）。
- **试验与看图证据**：内环与外框同向时像素回读 (185,168,143)＝层色（孔未打通）；
  改反向环后同一坐标回读 (246,243,236)＝纸色，三处漏失全部通过；
  砾石三角第一版路径写成绝对坐标 → 被本地盒子裁光；
  Stack 全 Positioned 子节点 → `Layout size is infinite`。
  看图 `case06-v1…v3` + `zoom-c06-upper.png`。
- **应用价值**：报告附图可直量校核（50 px/m 由 assert 锁定），
  采取率 <80% 的层自动标红，与数据字段一致。
- **已确认边界**：岩芯照片与回次表无法由 DSL 生成，只画数据可支撑的部分。

## case-07 织纹组织卡（1180×730，`B03-case07-v5`）

- **独到手法**：整张 24×24 组织图＝**一条 ClipPath 的数百个子路径**（1 个元素），
  布面由同一矩阵按浮长线分色；下方纱截面纹理才用 `RADIAL + gradientTileMode`
  并排 CLAMP/REPEAT/MIRROR 三种模式，让"平铺"在唯一能成立的地方被看见。
- **文档依据**：`reference_parser-tags.txt` 渐变表（TileMode 四值、radius>0）；
  ClipPath 多子路径。
- **试验与看图证据**：`B03-p2-tile2` 证明 LINEAR 平铺不可见 → 布面放弃 tile 改几何分色；
  `B03-p4-radialtile*` 给出 1/5/3/1 环的实测差异；
  4096 上限（`B03-probe-nodes4000`）使逐格 Container 方案（4 401 元素）被守卫拦下；
  **像素回读校验** `case07_check.py`：4 块布面 × 576 格 = 2 304 格 0 处不一致
  （`case07-verify.json`）。看图 `case07-v1…v5`。
- **应用价值**：学生可自己改 lift 函数生成新组织，卡片自证图与布一致。
- **已确认边界**：纱线捻向阴影不画；平铺不参与组织定义（卡上已写明）。

## case-08 AED 覆盖复盘板（1600×1000，`B03-case08-v5`）

- **独到手法**：泰尔森单元由**半平面交计算**得到（Sutherland–Hodgman 逐条垂直平分线裁剪
  图框），因此 Σ单元面积必须等于图框面积；单元文字压在自绘白色底板上以保证对比度。
- **文档依据**：ClipPath 多边形；`reference_enums.txt` BoxShape=CIRCLE 用于等时圈。
- **试验与看图证据**：断言 `abs(Σ面积 − 图框面积) < 1.0` 实测 887 960 = 887 960（0 残差）；
  Container 的 border 随自身矩形被裁剪、**不会**沿 ClipPath 轮廓描边（v1 边界完全不见）
  → 改逐边 `line`；面积换算曾写成 ÷MPP² 导致"0.00 km²/台"→ 修正为 ×MPP²；
  8 处单元底色与正文墨色 ratio > 4.5 全部通过。看图 `case08-v1…v5`。
- **应用价值**：规划者可以质疑速度假设但无法质疑几何；每单元面积/顶点数可复核。
- **已确认边界**：图面是直线距离而非路网可达域（图上与页脚都写明）；
  8 分钟按步行 5 km/h（车速口径会让圆环大于图幅，已记入 change_log）。

## case-09 城市夜航播客头图（1200×400，`B03-case09-v2`）

- **独到手法**：2 498 个半调圆盘写进**一条** ClipPath（1 个元素）绕开 4096 上限；
  同一组塔楼高度复制三份、只用 `Opacity` 0.42/0.72/1.0 拉开景深；
  窗灯由 `(ci·7 + ri·13 + x) % 5` 的确定性规则点亮。
- **文档依据**：`reference_parser-tags.txt` Opacity 作用于整棵子树；path 弧段 `a`。
- **试验与看图证据**：SWEEP 落日画成硬楔形（`B03-case09-v1` 看图）→ 改双层 RADIAL 光晕；
  缩略校核：交付图不变，另存 240×80 与 120×40 副本，标题区亮度标准差
  79.6 / 62.6、极差 0–235 → 列表尺寸仍可辨（`thumb-c09-240.png`）。
- **应用价值**：换期数/换比例尺直接复用；密度与景深都是函数参数。
- **已确认边界**：400px 高画幅容不下第二信息层，统计压成一条角标；
  景深不靠渐变遮罩伪造。

## case-10 站台预变形地贴（1000×1000，`B03-case10-v6`）

- **独到手法**：承认 **2D 仿射表达不了射影**，于是逐字用最小二乘拟合一个仿射
  （6 参数 × 7 字）去逼近该字四角的精确射影目标，并把最大残差印在图上。
- **文档依据**：`widget_layout_transform.txt`（matrix 列主序、alignment 必填、
  origin 仅 `"(x,y)"`）。
- **试验与看图证据**：整句共用仿射残差 38–61 mm（不可接受）→ 逐字拟合后 4.6 mm；
  `Positioned width/height="1"` 把字压成 1×1 → 面板全空（`B03-case10-v1` 看图）；
  ClipPath 的 path 在子节点自身坐标系内，用绝对坐标导致校验面板为空 → 局部化；
  角点 x 单调断言防止翻转。看图 `case10-v1…v6`。
- **应用价值**：制作厂拿到的是可打印形状 + 公差；改观察距离即重算，
  残差自动提示"逐字仿射"是否仍然够用。
- **已确认边界**：不是精确射影变形；校验面板放大 2.5× 已在图上注明，避免误读实尺。

---

## 边界总表（本套后续题目应遵守）

| 边界 | 处置 |
|---|---|
| 文档 ≤4096 元素 | `bkit.Sheet.elements()` + `finish()` 抛错；程序化构图改为单路径多子形状 |
| BackdropFilter 必须裁剪 | `bkit.Sheet.glass()` 内部强制 ClipRRect/ClipPath |
| border 宽 > borderRadius → 500 | `bkit.rect()` 抛错 |
| Stack 子节点全 Positioned → 无限布局 | `bkit.finish()` 始终插入带尺寸背景 Container |
| Positioned 只能直接挂在 Stack 下 | 滤镜/裁剪节点内不写 Positioned |
| LINEAR 平铺不可见 | 平铺只用于 RADIAL；需要图案重复时改几何 |
| smcp 无效 / tnum 有效 | 数字一律 tnum 或 MONO，不用小型大写 |
| 普通 Text 与 U+3000 都被 trim | 需要空格时用 `Raw`（且自带 fontSize） |
| Emoji 只能行内、dataUri 需完整前缀 | 行内图标用 `Text>Emoji dataUri=…`，不作独立节点 |
| 渐变色标间为线性光插值 | 只在色标位置给硬色彩承诺，中点用回读校验 |
