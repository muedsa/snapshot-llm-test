# B03 · 作品画廊

用十件作品探索DSL的创意边界

- 状态：`completed`　独立完整作品：10 件　规定下限：10 件
- 全部 PNG 都是 `POST https://open-snapshot.muedsa.com/snapshot` 的**原始响应字节**，
  无本地绘图与后处理；每件都配一份可复现的同名 `.snapshot`。
- 链接相对本文件所在的任务输出目录。
- 逐件展示，不是接触表。

## 策展说明

这十件不是十个题材，而是十次「把一个视觉主张压到只剩一种手段」的实验。case-01 让渐变去编码潮位而不是当底色；case-03 让影子深度等于嵌套层数；case-06 让模糊只作用在背景上、读数保持像素锐利；case-07 用逐通道乘法算出减色叠印的算术并把「C×M 必须等于 M×C」当成可证伪的判据；case-08 让两个半透明组相交处自己变深，从而模拟 GIS 的复合风险；case-09 让一行内标签、一段有缩进的代码、一个斜杠零各自落在它该在的位置上；case-10 让 12 根柱子真的是 12 个 Expanded、让方位角轴真的是一条 SWEEP 渐变。十件里有三件是彻底的反例记录：case-02 的倒角描边做不到、case-05 的 ClipPath 根本没注册、case-09 的行高属性会让整段文字空白 —— 这三条被写进了作品本身，而不是被藏进备注。技术笔记（technique-notes.md）逐件记录了探针图、真实响应与从 PNG 上读回的像素证据。

## 目录

- [`case-01` · 潮汐与风 · 澄澳灯桩海岸观测站值班板](#case-01)
- [`case-02` · 边缘语言 · 云吞巷票券与会员卡印刷规格稿](#case-02)
- [`case-03` · 拣选层级 · 华东三仓 E3 手持终端](#case-03)
- [`case-04` · 舞台透视 · 《夜航》选座预览](#case-04)
- [`case-05` · 三种取景 · 屿东 07 海洋浮标观测卡](#case-05)
- [`case-06` · 起降简报 · 临川 LKC 起飞天气](#case-06)
- [`case-07` · 叠印配方单 · 四色](#case-07)
- [`case-08` · 淹没深度分级 · 青屿河断面 K12+400](#case-08)
- [`case-09` · 版本说明 · anvilplot 3.14.0 发行单页](#case-09)
- [`case-10` · 日照剖面研究墙 · 青屿书院实验楼](#case-10)

---

## case-01 · 潮汐与风 · 澄澳灯桩海岸观测站值班板

![B03 case-01 潮汐与风 · 澄澳灯桩海岸观测站值班板](case-01/final.png)

- 作品：`case-01`　说明：[`case.md`](case-01/case.md)
- 场景：暗色值班大屏，每 10 分钟刷新一次　受众：常开 1600×1000 横屏的值班员（暗值班室，70 cm），以及每天早上交接班的海洋观测组长
- 视觉意图：渐变承担编码：潮位柱「顶透明→底实」的高度、水深 8 级同一色相的 alpha、月面逐行 Lambert 明暗（晨昏线由 R(1−2k) 半椭圆解析填充，不是画一个偏移圆）
- 原图：[`final.png`](case-01/final.png)　DSL：[`final.snapshot`](case-01/final.snapshot)
- 尺寸 1600 × 1000　PNG 198.3 KB　DSL 119.6 KB　DSL 元素 1394 / 4096

## case-02 · 边缘语言 · 云吞巷票券与会员卡印刷规格稿

![B03 case-02 边缘语言 · 云吞巷票券与会员卡印刷规格稿](case-02/final.png)

- 作品：`case-02`　说明：[`case.md`](case-02/case.md)
- 场景：要真的送去印厂的对版稿，A3 纸按 90 mm 取餐牌等比放大后阅读　受众：虚构商户「云吞巷」的老板，以及接单的印厂（文盛印务）制版师傅
- 视觉意图：把印刷知识做成可执行规格：每种边缘配方一个样例 + 尺寸标注
- 原图：[`final.png`](case-02/final.png)　DSL：[`final.snapshot`](case-02/final.snapshot)
- 尺寸 1600 × 1010　PNG 222.3 KB　DSL 25.7 KB　DSL 元素 316 / 4096

## case-03 · 拣选层级 · 华东三仓 E3 手持终端

![B03 case-03 拣选层级 · 华东三仓 E3 手持终端](case-03/final.png)

- 作品：`case-03`　说明：[`case.md`](case-03/case.md)
- 场景：货架前站姿，50–70 cm，无鼠标，触控目标必须 ≥76 px　受众：戴手套、单手操作、强光下的拣货员，1440×1024 加固终端
- 视觉意图：影子深度 = 嵌套层数，成为真正的信息编码而不是装饰
- 原图：[`final.png`](case-03/final.png)　DSL：[`final.snapshot`](case-03/final.snapshot)
- 尺寸 1440 × 1024　PNG 185.8 KB　DSL 27.4 KB　DSL 元素 341 / 4096

## case-04 · 舞台透视 · 《夜航》选座预览

![B03 case-04 舞台透视 · 《夜航》选座预览](case-04/final.png)

- 作品：`case-04`　说明：[`case.md`](case-04/case.md)
- 场景：明亮办公室，鼠标可滚动可缩放（这里只交付静态帧）　受众：在选座流程第二步的购票观众，桌面浏览器 1500×1100
- 视觉意图：同一份针孔投影几何在 5 个尺寸的盒子里复用 + 5 种不同矩阵，因此座位数/票价/选中座位不可能对不上
- 原图：[`final.png`](case-04/final.png)　DSL：[`final.snapshot`](case-04/final.snapshot)
- 尺寸 1500 × 1100　PNG 223.3 KB　DSL 49.8 KB　DSL 元素 646 / 4096

## case-05 · 三种取景 · 屿东 07 海洋浮标观测卡

![B03 case-05 三种取景 · 屿东 07 海洋浮标观测卡](case-05/final.png)

- 作品：`case-05`　说明：[`case.md`](case-05/case.md)
- 场景：桌面 1600×1060，值班室双屏　受众：运维工程师（看整幅谱）与值班研究员（看圆形镜头）
- 视觉意图：三种取景调用同一个 energy()，所以全景/镜头/缩略图的数值必然一致
- 原图：[`final.png`](case-05/final.png)　DSL：[`final.snapshot`](case-05/final.snapshot)
- 尺寸 1600 × 1060　PNG 220.7 KB　DSL 236.1 KB　DSL 元素 3402 / 4096

## case-06 · 起降简报 · 临川 LKC 起飞天气

![B03 case-06 起降简报 · 临川 LKC 起飞天气](case-06/final.png)

- 作品：`case-06`　说明：[`case.md`](case-06/case.md)
- 场景：值班室，60 cm，需要眯眼看清数字的每个字符　受众：虚构机场起飞口的签派员，值班台第二块 1400×1000 屏
- 视觉意图：背景先放进 ImageFiltered，再把 BackdropFilter 作为后面的兄弟盖上去，文字另画
- 原图：[`final.png`](case-06/final.png)　DSL：[`final.snapshot`](case-06/final.snapshot)
- 尺寸 1400 × 1000　PNG 265.7 KB　DSL 35.5 KB　DSL 元素 494 / 4096

## case-07 · 叠印配方单 · 四色

![B03 case-07 叠印配方单 · 四色](case-07/final.png)

- 作品：`case-07`　说明：[`case.md`](case-07/case.md)
- 场景：印厂控制室，屏幕上并排对比色块，色差 1 px 都要看得出来　受众：虚构印厂「文盛印务」的机长（看叠印梯与矩阵）与调墨工（看墨量与叠印顺序）
- 视觉意图：每块色都是「下版纯色 × 上版纯色」的一次真实乘法；C×M 与 M×C 渲染相同，这正是减色叠印该有的对称性
- 原图：[`final.png`](case-07/final.png)　DSL：[`final.snapshot`](case-07/final.snapshot)
- 尺寸 1600 × 1120　PNG 182.0 KB　DSL 51.4 KB　DSL 元素 714 / 4096

## case-08 · 淹没深度分级 · 青屿河断面 K12+400

![B03 case-08 淹没深度分级 · 青屿河断面 K12+400](case-08/final.png)

- 作品：`case-08`　说明：[`case.md`](case-08/case.md)
- 场景：A3 打印 + 屏幕投影，最远看 2 m，所以关键数字 ≥11 px　受众：防汛办值班调度（看断面）与每周例会拿这张纸的社区网格员（看分级→处置）
- 视觉意图：两个 Opacity 组相交处自然加深，和真实 GIS 的复合风险渲染一致
- 原图：[`final.png`](case-08/final.png)　DSL：[`final.snapshot`](case-08/final.snapshot)
- 尺寸 1500 × 1050　PNG 173.6 KB　DSL 38.8 KB　DSL 元素 507 / 4096

## case-09 · 版本说明 · anvilplot 3.14.0 发行单页

![B03 case-09 版本说明 · anvilplot 3.14.0 发行单页](case-09/final.png)

- 作品：`case-09`　说明：[`case.md`](case-09/case.md)
- 场景：项目主页 + 可打印 A3 单页，100% 尺寸阅读，最小字号 10 px　受众：准备把依赖从 3.13 升到 3.14 的下游数据工程师，以及维护者本人
- 视觉意图：空心版本号 + 斜杠零是刚需信息编码（版本号里要区分 0 与 O）；行内色标用 WidgetSpan；代码块用 Raw 保缩进
- 原图：[`final.png`](case-09/final.png)　DSL：[`final.snapshot`](case-09/final.snapshot)
- 尺寸 1500 × 1090　PNG 369.8 KB　DSL 33.5 KB　DSL 元素 372 / 4096

## case-10 · 日照剖面研究墙 · 青屿书院实验楼

![B03 case-10 日照剖面研究墙 · 青屿书院实验楼](case-10/final.png)

- 作品：`case-10`　说明：[`case.md`](case-10/case.md)
- 场景：墙面远观 2 m，评审时近看 60 cm　受众：建筑师与报建审图员；钉在工作室墙上的 A1 分析墙 + 评审会屏幕
- 视觉意图：「内容真的需要等分」的地方才用 Flex；SWEEP + gradientStops 把冬至白昼窗口直接刷到方位角轴上
- 原图：[`final.png`](case-10/final.png)　DSL：[`final.snapshot`](case-10/final.snapshot)
- 尺寸 1600 × 1150　PNG 266.2 KB　DSL 87.5 KB　DSL 元素 1183 / 4096

---

## 整体最终审查 / 完成标准

```json
{
  "reviewed": true,
  "method": "把十张 final.png 用图像查看工具逐张重新打开，做整体审查：确认画幅/配色互不重复（深色值班板、暖白印刷稿、浅色仓储终端、深色选座页、深色观测卡、深色简报、暖白配方单、深色断面、高对比浅底发行单、深色日照墙共九种底色基调）；确认每张都有可复述的核心数字；确认没有一张是「只有标签名和小方块」的能力示范板。",
  "findings_fixed_during_collection_review": [
    "case-04 主视角曾有一处紫色圆点压在舞台条上，无法解释 → 复查 build_c04.py 确认那是探针遗留的选中座位标记在缩略图里的复用坐标，已确认不属于最终画面元素；主视角无残留",
    "case-09 右栏兼容性矩阵最后一列曾越出画布（v3）→ v4 改为独立标签列 + 5 个等宽数据列",
    "case-09 「变更清单」第 12 条曾被摘要带盖住（v3）→ v4 行距 56→50",
    "case-10 剖面曾被压成 12 px 一条线（v2，误把米当像素）→ v3 引入 SCALE=17 px/m",
    "case-10 太阳光线曾压穿右侧进深条标题（v3）→ v4 起点贴边、长度 130→96 px",
    "case-10 月柱高曾算出负数（v1 漏了 degrees()、v2 下界设错）→ v3/v4 修正"
  ],
  "coverage_check": {
    "independent_cases": 10,
    "distinct_lead_capability_families": 10,
    "images_opened_with_viewer": 10,
    "crops_inspected": 8,
    "external_bitmaps_used": 0,
    "images_embedded_via_image_tag": 0
  }
}
```

## 未解决事项（如实）

- case-09：Text 的 height 属性与 strutLeading / strutHeightOverridden 在本服务版本会让整段文字空白，因此「真正的行高控制」做不到，多行文本只能手工分行排布
- case-09：fontFeatures 只有 Inter 的 ss01/ss02 生效，tnum 无效，数字表格无法做到等宽对齐
- case-05：ClipPath 在官方 Widget 列表里存在，但解析器未注册（400 Unknown element tag），任意形状裁剪做不到
- case-10：日照模型只含几何，未做遮挡/反射/透光率；只出三个代表日
- 本服务只出静态 PNG，不提供交互/动画，也不报告 token 与费用，相关计量一律 null

