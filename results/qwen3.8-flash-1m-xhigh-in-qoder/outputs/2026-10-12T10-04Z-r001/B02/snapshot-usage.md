# B02 使用说明 · 文档、DSL、服务与看图迭代

run `2026-10-12T10-04Z-r001` · 路径基准 `path_base = suite_root`。

## 1. 实际读过的文档

| 来源 | 本地缓存 | 在 B02 里实际用到什么 |
|---|---|---|
| `https://open-snapshot.muedsa.com/ai-guide.md` | `tmp/<run>/_suite/docs/`（共享准备阶段取得，B02 复用未重复请求） | 请求体为 UTF-8 纯文本 DSL；`type` 仅 png/jpg/webp；`Snapshot.background` 默认透明（十件全部显式给底色） |
| `https://snapshot.muedsa.com/` DSL 文档 | 同上 | `Container` 的 `borderRadius`/`shape`/`border`/`boxShadow`/渐变；`Text` 的 `fontFamily`/`fontStyle`/`textAlign`；`ClipPath path`；`Transform matrix` |
| `GET /fonts` | `tmp/<run>/_suite/` | 确认 `Noto Sans CJK SC` / `Noto Sans Mono CJK SC` / `Noto Serif CJK SC` 三族可用（本项目只用前两族） |

B01 已经踩过的边界在 B02 直接复用（记录在 `tmp/<run>/B01/snapshot-usage.md`），
本题新增/复现的有两条，见 §3。

## 2. 真实服务调用

- B02 目录内 **34 次请求**：30 次成功渲染 + 4 次共享构件探针（`kit-proof`、`kit-proof2`
  用于确认标记在 24/32/48/64/96 px 与反白下的形状），**0 次失败**。请求总耗时 130.1 s。
- 每件 `final.png` 是服务原始响应字节：与 `tmp/<run>/B02/` 中对应版本 `sha256` 逐一比对
  （10/10 相同），无后处理、无错误响应冒充。
- 复现单件：

```bash
python tmp/<run>/B02/case04_map.py          # 生成 DSL + 打印布局审计
python tmp/<run>/_suite/scripts/render.py \
  --dsl tmp/<run>/B02/case04.snapshot \
  --out outputs/<run>/B02/case-04/final.png \
  --log tmp/<run>/B02/requests.jsonl --req-id B02-case04-final --task B02 --kind final
```

- 整件重跑只需改 `tmp/<run>/B02/data.py`（数字）或 `tide.py`（样式），十件同步。

## 3. 本题新增/复现的踩坑（真实发生）

1. **文本里的 `<` `>` 被原样渲染成 `&lt;` `&gt;`**（B01 case-08 首次发现，B02 case-01 复现）：
   页脚写 `tmp/<run_id>/B02/...` 时，图上出现 `tmp/&lt;run_id&gt;/...`。
   处理：文档类文案改用 `[run_id]`；需要比较符时用全角 `＜` `＞`。已写入 case-01 的
   `change_log`。
2. **描边宽度 > 圆角半径 → 500 INTERNAL_ERROR**（B01 case-09 发现，B02 起在构件层拦截）：
   `tide.py` 的 `rect()` 现在会在构建期抛 `ValueError`，本题未再产生一次失败渲染。
3. **`Text` 宽度小于内容会被服务自动换行**：本题所有文本按实测字宽给宽
   （CJK 1.0em、比例拉丁 0.62em、等宽 0.52em、粗体余量 1.14、行距 1.46em），
   因此 `s.para()` 的换行位置与图上完全一致，也用于"两行放不下就抛错"。
4. **`bkit.para()` 返回的是下一行的行顶**，不是最后一行的底边（差 `size*(LINE_H-1.06)+gap`）；
   版心断言统一按 `end - 15 <= 底部` 计算，避免误判溢出。
5. **等时圈会冲出图幅**：case-04 第一版直接画整圆，圆环压在标题与右栏上。
   改为按 96 段采样、只画落在图幅内的小段（`s.line` 逐段），既保留圆环语义又不越界。
6. **小尺寸媒介的字号地板要用物理尺寸核对**：case-08 的 600 px = 100 mm → 18 px ≈ 3 mm 字高；
   case-10 的 800 px = 600 mm → 44 px ≈ 33 mm，对应 5–8 m 视认。这两个换算写进了
   `case.md` 与 `design-system.json`，不是凭感觉定的。

## 4. 逐件看图与修改（实际发生）

| 件 | 渲染 | 看到的问题 → 修改 |
|---|---|---|
| case-01 | 4 | 1680 高放不下六章节（`used_height` 断言）→ 画布 2520；标记尺寸标签压住 02 标题 → 行距；四级色卡 4 列放不下动作文案 → 改 2×2；页脚 `&lt;run_id&gt;` → 改 `[run_id]`；micro 14 px 样本与 18 px 地板冲突 → 改"放大示意" |
| case-02 | 5 | TIDELINE 被状态条压住、四级行动文字出行框、集合点插图标签互叠 → 头部条带加高、行高 80、插图改集合点表格；分隔线压住电话 → 按实测字宽定位 |
| case-03 | 4 | 阈值标签压曲线 → 移到曲线左端；铃铛与社区名重叠 → 图标右移；行动卡溢出且底部大片空白 → 卡片加高并补"今晚社区任务"两行 |
| case-04 | 6 | 等时圈冲出图幅、集合点标签互叠 → 圆环裁切、名称移入右栏；断面纵轴 6 档标签重叠 → 改 0/25/50/75/100；`km` 单位与右栏数字冲突 → 单位并入图框右下 |
| case-05 | 1 | 首版审计通过；看图确认 10 m 阅读下任务卡与名单层级成立（不为凑迭代而重排） |
| case-06 | 1 | 首版通过；额外用 PIL 缩到 220 px 实测缩略可读性（`case06-thumb220.png`） |
| case-07 | 1 | 首版通过；核对水深色条四档与 `data.PED` 边界一致 |
| case-08 | 2 | 待处理与检查说明超出 600 px → 改自动换行；页脚与封条行挤压 → 合并为一句 |
| case-09 | 2 | 响应时长柱顶数值压住标题 → 标签钳制；KPI 备注 18 px 低于地板 → 提到 20 px；画布按 `used_height` 收到 1780 |
| case-10 | 4 | 编号与名称重叠、两行信息互压 → 字级重排；圆环半径 372→320；底部信息被圆环穿过 → 加同色底带；品牌行低于字号地板且出界 → 提到 44 px 并上移 |

看图方式：100% 全图 + 局部放大（`case02-zoom-top.png`、`case02-zoom-foot.png`、
`case03-v2-2x.png`、`case03-v3-2x.png`、`case06-thumb220.png`），仅用于观察，不参与生成。

## 5. 其他工具的实际用途

见 `tmp/<run>/B02/tool-usage.jsonl`：PIL（缩略实测与局部放大）、`tide.py`（12 个组件 +
WCAG 断言）、`data.py`（等级判定、风险场、marching squares、run-length 合并、步行距离、
季度分位数）、`hashlib`（final 与响应字节一致性）、共享文档缓存。**未使用任何外部图像素材**，
因此没有 `asset-sources.json`（赛道允许而非要求）。

## 6. 最终审查与剩余事项

- 逐件：尺寸与 `Snapshot` 声明一致、`final.png`↔`final.snapshot` 配对、审计 0/0/0、
  `case.md` 与画面一致、`computed-data.json` 与图上数字可互查。
- 整体：`gallery.md` 覆盖 10/10；`touchpoint-map.json` 的共享数据映射与
  `portfolio.json` 的 `cross_check` 一致；`design-system.json` 描述的组件确实被
  其余九件调用（grep 生成脚本 import）。
- 未解决 / 已知不足：
  1. 未使用纹理或照片辅助素材，材质表现（沥青、水渍、覆膜反光）留白；
  2. case-04 色带为分档栅格，放大可见台阶；连续色场需更密网格或更多节点；
  3. case-05/06/07 各只有 1 次渲染即定稿——这是"首版达标不制造迭代"的选择，
     若评审期望更多视觉迭代，可在这三件上继续加密度（例如大屏增加时段热力与地图底图）；
  4. 全部数据为虚构参数，不能当作任何真实城市的结论。
