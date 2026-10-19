# A21 round-03 · snapshot-usage

## 状态
completed。round-03/launch-portrait.png/.snapshot(1080×1350)、launch-wide.png/.snapshot
(1440×810) 为服务 200 真实响应（v2 重渲后版本）；round-01/02 全部文件不改动完整保留。

## 本轮变更（design-tokens.changes 同源）
1. 深空主题→浅色：底渐变 #F5F8FC→#E9EFF7，文字墨色系 #0F1B2D/#2A3A54/#44536B，
   网址胶囊反转（#0D2237 底 + #7FF3E6 文），免费胶囊白底描边。
2. 新增网址上方英文副句『Clarity through structure』(26px)：竖 y1108、横 y624。
3. 品牌青文字色加深 #0A6E62→#085F55（审计驱动，见下），装饰渐变端色与主色不变；
   4 构件（横带/双环/信标/点阵）坐标继承，描线/点/晕改浅色系。
4. 全部 round-02 文案（标题 3 行/眉行/日期/讲者/赞助/免费参加/网址）保留并级联微移。

## 对比度审计（round-03/contrast-audit.json）
- 公式：WCAG 2.x sRGB 线性化 L=0.2126R+0.7152G+0.0722B，ratio=(L亮+0.05)/(L暗+0.05)，
  未舍入判值，阈值 4.5；阈值未用 UA 特殊公式豁免。
- 背景：使用两张**去文字辅助渲染**（同构布局删除全部 Text 及仅含 Text 的 Positioned，
  保留渐变底/幽灵环/点阵/白胶囊/深胶囊；label a21-r03-*-bg，响应与 PNG 保留于
   tmp/20261016T164020-m1/A21/bg-data/），在**最终图实测字形范围（前景色 ±3 通道匹配紧外包 + 2px
  反锯齿容差）**内逐像素取最劣背景样本。
- 结果：2 图 ×12 段全部 pass_unrounded；最小 5.199784（sponsor 前缀 #506681 on #ECF1F8）。
- 审计发现并修复的问题：v1 眉题 ONLINE LAUNCH 的 O 落在幽灵内环线上
  （#C7DCEE）仅 4.356541<4.5 → TEAL_INK 加深为 #085F55 重渲 v2 → 5.362942，24/24 通过。
- 失败尝试留痕：首轮辅助渲染 2×400（ProxyWidget has no widget，strip 后空
  Positioned 无子节点）；修好后同构重渲 2×200（过程入 syntax-fix 迭代记录）。

## 实际查看记录
- v1：两图 half + 竖 top/title/mid/bottom + 横 top/bottom + 2 张 bg-half 共 10 次查看。
- v2：两图 half + 眉题放大 3 次查看；audit 全红→全绿前后对比。
- iterations：baseline-v01（v1 两图，观察项：环线对比不足）→ syntaxfix-helper →
  visual-v02（TEAL_INK 修复；复查通过）。

## 未解决事项
无。
