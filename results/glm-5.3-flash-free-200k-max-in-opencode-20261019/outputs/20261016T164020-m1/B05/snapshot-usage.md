# B05 Snapshot 使用与留痕

## 文档与能力应用（真实取用）
- 本题未新增 HTTP 文档/字体请求（0 条）。B04 期间已实抓 ai-guide.md 与 DSL 文档（缓存存于
  `tmp/20261016T164020-m1/B04/renders/`，引用不重复计请求）；规约直接沿用：DSL XML 属性、
  CJK/Inter 双字体纪律（仅纯 ASCII 用 Inter；CJK 用 Noto Sans CJK SC；禁裸 `<`）、
  border 枚举仅 NONE/SOLID——本题 v1 再次实际踩坑（见下）、每 canvas 首笔全幅底色。
- 组件能力：Positioned/Container、Text（对齐/加粗/box_w）、line_thick、poly_rows（锯齿撕线）、
  hill_rows（c06 照片示意）、task_row/pill/lamp/statusbar（B04 已验证组件复用 + 本题扩展）。

## 服务调用
- 渲染 POST /snapshot：32 次（30×200 + 2×400）。400 均为 case-09 border `1.x DASHED`：
  服务枚举只有 NONE/SOLID，与 B04 的 border 踩坑同因（枚举常量不会自动放行）。
  失败响应原样留痕：`tmp/<run>/B05/renders/b05-case-09-v1-195341586.resp` 与
  `b05-case-09-v2-195427607.resp`（后者为渲染驱动回退到旧版 DSL 所致，教训入 iterations）。
- 无字体查询请求；无 429/超时；密钥零写入。逐请求明细 `tmp/<run>/B05/requests.jsonl`（32 行）。

## 逐件看图与修改（全部真实打开观察）
- 看图 33 次：v1 五张接触表（10 屏初判）→ v2 批重排（9 屏重渲+复看）→ 密集区放大 5 张 →
  c02/c03/c10 微调 → c08 流水卡裁切（放大捕捉）→ v3 加高复看 → c02 v4/c08 v4 整幅 →
  旅程级文案 4 屏修正（c01/c07/c09/c10）复看 → c09 v5 整幅 → 终态五张接触表整卷复审（旅程连贯性）。
- 修复汇总：右列重叠（c02/c05）、消息纵向溢出（c06）、字体误植（c08 元字 inter）、
  日期章压表头（c03）、周末口径矛盾（c04）、「元/分摊」流水对平（c08）、卡片裁切（c08/c09）、
  出画磁贴与行距（c09）、跨屏一致性 6 处（复盘日 / 已值口径 / 表态时序 / 下次复盘日期 / 清单时间语义 / 复印病句）。
- 做法依据 AGENTS.md「看图、迭代与最终审查」：每次成功响应实际打开判断，接触表仅工具不替代整幅查看。

## 复现条件
- 生成：`python b05_build.py <后缀>`（如 `_v2`）→ `tmp/<run>/B05/dsl/case-XX[-vN].snapshot`。
- 渲染：`python tmp/<run>/_suite/snapshot_client.py render B05 <dsl> <tag> <outdir>`，
  环境变量 SNAPSHOT_TASK_ROOT / SNAPSHOT_RUN_ID；响应 200 字节直存 final.png，无后处理。

## 最终审查
- 逐屏整幅 + 终版接触表双重过目；旅程连贯性（流程/时刻/色码/数据一致性）通过。
- 遗留事项：无；asset-sources.json 不设（零外部素材）。
