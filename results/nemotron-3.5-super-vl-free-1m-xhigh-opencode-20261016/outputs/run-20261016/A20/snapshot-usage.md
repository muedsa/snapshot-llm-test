# A20 Snapshot 使用报告

## 任务概述
- 任务ID: A20
- 标题: 二十四密集点的无重叠标注
- 画布尺寸: 1600×1100
- 输出文件: annotated-map.png, annotated-map.snapshot, label-layout.json, layout-audit.json

## DSL 标签能力
使用的 Snapshot DSL 标签：
- `<Snapshot>`: 根节点，type="png"
- `<SizedBox>`: 固定尺寸容器
- `<Stack>`: 垂直堆叠布局，alignment="TOP_LEFT"
- `<Container>`: 矩形容器，用于背景、主图边框、坐标轴线、点圆形（borderRadius）、标签盒底板、引导线段、图例色块
- `<Text>`: 文本渲染，支持 fontSize, fill, fontStyle, fontFamily, left, top

未使用的标签：`<Line>`, `<Circle>`（服务器不支持，改用 `<Container>` 模拟：圆点用 borderRadius 的正方形 Container，线条用 1px 宽/高的长条 Container）

## 几何映射
- 像素锚点公式: px = 280 + 10.4×x, py = 920 − 7.6×y（画布左上原点，x向右/y向下）
- 主图区: 左上(280,160)，宽1040，高760
- 普通点直径: 12px（半径6px）
- 密集中心点直径: 8px（半径4px，M06/M08/M09/M10/M11/M12）
- Value 最高3点: M10(93), M08(91), M23(90)，红色高亮

## 标签布局
- 24个标签分两列排布：左列7个（x=40），右列17个（x=1340）
- 每个标签盒 190×45px，包含两行文本（编号+name，value），正文20px
- 所有标签到锚点距离≥24px，均使用阶梯式引导线（水平+垂直段）
- 标签盒垂直间距≥52px，远超4px要求
- 无标签盒重叠，无引导线交叉，无边界违规

## 渲染验证
- HTTP 200，PNG 32242 字节，尺寸 1600×1100
- DSL 文件与 PNG 均已保存到输出目录

## 交付文件
- outputs/run-20261016/A20/annotated-map.png (最终图片)
- outputs/run-20261016/A20/annotated-map.snapshot (完整DSL)
- outputs/run-20261016/A20/label-layout.json (标签布局数据)
- outputs/run-20261016/A20/layout-audit.json (几何审计)
- outputs/run-20261016/A20/snapshot-usage.md (本报告)
- outputs/run-20261016/A20/task-metrics.json (耗时指标)

## 临时目录
- tmp/run-20261016/A20/gen_a20.py (生成脚本)
- tmp/run-20261016/A20/annotated-map.v1.snapshot (DSL草稿)
- tmp/run-20261016/A20/label-layout.json (布局数据)
- tmp/run-20261016/A20/markers-with-px.json (带像素坐标的标记点)

## 未解决事项
无。所有几何约束均已满足，标签无重叠，引导线无交叉，点不互相遮挡。
