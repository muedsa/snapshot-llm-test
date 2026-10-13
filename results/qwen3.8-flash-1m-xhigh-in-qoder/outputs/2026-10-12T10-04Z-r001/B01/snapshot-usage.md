# B01 使用说明 · 文档、DSL、服务与看图迭代

run `2026-10-12T10-04Z-r001` · 路径基准 `path_base = suite_root`（相对总任务根）。

## 1. 实际读过的文档与其用途

| 来源 | 本地缓存 | 在 B01 里实际用到了什么 |
|---|---|---|
| `https://open-snapshot.muedsa.com/ai-guide.md` | `tmp/<run_id>/_suite/docs/`（共享准备阶段真实取得，B01 复用未重复请求） | 接口边界：`POST /snapshot` 请求体为 UTF-8 纯文本 DSL、`GET /fonts` 返回 text/plain；`type` 只接受 png/jpg/webp；`Snapshot.background` 默认透明（因此每件都显式给底色） |
| `https://snapshot.muedsa.com/` DSL 文档 | 同上 | 类 DOM 结构 `Snapshot > Stack > Positioned > Container/Text/Transform/ClipPath`；`Positioned` 必须是 Stack/Flex 直接子节点；`Container` 的 `borderRadius`/`shape`/`border`/`gradientColors`；`Text` 的 `fontFamily`/`fontSize`/`fontStyle`/`textAlign` |
| 字体清单 `GET /fonts` | `tmp/<run_id>/_suite/` 记录 | 确认可用的中文字体族名：`Noto Sans CJK SC` / `Noto Sans Mono CJK SC` / `Noto Serif CJK SC`，十件全部只用这三族 |

文档只给了能力清单，**行为边界全部靠真实探针确认**（`tmp/<run_id>/B01/probe-*.snapshot` 与
`probe-*.png`，共 41 次探针请求（其中 19 次为预期失败），记入 `tmp/<run_id>/B01/requests.jsonl`）。

## 2. 探针确认下来的硬约束（写进了 bkit 构件）

1. `ClipPath` 的属性名是 `path`，写成 `clipPath` 直接 `400 PARSE_ERROR: Attr [path] must not be null`。
2. `fillType="EVEN_ODD"` **被静默忽略**，填充按非零环绕：环形/挖孔必须用反向子路径（case-02 月牙、
   case-08 等值线 chip、case-03 风味轮环都依赖这条）。
3. `path` 支持 `M L H V C Q A Z`（含相对小写），`A` 圆弧可用 → case-02 的双弧月面、case-07 的银幕带。
4. **`border` 宽度大于 `borderRadius` 会让服务返回 `500 INTERNAL_ERROR`**，且没有解析错误提示：
   `border="2.5 SOLID …" borderRadius="2"` 必炸，`radius=3` 或 `border=1.5` 就正常（case-09 首版
   连续 3 次 500，用节点数二分定位到第 75 个节点）。已在 `bkit.rect()` 加构建期校验，宁可本地报错
   也不浪费一次渲染。
5. `shape="CIRCLE"` 与 `borderRadius` 不能同时给（A24 已踩，B01 规避）。
6. `Text` 给定的 `width` 小于内容时**服务会自动换行**，不会溢出裁掉 → 所有文本都按实测字宽给宽：
   CJK 1.0em、比例拉丁 0.62em、等宽 0.52em、粗体再乘 1.14 余量、行距 1.46em。
7. 文本里的 `<` 会被原样渲染成 `&lt;`（case-08 图例），需要比较符时用全角 `＜`。
8. 环形扇段的角度约定是 0°=12 点、顺时针（case-04 仪表弧、case-03 风味轮）。

## 3. 真实服务调用

- B01 目录内共 **88 次请求**：44 次成功渲染 + 3 次渲染失败（case-09 的 500 圆角问题）
  + 22 次探针成功 + 19 次探针失败（400/500，用来确认边界）；请求总耗时 299.6 s，单次 2.0–8.8 s（`Server-Timing: render;dur=…` 与 `cache` 头逐条记录）。
- 文档与字体查询发生在共享准备阶段，计入 `_suite` 的请求日志，本题不重复计数。
- 每件 `final.png` 都是服务原始响应字节：与 `tmp` 中对应版本 `sha256` 逐一比对相同（10/10 一致），
  没有二次加工、没有用错误响应冒充图片。
- 复现单件：

```bash
python tmp/<run_id>/B01/case06_festival.py      # 生成 DSL 并打印布局审计
python tmp/<run_id>/_suite/scripts/render.py \
  --dsl tmp/<run_id>/B01/case06.snapshot \
  --out outputs/<run_id>/B01/case-06/final.png \
  --log tmp/<run_id>/B01/requests.jsonl \
  --req-id B01-case06-final --task B01 --kind final
```

## 4. 逐件看图与修改（真实发生过的）

| 用例 | 渲染 | 看图发现的问题 → 修改 |
|---|---|---|
| case-01 | 3 | 换乘站没有共用顶点、线段不成 45° → 重排 L1 格点；站名压线 → 避让函数 |
| case-02 | 12 | 新月/满月被数成 21/23（容差窗口）→ 改过零检测得 12/13；月面凸向反了 → 交换双弧 |
| case-03 | 3 | 时间轴文字行距过挤 → 重排；雷达与柱状核对同源 |
| case-04 | 5 | 仪表弧被画成左半圆 → `donut_segment` 起始角统一减 90° |
| case-05 | 3 | 标记引线与站名重叠 → 交错避让；摘要数字改由数组反算 |
| case-06 | 4 | v1 冲突标签重叠、警示语出界 → 底部改成核对表 + 双动线面板；v2→v3 舞台底色留边；v3→v4 色条内收、未选节目改中性灰（原用风格色，与状态色撞车） |
| case-07 | 3 | v1 银幕标签压线、未选/受限与状态色混淆 → 尺寸线下移；v2 文字对比度按 WCAG 复算后把 `INK3` 从 `#8A8F9F` 压到 `#5A5F6D`（面板底上 4.63:1）；v3 说明段改定宽两行 |
| case-08 | 4 | v1 等值线满屏乱线（marching squares 插值漏了 level 项）→ 修正后成环；v2→v3 标签避让与比例尺底板；v3→v4 图例 `<` 改全角 `＜` |
| case-09 | 3 成 / 3 败 | 500 由圆角与描边冲突引起（见 §2.4）；真眼判定第一版把"斜角相连的两个空点"误判成两眼 → 加斜角全控规则；穷举从"24 种次序"修正为"16 条合法次序 + 16 手禁着" |
| case-10 | 4 | v1 航线与组件同色糊在一起、状态行伸进右栏 → 扫描线上移 28px、文案定宽；v2→v3 电量红线改画到"剩余 10%"的真实位置；v3→v4 补航线配色图例 |

看图为 100% 全图 + 局部放大（`tmp/<run_id>/B01/case0*-zoom-*.png`，用 PIL 裁剪，只用于观察，
不参与生成）。`iterations.jsonl` 逐版记录观察与修改；case-01..05 的查看时间按版本文件 mtime
补记并标注 `timestamp_source`，case-06..10 为会话内实时。

## 5. 其他工具的实际用途

见 `tmp/<run_id>/B01/tool-usage.jsonl`：PIL（读响应像素、裁剪放大、连通域）、自研 `bkit`
（测宽/避让/环形扇段/ClipPath/审计）、算法脚本（区间冲突与上界穷举、观影视角评分、
marching squares、围棋规则引擎、航段能耗与覆盖核算）、`hashlib`（final 与响应字节一致性）。
没有为了凑工具数量而调用；未使用外部图像素材，因此 `asset-sources.json` 不需要（十件全部
纯 DSL，见各 `case.md` 的"素材情况"）。

## 6. 最终审查与剩余事项

- 逐件复核：尺寸与 `Snapshot` 声明一致、`final.png` 与 `final.snapshot` 配对、布局审计
  0 重叠/0 出界/最小字号 20px、图中数字与 `computed-data.json` 一致、`case.md` 与实际画面相符。
- 整体复核：`gallery.md` 覆盖 10/10 件、链接相对本题输出根可离线打开；`portfolio.json` 的
  `criteria_results` 与 `work-plan.json` 判据一一对应。
- 已知不足（如实记录，不影响交付但影响"更像真实产品"）：
  1. 十件均未使用任何外部素材，B 赛道允许的纹理/照片层没有实践（`asset_policy` 允许而非要求）；
  2. case-08 的栅格是 run-length 合并的分档色块，放大看会有台阶，若要连续色场需要更密的网格
     或接受上千节点；
  3. case-01..06 的完成标准是事后写入计划文件的（`work-plan.json` 的 `change_log` 有记录）；
  4. case-09 的教学结论只覆盖"禁自杀 + 提子 + 真假眼"，未实现劫争，已在画面上写明边界。
