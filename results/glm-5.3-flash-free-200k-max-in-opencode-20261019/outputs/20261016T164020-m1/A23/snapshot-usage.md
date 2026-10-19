# A23 · snapshot-usage

## 状态
completed。cover.png（1200×800 RGB 深底）+ frame-01..06.png（600×600 透明 RGBA）
七张最终图与同名 .snapshot 全部为服务 200 真实渲染；frame-data.json / timing.json /
limitations.md 就位。所有渲染响应（probe、v1–v5 各轮 7 张）保留在 tmp renders 目录。

## 客户四项需求判定（详见 limitations.md）
1. 文字可编辑 SVG → 服务无 SVG 输出（仅 png/jpg/webp 位图）。替代：封面文字
   依然全部是 DSL `Text`（cover.snapshot 中可编辑），位图交付 + 语义保留。
2. CMYK 印刷稿 → 服务无色彩空间转换。替代：1200×800 RGB PNG 封面（授权）；
   剩余 ICC/印刷转化留给打印端。
3. 6 帧透明 GIF → 服务单帧静态、无 GIF 合成。替代：6 透明 PNG 关键帧 +
   timing.json（250ms/帧、循环 1500ms）+ frame-data.json（含接缝分析），
   供 Pillow/ffmpeg 接力合成；未伪造 .gif。
4. PNG 封面 ✓ 原生支持。

## 能力验证（probe）
- Transform：matrix (cos,sin,0,0,−sin,cos,0,0,…) + origin=(w/2,h/2) 实现"绕自身
  中心的屏幕顺时针旋转"——用 0/30/90/180° 四矩形对比 bounding box 与顶端尖点实测
  （30° 尖点 x≈324 vs 顺时针理论 321.5，非逆时针 278.5）。
- 透明：`<Snapshot type="png">` 不设 background 时返回 RGBA 且空区 alpha=0
  （6 帧透明占比 73–77%）。
- Opacity、borderRadius、DrawCIRCLE（shape=CIRCLE）在同一 DSL 校验可用。

## 设计与迭代
12 单元：U01–U08 矩形风车叶（60×160、圆角 16，4 色×2，终态 r=165，
径向角 −90+45i°，rotation=径向角−90°）；U09–U12 圆点（d=54，45° 相位错开于
叶间 r=48，色与两邻轴叶均异）。t=0 分散：叶 r0=195 ±jit，圆点 r0=268 四角；
缓动 ease-in-out cubic f=[0,1/54,4/27,.5,23/27,53/54]。
四次视觉迭代：v2 点分布/内圈 r、v3 再错点色、v4 点相位 45°、v5 叶长 160+
点 r=48（几何上心点与叶带彻底分离）。终版 F6 为 8 放射花 + 4 心点可识别图形。

## 查看记录
probe NNzoom + pixel audit；v5 contact sheet（6 帧并排）、F6 中心 3× 放大、
cover half + 绿点 80px 窗 pixel 核验。v1..v4 的 sheet/zoom 仅作修复依据
存 tmp steps（v2/v3/v4 半径/色序/相位问题都定位并修复）。

## 未解决事项
无。循环接缝为设计取舍，已按题面要求在 timing.json 与 frame-data.json 中
如实声明非无缝并给逐单元证据；不属于缺陷。
