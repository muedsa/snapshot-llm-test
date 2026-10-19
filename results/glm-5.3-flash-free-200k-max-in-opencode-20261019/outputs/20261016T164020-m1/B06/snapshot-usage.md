# B06 Snapshot 使用与留痕

## 文档与能力应用（真实取用）
- 本题未新增 HTTP 文档/字体请求（0 条）。ai-guide.md 与 DSL 文档在 B04 期间已实抓（缓存
  `tmp/20261016T164020-m1/B04/renders/`），规约沿用：DSL XML 属性、CJK/Inter 双字体纪律
  （仅纯 ASCII 用 Inter；CJK 用 Noto Sans CJK SC；禁裸 `<`）、每 canvas 首笔全幅底色。
- **本题踩坑（核心）**：v1 按「凭记忆的语法」写成——给 `<Text>` 想象了 x/y/boxWidth 属性、给
  `<Container>` 想象了 left/top/backgroundColor：10 张响应 200 但全部塌左上（不可用化）。
  复核后以 B05 已验证格式重写公共组件（`<Positioned left top width height>` 包
  `<Container width height color borderRadius border>`；`fontStyle="BOLD"`；胶囊字宽估算）。教训入 iterations。
- 组件能力：Positioned/Container/Stack、Text（对齐/加粗/box_w）、Transform matrix（4×4 列主序）、
  line_thick 折线、poly/网格枚举、stadium 胶囊、pill 自估宽、状态色语。

## 服务调用
- 渲染 POST /snapshot：39 次（39×200 + 0×失败）。v1（10，版式崩坏留证）→ v2（10，驱动误渲旧格式、
  响应字节与 v1 相同——哈希对比鉴别，不入看图数）→ v3（10，真实语法修复）→ v4（7）→ v5（c02）→ v6（c06）= 39。
- 无字体查询；无 429/超时/Retry-After；密钥零写入。逐请求明细 `tmp/<run>/B06/requests.jsonl`（39 行，
  Server-Timing/requestId 全采）。除渲染 HTTP 外的 2 次 websearch（政策号/WHO 口径）在 tool-usage.jsonl 记录，不重复计请求。

## 逐件看图与修改（全部真实打开观察）
**看图 41 次**：5（v1 接触表初判——发现版式崩坏）→ 10（v3 整幅逐件）→ 21（20 张 1:1 放大切片 +
 c06 修复后重看 zoom-b）→ 5（终态接触表整卷复审）。
- **修复汇总**：语法格式重写（全件）；c02 三问/页脚下移→再改短句（v4/v5）；c04 层序反转+读数保留（v4）；
  c06 页脚移位→「你的包裹」不压芯片（v4/v6）；c07 三角白底描边（v4）；c08 决策条三行下移（v4）；
  c09 B 列双行（v4）；c10 板标题/步骤两行（v4）。
- **未声称修改**：c01/c03/c05 自 v3 起无缺陷改型（整幅+放大复核通过，避免无意义迭代）。
- 做法依据 B06 AGENTS「看图、迭代与最终审查」：每次成功响应实际打开判断；接触表与放大为工具，不替代整幅查看。

## 数值与检索（真实发生）
- 数值唯一基准 `tmp/20261016T164020-m1/B06/research/calcs.json`（c02 IRR 月 1.0862%、c03 拆段 270.60、c09 四点税额、c05 50g 换算），本地先算后图。
- 两次 websearch 真实执行（2026-10-18 晚）：政策文件号（财政部/SAT2023-30→2027-12-31）与 WHO 25g；
  核实意见先记 plan v1.1，随后入图。无其他外部检索。

## 复现条件
- 生成：`python b06_build.py <后缀>`（如 `_v4`）→ `tmp/<run>/B06/dsl/case-XX[_vN].snapshot`（不可覆盖旧版）。
- 渲染：`python tmp/<run>/_suite/snapshot_client.py render B06 <dsl> <tag> <outdir>`，环境变量
  SNAPSHOT_TASK_ROOT / SNAPSHOT_RUN_ID；响应 200 字节直存 final.png，无后处理。
- 校验：十张终图与本处 events/checkpoints 追加式留痕全齐（events 下一编号由行数推导，不覆盖）。

## 最终审查
- 逐件：整幅（v3 起）+ 密集区 1:1 放大 + 终态接触表整卷 + 352 条画面文本抽取校笔（text_dump.txt）。
- G1–G5 与 S1–S10 对照全部通过（明细见各 case.md 第六节、design-review.md）。
- 遗留：无未决缺陷；未验证效果（用户实验类）已在 design-review.md/problem-evidence.json 如实单列；
  asset-sources.json 不设（零嵌入素材，无外部资产引用）。
