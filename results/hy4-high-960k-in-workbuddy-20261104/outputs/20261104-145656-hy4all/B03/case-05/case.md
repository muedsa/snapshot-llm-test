# case-05 · 光谱 · 摄影色温速查卡

## 场景

- 受众：摄影棚灯光师与影视现场摄影师
- 使用环境：灯光间墙面速查卡 / 平板对照卡
- 使用者要完成的事：按光源快速定位色温 K 值并选定白平衡档位
- 尺寸：1600 × 1000

## 内容

- 内容来源：通用摄影色温常识（颜色映射为近似示意）
- 主要信息：见最终图中标题、说明、数值区与脚注。

## 视觉选择

- 视觉主张：一条连续色温带承担全部核心信息，下方光源定位与白平衡卡片给出可执行结论
- 独到手法：多段 gradientStops 精确定位 11 个色温节点 + 8 位透明度刻度网格 + 分层信息卡
- 实际使用能力：gradientType=LINEAR(gradientStops)/8位 #RRGGBBAA/rect/line/circle/text/gradient 头部

## 素材情况

纯 DSL 构造，无外部图片素材；品牌、数值与文案为自拟演示内容。

## 实际自检

打开 `outputs/<run_id>/B03/case-05/final.png` 实际逐区查看。v1 因 gradientStops 传入字符串被二次 join 拆成字符，服务返回 400 PARSE_ERROR（错误响应保留在 case-05/responses/）；v2 改传列表修复并成功渲染。首版还发现「12 000 K」长标注射位与 1k–12k 刻度数字重叠；v3 改为居中冷暖说明 + 6 个带 K 值标签的定位圆点。最终逐区查看：11 段 gradientStops 连续色温带、刻度网格、6 张光源卡、4 张白平衡卡与脚注完整。通过。

- 尺寸（PNG IHDR 实测）：1600 × 1000
- 实际渲染请求 ID：B03-final-44173-0, B03-final-29513-0, B03-final-80764-0, B03-final-82291-1
- 完成标准：case-05-C1、case-05-C2、case-05-C3、case-05-C4 全部 passed（见 portfolio.json 的 criterion_results）
- 素材：纯 DSL，无外部素材；品牌与数值为自拟演示内容。


