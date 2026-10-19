# B03 · snapshot-usage

## 状态与统计
completed。十件场景作品全部 open-snapshot 200 真实渲染与同名 .snapshot；
渲染 24 次（24 成功：探针 3 + 案例 21），
服务端时长合计 16.80s；DSL 4 版本；13 次看图；
1 基线 + 4 轮完整视觉迭代。

## 探索方式（先探针后成品）
1. probe-rot / probe-rot2：Transform 矩阵旋转文本全角度可行
   （0–135° 与背向六角均单字形）→ case-02 启用 24 处 rot_text。
2. probe-iso：异形圆角降级胶囊、同心环叠色可行、剪切矩阵不可靠
   → 放弃 Transform 等距，改用扫描线多边形（case-09 六面体、
   case-06 楔形、case-01 等高线、case-08 胶囊均为该结论的产物）。
   证据：steps/probe-*.png；探针 DSL 与脚本保留于本题 tmp 目录。

## 检查与修复（真图检视）
1. case-03 恒零板初版为实心块 → 改 4px 直条（visual-02）。
2. case-04 下半空洞扩容后，阶梯最高条压标题 → 标题上移+底线 1310
   （visual-03 复核通过）。
3. case-06 射线内联标签陡角段重叠 → 改左下图例列（visual-04）。
4. case-01 数值标签杂乱 → 单行高程键；外环对比弱 → 色阶加深
   （visual-04/05 分两步收敛）。
5. case-07 标签抬离标记点、case-09 文案『大不压小』、case-10 卡片右移
   让出竖排标题列（visual-03）。
6. 构建期修复：c02 rect 缺 s 参（第一个 build 即拦截）、c10 enumerate
   括号笔误——均为渲染前语法级修复。

## 文档与工具复用
未发起新的文档 HTTP 请求；沿用 tmp/docs/ 缓存（ai-guide/DSL/layout/fonts）。
三支探针 DSL/脚本/PNG 响应全部保留（renders/ 与本题 tmp 根）。

## 未解决事项
无。十件均为纯 DSL 构造（唯一字体能力内），品牌与数字标明演示/虚构；
无外部素材图片参与主体。
